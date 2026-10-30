//! D234 original-mask/bit-field direct GPU comparator, no timing score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
type Out=BufWriter<File>;
fn emit(v:Value){let mut o=std::io::stdout().lock();writeln!(o,"D234_CONTROL {v}").unwrap();o.flush().unwrap();}
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
struct Case{d:Vec<u32>}
impl Case{fn family(&self)->usize{self.d[0] as usize}fn n0(&self)->usize{self.d[1] as usize}fn n1(&self)->usize{self.d[2] as usize}fn threads(&self)->u32{self.d[3]}fn active(&self)->bool{self.d[4]!=0}fn mode(&self)->usize{self.d[5] as usize}fn perm(&self)->usize{self.d[6] as usize}fn width(&self)->usize{self.d[7] as usize}fn pattern(&self)->usize{self.d[8] as usize}fn salt(&self)->usize{self.d[9] as usize}}
struct Down{parents:Vec<u32>,childs:Vec<u32>,cards:Vec<u32>,r0:Vec<u32>,r1:Vec<u32>,m0:Vec<u64>,m1:Vec<u64>,a0:Vec<u32>,b0:Vec<u32>,a1:Vec<u32>,b1:Vec<u32>,seed0:Vec<f32>,seed1:Vec<f32>}
impl Down{
 fn new(c:&Case)->Self{
  let w=c.width();let nn=w+10;let mut parents=vec![0xdeadbeef;w+4];let mut childs=parents.clone();let mut cards=parents.clone();let mut r0=vec![0;nn];let mut r1=r0.clone();r0[2]=2;r1[2]=3;
  for j in 0..w{parents[j+1]=2;childs[j+1]=(j+4) as u32;cards[j+1]=match c.pattern(){0=>j as u32%52,1=>[0,25,51][j%3],2=>((j*17+13)%52) as u32,_=>((j+c.salt())%52) as u32};r0[j+4]=(4+j) as u32;r1[j+4]=(6+w-1-j) as u32;}
  let(a0,b0,m0)=hands(c.n0(),c.salt());let(a1,b1,m1)=hands(c.n1(),c.salt()+19);
  let seed0=(0..(w+12)*c.n0()+17).map(|i|float(i+c.salt(),c.mode())).collect();let seed1=(0..(w+12)*c.n1()+17).map(|i|float(i+c.salt()+37,c.mode())).collect();
  Self{parents,childs,cards,r0,r1,m0,m1,a0,b0,a1,b1,seed0,seed1}
 }
 fn inputs(&self)->Vec<Vec<u32>>{vec![self.parents.clone(),self.childs.clone(),self.cards.clone(),self.r0.clone(),self.r1.clone(),split(&self.m0),split(&self.m1),self.a0.clone(),self.b0.clone(),self.a1.clone(),self.b1.clone()]}
 fn seeds(&self)->Vec<Vec<u32>>{vec![bits(&self.seed0),bits(&self.seed1)]}
 fn run(&self,c:&Case,s:&Arc<CudaStream>,f:&cudarc::driver::CudaFunction,_new:bool)->(Vec<Vec<u32>>,Vec<Vec<u32>>){
  let parents=s.clone_htod(&self.parents).unwrap();let childs=s.clone_htod(&self.childs).unwrap();let cards=s.clone_htod(&self.cards).unwrap();let r0=s.clone_htod(&self.r0).unwrap();let r1=s.clone_htod(&self.r1).unwrap();
  let m0=s.clone_htod(&self.m0).unwrap();let m1=s.clone_htod(&self.m1).unwrap();let a0=s.clone_htod(&self.a0).unwrap();let b0=s.clone_htod(&self.b0).unwrap();let a1=s.clone_htod(&self.a1).unwrap();let b1=s.clone_htod(&self.b1).unwrap();
  let mut reach0=s.clone_htod(&self.seed0).unwrap();let mut reach1=s.clone_htod(&self.seed1).unwrap();let start=1i32;let count=if c.active(){c.width() as i32}else{0};let nh0=c.n0() as i32;let nh1=c.n1() as i32;
  let cfg=LaunchConfig{grid_dim:((c.width()+2) as u32,1,1),block_dim:(c.threads(),1,1),shared_mem_bytes:0};
  unsafe{s.launch_builder(f).arg(&parents).arg(&childs).arg(&cards).arg(&start).arg(&count).arg(&r0).arg(&r1).arg(&m0).arg(&m1).arg(&mut reach0).arg(&mut reach1).arg(&nh0).arg(&nh1).launch(cfg).unwrap();}
  s.synchronize().unwrap();let post=vec![du32(s,&parents),du32(s,&childs),du32(s,&cards),du32(s,&r0),du32(s,&r1),du64(s,&m0),du64(s,&m1),du32(s,&a0),du32(s,&b0),du32(s,&a1),du32(s,&b1)];let out=vec![df32(s,&reach0),df32(s,&reach1)];(post,out)
 }
 fn guards(&self,c:&Case,output:&[Vec<u32>])->u64{
  let seeds=self.seeds();let mut checked=0;
  for p in 0..2{let nh=if p==0{c.n0()}else{c.n1()};let rs=if p==0{&self.r0}else{&self.r1};let mut owned=vec![false;seeds[p].len()];
   if c.active(){for j in 0..c.width(){let slot=rs[self.childs[j+1] as usize] as usize;for i in 0..nh{owned[slot*nh+i]=true;}}}
   for i in 0..owned.len(){if !owned[i]{assert_eq!(output[p][i],seeds[p][i],"down guard{p}/{i}");checked+=1;}}
   if c.mode()==0&&c.active(){for j in 0..c.width(){let card=self.cards[j+1];let slot=rs[self.childs[j+1] as usize] as usize;let parent=rs[2] as usize;let mask=if p==0{&self.m0}else{&self.m1};for i in 0..nh{let expected=if mask[i]&(1u64<<card)!=0{0}else{seeds[p][parent*nh+i]};assert_eq!(output[p][slot*nh+i],expected,"down canonical relation{p}/{j}/{i}");}}}
  }checked
 }
}
struct Up{nodes:Vec<u32>,start:Vec<u32>,count:Vec<u32>,card:Vec<u32>,child:Vec<u32>,perm:Vec<u32>,inv:Vec<f32>,mask:Vec<u64>,a:Vec<u32>,b:Vec<u32>,hp:Vec<u32>,slot:Vec<u32>,seed:Vec<f32>}
impl Up{
 fn new(c:&Case)->Self{
  let w=c.width();let n=c.n0();let nn=w+10;let nodes=vec![0xdeadbeef,2,0xdeadbeef];let mut start=vec![0;nn];let mut count=start.clone();start[2]=3;count[2]=w as u32;let mut card=vec![0xdeadbeef;w+6];let mut child=card.clone();let mut perm=card.clone();let mut slot=vec![0;nn];slot[2]=2;
  for j in 0..w{card[j+3]=match c.pattern(){0=>j as u32%52,1=>[0,25,51][j%3],2=>((j*17+13)%52) as u32,_=>((j+c.salt())%52) as u32};child[j+3]=(4+j) as u32;perm[j+3]=if c.perm()==0{0}else{(j%4) as u32};slot[4+j]=(4+w-1-j) as u32;}
  let mut inv=vec![f32::from_bits(0x7fc0eeee);nn];inv[2]=1.0/46.0;let(a,b,mask)=hands(n,c.salt());let hp=(0..4*n+7).map(|i|if n>0{((i%n+(i/n)*17)%n) as u32}else{0}).collect();
  let seed=(0..(w+12)*(n+5)+17).map(|i|float(i+c.salt(),c.mode())).collect();Self{nodes,start,count,card,child,perm,inv,mask,a,b,hp,slot,seed}
 }
 fn inputs(&self)->Vec<Vec<u32>>{vec![self.nodes.clone(),self.start.clone(),self.count.clone(),self.card.clone(),self.child.clone(),self.perm.clone(),bits(&self.inv),split(&self.mask),self.a.clone(),self.b.clone(),self.hp.clone(),self.slot.clone()]}
 fn seeds(&self)->Vec<Vec<u32>>{vec![bits(&self.seed)]}
 fn run(&self,c:&Case,s:&Arc<CudaStream>,f:&cudarc::driver::CudaFunction,_new:bool)->(Vec<Vec<u32>>,Vec<Vec<u32>>){
  let nodes=s.clone_htod(&self.nodes).unwrap();let cs=s.clone_htod(&self.start).unwrap();let cc=s.clone_htod(&self.count).unwrap();let card=s.clone_htod(&self.card).unwrap();let child=s.clone_htod(&self.child).unwrap();let perm=s.clone_htod(&self.perm).unwrap();let inv=s.clone_htod(&self.inv).unwrap();let mask=s.clone_htod(&self.mask).unwrap();let a=s.clone_htod(&self.a).unwrap();let b=s.clone_htod(&self.b).unwrap();let hp=s.clone_htod(&self.hp).unwrap();let slot=s.clone_htod(&self.slot).unwrap();let mut cfv=s.clone_htod(&self.seed).unwrap();
  let start=1i32;let count=if c.active(){1i32}else{0};let nh=c.n0() as i32;let stride=nh+5;let cfg=LaunchConfig{grid_dim:(3,1,1),block_dim:(c.threads(),1,1),shared_mem_bytes:0};
  unsafe{s.launch_builder(f).arg(&nodes).arg(&start).arg(&count).arg(&cs).arg(&cc).arg(&card).arg(&child).arg(&perm).arg(&inv).arg(&mask).arg(&hp).arg(&slot).arg(&mut cfv).arg(&nh).arg(&stride).launch(cfg).unwrap();}
  s.synchronize().unwrap();let post=vec![du32(s,&nodes),du32(s,&cs),du32(s,&cc),du32(s,&card),du32(s,&child),du32(s,&perm),df32(s,&inv),du64(s,&mask),du32(s,&a),du32(s,&b),du32(s,&hp),du32(s,&slot)];let out=vec![df32(s,&cfv)];(post,out)
 }
 fn guards(&self,c:&Case,output:&[Vec<u32>])->u64{let seed=bits(&self.seed);let lo=2*(c.n0()+5);let hi=lo+if c.active(){c.n0()}else{0};let mut checked=0;for i in 0..seed.len(){if i<lo||i>=hi{assert_eq!(output[0][i],seed[i],"up guard{i}");checked+=1;}}checked}
}
fn main(){
 let dir=PathBuf::from(std::env::var_os("D234_CONTROL_DIR").expect("fresh output required"));std::fs::create_dir(&dir).unwrap();
 let corpus:Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let cases=corpus["cases"].as_array().unwrap();assert_eq!(cases.len(),corpus["case_count"].as_u64().unwrap() as usize);
 let mut input=file(dir.join("inputs.bin"),b"D234_IN1");let mut baseline=file(dir.join("baseline.bin"),b"D234_OUT1");let mut candidate=file(dir.join("candidate.bin"),b"D234_OUT1");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
 let bf=[bm.load_function("down_chance").unwrap(),bm.load_function("up_chance").unwrap()];let cf=[cm.load_function("down_chance").unwrap(),cm.load_function("up_chance").unwrap()];
 let mut completed=0usize;let mut launches=0usize;let mut output_words=0u64;let mut immutable_words=0u64;let mut guards=0u64;
 for (id,row) in cases.iter().enumerate(){
  assert_eq!(row["id"].as_u64().unwrap(),id as u64);let c=Case{d:row["descriptor"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as u32).collect()};assert_eq!(c.d.len(),10);
  let down=if c.family()==0{Some(Down::new(&c))}else{None};let up=if c.family()==1{Some(Up::new(&c))}else{None};assert!(c.family()<=1);
  let im=if let Some(x)=&down{x.inputs()}else{up.as_ref().unwrap().inputs()};let seeds=if let Some(x)=&down{x.seeds()}else{up.as_ref().unwrap().seeds()};u32w(&mut input,id as u32);vecw(&mut input,&c.d);vecs(&mut input,&im);vecs(&mut input,&seeds);
  let mut expected:Option<Vec<Vec<u32>>>=None;
  for (new,f,outfile) in [(false,&bf[c.family()],&mut baseline),(true,&cf[c.family()],&mut candidate)]{
   let (post,out)=if let Some(x)=&down{x.run(&c,&stream,f,new)}else{up.as_ref().unwrap().run(&c,&stream,f,new)};launches+=1;
   assert_eq!(post,im,"immutable inputs case{id}/{new}");assert_eq!(out.iter().map(Vec::len).collect::<Vec<_>>(),seeds.iter().map(Vec::len).collect::<Vec<_>>());
   guards+=if let Some(x)=&down{x.guards(&c,&out)}else{up.as_ref().unwrap().guards(&c,&out)};
   if let Some(e)=&expected{assert_eq!(&out,e,"raw original/candidate case{id}");}else{expected=Some(out.clone());}
   u32w(outfile,id as u32);vecs(outfile,&post);vecs(outfile,&out);output_words+=out.iter().map(|v|v.len() as u64).sum::<u64>();immutable_words+=post.iter().map(|v|v.len() as u64).sum::<u64>();
  }
  completed+=1;emit(json!({"stage":"case","id":id,"descriptor":c.d,"full_outputs_exact":true,"actual_immutable_inputs_exact":true,"guards_exact":true}));
 }
 stream.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(stream);ctx.check_err().unwrap();
 for f in [&mut input,&mut baseline,&mut candidate]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 assert_eq!(completed,cases.len());assert_eq!(launches,2*completed);
 emit(json!({"stage":"complete","cases":completed,"kernel_launches":launches,"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guards,"full_outputs_exact":true,"actual_immutable_inputs_exact":true,"raw_files":3,"solver_executions":0,"performance_measured":false,"candidate_accepted":false}));
}
