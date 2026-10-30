use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E091_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
 let(major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let actual:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 let output=std::path::PathBuf::from(std::env::args().nth(1).expect("fresh output directory"));
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let block_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 emit(serde_json::json!({"stage":"device","device":ctx.name().unwrap(),"architecture":actual,"shared_limit":shared_limit,"block_limit":block_limit,"kernel_launches":0}));
 for arch in [actual,"compute_75"]{
  for(variant,source) in [("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))]{
   let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
   let mut file=OpenOptions::new().create_new(true).write(true).open(output.join(format!("{variant}-{arch}.ptx"))).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.flush().unwrap();file.sync_all().unwrap();drop(file);
   if arch==actual{
    let stack_before=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
    let module=ctx.load_module(ptx).unwrap();
    let stack_after=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
    for kernel in ["down_action"]{
     let f=module.load_function(kernel).unwrap();let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();let shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
     let dynamic=0u32;
     let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|t|(t,f.occupancy_max_active_blocks_per_multiprocessor(t,dynamic as usize,None).unwrap())).collect();
     emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":kernel,"shape":"same128threads_no_dynamic_shared","registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":dynamic,"context_stack_limit_before_load":stack_before,"context_stack_limit_after_load":stack_after,"max_threads":max_threads,"actual_block_threads":128,"occupancy_by_threads":occupancy,"fits_default_limits":shared+dynamic as i32<=shared_limit&&max_threads>=256&&block_limit>=256,"kernel_launches":0,"performance_measurement":false}));
    }
    drop(module);ctx.check_err().unwrap();
   }
  }
 }
 ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete","resource_rows":2,"compile_variants":4,"kernel_launches":0,"solver_executions":0,"performance_measurement":false,"candidate_accepted":false}));
}
