"""Summarize verified outputs; never fits or selects a replacement model."""
import json
import numpy as np
import shallow_native_feedback as study


def policy_changes():
    rows=[]
    snapshots={arm:study.read(study.OUT/arm/'3000/iteration-3000.json') for arm in ['baseline','shallow']}
    for path in [[],[2]]:
        views={a:next(r['view'] for r in s['views'] if r['path']==path) for a,s in snapshots.items()}
        a,b=[np.array(views[arm]['strategy']).reshape(-1,169) for arm in ['baseline','shallow']]
        tv=abs(a-b).sum(axis=0)/2
        rows.append(dict(path=path,actions=[x['label'] for x in views['shallow']['actions']],
            frequencies={arm:[x['freq'] for x in view['actions']] for arm,view in views.items()},
            combo_weighted_hand_variation=float(tv@study.pilot.COMBOS/1326),
            hands=[dict(hand=study.pilot.LABELS[k],baseline=a[:,k].tolist(),shallow=b[:,k].tolist(),variation=float(tv[k]))
                   for k in np.argsort(-tv)]))
    study.write(study.OUT/'policy-changes.json',dict(rows=rows))
    return rows


def report():
    study.checked();rows=policy_changes();e=study.read(study.OUT/'evaluation.json')
    stable=study.read(study.OUT/'stability.json');timing=study.read(study.OUT/'timing.json')
    lines=['# Native shallow correction: fresh-policy feedback','',
        'Research only. Production port 56708, server code, binaries and defaults were unchanged.',
        'The frozen 18-coefficient model was ported into an explicitly selected offline CUDA kernel.',
        'No coefficients were refitted using these ranges or reference labels.','',
        '## Integration and stability','',
        'Python, native CPU and CUDA agreed on 126 range/stack fixtures (42,588 values).',
        'Exact zero-stack and stack-transition tests conserve the pot. Native complete action',
        'values agree with an independent Python tree reconstruction within 0.000004bb.',
        'Eleven complete-tree fixtures also passed the stack-boundary checks; the largest',
        'action-value movement across a boundary perturbation was below 0.000006bb.',
        'Disabled, sparse-range, and three/eight-player guard fixtures reproduced baseline values.',
        'Saved strategies were checked unchanged during each native evaluation.','',
        '| Policy | Root action movement, 1500 to 3000 | BB vs open movement | Stability screen |',
        '|---|---:|---:|---|']
    for arm,s in stable.items():
        lines.append(f"| {arm} | {s['rows'][0]['max_aggregate_movement_pp']:.4f} pp | {s['rows'][1]['max_aggregate_movement_pp']:.4f} pp | {'Pass' if s['passed'] else 'Fail'} |")
    lines += ['', 'These are small 40bb heads-up games. A small frozen-range gap is not proof of',
        'full-game equilibrium when the continuation values themselves depend on ranges.','',
        '## Changed strategy','', '| Decision / action | Baseline | Shallow |','|---|---:|---:|']
    for r in rows:
        position='SB first in' if r['path']==[] else 'BB vs 2.5bb open'
        for i,label in enumerate(r['actions']):
            lines.append(f"| {position}: {label} | {100*r['frequencies']['baseline'][i]:.2f}% | {100*r['frequencies']['shallow'][i]:.2f}% |")
    lines += ['', '## Fresh postflop references','',
        f"All {e['reference_count']} solves passed the CPU and GPU 0.1%-pot checks; maxima were {e['max_cpu_gap_pct']:.5f}% and {e['max_gpu_gap_pct']:.5f}%.",
        'The same 50 stratified boards were solved in three contexts using the corrected',
        'policy\'s final reaching ranges. All comparisons below hold those new ranges fixed.',
        'They do not measure the full-game EV improvement of one policy over another.','',
        '| Context | Previous model MAE | Shallow MAE | Reduction | Qualified pair mass |',
        '|---|---:|---:|---:|---:|']
    for name,r in e['leaf_reports'].items():
        lines.append(f"| {name} | {r['mae_bb']['baseline']['corrected']:.3f}bb | {r['mae_bb']['shallow']['corrected']:.3f}bb | {100*r['improvements']['corrected']:.1f}% | {100*r['qualified_pair_mass_fraction']:.3f}% |")
    lines += ['', 'MAE is legal-pair-weighted mean absolute hand-value error across both players,',
        'using an equity control variate. The direct estimates and paired, stratified',
        '5000-resample intervals are retained in evaluation.json. Unsettled individual',
        'hands remain excluded even when the whole-node solve passes.','',
        '## Does the gain reach the preflop decision?','',
        '| Comparison | Estimator | Previous model error | Shallow error | Qualified classes / mass |',
        '|---|---|---:|---:|---:|']
    for kind in ['call_vs_fold','call_vs_raise']:
        r=e['actions'][kind]
        for estimator in ['direct','corrected']:
            errs=r['pair_weighted_mae_bb']
            lines.append(f"| {kind} | {estimator} | {errs['baseline'][estimator]:.4f}bb | {errs['shallow'][estimator]:.4f}bb | {r['qualified_hand_classes']} / {100*r['qualified_decision_pair_mass_fraction']:.1f}% |")
    lines += ['', 'These action comparisons keep later preflop choices fixed. The call-versus-raise',
        'screen requires support for both actions; unsupported hands are not evidence of',
        'agreement. All-in leaves retain cached equities. Full postflop menus and folded-card',
        'effects remain outside this test.','', '## Cost and decision','',
        f"Median 1000-iteration time after warmup: baseline {timing['medians']['baseline']:.3f}s; shallow {timing['medians']['shallow']:.3f}s ({100*(timing['shallow_over_baseline']-1):.1f}% slower).",
        'Three alternating-order pairs isolate learning time from setup. This measures',
        'the 40-node fixture only, not the large multiway trees in the live app.','',
        f"Predeclared accuracy feedback screen: {'PASS' if e['primary_feedback_pass'] else 'FAIL'}.",'']
    for gate,passed in e['gates'].items():lines.append(f"- {gate}: {'pass' if passed else 'fail'}")
    lines += ['', 'Integration is deliberately not deployed. The shallow model was trained only at',
        'SPR 0.2 and 0.75; this game tests one shallow SPR (17.5/45). Below 0.2 its residual',
        'scales to zero, and from 0.75 to 1 it blends into the old model. Those transitions',
        'are numerically verified assumptions, not new accuracy evidence.','',
        'See CONCLUSIONS.md for the interpretation and next recommendation, PROTOCOL.md for',
        'the predeclared screen, implementation-freeze.json and manifest.json for input hashes,',
        'and evaluation.json for all 169 hand classes.']
    (study.OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4.2))
    panels=[('Called 4-bet: hand-value error',e['leaf_reports']['fourbet-call']['mae_bb']),
            ('BB call vs 3-bet: decision-value error',e['actions']['call_vs_raise']['pair_weighted_mae_bb'])]
    for ax,(title,metrics) in zip(axes,panels):
        x=np.arange(2)
        for offset,name,color,label in [(-.18,'baseline','#777e88','Previous model'),(.18,'shallow','#318564','Shallow correction')]:
            bars=ax.bar(x+offset,[metrics[name][k] for k in ['direct','corrected']],.34,color=color,label=label)
            ax.bar_label(bars,fmt='%.3f',padding=3,fontsize=9)
        ax.set_xticks(x,['Direct reference','Equity adjusted']);ax.set_ylabel('Mean absolute error (bb)')
        ax.set_title(title,fontsize=11);ax.set_ylim(bottom=0,top=ax.get_ylim()[1]*1.2)
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    axes[0].legend(frameon=False,fontsize=9)
    fig.suptitle('Accuracy after re-solving the 40bb heads-up game',fontsize=13)
    fig.text(.5,.02,'150 fresh postflop solves · frozen model · qualified hands only · not a full-game win-rate comparison',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.065,1,.94));fig.savefig(study.OUT/'comparison.png',dpi=160);plt.close(fig)


if __name__=='__main__':report()
