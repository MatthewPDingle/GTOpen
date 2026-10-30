"""Root inverse replay of all persisted model words; no GPU or timing."""
import array,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
spec=importlib.util.spec_from_file_location('modelio',ROOT/'runs/D267-model-io.py');io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
assert len(sys.argv)==2;H=ROOT/'runs/D267-node-order-model';h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json');Q=h.read(H/'model-report.json');fields=[x[0]for x in h.read(P['schema_path'])['fields']];h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
gpu={x['fixture']:io.gpu_metadata(x['path'])for x in P['GPU_metadata_inputs']};kinds=[('action_nodes','action_spans'),('chance_nodes','chance_node_spans'),('fold_nodes','fold_spans'),('show_nodes','show_spans')];nodefields=['node_player','node_na','node_data_off','node_children_start','node_twin','node_tlose','node_ttie','node_cdiv','node_river_slot','cc_start','cc_count','cfv_slot'];values=[x[0]for x in kinds]+['chance_parents','chance_children','cc_child'];checks=words=0;rows=[];negative=[]
for item,row in zip(P['raw_inputs'],Q['cases']):
 assert item['fixture']['id']==row['id'];h.pin(item['path'],item['sha256']);raw=io.plans(item['path'],fields);nn,=struct.unpack('<Q',raw['num_nodes']);levels,=struct.unpack('<Q',raw['num_levels'])
 for key in ['projection','maps']:h.pin(row[key]['path'],row[key]['sha256']);assert Path(row[key]['path']).stat().st_size==row[key]['bytes']
 maps=io.read_projection(row['maps']['path']);assert set(maps)=={'old_to_new','new_to_old'};forward,reverse=maps['old_to_new'],maps['new_to_old'];assert len(forward)==len(reverse)==nn
 # Rebuild the ordering independently by complete frontier concatenation.
 expected=[]
 for level in range(levels):
  for n,s in kinds:
   a,count=io.spans(raw[s])[level];expected.extend(io.vec(raw[n],'I')[a:a+count])
 visited=set(expected);assert len(visited)==len(expected)==row['visited_nodes'];expected.extend(i for i in range(nn)if i not in visited);assert array.array('I',expected)==reverse and len(set(reverse))==nn;assert all(forward[old]==new for new,old in enumerate(reverse));assert forward[0]==reverse[0]==0;checks+=3*nn
 source={n:io.vec(raw[n],'Q'if n=='node_data_off'else'I')for n in nodefields};reach=io.nested(raw['reach_slot']);source['reach_slot[0]'],source['reach_slot[1]']=reach;source['d_lock_off']=gpu[row['fixture']]['d_lock_off'];source['synthetic_lock_offsets']=array.array('Q',(i*16 if i%3==0 else 0xffffffffffffffff for i in range(nn)));pernode=set(source)
 for n in values:source[n]=io.vec(raw[n],'I')
 source['tree.children']=gpu[row['fixture']]['d_children'];proposal=io.read_projection(row['projection']['path']);assert set(source)==set(proposal)and len(proposal)==24
 for name,original in source.items():
  actual=proposal[name];assert actual.typecode==original.typecode and len(actual)==len(original)
  restored=array.array(actual.typecode,(actual[forward[i]]for i in range(nn)))if name in pernode else array.array('I',(v if v==0xffffffff else reverse[v]for v in actual));assert restored.tobytes()==original.tobytes(),name;checks+=len(original);words+=len(original)*(original.itemsize//4)
 footprint=[]
 for old in row['footprints']:
  name=old['worklist'];start,count=io.spans(raw[dict(kinds)[name]])[old['level']];a=source[name][start:start+count];b=proposal[name][start:start+count];assert array.array('I',(reverse[v]for v in b))==a
  counts={str(w):{'old':len({(v*w)>>5 for v in a}),'new':len({(v*w)>>5 for v in b})}for w in[4,8]};assert old['hypothetical_relative_32B_groups']==counts;footprint.append(counts);checks+=3
 old4=sum(x['4']['old']for x in footprint);new4=sum(x['4']['new']for x in footprint);old8=sum(x['8']['old']for x in footprint);new8=sum(x['8']['new']for x in footprint)
 assert sum(len(v)*v.itemsize for v in source.values())==row['original_projected_payload_bytes']==row['proposal_projected_payload_bytes'];rows.append({'id':row['id'],'nodes':nn,'visited_nodes':len(visited),'changed_node_IDs':row['changed_node_IDs'],'projected_arrays':24,'all_projection_words_exactly_reversed':True,'projected_payload_bytes':row['proposal_projected_payload_bytes'],'summed_frontier_relative_32B_groups':{'4byte_node_fields':{'old':old4,'new':new4},'8byte_node_fields':{'old':old8,'new':new8}},'footprint_is_not_measured_cache_misses_or_time':True})
 # Actual persisted mapping supplies anti-vacuity cases without changing any files.
 changed=next(i for i in range(1,nn)if forward[i]!=i);assert reverse[forward[changed]]==changed;assert reverse[changed]!=changed;negative.append({'case':row['id'],'fixture':'identity_inverse_for_changed_node','rejected':reverse[changed]!=changed})
 child=next(v for v in source['tree.children']if v!=0xffffffff and forward[v]!=v);assert reverse[child]!=child;negative.append({'case':row['id'],'fixture':'unmapped_child_ID','rejected':True})
 old_slot=next(i for i,v in enumerate(source['cfv_slot'])if v<nn and forward[v]!=v);assert forward[source['cfv_slot'][old_slot]]!=proposal['cfv_slot'][forward[old_slot]];negative.append({'case':row['id'],'fixture':'mistaken_remap_of_physical_CFV_slot_value','rejected':True});print('Root model replay complete:',row['id'],flush=True)
assert len(rows)==6 and words==sum(x['exact_inverse_words']for x in Q['cases']);h.custody();h.save(H/'root-report.json',{'id':'D267-root','at':h.now(),'status':'pass_full_inverse_CPU_model_replay','protocol_sha256':sys.argv[1],'model_report_sha256':h.sha(H/'model-report.json'),'checks':checks,'projection_words_replayed':words,'cases':rows,'negative_reader_fixtures':negative,'all24proposed_arrays_every_word_reversed':True,'all_N_rows_spans_CTAorder_payload_lengths_unchanged':True,'candidate_or_GPU_output_created':False,'new_compiler_CUDA_kernel_solver_or_speed_runs':0,'same_agent_root_replay_shared_frame_parser_not_external_audit':True,'limits':'Only a reversible source-derived metadata model and relative address footprint. Actual private host layout, pinned staging reuse/alignment, locks/nonaction inputs, all experimental projection callers, CPU/GPU costs and every original correctness/performance/adoption gate remain. No candidate admitted by footprint counts.'});print(json.dumps({'status':'pass_CPU_model_only','checks':checks,'projection_words':words,'negative_fixtures':len(negative),'footprints':rows}),flush=True)
