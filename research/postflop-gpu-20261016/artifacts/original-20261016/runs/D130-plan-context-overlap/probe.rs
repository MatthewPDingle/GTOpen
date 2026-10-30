#![allow(dead_code)]
use solver::{Solver,Spot,SpotConfig,store::Storage,gpu::plan::{GpuPlan,LevelSpan}};
use cudarc::driver::{CudaContext,CudaStream};
use std::{ffi::c_void,fs::{File,OpenOptions},io::{self,BufWriter,Write},path::Path,sync::{Arc,atomic::{AtomicUsize,Ordering}},time::Instant};
use serde_json::{json,Value};
trait Encode {fn encode(&self,v:&mut Vec<u64>);fn caps(&self,_v:&mut Vec<u64>) {}}
macro_rules! prim {($($t:ty),*)=>{$(impl Encode for $t {fn encode(&self,v:&mut Vec<u64>){v.push(*self as u64);}})*};}
prim!(usize,u64,u32,i32,u8,bool);
impl Encode for f32 {fn encode(&self,v:&mut Vec<u64>){v.push(self.to_bits() as u64);}}
impl<T:Encode> Encode for Vec<T>{fn encode(&self,v:&mut Vec<u64>){v.push(self.len() as u64);for x in self{x.encode(v);}}fn caps(&self,v:&mut Vec<u64>){v.push(self.capacity() as u64);for x in self{x.caps(v);}}}
impl<T:Encode,const N:usize> Encode for [T;N]{fn encode(&self,v:&mut Vec<u64>){v.push(N as u64);for x in self{x.encode(v);}}fn caps(&self,v:&mut Vec<u64>){v.push(N as u64);for x in self{x.caps(v);}}}
impl Encode for LevelSpan {fn encode(&self,v:&mut Vec<u64>){v.extend([self.start as u64,self.count as u64]);}}
fn words<T:Encode>(v:&T)->Vec<u64>{let mut w=Vec::new();v.encode(&mut w);w}
fn caps<T:Encode>(v:&T)->Vec<u64>{let mut w=Vec::new();v.caps(&mut w);w}
fn dump(f:&mut BufWriter<File>,v:&[u64]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();let mut b=Vec::with_capacity(65536);for c in v.chunks(8192){b.clear();for x in c{b.extend(x.to_le_bytes());}f.write_all(&b).unwrap();}}
fn field<A:Encode,B:Encode>(f:&mut BufWriter<File>,id:u32,name:&str,a:&A,b:&B,permute:bool)->u64{let ca=caps(a);let cb=caps(b);assert_eq!(ca,cb,"capacity {name}");let wa=words(a);let wb=words(b);if !permute{assert_eq!(wa,wb,"field {name}");}f.write_all(&id.to_le_bytes()).unwrap();for v in [&ca,&cb,&wa,&wb]{dump(f,v);}wa.len() as u64}

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
    f.write_all(&(0u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.num_levels));dump(&mut f,&words(&plan.num_levels));
    f.write_all(&(1u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.nh));dump(&mut f,&words(&plan.nh));
    f.write_all(&(2u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.nh_max));dump(&mut f,&words(&plan.nh_max));
    f.write_all(&(3u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.num_nodes));dump(&mut f,&words(&plan.num_nodes));
    f.write_all(&(4u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.iso_active));dump(&mut f,&words(&plan.iso_active));
    f.write_all(&(5u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.action_nodes));dump(&mut f,&words(&plan.action_nodes));
    f.write_all(&(6u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.action_spans));dump(&mut f,&words(&plan.action_spans));
    f.write_all(&(7u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.chance_parents));dump(&mut f,&words(&plan.chance_parents));
    f.write_all(&(8u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.chance_children));dump(&mut f,&words(&plan.chance_children));
    f.write_all(&(9u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.chance_cards));dump(&mut f,&words(&plan.chance_cards));
    f.write_all(&(10u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.chance_spans));dump(&mut f,&words(&plan.chance_spans));
    f.write_all(&(11u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.chance_nodes));dump(&mut f,&words(&plan.chance_nodes));
    f.write_all(&(12u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.chance_node_spans));dump(&mut f,&words(&plan.chance_node_spans));
    f.write_all(&(13u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.fold_nodes));dump(&mut f,&words(&plan.fold_nodes));
    f.write_all(&(14u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.fold_spans));dump(&mut f,&words(&plan.fold_spans));
    f.write_all(&(15u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.show_nodes));dump(&mut f,&words(&plan.show_nodes));
    f.write_all(&(16u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.show_spans));dump(&mut f,&words(&plan.show_spans));
    f.write_all(&(17u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.cc_start));dump(&mut f,&words(&plan.cc_start));
    f.write_all(&(18u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.cc_count));dump(&mut f,&words(&plan.cc_count));
    f.write_all(&(19u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.cc_card));dump(&mut f,&words(&plan.cc_card));
    f.write_all(&(20u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.cc_child));dump(&mut f,&words(&plan.cc_child));
    f.write_all(&(21u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.cc_perm));dump(&mut f,&words(&plan.cc_perm));
    f.write_all(&(22u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.hand_perm_flat));dump(&mut f,&words(&plan.hand_perm_flat));
    f.write_all(&(23u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_player));dump(&mut f,&words(&plan.node_player));
    f.write_all(&(24u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_na));dump(&mut f,&words(&plan.node_na));
    f.write_all(&(25u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_data_off));dump(&mut f,&words(&plan.node_data_off));
    f.write_all(&(26u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.arena_elements));dump(&mut f,&words(&plan.arena_elements));
    f.write_all(&(27u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_children_start));dump(&mut f,&words(&plan.node_children_start));
    f.write_all(&(28u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_twin));dump(&mut f,&words(&plan.node_twin));
    f.write_all(&(29u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_tlose));dump(&mut f,&words(&plan.node_tlose));
    f.write_all(&(30u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_ttie));dump(&mut f,&words(&plan.node_ttie));
    f.write_all(&(31u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_cdiv));dump(&mut f,&words(&plan.node_cdiv));
    f.write_all(&(32u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.node_river_slot));dump(&mut f,&words(&plan.node_river_slot));
    f.write_all(&(33u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.reach_src));dump(&mut f,&words(&plan.reach_src));
    f.write_all(&(34u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.reach_slot));dump(&mut f,&words(&plan.reach_slot));
    f.write_all(&(35u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.reach_blocks));dump(&mut f,&words(&plan.reach_blocks));
    f.write_all(&(36u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.cfv_slot));dump(&mut f,&words(&plan.cfv_slot));
    f.write_all(&(37u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.cfv_blocks));dump(&mut f,&words(&plan.cfv_blocks));
    f.write_all(&(38u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.hand_c1));dump(&mut f,&words(&plan.hand_c1));
    f.write_all(&(39u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.hand_c2));dump(&mut f,&words(&plan.hand_c2));
    f.write_all(&(40u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.hand_mask));dump(&mut f,&words(&plan.hand_mask));
    f.write_all(&(41u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.same_combo));dump(&mut f,&words(&plan.same_combo));
    f.write_all(&(42u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.weights));dump(&mut f,&words(&plan.weights));
    f.write_all(&(43u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.num_slots));dump(&mut f,&words(&plan.num_slots));
    f.write_all(&(44u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_off));dump(&mut f,&words(&plan.riv_off));
    f.write_all(&(45u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_cnt));dump(&mut f,&words(&plan.riv_cnt));
    f.write_all(&(46u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_sorted_idx));dump(&mut f,&words(&plan.riv_sorted_idx));
    f.write_all(&(47u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_sorted_str));dump(&mut f,&words(&plan.riv_sorted_str));
    f.write_all(&(48u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_lower));dump(&mut f,&words(&plan.riv_lower));
    f.write_all(&(49u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_upper));dump(&mut f,&words(&plan.riv_upper));
    f.write_all(&(50u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_card_off));dump(&mut f,&words(&plan.riv_card_off));
    f.write_all(&(51u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_card_pos));dump(&mut f,&words(&plan.riv_card_pos));
    f.write_all(&(52u32).to_le_bytes()).unwrap();dump(&mut f,&caps(&plan.riv_max_cnt));dump(&mut f,&words(&plan.riv_max_cnt));
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
