import json, shutil, sys
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
folder=ar.RESEARCH/'comparisons/E020-broader-independent-review'
pins={'summary.md':'d0b7539ef867e11fd52d59ee4610a6f803430b0b422927ab8394deb6a7d4c173',
 'validation.json':'7b5613f4e8871453689ace399246662e8258a257691c91b482e26349dd2c60bd',
 'manifest.json':'467a30f4f38f08983713a2762af461b3f473ffe817d7d67698c77722f9bba17e'}
for name,h in pins.items():
    assert ar.sha256(folder/name)==h
    target=ar.DASHBOARD/'evidence/E020-broader-independent-review'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert ar.sha256(target)==h
    else:shutil.copyfile(folder/name,target)
report=json.loads((ar.RESEARCH/'comparisons/E020-cumulative-comparison/report.json').read_text(encoding='utf-8'))
assert report['decision']=='qualifying' and report['accepted'] is False and report['deployed'] is False
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(r for r in s['experiments'] if r['id']=='E020')
    physical=next(r for r in s['experiments'] if r['id']=='E020R1')
    for key in ['status','correctness','reason','qualification_summary']:row[key]=physical[key]
    row.update(updated_at=ar.now(),stage='Cumulative screen passed; final independent audit pending',
      details='Fresh original comparison: 10952.0754 to 9815.2669 ms, 10.3798% aggregate reduction; all 18 non-timing results exact and no repeated fixture guard failure. Flop medians improve 10.7634% and 10.0764%; river median is 0.7128% slower with one of three pairs over 3%. Primary gain versus E015 was 2.2141%; separately audited full-range holdout was 1.7615% faster. Broader audit passed 160 original snapshots, three F32 fixtures, six GPU and three continuation controls. These percentages are separate cohorts, not additive. Final audit pending; accepted headline remains E015, no deployment.')
    for e in physical['evidence']:
        if not any(x['url']==e['url'] for x in row['evidence']):row['evidence'].append(e)
    url='evidence/E020-broader-independent-review/summary.md'
    if not any(e['url']==url for e in row['evidence']):row['evidence'].append({'label':'Independent broader correctness audit','url':url})
    for r in s['experiments']:
        if r['id'].startswith('V020-'):
            r['correctness']='pass'
    s.update(updated_at=ar.now(),active_experiment=None,stage='Auditing E020 cumulative result',
      activity='The fixed fresh-original comparison qualifies at 10.38% aggregate improvement. All required correctness and wide-range checks passed; final raw timing/state audit is pending. Accepted headline stays at 9.62% until acceptance.')
    ar.atomic_json(ar.STATUS,s)
print('Published provisional cumulative result and sealed broader audit.')
