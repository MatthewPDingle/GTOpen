"""Read-only postprocessing once the isolated solve has completed."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import analyze
import run

OUT, ROOT = run.OUT, run.ROOT


def sha256(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def main():
    provenance = analyze.read(OUT / "provenance.json")
    assert sha256(ROOT / "cache/preflop_eq169.bin") == provenance["equity_sha256"]
    assert sha256(ROOT / "cache/realization_fit.json") == provenance["realization_fit_sha256"]
    status = run.request("status")
    assert status["state"] == "done", status["state"]
    assert status["iteration"] == analyze.read(OUT / "refined-status.json")["iteration"]
    audits = []
    for k, actor in enumerate(["HJ", "CO", "BTN", "SB", "BB", "UTG"]):
        path = [1, 2] + [0] * k
        node = run.request("node", {"path": path})
        assert node["actor_pos"] == actor
        audits.append({"path": path, "actor": actor, "actions": node["actions"],
                       "branch_probability": node.get("branch_probability")})
    path = [1, 2] + [0] * 6 + [2]
    node = run.request("node", {"path": path})
    assert node["actor_pos"] == "MP"
    assert [analyze.action_name(a) for a in node["actions"]] == ["Fold", "Call", "Allin 200"]
    audits.append({"path": path, "actor": "MP", "role": "5-bet response", "actions": node["actions"]})
    run.dump("later-menu-audit.json", audits)
    analyze.main()
    # Saved-game evaluation is independent of the live server and asserts
    # internally that it did not mutate any strategy arena.
    executable = ROOT / "target/release/examples/preflop_action_evs.exe"
    save = ROOT / "saves/preflop" / (run.SAVE + "-refined.gtop")
    run.dump("save-provenance.json", {
        "save": str(save.relative_to(ROOT)), "sha256": sha256(save),
        "action_evaluator_sha256": sha256(executable),
    })
    for key, (path, _) in run.CASES.items():
        dest = OUT / (key + "-action-evs.json")
        if not dest.exists():
            with (OUT / (key + "-action-evs.log")).open("w") as log:
                subprocess.run([str(executable), str(save), str(dest), ",".join(map(str, path))],
                               cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        result = analyze.read(dest)
        assert result["config"] == analyze.read(OUT / "config.json")
        assert result["path"] == path and result["iteration"] == status["iteration"]
    print("All six action-value readouts validated.")


if __name__ == "__main__":
    main()
