import ast,json,re,shutil,sys,urllib.request,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
S=ROOT/'runs/E104-source';schema=h.read(S/'schema.json');hostreview=h.read(S/'host-source-review.json');manifest=h.read(S/'manifest.json');H=ROOT/'runs/D208-resident-host-layout';H.mkdir(exist_ok=False);(H/'gpu').mkdir()
base=(S/'baseline-mod.rs').read_text();candidate=(S/'candidate-mod.rs').read_text();methods=(S/'host-methods.rs.txt').read_text();roles=hostreview['pointer_sources']
start=base.index('    fn paired_sweep(');opening=base.index('{',start);at=opening+1;depth=1
while depth:
 if base[at]=='{':depth+=1
 elif base[at]=='}':depth-=1
 at+=1
paired=base[start:at];role_checks=[]
def normalize(x,p):
 x=re.sub(r'\s+','',x).replace('&mut','').replace('&','').replace('*','');x=x.replace('reach0','self.d_reach[0]').replace('reach1','self.d_reach[1]');x=x.replace('[1-p]','['+str(1-p)+']').replace('[p]','['+str(p)+']');return str(p) if x=='pi' else x
def actual_carg(x,p):
 if x=='(int)sp.start':return 'start'
 if x=='(int)sp.count':return 'count'
 if '?' in x:
  m=re.fullmatch(r'a\.p == 0 \? a\.(\w+) : a\.(\w+)',x);assert m;x='a.'+m[1 if p==0 else 2]
 assert x.startswith('a.');key=x[2:]
 if key in roles:return normalize(roles[key],p)
 if key=='p':return str(p)
 assert key in ['nh0','down_nh1','nh_p','nh_o','nh_max'];return key
for kernel,call in schema['helper_calls'].items():
 pattern=r'\.launch_builder\(&self\.f_'+kernel+r'\)(.*?)\.launch\(Self::cfg';m=re.findall(pattern,paired,re.S);assert len(m)==1,kernel;oldargs=re.findall(r'\.arg\(([^\n]+)\)',m[0]);assert len(oldargs)==len(call),(kernel,len(oldargs),len(call))
 for p in [0,1]:
  old=[normalize(x,p) for x in oldargs];new=[actual_carg(x,p) for x in call];assert old==new,(kernel,p,old,new)
  role_checks.append({'kernel':kernel,'p':p,'formal_names':schema['formal_names'][kernel],'original_normalized_args':old,'resident_normalized_args':new,'all_original_argument_roles_exact':True})
root_pattern=r'\.launch_builder\(&self\.f_copy_root\)(.*?)\.launch\(Self::cfg\(4, 0\)\)';oldroot=re.findall(root_pattern,paired,re.S);newroot=re.findall(root_pattern,methods,re.S);assert len(oldroot)==len(newroot)==1
for p in [0,1]:assert [normalize(x,p) for x in re.findall(r'\.arg\(([^\n]+)\)',oldroot[0])]==[normalize(x,p) for x in re.findall(r'\.arg\(([^)]+)\)',newroot[0])]
h.save(H/'role-review.json',{'id':'D208-role-review','at':h.now(),'status':'pass_all_original_host_argument_roles','all12_kernel_player_role_checks':role_checks,'identical_root_copy_roles_and_fixed4CTAlaunch':True,'all52_current_pointer_assignments':roles,'parameter_source_current_not_cached':True,'limits':'Staticrolebinding/sourceproof,notGPUdereference/FP/math/graph/lifecycleorperformanceproof.'})
prior=(ROOT/'runs/D178-canonical-cache-control/baseline/mod.rs').read_text();shim=prior[prior.index('pub mod plan {'):prior.index('\nmod arena;')]
source=candidate.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
assert source.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==candidate
source+='''
pub fn d208_layout()->serde_json::Value{
 serde_json::json!({"actual_wrapper_bytes":std::mem::size_of::<GpuSolver>(),"actual_state_bytes":std::mem::size_of::<ResidentState>(),"parameter_bytes":std::mem::size_of::<ResidentArgs>(),"parameter_alignment":std::mem::align_of::<ResidentArgs>(),"span_offset":std::mem::offset_of!(ResidentArgs,spans),"reserved_offset":std::mem::offset_of!(ResidentArgs,_reserved),"CUDA_or_constructor_calls":0})
}
'''
(H/'gpu/mod.rs').write_text(source,encoding='utf-8',newline='\n');shutil.copyfile(h.REPO/'crates/solver/src/gpu/arena.rs',H/'gpu/arena.rs');shutil.copyfile(S/'candidate-kernels.cu',H/'gpu/kernels.cu')
probe='''#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="gpu/mod.rs"]mod observed;
fn main(){
 let layout=observed::d208_layout();let baseline=std::mem::size_of::<solver::gpu::GpuSolver>();assert_eq!(baseline,4448);let actual=layout["actual_wrapper_bytes"].as_u64().unwrap() as usize;assert!(actual>=baseline&&actual-baseline<=32);assert_eq!(layout["actual_state_bytes"],24);assert_eq!(layout["parameter_bytes"],3008);assert_eq!(layout["parameter_alignment"],8);assert_eq!(layout["span_offset"],444);assert_eq!(layout["reserved_offset"],3004);
 let _=std::hint::black_box(observed::GpuSolver::new as fn(&solver::Solver)->Result<observed::GpuSolver,String>);let _=std::hint::black_box(observed::GpuSolver::iterate as fn(&mut observed::GpuSolver)->Result<(),String>);
 println!("D208_LAYOUT {}",serde_json::json!({"candidate":layout,"baseline_wrapper_bytes":baseline,"wrapper_delta_bytes":actual-baseline,"actual_constructor_CUDA_kernel_or_solver_calls":0}));
}
'''
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
execute='''import sys,json,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',1200);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe')],O,'layout',120);verify()
rows=[json.loads(x.split('D208_LAYOUT ',1)[1]) for x in (O/'layout.stdout.log').read_text().splitlines() if 'D208_LAYOUT ' in x];assert len(rows)==1;r=rows[0]
h.save(H/'report.json',{'id':'D208','at':h.now(),'status':'pass_complete_host_compile_role_bindings_and_prospective_layout','protocol_sha256':sys.argv[1],'layout':r,'role_review_sha256':h.sha(H/'role-review.json'),'baseline_host_source_sha256':h.sha(ROOT/'runs/E104-source/baseline-mod.rs'),'candidate_host_source_sha256':h.sha(ROOT/'runs/E104-source/candidate-mod.rs'),'all_owned_compiler_layout_children_terminal':True,'actual_constructor_CUDA_kernel_or_solver_calls':0,'performance_samples':0,'candidate_accepted':False,'scope':'FullcandidateRusthosttypechecked/codegeneratedofftreeandactualtypedhost/framecostlayout. Alloriginalkernel/playerargumentrolesandrootcopy staticallymatch. NoGPUconstructor/resource requery/rawCFR/dereference/numeric/lifecycle/fullsolver/speed/adoptionproof. Actualwrapperdelta wasprospectivelybounded<=32,alloriginalnumeric/device/state fieldsstillmustexact.'});h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'application_kernel_or_solver_runs':0});verify();print(json.dumps({'status':'host_compile_layout_pass','layout':r,'new_CFR_GPU_calls':0}),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
files=[Path(__file__),ROOT/'runs/E104-prepare-host.py',S/'manifest.json',S/'schema.json',S/'source-review.json',S/'host-source-review.json',S/'baseline-mod.rs',S/'candidate-mod.rs',S/'host-methods.rs.txt',ROOT/'runs/D207-resident-resource/report.json',ROOT/'runs/D207-resident-resource/protocol.json',ROOT/'runs/D207-resident-resource/execution/complete.json',ROOT/'epoch/common.py']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D208','at':h.now(),'status':'FROZEN_PRE_COMPLETE_HOST_COMPILER_AND_CPU_LAYOUT_OBSERVER','rustc_command':cmd,'required_free_bytes':64*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'OneofftreecompletehostRustcompiler/oneCPUlayoutprocess. Existingpublicplanvisibility/fullarenaadapteronly;nohostnumeric/ABI/sourceprefixexception. Actualwrappergrowth<=32Bprospectively,ResidentState24/frame3008/align8/span444/reserved3004 mustmatchbeforeanynewCFRGPUobservation. Alloriginalrolebindings/rootcopy/sourceprojection checked. NoNVRTC/CUDA/context/constructor/applicationkernel/solver orspeedcall. Allraw/lifecycle/broad/material/fullspeed/application gatesremain.'})
print(h.sha(H/'protocol.json'),flush=True)
