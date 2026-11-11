#!/usr/bin/env python3
"""Freeze a leaf-net training snapshot (part of the frozen harness: the
autoresearch agent never edits this file).

    python tools/leafnet/prepare.py                      # download/refresh the dataset, freeze it
    python tools/leafnet/prepare.py --data DIR           # freeze local job files instead
    python tools/leafnet/prepare.py --leafcheck datagen_leafcheck_v2   # also add a real-leaf test set
    python tools/leafnet/prepare.py --files-from SNAP --extra DIR      # SNAP's job files plus more (real ranges)

A snapshot is the sorted list of job files plus a SHA-256 manifest, so a run
can always say exactly which data it saw. Every example is priced once with
the Preflop Lab's realization models (`solve-cli datagen baseline`); prices
are cached per job file (keyed by the file's hash), so refreezing a bigger
dataset only prices the new jobs. Splits come from gonogo.split_of, so the
held-out jobs are the go/no-go's: hash 0 = test, 1 = validation, the rest
train. Real-leaf sets (`--leafcheck DIR`, a `datagen leaves` + `datagen
solve` folder) are priced the same way and kept as test sets: they are
never trained on.

More training data (`--extra DIR`, repeatable): job files from outside the
pool, added after the pool's. `realrange.py pack` writes exact solves of real
preflop ranges that way, one file per leaf, marked generator version 100
(REAL_GENERATOR), with job numbers that land in the training split, so the
validation and test jobs stay the pool's. `--files-from SNAP` takes exactly
the pool files SNAP lists (hashes checked) instead of everything downloaded
since, so two snapshots that differ only in their extra files have the same
validation and test examples in the same rows.

Writes WORK/snapshots/<name>/ with:
    manifest.json   files, hashes, counts, split sizes, solve-cli used
    x.npy           features (n, 686), the layout of leafnet_io.FEATURES and
                    LeafNet::features: range oop/ip, balanced oop/ip, 10 meta
    y.npy           solved values (n, 2, 169); mask.npy where they exist
    reach.npy       combo mass per class (n, 2, 169)
    w.npy           class weights (n, 2, 169) as gonogo: reach share x 169 x mask
    base_<model>.npy  realization-model values (n, 2, 169)
    jobs.npy, split.npy (0 train, 1 val, 2 test), pot_type.npy (0..3),
    pot_scale.npy, generator.npy
    inputs_val.jsonl  the validation examples' inputs (for the export parity check)
    leaf/<set>/...  the same arrays for each real-leaf set, plus inputs.jsonl and leaves.json

WORK defaults to $LEAFNET_WORK, else <repo>/leafnet_work (gitignored).
"""

import argparse
import datetime
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "datagen"))

import numpy as np  # noqa: E402

from gonogo import INPUT_KEYS, MODELS, NC, arrays, features, job_files, split_of  # noqa: E402
from validate import cuda_env, default_cli, load_config  # noqa: E402

POT_TYPES = ["limped", "srp", "3bet", "4bet"]
SPLIT_CODE = {"train": 0, "val": 1, "test": 2}
REAL_GENERATOR = 100    # generator.npy for exact solves of real preflop ranges (realrange.py pack); the pool's are 1..3


def work_dir():
    return os.environ.get("LEAFNET_WORK") or os.path.join(ROOT, "leafnet_work")


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_file(path):
    """(header, [example records]) of one job file (.jsonl or .jsonl.gz)."""
    opener = gzip.open if path.endswith(".gz") else open
    header, recs = None, []
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            kind = rec.get("type")
            if kind == "header":
                header = rec
            elif kind == "example":
                recs.append(rec)
    return header or {}, recs


def price(cli, records, chunk=4000):
    """{model: (n, 2, 169)} from `solve-cli datagen baseline`, in input order."""
    out = {m: [] for m in MODELS}
    for i in range(0, len(records), chunk):
        part = records[i:i + chunk]
        text = "\n".join(json.dumps({k: r[k] for k in INPUT_KEYS}) for r in part) + "\n"
        proc = subprocess.run([cli, "datagen", "baseline"], input=text, capture_output=True, text=True,
                              cwd=ROOT, env=cuda_env())
        got = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
        if proc.returncode != 0 or len(got) != len(part):
            sys.exit(f"solve-cli datagen baseline failed: {proc.stderr.strip()[-600:]}")
        for r, g in zip(part, got):
            if (int(g["job"]), int(g["index"])) != (int(r["job"]), int(r["index"])):
                sys.exit("solve-cli datagen baseline returned examples out of order")
            for m in MODELS:
                out[m].append(g["models"][m])
    return {m: np.asarray(v, dtype=np.float32).reshape(len(records), 2, NC) for m, v in out.items()}


def priced_files(cli, paths, cache_dir):
    """Read and price job files, using and filling the per-file price cache.
    Returns (records, headers per record, {model: (n, 2, 169)}, manifest rows)."""
    os.makedirs(cache_dir, exist_ok=True)
    rows, todo, loaded = [], [], {}
    for p in paths:
        digest = sha256(p)
        rows.append({"file": p, "sha256": digest, "bytes": os.path.getsize(p)})
        cached = os.path.join(cache_dir, digest + ".npz")
        if not os.path.exists(cached):
            todo.append((p, digest))
    log(f"{len(paths)} job files, {len(paths) - len(todo)} already priced, {len(todo)} to price")
    batch, batch_files = [], []

    def flush():
        if not batch:
            return
        vals = price(cli, batch)
        pos = 0
        for p, digest, n in batch_files:
            np.savez(os.path.join(cache_dir, digest + ".npz"), **{m: vals[m][pos:pos + n] for m in MODELS})
            pos += n
        batch.clear()
        batch_files.clear()

    for k, (p, digest) in enumerate(todo, 1):
        _, recs = read_file(p)
        batch.extend(recs)
        batch_files.append((p, digest, len(recs)))
        if len(batch) >= 4000:
            flush()
            log(f"   priced {k} of {len(todo)} files")
    flush()
    records, headers, base = [], [], {m: [] for m in MODELS}
    for row in rows:
        header, recs = read_file(row["file"])
        with np.load(os.path.join(cache_dir, row["sha256"] + ".npz")) as z:
            if len(z[MODELS[0]]) != len(recs):
                sys.exit(f"price cache for {row['file']} does not match its examples; delete {cache_dir}")
            for m in MODELS:
                base[m].append(z[m])
        records.extend(recs)
        headers.extend([header] * len(recs))
        row["examples"] = len(recs)
        row["generator_version"] = header.get("generator_version")
    base = {m: (np.concatenate(v) if v else np.zeros((0, 2, NC), np.float32)) for m, v in base.items()}
    return records, headers, base, rows


def save_arrays(out, records, headers, base, split=None):
    os.makedirs(out, exist_ok=True)
    rng, meta, y, mask, reach, w = arrays(records)
    n = len(records)
    np.save(os.path.join(out, "x.npy"), features(rng, meta, base["balanced"]))
    np.save(os.path.join(out, "y.npy"), y)
    np.save(os.path.join(out, "mask.npy"), mask)
    np.save(os.path.join(out, "reach.npy"), reach)
    np.save(os.path.join(out, "w.npy"), w)
    for m in MODELS:
        np.save(os.path.join(out, f"base_{m}.npy"), base[m])
    jobs = np.array([int(r["job"]) for r in records], dtype=np.int64)
    np.save(os.path.join(out, "jobs.npy"), jobs)
    np.save(os.path.join(out, "pot_type.npy"), np.array([POT_TYPES.index(r["pot_type"]) for r in records], np.int8))
    np.save(os.path.join(out, "pot_scale.npy"), np.array([float(r.get("pot_scale", 1.0)) for r in records], np.float32))
    np.save(os.path.join(out, "generator.npy"), np.array([int(h.get("generator_version", 0)) for h in headers], np.int8))
    if split is None:
        split = np.array([SPLIT_CODE[split_of(int(j))] for j in jobs], dtype=np.int8)
    np.save(os.path.join(out, "split.npy"), split)
    return jobs, split


def write_inputs(path, records):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps({k: r[k] for k in INPUT_KEYS}) + "\n")


def add_leafcheck(cli, snap, cache_dir, folder):
    name = os.path.basename(os.path.normpath(folder))
    solved = os.path.join(folder, "solved.jsonl")
    if not os.path.exists(solved):
        sys.exit(f"{solved} not found: run solve-cli datagen solve {folder} first")
    records = []
    with open(solved, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                if rec.get("type") == "example":
                    records.append(rec)
    digest = sha256(solved)
    cached = os.path.join(cache_dir, "leaf-" + digest + ".npz")
    if os.path.exists(cached):
        with np.load(cached) as z:
            base = {m: z[m] for m in MODELS}
    else:
        log(f"pricing {len(records)} real-leaf flops from {folder}")
        base = price(cli, records)
        np.savez(cached, **base)
    out = os.path.join(snap, "leaf", name)
    split = np.full(len(records), 3, dtype=np.int8)  # 3 = real-leaf test set
    jobs, _ = save_arrays(out, records, [{}] * len(records), base, split)
    write_inputs(os.path.join(out, "inputs.jsonl"), records)
    if os.path.exists(os.path.join(folder, "leaves.json")):
        shutil.copy(os.path.join(folder, "leaves.json"), os.path.join(out, "leaves.json"))
    log(f"real-leaf set {name}: {len(records)} flops from {len(set(jobs.tolist()))} leaves")
    return {"name": name, "folder": os.path.abspath(folder), "solved_sha256": digest, "flops": len(records),
            "leaves": len(set(jobs.tolist()))}


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", help="local folder of job files (default: download the dataset into WORK/dataset)")
    ap.add_argument("--files-from", metavar="SNAPSHOT",
                    help="take exactly the job files that snapshot lists (its folder unless --data; hashes checked), "
                         "not everything in the folder")
    ap.add_argument("--extra", action="append", default=[], metavar="DIR",
                    help="more job files to add after those (a `realrange.py pack` folder's train/); repeatable")
    ap.add_argument("--repo", default=cfg["hf_repo"])
    ap.add_argument("--name", help="snapshot name (default: snap-<examples>-<date>)")
    ap.add_argument("--leafcheck", action="append", default=[], help="real-leaf folder(s) to add as test sets")
    ap.add_argument("--side", action="store_true",
                    help="an experiment's snapshot: do not make it the current one (runs name it with --snapshot)")
    ap.add_argument("--solve-cli", default=default_cli())
    ap.add_argument("--work", default=work_dir())
    ap.add_argument("--attach", action="store_true",
                    help="add --leafcheck set(s) to the existing snapshot --name (test sets only; training data stays frozen)")
    args = ap.parse_args()
    if not os.path.exists(args.solve_cli):
        sys.exit(f"{args.solve_cli} not found: cargo build --release -p solver --features gpu --bin solve-cli")
    cache_dir = os.path.join(args.work, "price_cache")
    if args.attach:
        if not args.name or not args.leafcheck:
            sys.exit("--attach needs --name SNAPSHOT and at least one --leafcheck DIR")
        snap = os.path.join(args.work, "snapshots", args.name)
        mpath = os.path.join(snap, "manifest.json")
        with open(mpath, encoding="utf-8") as f:
            manifest = json.load(f)
        have = {s["name"] for s in manifest.get("leaf_sets", [])}
        for d in args.leafcheck:
            if os.path.basename(os.path.normpath(d)) in have:
                sys.exit(f"{d} is already attached to {args.name}")
            manifest.setdefault("leaf_sets", []).append(add_leafcheck(args.solve_cli, snap, cache_dir, d))
        with open(mpath, "w", encoding="utf-8", newline="\n") as f:
            json.dump(manifest, f, indent=1)
        return

    expect = {}
    if args.files_from:
        with open(os.path.join(args.work, "snapshots", args.files_from, "manifest.json"), encoding="utf-8") as f:
            prev = json.load(f)
        folder = args.data or prev["source"]
        listed = [fm for fm in prev["files_manifest"] if not fm.get("extra")]
        paths = [os.path.join(folder, fm["file"]) for fm in listed]
        expect = {p: fm["sha256"] for p, fm in zip(paths, listed)}
        gone = [p for p in paths if not os.path.exists(p)]
        if gone:
            sys.exit(f"{len(gone)} of {args.files_from}'s {len(paths)} job files are not in {folder} (first: {gone[0]})")
    else:
        if args.data:
            folder = args.data
        else:
            from huggingface_hub import snapshot_download
            dest = os.path.join(args.work, "dataset")
            log(f"refreshing {args.repo} in {dest}")
            snapshot_download(args.repo, repo_type="dataset", allow_patterns=["data/*/*.jsonl.gz"], local_dir=dest)
            folder = os.path.join(dest, "data")
        paths = job_files(folder)
    if not paths:
        sys.exit(f"no job files in {folder}")
    extra = []
    for d in args.extra:
        found = [os.path.abspath(p) for p in job_files(d)]
        if not found:
            sys.exit(f"no job files in {d}")
        extra += found
    if set(extra) & {os.path.abspath(p) for p in paths}:
        sys.exit("--extra repeats job files of the main folder")
    n_main = len(paths)
    paths = paths + extra
    records, headers, base, rows = priced_files(args.solve_cli, paths, cache_dir)
    changed = [r["file"] for r in rows if expect.get(r["file"], r["sha256"]) != r["sha256"]]
    if changed:
        sys.exit(f"{len(changed)} job files differ from the ones {args.files_from} froze (first: {changed[0]})")
    for k, r in enumerate(rows):
        r["extra"] = k >= n_main
    n = len(records)
    extra_row = np.repeat([r["extra"] for r in rows], [r["examples"] for r in rows]).astype(bool)
    all_jobs = np.array([int(r["job"]) for r in records], dtype=np.int64)
    shared = sorted(set(all_jobs[extra_row].tolist()) & set(all_jobs[~extra_row].tolist()))
    if shared:
        sys.exit(f"--extra job numbers repeat the main folder's (first: {shared[0]}): splits and scores are per job")
    stray = sorted({int(j) for j in all_jobs[extra_row].tolist() if split_of(int(j)) != "train"})
    if stray:
        sys.exit(f"{len(stray)} --extra jobs fall in the validation or test split (first: {stray[0]}): "
                 "extra files are training data only, so the held-out examples stay the main folder's")
    name = args.name or f"snap-{n // 1000}k-{datetime.date.today().isoformat()}"
    snap = os.path.join(args.work, "snapshots", name)
    if os.path.exists(snap):
        sys.exit(f"{snap} exists: snapshots are frozen; pick another --name")
    jobs, split = save_arrays(snap, records, headers, base)
    val_records = [r for r, s in zip(records, split) if s == SPLIT_CODE["val"]]
    write_inputs(os.path.join(snap, "inputs_val.jsonl"), val_records)
    leafsets = [add_leafcheck(args.solve_cli, snap, cache_dir, d) for d in args.leafcheck]

    # a file's name in the manifest: relative to the main folder, or its full path for an --extra file
    # (flops.load_side joins it to "source", and a full path stands on its own)
    listed_as = lambda r: r["file"] if r["extra"] else os.path.relpath(r["file"], folder)
    hashed_as = lambda r: "extra:" + os.path.basename(r["file"]) if r["extra"] else os.path.relpath(r["file"], folder)
    manifest_lines = "\n".join(f"{hashed_as(r)} {r['sha256']}" for r in rows)
    counts = {s: int((split == c).sum()) for s, c in SPLIT_CODE.items()}
    job_counts = {s: len(set(jobs[split == c].tolist())) for s, c in SPLIT_CODE.items()}
    manifest = {
        "name": name, "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": os.path.abspath(folder), "examples": n, "files": len(rows),
        "snapshot_sha256": hashlib.sha256(manifest_lines.encode()).hexdigest(),
        "examples_by_split": counts, "jobs_by_split": job_counts,
        "generator_versions": {str(v): int((np.array([r.get("generator_version") or 0 for r in rows]) == v).sum())
                               for v in sorted({r.get("generator_version") or 0 for r in rows})},
        "solve_cli": os.path.abspath(args.solve_cli), "leaf_sets": leafsets,
        "files_manifest": [{"file": listed_as(r), "sha256": r["sha256"], "examples": r["examples"],
                            "generator_version": r.get("generator_version"), **({"extra": True} if r["extra"] else {})}
                           for r in rows],
    }
    if args.files_from:
        manifest["files_from"] = args.files_from
    if extra:
        manifest["extra_sources"] = [os.path.abspath(d) for d in args.extra]
        manifest["extra_examples_by_split"] = {s: int((extra_row & (split == c)).sum()) for s, c in SPLIT_CODE.items()}
    with open(os.path.join(snap, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1)
    log(f"snapshot {name}: {n:,} examples from {len(rows)} files; "
        f"train {counts['train']:,} / val {counts['val']:,} ({job_counts['val']} jobs) / test {counts['test']:,} "
        f"({job_counts['test']} jobs); {len(leafsets)} real-leaf set(s) -> {snap}")
    if extra:
        by = manifest["extra_examples_by_split"]
        log(f"   of those, {int(extra_row.sum()):,} examples from {len(extra)} --extra files: "
            f"train {by['train']:,} / val {by['val']:,} / test {by['test']:,}")
    if args.side:
        log("--side: CURRENT_SNAPSHOT is unchanged; pass --snapshot " + name + " to train.py and harness.py")
        return
    with open(os.path.join(args.work, "CURRENT_SNAPSHOT"), "w", encoding="utf-8") as f:
        f.write(name + "\n")


if __name__ == "__main__":
    main()
