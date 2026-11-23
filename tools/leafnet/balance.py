#!/usr/bin/env python3
"""Weigh a snapshot's pool rows so that each game mix counts as it was meant to,
whatever cards the contributors had.

    python tools/leafnet/balance.py SNAPSHOT          # writes snapshots/SNAPSHOT/balance.npy and balance.json
    python tools/leafnet/balance.py SNAPSHOT --clip 8

Why. A contributor's card only solves flop trees that fit its memory: the
generator draws an example from the job's game mix and, when the tree is over
the card's cap (`max_vram_gb` in the job header), draws again
(`datagen::capped`). From generator v6 a mix can also have big cards pass over
most small trees (`datagen_mix::CardRule`). Either way, what one card solves
is the mix's games tilted by size, and the pool is a blend of such tilts in
the proportions the cards happened to contribute. With many small cards it
leans towards small trees (short stacks, 3-bet and 4-bet pots), and the big
ones rest on the few big cards.

The weights undo the tilt. For an example x of a mix, a card c takes it with
probability a_c(x) / Z_c relative to the mix itself, where a_c(x) is 1 if
the card takes a tree of that size, `keep` if a card rule makes it pass over
most such trees, 0 if the tree is over its cap; Z_c is the share of the mix's
draws the card takes, estimated from the examples' draw counts (`attempt`:
the draws passed over before the one taken, so Z_c = examples / total draws).
The pool's rows of that mix come from the cards in proportion f_c to their
examples, so a row's weight is the mix's density over the pool's:

    w(x) = 1 / sum_c f_c * a_c(x) / Z_c

(the "balance heuristic" of multiple importance sampling). A tree only big
cards take gets the weight that makes their share of it count for everyone; a
tree every card takes gets less than 1. A tree no card in the pool takes
cannot be made up for and is simply missing: the report says how many of the
mix's draws that is likely to be (the smallest cards' passed draws).

Each mix keeps its total: weights are scaled to average 1 within a mix, so
the mixes stay in the proportions the pool solved them (a change of mix is a
choice, not a tilt). Rows that are not pool examples (`prepare.py --extra`
files) get 1. Weights are clipped at --clip times the average and scaled
again, so a handful of rows cannot dominate the loss; the report gives the
effective number of rows (sum w)^2 / sum w^2 per mix.

Tree sizes: an example of generator v6 on records its own (`tree_bytes`);
for older ones `solve-cli datagen tree-sizes` builds each tree to count it
(no solve; about a fifth of a second of one core per example, all cores used).
Sizes are cached per job file in WORK/size_cache/<sha256>.npy like
prepare.py's prices, so a bigger snapshot only sizes its new files.

train.py uses balance.npy when CONFIG["balance"] is True (off by default): it
multiplies the training rows' loss weight. Nothing else reads it.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "datagen"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from prepare import read_file, sha256, work_dir  # noqa: E402

MIXES = os.path.join(ROOT, "tools", "datagen", "mixes.json")
MIX_SHIFT = 44
LAST_CODED_GENERATOR = 4
SIZE_BANDS = ((0, 6), (6, 12), (12, 19), (19, None))   # GB, as the validator counts them


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def load_rules(path=MIXES):
    """{mix id: [card rules, ascending cap_from_gb]} from the published list of mixes (never edited, so the
    repository's copy holds every mix's rules)."""
    with open(path, encoding="utf-8") as f:
        mixes = json.load(f)["mixes"]
    return {int(m["id"]): sorted(m.get("card_rules") or [], key=lambda r: r["cap_from_gb"]) for m in mixes}


def rule_for(rules, cap):
    """The card rule a card with memory cap `cap` (None: no cap) follows, as datagen_mix::Mix::rule_for."""
    for r in reversed(rules):
        if cap is None or cap >= r["cap_from_gb"]:
            return r
    return None


def accept(size_bytes, cap, rule):
    """a_c(x): how likely a card with cap `cap` and card rule `rule` is to take a draw of this tree size."""
    size = np.asarray(size_bytes, np.float64)
    a = np.ones_like(size)
    if cap is not None:
        a[size > cap * 1e9] = 0.0
    if rule is not None:
        a[(size < rule["under_gb"] * 1e9) & (a > 0)] = rule["keep"]
    return a


def mix_of(header):
    """Which mix a pooled job was drawn from: ("generator", v) up to v4, whose mix was written in code,
    ("mix", id) from v5."""
    gen = int(header.get("generator_version") or 0)
    if gen <= LAST_CODED_GENERATOR:
        return ("generator", gen)
    mix = header.get("mix")
    if mix is None:
        mix = int(header["job"]) >> MIX_SHIFT
    return ("mix", int(mix))


def weights(groups, sizes, attempts, rules_of, clip=10.0):
    """Row weights for one snapshot.

    groups: per row, None for a row that is not a pool example, else (mix, cap) with mix as mix_of and cap
    the job's max_vram_gb (None = no cap). sizes: tree bytes per row. attempts: draws passed over per row.
    rules_of(mix): that mix's card rules. Returns (weights, report)."""
    n = len(groups)
    w = np.ones(n, np.float64)
    sizes = np.asarray(sizes, np.float64)
    attempts = np.asarray(attempts, np.float64)
    report = {}
    mixes = sorted({g[0] for g in groups if g is not None}, key=str)
    for mix in mixes:
        rows = np.array([i for i, g in enumerate(groups) if g is not None and g[0] == mix])
        caps = sorted({groups[i][1] for i in rows}, key=lambda c: (c is None, c or 0))
        rules = rules_of(mix)
        denom = np.zeros(len(rows))
        cards = []
        for cap in caps:
            mine = np.array([groups[i][1] == cap for i in rows])
            f = mine.mean()
            z = mine.sum() / (attempts[rows][mine] + 1).sum()    # the share of the mix's draws this card takes
            rule = rule_for(rules, cap)
            denom += f * accept(sizes[rows], cap, rule) / z
            cards.append({"cap_gb": cap, "examples": int(mine.sum()), "share": round(float(f), 4),
                          "draws_taken": round(float(z), 4), "rule": rule})
        raw = np.where(denom > 0, 1.0 / np.maximum(denom, 1e-300), np.nan)
        raw[np.isnan(raw)] = np.nanmax(raw) if np.isfinite(raw).any() else 1.0   # a fallback draw no card takes
        mw = raw / raw.mean()
        clipped = int((mw > clip).sum())
        for _ in range(20):                                     # clip and scale again until it holds
            mw = np.minimum(mw, clip)
            mw /= mw.mean()
            if mw.max() <= clip * (1 + 1e-9):
                break
        w[rows] = mw
        by_band = {}
        for lo, hi in SIZE_BANDS:
            band = (sizes[rows] >= lo * 1e9) & ((sizes[rows] < hi * 1e9) if hi else True)
            name = f"{lo}-{hi}" if hi else f"{lo}+"
            by_band[name] = {"rows": round(float(band.mean()), 4), "weighted": round(float((mw * band).sum() / mw.sum()), 4)}
        report[f"{mix[0]} {mix[1]}"] = {
            "rows": int(len(rows)), "cards": cards, "clipped": clipped,
            "effective_rows": int(round(mw.sum() ** 2 / (mw ** 2).sum())),
            "weight_range": [round(float(mw.min()), 3), round(float(mw.max()), 3)],
            "share_by_size_gb": by_band,
        }
    return w.astype(np.float32), report


def file_sizes(cli, path, cache_dir):
    """Tree bytes of every example of a job file, in file order (cached by the file's SHA-256)."""
    digest = sha256(path)
    cached = os.path.join(cache_dir, digest + ".npy")
    if os.path.exists(cached):
        return np.load(cached)
    plain = path
    if path.endswith(".gz"):
        import gzip
        import tempfile
        fd, plain = tempfile.mkstemp(suffix=".jsonl")
        with gzip.open(path, "rb") as src, os.fdopen(fd, "wb") as dst:
            dst.write(src.read())
    try:
        proc = subprocess.run([cli, "datagen", "tree-sizes", plain], capture_output=True, text=True, cwd=ROOT)
    finally:
        if plain != path:
            os.remove(plain)
    if proc.returncode != 0:
        sys.exit(f"solve-cli datagen tree-sizes {path} failed: {proc.stderr.strip()[-400:]}")
    sizes = np.array([json.loads(l)["tree_bytes"] for l in proc.stdout.splitlines() if l.startswith("{")], np.int64)
    os.makedirs(cache_dir, exist_ok=True)
    np.save(cached, sizes)
    return sizes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("snapshot")
    ap.add_argument("--work", default=work_dir())
    ap.add_argument("--clip", type=float, default=10.0, help="largest weight, as a multiple of a mix's average")
    ap.add_argument("--mixes", default=MIXES, help="the published list of mixes (for card rules)")
    from validate import default_cli
    ap.add_argument("--solve-cli", default=default_cli())
    args = ap.parse_args()
    snap = os.path.join(args.work, "snapshots", args.snapshot)
    with open(os.path.join(snap, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    rules = load_rules(args.mixes)
    groups, sizes, attempts = [], [], []
    files = manifest["files_manifest"]
    for k, fm in enumerate(files, 1):
        path = fm["file"] if os.path.isabs(fm["file"]) else os.path.join(manifest["source"], fm["file"])
        header, recs = read_file(path)
        if fm.get("extra") or header.get("format") != "gtopen-leaf-values":
            groups += [None] * len(recs)                         # not a pooled job: weight 1
            sizes += [0] * len(recs)
            attempts += [0] * len(recs)
            continue
        got = file_sizes(args.solve_cli, path, os.path.join(args.work, "size_cache"))
        if len(got) != len(recs):
            sys.exit(f"{path}: {len(got)} tree sizes for {len(recs)} examples")
        g = (mix_of(header), header.get("max_vram_gb"))
        groups += [g] * len(recs)
        sizes += got.tolist()
        attempts += [int(r.get("attempt") or 0) for r in recs]
        if k % 200 == 0:
            log(f"   sized {k} of {len(files)} files")
    if len(groups) != manifest["examples"]:
        sys.exit(f"{len(groups)} rows read, the snapshot has {manifest['examples']}")
    rules_of = lambda mix: rules.get(mix[1], []) if mix[0] == "mix" else []
    w, report = weights(groups, sizes, attempts, rules_of, args.clip)
    np.save(os.path.join(snap, "balance.npy"), w)
    out = {"snapshot": args.snapshot, "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "clip": args.clip, "mixes": report}
    with open(os.path.join(snap, "balance.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    for name, r in report.items():
        caps = ", ".join(f"{c['cap_gb'] or 'no cap'} GB {c['share']:.0%}" for c in r["cards"])
        big = r["share_by_size_gb"]["19+"]
        log(f"{name}: {r['rows']:,} rows from cards {caps}; trees over 19 GB {big['rows']:.1%} of rows, "
            f"{big['weighted']:.1%} weighted; effective rows {r['effective_rows']:,}; {r['clipped']} clipped")
    log(f"wrote {snap}/balance.npy and balance.json")


if __name__ == "__main__":
    main()
