import ast,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D254-constant-host-operand';S=ROOT/'runs/E112-source';R=ROOT/'runs/E112-resource'
def witness(t):
 ops=[re.sub(r'\s+',' ',l.strip())for l in t.splitlines()if l.strip()and not l.strip().startswith('//')];loads={}
 for op in ops:
  m=re.fullmatch(r'ld.const.f32 (%f\d+), \[gto_postflop_discounts(?:\+(\d+))?\];',op)
  if m:assert m[1]not in loads;loads[m[1]]=int(m[2]or 0)
 assert len(loads)==12 and sorted(loads.values())==[0]*4+[4]*4+[8]*4
 evidence=[]
 for reg,offset in loads.items():
  definitions=[x for x in ops if re.match(r'\w[\w.]* '+re.escape(reg)+r'[,;]',x)];assert len(definitions)==1 and definitions[0].startswith('ld.const.f32 ')
  uses=[x for x in ops if reg in re.findall(r'%f\d+',x)and x!=definitions[0]];assert uses
  for use in uses:
   if offset in[0,4]:
    m=re.fullmatch(r'selp.f32 (%f\d+), (%f\d+), (%f\d+), %p\d+;',use);assert m,use;assert loads.get(m[2])==0 and loads.get(m[3])==4
   else:
    assert re.fullmatch(r'mul.f32 %f\d+, %f\d+, %f\d+;',use),use
  evidence.append({'constant_offset_bytes':offset,'producer_register':reg,'single_definition':definitions[0],'direct_arithmetic_consumers':uses})
 assert not re.search(r'ld.param.u64\s+%rd\d+, \[up_action_param_17\]',t)
 return evidence
def caller(t):
 a=t.index('.launch_builder(&self.f_up_action)');b=t.index('.map_err(e)?;',a);return re.findall(r'\.arg\(([^\n]*)\)',t[a:b])
if sys.argv[1]=='prepare':
 h.custody();h.ar.refuse_active(h.ar.live_status());assert all(h.read(R/'report-r2.json')['gates'].values());H.mkdir(exist_ok=False)
 parent=ROOT/'runs/D249-cluster-host-operand';old=(parent/'baseline/mod.rs').read_bytes().decode();shim=old[old.index('pub mod plan {'):old.index('\nmod arena;')];projection={}
 for arm in['baseline','candidate']:
  d=H/arm;d.mkdir();prod=(S/(arm+'-mod.rs')).read_bytes().decode();src=prod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
  gate='#[cfg(feature = "preflop-research")]\nmod continuation_capacity;';assert src.count(gate)==1;src=src.replace(gate,'mod continuation_capacity;',1)
  assert src.replace('mod continuation_capacity;',gate,1).replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==prod
  (d/'mod.rs').write_bytes(src.encode());shutil.copyfile(h.REPO/'crates/solver/src/gpu/arena.rs',d/'arena.rs');shutil.copyfile(S/(arm+'-kernels.cu'),d/'kernels.cu');shutil.copyfile(S/(arm+'-continuation_capacity.rs'),d/'continuation_capacity.rs');projection[arm]={'frozen_host_sha256':h.sha(S/(arm+'-mod.rs')),'adapted_sha256':h.sha(d/'mod.rs'),'only_known_plan_and_capacity_cfg_adapters_reverse_exact':True}
 code='''#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
fn main(){let b=(std::mem::size_of::<baseline::GpuSolver>(),std::mem::align_of::<baseline::GpuSolver>());let c=(std::mem::size_of::<candidate::GpuSolver>(),std::mem::align_of::<candidate::GpuSolver>());println!("D254_HOST {}",serde_json::json!({"baseline_size":b.0,"baseline_align":b.1,"candidate_size":c.0,"candidate_align":c.1,"constructors_called":0,"CUDA_APIs_or_kernels":0,"capacity_modules_typechecked":true}));assert_eq!(b,(4448,8));assert!(c.0<=b.0);assert_eq!(b.1,c.1);}
''';(H/'probe.rs').write_bytes(code.encode());oldp=h.read(parent/'protocol.json');cmd=[x.replace(str(parent),str(H))for x in oldp['rustc_command']]
 files=[Path(__file__),ROOT/'epoch/common.py',S/'manifest.json',S/'source-review.json',R/'report-r2.json',R/'execution/candidate-compute_120-up_action.ptx.txt',R/'execution/candidate-compute_75-up_action.ptx.txt',parent/'baseline/mod.rs']+[p for p in H.rglob('*')if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
 h.save(H/'protocol.json',{'id':'D254','at':h.now(),'status':'FROZEN_PRE_CPU_OPERAND_READER_AND_HOST_COMPILER','rustc_command':cmd,'input_sha256':{str(p):h.sha(p)for p in files},'source_projection':projection,'gates':['Twelve actual constantf32loads pertarget, offsets0/4/8fourtimes, eachsingledefinition andconsumed; pos/neg feedoriginalselp roles, strategy feedsmultiply. No reintroduced64bit pointer read atnewintegerordinal17.','Hosttrainingcaller20to19exact removaloforiginaldiscargument17,others unchanged.','AllrealRusthost andbothactualcapacitymodules typecheck afterknownplanvisibility/cfgadapters; originalsizeof4448/8,candidatenolarger/samealignment.','Wrongconstantoffset,wrongmemoryspace andunconsumedproduceractualnegativefixtures.'],'scope':'Staticlocalcompiledproducer/directconsumer andsourcecaller witnesses plusoneRustcompiler/oneCPUsizeof-onlyprocess. Not fullCFG/FPDAG/nativeCFR/IEEE/liveness/actualcapacity/processpeak/performance proof. Constructor size12query wasreal inresourceprocess, but fullrealhostconstructor/allpayload/raw/F32/graph/lifecycle/multisession/fallback tests remain beforeperformance. No CUDA APIs/constructors from sizeofprocess.','failure':'Genuine mechanism/caller/host/lifetime/resource failure closes fixedE112form withoutsource/helper/width/flags/sample rescue. Mechanical observer/binding errors additive, completednativecases not repeated.'})
 print(h.sha(H/'protocol.json'),flush=True)
else:
 h.pin(H/'protocol.json',sys.argv[2]);P=h.read(H/'protocol.json')
 for p,d in P['input_sha256'].items():h.pin(p,d)
 proof={}
 for arch in['120','75']:
  t=(R/'execution'/('candidate-compute_'+arch+'-up_action.ptx.txt')).read_text(encoding='utf-8');proof[arch]=witness(t)
  # Each mutation changes actual retained text; no shader/compiler/kernel repeat.
  offset=re.search(r'ld.const.f32\s+%f\d+, \[gto_postflop_discounts\];',t);assert offset;bad_offset=t[:offset.start()]+offset[0].replace('gto_postflop_discounts]','gto_postflop_discounts+12]')+t[offset.end():]
  bad_space=t.replace('ld.const.f32','ld.global.nc.f32',1);reg=re.search(r'ld.const.f32\s+(%f\d+),',t);assert reg;bad_dead=t[:reg.start(1)]+'%f999999'+t[reg.end(1):]
  for bad in[bad_offset,bad_space,bad_dead]:
   assert bad!=t
   try:witness(bad)
   except AssertionError:pass
   else:raise AssertionError('missed constant producer negative fixture')
 b,c=caller((S/'baseline-mod.rs').read_bytes().decode()),caller((S/'candidate-mod.rs').read_bytes().decode());assert len(b)==20 and len(c)==19 and b[17]=='&self.d_disc'and b[:17]+b[18:]==c
 h.save(H/'operand-report.json',{'id':'D254-operand','at':h.now(),'protocol_sha256':sys.argv[2],'actual_compiled_constant_operands':proof,'source_training_caller_old_args':b,'source_training_caller_new_args':c,'three_negative_fixtures_caught_each_architecture':True,'limits':P['scope']});O=H/'execution';O.mkdir(exist_ok=False)
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.custody();h.ar.refuse_active(h.ar.live_status());h.child(P['rustc_command'],O,'rustc',600);h.child([str(H/'probe.exe')],O,'host-size',120);h.custody()
 rows=[json.loads(x.split('D254_HOST ',1)[1])for x in(O/'host-size.stdout.log').read_text(encoding='utf-8').splitlines()if'D254_HOST 'in x];assert len(rows)==1 and rows[0]['baseline_size']==4448 and rows[0]['candidate_size']<=4448 and rows[0]['baseline_align']==rows[0]['candidate_align']==8
 h.save(H/'report.json',{'id':'D254','at':h.now(),'status':'pass_scoped_constant_operand_caller_and_actual_host_layout','protocol_sha256':sys.argv[2],'operand_report_sha256':h.sha(H/'operand-report.json'),'actual_compiled_host_layout':rows[0],'host_binary_sha256':h.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_GPU_kernel_launches_solver_or_speed_samples':0,'source_and_live_unchanged':True,'limits':P['scope']})
 for name in['protocol.json','operand-report.json','report.json']:
  p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
 with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
  s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D254','title':'Constant operand, caller and host layout controls','kind':'diagnostic','status':'measured','accepted':False,'measurement_epoch':'RAM20261028','stage':'Compiled constant roles and actual host layout passed','reason':'Both targets have12constantf32loads at0/4/8feeding originalselect/multiply roles;3negativefixtures each. Sourcecaller removes onlypointerarg17. Actualhost/capacitymodules typechecked andwrappermeasured; no CUDA constructors or solver/speed.','evidence':[{'label':n,'url':'evidence/'+H.name+'/'+n}for n in['protocol.json','operand-report.json','report.json']]});e=next(x for x in s['experiments']if x['id']=='E112');e.update(stage='Resource/ABI/operand/caller/host pass; numerical controls pending',reason='Constant transport and static/host prerequisites passed. Realconstructor accounting, fullCFR/raw state, graphs, lifecycle andallordinary/performance/material qualification remain. E080 remains live.');e['evidence'].append({'label':'Operand/caller/actual host report','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E112',stage=e['stage'],activity=e['reason']);h.ar.atomic_json(h.ar.STATUS,s)
 print('D254 constant operands, source caller and actual host layout passed',flush=True)
