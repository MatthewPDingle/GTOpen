"""Stream every full frame; decode all CFV guards and all graph arguments/edges."""
import array,hashlib,json,statistics,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D287-terminal-component';P=h.read(H/'protocol.json');O=H/'execution';OUT=H/'component-output';h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
inventory=h.read(H/'source-review.json')['device_field_inventory'];checks=0;allbytes=0;allwords=0;guardwords=0;hashes={}
def req(v,label):
 global checks
 assert v,label;checks+=1
raw=(O/'probe.stdout.log').read_text(encoding='utf-8');results=[json.loads(l.split('AUTORESEARCH_RESULT ',1)[1])for l in raw.splitlines()if l.startswith('AUTORESEARCH_RESULT ')];stages=[json.loads(l.split('AUTORESEARCH_STAGE ',1)[1])for l in raw.splitlines()if l.startswith('AUTORESEARCH_STAGE ')];anchor=h.read(ROOT/'epoch/exact-anchor.json');excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms','runtime_nvrtc_jit_included'}
conv=[{k:r[k]for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}for r in stages if r.get('stage')=='convergence_check']
req([[{k:v for k,v in r.items()if k not in excluded}for r in results],conv]==[[{k:v for k,v in r.items()if k not in excluded}for r in anchor[0]],anchor[1]],'entire originalscience and23convergence checkpoints');req(all(not r['runtime_nvrtc_jit_included']for r in results),'prebuiltPTX clocks honest')
req([l for l in raw.splitlines()if l.startswith('D287_BIND ')]==['D287_BIND baseline']*3,'sameacceptedmodule3constructors')
records=[json.loads(l.split('D287_CASE ',1)[1])for l in raw.splitlines()if l.startswith('D287_CASE ')];starts=[json.loads(l.split('D287_CASE_START ',1)[1])for l in raw.splitlines()if l.startswith('D287_CASE_START ')];before={r['fixture']:r['info']for r in [json.loads(l.split('D287_BEFORE ',1)[1])for l in raw.splitlines()if l.startswith('D287_BEFORE ')]};ends=[json.loads(l.split('D287_FIXTURE_COMPLETE ',1)[1])for l in raw.splitlines()if l.startswith('D287_FIXTURE_COMPLETE ')]
expected=[f'{fixture}-p{p}-{tag}'for fixture in P['fixture_order']for p in P['players']for tag in P['cohort_tags']]
req([r['id']for r in records]==[r['id']for r in starts]==expected,'all60nativecases/order');req([r['fixture']for r in ends]==P['fixture_order']and all(r['CPU_state_fingerprint_unchanged']and r['all_owned_GPU_and_CPU_objects_dropped']for r in ends),'CPUstateandterminalowners');req('test result: ok. 1 passed; 0 failed;'in raw,'originalfixture test terminal')
def vector(raw,code):
 n,=struct.unpack_from('<Q',raw);a=array.array(code);a.frombytes(raw[8:]);req(len(a)==n,'planvectorwidth');return a
plans={};schema=[v[0]for v in h.read(P['schema_path'])['fields']]
select={'num_nodes','num_levels','nh','nh_max','cfv_blocks','cfv_slot','fold_nodes','fold_spans','show_nodes','show_spans','riv_max_cnt'}
for item in P['raw_input_plans']:
 path=Path(item['path']);h.pin(path,item['sha256']);d={}
 with path.open('rb')as f:
  req(f.read(17)==b'D183_PLAN_RAW1\0\0\0','entireoriginalplanmagic')
  for name in schema:
   n,=struct.unpack('<I',f.read(4));req(f.read(n).decode()==name,'originalplanfieldorder');size,=struct.unpack('<Q',f.read(8))
   if name in select:d[name]=f.read(size);req(len(d[name])==size,'entireselectedplanfield')
   else:f.seek(size,1)
  req(f.read(1)==b'','wholeplanendpoint')
 model={k:struct.unpack('<Q',d[k])[0]for k in ['num_nodes','num_levels','nh_max','cfv_blocks']};model['nh']=list(vector(d['nh'],'Q'));model['riv_max_cnt']=list(vector(d['riv_max_cnt'],'Q'))
 for k in ['cfv_slot','fold_nodes','show_nodes']:model[k]=vector(d[k],'I')
 for k in ['fold_spans','show_spans']:
  n,=struct.unpack_from('<Q',d[k]);req(n==model['num_levels']and len(d[k])==8+8*n,'alllevelspans');model[k]=list(struct.Struct('<II').iter_unpack(d[k][8:]))
 slots=np.array([model['cfv_slot'][node]for node in list(model['fold_nodes'])+list(model['show_nodes'])],dtype=np.int64);req(len(slots)==len(np.unique(slots))and np.all(slots<model['cfv_blocks']),'terminalrowunique/bounds');mask=np.zeros(model['cfv_blocks'],dtype=bool);mask[slots]=True;model['mask']=mask;plans[item['fixture']['fixture']]=model
def frame(path,info,model,player=None,poison=None):
 global allbytes,allwords,guardwords
 desc={v['name']:v for v in info['device_fields']};req(list(desc)==inventory and len(desc)==66,'all66actualbuffers');req(info['host_fields']==3 and info['wrapper_bytes']==4448 and info['CFV_words']==model['cfv_blocks']*model['nh_max'],'fullphysicalgeometry')
 digest=hashlib.sha256();fieldhash={};nonzero=0
 def read(f,n):
  global allbytes
  data=f.read(n);req(len(data)==n,'fullrawextent');digest.update(data);allbytes+=n;return data
 with path.open('rb')as f:
  req(read(f,16)==b'D166-GPU-RAW1\0\0\0','GPUrawmagic')
  for name in ['iteration','algorithm','hands']+inventory:
   kind,n=struct.unpack('<II',read(f,8));req(0<n<512,'fieldnamebound');req(read(f,n).decode()==name,'all69typedfieldorder');count,=struct.unpack('<Q',read(f,8));req(count<2**31,'fieldwordbound');allwords+=count
   hd=hashlib.sha256();hd.update(struct.pack('<IQ',kind,count))
   if name in desc:
    q=desc[name];req(q['elements']*q['element_bytes']==q['words']*4==q['raw_bytes']==count*4 and q['element_bytes']in[4,8],'actualdtypeandwholephysicalextent');req((count==0 or q['address']>0)and q['address']%q['element_bytes']==0,'actualdevicealignment')
   if kind==0:
    data=read(f,4);req(data==b'\0'*4,'losslesszeroimage');hd.update(data);req(not(name=='d_cfv'and poison is not None),'seededCFVliteralimage')
   else:
    req(kind==2,'literalrawkind')
    if name=='d_cfv'and poison is not None:
     stride=model['nh_max'];nh=model['nh'][player];req(count==model['cfv_blocks']*stride,'wholeCFVrowextent');rows=0
     while rows<model['cfv_blocks']:
      take=min(4096,model['cfv_blocks']-rows);data=read(f,take*stride*4);hd.update(data);a=np.frombuffer(data,dtype='<u4').reshape(take,stride);owned=model['mask'][rows:rows+take]
      req(np.all(a[~owned]==poison),'everyunownedCFVrowguard');req(np.all(a[:,nh:]==poison),'everyphysicalrowpaddingguard');active=a[owned,:nh];req(np.all((active&0x7f800000)!=0x7f800000),'allactualterminaloutputsfiniteandwritten');nonzero+=int(np.count_nonzero(active&0x7fffffff));guardwords+=int(np.count_nonzero(~owned))*stride+int(np.count_nonzero(owned))*(stride-nh);rows+=take
    else:
     remaining=count*4
     while remaining:
      data=read(f,min(16*1024**2,remaining));hd.update(data);remaining-=len(data)
   fieldhash[name]=hd.hexdigest()
  req(f.tell()==path.stat().st_size and f.read(1)==b'','all69fieldscompleteendpoint')
 hashes[str(path)]={'bytes':path.stat().st_size,'sha256':digest.hexdigest()}
 if poison is not None:req(nonzero>0,'nonvacuousactualterminalCFVs')
 return fieldhash
basehash={}
for fixture in P['fixture_order']:
 info=before[fixture];model=plans[fixture];req(info['iteration']==P['expected_stops'][fixture]and info['hands']==model['nh']and info['nh_max']==model['nh_max'],'originalsolvedinputgeometry')
 ranges=[(d['address'],d['address']+d['raw_bytes'])for d in info['device_fields']if d['raw_bytes']]
 for i,(a,b)in enumerate(ranges):
  for c,d in ranges[i+1:]:req(b<=c or d<=a,'allactualGPUallocationsdisjoint')
 basehash[fixture]=frame(OUT/f'{fixture}-before.gpu.bin',info,model)
def expected_args(family,level,p,info,model):
 a={x['name']:x['address']for x in info['device_fields']};start,count=model[family+'_spans'][level];nh,mo=model['nh'][p],model['nh'][1-p];stride=model['nh_max'];address=lambda name:a[name]
 if family=='fold':return[address('d_fold_nodes'),start,count,p,address('d_node_player'),address('d_node_twin'),address('d_node_tlose'),address('d_rsrc[0]'),address('d_rsrc[1]'),address('d_reach[0]'),address('d_reach[1]'),address(f'd_hand_c1[{p}]'),address(f'd_hand_c2[{p}]'),address(f'd_fold_card_off[{1-p}]'),address(f'd_fold_card_idx[{1-p}]'),address(f'd_same[{p}]'),address('d_cfv_slot'),address('d_cfv'),nh,mo,stride]
 return[address('d_show_nodes'),start,count,address('d_node_twin'),address('d_node_tlose'),address('d_node_ttie'),address('d_node_river_slot'),address(f'd_rsrc[{1-p}]'),address(f'd_reach[{1-p}]'),address(f'd_riv_off[{p}]'),address(f'd_riv_cnt[{p}]'),address(f'd_riv_idx[{p}]'),address(f'd_riv_lower[{p}]'),address(f'd_riv_upper[{p}]'),address(f'd_riv_off[{1-p}]'),address(f'd_riv_cnt[{1-p}]'),address(f'd_riv_idx[{1-p}]'),address(f'd_riv_card_off[{1-p}]'),address(f'd_riv_card_pos[{1-p}]'),address(f'd_same[{p}]'),address(f'd_hand_c1[{p}]'),address(f'd_hand_c2[{p}]'),address('d_cfv_slot'),address('d_cfv'),nh,mo,stride]
function_handles={}
def dag(record,model):
 stats=record['stats'];nodes=stats['dag']['nodes'];p=record['player'];req([n['index']for n in nodes]==list(range(len(nodes))),'allactualgraphnodes');req(all(n['kind']in['empty','kernel']for n in nodes),'onlydeclaredgraphnodekinds')
 expected={(kind,l)for kind in ['fold','show']for l,(_,count)in enumerate(model[kind+'_spans'])if count};ks=[n for n in nodes if n['kind']=='kernel'];req({(n['family'],n['level'])for n in ks}==expected and len(ks)==len(expected)==stats['dag']['all_original_terminal_nodes'],'everyoriginalterminalgridexactlyonce');req(len(nodes)-len(ks)<=2*sum(bool(f[1]and s[1])for f,s in zip(model['fold_spans'],model['show_spans']))+1,'emptydependencyoverheadbounded')
 ancestors={}
 def walk(i,trail=None):
  trail=set()if trail is None else trail;req(i not in trail,'graphacyclic');trail=trail|{i}
  if i not in ancestors:
   req(len(nodes[i]['dependencies'])==len(set(nodes[i]['dependencies']))and all(0<=j<len(nodes)for j in nodes[i]['dependencies']),'validactualgraphdependencies');out=set(nodes[i]['dependencies'])
   for j in nodes[i]['dependencies']:out|=walk(j,trail)
   ancestors[i]=out
  return ancestors[i]
 for n in nodes:walk(n['index'])
 for node in ks:
  family,l=node['family'],node['level'];req(node['args']==expected_args(family,l,p,record['info'],model),'allactual21or27arguments');count=model[family+'_spans'][l][1];req(node['grid']==[count,1,1]and node['block']==[128,1,1],'originalgridblock');shared=model['nh'][1-p]*4+(16*model['riv_max_cnt'][1-p]if family=='show'else 0);req(node['shared_bytes']==shared,'originaldynamicsharedextent')
  key=(record['fixture'],family);function_handles.setdefault(key,node['function']);req(node['function']==function_handles[key]and node['function']>0,'sameactualoriginalfunctionhandle')
 for x in ks:
  for y in ks:
   if x['level']>y['level']:req(x['index']in ancestors[y['index']],'joinbeforeeverylowerlevel')
   elif x['level']==y['level']and x['family']=='fold'and y['family']=='show':
    req((x['index']not in ancestors[y['index']]and y['index']not in ancestors[x['index']])if stats['selected']else x['index']in ancestors[y['index']],'actualsamelevelbranchindependenceorserialfallback')
for index,r in enumerate(records):
 model=plans[r['fixture']];req(r['info']==before[r['fixture']],'alloriginalphysicaldtypegeometryhoststatewrapperandaddresses');req(r['replays']==P['expected_stops'][r['fixture']]==r['stats']['replays'],'fixedbatchreplays');s=r['stats'];req(s['player']==r['player']and s['candidate']==r['candidate'],'actualrouteidentity');selected=r['candidate']and model['num_nodes']>=65536 and any(f[1]and z[1]for f,z in zip(model['fold_spans'],model['show_spans']));req(s['selected']==bool(selected),'actualfixedselection/fallback');req(s['component_ns']==s['setup_capture_ns']+s['replays_completion_ns']+s['cleanup_ns']and s['method_wall_ns']>=s['component_ns']+s['inspection_ns_excluded'],'allinclusivecomponentwindows');req(s['all_temporary_graph_stream_events_dropped']and s['no_new_application_device_arrays'],'explicittemporarycleanup/applicationpayloadscope');dag(r,model)
 got=frame(OUT/(r['id']+'.gpu.bin'),r['info'],model,r['player'],r['poison_bits']);req(all(got[k]==v for k,v in basehash[r['fixture']].items()if k!='d_cfv'),'all65devicebuffersand3hostfieldsunchanged');r['_fieldhash']=got
 for counter in ['kernel_ticks100ns','user_ticks100ns']:req(r['OS_after'][counter]>=r['OS_before'][counter],'allthreadprocessCPUmonotonic')
 print('D287 fullraw case',index+1,'/',len(records),r['id'],flush=True)
def literal_pair(a,b):
 req(a.stat().st_size==b.stat().st_size,'literalfullpairsizes')
 with a.open('rb')as f,b.open('rb')as g:
  while True:
   x=f.read(16*1024**2);y=g.read(16*1024**2);req(x==y,'everyliteralpairedbyte')
   if not x:break
for fixture in P['fixture_order']:
 for p in P['players']:
  for a,b in [('W0B','W0C'),('W1B','W1C'),('B1','C1'),('B2','C2'),('B3','C3')]:literal_pair(OUT/f'{fixture}-p{p}-{a}.gpu.bin',OUT/f'{fixture}-p{p}-{b}.gpu.bin')
 literal_pair(OUT/f'{fixture}-before.cpu.bin',OUT/f'{fixture}-after.cpu.bin')
 for side in ['before','after']:
  path=OUT/f'{fixture}-{side}.cpu.bin';hashes[str(path)]={'sha256':h.sha(path),'bytes':path.stat().st_size}
  with path.open('rb')as f:
   req(f.read(16)==b'D156-CPU-RAW1\0\0\0','CPUqscalemagic');it,iso,locks,preds=struct.unpack('<IIII',f.read(16));req(it==P['expected_stops'][fixture]and iso==1 and locks==preds==0,'originalCPUpublishedstate')
   for expected in[1,1,2,2]:
    kind,=struct.unpack('<I',f.read(4));n,sc=struct.unpack('<QQ',f.read(16));req(kind==expected,'originalCPUstoretypes');f.seek(2*n+4*sc,1)
   req(f.tell()==path.stat().st_size,'entireCPUqscaleendpoint')
rows=[];gates={};total_b=total_c=0.
for fixture in P['fixture_order']:
 for p in P['players']:
  arms={arm:[next(r for r in records if r['id']==f'{fixture}-p{p}-{arm}{i}')for i in[1,2,3]]for arm in['B','C']};b=[r['stats']['component_ns']/1e6 for r in arms['B']];c=[r['stats']['component_ns']/1e6 for r in arms['C']];bm,cm=statistics.median(b),statistics.median(c);slower=sum(y>x for x,y in zip(b,c));total_b+=bm;total_c+=cm
  cpu=lambda r:sum(r['OS_after'][k]-r['OS_before'][k]for k in['kernel_ticks100ns','user_ticks100ns'])/10000
  bcpu,ccpu=[cpu(r)for r in arms['B']],[cpu(r)for r in arms['C']];mem={}
  for field in['private_bytes','working_set_bytes']:mem[field]=statistics.median(r['OS_after'][field]-r['OS_before'][field]for r in arms['C'])-statistics.median(r['OS_after'][field]-r['OS_before'][field]for r in arms['B'])
  guard=cm>bm and slower>=2;cpu_pass=statistics.median(ccpu)<=statistics.median(bcpu)*1.01;memory_pass=all(v<=64*1024**2 for v in mem.values());key=f'{fixture}:p{p}';gates[key+':fixture_clear']=not guard;gates[key+':CPU_clear']=cpu_pass;gates[key+':current_memory_clear']=memory_pass
  rows.append({'fixture':fixture,'player':p,'baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'slower_pairs':slower,'strict_guard_failed':guard,'CPU_baseline_ms':bcpu,'CPU_candidate_ms':ccpu,'CPU_guard_pass':cpu_pass,'added_current_memory_delta_bytes':mem,'current_memory_guard_pass':memory_pass})
for fixture in P['fixture_order']:
 frows=[r for r in rows if r['fixture']==fixture];b=[sum(r['baseline_ms'][i]for r in frows)for i in range(3)];c=[sum(r['candidate_ms'][i]for r in frows)for i in range(3)];gates[fixture+':aggregate_players_guard_clear']=not(statistics.median(c)>statistics.median(b)and sum(y>x for x,y in zip(b,c))>=2)
saving=total_b-total_c;gates['minimum_component_effort_saving']=saving>=P['minimum_component_saving_ms'];gates['all_bit_graph_guard_science_controls']=True;resource=h.read(O/'probe.resource.json');L=P['limits'];gates['whole_native_memory_admission']=resource['reported_peak_working_set_bytes']<=L['process_reported_peak_max_bytes']and resource['reported_peak_commit_bytes']<=L['process_reported_peak_max_bytes']and resource['minimum_observed_available_RAM_bytes']>=L['available_RAM_during_bytes'];passed=all(gates.values());h.custody()
h.save(H/'report.json',{'id':'D287','at':h.now(),'status':'pass_component_effort_cost_and_bits_only'if passed else'decline_fixed_terminal_concurrency_at_component_gate','protocol_sha256':h.sha(H/'protocol.json'),'gates':gates,'failed_gates':[k for k,v in gates.items()if not v],'baseline_sum_player_fixture_median_ms':total_b,'candidate_sum_player_fixture_median_ms':total_c,'component_saving_ms':saving,'minimum_component_saving_ms':P['minimum_component_saving_ms'],'cases':rows,'full_component_cases':60,'entire_GPU_frames':63,'entire_device_fields_per_frame':66,'original_scientific_results_exact':3,'original_convergence_checks_exact':23,'all30_literal_full69field_pairs_exact':True,'all65other_device_and3host_fields_unchanged':True,'whole_CPU_qscale_pairs_exact':3,'every_physical_CFV_and_guard_word_checked':True,'CFV_guard_words':guardwords,'all_GPU_raw_words_in_complete_frames':allwords,'all_GPU_raw_encoded_bytes_decoded':allbytes,'reader_checks':checks,'full_raw_file_sha256':hashes,'whole_process_accounting':resource,'new_optimizer_source_or_fullspeed_samples':0,'candidate_accepted':False,'limits':'Actual unchanged terminalkernel component atstablefinalaverage-policyreach; fixed iteration-count batches, sumofsix medians, not complete solver/CFR timing orprovenremovablecriticalpath. WholeCFV/65otherdevices/allgraphparameters/pointerextents/joins exact. No physicalco-residency/counter/everyintermediateCFRinput/universalmaterial/instantaneousGPUpeak/adoptionclaim. Driver/graph/auxstream cost muststillcount inreal production source/fullsolverifcomponentpasses. Ifdeclined, exactroute/threshold/event/order/scope/helper/source/samplefamilyclosedwithoutrescue.'});print(json.dumps({'status':'pass_component_only'if passed else'decline','saving_ms':saving,'minimum_ms':P['minimum_component_saving_ms'],'failed_gates':[k for k,v in gates.items()if not v]}),flush=True)
