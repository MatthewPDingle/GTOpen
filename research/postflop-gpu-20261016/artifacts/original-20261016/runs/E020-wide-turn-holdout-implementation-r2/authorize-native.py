import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
here=Path(__file__).resolve().parent
phase=sys.argv[1]
assert phase in ['resource','cohort']
build=here/'build-authorization.json'
assert ar.sha256(build)=='c98bed5d2b8effd17df9a46ad2d39b074cc4a818cf4035d3a7e9ac73a8ebb60a'
record=json.loads(build.read_text(encoding='utf-8'))
ready=ar.RESEARCH/'runs/E020-qualification-plan-r3/all-builds-ready.json'
ready_hash='4c53c85b4d7e83915ce31ec93d13a0dc916d8aca5c722441152e10886a6fdda0'
assert ar.sha256(ready)==ready_hash
review=ar.RESEARCH/'comparisons/E020-build-readiness-review/readiness-r2-validation.json'
review_hash='505a129c4a3996aa4bd3ae790cb286448374f2f530e543c6e62b16f1d720b5a8'
assert ar.sha256(review)==review_hash
record['required_evidence'].append({'path':str(review),'sha256':review_hash})
record.update(at=ar.now(),phase=phase,all_builds_ready={'path':str(ready),'sha256':ready_hash},
 scope='Reviewed R2 native '+phase+' only, under the unchanged prospective holdout protocol. No acceptance or deployment.')
if phase=='cohort':
    assert len(sys.argv)==3
    resource=here/'resource/report.json'
    assert ar.sha256(resource)==sys.argv[2]
    assert json.loads(resource.read_text(encoding='utf-8'))['status']=='pass'
    record['resource_report']={'path':str(resource),'sha256':sys.argv[2]}
for item in record['required_evidence']:assert ar.sha256(Path(item['path']))==item['sha256']
assert not (ar.RESEARCH/'gpu-run.lock').exists()
with (here/(phase+'-authorization.json')).open('x',encoding='utf-8',newline='\n') as f:
    json.dump(record,f,indent=2);f.write('\n')
print(ar.sha256(here/(phase+'-authorization.json')))
