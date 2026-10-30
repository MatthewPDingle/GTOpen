use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E070_HELPER_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let out=PathBuf::from(std::env::var_os("E070_HELPER_RESOURCE_DIR").expect("fresh S: resource output required"));
 assert!(out.starts_with(r"S:\GTOpen-research\postflop-gpu-20261016"));std::fs::create_dir(&out).unwrap();
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
 let(major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let actual:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let block_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 emit(serde_json::json!({"stage":"device","architecture":actual,"shared_limit":shared_limit,"block_limit":block_limit,"kernel_launches":0}));
 let groups:[(&str,&str,&str,&[&str]);2]=[
  ("projection",include_str!("baseline-projection.cu"),include_str!("candidate-projection.cu"),&["continuation_project","continuation_transport"]),
  ("storage-copy",include_str!("baseline-storage-copy.cu"),include_str!("candidate-storage-copy.cu"),&["continuation_storage_copy"])
 ];
 for arch in [actual,"compute_75"]{
  for (name,baseline,candidate,kernels) in groups{
   for (variant,source) in [("baseline",baseline),("candidate",candidate)]{
    let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
    let mut f=OpenOptions::new().create_new(true).write(true).open(out.join(format!("{name}-{variant}-{arch}.ptx"))).unwrap();
    f.write_all(ptx.to_src().as_bytes()).unwrap();f.flush().unwrap();f.sync_all().unwrap();drop(f);
    if arch==actual{
     let module=ctx.load_module(ptx).unwrap();
     for &kernel in kernels{
      let function=module.load_function(kernel).unwrap();
      let registers=function.num_regs().unwrap();let local=function.local_size_bytes().unwrap();let shared=function.shared_size_bytes().unwrap();let max_threads=function.max_threads_per_block().unwrap();
      let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|threads|(threads,function.occupancy_max_active_blocks_per_multiprocessor(threads,0,None).unwrap())).collect();
      emit(serde_json::json!({"stage":"resource","module":name,"variant":variant,"kernel":kernel,"registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":0,"max_threads":max_threads,"actual_block_threads":128,"occupancy_by_threads":occupancy,"fits_default_limits":shared<=shared_limit&&max_threads>=256&&block_limit>=256,"kernel_launches":0,"performance_measurement":false}));
     }
     drop(module);ctx.check_err().unwrap();
    }
   }
  }
 }
 ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete","resource_rows":6,"compile_variants":8,"kernel_launches":0,"solver_executions":0,"performance_measurement":false,"candidate_accepted":false}));
}
