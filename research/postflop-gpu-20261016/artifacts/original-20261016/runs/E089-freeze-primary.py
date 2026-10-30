import sys,ast,re,shutil,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018';sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
build=R/'runs/E089-final-build/complete.json';done=old.read(build)
assert done['all_compilers_terminal']and done['native_executions']==0
for p,h in done['evidence_sha256'].items():old.pin(p,h)
direct=R/'comparisons/E089-kernel-control-root-check/report.json';q=old.read(direct)
assert q['status']=='pass_scoped_full_serial_card_loop_raw_equivalence' and q['inventory']['comparison_pairs']==1820 and q['whole_physical_outputs_bitwise_equal'] and q['all21_input_buffers_identical']
S=R/'runs/E089-source';source=old.read(S/'manifest.json')
H=R/'runs/E089-primary-plan';H.mkdir(exist_ok=False)
predicate="assert control['status']=='pass_scoped_full_serial_card_loop_raw_equivalence' and control['inventory']['comparison_pairs']==1820 and control['whole_physical_outputs_bitwise_equal'] and control['all21_input_buffers_identical']"
for name in ['native.py','assess.py','root-check.py','run.py']:
 t=(R/'runs/E086-primary-plan'/name).read_text(encoding='utf-8').replace('E086','E089').replace('e086','e089')
 if name in ['native.py','assess.py']:
  t,n=re.subn(r"assert control\['status'\][^\n]+",predicate,t);assert n==1
 t=t.replace("[('86','0','4','0','0')]","[('86','0','4','0','0')]").replace("'ordinary_units_passed':86","'ordinary_units_passed':86").replace('exact one-source scope','exact one-CUDA-file source scope')
 ast.parse(t);(H/name).write_bytes(t.encode())
P=old.read(R/'runs/E086-primary-plan/protocol.json')
base=C/'baseline.json';bexe=R/'binaries/E080-postflop_autoresearch.exe';bmp=bexe.with_suffix('.manifest.json');bm=old.read(bmp)
old.pin(bexe,bm['binary_sha256']);assert bm['source_sha256']==old.BASE
P.update(id='E089-primary',at=old.now(),baseline={'path':str(base),'sha256':old.sha(base)},baseline_binary={'path':str(bexe),'sha256':old.sha(bexe),'manifest':str(bmp),'manifest_sha256':old.sha(bmp)},candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E089-build-plan/build-protocol.json'),ordinary_unit_id='V089-unit',control_ids=['V089-unit'],pairs=[{'baseline':'B290','candidate':'E089R1'},{'baseline':'B291','candidate':'E089R2'},{'baseline':'B292','candidate':'E089R3'}],measurement_order=['B290','E089R1','E089R2','B291','B292','E089R3'],direct_control_report={'path':str(direct),'sha256':old.sha(direct)},source_scope=source['scope']+' All1820fixed rawshowdownpairs and fullactualinputs/guards pass; broadstatecompatibility remains required. Complete clocks include tree/CPUallocation,all GPUinitialization/NVRTC/JIT,samequality solve/checks/fullreadback. No historical pooling/exclusions/extensions. Initial pass is not adoption; fresh16,broad/material/capacity/holdout/cumulative gates remain.')
files=[Path(__file__),build,direct,R/'runs/E089-kernel-control/protocol.json',R/'runs/E089-kernel-control/execution/complete.json',R/'runs/E089-build-plan/build-protocol.json',*[p for p in S.rglob('*')if p.is_file()],base,bexe,bmp,C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in ['native.py','assess.py','root-check.py','run.py']]]
for stem in ['E089-feature-solver','E089-solver','E089-postflop_autoresearch']:
 exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp)
 old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];files += [exe,mp]
s=old.read(old.ar.STATUS)
for ident in P['control_ids']+P['measurement_order']:
 assert not(R/'runs'/ident).exists()and not any(x['id']==ident for x in s['experiments'])
for ident in ['E089-native-execution','E089-primary-wrapper']:assert not(R/'runs'/ident).exists()
for ident in ['E089-three-pair-comparison','E089-root-crosscheck']:assert not(R/'comparisons'/ident).exists()
P['input_sha256']={str(p):old.sha(p)for p in files};old.save(H/'protocol.json',P)
pub=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_verified_artifacts':pub,'native_primary_or_ordinary_units':0,'all_compilers_terminal':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E089')
 x.update(stage='86 ordinary tests and three complete-solve pairs',reason='Fresh builds terminal; accepted E080 restored. Exactly B290/E089R1,E089R2/B291,B292/E089R3. Unchanged unrounded1%/strictfixture/exactquality gates; no added samples or adoption from initial screen.')
 x['evidence'].append({'label':'Frozen complete-solve screen','url':'evidence/E089-primary-plan/protocol.json'})
 s.update(updated_at=old.now(),stage='E089 complete-solve comparison',activity='Run86ordinary solver tests, then fixed same-quality complete-solve comparisons. E080 remains live; candidate code stays isolated.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
