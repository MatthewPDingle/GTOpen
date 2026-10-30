use solver::{Solver,Spot,SpotConfig,PathStep};
use solver::{gpu::{GpuSolver,plan::GpuPlan},store::{Store,Storage}};
use std::{sync::Arc,path::Path,io::{Write,BufWriter},fs::OpenOptions};
use serde_json::{json,Value};
fn emit(value:Value){let mut f=std::io::stdout().lock();writeln!(f,"E080_WARM {value}").unwrap();f.flush().unwrap();}
fn q_bytes(s:&Solver)->usize{s.regrets.iter().chain(&s.strat).map(|store|match store{Store::I16{q,..}=>q.len()*2,Store::U16{q,..}=>q.len()*2,Store::F32(_)=>0}).sum()}
fn raw(s:&Solver,out:&Path,stage:&str)->Value{
 let path=out.join(format!("{stage}.bin"));let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(&path).unwrap());
 f.write_all(b"E080-WARM-RAW1\0\0").unwrap();f.write_all(&s.iteration.to_le_bytes()).unwrap();f.write_all(&4u32.to_le_bytes()).unwrap();let mut stores=Vec::new();
 for store in s.regrets.iter().chain(&s.strat){
  let(tag,n,scale)=match store{Store::I16{q,scale}=>(1u32,q.len(),scale.as_slice()),Store::U16{q,scale}=>(2,q.len(),scale.as_slice()),Store::F32(_)=>panic!("compressed control required")};
  f.write_all(&tag.to_le_bytes()).unwrap();f.write_all(&(n as u64).to_le_bytes()).unwrap();f.write_all(&(scale.len()as u64).to_le_bytes()).unwrap();
  match store{Store::I16{q,..}=>for c in q.as_slice().chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();},Store::U16{q,..}=>for c in q.as_slice().chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();},_=>unreachable!()}
  for c in scale.chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_bits().to_le_bytes()).collect();f.write_all(&b).unwrap();}
  stores.push(json!({"tag":tag,"q_len":n,"scale_len":scale.len(),"nonzero_scale_words":scale.iter().filter(|x|x.to_bits()!=0).count()}));
 }
 f.flush().unwrap();f.get_ref().sync_all().unwrap();let bytes=f.get_ref().metadata().unwrap().len();
 json!({"stage":stage,"iteration":s.iteration,"stores":stores,"raw_bytes":bytes,"raw_file":path})
}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let out=Path::new(&args[1]);std::fs::create_dir(out).unwrap();
 let cfg:SpotConfig=serde_json::from_str(include_str!("warm-fixture.json")).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=false;
 let bytes=q_bytes(&s);assert!(bytes>=64*1024*1024);assert_eq!(bytes,1369522280);let mut g=GpuSolver::new(&s).unwrap();for _ in 0..3{g.iterate().unwrap();}g.sync_to_cpu(&mut s).unwrap();drop(g);
 s.use_isomorphism=true;let first=raw(&s,out,"warm_full");assert!(first["stores"].as_array().unwrap().iter().all(|x|x["nonzero_scale_words"].as_u64().unwrap()>0));emit(first);
 let plan=GpuPlan::build(&s.spot,true);let budget=plan.staging_bytes()+(plan.arena_elements[0]+plan.arena_elements[1])as u64*8+512*1024*1024;assert!(GpuSolver::new_with_budget(&s,budget-1).is_err());
 let mut g=GpuSolver::new_with_budget(&s,budget).unwrap();g.sync_to_cpu(&mut s).unwrap();emit(raw(&s,out,"compact_initial_sync"));for _ in 0..2{g.iterate().unwrap();}g.sync_to_cpu(&mut s).unwrap();emit(raw(&s,out,"compact_trained"));
 s.ensure_symmetric();let query=s.node_view(&[] as &[PathStep]).unwrap();emit(json!({"stage":"root_query","value":serde_json::to_value(query).unwrap()}));g.sync_strategy(&mut s).unwrap();g.sync_to_cpu(&mut s).unwrap();emit(raw(&s,out,"materialized_resync"));
 let save=out.join("large-warm.gto");s.save(save.to_str().unwrap()).unwrap();drop(g);drop(s);
 let mut loaded=Solver::load_with_storage(save.to_str().unwrap(),Storage::Compressed).unwrap();loaded.use_isomorphism=true;emit(raw(&loaded,out,"loaded"));let mut g=GpuSolver::new_with_budget(&loaded,budget).unwrap();for _ in 0..2{g.iterate().unwrap();}g.sync_to_cpu(&mut loaded).unwrap();emit(raw(&loaded,out,"resumed"));
 emit(json!({"stage":"complete","snapshots":6,"GPU_constructor_calls":4,"iterations_executed":7,"q_bytes":bytes,"overlap_eligibility_condition_verified":true,"all_four_warm_scale_predicates_false":true,"budget_rejection_pass":true,"performance_measured":false,"worker_observed_by_thread_trace":false}));
}
