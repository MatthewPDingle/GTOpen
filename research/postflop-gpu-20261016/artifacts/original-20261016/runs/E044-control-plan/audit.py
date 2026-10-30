"""Root full-payload decoder/cross-check for E044 discount staging controls."""
import json,math,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
P=old.read(HERE/'protocol.json');C=old.read(old.ROOT/'runs/E044-control-execution/complete.json');ROOT=Path(P['output_dir']);S=old.read(ROOT/'evidence.json')
assert C['unit_passed']==84 and C['gpu_cases']==14
OUT=old.ROOT/'comparisons/E044-discount-control';assert not OUT.exists();OUT.mkdir();checks=0
def req(v,m):
 global checks
 assert v,m;checks+=1
def host(raw):
 req(raw[:9]==b'E044HOST1','host magic');at=9;it,=struct.unpack_from('<Q',raw,at);at+=8;iso=raw[at];at+=1;stores=[]
 for _ in range(4):
  k,n=struct.unpack_from('<IQ',raw,at);at+=12;req(k in [0,1,2],'store kind');width=4 if k==0 else 2
  data=raw[at:at+width*n];at+=width*n;req(len(data)==width*n,'full raw store');scale=b''
  if k:
   ns,=struct.unpack_from('<Q',raw,at);at+=8;scale=raw[at:at+4*ns];at+=4*ns;req(len(scale)==4*ns,'full raw scales')
  stores.append((k,n,data,scale))
 req(at==len(raw),'host endpoint');return it,iso,stores
def gpu(raw,iteration,algo):
 req(raw[:8]==b'E044GPU1','GPU magic');it,=struct.unpack_from('<Q',raw,8);req(it==iteration,'GPU iteration')
 nh=struct.unpack_from('<III',raw,16);req(nh[0]>0 and nh[1]>0 and nh[2]>=max(nh[:2]),'GPU hand geometry');at=28;arrays=[]
 for _ in range(9):
  n,=struct.unpack_from('<Q',raw,at);at+=8;data=raw[at:at+4*n];at+=4*n;req(len(data)==4*n,'full GPU array');arrays.append((n,data))
 req(at==len(raw),'GPU endpoint');req(arrays[-1][0]==3,'discount device geometry')
 bits=lambda x:struct.unpack('<I',struct.pack('<f',x))[0]
 if iteration==0:expected=[0,0,0]
 else:
  t=float(iteration);ta=math.pow(t,1.5);expected=[bits(ta/(ta+1)) if algo=='Dcfr' else bits(1.0),bits(.5) if algo=='Dcfr' else 0,bits((t/(t+1))**2)]
 req(list(struct.unpack('<III',arrays[-1][1]))==expected,'last applied production discount bits')
 return nh,arrays
req([c['name'] for c in S['cases']]==P['cases'],'case inventory');inventory={};details=[];eligible=0
gpu_epochs={'initial':0,'batch0':1,'batch1':3,'batch2':6,'batch3':11,'batch4':19,'profiled':20,'evaluation':20,'locked':22,'continued':24}
host_epochs={'input':0,'first':20,'materialized':20,'strategy':22,'locked_full':22,'continued':24}
for case in S['cases']:
 name=case['name'];r=case['result'];d=ROOT/name;files={x['file']:x['bytes'] for x in r['files']}
 req(len(files)==45 and set(p.name for p in d.iterdir())==set(files),'actual raw file inventory');pairs=0;gpu_shapes=[]
 for n,size in files.items():
  p=d/n;raw=p.read_bytes();req(len(raw)==size,'raw file size');inventory[str(p)]=old.sha(p)
  if '.reference.' in n:
   req(raw==(d/n.replace('.reference.','.candidate.')).read_bytes(),'full reference/candidate bytes '+n);pairs+=1
  if '.gpu.' in n:
   label=n.split('.gpu.',1)[0];nh,a=gpu(raw,gpu_epochs[label],r['algorithm']);gpu_shapes.append((nh,[x[0] for x in a]))
  if n.endswith('.host.bin') or '.host.' in n:
   it,iso,stores=host(raw);label=n.split('.host',1)[0]
   req(it==host_epochs[label] and bool(iso)==r['iso'],'CPU iteration/isomorphism')
   req([s[0] for s in stores]==([1,1,2,2] if r['storage']=='Compressed' else [0,0,0,0]),'CPU storage variants')
 req(pairs==22,'pair count');req(len(gpu_shapes)==20 and all(x==gpu_shapes[0] for x in gpu_shapes),'all GPU buffer lengths/hand geometry stable')
 req(r['pinned_pipeline_eligible']==(r['staging_words']>=6)==(not r['tiny']),'actual pipeline/fallback geometry');eligible+=int(r['pinned_pipeline_eligible'])
 first=host((d/'first.host.candidate.bin').read_bytes());strategy=host((d/'strategy.host.candidate.bin').read_bytes());full=host((d/'locked_full.host.candidate.bin').read_bytes())
 req(strategy[2][:2]==first[2][:2],'strategy-only preserves complete previous raw regrets')
 req(strategy[2][2:]==full[2][2:],'strategy-only strategies equal full readback')
 details.append({'name':name,'raw_files':45,'raw_pairs':pairs,'pinned_pipeline_eligible':r['pinned_pipeline_eligible'],'storage':r['storage'],'algorithm':r['algorithm'],'compact':r['compact'],'staging_words':r['staging_words'],'bytes':sum(files.values())})
req(eligible==10 and len(details)-eligible==4,'pipeline and tiny fallback coverage')
req([d['mode'] for d in S['drop_controls']]==[0,1,2],'drop-mode inventory')
for d in S['drop_controls']:req(d['drain_calls']==1 and d['stream_ready_before_field_release'] and d['cleanup_complete'],'first-field drop drain trace')
req(S['candidate_solver_size']<=S['original_solver_size']+32,'bounded host object size');req(math.isfinite(float(S['discount_stage_size'])),'host control size')
old.custody()
report={'id':'E044-discount-control','at':old.now(),'status':'pass_scoped_discount_gpu_lifecycle','root_cross_check_only':True,'checks':checks,'cases':details,'gpu_cases':14,'raw_files':630,'raw_pairs':308,'eligible_cases':10,'tiny_fallback_cases':4,'drop_modes':3,'original_solver_size':S['original_solver_size'],'candidate_solver_size':S['candidate_solver_size'],'discount_stage_size':S['discount_stage_size'],'ordinary_tests_passed':84,'protocol_sha256':old.sha(HERE/'protocol.json'),'native_complete_sha256':old.sha(old.ROOT/'runs/E044-control-execution/complete.json'),'raw_summary_sha256':old.sha(ROOT/'evidence.json'),'raw_file_sha256':inventory,'accepted162_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Finite small fixtures and declared sequences/error/drop paths. Reference methods are the accepted originals; GPU code unchanged. Root decoder is not an external independent audit. No speed, idle-time, stop-latency or full-process performance claim.'}
old.save(OUT/'report.json',report);print(json.dumps({k:report[k] for k in ['status','checks','raw_files','raw_pairs','original_solver_size','candidate_solver_size']}));print(old.sha(OUT/'report.json'))
