"""Render pass-local measurements, retaining rejected and incomplete trials."""
import json
from pathlib import Path
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
events=[json.loads(line) for line in (HERE/'events.jsonl').read_text(encoding='utf-8').splitlines()]
rows=[]
for event in events:
    if 'rows' not in event:
        continue
    result=next((r for r in event['rows'] if r.get('phase')=='result'),None)
    if result is None:
        continue
    rows.append({**event, **result, 'iteration_ms':statistics.median(result['times_ms'][1:] or result['times_ms'])})
(HERE/'results.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
if rows:
    fig,axes=plt.subplots(2,2,figsize=(12,7),layout='constrained')
    for ax,metric,title in zip(axes.flat,['iteration_ms','check_ms','sync_ms','load_ms'],
                             ['Iteration (median after first)','Accuracy check','GPU to CPU sync','Saved game load']):
        ax.barh([r['id'] for r in rows],[r[metric]/1000 for r in rows],color='#518bba')
        ax.set_title(title); ax.set_xlabel('seconds'); ax.grid(axis='x',alpha=.2)
    fig.suptitle('Preflop autoresearch — fixed input and iteration budget')
    fig.savefig(HERE/'progress.png',dpi=140)
    plt.close(fig)
print(f'{len(rows)} completed measurements rendered')
