//! Finite full-device input/output comparison. No solver or performance score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
use cudarc::driver::sys;
include!("lock_arg.rs");
type Out=BufWriter<File>;
fn file(p:PathBuf,magic:&[u8])->Out{let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(p).unwrap());f.write_all(magic).unwrap();f}
fn words(f:&mut Out,v:&[u32]){f.write_all(&(v.len()as u64).to_le_bytes()).unwrap();for x in v{f.write_all(&x.to_le_bytes()).unwrap();}}
fn id(f:&mut Out,n:usize){f.write_all(&(n as u32).to_le_bytes()).unwrap();}
fn fb(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn split64(v:impl IntoIterator<Item=u64>)->Vec<u32>{v.into_iter().flat_map(|x|[x as u32,(x>>32)as u32]).collect()}
fn readf(s:&Arc<CudaStream>,d:&CudaSlice<f32>)->Vec<u32>{let v=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();fb(&v)}
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E106_DOWN {v}").unwrap();o.flush().unwrap();}
fn reach(i:usize,mode:usize)->f32{match mode{
 1=>0.0,2=>-0.0,3=>if i%2==0{0.0}else{-0.0},
 4=>[0.0,-0.0,f32::INFINITY,f32::NEG_INFINITY,f32::from_bits(0x7fc0_1234),f32::from_bits(0xffc0_5678),1.25,-3.5][i%8],
 _=>[0.0,-0.0,0.5,1.0,1e-20,f32::from_bits(1),1e20][i%7]}}
fn regret(i:usize,a:usize,mode:usize)->f32{match mode{
 1=>if(a+i)%2==0{0.0}else{-0.0},
 2=>[-1.0,-0.0,f32::NEG_INFINITY,f32::from_bits(0x7fc0_4321),-f32::from_bits(1)][(i+a)%5],
 3=>f32::MAX,
 4=>[f32::INFINITY,f32::NEG_INFINITY,f32::from_bits(0x7fc0_1234),f32::from_bits(0xffc0_5678),0.0,-0.0,2.5][(i+a)%7],
 5=>[f32::from_bits(1),-f32::from_bits(1),f32::MIN_POSITIVE,f32::from_bits(0x0080_0001),1e-13,1e-12,1.000001e-12][(i+a)%7],
 6=>if a==0{f32::MAX/2.0}else{if(i+a)%2==0{0.0}else{1.0}},
 _=>[0.0,-0.0,0.25,-0.75,13.25,-7.125,1e10,-1e10,1e-20,-1e-20][(i*5+a*3+i/11)%10]}}
fn main(){
 let out=PathBuf::from(std::env::args().nth(1).expect("fresh output"));std::fs::create_dir(&out).unwrap();
 let corpus:Vec<serde_json::Value>=serde_json::from_str(include_str!("corpus.json")).unwrap();
 let mut input=file(out.join("inputs.bin"),b"E106_DOWN_IN1");let mut baseline=file(out.join("baseline.bin"),b"E106_DOWN_OUT1");let mut candidate=file(out.join("candidate.bin"),b"E106_DOWN_OUT1");let mut bi=file(out.join("baseline-inputs.bin"),b"E106_DOWN_IM1");let mut ci=file(out.join("candidate-inputs.bin"),b"E106_DOWN_IM1");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));let s=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();let bf=bm.load_function("down_action").unwrap();let cf=cm.load_function("down_action").unwrap();
 let mut output_words=0u64;let mut immutable_words=0u64;let mut guard_words=0u64;let mut zero_words=0u64;
 for(index,c)in corpus.iter().enumerate(){
  let get=|name:&str|c[name].as_u64().unwrap()as usize;
  let nh=get("nh");let na=get("na");let block=get("block")as u32;let actor=get("actor");let locked=get("lock_mode");let rm=get("regret_mode");let pm=get("reach_mode");let count=get("count")as i32;
  let nullable=c["nullable"].as_bool().unwrap();let reuse=c["reuse_zero"].as_bool().unwrap();let other=if nh==0{5}else{nh+5};let mut nhs=if actor==0{[nh,other]}else{[other,nh]};if reuse{nhs[1]=0;}let active_nh=nhs[actor];let nn=na+9;let parent=2;let off=13;let cs=2;let loff=7;let rows=na+10;let start=1i32;
  let nodes=vec![0xdead_beefu32,parent as u32,0xdead_beef];let mut player=vec![-7i32;nn];player[parent]=actor as i32;let mut arity=vec![-7i32;nn];arity[parent]=na as i32;let mut offsets=vec![0u64;nn];offsets[parent]=off as u64;let mut childstart=vec![0u32;nn];childstart[parent]=cs as u32;
  let mut children=vec![0xdead_beefu32;na+4];let mut rs0=vec![0u32;nn];let mut rs1=vec![0u32;nn];rs0[parent]=2;rs1[parent]=3;
  for a in 0..na{children[cs+a]=(4+a)as u32;rs0[4+a]=(5+na-1-a)as u32;rs1[4+a]=(5+na-1-a)as u32;}
  let mut lock=vec![-1i64;nn];if locked>0{lock[parent]=loff as i64;}
  assert!(!nullable || lock.iter().all(|x|*x<0),"null only for globally unlocked table");
  let mut sigma=vec![f32::from_bits(0x7fc0_cafe);loff+na*nh+19];for a in 0..na{for i in 0..nh{sigma[loff+a*nh+i]=match locked{2=>reach(i+a,4),3=>if(i+a)%2==0{-0.25}else{0.5},_=>1.0/(na as f32)};}}
  let mut regs=[vec![f32::from_bits(0x7fc0_aa55);off+na*nhs[0]+17],vec![f32::from_bits(0x7fc0_aa55);off+na*nhs[1]+17]];
  for p in 0..2{for a in 0..na{for i in 0..nhs[p]{regs[p][off+a*nhs[p]+i]=regret(i+index,a,rm);}}}
  let mut reaches=[vec![f32::from_bits(0x7fc0_babe);rows*nhs[0].max(1)+17],vec![f32::from_bits(0x7fc0_babe);rows*nhs[1].max(1)+17]];
  for p in 0..2{let src=if p==0{2}else{3};for i in 0..nhs[p]{reaches[p][src*nhs[p]+i]=reach(i+index,if p==actor{pm}else{4});}}
  let imm=vec![nodes.clone(),player.iter().map(|x|*x as u32).collect(),arity.iter().map(|x|*x as u32).collect(),split64(offsets.iter().copied()),childstart.clone(),children.clone(),rs0.clone(),rs1.clone(),fb(&regs[0]),fb(&regs[1]),split64(lock.iter().map(|x|*x as u64)),fb(&sigma)];
  id(&mut input,index);words(&mut input,&[nhs[0]as u32,nhs[1]as u32,na as u32,block,actor as u32,locked as u32,rm as u32,pm as u32,count as u32,start as u32,parent as u32,off as u32,loff as u32,cs as u32,rows as u32,nullable as u32,reuse as u32]);for v in &imm{words(&mut input,v);}for v in &reaches{words(&mut input,&fb(v));}input.flush().unwrap();
  let dn=s.clone_htod(&nodes).unwrap();let dp=s.clone_htod(&player).unwrap();let da=s.clone_htod(&arity).unwrap();let doff=s.clone_htod(&offsets).unwrap();let dcs=s.clone_htod(&childstart).unwrap();let dc=s.clone_htod(&children).unwrap();let drs0=s.clone_htod(&rs0).unwrap();let drs1=s.clone_htod(&rs1).unwrap();let dr0=s.clone_htod(&regs[0]).unwrap();let dr1=s.clone_htod(&regs[1]).unwrap();let dl=s.clone_htod(&lock).unwrap();let dls=s.clone_htod(&sigma).unwrap();let mut expected=None;
  for(label,f)in[("baseline",&bf),("candidate",&cf)]{
   let mut d0=s.clone_htod(&reaches[0]).unwrap();let mut d1=s.clone_htod(&reaches[1]).unwrap();let nh0=nhs[0]as i32;let nh1=nhs[1]as i32;
   unsafe{s.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&drs0).arg(&drs1).arg(&dr0).arg(&dr1).arg(E106LockArg(&dl,label=="candidate" && nullable)).arg(&dls).arg(&mut d0).arg(&mut d1).arg(&nh0).arg(&nh1).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}
   s.synchronize().unwrap();let result=vec![readf(&s,&d0),readf(&s,&d1)];let dst=if label=="baseline"{&mut baseline}else{&mut candidate};id(dst,index);for v in &result{words(dst,v);}dst.flush().unwrap();
   let post=vec![s.clone_dtoh(&dn).unwrap(),s.clone_dtoh(&dp).unwrap().iter().map(|x|*x as u32).collect(),s.clone_dtoh(&da).unwrap().iter().map(|x|*x as u32).collect(),split64(s.clone_dtoh(&doff).unwrap()),s.clone_dtoh(&dcs).unwrap(),s.clone_dtoh(&dc).unwrap(),s.clone_dtoh(&drs0).unwrap(),s.clone_dtoh(&drs1).unwrap(),readf(&s,&dr0),readf(&s,&dr1),split64(s.clone_dtoh(&dl).unwrap().iter().map(|x|*x as u64)),readf(&s,&dls)];s.synchronize().unwrap();let pi=if label=="baseline"{&mut bi}else{&mut ci};id(pi,index);for v in &post{words(pi,v);}pi.flush().unwrap();assert_eq!(post,imm,"all actual immutable inputs {index}/{label}");
   for p in 0..2{for i in 0..result[p].len(){let live=count!=0&&p==actor&&active_nh>0&&i/active_nh>=5&&i/active_nh<5+na;if !live{assert_eq!(result[p][i],reaches[p][i].to_bits(),"full guard {index}/{label}/{p}/{i}");guard_words+=1;}else if result[p][i]&0x7fff_ffff==0{zero_words+=1;}}}
   if let Some(ref prev)=expected{assert_eq!(&result,prev,"all output words {index}");}else{expected=Some(result.clone());}output_words+=result.iter().map(|v|v.len()as u64).sum::<u64>();immutable_words+=imm.iter().map(|v|v.len()as u64).sum::<u64>();
  }
  emit(serde_json::json!({"stage":"case","id":index,"case":c,"all_raw_outputs_and_inputs_exact":true,"all_guards_exact":true}));
 }
 s.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(s);ctx.check_err().unwrap();for f in[&mut input,&mut baseline,&mut candidate,&mut bi,&mut ci]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 emit(serde_json::json!({"stage":"complete","cases":corpus.len(),"kernel_launches":2*corpus.len(),"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guard_words,"active_zero_words_both_arms":zero_words,"performance_measurement":false}));
}
