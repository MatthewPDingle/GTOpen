#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
use solver::Solver;
use std::path::Path;
use serde_json::Value;
pub enum GpuSolver{Baseline(baseline::GpuSolver),Candidate(candidate::GpuSolver)}
macro_rules! call{($self:expr,$method:ident($($arg:expr),*))=>{match $self{GpuSolver::Baseline(x)=>x.$method($($arg),*),GpuSolver::Candidate(x)=>x.$method($($arg),*)}};}
impl GpuSolver{
 pub fn new(s:&Solver)->Result<Self,String>{match crate::D257_ARM.load(std::sync::atomic::Ordering::SeqCst){0=>Ok(Self::Baseline(baseline::GpuSolver::new(s)?)),1=>Ok(Self::Candidate(candidate::GpuSolver::new(s)?)),_=>Err("unbound diagnostic arm".into())}}
 pub fn d257_arm(&self)->usize{match self{Self::Baseline(_)=>0,Self::Candidate(_)=>1}}
 pub fn d257_discount_region(&self)->[u64;2]{call!(self,d257_discount_region())}
 pub fn iterate(&mut self)->Result<(),String>{call!(self,iterate())}
 pub fn exploitability(&mut self,s:&Solver)->Result<f64,String>{call!(self,exploitability(s))}
 pub fn sync_to_cpu(&mut self,s:&mut Solver)->Result<(),String>{call!(self,sync_to_cpu(s))}
 pub fn sync_strategy(&mut self,s:&mut Solver)->Result<(),String>{call!(self,sync_strategy(s))}
 pub fn update_locks(&mut self,s:&Solver)->Result<(),String>{call!(self,update_locks(s))}
 pub fn research_continuation_sweep(&mut self,p:usize,t:u32,own:&[f32],opp:&[f32])->Result<Vec<f32>,String>{call!(self,research_continuation_sweep(p,t,own,opp))}
 pub fn d150_validate(&self,s:&Solver,path:&Path,fresh:bool)->Value{call!(self,d150_validate(s,path,fresh))}
 pub fn d150_snapshot(&self,path:&Path,p:usize)->(Vec<Vec<u32>>,Value,Vec<u32>){call!(self,d150_snapshot(path,p))}
 pub fn d150_clobber(&mut self,before:&Path,after:&Path,p:usize,epoch:usize)->Value{call!(self,d150_clobber(before,after,p,epoch))}
}
