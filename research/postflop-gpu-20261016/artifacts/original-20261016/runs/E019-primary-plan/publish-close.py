import json, shutil, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
base=ar.RESEARCH
pins={'validation.json':'9e46388ac83008c2523c2f76c72edf873a9dba044ace8c4868635c5d4b079bd6',
      'summary.md':'3696c39e1d93d7cdd274903fc03af2f8ef32a1325990d863cdc242776ec75ad7',
      'manifest.json':'37485f174e1df42e0ae23917634eea761a343e352adcf2878f153963309fb53c'}
review=base/'comparisons/E019-independent-review'
for name,h in pins.items(): assert ar.sha256(review/name)==h
links=[]
for source in [review/n for n in pins]+[base/'runs/E019-cleanup-restored-E015.json',base/'runs/E019-qualification-plan/terminal-inapplicable.json']:
    destination=ar.DASHBOARD/'evidence'/source.parent.name/source.name
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists(): assert ar.sha256(source)==ar.sha256(destination)
    else: shutil.copyfile(source,destination)
    links.append({'label':source.name,'url':'evidence/'+source.parent.name+'/'+source.name})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    for identity in ['E019','E019R1']:
        row=next(r for r in s['experiments'] if r['id']==identity)
        row.update(updated_at=ar.now(),stage='Rejected; independent audit complete',
            reason='Rejected and independently audited: 9981.6832 to 9910.0980 ms, 0.7172% observed complete-cycle improvement, below the 2% gate. All 18 complete non-timing records and 138 convergence checks match exactly; 84 unit tests passed. No fixture guard failed. Broader qualification was not run after the failed speed screen. Accepted E015 source restored; no integration or deployment.',
            details='Independent audit verified 96 input artifacts and 754 assertions. All fixed samples and failed audit attempts are preserved. Component timings varied and do not establish a unique cause or statistical significance. All 162 accepted E015 source entries match after restoring only the candidate CUDA file.')
        for e in [dict(links[1],label='Independent terminal audit'),dict(links[0],label='Independent validation details'),dict(links[3],label='Exact accepted-source restoration')]:
            if not any(x['url']==e['url'] for x in row['evidence']):row['evidence'].append(e)
    unit=next(r for r in s['experiments'] if r['id']=='V019-unit')
    unit.update(correctness='pass',reason='Independent audit confirms 84 passed, zero failed and four ignored; same inventory as accepted E015. Unit evidence only, no timing or acceptance claim.')
    s.update(updated_at=ar.now(),stage='Reviewing showdown index caching',active_experiment=None,
        activity='E019 rejection is independently audited and accepted E015 source is restored. Reviewing a distinct integer-index cache for showdown evaluation. Accepted complete-solve improvement remains 9.62%.')
    ar.atomic_json(ar.STATUS,s)
print('Published E019 terminal audit; accepted performance unchanged.')
