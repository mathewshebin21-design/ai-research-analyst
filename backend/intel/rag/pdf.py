"""Secure PDF intake and page-level chunking."""

import hashlib
import io
import secrets
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from intel.rag.text import normalize, split_passages


class UploadRejected(ValueError):
    """The upload failed validation. The message is shown to the user."""


@dataclass
class PageText:
    page: int
    text: str


def validate_pdf(data: bytes, *, max_bytes: int, max_pages: int) -> list[PageText]:
    if len(data) == 0:
        raise UploadRejected("The file is empty.")
    if len(data) > max_bytes:
        raise UploadRejected(f"The file is larger than {max_bytes // (1024 * 1024)} MB.")
    if not data[:1024].lstrip().startswith(b"%PDF-"):
        raise UploadRejected("Only PDF files are accepted.")
    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise UploadRejected("Password-protected PDFs are not supported. Remove the password and upload again.")
        n = len(reader.pages)
        if n > max_pages:
            raise UploadRejected(f"The PDF has {n} pages; the limit is {max_pages}.")
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:  # noqa: BLE001 - one bad page should not sink the document
                text = ""
            pages.append(PageText(page=i, text=text))
    except UploadRejected:
        raise
    except (PdfReadError, ValueError, KeyError, TypeError) as exc:
        raise UploadRejected("The PDF could not be read. It may be damaged.") from exc
    if not any(p.text.strip() for p in pages):
        raise UploadRejected("No text could be extracted. Scanned PDFs need OCR before upload.")
    return pages


def chunk_pages(pages: list[PageText]) -> list[tuple[int, int, str]]:
    """Return (page, ordinal, text). Chunks never cross a page boundary, so citations stay exact."""
    out = []
    for p in pages:
        for j, passage in enumerate(split_passages(p.text, target=900)):
            if len(normalize(passage)) >= 40:
                out.append((p.page, j, passage))
    return out


def store_bytes(storage_dir: str, data: bytes, suffix: str) -> tuple[str, str]:
    """Write under a random name. Client filenames are never used in paths."""
    key = secrets.token_hex(16) + suffix
    root = Path(storage_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / key).write_bytes(data)
    return key, hashlib.sha256(data).hexdigest()


def storage_path(storage_dir: str, key: str) -> Path:
    if "/" in key or "\\" in key or key.startswith("."):
        raise ValueError("invalid storage key")
    return Path(storage_dir) / key
