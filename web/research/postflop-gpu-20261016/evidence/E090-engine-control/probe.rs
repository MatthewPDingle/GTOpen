#![allow(dead_code,unused_imports,unused_mut)]
pub use solver::*;
use solver::store::{Store,Storage};
use cudarc::driver::{CudaContext,CudaSlice,CudaStream,DeviceRepr};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf},sync::Arc};
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
pub trait Word:DeviceRepr+Clone+Default{fn append(&self,out:&mut Vec<u32>);}
impl Word for u32{fn append(&self,out:&mut Vec<u32>){out.push(*self);}}
impl Word for i32{fn append(&self,out:&mut Vec<u32>){out.push(*self as u32);}}
impl Word for f32{fn append(&self,out:&mut Vec<u32>){out.push(self.to_bits());}}
impl Word for u64{fn append(&self,out:&mut Vec<u32>){out.push(*self as u32);out.push((*self>>32)as u32);}}
impl Word for i64{fn append(&self,out:&mut Vec<u32>){(*self as u64).append(out);}}
fn words<T:Word>(values:&[T])->Vec<u32>{let mut out=Vec::with_capacity(values.len()*std::mem::size_of::<T>()/4);for v in values{v.append(&mut out);}out}
fn write_words(out:&mut BufWriter<File>,values:&[u32]){for v in values{out.write_all(&v.to_le_bytes()).unwrap();}}
fn frame_header(out:&mut BufWriter<File>,kind:u32,name:&str,count:usize){out.write_all(&kind.to_le_bytes()).unwrap();out.write_all(&(name.len()as u32).to_le_bytes()).unwrap();out.write_all(name.as_bytes()).unwrap();out.write_all(&(count as u64).to_le_bytes()).unwrap();}
pub fn capture<T:Word>(s:&Arc<CudaStream>,name:&str,d:&CudaSlice<T>,expected:&[T],out:&mut BufWriter<File>)->Value{
 assert_eq!(d.len(),expected.len(),"length {name}");
 let actual=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();let actual=words(&actual);let expected=words(expected);assert_eq!(actual,expected,"full device {name}");
 frame_header(out,1,name,actual.len());write_words(out,&expected);write_words(out,&actual);
 json!({"name":name,"encoding":"explicit expected and actual u32 words","words":actual.len(),"full_exact":true})
}
pub fn capture_zero(s:&Arc<CudaStream>,name:&str,d:&CudaSlice<f32>,out:&mut BufWriter<File>)->Value{
 let actual=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();assert_eq!(actual.len(),d.len());let all_bits=actual.iter().fold(0u32,|bits,v|bits|v.to_bits());assert_eq!(all_bits,0,"all actual positive-zero words {name}");
 // This run record losslessly represents every verified word. No sampling,
 // checksum cancellation or multi-gigabyte duplicate zero files.
 frame_header(out,0,name,actual.len());out.write_all(&all_bits.to_le_bytes()).unwrap();
 json!({"name":name,"encoding":"verified positive-zero run","words":actual.len(),"all_actual_bits_OR":all_bits,"full_exact":true})
}
pub fn expected_arena(s:&Solver,p:&solver::gpu::plan::GpuPlan,seat:usize,which:usize)->Vec<f32>{
 let store=if which==0{&s.regrets[seat]}else{&s.strat[seat]};let mut out=vec![0.0;p.arena_elements[seat]];let nh=s.spot.hands[seat].len();
 for(i,node)in s.spot.tree.nodes.iter().enumerate(){
  if node.kind!=solver::tree::KIND_ACTION||node.player as usize!=seat{continue;}
  let off=p.node_data_off[i];if off==u64::MAX{continue;}
  let n=node.num_children as usize*nh;unsafe{store.read_f32(i as u32,node.data_offset,n,&mut out[off as usize..off as usize+n]);}
 }
 out
}


fn host_field(out:&mut BufWriter<File>,name:&str,v:&[u32]){
    if v.iter().fold(0u32,|a,&b|a|b)==0{frame_header(out,0,name,v.len());out.write_all(&0u32.to_le_bytes()).unwrap();}
    else{frame_header(out,2,name,v.len());write_words(out,v);}
}
fn state_frame(s:&Solver,path:&Path){
    let mut o=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());
    o.write_all(b"E090-STATE-v1\0\0\0").unwrap();
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
fn emit(value:Value){let mut o=std::io::stdout().lock();writeln!(o,"E090_CONTROL {value}").unwrap();o.flush().unwrap();}
fn same_files(a:&Path,b:&Path){assert_eq!(std::fs::read(a).unwrap(),std::fs::read(b).unwrap(),"whole files {} {}",a.display(),b.display());}
fn scenario(storage:Storage,algo:Algorithm,reverse:bool,iso:bool,warm:bool)->(Solver,Solver) {
    let sizing=||StreetSizing{bet:parse_sizes("50").unwrap(),raise:vec![],donk:vec![]};
    let mut cfg=SpotConfig{board:"KsQs2dJd".into(),range_oop:"AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),range_ip:"AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
        tree:TreeConfig{starting_pot:10.,effective_stack:20.,oop:std::array::from_fn(|_|sizing()),ip:std::array::from_fn(|_|sizing()),rake_pct:if warm{0.05}else{0.},rake_cap:3.,..Default::default()}};
    if reverse{std::mem::swap(&mut cfg.range_oop,&mut cfg.range_ip);}
    let spot=Arc::new(Spot::new(cfg).unwrap());assert_ne!(spot.hands[0].len(),spot.hands[1].len());
    let mut a=Solver::with_storage(spot.clone(),storage);let mut b=Solver::with_storage(spot,storage);
    a.algo=algo;b.algo=algo;a.use_isomorphism=iso;b.use_isomorphism=iso;
    if warm{a.iterate();b.iterate();}
    (a,b)
}
fn snapshot(b:&baseline::GpuSolver,c:&candidate::GpuSolver,out:&Path,id:usize,stage:&str,p:usize,poisoned:bool,proofs:&mut Vec<Value>){
    let bf=out.join(format!("baseline-{id:02}-{stage}.gpu.bin"));
    let cf=out.join(format!("candidate-{id:02}-{stage}.gpu.bin"));
    let (x,bi)=b.e090_snapshot(&bf,p,poisoned);let(y,ci)=c.e090_snapshot(&cf,p,poisoned);
    assert_eq!(x,y,"all learning/reach/discount/lock/logicalCFV words {id} {stage}");
    for k in ["p","rows","logical_hands","original_width","physical_words","logical_words","poisoned","full_physical_guard_words","wrapper_bytes","pinned_words","arena_words","reach_words","graphs_present","eval_graph_present"]{assert_eq!(bi[k],ci[k],"{k}");}
    proofs.push(json!({"stage":stage,"baseline":bi,"candidate":ci,"all_logical_and_other_full_images_exact":true}));
}
fn cpu_pair(a:&Solver,b:&Solver,out:&Path,id:usize,stage:&str){
    let x=out.join(format!("baseline-{id:02}-{stage}.cpu.bin"));let y=out.join(format!("candidate-{id:02}-{stage}.cpu.bin"));
    state_frame(a,&x);state_frame(b,&y);same_files(&x,&y);
}
fn main(){
    let out=PathBuf::from(std::env::args().nth(1).expect("fresh output"));std::fs::create_dir(&out).unwrap();
    let mut cases=Vec::new();let mut id=0usize;
    for storage in[Storage::Compressed,Storage::F32]{for algo in[Algorithm::Dcfr,Algorithm::CfrPlus]{for reverse in[false,true]{for iso in[false,true]{for warm in[false,true]{
        let(mut a,mut c)=scenario(storage,algo,reverse,iso,warm);
        cpu_pair(&a,&c,&out,id,"input");
        let be=baseline::GpuSolver::new_with_budget(&a,1).err().unwrap();let ce=candidate::GpuSolver::new_with_budget(&c,1).err().unwrap();assert_eq!(be,ce);assert!(be.contains("budget"));
        let mut b=baseline::GpuSolver::new(&a).unwrap();let mut g=candidate::GpuSolver::new(&c).unwrap();
        b.synchronize().unwrap();g.synchronize().unwrap();
        let bc=out.join(format!("baseline-{id:02}-constructor.bin"));let cc=out.join(format!("candidate-{id:02}-constructor.bin"));
        let bp=b.e090_validate(&a,&bc,!warm);let cp=g.e090_validate(&c,&cc,!warm);assert_eq!(bp,cp);same_files(&bc,&cc);
        let mut proofs=Vec::new();let mut exploit=Vec::new();
        for p in 0..2{
            b.e090_force_sweep(p);g.e090_force_sweep(p);
            snapshot(&b,&g,&out,id,&format!("forced-p{p}"),p,true,&mut proofs);
        }
        for i in 0..2{
            b.iterate().unwrap();g.iterate().unwrap();
            snapshot(&b,&g,&out,id,&format!("graph-iteration-{i}"),1,false,&mut proofs);
        }
        for i in 0..2{
            let x=b.exploitability(&a).unwrap().to_bits();let y=g.exploitability(&c).unwrap().to_bits();assert_eq!(x,y);exploit.push(x);
            snapshot(&b,&g,&out,id,&format!("evaluation-{i}"),1,false,&mut proofs);
        }
        b.sync_strategy(&mut a).unwrap();g.sync_strategy(&mut c).unwrap();cpu_pair(&a,&c,&out,id,"strategy");
        b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();cpu_pair(&a,&c,&out,id,"full");
        a.ensure_symmetric();c.ensure_symmetric();
        let aq=serde_json::to_vec(&a.node_view(&[]).unwrap()).unwrap();let cq=serde_json::to_vec(&c.node_view(&[]).unwrap()).unwrap();assert_eq!(aq,cq);
        std::fs::write(out.join(format!("baseline-{id:02}-query.json")),&aq).unwrap();std::fs::write(out.join(format!("candidate-{id:02}-query.json")),&cq).unwrap();
        a.lock_node(&[],LockMode::Freeze,"control".into()).unwrap();c.lock_node(&[],LockMode::Freeze,"control".into()).unwrap();
        b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();b.iterate().unwrap();g.iterate().unwrap();
        for _ in 0..2{let x=b.exploitability(&a).unwrap().to_bits();let y=g.exploitability(&c).unwrap().to_bits();assert_eq!(x,y);exploit.push(x);}
        snapshot(&b,&g,&out,id,"locked-recapture",1,false,&mut proofs);
        a.clear_locks();c.clear_locks();b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();b.iterate().unwrap();g.iterate().unwrap();
        snapshot(&b,&g,&out,id,"unlocked-recapture",1,false,&mut proofs);
        b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();a.ensure_symmetric();c.ensure_symmetric();cpu_pair(&a,&c,&out,id,"before-save");
        let asave=out.join(format!("baseline-{id:02}-state.save"));let csave=out.join(format!("candidate-{id:02}-state.save"));
        a.save(asave.to_str().unwrap()).unwrap();c.save(csave.to_str().unwrap()).unwrap();same_files(&asave,&csave);
        drop(b);drop(g);drop(a);drop(c);
        let mut a=Solver::load_with_storage(asave.to_str().unwrap(),storage).unwrap();let mut c=Solver::load_with_storage(csave.to_str().unwrap(),storage).unwrap();cpu_pair(&a,&c,&out,id,"loaded");
        let mut b=baseline::GpuSolver::new(&a).unwrap();let mut g=candidate::GpuSolver::new(&c).unwrap();b.iterate().unwrap();g.iterate().unwrap();
        snapshot(&b,&g,&out,id,"resumed",1,false,&mut proofs);
        b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();cpu_pair(&a,&c,&out,id,"resumed");
        assert_eq!(proofs.len(),9);assert_eq!(exploit.len(),4);
        cases.push(json!({"case":id,"storage":format!("{storage:?}"),"algorithm":format!("{algo:?}"),"reverse_ranges":reverse,"isomorphism":iso,"warm_CPU_start":warm,"raked":warm,"budget_error":be,"constructor":bp,"snapshots":proofs,"exploit_bits":exploit,"all_CPU_query_save_files_exact":true}));
        emit(json!({"stage":"case_complete","case":id,"snapshots":9,"exact":true}));id+=1;
    }}}}}
    assert_eq!(id,32);
    let meta=json!({"id":"E090-engine-control","cases":cases,"case_count":32,"GPU_snapshot_pairs":288,"constructor_pairs":32,"exploitability_pairs":128,"standard_training_iterations":320,"extra_single_player_sweeps":128,"performance_measurement":false,"candidate_accepted":false});
    let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap();f.write_all(serde_json::to_string_pretty(&meta).unwrap().as_bytes()).unwrap();f.sync_all().unwrap();
    emit(json!({"stage":"complete","cases":32,"GPU_snapshot_pairs":288,"performance_measurement":false}));
}
