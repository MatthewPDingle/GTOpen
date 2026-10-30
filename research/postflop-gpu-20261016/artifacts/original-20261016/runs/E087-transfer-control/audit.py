import sys,json,struct,mmap,itertools,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
P=old.read(H/'protocol.json');O=H/'output';M=old.read(O/'metadata.json')
assert M['id']=='E087-transfer-control' and M['performance_measurement'] is False and M['candidate_accepted'] is False
assert len(M['manual'])==96 and len(M['engines'])==8 and len(M['constructors'])==8
checks=0;words=0;fields=0;frames=0;pairs=0;rawbytes=0
def exact_files(a,b):
 global checks,rawbytes,pairs
 assert a.stat().st_size==b.stat().st_size
 with a.open('rb')as x,b.open('rb')as y:
  while True:
   u=x.read(4*1024*1024);v=y.read(4*1024*1024);assert u==v;checks+=1
   if not u:break
 rawbytes+=a.stat().st_size+b.stat().st_size;pairs+=1
def parse(p):
 global words,fields,frames,checks
 names=[]
 with p.open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as b:
  magic=b[:16];assert magic in [b'E087-FRAME-v1\0\0\0',b'E087-STATE-v1\0\0\0'];pos=16
  while pos<len(b):
   kind,n=struct.unpack_from('<II',b,pos);pos+=8
   name=b[pos:pos+n].decode();pos+=n
   count=struct.unpack_from('<Q',b,pos)[0];pos+=8
   assert name not in names;names.append(name);assert kind in [0,1,2]
   words+=count;fields+=1
   if kind==0:assert struct.unpack_from('<I',b,pos)[0]==0;pos+=4;checks+=count
   elif kind==1:
    length=count*4;assert pos+2*length<=len(b)
    for start in range(0,length,4*1024*1024):
     stop=min(start+4*1024*1024,length)
     assert b[pos+start:pos+stop]==b[pos+length+start:pos+length+stop]
    pos+=2*length;checks+=count
   else:assert magic==b'E087-STATE-v1\0\0\0';pos+=count*4;checks+=1
  assert pos==len(b);frames+=1
 if magic==b'E087-FRAME-v1\0\0\0':assert len(names)in [1,66]
 else:assert names[:4]==['iteration','isomorphism','predictions_present','locks']
 return names
actual_pairs=[]
for p in sorted(O.glob('baseline-*')):
 assert p.is_file()
 c=O/p.name.replace('baseline-','candidate-',1)
 actual_pairs.append([p.name,c.name]);exact_files(p,c)
 if p.suffix=='.bin':
  left=parse(p);right=parse(c);assert left==right
  if '-large-'in p.name or '.constructor.'in p.name:assert len(left)==66
assert actual_pairs==M['full_file_pairs']
for arm in ['baseline','candidate']:
 rows=[x for x in M['manual']if x['arm']==arm];assert [x['case']for x in rows]==list(range(48))
 for x,(storage,full,profile,prechecked,p)in zip(rows,itertools.product(['Compressed','F32'],[False,True],range(3),[False,True],range(2))):
  r=x['result'];assert x['storage']==storage and x['profile']==profile
  assert r['p']==p and r['force_full']==full and r['prechecked']==prechecked
  assert r['performance_measurement']is False and r['GPU_compute_kernel_launches']==0
  assert r['full_metadata_cleanup_exact']is True
  assert r['capacity_words']>=257 and r['capacity_words']<=r['device_words']
  if arm=='baseline':assert r['capacity_words']==r['device_words']
  else:assert r['capacity_words']<r['device_words']
  if full:assert r['compact']is False
  for phase,w in zip(r['phases'],range(2)):
   assert phase['which']==w and phase['device_words']==r['device_words']
   for k in ['whole_GPU_before_after_exact','whole_CPU_source_upload_unchanged','repeat_CPU_output_exact','warm_reupload_device_exact']:assert phase[k]is True
 b=[x for x in M['engines']if x['arm']=='baseline'];c=[x for x in M['engines']if x['arm']=='candidate']
 for x,y in zip(b,c):
  for k in ['case','storage','warm','exploit_bits','budget_error','full_resync_exact']:assert x[k]==y[k]
  assert 'budget'in x['budget_error'] and x['full_resync_exact']is True
  for k in ['wrapper_bytes','layout_bytes','device_arena_words']:assert x['info'][k]==y['info'][k]
constructors=[]
for x,y in zip([x for x in M['constructors']if x['arm']=='baseline'],[x for x in M['constructors']if x['arm']=='candidate']):
 assert (x['case'],x['fixture'],x['storage'])==(y['case'],y['fixture'],y['storage'])
 for k in ['wrapper_bytes','layout_bytes','device_arena_words']:assert x['info'][k]==y['info'][k]
 assert x['proof']==y['proof'] and x['proof']['fields']==66 and x['proof']['metadata_fields']==57
 assert y['info']['pinned_request_bytes']==min(x['info']['pinned_request_bytes'],67108864)
 constructors.append({'fixture':x['fixture'],'baseline_pinned_request_bytes':x['info']['pinned_request_bytes'],'candidate_pinned_request_bytes':y['info']['pinned_request_bytes']})
d=M['drain']
for k in ['queued_valid_DMA_before_reported_error_drained','original_reported_copy_error_priority_exact','post_ready_CPU_unwind_caught','staging_reuse_after_drain_exact']:assert d[k]is True
assert d['actual_words']==16384 and not d['real_hardware_failure_injected']and not d['atomic_rollback_claim']
old.custody()
report={'id':'E087-transfer-control','at':old.now(),'status':'pass_raw_GPU_controls','protocol_sha256':old.sha(H/'protocol.json'),'binary_sha256':old.sha(H/'probe.exe'),'manual_layouts':96,'manual_arena_phases':192,'small_trained_engine_cases':8,'large_constructor_cases':8,'GPU_training_iterations':24,'exploitability_checks':8,'full_file_pairs_exact':pairs,'frames':frames,'fields':fields,'represented_full_words':words,'reader_checks':checks,'raw_pair_bytes':rawbytes,'pinned_requests':constructors,'copy_drain_and_post_ready_unwind_controls':d,'all_complete_files_compared_in_full':True,'production_source_activated':False,'performance_measurement':False,'candidate_accepted':False,'scope':'Raw functional transfers, whole CPU and GPU images, actual complete constructors with bounded allocation request, small trained query/save/load/resume. Allocation request size is not measured memory footprint or speed. No real hardware/allocator failure or atomic rollback claim.'}
D=R/'comparisons/E087-transfer-control';D.mkdir(exist_ok=False);old.save(D/'report.json',report)
print(json.dumps({k:report[k]for k in ['status','full_file_pairs_exact','represented_full_words','reader_checks','pinned_requests']}),flush=True)
