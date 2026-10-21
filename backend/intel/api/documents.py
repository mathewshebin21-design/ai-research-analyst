from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from intel.api.deps import audit, expensive, rate_limited
from intel.api.readmodel import iso
from intel.config import Settings, get_settings
from intel.db import get_db
from intel.models import Chunk, Document, EvidenceLink, Source, User
from intel.rag.pdf import UploadRejected, chunk_pages, storage_path, store_bytes, validate_pdf
from intel.security.auth import accepted_user, require_role

router = APIRouter(dependencies=[Depends(rate_limited)])


def doc_out(d: Document) -> dict:
    return {
        "id": d.id,
        "filename": d.filename,
        "pages": d.pages,
        "size_bytes": d.size_bytes,
        "status": d.status,
        "uploaded_at": iso(d.created_at),
    }


@router.get("/workspaces/{workspace_id}/documents")
def list_documents(workspace_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> list[dict]:
    require_role(db, user, workspace_id, "viewer")
    return [
        doc_out(d) for d in db.query(Document).filter_by(workspace_id=workspace_id).order_by(Document.created_at.desc())
    ]


@router.post("/workspaces/{workspace_id}/documents", status_code=201, dependencies=[Depends(expensive)])
async def upload_document(
    workspace_id: str,
    file: UploadFile = File(...),
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    require_role(db, user, workspace_id, "editor")
    limit = settings.max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    try:
        pages = validate_pdf(data, max_bytes=limit, max_pages=settings.max_pdf_pages)
    except UploadRejected as exc:
        raise HTTPException(422, str(exc)) from exc
    key, digest = store_bytes(settings.storage_dir, data, ".pdf")
    name = (file.filename or "document.pdf").replace("\\", "/").rsplit("/", 1)[-1][:200] or "document.pdf"
    doc = Document(
        workspace_id=workspace_id,
        uploaded_by=user.id,
        filename=name,
        storage_key=key,
        sha256=digest,
        size_bytes=len(data),
        pages=len(pages),
    )
    db.add(doc)
    db.flush()
    for page, ordinal, text in chunk_pages(pages):
        db.add(Chunk(document_id=doc.id, page=page, ordinal=ordinal, text=text))
    audit(db, "document.uploaded", user.id, workspace_id, document=doc.id, pages=len(pages))
    db.commit()
    return doc_out(doc)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(404, "Document not found.")
    require_role(db, user, doc.workspace_id, "editor")
    # Remove the text everywhere it was copied, including evidence extracts in past runs.
    for src in db.query(Source).filter_by(document_id=doc.id):
        src.content = "[document deleted]"
        for link in db.query(EvidenceLink).filter_by(source_id=src.id):
            link.passage, link.quote = "[document deleted]", None
    key = doc.storage_key
    db.delete(doc)
    audit(db, "document.deleted", user.id, doc.workspace_id, document=document_id)
    db.commit()
    storage_path(settings.storage_dir, key).unlink(missing_ok=True)
    return {"deleted": True}
