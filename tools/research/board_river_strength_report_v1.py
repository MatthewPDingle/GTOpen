"""Independent readback of the registered river-input fit comparison."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-river-strength-fit-v1';ARMS=('original','geometry','strength')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def near(a,b):assert np.isclose(a,b,rtol=1e-11,atol=1e-9),(a,b)


def main():
    rp=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    reg=read(rp);result=read(result_path)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert not result['final_test_evaluated'] and not result['production_modified'] and not result['accuracy_qualified']
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    records=result['datasets'];assert len(records)==4
    for row in records:
        assert set(row['arms'])==set(ARMS) and set(row['feature_preparation']['partitions'])=={'train','validation'}
        assert not row['feature_preparation']['final_test_features_created']
        for arm,point in row['arms'].items():
            assert sha(point['weights'])==point['weights_sha256'] and point['step']==512
            if arm=='original':
                assert point['baseline_reproduction']['maximum_parameter_difference']<1e-7
                assert point['baseline_reproduction']['maximum_validation_loss_difference']<1e-7
            c=point['contrast'];assert sum(p['rows'] for p in c['pots'])==c['all']['rows']
            assert c['all']['rows']==row['feature_preparation']['eligible_rows']['validation']
            for value in [c['all'],c['under_50bb'],*c['pots']]:
                if value['source_weight']:
                    near(value['mse_bb2'],value['squared_error_bb2']/value['source_weight'])
                    near(value['error_relative_to_zero'],value['squared_error_bb2']/value['target_energy_bb2'])
            for key in ('source_weight','squared_error_bb2','target_energy_bb2'):
                near(sum(p[key] for p in c['pots']),c['all'][key])
                near(sum(p[key] for p in c['pots'][:2]),c['under_50bb'][key])
            # Reconstruct the postflop action loss from street numerators.
            streets=[point['validation'][s] for s in ('flop','turn','river')]
            mass=sum(s['legal_target_mass'] for s in streets)
            near(mass,point['validation']['postflop']['legal_target_mass'])
            near(sum(s['normalized_loss']*s['legal_target_mass'] for s in streets)/mass,
                 point['validation']['postflop']['normalized_loss'])
    scores={metric:{arm:float(np.mean([r['arms'][arm]['validation']['postflop']['normalized_loss']
        if metric=='postflop' else r['arms'][arm]['contrast'][metric]['mse_bb2'] for r in records])) for arm in ARMS}
        for metric in ('postflop','all','under_50bb')}
    for metric in scores:
        for arm in ARMS:near(scores[metric][arm],result['scores'][metric][arm])
    changes={base:dict(river_mean_change_percent=100*(scores['all']['strength']/scores['all'][base]-1),
        under_50bb_mean_change_percent=100*(scores['under_50bb']['strength']/scores['under_50bb'][base]-1),
        postflop_mean_change_percent=100*(scores['postflop']['strength']/scores['postflop'][base]-1)) for base in ('original','geometry')}
    for base in changes:
        for key in ('river_mean_change_percent','under_50bb_mean_change_percent'):near(changes[base][key],result['comparisons'][base][key])
    rules=dict(
        lower_river_error_every_dataset=all(r['arms']['strength']['contrast']['all']['mse_bb2']<r['arms']['original']['contrast']['all']['mse_bb2'] for r in records),
        no_small_pot_regression_any_dataset=all(r['arms']['strength']['contrast']['under_50bb']['mse_bb2']<=r['arms']['original']['contrast']['under_50bb']['mse_bb2'] for r in records),
        mean_postflop_does_not_increase=scores['postflop']['strength']<=scores['postflop']['original'],
        no_postflop_dataset_more_than_one_percent_worse=all(r['arms']['strength']['validation']['postflop']['normalized_loss']<=1.01*r['arms']['original']['validation']['postflop']['normalized_loss'] for r in records),
        river_mean_at_least_one_percent_below_both=all(v['river_mean_change_percent']<=-1 for v in changes.values()),
        small_pot_mean_at_least_five_percent_below_both=all(v['under_50bb_mean_change_percent']<=-5 for v in changes.values()))
    assert rules==result['gate_rules'];qualifies=all(rules.values());assert qualifies==result['qualifies_for_policy_comparison']
    colors=('#527fbd','#b4b8bd','#57a76b');names=('Original','Geometry only','Visible strength')
    fig,axes=plt.subplots(1,3,figsize=(14.5,4.8),layout='constrained');x=np.arange(4);width=.25
    for ax,metric,title,label in zip(axes,('postflop','all','under_50bb'),
            ('All postflop action predictions','River: call minus fold','River: pots below 50 bb'),
            ('Original normalized squared error','Contrast squared error (bb²)','Contrast squared error (bb²)')):
        for i,(arm,color,name) in enumerate(zip(ARMS,colors,names)):
            values=[r['arms'][arm]['validation']['postflop']['normalized_loss'] if metric=='postflop'
                else r['arms'][arm]['contrast'][metric]['mse_bb2'] for r in records]
            ax.bar(x+(i-1)*width,values,width,color=color,label=name)
        ax.set_xticks(x,['A · BB','A · BTN','B · BB','B · BTN']);ax.set_title(title);ax.set_ylabel(label)
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    axes[0].legend(frameon=False,fontsize=9)
    fig.suptitle('Fixed-data validation · lower is better · no preflop strength claim',fontsize=13)
    image=OUT/(PREFIX+'.png');assert not image.exists();fig.savefig(image,dpi=150);plt.close(fig)
    direction='passes' if qualifies else 'does not pass'
    lines=[f'# Visible river strength {direction} the research advancement gate','',
        f"Adding visible river strength changed mean river Call-minus-Fold validation error by **{changes['original']['river_mean_change_percent']:+.2f}%** "
        f"versus the original and **{changes['geometry']['river_mean_change_percent']:+.2f}%** versus the geometry-only control. "
        f"Mean under-50-bb river contrast error changed **{changes['original']['under_50bb_mean_change_percent']:+.2f}%** versus original. "
        f"Mean full-postflop action error changed **{changes['original']['postflop_mean_change_percent']:+.2f}%**. These are reused-validation prediction results, not demonstrated poker accuracy.",'',
        '## Fixed comparison','',
        'The four generation-77 datasets, input-disjoint partitions, source weights, train-only scales, seeds, 512 fitting steps and full-gradient Adam settings stayed fixed. '
        'The original arm retained 302 inputs; both other arms had 307, with zero-initialized added columns and otherwise identical original weights. '
        'All original fits reproduced their saved weights and validation errors within 1e-7. Initial functions matched exactly in the controls, and captured/eager training matched exactly for both added-input arms.','',
        'The five added inputs are zero except at river decisions with legal Fold and Call actions. They describe eligibility, net matched pot, incremental call, centered equity and the corresponding call value, with chip features divided by the public branch total. '
        'Geometry-only fixes equity at 50%; the strength arm enumerates all 990 legal uniform-opponent hands. No sampled hidden opponent, target outcome or future card is used as an input.','',
        '| Metric (equal-dataset mean) | Original | Geometry only | Visible strength |',
        '|---|---:|---:|---:|',
        *[f"| {label} | {scores[key]['original']:.6f} | {scores[key]['geometry']:.6f} | {scores[key]['strength']:.6f} |" for key,label in
          [('postflop','Full postflop normalized action MSE'),('all','River contrast MSE (bb²)'),('under_50bb','River contrast below 50 bb (bb²)')]],'',
        f'![River strength comparison]({image.name})','',
        '## Dataset results','',
        '| Dataset | Arm | Full postflop loss | River contrast | River contrast <50 bb |',
        '|---|---|---:|---:|---:|']
    for row in records:
        for arm in ARMS:
            p=row['arms'][arm]
            lines.append(f"| {row['dataset']} | {arm} | {p['validation']['postflop']['normalized_loss']:.6f} | {p['contrast']['all']['mse_bb2']:.3f} | {p['contrast']['under_50bb']['mse_bb2']:.3f} |")
    lines += ['', '## Predeclared gate','', '| Requirement | Passed |','|---|---|',
        *[f"| {name} | {value} |" for name,value in rules.items()], '',
        '## Interpretation and next action','',
        ('The input candidate qualifies for a separately registered full policy-training experiment. Before that, reproduce these features and predictions in the sampler runtime, check visible-information boundaries and benchmark its cost. Then compare complete interacting policies on fresh deals. Do not promote a production model from this fit alone.' if qualifies else
         'The strength input did not meet every predeclared requirement. Preserve the mixed or negative result without changing thresholds after seeing it. Do not promote the model or claim better preflop ranges; inspect the comparison with geometry-only and per-street errors before specifying another test.'), '',
        'The under-50-bb metric pools the two smaller-pot bands by source-weight mass inside each dataset, then averages datasets equally. '
        'Every contrast uses source-weight sum as its denominator, not legal-action count. Full postflop errors keep their original loss definition. '
        'Uniform equity remains an input the model can discount; it is not substituted for the actual opponent range.', '',
        'All results concern two synthetic training runs of one restricted 200bb BB-versus-BTN game. The validation data informed this experiment’s hypothesis. '
        'No final-test predictions, new deal evaluations or production updates occurred. Other stacks, positions, size menus and multiway play remain unqualified.', '',
        '## Resources','',
        f"End-to-end runtime including storage admission: {result['seconds']/60:.2f} minutes. Retained fit outputs: {result['retained_bytes']/1e6:.2f} MB. "
        f"Peak own CUDA allocation: {max(p['timing']['peak_allocated_bytes'] for r in records for p in r['arms'].values())/1e9:.3f} GB. "
        'Four CPU preparation workers shared up to 16 native enumeration threads; one GPU performed the fits with the light-desktop sharing guard enabled. '
        'Visible-card caches were temporary memory only. The global 800 GB allocated-storage cap remained enforced.','']
    report=OUT/'BOARD-RIVER-STRENGTH-FINDINGS.md';assert not report.exists();report.write_text('\n'.join(lines),encoding='utf-8')
    analysis=dict(inputs={str(Path(__file__)):sha(__file__),str(rp):sha(rp),str(result_path):sha(result_path)},
        scores=scores,comparisons=changes,gate_rules=rules,qualifies_for_policy_comparison=qualifies,
        report_sha256=sha(report),plot_sha256=sha(image),independent_confirmation=False,production_adoption=False)
    destination=OUT/(PREFIX+'-analysis.json')
    with destination.open('x',encoding='utf-8') as f:json.dump(analysis,f,separators=(',',':'),allow_nan=False)
    print(json.dumps(dict(report=str(report),scores=scores,comparisons=changes,qualifies=qualifies)))


if __name__=='__main__':main()
