import json, shutil, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
pins={
 'runs/E020-wide-turn-holdout-implementation-r2/cohort/report.json':'97061633cd79146984c66494d5119aaf628078c47488e2486122dd1d92ee25f4',
 'comparisons/E020-build-readiness-review/readiness-r2-summary.md':'d35790c57d7ccc6fc5a263ac1f7d87819ee7e22f2ee417320d46a7fe580c8476',
}
links=[]
for relative,h in pins.items():
    source=ar.RESEARCH/relative;assert ar.sha256(source)==h
    name='E020-wide-turn-holdout-result.json' if source.name=='report.json' else source.name
    target=ar.DASHBOARD/'evidence/E020-qualification'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert ar.sha256(target)==h
    else:shutil.copyfile(source,target)
    links.append('evidence/E020-qualification/'+name)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(r for r in s['experiments'] if r['id']=='E020')
    row.update(updated_at=ar.now(),stage='Wide-range holdout passed; broader controls running',
      details='Corrected isolated builds passed independent linked-source/readiness review. The six fixed full-range turn runs passed exact compressed-state byte and non-timing/convergence comparisons: median 924.2086 to 907.9290 ms, 1.7615% lower; candidate faster in all three pairs. Holdout raw audit and broader controls are pending. This separate holdout is not merged into the primary score or accepted headline; no deployment.')
    for label,url in zip(['Full-range turn holdout result (audit pending)','Corrected build-readiness audit'],links):
        if not any(e['url']==url for e in row['evidence']):row['evidence'].append({'label':label,'url':url})
    ar.atomic_json(ar.STATUS,s)
print('Published provisional holdout pass; runner owns current activity.')
