use cudarc::{driver::{CudaContext,CudaFunction,CudaSlice,CudaStream,DevicePtr,LaunchConfig,PushKernelArg,sys},nvrtc::Ptx};
use std::{fs::OpenOptions,io::{BufWriter,Write},path::PathBuf,sync::Arc};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"D205_CONTROL {v}").unwrap();o.flush().unwrap();}
fn oracle(state:&mut [u32],scratch:&mut [u32],n:usize,phases:u32,mode:u32){
 for phase in 0..phases{
  for i in 0..n{let value=state[17+(i+128)%n];scratch[17+i]=if mode==0{value}else{value^0x9e3779b9u32.wrapping_add(phase)};}
  state[17..17+n].copy_from_slice(&scratch[17..17+n]);
 }
}
fn seed(len:usize,id:u32,which:u32,n:usize)->Vec<u32>{
 const B:[u32;16]=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc01234,0xffc01234,0x7f801234,0xff801234,0x7f7fffff,0xffffffff];
 let mut out:Vec<u32>=(0..len).map(|i|0xa5123456u32.wrapping_add(id.wrapping_mul(131)).wrapping_add((i as u32).wrapping_mul(17)).wrapping_add(which*12345)).collect();
 for i in 0..n{out[17+i]=if i%3==0{(i as u32).wrapping_mul(0x85ebca6b)^id.wrapping_mul(0xc2b2ae35)^which}else{B[(i+id as usize+which as usize)%16]};}out
}
fn launch(f:&CudaFunction,s:&Arc<CudaStream>,state:&mut CudaSlice<u32>,scratch:&mut CudaSlice<u32>,n:i32,phases:i32,mode:i32,blocks:u32)->Result<(),cudarc::driver::DriverError>{
 let base=17i32;
 unsafe{s.launch_builder(f).arg(state).arg(scratch).arg(&n).arg(&base).arg(&phases).arg(&mode).launch_cooperative(LaunchConfig{grid_dim:(blocks,1,1),block_dim:(128,1,1),shared_mem_bytes:0}).map(|_|())}
}
fn physical(s:&Arc<CudaStream>,a:&CudaSlice<u32>,b:&CudaSlice<u32>)->serde_json::Value{
 let (ap,ag)=a.device_ptr(s);let (bp,bg)=b.device_ptr(s);let bytes=(a.len()*4) as u64;assert_eq!(a.len(),b.len());assert!(ap+bytes<=bp||bp+bytes<=ap);drop(ag);drop(bg);serde_json::json!({"state":ap,"scratch":bp,"each_bytes":bytes,"disjoint":true})
}
fn graph_witness(graph:&cudarc::driver::CudaGraph)->serde_json::Value{
 unsafe{
  let mut count=0;assert_eq!(sys::cuGraphGetNodes(graph.cu_graph(),std::ptr::null_mut(),&mut count),sys::CUresult::CUDA_SUCCESS);assert!(count>0&&count<=32);
  let mut nodes=vec![std::ptr::null_mut();count];assert_eq!(sys::cuGraphGetNodes(graph.cu_graph(),nodes.as_mut_ptr(),&mut count),sys::CUresult::CUDA_SUCCESS);assert_eq!(count,nodes.len());
  let mut kinds=Vec::new();let mut kernel=0;
  for node in nodes{
   let mut kind=sys::CUgraphNodeType::CU_GRAPH_NODE_TYPE_KERNEL;assert_eq!(sys::cuGraphNodeGetType(node,&mut kind),sys::CUresult::CUDA_SUCCESS);kinds.push(kind as i32);
   if kind==sys::CUgraphNodeType::CU_GRAPH_NODE_TYPE_KERNEL{kernel+=1;let mut value:sys::CUkernelNodeAttrValue=std::mem::zeroed();assert_eq!(sys::cuGraphKernelNodeGetAttribute(node,sys::CUkernelNodeAttrID::CU_LAUNCH_ATTRIBUTE_COOPERATIVE,&mut value),sys::CUresult::CUDA_SUCCESS);assert_eq!(value.cooperative,1);}
  }
  assert_eq!(kernel,1);serde_json::json!({"node_types":kinds,"kernel_nodes":kernel,"cooperative_kernel_attribute":1})
 }
}
fn write_vec(out:&mut BufWriter<std::fs::File>,v:&[u32]){for x in v{out.write_all(&x.to_le_bytes()).unwrap();}}
fn main(){
 let out=PathBuf::from(std::env::args().nth(1).unwrap());std::fs::create_dir(&out).unwrap();
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));assert_eq!(ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH).unwrap(),1);
 let stream=ctx.new_stream().unwrap();let module=ctx.load_module(Ptx::from_src(include_str!("primitive.ptx"))).unwrap();let f=module.load_function("d204_grid_order").unwrap();
 let resident=f.occupancy_max_active_blocks_per_multiprocessor(128,0,None).unwrap();let sms=ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT).unwrap() as u32;assert_eq!((resident,sms),(12,170));let max_grid=resident*sms;assert_eq!(max_grid,2040);
 let mut raw=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(out.join("raw.bin")).unwrap());raw.write_all(b"D205-GRID-RAW1\0\0").unwrap();raw.write_all(&256u32.to_le_bytes()).unwrap();
 let mut id=0u32;let mut metadata=Vec::new();let mut words=0usize;
 for blocks in [1u32,2,170,max_grid]{
  for (length_index,n) in [0usize,1,127,128,129,513,1326,blocks as usize*128+1].into_iter().enumerate(){
   assert!(blocks<=max_grid&&n<=i32::MAX as usize);
   for phases in [0u32,1,2,17]{for mode in [0u32,1]{
    let len=n+36;let initial_state=seed(len,id,0,n);let initial_scratch=seed(len,id,1,n);let mut expected_state=initial_state.clone();let mut expected_scratch=initial_scratch.clone();oracle(&mut expected_state,&mut expected_scratch,n,phases,mode);
    let mut a=stream.clone_htod(&initial_state).unwrap();let mut b=stream.clone_htod(&initial_scratch).unwrap();let eager_addresses=physical(&stream,&a,&b);
    launch(&f,&stream,&mut a,&mut b,n as i32,phases as i32,mode as i32,blocks).unwrap();stream.synchronize().unwrap();let eager_state=stream.clone_dtoh(&a).unwrap();let eager_scratch=stream.clone_dtoh(&b).unwrap();assert_eq!(eager_state,expected_state,"eagerstate{id}");assert_eq!(eager_scratch,expected_scratch,"eagerscratch{id}");drop(a);drop(b);
    let mut a=stream.clone_htod(&initial_state).unwrap();let mut b=stream.clone_htod(&initial_scratch).unwrap();let graph_addresses=physical(&stream,&a,&b);
    stream.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL).unwrap();let result=launch(&f,&stream,&mut a,&mut b,n as i32,phases as i32,mode as i32,blocks);let graph=stream.end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH);result.unwrap();let graph=graph.unwrap().unwrap();let graph_proof=graph_witness(&graph);
    graph.launch().unwrap();stream.synchronize().unwrap();let graph1_state=stream.clone_dtoh(&a).unwrap();let graph1_scratch=stream.clone_dtoh(&b).unwrap();assert_eq!(graph1_state,expected_state,"graph1state{id}");assert_eq!(graph1_scratch,expected_scratch,"graph1scratch{id}");
    oracle(&mut expected_state,&mut expected_scratch,n,phases,mode);graph.launch().unwrap();stream.synchronize().unwrap();let graph2_state=stream.clone_dtoh(&a).unwrap();let graph2_scratch=stream.clone_dtoh(&b).unwrap();assert_eq!(graph2_state,expected_state,"graph2state{id}");assert_eq!(graph2_scratch,expected_scratch,"graph2scratch{id}");drop(graph);drop(a);drop(b);ctx.check_err().unwrap();
    write_vec(&mut raw,&[id,blocks,length_index as u32,n as u32,phases,mode,len as u32]);
    for v in [&initial_state,&initial_scratch,&eager_state,&eager_scratch,&graph1_state,&graph1_scratch,&graph2_state,&graph2_scratch]{write_vec(&mut raw,v);words+=v.len();}
    metadata.push(serde_json::json!({"id":id,"blocks":blocks,"length_index":length_index,"active_words":n,"phases":phases,"mode":mode,"physical_words_each":len,"eager_addresses":eager_addresses,"graph_addresses":graph_addresses,"graph":graph_proof,"all_full_vectors_and_guards_exact":true,"completed_eager_launches":1,"completed_graph_replays":2}));emit(serde_json::json!({"stage":"case_complete","id":id,"blocks":blocks,"n":n,"phases":phases,"mode":mode,"exact":true}));id+=1;
   }}
  }
 }
 assert_eq!(id,256);raw.flush().unwrap();raw.get_ref().sync_all().unwrap();drop(raw);
 let mut m=OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap();m.write_all(serde_json::to_string_pretty(&serde_json::json!({"cases":metadata,"case_count":id,"kernel_launches":id*3,"capture_kernel_nodes":id,"represented_u32_words":words,"resident_blocks_per_SM":resident,"SM_count":sms,"max_cooperative_grid_blocks":max_grid,"solver_or_speed_samples":0})).unwrap().as_bytes()).unwrap();m.sync_all().unwrap();drop(m);drop(f);drop(module);drop(stream);ctx.check_err().unwrap();drop(ctx);
 emit(serde_json::json!({"stage":"complete","cases":id,"kernel_launches":id*3,"represented_u32_words":words,"solver_or_speed_samples":0,"candidate_accepted":false}));
}

const _: () = assert!(sys::CUkernelNodeAttrID::CU_LAUNCH_ATTRIBUTE_COOPERATIVE as u32 == 2);
