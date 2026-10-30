use std::ffi::c_void;
use std::sync::Mutex;
static D174_EVENTS:Mutex<Vec<serde_json::Value>>=Mutex::new(Vec::new());
pub fn d174_mark(role:&'static str,label:&'static str) {
 D174_EVENTS.lock().unwrap().push(serde_json::json!({"role":role,"label":label,"thread":format!("{:?}",std::thread::current().id())}));
}
#[repr(C)]#[derive(Default)]struct D174FileTime{lo:u32,hi:u32}
impl D174FileTime{fn ticks(&self)->u64{self.lo as u64|((self.hi as u64)<<32)}}
#[link(name="kernel32")]
extern "system" {
 fn GetCurrentProcess()->*mut c_void;
 fn GetProcessTimes(process:*mut c_void,created:*mut D174FileTime,exit:*mut D174FileTime,kernel:*mut D174FileTime,user:*mut D174FileTime)->i32;
 fn GetModuleHandleW(name:*const u16)->*mut c_void;
}
fn d174_cpu()->u64 {
 let(mut c,mut e,mut k,mut u)=(D174FileTime::default(),D174FileTime::default(),D174FileTime::default(),D174FileTime::default());
 assert_ne!(unsafe{GetProcessTimes(GetCurrentProcess(),&mut c,&mut e,&mut k,&mut u)},0);k.ticks()+u.ticks()
}
fn d174_driver_loaded()->bool{let dll:Vec<u16>="nvcuda.dll\0".encode_utf16().collect();!unsafe{GetModuleHandleW(dll.as_ptr())}.is_null()}

#[test]
fn d174_budget_failure_costs() {
 assert!(!d174_driver_loaded());
 let order=[["baseline","candidate"],["candidate","baseline"],["baseline","candidate"]];
 for (fixture,board,rake) in FIXTURES {
  let mut config:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();config.board=board.into();config.tree.rake_pct=rake;config.tree.rake_cap=3.;
  let host=Solver::with_storage(Arc::new(Spot::new(config).unwrap()),Storage::Compressed);
  for (pair,arms) in order.iter().enumerate(){
   let mut errors=Vec::new();
   for role in arms {
    let before=state_fingerprint(&host,0.);D174_EVENTS.lock().unwrap().clear();
    let cpu_start=d174_cpu();let clock=Instant::now();
    let outcome=match *role {"baseline"=>reference::GpuSolver::new_with_budget(&host,0).err().unwrap(),"candidate"=>changed::GpuSolver::new_with_budget(&host,0).err().unwrap(),_=>unreachable!()};
    let wall_ms=clock.elapsed().as_secs_f64()*1000.;let cpu_ms=(d174_cpu()-cpu_start) as f64/10000.;
    let events=D174_EVENTS.lock().unwrap().clone();assert!(!d174_driver_loaded());
    let after=state_fingerprint(&host,0.);assert_eq!(before,after);assert!(outcome.contains("budget 0 MB"));errors.push(outcome.clone());
    println!("D174_RESULT {}",serde_json::json!({"fixture":fixture,"board":board,"nodes":host.spot.tree.nodes.len(),"pair":pair,"role":role,"budget_bytes":0,"error":outcome,"wall_ms":wall_ms,"CPU_ms":cpu_ms,"events":events,"before_CPU_fingerprint":before,"after_CPU_fingerprint":after,"nvcuda_loaded":false,"application_kernels":0,"performance_qualification_sample":false}));
   }
   assert_eq!(errors[0],errors[1]);
  }
 }
 // Unsupported algorithms reject before planning/scans/CUDA, including the moved setup.
 let mut config:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();config.board="Ks7h2dQhTc".into();
 let mut host=Solver::with_storage(Arc::new(Spot::new(config).unwrap()),Storage::Compressed);host.algo=Algorithm::PcfrPlus;
 for role in ["baseline","candidate"] {
  D174_EVENTS.lock().unwrap().clear();let before=state_fingerprint(&host,0.);
  let error=if role=="baseline" {reference::GpuSolver::new_with_budget(&host,u64::MAX).err().unwrap()} else {changed::GpuSolver::new_with_budget(&host,u64::MAX).err().unwrap()};
  assert_eq!(error,"GPU solver supports dcfr/cfr+ only");assert_eq!(before,state_fingerprint(&host,0.));assert!(!d174_driver_loaded());
  println!("D174_UNSUPPORTED {}",serde_json::json!({"role":role,"error":error,"events":D174_EVENTS.lock().unwrap().clone(),"nvcuda_loaded":false,"CPU_fingerprint":before}));
 }
 println!("D174_COMPLETE {}",serde_json::json!({"budget_calls":18,"unsupported_calls":2,"CPU_immutability_checks":20,"nvcuda_loaded":false,"application_kernels":0,"all_constructor_calls_returned":true}));
}
