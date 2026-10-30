import hashlib,json,math,struct,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
P=h.read(H/'protocol.json')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
inventory=h.read(H/'source-review.json')['device_field_inventory'];anchor=h.read(ROOT/'epoch/exact-anchor.json');hashes={};checks=pair_bytes=offset_values=0
def req(ok,label):
 global checks
 assert ok,label;checks+=1
def pair(a,b):
 global pair_bytes
 req(a.stat().st_size==b.stat().st_size,'equal whole extent');digest=hashlib.sha256()
 with a.open('rb') as x,b.open('rb') as y:
  while True:
   left=x.read(1024*1024);right=y.read(1024*1024);req(left==right,'all retained bytes')
   if not left:break
   digest.update(left);pair_bytes+=len(left)
 for p in [a,b]:hashes[str(p)]={'bytes':p.stat().st_size,'sha256':digest.hexdigest()}
def gpu_pair(a,b,bi,ci):
 global pair_bytes,offset_values
 names=['iteration','algorithm','hands']+inventory;descs=[{x['name']:x for x in info['device_fields']} for info in [bi,ci]]
 req([list(x) for x in descs]==[inventory,inventory],'all actual device fields')
 req(bi['offset_format_bits']==64 and ci['offset_format_bits']==32,'actual immutable offset format')
 req(bi['offset_enum_extra_bytes']==0 and ci['wrapper_bytes']==bi['wrapper_bytes']+ci['offset_enum_extra_bytes'],'only exact enum wrapper size delta')
 excluded={'device_fields','wrapper_bytes','offset_enum_extra_bytes','offset_format_bits'}
 req({k:v for k,v in bi.items() if k not in excluded}=={k:v for k,v in ci.items() if k not in excluded},'all other host/device geometry')
 streams=[a.open('rb'),b.open('rb')];digests=[hashlib.sha256(),hashlib.sha256()]
 def read(side,n):
  data=streams[side].read(n);req(len(data)==n,'full declared record extent');digests[side].update(data);return data
 try:
  req(read(0,16)==read(1,16)==b'D166-GPU-RAW1\0\0\0','GPU magic')
  for name in names:
   records=[]
   for side in [0,1]:
    kind,length=struct.unpack('<II',read(side,8));req(0<length<512,'boundedname');actual=read(side,length).decode();words,=struct.unpack('<Q',read(side,8));req(actual==name and kind in [0,2] and words<=2**31,'complete ordered unique inventory')
    if name in descs[side]:
     d=descs[side][name];req(d['elements']*d['element_bytes']==d['raw_bytes']==words*4 and d['words']==words,'actual typed buffer extent')
    else:req(words==(2 if name=='hands' else 1),'host scalar extent')
    records.append((kind,words))
   if name=='d_node_data_off':
    bd,cd=descs[0][name],descs[1][name];req(bd['element_bytes']==8 and cd['element_bytes']==4 and bd['elements']==cd['elements'],'exact original64 and narrow32 physical allocation')
    values=[]
    for side,bits in [(0,64),(1,32)]:
     kind,words=records[side];data=read(side,4 if kind==0 else words*4)
     if kind==0:req(data==b'\0'*4,'lossless zero encoding');values.append((0 for _ in range(bd['elements'])))
     else:values.append((x[0] for x in struct.iter_unpack('<Q' if bits==64 else '<I',data)))
    for left,right in zip(*values):req(left==(2**64-1 if right==2**32-1 else right),'every original offset decoded exactly');offset_values+=1
   else:
    req(records[0]==records[1],'unchanged physical field header')
    if name in descs[0]:req(descs[0][name]==descs[1][name],'unchanged original field dtype/extent')
    remaining=4 if records[0][0]==0 else records[0][1]*4
    while remaining:
     n=min(remaining,1024*1024);left=read(0,n);right=read(1,n);req(left==right,'every unchanged physical field byte');pair_bytes+=n;remaining-=n
  for side,path in enumerate([a,b]):req(streams[side].tell()==path.stat().st_size and streams[side].read(1)==b'','entire GPU physical frame');hashes[str(path)]={'bytes':path.stat().st_size,'sha256':digests[side].hexdigest()}
 finally:
  for stream in streams:stream.close()
logs={};science=quality=0
excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms','runtime_nvrtc_jit_included'}
for arm in P['sequence']:
 raw=(H/'execution'/(arm+'.stdout.log')).read_text(encoding='utf-8');results=[json.loads(s.split('AUTORESEARCH_RESULT ',1)[1]) for s in raw.splitlines() if 'AUTORESEARCH_RESULT ' in s];stages=[json.loads(s.split('AUTORESEARCH_STAGE ',1)[1]) for s in raw.splitlines() if 'AUTORESEARCH_STAGE ' in s];conv=[{k:s[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for s in stages if s.get('stage')=='convergence_check']
 req(len(results)==3 and all(x['runtime_nvrtc_jit_included'] is False for x in results),'honest unscored compile telemetry')
 req([[{k:v for k,v in x.items() if k not in excluded} for x in results],conv]==[[{k:v for k,v in x.items() if k not in excluded} for x in anchor[0]],anchor[1]],'every original complete scientific/stopping/quality record')
 req(len(conv)==23 and 'test result: ok. 1 passed; 0 failed; 0 ignored;' in raw,'original checkpoints and terminal test')
 req(sum(s=='D171_BIND '+arm for s in raw.splitlines())==6,'six original/lifecycle GPU constructions use proper sealed format binding')
 science+=len(results);quality+=len(conv);logs[arm]=[json.loads(s.split('D156_CONTROL ',1)[1]) for s in raw.splitlines() if s.startswith('D156_CONTROL ')]
 resource=h.read(H/'execution'/(arm+'.resource.json'));req(resource['reported_peak_working_set_bytes']<=P['limits']['process_reported_peak_max_bytes'] and resource['reported_peak_commit_bytes']<=P['limits']['process_reported_peak_max_bytes'],'reported memory caps');req(resource['minimum_observed_available_RAM_bytes']>=P['limits']['available_RAM_during_bytes'],'available RAM cap')
cpu=gpu=query=save=evs=0
for b,c in zip(logs['baseline'],logs['candidate']):
 name=b['fixture_id'];req(name==c['fixture_id'] and b['all_GPU_and_CPU_objects_dropped'] and c['all_GPU_and_CPU_objects_dropped'],'whole fixture ownership terminal')
 req([x['stage'] for x in b['stages']]==[x['stage'] for x in c['stages']]==P['lifecycle_stages'],'all fixed lifecycle stages')
 for bs,cs in zip(b['stages'],c['stages']):
  req({k:v for k,v in bs.items() if k!='info'}=={k:v for k,v in cs.items() if k!='info'},'all stage iteration/future EV bits');stage=bs['stage'];bo=H/'baseline-output';co=H/'candidate-output'
  if bs['ev_bits'] is not None:req(math.isfinite(struct.unpack('<d',struct.pack('<Q',bs['ev_bits']))[0]),'finite future EV');evs+=1
  pair(bo/f'{name}-{stage}.cpu.bin',co/f'{name}-{stage}.cpu.bin');cpu+=1
  gpu_pair(bo/f'{name}-{stage}.gpu.bin',co/f'{name}-{stage}.gpu.bin',bs['info'],cs['info']);gpu+=1
  print('D171 complete raw reader',name,stage,'exact',flush=True)
 for stage in ['locked','resumed']:pair(H/'baseline-output'/f'{name}-{stage}.query.json',H/'candidate-output'/f'{name}-{stage}.query.json');query+=1
 pair(H/'baseline-output'/f'{name}.save',H/'candidate-output'/f'{name}.save');save+=1
req(science==6 and quality==46 and cpu==gpu==12 and query==6 and save==3 and evs==9,'complete fixed fullsize matrix')
req(len(hashes)==66,'all66 retained files streamed and hashed');raw_bytes=sum(p.stat().st_size for d in H.glob('*-output') for p in d.iterdir() if p.is_file());req(raw_bytes<=P['limits']['raw_reservation_bytes'],'raw reservation')
h.custody();D=ROOT/'comparisons/D171-offset-raw-control';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D171','at':h.now(),'status':'pass_full_canonical_state_and_lossless_offset_representation','protocol_sha256':h.sha(H/'protocol.json'),'full_records_exact':science,'checkpoints_exact':quality,'whole_CPU_pairs':cpu,'whole_GPU69field_pairs':gpu,'query_pairs':query,'save_pairs':save,'future_EV_pairs':evs,'unchanged_physical_pair_bytes':pair_bytes,'exact_decoded_offset_values':offset_values,'reader_checks':checks,'whole_compared_file_sha256':hashes,'raw_output_bytes':raw_bytes,'all_owned_children_terminal':True,'performance_measurements':0,'candidate_accepted':False,'scope':'Entire original canonical CPU state and65 unchanged physical GPU arrays including full CFV byte exact. All actual offset32/64 physical payload retained/hashed and every value exactly decoded. Only prospective private dtype/extent and measured enum size differences, no other field/padding/numerical exception. Warm/locked/continued/save/resume/query/EV full exact. Prebuilt PTX giant observer timings unscored. Broad/source/feature/fallback-resource/full-speed/adoption gates remain.'})
print(json.dumps({'status':'pass','checks':checks,'unchanged_pair_bytes':pair_bytes,'offset_values_exact':offset_values,'raw_bytes':raw_bytes}),flush=True)
