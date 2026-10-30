use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E063_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
 let (major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let actual:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let block_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 emit(serde_json::json!({"stage":"device","device":ctx.name().unwrap(),"architecture":actual,"shared_limit":shared_limit,"block_limit":block_limit,"kernel_launches":0}));
 let shapes=[("rainbow_p0",319u32,314u32),("rainbow_p1",257,252),("two_tone_p0",320,315),("two_tone_p1",258,253),("river_p0",280,280),("river_p1",233,233),("wide_turn",1128,1081),("full_hand_upper_bound",1326,1326),("empty_sorted_opponent",319,0),("single_sorted_opponent",319,1)];
 for arch in [actual,"compute_75"] {
  for (variant,source) in [("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))]{
   let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
   let mut file=OpenOptions::new().create_new(true).write(true).open(format!("{variant}-{arch}.ptx")).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.flush().unwrap();file.sync_all().unwrap();drop(file);
   if arch==actual {
    let module=ctx.load_module(ptx).unwrap();let f=module.load_function("up_show").unwrap();
    let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();let shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
    for (shape,nh_o,m) in shapes {
     let dynamic=4*nh_o+16*m;
     let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|t|(t,f.occupancy_max_active_blocks_per_multiprocessor(t,dynamic as usize,None).unwrap())).collect();
     emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":"up_show","shape":shape,"registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":dynamic,"max_threads":max_threads,"actual_block_threads":128,"occupancy_by_threads":occupancy,"fits_default_limits":shared+dynamic as i32<=shared_limit&&max_threads>=128&&block_limit>=128,"kernel_launches":0,"performance_measurement":false}));
    }
    drop(f);drop(module);ctx.check_err().unwrap();
   }
  }
 }
 ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete","resource_rows":20,"compile_variants":4,"kernel_launches":0,"solver_executions":0,"performance_measurement":false,"candidate_accepted":false}));
}
