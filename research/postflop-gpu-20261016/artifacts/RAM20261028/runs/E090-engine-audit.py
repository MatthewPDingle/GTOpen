import sys,json,array,struct,itertools
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
P=h.read(H/'protocol.json')
for p,digest in P['input_sha256'].items():h.pin(p,digest)
O=H/'output';M=h.read(O/'metadata.json');assert M['case_count']==32 and not M['performance_measurement']
checks=0;words=0;frames=0;guardwords=0;logicalwords=0;rawbytes=0
def req(v,label):
 global checks
 assert v,label;checks+=1
def frame(p):
 global frames,words
 data=p.read_bytes();magic=data[:16];req(magic in [b'E090-GPU-RAW1\0\0\0',b'E090-FRAME-v1\0\0\0',b'E090-STATE-v1\0\0\0'],'frame magic')
 at=16;fields={}
 while at<len(data):
  kind,n=struct.unpack_from('<II',data,at);at+=8;name=data[at:at+n].decode();at+=n
  count=struct.unpack_from('<Q',data,at)[0];at+=8;req(name not in fields,'unique field')
  if kind==0:req(struct.unpack_from('<I',data,at)[0]==0,'full positivezero run');at+=4;values=array.array('I',[0])*count
  else:
   req(kind in [1,2],'field kind')
   values=array.array('I');values.frombytes(data[at:at+count*4]);at+=count*4;req(len(values)==count,'full field')
   if kind==1:
    actual=array.array('I');actual.frombytes(data[at:at+count*4]);at+=count*4;req(actual==values,'every expected actual word')
  fields[name]=values;words+=count
 req(at==len(data),'complete frame');frames+=1;return fields
expected=list(itertools.product(['Compressed','F32'],['Dcfr','CfrPlus'],[False,True],[False,True],[False,True]))
for row,(storage,algo,reverse,iso,warm)in zip(M['cases'],expected):
 ident=row['case'];req(ident==M['cases'].index(row),'case order')
 req((row['storage'],row['algorithm'],row['reverse_ranges'],row['isomorphism'],row['warm_CPU_start'])==(storage,algo,reverse,iso,warm),'fixed dimensions')
 req(row['raked']==warm and'budget'in row['budget_error'],'rake/budget')
 req(row['constructor']['fields']==66 and len(row['exploit_bits'])==4 and len(row['snapshots'])==9,'case inventory')
 for proof in row['snapshots']:
  stage=proof['stage'];bi,ci=proof['baseline'],proof['candidate']
  b=frame(O/f'baseline-{ident:02d}-{stage}.gpu.bin');c=frame(O/f'candidate-{ident:02d}-{stage}.gpu.bin')
  req(set(b)==set(c)and len(b)==14,'full GPU fields')
  for name in b:
   if name!='CFV_physical':req(b[name]==c[name],'whole mutable/immutable/logical image '+name)
  for arm,fields,info in [('baseline',b,bi),('candidate',c,ci)]:
   n=info['rows'];s=info['logical_hands'];w=info['original_width'];stride=info['actual_stride']
   req(stride==(w if arm=='baseline'else s),'actual observer stride')
   phys=fields['CFV_physical'];logical=fields['CFV_logical']
   req(len(phys)==info['physical_words']==n*w and len(logical)==info['logical_words']==n*s,'full row geometry')
   for r in range(n):req(phys[r*stride:r*stride+s]==logical[r*s:r*s+s],'every full logical row maps to physical image')
   logicalwords+=len(logical)
   if info['poisoned']:
    count=0
    for i,v in enumerate(phys):
     live=i//stride<n and i%stride<s
     if not live:req(v==0x4b123456,'every nonowned physical guard');count+=1
    req(count==info['full_physical_guard_words'],'complete guard inventory')
    req(all(v!=0x4b123456 for v in logical),'every logical word overwritten');guardwords+=count
  for name in ['wrapper_bytes','pinned_words','arena_words','reach_words','physical_words','graphs_present','eval_graph_present']:req(bi[name]==ci[name],'unchanged actual '+name)
pairs=0;constructorpairs=0
for p in sorted(O.glob('baseline-*')):
 if p.name.endswith('.gpu.bin'):continue
 other=O/p.name.replace('baseline-','candidate-',1);req(p.read_bytes()==other.read_bytes(),'whole CPU/query/save/constructor file')
 rawbytes+=p.stat().st_size+other.stat().st_size;pairs+=1
 if p.name.endswith('-constructor.bin'):
  req(len(frame(p))==len(frame(other))==66,'all66 constructor buffers');constructorpairs+=1
 elif p.name.endswith('.cpu.bin'):req(frame(p)==frame(other),'every CPU Store/scale/flag word')
req(constructorpairs==32,'constructor inventory')
req(M['GPU_snapshot_pairs']==288 and M['exploitability_pairs']==128 and M['standard_training_iterations']==320 and M['extra_single_player_sweeps']==128,'whole fixed native inventory')
h.custody();D=ROOT/'comparisons/E090-engine-control';D.mkdir(exist_ok=False)
report={'id':'E090-engine-control','at':h.now(),'status':'pass_scoped_engine_raw_equivalence','protocol_sha256':h.sha(H/'protocol.json'),'binary_sha256':h.sha(H/'probe.exe'),'cases':32,'GPU_snapshot_pairs':288,'constructor_pairs':constructorpairs,'exploitability_pairs':128,'standard_training_iterations':320,'extra_single_player_sweeps':128,'CPU_query_save_constructor_file_pairs':pairs,'raw_frames':frames,'represented_frame_words':words,'logical_CFV_words_checked':logicalwords,'physical_guard_words_checked':guardwords,'reader_checks':checks,'whole_nonGPU_pair_bytes':rawbytes,'all_learning_reach_discount_weight_lock_logical_CFV_images_exact':True,'full_physical_CFV_images_retained_and_all_poisoned_nonowned_words_exact':True,'all_CPU_query_save_resume_images_exact':True,'all66constructor_images_match_CPU_reference':True,'physical_layouts_byte_identical_claimed':False,'source_main_live_PTX_custody_pass':True,'performance_measurement':False,'candidate_accepted':False,'scope':'Finite32case matrix; complete words and guards compared, no hash-only substitute. Physical CFV layouts differ with every complete image retained and logical rows explicitly mapped. No large-workload raw state, actual paging, physical peak/capacity or whole-solve speed qualification.'}
h.save(D/'report.json',report);print(json.dumps({k:report[k]for k in ['status','cases','GPU_snapshot_pairs','logical_CFV_words_checked','physical_guard_words_checked','reader_checks']}),flush=True)
