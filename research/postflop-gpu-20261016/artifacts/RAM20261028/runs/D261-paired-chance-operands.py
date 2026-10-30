"""Conservative PTX pointer/load ancestry and independent-recurrence witnesses."""
import collections,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();R=ROOT/'runs/E114-resource';Q=h.read(R/'report.json');assert Q['status']=='pass_compiled_resources_mechanism_pending'and all(Q['gates'].values());O=ROOT/'runs/D261-paired-chance-operands';O.mkdir(exist_ok=False)
def review(text):
 head,body=text.split('{',1);assert head.count('.param ')==15;ins=[]
 for line_no,line in enumerate(body.splitlines(),1):
  line=line.strip();m=re.fullmatch(r'(?:@!?%p\d+\s+)?([a-z][a-z0-9_.]*)\s+(.*);',line)
  if m:ins.append({'line':line_no,'op':m[1],'args':[x.strip()for x in m[2].split(',')],'text':line})
  elif line and not(line.startswith(('.reg ','$L__','}'))or line=='ret;'):raise AssertionError('unparsed instruction '+line)
 assert ins and not any(x['op'].startswith(('call','atom','red','bar'))for x in ins)
 ptr=collections.defaultdict(set);deps=collections.defaultdict(set);loads={};definitions=[]
 for idx,x in enumerate(ins):
  op,args=x['op'],x['args'];isload=op.startswith('ld.global');isparam=op.startswith('ld.param');dest=args[0]if not op.startswith(('st.','bra'))else None;inputs=set(re.findall(r'%[a-z]+\d+',','.join(args[1:]if dest else args)))
  assert dest is None or re.fullmatch(r'%[a-z]+\d+',dest)
  param=None
  if isparam:
   m=re.fullmatch(r'\[up_chance_param_(\d+)\]',args[1]);assert m;param=int(m[1]);assert param<15
  if isload:loads[idx]=x
  definitions.append((idx,dest,inputs,isload,param,op))
 for turn in range(1000):
  changed=False
  for idx,dest,inputs,isload,param,op in definitions:
   if dest is None:continue
   np=set()if isload else({param}if param is not None and'.u64'in op else set()if param is not None else set().union(*(ptr[v]for v in inputs)))
   nd=({idx}if isload else set())|set().union(*(deps[v]for v in inputs))
   a,b=len(ptr[dest]),len(deps[dest]);ptr[dest]|=np;deps[dest]|=nd;changed|=(a!=len(ptr[dest])or b!=len(deps[dest]))
  if not changed:break
 else:raise AssertionError('dataflow did not converge')
 for idx,x in loads.items():
  regs=re.findall(r'%[a-z]+\d+',x['args'][1]);orig=set().union(*(ptr[v]for v in regs));assert len(orig)==1,(x,orig);x['parameter']=next(iter(orig));x['address_load_ancestors']=sorted(set().union(*(deps[v]for v in regs)))
 # Every paired CFV address uses one child-slot lookup whose index came from cc_child.
 childslots={idx for idx,x in loads.items()if x['parameter']==11 and any(loads[j]['parameter']==6 for j in x['address_load_ancestors'])};groups={idx:[]for idx in childslots};cfv={idx:x for idx,x in loads.items()if x['parameter']==12};assert cfv and childslots
 for idx,x in cfv.items():
  assert x['op']=='ld.global.f32';uses=childslots.intersection(x['address_load_ancestors']);assert len(uses)==1,(idx,uses);groups[next(iter(uses))].append(idx)
 assert all(len(v)==2 for v in groups.values()),groups
 sites=collections.Counter(x['parameter']for x in loads.values());assert all(sites[p]==len(groups)for p in[5,6,7]);assert len(cfv)==2*len(groups)
 # Actual scalar FADD sites keep separate self recurrence variables; first contributions add +0.
 bydest={x['args'][0]:idx for idx,x in cfv.items()};adds=[x for x in ins if x['op']=='add.f32'];assert len(adds)==len(cfv);used=[];carried=set()
 for x in adds:
  dest,a,b=x['args'];vals=[v for v in[a,b]if v in bydest];assert len(vals)==1,x;other=b if vals[0]==a else a;assert other==dest or other=='0f00000000',x
  if other==dest:carried.add(dest)
  used.append(bydest[vals[0]])
 assert len(carried)==2 and len(used)==len(set(used))==len(cfv)
 floats=collections.Counter(x['op']for x in ins if re.search(r'\.f32(?:\.|$)',x['op'])and not x['op'].startswith(('ld.','st.','mov.')));assert set(floats)=={'add.f32','mul.f32'}
 # Parent stores all derive from the same original cfv formal, no vector/store ABI change.
 stores=[x for x in ins if x['op'].startswith('st.global')];assert stores
 for x in stores:
  assert x['op']=='st.global.f32';regs=re.findall(r'%[a-z]+\d+',x['args'][0]);assert set().union(*(ptr[v]for v in regs))=={12}
 return {'instructions':len(ins),'dataflow_iterations':turn+1,'scalar_global_load_sites_by_parameter':dict(sorted(sites.items())),'shared_child_slot_groups':[{'child_slot_load':loads[k],'two_CFV_loads':[loads[j]for j in v]}for k,v in sorted(groups.items())],'scalar_CFV_load_sites':len(cfv),'one_metadata_set_per_two_CFV_sites':True,'independent_loop_carried_accumulators':sorted(carried),'scalar_FP_op_inventory':dict(floats),'all_FADD_sites_have_CFV_plus_self_or_positive_zero':True,'scalar_parent_store_sites':stores,'no_barrier_or_calls':True,'proof_scope':'Static conservative register ancestry and local source/operand witnesses only. Does not prove dynamic execution counts, full control-flow/FP equivalence, final driver SASS or speed.'}
reports={};negative=[]
for arch in ['compute_120','compute_75']:
 path=R/'execution'/('candidate-'+arch+'-up_chance.ptx.txt');text=path.read_text(encoding='utf-8');r=review(text);r['path']=str(path);r['sha256']=h.sha(path);reports[arch]=r
 # In-memory negative controls alter neither sealed PTX nor scientific source.
 first=r['shared_child_slot_groups'][0]['two_CFV_loads'][0]['text'];other=r['shared_child_slot_groups'][1]['two_CFV_loads'][0]['text'];first_args=re.fullmatch(r'ld.global.f32\s+(%f\d+),\s*(\[%rd\d+\]);',first).groups();other_args=re.fullmatch(r'ld.global.f32\s+(%f\d+),\s*(\[%rd\d+\]);',other).groups()
 # Replace the first address by another card's base: groups become1/3, not2/2.
 mutations=[('wrong_card_shared_base',text.replace(first_args[1],other_args[1],1))]
 self_add=re.search(r'add\.f32\s+(%f\d+),\s*\1,\s*(%f\d+);',text);assert self_add;peer=next(v for v in r['independent_loop_carried_accumulators']if v!=self_add[1]);mutations.append(('cross_accumulator_recurrence',text[:self_add.start()]+self_add[0].replace(', '+self_add[1]+',',', '+peer+',')+text[self_add.end():]))
 # A malformed FP primitive must never be interpreted as an ordered scalar add.
 mutations.append(('wrong_float_operation',text[:self_add.start()]+self_add[0].replace('add.f32','sub.f32',1)+text[self_add.end():]))
 for label,bad in mutations:
  assert bad!=text,(arch,label)
  try:review(bad)
  except AssertionError:negative.append({'arch':arch,'fixture':label,'rejected':True})
  else:raise AssertionError('negative accepted '+arch+'/'+label)
# Independent arithmetic decode of every integer proof record, no compiler/GPU.
D=ROOT/'runs/D260-paired-chance-scout';d=h.read(D/'report.json');h.pin(D/'ownership.bin',d['raw_ownership_sha256']);import struct
count=0
with(D/'ownership.bin').open('rb')as f:
 assert f.read(16)==b'D260-HAND-MAP1\0\0'
 for w in range(1,1025):
  for n in range(1327):
   b=f.read(24);assert len(b)==24;nh,width,first,second,cycles,tail=struct.unpack('<6I',b);assert(nh,width)==(n,w);expected_first=(n//(w*2))*w+min(n%(w*2),w);assert first==expected_first and second==n-expected_first and cycles==n//(2*w)and tail==n%(2*w);count+=1
 assert not f.read(1)
assert count==1358848
h.save(O/'report.json',{'id':'D261','at':h.now(),'status':'pass_scoped_emitted_two_accumulator_metadata_reuse','resource_protocol_sha256':Q['protocol_sha256'],'resource_report_sha256':h.sha(R/'report.json'),'source_manifest_sha256':h.sha(ROOT/'runs/E114-source/manifest.json'),'architectures':reports,'negative_reader_fixtures':negative,'all_integer_records_replayed':count,'source_and_PTX_unchanged':True,'all_owned_resource_children_terminal':True,'new_compiler_CUDA_or_GPU_processes':0,'candidate_accepted':False,'limits':'Scoped static ancestry/recurrence and integer ownership replay, same-agent review. Not whole CFG/SASS/FP-equivalence/dynamic-count/cost/speed proof. Actual full raw direct and engine/canonical plus all original adoption gates still required.'});h.custody();print(json.dumps({'status':'pass_scoped_static_only','architectures':{a:{'metadata_groups':len(r['shared_child_slot_groups']),'CFV_loads':r['scalar_CFV_load_sites'],'carried_accumulators':r['independent_loop_carried_accumulators']}for a,r in reports.items()},'negative_fixtures':len(negative),'integer_records':count}),flush=True)
