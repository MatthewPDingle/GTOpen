"""Render the complete descriptive trajectory after independent readback."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
source=OUT/'board-root-trajectory-v1-result.json'
review=json.loads((OUT/'board-root-trajectory-v1-review.json').read_text())
assert review['passed'] and review['source_result_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
result=json.loads(source.read_text());cross=result['candidate_cross_seed_trajectory']
destination=OUT/'board-root-trajectory-v1.png'
assert not destination.exists()
fig,axes=plt.subplots(1,2,figsize=(12.6,4.6),gridspec_kw={'width_ratios':[1.6,1]},layout='constrained')
rows=cross['played_prefixes']
axes[0].plot([r['played_generations'] for r in rows],[100*r['weighted_tv'] for r in rows],color='#2574a8',linewidth=2)
axes[0].set(title='Disagreement between cumulative averages',xlabel='Played generations included',ylabel='Weighted disagreement (%)',ylim=(0,60),xlim=(1,78))
axes[0].grid(alpha=.2)
values=[100*r['weighted_tv'] for r in cross['windows']]
bars=axes[1].bar(['First 26','Middle 26','Last 26'],values,color=['#789baa','#427c9e','#2574a8'],width=.65)
axes[1].bar_label(bars,labels=[f'{v:.1f}%' for v in values],padding=5)
axes[1].set(title='Disagreement in fixed training windows',ylabel='Weighted disagreement (%)',ylim=(0,60))
axes[1].grid(axis='y',alpha=.2);axes[1].set_axisbelow(True)
fig.suptitle('Saved training history: two board-root runs\nDescriptive consistency, not an accuracy or convergence certificate',fontsize=13)
fig.savefig(destination,dpi=150);plt.close(fig)
print(json.dumps({'plot':str(destination),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'visual_review_required':True}))
