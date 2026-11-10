#!/usr/bin/env python3
"""Leaf-net scaling law: how validation and real-leaf error fall with net size
and training data.

    python tools/leafnet/scaling.py run  [--trainer tools/leafnet/train.py] [--sizes 1x128,2x512,...]
                                         [--fractions 0.0625,0.125,0.25,0.35,0.5,0.7,1] [--seeds 2]
    python tools/leafnet/scaling.py fit  [--snapshot SNAP] [--min-fraction 0.25]

`run` trains the trainer's recipe (its run() and CONFIG, with "depth" and
"hidden" overridden) at every net size x data fraction x seed on the current
snapshot, scores each net like the harness does, and appends one line per
run to WORK/scaling/<snapshot>/runs.jsonl. Finished points are skipped, so a
stopped grid resumes. Nothing here touches results.tsv, state.json or the
best net: the keep rule is not involved.

Data fractions take whole training jobs, in a fixed hash order, so every
smaller fraction is contained in every larger one (curves are nested, like
a dataset growing). Input normalization stays the full training split's
(input statistics only; no labels). A trainer that reads its own
per-example arrays for the training split must select rows with
`getattr(data, "train_index", None)` (None = all rows).

`fit` fits, for validation class error and for each real-leaf set's class
error, the form used for language-model scaling (Hoffmann et al. 2022):

    error(N, D) = E + A / N^a + B / D^b

with N = parameters, D = training examples, by least squares on the seed
means (exponents by grid search, E, A, B >= 0 linear), using only data
fractions of --min-fraction (0.25) and up. It writes fit.json and scaling.md
with the fitted terms (flagging exponents stuck at the end of the search
range), the fit's miss at full data for every size, a hold-out check (fit
without the full data fraction, predict it), and predictions at the next data
milestones. A prediction is only as good as the full-data miss next to it.
Sizes above the deployment cost cap may be in the grid on purpose: they show
whether the cap is what limits the net.
"""

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import harness  # noqa: E402

DEFAULT_SIZES = "1x128,1x256,2x256,2x512,4x512,4x768,4x1024"
DEFAULT_FRACTIONS = "0.0625,0.125,0.25,0.35,0.5,0.7,1"
# The law is fitted on these fractions of the full data and up: below them the
# recipe (tuned at full data) is erratic and the large errors dominate the fit.
DEFAULT_MIN_FRACTION = 0.25
# Exponent search range (log-spaced). A fitted exponent on either end means the
# data did not pin it down.
EXPONENTS = np.exp(np.linspace(np.log(0.02), np.log(4.0), 200))
# Total validated examples at the next data milestones; the train split is
# the same share of them as in the fitted snapshot.
MILESTONES = [100_000, 150_000, 300_000, 1_000_000]


def params(sizes):
    return sum(a * b + b for a, b in zip(sizes, sizes[1:]))


def parse_sizes(text):
    out = []
    for tok in text.split(","):
        d, w = tok.lower().split("x")
        out.append((int(d), int(w)))
    return out


def job_order(jobs):
    """Training jobs in a fixed pseudo-random order (sha256 of the job id)."""
    return sorted(set(int(j) for j in jobs), key=lambda j: hashlib.sha256(str(j).encode()).hexdigest())


def subset_mask(train_jobs, frac):
    """Mask over training examples: the first ceil(frac x jobs) jobs in job_order (nested in frac)."""
    order = job_order(train_jobs)
    keep = set(order[:max(1, int(np.ceil(frac * len(order))))])
    return np.array([int(j) in keep for j in train_jobs])


# ------------------------------------------------------------------ fit ----

def _nnls3(X, y):
    """Least squares with nonnegative coefficients for <= 3 columns (all subsets)."""
    best = (np.inf, np.zeros(X.shape[1]))
    for k in range(1, X.shape[1] + 1):
        for cols in itertools.combinations(range(X.shape[1]), k):
            c, *_ = np.linalg.lstsq(X[:, cols], y, rcond=None)
            if (c < 0).any():
                continue
            full = np.zeros(X.shape[1])
            full[list(cols)] = c
            sse = float(((X @ full - y) ** 2).sum())
            if sse < best[0]:
                best = (sse, full)
    return best


def fit_law(N, D, err, exps=EXPONENTS):
    """Fit err = E + A N^-a + B D^-b. Returns dict(E, A, a, B, b, rmse, at_edge), at_edge naming the
    exponents that ended on the end of the search range (not pinned down by the data)."""
    N, D, err = (np.asarray(v, dtype=float) for v in (N, D, err))
    # scale N and D so the coefficients are of order one
    n0, d0 = N.max(), D.max()
    best = None
    for a in exps:
        xa = (N / n0) ** -a
        for b in exps:
            X = np.stack([np.ones_like(err), xa, (D / d0) ** -b], axis=1)
            sse, c = _nnls3(X, err)
            if best is None or sse < best[0]:
                best = (sse, c, a, b)
    sse, (E, A, B), a, b = best
    lo, hi = float(np.min(exps)), float(np.max(exps))
    # an exponent whose term is zero is not fitted at all: only flag the ones in use
    edge = [k for k, v, c in (("a", a, A), ("b", b, B)) if c > 0 and (np.isclose(v, lo) or np.isclose(v, hi))]
    return {"E": float(E), "A": float(A * n0 ** a), "a": float(a), "B": float(B * d0 ** b), "b": float(b),
            "rmse": float(np.sqrt(sse / len(err))), "at_edge": edge}


def predict_law(f, N, D):
    return f["E"] + f["A"] * np.asarray(N, float) ** -f["a"] + f["B"] * np.asarray(D, float) ** -f["b"]


def seed_means(rows, key):
    """[(params, train examples, mean error, seeds)] over rows that have `key`."""
    groups = {}
    for r in rows:
        if r.get(key) is None:
            continue
        groups.setdefault((r["params"], r["train_examples"]), []).append(r[key])
    return [(n, d, float(np.mean(v)), len(v)) for (n, d), v in sorted(groups.items())]


def fit_report(rows, manifest, cap_params, min_fraction=DEFAULT_MIN_FRACTION):
    """Fits and checks for every error measure in rows; the law is fitted on points with at least
    min_fraction of the most training examples in rows (all points are still listed)."""
    keys = ["val_class"] + (["val_cv_class"] if any("val_cv_class" in r for r in rows) else []) \
        + sorted({k for r in rows for k in r if k.startswith("leaf_class:")})
    total = manifest["examples"]
    train_share = manifest["examples_by_split"]["train"] / total
    out = {}
    for key in keys:
        pts = seed_means(rows, key)
        if len(pts) < 6:
            continue
        N_all, D_all, err_all, _ = map(np.array, zip(*pts))
        # job fractions give a little more or less than the fraction of examples: allow 10%
        used = D_all >= 0.9 * min_fraction * D_all.max()
        if used.sum() < 6:
            continue
        N, D, err = N_all[used], D_all[used], err_all[used]
        f = fit_law(N, D, err)
        rep = {"fit": f, "min_fraction": min_fraction,
               "points": [{"params": int(n), "train_examples": int(d), "error": e, "seeds": s, "fitted": bool(u)}
                          for (n, d, e, s), u in zip(pts, used)]}
        full = D == D.max()
        rep["full_data"] = [{"params": int(n), "measured": float(e), "fitted": float(predict_law(f, n, D.max())),
                             "miss": float(predict_law(f, n, D.max()) - e)} for n, e in zip(N[full], err[full])]
        if (~full).sum() >= 6 and len(set(D[~full])) >= 2:
            h = fit_law(N[~full], D[~full], err[~full])
            pred = predict_law(h, N[full], D[full])
            rep["holdout_full_data"] = {"fit": h, "max_abs_error": float(np.abs(pred - err[full]).max()),
                                        "mean_abs_error": float(np.abs(pred - err[full]).mean())}
        sizes = sorted(set(N.tolist()))
        deploy = max([n for n in sizes if n <= cap_params], default=max(sizes))
        miss = {p["params"]: p["miss"] for p in rep["full_data"]}
        rep["deployable_full_data_miss"] = miss.get(int(deploy))
        rep["predictions"] = [
            {"examples": m, "train_examples": int(m * train_share),
             "at_cap": float(predict_law(f, cap_params, m * train_share)),
             "largest_deployable_in_grid": float(predict_law(f, deploy, m * train_share)),
             "infinite_net": float(f["E"] + f["B"] * (m * train_share) ** -f["b"])}
            for m in [total] + [m for m in MILESTONES if m > total]]
        out[key] = rep
    return out


def markdown(snapshot, report, cap_params):
    lines = [f"# Leaf-net scaling fit: {snapshot}", "",
             "error(N, D) = E + A / N^a + B / D^b, N = parameters, D = training examples. "
             f"Deployment cap ~ {cap_params:,} parameters (2x v1's multiply-adds).", ""]
    for key, rep in report.items():
        f = rep["fit"]
        n_fit = sum(p["fitted"] for p in rep["points"])
        lines += [f"## {key}", "",
                  f"E = {f['E']:.6f} (floor), A = {f['A']:.4g}, a = {f['a']:.2f}, B = {f['B']:.4g}, "
                  f"b = {f['b']:.2f}; fit RMSE {f['rmse']:.6f} over {n_fit} points (data fractions of "
                  f"{rep['min_fraction']:g} and up).", ""]
        if f["at_edge"]:
            lines += [f"**Warning:** exponent {' and '.join(f['at_edge'])} ended on the end of the search range "
                      f"({EXPONENTS[0]:.2f} to {EXPONENTS[-1]:.1f}): the data does not pin it down, so do not "
                      "trust the floor or the predictions.", ""]
        lines += ["Fit at full data, every size (miss = fitted - measured):", "",
                  "| params | measured | fitted | miss |", "|---|---|---|---|"]
        lines += [f"| {p['params']:,} | {p['measured']:.6f} | {p['fitted']:.6f} | {p['miss']:+.6f} |"
                  for p in rep["full_data"]]
        lines.append("")
        if "holdout_full_data" in rep:
            h = rep["holdout_full_data"]
            lines += [f"Hold-out check (fit without the full data, predict it): mean |error| "
                      f"{h['mean_abs_error']:.6f}, max {h['max_abs_error']:.6f}.", ""]
        if rep.get("deployable_full_data_miss") is not None:
            lines += [f"The fit misses the largest deployable size at full data by "
                      f"{rep['deployable_full_data_miss']:+.6f}; read the predictions with that in mind.", ""]
        lines += ["| examples (train) | at the cap | largest deployable size in grid | unlimited size |",
                  "|---|---|---|---|"]
        for p in rep["predictions"]:
            lines.append(f"| {p['examples']:,} ({p['train_examples']:,}) | {p['at_cap']:.5f} | "
                         f"{p['largest_deployable_in_grid']:.5f} | {p['infinite_net']:.5f} |")
        lines += ["", "| params | train examples | mean error | seeds | in the fit |", "|---|---|---|---|---|"]
        lines += [f"| {p['params']:,} | {p['train_examples']:,} | {p['error']:.6f} | {p['seeds']} | "
                  f"{'yes' if p['fitted'] else 'no'} |" for p in rep["points"]]
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------ run ----

def load_trainer(path):
    spec = importlib.util.spec_from_file_location("leafnet_trainer", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "run") or not hasattr(mod, "CONFIG"):
        sys.exit(f"{path} has no run() and CONFIG")
    if not {"depth", "hidden"} <= set(mod.CONFIG):
        sys.exit(f"{path}: CONFIG needs 'depth' and 'hidden' keys for the size grid")
    return mod


class Subset:
    """A view of harness.Data with only some training examples (everything else shared)."""

    def __init__(self, data, mask):
        self.__dict__.update(data.__dict__)
        idx = data.torch.from_numpy(np.nonzero(mask)[0]).to(data.x_train.device)
        self.x_train, self.r_train, self.w_train = (t[idx] for t in (data.x_train, data.r_train, data.w_train))
        self.n_train = int(mask.sum())
        # rows of the full training split these examples are, for trainers that read extra per-example arrays
        self.train_index = np.nonzero(mask)[0]

    batches = harness.Data.batches
    val_loss = harness.Data.val_loss


def cmd_run(args):
    out_dir = os.path.join(args.work, "scaling", args.snapshot)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "runs.jsonl")
    trainer = load_trainer(args.trainer)
    with open(args.trainer, "rb") as f:
        trainer_sha = hashlib.sha256(f.read()).hexdigest()[:12]
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    done.add((r["trainer_sha"], r["depth"], r["hidden"], r["fraction"], r["seed"]))
    data = harness.Data(args.work, args.snapshot)
    split = np.load(os.path.join(data.dir, "split.npy"))
    train_jobs = np.load(os.path.join(data.dir, "jobs.npy"))[split == harness.SPLITS["train"]]
    sets = harness.eval_sets(data)
    grid = [(d, w, fr, s) for fr in args.fractions for (d, w) in args.sizes for s in range(args.seeds)]
    todo = [g for g in grid if (trainer_sha, g[0], g[1], g[2], g[3]) not in done]
    harness.log(f"scaling grid: {len(grid)} runs, {len(grid) - len(todo)} already done; trainer {args.trainer} "
                f"({trainer_sha})")
    views = {}
    for i, (depth, hidden, frac, seed) in enumerate(todo, 1):
        if frac not in views:
            views[frac] = Subset(data, subset_mask(train_jobs, frac)) if frac < 1 else data
        view = views[frac]
        cfg = dict(trainer.CONFIG, depth=depth, hidden=hidden)
        sizes = [data.n_in] + [hidden] * depth + [data.n_out]
        t0 = time.time()
        model, budget = harness.train_once(trainer.run, cfg, view, seed)
        scored = harness.score_model(model, data, sets)
        row = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "snapshot": args.snapshot, "trainer": args.trainer,
               "trainer_sha": trainer_sha, "depth": depth, "hidden": hidden, "params": params(sizes),
               "macs": harness.macs(sizes), "fraction": frac, "train_examples": view.n_train, "seed": seed,
               "steps": getattr(model, "steps_taken", None), "seconds": round(time.time() - t0, 1),
               "val_class": scored["val"][1][0], "val_range": scored["val"][1][1]}
        if "val_cv" in scored:
            row["val_cv_class"], row["val_cv_range"] = scored["val_cv"][1]
        for k, (_, (c, r)) in scored.items():
            if k.startswith("leaf:"):
                row[f"leaf_class:{k[5:]}"], row[f"leaf_range:{k[5:]}"] = c, r
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(row) + "\n")
        harness.log(f"[{i}/{len(todo)}] {depth}x{hidden} on {view.n_train:,} examples (seed {seed}): "
                    f"val class {row['val_class']:.6f} in {row['seconds']:.0f} s")
        del model


def cmd_fit(args):
    out_dir = os.path.join(args.work, "scaling", args.snapshot)
    with open(os.path.join(out_dir, "runs.jsonl"), encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    if args.trainer_sha:
        rows = [r for r in rows if r["trainer_sha"] == args.trainer_sha]
    shas = {r["trainer_sha"] for r in rows}
    if len(shas) > 1:
        sys.exit(f"runs from several trainers {sorted(shas)}: pick one with --trainer-sha")
    with open(os.path.join(args.work, "snapshots", args.snapshot, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    cap = harness.MAX_MACS  # params ~ multiply-adds for an MLP (biases aside)
    report = fit_report(rows, manifest, cap, args.min_fraction)
    with open(os.path.join(out_dir, "fit.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"snapshot": args.snapshot, "trainer_sha": shas.pop() if shas else None,
                   "cap_params": cap, "measures": report}, f, indent=1)
    md = markdown(args.snapshot, report, cap)
    with open(os.path.join(out_dir, "scaling.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print(md)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", default=harness.work_dir())
    ap.add_argument("--snapshot")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="train the size x data grid")
    r.add_argument("--trainer", default=os.path.join(HERE, "train.py"))
    r.add_argument("--sizes", type=parse_sizes, default=parse_sizes(DEFAULT_SIZES), help="DEPTHxWIDTH,...")
    r.add_argument("--fractions", type=lambda s: [float(x) for x in s.split(",")],
                   default=[float(x) for x in DEFAULT_FRACTIONS.split(",")])
    r.add_argument("--seeds", type=int, default=2)
    f = sub.add_parser("fit", help="fit the scaling law to the finished runs")
    f.add_argument("--trainer-sha", help="use only runs of this trainer version")
    f.add_argument("--min-fraction", type=float, default=DEFAULT_MIN_FRACTION,
                   help="fit only data fractions of this much of the full data and up")
    args = ap.parse_args()
    args.snapshot = args.snapshot or harness.current_snapshot(args.work)
    {"run": cmd_run, "fit": cmd_fit}[args.cmd](args)


if __name__ == "__main__":
    main()
