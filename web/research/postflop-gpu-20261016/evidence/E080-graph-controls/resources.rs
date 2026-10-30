use cudarc::{driver::CudaContext,nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn main(){
 let out=PathBuf::from(std::env::args().nth(1).unwrap());assert!(out.is_dir());
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
 let (major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 for (arm,source) in [("baseline",include_str!("accepted.cu")),("candidate",include_str!("candidate.cu"))]{
  let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
  let mut f=OpenOptions::new().write(true).create_new(true).open(out.join(format!("{arm}.ptx"))).unwrap();f.write_all(ptx.to_src().as_bytes()).unwrap();f.sync_all().unwrap();drop(f);
  let module=ctx.load_module(ptx).unwrap();
  for name in ["copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","copy_span","up_action_eval"]{
   let f=module.load_function(name).unwrap();
   let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|n|(n,f.occupancy_max_active_blocks_per_multiprocessor(n,0,None).unwrap())).collect();
   println!("E080_RESOURCE {}",serde_json::json!({"arm":arm,"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes":f.local_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"max_threads":f.max_threads_per_block().unwrap(),"occupancy":occupancy,"architecture":arch,"kernel_launches":0}));
  }
  drop(module);ctx.check_err().unwrap();
 }
}
