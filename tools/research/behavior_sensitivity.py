"""Fixed-opponent preflop strategy sensitivity, isolated from the desktop app.

The odds perturbations are explicit research assumptions, NOT confidence bounds.
Public output contains aggregate policies, metrics and charts; no raw histories.
"""
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

os.environ["RAYON_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
from scipy.optimize import linprog
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "research/preflop-evolution/behavior"
WORLD_LABELS = ["Legacy", "Contextual v1", "Half call odds", "Double call odds"]
COLORS = ["#8492a6", "#55ae80", "#58a5ce", "#ce9558"]


def config(players, raises):
    return dict(positions={3:["BTN","SB","BB"],6:["UTG","HJ","CO","BTN","SB","BB"]}[players],
        stack=100., posts=[0.]*(players-2)+[.5,1.], ante=0., limp=True,
        open_raises=[2.5], raise_mults=[2.,2.5] if raises==3 else [2.,3.],
        max_raises=raises, add_allin=False, allin_threshold=.85,
        rake_pct=5., rake_cap=3., no_flop_no_drop=True, realization="calibrated", call_only_seats=[])


def scenarios():
    return [dict(name="3p BTN",cfg=config(3,3),hero=0,focal_history=[]),
        dict(name="3p BB",cfg=config(3,3),hero=2,focal_history=["raise","call"]),
        dict(name="6p BTN",cfg=config(6,2),hero=3,focal_history=["fold"]*3),
        dict(name="6p SB",cfg=config(6,2),hero=4,focal_history=["fold"]*3+["raise"])]


def source_support(path, cheap=.25):
    if not path.exists():
        return dict(available=False,note="Private aggregate analysis unavailable on this machine; solve study remains reproducible from published models.")
    analysis=json.loads(path.read_text(encoding="utf-8"))
    selected=[];all_decisions=0;session_count=0;hands=set();prices={"up_to_15pct":0,"15_to_25pct":0};entries={};positions={};depths={};tables={};actions={}
    for session in analysis["sessions"]:
        touched=False
        for key,count in session["reraise_cells"].items():
            state,action=key.split("|");n,pos,entry,depth,price,invested,remaining,hand=state.split("/")
            all_decisions+=count;h=int(hand)
            if entry=="cold" or float(price)>cheap or not (h//13<h%13 and h%13<9):continue
            touched=True;hands.add(h);selected.append(count)
            price_group="up_to_15pct" if float(price)<=.15 else "15_to_25pct"
            prices[price_group]+=count;entries[entry]=entries.get(entry,0)+count
            positions[pos]=positions.get(pos,0)+count;depths[depth]=depths.get(depth,0)+count
            tables[n]=tables.get(n,0)+count;actions[action]=actions.get(action,0)+count
        session_count+=int(touched)
    return dict(available=True,source_hands=analysis["audit"]["accepted"],total_known_card_reraise_decisions=all_decisions,
        targeted_decisions=sum(selected),targeted_sessions=session_count,targeted_hand_classes=len(hands),possible_hand_classes=36,
        by_price=prices,by_entry=entries,by_position=positions,by_raise_depth=depths,by_table_size=tables,by_action=actions,
        definition="Known-card after-entry re-raises, nominal call price <=25%, offsuit T-high or lower; all available source periods pooled.",
        note="Counts do not make individual hand/position/price estimates precise. All these source periods have already been inspected; none is a fresh holdout.")


def enrich(result):
    for scenario in result["scenarios"]:
        rows=scenario["trained"]
        ev=np.array([[r["hero_ev_bb_per_hand"] for r in row["cross_evaluation"]] for row in rows])
        gaps=np.array([[r["best_response_gap_bb_per_hand"] for r in row["cross_evaluation"]] for row in rows])
        best=np.array([[r["best_response_ev_bb_per_hand"] for r in row["cross_evaluation"]] for row in rows])
        spread=float(np.ptp(best,axis=0).max())
        assert spread<.002, f"Best response changed with hero's evaluated policy: {scenario['name']} spread={spread}"
        assert gaps.min()>-1e-4, "Negative best-response gap beyond numerical tolerance"
        assert all(row["converged"] for row in rows), f"Unconverged scenario {scenario['name']}; increase iterations"
        # Ex-ante mixture: choose one entire trained policy at the start of a
        # hand. This is not a naive average of conditional node strategies.
        loss=np.maximum(gaps,0)
        objective=np.r_[np.zeros(4),1.]
        constraints=np.column_stack([loss.T,-np.ones(4)])
        fit=linprog(objective,A_ub=constraints,b_ub=np.zeros(4),A_eq=[np.r_[np.ones(4),0.]],b_eq=[1.],bounds=[(0,1)]*4+[(0,None)],method="highs")
        assert fit.success, fit.message
        weights=fit.x[:4];worst=loss.max(1)
        strategies=[np.array(row["focal"]["strategy"]).reshape(-1,169) for row in rows]
        for s in strategies:assert np.max(np.abs(s.sum(0)-1))<2e-5
        # Full class-combo weights, not uniform weighting of 169 labels.
        counts=np.array([6 if h//13==h%13 else 4 if h//13>h%13 else 12 for h in range(169)],float)
        weights_h=counts/counts.sum()
        distance=np.array([[float(np.sum(np.abs(a-b)*weights_h)/2) for b in strategies] for a in strategies])
        scenario["summary"]=dict(ev_matrix_bb_per_hand=ev.tolist(),gap_matrix_bb_per_hand=gaps.tolist(),
            best_response_consistency_spread_bb_per_hand=spread,worst_gap_by_trained_policy_bb_per_hand=worst.tolist(),
            finite_candidate_minimax_weights=weights.tolist(),finite_candidate_minimax_worst_gap_bb_per_hand=float((weights@loss).max()),
            focal_combo_weighted_total_variation=distance.tolist(),
            focal_argmax_changes_legacy_to_contextual=int(np.sum(strategies[0].argmax(0)!=strategies[1].argmax(0))))
    return result


def graphs(result,out):
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    scenarios=result["scenarios"];n=len(scenarios)
    fig,axes=plt.subplots(1,n,figsize=(4.2*n,4),squeeze=False,layout="constrained")
    vmax=max(max(max(row) for row in s["summary"]["gap_matrix_bb_per_hand"])*1000 for s in scenarios)
    for ax,s in zip(axes[0],scenarios):
        matrix=np.array(s["summary"]["gap_matrix_bb_per_hand"])*1000
        ax.imshow(matrix,cmap="YlOrRd",vmin=0,vmax=max(vmax,1))
        for i in range(4):
            for j in range(4):ax.text(j,i,f"{matrix[i,j]:.2f}",ha="center",va="center",fontsize=9,color="white" if matrix[i,j]>.6*vmax else "black")
        ax.set_xticks(range(4),["Legacy","Context","Half","Double"],rotation=35,ha="right")
        ax.set_yticks(range(4),WORLD_LABELS if ax==axes[0,0] else [])
        ax.set_title(s["name"]);ax.set_xlabel("Evaluated opponent world")
    axes[0,0].set_ylabel("Hero policy trained against")
    fig.suptitle("Best-response opportunity loss · milli-bb per dealt hand\nHypothetical worlds; lower is better",fontsize=12)
    fig.savefig(out/"cross_world_regret.png",dpi=150);plt.close(fig)

    fig,axes=plt.subplots(1,n,figsize=(4.2*n,3.7),squeeze=False,layout="constrained")
    for ax,s in zip(axes[0],scenarios):
        for i,row in enumerate(s["trained"]):
            t=row["convergence"];ax.plot([v["iterations"] for v in t],[max(v["hero_gap_bb_per_hand"]*1000,1e-4) for v in t],marker="o",color=COLORS[i],label=WORLD_LABELS[i])
        ax.axhline(result["target_gap_bb_per_hand"]*1000,color="#666",linestyle="--",lw=1)
        ax.set_yscale("log");ax.set_title(s["name"]);ax.set_xlabel("CPU DCFR iterations")
    axes[0,0].set_ylabel("Own-world gap · milli-bb/hand");axes[0,-1].legend(fontsize=8)
    fig.suptitle("Convergence controls · same continuation approximation in every world")
    fig.savefig(out/"convergence.png",dpi=150);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11,4),layout="constrained")
    x=np.arange(n)
    for i in range(4):axes[0].bar(x+(i-1.5)*.16,[s["summary"]["worst_gap_by_trained_policy_bb_per_hand"][i]*1000 for s in scenarios],.16,label=WORLD_LABELS[i],color=COLORS[i])
    axes[0].plot(x,[s["summary"]["finite_candidate_minimax_worst_gap_bb_per_hand"]*1000 for s in scenarios],"kD",label="Minimax policy mixture")
    axes[0].set_xticks(x,[s["name"] for s in scenarios]);axes[0].set_ylabel("Worst-world gap · milli-bb/hand");axes[0].legend(fontsize=8,loc="upper center",bbox_to_anchor=(.5,-.12),ncol=3);axes[0].set_title("Sensitivity envelope, not statistical uncertainty")
    for i in range(4):axes[1].bar(x+(i-1.5)*.16,[s["trained"][i]["target_events"]["weak_hand_decisions_per_100_hands"] for s in scenarios],.16,color=COLORS[i])
    axes[1].set_xticks(x,[s["name"] for s in scenarios]);axes[1].set_ylabel("Targeted decisions per 100 dealt hands");axes[1].set_title("How often the sparse contexts actually matter")
    fig.savefig(out/"robustness_and_reach.png",dpi=150);plt.close(fig)

    fig,axes=plt.subplots(1,n,figsize=(4.2*n,3.8),squeeze=False,layout="constrained")
    for ax,s in zip(axes[0],scenarios):
        totals=np.zeros(4)
        for a,action in enumerate(s["trained"][0]["focal"]["actions"]):
            values=np.array([r["focal"]["actions"][a]["freq"]*100 for r in s["trained"]])
            color="#547bba" if action["kind"]=="fold" else "#78a964" if action["kind"] in ["call","check"] else ["#d65759","#a83449"][max(0,a-2)%2]
            post=s["config"]["posts"][s["config"]["positions"].index(s["hero"])]
            label="Fold" if action["kind"]=="fold" else f"Call {action['to']-post:g} bb" if action["kind"]=="call" else f"Raise to {action['to']:g} bb"
            ax.barh(np.arange(4),values,left=totals,color=color,label=label)
            totals+=values
        ax.set_yticks(range(4),WORLD_LABELS if ax==axes[0,0] else []);ax.invert_yaxis();ax.set_xlim(0,100)
        ax.set_title(s["name"]);ax.set_xlabel("Frequency (%)");ax.legend(fontsize=8,loc="lower center",bbox_to_anchor=(.5,-.48),ncol=2)
    fig.suptitle("Hero decisions can change even when local cheap-call sensitivity is small",fontsize=12)
    fig.savefig(out/"focal_actions.png",dpi=150,bbox_inches="tight");plt.close(fig)


def report(result,out):
    rows=[]
    for s in result["scenarios"]:
        summary=s["summary"]
        rows.append(f"| {s['name']} | {s['nodes']:,} | {max(v['self_gap_bb_per_hand'] for v in s['trained'])*1000:.3f} | {summary['worst_gap_by_trained_policy_bb_per_hand'][0]*1000:.3f} | {summary['worst_gap_by_trained_policy_bb_per_hand'][1]*1000:.3f} | {summary['finite_candidate_minimax_worst_gap_bb_per_hand']*1000:.3f} |")
    support=result["source_support"]
    overall_costs=[s["summary"]["gap_matrix_bb_per_hand"][0][1]*1000 for s in result["scenarios"]]
    local_costs=[max(s["summary"]["gap_matrix_bb_per_hand"][1][2:])*1000 for s in result["scenarios"]]
    stable=max(s["summary"]["best_response_consistency_spread_bb_per_hand"] for s in result["scenarios"])
    evidence=(f"The existing aggregate source contains **{support['targeted_decisions']:,} targeted decisions** across {support['targeted_sessions']} sessions and {support['targeted_hand_classes']}/36 relevant hand classes. These are pooled over positions, table sizes, entry histories and prices, so individual cells are considerably thinner. " if support["available"] else support["note"]+" ")
    text=f'''# Opponent-behavior sensitivity — research pass 2

This study asks whether uncertain re-raise predictions change **decisions and EV**, not whether a range looks plausible. It uses actual preflop CPU solves against fixed measured opponents, then evaluates each learned hero strategy against all four hypothetical opponent worlds.

Run: `{result['created_at']}`. Model: `{result['model_version']}`. No production profile, artifact, save or live session was changed.

| Scenario | Tree nodes | Largest own-world gap | Legacy worst-world loss | Contextual worst-world loss | Candidate-mixture worst loss |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

All three loss columns and the convergence column are **milli-bb per dealt hand** (1 milli-bb = 0.001 bb). They are best-response opportunity costs **inside these specified models**, not measured poker win rates. Compare strategies within the same evaluated world; different worlds need not have the same attainable EV.

## Findings

The broad choice between the legacy and contextual response models matters much more here than the narrow cheap-call stress test. A legacy-trained hero loses **{min(overall_costs):.1f}–{max(overall_costs):.1f} milli-bb/hand** against the contextual world relative to its model best response. That is not evidence that the contextual world is the truth: the reverse cross-evaluations also incur substantial loss.

The contextual-trained hero's opportunity loss in the halved/doubled cheap-call worlds is only **{min(local_costs):.3f}–{max(local_costs):.3f} milli-bb/hand**, including its residual convergence gap. These cells are sparse in the data and infrequent along the hero's selected lines. Their visual irregularity is a reason to inspect evidence, but these fixtures do not justify treating them as the largest source of decision error.

The scenario results are not interchangeable. The 3-player BTN opening frequencies barely change, although later responses change EV. In the blind-defense and 6-player fixtures, focal action mixtures can change sharply between the broad model choices. This argues for contextual sensitivity displays and stronger validation, rather than a universal statement that every displayed range is stable.

The fixed-world best-response value stayed consistent across evaluated hero policies within {stable:.2g} bb/hand, providing a check that cross-evaluation preserved the learned hero policy and did not accidentally re-solve it.

![Cross-world best-response gaps](cross_world_regret.png)

## Study design

- Four worlds: the existing static Ignition pool; Contextual v1; Contextual v1 with call/fold odds halved in the targeted cells; and Contextual v1 with those odds doubled. Raising mass is retained when raising is legal. If the tree caps further raises, the existing mapping first puts that mass onto the legal call action.
- Targets: **after voluntarily entering**, nominal call price at most 25%, offsuit T-high or lower. Cold re-raises, premiums, other hands and other situations retain their original predictions. The 0.5× and 2× odds factors are declared stress assumptions; they are **not fitted confidence bounds**.
- 100bb, 0.5/1 blinds, no ante; 5% rake capped at 3bb. Three-player trees allow three total raises with 2×/2.5× re-raises; six-player trees allow two total raises with 2×/3× re-raises. Every faced re-raise remains below 25% of stack. Jams are omitted. These bounded trees isolate ordinary response modeling and do not represent unrestricted full-game poker.
- All non-hero seats use the existing measured Ignition position policies in all other buckets and remain fixed throughout a run. This makes the hero's best response well-defined. The study does not emulate a jointly adaptive table.
- The same calibrated continuation approximation, equity cache, four CPU threads and legal action grammar are used in every world. Its known range/rake limitations remain; this experiment does not validate those values.
- Hero trains separately against each world, stopping at a best-response gap ≤ {result['target_gap_bb_per_hand']:.6f} bb/hand. Cross-world comparisons preserve the learned strategy sums and replace only opponent policies. The exact model best-response traversal supplies each opportunity gap; we also check that the best-response value is consistent across evaluated hero policies in the same world.
- The optional minimax mixture chooses one **entire learned policy before the hand**, with weights optimized against this finite four-world set. It is not a naive average of conditional ranges, a calibrated uncertainty strategy, or a production recommendation.

![Convergence](convergence.png)

![Robustness and actual reach](robustness_and_reach.png)

![Focal action frequencies](focal_actions.png)

Focal decisions: 3-player BTN unopened; 3-player BB after BTN opens and SB calls; 6-player BTN after the first three seats fold; 6-player SB after those folds and BTN opens. Other branches and the complete 169-hand strategies remain in the aggregate JSON.

## What the data can support next

{evidence}All available source periods have already been inspected in earlier development. The retrospective later-period results are useful diagnostics but **there is no untouched fresh holdout here**.

The next candidate should use **support-aware, hierarchical context effects**: estimate a population price response, permit entry/position/hand-family deviations where there is evidence, and shrink sparse hand-context effects toward that response. The current predictor already uses ridge regularization; this proposal makes its shrinkage depend on the hierarchy and available support instead of treating all context coefficients alike. It should preserve strong own-hand observations and should not impose cosmetic fold floors. Cheap weak-hand predictions should carry source counts and a sensitivity indicator in the editor.

Before fitting that candidate, reserve newly acquired sessions untouched, group splits by session, and predeclare comparisons: overall log loss, calibration and per-context losses, plus strategy opportunity loss on these fixed fixtures. Use only earlier sessions for model and regularization choices. A new source period is needed for a genuine promotion decision. More data at the same already-dense contexts is less valuable than known-card decisions in missing prices, prior-entry paths and raise depths.

## Reproduce

```powershell
python tools/research/behavior_sensitivity.py
```

The default command builds a standalone Rust executable, runs all four fixtures, verifies normalization/convergence and consistent best-response values, and regenerates this report. Optional private aggregate coverage is read from `output/ignition-contextual-reraise/analysis.json`; raw histories are never read or published by this study. Its absence does not prevent the solve experiment.

Outputs: [full aggregate results](results.json), [summary metrics](summary.json). Source: `crates/solver/examples/behavior_sensitivity.rs`, `tools/research/behavior_sensitivity.py`.
'''
    (out/"README.md").write_text(text,encoding="utf-8")
    cards="".join(f'<figure><img src="{name}.png" alt="{alt}"><figcaption>{alt}</figcaption></figure>' for name,alt in [("cross_world_regret","Cross-world opportunity loss"),("convergence","Convergence checks"),("robustness_and_reach","Sensitivity and reaching probability"),("focal_actions","Focal hero decisions")])
    (out/"index.html").write_text(f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>GTOpen · behavior sensitivity</title><style>body{{margin:24px auto;max-width:1500px;background:#161b20;color:#dde6ee;font:15px system-ui;padding:0 20px}}a{{color:#72c69a}}h1{{font-size:26px}}p{{max-width:1000px;line-height:1.55}}figure{{background:white;border-radius:8px;padding:12px;margin:20px 0}}img{{width:100%;height:auto}}figcaption{{color:#56616a}}.note{{padding:14px;background:#27352d;border-radius:6px}}</style><h1>Opponent-behavior sensitivity</h1><p>Actual CPU preflop solves, cross-evaluated against four fixed opponent worlds. Models, live sessions and saved profiles remain unchanged.</p><p class="note">The halved/doubled call-odds worlds are explicit stress assumptions, not statistical confidence bounds. All EVs use the current continuation approximation; they are not measured poker win rates.</p><p><a href="../index.html">Research progress</a> · <a href="README.md">Method and findings</a> · <a href="summary.json">Summary metrics</a></p>{cards}''',encoding="utf-8")


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--max-iterations",type=int,default=500);parser.add_argument("--target-gap",type=float,default=.00001)
    parser.add_argument("--scenario",action="append");parser.add_argument("--skip-build",action="store_true");parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    if args.max_iterations<10 or args.target_gap<=0:raise ValueError("Use at least 10 iterations and a positive gap target")
    selected=[s for s in scenarios() if not args.scenario or s["name"] in args.scenario]
    if not selected:raise ValueError("No matching scenario")
    library=json.loads((ROOT/"cache/archetypes.json").read_text(encoding="utf-8"))
    stats=copy.deepcopy(next(p["stats"] for p in library if p["name"]=="Data · Ignition · NL10 regular · Pool"))
    stats["dataset"].pop("contextual_reraise",None)
    request=dict(scenarios=selected,source_stats=stats,max_iterations=args.max_iterations,target_gap=args.target_gap,cheap_price=.25)
    if not args.skip_build:subprocess.run(["cargo","build","--release","-p","solver","--example","behavior_sensitivity"],cwd=ROOT,check=True)
    exe=ROOT/"target/release/examples"/("behavior_sensitivity.exe" if os.name=="nt" else "behavior_sensitivity")
    start=time.perf_counter()
    with (out/"run.log").open("w",encoding="utf-8") as log:
        native=subprocess.run([str(exe)],input=json.dumps(request),text=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=log,cwd=ROOT)
    print((out/"run.log").read_text(encoding="utf-8"),end="",flush=True)
    native.check_returncode();result=enrich(json.loads(native.stdout))
    result.update(created_at=dt.datetime.now(dt.timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-start,
        revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),model_version="ignition-nl10-reraise-v1",
        source_support=source_support(ROOT/"output/ignition-contextual-reraise/analysis.json"),
        assumption_note="Call odds perturbations are declared sensitivity assumptions, not measured confidence intervals.",
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ["cache/contextual/ignition-nl10-reraise-v1.json","cache/archetypes.json","crates/solver/examples/behavior_sensitivity.rs","tools/research/behavior_sensitivity.py","crates/solver/src/preflop/mod.rs","crates/solver/src/preflop/contextual.rs","cache/realization_fit.json","cache/preflop_eq169.bin"]})
    (out/"results.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    summary={k:v for k,v in result.items() if k!="scenarios"};summary["scenarios"]=[{k:v for k,v in s.items() if k!="trained"} for s in result["scenarios"]]
    (out/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    graphs(result,out);report(result,out)
    print(f"Published {len(selected)} scenarios to {out}")


if __name__=="__main__":main()
