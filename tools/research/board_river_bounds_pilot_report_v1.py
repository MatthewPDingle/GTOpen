"""Report a completed, independently checked pilot; no selection or refitting."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import json
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from board_later_fit_holdout_run_v1 import OUT,read,sha,verify
from board_prefix_publication_v1 import atomic_json

PREFIX='weighted-complete-river-bounds-pilot-v1'


def main():
    rp=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    review_path=OUT/(PREFIX+'-independent-review.json');rr=OUT/(PREFIX+'-readback-registration.json')
    control_path=OUT/(PREFIX+'-transport-result.json')
    reg=read(rp);result=read(result_path);review=read(review_path);control=read(control_path)
    assert result['passed'] and result['complete'] and review['passed'] and review['complete']
    assert result['registration_sha256']==sha(rp) and review['source_result_sha256']==sha(result_path)
    assert review['registration_sha256']==sha(rr) and result['deals']==review['deals']==4096
    verify(reg['inputs']);verify(read(rr)['inputs'])
    store=Path(result['store']);stats=review['statistics'];assert len(stats)==8
    attempts=sorted({r['attempt'] for r in result['routes'].values()})
    invocations=[read(store/a/'invocation.json') for a in attempts]
    assert any(not x['resumed'] and x['initial_completed']==0 for x in invocations)
    assert any(x['resumed'] and x['initial_completed']==32 for x in invocations)
    manifests=[read(store/r['attempt']/(name+'.manifest.json')) for name,r in result['routes'].items()]
    packed=sum(m['packed_bytes'] for m in manifests)
    formal_positive=[s['name'] for s in stats if s['bounded_lower']>0]
    formal_negative=[s['name'] for s in stats if s['bounded_upper']<0]
    planning=review['approximate_planning_deals_for_three_se_001bb']
    assert planning==math.ceil((3*max(s['standard_deviation'] for s in stats)/.01)**2)
    counts=dict(positive_point_estimates=sum(s['mean']>0 for s in stats),negative_point_estimates=sum(s['mean']<0 for s in stats),
        bounded_positive_contrasts=formal_positive,bounded_negative_contrasts=formal_negative)
    labels=[f"Run {run} · {seat} vs {opponent} opponent" for run in ('A','B')
            for seat,opponent in (('BB','original'),('BB','bounded'),('BTN','original'),('BTN','bounded'))]
    image=OUT/(PREFIX+'-payoffs.png');report=OUT/'BOARD-RIVER-BOUNDS-POLICY-PILOT-FINDINGS.md'
    analysis_path=OUT/(PREFIX+'-analysis.json')
    assert not image.exists() and not report.exists() and not analysis_path.exists()
    fig,axes=plt.subplots(1,2,figsize=(14,6),sharey=True,layout='constrained')
    y=np.arange(8);means=np.array([s['mean'] for s in stats])
    for ax,kind,color,title in zip(axes,('bounded','approximate_95'),('#526985','#238a78'),
            ('Registered simultaneous bounds','Approximate 95% intervals — descriptive')):
        low=np.array([s[kind+'_lower'] for s in stats]);high=np.array([s[kind+'_upper'] for s in stats])
        ax.errorbar(means,y,xerr=np.stack((means-low,high-means)),fmt='o',color=color,capsize=3)
        ax.axvline(0,color='#888888',linewidth=1,linestyle='--');ax.grid(axis='x',alpha=.2)
        ax.set_title(title,fontsize=11);ax.set_xlabel('Payoff change (bb per entry)')
        ax.set_yticks(y,labels);ax.spines[['top','right']].set_visible(False)
    axes[0].invert_yaxis()
    fig.suptitle('River payoff correction: fixed 4,096-deal pilot\n200bb BB vs BTN · frozen policies and entry ranges',fontsize=14)
    fig.savefig(image,dpi=160);plt.close(fig)
    uncertain='All eight registered bounded intervals include zero.' if not formal_positive and not formal_negative else \
        f"Registered bounds exclude zero for {len(formal_positive)} positive and {len(formal_negative)} negative contrasts."
    lines=['# River-bounds policy pilot','',
        f"Completed **4,096 fresh physical deals**, evaluating eight BB/BTN policy combinations on each common deal. {uncertain} "
        'This is a restricted policy-effect pilot, not evidence of a newly solved preflop equilibrium.','',
        '## Payoff changes','',
        'Positive values favor replacing the named player with the bounded version. Units are bb per entry to the fixed BB-versus-BTN subtree, not bb per dealt full-table hand. '
        'The bounded intervals have the registered 5% family error allowance across all eight comparisons. '
        'The approximate intervals use mean ±1.96 standard errors; they are descriptive and do not supply the same guarantee.','',
        '| Run / player / opponent | Mean gain | Standard error | Simultaneous bounded interval | Approximate 95% interval |',
        '|---|---:|---:|---:|---:|']
    for label,s in zip(labels,stats):
        lines.append(f"| {label} | {s['mean']:+.6f} | {s['standard_error']:.6f} | [{s['bounded_lower']:+.6f}, {s['bounded_upper']:+.6f}] | [{s['approximate_95_lower']:+.6f}, {s['approximate_95_upper']:+.6f}] |")
    lines += ['',f'![All eight paired payoff comparisons]({image.name})','',
        '## What was checked','',
        'The correction-off control reproduced all original native payoffs exactly on the archived 32-hand control. '
        'Correction-on/off transported probabilities matched recomputation exactly. Control hands were excluded from the pilot. '
        'The pilot completed its registered seed and sample count without outcome-dependent stopping. '
        'A real process restart after the first 32 hands resumed the saved chance and statistics prefix.','',
        f"Independent readback checked every archived batch: **{review['queries_checked']:,} decision queries**, all legal action probabilities, "
        'all eight player combinations, conditional all-in labels, native values, paired differences and final statistics. '
        f"Maximum observed cashflow discrepancy was {review['maximum_cashflow_error']:.3g} bb; conservation discrepancy was {review['maximum_conservation_error']:.3g} bb. "
        'This review recomputed statistics and transport identities; it did not implement a second poker engine or rerun neural inference.','',
        '## Runtime and storage','',
        f"The resumed invocation took **{result['seconds_this_invocation']/60:.2f} minutes**, including startup checks and model loading. "
        'This excludes the first one-batch invocation and the earlier transport control. '
        f"Independent readback took {review['seconds']/60:.2f} minutes using eight CPU workers. "
        f"Pilot files occupied {result['storage']['allocated_file_bytes']/1e6:.2f} MB; packed hand archives totalled {packed/1e6:.2f} MB. "
        'The pilot stayed within its 2 GB allowance and the global 800 GB allocated-storage cap.','',
        f"Peak own GPU tensor allocation was {result['peak_cuda_allocated_bytes']/1e9:.3f} GB and peak allocator reservation was {result['peak_cuda_reserved_bytes']/1e9:.3f} GB. "
        'The revised admission rule capped this allocator at 4 GB and reserved 2 GB of external headroom. '
        'GPU policy parameters and query preparation were shared between original and corrected policies; '
        'archive compression used up to four CPU workers. Light desktop use was allowed; heavier GPU work caused yielding. '
        'Low average GPU utilization is expected when native query generation, serialization, compression or resource checks dominate.','',
        f"The largest measured paired standard deviation implies approximately **{planning:,} fresh deals** for a three-standard-error "
        'planning half-width of 0.01 bb per entry. This plug-in estimate is approximate and does not guarantee the bounded intervals will be that narrow. '
        f"At the measured archive rate this would retain approximately {planning*packed/4096/1e6:.2f} MB of packed batches, excluding startup and metadata. "
        'Any confirmation requires a separate design and fresh chance; this pilot must not be extended until a preferred sign appears.','',
        '## Limits','',
        'Only the validated terminal river Fold/Call decisions were corrected. The preflop ranges, model weights, action tree, stack, rake and entry distribution stayed fixed. '
        'The earlier reduction in prediction error does not by itself guarantee a profitable policy change. '
        'The two training runs and both player roles are reported separately. No production settings or solver code were changed.','']
    report.write_text('\n'.join(lines),encoding='utf-8')
    analysis=dict(inputs={str(p):sha(p) for p in (Path(__file__),rp,result_path,review_path,rr,control_path)},
        **counts,planning_deals=planning,packed_bytes=packed,report_sha256=sha(report),image_sha256=sha(image),
        production_adoption=False,preflop_equilibrium_retrained=False)
    atomic_json(analysis_path,analysis);print(json.dumps(dict(report=str(report),**counts,planning_deals=planning)),flush=True)


if __name__=='__main__':main()
