"""Render the registered conditional-game comparison without selecting runs."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import conditional_hu_audit as study
from wizard_continuation_study import read,write,sha


def main():
    manifest=study.frozen();review=read(study.OUT/'review.json')
    records=[r for r in review['results'] if r['iteration']==50000]
    saved=review['saved']['independent']
    selected=[saved]+[r['evaluations']['compatible' if r['job'].startswith('compatible') else 'independent'] for r in records]
    labels=['Saved policy','Independent\nre-solved','Compatible\nfresh','Compatible\nsaved seed']
    colors=['#647bbd','#80a866','#d65454','#873d67']
    fig,axes=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
    freq=np.array([x['nodes']['0']['action_frequencies'] for x in selected])*100
    bottom=np.zeros(4)
    for a,label in enumerate(['Fold','Call','4-bet to 45','Jam to 200']):
        axes[0].bar(labels,freq[:,a],bottom=bottom,color=colors[a],label=label)
        bottom+=freq[:,a]
    axes[0].set(ylabel='UTG action frequency (%)',ylim=(0,100),title='Both players adapt; incoming ranges stay fixed')
    axes[0].legend(loc='lower left',fontsize=8)
    aa=[np.array(read(study.OUT/'subtree.json')['nodes'][0]['strategy']).reshape(-1,169)[:,168]]
    aa.extend(np.array(read(study.OUT/(j+'.json'))['records'][-1]['policy']['0'])[:,168] for j in manifest['jobs'])
    bottom=np.zeros(4)
    for a in range(4):
        values=np.array(aa)[:,a]*100;axes[1].bar(labels,values,bottom=bottom,color=colors[a]);bottom+=values
    axes[1].set(ylabel='AA action frequency (%)',ylim=(0,100),title='Card accounting alone does not fix the AA incentive')
    fig.suptitle('Research only: the saved UTG–LJ conditional branch\nFixed Balanced postflop values; configured 4% rake / 6 bb cap',fontsize=12)
    fig.savefig(study.OUT/'conditional-comparison.png',dpi=160)
    paths=[study.OUT/'review.json',study.OUT/'pure-plan-verification.json',study.OUT/'conditional-comparison.png',
        study.s.ROOT/'tools/research/conditional_hu_verify.py',study.s.ROOT/'tools/research/conditional_hu_report.py']
    paths.extend(study.OUT/(j+'.json') for j in manifest['jobs'])
    write(study.OUT/'result-hashes.json',{p.relative_to(study.s.ROOT).as_posix():sha(p) for p in paths})


if __name__=='__main__':main()
