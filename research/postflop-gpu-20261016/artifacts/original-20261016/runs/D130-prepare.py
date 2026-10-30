"""Freeze plan-budget/CUDA-context overlap as one distinct component hypothesis."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D130-plan-context-overlap';assert not H.exists();H.mkdir();A=R/'runs/D092-action-arity-order';F=R/'runs/E077-plan-control';schema=old.read(A/'field-schema.json')['fields'];assert len(schema)==53
history=subprocess.run(['git','log','--all','--format=%H','-G','spawn_scoped|spawn.*CudaContext|context.*join|join.*context|context_worker|plan_and_context','--','crates/solver/src/gpu'],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
old.save(H/'source-api-review.json',{'at':old.now(),'history_query':history.args,'all_ref_matches':history.stdout.splitlines(),'mechanism':'The original serial GpuPlan build and compressed budget arithmetic run on the caller while one scoped worker creates the same CUDA primary-context owner and stream. Join before returning or consuming the result. No context cache/lifetime extension, plan stage parallelism, NVRTC overlap, memory hint, kernel/math/quality/storage/layout changes.','eligibility':'Fixed original tree.nodes.len>=65536; smaller trees run original serial path. This threshold is fixed before first compiler/native/component data and cannot be adjusted after failure.','failure_contract':'Budget/plan error retains priority over worker CUDA error/panic. Every spawned worker joined, results dropped before error returns. For admitted plan, original GPU error propagates or panic resumes on caller. Failed OS spawn falls back to serial CUDA creation after successful plan. No unjoined/detached task. Extra speculative context work on budget rejection and warm server setup still need material checks before adoption.','primary_sources':{'CUDA_primary':'https://docs.nvidia.com/cuda/archive/12.9.2/cuda-driver-api/group__CUDA__PRIMARY__CTX.html','CUDA_binding':'https://docs.nvidia.com/cuda/archive/12.9.2/cuda-driver-api/group__CUDA__CTX.html','Rust_scoped_builder':'https://doc.rust-lang.org/std/thread/struct.Builder.html','Rust_join':'https://doc.rust-lang.org/std/thread/struct.ScopedJoinHandle.html','process_CPU':'https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes'},'local_api':'Pinned cudarc0.19.7 has Send+Sync for context/stream, bind_to_thread uses driver current-thread binding; new retains primary context, new_stream binds context. Returned context rebound to caller inside both component clocks. No driver configuration/reset/limit change.','counterevidence':'D041: server VRAM query already retains a context, so fresh-process savings are not a universal server gain. D088 stages only motivate the test, not native headroom bound. D109 module caching is closed. D116/E071 parallel CPU plan stages, D126 memory hint, D127 sparse page reads and E078 parent-fold fusion stay closed. No failed mechanism composed or rescued.'})
for i in range(3):shutil.copyfile(A/f'fixture-{i}.json',H/f'fixture-{i}.json')
oldprobe=(F/'probe.rs').read_text(encoding='utf-8');enc=oldprobe[oldprobe.index('trait Encode'):oldprobe.index('fn main')];enc=enc.replace('accepted::LevelSpan','LevelSpan');enc='\n'.join(line for line in enc.splitlines()if 'impl Encode for candidate::LevelSpan'not in line)+'\n'
fields='\n'.join(f'    f.write_all(&({i}u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.{x["name"]}));dump(&mut f,&words(&plan.{x["name"]}));'for i,x in enumerate(schema))
probe=r'''#![allow(dead_code)]
use solver::{Solver,Spot,SpotConfig,store::Storage,gpu::plan::{GpuPlan,LevelSpan}};
use cudarc::driver::{CudaContext,CudaStream};
use std::{ffi::c_void,fs::{File,OpenOptions},io::{self,BufWriter,Write},path::Path,sync::{Arc,atomic::{AtomicUsize,Ordering}},time::Instant};
use serde_json::{json,Value};
ENCODE
#[repr(C)]#[derive(Default)]struct FileTime{low:u32,high:u32}
#[repr(C)]#[derive(Default)]struct MemoryCounters{cb:u32,faults:u32,peak_ws:usize,ws:usize,quota_peak_paged:usize,quota_paged:usize,quota_peak_nonpaged:usize,quota_nonpaged:usize,commit:usize,peak_commit:usize}
#[link(name="kernel32")]extern "system"{fn GetCurrentProcess()->*mut c_void;fn GetProcessTimes(p:*mut c_void,c:*mut FileTime,e:*mut FileTime,k:*mut FileTime,u:*mut FileTime)->i32;fn K32GetProcessMemoryInfo(p:*mut c_void,c:*mut MemoryCounters,n:u32)->i32;}
fn cpu_ticks()->u64{let(mut c,mut e,mut k,mut u)=(FileTime::default(),FileTime::default(),FileTime::default(),FileTime::default());assert_ne!(unsafe{GetProcessTimes(GetCurrentProcess(),&mut c,&mut e,&mut k,&mut u)},0);let cvt=|t:FileTime|((t.high as u64)<<32)|t.low as u64;cvt(k)+cvt(u)}
fn counters()->MemoryCounters{let mut m=MemoryCounters::default();m.cb=std::mem::size_of::<MemoryCounters>()as u32;assert_eq!(m.cb,72);assert_ne!(unsafe{K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,m.cb)},0);m}
fn mem(m:&MemoryCounters)->Value{json!({"faults":m.faults,"working_set_bytes":m.ws,"peak_working_set_bytes":m.peak_ws,"commit_bytes":m.commit,"peak_commit_bytes":m.peak_commit})}
fn emit(v:Value){let mut out=io::stdout().lock();writeln!(out,"D130 {v}").unwrap();out.flush().unwrap();}
fn coordinate<P,G:Send,F:FnOnce()->Result<P,String>,C:Fn()->Result<G,String>+Sync>(eligible:bool,plan:F,create:C)->Result<(P,G),String>{
 if !eligible{let p=plan()?;return Ok((p,create()?));}
 std::thread::scope(|scope|{
  let worker=std::thread::Builder::new().name("gtopen-cuda-init".into()).spawn_scoped(scope,||create());
  let p=plan();let result=worker.ok().map(|h|h.join());
  let p=p?;
  let gpu=match result{Some(Ok(v))=>v?,Some(Err(payload))=>std::panic::resume_unwind(payload),None=>create()?};
  Ok((p,gpu))
 })
}
fn plan_budget(s:&Solver,budget:u64)->Result<GpuPlan,String>{
 assert_eq!(s.storage,Storage::Compressed);
 let plan=GpuPlan::build(&s.spot,s.use_isomorphism);
 let arena_bytes=(plan.arena_elements[0]+plan.arena_elements[1])as u64*8;
 let needed=plan.staging_bytes()+arena_bytes+512*1024*1024;
 if needed>budget{return Err(format!("spot needs ~{:.0} MB VRAM (budget {:.0} MB)",needed as f64/1e6,budget as f64/1e6));}
 Ok(plan)
}
fn create_gpu()->Result<(Arc<CudaContext>,Arc<CudaStream>),String>{let ctx=CudaContext::new(0).map_err(|e|format!("{e:?}"))?;let stream=ctx.new_stream().map_err(|e|format!("{e:?}"))?;unsafe{ctx.disable_event_tracking();}Ok((ctx,stream))}
struct Mock(Arc<AtomicUsize>);impl Drop for Mock{fn drop(&mut self){self.0.fetch_add(1,Ordering::SeqCst);}}
fn ability(){
 assert_eq!(std::mem::size_of::<FileTime>(),8);assert_eq!(std::mem::size_of::<MemoryCounters>(),72);let before=cpu_ticks();let _=counters();let mut controls=0;
 for eligible in[false,true]{for planmode in[0,1,2]{for gpumode in[0,1,2]{
  let creates=Arc::new(AtomicUsize::new(0));let drops=Arc::new(AtomicUsize::new(0));let c=creates.clone();let d=drops.clone();
  let outcome=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||coordinate(eligible,||match planmode{0=>Ok(7usize),1=>Err("budget".to_string()),_=>panic!("plan mock")},||{c.fetch_add(1,Ordering::SeqCst);match gpumode{0=>Ok(Mock(d.clone())),1=>Err("cuda mock".to_string()),_=>panic!("cuda mock")}})));
  let expected_creates=if eligible||planmode==0{1}else{0};assert_eq!(creates.load(Ordering::SeqCst),expected_creates);
  match(planmode,gpumode,outcome){(1,_,Ok(Err(e)))=>assert_eq!(e,"budget"),(2,_,Err(_))=>{},(0,0,Ok(Ok((p,g))))=>{assert_eq!(p,7);drop(g);},(0,1,Ok(Err(e)))=>assert_eq!(e,"cuda mock"),(0,2,Err(_))=>{},_=>panic!("incorrect coordinator outcome")}
  assert_eq!(drops.load(Ordering::SeqCst),if gpumode==0{expected_creates}else{0});controls+=1;
 }}}
 assert!(cpu_ticks()>=before);emit(json!({"stage":"ability","controls":controls,"plan_budget_error_priority_pass":true,"successful_and_error_and_panic_worker_cleanup_pass":true,"mock_resources_dropped":true,"CUDA_context_or_application_kernel_executions":0,"CPU_counter_ABI_pass":true}));
}
fn write_plan(path:&Path,case:u32,plan:&GpuPlan,s:&Solver){let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());f.write_all(b"D130-PLAN-RAW1\0\0").unwrap();f.write_all(&case.to_le_bytes()).unwrap();f.write_all(&(53u32).to_le_bytes()).unwrap();f.write_all(&(std::mem::size_of::<GpuPlan>()as u64).to_le_bytes()).unwrap();
FIELDS
 let kinds:Vec<u8>=s.spot.tree.nodes.iter().map(|n|n.kind).collect();dump(&mut f,&words(&kinds));dump(&mut f,&words(&s.spot.tree.children));f.flush().unwrap();f.get_ref().sync_all().unwrap();}
fn run(arm:&str,out:&Path){std::fs::create_dir(out).unwrap();let configs=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];
 for(i,config)in configs.iter().enumerate(){let cfg:SpotConfig=serde_json::from_str(config).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=true;let n=s.spot.tree.nodes.len();let eligible=arm=="overlap"&&n>=65536;
  let mb=counters();let cb=cpu_ticks();let clock=Instant::now();let(plan,(ctx,stream))=coordinate(eligible,||plan_budget(&s,u64::MAX),create_gpu).unwrap();ctx.bind_to_thread().unwrap();let elapsed=clock.elapsed().as_secs_f64()*1000.0;let ca=cpu_ticks();let ma=counters();assert!(ca>=cb);assert_eq!(ctx.compute_capability().unwrap(),(12,0));assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");stream.synchronize().unwrap();
  let case=[2u32,6,10][i];let raw=out.join(format!("fixture-{i}.bin"));write_plan(&raw,case,&plan,&s);
  emit(json!({"stage":"plan_context_component","fixture_index":i,"reference_case":case,"arm":arm,"board":s.spot.config.board,"nodes":n,"overlap_eligible":eligible,"component_ms":elapsed,"process_CPU_ms":(ca-cb)as f64/10000.0,"cpu_before_ticks100ns":cb,"cpu_after_ticks100ns":ca,"before":mem(&mb),"after":mem(&ma),"raw_plan":raw,"CUDA_context_and_stream_pairs":1,"application_kernel_launches":0,"GPU_solver_executions":0,"performance_is_full_solve":false}));
  drop(stream);drop(ctx);drop(plan);drop(s);
 }
 emit(json!({"stage":"complete","arm":arm,"fixtures":3,"application_kernel_launches":0,"GPU_solver_executions":0,"performance_is_full_solve":false}));}
fn main(){let args:Vec<_>=std::env::args().collect();match args.get(1).map(String::as_str){Some("ability")=>{assert_eq!(args.len(),2);ability();},Some("baseline")|Some("overlap")=>{assert_eq!(args.len(),3);run(&args[1],Path::new(&args[2]));},_=>panic!("invalid mode")}}
''';assert probe.count('ENCODE')==probe.count('FIELDS')==1;probe=probe.replace('ENCODE',enc).replace('FIELDS',fields);(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
P0=old.read(R/'runs/D123-node-array-initialization/protocol.json');command=[x.replace(str(R/'runs/D123-node-array-initialization'),str(H)).replace('d123_plan_probe','d130_plan_context_probe')for x in P0['compile_commands']['rustc']];at=command.index('-L');dep=R/'build-e051-final-primary/release/deps/libcudarc-ba3140064b5903a3.rlib';command[at:at]=['--extern','cudarc='+str(dep)]
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in['.rlib','.rmeta','.lib','.dll']};deps[str(dep)]=old.sha(dep)
for p,h in deps.items():old.pin(p,h)
AR=old.read(A/'report.json');references=[{'case':i,'path':str(A/'execution'/f'case-{i:02d}.bin'),'sha256':AR['cases'][i]['raw_sha256']}for i in[2,6,10]]
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],A/'report.json',A/'field-schema.json',old.REPO/'crates/solver/src/gpu/mod.rs',old.REPO/'crates/solver/src/gpu/plan.rs',R/'runs/E078-initial-closure/decision.json',R/'runs/D088-cohort/report-r2.json',C/'common_e051_live.py',C/'protected-main.json',Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\driver\safe\core.rs')]
P={'id':'D130','at':old.now(),'status':'FROZEN_PRE_COMPILER_COMPONENT','input_sha256':deps|{str(p):old.sha(p)for p in paths},'rustc_command':command,'references':references,'order':[{'id':'D130B1','arm':'baseline'},{'id':'D130T1','arm':'overlap'},{'id':'D130T2','arm':'overlap'},{'id':'D130B2','arm':'baseline'},{'id':'D130B3','arm':'baseline'},{'id':'D130T3','arm':'overlap'}],'screen':{'minimum_sum_fixture_median_saving_ms':95.825124,'minimum_original_nodes':65536,'maximum_CPU_median_ratio':1.10,'CPU_median_allowance_ms':5.0,'applicable_wall_guard':'Positive median saving and at least2/3 improving pairs for eligiblelargefixtures. Tinyserialfallback retained; laterstrictfullcyclefixtureguard unchanged.','meaning':'1%ofpreserved9582.5124msE051suite is prospectivecomponentbudget only,nohistoricalpooling/headroom/speed/no-tradeoffclaim.'},'scope':'Onecompiler,oneCPU-only18mockerror/lifecycle+counterabilityprocess.Thenexactly6freshprocessesBC/CB/BC,each3originalcompressedfixturesandonecontext/streamperfixture. OriginalserialCPUplan+budget vsconcurrentoriginalCPUplan+GPUcontext/stream,rootbindbothinsideclock;all53fullactualmetadata/capacities/struct/kind/childwords comparedoutsideclocktoacceptedD092. NoNVRTC/module/pinned/devicearrays/applicationkernels/fullsolves. Oneworkerfixed65536nodeeligibility, no stages/Rayonvariants. Stopfirstability/native/invariant failure,nosample/source/thread/threshold/placement/helper/scope rescueafteractualfailedcomponent.','limits':'SpeculativeCUDAworkonbudgetfailureandwarmservercontextcoststillneedfuturematerial/compatibilitycontrols. ServerVRAMqueryalreadyretainscontext;freshprocesscomponentgainisnotuniversalservergain. SourceGPUlifetimeunchanged,butcross-threadbinding/error/capacity/actualGPUstreamintegratednumericsnotproven. Fullstate/F32/menu/save/resume/continuation/material/fullcycle1%/strictfixture/fresh16/holdout/freshoriginalcumulative remain.','candidate_accepted':False};old.save(H/'protocol.json',P)
for p in H.iterdir():
 if p.is_file():
  key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'all_prepared_artifacts_HTTP_byte_verified':True,'compiler_native_or_CUDA_context_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D130'for x in s['experiments']);s['experiments'].append({'id':'D130','at':old.now(),'title':'Overlap CPU plan construction with CUDA context creation','kind':'diagnostic','status':'running','correctness':'Frozen error/lifecycle mocks and full metadata comparisons','fixture':'Six fresh component processes, three compressed fixtures each','stage':'Plan/context component feasibility','reason':'Test one independent setup overlap with fixed large-tree eligibility and serial small-tree path. No context caching/lifetime extension or changed plan algorithm. Measure wall and all-thread CPU costs; compare full plan metadata. No full-solve speed claim.','accepted':False,'evidence':[{'label':'Frozen component and lifecycle protocol','url':'evidence/D130-plan-context-overlap/protocol.json'},{'label':'Source/API contract and existing counterevidence','url':'evidence/D130-plan-context-overlap/source-api-review.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D130',stage='D130 plan/context overlap component screen',activity='E078 closed on full-solve slowdown. Test a distinct overlap of unchanged CPU planning and CUDA context creation, with error/cleanup controls, full metadata equality, and CPU cost limits. Accepted/live E051 gain remains 12.44%.');old.ar.atomic_json(old.ar.STATUS,s)
print('D130preparationprotocol',old.sha(H/'protocol.json'),flush=True)
