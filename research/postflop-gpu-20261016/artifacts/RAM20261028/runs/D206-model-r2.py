import json,struct,sys,shutil,urllib.request
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D206-resident-phase-model';h.pin(H/'protocol-r2.json',sys.argv[1]);P=h.read(H/'protocol-r2.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
fields=[x[0] for x in h.read(P['schema_path'])['fields']];checks=0
def req(v,label):
 global checks
 assert v,label;checks+=1
def vector(raw,dtype):
 n,=struct.unpack_from('<Q',raw);v=np.frombuffer(raw,dtype=dtype,offset=8);req(len(v)==n,'whole typed vector');return v
def spanvec(raw):
 n,=struct.unpack_from('<Q',raw);req(len(raw)==8+n*8,'whole LevelSpan vector count and two u32 fields');return np.frombuffer(raw,dtype='<u4',offset=8).reshape((n,2))
def pairvec(raw,dtype):
 count,=struct.unpack_from('<Q',raw);req(count==2,'two player array');at=8;result=[]
 for _ in range(2):
  n,=struct.unpack_from('<Q',raw,at);size=8+n*np.dtype(dtype).itemsize;result.append(vector(raw[at:at+size],dtype));at+=size
 req(at==len(raw),'whole nested array');return result
def plan(path):
 selected={}
 with path.open('rb') as f:
  req(f.read(17)==b'D183_PLAN_RAW1\0\0\0','original plan magic')
  for expected in fields:
   length,=struct.unpack('<I',f.read(4));name=f.read(length).decode();req(name==expected,'all original field order');size,=struct.unpack('<Q',f.read(8))
   if name in P['selected_fields']:raw=f.read(size);req(len(raw)==size,'whole selected field');selected[name]=raw
   else:f.seek(size,1)
  req(f.read(1)==b'','whole plan EOF')
 return selected
def gpu_children(item):
 path=Path(item['path']);req(path.stat().st_size==item['bytes'],'GPU source file extent');h.pin(path,item['sha256']);out={}
 with path.open('rb') as f:
  req(f.read(16)==b'D166-GPU-RAW1\0\0\0','actual GPU frame magic')
  for expected in ['iteration','algorithm','hands']+P['device_inventory']:
   kind,length=struct.unpack('<II',f.read(8));name=f.read(length).decode();n,=struct.unpack('<Q',f.read(8));req(name==expected and kind in [0,2],'complete original GPU field order/encoding')
   if kind==0:
    req(f.read(4)==b'\0'*4,'lossless zero representation');raw=b'\0'*(n*4) if name in P['GPU_selected_fields'] else None
   elif name in P['GPU_selected_fields']:raw=f.read(n*4);req(len(raw)==n*4,'whole selected actual GPU field')
   else:f.seek(n*4,1);raw=None
   if raw is not None:out[name]=np.frombuffer(raw,dtype='<u4')
  req(f.tell()==item['bytes'] and f.read(1)==b'','whole GPU frame EOF')
 return out
def unique(values,label):
 req(len(np.unique(values))==len(values),label)
def disjoint(a,b,label):
 req(len(np.intersect1d(a,b,assume_unique=False))==0,label)
def bounds(values,limit,label):
 req(len(values)==0 or int(np.max(values))<limit,label)
def descendants(nodes,na,start,children):
 # Preserve each original node's ordered child span, including arbitrary arity.
 arrays=[]
 for node in nodes:
  count=int(na[node]);begin=int(start[node]);req(count>0 and begin+count<=len(children),'action ordered child span in actual allocation');arrays.append(children[begin:begin+count])
 return np.concatenate(arrays) if arrays else np.array([],dtype='<u4')
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.custody();h.ar.refuse_active(h.ar.live_status());req(shutil.disk_usage(ROOT).free>=P['required_free_bytes'],'X free admission')
 actual={}
 for item in P['children_inputs']:
  print('Hash/read original child geometry',item['fixture'],flush=True);actual[item['fixture']]=gpu_children(item)
 results=[]
 for item in P['raw_inputs']:
  print('Model original plan',item['fixture']['id'],flush=True);path=Path(item['path']);req(path.stat().st_size==item['bytes'],'plan input extent');h.pin(path,item['sha256']);raw=plan(path)
  levels,=struct.unpack('<Q',raw['num_levels']);nn,=struct.unpack('<Q',raw['num_nodes']);cfv_blocks,=struct.unpack('<Q',raw['cfv_blocks']);nh=vector(raw['nh'],'<u8');reach_blocks=vector(raw['reach_blocks'],'<u8');arenas=vector(raw['arena_elements'],'<u8')
  U={name:vector(raw[name],'<u4') for name in ['action_nodes','chance_parents','chance_children','chance_nodes','fold_nodes','show_nodes','cc_start','cc_count','cc_child','node_children_start','cfv_slot']}
  na=vector(raw['node_na'],'<i4');players=vector(raw['node_player'],'<i4');offsets=vector(raw['node_data_off'],'<u8');slots=pairvec(raw['reach_slot'],'<u4');children=actual[item['fixture']['fixture']]['d_children']
  req(np.array_equal(na.view('<u4'),actual[item['fixture']['fixture']]['d_node_na']) and np.array_equal(U['node_children_start'],actual[item['fixture']['fixture']]['d_node_children_start']),'entire tree child-span signature matches actual solver GPU geometry')
  spans={name:spanvec(raw[name]) for name in ['action_spans','chance_spans','chance_node_spans','fold_spans','show_spans']}
  req(all(len(x)==levels for x in spans.values()),'all original levels represented')
  node_level=np.full(nn,0xffffffff,dtype='<u4');by={};all_nodes=[]
  for role,list_name,span_name in [('action','action_nodes','action_spans'),('chance','chance_nodes','chance_node_spans'),('fold','fold_nodes','fold_spans'),('show','show_nodes','show_spans')]:
   by[role]=[];last=0
   for l,(start,count) in enumerate(spans[span_name]):
    start,count=int(start),int(count);req(start==last and start+count<=len(U[list_name]),'exact contiguous original level span');nodes=U[list_name][start:start+count];bounds(nodes,nn,'node ID bound');unique(nodes,'node IDs unique per phase');req(bool(np.all(node_level[nodes]==0xffffffff)),'disjoint work item lists');node_level[nodes]=l;by[role].append(nodes);last=start+count
   req(last==len(U[list_name]),'whole work list covered');all_nodes.extend(U[list_name].tolist())
  bounds(U['cfv_slot'][np.array(all_nodes,dtype='<u4')],cfv_blocks,'all visited CFV rows in physical allocation')
  action_all=U['action_nodes'];bounds(players[action_all],2,'action actor IDs');req(bool(np.all(players[action_all]>=0)),'nonnegative actor IDs')
  learning=[]
  for p in range(2):
   nodes=action_all[players[action_all]==p];begins=offsets[nodes];sizes=na[nodes].astype(np.uint64)*nh[p];order=np.argsort(begins);lo=begins[order];hi=lo+sizes[order]
   req(bool(np.all(sizes>0)) and bool(np.all(hi>=lo)) and bool(np.all(hi<=arenas[p])),'all learning intervals in actual arena')
   req(len(lo)<2 or bool(np.all(lo[1:]>=hi[:-1])),'all persistent learning intervals mutually disjoint')
   learning.append({'player':p,'action_blocks':len(nodes),'arena_words':int(arenas[p]),'owned_words':int(np.sum(sizes)),'all_intervals_disjoint':True})
  level_rows=[];phase_rows=[];last_edge=0
  for l in range(levels):
   action,cnodes,fold,show=(by[x][l] for x in ['action','chance','fold','show'])
   cs=descendants(action,na,U['node_children_start'],children);bounds(cs,nn,'action child ID bounds');req(bool(np.all(node_level[cs]==l+1)),'all action children on immediately deeper phase')
   down=[]
   for p in range(2):
    nodes=action[players[action]==p];writes=descendants(nodes,na,U['node_children_start'],children);sources=slots[p][nodes];destinations=slots[p][writes]
    bounds(sources,int(reach_blocks[p]),'action input reach slots');bounds(destinations,int(reach_blocks[p]),'action output reach slots');unique(destinations,'every actor-side child output has unique owner');disjoint(sources,destinations,'action phase inputs/outputs disjoint')
    down.append({'player':p,'input_slots':len(np.unique(sources)),'output_slots':len(destinations),'all_output_owners_unique':True,'phase_read_write_disjoint':True})
   es,ec=map(int,spans['chance_spans'][l]);req(es==last_edge and es+ec<=len(U['chance_parents']),'whole ordered flat chance-edge span');ep=U['chance_parents'][es:es+ec];ed=U['chance_children'][es:es+ec];req(len(ep)==len(ed),'paired flat edge lists');bounds(ep,nn,'chance parent IDs');bounds(ed,nn,'chance child IDs');req(bool(np.all(node_level[ep]==l)) and bool(np.all(node_level[ed]==l+1)),'flat chance edges join original adjacent levels');last_edge=es+ec
   for p in range(2):
    sources=slots[p][ep];destinations=slots[p][ed];bounds(sources,int(reach_blocks[p]),'chance input reach slots');bounds(destinations,int(reach_blocks[p]),'chance output reach slots');unique(destinations,'chance child outputs unique');disjoint(sources,destinations,'chance edge phase reads/writes disjoint')
   up=[]
   for role,nodes in [('fold',fold),('show',show),('chance',cnodes),('action',action)]:
    outputs=U['cfv_slot'][nodes];bounds(outputs,cfv_blocks,'CFV output row bound');unique(outputs,'CFV output rows unique per original phase')
    if role=='action':inputs=U['cfv_slot'][cs]
    elif role=='chance':
     selected=[]
     for n in nodes:
      begin=int(U['cc_start'][n]);count=int(U['cc_count'][n]);req(begin+count<=len(U['cc_child']),'chance complete child-table bound');selected.append(U['cc_child'][begin:begin+count])
     child=np.concatenate(selected) if selected else np.array([],dtype='<u4');bounds(child,nn,'chance orbit representative child IDs');req(bool(np.all(node_level[child]==l+1)),'all orbit representatives on original child level');inputs=U['cfv_slot'][child]
    else:inputs=np.array([],dtype='<u4')
    bounds(inputs,cfv_blocks,'all original input CFV rows bound');disjoint(outputs,inputs,'entire original phase CFV input/output rows disjoint')
    up.append({'role':role,'work_items':len(nodes),'output_rows':len(outputs),'input_rows':len(inputs),'all_outputs_unique':True,'phase_input_output_disjoint':True})
   level_rows.append({'level':l,'down_action_owners':down,'down_chance_edges':ec,'up_phases':up})
  req(last_edge==len(U['chance_parents'])==len(U['chance_children']),'whole flat chance work list')
  for l in range(levels):
   for role,span_name in [('down_action','action_spans'),('down_chance','chance_spans')]:
    start,count=map(int,spans[span_name][l])
    if count:phase_rows.append([role,l,start,count])
  for l in reversed(range(levels)):
   for role,span_name in [('up_fold','fold_spans'),('up_show','show_spans'),('up_chance','chance_node_spans'),('up_action','action_spans')]:
    start,count=map(int,spans[span_name][l])
    if count:phase_rows.append([role,l,start,count])
  req(all(0<=start<2**31 and 0<count<2**31 for _,_,start,count in phase_rows),'original signed start/count domains')
  results.append({'id':item['fixture']['id'],'node_count':nn,'levels':levels,'hands':[int(x) for x in nh],'within_proposed64level_frame':levels<=64,'maximum_phase_work_items':max(x[3] for x in phase_rows),'learning_interval_ownership':learning,'levels_detail':level_rows,'unchanged_nonempty_phase_schedule':phase_rows,'input_sha256':item['sha256'],'structural_checks_pass':True})
  print('Model',item['fixture']['id'],'passed',len(phase_rows),'original phases',flush=True)
 h.custody()
D=ROOT/'comparisons/D206-resident-phase-model';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D206','at':h.now(),'status':'pass_scoped_full_original_phase_ownership_model','protocol_sha256':sys.argv[1],'checks':checks,'cases':results,'all6_original_plan_full_hashes_verified':True,'all3_original_actual_GPU_geometry_frame_hashes_verified':True,'D183_phase_timing_used':False,'new_native_compiler_CUDA_or_solver_samples':0,'optimizer_or_gain_accepted':False,'shared_scratch_lifetime_requirement':'Original helpers own fresh CTA shared/local lifetimes. Persistent wrapper must synchronize all128threads afterevery helper work item before reusing the CTA for another node, including up_fold/up_show dynamic/static shared arrays. Existing helperfirstbarrier alone is insufficient: nextnode writes can race priornode finalsharedreads. Allhelperreturns mustreturnonlyto wrapper, all128threadsreach after-item barrier; then allgridthreadsjoin phasegrid.sync.','scope':'Complete selected canonical iso on/off integer arrays and exact original GPU child geometry; preserves original per-phase input/output ownership, signed span domains and dependency order. Doesnotproveallotherplans/CUDAhelperprojection/FPmath/liveness/resources/barrierkernel/graph/quality/material/performance. Onefixedsource/resourceprototype still requires source projection and prospective costs; no speed/headroom from counts/timings.'})
print(json.dumps({'status':'pass_phase_ownership','checks':checks,'cases':len(results),'phase_counts':{x['id']:len(x['unchanged_nonempty_phase_schedule']) for x in results},'new_native_samples':0}),flush=True)
