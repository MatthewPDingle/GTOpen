//! Same accepted copy_span PTX, one allocation with disjoint producer rows.
//! Explicit events only; automatic per-buffer event tracking is disabled as in production.
use cudarc::driver::{CudaContext,CudaEvent,CudaFunction,CudaGraph,CudaSlice,CudaStream,DevicePtr,LaunchConfig,PushKernelArg,sys};
use serde_json::{json,Value};
use std::{collections::BTreeMap,fs::OpenOptions,io::{BufWriter,Write},sync::Arc};
type Result<T>=std::result::Result<T,Box<dyn std::error::Error>>;
fn emit(v:Value)->Result<()>{println!("D286_RESULT {v}");std::io::stdout().flush()?;Ok(())}
fn floats(v:&[u32])->Vec<f32>{v.iter().copied().map(f32::from_bits).collect()}
fn bits(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn pattern(n:usize,tag:u32)->Vec<u32>{let special=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc54321,0x7f812345,0xff854321];(0..n).map(|i|if i<16{special[i]^(if tag&1!=0{0x80000000}else{0})}else{(i as u32).wrapping_mul(0x9e3779b9).wrapping_add(tag.wrapping_mul(0x85ebca6b)).rotate_left(tag%31+1)}).collect()}
fn cu(code:sys::CUresult)->Result<()>{if code==sys::cudaError_enum::CUDA_SUCCESS{Ok(())}else{Err(format!("CUDA raw {code:?}").into())}}
fn ptr(d:&CudaSlice<f32>,s:&CudaStream)->u64{let(p,guard)=d.device_ptr(s);drop(guard);p}
fn copy(s:&Arc<CudaStream>,f:&CudaFunction,src:u64,dst:u64,n:usize)->Result<()>{let n=i32::try_from(n)?;unsafe{s.launch_builder(f).arg(&src).arg(&dst).arg(&n).launch(LaunchConfig{grid_dim:(((n as u32+127)/128).max(1),1,1),block_dim:(128,1,1),shared_mem_bytes:0})?;}Ok(())}
struct Data{n:usize,total:usize,a:CudaSlice<f32>,b:CudaSlice<f32>,init:CudaSlice<f32>,cfv:CudaSlice<f32>,out:CudaSlice<f32>}
impl Data{
 fn new(s:&Arc<CudaStream>,n:usize)->Result<Self>{let total=2*n+37;Ok(Self{n,total,a:s.clone_htod(&vec![0f32;n+6])?,b:s.clone_htod(&vec![0f32;n+10])?,init:s.clone_htod(&vec![0f32;total])?,cfv:s.clone_htod(&vec![0f32;total])?,out:s.clone_htod(&vec![0f32;total])?})}
 fn fill(&mut self,s:&Arc<CudaStream>,epoch:u32)->Result<()>{s.memcpy_htod(&floats(&pattern(self.n+6,epoch*10+1)),&mut self.a)?;s.memcpy_htod(&floats(&pattern(self.n+10,epoch*10+2)),&mut self.b)?;s.memcpy_htod(&floats(&pattern(self.total,epoch*10+3)),&mut self.init)?;s.memcpy_htod(&floats(&vec![0x4b123456;self.total]),&mut self.cfv)?;s.memcpy_htod(&floats(&vec![0x4b654321;self.total]),&mut self.out)?;Ok(())}
 fn regions(&self,s:&CudaStream)->Value{json!({"a":[ptr(&self.a,s),(self.n+6)*4],"b":[ptr(&self.b,s),(self.n+10)*4],"init":[ptr(&self.init,s),self.total*4],"cfv":[ptr(&self.cfv,s),self.total*4],"out":[ptr(&self.out,s),self.total*4],"producer_a_offset_words":7,"producer_b_offset_words":self.n+19,"producer_words":self.n})}
 fn queue(&self,s:&Arc<CudaStream>,side:&Arc<CudaStream>,f:&CudaFunction,start:&CudaEvent,done:&CudaEvent,fork:bool,abort:bool)->Result<()>{
  copy(s,f,ptr(&self.init,s),ptr(&self.cfv,s),self.total)?;
  if fork{start.record(s)?;side.wait(start)?;}
  copy(s,f,ptr(&self.a,s)+3*4,ptr(&self.cfv,s)+7*4,self.n)?;
  copy(if fork{side}else{s},f,ptr(&self.b,s)+5*4,ptr(&self.cfv,s)+(self.n as u64+19)*4,self.n)?;
  if fork{done.record(side)?;s.wait(done)?;}
  if abort{return Err("injected host abort after producer enqueue; joined before return".into());}
  copy(s,f,ptr(&self.cfv,s),ptr(&self.out,s),self.total)?;Ok(())
 }
 fn snapshot(&self,s:&Arc<CudaStream>,epoch:u32,arm:&str,stage:&str,state:&str,file:&mut BufWriter<std::fs::File>)->Result<()>{
  s.synchronize()?;let a=bits(&s.clone_dtoh(&self.a)?);let b=bits(&s.clone_dtoh(&self.b)?);let init=bits(&s.clone_dtoh(&self.init)?);let cfv=bits(&s.clone_dtoh(&self.cfv)?);let out=bits(&s.clone_dtoh(&self.out)?);
  assert_eq!(a,pattern(self.n+6,epoch*10+1));assert_eq!(b,pattern(self.n+10,epoch*10+2));assert_eq!(init,pattern(self.total,epoch*10+3));let mut expected=init.clone();expected[7..7+self.n].copy_from_slice(&a[3..3+self.n]);expected[self.n+19..2*self.n+19].copy_from_slice(&b[5..5+self.n]);
  if state=="outputs"{assert_eq!(cfv,expected);assert_eq!(out,expected);}else if state=="producer_only"{assert_eq!(cfv,expected);assert!(out.iter().all(|x|*x==0x4b654321));}else{assert_eq!(state,"poisoned");assert!(cfv.iter().all(|x|*x==0x4b123456));assert!(out.iter().all(|x|*x==0x4b654321));}
  serde_json::to_writer(&mut *file,&json!({"n":self.n,"total":self.total,"epoch":epoch,"arm":arm,"stage":stage,"expected_state":state,"regions":self.regions(s),"source_a_words":a,"source_b_words":b,"initial_words":init,"cfv_words":cfv,"consumer_words":out}))?;file.write_all(b"\n")?;file.flush()?;
  emit(json!({"stage":"snapshot_exact","n":self.n,"epoch":epoch,"arm":arm,"case_stage":stage,"state":state,"all_inputs_outputs_guards_exact":true}))?;Ok(())
 }
}
fn dag(graph:&CudaGraph,d:&Data,s:&CudaStream,fork:bool,abort:bool)->Result<Value>{
 let g=graph.cu_graph();let mut count=0;cu(unsafe{sys::cuGraphGetNodes(g,std::ptr::null_mut(),&mut count)})?;let expected=if abort{3}else{4};assert_eq!(count,expected);let mut nodes=vec![std::ptr::null_mut();count];cu(unsafe{sys::cuGraphGetNodes(g,nodes.as_mut_ptr(),&mut count)})?;
 let cfv=ptr(&d.cfv,s);let out=ptr(&d.out,s);let mut names=BTreeMap::new();let mut raw=Vec::new();
 for node in &nodes{let mut ty=sys::CUgraphNodeType::CU_GRAPH_NODE_TYPE_EMPTY;cu(unsafe{sys::cuGraphNodeGetType(*node,&mut ty)})?;assert_eq!(ty,sys::CUgraphNodeType::CU_GRAPH_NODE_TYPE_KERNEL);let mut p:sys::CUDA_KERNEL_NODE_PARAMS=unsafe{std::mem::zeroed()};cu(unsafe{sys::cuGraphKernelNodeGetParams(*node,&mut p)})?;assert!(!p.kernelParams.is_null());let src=unsafe{*(p.kernelParams.add(0).read()as*const u64)};let dst=unsafe{*(p.kernelParams.add(1).read()as*const u64)};let n=unsafe{*(p.kernelParams.add(2).read()as*const i32)};
  let(label,es,en)=if dst==cfv{("prefix",ptr(&d.init,s),d.total)}else if dst==cfv+28{("a",ptr(&d.a,s)+12,d.n)}else if dst==cfv+(d.n as u64+19)*4{("b",ptr(&d.b,s)+20,d.n)}else{assert_eq!(dst,out);("consumer",cfv,d.total)};assert_eq!(src,es);assert_eq!(n as usize,en);assert_eq!((p.blockDimX,p.blockDimY,p.blockDimZ,p.sharedMemBytes),(128,1,1,0));assert_eq!(p.gridDimX,((en as u32+127)/128).max(1));assert!(names.insert(*node as usize,label.to_string()).is_none());raw.push((*node,src,dst,n));
 }
 assert_eq!(names.values().collect::<std::collections::BTreeSet<_>>().len(),expected);let mut dependencies=BTreeMap::new();
 for node in &nodes{let mut n=0;cu(unsafe{sys::cuGraphNodeGetDependencies(*node,std::ptr::null_mut(),&mut n)})?;let mut deps=vec![std::ptr::null_mut();n];if n>0{cu(unsafe{sys::cuGraphNodeGetDependencies(*node,deps.as_mut_ptr(),&mut n)})?;}dependencies.insert(names[&(*node as usize)].clone(),deps.iter().map(|v|names[&(*v as usize)].clone()).collect::<Vec<_>>());}
 fn ancestor(deps:&BTreeMap<String,Vec<String>>,from:&str,to:&str)->bool{let mut todo=deps[to].clone();let mut seen=std::collections::BTreeSet::new();while let Some(x)=todo.pop(){if x==from{return true;}if seen.insert(x.clone()){todo.extend(deps[&x].clone());}}false}
 assert!(ancestor(&dependencies,"prefix","a")&&ancestor(&dependencies,"prefix","b"));if fork{assert!(!ancestor(&dependencies,"a","b")&&!ancestor(&dependencies,"b","a"));}else{assert!(ancestor(&dependencies,"a","b"));}if !abort{assert!(ancestor(&dependencies,"a","consumer")&&ancestor(&dependencies,"b","consumer"));}
 Ok(json!({"n":d.n,"fork":fork,"abort":abort,"kernel_nodes":count,"dependencies":dependencies,"parameters":raw.iter().map(|(node,src,dst,n)|json!({"label":names[&(*node as usize)],"src":src,"dst":dst,"words":n})).collect::<Vec<_>>(),"branch_independence_and_consumer_dependencies_exact":true}))
}
fn run()->Result<()>{
 let ctx=CudaContext::new(0)?;assert_eq!(ctx.name()?,"NVIDIA GeForce RTX 5090");assert_eq!(ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR)?,12);assert_eq!(ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR)?,0);unsafe{ctx.disable_event_tracking();}assert!(!ctx.is_event_tracking());
 let s=ctx.new_stream()?;let side=ctx.new_stream()?;let start=ctx.new_event(None)?;let done=ctx.new_event(None)?;let module=ctx.load_module(cudarc::nvrtc::Ptx::from_src(include_str!("baseline.ptx")))?;let f=module.load_function("copy_span")?;
 emit(json!({"stage":"device","name":ctx.name()?,"uuid":format!("{:?}",ctx.uuid()?),"concurrent_kernels":ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_CONCURRENT_KERNELS)?,"event_tracking_disabled":true,"same_accepted_PTX_no_NVRTC":true}))?;
 let mut file=BufWriter::new(OpenOptions::new().write(true).create_new(true).open("raw-results.jsonl")?);let mut graphs=Vec::new();let mut snapshots=0;
 for n in [0,1,31,32,257,4097,131073]{let mut d=Data::new(&s,n)?;
  let r=d.regions(&s);let ranges:Vec<_>=["a","b","init","cfv","out"].iter().map(|k|{let a=r[k][0].as_u64().unwrap();(a,a+r[k][1].as_u64().unwrap())}).collect();for i in 0..ranges.len(){for j in i+1..ranges.len(){assert!(ranges[i].1<=ranges[j].0||ranges[j].1<=ranges[i].0);}}assert!(7+n<=n+19&&2*n+19<=d.total);
  for(fork,arm)in[(false,"serial"),(true,"fork")]{d.fill(&s,0)?;d.queue(&s,&side,&f,&start,&done,fork,false)?;d.snapshot(&s,0,arm,"eager","outputs",&mut file)?;snapshots+=1;
   s.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL)?;let result=d.queue(&s,&side,&f,&start,&done,fork,false);let graph=s.end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH)?.ok_or("empty capture")?;result?;graphs.push(dag(&graph,&d,&s,fork,false)?);
   for epoch in 1..=4{d.fill(&s,epoch)?;graph.launch()?;d.snapshot(&s,epoch,arm,"graph_replay","outputs",&mut file)?;snapshots+=1;}s.synchronize()?;side.synchronize()?;drop(graph);
  }s.synchronize()?;side.synchronize()?;drop(d);
 }
 let mut d=Data::new(&s,257)?;d.fill(&s,10)?;assert!(d.queue(&s,&side,&f,&start,&done,true,true).is_err());d.snapshot(&s,10,"fork","host_abort_eager","producer_only",&mut file)?;snapshots+=1;d.fill(&s,11)?;d.queue(&s,&side,&f,&start,&done,true,false)?;d.snapshot(&s,11,"fork","recovery_eager","outputs",&mut file)?;snapshots+=1;
 d.fill(&s,12)?;s.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL)?;let result=d.queue(&s,&side,&f,&start,&done,true,true);let graph=s.end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH)?.ok_or("empty aborted capture")?;assert!(result.is_err());graphs.push(dag(&graph,&d,&s,true,true)?);drop(graph);d.snapshot(&s,12,"fork","host_abort_capture","poisoned",&mut file)?;snapshots+=1;d.fill(&s,13)?;d.queue(&s,&side,&f,&start,&done,true,false)?;d.snapshot(&s,13,"fork","recovery_capture","outputs",&mut file)?;snapshots+=1;
 assert_eq!(snapshots,74);assert_eq!(graphs.len(),15);s.synchronize()?;side.synchronize()?;drop(d);drop(f);drop(module);drop(start);drop(done);s.synchronize()?;side.synchronize()?;drop(side);drop(s);ctx.check_err()?;drop(ctx);file.flush()?;file.get_ref().sync_all()?;
 let graph_file=OpenOptions::new().write(true).create_new(true).open("graph-dags.json")?;serde_json::to_writer_pretty(graph_file,&graphs)?;
 emit(json!({"stage":"complete","snapshots":74,"graphs_inspected":15,"captured_kernel_nodes":59,"actual_application_kernel_executions":291,"all_actual_input_output_guard_bits_exact":true,"all_streams_events_graphs_buffers_context_released":true,"CFR_or_solver_calls":0,"NVRTC_calls":0,"speed_samples":0,"candidate_accepted":false}))?;Ok(())
}
fn main(){if let Err(error)=run(){eprintln!("{error}");std::process::exit(1);}}
