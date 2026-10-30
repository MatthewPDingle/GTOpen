import sys,json,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status());RES=ROOT/'runs/E091-resource';q=h.read(RES/'report.json');assert q['status']=='pass_compiled_prerequisites'and all(q['gates'].values());H=ROOT/'runs/E091-raw-control';H.mkdir(exist_ok=False)
for v in['baseline','candidate']:p=RES/'execution'/(v+'-compute_120.ptx');h.pin(p,q['ptx_sha256'][v+'-compute_120']);shutil.copyfile(p,H/(v+'.ptx'))
shutil.copyfile(ROOT/'runs/E091-raw-probe.rs',H/'probe.rs');cases=[]
def case(nh,na,block,actor,lock_mode,regret_mode,reach_mode,count=1):cases.append(dict(nh=nh,na=na,block=block,actor=actor,lock_mode=lock_mode,regret_mode=regret_mode,reach_mode=reach_mode,count=count))
nas=[1,2,3,4,5,8,9,16,17]
for na in nas:
 for actor in[0,1]:
  for rm in range(7):
   for pm in range(5):case(257,na,128,actor,0,rm,pm)
for na in nas:
 for nh in[0,1,31,32,33,63,64,65,127,128,129,513,1024,1326]:
  for actor in[0,1]:case(nh,na,128,actor,0,0,0)
for na in nas:
 for actor in[0,1]:
  for lm in[1,2,3]:
   for rm in[0,4]:
    for pm in range(5):case(129,na,128,actor,lm,rm,pm)
for na in[2,9,17]:
 for block in[1,32,64,256]:
  for nh in[7,129,513]:
   for actor in[0,1]:case(nh,na,block,actor,0,0,3)
for na in nas:
 for actor in[0,1]:
  for lm in[0,1]:case(129,na,128,actor,lm,0,0,0)
assert len(cases)==1530;h.save(H/'corpus.json',cases)
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,stem in[('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',name+'='+str(deps/stem)]
cmd+=['-o',str(H/'probe.exe')]
files=[Path(__file__),ROOT/'runs/E091-raw-execute.py',ROOT/'runs/E091-raw-audit.py',ROOT/'runs/E091-raw-probe.rs',H/'probe.rs',H/'corpus.json',H/'baseline.ptx',H/'candidate.ptx',RES/'report.json',RES/'protocol.json',RES/'execution/complete.json',ROOT/'runs/E091-source/manifest.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json']+[p for p in deps.iterdir()if p.is_file()]
for p in[ROOT/'runs/E091-raw-execute.py',ROOT/'runs/E091-raw-audit.py',Path(__file__)]:compile(p.read_text(encoding='utf-8'),str(p),'exec')
P={'id':'E091-raw-control','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_KERNELS','measurement_epoch':'RAM20261028','rustc_command':cmd,'GPU_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','cases':len(cases),'kernel_launches':2*len(cases),'raw_reservation_bytes':8*1024**3,'required_free_bytes':74*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'scope':'One compiler and one finite raw CUDA process using sealed resource PTX, then independent full-array reader. Both actor orientations/asymmetric widths, zero and boundary hands, common/generic action menus, valid1/32/64/128/256-thread shapes, locks, signed zeros, overflow/nonfinite sums/inputs and count0. All actual twelve immutable input vectors, full physical output vectors and guards retained for both arms. No solver/performance measurement. Any actual numerical failure closes this source form; no source/corpus/sample rescue.'}
h.save(H/'protocol.json',P);pub=[]
for folder,prefix in[(RES,'E091-resource'),(H,'E091-raw-control')]:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in['.json','.rs','.cu','.log','.ptx']:continue
  key=prefix+'/'+p.relative_to(folder).as_posix();dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
h.save(H/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'protocol_sha256':h.sha(H/'protocol.json'),'raw_controls_not_started':True})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E091');x.update(stage='1530 raw GPU comparison cases',reason='Compiled prerequisites pass: registers40/40, local32/32 bytes, shared unchanged, occupancy12/12 at128 threads. Compare3060 launches and all input/output/guard words next. No production correctness or speed result.');x.setdefault('evidence',[]).extend([{'label':'Compiled resource results','url':'evidence/E091-resource/report.json'},{'label':'Frozen raw comparison','url':'evidence/E091-raw-control/protocol.json'}]);s.update(updated_at=h.now(),stage='E091 raw GPU controls',activity='Resource prerequisites passed. Test1530 fixed input cases with all physical input/output words retained. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
