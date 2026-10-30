"""Render both completed precision runs; no partial-result or deployment path."""
import json
from pathlib import Path
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha


def main():
    paths=[OUT/'BOARD-PRECISION-COMPARISON.md',OUT/'board-precision-comparison.png',
           OUT/'board-precision-comparison-evidence.json']
    assert not any(p.exists() for p in paths)
    inputs=[Path(__file__)];runs=[]
    for prefix,n in [('board-precision-pilot-v1',32),('board-precision-repeat-v1',128)]:
        rp=OUT/f'{prefix}-registration.json';resultp=OUT/f'{prefix}-result.json';reviewp=OUT/f'{prefix}-review.json'
        reg,result,review=map(read,(rp,resultp,reviewp))
        assert review['passed'] and result['passed'] and reg['boards']==n and reg['private_deals']==169*n
        assert review['registration_sha256']==result['registration_sha256']==sha(rp)
        assert review['pilot_result_sha256']==sha(resultp)
        assert sha(review['class_table'])==review['class_table_sha256']
        for p,h in review['inputs'].items():assert sha(p)==h,p
        table=read(review['class_table']);assert len(table)==169 and [x['hand_class'] for x in table]==list(range(169))
        runs.append((reg,review,table));inputs.extend([rp,resultp,reviewp,Path(review['class_table'])])
    assert runs[0][0]['model']==runs[1][0]['model']
    assert runs[0][0]['board_seed']!=runs[1][0]['board_seed'] and runs[0][0]['private_seed']!=runs[1][0]['private_seed']
    order=['raise-call','call-fold','raise-fold'];labels=['Raise vs call','Call vs fold','Raise vs fold']
    assert all([x['contrast'] for x in r[1]['summaries']]==order for r in runs)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,2,figsize=(12,5.3),layout='constrained')
    y=np.arange(3);colors=['#4e79a7','#23856b']
    for k,(reg,review,_) in enumerate(runs):
        values=[x['board_to_private_variance_cost_ratio'] for x in review['summaries']]
        axes[0].scatter(values,y+(-.12 if k==0 else .12),s=60,color=colors[k],label=f"{reg['boards']} boards")
        for yy,v in zip(y+(-.12 if k==0 else .12),values):axes[0].annotate(f'{v:.3f}',(v,yy),xytext=(6,0),textcoords='offset points',va='center',fontsize=9)
    axes[0].axvline(1,color='#666',linestyle='--');axes[0].set_xlim(0,1.15)
    axes[0].set_yticks(y,labels);axes[0].invert_yaxis();axes[0].legend(loc='lower right')
    axes[0].set_title('Variance × computation time\nEach private-first reference = 1')
    axes[0].set_xlabel('Lower is better; CPU research estimators')
    repeat=runs[1][1]['summaries']
    for values,offset,color,name in [([x['private_rms_se'] for x in repeat],-.18,'#9b9b9b','Private-first'),
                                     ([x['board_rms_se'] for x in repeat],.18,colors[1],'Board-first')]:
        axes[1].barh(y+offset,values,height=.32,color=color,label=name)
        for yy,v in zip(y+offset,values):axes[1].text(v,yy,f' {v:.2f}',va='center',fontsize=9)
    axes[1].set_yticks(y,labels);axes[1].invert_yaxis();axes[1].legend(loc='lower right')
    axes[1].set_title('Independent repeat: estimated noise\n128 samples per hand class')
    axes[1].set_xlabel('Entry-weighted RMS standard error (bb)')
    axes[1].set_xlim(0,max(x['private_rms_se'] for x in repeat)*1.25)
    for ax in axes:ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
    fig.suptitle('Fixed-policy board integration: two precision diagnostics\nDescriptive estimates; no solver speedup or playing-strength claim',fontsize=13)
    fig.savefig(paths[1],dpi=150);plt.close(fig)
    lines=['# Fixed-policy precision comparison','',
        'Both runs completed their registered samples and readback checks. They use the same saved generation-77 policy and independent chance seeds. These are estimator diagnostics, not trained-range or playing-strength results.','',
        '![Precision and computation comparison](board-precision-comparison.png)','',
        '| Comparison | Pilot variance-time ratio | Repeat variance-time ratio | Repeat private RMS SE | Repeat board RMS SE |',
        '| --- | ---: | ---: | ---: | ---: |']
    for a,b in zip(runs[0][1]['summaries'],runs[1][1]['summaries']):
        lines.append(f"| {a['contrast']} | {a['board_to_private_variance_cost_ratio']:.3f} | {b['board_to_private_variance_cost_ratio']:.3f} | {b['private_rms_se']:.3f} bb | {b['board_rms_se']:.3f} bb |")
    lines += ['', 'Ratios below one favour board integration on this measured variance-times-summed-worker-wall-time metric. This does not compare against production GPU throughput. Class errors share boards and are correlated; no confidence intervals or significance claim are supplied.','']
    for reg,review,table in runs:
        lines += [f"## {reg['boards']}-board run",'',f"Private deals: {reg['private_deals']:,}. Total elapsed: {review['pilot_elapsed_seconds']:.1f} s. Summed worker time: board {review['summed_worker_seconds']['board']:.1f} s; private {review['summed_worker_seconds']['private']:.1f} s.",'']
        for summary in review['summaries']:
            name=summary['contrast'];ranked=sorted(table,key=lambda x:abs(x['contrasts'][name]['descriptive_difference_over_se'] or 0),reverse=True)
            worst=ranked[0];v=worst['contrasts'][name]
            diff=sum(x['entry_mass']*x['contrasts'][name]['mean_difference'] for x in table)
            lines.append(f"- {name}: lower measured board variance for {summary['classes_with_lower_board_sample_variance']}/169 classes. Entry-weighted mean difference {diff:+.3f} bb. Largest absolute descriptive mean discrepancy: {worst['hand']}, {v['mean_difference']:+.3f} bb, {v['descriptive_difference_over_se']:+.2f} combined SE.")
        lines += ['',f"Every class, including regressions: `{Path(review['class_table']).name}`.",'']
    lines += ['## Limits and next decision','',
        'The arithmetic controls and independent chance streams support assessing precision per computation budget. They do not prove unbiasedness from finite mean agreement, establish equilibrium accuracy, or show faster learning. Rare large-payoff outcomes still require attention. The largest standardized discrepancies are descriptive diagnostics selected from all classes, not multiplicity-adjusted tests.','',
        'Interpret these complete results before choosing a training experiment. A new root estimator needs its own typed state and checkpoint admission, a mechanical update/recovery control, and matched training plus held-out payoff evaluation. The active stratified study is separate and remains pending until its registered final evaluation finishes.','']
    paths[0].write_text('\n'.join(lines),encoding='utf-8')
    save(paths[2],dict(inputs={str(p):sha(p) for p in inputs},outputs={str(p):sha(p) for p in paths[:2]},
        interpretation_pending=True,accuracy_qualified=False,production_modified=False))
    print('Rendered both complete precision runs; visual review and interpretation remain.')


if __name__=='__main__':main()
