"""Plot verified descriptive root/later-policy values and the prior 88 example."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())


def main():
    rp=OUT/'board-root-policy-effects-v1-registration.json';p=OUT/'board-root-policy-effects-v1-result.json'
    r=read(p);assert r['passed'] and r['registration_sha256']==sha(rp)
    for path,h in read(rp)['inputs'].items():assert sha(path)==h,path
    summary_path=Path('S:/GTOpen-research/board-root-action-replay-v1/summary.json');summary=read(summary_path)
    fig,axes=plt.subplots(1,2,figsize=(13.2,5.7),gridspec_kw={'width_ratios':[1.5,1]})
    colors=['#287db0','#da7a24'];width=.34
    labels=['Original pair','Change opening\nrange only','Change later\nplay only','Change both']
    for seed in (0,1):
        order=[(0,0),(1,0),(0,1),(1,1)]
        means=[r['cells']['means'][seed][a][b][0] for a,b in order]
        se=[r['cells']['paired_standard_errors'][seed][a][b][0] for a,b in order]
        x=np.arange(4)+(seed-.5)*width
        axes[0].bar(x,means,width,color=colors[seed],label=('Run A','Run B')[seed],
            yerr=se,capsize=3,error_kw={'linewidth':1})
        for xx,yy in zip(x,means):axes[0].text(xx,yy-.10,f'{yy:.2f}',ha='center',va='top',fontsize=9)
        row=summary['profiles'][3+4*seed]['classes'][84]
        m=[row['action_means'][a][0] for a in (1,2)];e=[row['action_standard_errors'][a][0] for a in (1,2)]
        axes[1].bar(np.arange(2)+(seed-.5)*width,m,width,color=colors[seed],yerr=e,capsize=4,
            label=('Run A','Run B')[seed],error_kw={'linewidth':1})
    axes[0].set_xticks(np.arange(4),labels,fontsize=9);axes[0].set_ylim(-1.23,.07)
    axes[0].set_title('Opening ranges and later play work together',fontsize=12,pad=15)
    axes[0].set_ylabel('BB value (bb per entry)')
    axes[0].set_xlabel('BTN policy held fixed within each run',labelpad=14)
    axes[1].set_xticks([0,1],['Call','Raise']);axes[1].set_ylabel('BB value with 88 (bb per entry)')
    axes[1].set_title('88: different policies value actions differently',fontsize=11,pad=15)
    axes[1].set_xlabel('Each candidate run uses its own later play\nand its own BTN opponent (295 deals)',fontsize=9,labelpad=12)
    for ax in axes:
        ax.axhline(0,color='#555555',linewidth=.8);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
        ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,fontsize=9)
    fig.suptitle('Verified root-action diagnostic',fontsize=16,y=.98)
    fig.text(.5,.018,'Reused evaluation data. Whiskers show ±1 descriptive standard error; these are not accuracy guarantees.',
        ha='center',fontsize=9,color='#555555')
    fig.tight_layout(rect=[0,.05,1,.94])
    target=OUT/'board-root-policy-effects-v1.png';manifest=OUT/'board-root-policy-effects-v1-plot.json'
    assert not target.exists() and not manifest.exists();fig.savefig(target,dpi=170);plt.close(fig)
    evidence=dict(inputs={str(x):sha(x) for x in (rp,p,summary_path,Path(__file__))},output=str(target),sha256=sha(target))
    with manifest.open('x') as f:json.dump(evidence,f,indent=2);f.write('\n')
    print(json.dumps(dict(output=str(target),sha256=evidence['sha256'])))


if __name__=='__main__':main()
