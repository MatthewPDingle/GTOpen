#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
use solver::Solver;
use std::path::Path;
use serde_json::{json,Value};
enum Inner{Baseline(baseline::GpuSolver),Candidate(candidate::GpuSolver)}
pub struct GpuSolver{inner:Inner,pub forward:Vec<u32>,inverse:Vec<u32>,pub selected:bool,pub info:Value}
macro_rules! call{($self:expr,$method:ident($($arg:expr),*))=>{match &$self.inner{Inner::Baseline(x)=>x.$method($($arg),*),Inner::Candidate(x)=>x.$method($($arg),*)}};}
macro_rules! call_mut{($self:expr,$method:ident($($arg:expr),*))=>{match &mut $self.inner{Inner::Baseline(x)=>x.$method($($arg),*),Inner::Candidate(x)=>x.$method($($arg),*)}};}
impl GpuSolver{
 pub fn new(s:&Solver)->Result<Self,String>{
  let arm=crate::D271_ARM.load(std::sync::atomic::Ordering::SeqCst);
  let inner=match arm{0=>Inner::Baseline(baseline::GpuSolver::new(s)?),1=>Inner::Candidate(candidate::GpuSolver::new(s)?),_=>return Err("unbound diagnostic arm".into())};
  let(plan,forward,inverse,info)=match &inner{Inner::Baseline(x)=>x.d271_map_data(s),Inner::Candidate(x)=>x.d271_map_data(s)};
  let call=crate::D271_BINDS[arm].load(std::sync::atomic::Ordering::SeqCst);
  let output=crate::D271_OUTPUT.get().unwrap();let stem=format!("map-{arm}-{call:03}");
  crate::dump_baseline(&plan,&output.join(format!("{stem}.plan.bin")));
  crate::d271_dump_maps(&output.join(format!("{stem}.maps.bin")),&forward,&inverse);
  {use std::io::Write;let mut f=std::fs::OpenOptions::new().write(true).create_new(true).open(output.join(format!("{stem}.kinds.bin"))).unwrap();
   for n in &s.spot.tree.nodes{f.write_all(&[n.kind]).unwrap();}f.sync_all().unwrap();}
  println!("D271_METADATA_BIND {}",json!({"arm":arm,"call":call,"plan_file":format!("{stem}.plan.bin"),"maps_file":format!("{stem}.maps.bin"),"kinds_file":format!("{stem}.kinds.bin"),"info":info}));
  let selected=info["ordered"].as_bool().unwrap();
  Ok(Self{inner,forward,inverse,selected,info})
 }
 pub fn d271_arm(&self)->usize{match &self.inner{Inner::Baseline(_)=>0,Inner::Candidate(_)=>1}}
 pub fn iterate(&mut self)->Result<(),String>{call_mut!(self,iterate())}
 pub fn exploitability(&mut self,s:&Solver)->Result<f64,String>{call_mut!(self,exploitability(s))}
 pub fn sync_to_cpu(&mut self,s:&mut Solver)->Result<(),String>{call_mut!(self,sync_to_cpu(s))}
 pub fn sync_strategy(&mut self,s:&mut Solver)->Result<(),String>{call_mut!(self,sync_strategy(s))}
 pub fn update_locks(&mut self,s:&Solver)->Result<(),String>{call_mut!(self,update_locks(s))}
 pub fn research_continuation_sweep(&mut self,p:usize,t:u32,own:&[f32],opp:&[f32])->Result<Vec<f32>,String>{call_mut!(self,research_continuation_sweep(p,t,own,opp))}
 pub fn d150_validate(&self,s:&Solver,path:&Path,fresh:bool)->Value{call!(self,d150_validate(s,path,fresh))}
 pub fn d271_same_constructor(&self,a:&Path,b:&Path){
  let original=std::fs::read(a).unwrap();let actual=std::fs::read(b).unwrap();
  assert_eq!(original,crate::d271_normalize_frame(actual,&self.forward,&self.inverse),"all original constructor frame bytes after exact metadata inverse");
 }
 pub fn d150_snapshot(&self,path:&Path,p:usize)->(Vec<Vec<u32>>,Value,Vec<u32>){
  let(mut image,info,physical)=call!(self,d150_snapshot(path,p));
  crate::d271_normalize_image(&mut image,&self.forward,&self.inverse);(image,info,physical)
 }
 pub fn d150_clobber(&mut self,before:&Path,after:&Path,p:usize,epoch:usize)->Value{call_mut!(self,d150_clobber(before,after,p,epoch))}
}
