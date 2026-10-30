import json, shutil, sys
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
pins={'review.md':'a7a357c9cebfbdc92774f9a88b40ff64b04421c95784ef3f3a8b982e1c36d84a',
 'validation.json':'c2d029eacabaf16209cc871a22442ab0460716c5a52c07db9cdbd8ad8530711b',
 'manifest.json':'9d7201571cfc3e82fc73c44f2af044b2fdeac1e33e2a8d41ea313488bff4b413'}
folder=ar.RESEARCH/'comparisons/E020-holdout-independent-review'
for name,h in pins.items():
    assert ar.sha256(folder/name)==h
    target=ar.DASHBOARD/'evidence/E020-holdout-independent-review'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert ar.sha256(target)==h
    else:shutil.copyfile(folder/name,target)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(r for r in s['experiments'] if r['id']=='E020')
    row.update(updated_at=ar.now(),stage='Holdout independently audited; broader audit pending',
      details='Independent holdout audit confirms all six 40,550,834-byte state files, complete non-timing results and convergence records exact. At 120 iterations, all runs reached 0.255886% of pot. Median 924.2086 to 907.9290 ms (1.7615% lower); all three candidate pairs faster. All nine broader processes also passed, with their independent raw audit pending before fresh-original timing. No acceptance or deployment.')
    for e in row['evidence']:
        if e['url']=='evidence/E020-qualification/E020-wide-turn-holdout-result.json':e['label']='Full-range turn holdout result'
    url='evidence/E020-holdout-independent-review/review.md'
    if not any(e['url']==url for e in row['evidence']):row['evidence'].append({'label':'Independent full-range holdout audit','url':url})
    ar.atomic_json(ar.STATUS,s)
print('Published sealed holdout audit.')
