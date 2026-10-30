#![allow(dead_code,unused_imports,unused_mut)]
pub use solver::*;
use solver::store::{Store,Storage};
use cudarc::driver::{CudaContext,CudaSlice,CudaStream,DeviceRepr};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf},sync::Arc};
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;

// D134_CAPTURE_HELPERS

fn emit(v:Value){let mut o=std::io::stdout().lock();writeln!(o,"E087_TRANSFER {v}").unwrap();o.flush().unwrap();}
fn same_files(a:&Path,b:&Path){assert_eq!(std::fs::read(a).unwrap(),std::fs::read(b).unwrap(),"full files {} {}",a.display(),b.display());}
fn host_field(out:&mut BufWriter<File>,name:&str,v:&[u32]){
    if v.iter().fold(0u32,|a,&b|a|b)==0{frame_header(out,0,name,v.len());out.write_all(&0u32.to_le_bytes()).unwrap();}
    else{frame_header(out,2,name,v.len());write_words(out,v);}
}
fn state_frame(s:&Solver,path:&Path){
    let mut o=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());
    o.write_all(b"E087-STATE-v1\0\0\0").unwrap();
    host_field(&mut o,"iteration",&[s.iteration]);
    host_field(&mut o,"isomorphism",&[s.use_isomorphism as u32]);
    host_field(&mut o,"predictions_present",&[s.preds.is_some()as u32]);
    host_field(&mut o,"locks",&[s.locks.len()as u32]);
    for (which,stores)in [("regret",&s.regrets),("strategy",&s.strat)]{for p in 0..2{
        let name=format!("{which}{p}");
        match &stores[p]{
            Store::F32(v)=>host_field(&mut o,&(name+".f32"),&v.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),
            Store::I16{q,scale}=>{
                host_field(&mut o,&(name.clone()+".i16"),&q.as_slice().iter().map(|&x|x as u16 as u32).collect::<Vec<_>>());
                host_field(&mut o,&(name+".scale"),&scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>());
            },
            Store::U16{q,scale}=>{
                host_field(&mut o,&(name.clone()+".u16"),&q.as_slice().iter().map(|&x|x as u32).collect::<Vec<_>>());
                host_field(&mut o,&(name+".scale"),&scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>());
            },
        }
    }}
    o.flush().unwrap();o.get_ref().sync_all().unwrap();
}
fn device_frame(stream:&Arc<CudaStream>,d:&CudaSlice<f32>,expected:&[f32],path:&Path){
    let mut o=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());
    o.write_all(b"E087-FRAME-v1\0\0\0").unwrap();
    capture(stream,"arena",d,expected,&mut o);
    o.flush().unwrap();o.get_ref().sync_all().unwrap();
}
fn fill_store(s:&Solver,p:usize,which:usize,mode:usize){
    let store=if which==0{&s.regrets[p]}else{&s.strat[p]};let nh=s.spot.hands[p].len();
    for(i,n)in s.spot.tree.nodes.iter().enumerate(){
        if n.kind!=solver::tree::KIND_ACTION||n.player as usize!=p{continue}
        let v:Vec<f32>=(0..n.num_children as usize*nh).map(|j|{
            let bits=[0x80000000u32,1,0x80000001,0x7f800000,0xff800000,0x7fc01234,0xffc05678,0x3f800000,0xbf800000];
            if mode%2==0{f32::from_bits(bits[(i+j+mode)%bits.len()])}
            else{((i*17+j*73+mode)%1009)as f32/31.0-13.0}
        }).collect();
        unsafe{store.write_f32(i as u32,n.data_offset,v.len(),&v)}
    }
}
fn small(storage:Storage)->Solver{
    let sizing=||StreetSizing{bet:parse_sizes("50").unwrap(),raise:vec![],donk:vec![]};
    let spot=Spot::new(SpotConfig{
        board:"KsQs2dJd".into(),
        range_oop:"AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),
        range_ip:"AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
        tree:TreeConfig{starting_pot:10.,effective_stack:20.,
            oop:std::array::from_fn(|_|sizing()),ip:std::array::from_fn(|_|sizing()),..Default::default()}
    }).unwrap();
    Solver::with_storage(Arc::new(spot),storage)
}
enum Engine{Baseline(baseline::GpuSolver),Candidate(candidate::GpuSolver)}
impl Engine{
    fn new(arm:&str,s:&Solver)->Self{if arm=="baseline"{Self::Baseline(baseline::GpuSolver::new(s).unwrap())}else{Self::Candidate(candidate::GpuSolver::new(s).unwrap())}}
    fn ready(&self){match self{Self::Baseline(g)=>g.synchronize().unwrap(),Self::Candidate(g)=>g.synchronize().unwrap()}}
    fn iterate(&mut self){match self{Self::Baseline(g)=>g.iterate().unwrap(),Self::Candidate(g)=>g.iterate().unwrap()}}
    fn exploit(&mut self,s:&Solver)->u64{match self{Self::Baseline(g)=>g.exploitability(s).unwrap().to_bits(),Self::Candidate(g)=>g.exploitability(s).unwrap().to_bits()}}
    fn full(&mut self,s:&mut Solver){match self{Self::Baseline(g)=>g.sync_to_cpu(s).unwrap(),Self::Candidate(g)=>g.sync_to_cpu(s).unwrap()}}
    fn strategy(&mut self,s:&mut Solver){match self{Self::Baseline(g)=>g.sync_strategy(s).unwrap(),Self::Candidate(g)=>g.sync_strategy(s).unwrap()}}
    fn validate(&self,s:&Solver,path:&Path,zero:bool)->Value{match self{Self::Baseline(g)=>g.e087_validate(s,path,zero),Self::Candidate(g)=>g.e087_validate(s,path,zero)}}
    fn info(&self)->Value{match self{Self::Baseline(g)=>g.e087_info(),Self::Candidate(g)=>g.e087_info()}}
}
fn budget(arm:&str,s:&Solver)->String{
    if arm=="baseline"{baseline::GpuSolver::new_with_budget(s,1).err().unwrap()}
    else{candidate::GpuSolver::new_with_budget(s,1).err().unwrap()}
}
fn main(){
    let out=PathBuf::from(std::env::args().nth(1).expect("fresh output"));std::fs::create_dir(&out).unwrap();
    let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
    unsafe{ctx.disable_event_tracking()};let stream=ctx.new_stream().unwrap();
    let mut manual=Vec::new();let mut engines=Vec::new();let mut constructors=Vec::new();
    for arm in ["baseline","candidate"]{
        let mut id=0usize;
        for storage in [Storage::Compressed,Storage::F32]{for full in [false,true]{for profile in 0..3{for prechecked in [false,true]{for p in 0..2{
            let mut s=small(storage);
            if profile==1{s.iterate()}
            if profile==2{for seat in 0..2{for which in 0..2{fill_store(&s,seat,which,2)}}}
            let name=format!("{arm}-arena-{id:03}");
            let result=if arm=="baseline"{baseline::e087_manual(&mut s,&stream,p,full,prechecked,&out,&name)}
                else{candidate::e087_manual(&mut s,&stream,p,full,prechecked,&out,&name)};
            manual.push(json!({"arm":arm,"case":id,"storage":format!("{storage:?}"),"profile":profile,"result":result}));
            id+=1;
        }}}}}
        assert_eq!(id,48);
        emit(json!({"stage":"manual_complete","arm":arm,"layouts":id,"arena_phases":2*id}));
        let mut id=0usize;
        for storage in [Storage::Compressed,Storage::F32]{for warm in [false,true]{
            let mut s=small(storage);if warm{s.iterate()}
            let name=format!("{arm}-engine-{id:02}");
            let b=out.join(&name);state_frame(&s,&b.with_extension("input.bin"));
            let reject=budget(arm,&s);assert!(reject.contains("budget"));
            let mut g=Engine::new(arm,&s);g.ready();
            g.validate(&s,&b.with_extension("constructor.bin"),!warm);
            let info=g.info();
            g.iterate();g.iterate();let exploit=g.exploit(&s);
            g.strategy(&mut s);state_frame(&s,&b.with_extension("strategy.bin"));
            g.full(&mut s);state_frame(&s,&b.with_extension("full.bin"));
            s.ensure_symmetric();
            std::fs::write(b.with_extension("query.json"),serde_json::to_vec(&s.node_view(&[]).unwrap()).unwrap()).unwrap();
            g.full(&mut s);state_frame(&s,&b.with_extension("resync.bin"));
            same_files(&b.with_extension("full.bin"),&b.with_extension("resync.bin"));
            s.ensure_symmetric();s.save(b.with_extension("state.save").to_str().unwrap()).unwrap();
            drop(g);drop(s);
            let mut loaded=Solver::load_with_storage(b.with_extension("state.save").to_str().unwrap(),storage).unwrap();
            state_frame(&loaded,&b.with_extension("loaded.bin"));
            let mut reload=Engine::new(arm,&loaded);reload.ready();reload.iterate();reload.full(&mut loaded);
            state_frame(&loaded,&b.with_extension("resumed.bin"));
            engines.push(json!({"arm":arm,"case":id,"storage":format!("{storage:?}"),"warm":warm,"exploit_bits":exploit,"budget_error":reject,"info":info,"full_resync_exact":true}));
            id+=1;
        }}
        emit(json!({"stage":"engines_complete","arm":arm,"cases":id}));
        for (id,(name,board,rake,storage))in [
            ("rainbow","Ks7h2d",0.,Storage::Compressed),
            ("two-tone","Ks7s2d",0.05,Storage::Compressed),
            ("river","Ks7h2dQhTc",0.05,Storage::Compressed),
            ("two-tone-F32","Ks7s2d",0.05,Storage::F32),
        ].into_iter().enumerate(){
            let mut cfg:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();
            cfg.board=board.into();cfg.tree.rake_pct=rake;cfg.tree.rake_cap=3.;
            let s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),storage);
            let gpu=Engine::new(arm,&s);gpu.ready();
            let proof=gpu.validate(&s,&out.join(format!("{arm}-large-{id:02}.bin")),true);
            constructors.push(json!({"arm":arm,"case":id,"fixture":name,"storage":format!("{storage:?}"),"info":gpu.info(),"proof":proof}));
            emit(json!({"stage":"large_constructor","arm":arm,"case":id,"fixture":name}));
        }
    }
    let drain=candidate::e087_drain(&stream);
    let mut pairs=Vec::new();let mut paths:Vec<_>=std::fs::read_dir(&out).unwrap().map(|x|x.unwrap().path()).filter(|p|p.is_file()&&p.file_name().unwrap().to_string_lossy().starts_with("baseline-")).collect();paths.sort();
    for p in paths{
        let name=p.file_name().unwrap().to_string_lossy();
        let other=out.join(name.replacen("baseline-","candidate-",1));
        same_files(&p,&other);pairs.push([p.file_name().unwrap().to_string_lossy().to_string(),other.file_name().unwrap().to_string_lossy().to_string()]);
    }
    let meta=json!({"id":"E087-transfer-control","manual":manual,"engines":engines,"constructors":constructors,"drain":drain,"full_file_pairs":pairs,"performance_measurement":false,"candidate_accepted":false});
    let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap();f.write_all(serde_json::to_string_pretty(&meta).unwrap().as_bytes()).unwrap();f.sync_all().unwrap();
    stream.synchronize().unwrap();ctx.check_err().unwrap();
    emit(json!({"stage":"complete","manual_layouts":96,"manual_arenas":192,"small_engine_cases":8,"large_constructors":8,"full_file_pairs":meta["full_file_pairs"].as_array().unwrap().len(),"all_full_file_pairs_exact":true,"performance_measurement":false,"candidate_accepted":false}));
}
