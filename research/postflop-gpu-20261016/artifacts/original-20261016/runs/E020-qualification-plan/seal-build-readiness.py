import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
base=ar.RESEARCH
here=Path(__file__).resolve().parent
holdout=base/'runs/E020-wide-turn-holdout-implementation'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def record(p):return {'path':str(p),'sha256':ar.sha256(p)}
assert not (base/'gpu-run.lock').exists()
complete_path=base/'runs/E020-qualification-build/complete.json'
complete=read(complete_path)
assert complete['status']=='pass' and len(complete['binary_pins'])==7
assert complete['source_sha256']==ar.source_identity()['source_sha256']
assert read(holdout/'build/report.json')['status']=='pass'
artifacts={}
for name,pins in complete['binary_pins'].items():
    binary=base/'binaries'/(name+'.exe');manifest=binary.with_suffix('.manifest.json')
    assert ar.sha256(binary)==pins['binary_sha256']==read(manifest)['binary_sha256']
    assert ar.sha256(manifest)==pins['manifest_sha256']
    for p in (binary,manifest):artifacts[str(p)]=ar.sha256(p)
for name in ['E015-holdout','E020-holdout','E015-resource']:
    binary=holdout/'build/binaries'/(name+'.exe');manifest=binary.with_suffix('.manifest.json')
    assert ar.sha256(binary)==read(manifest)['binary_sha256']
    assert read(manifest)['prepared_manifest_sha256']=='cac3399c20ce42c85fd0f2074f41cbb93d790ebe345673808857f46892f43340'
    for p in (binary,manifest):artifacts[str(p)]=ar.sha256(p)
for group in ['cargo-1','cargo-2']:
    folder=base/'runs/E020-qualification-build'/group
    assert read(folder/'exit.json')['returncode']==0
    for name in ['invocation.json','exit.json','stdout.log','stderr.log']:
        p=folder/name;artifacts[str(p)]=ar.sha256(p)
for group in ['E015','E020']:
    folder=holdout/'build'/group
    assert read(folder/'exit.json')['returncode']==0
    for name in ['invocation.json','exit.json','stdout.log','stderr.log']:
        p=folder/name;artifacts[str(p)]=ar.sha256(p)
for p in [complete_path,holdout/'build/report.json',holdout/'build/started.json',holdout/'build-authorization.json',
          here/'authorization.json',base/'comparisons/E020-holdout-source-review/manifest.json',
          base/'comparisons/E020-build-readiness-review/broader-build-validation.json']:
    artifacts[str(p)]=ar.sha256(p)
result={'at':ar.now(),'candidate':'E020','all_required_builds_terminal':True,'all_builds_terminal':True,
 'holdout_builds_terminal':True,'holdout_build_source_review_pass':True,'broader_build_complete':record(complete_path),
 'holdout_build_report':record(holdout/'build/report.json'),'artifacts':artifacts,
 'root_terminal_observations':{'broader_exec_session':8151,'broader_exit_code':0,'holdout_exec_session':89038,'holdout_exit_code':0},
 'scope':'All ten executables frozen after observed successful terminal build processes. No additional GPU execution or acceptance implied.'}
with (here/'all-builds-ready.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(ar.sha256(here/'all-builds-ready.json'))
