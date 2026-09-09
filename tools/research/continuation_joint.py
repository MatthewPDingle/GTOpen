"""Frozen stratified continuation experiment; no app or private histories used.

prepare: create deterministic disjoint board manifest (never overwrites it).
fit: use FIT jobs only; freeze the candidate before inspecting holdout outcomes.
report: compare board-independent estimates with weighted holdout expectations.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import math
import os
import subprocess
import time
from datetime import datetime, timezone

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/preflop-evolution/continuation/pass2"
SEED = "gtopen-continuation-v2-20260909"
RANKS = "23456789TJQKA"
SUITS = "cdhs"


class IntegrityError(ValueError):
    """A frozen experiment input or checkpoint failed validation."""


def require(condition, message):
    if not condition:
        raise IntegrityError(message)


def canon(cards):
    return min(tuple(sorted((4*(c//4)+p[c%4] for c in cards), reverse=True)) for p in itertools.permutations(range(4)))


def label(cards):
    return "".join(RANKS[c//4]+SUITS[c%4] for c in cards)


def canonical_inventory():
    counts = {}
    for cards in itertools.combinations(range(52), 3):
        k = canon(cards)
        counts[k] = counts.get(k, 0)+1
    assert len(counts) == 1755 and sum(counts.values()) == 22100
    return counts


def stratum(cards):
    ranks = [c//4 for c in cards]
    hi = max(ranks)
    return ("A" if hi == 12 else "KQ" if hi >= 10 else "JT" if hi >= 8 else "9-low") + ("/paired" if len(set(ranks)) < 3 else "/unpaired")


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "manifest.json"
    if path.exists():
        print("Existing frozen manifest retained:", path)
        return
    inventory = canonical_inventory()
    excluded = {canon([4*RANKS.index(b[i])+SUITS.index(b[i+1]) for i in range(0, 6, 2)]) for b in ["As7h2d", "Ts9s8d", "7s7h2d"]}
    groups = {}
    for cards, multiplicity in inventory.items():
        if cards not in excluded:
            groups.setdefault(stratum(cards), []).append((cards, multiplicity))
    boards = []
    for key, rows in sorted(groups.items()):
        rows.sort(key=lambda x: hashlib.sha256((SEED+label(x[0])).encode()).digest())
        for i, (cards, multiplicity) in enumerate(rows[:4]):
            boards.append(dict(board=label(cards), iso_weight=multiplicity, stratum=key,
                partition="fit" if i < 2 else "holdout", cv_fold=i if i < 2 else None,
                population_in_stratum=len(rows), sampled_in_partition=2,
                inclusion_probability=2/len(rows)))
    assert len(boards) == 32
    assert len({b["board"] for b in boards}) == 32
    medium = "22+,A2s+,K9s+,QTs+,JTs,T9s,98s,87s,76s,ATo+,KJo+,QJo"
    tight = "88+,ATs+,KQs,AQo+"
    cases = {"medium_symmetric": [medium, medium], "caller_vs_raiser": [medium, tight], "raiser_vs_caller": [tight, medium]}
    sizing = {"bet": [{"PotPct": 50}], "raise": [{"PotPct": 100}], "donk": []}
    jobs = []
    for partition in ["fit", "holdout"]:
        for board in boards:
            if board["partition"] != partition:
                continue
            for case, ranges in cases.items():
                for rake in [0, 5]:
                    config = dict(board=board["board"], range_oop=ranges[0], range_ip=ranges[1],
                        tree=dict(starting_pot=20, effective_stack=80, rake_pct=rake/100, rake_cap=3,
                                  oop=[sizing]*3, ip=[sizing]*3, max_raises=1, add_allin=False, allin_threshold=.85))
                    jobs.append(dict(**board, case=case, rake_pct=rake,
                        id=f"{case}-{board['board']}-r{rake}", config=config))
    manifest = dict(schema=1, seed=SEED, boards=boards, cases=cases, jobs=jobs,
        excluded_old_boards=sorted(label(b) for b in excluded),
        universe="1752 canonical flops after excluding the three previously inspected audit boards",
        sampling="Uniform pseudo-random without replacement within 8 high-card/pairedness strata; fixed seed. 2 fit and 2 disjoint holdout boards per stratum.",
        weighting="iso_weight * compatible_pair_mass / inclusion_probability, normalized within each case/rake/partition (ratio estimate).",
        candidate_family="Rake multiplier plus OOP value transfer linear in preflop range equity. Inputs never include the flop or flop-specific equity.",
        ridge_candidates=[0, .01, .1, 1], cv="2 folds: one fit board per stratum per fold, all ranges/rakes on the same board kept together",
        reference_target_gap_pct=.3, reference_max_iterations=500, threads=4)
    manifest["id"] = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    path.write_text(json.dumps(manifest, indent=2)+"\n")
    print(f"Frozen {len(jobs)} jobs: 96 fit + 96 holdout. Manifest {manifest['id']}")


def provenance_signature(provenance):
    return (provenance["binary_sha256"], *(provenance["source_sha256"][path] for path in
            ["cache/realization_fit.json", "cache/preflop_eq169.bin"]))


def validate_provenance(rows):
    signatures = {provenance_signature(row["provenance"]) for row in rows}
    require(len(signatures) == 1, "Corpus mixes executable or input-cache hashes; use a separate experiment for changed inputs")
    return next(iter(signatures))


def load(partition):
    manifest = json.loads((OUT/"manifest.json").read_text())
    rows = []
    missing = []
    for job in manifest["jobs"]:
        if job["partition"] != partition:
            continue
        path = OUT/"jobs"/(job["id"]+".json")
        if not path.exists():
            missing.append(job["id"])
            continue
        row = json.loads(path.read_text())
        require(row["manifest_id"] == manifest["id"] and row["job"] == job, f"Checkpoint disagrees with frozen manifest: {job['id']}")
        require(row["target_met"] is True, f"Unconverged reference {job['id']}")
        require(0 <= row["gap_pct_pot"] <= manifest["reference_target_gap_pct"], "Invalid reference gap")
        require(row.get("provenance", {}).get("binary_sha256"), f"Missing executable provenance: {job['id']}")
        row["weight"] = job["iso_weight"]*row["compatible_pair_mass"]/job["inclusion_probability"]
        rows.append(row)
    if missing:
        raise ValueError(f"{len(missing)} {partition} jobs remain; first {missing[0]}")
    validate_provenance(rows)
    return manifest, rows


def normalized_weights(rows):
    # Give each range/rake configuration equal model-fitting importance; use
    # the blocker/inclusion weighted population within that configuration.
    w = np.array([r["weight"] for r in rows], dtype=float)
    for case in {r["job"]["case"] for r in rows}:
        for rake in [0, 5]:
            mask = np.array([r["job"]["case"] == case and r["job"]["rake_pct"] == rake for r in rows])
            w[mask] /= w[mask].sum()
    return w/w.sum()


def q0(row):
    # Current engine equity estimate is an available PRE-FLOP input; its tiny
    # finite-Monte-Carlo diagonal asymmetry is not allowed to create pot value.
    return float(np.clip(row["preflop_leaf"]["equity"][0], 0, 1))


def train(rows, ridge):
    w = normalized_weights(rows)
    raked = np.array([r["job"]["rake_pct"] > 0 for r in rows])
    rake_multipliers = np.array([r["reference_expected_rake_bb"]/(20*.05) for r in rows])
    multiplier = float(np.average(rake_multipliers[raked], weights=w[raked]))
    x = np.array([[1, q0(r)-.5] for r in rows])
    y = np.array([(r["reference_ev_bb"][0]-(20-r["reference_expected_rake_bb"])*q0(r))/20 for r in rows])
    penalty = np.diag([0, ridge])
    beta = np.linalg.solve(x.T@(w[:, None]*x)+penalty, x.T@(w*y))
    return dict(rake_multiplier=multiplier, transfer_intercept=float(beta[0]), transfer_equity_slope=float(beta[1]), ridge=ridge)


def predict(row, model):
    config = row["job"]["config"]["tree"]
    pot, stack, rate, cap = [config[k] for k in ["starting_pot", "effective_stack", "rake_pct", "rake_cap"]]
    limit = cap if cap > 0 else math.inf  # Solver convention: cap 0 means uncapped.
    lower = min(pot*rate, limit)
    upper = min((pot+2*stack)*rate, limit)
    rake = float(np.clip(pot*rate*model["rake_multiplier"], lower, upper))
    q = q0(row)
    oop = (pot-rake)*q + pot*(model["transfer_intercept"]+model["transfer_equity_slope"]*(q-.5))
    oop = float(np.clip(oop, -stack, pot-rake+stack))
    ip = pot-rake-oop
    assert abs(oop+ip+rake-pot) < 1e-9
    return np.array([oop, ip]), rake


def fit():
    manifest, rows = load("fit")
    artifact_path = OUT/"joint-v1.json"
    if artifact_path.exists():
        existing = json.loads(artifact_path.read_text())
        require(existing["manifest_id"] == manifest["id"], "Frozen fit belongs to another manifest")
        for job_id, expected in existing["fit_data_sha256"].items():
            require(hashlib.sha256((OUT/"jobs"/(job_id+".json")).read_bytes()).hexdigest() == expected, "Frozen fit source changed")
        reproduced = train(rows, existing["parameters"]["ridge"])
        for key, value in reproduced.items():
            require(math.isclose(value, existing["parameters"][key], rel_tol=1e-12, abs_tol=1e-12), "Frozen parameters no longer reproduce")
        (OUT/"fit-verification.json").write_text(json.dumps(dict(
            artifact_sha256=hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
            verified_utc=datetime.now(timezone.utc).isoformat(),
            fitting_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            parameters_reproduced=True, fit_source_hashes_verified=True), indent=2)+"\n")
        print("Frozen candidate retained:", artifact_path)
        return
    grid = []
    for ridge in manifest["ridge_candidates"]:
        errors = []
        for fold in [0, 1]:
            training = [r for r in rows if r["job"]["cv_fold"] != fold]
            validation = [r for r in rows if r["job"]["cv_fold"] == fold]
            model = train(training, ridge)
            w = normalized_weights(validation)
            errors.append(float(sum(weight*np.square(predict(r, model)[0]-r["reference_ev_bb"]).mean() for r, weight in zip(validation, w))))
        grid.append(dict(ridge=ridge, cv_mse_bb2=float(np.mean(errors)), folds=errors))
    best = min(grid, key=lambda v: v["cv_mse_bb2"])
    artifact = dict(schema=1, version="continuation-joint-research-v1", research_only=True,
        manifest_id=manifest["id"], parameters=train(rows, best["ridge"]), selection=grid,
        input_scope="preflop range equity, pot, stack, rake rate and cap only; no board-conditioned input",
        validated_domain="These three fixed ranges at 20 bb pot, 80 bb behind, 0/5% rake capped at 3 bb, restricted postflop menu. No range or format holdout yet.",
        fit_job_ids=[r["job"]["id"] for r in rows],
        fit_data_sha256={r["job"]["id"]: hashlib.sha256((OUT/"jobs"/(r["job"]["id"]+".json")).read_bytes()).hexdigest() for r in rows})
    artifact_path.write_text(json.dumps(artifact, indent=2)+"\n")
    print(json.dumps(dict(parameters=artifact["parameters"], selection=grid), indent=2))


def grouped(rows, candidate, resample=None):
    result = []
    for case in sorted({r["job"]["case"] for r in rows}):
        for rake in [0, 5]:
            chosen = [r for r in rows if r["job"]["case"] == case and r["job"]["rake_pct"] == rake]
            require(all(r["preflop_leaf"] == chosen[0]["preflop_leaf"] for r in chosen), "Board-independent baseline changed within a configuration")
            w = np.array([r["weight"]*(1 if resample is None else resample[r["job"]["board"]]) for r in chosen])
            ref = np.average([r["reference_ev_bb"] for r in chosen], weights=w, axis=0)
            predictions = {m: np.array(chosen[0]["preflop_leaf"][m+"_bb"]) for m in ["raw", "static", "calibrated"]}
            predictions["joint"] = predict(chosen[0], candidate)[0]
            result.append(dict(case=case, rake_pct=rake, reference_ev_bb=ref.tolist(),
                               predictions={k: v.tolist() for k, v in predictions.items()},
                               abs_error_bb={k: abs(v-ref).tolist() for k, v in predictions.items()},
                               reference_expected_rake_bb=float(20-ref.sum()),
                               joint_expected_rake_bb=predict(chosen[0], candidate)[1]))
    return result


def report():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    manifest, rows = load("holdout")
    _, fit_rows = load("fit")
    validate_provenance(fit_rows+rows)
    artifact = json.loads((OUT/"joint-v1.json").read_text())
    require(artifact["manifest_id"] == manifest["id"], "Frozen fit belongs to another manifest")
    for job_id, expected in artifact["fit_data_sha256"].items():
        require(hashlib.sha256((OUT/"jobs"/(job_id+".json")).read_bytes()).hexdigest() == expected, "Frozen fit source changed")
    require(set(artifact["fit_job_ids"]).isdisjoint(r["job"]["id"] for r in rows), "Fit and evaluation jobs overlap")
    candidate = artifact["parameters"]
    groups = grouped(rows, candidate)
    models = ["raw", "static", "calibrated", "joint"]
    errors = {m: float(np.mean([g["abs_error_bb"][m] for g in groups])) for m in models}
    strata = {s: [b["board"] for b in manifest["boards"] if b["partition"] == "holdout" and b["stratum"] == s] for s in sorted({b["stratum"] for b in manifest["boards"]})}
    rng = np.random.default_rng(20260909)
    draws = []
    for _ in range(2000):
        weights = {b: 0 for boards in strata.values() for b in boards}
        for boards in strata.values():
            for b in rng.choice(boards, size=len(boards), replace=True):
                weights[b] += 1
        sampled = grouped(rows, candidate, weights)
        e = {m: float(np.mean([g["abs_error_bb"][m] for g in sampled])) for m in models}
        draws.append([e[m]-e["joint"] for m in models[:-1]])
    intervals = {m: np.quantile(np.array(draws)[:, i], [.025, .975]).tolist() for i, m in enumerate(models[:-1])}
    all_rows = fit_rows+rows
    reference_validation = dict(
        jobs=len(all_rows), target_met=sum(r["target_met"] for r in all_rows),
        gap_pct_pot_min=min(r["gap_pct_pot"] for r in all_rows),
        gap_pct_pot_max=max(r["gap_pct_pot"] for r in all_rows),
        iterations_min=min(r["iterations"] for r in all_rows), iterations_max=max(r["iterations"] for r in all_rows),
        accumulated_job_wall_seconds=sum(r["build_seconds"]+r["solve_seconds"]+r["query_seconds"] for r in all_rows),
        max_arena_mib=max(r["arena_bytes"] for r in all_rows)/2**20,
        max_tree_mib=max(r["tree_bytes"] for r in all_rows)/2**20,
        zero_rake_max_accounting_residual_bb=max(abs(r["reference_expected_rake_bb"]) for r in all_rows if r["job"]["rake_pct"] == 0),
        max_equity_complement_residual=max(abs(sum(r["reference_equity"])-1) for r in all_rows))
    accounting = dict(
        joint_max_residual_bb=max(abs(sum(g["predictions"]["joint"])+g["joint_expected_rake_bb"]-20) for g in groups),
        zero_rake_unallocated_bb={g["case"]: {m: 20-sum(g["predictions"][m]) for m in models} for g in groups if g["rake_pct"] == 0})
    summary = dict(schema=1, manifest_id=manifest["id"], model=artifact["version"], weighted_holdout_groups=groups,
        artifact_sha256=hashlib.sha256((OUT/"joint-v1.json").read_bytes()).hexdigest(),
        evaluation_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        holdout_data_sha256={r["job"]["id"]: hashlib.sha256((OUT/"jobs"/(r["job"]["id"]+".json")).read_bytes()).hexdigest() for r in rows},
        aggregate_mae_bb=errors, error_reduction_vs_joint_95_interval=intervals,
        reference_validation=reference_validation, accounting=accounting,
        uncertainty="Conditional on the frozen fit: paired within-stratum bootstrap of 2 holdout boards per stratum, keeping all cases/rakes for a board together. Small-sample intervals; no uncertainty for unseen range families or bet menus.",
        no_production_promotion=True)
    (OUT/"evaluation.json").write_text(json.dumps(summary, indent=2)+"\n")
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.7))
    colors = ["#858b92", "#bf873c", "#9859ad", "#3283a8"]
    axes[0].bar(models, [errors[m] for m in models], color=colors)
    axes[0].set_ylabel("Mean absolute error (bb per player's value)")
    axes[0].set_title("Weighted held-out preflop expectations")
    for x, m in enumerate(models):
        axes[0].text(x, errors[m], f"{errors[m]:.3f}", ha="center", va="bottom")
    x = np.arange(len(groups))
    axes[1].bar(x-.16, [g["reference_expected_rake_bb"] for g in groups], width=.3, color="#6e7981", label="Weighted held-out reference")
    axes[1].bar(x+.16, [g["joint_expected_rake_bb"] for g in groups], width=.3, color="#3283a8", label="Joint candidate")
    axes[1].set_xticks(x, [g["case"].replace("_", "\n")+f"\n{g['rake_pct']}%" for g in groups], fontsize=8)
    axes[1].set_ylabel("Expected rake (bb)")
    axes[1].set_title("Rake response with fixed reaching ranges")
    axes[1].set_ylim(0, max(g["reference_expected_rake_bb"] for g in groups)*1.28)
    axes[1].legend(fontsize=8)
    fig.suptitle("Continuation pass 2 · research candidate, unchanged production default")
    fig.tight_layout()
    fig.savefig(OUT/"holdout.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, m in enumerate(models[:-1]):
        lower, upper = intervals[m]
        gain = errors[m]-errors["joint"]
        ax.plot([lower, upper], [i, i], color=colors[i], linewidth=3)
        ax.scatter([gain], [i], color=colors[i], s=45, zorder=3)
        ax.annotate(f"{gain:.3f} [{lower:.3f}, {upper:.3f}]", (upper, i), xytext=(7, 0), textcoords="offset points", va="center", fontsize=9)
    ax.axvline(0, color="#858b92", linestyle="--", linewidth=1)
    ax.set_yticks(range(3), models[:-1])
    ax.set_ylim(-.6, 2.6)
    ax.margins(x=.35)
    ax.set_xlabel("Baseline MAE − joint MAE (bb per player; positive favors joint)")
    ax.set_title("Paired improvement · conditional 95% bootstrap interval")
    fig.tight_layout()
    fig.savefig(OUT/"gain-intervals.png", dpi=160)
    plt.close(fig)
    progress()
    print(json.dumps(dict(errors=errors, gain_intervals=intervals), indent=2))


def progress():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    manifest = json.loads((OUT/"manifest.json").read_text())
    rows = [json.loads(p.read_text()) for p in (OUT/"jobs").glob("*.json")]
    byid = {r["job"]["id"]: r for r in rows}
    ordered = [byid[j["id"]] for j in manifest["jobs"] if j["id"] in byid]
    if not ordered:
        return
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    x = np.arange(1, len(ordered)+1)
    colors = ["#3283a8" if r["job"]["partition"] == "fit" else "#9859ad" for r in ordered]
    axes[0].plot(x, np.cumsum([r["build_seconds"]+r["solve_seconds"]+r["query_seconds"] for r in ordered])/60)
    axes[0].set_ylabel("Accumulated CPU-job wall time (minutes)")
    axes[1].scatter(x, [r["gap_pct_pot"] for r in ordered], c=colors, s=12)
    axes[1].axhline(.3, color="#bf873c", ls="--")
    axes[1].set_ylabel("Final best-response gap (% pot)")
    axes[2].scatter(x, [r["arena_bytes"]/2**20 for r in ordered], c=colors, s=12)
    axes[2].set_ylabel("Solver arena allocation (MiB)")
    for ax in axes:
        ax.set_xlabel("Completed job")
    fig.suptitle(f"Continuation corpus · {len(ordered)}/{len(manifest['jobs'])} jobs · blue fit, purple holdout · 4 CPU threads/job")
    fig.tight_layout()
    fig.savefig(OUT/"progress.png", dpi=150)
    plt.close(fig)
    (OUT/"progress.json").write_text(json.dumps(dict(completed=len(ordered), total=len(manifest["jobs"]),
        target_met=sum(r["target_met"] for r in ordered),
        wall_seconds=sum(r["build_seconds"]+r["solve_seconds"]+r["query_seconds"] for r in ordered),
        max_arena_mib=max(r["arena_bytes"] for r in ordered)/2**20), indent=2)+"\n")


def run():
    """Checkpointed CPU worker; freeze fit before launching any holdout job."""
    manifest = json.loads((OUT/"manifest.json").read_text())
    checkpoints = [OUT/"jobs"/(job["id"]+".json") for job in manifest["jobs"]]
    if all(path.exists() and json.loads(path.read_text()).get("target_met") for path in checkpoints):
        fit()
        report()
        return  # An archived complete corpus does not need to rerun its executable.
    binary = ROOT/("target/release/examples/continuation_joint"+(".exe" if os.name == "nt" else ""))
    if not binary.exists():
        raise ValueError("Build the continuation_joint example first")
    provenance = dict(started_utc=datetime.now(timezone.utc).isoformat(),
        binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        source_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ["crates/solver/examples/continuation_joint.rs", "crates/solver/src/cfr.rs", "crates/solver/src/best_response.rs",
             "crates/solver/src/preflop/mod.rs", "cache/realization_fit.json", "cache/preflop_eq169.bin"]})
    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    (OUT/("run-"+provenance["binary_sha256"][:12]+"-"+run_stamp+".json")).write_text(json.dumps(provenance, indent=2)+"\n")
    workers = int(os.environ.get("CONTINUATION_WORKERS", "1"))
    require(workers in [1, 2], "One or two independent 4-thread workers are supported.")
    for checkpoint in (OUT/"jobs").glob("*.json"):
        previous = json.loads(checkpoint.read_text())
        require(provenance_signature(previous["provenance"]) == provenance_signature(provenance), "Resume executable or input-cache differs from accepted checkpoints")
    for partition in ["fit", "holdout"]:
        env = dict(os.environ, CONTINUATION_PARTITION=partition, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                   CONTINUATION_PROVENANCE=json.dumps(provenance), CONTINUATION_SHARDS="2")
        env.pop("CONTINUATION_JOB_LIMIT", None)
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        pending = [0, 1]
        active = []
        last_count = -1
        while pending or active:
            while pending and len(active) < workers:
                for source in ["cache/realization_fit.json", "cache/preflop_eq169.bin"]:
                    require(hashlib.sha256((ROOT/source).read_bytes()).hexdigest() == provenance["source_sha256"][source], "Continuation input cache changed during corpus collection")
                shard = pending.pop(0)
                log = (OUT/f"worker-{partition}-{shard}.log").open("a")
                worker = subprocess.Popen([str(binary)], cwd=ROOT, env=dict(env, CONTINUATION_SHARD=str(shard)),
                    stdout=log, stderr=subprocess.STDOUT, text=True, creationflags=creationflags)
                active.append((worker, log, shard))
                print(f"Started {partition} shard {shard}, PID {worker.pid}, 4 CPU threads", flush=True)
            for worker, log, shard in list(active):
                result = worker.poll()
                if result is not None:
                    log.close()
                    active.remove((worker, log, shard))
                    if result != 0:
                        for other, other_log, _ in active:
                            other.terminate(); other.wait(); other_log.close()
                        raise RuntimeError(f"{partition} shard {shard} failed; checkpoints retained")
            count = len(list((OUT/"jobs").glob("*.json")))
            if count != last_count:
                progress()
                print(f"Corpus progress: {count}/192 complete ({partition})", flush=True)
                last_count = count
            if active:
                time.sleep(5)
        if partition == "fit":
            fit()  # This function reads no holdout file.
    report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "fit", "report", "progress", "run"])
    args = parser.parse_args()
    globals()[args.command]()
