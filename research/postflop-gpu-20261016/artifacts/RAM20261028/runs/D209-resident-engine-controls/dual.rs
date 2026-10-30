use solver::Solver;
use std::path::Path;
pub enum GpuSolver{Baseline(crate::baseline::GpuSolver),Candidate(crate::candidate::GpuSolver)}
impl GpuSolver{
 pub fn new(s:&Solver)->Result<Self,String>{if crate::D209_ARM.load(std::sync::atomic::Ordering::SeqCst)==0{crate::baseline::GpuSolver::new(s).map(Self::Baseline)}else{crate::candidate::GpuSolver::new(s).map(Self::Candidate)}}
 pub fn iterate(&mut self)->Result<(),String>{match self{Self::Baseline(g)=>g.iterate(),Self::Candidate(g)=>g.iterate()}}
 pub fn exploitability(&mut self,s:&Solver)->Result<f64,String>{match self{Self::Baseline(g)=>g.exploitability(s),Self::Candidate(g)=>g.exploitability(s)}}
 pub fn sync_strategy(&mut self,s:&mut Solver)->Result<(),String>{match self{Self::Baseline(g)=>g.sync_strategy(s),Self::Candidate(g)=>g.sync_strategy(s)}}
 pub fn sync_to_cpu(&mut self,s:&mut Solver)->Result<(),String>{match self{Self::Baseline(g)=>g.sync_to_cpu(s),Self::Candidate(g)=>g.sync_to_cpu(s)}}
 pub fn update_locks(&mut self,s:&Solver)->Result<(),String>{match self{Self::Baseline(g)=>g.update_locks(s),Self::Candidate(g)=>g.update_locks(s)}}
 pub fn research_continuation_sweep(&mut self,p:usize,t:u32,own:&[f32],opp:&[f32])->Result<Vec<f32>,String>{match self{Self::Baseline(g)=>g.research_continuation_sweep(p,t,own,opp),Self::Candidate(g)=>g.research_continuation_sweep(p,t,own,opp)}}
 pub fn d150_validate(&self,s:&Solver,path:&Path,fresh:bool)->serde_json::Value{match self{Self::Baseline(g)=>g.d150_validate(s,path,fresh),Self::Candidate(g)=>g.d150_validate(s,path,fresh)}}
 pub fn d150_snapshot(&self,path:&Path,p:usize)->(Vec<Vec<u32>>,serde_json::Value,Vec<u32>){match self{Self::Baseline(g)=>g.d150_snapshot(path,p),Self::Candidate(g)=>g.d150_snapshot(path,p)}}
 pub fn d150_clobber(&mut self,before:&Path,after:&Path,p:usize,epoch:usize)->serde_json::Value{match self{Self::Baseline(g)=>g.d150_clobber(before,after,p,epoch),Self::Candidate(g)=>g.d150_clobber(before,after,p,epoch)}}
 pub fn d209_state(&self)->serde_json::Value{match self{Self::Baseline(g)=>g.d209_state(),Self::Candidate(g)=>g.d209_state()}}
}
