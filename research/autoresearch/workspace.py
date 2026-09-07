"""Locate/create the research checkout without machine-specific paths."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LAB = ROOT / "target/autoresearch/workspace"


def ensure_workspace():
    config = json.loads((HERE / "run.json").read_text(encoding="utf-8"))
    revision = config["final_kept_commit"]
    def git(*args, check=True):
        return subprocess.run(["git", "-C", str(ROOT), *args], check=check,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if git("cat-file", "-e", revision + "^{commit}", check=False).returncode:
        print("Fetching published research history...", flush=True)
        git("fetch", "origin", "codex/autoresearch-20260907")
    if LAB.exists():
        # Never reset an existing experiment, including uncommitted work.
        probe = subprocess.run(["git", "-C", str(LAB), "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True)
        if probe.returncode or Path(probe.stdout.strip()).resolve() != LAB.resolve():
            raise RuntimeError(f"{LAB} already exists but is not a research checkout; leaving it untouched.")
        return LAB
    LAB.parent.mkdir(parents=True, exist_ok=True)
    git("-c", "core.autocrlf=false", "worktree", "add", "--detach", str(LAB), revision)
    print(f"Prepared research checkout: {LAB}", flush=True)
    return LAB
