#!/usr/bin/env python3
"""One trial of the bomb pot research loop: a full self-play run from a
config file, and one line with its result.

    python tools/bombpot/trial.py --config research/base.json --work DIR
        --exe target/release/bombpot [--threads 10] [--gpu-free-gb 2]

A config (see research/base.json) names the game settings (`spec`), the
number of rounds, the options of loop.py (`loop`; `flags` lists the on/off
ones) and two lists of flops to score the final strategy net on: `trained`
(flops the spec practises on) and `unseen` (flops it never plays). Paths in
a config are taken from the folder of this script.

The run goes to DIR/<name>/ and can be stopped and started again. When it
ends, DIR/<name>/result.json holds the scores and a copy of that line is
added to DIR/trials.jsonl:

    unseen    average % of the pot a perfect opponent gains on the unseen
              flops, from the flop (the number a trial is judged on)
    trained   the same on the trained flops
    by_flop   every flop's score from the flop, from the turn, on the river
    minutes   wall time of the whole trial
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def scores(log_path, rounds):
    """The last score line of each flop at the final round."""
    out = {}
    with open(log_path) as f:
        for line in f:
            row = json.loads(line)
            if row.get("event") == "score" and row.get("iter") == rounds:
                out[row["boards"][0]] = row
    return out


def summary(cfg, log_path):
    got = scores(log_path, cfg["rounds"])
    missing = [b for b in cfg["trained"] + cfg["unseen"] if b not in got]
    if missing:
        sys.exit(f"no final score for {missing}")
    mean = lambda flops: round(sum(got[b]["gain_pct_of_pot"] for b in flops) / len(flops), 3)
    return {
        "name": cfg["name"],
        "unseen": mean(cfg["unseen"]),
        "trained": mean(cfg["trained"]),
        "exact": all(got[b]["exact"] for b in got),
        "by_flop": {b: [round(x, 2) for x in got[b]["gain_pct_from_street"]] for b in cfg["trained"] + cfg["unseen"]},
        "rounds": cfg["rounds"],
        "config": cfg,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--exe", required=True)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--gpu-free-gb", type=float, default=0)
    a = ap.parse_args()
    with open(a.config) as f:
        cfg = json.load(f)
    work = os.path.join(a.work, cfg["name"])
    os.makedirs(work, exist_ok=True)
    result_path = os.path.join(work, "result.json")
    if os.path.exists(result_path):
        sys.exit(f"{result_path} exists: this trial is finished (use another name)")
    with open(os.path.join(work, "config.json"), "w") as f:
        json.dump(cfg, f, indent=1)
    games = [os.path.join(HERE, "specs", f"flop_{b}.json") for b in cfg["trained"] + cfg["unseen"]]
    for g in games:
        if not os.path.exists(g):
            sys.exit(f"no score game {g}")
    cmd = [sys.executable, os.path.join(HERE, "loop.py"), "--spec", os.path.join(HERE, cfg["spec"]),
           "--work", work, "--exe", a.exe, "--iters", str(cfg["rounds"]),
           "--score-every", str(cfg.get("score_every", cfg["rounds"])), "--score", *games]
    opts = dict(cfg.get("loop", {}))
    for flag in opts.pop("flags", []):
        cmd.append("--" + flag)
    for key, value in opts.items():
        cmd += ["--" + key, str(value)]
    if a.threads:
        cmd += ["--threads", str(a.threads)]
    if a.gpu_free_gb:
        cmd += ["--gpu-free-gb", str(a.gpu_free_gb)]
    t0 = time.time()
    with open(os.path.join(work, "loop.out"), "a") as out, open(os.path.join(work, "loop.err"), "a") as err:
        code = subprocess.run(cmd, stdout=out, stderr=err).returncode
    if code:
        sys.exit(f"the loop ended with code {code}; see {work}/loop.err")
    res = summary(cfg, os.path.join(work, "log.jsonl"))
    # A trial that was stopped and started again took longer than this run
    # of the script: the log's first and last lines give the whole time.
    with open(os.path.join(work, "log.jsonl")) as f:
        times = [json.loads(line)["time"] for line in f]
    span = time.mktime(time.strptime(times[-1], "%Y-%m-%dT%H:%M:%S")) - time.mktime(time.strptime(times[0], "%Y-%m-%dT%H:%M:%S"))
    res["minutes"] = round(max(span, time.time() - t0) / 60, 1)
    with open(result_path, "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(a.work, "trials.jsonl"), "a") as f:
        f.write(json.dumps(res) + "\n")
    print(json.dumps({k: res[k] for k in ("name", "unseen", "trained", "minutes")}))


if __name__ == "__main__":
    main()
