//! E085 direct original/candidate up_action raw comparison, no timing score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,DevicePtr,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
include!("discounts.rs");
type Out=BufWriter<File>;
fn file(p:PathBuf,magic:&[u8])->Out{let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(p).unwrap());f.write_all(magic).unwrap();f}
fn words(f:&mut Out,v:&[u32]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();let b:Vec<u8>=v.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();}
fn id(f:&mut Out,n:usize){f.write_all(&(n as u32).to_le_bytes()).unwrap();}
fn fb(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn split64(v:impl IntoIterator<Item=u64>)->Vec<u32>{v.into_iter().flat_map(|x|[x as u32,(x>>32) as u32]).collect()}
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E085_UNIT {v}").unwrap();o.flush().unwrap();}
fn readf(s:&Arc<CudaStream>,d:&CudaSlice<f32>)->Vec<u32>{let v=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();fb(&v)}
#[derive(Clone,Copy)]
struct Case {nh:usize,na:usize,block:u32,p:i32,role:u32,algo:u32,t:u32,mode:u32,count:i32}
fn value(i:usize,mode:u32)->f32 {
 match mode {
  1=>if i%2==0 {0.0}else{-0.0},
  2=>if i%7==0 {[f32::INFINITY,f32::NEG_INFINITY,f32::from_bits(0x7fc0_1234),f32::from_bits(0xffc0_5678)][(i/7)%4]}else{((i*73%1009) as f32-504.0)/32.0},
  3=>if i%3==0 {-f32::MAX}else{f32::MAX},
  4=>[f32::from_bits(1),-f32::from_bits(1),0.0,-0.0,f32::MIN_POSITIVE,-f32::MIN_POSITIVE,f32::from_bits(0x0080_0001)][i%7],
  _=>[0.0,-0.0,0.25,-0.75,13.25,-7.125,1e10,-1e10,1e-20,-1e-20][(i*5+i/11)%10],
 }
}
fn disjoint_regions(s:&Arc<CudaStream>,buffers:[&CudaSlice<f32>;3])->Vec<[u64;2]> {
 let mut regions=Vec::new();
 for buffer in buffers {let (ptr,_guard)=buffer.device_ptr(s);regions.push([ptr,buffer.len() as u64*4]);}
 for i in 0..regions.len() {for j in i+1..regions.len() {
  let ie=regions[i][0].checked_add(regions[i][1]).unwrap();let je=regions[j][0].checked_add(regions[j][1]).unwrap();
  assert!(ie<=regions[j][0]||je<=regions[i][0],"actual mutable device buffers overlap");
 }}
 regions
}
fn main(){
 let dir=PathBuf::from(std::env::args_os().nth(1).expect("fresh output dir required"));std::fs::create_dir(&dir).unwrap();
 let mut input=file(dir.join("inputs.bin"),b"E085_IN1");
 let mut baseline=file(dir.join("baseline.bin"),b"E085_OUT1");let mut candidate=file(dir.join("candidate.bin"),b"E085_OUT1");
 let mut bi=file(dir.join("baseline-inputs.bin"),b"E085_IM1");let mut ci=file(dir.join("candidate-inputs.bin"),b"E085_IM1");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
 let bf=bm.load_function("up_action").unwrap();let cf=cm.load_function("up_action").unwrap();
 let mut cases=Vec::new();
 for na in [1,2,3,4,5,8,9,16,17] {for role in 0..3 {for p in 0..2 {for algo in 0..2 {
  for (nh,t) in [(1,1),(129,20),(257,200)] {cases.push(Case{nh,na,block:128,p,role,algo,t,mode:0,count:1});}
 }}}}
 for na in [1,2,8,9,17] {for role in 0..3 {for nh in [0,31,32,33,63,64,65,127,128,255,256,511,512,513,1023,1024,1326] {
  cases.push(Case{nh,na,block:128,p:1,role,algo:0,t:200,mode:0,count:1});
 }}}
 for na in [1,2,9,17] {for role in 0..3 {for block in [1,32,64,256] {for nh in [7,129,513] {
  cases.push(Case{nh,na,block,p:0,role,algo:1,t:20,mode:0,count:1});
 }}}}
 for na in [1,2,3,4,8,9,17] {for role in 0..3 {for mode in 1..=4 {
  cases.push(Case{nh:257,na,block:128,p:1,role,algo:mode%2,t:200,mode,count:1});
 }}}
 for na in [1,2,9,17] {for role in 0..3 {cases.push(Case{nh:129,na,block:128,p:0,role,algo:0,t:20,mode:0,count:0});}}
 assert_eq!(cases.len(),819);
 let case_count=cases.len();
 let mut output_words=0u64;let mut immutable_words=0u64;let mut guard_words=0u64;
 for (index,c) in cases.iter().enumerate(){
  let Case{nh,na,block,p,role,algo,t,mode,count}=*c;
  let nn=na+8;let max=nh+5;let parent=2usize;let off=13usize;let cs=2usize;let loff=5usize;let start=1i32;
  let nodes=vec![0xdead_beefu32,parent as u32,0xdead_beef];
  let mut player=vec![-7i32;nn];player[parent]=if role==2 {1-p}else{p};
  let mut arity=vec![-7i32;nn];arity[parent]=na as i32;
  let mut offset=vec![0u64;nn];offset[parent]=off as u64;
  let mut childstart=vec![0u32;nn];childstart[parent]=cs as u32;
  let mut children=vec![0xdead_beefu32;na+4];for a in 0..na {children[cs+a]=(4+a) as u32;}
  let mut rsrc=vec![0u32;nn];rsrc[parent]=3;
  let reach:Vec<f32>=(0..6*nh.max(1)+7).map(|i|value(i+19,mode).abs()).collect();
  let mut lock=vec![-1i64;nn];if role==1 {lock[parent]=loff as i64;}
  let mut sigma=vec![f32::from_bits(0x7fc0_cafe);loff+na*nh+17];
  for a in 0..na {for i in 0..nh {sigma[loff+a*nh+i]=(a+1) as f32/((na*(na+1)/2) as f32);}}
  let mut slots:Vec<u32>=(0..nn as u32).collect();for a in 0..na {slots[4+a]=(4+na-1-a) as u32;}
  assert_eq!(slots[parent],parent as u32);
  for child in &children[cs..cs+na] {assert_ne!(slots[parent],slots[*child as usize],"parent/child CFVrows overlap");}
  let discounts=Discounts::for_iteration(if algo==0 {Algorithm::Dcfr}else{Algorithm::CfrPlus},t);
  let disc=vec![discounts.pos,discounts.neg,discounts.strat];
  let mut regret=vec![f32::from_bits(0x7fc0_aa55);off+na*nh+17];let mut strategy=regret.clone();
  for i in 0..na*nh {regret[off+i]=value(i+index,mode);strategy[off+i]=value(i+index+3,mode).abs();}
  let mut cfv:Vec<f32>=(0..(nn+3)*max+17).map(|i|value(i+index*7,mode)).collect();
  for i in parent*max..parent*max+max {cfv[i]=f32::from_bits(0x7fc0_babe);}
  let immutable=vec![nodes.clone(),player.iter().map(|x|*x as u32).collect(),arity.iter().map(|x|*x as u32).collect(),split64(offset.iter().copied()),childstart.clone(),children.clone(),rsrc.clone(),fb(&reach),split64(lock.iter().map(|x|*x as u64)),fb(&sigma),slots.clone(),fb(&disc)];
  id(&mut input,index);words(&mut input,&[nh as u32,na as u32,block,p as u32,role,algo,t,mode,count as u32,max as u32,start as u32,parent as u32,off as u32,loff as u32]);
  for v in &immutable {words(&mut input,v);}for v in [&regret,&strategy,&cfv] {words(&mut input,&fb(v));}
  input.flush().unwrap();
  let dn=stream.clone_htod(&nodes).unwrap();let dp=stream.clone_htod(&player).unwrap();let da=stream.clone_htod(&arity).unwrap();let doff=stream.clone_htod(&offset).unwrap();let dcs=stream.clone_htod(&childstart).unwrap();let dc=stream.clone_htod(&children).unwrap();let drs=stream.clone_htod(&rsrc).unwrap();let drp=stream.clone_htod(&reach).unwrap();let dl=stream.clone_htod(&lock).unwrap();let dls=stream.clone_htod(&sigma).unwrap();let dslot=stream.clone_htod(&slots).unwrap();let dd=stream.clone_htod(&disc).unwrap();
  let mut expected:Option<Vec<Vec<u32>>>=None;
  let mut device_ranges=Vec::new();
  for (label,f) in [("baseline",&bf),("candidate",&cf)] {
   let mut dr=stream.clone_htod(&regret).unwrap();let mut ds=stream.clone_htod(&strategy).unwrap();let mut dv=stream.clone_htod(&cfv).unwrap();let nharg=nh as i32;let maxarg=max as i32;
   device_ranges.push(serde_json::json!({"arm":label,"regions":disjoint_regions(&stream,[&dr,&ds,&dv])}));
   unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&p).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&mut dr).arg(&mut ds).arg(&drs).arg(&drp).arg(&dl).arg(&dls).arg(&dslot).arg(&mut dv).arg(&dd).arg(&nharg).arg(&maxarg).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}
   stream.synchronize().unwrap();let result=vec![readf(&stream,&dr),readf(&stream,&ds),readf(&stream,&dv)];
   let out=if label=="baseline" {&mut baseline}else{&mut candidate};id(out,index);for v in &result {words(out,v);}out.flush().unwrap();
   let mut post=vec![stream.clone_dtoh(&dn).unwrap(),stream.clone_dtoh(&dp).unwrap().iter().map(|x|*x as u32).collect(),stream.clone_dtoh(&da).unwrap().iter().map(|x|*x as u32).collect(),split64(stream.clone_dtoh(&doff).unwrap()),stream.clone_dtoh(&dcs).unwrap(),stream.clone_dtoh(&dc).unwrap(),stream.clone_dtoh(&drs).unwrap()];
   post.push(readf(&stream,&drp));post.push(split64(stream.clone_dtoh(&dl).unwrap().iter().map(|x|*x as u64)));post.push(readf(&stream,&dls));post.push(stream.clone_dtoh(&dslot).unwrap());post.push(readf(&stream,&dd));stream.synchronize().unwrap();
   let pi=if label=="baseline" {&mut bi}else{&mut ci};id(pi,index);for v in &post {words(pi,v);}pi.flush().unwrap();
   assert_eq!(post,immutable,"immutable inputs case{index}/{label}");
   let seeds=[fb(&regret),fb(&strategy),fb(&cfv)];
   for kind in 0..3 {for i in 0..result[kind].len() {
    let owned=count!=0 && if kind<2 {role==0 && i>=off && i<off+na*nh}else{i>=parent*max && i<parent*max+nh};
    if !owned {assert_eq!(result[kind][i],seeds[kind][i],"guard {index}/{label}/{kind}/{i}");guard_words+=1;}
   }}
   if let Some(ref before)=expected {assert_eq!(&result,before,"original/candidate case{index}");}else{expected=Some(result.clone());}
   output_words+=result.iter().map(|v|v.len() as u64).sum::<u64>();immutable_words+=immutable.iter().map(|v|v.len() as u64).sum::<u64>();
  }
  emit(serde_json::json!({"stage":"case","id":index,"hands":nh,"actions":na,"threads":block,"p":p,"role":role,"algorithm":algo,"iteration":t,"value_mode":mode,"count":count,"discount_bits":fb(&disc),"output_words_per_arm":regret.len()+strategy.len()+cfv.len(),"immutable_words_per_arm":immutable.iter().map(Vec::len).sum::<usize>(),"all_raw_exact":true,"guards_exact":true,"disjoint_device_ranges":device_ranges,"parent_child_rows_disjoint":true}));
 }
 stream.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(stream);ctx.check_err().unwrap();
 for f in [&mut input,&mut baseline,&mut candidate,&mut bi,&mut ci] {f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 emit(serde_json::json!({"stage":"complete","cases":case_count,"kernel_launches":2*case_count,"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guard_words,"all_raw_exact":true,"all_inputs_and_guards_exact":true,"raw_device_inputs_retained_both_arms":true,"performance_measurement":false,"solver_executions":0,"candidate_accepted":false}));
}
