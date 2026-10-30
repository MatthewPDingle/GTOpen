//! E086 original-mask/bit-field direct GPU comparator, no timing score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
type Out=BufWriter<File>;
fn emit(v:Value){let mut o=std::io::stdout().lock();writeln!(o,"E102_FAN_CONTROL {v}").unwrap();o.flush().unwrap();}
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
// Appended to the pinned original pure-copy raw helper functions.
struct FanCase { d: Vec<u32> }
impl FanCase {
    fn n0(&self)->usize { self.d[0] as usize }
    fn n1(&self)->usize { self.d[1] as usize }
    fn threads(&self)->u32 { self.d[2] }
    fn parents(&self)->usize { self.d[3] as usize }
    fn active(&self)->bool { self.d[4]!=0 }
    fn mode(&self)->usize { self.d[5] as usize }
    fn pattern(&self)->usize { self.d[6] as usize }
    fn salt(&self)->usize { self.d[7] as usize }
}
fn fan_float(i:usize,mode:usize)->f32 {
    if mode==0 { return 1.0+(i%257) as f32/32.0; }
    let data: &[u32] = if mode==1 {
        &[0,0x80000000,1,0x80000001,0x00800000,0x80800000,
          0x7f800000,0xff800000,0x7fc01234,0xffc05678,0x7f800001,
          0xff800123,0x3f800000,0xbf800000,0x007fffff,0x807fffff]
    } else {
        &[0x7f7fffff,0xff7fffff,0x00800000,0x80800000,1,0x80000001,
          0x41540000,0xc0e40000]
    };
    f32::from_bits(data[i%data.len()])
}
fn rep_count(pattern:usize,parent:usize)->usize {
    match pattern {0=>0,1=>1,2=>3,3=>7,4=>47-parent%3,5=>52,_=>panic!("pattern")}
}
fn skip_count(pattern:usize,parent:usize)->usize {
    match pattern {0=>if parent%2==1{2}else{0},1=>0,2=>2,3=>3,4=>4,5=>24,_=>panic!("pattern")}
}
struct Fan {
    im: Vec<Vec<u32>>, m0: Vec<u64>, m1: Vec<u64>,
    seed: [Vec<f32>;2], parents: usize, edges: usize,
}
impl Fan {
    fn new(c:&FanCase)->Self {
        let np=c.parents();let counts:Vec<_>=(0..np).map(|p|rep_count(c.pattern(),p)).collect();
        let ne:usize=counts.iter().sum();let child_base=3*np+11;let nn=child_base+2*ne+7;
        let mut pa=vec![0xdeadbeef];let mut ch=pa.clone();let mut ca=pa.clone();
        let mut nodes=vec![0xdeadbeef];let mut cs=vec![0;nn];let mut cc=cs.clone();
        let mut card=vec![0xdeadbeef;3];let mut child=card.clone();let mut perm=card.clone();
        let mut r0=vec![0;nn];let mut r1=r0.clone();let mut triples=Vec::new();let mut edge=0usize;
        for p in 0..np {
            let n=2+3*p;nodes.push(n as u32);r0[n]=(2+2*p) as u32;r1[n]=(3+2*(np-1-p)) as u32;
            cs[n]=card.len() as u32;let extra=skip_count(c.pattern(),p);let first_edge=edge;
            for j in 0..counts[p] {
                let cn=child_base+2*edge;let dealt=((j*17+p*11+c.salt())%52) as u32;
                r0[cn]=(2*np+8+edge) as u32;r1[cn]=(2*np+8+ne-1-edge) as u32;
                card.push(dealt);child.push(cn as u32);perm.push(0);
                triples.push((n as u32,cn as u32,dealt));edge+=1;
                if j<extra {
                    card.push(if j%2==0 {0xdeadbeef}else{dealt});
                    child.push(if j%2==0 {u32::MAX}else{cn as u32});
                    perm.push([1,2,23,u32::MAX][(j+p)%4]);
                }
            }
            for j in counts[p]..extra {
                card.push(0xdeadbeef);child.push(if counts[p]>0{(child_base+2*first_edge) as u32}else{u32::MAX});
                perm.push([1,2,23,u32::MAX][(j+p)%4]);
            }
            cc[n]=card.len() as u32-cs[n];
            card.extend([0xdeadbeef;2]);child.extend([0xdeadbeef;2]);perm.extend([0xdeadbeef;2]);
        }
        assert_eq!(edge,ne);nodes.extend([0xdeadbeef;2]);
        if c.salt()%2==1 {triples.reverse();}
        else {triples.sort_by_key(|&(p,cn,_)|(cn%14,u32::MAX-p,cn));}
        for (p,n,c) in triples {pa.push(p);ch.push(n);ca.push(c);}
        pa.extend([0xdeadbeef;2]);ch.extend([0xdeadbeef;2]);ca.extend([0xdeadbeef;2]);
        let (a0,b0,m0)=hands(c.n0(),c.salt());let(a1,b1,m1)=hands(c.n1(),c.salt()+19);
        let rows=2*np+8+ne+8;
        let seed=[(0..rows*c.n0()+19).map(|i|fan_float(i+c.salt(),c.mode())).collect(),
                  (0..rows*c.n1()+19).map(|i|fan_float(i+c.salt()+37,c.mode())).collect()];
        let im=vec![pa,ch,ca,r0,r1,split(&m0),split(&m1),a0,b0,a1,b1,nodes,cs,cc,card,child,perm];
        Self{im,m0,m1,seed,parents:np,edges:ne}
    }
    fn seed_bits(&self)->Vec<Vec<u32>> {vec![bits(&self.seed[0]),bits(&self.seed[1])]}
    fn run(&self,c:&FanCase,s:&Arc<CudaStream>,f:&cudarc::driver::CudaFunction,new:bool)->(Vec<Vec<u32>>,Vec<Vec<u32>>) {
        let uploaded:Vec<Option<CudaSlice<u32>>>=self.im.iter().enumerate()
            .map(|(i,x)|if i==5 || i==6 {None}else{Some(s.clone_htod(x).unwrap())}).collect();
        let get=|i:usize|uploaded[i].as_ref().unwrap();
        let m0=s.clone_htod(&self.m0).unwrap();let m1=s.clone_htod(&self.m1).unwrap();
        let mut r0=s.clone_htod(&self.seed[0]).unwrap();let mut r1=s.clone_htod(&self.seed[1]).unwrap();
        let start=1i32;let n0=c.n0() as i32;let n1=c.n1() as i32;
        let count=if c.active(){if new{self.parents}else{self.edges}}else{0} as i32;
        let cfg=LaunchConfig{grid_dim:((if new{self.parents}else{self.edges}) as u32+3,1,1),block_dim:(c.threads(),1,1),shared_mem_bytes:0};
        unsafe {
            if new {
                s.launch_builder(f).arg(get(11)).arg(&start).arg(&count)
                 .arg(get(12)).arg(get(13)).arg(get(14)).arg(get(15)).arg(get(16))
                 .arg(get(3)).arg(get(4)).arg(&m0).arg(&m1)
                 .arg(&mut r0).arg(&mut r1).arg(&n0).arg(&n1).launch(cfg).unwrap();
            } else {
                s.launch_builder(f).arg(get(0)).arg(get(1)).arg(get(2))
                 .arg(&start).arg(&count).arg(get(3)).arg(get(4)).arg(&m0).arg(&m1)
                 .arg(&mut r0).arg(&mut r1).arg(&n0).arg(&n1).launch(cfg).unwrap();
            }
        }
        s.synchronize().unwrap();let post:Vec<_>=uploaded.iter().enumerate().map(|(i,x)|
            if i==5{du64(s,&m0)}else if i==6{du64(s,&m1)}else{du32(s,x.as_ref().unwrap())}).collect();
        (post,vec![df32(s,&r0),df32(s,&r1)])
    }
    fn oracle(&self,c:&FanCase,out:&[Vec<u32>])->u64 {
        let seed=self.seed_bits();let mut guards=0u64;
        for p in 0..2 {
            let nh=if p==0{c.n0()}else{c.n1()};let rs=&self.im[3+p];let mask=if p==0{&self.m0}else{&self.m1};
            let mut owned=vec![false;seed[p].len()];
            if c.active() {
                for e in 0..self.edges {
                    let parent=self.im[0][1+e] as usize;let child=self.im[1][1+e] as usize;let card=self.im[2][1+e];
                    let from=rs[parent] as usize*nh;let to=rs[child] as usize*nh;
                    assert!(from+nh<=seed[p].len() && to+nh<=seed[p].len());
                    assert!(to+nh<=from || from+nh<=to);
                    for i in 0..nh {
                        assert!(!owned[to+i]);owned[to+i]=true;
                        let expected=if mask[i]&(1u64<<card)!=0{0}else{seed[p][from+i]};
                        assert_eq!(out[p][to+i],expected,"fan bit-copy oracle player{p}/edge{e}/hand{i}");
                    }
                }
            }
            for i in 0..seed[p].len(){if !owned[i]{assert_eq!(out[p][i],seed[p][i],"fan guard {p}/{i}");guards+=1;}}
        }
        guards
    }
}
fn main() {emit(json!({"stage":"binding","baseline_ptx_sha256":"4457a101f35369c5d1d9893409e4bc8a9dc027fc4234e325b72c621f73017c12","candidate_ptx_sha256":"b95364b9b3bd4a8873fc185afff9834028d817b5075ad9257386c015d51fdbef","runtime_NVRTC_compiles":0}));
    let dir=PathBuf::from(std::env::args_os().nth(1).expect("fresh output required"));std::fs::create_dir(&dir).unwrap();
    let corpus:Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let cases=corpus["cases"].as_array().unwrap();
    let mut input=file(dir.join("inputs.bin"),b"FAN1_IN\0");let mut baseline=file(dir.join("baseline.bin"),b"FAN1OUT\0");let mut candidate=file(dir.join("candidate.bin"),b"FAN1OUT\0");
    let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
    let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
    let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
    let bf=bm.load_function("down_chance").unwrap();let cf=cm.load_function("down_chance_parent").unwrap();
    let(mut output_words,mut immutable_words,mut guards)=(0u64,0u64,0u64);
    for (id,row) in cases.iter().enumerate() {
        assert_eq!(row["id"].as_u64().unwrap(),id as u64);
        let c=FanCase{d:row["descriptor"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as u32).collect()};assert_eq!(c.d.len(),8);
        let fan=Fan::new(&c);let im=&fan.im;let seeds=fan.seed_bits();u32w(&mut input,id as u32);vecw(&mut input,&c.d);vecs(&mut input,im);vecs(&mut input,&seeds);
        let mut expected=None;
        for(new,f,outfile) in [(false,&bf,&mut baseline),(true,&cf,&mut candidate)] {
            let(post,out)=fan.run(&c,&stream,f,new);assert_eq!(&post,im,"fan immutable case{id}/{new}");
            guards+=fan.oracle(&c,&out);
            if let Some(e)=&expected {assert_eq!(&out,e,"fan original/candidate case{id}");}else{expected=Some(out.clone());}
            u32w(outfile,id as u32);vecs(outfile,&post);vecs(outfile,&out);
            output_words+=out.iter().map(|x|x.len() as u64).sum::<u64>();immutable_words+=post.iter().map(|x|x.len() as u64).sum::<u64>();
        }
        emit(json!({"stage":"case","id":id,"descriptor":c.d,"parents":fan.parents,"representative_edges":fan.edges,"full_outputs_immutable_oracle_and_guards_exact":true}));
    }
    stream.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(stream);ctx.check_err().unwrap();
    for f in [&mut input,&mut baseline,&mut candidate]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
    emit(json!({"stage":"complete","cases":cases.len(),"kernel_launches":2*cases.len(),"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guards,"full_outputs_exact":true,"actual_immutable_inputs_exact":true,"raw_files":3,"solver_executions":0,"performance_measured":false,"candidate_accepted":false}));
}
