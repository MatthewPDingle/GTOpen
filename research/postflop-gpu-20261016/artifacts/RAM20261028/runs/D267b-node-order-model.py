import array,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
spec=importlib.util.spec_from_file_location('modelio',ROOT/'runs/D267b-model-io.py');io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
assert len(sys.argv)==2;H=ROOT/'runs/D267b-node-order-model';h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json');fields=[x[0]for x in h.read(P['schema_path'])['fields']];h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
out=H/'output';out.mkdir(exist_ok=False);gpu={}
for item in P['GPU_metadata_inputs']:
 h.pin(item['path'],item['sha256']);gpu[item['fixture']]=io.gpu_metadata(item['path'])
kinds=[('action_nodes','action_spans'),('chance_nodes','chance_node_spans'),('fold_nodes','fold_spans'),('show_nodes','show_spans')];nodefields=['node_player','node_na','node_data_off','node_children_start','node_twin','node_tlose','node_ttie','node_cdiv','node_river_slot','cc_start','cc_count','cfv_slot'];valuefields=[x[0]for x in kinds]+['chance_parents','chance_children','cc_child'];rows=[];checks=0
for item in P['raw_inputs']:
 h.pin(item['path'],item['sha256']);raw=io.plans(item['path'],fields);nn,=struct.unpack('<Q',raw['num_nodes']);levels,=struct.unpack('<Q',raw['num_levels']);fwd=array.array('I',[0xffffffff])*nn;inv=array.array('I');lists={n:io.vec(raw[n],'I')for n,_ in kinds};span={n:io.spans(raw[s])for n,s in kinds};assert all(len(v)==levels for v in span.values())
 for level in range(levels):
  for name,_ in kinds:
   a,n=span[name][level]
   for old in lists[name][a:a+n]:assert old<nn and fwd[old]==0xffffffff;fwd[old]=len(inv);inv.append(old)
 visited=len(inv)
 for old in range(nn):
  if fwd[old]==0xffffffff:fwd[old]=len(inv);inv.append(old)
 assert len(inv)==nn and fwd[0]==inv[0]==0;assert all(inv[fwd[i]]==i for i in range(nn));checks+=2*nn
 original={name:io.vec(raw[name],'Q'if name=='node_data_off'else'I')for name in nodefields};reach=io.nested(raw['reach_slot']);original.update({'reach_slot[0]':reach[0],'reach_slot[1]':reach[1]});assert len(original)==14 and all(len(v)==nn for v in original.values());parent_names=set(original);g=gpu[item['fixture']['fixture']];assert len(g['d_lock_off'])==nn;original['d_lock_off']=g['d_lock_off'];original['synthetic_lock_offsets']=array.array('Q',(i*16 if i%3==0 else 0xffffffffffffffff for i in range(nn)));parent_names|={'d_lock_off','synthetic_lock_offsets'}
 for name in valuefields:original[name]=io.vec(raw[name],'I')
 original['tree.children']=g['d_children'];proposal={}
 for name,v in original.items():
  if name in parent_names:new=array.array(v.typecode,(v[old]for old in inv));back=array.array(v.typecode,(new[fwd[old]]for old in range(nn)))
  else:
   assert all(x==0xffffffff or x<nn for x in v);new=array.array('I',(x if x==0xffffffff else fwd[x]for x in v));back=array.array('I',(x if x==0xffffffff else inv[x]for x in new))
  assert back==v;checks+=len(v);proposal[name]=new
 # All active action children retain their physical CFV rows after node-ID remapping.
 for node in lists['action_nodes']:
  first=original['node_children_start'][node];na=original['node_na'][node];assert first+na<=len(original['tree.children'])
  for child in original['tree.children'][first:first+na]:assert child!=0xffffffff and proposal['cfv_slot'][fwd[child]]==original['cfv_slot'][child];checks+=1
 footprints=[]
 for level in range(levels):
  for name,_ in kinds:
   a,n=span[name][level];old=lists[name][a:a+n];new=proposal[name][a:a+n]
   if n:assert list(new)==list(range(new[0],new[0]+n))
   assert array.array('I',(inv[x]for x in new))==old
   footprints.append({'level':level,'worklist':name,'nodes':n,'ordered_CPU_node_IDs_preserved':True,'hypothetical_relative_32B_groups':{str(width):{'old':len({(x*width)//32 for x in old}),'new':len({(x*width)//32 for x in new})}for width in[4,8]}})
 ident=item['fixture']['id'];path=out/(ident+'.projection.bin');mp=out/(ident+'.maps.bin');io.write_projection(path,proposal);io.write_projection(mp,{'old_to_new':fwd,'new_to_old':inv});rows.append({'id':ident,'fixture':item['fixture']['fixture'],'nodes':nn,'visited_nodes':visited,'inactive_tail_nodes':nn-visited,'changed_node_IDs':sum(i!=x for i,x in enumerate(fwd)),'projected_arrays':len(proposal),'node_indexed_arrays_including_actual_and_synthetic_locks':len(parent_names),'exact_inverse_words':sum(len(v)*(v.itemsize//4)for v in original.values()),'original_projected_payload_bytes':sum(len(v)*v.itemsize for v in original.values()),'proposal_projected_payload_bytes':sum(len(v)*v.itemsize for v in proposal.values()),'projection':{'path':str(path),'bytes':path.stat().st_size,'sha256':h.sha(path)},'maps':{'path':str(mp),'bytes':mp.stat().st_size,'sha256':h.sha(mp)},'source_plan_sha256':item['sha256'],'footprints':footprints});assert rows[-1]['original_projected_payload_bytes']==rows[-1]['proposal_projected_payload_bytes'];print('CPU node-order model complete:',ident,flush=True)
h.save(H/'model-report.json',{'id':'D267-model','at':h.now(),'status':'pass_reversible_CPU_metadata_projection_only','protocol_sha256':sys.argv[1],'checks':checks,'cases':rows,'raw_bytes':sum(x.stat().st_size for x in out.iterdir()),'candidate_created_or_activated':False,'CUDA_or_kernel_or_solver_runs':0,'performance_samples':0,'limits':P['footprint_rule']+' Source-derived projection, not candidate GPU output, material neutrality or speed proof.'});h.custody();print(json.dumps({'cases':len(rows),'checks':checks,'raw_bytes':sum(x.stat().st_size for x in out.iterdir())}),flush=True)
