#!/usr/bin/env python3
"""Exact flop solves of real preflop ranges, as leaf-net training data and check sets.

    python tools/leafnet/realrange.py pack PILOT_ROOT --out DIR
    python tools/leafnet/realrange.py compare --snapshot SNAP --arm pool=RUN,RUN,RUN --arm real=RUN,RUN,RUN

Why. The pool's ranges are drawn by a sampler. The ranges a preflop solve
brings to a flop are not, and a solve steers them toward the leaves where
its net pays too much: each net is too generous on the ranges of its own
solves (loop 4's nets by 0.9% of the pot on six games solved with them, v1
by 3.6% on a game solved with v1) and reads lower on another net's. The cure
is training data on the ranges a net's own solves produce: solve preflop
games, export their heads-up flop leaves (`solve-cli datagen leaves`), solve
those exactly (`solve-cli datagen solve`), train on them next to the pool,
and check by solving again with the retrained net. Whole games are held out
for checking, never single leaves, because one game's leaves share their
ranges' ancestry.

pack reads PILOT_ROOT/manifest.json,

    {"games": [{"id": "g01", "folder": "g01", "held_out": false, "source": "leafnet", "config": {...}}, ...]}

(folder: a `datagen leaves` + `datagen solve` folder, absolute or relative to
PILOT_ROOT; config: the game's preflop config; source: the realization it was
solved under) and writes

    DIR/train/<id>/job-<job>.jsonl.gz    a training game's leaves, one file each:   prepare.py --extra DIR/train
    DIR/<name>/solved.jsonl, leaves.json every held-out game's leaves as one set:   prepare.py --leafcheck DIR/<name>
    DIR/pack.json                        what went where

`datagen leaves` numbers every game's leaves from the same base, so pack
renumbers them. Training leaves get job numbers that gonogo.split_of puts in
the training split, so the validation and test jobs stay the pool's and a
snapshot with these files has the pool snapshot's held-out rows unchanged.
Held-out leaves get a range of their own. A held-out game with a twin in
training (the same config under another realization or net) is refused. The
job files' headers say generator version 100 (prepare.REAL_GENERATOR), which
is how train.py finds these rows ("real_weight", "real_distill_mix").

Nothing here uploads anything. Ranges solved by GTOpen stay on the machine
that solved them: never add a pack folder to the public dataset.

compare scores net files on every scoring set of a snapshot (validation, the
referee's val_cv, the real-leaf sets), with numpy alone. An arm is one recipe:
its nets are seed copies, and its errors are the per-leaf errors averaged
over them (or, with --ensemble, the errors of the nets' mean output, which is
what a solve uses). A net is a run id of any snapshot, a run folder or a net
file, so nets trained on another snapshot are scored on the same examples.
Besides the harness's class and range error it reports the "total": both
players' predicted range values minus the exact solve's, in percent of the
pot. Zero is right; negative means the ranges are undervalued. A real-leaf
set's total belongs to the net whose solve chose the ranges: the same net
scores differently on the leaves of another net's solve.
Intervals resample whole leaves (jobs); differences are against the first arm.
"""

import argparse
import datetime
import glob
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "datagen"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import leafnet_io  # noqa: E402
from gonogo import NC, range_values, split_of  # noqa: E402
from prepare import POT_TYPES, REAL_GENERATOR, work_dir  # noqa: E402

TRAIN_BASE = 910_000_000_000     # above the leaf-check jobs (900e9 + rank), far above contributor blocks
HELD_BASE = 920_000_000_000
PER_GAME = 1_000_000
REPS = 2000


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------------------------ pack ----

def read_solved(folder):
    """{leaf job: [example records by board index]} of a `datagen solve` folder (a board solved twice counts once)."""
    path = os.path.join(folder, "solved.jsonl")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("type") == "example" and "value" in rec:
                out.setdefault(int(rec["job"]), {}).setdefault(int(rec["index"]), rec)
    return {j: [by[i] for i in sorted(by)] for j, by in sorted(out.items())}


def read_leaves(folder):
    """{leaf job: its description} from the folder's leaves.json ({} when it is missing)."""
    path = os.path.join(folder, "leaves.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {int(l["job"]): l for l in json.load(f).get("leaves", [])}


def count_inputs(folder):
    path = os.path.join(folder, "inputs.jsonl")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def game_key(config):
    """A game's identity whatever it was solved under: its config without the realization and the net's name."""
    return json.dumps({k: v for k, v in (config or {}).items() if k not in ("realization", "leaf_net")}, sort_keys=True)


def train_job_numbers(game_index):
    """Job numbers for one training game's leaves: its block's numbers that fall in the training split."""
    j = TRAIN_BASE + game_index * PER_GAME
    while True:
        if split_of(j) == "train":
            yield j
        j += 1


def write_job_file(path, header, records):
    """One gzip job file; no timestamp inside, so packing the same solves again gives the same bytes
    (and prepare.py's price cache, keyed by the file's hash, still applies)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        for rec in [header] + records:
            gz.write((json.dumps(rec, separators=(",", ":")) + "\n").encode())


def cmd_pack(args):
    root = os.path.abspath(args.root)
    with open(args.manifest or os.path.join(root, "manifest.json"), encoding="utf-8") as f:
        games = json.load(f)["games"]
    ids = [g["id"] for g in games]
    if len(set(ids)) != len(ids):
        sys.exit("manifest: game ids repeat")
    if os.path.exists(args.out) and os.listdir(args.out):
        sys.exit(f"{args.out} exists and is not empty: a pack is written once (snapshots point at its files)")
    held_keys = {game_key(g.get("config")): g["id"] for g in games if g.get("held_out")}
    for g in games:
        twin = held_keys.get(game_key(g.get("config")))
        if not g.get("held_out") and twin is not None and g.get("config"):
            sys.exit(f"training game {g['id']} is held-out game {twin} under another realization: "
                     "a held-out game must not be trained on in any form")
    held_dir = os.path.join(args.out, args.held_name)
    held_records, held_leaves, summary, exploit = [], [], [], []
    for gi, g in enumerate(games):
        folder = g["folder"] if os.path.isabs(g["folder"]) else os.path.join(root, g["folder"])
        solved, leaves, asked = read_solved(folder), read_leaves(folder), count_inputs(folder)
        n = sum(len(v) for v in solved.values())
        row = {"id": g["id"], "held_out": bool(g.get("held_out")), "source": g.get("source"),
               "leaves": len(solved), "examples": n, "inputs": asked}
        summary.append(row)
        if not solved:
            log(f"{g['id']}: no solved examples in {folder}: skipped")
            continue
        if asked is not None and n < asked:
            log(f"{g['id']}: {n} of {asked} examples solved so far: packing what is there")
        exploit += [float(r.get("exploit_pct_pot", 0.0)) for recs in solved.values() for r in recs]
        numbers = train_job_numbers(gi)
        first = None
        for rank, (leaf, recs) in enumerate(solved.items()):
            job = HELD_BASE + gi * PER_GAME + rank if g.get("held_out") else next(numbers)
            first = job if first is None else first
            recs = [dict(r, job=job) for r in recs]
            if g.get("held_out"):
                held_records += recs
                held_leaves.append(dict(leaves.get(leaf, {}), job=job, game=g["id"], source=g.get("source"), leaf_job=leaf))
            else:
                header = {"type": "header", "format": "gtopen-real-range", "generator_version": REAL_GENERATOR,
                          "job": job, "game": g["id"], "source": g.get("source"), "leaf_job": leaf, "examples": len(recs)}
                write_job_file(os.path.join(args.out, "train", g["id"], f"job-{job}.jsonl.gz"), header, recs)
        row["jobs"] = [first, job]
    if held_records:
        os.makedirs(held_dir, exist_ok=True)
        with open(os.path.join(held_dir, "solved.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            for r in held_records:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
        with open(os.path.join(held_dir, "leaves.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"games": [g["id"] for g in games if g.get("held_out")], "leaves": held_leaves}, f, indent=1)
    tr = [s for s in summary if not s["held_out"] and s["examples"]]
    he = [s for s in summary if s["held_out"] and s["examples"]]
    ex = np.array(exploit or [0.0])
    pack = {"created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "root": root,
            "generator_version": REAL_GENERATOR, "held_name": args.held_name,
            "train": {"games": len(tr), "leaves": sum(s["leaves"] for s in tr), "examples": sum(s["examples"] for s in tr)},
            "held_out": {"games": len(he), "leaves": sum(s["leaves"] for s in he), "examples": sum(s["examples"] for s in he)},
            "exploit_pct_pot": {"median": float(np.median(ex)), "p90": float(np.percentile(ex, 90)), "max": float(ex.max())},
            "games": summary}
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "pack.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(pack, f, indent=1)
    log(f"training: {pack['train']['examples']:,} examples, {pack['train']['leaves']:,} leaves, {len(tr)} games "
        f"-> {os.path.join(args.out, 'train')}")
    log(f"held out: {pack['held_out']['examples']:,} examples, {pack['held_out']['leaves']:,} leaves, {len(he)} games "
        f"-> {held_dir}")
    log(f"exploitability of the flop solves, % of pot: median {pack['exploit_pct_pot']['median']:.2f}, "
        f"90th percentile {pack['exploit_pct_pot']['p90']:.2f}, max {pack['exploit_pct_pot']['max']:.2f}")
    return pack


# --------------------------------------------------------------- compare ----

N_COLS = 6 + 2 * len(POT_TYPES)


def set_sums(es, pred):
    """Per job: gonogo.per_job_sums' four columns (class error sum, weight, range error sum, count), then
    for the shortfall the summed (predicted - solved) total of both players' range values and the examples
    counted, overall and for each pot type."""
    base = es.sums(pred)
    live = (es.reach * es.mask).sum(axis=2) > 0
    both = live.all(axis=1)
    d = np.where(both, (range_values(pred, es.reach, es.mask) - range_values(es.y, es.reach, es.mask)).sum(axis=1), 0.0)
    order = np.argsort(es.jobs, kind="stable")
    jobs, start = np.unique(es.jobs[order], return_index=True)
    out = {}
    for j, rows in zip(jobs, np.split(order, start[1:])):
        cols = [d[rows].sum(), both[rows].sum()]
        for t in range(len(POT_TYPES)):
            sel = rows[es.pot_type[rows] == t]
            cols += [d[sel].sum(), both[sel].sum()]
        out[int(j)] = np.concatenate([base[int(j)], cols])
    return out


def stats(S):
    """(class error, range error, total shortfall % of pot, [shortfall per pot type or nan]) of summed columns."""
    pct = lambda k: 100.0 * S[k] / S[k + 1] if S[k + 1] > 0 else float("nan")
    return S[0] / max(S[1], 1e-12), S[2] / max(S[3], 1.0), pct(4), [pct(6 + 2 * t) for t in range(len(POT_TYPES))]


def resample(tables, reps=REPS, seed=0):
    """Bootstrap over jobs, the same resamples for every arm: {arm: (reps, 3)} of class, range, shortfall."""
    keys = sorted(next(iter(tables.values())))
    mats = {a: np.array([t[k] for k in keys]) for a, t in tables.items()}
    r = np.random.default_rng(seed)
    out = {a: np.zeros((reps, 3)) for a in tables}
    for i in range(reps):
        idx = r.integers(0, len(keys), len(keys))
        for a, m in mats.items():
            out[a][i] = stats(m[idx].sum(axis=0))[:3]
    return out


def resolve_net(work, spec):
    """A net file from a path to one, a run folder, or a run id under WORK/runs/<any snapshot>/."""
    if os.path.isfile(spec):
        return spec
    if os.path.isfile(os.path.join(spec, "leaf_net.bin")):
        return os.path.join(spec, "leaf_net.bin")
    found = sorted(glob.glob(os.path.join(work, "runs", "*", spec, "leaf_net.bin")))
    if len(found) != 1:
        sys.exit(f"{spec}: " + ("no such net file, run folder or run id" if not found else f"run id in several snapshots: {found}"))
    return found[0]


def parse_arms(work, specs):
    arms = {}
    for spec in specs:
        name, eq, nets = spec.partition("=")
        if not eq or not nets or name in arms or name == "balanced":
            sys.exit(f"--arm {spec}: use NAME=NET[,NET...] with a new name per arm")
        arms[name] = [resolve_net(work, s) for s in nets.split(",")]
    return arms


def leaf_games(sdir, set_name):
    """{job: game id} when the set's leaves.json names each leaf's game (a packed held-out set)."""
    path = os.path.join(sdir, "leaf", set_name[5:], "leaves.json") if set_name.startswith("leaf:") else ""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {int(l["job"]): l["game"] for l in json.load(f).get("leaves", []) if "game" in l}


def compare(work, snapshot, arms, ensemble=False, reps=REPS):
    """{set: {"examples", "jobs", "arms": {arm: {...}}, "games": {game: {arm: {...}}}}}; the first entry of
    "arms" is the balanced model (no net), for scale."""
    import harness
    sdir, sets = harness.scoring_sets(work, snapshot)
    members = {a: [leafnet_io.read_members(p)[1] for p in paths] for a, paths in arms.items()}
    first = next(iter(arms))
    report = {}
    for name, es in sets.items():
        tables = {"balanced": set_sums(es, es.base["balanced"])}
        for a, nets in members.items():
            preds = [es.base["balanced"] + leafnet_io.forward_members(m, es.x).reshape(es.n, 2, NC) for m in nets]
            if ensemble:
                preds = [np.mean(preds, axis=0)]
            per = [set_sums(es, p) for p in preds]
            tables[a] = {k: np.mean([t[k] for t in per], axis=0) for k in per[0]}
        boot = resample(tables, reps)
        q = lambda x: [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]
        entry = {"examples": int(es.n), "jobs": len(tables["balanced"]), "arms": {}, "games": {}}
        for a, t in tables.items():
            c, r, s, by = stats(np.array(list(t.values())).sum(axis=0))
            row = {"nets": len(arms.get(a, [])), "class_error": float(c), "range_error": float(r), "total_pct": float(s),
                   "total_pct_ci": q(boot[a][:, 2]), "total_pct_by_type": dict(zip(POT_TYPES, map(float, by)))}
            if a not in ("balanced", first):
                # differences against the first arm, on the same resamples: below zero = this arm's error is lower
                row["vs_first"] = {"class_error": float(c - entry["arms"][first]["class_error"]),
                                   "class_error_ci": q(boot[a][:, 0] - boot[first][:, 0]),
                                   "range_error": float(r - entry["arms"][first]["range_error"]),
                                   "range_error_ci": q(boot[a][:, 1] - boot[first][:, 1]),
                                   "total_pct": float(s - entry["arms"][first]["total_pct"]),
                                   "total_pct_ci": q(boot[a][:, 2] - boot[first][:, 2])}
            entry["arms"][a] = row
        games = leaf_games(sdir, name)
        for g in sorted(set(games.values())):
            entry["games"][g] = {}
            for a, t in tables.items():
                rows = [v for k, v in t.items() if games.get(k) == g]
                c, r, s, _ = stats(np.array(rows).sum(axis=0))
                entry["games"][g][a] = {"leaves": len(rows), "class_error": float(c), "range_error": float(r), "total_pct": float(s)}
        report[name] = entry
    return report


def markdown(snapshot, arms, report, ensemble):
    first = next(iter(arms))
    f2 = lambda x: "" if x != x else f"{x:+.2f}"
    lines = [f"# Nets compared on {snapshot}", "",
             "Arms: " + "; ".join(f"**{a}** ({len(p)} net{'s' if len(p) != 1 else ''}"
                                  + (", scored as their mean output" if ensemble and len(p) > 1 else "") + ")"
                                  for a, p in arms.items()) + ".",
             "Class and range error are the harness's (lower is better). Total = both players' predicted range "
             "values minus the exact solve's, % of the pot: zero is right, negative undervalues the ranges. "
             "Intervals are 95%, resampling whole leaves.", ""]
    for name, e in report.items():
        lines += [f"## {name} ({e['examples']:,} examples, {e['jobs']:,} leaves)", "",
                  "| Arm | Class error | Range error | Total | " + " | ".join(POT_TYPES) + " |",
                  "| --- | ---: | ---: | ---: | " + " | ".join("---:" for _ in POT_TYPES) + " |"]
        for a, r in e["arms"].items():
            label = "balanced model" if a == "balanced" else f"**{a}**"
            lines.append(f"| {label} | {r['class_error']:.6f} | {r['range_error']:.6f} | "
                         f"{r['total_pct']:+.2f} [{r['total_pct_ci'][0]:+.2f}, {r['total_pct_ci'][1]:+.2f}] | "
                         + " | ".join(f2(r["total_pct_by_type"][t]) for t in POT_TYPES) + " |")
        lines.append("")
        for a, r in e["arms"].items():
            v = r.get("vs_first")
            if v:
                lines.append(f"{a} minus {first}: class error {v['class_error']:+.6f} "
                             f"[{v['class_error_ci'][0]:+.6f}, {v['class_error_ci'][1]:+.6f}], range error "
                             f"{v['range_error']:+.6f} [{v['range_error_ci'][0]:+.6f}, {v['range_error_ci'][1]:+.6f}], "
                             f"total {v['total_pct']:+.2f} [{v['total_pct_ci'][0]:+.2f}, {v['total_pct_ci'][1]:+.2f}].")
        if e["games"]:
            names = list(e["arms"])
            lines += ["", "| Game | Leaves | " + " | ".join(f"{a}: class, total" for a in names) + " |",
                      "| --- | ---: | " + " | ".join("---:" for _ in names) + " |"]
            for g, per in e["games"].items():
                lines.append(f"| {g} | {per[names[0]]['leaves']} | "
                             + " | ".join(f"{per[a]['class_error']:.5f}, {per[a]['total_pct']:+.2f}" for a in names) + " |")
        lines.append("")
    return "\n".join(lines)


def cmd_compare(args):
    import harness
    snapshot = args.snapshot or harness.current_snapshot(args.work)
    arms = parse_arms(args.work, args.arm)
    report = compare(args.work, snapshot, arms, args.ensemble, args.reps)
    text = markdown(snapshot, arms, report, args.ensemble)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        with open(os.path.splitext(args.out)[0] + ".json", "w", encoding="utf-8", newline="\n") as f:
            json.dump({"snapshot": snapshot, "arms": arms, "ensemble": args.ensemble, "sets": report}, f, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pack", help="solved game folders -> training job files and a held-out check set")
    p.add_argument("root", help="the folder with manifest.json and the games' folders")
    p.add_argument("--out", required=True, help="a new folder for the pack")
    p.add_argument("--manifest", help="the manifest (default: ROOT/manifest.json)")
    p.add_argument("--held-name", default="realrange-heldout", help="the held-out check set's name")
    p.set_defaults(fn=cmd_pack)
    c = sub.add_parser("compare", help="score groups of nets on a snapshot's scoring sets")
    c.add_argument("--arm", action="append", required=True, metavar="NAME=NET[,NET...]",
                   help="one recipe's nets (run ids, run folders or net files); the first arm is the reference")
    c.add_argument("--snapshot", help="whose scoring sets (default: the current snapshot)")
    c.add_argument("--work", default=work_dir())
    c.add_argument("--ensemble", action="store_true", help="score each arm as the mean of its nets' outputs")
    c.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples")
    c.add_argument("--out", help="also write the report here (.md) and its numbers next to it (.json)")
    c.set_defaults(fn=cmd_compare)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
