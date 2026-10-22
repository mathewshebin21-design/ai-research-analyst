"""Save a completed run as the public sample report.

    python -m intel.export_sample RUN_ID "A real run recorded on 22 October 2026."

The sample uses the same read-only view as a share link (no activity, costs, members or settings)
and is labelled with the note given, which the sample page shows above the report.
"""

import json
import sys

from intel.api.share import public_view
from intel.db import session_factory
from intel.growth import SAMPLE_PATH
from intel.models import Run


def export(run_id: str, note: str) -> dict:
    with session_factory()() as db:
        run = db.get(Run, run_id)
        if run is None or run.status != "completed":
            raise SystemExit("Choose a completed run.")
        data = public_view(db, run)
    data.update(workspace_name="Sample", sample_note=note, previous_run_id=None, changes=None, refresh_monthly=False)
    SAMPLE_PATH.parent.mkdir(exist_ok=True)
    SAMPLE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    export(sys.argv[1], sys.argv[2])
    print(f"Wrote {SAMPLE_PATH}")
