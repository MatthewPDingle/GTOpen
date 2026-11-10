#!/usr/bin/env python3
"""The frozen leaf-net harness: data on the GPU, scoring, the keep rule,
export and logging. The autoresearch agent never edits this file (see
program.md); it edits train.py only.

    python tools/leafnet/train.py --desc "baseline"        # one run, scored and logged (via harness.main)
    python tools/leafnet/train.py --prepare                # only build the recipe's shared side data (its prepare())
    python tools/leafnet/harness.py noise --seeds 5        # seed spread of train.py's CONFIG
    python tools/leafnet/harness.py status                 # snapshot, best run, seed spread
    python tools/leafnet/harness.py confirm RUN RUN RUN    # seed-averaged keep rule for a near miss
    python tools/leafnet/harness.py rescore                # add the referee's val_cv score to existing runs
    python tools/leafnet/harness.py ensemble               # average the best's seed copies into one net file
    python tools/leafnet/harness.py final RUN_ID           # the ONLY command that reads the test split

Scoring is gonogo.py's: per-class squared error weighted by combo mass
("class error") and each player's whole-range value error ("range error"),
summed per job so the paired bootstrap resamples whole held-out jobs.
A candidate is compared with the current best on the same validation jobs,
so flop-to-flop noise cancels in the difference.

The score. When the snapshot has a referee (referee.py: validation targets
with the flop luck taken out, "val_cv"), the keep rule's class gain, interval
and seed spread are measured on val_cv, and the raw validation error becomes
a guard (not significantly worse). Without one, they use the raw validation
error as before. `harness.py rescore` adds val_cv to runs scored before the
referee existed, and the val_cv seed spread from the noise runs.

Keep rule (all must hold):
  1. the model exports to the GTOLEAF format (plain Linear/ReLU stack) and
     `solve-cli datagen leafnet` reproduces its outputs (parity);
  2. it costs at most 4x leaf net v1's multiply-adds per leaf;
  3. the 95% bootstrap interval of (best - candidate) class error on the
     score is above 0, and the gain is larger than the measured seed spread;
  4. its range error on the score is not significantly worse than the best's;
  5. on every real-leaf set, and on raw validation when the score is val_cv,
     it is not significantly worse than the best.

A run that passes everything except the seed spread (interval above zero,
gain positive but small) is a "near" miss, not noise yet: train it with
`--seed 1` and `--seed 2` (`--replicate` keeps those runs out of the
keep rule) and run `harness.py confirm` on the three. Confirmation applies
the same rule to per-job errors averaged over the candidate's seeds and the
best's seeds, with the spread threshold shrunk for the averaging:
spread x sqrt((1/n + 1/m) / 2) for n candidate and m best seeds, which is
the spread itself when n = m = 1.

Ensembles. `harness.py ensemble` writes one net file holding several kept
runs (by default the best and its seed replicates); the solver's output for
it is the mean of the members' outputs. Seed copies of one recipe disagree
at a solve's leaves by more than recipes now improve on each other, so the
mean is what to deploy: steadier ranges and a slightly better score. An
ensemble is not a keep-rule candidate and never becomes the best: recipes
are still compared net against net. It is checked for parity with
solve-cli, must score no worse than its members' average on every set, and
may hold up to 16x v1's multiply-adds in total (the net runs once per
refresh of a solve's leaf values, not per iteration).
"""

import argparse
import copy
import datetime
import hashlib
import json
import os
import random
import re
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
MAX_MACS_X = 4                               # size limit, in multiples of v1's multiply-adds per leaf
MAX_MACS = MAX_MACS_X * sum(a * b for a, b in zip(V1_SIZES, V1_SIZES[1:]))
MAX_ENSEMBLE_MACS_X = 16                     # an ensemble's limit, all members together
MAX_ENSEMBLE_MACS = MAX_ENSEMBLE_MACS_X * sum(a * b for a, b in zip(V1_SIZES, V1_SIZES[1:]))
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

    def with_targets(self, y):
        """The same examples scored against other targets (same shape as y)."""
        out = copy.copy(self)
        assert y.shape == self.y.shape, f"targets {y.shape} do not match {self.y.shape}"
        out.y = y
        return out


def load_val_cv(snapshot_dir, val):
    """The referee's low-noise validation set (None without a referee); checks the file is unchanged."""
    path = os.path.join(snapshot_dir, "referee", "val_cv.npy")
    if not os.path.exists(path):
        return None
    with open(os.path.join(snapshot_dir, "referee", "referee.json"), encoding="utf-8") as f:
        meta = json.load(f)
    with open(path, "rb") as f:
        if hashlib.sha256(f.read()).hexdigest() != meta["val_cv_sha256"]:
            sys.exit(f"{path} does not match referee.json: rerun referee.py --force, then harness.py rescore")
    return val.with_targets(np.load(path))


def eval_sets(data):
    """Every set a run is scored on: validation, the referee's val_cv if any, the real-leaf sets."""
    return {"val": data.val, **({"val_cv": data.val_cv} if data.val_cv is not None else {}),
            **{f"leaf:{k}": v for k, v in data.leaf.items()}}


def scoring_sets(work, snapshot):
    """(snapshot folder, {set: EvalSet}) for scoring an exported net with numpy alone: validation, the
    referee's val_cv if any and the real-leaf sets. No GPU, no training data, no test split."""
    sdir = os.path.join(work, "snapshots", snapshot)
    with open(os.path.join(sdir, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    val = EvalSet(sdir, np.load(os.path.join(sdir, "split.npy")) == SPLITS["val"])
    val_cv = load_val_cv(sdir, val)
    sets = {"val": val, **({"val_cv": val_cv} if val_cv is not None else {})}
    for s in manifest.get("leaf_sets", []):
        sets[f"leaf:{s['name']}"] = EvalSet(os.path.join(sdir, "leaf", s["name"]))
    return sdir, sets


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
        self.val_cv = load_val_cv(self.dir, self.val)
        self.x_val = torch.from_numpy((self.val.x - self.mu) / self.sd).to(device, torch.float32)
        r_val = ((self.val.y - self.val.base["balanced"]) * self.val.mask).reshape(self.val.n, -1)
        self.r_val = torch.from_numpy(r_val.astype(np.float32)).to(device)
        self.w_val = torch.from_numpy(self.val.w.reshape(self.val.n, -1).astype(np.float32)).to(device)
        self.leaf = {}
        for s in self.manifest.get("leaf_sets", []):
            self.leaf[s["name"]] = EvalSet(os.path.join(self.dir, "leaf", s["name"]))
        self.test = EvalSet(self.dir, split == SPLITS["test"]) if with_test else None
        log(f"snapshot {self.snapshot}: train {self.n_train:,}, val {self.val.n:,} "
            f"({len(set(self.val.jobs.tolist()))} jobs{', referee val_cv' if self.val_cv is not None else ''}), "
            f"real-leaf sets {list(self.leaf) or 'none'}; "
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


def rust_residuals(cli, net_path, inputs_path, count=PARITY_EXAMPLES):
    """The Rust loader's residuals (n, 2, 169) for the first `count` validation examples."""
    with open(inputs_path, encoding="utf-8") as f:
        lines = [l for l in f if l.strip()][:count]
    proc = subprocess.run([cli, "datagen", "leafnet", net_path], input="".join(lines), capture_output=True,
                          text=True, cwd=ROOT, env=cuda_env())
    got = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
    if proc.returncode != 0 or len(got) != len(lines):
        raise ValueError(f"solve-cli datagen leafnet failed: {proc.stderr.strip()[-400:]}")
    return np.asarray([g["residual"] for g in got], dtype=np.float32).reshape(len(got), 2, NC)


def parity(cli, net_path, inputs_path, model, data, count=PARITY_EXAMPLES):
    """Max |Rust residual - torch residual| over the first validation examples."""
    rust = rust_residuals(cli, net_path, inputs_path, count)
    mine = predict(model, (data.val.x[:len(rust)] - data.mu) / data.sd)
    return float(np.abs(rust - mine).max())


def file_parity(cli, net_path, inputs_path, val, count=PARITY_EXAMPLES):
    """Max |Rust residual - numpy residual| of a net file (plain or ensemble) over the first validation examples."""
    rust = rust_residuals(cli, net_path, inputs_path, count)
    _, members = leafnet_io.read_members(net_path)
    mine = leafnet_io.forward_members(members, val.x[:len(rust)]).reshape(len(rust), 2, NC)
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


def score_file(net_path, sets):
    """{set: (per-job sums, (class error, range error))} for a net file (plain or ensemble), numpy only."""
    _, members = leafnet_io.read_members(net_path)
    out = {}
    for name, es in sets.items():
        s = es.sums(es.base["balanced"] + leafnet_io.forward_members(members, es.x).reshape(es.n, 2, NC))
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
        return self.group_sums([b])

    def best_seeds(self):
        """The best run and its seed replicates (one setup, different seeds)."""
        b = self.s.get("best")
        seeds = [r for r in self.s.get("best_seeds", []) if r != b]
        return ([b] + seeds) if b else []

    def group_sums(self, runs):
        """Per-job sums averaged over `runs` (seed replicates of one setup),
        for every evaluation set all of them were scored on."""
        loaded = []
        for r in runs:
            with open(os.path.join(self.dir, r, "sums.json"), encoding="utf-8") as f:
                loaded.append(json.load(f))
        out = {}
        for name in sorted(set.intersection(*(set(d) for d in loaded))):
            per = [sums_from_json(d[name]) for d in loaded]
            out[name] = {k: np.mean([p[k] for p in per], axis=0) for k in per[0]}
        return out


def score_key(best, cand):
    """The set the keep rule measures gains on: the referee's val_cv when both sides have it, else val."""
    return "val_cv" if "val_cv" in best and "val_cv" in cand else "val"


def spread_need(spread, key, n_cand=1, n_best=1):
    """(threshold, measured) for the score `key` from state's seed_spread."""
    k = "class_cv" if key == "val_cv" else "class"
    return seed_need(float(spread.get(k, 0.0)), n_cand, n_best), k in spread


def judge(best, cand, need, spread_measured=True):
    """The keep rule's statistics: candidate sums vs best sums (both
    {set: per-job sums}). Returns (problems, near, stats); `near` means only
    the seed-spread condition failed. The gain is measured on score_key()."""
    key = score_key(best, cand)
    (c_lo, c_hi), (r_lo, r_hi) = bootstrap(best[key], cand[key], BOOTSTRAP_REPS, 0)
    gain = totals(best[key])[0] - totals(cand[key])[0]
    stats = {"gain_class": gain, "ci_class_lo": c_lo, "ci_class_hi": c_hi, "ci_range_lo": r_lo, "ci_range_hi": r_hi}
    problems, small = [], False
    if c_lo <= 0:
        problems.append(f"class gain not significant (interval {c_lo:+.6f} to {c_hi:+.6f})")
    if gain <= need:
        small = True
        problems.append(f"gain {gain:.6f} not above the seed spread {need:.6f}"
                        + ("" if spread_measured else " (run `harness.py noise` to measure it)"))
    if r_hi < 0:
        problems.append(f"range error significantly worse (interval {r_lo:+.6f} to {r_hi:+.6f})")
    if key == "val_cv":
        (v_lo, v_hi), _ = bootstrap(best["val"], cand["val"], BOOTSTRAP_REPS, 2)
        if v_hi < 0:
            problems.append(f"raw validation class error significantly worse (interval {v_lo:+.6f} to {v_hi:+.6f})")
    for k in cand:
        if k.startswith("leaf:") and k in best:
            (l_lo, l_hi), (lr_lo, lr_hi) = bootstrap(best[k], cand[k], BOOTSTRAP_REPS, 1)
            if l_hi < 0 or lr_hi < 0:
                problems.append(f"significantly worse on real leaves {k[5:]}")
    near = small and len(problems) == 1 and gain > 0
    return problems, near, stats


def seed_need(spread_class, n_cand, n_best):
    """Seed-spread threshold for a difference of seed means (= the spread for 1 vs 1)."""
    return spread_class * ((1 / n_cand + 1 / n_best) / 2) ** 0.5


def make_best(state, run_id, seeds):
    state.s["best"] = run_id
    state.s["best_seeds"] = list(seeds)
    state.s.setdefault("history", []).append(run_id)
    state.save()
    shutil.copy(os.path.join(state.dir, run_id, "leaf_net.bin"), os.path.join(state.dir, "best_leaf_net.bin"))


TSV_COLS = ["time", "snapshot", "run", "commit", "dirty", "desc", "seed", "steps", "seconds", "macs",
            "val_class", "val_range", "gain_class", "ci_class_lo", "ci_class_hi", "ci_range_lo", "ci_range_hi",
            "leaf_class", "leaf_range", "parity", "verdict", "reason",
            "val_cv_class"]    # new columns go at the end: older rows simply lack them


def git_rev():
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "tools/leafnet/train.py"], capture_output=True,
                               text=True, cwd=ROOT).stdout.strip() != ""
        return rev, dirty
    except OSError:
        return "?", True


def upgrade_tsv_header(path):
    """A results.tsv written before a column was added gets the current header (its rows keep fewer fields)."""
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    head, sep, rest = text.partition("\n")
    cols = head.rstrip("\r").split("\t")
    if cols == TSV_COLS or cols != TSV_COLS[:len(cols)]:
        return                      # current already, or not a header this harness wrote: leave it alone
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(TSV_COLS) + sep + rest)
    os.replace(tmp, path)


def append_tsv(work, row):
    path = os.path.join(work, "results.tsv")
    new = not os.path.exists(path)
    if not new:
        upgrade_tsv_header(path)
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


def prepare_once(prepare_fn, cfg, data):
    """Runs the trainer's optional prepare(cfg, data) before a run's clock starts: side data that the
    recipe's runs share and cache (a bank of teachers, say). Returns the seconds it took."""
    if prepare_fn is None:
        return 0.0
    t0 = time.time()
    prepare_fn(dict(cfg), data)
    seconds = time.time() - t0
    if seconds >= 1:
        log(f"prepared the recipe's shared side data in {seconds:.0f} s (outside the run's budget)")
    return seconds


def train_once(run_fn, cfg, data, seed):
    import torch
    seed_everything(seed)
    gen = torch.Generator().manual_seed(seed)
    budget = Budget()
    model = run_fn(dict(cfg, seed=seed), data, budget, gen)
    model = model.float().to(data.device).eval()
    return model, budget


def evaluate_run(model, data, cfg, seed, steps, seconds, desc, cli, state, decide=True, run_id=None,
                 label="sweep"):
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
            raise ValueError(f"{row['macs']:,} multiply-adds per leaf is over the limit {MAX_MACS:,} ({MAX_MACS_X}x v1)")
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
    scored = score_model(model, data, eval_sets(data))
    row["val_class"], row["val_range"] = (f"{x:.6f}" for x in scored["val"][1])
    if "val_cv" in scored:
        row["val_cv_class"] = f"{scored['val_cv'][1][0]:.6f}"
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
        verdict, reason = label, ""
    elif best is None:
        verdict, reason = "keep", "first run on this snapshot: becomes the best"
    else:
        cand = {k: v[0] for k, v in scored.items()}
        key = score_key(best, cand)
        need, measured = spread_need(spread, key)
        problems, near, st = judge(best, cand, need, measured)
        row.update({k: f"{v:.6f}" for k, v in st.items()})
        verdict = "keep" if not problems else ("near" if near else "discard")
        reason = "; ".join(problems) or f"gain {st['gain_class']:.6f} " \
                                        f"(interval {st['ci_class_lo']:+.6f} to {st['ci_class_hi']:+.6f})"
        reason = f"[{key}] {reason}"
        if near:
            reason += f"; near miss: train --seed 1 and --seed 2 with --replicate {run_id}, then harness.py confirm"
    row.update(verdict=verdict, reason=reason)
    if verdict == "keep":
        make_best(state, run_id, [run_id])
    elif verdict == "replicate" and state.s.get("best") and desc.startswith(f"replicate of {state.s['best']}"):
        state.s["best_seeds"] = state.best_seeds() + [run_id]
        state.save()
    append_tsv(data.work, row)
    log(f"{verdict.upper()}: val class {row['val_class']} range {row['val_range']}"
        + (f", val_cv class {scored['val_cv'][1][0]:.6f}" if "val_cv" in scored else "")
        + (f", real leaves class {row['leaf_class']}" if leaf_names else "") + (f" -- {reason}" if reason else ""))
    return verdict, row


def main(run_fn, config, prepare_fn=None):
    """Entry point used by train.py: one run, scored against the best and logged. prepare_fn is the
    trainer's optional prepare(cfg, data): it runs first, outside the run's budget."""
    ap = argparse.ArgumentParser(description="Train one leaf net with train.py's CONFIG and apply the keep rule.")
    ap.add_argument("--desc", help="one line: what this run changes (required for a run)")
    ap.add_argument("--prepare", action="store_true",
                    help="only build the recipe's shared side data (the trainer's prepare()), then exit")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--replicate", metavar="RUN",
                    help="this is another seed of RUN (same train.py): scored and logged, not judged; "
                         "replicates of the best count toward its seed average")
    ap.add_argument("--snapshot")
    ap.add_argument("--work", default=work_dir())
    ap.add_argument("--solve-cli", default=default_cli())
    args = ap.parse_args()
    if not args.prepare and not args.desc:
        ap.error("--desc is required")
    data = Data(args.work, args.snapshot)
    prepare_once(prepare_fn, config, data)
    if args.prepare:
        print("PREPARED" if prepare_fn is not None else "PREPARED: this trainer has no prepare()")
        return
    state = State(args.work, data.snapshot)
    model, budget = train_once(run_fn, config, data, args.seed)
    steps = getattr(model, "steps_taken", "")
    log(f"trained in {budget.elapsed():.0f} s ({steps} steps)")
    if budget.elapsed() > WALL_CAP_S * 1.05:
        log("over the wall-clock cap: discarded")
        sys.exit(1)
    if args.replicate:
        desc = f"replicate of {args.replicate} seed {args.seed}: {args.desc}"
        verdict, _ = evaluate_run(model, data, config, args.seed, steps, budget.elapsed(), desc, args.solve_cli,
                                  state, decide=False, label="replicate")
    else:
        verdict, _ = evaluate_run(model, data, config, args.seed, steps, budget.elapsed(), args.desc,
                                  args.solve_cli, state)
    print(f"VERDICT: {verdict}")


# ------------------------------------------------------------- commands ----

def cmd_noise(args):
    import train
    data = Data(args.work, args.snapshot)
    state = State(args.work, data.snapshot)
    results = []
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")   # a new noise round never overwrites an older one
    prepare_once(getattr(train, "prepare", None), train.CONFIG, data)
    for seed in range(args.seeds):
        model, budget = train_once(train.run, train.CONFIG, data, seed)
        steps = getattr(model, "steps_taken", "")
        _, row = evaluate_run(model, data, train.CONFIG, seed, steps, budget.elapsed(), f"noise seed {seed}",
                              args.solve_cli, state, decide=False, run_id=f"noise-{stamp}-s{seed}")
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
    spread["runs"] = [r["run"] for r in results]
    spread.update(cv_spread(state, spread["runs"]))
    state.s["seed_spread"] = spread
    if not state.s.get("best"):
        # seed 0 (the default seed of train.py runs) is the bar: like for like, not the luckiest seed
        best = results[0]["run"]
        state.s["best"] = best
        state.s["best_seeds"] = [r["run"] for r in results]   # same setup: all of them are the best's seeds
        shutil.copy(os.path.join(state.dir, best, "leaf_net.bin"), os.path.join(state.dir, "best_leaf_net.bin"))
    state.save()
    print(json.dumps(spread, indent=1))


def cv_spread(state, runs):
    """Seed spread of the val_cv score over scored runs of one setup ({} when they lack val_cv)."""
    errs = []
    for r in runs:
        with open(os.path.join(state.dir, r, "sums.json"), encoding="utf-8") as f:
            d = json.load(f)
        if "val_cv" not in d:
            return {}
        errs.append(totals(sums_from_json(d["val_cv"]))[0])
    errs = np.array(errs)
    if len(errs) < 2:
        return {}
    return {"class_cv": float(errs.max() - errs.min()), "class_cv_std": float(errs.std(ddof=1)),
            "class_cv_errors": errs.tolist()}


def cmd_rescore(args):
    """Score every run of the snapshot on the referee's val_cv (from its exported net, on the CPU), then
    the val_cv seed spread from the noise runs."""
    work = args.work
    snap = args.snapshot or current_snapshot(work)
    sdir = os.path.join(work, "snapshots", snap)
    split = np.load(os.path.join(sdir, "split.npy"))
    val = EvalSet(sdir, split == SPLITS["val"])
    val_cv = load_val_cv(sdir, val)
    if val_cv is None:
        sys.exit(f"no referee for {snap}: run tools/leafnet/referee.py first")
    st = State(work, snap)
    done = 0
    for run in sorted(os.listdir(st.dir)):
        rdir = os.path.join(st.dir, run)
        sp, net = os.path.join(rdir, "sums.json"), os.path.join(rdir, "leaf_net.bin")
        if not (os.path.exists(sp) and os.path.exists(net)):
            continue
        with open(sp, encoding="utf-8") as f:
            d = json.load(f)
        if "val_cv" in d and not args.force:
            continue
        d["val_cv"] = sums_to_json(score_file(net, {"val_cv": val_cv})["val_cv"][0])
        with open(sp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(d, f)
        done += 1
    log(f"scored {done} runs on val_cv")
    spread = st.s.get("seed_spread")
    if spread:
        runs = spread.get("runs") or sorted(r for r in os.listdir(st.dir) if r.startswith("noise-"))
        spread.update(cv_spread(st, runs))
        spread["runs"] = runs
        st.save()
    out = {"seed_spread": {k: v for k, v in (spread or {}).items() if "class" in k and "errors" not in k}}
    if st.s.get("best"):
        g = st.group_sums(st.best_seeds())
        out["best"] = {"runs": st.best_seeds(), "val_class": totals(g["val"])[0], "val_cv_class": totals(g["val_cv"])[0]}
    out["balanced"] = {"val_class": totals(val.sums(val.base["balanced"]))[0],
                       "val_cv_class": totals(val_cv.sums(val.base["balanced"]))[0]}
    print(json.dumps(out, indent=1))


def cmd_status(args):
    work = args.work
    snap = args.snapshot or current_snapshot(work)
    st = State(work, snap)
    with open(os.path.join(work, "snapshots", snap, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    print(json.dumps({"snapshot": snap, "examples": m["examples"], "examples_by_split": m["examples_by_split"],
                      "leaf_sets": [s["name"] for s in m.get("leaf_sets", [])], "best": st.s.get("best"),
                      "best_seeds": st.best_seeds(), "ensembles": st.s.get("ensembles", []),
                      "seed_spread": st.s.get("seed_spread")}, indent=1))


def cmd_confirm(args):
    """The keep rule on seed averages: candidate runs (one setup, several seeds) vs the best's seeds."""
    work = args.work
    snap = args.snapshot or current_snapshot(work)
    st = State(work, snap)
    if not st.s.get("best"):
        sys.exit("no best run on this snapshot yet")
    against = args.against or st.best_seeds()
    if st.s["best"] not in against:
        sys.exit(f"--against must include the current best {st.s['best']}")
    runs = list(dict.fromkeys(args.runs))
    if len(runs) < 2:
        sys.exit("confirm needs at least two seeds of the candidate")
    if set(runs) & set(against):
        sys.exit("a run can't be both candidate and best")
    for r in runs + against:
        if not os.path.exists(os.path.join(st.dir, r, "sums.json")):
            sys.exit(f"{r}: no scored run in {st.dir}")
        if r in st.s.get("ensembles", []):
            sys.exit(f"{r} is an ensemble: the keep rule compares single nets (confirm its members instead)")
    spread = st.s.get("seed_spread", {})
    best, cand = st.group_sums(against), st.group_sums(runs)
    key = score_key(best, cand)
    need, measured = spread_need(spread, key, len(runs), len(against))
    problems, _, stats = judge(best, cand, need, measured)
    singles = sorted((totals(st.group_sums([r])[key])[0], r) for r in runs)
    chosen = singles[(len(singles) - 1) // 2][1]   # the median seed: neither the luckiest nor the unluckiest
    verdict = "keep" if not problems else "discard"
    reason = f"[{key}] " + ("; ".join(problems) or (f"seed-averaged gain {stats['gain_class']:.6f} "
                                                    f"(interval {stats['ci_class_lo']:+.6f} to "
                                                    f"{stats['ci_class_hi']:+.6f}), need {need:.6f}"))
    cls, rng = totals(cand["val"])
    leaf = [k for k in cand if k.startswith("leaf:")]
    row = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "snapshot": snap, "run": chosen,
           "desc": f"confirm {len(runs)} seeds ({', '.join(runs)}) vs {len(against)} ({', '.join(against)})",
           "seed": "mean", "val_class": f"{cls:.6f}", "val_range": f"{rng:.6f}",
           "leaf_class": " ".join(f"{totals(cand[k])[0]:.5f}" for k in leaf),
           "leaf_range": " ".join(f"{totals(cand[k])[1]:.6f}" for k in leaf),
           **{k: f"{v:.6f}" for k, v in stats.items()}, "verdict": verdict, "reason": reason}
    if "val_cv" in cand:
        row["val_cv_class"] = f"{totals(cand['val_cv'])[0]:.6f}"
    row["commit"], row["dirty"] = git_rev()
    row["macs"] = macs(leafnet_io.read(os.path.join(st.dir, chosen, "leaf_net.bin"))[0]["sizes"])
    if verdict == "keep":
        make_best(st, chosen, runs)
    append_tsv(work, row)
    log(f"{verdict.upper()}: seed-averaged {key} class {totals(cand[key])[0]:.6f} vs {totals(best[key])[0]:.6f} "
        f"-- {reason}"
        + (f"; new best {chosen}" if verdict == "keep" else ""))
    print(f"VERDICT: {verdict}")


def cmd_ensemble(args):
    """One net file whose output is the mean of several kept runs' outputs (default: the best and its
    seed replicates). Scored like a run and checked against its members' average; never judged by the
    keep rule and never the best."""
    work = args.work
    snap = args.snapshot or current_snapshot(work)
    st = State(work, snap)
    runs = list(dict.fromkeys(args.runs or st.best_seeds()))
    if len(runs) < 2:
        sys.exit("an ensemble needs at least two runs: train seed copies of the best first "
                 "(train.py --seed N --replicate RUN --desc ...)")
    members = []
    for r in runs:
        net = os.path.join(st.dir, r, "leaf_net.bin")
        if not (os.path.exists(net) and os.path.exists(os.path.join(st.dir, r, "sums.json"))):
            sys.exit(f"{r}: no scored run in {st.dir}")
        ms = leafnet_io.read_members(net)[1]
        if len(ms) != 1:
            sys.exit(f"{r} is an ensemble itself: list its members instead")
        members.append(ms[0])
    total = sum(macs(leafnet_io.layer_sizes(m[0])) for m in members)
    if total > MAX_ENSEMBLE_MACS:
        sys.exit(f"{total:,} multiply-adds per leaf is over the ensemble limit {MAX_ENSEMBLE_MACS:,} "
                 f"({MAX_ENSEMBLE_MACS_X}x v1)")
    ens_id = args.name or f"ens{len(runs)}-{runs[0]}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", ens_id):
        sys.exit(f"--name {ens_id!r}: letters, digits, '.', '_' and '-' only")
    rdir = os.path.join(st.dir, ens_id)
    cfg_path = os.path.join(rdir, "config.json")
    if os.path.exists(rdir):
        # a net's name is permanent (saved games refer to it): the same members may be rebuilt, others may not
        had = None
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                had = json.load(f).get("ensemble")
        if had != runs:
            sys.exit(f"{ens_id} already exists with other contents: pick another --name")
    os.makedirs(rdir, exist_ok=True)
    net_path, tmp = os.path.join(rdir, "leaf_net.bin"), os.path.join(rdir, "leaf_net.bin.tmp")
    desc = f"ensemble: mean of {len(runs)} nets ({', '.join(runs)})"
    row = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "snapshot": snap, "run": ens_id,
           "desc": desc, "seed": "ens", "macs": total}
    row["commit"], row["dirty"] = git_rev()
    leafnet_io.write_ensemble(tmp, members, extra={"snapshot": snap, "run": ens_id, "members": runs,
                                                   "trainer": "tools/leafnet/harness.py ensemble"})
    sdir, sets = scoring_sets(work, snap)
    try:
        row["parity"] = f"{file_parity(args.solve_cli, tmp, os.path.join(sdir, 'inputs_val.jsonl'), sets['val']):.2e}"
        if float(row["parity"]) > PARITY_TOL:
            raise ValueError(f"Rust and numpy outputs differ by {row['parity']} (> {PARITY_TOL})")
        scored = score_file(tmp, sets)
        cand = {k: v[0] for k, v in scored.items()}
        # squared error is convex, so a mean of nets can never score worse than its members' average:
        # anything else means the file is not the mean of these runs
        problems, _, stats = judge(st.group_sums(runs), cand, 0.0)
        if problems:
            raise ValueError("worse than its members' average: " + "; ".join(problems))
    except ValueError as e:
        os.remove(tmp)
        row.update(verdict="rejected", reason=str(e))
        append_tsv(work, row)
        log(f"REJECTED: {e}")
        print("VERDICT: rejected")
        return
    key = score_key(cand, cand)
    row["val_class"], row["val_range"] = (f"{x:.6f}" for x in scored["val"][1])
    if "val_cv" in scored:
        row["val_cv_class"] = f"{scored['val_cv'][1][0]:.6f}"
    leaf = [k for k in scored if k.startswith("leaf:")]
    if leaf:
        row["leaf_class"] = " ".join(f"{scored[k][1][0]:.5f}" for k in leaf)
        row["leaf_range"] = " ".join(f"{scored[k][1][1]:.6f}" for k in leaf)
    row.update({k: f"{v:.6f}" for k, v in stats.items()})
    reason = (f"[{key}] {stats['gain_class']:.6f} better than its members' average "
              f"(interval {stats['ci_class_lo']:+.6f} to {stats['ci_class_hi']:+.6f})")
    row.update(verdict="ensemble", reason=reason)
    with open(os.path.join(rdir, "sums.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({k: sums_to_json(v[0]) for k, v in scored.items()}, f)
    with open(cfg_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"ensemble": runs, "desc": desc, "macs": total, "scores": {k: v[1] for k, v in scored.items()}},
                  f, indent=1)
    os.replace(tmp, net_path)
    st.s["ensembles"] = [e for e in st.s.get("ensembles", []) if e != ens_id] + [ens_id]
    st.save()
    append_tsv(work, row)
    log(f"ENSEMBLE {ens_id}: {key} class {scored[key][1][0]:.6f}, val class {row['val_class']} range {row['val_range']}"
        + (f", real leaves class {row['leaf_class']}" if leaf else "") + f" -- {reason}")
    print("VERDICT: ensemble")


def cmd_final(args):
    """Score a run's exported net on the test split and the real-leaf sets, against today's models."""
    data = Data(args.work, args.snapshot, device="cpu", with_test=True)
    st = State(args.work, data.snapshot)
    run = args.run or st.s.get("best")
    sets = {"test": data.test, **{f"leaf:{k}": v for k, v in data.leaf.items()}}
    scored = score_file(os.path.join(st.dir, run, "leaf_net.bin"), sets)
    report = {"run": run, "snapshot": data.snapshot}
    for name, es in sets.items():
        sums = {"net": scored[name][0], **{m: es.sums(es.base[m]) for m in MODELS}}
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
    c = sub.add_parser("confirm", help="keep rule on seed averages: seeds of a near miss vs the best's seeds")
    c.add_argument("runs", nargs="+", help="the candidate's runs (same train.py, different seeds)")
    c.add_argument("--against", nargs="+", help="the best's seed runs (default: the best and its replicates)")
    r = sub.add_parser("rescore", help="add the referee's val_cv score to every run, and its seed spread")
    r.add_argument("--force", action="store_true", help="rescore runs that already have val_cv")
    e = sub.add_parser("ensemble", help="one net file that averages several kept runs (default: the best's seeds)")
    e.add_argument("runs", nargs="*", help="the runs to average (default: the best and its seed replicates)")
    e.add_argument("--name", help="the ensemble's run id (default: ensN-FIRSTRUN)")
    f = sub.add_parser("final", help="score a run on the TEST split (milestones only)")
    f.add_argument("run", nargs="?")
    args = ap.parse_args()
    {"noise": cmd_noise, "status": cmd_status, "confirm": cmd_confirm, "rescore": cmd_rescore,
     "ensemble": cmd_ensemble, "final": cmd_final}[args.cmd](args)


if __name__ == "__main__":
    cli()
