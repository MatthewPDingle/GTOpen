#![cfg(all(target_os="windows",target_pointer_width="64"))]
use solver::{Solver,Spot,SpotConfig,store::{Store,Storage},gpu::plan::GpuPlan};
use std::{ffi::c_void,io::{self,Write},sync::Arc,time::Instant};
use serde_json::{json,Value};
#[repr(C)]#[derive(Clone,Copy)]struct MemoryRange {address:*mut c_void,bytes:usize}
#[repr(C)]#[derive(Default)]struct MemoryCounters {cb:u32,faults:u32,peak_ws:usize,ws:usize,quota_peak_paged:usize,quota_paged:usize,quota_peak_nonpaged:usize,quota_nonpaged:usize,commit:usize,peak_commit:usize}
#[link(name="kernel32")]extern "system" {
 fn GetCurrentProcess()->*mut c_void;
 fn GetLastError()->u32;
 fn PrefetchVirtualMemory(process:*mut c_void,entries:usize,ranges:*const MemoryRange,flags:u32)->i32;
 fn K32GetProcessMemoryInfo(process:*mut c_void,counters:*mut MemoryCounters,bytes:u32)->i32;
}
fn emit(value:Value){let mut out=io::stdout().lock();writeln!(out,"D126 {value}").unwrap();out.flush().unwrap();}
fn counters()->MemoryCounters {let mut m=MemoryCounters::default();m.cb=std::mem::size_of::<MemoryCounters>()as u32;assert_ne!(unsafe{K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,m.cb)},0);assert_eq!(m.cb,72);assert!(m.ws>0&&m.peak_ws>=m.ws);m}
fn counter_json(m:&MemoryCounters)->Value{json!({"page_faults":m.faults,"working_set_bytes":m.ws,"peak_working_set_bytes":m.peak_ws,"commit_bytes":m.commit,"peak_commit_bytes":m.peak_commit})}
#[inline(never)]fn original_zero_predicate(store:&Store)->bool {match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0
            }
            Store::U16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0
            }
            Store::F32(_) => false,
        }}
fn zero_ranges(stores:[&Store;4])->(usize,Option<[MemoryRange;4]>) {
 let mut ranges=[MemoryRange{address:std::ptr::null_mut(),bytes:0};4];let mut total=0usize;
 for(i,store)in stores.iter().enumerate(){let(ptr,bytes)=match store {Store::I16{q,..}=>(q.as_slice().as_ptr()as *mut c_void,q.len().checked_mul(2).unwrap()),Store::U16{q,..}=>(q.as_slice().as_ptr()as *mut c_void,q.len().checked_mul(2).unwrap()),Store::F32(_)=>return(0,None)};ranges[i]=MemoryRange{address:ptr,bytes};total=total.checked_add(bytes).unwrap();}
 if total<64*1024*1024||ranges.iter().any(|r|r.bytes==0){return(total,None);}
 for store in stores {let scale=match store{Store::I16{scale,..}|Store::U16{scale,..}=>scale,Store::F32(_)=>unreachable!()};if !scale.as_slice().iter().all(|v|v.to_bits()==0){return(total,None);}}
 (total,Some(ranges))
}
fn ability(){
 assert_eq!(std::mem::size_of::<MemoryRange>(),16);assert_eq!(std::mem::align_of::<MemoryRange>(),8);assert_eq!(std::mem::size_of::<MemoryCounters>(),72);
 let input:Vec<u16>=(0..4128).map(|i|((i*73+17)&65535)as u16).collect();let mut values=input.clone();let range=MemoryRange{address:unsafe{values.as_mut_ptr().add(16)}as *mut c_void,bytes:4096*2};let before=counters();let ok=unsafe{PrefetchVirtualMemory(GetCurrentProcess(),1,&range,0)};let error=if ok==0{unsafe{GetLastError()}}else{0};let after=counters();assert_eq!(values,input);
 let mut controls=0;
 for signed in [false,true]{let mut s=if signed{Store::i16(257,4)}else{Store::u16(257,4)};assert!(original_zero_predicate(&s));controls+=1;
  match &mut s {Store::I16{q,..}=>q.as_mut_slice()[256]=-1,Store::U16{q,..}=>q.as_mut_slice()[256]=1,_=>unreachable!()};assert!(!original_zero_predicate(&s));controls+=1;
  match &mut s {Store::I16{q,..}=>q.as_mut_slice()[256]=0,Store::U16{q,..}=>q.as_mut_slice()[256]=0,_=>unreachable!()};
  for bits in [0x8000_0000,0x7f80_0000,0xff80_0000,0x7fc0_1234,1] {match &mut s {Store::I16{scale,..}|Store::U16{scale,..}=>scale.as_mut_slice()[3]=f32::from_bits(bits),_=>unreachable!()};assert!(!original_zero_predicate(&s));controls+=1;}
 }
 assert!(!original_zero_predicate(&Store::f32(257)));controls+=1;
 emit(json!({"stage":"ability","prefetch_success":ok!=0,"last_error":error,"prefetch_calls":1,"owned_range_bytes":8192,"full_before_u16":input,"full_after_u16":values,"all_guards_and_data_exact":true,"predicate_controls":controls,"range_struct_bytes":16,"memory_counter_bytes":72,"before":counter_json(&before),"after":counter_json(&after),"GPU_executions":0}));
}
fn run(arm:&str){
 let fixtures=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];
 for(case,config)in fixtures.iter().enumerate(){
  let cfg:SpotConfig=serde_json::from_str(config).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=true;
  let plan=GpuPlan::build(&s.spot,s.use_isomorphism);std::hint::black_box(&plan);
  let stores=[&s.regrets[0],&s.regrets[1],&s.strat[0],&s.strat[1]];let q_bytes:usize=stores.iter().map(|store|match store{Store::I16{q,..}=>q.len()*2,Store::U16{q,..}=>q.len()*2,_=>0}).sum();assert!(q_bytes<4*1024*1024*1024usize);
  let before=counters();let t=Instant::now();let(mut calls,mut success,mut error,mut range_count,mut range_bytes)=(0,false,0,0,0);let mut prefetch_ms=0.0;
  if arm=="prefetch" {let(bytes,ranges)=zero_ranges(stores);if let Some(ranges)=ranges {assert_eq!(bytes,q_bytes);for r in ranges {assert!(!r.address.is_null()&&r.bytes>0);}let start=Instant::now();let ok=unsafe{PrefetchVirtualMemory(GetCurrentProcess(),4,ranges.as_ptr(),0)};prefetch_ms=start.elapsed().as_secs_f64()*1000.0;calls=1;success=ok!=0;error=if success{0}else{unsafe{GetLastError()}};range_count=4;range_bytes=bytes;}}
  let checked=stores.map(original_zero_predicate);std::hint::black_box(checked);let elapsed=t.elapsed().as_secs_f64()*1000.0;let after=counters();assert_eq!(checked,[true;4]);
  emit(json!({"stage":"CPU_zero_scan","fixture_index":case,"board":s.spot.config.board,"arm":arm,"q_bytes":q_bytes,"cpu_arena_bytes":s.arena_bytes(),"nodes":s.spot.tree.nodes.len(),"plan_levels":plan.num_levels,"component_ms":elapsed,"prefetch_ms_contained":prefetch_ms,"prefetch_calls":calls,"prefetch_success":success,"prefetch_error":error,"prefetch_range_count":range_count,"prefetch_bytes":range_bytes,"all4_original_full_checks_pass":checked,"before":counter_json(&before),"after":counter_json(&after),"process_page_fault_delta":after.faults.wrapping_sub(before.faults),"GPU_executions":0,"full_solve_performance_measured":false}));
 }
 emit(json!({"stage":"complete","arm":arm,"fixtures":3,"GPU_executions":0,"full_solve_performance_measured":false}));
}
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);match args[1].as_str(){"ability"=>ability(),"baseline"=>run("baseline"),"prefetch"=>run("prefetch"),_=>panic!("invalid mode")}}
