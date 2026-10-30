//! E042 compiler/load/resource inspection only; no kernels or solvers execute.
use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E042_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let ctx=CudaContext::new(0).unwrap();let device=ctx.name().unwrap();assert_eq!(device,"NVIDIA GeForce RTX 5090");
 let (major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let block_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 emit(serde_json::json!({"stage":"device","device":device,"architecture":arch,"shared_limit":shared_limit,"block_thread_limit":block_limit,"kernel_launches":0}));
 for (variant,source) in [("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))]{
  let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
  let mut file=OpenOptions::new().write(true).create_new(true).open(format!("{variant}.ptx")).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.flush().unwrap();file.sync_all().unwrap();drop(file);
  let module=ctx.load_module(ptx).unwrap();let f=module.load_function("up_action").unwrap();
  let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();let shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
  let blocks=f.occupancy_max_active_blocks_per_multiprocessor(128,0,None).unwrap();
  let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|threads|
   (threads,f.occupancy_max_active_blocks_per_multiprocessor(threads,0,None).unwrap())).collect();
  emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":"up_action","registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":0,"max_threads":max_threads,"actual_block_threads":128,"theoretical_blocks_per_sm":blocks,"occupancy_by_threads":occupancy,"fits_default_limits":shared<=shared_limit && max_threads>=128 && block_limit>=128,"kernel_launches":0,"performance_measurement":false}));
  drop(f);drop(module);ctx.check_err().unwrap();
 }
 ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete","kernel_launches":0,"solver_executions":0,"performance_measurement":false,"candidate_accepted":false}));
}
