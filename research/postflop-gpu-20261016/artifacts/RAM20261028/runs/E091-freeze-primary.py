import sys,json,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
build=ROOT/'runs/E091-final-build/complete.json';done=h.read(build);assert done['all_compilers_terminal']and done['native_executions']==0
for p,digest in done['evidence_sha256'].items():h.pin(p,digest)
for phase in['feature','primary']:
 for p,digest in h.read(ROOT/'runs/E091-final-build'/phase/'complete.json')['artifact_sha256'].items():h.pin(p,digest)
H=ROOT/'runs/E091-primary-plan';H.mkdir(exist_ok=False);bp=ROOT/'runs/E091-build-plan/protocol.json';b=h.read(bp)
sequence=[{'id':'V091-unit','binary':'E091-solver','unit':True}]+[{'id':i,'binary':'E080-postflop_autoresearch'if i.startswith('B')else'E091-postflop_autoresearch','unit':False}for i in['B296','E091R1','E091R2','B297','B298','E091R3']]
state=h.read(h.ar.STATUS)
for rec in sequence:assert not(ROOT/'runs'/rec['id']).exists()and not any(x['id']==rec['id']for x in state['experiments'])
files=[Path(__file__),ROOT/'runs/E091-primary-native.py',ROOT/'runs/E091-primary-assess.py',ROOT/'runs/E091-primary-root-check.py',ROOT/'epoch/runner.py',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',build,bp,ROOT/'comparisons/E091-raw-control/report.json',ROOT/'runs/E091-raw-control/execution/complete.json',ROOT/'comparisons/RAM20261028-baseline/report.json',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for stem in['E091-feature-solver','E091-solver','E091-postflop_autoresearch','E080-postflop_autoresearch']:
 exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=h.read(mp);h.pin(exe,m['binary_sha256']);assert m['source_sha256']==b['accepted_source_sha256']|(b['candidate_owned_sha256']if stem.startswith('E091')else{});files +=[exe,mp]
files += [ROOT/'runs/E091-primary-adapter.json',ROOT/'comparisons/D144-incidence/report.json',ROOT/'runs/E091-resource/report.json',ROOT/'runs/E091-resource/protocol.json']
P={'id':'E091-primary','at':h.now(),'status':'FROZEN_PRE_ORDINARY_UNITS_AND_PRIMARY_TIMING','measurement_epoch':'RAM20261028','build_protocol_sha256':h.sha(bp),'accepted_source_sha256':b['accepted_source_sha256'],'candidate_owned_sha256':b['candidate_owned_sha256'],'sequence':sequence,'pairs':[{'baseline':'B296','candidate':'E091R1'},{'baseline':'B297','candidate':'E091R2'},{'baseline':'B298','candidate':'E091R3'}],'required_ordinary_units':86,'required_aggregate_gain_pct':1.,'fixture_guard':'Reject positive median slowdown with at least2/3 slower pairs, even below3%.','excluded_samples_allowed':False,'extension_runs_allowed':False,'historical_or_RAM_baseline_timing_pooling_allowed':False,'required_free_bytes':66*1024**3,'adoption_requirements':['Separately frozen fresh16 pairs: unrounded aggregate >=1%, >=13 improving pairs, positive paired/block/order medians, no repeatable fixture slowdown.','Broader exact state/F32/menu/save/resume/continuation, actual graph/launch/memory/capacity and material CPU setup-cost checks.','Fixed holdout and fresh-original cumulative qualification. Initial screen alone does not establish significance, universal behavior or adoption.'],'scope':'Same three registered complete cycles, compressed/Rayon16/fresh native processes/warm driver cache on current RAM. Includes tree/CPUallocation,all GPUinit/NVRTC/JIT,samequality solve/checks/fullreadback. Cargo and fingerprints excluded. No current-RAM causal claim. No candidate source/width/threshold variant after failure. All outputs physically X.','input_sha256':{str(p):h.sha(p)for p in files},'candidate_accepted':False}
h.save(H/'protocol.json',P)
pub=[]
for folder,prefix in[(ROOT/'runs/E091-final-build','E091-final-build'),(H,H.name)]:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in['.json','.log','.rs']:continue
  key=prefix+'/'+p.relative_to(folder).as_posix();dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
h.save(H/'publication.json',{'at':h.now(),'protocol_sha256':h.sha(H/'protocol.json'),'HTTP_verified_artifacts':pub,'primary_or_ordinary_native_executions':0})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E091');x.update(stage='Ordinary units and three complete-solve pairs',reason='Fresh feature and primary builds finished and accepted source restored. Run86 ordinary units then B296/E091R1,E091R2/B297,B298/E091R3. Exactness,unrounded1% and strict fixture guards; no exclusions/extensions/pooling or adoption from screen.');x.setdefault('evidence',[]).append({'label':'Frozen speed comparison','url':'evidence/E091-primary-plan/protocol.json'})
 s.update(updated_at=h.now(),stage='E091 complete-solve comparison',activity='Run86 ordinary units, then six fixed complete-solve measurements under current RAM. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
