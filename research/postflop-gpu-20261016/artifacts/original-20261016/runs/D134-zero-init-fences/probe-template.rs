#![allow(dead_code,unused_imports)]
pub use solver::*;
use cudarc::driver::{CudaSlice,CudaStream,DeviceRepr};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf},sync::Arc,time::Instant};
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;

// D134_OS_BRIDGE

fn emit(value:Value){let mut out=std::io::stdout().lock();writeln!(out,"D134 {value}").unwrap();out.flush().unwrap();}
pub trait Word:DeviceRepr+Clone+Default{fn append(&self,out:&mut Vec<u32>);}
impl Word for u32{fn append(&self,out:&mut Vec<u32>){out.push(*self);}}
impl Word for i32{fn append(&self,out:&mut Vec<u32>){out.push(*self as u32);}}
impl Word for f32{fn append(&self,out:&mut Vec<u32>){out.push(self.to_bits());}}
impl Word for u64{fn append(&self,out:&mut Vec<u32>){out.push(*self as u32);out.push((*self>>32)as u32);}}
impl Word for i64{fn append(&self,out:&mut Vec<u32>){(*self as u64).append(out);}}
fn words<T:Word>(values:&[T])->Vec<u32>{let mut out=Vec::with_capacity(values.len()*std::mem::size_of::<T>()/4);for v in values{v.append(&mut out);}out}
fn write_words(out:&mut BufWriter<File>,values:&[u32]){for v in values{out.write_all(&v.to_le_bytes()).unwrap();}}
fn frame_header(out:&mut BufWriter<File>,kind:u32,name:&str,count:usize){out.write_all(&kind.to_le_bytes()).unwrap();out.write_all(&(name.len()as u32).to_le_bytes()).unwrap();out.write_all(name.as_bytes()).unwrap();out.write_all(&(count as u64).to_le_bytes()).unwrap();}
pub fn capture<T:Word>(s:&Arc<CudaStream>,name:&str,d:&CudaSlice<T>,expected:&[T],out:&mut BufWriter<File>)->Value{
 assert_eq!(d.len(),expected.len(),"length {name}");
 let actual=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();let actual=words(&actual);let expected=words(expected);assert_eq!(actual,expected,"full device {name}");
 frame_header(out,1,name,actual.len());write_words(out,&expected);write_words(out,&actual);
 json!({"name":name,"encoding":"explicit expected and actual u32 words","words":actual.len(),"full_exact":true})
}
pub fn capture_zero(s:&Arc<CudaStream>,name:&str,d:&CudaSlice<f32>,out:&mut BufWriter<File>)->Value{
 let actual=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();assert_eq!(actual.len(),d.len());let all_bits=actual.iter().fold(0u32,|bits,v|bits|v.to_bits());assert_eq!(all_bits,0,"all actual positive-zero words {name}");
 // This run record losslessly represents every verified word. No sampling,
 // checksum cancellation or multi-gigabyte duplicate zero files.
 frame_header(out,0,name,actual.len());out.write_all(&all_bits.to_le_bytes()).unwrap();
 json!({"name":name,"encoding":"verified positive-zero run","words":actual.len(),"all_actual_bits_OR":all_bits,"full_exact":true})
}
pub fn expected_arena(s:&Solver,p:&solver::gpu::plan::GpuPlan,seat:usize,which:usize)->Vec<f32>{
 let store=if which==0{&s.regrets[seat]}else{&s.strat[seat]};let mut out=vec![0.0;p.arena_elements[seat]];let nh=s.spot.hands[seat].len();
 for(i,node)in s.spot.tree.nodes.iter().enumerate(){
  if node.kind!=solver::tree::KIND_ACTION||node.player as usize!=seat{continue;}
  let off=p.node_data_off[i];if off==u64::MAX{continue;}
  let n=node.num_children as usize*nh;unsafe{store.read_f32(i as u32,node.data_offset,n,&mut out[off as usize..off as usize+n]);}
 }
 out
}
fn zero_source(s:&Solver)->bool{[&s.regrets[0],&s.regrets[1],&s.strat[0],&s.strat[1]].iter().all(|store|match store{
 solver::store::Store::I16{q,scale}=>scale.as_slice().iter().all(|v|v.to_bits()==0)&&q.as_slice().iter().fold(0u16,|bits,&v|bits|v as u16)==0,
 solver::store::Store::U16{q,scale}=>scale.as_slice().iter().all(|v|v.to_bits()==0)&&q.as_slice().iter().fold(0u16,|bits,&v|bits|v)==0,
 solver::store::Store::F32(v)=>v.as_slice().iter().all(|v|v.to_bits()==0),
 })}
enum Engine{Baseline(baseline::GpuSolver),Candidate(candidate::GpuSolver)}
impl Engine{
 fn new(arm:&str,s:&Solver)->Self{match arm{"baseline"=>Self::Baseline(baseline::GpuSolver::new(s).unwrap()),"candidate"=>Self::Candidate(candidate::GpuSolver::new(s).unwrap()),_=>panic!("arm")}}
 fn synchronize(&self){match self{Self::Baseline(g)=>g.synchronize().unwrap(),Self::Candidate(g)=>g.synchronize().unwrap()}}
 fn validate(&self,s:&Solver,path:&Path,zero:bool)->Value{match self{Self::Baseline(g)=>g.d134_validate(s,path,zero),Self::Candidate(g)=>g.d134_validate(s,path,zero)}}
}
fn run_case(arm:&str,s:&Solver,out:&Path,id:&str,timed:bool)->Value{
 let is_zero=zero_source(s);let before=resource_os_sample();let cpu=before["cpu_ticks100ns"].as_u64().unwrap();let start=Instant::now();let gpu=Engine::new(arm,s);gpu.synchronize();let ms=start.elapsed().as_secs_f64()*1000.;let after=resource_os_sample();let cpu_ms=(after["cpu_ticks100ns"].as_u64().unwrap()-cpu)as f64/10000.;
 let proof=gpu.validate(s,&out.join(format!("{id}-device-frame.bin")),is_zero);let record=json!({"stage":"case","id":id,"arm":arm,"component_ms":ms,"CPU_ms":cpu_ms,"OS_before":before,"OS_after":after,"all_four_host_stores_positive_zero":is_zero,"solver_iteration":s.iteration,"board":s.spot.config.board,"nodes":s.spot.tree.nodes.len(),"storage":format!("{:?}",s.storage),"component_only":true,"timed":timed,"proof":proof,"kernel_launches":0});emit(record.clone());drop(gpu);record
}
fn ability(out:&Path){
 for bits in[1u32,0x8000_0000,0x7fc0_1234]{let v=[0.0,f32::from_bits(bits),0.0];assert_ne!(v.iter().fold(0u32,|a,v|a|v.to_bits()),0);}
 let mut cfg:SpotConfig=serde_json::from_str(include_str!("tiny.json")).unwrap();cfg.tree.rake_pct=0.;let spot=Arc::new(Spot::new(cfg).unwrap());
 let mut comparisons=0;
 for storage in[solver::store::Storage::Compressed,solver::store::Storage::F32]{for warm in[false,true]{
  let mut s=Solver::with_storage(spot.clone(),storage);if warm{s.iterate();}
  let id=format!("{:?}-{}",storage,if warm{"warm"}else{"fresh"});
  let b=run_case("baseline",&s,out,&("B-".to_owned()+&id),false);let c=run_case("candidate",&s,out,&("C-".to_owned()+&id),false);assert_eq!(b["proof"],c["proof"]);assert_eq!(std::fs::read(out.join(format!("B-{id}-device-frame.bin"))).unwrap(),std::fs::read(out.join(format!("C-{id}-device-frame.bin"))).unwrap());comparisons+=1;
  let be=baseline::GpuSolver::new_with_budget(&s,1).err().unwrap();let ce=candidate::GpuSolver::new_with_budget(&s,1).err().unwrap();assert_eq!(be,ce);assert!(be.contains("budget"));
 }}emit(json!({"stage":"ability_complete","comparisons":comparisons,"fresh_warm_compressed_F32":true,"four_budget_rejections_equal":true,"injected_nonzero_OR_controls_rejected":3,"kernel_launches":0,"performance_score":false}));
}
fn main(){
 let arm=std::env::args().nth(1).unwrap();let out=PathBuf::from(std::env::args().nth(2).unwrap());assert!(out.is_dir());
 if arm=="ability"{ability(&out);return;}
 assert!(arm=="baseline"||arm=="candidate");let mut records=Vec::new();
 for(i,(name,board,rake))in[("rainbow","Ks7h2d",0.),("two-tone","Ks7s2d",0.05),("river","Ks7h2dQhTc",0.05)].into_iter().enumerate(){
  let mut cfg:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();cfg.board=board.into();cfg.tree.rake_pct=rake;cfg.tree.rake_cap=3.;let s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),solver::store::Storage::Compressed);assert!(zero_source(&s));let id=format!("{i}-{name}");records.push(run_case(&arm,&s,&out,&id,true));
 }emit(json!({"stage":"complete","arm":arm,"cases":records.len(),"kernel_launches":0,"full_solver_executions":0,"component_only":true,"all_device_fields_exact":true,"all_zero_fields_scanned_in_full":true,"candidate_adopted":false}));
}
