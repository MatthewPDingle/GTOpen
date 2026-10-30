"""Freeze two fresh full builds after resource and raw numerical gates passed."""
import ast
from pathlib import Path
import shutil
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
D=R/'runs/E086-kernel-control';RES=R/'runs/E086-resource'
root=R/'comparisons/E086-kernel-control'
q=old.read(root/'report.json')
assert q['status']=='pass_scoped_chance_raw_equivalence'
assert q['full_raw_files_equal'] and q['actual_immutable_images_preserved']
assert q['cases']==425 and q['kernel_launches']==850
for name in ['direct','audit']:
    receipt=old.read(R/'runs/E086-direct-manager'/(name+'.exit.json'))
    assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
S=R/'runs/E086-source';source=old.read(S/'manifest.json')
H=R/'runs/E086-build-plan';H.mkdir(exist_ok=False)
code=(R/'runs/E084-build-plan/build.py').read_text().replace('E084','E086').replace('e084','e086')
code=code.replace("'terminal; accepted E051 restored.'","'terminal; accepted E080 restored.'")
ast.parse(code);(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
P=old.read(R/'runs/E084-build-plan/build-protocol.json')
owned={}
for name,v in source['owned'].items():
    old.pin(v['base'],old.BASE[name]);old.pin(v['candidate'],source['candidate_owned_sha256'][name])
    owned[name]={'base':v['base'],'base_sha256':old.BASE[name],
                 'candidate':v['candidate'],'candidate_sha256':source['candidate_owned_sha256'][name]}
P.update(id='E086-final-build',at=old.now(),owned=owned,accepted_source_sha256=old.BASE,
    protected_main=str(C/'protected-main.json'),native_before_builds_terminal=True,
    CUDA_source_unchanged=False,direct_pairs=425,direct_launches=850,
    source_scope=source['scope']+' Actual resources30registers,local0/static0/dynamic0,maxthreads1024,theoretical128thread residency12 unchanged. All425direct pairs and full actual inputs/guards passed. No speed/material qualification yet.')
for phase in P['phases']:
    phase['target']=str(R/('build-e086-final-'+phase['id']))
    phase['outputs']={k:v.replace('E084','E086')for k,v in phase['outputs'].items()}
    assert not Path(phase['target']).exists()
paths=[Path(__file__),H/'build.py',root/'report.json',D/'protocol.json',D/'execution/complete.json',
    RES/'protocol.json',RES/'report.json',C/'common_e080_live.py',C/'protected-main.json',
    C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',
    *[p for folder in [S,D,R/'runs/D137-bitfield-membership']for p in folder.iterdir()
      if p.is_file()and p.suffix in ['.json','.rs','.py','.cu','.ptx','.patch']]]
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'build-protocol.json',P)
pub=[]
for folder in [D,R/'runs/E086-direct-manager',root,H]:
    for p in folder.rglob('*'):
        if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
        key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
        pub.append(key)
old.save(H/'pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'build-protocol.json'),
    'HTTP_verified_artifacts':pub,'raw_files_on_S_only':q['raw_file_sha256'],'integrated_compilers_or_solves':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E086')
    e.update(stage='Fresh full solver builds',correctness='direct_controls_pass',reason='All425raw chance pairs and2508695reader checks passed. Fresh feature and primary builds next; speed remains unproven.')
    e['evidence'].extend([{'label':'Full raw GPU replay','url':'evidence/E086-kernel-control/report.json'},{'label':'Frozen integrated builds','url':'evidence/E086-build-plan/build-protocol.json'}])
    s.update(updated_at=old.now(),stage='Building E086 complete-solve trial',activity='Full chance outputs and actual inputs match exactly in425fixed pairs. Building the unchanged candidate for ordinary solver tests and a three-pair complete-solve comparison. E080 remains live.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'build-protocol.json'),flush=True)
