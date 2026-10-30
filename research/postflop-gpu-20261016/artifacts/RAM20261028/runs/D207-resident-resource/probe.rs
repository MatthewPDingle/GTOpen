use cudarc::{driver::{CudaContext,CudaFunction,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
#[repr(C)]struct E104Args{
 action_nodes:u64,
 chance_parents:u64,
 chance_children:u64,
 chance_cards:u64,
 chance_nodes:u64,
 fold_nodes:u64,
 show_nodes:u64,
 node_player:u64,
 node_na:u64,
 node_data_off:u64,
 node_children_start:u64,
 children:u64,
 node_twin:u64,
 node_tlose:u64,
 node_ttie:u64,
 node_cdiv:u64,
 node_river_slot:u64,
 reach0:u64,
 reach1:u64,
 rsrc0:u64,
 rsrc1:u64,
 regrets0:u64,
 regrets1:u64,
 strat_p:u64,
 lock_off:u64,
 lock_sigma:u64,
 cfv_slot:u64,
 cfv:u64,
 disc:u64,
 mask0:u64,
 mask1:u64,
 hand_perm:u64,
 pc1:u64,
 pc2:u64,
 same:u64,
 fold_card_off:u64,
 fold_card_idx:u64,
 p_off:u64,
 p_cnt:u64,
 p_idx:u64,
 p_lower:u64,
 p_upper:u64,
 o_off:u64,
 o_cnt:u64,
 o_idx:u64,
 o_card_off:u64,
 o_card_pos:u64,
 cc_start:u64,
 cc_count:u64,
 cc_card:u64,
 cc_child:u64,
 cc_perm:u64,
 num_levels:i32,
 p:i32,
 nh0:i32,
 down_nh1:i32,
 nh_p:i32,
 nh_o:i32,
 nh_max:i32,
 spans:[[[u32;2];64];5],
}
#[repr(C)]struct ProposedHostState{function:Option<CudaFunction>,blocks:u32,shared:u32}
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"D207_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 assert_eq!(std::mem::size_of::<E104Args>(),3008);assert_eq!(std::mem::align_of::<E104Args>(),8);assert_eq!(std::mem::offset_of!(E104Args,spans),444);
 let out=PathBuf::from(std::env::args().nth(1).unwrap());let paths:Vec<String>=serde_json::from_str(include_str!("includes.json")).unwrap();let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));assert_eq!(ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH).unwrap(),1);
 let baseline_wrapper=std::mem::size_of::<solver::gpu::GpuSolver>();let state_bytes=std::mem::size_of::<ProposedHostState>();assert_eq!((baseline_wrapper,state_bytes),(4448,24));
 emit(serde_json::json!({"stage":"typed_layout","parameter_bytes":std::mem::size_of::<E104Args>(),"parameter_alignment":std::mem::align_of::<E104Args>(),"span_offset":std::mem::offset_of!(E104Args,spans),"baseline_host_wrapper_bytes":baseline_wrapper,"proposed_host_state_bytes":state_bytes,"prospective_wrapper_total_bytes":baseline_wrapper+state_bytes,"actual_candidate_host_not_yet_built":true,"application_kernels":0}));
 let old_names=["copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","copy_span","up_action_eval"];
 for variant in ["baseline","candidate"]{
  let ptx=if variant=="baseline"{Ptx::from_src(include_str!("baseline-compute_120.ptx"))}else{
   let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_120"),include_paths:paths.clone(),..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_120.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();p
  };
  let before=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let module=ctx.load_module(ptx).unwrap();let after=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let mut names=old_names.to_vec();if variant=="candidate"{names.push("e104_train");}
  for name in names{
   let f=module.load_function(name).unwrap();let dynamic=match name{"up_fold"=>1326*4,"up_show"|"e104_train"=>1326*20,_=>0};let occ=f.occupancy_max_active_blocks_per_multiprocessor(128,dynamic,None).unwrap();
   emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"dynamic_shared_bytes":dynamic,"max_threads":f.max_threads_per_block().unwrap(),"fixed_block_threads":128,"resident_blocks_per_SM_worst1326":occ,"SM_count":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT).unwrap(),"device_shared_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap(),"context_stack_before":before,"context_stack_after":after,"application_kernels":0}));
  }
  drop(module);ctx.check_err().unwrap();
 }
 let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_75"),include_paths:paths,..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_75.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();drop(f);ctx.check_err().unwrap();drop(ctx);
 emit(serde_json::json!({"stage":"complete","candidate_compile_variants":2,"reused_baseline_PTX":true,"resource_rows":19,"application_kernels":0,"solver_or_speed_samples":0}));
}
