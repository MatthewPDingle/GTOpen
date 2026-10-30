import sys,ast,shutil,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
S=R/'runs/E087-source';D=R/'runs/E087-transfer-control';Q=R/'comparisons/E087-transfer-control'
assert old.read(Q/'report.json')['status']=='pass_raw_GPU_controls'
for label in ['rustc','probe','audit']:
 x=old.read(D/'execution'/(label+'.exit.json'))
 assert x['returncode']==0 and x['error']is x['cleanup']is None
H=R/'runs/E087-build-plan';H.mkdir(exist_ok=False)
code=(R/'runs/E086-build-plan/build.py').read_text(encoding='utf-8').replace('E086','E087').replace('one-file','three-host-file')
ast.parse(code);(H/'build.py').write_bytes(code.encode())
P=old.read(R/'runs/E086-build-plan/build-protocol.json');source=old.read(S/'manifest.json')
owned={}
for n,v in source['owned'].items():
 old.pin(v['base'],old.BASE[n]);old.pin(v['candidate'],source['candidate_owned_sha256'][n])
 owned[n]={'base':v['base'],'base_sha256':old.BASE[n],'candidate':v['candidate'],'candidate_sha256':source['candidate_owned_sha256'][n]}
P.update(id='E087-final-build',at=old.now(),owned=owned,accepted_source_sha256=old.BASE,CUDA_source_unchanged=True,
 direct_pairs=808,direct_launches=0,expected_ordinary_units=88,source_scope=source['scope']+' Exact production arena7CPUunits and808whole actual paired raw files/8smalltrainedengines/8largeconstructors passed; no performance or measured footprint claim.')
for phase in P['phases']:
 phase['target']=str(R/('build-e087-final-'+phase['id']))
 phase['outputs']={k:v.replace('E086','E087')for k,v in phase['outputs'].items()}
 assert not Path(phase['target']).exists()
files=[Path(__file__),H/'build.py',Q/'report.json',D/'protocol.json',D/'execution/complete.json',R/'runs/accepted-E080-live-20261018/common_e080_live.py',R/'runs/accepted-E080-live-20261018/protected-main.json',R/'runs/accepted-E080-live-20261018/preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
files += [p for folder in [S,D]for p in folder.rglob('*')if p.is_file()and p.suffix in ['.json','.rs','.py','.cu','.patch','.log']]
P['input_sha256']={str(p):old.sha(p)for p in files};old.save(H/'build-protocol.json',P)
pub=[]
for folder,prefix in [(D,'E087-transfer-control'),(Q,'E087-transfer-control-comparison'),(H,'E087-build-plan')]:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
  key=prefix+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
old.save(H/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'raw_bulk_on_S_only':True,'protocol_sha256':old.sha(H/'build-protocol.json')})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E087')
 x.update(stage='Fresh integrated solver builds',correctness='raw_transfer_controls_pass',reason='All808whole raw CPU/GPU/query/save file pairs,192manual arena phases,8smalltrainedengines and8largeconstructors pass. Speed and actual material gates remain.')
 x['evidence'] += [{'label':'Whole GPU transfer evidence','url':'evidence/E087-transfer-control-comparison/report.json'},{'label':'Frozen full builds','url':'evidence/E087-build-plan/build-protocol.json'}]
 s.update(updated_at=old.now(),stage='E087 full builds before complete-solve timing',activity='Raw transfer and compatibility controls passed. Two fresh builds next, including paging-feature compilation. E080 remains live; no new measured speedup yet.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'build-protocol.json'),flush=True)
