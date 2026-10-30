//! E068 exact original/new bit-selected up_chance comparator, no timing score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
type Out=BufWriter<File>;
fn emit(v:Value){let mut o=std::io::stdout().lock();writeln!(o,"E068_CONTROL {v}").unwrap();o.flush().unwrap();}
fn file(p:PathBuf,magic:&[u8])->Out{let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(p).unwrap());f.write_all(magic).unwrap();f}
fn u32w(f:&mut Out,v:u32){f.write_all(&v.to_le_bytes()).unwrap();}
fn vecw(f:&mut Out,v:&[u32]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();for x in v{u32w(f,*x);}}
fn vecs(f:&mut Out,v:&[Vec<u32>]){u32w(f,v.len() as u32);for x in v{vecw(f,x);}}
fn bits(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn split(v:&[u64])->Vec<u32>{v.iter().flat_map(|&x|[x as u32,(x>>32) as u32]).collect()}
fn du32(s:&Arc<CudaStream>,v:&CudaSlice<u32>)->Vec<u32>{let x=s.clone_dtoh(v).unwrap();s.synchronize().unwrap();x}
fn du64(s:&Arc<CudaStream>,v:&CudaSlice<u64>)->Vec<u32>{let x=s.clone_dtoh(v).unwrap();s.synchronize().unwrap();split(&x)}
fn df32(s:&Arc<CudaStream>,v:&CudaSlice<f32>)->Vec<u32>{let x=s.clone_dtoh(v).unwrap();s.synchronize().unwrap();bits(&x)}
fn float(i:usize,mode:usize)->f32{match mode{
 0=>1.0+(i%257) as f32/32.0,
 1=>[0x00000000,0x80000000,0x00000001,0x80000001,0x00800000,0x80800000,0x7f800000,0xff800000,0x7fc01234,0xffc05678,0x3f800000,0xbf800000].map(f32::from_bits)[i%12],
 _=>[f32::MAX,-f32::MAX,1e-20,-1e-20,13.25,-7.125][i%6],}}
fn hands(n:usize,salt:usize)->(Vec<u32>,Vec<u32>,Vec<u64>){
 let all:Vec<_>=(0..52u32).flat_map(|a|(a+1..52u32).map(move|b|(a,b))).collect();assert_eq!(all.len(),1326);
 let mut a=vec![0; n.max(1)+3];let mut b=vec![0;n.max(1)+3];let mut m=vec![0;n.max(1)+3];
 for i in 0..a.len(){let (c,d)=all[(i*73+salt)%all.len()];a[i]=c;b[i]=d;m[i]=(1u64<<c)|(1u64<<d);}(a,b,m)
}
struct Case{d:Vec<u32>,inv_bits:u32,mask_style:u32}
impl Case{fn family(&self)->usize{self.d[0] as usize}fn n0(&self)->usize{self.d[1] as usize}fn pad(&self)->usize{self.d[2] as usize}fn threads(&self)->u32{self.d[3]}fn active(&self)->bool{self.d[4]!=0}fn mode(&self)->usize{self.d[5] as usize}fn perm(&self)->usize{self.d[6] as usize}fn width(&self)->usize{self.d[7] as usize}fn pattern(&self)->usize{self.d[8] as usize}fn salt(&self)->usize{self.d[9] as usize}}
struct Up{nodes:Vec<u32>,start:Vec<u32>,count:Vec<u32>,card:Vec<u32>,child:Vec<u32>,perm:Vec<u32>,inv:Vec<f32>,mask:Vec<u64>,a:Vec<u32>,b:Vec<u32>,hp:Vec<u32>,slot:Vec<u32>,seed:Vec<f32>}
impl Up{
 fn new(c:&Case)->Self{
  let w=c.width();let n=c.n0();let nn=w+10;let nodes=vec![0xdeadbeef,2,0xdeadbeef];let mut start=vec![0;nn];let mut count=start.clone();start[2]=3;count[2]=w as u32;let mut card=vec![0xdeadbeef;w+6];let mut child=card.clone();let mut perm=card.clone();let mut slot=vec![0;nn];slot[2]=2;
  for j in 0..w{card[j+3]=match c.pattern(){0=>j as u32%52,1=>[0,25,51][j%3],2=>((j*17+13)%52) as u32,4=>0,5=>51,_=>((j+c.salt())%52) as u32};child[j+3]=(4+j) as u32;perm[j+3]=if c.perm()==0{0}else{(j%4) as u32};slot[4+j]=(4+w-1-j) as u32;}
  let mut inv=vec![f32::from_bits(0x7fc0eeee);nn];inv[2]=f32::from_bits(c.inv_bits);let(mut a,mut b,mut mask)=hands(n,c.salt());if c.mask_style!=0{for i in 0..a.len(){a[i]=0;b[i]=if c.mask_style==1{1+(i%51) as u32}else{1};mask[i]=(1u64<<a[i])|(1u64<<b[i]);}}let hp=(0..4*n+7).map(|i|if n>0{((i%n+(i/n)*17)%n) as u32}else{0}).collect();
  let seed=(0..(w+12)*(n+c.pad())+17).map(|i|float(i+c.salt(),c.mode())).collect();Self{nodes,start,count,card,child,perm,inv,mask,a,b,hp,slot,seed}
 }
 fn read_contract(&self,c:&Case)->u64{
  let n=c.n0();let stride=n+c.pad();let parent=self.slot[self.nodes[1] as usize] as usize;let lo=parent*stride;let hi=lo+n;assert!(hi<=self.seed.len());let mut checks=0;
  for j in 0..c.width(){let t=3+j;assert!(self.card[t]<52);let k=self.perm[t] as usize;assert!(k<4);let child=self.child[t] as usize;assert!(child<self.slot.len());
   for i in 0..n{let index=if k==0{i}else{let at=k*n+i;assert!(at<self.hp.len());self.hp[at] as usize};assert!(index<n);let address=self.slot[child] as usize*stride+index;assert!(address<self.seed.len() && (address<lo||address>=hi));checks+=1;}
  }checks
 }
 fn inputs(&self)->Vec<Vec<u32>>{vec![self.nodes.clone(),self.start.clone(),self.count.clone(),self.card.clone(),self.child.clone(),self.perm.clone(),bits(&self.inv),split(&self.mask),self.a.clone(),self.b.clone(),self.hp.clone(),self.slot.clone()]}
 fn seeds(&self)->Vec<Vec<u32>>{vec![bits(&self.seed)]}
 fn run(&self,c:&Case,s:&Arc<CudaStream>,f:&cudarc::driver::CudaFunction)->(Vec<Vec<u32>>,Vec<Vec<u32>>){
  let nodes=s.clone_htod(&self.nodes).unwrap();let cs=s.clone_htod(&self.start).unwrap();let cc=s.clone_htod(&self.count).unwrap();let card=s.clone_htod(&self.card).unwrap();let child=s.clone_htod(&self.child).unwrap();let perm=s.clone_htod(&self.perm).unwrap();let inv=s.clone_htod(&self.inv).unwrap();let mask=s.clone_htod(&self.mask).unwrap();let a=s.clone_htod(&self.a).unwrap();let b=s.clone_htod(&self.b).unwrap();let hp=s.clone_htod(&self.hp).unwrap();let slot=s.clone_htod(&self.slot).unwrap();let mut cfv=s.clone_htod(&self.seed).unwrap();
  let start=1i32;let count=if c.active(){1i32}else{0};let nh=c.n0() as i32;let stride=nh+c.pad() as i32;let cfg=LaunchConfig{grid_dim:(3,1,1),block_dim:(c.threads(),1,1),shared_mem_bytes:0};
  unsafe{s.launch_builder(f).arg(&nodes).arg(&start).arg(&count).arg(&cs).arg(&cc).arg(&card).arg(&child).arg(&perm).arg(&inv).arg(&mask).arg(&hp).arg(&slot).arg(&mut cfv).arg(&nh).arg(&stride).launch(cfg).unwrap();}
  s.synchronize().unwrap();let post=vec![du32(s,&nodes),du32(s,&cs),du32(s,&cc),du32(s,&card),du32(s,&child),du32(s,&perm),df32(s,&inv),du64(s,&mask),du32(s,&a),du32(s,&b),du32(s,&hp),du32(s,&slot)];let out=vec![df32(s,&cfv)];(post,out)
 }
 fn guards(&self,c:&Case,output:&[Vec<u32>])->u64{let seed=bits(&self.seed);let lo=2*(c.n0()+c.pad());let hi=lo+if c.active(){c.n0()}else{0};let mut checked=0;for i in 0..seed.len(){if i<lo||i>=hi{assert_eq!(output[0][i],seed[i],"up guard{i}");checked+=1;}}checked}
}
fn main(){
 let dir=PathBuf::from(std::env::var_os("E068_CONTROL_DIR").expect("fresh output required"));std::fs::create_dir(&dir).unwrap();
 let corpus:Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let cases=corpus["cases"].as_array().unwrap();assert_eq!(cases.len(),1688);
 let mut input=file(dir.join("inputs.bin"),b"E068_IN1");let mut baseline=file(dir.join("baseline.bin"),b"E068_OUT1");let mut candidate=file(dir.join("candidate.bin"),b"E068_OUT1");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
 let bf=bm.load_function("up_chance").unwrap();let cf=cm.load_function("up_chance").unwrap();
 let mut launches=0usize;let mut output_words=0u64;let mut immutable_words=0u64;let mut guards=0u64;let mut read_addresses=0u64;
 for (id,row) in cases.iter().enumerate(){
  assert_eq!(row["id"].as_u64().unwrap(),id as u64);let c=Case{d:row["descriptor"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as u32).collect(),inv_bits:row["inv_bits"].as_u64().unwrap() as u32,mask_style:row["mask_style"].as_u64().unwrap() as u32};assert_eq!(c.d.len(),10);assert_eq!(c.family(),1);
  let up=Up::new(&c);let checked=up.read_contract(&c);read_addresses+=checked;let im=up.inputs();let seeds=up.seeds();u32w(&mut input,id as u32);vecw(&mut input,&c.d);vecs(&mut input,&im);vecs(&mut input,&seeds);
  let mut expected:Option<Vec<Vec<u32>>>=None;
  for (f,outfile) in [(&bf,&mut baseline),(&cf,&mut candidate)]{
   let (post,out)=up.run(&c,&stream,f);launches+=1;assert_eq!(post,im,"immutable case{id}");assert_eq!(out.iter().map(Vec::len).collect::<Vec<_>>(),seeds.iter().map(Vec::len).collect::<Vec<_>>());guards+=up.guards(&c,&out);
   if let Some(e)=&expected{assert_eq!(&out,e,"original/candidate raw case{id}");}else{expected=Some(out.clone());}
   u32w(outfile,id as u32);vecs(outfile,&post);vecs(outfile,&out);output_words+=out.iter().map(|v|v.len() as u64).sum::<u64>();immutable_words+=post.iter().map(|v|v.len() as u64).sum::<u64>();
  }
  emit(json!({"stage":"case","id":id,"descriptor":c.d,"inv_bits":c.inv_bits,"mask_style":c.mask_style,"read_addresses_prechecked":checked,"full_outputs_exact":true,"actual_immutable_inputs_exact":true,"guards_exact":true}));
 }
 stream.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(stream);ctx.check_err().unwrap();
 for f in [&mut input,&mut baseline,&mut candidate]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 assert_eq!(launches,2*cases.len());emit(json!({"stage":"complete","cases":cases.len(),"kernel_launches":launches,"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guards,"all_ignored_and_used_read_addresses_prechecked":read_addresses,"full_outputs_exact":true,"actual_immutable_inputs_exact":true,"solver_executions":0,"performance_measured":false,"candidate_accepted":false}));
}
