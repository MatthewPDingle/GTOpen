use cudarc::{driver::{CudaContext,sys::{CUdevice_attribute as Attr,CUlimit}},nvrtc::Ptx};
use std::{io::Write,path::PathBuf};
fn emit(v:serde_json::Value){println!("D161_RESOURCE {v}");std::io::stdout().flush().unwrap();}
fn main(){
 let dir=PathBuf::from(std::env::args().nth(1).unwrap());let ctx=CudaContext::new(0).unwrap();
 assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let thread_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 let names=["copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","copy_span","up_action_eval"];
 for variant in ["baseline","candidate"]{
  let stack_before=ctx.get_limit(CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let heap_before=ctx.get_limit(CUlimit::CU_LIMIT_MALLOC_HEAP_SIZE).unwrap();
  let module=ctx.load_module(Ptx::from_file(dir.join(format!("{variant}.ptx")))).unwrap();
  let stack_after=ctx.get_limit(CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let heap_after=ctx.get_limit(CUlimit::CU_LIMIT_MALLOC_HEAP_SIZE).unwrap();
  for name in names{
   let f=module.load_function(name).unwrap();let max=f.max_threads_per_block().unwrap();let shared=f.shared_size_bytes().unwrap();
   let sizes:Vec<u32>=match name {"up_fold"=>vec![4,256,4324,5304],"up_show"=>vec![20,1280,4*1176+16*1081,20*1326],_=>vec![0]};let mut controls=Vec::new();
   for dynamic in sizes{for threads in [64u32,128,256]{
    let occupancy=if threads<=max as u32{Some(f.occupancy_max_active_blocks_per_multiprocessor(threads,dynamic as usize,None).unwrap())}else{None};
    controls.push(serde_json::json!({"threads":threads,"dynamic_shared_bytes":dynamic,"supported_by_original_source_limit":threads<=max as u32,"occupancy":occupancy,"fits_default_limits":threads<=thread_limit as u32&&shared+dynamic as i32<=shared_limit}));
   }}
   emit(serde_json::json!({"variant":variant,"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"static_shared_bytes":shared,"max_threads":max,"default_shared_limit":shared_limit,"context_stack_before":stack_before,"context_stack_after":stack_after,"context_heap_before":heap_before,"context_heap_after":heap_after,"controls":controls,"kernel_launches":0}));
  }
  drop(module);ctx.check_err().unwrap();
 }
 emit(serde_json::json!({"stage":"complete","modules_loaded":2,"resource_rows":18,"NVRTC_compilations":0,"kernel_launches":0,"solver_executions":0,"performance_samples":0}));
}
