import sys,ast,re,shutil,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018';sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
build=R/'runs/E087-final-build/complete.json';done=old.read(build)
assert done['all_compilers_terminal']and done['native_executions']==0
for p,h in done['evidence_sha256'].items():old.pin(p,h)
direct=R/'comparisons/E087-transfer-control/report.json';q=old.read(direct)
assert q['status']=='pass_raw_GPU_controls' and q['full_file_pairs_exact']==808 and q['all_complete_files_compared_in_full']
S=R/'runs/E087-source';source=old.read(S/'manifest.json')
H=R/'runs/E087-primary-plan';H.mkdir(exist_ok=False)
predicate="assert control['status']=='pass_raw_GPU_controls' and control['full_file_pairs_exact']==808 and control['all_complete_files_compared_in_full'] and control['small_trained_engine_cases']==8 and control['large_constructor_cases']==8"
for name in ['native.py','assess.py','root-check.py','run.py']:
 t=(R/'runs/E086-primary-plan'/name).read_text(encoding='utf-8').replace('E086','E087').replace('e086','e087')
 if name in ['native.py','assess.py']:
  t,n=re.subn(r"assert control\['status'\][^\n]+",predicate,t);assert n==1
 t=t.replace("[('86','0','4','0','0')]","[('88','0','4','0','0')]").replace("'ordinary_units_passed':86","'ordinary_units_passed':88").replace('exact one-source scope','exact three-host-file source scope')
 ast.parse(t);(H/name).write_bytes(t.encode())
P=old.read(R/'runs/E086-primary-plan/protocol.json')
base=C/'baseline.json';bexe=R/'binaries/E080-postflop_autoresearch.exe';bmp=bexe.with_suffix('.manifest.json');bm=old.read(bmp)
old.pin(bexe,bm['binary_sha256']);assert bm['source_sha256']==old.BASE
P.update(id='E087-primary',at=old.now(),baseline={'path':str(base),'sha256':old.sha(base)},baseline_binary={'path':str(bexe),'sha256':old.sha(bexe),'manifest':str(bmp),'manifest_sha256':old.sha(bmp)},candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E087-build-plan/build-protocol.json'),ordinary_unit_id='V087-unit',control_ids=['V087-unit'],pairs=[{'baseline':'B287','candidate':'E087R1'},{'baseline':'B288','candidate':'E087R2'},{'baseline':'B289','candidate':'E087R3'}],measurement_order=['B287','E087R1','E087R2','B288','B289','E087R3'],direct_control_report={'path':str(direct),'sha256':old.sha(direct)},source_scope=source['scope']+' Raw CPU/GPU/state compatibility controls pass. Complete clocks include tree/CPUallocation,all GPUinitialization/NVRTC/JIT,samequality solve/checks/fullreadback. No historical pooling/exclusions/extensions. Initial pass is not adoption; fresh16,broad/material/capacity/holdout/cumulative gates remain.')
files=[Path(__file__),build,direct,R/'runs/E087-transfer-control/protocol.json',R/'runs/E087-transfer-control/execution/complete.json',R/'runs/E087-build-plan/build-protocol.json',*[p for p in S.rglob('*')if p.is_file()],base,bexe,bmp,C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in ['native.py','assess.py','root-check.py','run.py']]]
for stem in ['E087-feature-solver','E087-solver','E087-postflop_autoresearch']:
 exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp)
 old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];files += [exe,mp]
s=old.read(old.ar.STATUS)
for ident in P['control_ids']+P['measurement_order']:
 assert not(R/'runs'/ident).exists()and not any(x['id']==ident for x in s['experiments'])
for ident in ['E087-native-execution','E087-primary-wrapper']:assert not(R/'runs'/ident).exists()
for ident in ['E087-three-pair-comparison','E087-root-crosscheck']:assert not(R/'comparisons'/ident).exists()
P['input_sha256']={str(p):old.sha(p)for p in files};old.save(H/'protocol.json',P)
pub=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_verified_artifacts':pub,'native_primary_or_ordinary_units':0,'all_compilers_terminal':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E087')
 x.update(stage='88 ordinary tests and three complete-solve pairs',reason='Fresh builds terminal; accepted E080 restored. Exactly B287/E087R1,E087R2/B288,B289/E087R3. Unchanged unrounded1%/strictfixture/exactquality gates; no added samples or adoption from initial screen.')
 x['evidence'].append({'label':'Frozen complete-solve screen','url':'evidence/E087-primary-plan/protocol.json'})
 s.update(updated_at=old.now(),stage='E087 complete-solve comparison',activity='Run88ordinary solver tests, then fixed same-quality complete-solve comparisons. E080 remains live; candidate code stays isolated.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
