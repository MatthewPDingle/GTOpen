import ast,copy,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists()
assert h.read(ROOT/'runs/E106-engine-checkpoint/report.json')['status']=='scoped_engine_equivalence_pass_direct_and_canonical_pending'
R=ROOT/'runs/E106-resource-host';rr=h.read(R/'report.json');assert all(rr['gates'].values());H=ROOT/'runs/D217-nullable-lock-direct';H.mkdir(exist_ok=False);U=H/'up';V=H/'down';U.mkdir();V.mkdir();up_parent=ROOT/'runs/D177-up-action';down_parent=ROOT/'runs/D163-down-action'
host=(ROOT/'runs/E106-source-r2/candidate-mod.rs').read_bytes().decode('utf-8');a=host.index('struct E106LockArg');b=host.index('\npub const KERNEL_NAMES',a);helper=host[a:b];assert helper.count('unsafe impl')==1 and 'self.arg(&ABSENT)' in helper and 'self.arg(value.0)' in helper
for folder in [U,V]:
 (folder/'lock_arg.rs').write_bytes(helper.encode('utf-8'))
 for arm in ['baseline','candidate']:
  p=R/'baseline-compute_120.ptx' if arm=='baseline' else R/'execution/candidate-compute_120.ptx';h.pin(p,rr['PTX_sha256'][arm+'-compute_120']);shutil.copyfile(p,folder/(arm+'.ptx'))
old_up=h.read(up_parent/'corpus.json')['cases'];uc=[]
def append_up(c,kind,nullable):
 row=copy.deepcopy(c);row.update(id=len(uc),kernel_kind=kind,nullable=nullable);row['descriptor']=c['descriptor'][:14]+[kind,int(nullable)];uc.append(row)
for c in old_up:append_up(c,0,False)
for c in old_up:
 if c['role']!=1:append_up(c,0,True)
for kind in [1,2]:
 for c in old_up:append_up(c,kind,False)
 for c in old_up:
  if c['role']!=1:append_up(c,kind,True)
assert len(uc)==4095 and all({k:v for k,v in c.items() if k not in ['kernel_kind','nullable','descriptor']}=={k:v for k,v in old.items() if k!='descriptor'} and c['descriptor'][:14]==old['descriptor'] for c,old in zip(uc[:819],old_up))
h.save(U/'corpus.json',{'cases':uc,'legacy_prefix_cases':819,'train_cases':1365,'BR_cases':1365,'average_cases':1365,'scope':'All819originaltrain cases retained first, then null-unlocked variants and full duplicated corpus for each original evaluation mode. Data-value profiles and geometry axes preserved; newcase indices intentionally select same deterministic generators.'})
source=(up_parent/'probe.rs').read_bytes().decode('utf-8');changes=[]
def replace(s,old,new,count=1):
 assert s.count(old)==count,(old,s.count(old),count);changes.append({'old':old,'new':new,'count':count});return s.replace(old,new)
source=replace(source,'type Out=BufWriter<File>;','use cudarc::driver::sys;\ninclude!("lock_arg.rs");\ntype Out=BufWriter<File>;')
source=replace(source,'struct Case {nh:','struct Case {kernel_kind:u32,nullable:bool,nh:')
start=source.index(' let mut cases=Vec::new();');end=source.index(' let case_count=cases.len();',start);old_generator=source[start:end]
loader=''' let declared:serde_json::Value=serde_json::from_str(include_str!("corpus.json")).unwrap();
 let cases:Vec<Case>=declared["cases"].as_array().unwrap().iter().map(|c|{let n=|k:&str|c[k].as_u64().unwrap();Case{kernel_kind:n("kernel_kind") as u32,nullable:c["nullable"].as_bool().unwrap(),nh:n("hands") as usize,na:n("actions") as usize,block:n("threads") as u32,p:n("p") as i32,role:n("role") as u32,algo:n("algorithm") as u32,t:n("iteration") as u32,mode:n("value_mode") as u32,count:n("count") as i32}}).collect();assert_eq!(cases.len(),4095);
'''
source=source[:start]+loader+source[end:];changes.append({'old':old_generator,'new':loader,'count':1})
source=replace(source,'let Case{nh,na,block,p,role,algo,t,mode,count}=*c;','let Case{kernel_kind,nullable,nh,na,block,p,role,algo,t,mode,count}=*c;')
source=replace(source,' let bf=bm.load_function("up_action").unwrap();let cf=cm.load_function("up_action").unwrap();',' let bf=bm.load_function("up_action").unwrap();let cf=cm.load_function("up_action").unwrap();let be=bm.load_function("up_action_eval").unwrap();let ce=cm.load_function("up_action_eval").unwrap();')
source=replace(source,'  let mut sigma=vec!','  assert!(!nullable || lock.iter().all(|x|*x<0),"null only for globally unlocked table");\n  let mut sigma=vec!',1)
source=replace(source,'off as u32,loff as u32]);','off as u32,loff as u32,kernel_kind,nullable as u32]);')
source=replace(source,'  for (label,f) in [("baseline",&bf),("candidate",&cf)] {','  let(base_function,candidate_function)=if kernel_kind==0{(&bf,&cf)}else{(&be,&ce)};\n  for (label,f) in [("baseline",base_function),("candidate",candidate_function)] {')
source=replace(source,'.arg(&dl).arg(&dls)','.arg(E106LockArg(&dl,label=="candidate" && nullable)).arg(&dls)')
old='   unsafe{stream.launch_builder(f).arg(&dn)';new='   if kernel_kind==0 {unsafe{stream.launch_builder(f).arg(&dn)';source=replace(source,old,new)
endcall='.launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}'
evalcall=''' else {let evaluation_mode=(kernel_kind-1) as i32;unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&p).arg(&evaluation_mode).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&ds).arg(E106LockArg(&dl,label=="candidate" && nullable)).arg(&dls).arg(&dslot).arg(&mut dv).arg(&nharg).arg(&maxarg).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}}
'''
source=replace(source,endcall,endcall+'}'+evalcall)
source=replace(source,'role==0 && i>=off','kernel_kind==0 && role==0 && i>=off')
source=replace(source,'"stage":"case","id":index,','"stage":"case","id":index,"kernel_kind":kernel_kind,"nullable":nullable,')
source=replace(source,'drop(bf);drop(cf);drop(bm);','drop(bf);drop(cf);drop(be);drop(ce);drop(bm);')
for old,new in [('E085_IN1','E106_UP_IN1'),('E085_OUT1','E106_UP_OUT1'),('E085_IM1','E106_UP_IM1'),('E085_UNIT','E106_UP')]:source=source.replace(old,new)
(U/'probe.rs').write_text(source,encoding='utf-8',newline='\n');shutil.copyfile(up_parent/'discounts.rs',U/'discounts.rs');up_changes=changes;changes=[]
dc=copy.deepcopy(h.read(down_parent/'corpus.json'));legacy_down=len(dc);assert legacy_down==1530
for c in dc:c.update(nullable=False,reuse_zero=False)
for c in list(dc):
 if c['lock_mode']==0:q=copy.deepcopy(c);q['nullable']=True;dc.append(q)
for nh in [0,1,129,1326]:
 for na in [2,3,4,9,17]:
  for actor in [0,1]:
   for locked in [0,1,2,3]:
    for rm in [0,4,5]:
     for pm in [0,3,4]:
      row={'nh':nh,'na':na,'block':128,'actor':actor,'lock_mode':locked,'regret_mode':rm,'reach_mode':pm,'count':1,'nullable':False,'reuse_zero':True};dc.append(row)
      if locked==0:row=copy.deepcopy(row);row['nullable']=True;dc.append(row)
for c in dc:
 nh=c['nh'];other=5 if nh==0 else nh+5;ns=[nh,other] if c['actor']==0 else [other,nh]
 if c['reuse_zero']:ns[1]=0
 c['descriptor']=[ns[0],ns[1],c['na'],c['block'],c['actor'],c['lock_mode'],c['regret_mode'],c['reach_mode'],c['count'],1,2,13,7,2,c['na']+10,int(c['nullable']),int(c['reuse_zero'])]
h.save(V/'corpus.json',dc);source=(down_parent/'probe.rs').read_bytes().decode('utf-8');source=replace(source,'type Out=BufWriter<File>;','use cudarc::driver::sys;\ninclude!("lock_arg.rs");\ntype Out=BufWriter<File>;')
old='let other=if nh==0{5}else{nh+5};let nhs=if actor==0{[nh,other]}else{[other,nh]};';new='let nullable=c["nullable"].as_bool().unwrap();let reuse=c["reuse_zero"].as_bool().unwrap();let other=if nh==0{5}else{nh+5};let mut nhs=if actor==0{[nh,other]}else{[other,nh]};if reuse{nhs[1]=0;}let active_nh=nhs[actor];';source=replace(source,old,new)
source=replace(source,'  let mut sigma=vec!','  assert!(!nullable || lock.iter().all(|x|*x<0),"null only for globally unlocked table");\n  let mut sigma=vec!')
source=replace(source,'rows as u32]);','rows as u32,nullable as u32,reuse as u32]);')
source=replace(source,'.arg(&dl).arg(&dls)','.arg(E106LockArg(&dl,label=="candidate" && nullable)).arg(&dls)')
source=replace(source,'p==actor&&nh>0&&i/nh>=5&&i/nh<5+na','p==actor&&active_nh>0&&i/active_nh>=5&&i/active_nh<5+na')
for old,new in [('E091_IN1','E106_DOWN_IN1'),('E091_OUT1','E106_DOWN_OUT1'),('E091_IM1','E106_DOWN_IM1'),('E091_RAW','E106_DOWN')]:source=source.replace(old,new)
(V/'probe.rs').write_text(source,encoding='utf-8',newline='\n');h.save(H/'source-review.json',{'id':'D217','at':h.now(),'previous_goal_turn':'progress: E106 exact host/layout/compiler-resource/nullable-load mechanism and original36case/752phase raw engine/lock lifecycle comparisons passed; no speed/adoption.','up_cases':len(uc),'down_cases':len(dc),'original_up_prefix':819,'original_down_prefix':1530,'scope':'Original full arithmetic generators/seeds/guards preserved for first819up/1530down cases. Additional null-unlocked variants and both evaluation modes for full original up corpus; fixed down p1reuse-zero matrix. Three actual changed kernel entries tested. All nonnull cases keep original CudaSlice argument delegate; null candidate uses exact frozen E106LockArg code, baseline alwaysnonnull. Original source/math/discount/value/role/menu/tail generators intact. Actual seeded inputs and post-kernel immutable snapshots, whole mutable output arrays and every unowned guard retained.','source_relationship':'Copied exact sealed resource PTX, no runtime NVRTC or host/shader optimization edits. Only standalone harness case loader/argument wrapper/extra kernel mode/descriptor labels and guard ownership extension. Helper source bytes copied from frozen candidate. Historical magic labels replaced with new explicit formats. Native per-case checks plus independent whole retained reader required.','up_harness_changes':up_changes,'down_harness_changes':changes,'remaining_limits':'Direct finite corpus is not universal NaN/alias/address proof, graph/fullcanonical/empty-lock constructor/error/paging/material/capacity/complete speed qualification. Genuine numerical/guard failure closes exactE106 form without rescue; no completed case reruns for mechanical observer/reader repair.'})
deps=ROOT/'reference/accepted-e080-deps';commands={}
for name,folder in [('up',U),('down',V)]:
 cmd=['rustc',str(folder/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
 for dep,file in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',dep+'='+str(deps/file)]
 commands[name]=cmd+['-o',str(folder/'probe.exe')]
for script in ['D217-execute-direct.py','D217-audit-direct.py']:ast.parse((ROOT/'runs'/script).read_text(encoding='utf-8'))
files=[Path(__file__),ROOT/'runs/D217-execute-direct.py',ROOT/'runs/D217-audit-direct.py',ROOT/'runs/E106-engine-checkpoint/report.json',ROOT/'runs/D215-nullable-lock-CFG/report.json',R/'report.json',R/'protocol.json',ROOT/'runs/E106-source-r2/manifest.json',ROOT/'epoch/common.py',up_parent/'corpus.json',up_parent/'probe.rs',down_parent/'corpus.json',down_parent/'probe.rs']+[p for p in H.rglob('*') if p.is_file()]+[deps/'libcudarc-ba3140064b5903a3.rlib',deps/'libserde_json-83a0670a02a34a4d.rlib']
h.save(H/'protocol.json',{'id':'D217','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_DIRECT_GPU_CASES','category_order':['up','down'],'cases':{'up':len(uc),'down':len(dc)},'rustc_commands':commands,'expected_kernel_launches':2*(len(uc)+len(dc)),'required_free_bytes':84*1024**3,'raw_reservation_bytes':20*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Two serialized compilers/native direct processes/readers, up then down. Entire declared corpus retained; baseline original nonnull and candidate null/non-null. Fixed sealed shader/host source, original floating expressions. No speed samples, sourceactivation or adoption. Any genuine mismatch closes form without case/subset/entry/helper/arity/threshold/flags/quality/sample rescue. Mechanical observer/reader repairs retained without completed native case repeats.'})
for name in ['protocol.json','source-review.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D217','title':'Nullable lock direct arithmetic and exceptional values','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Frozen full retained direct corpus','reason':str(len(uc))+' training/evaluation pairs and '+str(len(dc))+' down-action pairs; null/non-null, exceptional values, modes, arbitrary menus, thread tails, reuse-zero and full guards. No speed claim.','evidence':[{'label':n,'url':'evidence/'+H.name+'/'+n} for n in ['protocol.json','source-review.json']]});s.update(updated_at=h.now(),active_experiment='D217',stage='Nullable lock direct arithmetic prerequisite',activity='E106 engine state passed. Now fixed direct whole-buffer arithmetic/exceptional/zero/generic/role/mode/guard comparisons before large canonical state and performance. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'up':len(uc),'down':len(dc),'launches':2*(len(uc)+len(dc))}),flush=True)
