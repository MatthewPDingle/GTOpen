use solver::{Spot,SpotConfig,Solver,Algorithm,TreeConfig,StreetSizing,parse_sizes};
use solver::gpu::{GpuSolver,StoredContinuationGpu,StoredWorkspace};
use solver::store::Store;
use cudarc::driver::CudaContext;
use std::{sync::Arc,path::PathBuf,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E051_CAPACITY {v}").unwrap();o.flush().unwrap();}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let root=PathBuf::from(&args[1]);std::fs::create_dir(&root).unwrap();
 // Retain one primary context for comparable unscored device-wide observations.
 // All owned-slice accounting below comes from the actual constructor method.
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let mut workspace=StoredWorkspace::default();let mut ram=u64::MAX;let mut cases=0;
 for board in ["KsQs2d","KsQs2s","KsQh2d"] {for (pot,stack) in [(39.5,80.),(93.5,155.)] {
  let z=StreetSizing{bet:parse_sizes("50").unwrap(),raise:vec![],donk:parse_sizes("50").unwrap()};
  let spot=Arc::new(Spot::new(SpotConfig{board:board.into(),range_oop:"AA,KK,AQs,KQo,88,76s".into(),range_ip:"AA,QQ,AKo,QJs,99".into(),tree:TreeConfig{starting_pot:pot,effective_stack:stack,rake_pct:0.04,rake_cap:6.,max_raises:0,oop:[z.clone(),z.clone(),z.clone()],ip:[z.clone(),z.clone(),z],..Default::default()}}).unwrap());
  let mut host=Solver::new(spot);host.algo=Algorithm::CfrPlus;host.use_isomorphism=false;assert!(host.regrets.iter().chain(&host.strat).all(|x|matches!(x,Store::F32(_))));
  let before=ctx.mem_get_info().unwrap();
  let gpu=StoredContinuationGpu::new(&host,&mut workspace,&root,cases,&mut ram).unwrap();ctx.synchronize().unwrap();
  let accounting=gpu.research_capacity_check();let after=ctx.mem_get_info().unwrap();
  emit(serde_json::json!({"stage":"case","id":cases,"board":board,"pot":pot,"stack":stack,"actual_metadata_assertions_passed":true,"capacity":accounting,"actual_workspace_bytes":workspace.bytes(),"remaining_ram_budget":ram,"host_type_bytes":{"GpuSolver":std::mem::size_of::<GpuSolver>(),"StoredContinuationGpu":std::mem::size_of::<StoredContinuationGpu>(),"StoredWorkspace":std::mem::size_of::<StoredWorkspace>()},"device_wide_observation":{"free_before":before.0,"free_with_entry":after.0,"total":after.1,"solver_only_delta":false},"solver_iterations":0}));
  drop(gpu);ctx.synchronize().unwrap();cases+=1;
 }}
 assert_eq!(cases,6);emit(serde_json::json!({"stage":"complete","cases":cases,"actual_workspace_bytes":workspace.bytes(),"solver_iterations":0,"performance_measured":false,"candidate_accepted":false}));ctx.check_err().unwrap();
}
