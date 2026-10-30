"""Verify resource result, extend the fixed corpus for the changed NA1 path, freeze control."""
import copy,hashlib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
RESOURCE=ROOT/'runs/E047-resource';P=old.read(RESOURCE/'protocol.json');R=old.read(RESOURCE/'report.json');checks=0
def req(v,m):
 global checks
 assert v,m;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
req(R['status']=='pass_resource_feasibility_only' and all(R['gates'].values()),'all frozen resource gates')
raw=(RESOURCE/'execution/probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E047_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E047_RESOURCE ' in x]
req(markers==R['raw_markers'] and len(markers)==4,'raw markers exact')
b,c=markers[1:3];req({k:v for k,v in b.items() if k!='variant'}=={k:v for k,v in c.items() if k!='variant'},'all queried resource metadata unchanged')
for label in ['rustc','probe']:
 e=old.read(RESOURCE/'execution'/(label+'.exit.json'));req(e['returncode']==0 and e['error'] is None and e['cleanup'] is None,'terminal child')
def entries(path):
 t=path.read_text(encoding='utf-8');result={};i=0
 while True:
  i=t.find('.visible .entry ',i)
  if i<0:return result
  par=t.index('(',i);name=t[i+len('.visible .entry '):par].strip();opening=t.index('{',par);end=opening+1;depth=1
  while depth:depth+=(t[end]=='{')-(t[end]=='}');end+=1
  req(name not in result,'unique entry');result[name]=t[i:end];i=end
be,ce=[entries(RESOURCE/'execution'/(v+'.ptx')) for v in ['baseline','candidate']]
req(set(be)==set(ce)==set(P['expected_entries']),'entry inventory')
for n in be:req((be[n]==ce[n])==(n!='up_action'),'only training action changed')
req(be['up_action'].split('{',1)[0]==ce['up_action'].split('{',1)[0],'exact ABI including qualifiers')
OUT=ROOT/'comparisons/E047-resource-root-check';OUT.mkdir()
resource_check={'id':'E047-resource-root-check','at':old.now(),'status':'pass_resource_feasibility_only','checks':checks,'root_cross_check_only':True,'resource_report_sha256':old.sha(RESOURCE/'report.json'),'same_resources':{'registers':66,'local_bytes_per_thread':64,'max_threads':896,'occupancy':[[64,14],[128,7],[256,3]]},'same_abi_other8_exact':True,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Root input/receipt/resource/rawPTX verification, not an external independent review or numerical/speed proof.'}
old.save(OUT/'report.json',resource_check)
HERE=ROOT/'runs/E047-kernel-control';HERE.mkdir();prior=ROOT/'runs/E042-kernel-control'
for v in ['baseline','candidate']:(HERE/(v+'.ptx')).write_bytes((RESOURCE/'execution'/(v+'.ptx')).read_bytes())
(HERE/'discounts.rs').write_bytes((prior/'discounts.rs').read_bytes())
source=(prior/'probe.rs').read_text(encoding='utf-8').replace('E042','E047').replace('for na in [2,8,9,17]','for na in [1,2,8,9,17]').replace('for na in [2,9,17]','for na in [1,2,9,17]').replace('for na in [2,3,4,8,9,17]','for na in [1,2,3,4,8,9,17]').replace('cases.len(),717','cases.len(),819')
assert 'cases.len(),819' in source;(HERE/'probe.rs').write_text(source,encoding='utf-8')
for n in ['execute.py','audit.py','child-helper.py']:
 s=(prior/n).read_text(encoding='utf-8').replace('E042','E047').replace('718','820').replace('717','819').replace('1434','1638');(HERE/n).write_text(s,encoding='utf-8')
oldc=old.read(prior/'corpus.json');oldcases=oldc['cases'];by={tuple(c[k] for k in ['hands','actions','threads','p','role','algorithm','iteration','value_mode','count']):c for c in oldcases};cases=[]
def add(nh,na,block,p,role,algo,t,mode,count):
 key=(nh,na,block,p,role,algo,t,mode,count)
 ref=by.get(key) or by[(nh,2 if na==1 else na,block,p,role,algo,t,mode,count)]
 row=copy.deepcopy(ref);row.update(id=len(cases),actions=na);row['descriptor'][1]=na;cases.append(row)
for na in [1,2,3,4,5,8,9,16,17]:
 for role in range(3):
  for p in range(2):
   for algo in range(2):
    for nh,t in [(1,1),(129,20),(257,200)]:add(nh,na,128,p,role,algo,t,0,1)
for na in [1,2,8,9,17]:
 for role in range(3):
  for nh in [0,31,32,33,63,64,65,127,128,255,256,511,512,513,1023,1024,1326]:add(nh,na,128,1,role,0,200,0,1)
for na in [1,2,9,17]:
 for role in range(3):
  for block in [1,32,64,256]:
   for nh in [7,129,513]:add(nh,na,block,0,role,1,20,0,1)
for na in [1,2,3,4,8,9,17]:
 for role in range(3):
  for mode in range(1,5):add(257,na,128,1,role,mode%2,200,mode,1)
for na in [1,2,9,17]:
 for role in range(3):add(129,na,128,0,role,0,20,0,0)
req(len(cases)==819 and sum(c['actions']==1 for c in cases)==138,'fixed prospective corpus size')
corpus={k:(v.replace('E042','E047').replace('717','819') if isinstance(v,str) else v) for k,v in oldc.items() if k!='cases'};corpus.update(id='E047-up-action-corpus',at=old.now(),case_count=819,kernel_launches=1638,cases=cases,changed_path_cases=138)
old.save(HERE/'corpus.json',corpus)
old.save(HERE/'source-review.json',{'id':'E047-direct-control-source-review','at':old.now(),'status':'pass_to_one_fixed_raw_control','root_review_only':True,'resource_root_check_sha256':old.sha(OUT/'report.json'),'changed_source':'Only existing entry dispatch adds unchanged template<1>. No body arithmetic/host/plan/launch/ABI change.','corpus_review':'819 cases/1638 launches;138 NA1 cases. Prospectively extends previous fixed corpus to include NA1 in all tail/thread/signedzero/nonfinite/overflow/subnormal/count0 subsets before execution. Both actor orientations in main matrix, all3 roles and both algorithms.','raw_evidence':'Five full raw files: declared inputs, both complete output states and both actual device immutable-input images. No fingerprints substitute for raw equality.','source_reference':'Exact passed-resource original/candidate PTX loaded as separate modules; accepted CPU Discounts formula copied exactly.','limits':'No spans above2^32; finite declared corpus. No solver speed or universal payload semantics claim.'})
p=old.read(prior/'protocol.json');p.update(id='E047-kernel-control',at=old.now(),resource_report=str(RESOURCE/'report.json'),raw_output=str(HERE/'evidence'),expected_cases=819,expected_launches=1638)
p['rustc_command']=[x.replace('E042-kernel-control','E047-kernel-control') for x in p['rustc_command']]
deps={n:h for n,h in p['input_sha256'].items() if '/build/' in n.replace('\\','/')};refs=[HERE/n for n in ['probe.rs','discounts.rs','baseline.ptx','candidate.ptx','corpus.json','source-review.json','execute.py','child-helper.py','audit.py']]+[RESOURCE/'report.json',OUT/'report.json',ROOT/'runs/E047-design/manifest.json',ar.REPO/'crates/solver/src/cfr.rs',ar.REPO/'tools/postflop_autoresearch.py']
p['input_sha256']=deps|{str(x):old.sha(x) for x in refs};old.save(HERE/'protocol.json',p)
published={}
for directory in [RESOURCE,OUT,HERE]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==raw
  else:dst.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(src)
old.save(HERE/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'kernel_launches':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='E047');e.update(stage='Resource gate passed; fixed819-case raw GPU control next',reason='Registers66/local64 and occupancy unchanged; same ABI, other8 entries exact.819-case control includes138 changed-path cases. No speed measured.');e['evidence'].extend([{'label':'E047 resource/root verification','url':'evidence/E047-resource-root-check/report.json'},{'label':'E047 fixed direct GPU corpus','url':'evidence/E047-kernel-control/corpus.json'}]);s.update(state='running',stage='E047 raw numerical controls',activity='Compile one fixed819case originalGPU comparator before solver build/timing.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'resource_root_sha256':old.sha(OUT/'report.json'),'control_protocol_sha256':old.sha(HERE/'protocol.json'),'cases':819,'changed_path_cases':138}),flush=True)
