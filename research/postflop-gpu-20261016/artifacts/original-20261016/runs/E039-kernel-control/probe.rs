//! Direct old/new up_chance GPU equivalence; no solver or timing score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,DeviceRepr,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use std::{fs::{File,OpenOptions},io::Write,path::PathBuf,sync::Arc,fmt::Debug};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E039_UNIT {v}").unwrap();o.flush().unwrap();}
fn file(p:PathBuf)->File{OpenOptions::new().create_new(true).write(true).open(p).unwrap()}
fn u32s(f:&mut File,v:&[u32]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();for x in v{f.write_all(&x.to_le_bytes()).unwrap();}}
fn u64s(f:&mut File,v:&[u64]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();for x in v{f.write_all(&x.to_le_bytes()).unwrap();}}
fn unchanged<T:DeviceRepr+PartialEq+Debug>(s:&Arc<CudaStream>,d:&CudaSlice<T>,h:&[T]){assert_eq!(s.clone_dtoh(d).unwrap(),h);}
fn main(){
 let out=PathBuf::from(std::env::var_os("E039_KERNEL_CONTROL_DIR").expect("fresh output directory required"));std::fs::create_dir(&out).unwrap();
 let mut inputs=file(out.join("inputs.bin"));inputs.write_all(b"E039_IN1").unwrap();
 let mut old_output=file(out.join("baseline.bin"));let mut new_output=file(out.join("candidate.bin"));
 old_output.write_all(b"E039_OUT1").unwrap();new_output.write_all(b"E039_OUT1").unwrap();
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let mb=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let mc=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
 let fb=mb.load_function("up_chance").unwrap();let fc=mc.load_function("up_chance").unwrap();
 // (hands,children,block threads,inverse bits,nonfinite values,all blocked,count)
 let mut cases:Vec<(usize,usize,u32,u32,bool,bool,i32)>=Vec::new();
 for width in 0..=53{for nh in [1,129,257]{cases.push((nh,width,128,(1.0f32/44.0).to_bits(),false,false,1));}}
 cases.extend([
  (0,52,128,1.0f32.to_bits(),false,false,1),
  (1326,52,128,(1.0f32/44.0).to_bits(),false,false,1),
  (257,64,128,(1.0f32/44.0).to_bits(),false,false,1),
  (7,52,1,(1.0f32/44.0).to_bits(),false,false,1),
  (129,52,32,(1.0f32/44.0).to_bits(),false,false,1),
  (129,52,64,(1.0f32/44.0).to_bits(),false,false,1),
  (129,52,256,(1.0f32/44.0).to_bits(),false,false,1),
  (257,52,128,(-0.0f32).to_bits(),false,false,1),
  (257,52,128,1.0f32.to_bits(),true,false,1),
  (257,0,128,(-0.0f32).to_bits(),false,false,1),
  (257,52,128,f32::INFINITY.to_bits(),false,false,1),
  (129,52,128,1.0f32.to_bits(),false,true,1),
  (129,52,128,1.0f32.to_bits(),false,false,0)]);
 assert_eq!(cases.len(),175);let mut words=0u64;let mut unchanged_words=0u64;
 for (id,&(nh,nc,block,inv_bits,nonfinite,blocked,count)) in cases.iter().enumerate(){
  let nn=nc+8;let nh_max=nh+5;let start=1i32;let parent=2usize;
  let nodes=vec![0xdeadbeefu32,parent as u32,0xdeadbeefu32];
  let mut cc_start=vec![0u32;nn];let mut cc_count=vec![0u32;nn];cc_start[parent]=2;cc_count[parent]=nc as u32;
  let mut cards=vec![0xabcdef01u32;nc+4];let mut children=vec![0xabcdef01u32;nc+4];let mut perm=vec![0xabcdef01u32;nc+4];
  let mut slots:Vec<u32>=(0..nn as u32).collect();
  for j in 0..nc{cards[2+j]=((j*17+3)%52) as u32;children[2+j]=(4+j) as u32;perm[2+j]=(j%3) as u32;slots[4+j]=(4+nc-1-j) as u32;}
  let mut inv=vec![1.0f32;nn];inv[parent]=f32::from_bits(inv_bits);
  let mut masks=vec![0u64;nh.max(1)];for i in 0..nh{masks[i]=if blocked{u64::MAX}else{(1u64<<(i%52))|(1u64<<((i+13)%52))};}
  let mut hands=vec![0u32;(3*nh).max(1)];for i in 0..nh{hands[i]=i as u32;hands[nh+i]=(nh-1-i) as u32;hands[2*nh+i]=((i+3)%nh) as u32;}
  let finite=[0.0f32,-0.0,0.25,-0.75,1e10,-1e10,f32::from_bits(1),f32::from_bits(0x80000001)];
  let special=[f32::INFINITY,f32::NEG_INFINITY,f32::from_bits(0x7fc01234),f32::from_bits(0xffc05678)];
  let mut seed=vec![0.0f32;(nn+3)*nh_max+17];for (i,v) in seed.iter_mut().enumerate(){*v=if nonfinite && i%11==0{special[(i/11)%4]}else{finite[(i*5+i/nh_max*17)%finite.len()]};}
  u32s(&mut inputs,&[id as u32,nh as u32,nc as u32,block,inv_bits,nonfinite as u32,blocked as u32,count as u32,nh_max as u32]);
  for v in [&nodes,&cc_start,&cc_count,&cards,&children,&perm]{u32s(&mut inputs,v);}
  u32s(&mut inputs,&inv.iter().map(|v|v.to_bits()).collect::<Vec<_>>());u64s(&mut inputs,&masks);u32s(&mut inputs,&hands);u32s(&mut inputs,&slots);u32s(&mut inputs,&seed.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
  let dn=stream.clone_htod(&nodes).unwrap();let ds=stream.clone_htod(&cc_start).unwrap();let dc=stream.clone_htod(&cc_count).unwrap();
  let dcard=stream.clone_htod(&cards).unwrap();let dchild=stream.clone_htod(&children).unwrap();let dp=stream.clone_htod(&perm).unwrap();let di=stream.clone_htod(&inv).unwrap();let dm=stream.clone_htod(&masks).unwrap();let dh=stream.clone_htod(&hands).unwrap();let dslot=stream.clone_htod(&slots).unwrap();
  let mut expected:Option<Vec<u32>>=None;
  for (name,f) in [("baseline",&fb),("candidate",&fc)]{
   let mut data=stream.clone_htod(&seed).unwrap();let nh_arg=nh as i32;let max_arg=nh_max as i32;
   unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&ds).arg(&dc).arg(&dcard).arg(&dchild).arg(&dp).arg(&di).arg(&dm).arg(&dh).arg(&dslot).arg(&mut data).arg(&nh_arg).arg(&max_arg).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}
   stream.synchronize().unwrap();let result=stream.clone_dtoh(&data).unwrap();let bits:Vec<u32>=result.iter().map(|x|x.to_bits()).collect();
   for i in 0..bits.len(){if count==0 || i<parent*nh_max || i>=parent*nh_max+nh{assert_eq!(bits[i],seed[i].to_bits(),"guard {id}/{name}/{i}");}}
   if let Some(ref reference)=expected{assert_eq!(&bits,reference,"old/new case{id}");}else{expected=Some(bits.clone());}
   let file=if name=="baseline"{&mut old_output}else{&mut new_output};file.write_all(&(id as u32).to_le_bytes()).unwrap();u32s(file,&bits);
   words+=bits.len() as u64;
  }
  unchanged(&stream,&dn,&nodes);unchanged(&stream,&ds,&cc_start);unchanged(&stream,&dc,&cc_count);unchanged(&stream,&dcard,&cards);unchanged(&stream,&dchild,&children);unchanged(&stream,&dp,&perm);unchanged(&stream,&dm,&masks);unchanged(&stream,&dh,&hands);unchanged(&stream,&dslot,&slots);
  assert_eq!(stream.clone_dtoh(&di).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),inv.iter().map(|x|x.to_bits()).collect::<Vec<_>>());
  unchanged_words+=(nodes.len()+cc_start.len()+cc_count.len()+cards.len()+children.len()+perm.len()+inv.len()+hands.len()+slots.len()+2*masks.len()) as u64;
  emit(serde_json::json!({"stage":"case","id":id,"hands":nh,"children":nc,"block_threads":block,"count":count,"inverse_bits":inv_bits,"nonfinite_values":nonfinite,"all_blocked":blocked,"full_output_words":seed.len(),"exact":true,"guards_and_inputs_exact":true}));
 }
 stream.synchronize().unwrap();drop(fb);drop(fc);drop(mb);drop(mc);drop(stream);ctx.check_err().unwrap();
 for f in [&mut inputs,&mut old_output,&mut new_output]{f.flush().unwrap();f.sync_all().unwrap();}
 emit(serde_json::json!({"stage":"complete","cases":175,"kernel_launches":350,"full_output_words_retained_both_arms":words,"immutable_input_words_verified":unchanged_words,"all_bit_exact":true,"all_guards_and_inputs_exact":true,"performance_measurement":false,"solver_executions":0,"candidate_accepted":false}));
}
