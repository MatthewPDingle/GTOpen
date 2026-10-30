//! D235 direct up_fold metadata comparison. No timings or solver execution.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
type Out=BufWriter<File>;
fn file(p:PathBuf,magic:&[u8])->Out{let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(p).unwrap());f.write_all(magic).unwrap();f}
fn words(f:&mut Out,v:&[u32]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();let b:Vec<u8>=v.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();}
fn id(f:&mut Out,n:usize){f.write_all(&(n as u32).to_le_bytes()).unwrap();}
fn u(v:&serde_json::Value,k:&str)->usize{v[k].as_u64().unwrap() as usize}
fn w(v:&serde_json::Value)->Vec<u32>{v.as_array().unwrap().iter().map(|x|u32::try_from(x.as_u64().unwrap()).unwrap()).collect()}
fn padded(mut v:Vec<u32>)->Vec<u32>{if v.is_empty(){v.push(0x4b123456);}v}
fn floats(v:&[u32])->Vec<f32>{v.iter().copied().map(f32::from_bits).collect()}
fn fb(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn readf(s:&Arc<CudaStream>,d:&CudaSlice<f32>)->Vec<u32>{let v=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();fb(&v)}
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"D235_FOLD_UNIT {v}").unwrap();o.flush().unwrap();}
fn main(){
 let dir=PathBuf::from(std::env::var_os("D235_FOLD_KERNEL_CONTROL_DIR").expect("fresh raw directory required"));std::fs::create_dir(&dir).unwrap();
 let mut input=file(dir.join("inputs.bin"),b"D235_FOLD_IN1");
 let mut baseline=file(dir.join("baseline.bin"),b"D235_FOLD_OUT1");let mut candidate=file(dir.join("candidate.bin"),b"D235_FOLD_OUT1");
 let mut bi=file(dir.join("baseline-inputs.bin"),b"D235_FOLD_IM1");let mut ci=file(dir.join("candidate-inputs.bin"),b"D235_FOLD_IM1");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
 let bf=bm.load_function("up_fold").unwrap();let cf=cm.load_function("up_fold").unwrap();
 let corpus:serde_json::Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let cases=corpus["cases"].as_array().unwrap();assert_eq!(cases.len(),360);
 let mut output_words=0u64;let mut immutable_words=0u64;let mut guard_words=0u64;let mut required_words=0u64;let mut nonzero_words=0u64;
 for (index,c) in cases.iter().enumerate(){
  assert_eq!(u(c,"id"),index);let scenario=&corpus["full_scenarios"][u(c,"scenario_index")];
  let p=u(c,"p") as i32;let block=u(c,"threads") as u32;let count=u(c,"count") as i32;
  let nhp=u(scenario,"nh_p") as i32;let nho=u(scenario,"nh_o") as i32;let max=u(scenario,"nh_max") as i32;let start=u(scenario,"start") as i32;
  let meta=scenario["node_meta"].as_array().unwrap();let owner:Vec<i32>=meta.iter().map(|x|u(x,"owner") as i32).collect();
  let twin:Vec<u32>=meta.iter().map(|x|u(x,"twin_bits") as u32).collect();let tlose:Vec<u32>=meta.iter().map(|x|u(x,"tlose_bits") as u32).collect();
  let nodes=w(&scenario["nodes"]);let rsrc0=w(&scenario["rsrc0"]);let rsrc1=w(&scenario["rsrc1"]);
  let reach0=w(&scenario["reach0_bits"]);let reach1=w(&scenario["reach1_bits"]);
  let pc1=padded(w(&scenario["pc1"]));let pc2=padded(w(&scenario["pc2"]));let off=w(&scenario["card_off"]);let idx=padded(w(&scenario["card_idx"]));
  let same=padded(w(&scenario["same_p"]));let slots=w(&scenario["cfv_slot"]);let seed=vec![0x4b123456u32;u(scenario,"cfv_words")];
  let immutable=vec![nodes.clone(),owner.iter().map(|&x|x as u32).collect(),twin.clone(),tlose.clone(),rsrc0.clone(),rsrc1.clone(),reach0.clone(),reach1.clone(),pc1.clone(),pc2.clone(),off.clone(),idx.clone(),same.clone(),slots.clone()];
  id(&mut input,index);words(&mut input,&[u(c,"scenario_index") as u32,p as u32,block,count as u32,nhp as u32,nho as u32,max as u32,start as u32]);for v in &immutable{words(&mut input,v);}words(&mut input,&seed);input.flush().unwrap();
  let dn=stream.clone_htod(&nodes).unwrap();let dp=stream.clone_htod(&owner).unwrap();
  let dtw=stream.clone_htod(&floats(&twin)).unwrap();let dtl=stream.clone_htod(&floats(&tlose)).unwrap();
  let drs0=stream.clone_htod(&rsrc0).unwrap();let drs1=stream.clone_htod(&rsrc1).unwrap();let dr0=stream.clone_htod(&floats(&reach0)).unwrap();let dr1=stream.clone_htod(&floats(&reach1)).unwrap();
  let dc1=stream.clone_htod(&pc1).unwrap();let dc2=stream.clone_htod(&pc2).unwrap();let doff=stream.clone_htod(&off).unwrap();let didx=stream.clone_htod(&idx).unwrap();let dsame=stream.clone_htod(&same).unwrap();let dslots=stream.clone_htod(&slots).unwrap();
  let mut active=vec![false;seed.len()];let mut required=active.clone();
  for &node in &nodes[start as usize..(start+count) as usize]{for h in 0..nhp as usize{
   let at=slots[node as usize] as usize*max as usize+h;assert!(!active[at],"disjoint parent output words");active[at]=true;required[at]=meta[node as usize]["required"].as_bool().unwrap();
  }}
  let mut expected:Option<Vec<u32>>=None;
  for (label,f) in [("baseline",&bf),("candidate",&cf)]{
   let mut dv=stream.clone_htod(&floats(&seed)).unwrap();
   unsafe{
    let mut launch=stream.launch_builder(f);launch.arg(&dn).arg(&start).arg(&count).arg(&p);
    launch.arg(&dp);
    launch.arg(&dtw).arg(&dtl).arg(&drs0).arg(&drs1).arg(&dr0).arg(&dr1)
      .arg(&dc1).arg(&dc2).arg(&doff).arg(&didx).arg(&dsame).arg(&dslots).arg(&mut dv)
      .arg(&nhp).arg(&nho).arg(&max).launch(LaunchConfig{grid_dim:(count as u32+2,1,1),block_dim:(block,1,1),shared_mem_bytes:nho as u32*4}).unwrap();
   }
   stream.synchronize().unwrap();let result=readf(&stream,&dv);
   let output=if label=="baseline"{&mut baseline}else{&mut candidate};id(output,index);words(output,&result);output.flush().unwrap();
   let post=vec![stream.clone_dtoh(&dn).unwrap(),stream.clone_dtoh(&dp).unwrap().iter().map(|&x|x as u32).collect(),readf(&stream,&dtw),readf(&stream,&dtl),stream.clone_dtoh(&drs0).unwrap(),stream.clone_dtoh(&drs1).unwrap(),readf(&stream,&dr0),readf(&stream,&dr1),stream.clone_dtoh(&dc1).unwrap(),stream.clone_dtoh(&dc2).unwrap(),stream.clone_dtoh(&doff).unwrap(),stream.clone_dtoh(&didx).unwrap(),stream.clone_dtoh(&dsame).unwrap(),stream.clone_dtoh(&dslots).unwrap()];stream.synchronize().unwrap();
   let image=if label=="baseline"{&mut bi}else{&mut ci};id(image,index);for v in &post{words(image,v);}image.flush().unwrap();assert_eq!(post,immutable,"immutable case{index}/{label}");
   let mut changed=0u64;let mut this_required=0u64;
   for i in 0..result.len(){
    if !active[i]{assert_eq!(result[i],seed[i],"guard{index}/{label}/{i}");guard_words+=1;}
    else if required[i]{assert!(f32::from_bits(result[i]).is_finite(),"required finite case{index}/{label}/{i}");required_words+=1;this_required+=1;if result[i]!=seed[i]{changed+=1;if result[i]&0x7fffffff!=0{nonzero_words+=1;}}}
   }
   if this_required>0{assert!(changed>0,"active finite outputs cannot all remain stale");}
   if let Some(ref before)=expected{assert_eq!(&result,before,"baseline/candidate fold case{index}, including nonfinite words");}else{expected=Some(result.clone());}
   output_words+=result.len() as u64;immutable_words+=post.iter().map(|v|v.len() as u64).sum::<u64>();
  }
  emit(serde_json::json!({"stage":"case","id":index,"scenario":scenario["id"],"p":p,"threads":block,"count":count,"nh_p":nhp,"nh_o":nho,"dynamic_shared_bytes":nho*4,"all_raw_exact":true,"guards_exact":true,"full_actual_immutable_images":14,"output_words_per_arm":seed.len()}));
 }
 assert!(nonzero_words>0,"nonvacuous finite nonzero output coverage");
 stream.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(stream);ctx.check_err().unwrap();
 for f in [&mut input,&mut baseline,&mut candidate,&mut bi,&mut ci]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 emit(serde_json::json!({"stage":"complete","cases":cases.len(),"kernel_launches":2*cases.len(),"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guard_words,"required_finite_words_both_arms":required_words,"required_nonzero_changed_words_both_arms":nonzero_words,"all_raw_exact":true,"all_inputs_and_guards_exact":true,"performance_measurement":false,"solver_executions":0,"candidate_accepted":false}));
}
