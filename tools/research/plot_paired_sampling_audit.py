"""Plot the completed, fixed-model sampling diagnostic without refitting."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/continuation/paired-continuation-20260917/sampling-audit'
old = json.loads((OUT / 'audit.json').read_text())['families']['linear']
new = json.loads((OUT / 'evaluation.json').read_text())['results']
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout='constrained')
x = np.arange(2)
for ax in axes:
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=.15)
    ax.set_axisbelow(True)
    ax.set_xticks(x, ['Original 10 flops', 'Fresh 50 flops'])
    ax.set_ylabel('Big blinds')
for offset, key, title, color in [(-.18, 'baseline_mae_bb', 'Unchanged baseline', '#4678a8'),
                                (.18, 'rejected_control_mae_bb', 'Rejected correction', '#c3664e')]:
    values = [old['corrected'][key], new['corrected'][key]]
    bars = axes[0].bar(x + offset, values, .34, label=title, color=color)
    axes[0].bar_label(bars, fmt='%.3f', padding=3, fontsize=10)
axes[0].set_title('Adjusted prediction error\nLower is better')
axes[0].set_ylim(0, .29)
axes[0].legend(frameon=False, fontsize=9)
values = [old['corrected']['weighted_target_se_bb'], new['corrected']['weighted_target_se_bb']]
bars = axes[1].bar(x, values, .52, color='#669966')
axes[1].bar_label(bars, fmt='%.3f', padding=3)
axes[1].set_ylim(0, .16)
axes[1].set_title('Estimated flop-sampling uncertainty\nWeighted mean target standard error')
fig.suptitle('A larger flop sample improves precision, but the correction still loses', fontsize=13)
fig.supxlabel('Linear family only • Models and ranges fixed • Sampling error is not total model error', fontsize=9)
fig.savefig(OUT / 'comparison.png', dpi=170)
