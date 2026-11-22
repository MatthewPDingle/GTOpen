#!/usr/bin/env python3
"""Self-play loop for the bomb pot net.

    python tools/bombpot/loop.py --spec spec.json --work DIR --iters 100
        --exe target/release/bombpot [--score game.json ...] [--score-every 10]

The seats take turns. In each half of a round the engine plays the games in
`spec.json` with the latest advantage net and writes examples of one seat's
decisions (`bombpot gen --seat`); the trainer then fits the next advantage
net to the examples of every round so far. Every `--score-every` rounds a
strategy net is fitted to the mixes played so far and the engine scores it
on each `--score` game (`bombpot score`): what a perfect opponent would gain
against it, in chips and as a share of the starting pot.

Everything goes under DIR: examples in mem/, nets as adv_NNNN.bin (one per
half round) and avg_NNNN.bin (per scored round), one JSON object per event
in log.jsonl. A stopped loop picks
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


LOW = {}


def lower_priority():
    """Run this process and the engine below normal priority, so a shared
    machine stays responsive."""
    if os.name == "nt":
        import ctypes
        below_normal = 0x00004000
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), below_normal)
        LOW["creationflags"] = below_normal
    else:
        os.nice(10)


def run(cmd):
    out = subprocess.run(cmd, check=True, capture_output=True, text=True, **LOW).stdout.strip().splitlines()
    return json.loads(out[-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--exe", required=True)
    ap.add_argument("--iters", type=int, default=100, help="rounds (each seat learns once per round)")
    ap.add_argument("--threads", type=int, default=0, help="engine threads (0: all)")
    ap.add_argument("--score", nargs="*", default=[], help="game files to score the strategy net on")
    ap.add_argument("--score-every", type=int, default=10)
    ap.add_argument("--score-turns", type=int, default=0, help="score on this many turn cards (0: all, exact)")
    ap.add_argument("--score-rivers", type=int, default=0)
    ap.add_argument("--hidden", type=int, default=256)
    ap.add_argument("--layers", type=int, default=3)
    ap.add_argument("--plain", action="store_true")
    ap.add_argument("--steps", type=int, default=2000, help="training steps per half round")
    ap.add_argument("--avg-steps", type=int, default=0, help="steps for a strategy net (0: twice --steps)")
    ap.add_argument("--batch", type=int, default=8192)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--warm", action="store_true", help="start each advantage net from the last one")
    ap.add_argument("--cap", type=int, default=40_000_000)
    ap.add_argument("--device", default="cuda" if T.torch.cuda.is_available() else "cpu")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--low-priority", action="store_true", help="run below normal priority")
    ap.add_argument("--torch-threads", type=int, default=0, help="CPU threads for training (0: PyTorch's choice)")
    a = ap.parse_args()
    if a.low_priority:
        lower_priority()
    if a.torch_threads:
        T.torch.set_num_threads(a.torch_threads)

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
    seats = 2
    for step in range(1, a.iters * seats + 1):
        it, seat = (step + seats - 1) // seats, (step - 1) % seats
        prefix = os.path.join(mem_dir, f"r{it:04d}s{seat}")
        done = os.path.exists(net_of("adv", step))
        if not (done and os.path.exists(prefix + ".strat.bps")):
            cmd = [a.exe, "gen", a.spec, "--out", prefix, "--iter", str(it), "--seat", str(seat),
                   "--seed", str(a.seed)] + threads
            if step > 1:
                cmd += ["--net", net_of("adv", step - 1)]
            log(run(cmd))
        adv.add(prefix + ".adv.bps")
        strat.add(prefix + ".strat.bps")
        if not done:
            init = net_of("adv", step - 1) if a.warm and step > 1 else None
            res = T.train(adv, net_of("adv", step) + ".tmp", a.hidden, a.layers, not a.plain, a.steps, a.batch, a.lr,
                          init, a.device, a.seed + step)
            os.replace(net_of("adv", step) + ".tmp", net_of("adv", step))
            log({"event": "train", "iter": it, "seat": seat, **res})
        scoring = a.score and seat == seats - 1 and (it % a.score_every == 0 or it == a.iters)
        if scoring and not os.path.exists(net_of("avg", it)):
            res = T.train(strat, net_of("avg", it) + ".tmp", a.hidden, a.layers, not a.plain,
                          a.avg_steps or 2 * a.steps, a.batch, a.lr, None, a.device, a.seed + step)
            os.replace(net_of("avg", it) + ".tmp", net_of("avg", it))
            log({"event": "train", "iter": it, **res})
            for game in a.score:
                cmd = [a.exe, "score", game, "--net", net_of("avg", it)] + threads
                if a.score_turns or a.score_rivers:
                    cmd += ["--turns", str(a.score_turns), "--rivers", str(a.score_rivers)]
                log({"iter": it, "game": os.path.basename(game), **run(cmd)})


if __name__ == "__main__":
    main()
