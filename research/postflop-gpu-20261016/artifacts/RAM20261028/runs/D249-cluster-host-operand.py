import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D249-cluster-host-operand';S=ROOT/'runs/E111-source';R=ROOT/'runs/E111-resource'

def prepare():
 h.custody();h.ar.refuse_active(h.ar.live_status());assert all(h.read(R/'report-r2.json')['gates'].values());H.mkdir(exist_ok=False)
 old=(ROOT/'runs/D244-fold-copy-canonical/baseline/mod.rs').read_bytes().decode();shim=old[old.index('pub mod plan {'):old.index('\nmod arena;')];proof={}
 for arm in ['baseline','candidate']:
  d=H/arm;d.mkdir();prod=(S/(arm+'-mod.rs')).read_bytes().decode();src=prod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
  assert src.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==prod
  (d/'mod.rs').write_bytes(src.encode());shutil.copyfile(h.REPO/'crates/solver/src/gpu/arena.rs',d/'arena.rs');shutil.copyfile(S/(arm+'-kernels.cu'),d/'kernels.cu');proof[arm]={'host_sha256':h.sha(S/(arm+'-mod.rs')),'adapted_sha256':h.sha(d/'mod.rs'),'only_existing_plan_visibility_adapter_exact_reversal':True}
 code='''#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
fn main(){let b=(std::mem::size_of::<baseline::GpuSolver>(),std::mem::align_of::<baseline::GpuSolver>());let c=(std::mem::size_of::<candidate::GpuSolver>(),std::mem::align_of::<candidate::GpuSolver>());println!("D249_HOST {}",serde_json::json!({"baseline_size":b.0,"baseline_align":b.1,"candidate_size":c.0,"candidate_align":c.1,"constructors_called":0,"CUDA_APIs_or_kernels":0}));assert_eq!(b,(4448,8));assert_eq!(b,c);}
'''
 (H/'probe.rs').write_bytes(code.encode());deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
 for n,f in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',n+'='+str(deps/f)]
 cmd+=['-o',str(H/'probe.exe')];files=[Path(__file__),S/'manifest.json',S/'source-review.json',R/'protocol.json',R/'report.json',R/'report-r2.json',R/'execution/candidate-compute_120.ptx',ROOT/'runs/D244-fold-copy-canonical/baseline/mod.rs',ROOT/'epoch/common.py']+[p for p in H.rglob('*')if p.is_file()]+[p for p in deps.iterdir()if p.is_file()]
 h.save(H/'protocol.json',{'id':'D249','at':h.now(),'status':'FROZEN_PRE_CPU_OPERAND_READER_AND_HOST_COMPILER','input_sha256':{str(p):h.sha(p)for p in files},'rustc_command':cmd,'source_projection':proof,'scope':'Static source/currentPTX local mappedoperand/copy predicate/lifetime witnesses, three actual negativefixtures and onehostcompiler/oneCPUsizeof-only child. Same originalhost source with known privateplan visibility adapter only. No CudaContext/constructors/API/kernels/solves/speed. Not a generalPTX interpreter/full CFG/FP proof.','gates':['Exact emitted peer-slot operand chain and bounds before peer load.','Identical card-copy predicate gates skip and map; card-position store targets exact local mapped offset.','Generic map rank0 output feeds all actual card-index loads before final lifetime barrier; original local scan state not mapped.','Inactive mate executes two synchronization phases then returns without any data-array read.','Original9entries unchanged and actual Rust wrapper size/alignment identical4448/8.','No source/helper/form correction after genuine failure; mechanical reader/binding errors additive, no completed scientific repeat.']})
 print(h.sha(H/'protocol.json'),flush=True)

def witness(text):
 a=text.index('.visible .entry up_show_cluster(');t=text[a:];ops=[]
 for raw in t.splitlines():
  s=raw.strip()
  if not s or s.startswith('//'):continue
  ops.append(re.sub(r'\s+',' ',s))
 def seq(lines):
  q=[re.sub(r'\s+',' ',s.strip())for s in lines.splitlines()if s.strip()];joined='\n'.join(ops);needle='\n'.join(q);assert joined.count(needle)==1,needle;return joined.index(needle)
 inactive=seq('''mov.u32 %r1, %ctaid.x;
setp.lt.s32 %p4, %r1, %r88;
@%p4 bra $L__BB9_2;
barrier.cluster.arrive.aligned;
barrier.cluster.wait.aligned;
barrier.cluster.arrive.aligned;
barrier.cluster.wait.aligned;
bra.uni $L__BB9_75;''')
 peer=seq('''xor.b32 %r3, %r1, 1;
setp.ge.u32 %p6, %r3, %r88;
mov.pred %p116, 0;
@%p6 bra $L__BB9_4;
add.s32 %r94, %r87, %r3;
mul.wide.s32 %rd53, %r94, 4;
add.s64 %rd54, %rd3, %rd53;
ld.global.nc.u32 %r95, [%rd54];
mul.wide.u32 %rd55, %r95, 4;
add.s64 %rd56, %rd2, %rd55;
ld.global.nc.u32 %r96, [%rd56];
setp.eq.s32 %p116, %r96, %r2;''')
 bindings=['ld.param.u64 %rd46, [up_show_cluster_param_0];','ld.param.u32 %r87, [up_show_cluster_param_1];','ld.param.u32 %r88, [up_show_cluster_param_2];','ld.param.u64 %rd47, [up_show_cluster_param_6];','ld.param.u32 %r90, [up_show_cluster_param_25];','cvta.to.global.u64 %rd2, %rd47;','cvta.to.global.u64 %rd3, %rd46;','ld.param.u64 %rd294, [up_show_cluster_param_15];','ld.param.u64 %rd297, [up_show_cluster_param_18];']
 for s in bindings:assert s in ops,s
 own=seq('''add.s32 %r92, %r87, %r1;
mul.wide.s32 %rd49, %r92, 4;
add.s64 %rd50, %rd3, %rd49;
ld.global.nc.u32 %r93, [%rd50];
cvt.u64.u32 %rd4, %r93;
mul.wide.u32 %rd51, %r93, 4;
add.s64 %rd52, %rd2, %rd51;
ld.global.nc.u32 %r2, [%rd52];''')
 count=seq('''cvta.to.global.u64 %rd57, %rd294;
mul.wide.s32 %rd58, %r2, 4;
add.s64 %rd59, %rd57, %rd58;
ld.global.nc.u32 %r4, [%rd59];''')
 skip=seq('''and.b32 %r99, %r1, 1;
setp.eq.b32 %p9, %r99, 1;
and.pred %p3, %p9, %p116;
@%p3 bra $L__BB9_11;''')
 fill=seq('''$L__BB9_10:
add.s32 %r100, %r237, %r6;
mul.wide.u32 %rd76, %r100, 4;
add.s64 %rd77, %rd12, %rd76;
ld.global.nc.u32 %r101, [%rd77];
mul.wide.s32 %rd80, %r237, 4;
add.s64 %rd81, %rd79, %rd80;
st.shared.u32 [%rd81], %r101;
add.s32 %r237, %r237, %r12;
setp.lt.s32 %p11, %r237, %r11;
@%p11 bra $L__BB9_10;''')
 seq('''add.s32 %r97, %r4, %r90;
mul.wide.s32 %rd7, %r97, 4;''')
 seq('''mov.u64 %rd75, shraw;
add.s64 %rd11, %rd75, %rd7;''')
 seq('''cvta.to.global.u64 %rd12, %rd297;
mul.wide.s32 %rd78, %r4, 4;
add.s64 %rd79, %rd11, %rd78;''')
 mapping=seq('''$L__BB9_11:
cvta.shared.u64 %rd83, %rd75;
add.s64 %rd84, %rd83, %rd7;
mul.wide.s32 %rd85, %r4, 4;
add.s64 %rd302, %rd84, %rd85;
barrier.cluster.arrive.aligned;
barrier.cluster.wait.aligned;
not.pred %p12, %p3;
@%p12 bra $L__BB9_13;
mov.b32 %r102, 0;
mapa.u64 %rd302, %rd302, %r102;
$L__BB9_13:''')
 tail=seq('''$L__BB9_74:
barrier.cluster.arrive.aligned;
barrier.cluster.wait.aligned;
$L__BB9_75:
ret;''')
 reads=[]
 for i,s in enumerate(ops):
  m=re.fullmatch(r'add.s64 (%rd\d+), %rd302, %rd\d+;',s)
  if m:
   addr=m[1];assert i+1<len(ops);ld=ops[i+1];assert re.fullmatch(r'ld.u32 %r\d+, \['+re.escape(addr)+r'\];',ld),(s,ld);reads.append([s,ld])
 assert len(reads)==30
 definitions=[s for s in ops if re.match(r'\w[\w.]* %rd302[,;]',s)];assert definitions==['add.s64 %rd302, %rd84, %rd85;','mapa.u64 %rd302, %rd302, %r102;']
 assert inactive<own<peer<count<skip<fill<mapping<tail
 return {'matched_copy_and_map_share_same_predicate':True,'all_generic_card_position_load_sites':len(reads),'mapped_pointer_definitions':definitions,'read_sites':reads,'bounds_before_peer_data_read':True,'inactive_two_phase_lifetime_path':True,'card_buffer_offset_bytes':'4*nh_o + 8*m_o, identical in producer and consumer when same slot','local_scan_or_reach_buffers_mapped':False,'limits':'Exact current emitted local operand/branch witnesses plus source projection, not complete CFG/loop/IEEE/native liveness or runtime proof.'}

def execute(identity):
 h.pin(H/'protocol.json',identity);P=h.read(H/'protocol.json')
 for p,d in P['input_sha256'].items():h.pin(p,d)
 t=(R/'execution/candidate-compute_120.ptx').read_text();result=witness(t)
 for name,bad in [('wrong_rank',t.replace('mov.b32 \t%r102, 0;','mov.b32 \t%r102, 1;')),('wrong_copy_predicate',t.replace('and.pred  \t%p3, %p9, %p116;','or.pred  \t%p3, %p9, %p116;')),('missing_lifetime_barrier',t.replace('$L__BB9_74:\n\t// begin inline asm\n\tbarrier.cluster.arrive.aligned;','$L__BB9_74:\n\t// begin inline asm\n\t// removed lifetime arrive;'))]:
  assert bad!=t,name
  try:witness(bad)
  except AssertionError:pass
  else:raise AssertionError('missed '+name)
 h.save(H/'operand-report.json',{'id':'D249-operand','at':h.now(),'protocol_sha256':identity,'result':result,'three_negative_fixtures_caught':True,'new_GPU_or_speed_samples':0})
 O=H/'execution';O.mkdir(exist_ok=False)
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.custody();h.ar.refuse_active(h.ar.live_status());h.child(P['rustc_command'],O,'rustc',600);h.child([str(H/'probe.exe')],O,'host-size',120);h.custody()
 rows=[json.loads(x.split('D249_HOST ',1)[1])for x in(O/'host-size.stdout.log').read_text().splitlines()if'D249_HOST 'in x];assert len(rows)==1 and rows[0]['baseline_size']==rows[0]['candidate_size']==4448 and rows[0]['baseline_align']==rows[0]['candidate_align']==8
 h.save(H/'report.json',{'id':'D249','at':h.now(),'status':'pass_scoped_mapped_operand_and_actual_host_layout','protocol_sha256':identity,'operand_report_sha256':h.sha(H/'operand-report.json'),'actual_compiled_host_layout':rows[0],'host_binary_sha256':h.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_GPU_kernel_launches_solver_or_speed_samples':0,'limits':P['scope'],'source_live_unchanged':True})
 for name in ['protocol.json','operand-report.json','report.json']:
  p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
 with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
  s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D249','title':'Metadata-sharing operands and actual host layout','kind':'diagnostic','status':'measured','accepted':False,'measurement_epoch':'RAM20261028','stage':'Mapped operand and compiled wrapper controls pass','reason':'Same slot/odd predicate gates omittedcopy and rank0mapping;30actual generic cardloadsites use mappedpointer. Publication/lifetime andinactive tailpaths bound,3negativefixtures caught. ActualbothRustwrappers4448B/align8, noCUDA constructors/APIs orspeed.','evidence':[{'label':n,'url':'evidence/'+H.name+'/'+n}for n in ['protocol.json','operand-report.json','report.json']]});e=next(x for x in s['experiments']if x['id']=='E111');e.update(stage='Resource/ABI/operand/host layout pass; solver raw controls pending',reason='Metadata-sharing prototype compiled; all9originalentrybodies/resources preserved, newcluster40regs/local0/static1040/dynamic26520/stack1024,positiveactualclusters. Hostwrapper4448unchanged; source/runtime/whole-state/exactness/material/speed gates remain.');e['evidence'].append({'label':'Mapped operands and actual host layout','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E111',stage=e['stage'],activity=e['reason']+' E080 remains live, no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
 print('D249 operand and actual host layout passed',flush=True)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:execute(sys.argv[2])
