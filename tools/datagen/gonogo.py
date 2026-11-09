#!/usr/bin/env python3
"""The 50k go/no-go check for the Preflop Lab leaf-value net.

Trains a small net on the pooled solved flops and scores it, on jobs it never
saw, against the realization models Preflop Lab uses today (balanced, the
default, plus static, calibrated and raw). The question: does a learned leaf
value beat today's model clearly enough to keep collecting toward 300k?

    python tools/datagen/gonogo.py --wait 50000   # wait for 50k validated, then run
    python tools/datagen/gonogo.py                # run now on whatever is merged
    python tools/datagen/gonogo.py --data datagen_out   # local job files (testing)

Writes datagen_gonogo/report.md (the verdict), report.json and the trained
net (net.npz). Needs numpy, huggingface_hub (except with --data) and a build
of solve-cli. Runs on the CPU; the generator can keep using the GPU.

How it scores. Each example is one exact flop solve: per-class values for
both players as a fraction of the pot. Preflop Lab has no board at a flop
leaf, so both the net and today's models predict the value averaged over
flops, and each is scored against single-flop solves. The flop-to-flop
spread adds the same noise to both scores, so the gap between them is the
signal. Errors are weighted by each class's combo mass. Held-out jobs are
chosen by a hash of the job number, and the confidence interval resamples
whole held-out jobs.
"""

import argparse
import datetime
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

try:
    import numpy as np
except ImportError:
    sys.exit("numpy is needed:  python -m pip install numpy")

from validate import cuda_env, default_cli, load_config  # noqa: E402

MODELS = ["balanced", "static", "calibrated", "raw"]
POT_TYPES = ["limped", "srp", "3bet", "4bet"]
NC = 169


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------------------------ data ----

def fetch_total(repo):
    url = f"https://huggingface.co/datasets/{repo}/resolve/main/progress.json"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return int(json.load(r).get("total_examples", 0))
    except Exception as e:
        log(f"could not read progress.json ({e}); will retry")
        return None


def wait_for(repo, n, every_min):
    while True:
        total = fetch_total(repo)
        if total is not None:
            if total >= n:
                log(f"{total:,} validated examples: starting")
                return
            log(f"{total:,} of {n:,} validated examples; checking again in {every_min:g} min")
        time.sleep(every_min * 60)


def download(repo, dest):
    from huggingface_hub import snapshot_download
    log(f"downloading {repo} to {dest}")
    snapshot_download(repo, repo_type="dataset", allow_patterns=["data/*/*.jsonl.gz"], local_dir=dest)
    return os.path.join(dest, "data")


def job_files(folder):
    out = []
    for dirpath, _, files in os.walk(folder):
        for name in files:
            if name.startswith("job-") and (name.endswith(".jsonl.gz") or name.endswith(".jsonl")):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def read_examples(paths):
    """[(job, raw line, record)] for every example in the files."""
    rows = []
    for p in paths:
        opener = gzip.open if p.endswith(".gz") else open
        with opener(p, "rt", encoding="utf-8") as f:
            for line in f:
                if '"type":"example"' not in line.replace(" ", ""):
                    continue
                rec = json.loads(line)
                rows.append((int(rec["job"]), line.strip(), rec))
    return rows


INPUT_KEYS = ("job", "index", "board", "pot_type", "pot_bb", "stack_bb", "rake_pct", "rake_cap_bb", "range")


def baselines(cli, records, chunk=2000):
    """Price examples with solve-cli datagen baseline: {model: (n, 2, 169)}."""
    out = {m: [] for m in MODELS}
    for i in range(0, len(records), chunk):
        part = records[i:i + chunk]
        text = "\n".join(json.dumps({k: r[k] for k in INPUT_KEYS}) for r in part) + "\n"
        proc = subprocess.run([cli, "datagen", "baseline"], input=text, capture_output=True, text=True,
                              cwd=ROOT, env=cuda_env())
        got = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
        if proc.returncode != 0 or len(got) != len(part):
            sys.exit(f"solve-cli datagen baseline failed: {proc.stderr.strip()[-600:]}\n"
                     "Rebuild solve-cli from this checkout "
                     "(cargo build --release -p solver --features gpu --bin solve-cli).")
        for g in got:
            for m in MODELS:
                out[m].append(g["models"][m])
    return {m: np.asarray(v, dtype=np.float32) for m, v in out.items()}


def arrays(records):
    """Inputs, targets, mask, combo mass and class weights as arrays."""
    rng = np.asarray([r["range"] for r in records], np.float32)
    values = np.asarray([r["value"] for r in records], np.float64)  # None -> nan
    mask = np.isfinite(values).astype(np.float32)
    y = np.nan_to_num(values).astype(np.float32)
    reach = np.asarray([r["reach"] for r in records], np.float32)
    meta = []
    for r in records:
        pot, stack, rake = float(r["pot_bb"]), float(r["stack_bb"]), float(r["rake_pct"])
        meta.append([np.log(pot), np.log(stack), np.log(stack / pot), 10 * rake,
                     float(r["rake_cap_bb"]) / pot, 1.0 if rake > 0 else 0.0]
                    + [1.0 if r["pot_type"] == t else 0.0 for t in POT_TYPES])
    meta = np.asarray(meta, np.float32)
    mass = reach.sum(axis=2, keepdims=True)
    weight = reach / np.maximum(mass, 1e-12) * NC * mask
    return rng, meta, y, mask, reach, weight.astype(np.float32)


def split_of(job):
    h = int(hashlib.sha1(str(job).encode()).hexdigest(), 16) % 10
    return "test" if h == 0 else "val" if h == 1 else "train"


# ------------------------------------------------------------------- net ----

class MLP:
    """Plain numpy MLP with Adam, so the check needs nothing beyond numpy."""

    def __init__(self, sizes, seed=0):
        r = np.random.default_rng(seed)
        self.W = [(r.standard_normal((a, b)) * np.sqrt(2.0 / a)).astype(np.float32) for a, b in zip(sizes, sizes[1:])]
        self.b = [np.zeros(b, np.float32) for b in sizes[1:]]
        self.W[-1] *= 0.1
        self.m = [np.zeros_like(p) for p in self.W + self.b]
        self.v = [np.zeros_like(p) for p in self.W + self.b]
        self.t = 0

    def forward(self, x):
        hs = [x]
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            x = x @ W + b
            if i < len(self.W) - 1:
                x = np.maximum(x, 0)
            hs.append(x)
        return hs

    def step(self, x, target, w, lr, wd):
        hs = self.forward(x)
        diff = hs[-1] - target
        g = 2 * w * diff / max(float(w.sum()), 1e-9)
        grads_W, grads_b = [], []
        for i in range(len(self.W) - 1, -1, -1):
            grads_W.append(hs[i].T @ g + wd * self.W[i])
            grads_b.append(g.sum(axis=0))
            if i:
                g = (g @ self.W[i].T) * (hs[i] > 0)
        grads = grads_W[::-1] + grads_b[::-1]
        params = self.W + self.b
        self.t += 1
        b1, b2 = 0.9, 0.999
        for j, (p, gr) in enumerate(zip(params, grads)):
            self.m[j] = b1 * self.m[j] + (1 - b1) * gr
            self.v[j] = b2 * self.v[j] + (1 - b2) * gr * gr
            mh = self.m[j] / (1 - b1 ** self.t)
            vh = self.v[j] / (1 - b2 ** self.t)
            p -= (lr * mh / (np.sqrt(vh) + 1e-8)).astype(np.float32)

    def predict(self, x, batch=4096):
        return np.concatenate([self.forward(x[i:i + batch])[-1] for i in range(0, len(x), batch)])


def features(rng, meta, base):
    n = len(rng)
    return np.concatenate([rng.reshape(n, -1), base.reshape(n, -1), meta], axis=1).astype(np.float32)


def weighted_mse(pred, y, w):
    return float((w * (pred - y) ** 2).sum() / max(float(w.sum()), 1e-12))


def train(xtr, rtr, wtr, xva, rva, wva, args):
    """Fit the residual (solved value minus the balanced model) on training jobs,
    early-stopping on validation jobs."""
    mu, sd = xtr.mean(axis=0), xtr.std(axis=0)
    sd = np.where(sd < 1e-3, 1.0, sd)  # inputs constant in training stay unscaled
    norm = lambda x: (x - mu) / sd
    xtr_n, xva_n = norm(xtr), norm(xva)
    net = MLP([xtr.shape[1], args.hidden, args.hidden, rtr.shape[1]], seed=args.seed)
    rng = np.random.default_rng(args.seed)
    best, best_state, stale = float("inf"), None, 0
    lr = args.lr
    for epoch in range(1, args.epochs + 1):
        order = rng.permutation(len(xtr_n))
        for i in range(0, len(order), args.batch):
            idx = order[i:i + args.batch]
            net.step(xtr_n[idx], rtr[idx], wtr[idx], lr, args.weight_decay)
        va = weighted_mse(net.predict(xva_n), rva, wva)
        if va < best * (1 - 1e-4):
            best, stale = va, 0
            best_state = ([W.copy() for W in net.W], [b.copy() for b in net.b])
        else:
            stale += 1
            if stale == args.patience // 2:
                lr *= 0.3
        if epoch == 1 or epoch % 5 == 0 or stale == 0:
            log(f"epoch {epoch:3}  validation error {va:.6f}  best {best:.6f}")
        if stale >= args.patience:
            break
    net.W, net.b = best_state
    return net, mu, sd


# ---------------------------------------------------------------- scoring ----

def range_values(v, reach, mask):
    """Each player's range value (combo-mass average over classes): (n, 2)."""
    w = reach * mask
    return (w * v).sum(axis=2) / np.maximum(w.sum(axis=2), 1e-12)


def per_job_sums(jobs, pred, y, w, reach, mask):
    """Per held-out job: (sum w*err^2 per class, sum w, sum range err^2, count)."""
    cls = (w * (pred - y) ** 2).reshape(len(y), -1).sum(axis=1)
    wsum = w.reshape(len(y), -1).sum(axis=1)
    has = (reach * mask).sum(axis=2) > 0
    rerr = np.where(has, (range_values(pred, reach, mask) - range_values(y, reach, mask)) ** 2, 0).sum(axis=1)
    rcnt = has.sum(axis=1)
    out = {}
    for j in np.unique(jobs):
        s = jobs == j
        out[int(j)] = np.array([cls[s].sum(), wsum[s].sum(), rerr[s].sum(), rcnt[s].sum()])
    return out


def bootstrap(sums_a, sums_b, reps, seed):
    """95% interval of (error of a) - (error of b), resampling held-out jobs."""
    keys = sorted(sums_a)
    A = np.array([sums_a[k] for k in keys])
    B = np.array([sums_b[k] for k in keys])
    r = np.random.default_rng(seed)
    cls, rng_ = [], []
    for _ in range(reps):
        idx = r.integers(0, len(keys), len(keys))
        a, b = A[idx].sum(axis=0), B[idx].sum(axis=0)
        cls.append(a[0] / a[1] - b[0] / b[1])
        rng_.append(a[2] / max(a[3], 1) - b[2] / max(b[3], 1))
    q = lambda x: (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5)))
    return q(cls), q(rng_)


def totals(sums):
    s = np.array(list(sums.values())).sum(axis=0)
    return float(s[0] / s[1]), float(s[2] / max(s[3], 1))


# ------------------------------------------------------------------- main ----

def main():
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wait", type=int, default=0, help="wait until the dataset has this many validated examples")
    ap.add_argument("--poll", type=float, default=10, help="minutes between progress checks while waiting")
    ap.add_argument("--repo", default=cfg["hf_repo"])
    ap.add_argument("--data", help="use local job files in this folder instead of downloading")
    ap.add_argument("--download-dir", default=os.path.join(ROOT, "datagen_dataset"))
    ap.add_argument("--out", default=os.path.join(ROOT, "datagen_gonogo"))
    ap.add_argument("--solve-cli", default=default_cli())
    ap.add_argument("--hidden", type=int, default=512)
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-5)
    ap.add_argument("--patience", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--min-fix", type=float, default=0.01,
                    help="smallest confirmed fix to the balanced model, as a fraction of the pot, for GO")
    args = ap.parse_args()
    if not os.path.exists(args.solve_cli):
        sys.exit(f"{args.solve_cli} not found: build it with  cargo build --release -p solver --features gpu --bin solve-cli")
    started = time.time()
    if args.wait and not args.data:
        wait_for(args.repo, args.wait, args.poll)
    folder = args.data or download(args.repo, args.download_dir)
    rows = read_examples(job_files(folder))
    if not rows:
        sys.exit(f"no examples found in {folder}")
    jobs = np.array([r[0] for r in rows], dtype=np.int64)
    split = np.array([split_of(j) for j in jobs])
    if not (split == "test").any() or not (split == "val").any():
        # tiny local sets: fall back to job order so every split has a job
        uniq = sorted(set(jobs.tolist()))
        if len(uniq) < 3:
            sys.exit("need examples from at least 3 jobs")
        role = {j: ("test" if i == 0 else "val" if i == 1 else "train") for i, j in enumerate(uniq)}
        split = np.array([role[j] for j in jobs])
    n_jobs = {s: len(set(jobs[split == s].tolist())) for s in ("train", "val", "test")}
    log(f"{len(rows):,} examples from {len(set(jobs.tolist())):,} jobs "
        f"(train {n_jobs['train']}, validation {n_jobs['val']}, held out {n_jobs['test']} jobs)")

    log("pricing every example with today's Preflop Lab models")
    records = [r[2] for r in rows]
    base = baselines(args.solve_cli, records)
    rng, meta, y, mask, reach, w = arrays(records)
    n = len(rows)
    x = features(rng, meta, base["balanced"])
    resid = (y - base["balanced"]).reshape(n, -1) * mask.reshape(n, -1)
    wf = w.reshape(n, -1)
    tr, va, te = split == "train", split == "val", split == "test"

    log(f"training ({x.shape[1]} inputs, 2 x {args.hidden} hidden, {resid.shape[1]} outputs)")
    net, mu, sd = train(x[tr], resid[tr], wf[tr], x[va], resid[va], wf[va], args)
    pred = base["balanced"] + net.predict((x - mu) / sd).reshape(n, 2, NC)

    log("scoring on held-out jobs")
    sums = {"net": per_job_sums(jobs[te], pred[te], y[te], w[te], reach[te], mask[te])}
    for m in MODELS:
        sums[m] = per_job_sums(jobs[te], base[m][te], y[te], w[te], reach[te], mask[te])
    scores = {k: totals(v) for k, v in sums.items()}
    best_model = min(MODELS, key=lambda m: scores[m][0])
    ci_bal = bootstrap(sums["balanced"], sums["net"], args.bootstrap, args.seed)
    ci_best = bootstrap(sums[best_model], sums["net"], args.bootstrap, args.seed + 1)
    gain_cls = 1 - scores["net"][0] / scores["balanced"][0]
    gain_rng = 1 - scores["net"][1] / scores["balanced"][1]
    # Single-flop noise is in both errors, so the drop in error is what the
    # net fixes: its square root is the balanced model's error, in pot units,
    # that held-out solves confirm the net removes.
    fixed = float(np.sqrt(max(scores["balanced"][0] - scores["net"][0], 0.0)))
    moved = float(np.sqrt(weighted_mse(pred[te], base["balanced"][te], w[te])))
    beats = all(lo > 0 for lo in (ci_bal[0][0], ci_bal[1][0], ci_best[0][0], ci_best[1][0]))
    clear = beats and fixed >= args.min_fix
    verdict = "GO" if clear else "NO-GO" if not beats else "BORDERLINE"

    os.makedirs(args.out, exist_ok=True)
    np.savez(os.path.join(args.out, "net.npz"), *net.W, *net.b, mu=mu, sd=sd,
             layout=np.array(["range oop 169, range ip 169, balanced oop 169, balanced ip 169, "
                              "log pot, log stack, log spr, 10 x rake, rake cap / pot, raked, pot type x4; "
                              "output = solved value minus balanced, oop 169 then ip 169"]))
    report = {
        "verdict": verdict, "examples": len(rows), "jobs": n_jobs,
        "held_out_examples": int(te.sum()),
        "class_error": {k: v[0] for k, v in scores.items()},
        "range_error": {k: v[1] for k, v in scores.items()},
        "improvement_vs_balanced": {"class": gain_cls, "range": gain_rng},
        "balanced_error_fixed_pot": fixed, "net_change_vs_balanced_pot": moved,
        "ci95_balanced_minus_net": {"class": ci_bal[0], "range": ci_bal[1]},
        "best_current_model": best_model,
        "ci95_best_minus_net": {"class": ci_best[0], "range": ci_best[1]},
        "minutes": (time.time() - started) / 60,
        "when": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    with open(os.path.join(args.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    lines = [
        f"# Leaf-value net go/no-go: {verdict}", "",
        f"{len(rows):,} solved flops from {sum(n_jobs.values())} jobs; "
        f"{int(te.sum()):,} examples in {n_jobs['test']} held-out jobs the net never saw. "
        f"{report['when']}, {report['minutes']:.0f} min.", "",
        "Weighted squared error against exact single-flop solves (lower is better). "
        "Class = each hand class's value; range = each player's whole-range value. "
        "Flop-to-flop spread adds the same noise to every row, so compare the gaps.", "",
        "| Model | Class error | Range error |", "| --- | ---: | ---: |",
    ]
    for k in ["net"] + MODELS:
        name = {"net": "**Leaf net**", "balanced": "Balanced (Preflop Lab default)"}.get(k, k.capitalize())
        lines.append(f"| {name} | {scores[k][0]:.6f} | {scores[k][1]:.6f} |")
    lines += [
        "",
        f"The net changes the balanced model's class values by {100 * moved:.1f}% of the pot (RMS), and "
        f"held-out solves confirm it removes {100 * fixed:.1f}% of the pot of the balanced model's error "
        "(the square root of the drop in class error).",
        f"Net vs balanced: class error {100 * gain_cls:.1f}% lower, range error {100 * gain_rng:.1f}% lower "
        "(negative = higher; most of the remaining class error is flop-to-flop spread no flop-blind "
        "model can remove).",
        f"95% interval of balanced minus net, by resampling held-out jobs: class "
        f"[{ci_bal[0][0]:.6f}, {ci_bal[0][1]:.6f}], range [{ci_bal[1][0]:.6f}, {ci_bal[1][1]:.6f}].",
        f"Best current model: {best_model}; best minus net: class "
        f"[{ci_best[0][0]:.6f}, {ci_best[0][1]:.6f}], range [{ci_best[1][0]:.6f}, {ci_best[1][1]:.6f}].",
        "",
        "Rule: GO when the net beats every current model on both errors with intervals above zero "
        f"and removes at least {100 * args.min_fix:g}% of the pot of the balanced model's error; "
        "NO-GO when it does not beat them all; BORDERLINE otherwise.",
    ]
    with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    log(f"report written to {os.path.join(args.out, 'report.md')}")


if __name__ == "__main__":
    main()
