"""Read back physical-bound diagnostics without treating loss as poker strength."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-river-bounds-v1'
ARMS=('baseline','projected')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def near(a,b):assert np.isclose(a,b,rtol=1e-10,atol=1e-8),(a,b)
def change(a,b):return 100*(b/a-1)


def main():
    rp=OUT/(PREFIX+'-registration.json');path=OUT/(PREFIX+'-result.json')
    reg=read(rp);result=read(path)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert result['no_training'] and result['new_deals']==0
    assert not any(result[k] for k in ('production_modified','accuracy_qualified','final_test_evaluated','full_run_cuda_initialized'))
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    records=result['datasets'];assert len(records)==4
    for row in records:
        assert not row['cuda_initialized'] and set(row['partitions'])=={'train','validation'}
        assert max(row['float64_vs_original_float32_loss_differences'].values())<1e-6
        for part in row['partitions'].values():
            checks=part['per_row_checks'];metrics=part['metrics'];pots=part['pots']
            assert checks['per_row_action_error_nonincrease'] and checks['per_row_contrast_error_nonincrease']
            assert checks['all_unaffected_rows_identical'] and part['endpoint_audit']['mismatches']==0
            assert part['maximum_fold_call_sum_error_bb']<1e-10
            assert len(pots)==5
            for key in ('rows','source_weight','eligible_rows','eligible_source_weight','below_rows','above_rows',
                        'violating_source_weight','policy_changed_rows','policy_changed_source_weight'):
                near(sum(p[key] for p in pots),metrics['eligible'][key])
                near(sum(p[key] for p in pots[:2]),metrics['under_50bb'][key])
            for name in ('preflop','flop','turn'):
                assert metrics[name]['baseline']==metrics[name]['projected']
                assert metrics[name]['policy_changed_rows']==0
            for v in [*metrics.values(),*pots]:
                mass=v['source_weight'];eligible=v['eligible_source_weight']
                if mass:
                    near(v['policy_changed_weight_fraction'],v['policy_changed_source_weight']/mass)
                    near(v['weighted_mean_policy_l1'],2*v['weighted_mean_policy_tv'])
                if eligible:near(v['violating_eligible_weight_fraction'],v['violating_source_weight']/eligible)
                for arm in ARMS:
                    c=v['contrast'][arm];a=v[arm]
                    if c['source_weight']:near(c['mse_bb2'],c['squared_error_bb2']/c['source_weight'])
                    if a['legal_target_mass']:near(a['normalized_loss'],a['squared_error']/a['legal_target_mass'])
                assert v['projected']['squared_error']<=v['baseline']['squared_error']+1e-7
                assert v['contrast']['projected']['squared_error_bb2']<=v['contrast']['baseline']['squared_error_bb2']+1e-5
            for arm in ARMS:
                for key in ('squared_error_bb2','source_weight','target_energy_bb2'):
                    near(sum(p['contrast'][arm][key] for p in pots),metrics['eligible']['contrast'][arm][key])
                for key in ('squared_error','legal_target_mass','source_weight'):
                    near(sum(metrics[s][arm][key] for s in ('flop','turn','river')),metrics['postflop'][arm][key])
    means={metric:{arm:float(np.mean([r['partitions']['validation']['metrics']['postflop'][arm]['normalized_loss']
        if metric=='postflop' else r['partitions']['validation']['metrics'][metric]['contrast'][arm]['mse_bb2']
        for r in records])) for arm in ARMS} for metric in ('postflop','eligible','under_50bb')}
    for metric in means:
        for arm in ARMS:near(means[metric][arm],result['validation_equal_dataset_means'][metric][arm])
    changes={key:change(v['baseline'],v['projected']) for key,v in means.items()}
    coverage={part:dict(
        total_rows=sum(r['partitions'][part]['metrics']['all']['rows'] for r in records),
        eligible_rows=sum(r['partitions'][part]['metrics']['eligible']['rows'] for r in records),
        violating_rows=sum(r['partitions'][part]['metrics']['eligible']['below_rows']+r['partitions'][part]['metrics']['eligible']['above_rows'] for r in records),
        policy_changed_rows=sum(r['partitions'][part]['metrics']['eligible']['policy_changed_rows'] for r in records),
        mean_violating_weight_fraction=float(np.mean([r['partitions'][part]['metrics']['eligible']['violating_eligible_weight_fraction'] for r in records])),
        mean_policy_changed_weight_fraction=float(np.mean([r['partitions'][part]['metrics']['eligible']['policy_changed_weight_fraction'] for r in records])),
        mean_policy_tv=float(np.mean([r['partitions'][part]['metrics']['eligible']['weighted_mean_policy_tv'] for r in records])),
        maximum_violation_bb=max(r['partitions'][part]['metrics']['eligible']['maximum_violation_bb'] for r in records))
        for part in ('train','validation')}
    fig,axes=plt.subplots(1,3,figsize=(14.5,4.8),layout='constrained')
    labels=['A · BB','A · BTN','B · BB','B · BTN'];x=np.arange(4)
    for i,(key,title) in enumerate((('eligible','All eligible river pots'),('under_50bb','River pots below 50 bb'))):
        values=[change(r['partitions']['validation']['metrics'][key]['contrast']['baseline']['mse_bb2'],
                       r['partitions']['validation']['metrics'][key]['contrast']['projected']['mse_bb2']) for r in records]
        axes[i].bar(x,values,color='#527fbd')
        axes[i].set_title(title);axes[i].set_ylabel('Change in prediction error (%)')
        axes[i].axhline(0,color='#555555',linewidth=.8)
        for at,value in enumerate(values):axes[i].annotate(f'{value:.2f}%',(at,value),xytext=(0,-12),textcoords='offset points',ha='center',fontsize=9)
        axes[i].margins(y=.2)
    values=[100*r['partitions']['validation']['metrics']['eligible']['policy_changed_weight_fraction'] for r in records]
    axes[2].bar(x,values,color='#bd914d');axes[2].set_title('Eligible river policies changed')
    axes[2].set_ylabel('Source-weight share (%)')
    for at,value in enumerate(values):axes[2].annotate(f'{value:.2f}%',(at,value),xytext=(0,5),textcoords='offset points',ha='center',fontsize=9)
    axes[2].margins(y=.2)
    for ax in axes:
        ax.set_xticks(x,labels);ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Physical river bounds · reused validation · policy changes are not proven gains',fontsize=13)
    image=OUT/(PREFIX+'.png');assert not image.exists();fig.savefig(image,dpi=150);plt.close(fig)
    lines=['# River payoff bounds: prediction and policy diagnostic','',
        f"Enforcing the exact Call-minus-Fold payoff limits changed mean eligible-river prediction error by **{changes['eligible']:+.3f}%**, "
        f"under-50-bb error by **{changes['under_50bb']:+.3f}%**, and full-postflop action error by **{changes['postflop']:+.3f}%**. "
        'This establishes a prediction correction on reused data, not stronger poker play.','',
        'At verified terminal river Fold/Call decisions, the difference must lie between the incremental call lost and the current pot won net of rake. '
        'The correction moves only the two scores equally in opposite directions, preserving their sum. It uses public pot/call/rake information and the saved training scale; '
        'it needs no hidden cards or guessed opponent range. Other actions and all other streets remain unchanged.','',
        '## Fixed experiment and controls','',
        'Four original 512-step diagnostic fits were scored with their stored float32 weights and original float32 features widened to float64. '
        'These are the holdout-study fits, not the complete models used by the played policy bank. The original source weights, partitions and train-only scales were preserved. '
        'CPU/GPU score and policy comparisons, endpoint targets, negative-score fallbacks, exact ties, wrong-menu rejection, unit changes, common offsets and idempotence passed. '
        'Every scored row passed the registered non-increasing action-error check, and every eligible row passed the contrast-error check. '
        'Baseline losses reproduced the earlier float32 results within 1e-6.','',
        '| Validation metric (equal-dataset mean) | Original | Bounded | Change |','|---|---:|---:|---:|',
        *[f"| {label} | {means[key]['baseline']:.6f} | {means[key]['projected']:.6f} | {changes[key]:+.3f}% |" for key,label in
          [('postflop','Full postflop normalized action error'),('eligible','River contrast error, bb²'),('under_50bb','River contrast below 50 bb, bb²')]],'',
        f'![River value bounds diagnostic]({image.name})','',
        '## Coverage and policy changes','',
        '| Partition | Total rows | Eligible river rows | Violating rows | Changed policy rows | Mean violating weight | Mean changed-policy weight | Mean TV | Max violation, bb |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,v in coverage.items():
        lines.append(f"| {name} | {v['total_rows']:,} | {v['eligible_rows']:,} | {v['violating_rows']:,} | {v['policy_changed_rows']:,} | {100*v['mean_violating_weight_fraction']:.3f}% | {100*v['mean_policy_changed_weight_fraction']:.3f}% | {v['mean_policy_tv']:.6f} | {v['maximum_violation_bb']:.3f} |")
    lines += ['', 'Fractions and TV average the four datasets equally and use the eligible-river source weight within each dataset. These are sampled training/validation weights, not actual game reach frequencies. '
        'TV is half the action-probability L1 distance. A changed policy is neither automatically better nor worse.','',
        '## Per-dataset pot breakdown','',
        '| Dataset | Partition | Pot | Below / above | Violating weight | Max violation, bb | Mean violation, bb | Original contrast | Bounded contrast | Changed policy weight | TV |',
        '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in records:
        for name,part in r['partitions'].items():
            for p in part['pots']:
                lines.append(f"| {r['dataset']} | {name} | {p['label']} | {p['below_rows']} / {p['above_rows']} | {100*p['violating_eligible_weight_fraction']:.3f}% | {p['maximum_violation_bb']:.3f} | {p['weighted_mean_violation_bb']:.3f} | {p['contrast']['baseline']['mse_bb2']:.3f} | {p['contrast']['projected']['mse_bb2']:.3f} | {100*p['policy_changed_weight_fraction']:.3f}% | {p['weighted_mean_policy_tv']:.6f} |")
    lines += ['', '## Limits and next decision','',
        'No new training, fresh deals, final-test scoring, policy-bank changes or production deployment occurred. The sources cover two synthetic runs of one restricted 200bb BB-versus-BTN game. '
        'The exact mathematical bound generalizes where its terminal-call assumptions hold, but these measurements do not qualify other stacks, positions, bet menus or multiway ranges.','',
        'Lower squared error is guaranteed only for valid targets under the equal-within-row action weighting tested here. The correction may still alter regret-matched policies, '
        'including probabilities of other actions through normalization. Before any runtime adoption, check complete historical banks, their per-model scales and their own-action reach weighting. '
        'Then require separate whole-policy and fresh-deal evaluation; do not infer EV gains from these loss numbers.','',
        '## Resources','',
        f"The four CPU workers completed the full diagnostic in {result['seconds']/60:.2f} minutes including the global storage admission scan. "
        'A short GPU equivalence control preceded it; the full data pass initialized no CUDA context. The global 800 GB allocation cap and production/shared-lock checks remained in force.','']
    report=OUT/'BOARD-RIVER-BOUNDS-FINDINGS.md';assert not report.exists();report.write_text('\n'.join(lines),encoding='utf-8')
    analysis=dict(inputs={str(Path(__file__)):sha(__file__),str(rp):sha(rp),str(path):sha(path)},means=means,
        change_percent=changes,coverage=coverage,report_sha256=sha(report),plot_sha256=sha(image),
        improved_poker_policy_demonstrated=False,production_adoption=False)
    with (OUT/(PREFIX+'-analysis.json')).open('x',encoding='utf-8') as f:json.dump(analysis,f,separators=(',',':'),allow_nan=False)
    print(json.dumps(dict(changes=changes,coverage=coverage,report=str(report))))


if __name__=='__main__':main()
