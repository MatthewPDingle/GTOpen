"""Combine completed fit-budget diagnostics; no refitting or test selection."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import hashlib
import json
from pathlib import Path
import numpy as np
from board_prefix_publication_v1 import atomic_json

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())


def main():
    short_path=OUT/'board-later-fit-early-budget-v1-result.json'
    long_path=OUT/'board-later-fit-holdout-v1-result.json'
    short,long=read(short_path),read(long_path)
    assert short['passed'] and short['complete'] and long['passed'] and long['complete']
    assert short['selected_steps']==long['selection']['selected_steps']==512
    for a,b in zip(short['datasets'],long['datasets']):
        assert a['dataset']==b['dataset']
        assert a['baseline_reproduction']==dict(maximum_parameter_difference=0.,maximum_validation_loss_difference=0.)
        assert a['checkpoints'][-1]['validation']==b['checkpoints'][0]['validation']
    steps=[64,128,256,512,2048,8192];curves=[]
    for a,b in zip(short['datasets'],long['datasets']):
        points=a['checkpoints']+b['checkpoints'][1:]
        assert [p['step'] for p in points]==steps
        curves.append([p['validation']['postflop']['normalized_loss'] for p in points])
    mean=np.mean(curves,axis=0);extra=100*(mean/mean[3]-1)
    assert np.argmin(mean)==3 and all(np.argmin(row)==3 for row in curves)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
    for i,row in enumerate(np.array(curves)):
        ax.plot(steps,100*(row/row[3]-1),color='#aaaaaa',alpha=.6,lw=1,label='Individual datasets' if i==0 else None)
    ax.plot(steps,extra,'o-',color='#267cae',lw=2.5,label='Four-dataset mean')
    ax.scatter([512],[0],color='#479047',s=90,zorder=4)
    for x,y in zip(steps,extra):ax.annotate(f'{y:+.2f}%' if x!=512 else 'Best tested', (x,y),
        xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
    ax.set_xscale('log',base=2);ax.set_xticks(steps,[f'{x:,}' for x in steps]);ax.set_xlabel('Optimizer steps')
    ax.set_ylabel('Extra postflop validation error vs 512 steps (%)')
    ax.set_title('Changing training duration alone did not improve predictions')
    ax.grid(alpha=.2);ax.legend(fontsize=9);ax.margins(y=.2)
    fig.supxlabel('Same four retained datasets and validation split. No poker-strength claim.',fontsize=9)
    png=OUT/'board-later-fit-budget-summary-v1.png';assert not png.exists();fig.savefig(png,dpi=170);plt.close(fig)
    lines=['# Training duration is not the current fix','',
        'Across both completed diagnostics, **512 steps was best in each of the four datasets**. Shorter fits had not learned enough; longer fits increasingly overfit the retained examples. This narrows the next research direction but does not establish accurate preflop ranges.','',
        '| Steps | Mean postflop validation loss | Extra error versus 512 |','|---:|---:|---:|']
    for step,value,delta in zip(steps,mean,extra):lines.append(f'| {step:,} | {value:.6f} | {delta:+.2f}% |')
    lines+=['',f'![Training-budget comparison]({png.name})','',
        'The shorter-budget follow-up reproduced every saved 512-step parameter and validation loss exactly. It did not score the final test again. Both diagnostics used the same validation partition, so this is a tuning result rather than fresh confirmation.','',
        'The longer-fit street readback found the same pattern on flop, turn and river in every dataset. At 8,192 steps, mean postflop training error was 25.34% lower while validation error was 9.32% higher.','',
        '## Next experiment','',
        'Test explicit public betting-state inputs: pot size, remaining stacks, amount to call, call price and available action costs. These are currently represented indirectly through the public branch and action history. Keep existing card/history inputs and targets unchanged.','',
        'The new native exporter has passed known-value controls across five pot/stack fixtures. Its 450 public decision templates join correctly to all 815,799 rows in the four retained datasets. New input columns start with zero weights, preserving the original initial function. No network has yet been trained with these added inputs, and no range improvement is claimed.','',
        'A separately registered validation comparison should hold the 512-step budget, data, normalization, learning rate and initialization fixed. Keep the final test closed during exploratory tuning; require fresh full-policy evaluation before adoption. Production remains unchanged.']
    report=OUT/'BOARD-LATER-FIT-BUDGET-SUMMARY.md';assert not report.exists();report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    atomic_json(OUT/'board-later-fit-budget-summary-v1.json',dict(inputs={str(p):sha(p) for p in (short_path,long_path,Path(__file__))},
        steps=steps,validation_mean=mean.tolist(),extra_error_percent=extra.tolist(),
        plot_sha256=sha(png),report_sha256=sha(report),selected_steps=512,independent_confirmation=False))
    print(json.dumps(dict(best_steps=512,extra_error_percent=dict(zip(steps,extra.tolist())),report=str(report))))


if __name__=='__main__':main()
