import array,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;O=ROOT/'runs/D262-chance-ownership';h.pin(O/'protocol.json',sys.argv[1]);P=h.read(O/'protocol.json');h.custody();h.ar.refuse_active(h.ar.live_status());fields=[x[0]for x in h.read(P['schema_path'])['fields']]
for p,d in P['input_sha256'].items():h.pin(p,d)
def vec(raw,code):
 n,=struct.unpack_from('<Q',raw);v=array.array(code);v.frombytes(raw[8:]);assert len(v)==n
 if sys.byteorder!='little':v.byteswap()
 return v
def read_plan(path):
 out={}
 with path.open('rb')as f:
  assert f.read(17)==b'D183_PLAN_RAW1\0\0\0'
  for name in fields:
   n,=struct.unpack('<I',f.read(4));assert f.read(n).decode()==name;size,=struct.unpack('<Q',f.read(8))
   if name in P['selected_fields']:out[name]=f.read(size);assert len(out[name])==size
   else:f.seek(size,1)
  assert not f.read(1)
 return out
rows=[];checks=0
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 for item in P['raw_inputs']:
  path=Path(item['path']);h.pin(path,item['sha256']);assert path.stat().st_size==item['bytes'];raw=read_plan(path);levels,=struct.unpack('<Q',raw['num_levels']);nn,=struct.unpack('<Q',raw['num_nodes']);stride,=struct.unpack('<Q',raw['nh_max']);blocks,=struct.unpack('<Q',raw['cfv_blocks']);nh=list(vec(raw['nh'],'Q'));assert len(nh)==2 and max(nh)==stride<=1326
  d={k:vec(raw[k],'I')for k in['chance_nodes','cc_start','cc_count','cc_card','cc_child','cc_perm','cfv_slot']};assert len(d['cfv_slot'])==len(d['cc_start'])==len(d['cc_count'])==nn;assert len(d['cc_card'])==len(d['cc_child'])==len(d['cc_perm']);hp=[];at=8;assert struct.unpack_from('<Q',raw['hand_perm_flat'])[0]==2
  for p in range(2):
   n,=struct.unpack_from('<Q',raw['hand_perm_flat'],at);size=8+4*n;v=vec(raw['hand_perm_flat'][at:at+size],'I');at+=size;assert nh[p]>0 and len(v)%nh[p]==0 and len(v)>=nh[p]and all(i<nh[p]for i in v);assert list(v[:nh[p]])==list(range(nh[p]));hp.append(len(v)//nh[p]);checks+=len(v)+3
  assert at==len(raw['hand_perm_flat']);spanraw=raw['chance_node_spans'];count,=struct.unpack_from('<Q',spanraw);assert count==levels and len(spanraw)==8+count*8;spans=list(struct.Struct('<II').iter_unpack(spanraw[8:]));levelrows=[];seen=[]
  for level,(start,count)in enumerate(spans):
   nodes=d['chance_nodes'][start:start+count];assert len(nodes)==count and len(set(nodes))==count;seen.extend(nodes);outputs=[d['cfv_slot'][n]for n in nodes];assert len(outputs)==len(set(outputs))and all(v<blocks for v in outputs);inputs=set();entries=0
   for node in nodes:
    begin=d['cc_start'][node];end=begin+d['cc_count'][node];assert begin<=end<=len(d['cc_card'])
    for t in range(begin,end):
     child=d['cc_child'][t];assert node<child<nn and d['cc_card'][t]<52 and all(d['cc_perm'][t]<x for x in hp);slot=d['cfv_slot'][child];assert slot<blocks;inputs.add(slot);entries+=1;checks+=5
   assert set(outputs).isdisjoint(inputs);checks+=len(outputs)+len(inputs)+4;levelrows.append({'level':level,'chance_nodes':count,'card_entries':entries,'unique_parent_output_rows':len(outputs),'unique_child_input_rows':len(inputs),'all_parents_children_disjoint':True,'all_rows_and_hand_permutation_indexes_bounded':True})
  assert len(seen)==len(set(seen))==len(d['chance_nodes']);rows.append({'id':item['fixture']['id'],'node_count':nn,'hands':nh,'CFV_stride':stride,'CFV_rows':blocks,'permutations_per_player':hp,'levels':levelrows,'raw_input_sha256':item['sha256']})
 assert len(rows)==6;h.custody()
h.save(O/'report.json',{'id':'D262','at':h.now(),'status':'pass_scoped_original_chance_CFV_ownership','protocol_sha256':sys.argv[1],'checks':checks,'cases':rows,'complete_original_plan_inputs_hash_verified':6,'all_original_chance_parent_outputs_unique_disjoint_from_child_reads':True,'unchanged_physical_hand_addresses_under_D260_bijection':True,'D183_phase_timings_used':False,'new_compiler_CUDA_context_kernel_solver_or_timing_samples':0,'candidate_accepted':False,'limits':'Complete selected arrays for six canonical iso on/off plans; same-agent structural proof only. Direct exceptional/tail/zero-hand cases and actual engine/canonical full state still required. No speed/capacity/no-tradeoff/adoption proof.'});print(json.dumps({'status':'pass_scoped_ownership','checks':checks,'cases':len(rows)}),flush=True)
