import sys,shutil,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
qpath=ROOT/'comparisons/E090-engine-control/report.json';q=h.read(qpath)
assert q['status']=='pass_scoped_engine_raw_equivalence'and q['GPU_snapshot_pairs']==288 and q['cases']==32
assert h.read(ROOT/'runs/E090-engine-control/execution/complete.json')['all_owned_children_terminal']
H=ROOT/'runs/E090-build-plan';H.mkdir(exist_ok=False);base=h.custody();n='crates/solver/src/gpu/mod.rs'
owned={n:{'base':str(ROOT/'reference/E090-source/baseline.rs'),'base_sha256':base[n],'candidate':str(ROOT/'reference/E090-source/candidate.rs'),'candidate_sha256':'92893002e72295c10ac8a899199a8046620daca37017aa4a75a80e988dd9339a'}}
for v in owned.values():h.pin(v['base'],v['base_sha256']);h.pin(v['candidate'],v['candidate_sha256'])
phases=[{'id':'feature','features':'preflop-research','expected_features':['gpu','preflop-research'],'integration':False,'outputs':{'solver':'E090-feature-solver'}},{'id':'primary','features':'gpu','expected_features':['gpu'],'integration':True,'outputs':{'solver':'E090-solver','postflop_autoresearch':'E090-postflop_autoresearch'}}]
for phase in phases:phase['target']=str(ROOT/('build-e090-final-'+phase['id']));assert not Path(phase['target']).exists()
files=[Path(__file__),ROOT/'runs/E090-build.py',qpath,ROOT/'runs/E090-engine-control/protocol.json',ROOT/'runs/E090-engine-control/execution/complete.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',ROOT/'reference/localization.json',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
files +=[p for p in(ROOT/'reference/E090-source').iterdir()if p.is_file()]
P={'id':'E090-final-build','at':h.now(),'status':'FROZEN_PRE_COMPILER','measurement_epoch':'RAM20261028','accepted_source_sha256':base,'candidate_owned_sha256':{n:owned[n]['candidate_sha256']},'owned':owned,'phases':phases,'required_free_bytes':74*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'scope':'Exactly two per-player CFV-stride substitutions. CUDA/plan/arena unchanged. Fresh feature and primary builds on X, restore accepted source after each. No native execution or performance acceptance in this protocol.'}
h.save(H/'protocol.json',P)
pub=[]
for folder,prefix in[(ROOT/'runs/E090-engine-control','E090-engine-control'),(qpath.parent,'E090-engine-control-result'),(H,H.name)]:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in['.json','.rs','.py','.log']:continue
  key=prefix+'/'+p.relative_to(folder).as_posix();dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
h.save(H/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'protocol_sha256':h.sha(H/'protocol.json'),'bulk_raw_physical_X_only':True})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E090');x.update(stage='Fresh isolated builds',correctness='scoped_raw_controls_pass',reason='All32fixed engine cases and288GPU state pairs passed, including all logical scratch, learning/reach images, guards, locks, query/save/resume. Build two fresh feature configurations next; no speed result or adoption.')
 x.setdefault('evidence',[]).extend([{'label':'Raw GPU engine controls','url':'evidence/E090-engine-control-result/report.json'},{'label':'Frozen fresh builds','url':'evidence/E090-build-plan/protocol.json'}])
 s.update(updated_at=h.now(),active_experiment='E090',stage='E090 fresh builds',activity='Raw engine equivalence passed. Build isolated binaries before ordinary tests and six fixed speed measurements. Current RAM E080 baseline 10.4564s; E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
