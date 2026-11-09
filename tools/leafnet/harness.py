#!/usr/bin/env python3
"""The frozen leaf-net harness: data on the GPU, scoring, the keep rule,
export and logging. The autoresearch agent never edits this file (see
program.md); it edits train.py only.

    python tools/leafnet/train.py --desc "baseline"        # one run, scored and logged (via harness.main)
    python tools/leafnet/harness.py noise --seeds 5        # seed spread of train.py's CONFIG
    python tools/leafnet/harness.py status                 # snapshot, best run, seed spread
    python tools/leafnet/harness.py final RUN_ID           # the ONLY command that reads the test split

Scoring is gonogo.py's: per-class squared error weighted by combo mass
("class error") and each player's whole-range value error ("range error"),
summed per job so the paired bootstrap resamples whole held-out jobs.
A candidate is compared with the current best on the same validation jobs,
so flop-to-flop noise cancels in the difference.

Keep rule (all must hold):
  1. the model exports to the GTOLEAF format (plain Linear/ReLU stack) and
     `solve-cli datagen leafnet` reproduces its outputs (parity);
  2. it costs at most 2x leaf net v1's multiply-adds per leaf;
  3. the 95% bootstrap interval of (best - candidate) class error is above 0,
     and the gain is larger than the measured seed spread;
  4. its validation range error is not significantly worse than the best's;
  5. on every real-leaf set it is not significantly worse than the best.
"""

import argparse
import datetime
import json
import os
import random
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "datagen"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import leafnet_io  # noqa: E402
from gonogo import MODELS, NC, bootstrap, per_job_sums, totals  # noqa: E402
from prepare import work_dir  # noqa: E402
from validate import cuda_env, default_cli  # noqa: E402

# ----------------------------------------------------------- fixed rules ----
V1_SIZES = [686, 512, 512, 2 * NC]           # leaf net v1 (cache/leaf_net_v1.bin)
MAX_MACS = 2 * sum(a * b for a, b in zip(V1_SIZES, V1_SIZES[1:]))
VRAM_CAP_GB = 3.0                            # hard cap: never push a datagen solve out of VRAM
STEP_BUDGET = 60_000                         # optimizer steps per run cap (~5 min for 2x512 at batch 256 on the 5090)
WALL_CAP_S = 15 * 60                         # a run over this is discarded
BOOTSTRAP_REPS = 2000
PARITY_EXAMPLES = 256
PARITY_TOL = 2e-3                            # max |residual difference|, fraction of the pot
SPLITS = {"train": 0, "val": 1, "test": 2}


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def current_snapshot(work):
    p = os.path.join(work, "CURRENT_SNAPSHOT")
    if not os.path.exists(p):
        sys.exit(f"no snapshot yet: run  python tools/leafnet/prepare.py  (WORK = {work})")
    with open(p, encoding="utf-8") as f:
        return f.read().strip()


def macs(sizes):
    return sum(a * b for a, b in zip(sizes, sizes[1:]))


# ------------------------------------------------------------------ data ----

class EvalSet:
    """Arrays for scoring one split or real-leaf set (numpy, CPU)."""

    def __init__(self, folder, sel=None):
        load = lambda n: np.load(os.path.join(folder, n + ".npy"), mmap_mode="r")
        idx = np.nonzero(sel)[0] if sel is not None else None
        take = (lambda a: np.ascontiguousarray(a[idx])) if idx is not None else (lambda a: np.ascontiguousarray(a[:]))
        self.x = take(load("x")).astype(np.float32)
        self.y = take(load("y"))
        self.mask = take(load("mask"))
        self.reach = take(load("reach"))
        self.w = take(load("w"))
        self.base = {m: take(load(f"base_{m}")) for m in MODELS}
        self.jobs = take(load("jobs"))
        self.pot_type = take(load("pot_type"))
        self.n = len(self.jobs)

    def sums(self, values):
        return per_job_sums(self.jobs, values, self.y, self.w, self.reach, self.mask)


class Data:
    """A frozen snapshot: training tensors on the GPU (under the VRAM cap),
    validation and real-leaf sets for scoring. Test jobs are loaded only by
    `harness.py final`."""

    def __init__(self, work=None, snapshot=None, device="cuda", with_test=False):
        import torch
        self.torch = torch
        self.work = work or work_dir()
        self.snapshot = snapshot or current_snapshot(self.work)
        self.dir = os.path.join(self.work, "snapshots", self.snapshot)
        with open(os.path.join(self.dir, "manifest.json"), encoding="utf-8") as f:
            self.manifest = json.load(f)
        if device == "cuda":
            if not torch.cuda.is_available():
                sys.exit("CUDA is not available to this PyTorch (see tools/leafnet/README.md for the setup)")
            total = torch.cuda.get_device_properties(0).total_memory
            torch.cuda.set_per_process_memory_fraction(min(1.0, VRAM_CAP_GB * 1e9 / total), 0)
        self.device = device
        split = np.load(os.path.join(self.dir, "split.npy"))
        x = np.load(os.path.join(self.dir, "x.npy"), mmap_mode="r")
        tr = split == SPLITS["train"]
        xtr = np.asarray(x[np.nonzero(tr)[0]], dtype=np.float32)
        # input normalization: train-split mean and scale (constant inputs stay unscaled), as gonogo
        self.mu = xtr.mean(axis=0).astype(np.float32)
        sd = xtr.std(axis=0)
        self.sd = np.where(sd < 1e-3, 1.0, sd).astype(np.float32)
        y = np.load(os.path.join(self.dir, "y.npy"), mmap_mode="r")
        mask = np.load(os.path.join(self.dir, "mask.npy"), mmap_mode="r")
        bal = np.load(os.path.join(self.dir, "base_balanced.npy"), mmap_mode="r")
        w = np.load(os.path.join(self.dir, "w.npy"), mmap_mode="r")
        idx = np.nonzero(tr)[0]
        n = len(idx)
        resid = ((np.asarray(y[idx]) - np.asarray(bal[idx])) * np.asarray(mask[idx])).reshape(n, -1)
        wtr = np.asarray(w[idx]).reshape(n, -1)
        self.n_in, self.n_out = xtr.shape[1], resid.shape[1]
        xn = (xtr - self.mu) / self.sd
        nbytes = 2 * (xn.size + resid.size + wtr.size)
        on_gpu = device == "cuda" and nbytes <= 1.5e9
        dev = device if on_gpu else "cpu"
        self.x_train = torch.from_numpy(xn).to(dev, torch.float16)
        self.r_train = torch.from_numpy(resid.astype(np.float32)).to(dev, torch.float16)
        self.w_train = torch.from_numpy(wtr.astype(np.float32)).to(dev, torch.float16)
        if not on_gpu and device == "cuda":
            self.x_train, self.r_train, self.w_train = (t.pin_memory() for t in (self.x_train, self.r_train, self.w_train))
        self.n_train = n
        self.val = EvalSet(self.dir, split == SPLITS["val"])
        self.x_val = torch.from_numpy((self.val.x - self.mu) / self.sd).to(device, torch.float32)
        r_val = ((self.val.y - self.val.base["balanced"]) * self.val.mask).reshape(self.val.n, -1)
        self.r_val = torch.from_numpy(r_val.astype(np.float32)).to(device)
        self.w_val = torch.from_numpy(self.val.w.reshape(self.val.n, -1).astype(np.float32)).to(device)
        self.leaf = {}
        for s in self.manifest.get("leaf_sets", []):
            self.leaf[s["name"]] = EvalSet(os.path.join(self.dir, "leaf", s["name"]))
        self.test = EvalSet(self.dir, split == SPLITS["test"]) if with_test else None
        log(f"snapshot {self.snapshot}: train {self.n_train:,}, val {self.val.n:,} "
            f"({len(set(self.val.jobs.tolist()))} jobs), real-leaf sets {list(self.leaf) or 'none'}; "
            f"training data on {'GPU' if on_gpu else 'pinned CPU memory' if device == 'cuda' else 'CPU'}")

    def batches(self, batch_size, generator):
        """Endless shuffled minibatches (x, residual target, weight) on the device, float32."""
        torch = self.torch
        while True:
            perm = torch.randperm(self.n_train, generator=generator, device="cpu")
            for i in range(0, self.n_train - batch_size + 1, batch_size):
                idx = perm[i:i + batch_size]
                if self.x_train.device.type == "cpu":
                    yield tuple(t[idx].to(self.device, non_blocking=True).float()
                                for t in (self.x_train, self.r_train, self.w_train))
                else:
                    idx = idx.to(self.device)
                    yield self.x_train[idx].float(), self.r_train[idx].float(), self.w_train[idx].float()

    def val_loss(self, model):
        """Weighted MSE of the residual on the validation split (for early stopping)."""
        torch = self.torch
        with torch.no_grad():
            was = model.training
            model.eval()
            pred = torch.cat([model(self.x_val[i:i + 8192]) for i in range(0, len(self.x_val), 8192)])
            model.train(was)
            return float((self.w_val * (pred - self.r_val) ** 2).sum() / self.w_val.sum())


class Budget:
    """Fixed per-run training budget; train.py must stop when done() says so."""

    def __init__(self, steps=STEP_BUDGET, seconds=WALL_CAP_S):
        self.steps, self.seconds, self.t0 = steps, seconds, time.time()

    def done(self, step):
        return step >= self.steps or time.time() - self.t0 >= self.seconds

    def elapsed(self):
        return time.time() - self.t0


# --------------------------------------------------------------- export ----

def to_mlp(model):
    """Weights and biases of a plain Linear/ReLU stack (Dropout and Identity
    ignored), or a ValueError saying why the model is not deployable."""
    import torch
    if not isinstance(model, torch.nn.Sequential):
        raise ValueError("train.py must return a torch.nn.Sequential of Linear and ReLU layers")
    mods = [m for m in model if not isinstance(m, (torch.nn.Dropout, torch.nn.Identity))]
    Ws, bs, expect_linear = [], [], True
    for m in mods:
        if isinstance(m, torch.nn.Linear) and expect_linear:
            Ws.append(m.weight.detach().float().cpu().numpy().T.copy())
            bs.append((m.bias.detach().float().cpu().numpy() if m.bias is not None
                       else np.zeros(m.out_features, np.float32)).copy())
            expect_linear = False
        elif isinstance(m, torch.nn.ReLU) and not expect_linear:
            expect_linear = True
        else:
            raise ValueError(f"not deployable: {type(m).__name__} where the Rust loader expects "
                             f"{'Linear' if expect_linear else 'ReLU'} (fold anything else into Linear layers first)")
    if expect_linear or not Ws:
        raise ValueError("not deployable: the model must end with a Linear layer")
    return Ws, bs


def predict(model, x_norm):
    """Residual predictions (n, 2, 169) for normalized inputs (numpy float32)."""
    import torch
    dev = next(model.parameters()).device
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(x_norm), 8192):
            out.append(model(torch.from_numpy(x_norm[i:i + 8192]).to(dev)).float().cpu().numpy())
    return np.concatenate(out).reshape(len(x_norm), 2, NC)


def parity(cli, net_path, inputs_path, model, data, count=PARITY_EXAMPLES):
    """Max |Rust residual - torch residual| over the first validation examples."""
    with open(inputs_path, encoding="utf-8") as f:
        lines = [l for l in f if l.strip()][:count]
    proc = subprocess.run([cli, "datagen", "leafnet", net_path], input="".join(lines), capture_output=True,
                          text=True, cwd=ROOT, env=cuda_env())
    got = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
    if proc.returncode != 0 or len(got) != len(lines):
        raise ValueError(f"solve-cli datagen leafnet failed: {proc.stderr.strip()[-400:]}")
    rust = np.asarray([g["residual"] for g in got], dtype=np.float32).reshape(len(got), 2, NC)
    mine = predict(model, (data.val.x[:len(got)] - data.mu) / data.sd)
    return float(np.abs(rust - mine).max())


# ------------------------------------------------------------- scoring ----

def score_model(model, data, sets):
    """{set: (per-job sums, (class error, range error))} for the model."""
    out = {}
    for name, es in sets.items():
        pred = es.base["balanced"] + predict(model, (es.x - data.mu) / data.sd)
        s = es.sums(pred)
        out[name] = (s, totals(s))
    return out


def sums_to_json(s):
    return {str(k): [float(x) for x in v] for k, v in s.items()}


def sums_from_json(d):
    return {int(k): np.asarray(v) for k, v in d.items()}


# ---------------------------------------------------------------- state ----

class State:
    def __init__(self, work, snapshot):
        self.dir = os.path.join(work, "runs", snapshot)
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, "state.json")
        self.s = json.load(open(self.path, encoding="utf-8")) if os.path.exists(self.path) else {}

    def save(self):
        with open(self.path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.s, f, indent=1)

    def best_sums(self):
        b = self.s.get("best")
        if not b:
            return None
        with open(os.path.join(self.dir, b, "sums.json"), encoding="utf-8") as f:
            d = json.load(f)
        return {k: sums_from_json(v) for k, v in d.items()}


TSV_COLS = ["time", "snapshot", "run", "commit", "dirty", "desc", "seed", "steps", "seconds", "macs",
            "val_class", "val_range", "gain_class", "ci_class_lo", "ci_class_hi", "ci_range_lo", "ci_range_hi",
            "leaf_class", "leaf_range", "parity", "verdict", "reason"]


def git_rev():
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "tools/leafnet/train.py"], capture_output=True,
                               text=True, cwd=ROOT).stdout.strip() != ""
        return rev, dirty
    except OSError:
        return "?", True


def append_tsv(work, row):
    path = os.path.join(work, "results.tsv")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        if new:
            f.write("\t".join(TSV_COLS) + "\n")
        f.write("\t".join(str(row.get(c, "")).replace("\t", " ") for c in TSV_COLS) + "\n")


# ------------------------------------------------------------------ runs ----

def seed_everything(seed):
    import torch
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False


def train_once(run_fn, cfg, data, seed):
    import torch
    seed_everything(seed)
    gen = torch.Generator().manual_seed(seed)
    budget = Budget()
    model = run_fn(dict(cfg, seed=seed), data, budget, gen)
    model = model.float().to(data.device).eval()
    return model, budget


def evaluate_run(model, data, cfg, seed, steps, seconds, desc, cli, state, decide=True, run_id=None):
    """Export, check, score and (optionally) apply the keep rule; logs to results.tsv."""
    run_id = run_id or datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + f"-s{seed}"
    rdir = os.path.join(state.dir, run_id)
    os.makedirs(rdir, exist_ok=True)
    row = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "snapshot": data.snapshot, "run": run_id,
           "desc": desc, "seed": seed, "steps": steps, "seconds": f"{seconds:.0f}"}
    row["commit"], row["dirty"] = git_rev()
    verdict, reason = "discard", ""
    try:
        Ws, bs = to_mlp(model)
        sizes = [Ws[0].shape[0]] + [W.shape[1] for W in Ws]
        row["macs"] = macs(sizes)
        if sizes[0] != data.n_in or sizes[-1] != data.n_out:
            raise ValueError(f"sizes {sizes} do not match {data.n_in} inputs / {data.n_out} outputs")
        if row["macs"] > MAX_MACS:
            raise ValueError(f"{row['macs']:,} multiply-adds per leaf is over the limit {MAX_MACS:,} (2x v1)")
        net_path = os.path.join(rdir, "leaf_net.bin")
        leafnet_io.write(net_path, Ws, bs, data.mu, data.sd,
                         extra={"snapshot": data.snapshot, "run": run_id, "trainer": "tools/leafnet/train.py"})
        row["parity"] = f"{parity(cli, net_path, os.path.join(data.dir, 'inputs_val.jsonl'), model, data):.2e}"
        if float(row["parity"]) > PARITY_TOL:
            raise ValueError(f"Rust and PyTorch outputs differ by {row['parity']} (> {PARITY_TOL})")
    except ValueError as e:
        reason = str(e)
        row.update(verdict="rejected", reason=reason)
        append_tsv(data.work, row)
        log(f"REJECTED: {reason}")
        return "rejected", row
    sets = {"val": data.val, **{f"leaf:{k}": v for k, v in data.leaf.items()}}
    scored = score_model(model, data, sets)
    row["val_class"], row["val_range"] = (f"{x:.6f}" for x in scored["val"][1])
    leaf_names = [k for k in scored if k.startswith("leaf:")]
    if leaf_names:
        row["leaf_class"] = " ".join(f"{scored[k][1][0]:.5f}" for k in leaf_names)
        row["leaf_range"] = " ".join(f"{scored[k][1][1]:.6f}" for k in leaf_names)
    with open(os.path.join(rdir, "sums.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({k: sums_to_json(v[0]) for k, v in scored.items()}, f)
    with open(os.path.join(rdir, "config.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"config": cfg, "seed": seed, "steps": steps, "seconds": seconds, "desc": desc,
                   "scores": {k: v[1] for k, v in scored.items()}}, f, indent=1)
    best = state.best_sums()
    spread = state.s.get("seed_spread", {})
    if not decide:
        verdict, reason = "sweep", ""
    elif best is None:
        verdict, reason = "keep", "first run on this snapshot: becomes the best"
    else:
        (c_lo, c_hi), (r_lo, r_hi) = bootstrap(best["val"], scored["val"][0], BOOTSTRAP_REPS, 0)
        b_cls, _ = totals(best["val"])
        gain = b_cls - scored["val"][1][0]
        row.update(gain_class=f"{gain:.6f}", ci_class_lo=f"{c_lo:.6f}", ci_class_hi=f"{c_hi:.6f}",
                   ci_range_lo=f"{r_lo:.6f}", ci_range_hi=f"{r_hi:.6f}")
        need = float(spread.get("class", 0.0))
        problems = []
        if c_lo <= 0:
            problems.append(f"class gain not significant (interval {c_lo:+.6f} to {c_hi:+.6f})")
        if gain <= need:
            problems.append(f"gain {gain:.6f} not above the seed spread {need:.6f}"
                            + ("" if spread else " (run `harness.py noise` to measure it)"))
        if r_hi < 0:
            problems.append(f"range error significantly worse (interval {r_lo:+.6f} to {r_hi:+.6f})")
        for k in leaf_names:
            if k in best:
                (l_lo, l_hi), (lr_lo, lr_hi) = bootstrap(best[k], scored[k][0], BOOTSTRAP_REPS, 1)
                if l_hi < 0 or lr_hi < 0:
                    problems.append(f"significantly worse on real leaves {k[5:]}")
        verdict = "keep" if not problems else "discard"
        reason = "; ".join(problems) or f"gain {gain:.6f} (interval {c_lo:+.6f} to {c_hi:+.6f})"
    row.update(verdict=verdict, reason=reason)
    if verdict == "keep":
        state.s["best"] = run_id
        state.s.setdefault("history", []).append(run_id)
        state.save()
        shutil.copy(os.path.join(rdir, "leaf_net.bin"), os.path.join(state.dir, "best_leaf_net.bin"))
    append_tsv(data.work, row)
    log(f"{verdict.upper()}: val class {row['val_class']} range {row['val_range']}"
        + (f", real leaves class {row['leaf_class']}" if leaf_names else "") + (f" -- {reason}" if reason else ""))
    return verdict, row


def main(run_fn, config):
    """Entry point used by train.py: one run, scored against the best and logged."""
    ap = argparse.ArgumentParser(description="Train one leaf net with train.py's CONFIG and apply the keep rule.")
    ap.add_argument("--desc", required=True, help="one line: what this run changes")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--snapshot")
    ap.add_argument("--work", default=work_dir())
    ap.add_argument("--solve-cli", default=default_cli())
    args = ap.parse_args()
    data = Data(args.work, args.snapshot)
    state = State(args.work, data.snapshot)
    model, budget = train_once(run_fn, config, data, args.seed)
    steps = getattr(model, "steps_taken", "")
    log(f"trained in {budget.elapsed():.0f} s ({steps} steps)")
    if budget.elapsed() > WALL_CAP_S * 1.05:
        log("over the wall-clock cap: discarded")
        sys.exit(1)
    verdict, _ = evaluate_run(model, data, config, args.seed, steps, budget.elapsed(), args.desc, args.solve_cli, state)
    print(f"VERDICT: {verdict}")


# ------------------------------------------------------------- commands ----

def cmd_noise(args):
    import train
    data = Data(args.work, args.snapshot)
    state = State(args.work, data.snapshot)
    results = []
    for seed in range(args.seeds):
        model, budget = train_once(train.run, train.CONFIG, data, seed)
        steps = getattr(model, "steps_taken", "")
        _, row = evaluate_run(model, data, train.CONFIG, seed, steps, budget.elapsed(), f"noise seed {seed}",
                              args.solve_cli, state, decide=False, run_id=f"noise-{datetime.date.today()}-s{seed}")
        results.append(row)
    cls = np.array([float(r["val_class"]) for r in results])
    rng = np.array([float(r["val_range"]) for r in results])
    sums = []
    for r in results:
        with open(os.path.join(state.dir, r["run"], "sums.json"), encoding="utf-8") as f:
            sums.append(sums_from_json(json.load(f)["val"]))
    false_pos = 0
    pairs = 0
    for i in range(len(sums)):
        for j in range(len(sums)):
            if i != j:
                (lo, _), _ = bootstrap(sums[i], sums[j], BOOTSTRAP_REPS, 0)
                pairs += 1
                false_pos += lo > 0
    bal = totals(data.val.sums(data.val.base["balanced"]))
    spread = {"balanced_val_class": bal[0], "balanced_val_range": bal[1],
              "class": float(cls.max() - cls.min()), "range": float(rng.max() - rng.min()),
              "class_std": float(cls.std(ddof=1)) if len(cls) > 1 else 0.0, "seeds": int(args.seeds),
              "class_errors": cls.tolist(), "range_errors": rng.tolist(),
              "same_config_pairs_called_significant": f"{false_pos}/{pairs}"}
    state.s["seed_spread"] = spread
    if not state.s.get("best"):
        # seed 0 (the default seed of train.py runs) is the bar: like for like, not the luckiest seed
        best = results[0]["run"]
        state.s["best"] = best
        shutil.copy(os.path.join(state.dir, best, "leaf_net.bin"), os.path.join(state.dir, "best_leaf_net.bin"))
    state.save()
    print(json.dumps(spread, indent=1))


def cmd_status(args):
    work = args.work
    snap = args.snapshot or current_snapshot(work)
    st = State(work, snap)
    with open(os.path.join(work, "snapshots", snap, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    print(json.dumps({"snapshot": snap, "examples": m["examples"], "examples_by_split": m["examples_by_split"],
                      "leaf_sets": [s["name"] for s in m.get("leaf_sets", [])], "best": st.s.get("best"),
                      "seed_spread": st.s.get("seed_spread")}, indent=1))


def cmd_final(args):
    """Score a run's exported net on the test split and the real-leaf sets, against today's models."""
    data = Data(args.work, args.snapshot, device="cpu", with_test=True)
    st = State(args.work, data.snapshot)
    run = args.run or st.s.get("best")
    header, Ws, bs, mu, sd = leafnet_io.read(os.path.join(st.dir, run, "leaf_net.bin"))
    sets = {"test": data.test, **{f"leaf:{k}": v for k, v in data.leaf.items()}}
    report = {"run": run, "snapshot": data.snapshot}
    for name, es in sets.items():
        pred = es.base["balanced"] + leafnet_io.forward(Ws, bs, mu, sd, es.x).reshape(es.n, 2, NC)
        sums = {"net": es.sums(pred), **{m: es.sums(es.base[m]) for m in MODELS}}
        ci = bootstrap(sums["balanced"], sums["net"], BOOTSTRAP_REPS, 0)
        report[name] = {"jobs": len(set(es.jobs.tolist())), "examples": es.n,
                        "class_error": {k: totals(v)[0] for k, v in sums.items()},
                        "range_error": {k: totals(v)[1] for k, v in sums.items()},
                        "balanced_minus_net_ci95": {"class": ci[0], "range": ci[1]}}
    with open(os.path.join(st.dir, run, "final.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))


def cli():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", default=work_dir())
    ap.add_argument("--snapshot")
    ap.add_argument("--solve-cli", default=default_cli())
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("noise", help="train train.py's CONFIG with several seeds; store the seed spread")
    n.add_argument("--seeds", type=int, default=5)
    sub.add_parser("status")
    f = sub.add_parser("final", help="score a run on the TEST split (milestones only)")
    f.add_argument("run", nargs="?")
    args = ap.parse_args()
    {"noise": cmd_noise, "status": cmd_status, "final": cmd_final}[args.cmd](args)


if __name__ == "__main__":
    cli()
