import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
base=ar.RESEARCH
here=Path(__file__).resolve().parent
holdout=base/'runs/E020-wide-turn-holdout-implementation-r2'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def record(p):return {'path':str(p),'sha256':ar.sha256(p)}
assert not (base/'gpu-run.lock').exists()
complete_path=base/'runs/E020-qualification-build/complete.json'
complete=read(complete_path)
assert complete['status']=='pass' and len(complete['binary_pins'])==7
assert complete['source_sha256']==ar.source_identity()['source_sha256']
hr=read(holdout/'build/report.json')
assert hr['status']=='pass' and hr['holdout_binary_hashes_distinct'] is True
assert hr['separate_empty_arm_targets'] is True and hr['solver_and_test_fresh'] is False
artifacts={}
for name,pins in complete['binary_pins'].items():
    binary=base/'binaries'/(name+'.exe');manifest=binary.with_suffix('.manifest.json')
    assert ar.sha256(binary)==pins['binary_sha256']==read(manifest)['binary_sha256']
    assert ar.sha256(manifest)==pins['manifest_sha256']
    for p in (binary,manifest):artifacts[str(p)]=ar.sha256(p)
linked={}
for name in ['E015-holdout','E020-holdout','E015-resource']:
    binary=holdout/'build/binaries'/(name+'.exe');manifest=binary.with_suffix('.manifest.json');m=read(manifest)
    assert ar.sha256(binary)==m['binary_sha256']
    assert m['prepared_manifest_sha256']=='3e55bec74defdbc3a5e87d299c08722bccfbfc9d388c2908f8e7f5273cafac91'
    data=binary.read_bytes()
    counts={role:data.count((holdout/(role+'-kernels.cu')).read_bytes()) for role in ['E015','E020']}
    if name=='E015-resource':assert all(n>0 for n in counts.values())
    else:
        role=name.split('-')[0];other='E020' if role=='E015' else 'E015'
        assert counts[role]>0 and counts[other]==0
    assert counts==m['embedded_cuda_occurrences']
    linked[name]=counts
    for p in (binary,manifest):artifacts[str(p)]=ar.sha256(p)
assert ar.sha256(holdout/'build/binaries/E015-holdout.exe')!=ar.sha256(holdout/'build/binaries/E020-holdout.exe')
for folder in [base/'runs/E020-qualification-build'/n for n in ['cargo-1','cargo-2']]+[holdout/'build'/n for n in ['E015','E020']]:
    assert read(folder/'exit.json')['returncode']==0
    for name in ['invocation.json','exit.json','stdout.log','stderr.log']:
        p=folder/name;artifacts[str(p)]=ar.sha256(p)
for p in [complete_path,holdout/'build/report.json',holdout/'build/started.json',holdout/'build/target-isolation.json',
          holdout/'build-authorization.json',here/'authorization.json',
          base/'comparisons/E020-holdout-r2-source-review/manifest.json',
          base/'comparisons/E020-build-readiness-review/broader-build-validation.json',
          base/'comparisons/E020-build-readiness-review/primary-and-broader-embedded-cuda.json',
          base/'comparisons/E020-build-readiness-review/readiness-r1-invalid.json']:
    artifacts[str(p)]=ar.sha256(p)
result={'at':ar.now(),'candidate':'E020','all_required_builds_terminal':True,'all_builds_terminal':True,
 'holdout_builds_terminal':True,'holdout_build_source_review_pass':True,'broader_build_complete':record(complete_path),
 'holdout_build_report':record(holdout/'build/report.json'),'artifacts':artifacts,'embedded_cuda_occurrences':linked,
 'root_terminal_observations':{'broader_exec_session':8151,'broader_exit_code':0,'holdout_r2_exec_session':81268,'holdout_exit_code':0},
 'invalid_prior_readiness':record(base/'runs/E020-qualification-plan/all-builds-ready.json'),
 'scope':'New R3 readiness after observed successful terminal R2 builds and direct linked-source checks. R1 is preserved and invalid. No native outcome, acceptance or deployment implied.'}
with (here/'all-builds-ready.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(ar.sha256(here/'all-builds-ready.json'))
