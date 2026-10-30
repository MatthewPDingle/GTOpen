extern crate solver;
use cudarc::driver::{result,sys,CudaContext};
use rayon::prelude::*;
use serde_json::{json,Value};
use std::{ffi::c_void,fs::OpenOptions,io::Write,mem::{size_of,align_of},path::PathBuf,ptr,sync::{Arc,atomic::{AtomicUsize,Ordering}},time::Instant};
const THRESHOLD:usize=64*1024*1024;
#[repr(C)]struct SystemInfo{arch:u32,page_size:u32,min:*mut c_void,max:*mut c_void,mask:usize,count:u32,kind:u32,granularity:u32,level:u16,revision:u16}
#[repr(C)]struct Region{base:*mut c_void,allocation_base:*mut c_void,allocation_protect:u32,partition:u16,pad:u16,bytes:usize,state:u32,protect:u32,kind:u32}
#[link(name="kernel32")]extern "system"{
 fn VirtualAlloc(address:*mut c_void,bytes:usize,kind:u32,protection:u32)->*mut c_void;
 fn VirtualFree(address:*mut c_void,bytes:usize,kind:u32)->i32;
 fn VirtualQuery(address:*const c_void,info:*mut Region,bytes:usize)->usize;
 fn GetSystemInfo(info:*mut SystemInfo);fn GetLastError()->u32;
}
static HOST_ALLOCS:AtomicUsize=AtomicUsize::new(0);static HOST_FREES:AtomicUsize=AtomicUsize::new(0);
static VM_ALLOCS:AtomicUsize=AtomicUsize::new(0);static VM_FREES:AtomicUsize=AtomicUsize::new(0);
static REGISTER_CALLS:AtomicUsize=AtomicUsize::new(0);static REGISTERS:AtomicUsize=AtomicUsize::new(0);static UNREGISTERS:AtomicUsize=AtomicUsize::new(0);
fn counts()->[usize;7]{[&HOST_ALLOCS,&HOST_FREES,&VM_ALLOCS,&VM_FREES,&REGISTER_CALLS,&REGISTERS,&UNREGISTERS].map(|x|x.load(Ordering::Relaxed))}
fn rounded(bytes:usize,page:usize)->Option<usize>{if bytes==0||!page.is_power_of_two()||bytes>isize::MAX as usize{return None}let n=bytes.checked_add(page-1)?&!(page-1);if n>isize::MAX as usize{None}else{Some(n)}}
fn page_size()->usize{assert_eq!(size_of::<SystemInfo>(),48);let mut info: SystemInfo=unsafe{std::mem::zeroed()};unsafe{GetSystemInfo(&mut info)};assert!(info.page_size.is_power_of_two()&&info.page_size>=4096);info.page_size as usize}
fn released(base:*mut c_void){assert_eq!(size_of::<Region>(),48);let mut r:Region=unsafe{std::mem::zeroed()};assert_eq!(unsafe{VirtualQuery(base,&mut r,size_of::<Region>())},size_of::<Region>());assert_eq!(r.state,0x10000,"released owned reservation must be MEM_FREE");}
struct Original{ptr:*mut u32,len:usize}
impl Original{
 fn new(ctx:&Arc<CudaContext>,len:usize)->Result<Self,String>{ctx.bind_to_thread().map_err(|e|format!("{e:?}"))?;let bytes=len.checked_mul(4).ok_or("size overflow")?;let p=unsafe{result::malloc_host(bytes,0)}.map_err(|e|format!("{e:?}"))?;HOST_ALLOCS.fetch_add(1,Ordering::Relaxed);Ok(Self{ptr:p.cast(),len})}
 fn close(&mut self)->Result<(),String>{if self.ptr.is_null(){return Ok(())}let p=self.ptr;self.ptr=ptr::null_mut();unsafe{result::free_host(p.cast())}.map_err(|e|format!("{e:?}"))?;HOST_FREES.fetch_add(1,Ordering::Relaxed);Ok(())}
}
impl Drop for Original{fn drop(&mut self){if let Err(e)=self.close(){eprintln!("D280_CLEANUP_ERROR {e}");std::process::abort()}}}
struct Registered{ptr:*mut u32,len:usize,ctx:Arc<CudaContext>}
impl Registered{
 fn new(ctx:&Arc<CudaContext>,len:usize,page:usize,registration_size_override:Option<usize>)->Result<Self,String>{
  ctx.bind_to_thread().map_err(|e|format!("{e:?}"))?;let bytes=len.checked_mul(4).ok_or("size overflow")?;let backing=rounded(bytes,page).ok_or("bad rounded size")?;
  let p=unsafe{VirtualAlloc(ptr::null_mut(),backing,0x1000|0x2000,0x04)};if p.is_null(){return Err(format!("VirtualAlloc {}",unsafe{GetLastError()}))}VM_ALLOCS.fetch_add(1,Ordering::Relaxed);assert_eq!(p as usize%page,0);
  REGISTER_CALLS.fetch_add(1,Ordering::Relaxed);let registration=unsafe{sys::cuMemHostRegister_v2(p,registration_size_override.unwrap_or(backing),0)}.result();
  if let Err(error)=registration{assert_ne!(unsafe{VirtualFree(p,0,0x8000)},0,"registration failure cleanup VirtualFree");VM_FREES.fetch_add(1,Ordering::Relaxed);released(p);return Err(format!("registration rejected, reservation released: {error:?}"))}
  REGISTERS.fetch_add(1,Ordering::Relaxed);Ok(Self{ptr:p.cast(),len,ctx:ctx.clone()})
 }
 fn close(&mut self)->Result<(),String>{
  if self.ptr.is_null(){return Ok(())}let p=self.ptr;self.ptr=ptr::null_mut();
  // On any failure never release a potentially registered/inflight range.
  self.ctx.bind_to_thread().map_err(|e|format!("{e:?}"))?;unsafe{sys::cuMemHostUnregister(p.cast())}.result().map_err(|e|format!("unregister {e:?}"))?;UNREGISTERS.fetch_add(1,Ordering::Relaxed);
  if unsafe{VirtualFree(p.cast(),0,0x8000)}==0{return Err(format!("VirtualFree {}",unsafe{GetLastError()}))}VM_FREES.fetch_add(1,Ordering::Relaxed);released(p.cast());Ok(())
 }
}
impl Drop for Registered{fn drop(&mut self){if let Err(e)=self.close(){eprintln!("D280_CLEANUP_ERROR {e}");std::process::abort()}}}
enum Buffer{Original(Original),Registered(Registered)}
impl Buffer{
 fn new(ctx:&Arc<CudaContext>,len:usize,page:usize,candidate:bool)->Self{if candidate&&len.checked_mul(4).unwrap()>=THRESHOLD{Self::Registered(Registered::new(ctx,len,page,None).expect("registered allocation"))}else{Self::Original(Original::new(ctx,len).expect("original allocation"))}}
 fn parts(&self)->(*mut u32,usize){match self{Self::Original(x)=>(x.ptr,x.len),Self::Registered(x)=>(x.ptr,x.len)}}
 fn read(&self)->&[u32]{let(p,n)=self.parts();assert!(!p.is_null());unsafe{std::slice::from_raw_parts(p,n)}}
 fn write(&mut self)->&mut[u32]{let(p,n)=self.parts();assert!(!p.is_null());unsafe{std::slice::from_raw_parts_mut(p,n)}}
 fn close(&mut self){match self{Self::Original(x)=>x.close().expect("original close"),Self::Registered(x)=>x.close().expect("registered close")}}
}
fn pattern(i:usize,round:u32)->u32{let seed=0x243f6a88u32^round.wrapping_mul(0x85ebca6b);(i as u32).wrapping_mul(0x9e3779b9).wrapping_add(seed).rotate_left(7)^0xa5a55a5a}
struct RawWrite(*mut u32);
unsafe impl Send for RawWrite{} unsafe impl Sync for RawWrite{}
impl RawWrite{fn set(&self,i:usize,value:u32){unsafe{self.0.add(i).write(value)}}}
fn dump(buf:&Buffer,path:PathBuf,round:u32,page:usize){let mut file=OpenOptions::new().create_new(true).write(true).open(path).unwrap();file.write_all(b"D280-PIN-RAW1\0\0\0").unwrap();file.write_all(&(buf.read().len()as u64).to_le_bytes()).unwrap();file.write_all(&round.to_le_bytes()).unwrap();file.write_all(&(page as u32).to_le_bytes()).unwrap();file.write_all(&(buf.read().len()as u64*4).to_le_bytes()).unwrap();let data=unsafe{std::slice::from_raw_parts(buf.read().as_ptr().cast::<u8>(),buf.read().len()*4)};file.write_all(data).unwrap();file.sync_all().unwrap();}
fn main(){
 assert!(cfg!(target_endian="little"));let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),4);let candidate=match args[1].as_str(){"baseline"=>false,"candidate"=>true,_=>panic!("arm")};let output=PathBuf::from(&args[2]);std::fs::create_dir(&output).unwrap();let warmup=match args[3].as_str(){"warmup"=>true,"scored"=>false,_=>panic!("role")};let page=page_size();assert_eq!(rayon::current_num_threads(),16);
 assert!(rounded(0,page).is_none()&&rounded(usize::MAX,page).is_none()&&rounded(isize::MAX as usize,page).is_none());assert_eq!(rounded(1,page),Some(page));assert_eq!(rounded(page,page),Some(page));assert_eq!(rounded(page+1,page),Some(2*page));
 assert_eq!(size_of::<Original>(),16);assert_eq!(size_of::<Registered>(),24);assert!(size_of::<Buffer>()<=32&&align_of::<Buffer>()==8);
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));assert!(ctx.has_async_alloc());unsafe{ctx.disable_event_tracking()};let stream=ctx.new_stream().unwrap();
 assert_ne!(ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_HOST_REGISTER_SUPPORTED).unwrap(),0);let before_gpu=ctx.mem_get_info().unwrap();
 if warmup&&candidate{let start=counts();let result=Registered::new(&ctx,1024,page,Some(0));match result{Err(e)=>assert!(e.contains("reservation released")),Ok(mut x)=>{x.close().unwrap();panic!("zero-byte registration unexpectedly accepted")}}let delta=std::array::from_fn::<_,7,_>(|i|counts()[i]-start[i]);assert_eq!(delta,[0,0,1,1,1,0,0]);println!("D280_FAILURE_CLEANUP {}",json!({"zero_byte_registration_rejected":true,"owned_VM_reservation_released":true,"no_unregister_for_failed_registration":true,"counter_delta":delta}));}
 let fixtures:Vec<Value>=serde_json::from_str(include_str!(r"@FIXTURES@")).unwrap();assert_eq!(fixtures.len(),3);let mut cases:Vec<(String,usize,bool)>=Vec::new();
 if warmup{for words in[1usize,1023,1024,1025]{cases.push((format!("boundary-{words}"),words,false));}}
 for f in fixtures{cases.push((f["fixture"].as_str().unwrap().into(),f["words"].as_u64().unwrap()as usize,true));}
 let mut records=0;let mut canonical=0;
 for(id,words,is_canonical)in cases{
  assert!(words>0&&words<=u32::MAX as usize);let logical=words.checked_mul(4).unwrap();let start_counts=counts();let guard_left:Vec<u32>=(0..64).map(|i|0xd34db33fu32.wrapping_add(i)).collect();let guard_right:Vec<u32>=(0..64).map(|i|0x78563412u32.wrapping_add(i)).collect();
  let mut device=stream.alloc_zeros::<u32>(words.checked_add(128).unwrap()).unwrap();stream.memcpy_htod(&guard_left,&mut device.slice_mut(0..64)).unwrap();stream.memcpy_htod(&guard_right,&mut device.slice_mut(64+words..128+words)).unwrap();stream.synchronize().unwrap();
  let allocation_clock=Instant::now();let mut buf=Buffer::new(&ctx,words,page,candidate);let allocation_ns=allocation_clock.elapsed().as_nanos()as u64;assert_eq!(buf.parts().1,words);assert_eq!(buf.parts().0 as usize%8,0);
  let mut cycles=[0u64;2];let mut guards:Vec<Vec<u32>>=Vec::new();
  for round in 0..2u32{
   let clock=Instant::now();let writer=RawWrite(buf.parts().0);(0..words).into_par_iter().for_each(|i|writer.set(i,pattern(i,round)));stream.memcpy_htod(buf.read(),&mut device.slice_mut(64..64+words)).unwrap();stream.synchronize().unwrap();
   buf.write().par_iter_mut().for_each(|x|*x=0xdeadbeef);stream.memcpy_dtoh(&device.slice(64..64+words),buf.write()).unwrap();stream.synchronize().unwrap();
   buf.read().par_iter().enumerate().for_each(|(i,&x)|assert_eq!(x,pattern(i,round),"every DMA word"));let left=stream.clone_dtoh(&device.slice(0..64)).unwrap();let right=stream.clone_dtoh(&device.slice(64+words..128+words)).unwrap();assert_eq!(left,guard_left);assert_eq!(right,guard_right);guards.push([left,right].concat());cycles[round as usize]=clock.elapsed().as_nanos()as u64;
   // Entire outputs retained; evidence writing is outside component stage clocks.
   dump(&buf,output.join(format!("{id}-round{round}.bin")),round,page);
  }
  let free_clock=Instant::now();buf.close();drop(buf);let close_ns=free_clock.elapsed().as_nanos()as u64;stream.synchronize().unwrap();drop(device);stream.synchronize().unwrap();
  let delta=std::array::from_fn::<_,7,_>(|i|counts()[i]-start_counts[i]);let registered=candidate&&logical>=THRESHOLD;assert_eq!(delta,if registered{[0,0,1,1,1,1,1]}else{[1,1,0,0,0,0,0]});
  let total=allocation_ns+cycles.iter().sum::<u64>()+close_ns;println!("D280_CASE {}",json!({"fixture":id,"canonical":is_canonical,"arm":args[1],"warmup":warmup,"words":words,"logical_bytes":logical,"backing_rounded_bytes":rounded(logical,page).unwrap(),"page_size":page,"registered_route":registered,"allocation_ns":allocation_ns,"cycles_ns":cycles,"close_ns":close_ns,"complete_component_ns":total,"all_words_full_bit_verified":true,"word_checks":words as u64*2,"device_guard_words":guards,"counter_delta":delta,"threads":16,"CUDA_application_kernels":0,"CFR_iterations":0}));std::io::stdout().flush().unwrap();records+=1;if is_canonical{canonical+=1}
 }
 stream.synchronize().unwrap();ctx.check_err().unwrap();let after_gpu=ctx.mem_get_info().unwrap();drop(stream);drop(ctx);let c=counts();assert_eq!(c[0],c[1]);assert_eq!(c[2],c[3]);assert_eq!(c[5],c[6]);println!("D280_COMPLETE {}",json!({"cases":records,"canonical_fixtures":canonical,"arm":args[1],"warmup":warmup,"counts":c,"GPU_memory_before":before_gpu,"GPU_memory_after_all_device_buffers_dropped":after_gpu,"original_PinnedBuf_bytes":size_of::<Original>(),"registered_owner_bytes":size_of::<Registered>(),"component_enum_bytes":size_of::<Buffer>(),"all_host_and_device_ranges_released":true,"all_CUDA_objects_dropped":true,"CPUglobalallocator":"accepted solver mimalloc","CUDA_application_kernels":0,"NVRTC_compiles":0,"CFR_iterations":0}));
}
