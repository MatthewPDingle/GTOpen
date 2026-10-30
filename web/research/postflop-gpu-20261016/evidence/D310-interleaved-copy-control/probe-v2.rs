extern crate solver;
use cudarc::driver::{result,sys,CudaContext,CudaStream,CudaSlice,DevicePtrMut};
use rayon::prelude::*;
use serde_json::json;
use std::{ffi::c_void,fmt::Debug,fs::OpenOptions,io::Write,mem::{size_of,align_of,offset_of},path::{Path,PathBuf},ptr,sync::Arc,time::Instant};
const G:usize=64;
const SPECIAL:[u32;13]=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0xffc54321];
fn pattern(i:usize,field:u32,seed:u32)->u32 {
 if i<SPECIAL.len(){SPECIAL[(i+field as usize*5+seed as usize%13)%13]}
 else {(i as u32).wrapping_mul(0x9e3779b9).wrapping_add(seed^field.wrapping_mul(0x85ebca6b)).rotate_left(7)^0xa5a55a5a}
}
fn guard(i:usize,field:u32,right:bool)->u32 {(if right{0x78563412u32}else{0xd34db33fu32}).wrapping_add(i as u32)^field.wrapping_mul(0x01010101)}
fn geometry(n:usize,field:u32)->Option<(usize,usize)> {
 if n==0||field>1{return None}
 let bytes=n.checked_mul(8)?;
 if bytes.checked_add(G*8)?>isize::MAX as usize{return None}
 let end=(n-1).checked_mul(8)?.checked_add(field as usize*4)?.checked_add(4)?;
 if end>bytes{return None}Some((bytes,end))
}
fn drain(s:&CudaStream){if let Err(e)=s.synchronize(){eprintln!("D310_UNSAFE_TO_FREE_AFTER_SYNC_FAILURE {e:?}");std::process::abort()}}
fn must<T,E:Debug>(s:&CudaStream,r:Result<T,E>)->T {match r{Ok(x)=>x,Err(e)=>{drain(s);panic!("D310_ENQUEUE_OR_API_ERROR_DRAINED {e:?}")}}}
struct Host{ptr:*mut u32,len:usize}
impl Host{
 fn new(ctx:&Arc<CudaContext>,len:usize)->Self{ctx.bind_to_thread().unwrap();let bytes=len.checked_mul(4).unwrap();let ptr=unsafe{result::malloc_host(bytes,0)}.unwrap().cast();Self{ptr,len}}
 fn read(&self,n:usize)->&[u32]{assert!(n<=self.len);unsafe{std::slice::from_raw_parts(self.ptr,n)}}
 fn write(&mut self,n:usize)->&mut[u32]{assert!(n<=self.len);unsafe{std::slice::from_raw_parts_mut(self.ptr,n)}}
 fn close(&mut self){if !self.ptr.is_null(){let p=self.ptr;self.ptr=ptr::null_mut();if let Err(e)=unsafe{result::free_host(p.cast())}{eprintln!("D310_PINNED_FREE_ERROR {e:?}");std::process::abort()}}}
}
impl Drop for Host{fn drop(&mut self){self.close()}}
fn descriptor(host:*mut u32,device:sys::CUdeviceptr,n:usize,field:u32,h2d:bool)->sys::CUDA_MEMCPY2D {
 geometry(n,field).unwrap();let ht=sys::CUmemorytype::CU_MEMORYTYPE_HOST;let dt=sys::CUmemorytype::CU_MEMORYTYPE_DEVICE;
 sys::CUDA_MEMCPY2D{srcXInBytes:if h2d{0}else{field as usize*4},srcY:0,srcMemoryType:if h2d{ht}else{dt},srcHost:if h2d{host.cast()}else{ptr::null()},srcDevice:if h2d{0}else{device},srcArray:ptr::null_mut(),srcPitch:if h2d{4}else{8},dstXInBytes:if h2d{field as usize*4}else{0},dstY:0,dstMemoryType:if h2d{dt}else{ht},dstHost:if h2d{ptr::null_mut()}else{host.cast()},dstDevice:if h2d{device}else{0},dstArray:ptr::null_mut(),dstPitch:if h2d{8}else{4},WidthInBytes:4,Height:n}
}
fn copy2d(s:&CudaStream,pair:&mut CudaSlice<u32>,host:&mut Host,n:usize,field:u32,h2d:bool)->u64{
 assert!(host.len>=n&&pair.len()==2*n+2*G);let mut payload=pair.slice_mut(G..G+2*n);
 let (p,_record)=payload.device_ptr_mut(s);let d=descriptor(host.ptr,p,n,field,h2d);
 let start=Instant::now();must(s,unsafe{sys::cuMemcpy2DAsync_v2(&d,s.cu_stream())}.result());drain(s);start.elapsed().as_nanos()as u64
}
fn header(file:&mut std::fs::File,words:usize,kind:u32,field:u32,fixture:u32,seed:u32,stage:u32,n:usize){
 file.write_all(b"D310RAW1").unwrap();file.write_all(&(words as u64).to_le_bytes()).unwrap();
 for x in[kind,field,fixture,seed,stage,0]{file.write_all(&x.to_le_bytes()).unwrap()}
 for x in[words as u64*4,if kind==0{0}else{G as u64},n as u64]{file.write_all(&x.to_le_bytes()).unwrap()}
}
fn raw_bytes(x:&[u32])->&[u8]{unsafe{std::slice::from_raw_parts(x.as_ptr().cast(),x.len()*4)}}
fn set_guards(s:&Arc<CudaStream>,device:&mut CudaSlice<u32>,field:u32){
 let len=device.len();for right in[false,true]{let g:Vec<u32>=(0..G).map(|i|guard(i,field,right)).collect();let start=if right{len-G}else{0};must(s,s.memcpy_htod(&g,&mut device.slice_mut(start..start+G)));drain(s)}
}
fn output(path:&Path,host:&Host,n:usize,field:u32,fixture:u32,seed:u32){
 let mut f=OpenOptions::new().write(true).create_new(true).open(path).unwrap();header(&mut f,n,0,field,fixture,seed,1,n);f.write_all(raw_bytes(host.read(n))).unwrap();f.sync_all().unwrap();
}
fn physical(s:&Arc<CudaStream>,device:&CudaSlice<u32>,host:&mut Host,path:&Path,n:usize,kind:u32,field:u32,fixture:u32,seed:u32,stage:u32){
 let len=device.len();assert_eq!(len,if kind==1{n+2*G}else{2*n+2*G});
 let mut f=OpenOptions::new().write(true).create_new(true).open(path).unwrap();header(&mut f,len,kind,field,fixture,seed,stage,n);
 let mut off=0;while off<len{let count=(len-off).min(host.len);must(s,s.memcpy_dtoh(&device.slice(off..off+count),host.write(count)));drain(s);
  host.read(count).par_iter().enumerate().for_each(|(i,&got)|{let j=off+i;let end=len-G;let expected=if j<G{guard(j,field,false)}else if j>=end{guard(j-end,field,true)}else if kind==1{pattern(j-G,field,seed)}else{pattern((j-G)/2,((j-G)%2)as u32,seed)};assert_eq!(got,expected,"physical word {j} kind{kind} field{field}")});
  f.write_all(raw_bytes(host.read(count))).unwrap();off+=count;
 }f.sync_all().unwrap();
}
fn main(){
 assert!(cfg!(target_endian="little"));assert_eq!(size_of::<Host>(),16);assert_eq!(rayon::current_num_threads(),16);
 assert_eq!(size_of::<sys::CUDA_MEMCPY2D>(),128);assert_eq!(align_of::<sys::CUDA_MEMCPY2D>(),8);
 let offsets=[offset_of!(sys::CUDA_MEMCPY2D,srcMemoryType),offset_of!(sys::CUDA_MEMCPY2D,srcHost),offset_of!(sys::CUDA_MEMCPY2D,srcDevice),offset_of!(sys::CUDA_MEMCPY2D,srcPitch),offset_of!(sys::CUDA_MEMCPY2D,dstXInBytes),offset_of!(sys::CUDA_MEMCPY2D,dstMemoryType),offset_of!(sys::CUDA_MEMCPY2D,dstHost),offset_of!(sys::CUDA_MEMCPY2D,dstDevice),offset_of!(sys::CUDA_MEMCPY2D,dstPitch),offset_of!(sys::CUDA_MEMCPY2D,WidthInBytes),offset_of!(sys::CUDA_MEMCPY2D,Height)];assert_eq!(offsets,[16,24,32,48,56,72,80,88,104,112,120]);
 for n in[0,usize::MAX,isize::MAX as usize]{assert!(geometry(n,0).is_none())}assert!(geometry(1,2).is_none());
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let out=PathBuf::from(&args[1]);std::fs::create_dir(&out).unwrap();
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));assert!(ctx.has_async_alloc());unsafe{ctx.disable_event_tracking()};let s=ctx.new_stream().unwrap();
 let max_pitch=ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MAX_PITCH).unwrap();assert!(max_pitch>=8);let before=ctx.mem_get_info().unwrap();
 println!("D310_ABI {}",json!({"descriptor_bytes":128,"alignment":8,"offsets":offsets,"pinned_owner_bytes":16,"cached_pinned_flags":0,"driver_max_pitch":max_pitch,"zero_overflow_bad_field_rejected_before_CUDA":true}));
 let mut cases:Vec<(String,usize)>=vec![];for n in[1,2,17,1023,1024,1025]{cases.push((format!("boundary-{n}"),n))}
 for (name,n) in[("rainbow",185172163),("two-tone",110745280),("river",4480)]{cases.push((name.into(),n))}
 let mut copied=0u64;let mut payload_checks=0u64;let mut raw_words=0u64;
 for (index,(id,n)) in cases.iter().enumerate(){let seed=0x243f6a88u32^(index as u32).wrapping_mul(0x85ebca6b);geometry(*n,0).unwrap();geometry(*n,1).unwrap();
  let free=ctx.mem_get_info().unwrap().0;let allocation_bytes=(4*n+6*G).checked_mul(4).unwrap();assert!(free>=allocation_bytes+1024*1024*1024);
  let mut host=Host::new(&ctx,(*n).max(128));let mut base=[must(&s,s.alloc_zeros::<u32>(n+2*G)),must(&s,s.alloc_zeros::<u32>(n+2*G))];let mut pair=must(&s,s.alloc_zeros::<u32>(2*n+2*G));drain(&s);
  for (field,device) in base.iter_mut().enumerate(){set_guards(&s,device,field as u32)}set_guards(&s,&mut pair,2);
  let mut upload=[0u64;4];for field in 0..2u32{host.write(*n).par_iter_mut().enumerate().for_each(|(i,x)|*x=pattern(i,field,seed));let t=Instant::now();must(&s,s.memcpy_htod(host.read(*n),&mut base[field as usize].slice_mut(G..G+n)));drain(&s);upload[field as usize]=t.elapsed().as_nanos()as u64;upload[2+field as usize]=copy2d(&s,&mut pair,&mut host,*n,field,true);}
  for stage in[0u32,2]{for field in 0..2u32{physical(&s,&base[field as usize],&mut host,&out.join(format!("{id}-physical-baseline-{field}-stage{stage}.bin")),*n,1,field,index as u32,seed,stage)}physical(&s,&pair,&mut host,&out.join(format!("{id}-physical-interleaved-stage{stage}.bin")),*n,2,2,index as u32,seed,stage);
   if stage==0{let mut download=[0u64;4];for arm in 0..2{for field in 0..2u32{host.write(*n).par_iter_mut().enumerate().for_each(|(i,x)|*x=!pattern(i,field,seed));let elapsed=if arm==0{let t=Instant::now();must(&s,s.memcpy_dtoh(&base[field as usize].slice(G..G+n),host.write(*n)));drain(&s);t.elapsed().as_nanos()as u64}else{copy2d(&s,&mut pair,&mut host,*n,field,false)};download[arm*2+field as usize]=elapsed;host.read(*n).par_iter().enumerate().for_each(|(i,&got)|assert_eq!(got,pattern(i,field,seed),"copyout arm{arm} field{field} index{i}"));output(&out.join(format!("{id}-output-arm{arm}-field{field}.bin")),&host,*n,field,index as u32,seed)}}
    println!("D310_COPY {}",json!({"fixture":id,"fixture_index":index,"words":n,"seed":seed,"upload_copy_and_sync_ns":upload,"download_copy_and_sync_ns":download,"timing_role":"single_diagnostic_round_not_solver_speed_or_acceptance","all_output_words_bit_exact":true}));std::io::stdout().flush().unwrap();
   }
  }
  drain(&s);drop(pair);drop(base);drain(&s);host.close();drop(host);drain(&s);ctx.check_err().unwrap();copied+=8*(*n as u64);payload_checks+=12*(*n as u64);raw_words+=12*(*n as u64)+12*G as u64;
  println!("D310_CASE_COMPLETE {}",json!({"fixture":id,"physical_before_after_words":8*n+12*G,"output_words":4*n,"raw_words":12*n+12*G,"pinned_words":(*n).max(128),"logical_device_words_per_arm":2*n,"physical_device_words_baseline":2*n+4*G,"physical_device_words_interleaved":2*n+2*G,"all_words_and_guards_checked":true,"owned_ranges_released":true}));std::io::stdout().flush().unwrap();
 }
 drain(&s);ctx.check_err().unwrap();let after=ctx.mem_get_info().unwrap();drop(s);drop(ctx);
 println!("D310_COMPLETE {}",json!({"cases":9,"cached_pinned_allocations":9,"cached_pinned_frees":9,"explicit_device_owners":27,"explicit_device_owner_drops":27,"typed_copy_words":copied,"payload_word_checks":payload_checks,"raw_words_including_guards":raw_words,"GPU_memory_before":before,"GPU_memory_after_owned_ranges_dropped":after,"CUDA_application_kernels":0,"NVRTC_compiles":0,"CFR_iterations":0,"all_owned_ranges_and_context_dropped":true,"exactness_scope":"transport_u32_bits_and_guards_only_not_CFR_numerical_equivalence","CPUglobalallocator":"accepted_solver_mimalloc","no_new_solver_candidate":true}));
}
