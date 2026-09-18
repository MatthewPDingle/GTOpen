"""Wait for this specific existing runner, then extract results once.

This launches no solve and never mutates either server. It may be restarted
after an extraction failure; validated action-value outputs are reused.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import traceback

import psutil
import run


def status(stage, **fields):
    run.dump("postprocess-status.json", {
        "stage": stage, "updated_utc": datetime.now(timezone.utc).isoformat(), **fields,
    })


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: postprocess.py EXISTING_RUNNER_PID")
    pid = int(sys.argv[1])
    marker = run.OUT / "production-preserved.json"
    if not marker.exists():
        worker = psutil.Process(pid)
        assert any("wizard-baseline-20260919/run.py" in a.replace("\\", "/")
                   for a in worker.cmdline()), "PID is not this study runner"
        status("waiting_for_solve", runner_pid=pid, runner_created=worker.create_time())
        worker.wait()  # Separate background helper; it does not block the agent.
    assert marker.exists(), "Solve runner ended before saving both checkpoints"
    for script in ("finish.py", "plot.py", "report.py"):
        status("extracting", script=script)
        with (run.OUT / (Path(script).stem + ".log")).open("w") as log:
            subprocess.run([sys.executable, str(run.OUT / script)], cwd=run.ROOT,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
    status("ready_for_review", report="RESULTS.md")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        status("failed", error=str(error), traceback=traceback.format_exc())
        raise
