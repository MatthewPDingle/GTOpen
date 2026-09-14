"""Audit complete-state and compiler evidence for ordinary static tables."""
import hashlib,json,re
from pathlib import Path
from check_d09 import entries
P=Path(__file__).resolve().parent;R=P/'raw';ROOT=P.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for stage in ['build','test']:
    r=read(R/f'c24-integration-{stage}-v1-exit.json');assert r['returncode']==0 and r['reason'] is None and r['seconds']<=300
    for file,digest in r['inputs'].items():assert sha(file)==digest,file
    for file,digest in r['solver_source_files'].items():assert sha(ROOT/file)==digest,file
    records.append(r)
assert records[0]['solver_source_files']==records[1]['solver_source_files']
for file,entry in read(P/'artifacts/c24-integration-source-map.json').items():
    assert sha(ROOT/file)==sha(P/entry['archive'])==entry['sha256']
log=(R/'c24-integration-test-v1.log').read_text(encoding='utf-8');assert '4 passed; 0 failed; 0 ignored' in log
out=R/'c24-integrated-v1';cases=read(out/'states.json')
assert cases==[dict(players=n,fixed=f,batch=b,rounds=3,exact=True) for n in [3,4,7,9] for f in [False,True] for b in [1,4,5,32]]
assert read(out/'zero-recovery.json')==dict(exact=True,fixtures=4,zero_states=5,gates=2)
saved=read(out/'continuation.json');assert saved['saved_exact'] and saved['actual_stop'] and saved['replay_exact'] and saved['reload_rounds']==3 and saved['matched_player'] in [0,1,3]
assert sha(out/'saved-false.gtop')==sha(out/'saved-true.gtop')
assert read(out/'allocation.json')==dict(actual_oom_stages=[1,2,3],leaked_bytes=0,recovery_rounds=3)
source=(out/'candidate.cu').read_text(encoding='utf-8');base=(R/'r04-integrated-v1/candidate.cu').read_text(encoding='utf-8')
assert source.startswith(base)
expected=base
for old,new in [('pf_static_cdf','pf_ordinary_static_cdf'),('pf_static_terminal','pf_ordinary_static_terminal')]:
    start=base.index('extern "C" __global__ void '+old+'(');end=start+base[start:].index('\n}\n')+3
    function=base[start:end].replace(old,new)
    alias='    if (aliases[blockIdx.x] != blockIdx.x) return;\n' if old=='pf_static_cdf' else '                cdf_slot = aliases[cdf_slot];\n'
    assert function.count(alias)==1 and function.count('const u32* aliases, ')==1
    function=function.replace(alias,'').replace('const u32* aliases, ','');assert 'aliases' not in function
    expected+=function
assert source==expected
a=entries((R/'r04-integrated-v1/candidate.ptx').read_text());b=entries((out/'candidate.ptx').read_text())
assert set(b)-set(a)=={'pf_ordinary_static_cdf','pf_ordinary_static_terminal'}
assert all(a[k]==b[k] for k in a)
resources=read(out/'resources.json');assert resources==[dict(kernel='writer',local_bytes=0,registers=25,shared_bytes=0),dict(kernel='terminal',local_bytes=0,registers=40,shared_bytes=44)]
frozen=read(R/'c24-integration-frozen.json');assert sha(frozen['path'])==frozen['sha256']
result=dict(verified=True,admitted=True,retained=False,
    status='Ordinary GPU integration exact; native saved-game timing next',
    full_solver_integrated=True,normal_app_integrated=False,complete_state_cases=len(cases),rounds_per_case=3,
    zero_recovery_exact=True,actual_stop_replay_exact=True,allocation_failure_stages=[1,2,3],
    saved_sha256=sha(out/'saved-true.gtop'),interrupted_sha256=sha(out/'interrupted.gtop'),
    unchanged_existing_ptx_entries=len(a),resources=resources,source_sha256=sha(out/'candidate.cu'),ptx_sha256=sha(out/'candidate.ptx'),
    frozen_executable=frozen,guarded_build_seconds=records[0]['seconds'],guarded_test_seconds=records[1]['seconds'],
    scope='Research-only ordinary-path numerical qualification on controlled fixtures. Their batch sizes are explicitly equal on both paths. Native user-game layout, full saved checkpoints and paired runtime remain; no speed claim or deployment.')
(R/'c24-integration-verified.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'c24-verified.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
