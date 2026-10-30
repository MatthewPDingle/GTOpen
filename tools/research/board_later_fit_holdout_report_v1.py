"""Summarize the fixed fitting-budget experiment without selecting on test data."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import hashlib
import json
from pathlib import Path
import numpy as np
from board_prefix_publication_v1 import atomic_json

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-later-fit-holdout-v1'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rp=OUT/(PREFIX+'-registration.json');path=OUT/(PREFIX+'-result.json')
    reg,result=read(rp),read(path)
    assert result['passed'] and result['complete'] and not result['accuracy_qualified']
    assert result['registration_sha256']==sha(rp) and reg['budgets']==[512,2048,8192]
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    records=result['datasets'];tests=result['final_tests'];selected=result['selection']['selected_steps']
    assert len(records)==len(tests)==len(reg['datasets'])==4
    scores=[]
    for i,step in enumerate(reg['budgets']):
        assert all(r['checkpoints'][i]['step']==step for r in records)
        value=float(np.mean([r['checkpoints'][i]['validation']['postflop']['normalized_loss'] for r in records]))
        assert abs(value-result['selection']['scores'][i]['mean_postflop_validation_loss'])<1e-12
        scores.append((value,step))
    assert min(scores)[1]==selected
    selection_path=Path(records[0]['checkpoints'][0]['weights']).parent/'selection.json'
    assert sha(selection_path)==result['selection_sha256']
    for r in records:
        for p in r['checkpoints']:assert sha(p['weights'])==p['weights_sha256']
    rows=[]
    for i,(r,test) in enumerate(zip(records,tests)):
        assert r['dataset']==test['dataset']==reg['datasets'][i]['name']
        assert [x['steps'] for x in test['checkpoints']]==sorted({512,selected})
        baseline=next(x for x in test['checkpoints'] if x['steps']==512)
        chosen=next(x for x in test['checkpoints'] if x['steps']==selected)
        gains={key:100*(baseline['metrics'][key]['normalized_loss']-chosen['metrics'][key]['normalized_loss'])/
            baseline['metrics'][key]['normalized_loss'] for key in ('all','postflop','preflop','flop','turn','river')}
        first=r['checkpoints'][0];last=next(p for p in r['checkpoints'] if p['step']==selected)
        rows.append(dict(dataset=r['dataset'],baseline_test_postflop=baseline['metrics']['postflop']['normalized_loss'],
            selected_test_postflop=chosen['metrics']['postflop']['normalized_loss'],test_error_reduction_percent=gains,
            training_error_reduction_percent=100*(first['normalized_training_loss']-last['normalized_training_loss'])/first['normalized_training_loss'],
            fitting_time_ratio=last['elapsed_fit_seconds']/first['elapsed_fit_seconds'],
            selected_validation_postflop=last['validation']['postflop']['normalized_loss']))
    base=float(np.mean([x['baseline_test_postflop'] for x in rows]));chosen=float(np.mean([x['selected_test_postflop'] for x in rows]))
    reduction=100*(base-chosen)/base
    successes=sum(x['selected_test_postflop']<x['baseline_test_postflop'] for x in rows)
    if selected==512:verdict='Longer fitting did not win the registered validation comparison.'
    elif reduction>0:verdict=f'Longer fitting improved average held-out prediction; {successes}/4 datasets improved.'
    else:verdict='The validation-selected longer fit did not improve average final-test prediction.'
    validation_increase={str(step):100*(value-scores[0][0])/scores[0][0] for value,step in scores}
    summary=dict(inputs={str(p):sha(p) for p in (rp,path,Path(__file__))},selected_steps=selected,
        verdict=verdict,mean_postflop_test_loss_reduction_percent=reduction,rows=rows,
        mean_validation_error_increase_percent=validation_increase,
        full_training_or_poker_strength_qualified=False,seconds=result['seconds'],retained_bytes=result['retained_bytes'])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    x=reg['budgets']
    for label,values,color in [('Training (all targets)',[np.mean([r['checkpoints'][i]['normalized_training_loss'] for r in records]) for i in range(3)],'#287eaf'),
        ('Validation (postflop)',[v for v,s in scores],'#da812b')]:
        axes[0].plot(x,values,'o-',label=label,color=color)
    axes[0].set_xscale('log',base=2);axes[0].set_xticks(x,[str(v) for v in x]);axes[0].set_xlabel('Optimizer steps')
    axes[0].set_ylabel('Mean normalized squared error');axes[0].set_title('Fixed architecture, four saved datasets')
    axes[0].grid(alpha=.2);axes[0].legend(fontsize=9)
    labels=['Run A BB','Run A BTN','Run B BB','Run B BTN']
    values=([100*(r['checkpoints'][0]['validation']['postflop']['normalized_loss']-
        r['checkpoints'][2]['validation']['postflop']['normalized_loss'])/r['checkpoints'][0]['validation']['postflop']['normalized_loss'] for r in records]
        if selected==512 else [r['test_error_reduction_percent']['postflop'] for r in rows])
    axes[1].bar(labels,values,color=['#287eaf' if v>=0 else '#be5555' for v in values])
    axes[1].axhline(0,color='#555',lw=.8);axes[1].set_ylabel(('Validation' if selected==512 else 'Final-test')+' error reduction (%)')
    axes[1].set_title('8,192 steps vs 512: all four got worse' if selected==512 and all(v<0 for v in values)
        else f'{8192 if selected==512 else selected:,} steps vs 512')
    axes[1].grid(axis='y',alpha=.2)
    for i,v in enumerate(values):axes[1].annotate(f'{v:.1f}%',(i,v),xytext=(0,5 if v>=0 else -12),textcoords='offset points',ha='center')
    axes[1].margins(y=.2)
    fig.suptitle('Does more later-play training generalize?',fontsize=15)
    fig.supxlabel('Withheld visible inputs from retained training histories; not a poker-strength or equilibrium test.',fontsize=9)
    png=OUT/(PREFIX+'-learning-curve.png');assert not png.exists();fig.savefig(png,dpi=170);plt.close(fig)
    summary['plot_sha256']=sha(png)
    atomic_json(OUT/(PREFIX+'-analysis.json'),summary)
    text=['# Later-play fitting-budget experiment','',verdict,'',
        (f'Validation selected the original **512-step** budget. Mean postflop validation error was **{validation_increase["2048"]:.2f}% higher at 2,048 steps** and **{validation_increase["8192"]:.2f}% higher at 8,192 steps**. The prescribed final-test comparison therefore contains only the baseline, with mean loss {base:.6f}; it is not an independent comparison of longer fits.' if selected==512 else
        f'Validation selected **{selected:,} steps**. Across the four equally weighted datasets, final-test postflop loss changed from **{base:.6f}** to **{chosen:.6f}**: **{reduction:.2f}% less prediction error**. This is not a percentage improvement in preflop accuracy.'),'',
        '| Dataset | 512 train / validation loss | 2,048 train / validation loss | 8,192 train / validation loss |',
        '|---|---:|---:|---:|']
    for r in records:
        cells=[f"{p['normalized_training_loss']:.4f} / {p['validation']['postflop']['normalized_loss']:.4f}" for p in r['checkpoints']]
        text.append('| '+r['dataset']+' | '+' | '.join(cells)+' |')
    text+=['',
        '| Dataset | Training error reduction | Test postflop error reduction | Fitting-time ratio |',
        '|---|---:|---:|---:|']
    for row in rows:text.append(f"| {row['dataset']} | {row['training_error_reduction_percent']:.2f}% | {row['test_error_reduction_percent']['postflop']:.2f}% | {row['fitting_time_ratio']:.2f}x |")
    text+=['','Positive reductions mean lower error. Training includes all targets; the primary validation/test measure is postflop because separate tables override preflop neural predictions. Time ratios include resource pauses during fitting and exclude setup/checkpoint scoring.','',
        '| Dataset | Flop test reduction | Turn test reduction | River test reduction |','|---|---:|---:|---:|']
    for row in rows:
        g=row['test_error_reduction_percent'];text.append(f"| {row['dataset']} | {g['flop']:.2f}% | {g['turn']:.2f}% | {g['river']:.2f}% |")
    text+=['',f'![Fitting curves]({png.name})','',
        '## Scope and limitations','',
        'The 302/64/64/4 architecture, Adam learning rate 0.003, initialization and data were fixed. Each dataset used one continuous trajectory with checkpoints at 512, 2,048 and 8,192 steps. A salted 70/15/15 split kept identical visible inputs together. Scaling used only training targets. Validation selected a single common budget before final-test scoring of that budget and the baseline. Raw-row losses preserve source weights, legal-action masks and target variance.','',
        'These are held-out observations from the same adaptive training histories, not independent fresh-game trials. Related positions and earlier policies can occur across splits. The result does not isolate optimization from representation limits, prove an equilibrium, establish agreement with GTO Wizard, or establish transfer to different stacks or positions.','',
        f"The run took {result['seconds']/60:.2f} minutes and retained {result['retained_bytes']/1e6:.2f} MB of study files. Production was unchanged.",'',
        '## Next decision','']
    if selected>512 and reduction>0:
        text+=['A separately registered, short paired training comparison is justified. Keep the original sampling and root method fixed, change only the selected fitting budget, and evaluate resulting complete policies on fresh deals. First budget its extra runtime; improved regression loss alone does not justify production deployment.']
    else:
        text+=['Do not increase production fitting time on this evidence. A bounded validation-only comparison of shorter fitting budgets is the cheapest next check, before considering regularization, representation and target variance. Keep the final test closed during that follow-up and require fresh full-policy evaluation before any adoption. Preserve this unsuccessful longer-fitting comparison.']
    destination=OUT/'BOARD-LATER-FIT-HOLDOUT-FINDINGS.md';assert not destination.exists()
    destination.write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(json.dumps(dict(verdict=verdict,selected_steps=selected,test_error_reduction_percent=reduction,report=str(destination))))


if __name__=='__main__':main()
