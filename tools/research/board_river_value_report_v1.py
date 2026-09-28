"""Independent accounting and a readable report for the river diagnostic."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('T:/Dev/GTOpen'); OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-river-value-reference-v1'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def near(a,b):assert np.isclose(a,b,rtol=1e-11,atol=1e-9),(a,b)


def main():
    rp=OUT/(PREFIX+'-registration.json'); result_path=OUT/(PREFIX+'-result.json')
    reg=read(rp); result=read(result_path)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert not result['production_modified'] and not result['final_test_evaluated'] and not result['accuracy_qualified']
    for path,digest in reg['inputs'].items():assert sha(path)==digest,path
    assert len(result['datasets'])==4
    models=('network','uniform_opponent','zero'); eligible=audited=0; maximum=0.
    for dataset in result['datasets']:
        for name,audit in dataset['audit'].items():
            assert audit['mismatches']==0 and not audit['first_mismatches']
            assert sum(x['rows'] for x in audit['pots'])==audit['rows']
            assert sum(x['rows'] for x in audit['outcomes_loss_tie_win'])==audit['rows']
            near(sum(x['source_weight'] for x in audit['pots']),audit['source_weight'])
            near(sum(x['source_weight'] for x in audit['outcomes_loss_tie_win']),audit['source_weight'])
            assert audit['maximum_endpoint_error_bb']<=reg['terminal_endpoint_tolerance_bb']
            maximum=max(maximum,audit['maximum_endpoint_error_bb']);audited+=audit['rows']
        comp=dataset['comparison']; total=comp['all']; eligible+=total['rows']
        assert total['rows']==dataset['eligible_validation_rows']==dataset['audit']['validation']['rows']
        assert sum(x['rows'] for x in comp['pots'])==total['rows']
        near(sum(x['source_weight'] for x in comp['pots']),total['source_weight'])
        for row in [total,*comp['pots']]:
            for model in models:
                p=row['predictions'][model]
                if not row['rows']:
                    assert p['mse_bb2'] is None;continue
                near(p['mse_bb2'],p['squared_error_bb2']/row['source_weight'])
                near(p['error_relative_to_zero'],p['squared_error_bb2']/row['target_energy_bb2'])
            near(row['predictions']['zero']['squared_error_bb2'],row['target_energy_bb2'])
        for model in models:near(sum(p['predictions'][model]['squared_error_bb2'] for p in comp['pots']),total['predictions'][model]['squared_error_bb2'])
    enumeration=result['enumeration'];assert enumeration['validation_rows']==eligible
    assert enumeration['total_pair_evaluations']==enumeration['unique_visible_card_sets']*990
    means={model:float(np.mean([r['comparison']['all']['predictions'][model]['mse_bb2'] for r in result['datasets']])) for model in models}
    for model in models:near(means[model],result['equal_dataset_mse_bb2'][model])
    change=(means['uniform_opponent']/means['network']-1)*100
    near(change,result['uniform_change_from_network_percent'])
    changes=[]
    for dataset in result['datasets']:
        p=dataset['comparison']['all']['predictions']
        changes.append((p['uniform_opponent']['mse_bb2']/p['network']['mse_bb2']-1)*100)
    every=all(v<0 for v in changes)
    pot_means=[]
    for i,pot in enumerate(result['datasets'][0]['comparison']['pots']):
        losses={model:float(np.mean([r['comparison']['pots'][i]['predictions'][model]['mse_bb2'] for r in result['datasets']
            if r['comparison']['pots'][i]['rows']])) for model in models}
        pot_means.append(dict(label=pot['label'],losses=losses,uniform_change_from_network_percent=(losses['uniform_opponent']/losses['network']-1)*100))
    fig,axes=plt.subplots(1,2,figsize=(12.5,4.8),layout='constrained')
    x=np.arange(4);width=.25
    labels=['Run A · BB','Run A · BTN','Run B · BB','Run B · BTN']
    colors=['#477bc3','#56a868','#aaaeb5'];names=['Saved network','Uniform opponent','Predict zero']
    for i,(model,color,name) in enumerate(zip(models,colors,names)):
        values=[r['comparison']['all']['predictions'][model]['mse_bb2'] for r in result['datasets']]
        axes[0].bar(x+(i-1)*width,values,width,label=name,color=color)
    axes[0].set_xticks(x,labels);axes[0].set_ylabel('Weighted squared error (bb²) · lower is better')
    axes[0].set_title('River call minus fold: validation prediction');axes[0].legend(frameon=False,fontsize=9)
    ratios=[p['uniform_change_from_network_percent'] for p in pot_means]
    axes[1].bar(np.arange(5),ratios,color=['#56a868' if v<0 else '#c95e57' for v in ratios])
    axes[1].axhline(0,color='#555',linewidth=.8);axes[1].set_xticks(np.arange(5),['<10','10–50','50–100','100–200','200+'])
    axes[1].set_xlabel('Current pot (bb)');axes[1].set_ylabel('Uniform reference error change vs network (%)')
    axes[1].set_title('Equal-dataset mean by pot size')
    for i,v in enumerate(ratios):axes[1].annotate(f'{v:+.1f}%',(i,v),ha='center',va='top' if v<0 else 'bottom',fontsize=9)
    for ax in axes:
        ax.spines[['right','top']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Diagnostic only: uniform opponent is not the actual betting range',fontsize=13)
    image_path=OUT/(PREFIX+'.png');assert not image_path.exists();fig.savefig(image_path,dpi=150);plt.close(fig)
    rows=[]
    for dataset,difference in zip(result['datasets'],changes):
        p=dataset['comparison']['all']['predictions']
        rows.append(f"| {dataset['dataset']} | {dataset['eligible_validation_rows']:,} | {p['network']['mse_bb2']:.3f} | {p['uniform_opponent']['mse_bb2']:.3f} | {p['zero']['mse_bb2']:.3f} | {difference:+.2f}% |")
    lines=[
        '# River call-versus-fold diagnostic', '',
        f"The visible-card uniform-opponent reference changed mean validation squared error by **{change:+.2f}%** versus the saved network. "
        f"It had lower error in **{sum(v<0 for v in changes)}/4 datasets**. This is a diagnostic on reused validation examples, not a demonstrated improvement in preflop ranges.", '',
        '## Stored payoff accounting', '',
        f"All **{audited:,}** eligible training/validation river records matched a legal win, tie or loss endpoint within the predeclared 1e-7 bb tolerance. "
        f"The largest residual was {maximum:.3g} bb. This rules out a simple payoff-unit or common-offset mismatch in these records. It does not independently verify the sampled opponent hand or establish that the sampling distribution is correct.", '',
        'Native controls covered 228 facing-bet templates, 1,104 known-deal walk records, four rake configurations, both players and changed branch offsets. '
        'Eight card fixtures matched an independent Python hand-ranking implementation and the separate native board-rank exporter; serial/parallel, suit/card order, duplicate rejection and exactly 990 opponents were checked.', '',
        '## Comparison', '',
        'Values below are source-weighted squared error in bb² for one action contrast. The denominator is source-weight sum, with no multiplication by legal-action count.', '',
        '| Dataset | Validation rows | Network error | Uniform opponent error | Zero error | Uniform vs network |',
        '|---|---:|---:|---:|---:|---:|',*rows,
        f"| Equal-dataset mean | — | {means['network']:.3f} | {means['uniform_opponent']:.3f} | {means['zero']:.3f} | {change:+.2f}% |", '',
        f'![River diagnostic]({image_path.name})','',
        '## What the reference knows', '',
        'It uses only the acting player’s two cards, the five visible river cards, the current pot, the incremental call and configured rake. '
        'Every one of the 990 physically legal opponent pairs receives equal weight. Prediction = equity × (pot + call − rake) − call. '
        'The actual hidden opponent, stored outcome and future cards are not inputs.', '',
        'A real opponent’s arriving range and decision to bet are not uniform. The reference deliberately omits those effects, so it is neither GTO nor the true expected value at the node. '
        'The saved model can use the visible betting history; the uniform hand-strength calculation cannot. Comparing their errors tests whether a simple physical relationship exposes structure missing from the learned predictions.', '',
        '## Scope and next action', '',
        ('The reference’s advantage warrants a separately registered visible-hand-strength input experiment. Keep the original loss, seeds, splits and budget fixed, include controls that separate hand strength from pot/price arithmetic, and qualify a fast runtime path before any policy trial.' if every else
         'The reference does not consistently beat the existing model. Inspect the per-dataset and pot-size results before changing training inputs; do not replace range-conditioned predictions with a uniform-opponent policy.'), '',
        'These are synthetic solver-generated examples from two runs of one restricted 200bb BB-versus-BTN game, not newly measured site hand histories. '
        'No model was trained, no new deals were sampled and the final-test partition was not scored. Accurate play across positions, stacks, sizes and multiway situations remains unproven. Production is unchanged.', '',
        '## Resources', '',
        f"End-to-end time including storage admission: {result['seconds']/60:.2f} minutes. Four CPU preparation/inference workers and up to 16 native enumeration workers were used. "
        f"{eligible:,} validation records reduced to {enumeration['unique_visible_card_sets']:,} unique visible card sets and {enumeration['total_pair_evaluations']:,} opponent-pair evaluations. "
        f"Native enumeration took {enumeration['native_seconds']:.3f} seconds. No GPU was initialized. Storage admission remained below the 800 GB allocation cap.", ''
    ]
    report_path=OUT/'BOARD-RIVER-VALUE-FINDINGS.md';assert not report_path.exists();report_path.write_text('\n'.join(lines),encoding='utf-8')
    analysis=dict(inputs={str(Path(__file__)):sha(__file__),str(rp):sha(rp),str(result_path):sha(result_path)},
        equal_dataset_mse_bb2=means,uniform_change_from_network_percent=change,lower_in_every_dataset=every,
        endpoint_rows=audited,maximum_endpoint_error_bb=maximum,pot_means=pot_means,
        report_sha256=sha(report_path),plot_sha256=sha(image_path),independent_confirmation=False,policy_adoption=False)
    dest=OUT/(PREFIX+'-analysis.json')
    with dest.open('x',encoding='utf-8') as f:json.dump(analysis,f,separators=(',',':'),allow_nan=False)
    print(json.dumps(dict(report=str(report_path),mean_change_percent=change,lower_in_every_dataset=every,endpoint_rows=audited)))


if __name__=='__main__':main()
