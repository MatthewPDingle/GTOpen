#![allow(dead_code)]
pub use solver::{cfr,store,tree};
use solver::{Solver,Spot,SpotConfig,store::{Storage,Store},gpu::plan::GpuPlan};
use cudarc::{driver::{CudaContext,CudaStream,CudaModule},nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx}};
use std::{ffi::c_void,fs::{File,OpenOptions},io::{self,BufWriter,Write},path::Path,sync::{Arc,atomic::{AtomicUsize,Ordering}},time::Instant};
use rayon::prelude::*;use serde_json::{json,Value};
mod plan{pub use solver::gpu::plan::GpuPlan;}
#[path="arena-observed.rs"]mod arena;
fn e(err:impl std::fmt::Debug)->String{format!("{err:?}")}
pub(crate) struct PinnedBuf {
    ptr: *mut f32,
    len: usize,
}

unsafe impl Send for PinnedBuf {}
unsafe impl Sync for PinnedBuf {}

impl PinnedBuf {
    pub(crate) fn new(ctx: &Arc<CudaContext>, len: usize) -> Result<PinnedBuf, String> {
        ctx.bind_to_thread().map_err(e)?;
        let ptr = unsafe { cudarc::driver::result::malloc_host(len * 4, 0) }.map_err(e)?;
        Ok(PinnedBuf {
            ptr: ptr as *mut f32,
            len,
        })
    }
    pub(crate) fn as_slice(&self) -> &[f32] {
        unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
    }
    pub(crate) fn as_mut_slice(&mut self) -> &mut [f32] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) }
    }
}

impl Drop for PinnedBuf {
    fn drop(&mut self) {
        unsafe {
            cudarc::driver::result::free_host(self.ptr as _).ok();
        }
    }
}


fn write_arena(solver: &Solver, which_strat: bool, p: usize, data: &[f32]) {
    let store = if which_strat {
        &solver.strat[p]
    } else {
        &solver.regrets[p]
    };
    match store {
        Store::F32(b) => unsafe { b.slice(0, data.len()) }.copy_from_slice(data),
        _ => {
            let nh = solver.spot.hands[p].len();
            // Every node owns disjoint entries and its own scale factor.
            solver.spot.tree.nodes.par_iter().enumerate().for_each(|(idx, node)| {
                if node.kind == crate::tree::KIND_ACTION && node.player as usize == p {
                    let cnt = node.num_children as usize * nh;
                    let off = node.data_offset as usize;
                    unsafe {
                        store.write_f32(idx as u32, node.data_offset, cnt, &data[off..off + cnt]);
                    }
                }
            });
        }
    }
}


#[repr(C)]#[derive(Default)]struct FileTime{low:u32,high:u32}
#[repr(C)]#[derive(Default)]struct MemoryCounters{cb:u32,faults:u32,peak_ws:usize,ws:usize,quota_peak_paged:usize,quota_paged:usize,quota_peak_nonpaged:usize,quota_nonpaged:usize,commit:usize,peak_commit:usize}
#[link(name="kernel32")]extern "system"{fn GetCurrentProcess()->*mut c_void;fn GetProcessTimes(p:*mut c_void,c:*mut FileTime,e:*mut FileTime,k:*mut FileTime,u:*mut FileTime)->i32;fn K32GetProcessMemoryInfo(p:*mut c_void,c:*mut MemoryCounters,n:u32)->i32;}
fn cpu_ticks()->u64{let(mut c,mut e,mut k,mut u)=(FileTime::default(),FileTime::default(),FileTime::default(),FileTime::default());assert_ne!(unsafe{GetProcessTimes(GetCurrentProcess(),&mut c,&mut e,&mut k,&mut u)},0);let cvt=|t:FileTime|((t.high as u64)<<32)|t.low as u64;cvt(k)+cvt(u)}
fn counters()->MemoryCounters{let mut m=MemoryCounters::default();m.cb=std::mem::size_of::<MemoryCounters>()as u32;assert_eq!(m.cb,72);assert_ne!(unsafe{K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,m.cb)},0);m}
fn mem(m:&MemoryCounters)->Value{json!({"faults":m.faults,"working_set_bytes":m.ws,"peak_working_set_bytes":m.peak_ws,"commit_bytes":m.commit,"peak_commit_bytes":m.peak_commit})}
fn emit(v:Value){let mut out=io::stdout().lock();writeln!(out,"D131 {v}").unwrap();out.flush().unwrap();}

struct ZeroCheck<'a>{store:&'a Store,positive:bool}
impl<'a> ZeroCheck<'a>{
 fn new(store:&'a Store)->Self{let positive={match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0
            }
            Store::U16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0
            }
            Store::F32(_) => false,
        }};Self{store,positive}}
 fn positive_for(&self,store:&Store)->Option<bool>{std::ptr::eq(self.store,store).then_some(self.positive)}
}
fn checks_with_setup<S,V:Send,F:FnOnce()->Result<S,String>,C:Fn()->V+Sync>(eligible:bool,setup:F,checks:C)->Result<(S,V),String>{
 if !eligible{let s=setup()?;return Ok((s,checks()));}
 std::thread::scope(|scope|{
  let worker=std::thread::Builder::new().name("gtopen-zero-check".into()).spawn_scoped(scope,||checks());
  let s=setup();let result=worker.ok().map(|h|h.join());let s=s?;
  let values=match result{Some(Ok(v))=>v,Some(Err(payload))=>std::panic::resume_unwind(payload),None=>checks()};Ok((s,values))
 })
}
struct Mock(Arc<AtomicUsize>);impl Drop for Mock{fn drop(&mut self){self.0.fetch_add(1,Ordering::SeqCst);}}
fn store_image(s:&Store)->Vec<u32>{match s{Store::I16{q,scale}=>q.as_slice().iter().map(|&x|x as u16 as u32).chain(scale.as_slice().iter().map(|x|x.to_bits())).collect(),Store::U16{q,scale}=>q.as_slice().iter().map(|&x|x as u32).chain(scale.as_slice().iter().map(|x|x.to_bits())).collect(),Store::F32(b)=>b.as_slice().iter().map(|x|x.to_bits()).collect()}}
fn ability(){
 let mut lifecycle=0;let caller=std::thread::current().id();
 for eligible in[false,true]{for setupmode in[0,1,2]{for checkmode in[0,1]{
  let calls=Arc::new(AtomicUsize::new(0));let drops=Arc::new(AtomicUsize::new(0));let c=calls.clone();let d=drops.clone();
  let outcome=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||checks_with_setup(eligible,||{assert_eq!(std::thread::current().id(),caller);match setupmode{0=>Ok(7usize),1=>Err("setup".into()),_=>panic!("setup mock")}},||{c.fetch_add(1,Ordering::SeqCst);assert_eq!(std::thread::current().id()==caller,!eligible);if checkmode==1{panic!("check mock");}Mock(d.clone())})));
  let expected=if eligible||setupmode==0{1}else{0};assert_eq!(calls.load(Ordering::SeqCst),expected);
  match(setupmode,checkmode,outcome){(1,_,Ok(Err(x)))=>assert_eq!(x,"setup"),(2,_,Err(_))=>{},(0,0,Ok(Ok((s,v))))=>{assert_eq!(s,7);drop(v);},(0,1,Err(_))=>{},_=>panic!("incorrect lifecycle")}
  assert_eq!(drops.load(Ordering::SeqCst),if checkmode==0{expected}else{0});lifecycle+=1;
 }}}
 let mut predicates=0;let mut full_words=0;let mut images=Vec::new();
 for signed in[false,true]{let mut s=if signed{Store::i16(257,4)}else{Store::u16(257,4)};
  for step in 0..7 {if step==1{match &mut s{Store::I16{q,..}=>q.as_mut_slice()[256]=-1,Store::U16{q,..}=>q.as_mut_slice()[256]=1,_=>unreachable!()}}else if step>=2{match &mut s{Store::I16{q,scale}=>{q.as_mut_slice()[256]=0;scale.as_mut_slice()[3]=f32::from_bits([0x8000_0000,0x7f80_0000,0xff80_0000,0x7fc0_1234,1][step-2]);},Store::U16{q,scale}=>{q.as_mut_slice()[256]=0;scale.as_mut_slice()[3]=f32::from_bits([0x8000_0000,0x7f80_0000,0xff80_0000,0x7fc0_1234,1][step-2]);},_=>unreachable!()}}
   let before=store_image(&s);let check=ZeroCheck::new(&s);let original=arena::ArenaLayout::probe_original_predicate(&s);assert_eq!(check.positive_for(&s),Some(original));assert_eq!(original,step==0);let other=Store::u16(257,4);assert_eq!(check.positive_for(&other),None);drop(check);let after=store_image(&s);assert_eq!(before,after);full_words+=before.len()*2;images.push(json!({"signed":signed,"step":step,"before":before,"after":after}));predicates+=1;
  }
 }
 let s=Store::f32(257);assert!(!arena::ArenaLayout::probe_original_predicate(&s));assert_eq!(ZeroCheck::new(&s).positive_for(&s),Some(false));predicates+=1;
 assert_eq!(lifecycle,12);assert_eq!(predicates,15);assert_eq!(std::mem::size_of::<FileTime>(),8);assert_eq!(std::mem::size_of::<MemoryCounters>(),72);let c=cpu_ticks();let _=counters();assert!(cpu_ticks()>=c);
 emit(json!({"stage":"ability","lifecycle_cases":lifecycle,"predicate_cases":predicates,"all_full_words_before_after_exact":true,"full_words_checked":full_words,"full_images":images,"wrong_store_tokens_rejected":14,"setup_stays_on_caller":true,"cleanup_and_setup_error_priority_pass":true,"CUDA_or_application_executions":0}));
}
fn setup(ctx:&Arc<CudaContext>,s:&Solver,plan:&GpuPlan)->Result<(Arc<CudaModule>,PinnedBuf,[arena::ArenaLayout;2]),String>{
 let(major,minor)=ctx.compute_capability().map_err(e)?;let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 static PTX:std::sync::OnceLock<Result<Ptx,String>>=std::sync::OnceLock::new();
 let ptx=PTX.get_or_init(||compile_ptx_with_opts(include_str!("kernels.cu"),CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
 let module=ctx.load_module(ptx).map_err(e)?;let data_len=plan.arena_elements;let pinned=PinnedBuf::new(ctx,data_len[0].max(data_len[1]))?;
 let layouts=[arena::ArenaLayout::new(s,plan,0),arena::ArenaLayout::new(s,plan,1)];Ok((module,pinned,layouts))
}
fn words(f:&mut impl Write,v:&[u64]){f.write_all(&(v.len()as u64).to_le_bytes()).unwrap();for c in v.chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();}}
fn run(arm:&str,out:&Path){std::fs::create_dir(out).unwrap();let configs=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];
 for(i,config)in configs.iter().enumerate(){let cfg:SpotConfig=serde_json::from_str(config).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=true;let plan=GpuPlan::build(&s.spot,s.use_isomorphism);let ctx=CudaContext::new(0).unwrap();let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}assert_eq!(ctx.compute_capability().unwrap(),(12,0));
  let stores=[&s.regrets[0],&s.regrets[1],&s.strat[0],&s.strat[1]];let q_bytes:usize=stores.iter().map(|s|match s{Store::I16{q,..}=>q.len()*2,Store::U16{q,..}=>q.len()*2,Store::F32(_)=>0}).sum();let eligible=arm=="overlap"&&q_bytes>=64*1024*1024;
  let mb=counters();let cb=cpu_ticks();let clock=Instant::now();
  let((module,pinned,layouts),proofs)=checks_with_setup(eligible,||setup(&ctx,&s,&plan),||stores.map(ZeroCheck::new)).unwrap();
  let flags=[proofs[0].positive_for(stores[0]).unwrap()&&layouts[0].probe_guards(0),proofs[1].positive_for(stores[1]).unwrap()&&layouts[1].probe_guards(0),proofs[2].positive_for(stores[2]).unwrap()&&layouts[0].probe_guards(1),proofs[3].positive_for(stores[3]).unwrap()&&layouts[1].probe_guards(1)];std::hint::black_box(flags);
  let elapsed=clock.elapsed().as_secs_f64()*1000.0;let ca=cpu_ticks();let ma=counters();assert_eq!(flags,[true;4]);assert!(ca>=cb);stream.synchronize().unwrap();
  let raw=out.join(format!("fixture-{i}.bin"));let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(&raw).unwrap());f.write_all(b"D131-LAYOUT-R1\0\0").unwrap();f.write_all(&(i as u32).to_le_bytes()).unwrap();f.write_all(&(2u32).to_le_bytes()).unwrap();let mut layout_words=0;
  for p in 0..2{let reference=arena::ArenaLayout::new(&s,&plan,p);let actual=layouts[p].probe_words();let expected=reference.probe_words();assert_eq!(actual,expected);layout_words+=actual.len();words(&mut f,&actual);words(&mut f,&expected);}f.flush().unwrap();f.get_ref().sync_all().unwrap();
  emit(json!({"stage":"zero_setup_component","fixture_index":i,"arm":arm,"board":s.spot.config.board,"nodes":s.spot.tree.nodes.len(),"q_bytes":q_bytes,"overlap_eligible":eligible,"pinned_bytes":pinned.len*4,"component_ms":elapsed,"process_CPU_ms":(ca-cb)as f64/10000.0,"cpu_before_ticks100ns":cb,"cpu_after_ticks100ns":ca,"before":mem(&mb),"after":mem(&ma),"all_original_full_predicates_and_guards":flags,"full_private_layout_words_per_arm":layout_words,"raw_layout":raw,"setup_CUDA_calls_stay_on_caller":true,"application_kernel_launches":0,"GPU_solver_executions":0,"performance_is_full_solve":false}));
  drop(proofs);drop(layouts);drop(pinned);drop(module);drop(stream);drop(ctx);drop(plan);drop(s);
 }
 emit(json!({"stage":"complete","arm":arm,"fixtures":3,"application_kernel_launches":0,"GPU_solver_executions":0,"performance_is_full_solve":false}));}
fn main(){let args:Vec<_>=std::env::args().collect();match args.get(1).map(String::as_str){Some("ability")=>{assert_eq!(args.len(),2);ability();},Some("baseline")|Some("overlap")=>{assert_eq!(args.len(),3);run(&args[1],Path::new(&args[2]));},_=>panic!("invalid mode")}}
