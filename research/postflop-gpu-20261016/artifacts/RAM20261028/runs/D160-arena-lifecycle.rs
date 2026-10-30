use std::{ffi::c_void,io::Write,mem::{align_of,size_of},ptr,sync::atomic::{AtomicUsize,Ordering},time::Instant};
use rayon::prelude::*;
#[path="store.rs"] mod store;
#[global_allocator] static GLOBAL:mimalloc::MiMalloc=mimalloc::MiMalloc;
#[link(name="kernel32")]
extern "system" {fn VirtualAlloc(address:*mut c_void,bytes:usize,kind:u32,protection:u32)->*mut c_void;fn VirtualFree(address:*mut c_void,bytes:usize,kind:u32)->i32;}
static ALLOCS:AtomicUsize=AtomicUsize::new(0);
static FREES:AtomicUsize=AtomicUsize::new(0);
const THRESHOLD:usize=64*1024*1024;
// Closed numeric corpus only; these three types have all-zero Default bits.
trait Word:Copy+Default+Send+Sync {fn bits(self)->u32;fn value(index:usize,round:usize,arena:usize)->Self;fn zero(slice:&[Self])->bool;}
impl Word for i16 {
 fn bits(self)->u32 {self as u16 as u32}
 fn value(i:usize,r:usize,a:usize)->Self {(i.wrapping_mul(17).wrapping_add(r*13+a*19)) as u16 as i16}
 fn zero(s:&[Self])->bool {s.iter().fold(0u16,|v,&x|v|x as u16)==0}
}
impl Word for u16 {
 fn bits(self)->u32 {self as u32}
 fn value(i:usize,r:usize,a:usize)->Self {(i.wrapping_mul(17).wrapping_add(r*13+a*19)) as u16}
 fn zero(s:&[Self])->bool {s.iter().fold(0u16,|v,&x|v|x)==0}
}
impl Word for f32 {
 fn bits(self)->u32 {self.to_bits()}
 fn value(i:usize,r:usize,a:usize)->Self {Self::from_bits(0x3f000000|((i.wrapping_mul(17).wrapping_add(r*13+a*19)) as u32&0x7fffff))}
 fn zero(s:&[Self])->bool {s.iter().all(|x|x.to_bits()==0)}
}
struct Vm<T:Word>{ptr:*mut T,len:usize}
impl<T:Word> Vm<T> {
 fn new(len:usize)->Self {
  let bytes=len.checked_mul(size_of::<T>()).unwrap();assert!(bytes>=THRESHOLD && bytes<=isize::MAX as usize);
  let p=unsafe{VirtualAlloc(ptr::null_mut(),bytes,0x1000|0x2000,0x04)};
  assert!(!p.is_null(),"VirtualAlloc failed");assert_eq!(p as usize%align_of::<T>(),0);
  ALLOCS.fetch_add(1,Ordering::Relaxed);Self{ptr:p.cast(),len}
 }
 fn read(&self)->&[T]{unsafe{std::slice::from_raw_parts(self.ptr,self.len)}}
 fn write(&mut self)->&mut[T]{unsafe{std::slice::from_raw_parts_mut(self.ptr,self.len)}}
}
impl<T:Word> Drop for Vm<T>{fn drop(&mut self){assert_ne!(unsafe{VirtualFree(self.ptr.cast(),0,0x8000)},0,"VirtualFree failed");FREES.fetch_add(1,Ordering::Relaxed);}}
enum Buf<T:Word>{Original(store::ArenaBuf<T>),Pages(Vm<T>)}
impl<T:Word> Buf<T>{
 fn new(n:usize,candidate:bool)->Self {if candidate&&n.checked_mul(size_of::<T>()).unwrap()>=THRESHOLD {Self::Pages(Vm::new(n))}else{Self::Original(store::ArenaBuf::new(n))}}
 fn read(&self)->&[T]{match self{Self::Original(x)=>x.as_slice(),Self::Pages(x)=>x.read()}}
 fn write(&mut self)->&mut[T]{match self{Self::Original(x)=>x.as_mut_slice(),Self::Pages(x)=>x.write()}}
 fn zero(&self)->bool {T::zero(std::hint::black_box(self.read()))}
 fn pattern(&mut self,round:usize,arena:usize){
  let s=self.write();let chunk=s.len().div_ceil(16).max(1);
  s.par_chunks_mut(chunk).enumerate().for_each(|(c,x)|{for(i,v)in x.iter_mut().enumerate(){*v=T::value(c*chunk+i,round,arena);}});
 }
 fn verify(&self,round:usize,arena:usize)->u64{
  // A serial complete read after joined writes; verifies every element,not samples.
  let mut sum=0u64;for(i,&x)in std::hint::black_box(self.read()).iter().enumerate(){assert_eq!(x.bits(),T::value(i,round,arena).bits());sum=sum.wrapping_add(x.bits() as u64);}sum
 }
}
enum Arena{Signed{q:Buf<i16>,scale:Buf<f32>},Unsigned{q:Buf<u16>,scale:Buf<f32>}}
impl Arena{
 fn signed(n:usize,nodes:usize,c:bool)->Self{Self::Signed{q:Buf::new(n,c),scale:Buf::new(nodes,c)}}
 fn unsigned(n:usize,nodes:usize,c:bool)->Self{Self::Unsigned{q:Buf::new(n,c),scale:Buf::new(nodes,c)}}
 fn zero(&self)->bool{match self{Self::Signed{q,scale}=>scale.zero()&&q.zero(),Self::Unsigned{q,scale}=>scale.zero()&&q.zero()}}
 fn pattern(&mut self,r:usize,a:usize){match self{Self::Signed{q,scale}=>{q.pattern(r,a*2);scale.pattern(r,a*2+1)},Self::Unsigned{q,scale}=>{q.pattern(r,a*2);scale.pattern(r,a*2+1)}}}
 fn verify(&self,r:usize,a:usize)->[u64;2]{match self{Self::Signed{q,scale}=>[q.verify(r,a*2),scale.verify(r,a*2+1)],Self::Unsigned{q,scale}=>[q.verify(r,a*2),scale.verify(r,a*2+1)]}}
}
fn ns(t:Instant)->u64{t.elapsed().as_nanos().try_into().unwrap()}
fn main(){
 let arm=std::env::args().nth(1).unwrap();assert!(arm=="baseline"||arm=="candidate");let candidate=arm=="candidate";
 rayon::ThreadPoolBuilder::new().num_threads(16).build_global().unwrap();assert_eq!(rayon::current_num_threads(),16);
 let fixtures:serde_json::Value=serde_json::from_str(include_str!("fixtures.json")).unwrap();
 for fixture in fixtures.as_array().unwrap(){
  let name=fixture["id"].as_str().unwrap();let nodes=fixture["nodes"].as_u64().unwrap()as usize;
  let n0=fixture["entries"][0].as_u64().unwrap()as usize;let n1=fixture["entries"][1].as_u64().unwrap()as usize;
  let before_a=ALLOCS.load(Ordering::Relaxed);let before_f=FREES.load(Ordering::Relaxed);
  let start=Instant::now();let t=Instant::now();
  // Same constructor order as Solver::with_storage: regret0,regret1,strategy0,strategy1.
  let mut arenas=[Arena::signed(n0,nodes,candidate),Arena::signed(n1,nodes,candidate),Arena::unsigned(n0,nodes,candidate),Arena::unsigned(n1,nodes,candidate)];
  let allocation_ns=ns(t);let t=Instant::now();for arena in &arenas{assert!(arena.zero());}let zero_scan_ns=ns(t);
  let mut rounds=Vec::new();let mut checksums=Vec::new();
  for round in 1..=2{
   let t=Instant::now();for(a,x)in arenas.iter_mut().enumerate(){x.pattern(round,a);}let write_ns=ns(t);
   let t=Instant::now();let sums:Vec<_>=arenas.iter().enumerate().map(|(a,x)|x.verify(round,a)).collect();let verify_ns=ns(t);
   checksums.push(sums);rounds.push(serde_json::json!({"write_ns":write_ns,"verify_ns":verify_ns}));
  }
  let t=Instant::now();drop(arenas);let drop_ns=ns(t);let complete_ns=ns(start);
  let allocations=ALLOCS.load(Ordering::Relaxed)-before_a;let frees=FREES.load(Ordering::Relaxed)-before_f;
  assert_eq!(allocations,frees);assert_eq!(allocations,if candidate&&name!="river"{4}else{0});
  println!("D160_ARENA {}",serde_json::json!({"fixture":name,"arm":arm,"CPU_arena_bytes":4*(n0+n1)+16*nodes,"q_entries":[n0,n1],"scale_entries":nodes,"allocation_ns":allocation_ns,"zero_scan_ns":zero_scan_ns,"rounds":rounds,"drop_ns":drop_ns,"complete_ns":complete_ns,"all_elements_verified":true,"checksums":checksums,"VM_allocations":allocations,"VM_releases":frees,"threads":16,"GPU_calls":0}));std::io::stdout().flush().unwrap();
 }
 assert_eq!(ALLOCS.load(Ordering::Relaxed),FREES.load(Ordering::Relaxed));
}
