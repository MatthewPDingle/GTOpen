"""Seal exactly three E086 complete-solve pairs after full builds finish."""
import ast
from pathlib import Path
import re
import shutil
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E086-final-build/complete.json';done=old.read(build)
assert done['all_compilers_terminal'] and done['native_executions']==0
for p,h in done['evidence_sha256'].items():old.pin(p,h)
x=old.read(R/'runs/E086-build-manager/build.exit.json')
assert x['returncode']==0 and x['error'] is x['cleanup'] is None
direct=R/'comparisons/E086-kernel-control/report.json';q=old.read(direct)
assert q['status']=='pass_scoped_chance_raw_equivalence'
assert q['full_raw_files_equal'] and q['actual_immutable_images_preserved']
assert q['kernel_launches']==850
S=R/'runs/E086-source';source=old.read(S/'manifest.json')
H=R/'runs/E086-primary-plan';H.mkdir(exist_ok=False)
predicate="assert control['status']=='pass_scoped_chance_raw_equivalence' and control['full_raw_files_equal'] and control['actual_immutable_images_preserved'] and control['kernel_launches']==850 and control['accepted162_main_live_ptx_unchanged']"
for name in ['native.py','assess.py','root-check.py','run.py']:
    t=(R/'runs/E084-primary-plan-r2'/name).read_text().replace('E084','E086').replace('e084','e086')
    if name in ['native.py','assess.py']:
        t,n=re.subn(r"assert control\['status'\][^\n]+",predicate,t)
        assert n==1
    ast.parse(t);(H/name).write_text(t,encoding='utf-8',newline='\n')
P=old.read(R/'runs/E084-primary-plan-r2/protocol.json')
base=C/'baseline.json';bexe=R/'binaries/E080-postflop_autoresearch.exe'
bmp=bexe.with_suffix('.manifest.json');bm=old.read(bmp)
old.pin(bexe,bm['binary_sha256']);assert bm['source_sha256']==old.BASE
P.update(id='E086-primary',at=old.now(),baseline={'path':str(base),'sha256':old.sha(base)},
    baseline_binary={'path':str(bexe),'sha256':old.sha(bexe),'manifest':str(bmp),'manifest_sha256':old.sha(bmp)},
    candidate_owned_sha256=source['candidate_owned_sha256'],
    build_protocol_sha256=old.sha(R/'runs/E086-build-plan/build-protocol.json'),
    ordinary_unit_id='V086-unit',control_ids=['V086-unit'],
    pairs=[{'baseline':'B284','candidate':'E086R1'},{'baseline':'B285','candidate':'E086R2'},{'baseline':'B286','candidate':'E086R3'}],
    measurement_order=['B284','E086R1','E086R2','B285','B286','E086R3'],
    direct_control_report={'path':str(direct),'sha256':old.sha(direct)},
    source_scope=source['scope']+' Resource and425raw chance pairs pass. Complete clocks include tree/CPU allocation,all GPU initialization/NVRTC/JIT,same quality solve/checks/full readback. No historical timing pooling, exclusions or extensions. Initial pass is not adoption; fresh16,broad/material/capacity/holdout/cumulative gates remain.')
paths=[Path(__file__),build,direct,R/'runs/E086-resource/protocol.json',R/'runs/E086-resource/report.json',
    R/'runs/E086-kernel-control/protocol.json',R/'runs/E086-kernel-control/execution/complete.json',
    R/'runs/E086-build-plan/build-protocol.json',*[p for p in S.iterdir()if p.is_file()],
    base,bexe,bmp,C/'common_e080_live.py',C/'protected-main.json',
    old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',
    *[H/n for n in ['native.py','assess.py','root-check.py','run.py']]]
for stem in ['E086-feature-solver','E086-solver','E086-postflop_autoresearch']:
    exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp)
    old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256']
    paths.extend([exe,mp])
s=old.read(old.ar.STATUS)
for ident in P['control_ids']+P['measurement_order']:
    assert not(R/'runs'/ident).exists()and not any(x['id']==ident for x in s['experiments'])
for ident in ['E086-native-execution','E086-primary-wrapper','E086-primary-manager']:
    assert not(R/'runs'/ident).exists()
for ident in ['E086-three-pair-comparison','E086-root-crosscheck']:
    assert not(R/'comparisons'/ident).exists()
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'protocol.json',P)
pub=[]
for p in H.iterdir():
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
    pub.append(key)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),
    'HTTP_verified_artifacts':pub,'native_primary_or_ordinary_units':0,'all_compilers_terminal':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E086')
    e.update(stage='86 ordinary tests and three complete-solve pairs',reason='Fresh builds terminal, accepted E080 restored. Exactly B284/E086R1,E086R2/B285,B286/E086R3. Unchanged unrounded1% cutoff, strict fixture guards and exact quality. No extra samples or adoption from initial screen.')
    e['evidence'].append({'label':'Frozen complete-solve screen','url':'evidence/E086-primary-plan/protocol.json'})
    s.update(updated_at=old.now(),stage='E086 complete-solve comparison',activity='Run ordinary solver tests, then fixed same-quality complete-solve comparisons. Candidate source remains isolated; accepted E080 is live.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
