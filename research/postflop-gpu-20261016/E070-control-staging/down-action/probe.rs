//! E070: exact original/candidate down_action full raw controls, no timing score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
type Out=BufWriter<File>;
fn file(p:PathBuf,magic:&[u8])->Out{assert_eq!(magic.len(),16);let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(p).unwrap());f.write_all(magic).unwrap();f}
fn words(f:&mut Out,v:&[u32]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();let b:Vec<u8>=v.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();}
fn id(f:&mut Out,n:usize){f.write_all(&(n as u32).to_le_bytes()).unwrap();}
fn fb(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn split64(v:impl IntoIterator<Item=u64>)->Vec<u32>{v.into_iter().flat_map(|x|[x as u32,(x>>32) as u32]).collect()}
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E070_DOWN_RAW {v}").unwrap();o.flush().unwrap();}
fn readf(s:&Arc<CudaStream>,d:&CudaSlice<f32>)->Vec<u32>{let v=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();fb(&v)}
fn value(i:usize,mode:u32)->f32{
 match mode {
  1=>if i%2==0{0.0}else{-0.0},
  2=>[1e-13,-1e-13,0.0,-0.0][i%4],
  3=>[f32::INFINITY,f32::NEG_INFINITY,f32::from_bits(0x7fc0_1234),f32::from_bits(0xffc0_5678),0.25,-0.75,1.0][i%7],
  4=>[f32::MAX,f32::MAX,-f32::MAX,1.0][i%4],
  5=>[f32::from_bits(1),-f32::from_bits(1),0.0,-0.0,f32::MIN_POSITIVE,-f32::MIN_POSITIVE,f32::from_bits(0x0080_0001)][i%7],
  6=>[f32::from_bits(0x2b8c_bccc),f32::from_bits(0x2b8c_bccd),f32::from_bits(0x2b8c_bcce),0.0,-1e-12][i%5],
  _=>[0.0,-0.0,0.25,-0.75,13.25,-7.125,1e10,-1e10,1e-20,-1e-20][(i*5+i/11)%10],
 }
}
fn u(c:&serde_json::Value,k:&str)->usize{c[k].as_u64().unwrap() as usize}
fn main(){
 let dir=PathBuf::from(std::env::var_os("E070_DOWN_RAW_DIR").expect("fresh raw directory required"));std::fs::create_dir(&dir).unwrap();
 let mut input=file(dir.join("inputs.bin"),b"E070-DOWN-IN1\0\0\0");
 let mut baseline=file(dir.join("baseline.bin"),b"E070-DOWN-OUT1\0\0");let mut candidate=file(dir.join("candidate.bin"),b"E070-DOWN-OUT1\0\0");
 let mut bi=file(dir.join("baseline-inputs.bin"),b"E070-DOWN-IM1\0\0\0");let mut ci=file(dir.join("candidate-inputs.bin"),b"E070-DOWN-IM1\0\0\0");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
 let bf=bm.load_function("down_action").unwrap();let cf=cm.load_function("down_action").unwrap();
 let corpus:serde_json::Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let cases=corpus["cases"].as_array().unwrap();assert_eq!(cases.len(),1196);
 let mut output_words=0u64;let mut immutable_words=0u64;let mut guard_words=0u64;
 for (index,c) in cases.iter().enumerate(){
  assert_eq!(u(c,"id"),index);let nh0=u(c,"nh0");let nh1=u(c,"nh1");let na=u(c,"actions");let block=u(c,"threads") as u32;let actor=c["actor"].as_i64().unwrap() as i32;let locked=u(c,"locked");let mode=u(c,"value_mode") as u32;let count=u(c,"count") as i32;let loff=u(c,"sigma_offset");
  let nn=na+9;let parent=3usize;let off=13usize;let cs=2usize;let start=2i32;let nha=if actor==0{nh0}else{nh1};let slots=10+2*na;
  let nodes=vec![0xdead_beefu32,0xdead_beef,parent as u32,0xdead_beef,0xdead_beef];
  let mut player=vec![255i32;nn];player[parent]=actor;let mut arity=vec![255i32;nn];arity[parent]=na as i32;
  let mut offset=vec![0u64;nn];offset[parent]=off as u64;let mut childstart=vec![0u32;nn];childstart[parent]=cs as u32;
  let mut children=vec![0xdead_beefu32;na+4];let mut rsrc0=vec![0u32;nn];let mut rsrc1=vec![0u32;nn];rsrc0[parent]=3;rsrc1[parent]=5;
  for a in 0..na{children[cs+a]=(4+a) as u32;rsrc0[4+a]=(8+2*(na-1-a)) as u32;rsrc1[4+a]=(9+2*a) as u32;}
  let reach0:Vec<f32>=(0..slots*nh0.max(1)+17).map(|i|value(i+index*7+19,mode).abs()).collect();
  let reach1:Vec<f32>=(0..slots*nh1.max(1)+17).map(|i|value(i+index*11+29,mode).abs()).collect();
  let mut lock=vec![-1i64;nn];if locked!=0{lock[parent]=loff as i64;}
  let mut sigma=vec![f32::from_bits(0x7fc0_cafe);loff+na*nha+17];for a in 0..na{for i in 0..nha{sigma[loff+a*nha+i]=if mode==0{(a+1) as f32/((na*(na+1)/2) as f32)}else{value(a*nha+i+index+3,mode)};}}
  let mut regret0=vec![f32::from_bits(0x7fc0_aa55);off+na*nh0+17];let mut regret1=vec![f32::from_bits(0x7fc0_bb66);off+na*nh1+17];
  for i in 0..na*nh0{regret0[off+i]=value(i+index,mode);}for i in 0..na*nh1{regret1[off+i]=value(i+index+5,mode);}
  let attrs:Vec<u16>=player.iter().zip(&arity).map(|(&p,&a)|{assert!((0..=255).contains(&p)&&(0..=255).contains(&a));((p as u16)<<8)|(a as u16)}).collect();
  let immutable=vec![nodes.clone(),player.iter().map(|x|*x as u32).collect(),arity.iter().map(|x|*x as u32).collect(),split64(offset.iter().copied()),childstart.clone(),children.clone(),rsrc0.clone(),rsrc1.clone(),fb(&regret0),fb(&regret1),split64(lock.iter().map(|x|*x as u64)),fb(&sigma),attrs.iter().map(|&x|x as u32).collect()];
  id(&mut input,index);words(&mut input,&[nh0 as u32,nh1 as u32,na as u32,block,actor as u32,locked as u32,mode,count as u32,loff as u32,start as u32,parent as u32,off as u32]);for v in &immutable{words(&mut input,v);}words(&mut input,&fb(&reach0));words(&mut input,&fb(&reach1));input.flush().unwrap();
  let dn=stream.clone_htod(&nodes).unwrap();let dp=stream.clone_htod(&player).unwrap();let da=stream.clone_htod(&arity).unwrap();let doff=stream.clone_htod(&offset).unwrap();let dcs=stream.clone_htod(&childstart).unwrap();let dc=stream.clone_htod(&children).unwrap();let drs0=stream.clone_htod(&rsrc0).unwrap();let drs1=stream.clone_htod(&rsrc1).unwrap();let dg0=stream.clone_htod(&regret0).unwrap();let dg1=stream.clone_htod(&regret1).unwrap();let dl=stream.clone_htod(&lock).unwrap();let dls=stream.clone_htod(&sigma).unwrap();let dattrs=stream.clone_htod(&attrs).unwrap();
  let mut expected:Option<Vec<Vec<u32>>>=None;
  for (label,f) in [("baseline",&bf),("candidate",&cf)]{
   let mut dr0=stream.clone_htod(&reach0).unwrap();let mut dr1=stream.clone_htod(&reach1).unwrap();let n0=nh0 as i32;let n1=nh1 as i32;
   unsafe{
    let mut launch=stream.launch_builder(f);launch.arg(&dn).arg(&start).arg(&count);
    if label=="baseline"{launch.arg(&dp).arg(&da);}else{launch.arg(&dattrs);}
    launch.arg(&doff).arg(&dcs).arg(&dc).arg(&drs0).arg(&drs1)
      .arg(&dg0).arg(&dg1).arg(&dl).arg(&dls).arg(&mut dr0).arg(&mut dr1)
      .arg(&n0).arg(&n1).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();
   }
   stream.synchronize().unwrap();let result=vec![readf(&stream,&dr0),readf(&stream,&dr1)];let out=if label=="baseline"{&mut baseline}else{&mut candidate};id(out,index);for v in &result{words(out,v);}out.flush().unwrap();
   let post=vec![stream.clone_dtoh(&dn).unwrap(),stream.clone_dtoh(&dp).unwrap().iter().map(|x|*x as u32).collect(),stream.clone_dtoh(&da).unwrap().iter().map(|x|*x as u32).collect(),split64(stream.clone_dtoh(&doff).unwrap()),stream.clone_dtoh(&dcs).unwrap(),stream.clone_dtoh(&dc).unwrap(),stream.clone_dtoh(&drs0).unwrap(),stream.clone_dtoh(&drs1).unwrap(),readf(&stream,&dg0),readf(&stream,&dg1),split64(stream.clone_dtoh(&dl).unwrap().iter().map(|x|*x as u64)),readf(&stream,&dls),stream.clone_dtoh(&dattrs).unwrap().iter().map(|&x|x as u32).collect()];stream.synchronize().unwrap();
   let pi=if label=="baseline"{&mut bi}else{&mut ci};id(pi,index);for v in &post{words(pi,v);}pi.flush().unwrap();assert_eq!(post,immutable,"immutable case{index}/{label}");
   let seeds=[fb(&reach0),fb(&reach1)];let maps=[&rsrc0,&rsrc1];let nhs=[nh0,nh1];let active=if actor==0{0}else{1};
   for arm in 0..2{for i in 0..result[arm].len(){let owned=count!=0&&arm==active&&nhs[arm]!=0&&(0..na).any(|a|{let base=maps[arm][4+a] as usize*nhs[arm];i>=base&&i<base+nhs[arm]});if !owned{assert_eq!(result[arm][i],seeds[arm][i],"guard{index}/{label}/{arm}/{i}");guard_words+=1;}}}
   if let Some(ref before)=expected{assert_eq!(&result,before,"original/candidate{index}");}else{expected=Some(result.clone());}
   output_words+=result.iter().map(|v|v.len() as u64).sum::<u64>();immutable_words+=immutable.iter().map(|v|v.len() as u64).sum::<u64>();
  }
  emit(serde_json::json!({"stage":"case","id":index,"nh0":nh0,"nh1":nh1,"actions":na,"threads":block,"actor":actor,"locked":locked,"value_mode":mode,"count":count,"sigma_offset":loff,"output_words_per_arm":reach0.len()+reach1.len(),"immutable_words_per_arm":immutable.iter().map(Vec::len).sum::<usize>(),"all_raw_exact":true,"guards_exact":true}));
 }
 stream.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(stream);ctx.check_err().unwrap();
 for f in [&mut input,&mut baseline,&mut candidate,&mut bi,&mut ci]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 emit(serde_json::json!({"stage":"complete","cases":cases.len(),"kernel_launches":2*cases.len(),"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guard_words,"all_raw_exact":true,"all_inputs_and_guards_exact":true,"raw_device_inputs_retained_both_arms":true,"performance_measurement":false,"solver_executions":0,"candidate_accepted":false}));
}
