use cudarc::driver::{CudaContext,result,sys::CUdeviceptr};
use serde_json::json;
use std::{io::{self,Write},sync::Arc};
struct Allocation{ptr:CUdeviceptr,bytes:usize}
impl Allocation{
 fn new(bytes:usize)->Self{let ptr=unsafe{result::malloc_sync(bytes)}.unwrap();let a=Self{ptr,bytes};unsafe{result::memset_d8_sync(ptr,0x5a,bytes)}.unwrap();let mut head=[0u8;64];let mut tail=[0u8;64];unsafe{result::memcpy_dtoh_sync(&mut head,ptr).unwrap();result::memcpy_dtoh_sync(&mut tail,ptr+(bytes-64)as u64).unwrap();}assert!(head.iter().chain(&tail).all(|&x|x==0x5a));a}
}
impl Drop for Allocation{fn drop(&mut self){unsafe{result::free_sync(self.ptr)}.unwrap();}}
fn hold(ctx:&Arc<CudaContext>,stage:&str,cpu:usize,gpu:usize){ctx.synchronize().unwrap();let(free,total)=ctx.mem_get_info().unwrap();println!("E080_MEM_ABILITY {}",json!({"stage":stage,"PID":std::process::id(),"CPU_owned_payload_bytes":cpu,"GPU_owned_payload_bytes":gpu,"device_free_bytes_informational":free,"device_total_bytes":total,"application_kernels":0,"NVRTC_compiles":0}));io::stdout().flush().unwrap();let mut ack=String::new();assert!(io::stdin().read_line(&mut ack).unwrap()>0);assert_eq!(ack.trim(),"continue");}
fn main(){let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));ctx.bind_to_thread().unwrap();assert!(ctx.mem_get_info().unwrap().0>=2*1024*1024*1024);
 let prime=Allocation::new(64*1024*1024);assert_eq!(prime.bytes,64*1024*1024);drop(prime);hold(&ctx,"baseline",0,0);
 let host=vec![0x4du8;128*1024*1024];std::hint::black_box(&host);assert_eq!(host[0],0x4d);assert_eq!(host[host.len()-1],0x4d);hold(&ctx,"CPU128",host.len(),0);drop(host);hold(&ctx,"CPU_free",0,0);
 for(name,mb)in[("GPU256",256usize),("GPU512",512),("GPU256_repeat",256)]{let a=Allocation::new(mb*1024*1024);hold(&ctx,name,0,a.bytes);drop(a);hold(&ctx,&format!("{name}_free"),0,0);}
 println!("E080_MEM_ABILITY {}",json!({"stage":"complete","states":9,"GPU_allocations_including_prime":4,"GPU_release_calls":4,"CPU_allocations":1,"canary_bytes_checked":4*128,"application_kernels":0,"NVRTC_compiles":0}));io::stdout().flush().unwrap();ctx.check_err().unwrap();}
