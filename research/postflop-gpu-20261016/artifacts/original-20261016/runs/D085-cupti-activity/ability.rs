use cudarc::{driver::{CudaContext,LaunchConfig,PushKernelArg,sys},nvrtc::{compile_ptx_with_opts,CompileOptions}};
#[link(name="D085Collector")] extern "system" {fn D085StartTrace()->u32;fn D085FlushTrace()->u32;fn D085StopTrace()->u32;}
struct Guard;impl Drop for Guard{fn drop(&mut self){unsafe{D085StopTrace();}}}
fn main(){
 let _guard=Guard;assert_eq!(unsafe{D085StartTrace()},1,"CUPTI activity initialization failed");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));unsafe{ctx.disable_event_tracking();}
 let s=ctx.new_stream().unwrap();let module=ctx.load_module(compile_ptx_with_opts("extern \"C\" __global__ void d085_tick(unsigned int* x,int n){int i=blockIdx.x*blockDim.x+threadIdx.x;if(i<n)x[i]+=1u;}",CompileOptions{arch:Some("compute_120"),..Default::default()}).unwrap()).unwrap();let f=module.load_function("d085_tick").unwrap();
 let mut seed=vec![0u32;259];seed[257]=0xdeadbeef;seed[258]=0x12345678;let mut data=s.clone_htod(&seed).unwrap();let n=257i32;
 let launch=|data:&mut cudarc::driver::CudaSlice<u32>|unsafe{s.launch_builder(&f).arg(data).arg(&n).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();};
 launch(&mut data);s.synchronize().unwrap();s.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL).unwrap();for _ in 0..3{launch(&mut data);}let graph=s.end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH).unwrap().unwrap();for _ in 0..4{graph.launch().unwrap();}s.synchronize().unwrap();
 let result=s.clone_dtoh(&data).unwrap();assert!(result[..257].iter().all(|x|*x==13));assert_eq!(&result[257..],&seed[257..]);assert_eq!(unsafe{D085FlushTrace()},1);assert_eq!(unsafe{D085StopTrace()},1);
 println!("D085_ABILITY {{\"expected_kernels\":13,\"eager_kernels\":1,\"graph_nodes\":3,\"graph_replays\":4,\"all257words_equal13\":true,\"guards_exact\":true,\"collector_stopped_with_context_alive\":true,\"performance_measured\":false}}");ctx.check_err().unwrap();
}
