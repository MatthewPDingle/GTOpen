"""Rebuild a concise evidence summary and chart from recorded overnight results."""
import json
from pathlib import Path
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'research/preflop-evolution'
OUT=BASE/'representative-coverage-20260919'
SYM=BASE/'symmetric-bridge-20260919'

def read(path):
    return json.loads(path.read_text()) if path.exists() else None

def coverage_plot():
    training=read(BASE/'integrated-coverage-20260919/flop-structure.json')
    validation=read(OUT/'validation-95-structure.json')
    if not training or not validation:return False
    x=list(range(13));labels=[r+r for r in training['ranks']]
    t=training['flop_set_or_quads_probability'];v=validation['pocket_pair_set_or_quads']
    fig,axes=plt.subplots(1,2,figsize=(11,4.1),sharey=True)
    for key,name,color in [('full_deck','Full-deck reference','#333333'),('panel-ab','10 training flops','#d68d41'),('report-47','47 training flops','#4f9877')]:
        axes[0].plot(x,[100*a for a in t[key]],label=name,color=color,marker='o',markersize=3)
    for key,name,color,style in [('full','Full-deck reference','#333333','-'),('eligible','Eligible validation population','#777777','--'),('original_reserved10','Original 10 reserved','#bc6877','-'),('validation95','Independent 95 reserved','#597ab9','-')]:
        axes[1].plot(x,[100*a for a in v[key]],label=name,color=color,linestyle=style,marker='o',markersize=3)
    for ax,title in zip(axes,['Training sample coverage','Reserved sample coverage']):
        ax.set(xticks=x,xticklabels=labels,xlabel='Opener pocket pair',title=title,ylim=(0,46))
        ax.tick_params(axis='x',labelsize=8);ax.grid(alpha=.2);ax.legend(fontsize=7)
    axes[0].set_ylabel('Flops with a matching pocket-pair rank (%)')
    fig.text(.06,.015,'Chance-only audit, conditional on the fixed opposing entry range. No strategic outcome used to choose the new sample.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(OUT/'independent-coverage.png',dpi=160);plt.close(fig)
    return True


def run():
    queue=read(OUT/'validation-queue-status.json')
    overnight=read(OUT/'overnight-accuracy-status.json')
    controls=read(OUT/'transfer-controls-status.json')
    held=read(OUT/'independent-transfer-summary.json') or []
    has_coverage=coverage_plot()
    information=read(OUT/'transfer-information-control.json')
    rows=[]
    for name in ['two','ab']:
        r=read(SYM/f'connected-{name}-review.json')
        if r:rows.append(dict(name=f'{2 if name=="two" else 10} flops',**r))
    unit=read(OUT/'paging-unit-status.json')
    paging=read(OUT/'paged-two-review.json')
    trial=read(OUT/'report47-trial-result.json')
    full=read(OUT/'report47-full-result.json')
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    if rows:
        axes[0].scatter([r['max_ev_difference_bb'] for r in rows],[r['name'] for r in rows],color='#4f9877',s=60,zorder=3)
        for r in rows:axes[0].annotate(f"{r['max_ev_difference_bb']:.8f}",(r['max_ev_difference_bb'],r['name']),xytext=(8,8),textcoords='offset points',fontsize=9)
        axes[0].axvline(.002,color='#ba6c38',linestyle='--',label='Registered EV threshold')
        axes[0].set_xlim(1e-6,4e-3);axes[0].margins(y=.4)
    axes[0].set(xscale='log',xlabel='Maximum player EV difference (bb)',title='Compact vs fully enumerated solver')
    axes[0].legend(fontsize=8);axes[0].grid(axis='x',alpha=.2)
    series=[('2 flops, resident',BASE/'integrated-coverage-20260919/old-two-orbits-result.json','#597ab9'),
            ('2 flops, paged',OUT/'paged-two-result.json','#b179bd'),
            ('10 flops',BASE/'integrated-coverage-20260919/panel-ab-result.json','#d68d41'),
            ('47 flops, trial',OUT/'report47-trial-result.json','#9d9d9d'),
            ('47 flops, main',OUT/'report47-full-result.json','#4f9877')]
    for name,path,color in series:
        r=read(path)
        if r:
            records=r['records']
            axes[1].loglog([x['iteration'] for x in records],[x['evaluation']['gap_total'] for x in records],
                          marker='o',markersize=3,label=name,color=color)
    axes[1].set(xlabel='Iterations',ylabel='Combined deviation gain (bb)',title='Convergence inside each sampled game')
    axes[1].legend(fontsize=8);axes[1].grid(alpha=.2)
    fig.text(.06,.015,'Small numerical gaps do not establish full-deck accuracy. Different board panels define different games.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(OUT/'validation-progress.png',dpi=160);plt.close(fig)
    lines=['# Overnight reference study','',f'Updated {datetime.datetime.now(datetime.timezone.utc).isoformat()}.',
           '', 'Research only. Production port 56708 has not been changed by this work.',
           '', 'This study follows one opener facing a 3-bet, after all other players have folded: '
           '200 bb starting stacks, open to 6, reraise to 18, and a 27.5 bb decision pot. '
           'It retains folding, calling, raising to 45 and jamming, with both called postflop branches. '
           'The game charges 4% rake capped at 6 bb and uses 50% postflop bets with pot-sized raises. '
           'It is a reference case for improving continuation values, not a solved replacement for every Preflop Lab situation.',
           '', 'Both entering ranges are frozen from the saved GTOpen baseline. This experiment re-solves decisions inside '
           'the selected branch; it does not jointly re-solve the earlier opening and 3-betting decisions that supplied those ranges. '
           'Earlier folded-card information is also omitted. Good transfer here would be evidence for this continuation method, '
           'not proof that the complete preflop game matches GTO Wizard.',
           '', '## Numerical correctness','',
           '| Comparison | Maximum EV difference | Root policy TV | Registered checks |',
           '|---|---:|---:|---|']
    for r in rows:
        lines.append(f'| Full vs compact, {r["name"]} | {r["max_ev_difference_bb"]:.8f} bb | {r["prior_weighted_policy_tv"]:.8f} | {"Passed" if r["passed"] else "Failed"} |')
    lines+=['', 'The separate abrupt-changing-range stress test still fails its 0.002 bb independent-trajectory value threshold. '
            'Successful converged tests do not erase that failure. The paging experiment uses the original fully enumerated path.',
            '',f'Paging unit test: {"passed, including bitwise CFV and arena agreement across 160 switches" if unit and unit["exit_code"]==0 else "pending or failed; inspect its recorded result"}.']
    if paging:
        lines.append(f'Connected two-flop paging: {"passed" if paging["passed"] else "failed"}; '
                     f'all checkpoint evaluations identical: {paging["every_checkpoint_evaluation_identical"]}. '
                     f'Shared workspace {paging["workspace_bytes"]/1e9:.3f} GB; {paging["seconds"]:.1f} seconds.')
    else:lines.append('Connected two-flop paging: full-run review pending.')
    lines+=['','## Broader coverage','',
            'The unchanged 47-flop candidate improves pocket-pair opportunity coverage over the ten-flop development panel. '
            'It remains an approximation; more representative chance coverage and unseen-board tests are needed before making accuracy claims.']
    for label,r in [('Feasibility trial',trial),('Main 47-flop solve',full)]:
        if r:
            last=r['records'][-1];lines.append(f'{label}: latest recorded iteration {last["iteration"]}, '
                f'gap {last["evaluation"]["gap_total"]:.6f} bb, elapsed {last["elapsed_seconds"]:.1f} seconds. '
                'A checkpoint alone does not prove completion.')
    lines+=['',f'Last recorded validation-queue stage: `{queue["step"] if queue else "unavailable"}`. '
            'Check the actual process before treating that stage as live.',
            f'Last recorded transfer-control stage: `{controls["step"] if controls else "unavailable"}`; '
            f'overnight sequence: `{overnight["step"] if overnight else "not registered"}`.',
            '', '![Recorded numerical checks and convergence](validation-progress.png)',
            '', '## Independent evaluation','',
            (f'The frozen-policy implementation controls passed. Streamed versus paged two-board evaluation '
             f'agreed within {controls["errors"]["ev"]:.3g} bb in EV and '
             f'{max(controls["errors"]["gaps"], controls["errors"]["postflop_gaps"]):.3g} bb in deviation gains. '
             'All imported preflop probabilities stayed bitwise unchanged. This validates the transfer implementation; '
             'it does not establish accuracy on unseen flops.') if controls and controls['step']=='complete-passed' else
            'Frozen-policy implementation validation remains pending or failed; inspect its recorded stage.', '',
            'The reserved-board protocol freezes all preflop decisions, solves their postflop continuations, '
            'then separates postflop numerical residual from profitable full-game deviations. '
            'Deterministic controls precede reserved-board use. Ten reserved flops are a transfer stress test, '
            'not a precise full-deck exploitability estimate. A separate 95-flop sample was frozen before any reserved strategic outcomes. '
            'Its complete suit orbits exclude all training/development and original reserved boards; '
            'it targets the eligible complement, with 4.525% of physical flops excluded.',
            '', 'The evaluator combines per-hand leaf values across all boards before allowing a preflop best response. '
            'Averaging separately optimized preflop choices would incorrectly give the player knowledge of the future flop.',
            (f'The synthetic hidden-chance control passed: correct deviation gain {information["hidden_chance_deviation_bb"]:.1f} bb, '
             f'versus {information["deliberately_invalid_clairvoyant_deviation_bb"]:.1f} bb under deliberately invalid advance knowledge. '
             'This checks information handling; its artificial utilities are not poker observations.') if information else '',
            '', '| Reserved panel | Frozen source | OOP EV | IP EV | Postflop residual | Full deviation gain | Numerical check |',
            '|---|---|---:|---:|---:|---:|---|']
    for row in held:
        residual=row['postflop_gap_total']
        lines.append(f'| {row["panel"]} | {row["source"]} | {row["ev"][0]:.5f} | {row["ev"][1]:.5f} | '
                     f'{residual:.6f} | {row["gap_total"]:.6f} | {"Passed" if residual<.01 else "Incomplete"} |')
    if not held:lines.append('| No completed reserved strategy evaluation yet | — | — | — | — | — | Pending |')
    lines+=['', 'Values are bb at the same entering two-player decision. Full deviation gain is against the particular '
            'evaluated postflop continuations, including off-path choices. It need not be zero when preflop is frozen. '
            'Neither a small residual nor favorable transfer in one finite panel proves full-deck accuracy.',
            '', '![Chance coverage before reserved strategic evaluation](independent-coverage.png)' if has_coverage else '',
            '', '[Paging protocol](PAGING-PROTOCOL.md) · [Reserved-board protocol](HOLDOUT-PROTOCOL.md) · '
            '[95-board selection](VALIDATION95-PROTOCOL.md) · [Overnight registration](OVERNIGHT-RUN-PROTOCOL.md) · '
            '[Transfer controls](TRANSFER-CONTROLS.md) · [Hand-level decision diagnostics](DECISION-DIAGNOSTICS.md) · '
            '[Earlier coverage findings](../integrated-coverage-20260919/RESULTS.md)']
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':run()
