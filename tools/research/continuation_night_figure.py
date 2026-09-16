"""Plot completed accuracy and settling evidence, without combining their gates."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'research/preflop-evolution/continuation'
OUT=BASE/'night-shift-20260916'


def read(path):return json.loads((BASE/path).read_text())


def main():
    menu=read('flop-menu-20260916/evaluation.json')
    settling=read('policy-stability-20260916/result.json')
    assert menu['accuracy_screen_passed'] and not settling['both_signals_passed']
    colors={'original':'#51769b','candidate':'#b14e45'}
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':12})
    fig,(left,right)=plt.subplots(1,2,figsize=(12,6),gridspec_kw={'width_ratios':[1.15,1]})
    fig.subplots_adjust(left=.18,right=.97,top=.77,bottom=.26,wspace=.37)
    cases=menu['cases'];ys=np.arange(len(cases))
    labels=[]
    for c in cases:
        arm,_,_,num,kind=c['case'].split('-')
        labels.append(f"{'Baseline' if arm=='original' else 'Learned'} range {int(num)+1} / {'wider' if kind=='expanded' else 'simple'}")
    left.barh(ys-.16,[c['mae_pct_pot']['balanced'] for c in cases],.3,color=colors['original'],label='Existing model')
    left.barh(ys+.16,[c['mae_pct_pot']['candidate'] for c in cases],.3,color=colors['candidate'],label='Full learned predictor')
    left.set(yticks=ys,yticklabels=labels,xlabel='Hand-value error (% of pot); lower is better',xlim=(0,11))
    left.invert_yaxis();left.set_title('Fresh-flop value accuracy\n160 reference solves, eight comparisons',loc='left',pad=14)
    left.legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.20),fontsize=9,ncol=2,borderaxespad=0)
    for arm in ['original','candidate']:
        initial=read(f'policy-transfer-optimized-20260916/N20/{arm}/iteration-500.json')
        ys=[sum(initial['gaps'])]+[r['gap_total_bb'] for r in settling['trajectory'][arm]]
        right.plot([500,1000,1500],ys,marker='o',lw=2,color=colors[arm],label=arm)
        right.annotate(f'{ys[-1]:.5f}',(1500,ys[-1]),xytext=(-3,8),textcoords='offset points',ha='right',color=colors[arm])
    right.axhline(.005,color='#555',ls='--',lw=1)
    right.text(510,.0055,'Registered target: 0.005 bb',fontsize=9,color='#555')
    right.set(yscale='log',xticks=[500,1000,1500],xlabel='Preflop iterations',ylabel='Frozen-value gap (bb, log scale)')
    right.set_title('Practical settling\nFull predictor misses the target',loc='left',pad=14)
    a=settling['additional_learning_seconds']
    fig.suptitle('Full predictor: better hand-value estimates, unresolved settling',x=.035,ha='left',fontsize=17,fontweight='bold',y=.965)
    fig.text(.035,.875,'Accuracy improved 31–43% in the wider-menu study. The full predictor still failed the practical settling screen.',fontsize=11)
    fig.text(.035,.115,f"Same additional 1,000 steps: existing model {a['original']/60:.1f} min; learned predictor {a['candidate']/60:.1f} min ({100*(a['candidate']/a['original']-1):.1f}% longer).",fontsize=10)
    fig.text(.035,.055,'Separate experiments and approximate continuation games. These gaps are not full-game exploitability.\nRestricted postflop menus; familiar range contexts with fresh boards. No production deployment.',fontsize=9,color='#555')
    fig.savefig(OUT/'accuracy-and-settling.png',dpi=170,facecolor='white')
    plt.close(fig)
    print(OUT/'accuracy-and-settling.png')


if __name__=='__main__':main()
