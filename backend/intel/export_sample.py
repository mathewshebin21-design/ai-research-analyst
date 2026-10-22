"""Save a completed run as the public sample report.

    python -m intel.export_sample RUN_ID "A real run recorded on 22 October 2026."

The sample uses the same read-only view as a share link (no activity, costs, members or settings)
and is labelled with the note given, which the sample page shows above the report. It is written to
the web app as a static file, so the sample page works without the API.
"""

import json
import sys
from pathlib import Path

from intel.api.share import public_view
from intel.db import session_factory
from intel.models import Run

SAMPLE_PATH = Path(__file__).resolve().parents[2] / "frontend" / "public" / "sample-run.json"


def export(run_id: str, note: str) -> dict:
    with session_factory()() as db:
        run = db.get(Run, run_id)
        if run is None or run.status != "completed":
            raise SystemExit("Choose a completed run.")
        data = public_view(db, run)
    data.update(
        workspace_name="Sample",
        sample=True,
        sample_note=note,
        previous_run_id=None,
        changes=None,
        refresh_monthly=False,
    )
    SAMPLE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    export(sys.argv[1], sys.argv[2])
    print(f"Wrote {SAMPLE_PATH}")
