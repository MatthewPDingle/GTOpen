#!/usr/bin/env python3
"""Self-play loop for the bomb pot net.

    python tools/bombpot/loop.py --spec spec.json --work DIR --iters 100
        --exe target/release/bombpot [--score game.json ...] [--score-every 10]

Each round: the engine plays the games in `spec.json` with the latest
advantage net and writes examples (`bombpot gen`); the trainer fits the next
advantage net to the examples of every round so far. Every `--score-every`
rounds a strategy net is fitted to the mixes played so far and the engine
scores it on each `--score` game (`bombpot score`): what a perfect opponent
would gain against it, in chips and as a share of the starting pot.

Everything goes under DIR: examples in mem/, nets as adv_NNNN.bin and
avg_NNNN.bin, one JSON object per event in log.jsonl. A stopped loop picks
up where it left off when started again with the same DIR.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import train as T  # noqa: E402


def run(cmd):
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip().splitlines()
    return json.loads(out[-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--exe", required=True)
    ap.add_argument("--iters", type=int, default=100)
    ap.add_argument("--threads", type=int, default=0, help="engine threads (0: all)")
    ap.add_argument("--score", nargs="*", default=[], help="game files to score the strategy net on")
    ap.add_argument("--score-every", type=int, default=10)
    ap.add_argument("--score-turns", type=int, default=0, help="score on this many turn cards (0: all, exact)")
    ap.add_argument("--score-rivers", type=int, default=0)
    ap.add_argument("--hidden", type=int, default=256)
    ap.add_argument("--layers", type=int, default=3)
    ap.add_argument("--plain", action="store_true")
    ap.add_argument("--steps", type=int, default=2000, help="training steps per round")
    ap.add_argument("--avg-steps", type=int, default=0, help="steps for a strategy net (0: twice --steps)")
    ap.add_argument("--batch", type=int, default=8192)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--warm", action="store_true", help="start each advantage net from the last one")
    ap.add_argument("--cap", type=int, default=40_000_000)
    ap.add_argument("--device", default="cuda" if T.torch.cuda.is_available() else "cpu")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    mem_dir = os.path.join(a.work, "mem")
    os.makedirs(mem_dir, exist_ok=True)
    log_path = os.path.join(a.work, "log.jsonl")

    def log(obj):
        obj["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        with open(log_path, "a") as f:
            f.write(json.dumps(obj) + "\n")
        print(json.dumps(obj), flush=True)

    threads = ["--threads", str(a.threads)] if a.threads else []
    adv, strat = T.Memory(a.cap, a.seed), T.Memory(a.cap, a.seed + 1)
    net_of = lambda kind, it: os.path.join(a.work, f"{kind}_{it:04d}.bin")
    for it in range(1, a.iters + 1):
        prefix = os.path.join(mem_dir, f"it{it:04d}")
        done = os.path.exists(net_of("adv", it))
        if not (done and os.path.exists(prefix + ".strat.bps")):
            cmd = [a.exe, "gen", a.spec, "--out", prefix, "--iter", str(it), "--seed", str(a.seed)] + threads
            if it > 1:
                cmd += ["--net", net_of("adv", it - 1)]
            log(run(cmd))
        adv.add(prefix + ".adv.bps")
        strat.add(prefix + ".strat.bps")
        if not done:
            init = net_of("adv", it - 1) if a.warm and it > 1 else None
            res = T.train(adv, net_of("adv", it) + ".tmp", a.hidden, a.layers, not a.plain, a.steps, a.batch, a.lr,
                          init, a.device, a.seed + it)
            os.replace(net_of("adv", it) + ".tmp", net_of("adv", it))
            log({"event": "train", "iter": it, **res})
        scoring = a.score and (it % a.score_every == 0 or it == a.iters)
        if scoring and not os.path.exists(net_of("avg", it)):
            res = T.train(strat, net_of("avg", it) + ".tmp", a.hidden, a.layers, not a.plain,
                          a.avg_steps or 2 * a.steps, a.batch, a.lr, None, a.device, a.seed + it)
            os.replace(net_of("avg", it) + ".tmp", net_of("avg", it))
            log({"event": "train", "iter": it, **res})
            for game in a.score:
                cmd = [a.exe, "score", game, "--net", net_of("avg", it)] + threads
                if a.score_turns or a.score_rivers:
                    cmd += ["--turns", str(a.score_turns), "--rivers", str(a.score_rivers)]
                log({"iter": it, "game": os.path.basename(game), **run(cmd)})


if __name__ == "__main__":
    main()
