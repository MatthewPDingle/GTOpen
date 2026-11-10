#!/usr/bin/env python3
"""Optuna sweep over train.py's numeric CONFIG (part of the frozen tooling).

    python tools/leafnet/sweep.py --trials 20 [--keys lr,weight_decay,hidden,depth,batch]

Each trial trains train.run with one sampled CONFIG under the same fixed
budget, scores it on the validation split, and logs it to results.tsv with
verdict "sweep". The sweep minimizes the keep rule's score: the referee's
low-noise val_cv class error when the snapshot has a referee, else the raw
validation class error. Sweeps never change the best run: apply the winning values
to CONFIG in train.py and run train.py normally, so the keep rule decides.
Configurations over the harness's multiply-add limit are skipped without
training. The study is stored in WORK/runs/<snapshot>/sweeps.db, so a sweep
can be resumed with the same --study name.
"""

import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import harness  # noqa: E402
import train  # noqa: E402

# search space for numeric CONFIG keys (only keys present in CONFIG are swept)
SPACE = {
    "lr": ("log", 1e-4, 3e-3),
    "weight_decay": ("log", 1e-8, 1e-3),
    "hidden": ("cat", [256, 384, 512, 640, 768, 1024]),
    "depth": ("cat", [1, 2, 3, 4]),
    "batch": ("cat", [128, 256, 512, 1024, 2048]),
    "lr_drop": ("float", 0.1, 0.7),
    "last_layer_scale": ("log", 0.01, 1.0),
}


def mlp_sizes(cfg, data):
    """Sizes of the plain MLP train.build makes for this cfg (for the cost check)."""
    return [data.n_in] + [cfg["hidden"]] * cfg["depth"] + [data.n_out]


def main():
    import optuna
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--keys", default=",".join(k for k in SPACE if k in train.CONFIG))
    ap.add_argument("--study", default="sweep-" + datetime.date.today().isoformat())
    ap.add_argument("--seed", type=int, default=0, help="training seed for every trial")
    ap.add_argument("--snapshot")
    ap.add_argument("--work", default=harness.work_dir())
    ap.add_argument("--solve-cli", default=harness.default_cli())
    args = ap.parse_args()
    keys = [k for k in args.keys.split(",") if k]
    for k in keys:
        if k not in SPACE or k not in train.CONFIG:
            sys.exit(f"cannot sweep {k!r}: it must be in both SPACE and train.CONFIG")
    data = harness.Data(args.work, args.snapshot)
    state = harness.State(args.work, data.snapshot)
    storage = "sqlite:///" + os.path.join(state.dir, "sweeps.db").replace("\\", "/")
    study = optuna.create_study(study_name=args.study, storage=storage, direction="minimize", load_if_exists=True,
                                sampler=optuna.samplers.TPESampler(seed=args.seed))

    def objective(trial):
        cfg = dict(train.CONFIG)
        for k in keys:
            kind, *spec = SPACE[k]
            if kind == "log":
                cfg[k] = trial.suggest_float(k, spec[0], spec[1], log=True)
            elif kind == "float":
                cfg[k] = trial.suggest_float(k, spec[0], spec[1])
            else:
                cfg[k] = trial.suggest_categorical(k, spec[0])
        if "hidden" in cfg and "depth" in cfg and harness.macs(mlp_sizes(cfg, data)) > harness.MAX_MACS:
            raise optuna.TrialPruned("over the multiply-add limit")
        model, budget = harness.train_once(train.run, cfg, data, args.seed)
        verdict, row = harness.evaluate_run(model, data, cfg, args.seed, getattr(model, "steps_taken", ""),
                                            budget.elapsed(), f"{args.study} trial {trial.number}", args.solve_cli,
                                            state, decide=False)
        if verdict == "rejected":
            raise optuna.TrialPruned(row.get("reason", "rejected"))
        return float(row.get("val_cv_class") or row["val_class"])

    study.optimize(objective, n_trials=args.trials)
    best = study.best_trial
    score = "val_cv" if data.val_cv is not None else "val"
    print(f"best trial {best.number}: {score} class error {best.value:.6f}")
    print("apply to train.py CONFIG, then run train.py so the keep rule decides:")
    for k, v in best.params.items():
        print(f"    {k!r}: {v!r},")


if __name__ == "__main__":
    main()
