import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
base=ar.RESEARCH;here=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def record(p):return {'path':str(p),'sha256':ar.sha256(p)}
ready=here/'all-builds-ready.json'
assert ar.sha256(ready)=='4c53c85b4d7e83915ce31ec93d13a0dc916d8aca5c722441152e10886a6fdda0'
broader=base/'comparisons/E020-broader-qualification/report.json'
assert ar.sha256(broader)=='b3ef310d7d69ae5d05b2d5644e49cc561571d7585aae4d3175d3b6429bcb880b'
b=read(broader);assert b['status']=='pass'
assert (b['original_snapshots'],b['f32_fixtures'],b['gpu_tests'],b['continuation_tests'])==(160,3,6,3)
holdout=base/'runs/E020-wide-turn-holdout-implementation-r2/cohort/report.json'
assert ar.sha256(holdout)=='97061633cd79146984c66494d5119aaf628078c47488e2486122dd1d92ee25f4'
h=read(holdout);assert h['status']=='pass' and h['repeatable_regression'] is False
pins={
 'comparisons/E020-broader-independent-review/validation.json':'7b5613f4e8871453689ace399246662e8258a257691c91b482e26349dd2c60bd',
 'comparisons/E020-broader-independent-review/summary.md':'d0b7539ef867e11fd52d59ee4610a6f803430b0b422927ab8394deb6a7d4c173',
 'comparisons/E020-broader-independent-review/manifest.json':'467a30f4f38f08983713a2762af461b3f473ffe817d7d67698c77722f9bba17e',
 'comparisons/E020-holdout-independent-review/validation.json':'c2d029eacabaf16209cc871a22442ab0460716c5a52c07db9cdbd8ad8530711b',
 'comparisons/E020-holdout-independent-review/review.md':'a7a357c9cebfbdc92774f9a88b40ff64b04421c95784ef3f3a8b982e1c36d84a',
 'comparisons/E020-holdout-independent-review/manifest.json':'9d7201571cfc3e82fc73c44f2af044b2fdeac1e33e2a8d41ea313488bff4b413',
}
for path,sha in pins.items():assert ar.sha256(base/path)==sha,path
assert read(base/'comparisons/E020-broader-independent-review/validation.json')['verdict']=='PASS_SCOPED_BROADER_CORRECTNESS'
assert not (base/'gpu-run.lock').exists()
result={'at':ar.now(),'broader_pass':True,'holdout_pass':True,'independent_broader_review_pass':True,
 'independent_holdout_review_pass':True,'all_builds_ready':record(ready),'broader_report':record(broader),
 'holdout_report':record(holdout),'evidence_sha256':{str(base/path):sha for path,sha in pins.items()},
 'root_controls_terminal_observation':{'session':23106,'exit_code':0},
 'root_holdout_terminal_observation':{'session':9814,'exit_code':0},
 'scope':'Authorizes only the prescribed six fresh-original cumulative observations and unchanged assessment. No acceptance or deployment.'}
with (here/'qualification-ready.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(ar.sha256(here/'qualification-ready.json'))
