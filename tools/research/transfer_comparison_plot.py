"""Plot the complete registered transfer comparison; never fills missing runs."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    panels = [('reserved10','Reserved 10\n(stress panel)'),
              ('validation95','Independent 95\n(eligible population)')]
    sources = [('ab','10 training flops','#4277aa'),
               ('report47','47 training flops','#d58a36')]
    values, inputs = {}, {}
    for panel,_ in panels:
        for source,_,_ in sources:
            path = OUT/f'held-{panel}-{source}-result-review.json'
            result = json.loads(path.read_text())
            assert result['preflop_exactly_preserved'] is True
            assert result['iteration'] == 2000
            e = result['final']
            assert 0 <= e['postflop_gap_total'] < .01
            assert np.isfinite(e['gap_total']) and e['gap_total'] >= 0
            values[panel,source] = e
            inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    fig,axes = plt.subplots(1,2,figsize=(12,5.5))
    for ax,key,title in zip(axes,['postflop_gap_total','gap_total'],
                           ['Postflop numerical residual','Remaining combined deviation gain']):
        for i,(source,label,color) in enumerate(sources):
            x = np.arange(len(panels))+(i-.5)*.30
            y = [values[panel,source][key] for panel,_ in panels]
            bars = ax.bar(x,y,.28,label=label,color=color)
            ax.bar_label(bars,labels=[f'{v:.6f}' for v in y],padding=4,fontsize=9)
        ax.set_xticks(np.arange(len(panels)),[label for _,label in panels])
        ax.set_title(title,fontsize=13,pad=14)
        ax.set_ylabel('bb at the entering two-player decision')
        ax.grid(axis='y',alpha=.22)
        ax.set_axisbelow(True)
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_yscale('log')
    axes[0].set_ylim(5e-5,.025)
    axes[0].axhline(.01,color='#666',ls='--',lw=1.2,label='Registered numerical gate')
    axes[0].legend(loc='upper left',bbox_to_anchor=(0,1.0),fontsize=8,framealpha=.95)
    axes[1].set_ylim(0,max(v['gap_total'] for v in values.values())*1.19)
    axes[1].legend(loc='upper right',fontsize=8)
    fig.suptitle('Converged postflop responses do not establish preflop transfer accuracy',fontsize=15,y=.99)
    fig.text(.02,.05,'Both players\' policies and postflop responses differ by source. These are conditional branch values,',fontsize=9)
    fig.text(.02,.02,'not head-to-head win rates or full-deck exploitability estimates. The two panels target different board populations.',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,.94))
    fig.savefig(OUT/'independent-transfer-comparison.png',dpi=160)
    plt.close(fig)
    evidence = dict(inputs_sha256=inputs,
                    values={f'{panel}/{source}':e for (panel,source),e in values.items()},
                    note='Complete original four comparisons only. Numerical postflop gates do not imply strategic transfer accuracy.')
    (OUT/'independent-transfer-comparison.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print('Rendered all four complete registered transfer comparisons.')


if __name__ == '__main__':
    main()
