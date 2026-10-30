#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
use serde_json::json;
use std::{sync::Arc,io::Write};
fn set_map(s:&mut Solver,pattern:&str){s.locks.clear();let root=&s.spot.tree.nodes[0];let n=root.num_children as usize*s.spot.hands[root.player as usize].len();assert!(n>1);match pattern{
 "empty"=>{},"valid_root"=>{s.locks.insert(0,vec![1.0/root.num_children as f32;n]);},"empty_root"=>{s.locks.insert(0,vec![]);},"empty_terminal"=>{let i=s.spot.tree.nodes.iter().position(|n|n.kind!=solver::tree::KIND_ACTION).unwrap();s.locks.insert(i as u32,vec![]);},"one_zero_root"=>{s.locks.insert(0,vec![0.0]);},_=>panic!("pattern")}}
fn record(s:&Solver,b:&baseline::GpuSolver,c:&candidate::GpuSolver,id:usize,stage:&str,pattern:&str)->serde_json::Value{
 let mut locks:Vec<_>=s.locks.iter().map(|(&node,v)|json!({"node":node,"bits":v.iter().map(|x|x.to_bits()).collect::<Vec<_>>()})).collect();locks.sort_by_key(|v|v["node"].as_u64().unwrap());let expected_absent=s.locks.is_empty();let bs=b.d218_state();let cs=c.d218_state();assert_eq!(bs["wrapper_bytes"],4448);assert_eq!(cs["wrapper_bytes"],4448);assert_eq!(cs["absent"],expected_absent);assert_eq!(bs["offsets"],cs["offsets"]);assert_eq!(bs["sigma_bits"],cs["sigma_bits"]);assert!(!bs["training_graphs_present"].as_bool().unwrap()&&!cs["training_graphs_present"].as_bool().unwrap());assert_eq!(bs["eval_graphs_present"],json!([false,false]));assert_eq!(cs["eval_graphs_present"],json!([false,false]));
 json!({"case":id,"stage":stage,"pattern":pattern,"node_count":s.spot.tree.nodes.len(),"CPU_locks":locks,"expected_absent":expected_absent,"baseline":bs,"candidate":cs})}
fn main(){let out=std::path::PathBuf::from(std::env::args().nth(1).unwrap());let mut config:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();config.board="Ks7h2dQhTc".into();let spot=Arc::new(Spot::new(config).unwrap());let mut records=Vec::new();let mut id=0;
 for storage in [store::Storage::Compressed,store::Storage::F32]{for algo in [Algorithm::Dcfr,Algorithm::CfrPlus]{for initial in ["empty","valid_root","empty_root","empty_terminal","one_zero_root"]{
  let mut s=Solver::with_storage(spot.clone(),storage);s.algo=algo;set_map(&mut s,initial);let mut b=baseline::GpuSolver::new(&s).unwrap();let mut c=candidate::GpuSolver::new(&s).unwrap();records.push(record(&s,&b,&c,id,"constructor",initial));
  for pattern in ["valid_root","empty_root","empty"]{set_map(&mut s,pattern);b.update_locks(&s).unwrap();c.update_locks(&s).unwrap();records.push(record(&s,&b,&c,id,"update",pattern));}
  drop(c);drop(b);drop(s);println!("D218_CASE {}",json!({"id":id,"exact":true}));std::io::stdout().flush().unwrap();id+=1;
 }}}
 assert_eq!(id,20);assert_eq!(records.len(),80);let mut f=std::fs::OpenOptions::new().create_new(true).write(true).open(out).unwrap();f.write_all(serde_json::to_string_pretty(&json!({"cases":20,"constructor_pairs":20,"update_pairs":60,"records":records,"application_kernel_launches":0,"solver_iterations":0,"malformed_vectors_only_constructor_and_table_updates_never_kernel_inputs":true})).unwrap().as_bytes()).unwrap();f.sync_all().unwrap();println!("D218_COMPLETE 20 cases 80 states no kernels");}
