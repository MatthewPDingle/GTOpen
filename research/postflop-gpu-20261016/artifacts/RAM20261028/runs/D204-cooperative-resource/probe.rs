use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"D204_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let out=PathBuf::from(std::env::args().nth(1).unwrap());
 let paths:Vec<String>=serde_json::from_str(include_str!("includes.json")).unwrap();
 for arch in ["compute_120","compute_75"]{
  let ptx=compile_ptx_with_opts(include_str!("primitive.cu"),CompileOptions{arch:Some(arch),include_paths:paths.clone(),..Default::default()}).unwrap();
  let mut f=OpenOptions::new().create_new(true).write(true).open(out.join(format!("primitive-{arch}.ptx"))).unwrap();f.write_all(ptx.to_src().as_bytes()).unwrap();f.flush().unwrap();f.sync_all().unwrap();
  emit(serde_json::json!({"stage":"compiled","architecture":arch,"application_kernels":0}));
  if arch=="compute_120"{
   let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
   assert_eq!(ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH).unwrap(),1);
   let before=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let module=ctx.load_module(ptx).unwrap();let f=module.load_function("d204_grid_order").unwrap();let after=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
   let resident=f.occupancy_max_active_blocks_per_multiprocessor(128,0,None).unwrap();let sms=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT).unwrap();assert!(resident>0&&sms==170);
   emit(serde_json::json!({"stage":"resources","architecture":arch,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"dynamic_shared_bytes":0,"max_threads":f.max_threads_per_block().unwrap(),"fixed_block_threads":128,"resident_blocks_per_SM":resident,"SM_count":sms,"max_cooperative_grid_blocks":resident as usize*sms as usize,"context_stack_before":before,"context_stack_after":after,"device_shared_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap(),"application_kernels":0}));
   drop(f);drop(module);ctx.check_err().unwrap();drop(ctx);
  }
 }
 emit(serde_json::json!({"stage":"complete","compile_variants":2,"application_kernels":0,"solver_or_speed_samples":0}));
}
