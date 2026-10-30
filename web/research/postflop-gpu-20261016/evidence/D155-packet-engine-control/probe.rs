#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
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
    o.write_all(b"D155-STATE-v1\0\0\0").unwrap();
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
fn readback(g:&mut candidate::GpuSolver, c:&mut Solver,out:&Path,id:usize,stage:&str,strategy:bool,proofs:&mut Vec<Value>) {
    let before=out.join(format!("pinned-{id:02}-{stage}-before.u32"));let after=out.join(format!("pinned-{id:02}-{stage}-after.u32"));
    let proof=g.d155_forced_sync(c,strategy,&before,&after);proofs.push(json!({"stage":stage,"proof":proof}));
}
fn emit(value: Value) { let mut o = std::io::stdout().lock(); writeln!(o, "D155_CONTROL {value}").unwrap(); o.flush().unwrap(); }
fn same_files(a: &Path, b: &Path) { assert_eq!(std::fs::read(a).unwrap(), std::fs::read(b).unwrap(), "{} {}", a.display(), b.display()); }
fn scenario(storage: Storage, algo: Algorithm, reverse: bool, iso: bool, warm: bool, extra_board: Option<&str>) -> (Solver, Solver) {
    let sizing = || StreetSizing { bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![] };
    let mut cfg = SpotConfig { board: extra_board.unwrap_or("KsQs2dJd").into(),
        range_oop: if extra_board.is_some() { "AA,AKs" } else { "AA,KK,QQ,JJ,TT,99,88,77,66,55,44,33,22,AKs,AQs,AJs,ATs,A9s,A8s,A7s,A6s,A5s,A4s,A3s,A2s,AKo,AQo,AJo,ATo,KQs,KJs,KTs,QJs,QTs,JTs" }.into(),
        range_ip: if extra_board.is_some() { "QQ,QJs" } else { "AA,QQ,JJ,TT,99,88,77,66,55,44,33,22,AQs,AJs,ATs,A9s,A8s,A7s,A6s,A5s,A4s,A3s,A2s,KQs,KJs,KTs,K9s,QJs,QTs,Q9s,JTs,J9s,T9s,98s,AQo,AJo,KQo" }.into(),
        tree: TreeConfig { starting_pot: 10., effective_stack: if extra_board.is_some() { 4. } else { 20. },
            oop: std::array::from_fn(|_| sizing()), ip: std::array::from_fn(|_| sizing()),
            rake_pct: if warm || (extra_board.is_some() && algo == Algorithm::CfrPlus) { 0.05 } else { 0. },
            rake_cap: 3., ..Default::default() } };
    if reverse { std::mem::swap(&mut cfg.range_oop, &mut cfg.range_ip); }
    let spot = Arc::new(Spot::new(cfg).unwrap());
    assert_ne!(spot.hands[0].len(), spot.hands[1].len());
    let mut a = Solver::with_storage(spot.clone(), storage);
    let mut b = Solver::with_storage(spot, storage);
    a.algo = algo; b.algo = algo; a.use_isomorphism = iso; b.use_isomorphism = iso;
    if warm { a.iterate(); b.iterate(); }
    (a, b)
}
fn poison(g: &mut candidate::GpuSolver, out: &Path, id: usize, stage: &str, p: usize, epoch: &mut usize, witnesses: &mut Vec<Value>) {
    *epoch += 1;
    let before = out.join(format!("clobber-{id:02}-{stage}-before.gpu.bin"));
    let after = out.join(format!("clobber-{id:02}-{stage}-after.gpu.bin"));
    let proof = g.d155_clobber(&before, &after, p, *epoch);
    witnesses.push(json!({"stage": stage, "proof": proof}));
}
fn snapshot(b: &baseline::GpuSolver, g: &candidate::GpuSolver, out: &Path, id: usize, stage: &str, p: usize, cfv_regenerated: bool, records: &mut Vec<Value>) {
    let (x, bi, _) = b.d155_snapshot(&out.join(format!("baseline-{id:02}-{stage}.gpu.bin")), p);
    let (y, gi, _) = g.d155_snapshot(&out.join(format!("candidate-{id:02}-{stage}.gpu.bin")), p);
    let mut normalized = gi.clone(); normalized["wrapper_bytes"] = bi["wrapper_bytes"].clone(); normalized["packet_module_loaded"] = bi["packet_module_loaded"].clone();
    assert_eq!(bi, normalized, "all geometry and graph presence");
    if cfv_regenerated { assert_eq!(x, y, "all state and logical CFV {id}/{stage}"); }
    else { assert_eq!(x[..x.len() - 1], y[..y.len() - 1], "all persistent and nonCFV state {id}/{stage}"); }
    records.push(json!({"stage": stage, "CFV_regenerated": cfv_regenerated, "baseline_info": bi, "candidate_info": gi, "all65other_device_arrays_exact": true}));
}
fn train(b: &mut baseline::GpuSolver, g: &mut candidate::GpuSolver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    b.iterate().unwrap(); g.iterate().unwrap();
    snapshot(b, g, out, id, stage, 1, true, records);
}
fn evaluate(b: &mut baseline::GpuSolver, g: &mut candidate::GpuSolver, a: &Solver, c: &Solver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>, evs: &mut Vec<u64>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    let bx = b.exploitability(a).unwrap(); let gy = g.exploitability(c).unwrap();
    assert!(bx.is_finite() && gy.is_finite()); let x = bx.to_bits(); let y = gy.to_bits();
    assert_eq!(x, y); evs.push(x);
    snapshot(b, g, out, id, stage, 1, true, records);
}
fn cpu_pair(a: &Solver, c: &Solver, out: &Path, id: usize, stage: &str) {
    let x = out.join(format!("baseline-{id:02}-{stage}.cpu.bin")); let y = out.join(format!("candidate-{id:02}-{stage}.cpu.bin"));
    state_frame(a, &x); state_frame(c, &y); same_files(&x, &y);
}
fn full_sync(b: &mut baseline::GpuSolver, g: &mut candidate::GpuSolver, a: &mut Solver, c: &mut Solver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>, readbacks: &mut Vec<Value>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    b.sync_to_cpu(a).unwrap(); readback(g,c,out,id,stage,false,readbacks);
    cpu_pair(a, c, out, id, stage);
    snapshot(b, g, out, id, stage, 1, false, records);
}
fn main() {
    let out = PathBuf::from(std::env::args().nth(1).expect("fresh output")); std::fs::create_dir(&out).unwrap();
    let mut configs = Vec::new();
    for storage in [Storage::Compressed, Storage::F32] { for algo in [Algorithm::Dcfr, Algorithm::CfrPlus] { for reverse in [false, true] { for iso in [false, true] { for warm in [false, true] {
        configs.push((storage, algo, reverse, iso, warm, None));
    } } } } }
    for board in ["Ks7s2d", "Ks7s2dQhTc"] { for (algo, iso) in [(Algorithm::Dcfr, false), (Algorithm::CfrPlus, true)] {
        configs.push((Storage::Compressed, algo, false, iso, false, Some(board)));
    } }
    assert_eq!(configs.len(), 36);
    let mut all = Vec::new(); let mut epoch = 0usize; let mut phase_pairs = 0usize; let mut root_pairs = 0usize;
    for (id, (storage, algo, reverse, iso, warm, extra_board)) in configs.into_iter().enumerate() {
        let (mut a, mut c) = scenario(storage, algo, reverse, iso, warm, extra_board);
        cpu_pair(&a, &c, &out, id, "input");
        let mut b = baseline::GpuSolver::new(&a).unwrap(); let mut g = candidate::GpuSolver::new(&c).unwrap();
        let bp = out.join(format!("baseline-{id:02}-constructor.bin")); let gp = out.join(format!("candidate-{id:02}-constructor.bin"));
        let bc = b.d155_validate(&a, &bp, !warm); let gc = g.d155_validate(&c, &gp, !warm); assert_eq!(bc, gc); same_files(&bp, &gp);
        b.sync_strategy(&mut a).unwrap();g.d155_default_sync(&mut c,true);cpu_pair(&a,&c,&out,id,"default-strategy");
        b.sync_to_cpu(&mut a).unwrap();g.d155_default_sync(&mut c,false);cpu_pair(&a,&c,&out,id,"default-full");
        let mut readbacks=Vec::new();
        let mut witnesses = Vec::new(); let mut records = Vec::new(); let mut evs = Vec::new(); let mut roots = Vec::new();
        for stage in ["train-first", "train-capture", "train-replay"] { train(&mut b, &mut g, &out, id, stage, &mut epoch, &mut witnesses, &mut records); }
        poison(&mut g, &out, id, "strategy-sync", 1, &mut epoch, &mut witnesses);
        b.sync_strategy(&mut a).unwrap(); readback(&mut g,&mut c,&out,id,"strategy-sync",true,&mut readbacks); cpu_pair(&a, &c, &out, id, "strategy-sync"); snapshot(&b, &g, &out, id, "strategy-sync", 1, false, &mut records);
        for stage in ["eval-eager", "eval-capture", "eval-replay"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "full-sync", &mut epoch, &mut witnesses, &mut records,&mut readbacks);
        train(&mut b, &mut g, &out, id, "train-after-sync", &mut epoch, &mut witnesses, &mut records);
        b.sync_to_cpu(&mut a).unwrap(); readback(&mut g,&mut c,&out,id,"prelock-full",false,&mut readbacks); a.ensure_symmetric(); c.ensure_symmetric();
        a.lock_node(&[], LockMode::Freeze, "control".into()).unwrap(); c.lock_node(&[], LockMode::Freeze, "control".into()).unwrap();
        b.update_locks(&a).unwrap(); g.update_locks(&c).unwrap();
        train(&mut b, &mut g, &out, id, "locked-train", &mut epoch, &mut witnesses, &mut records);
        for stage in ["locked-eval-eager", "locked-eval-capture"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        a.clear_locks(); c.clear_locks(); b.update_locks(&a).unwrap(); g.update_locks(&c).unwrap();
        train(&mut b, &mut g, &out, id, "unlocked-train", &mut epoch, &mut witnesses, &mut records);
        evaluate(&mut b, &mut g, &a, &c, &out, id, "unlocked-eval", &mut epoch, &mut witnesses, &mut records, &mut evs);
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "before-save", &mut epoch, &mut witnesses, &mut records,&mut readbacks);
        a.ensure_symmetric(); c.ensure_symmetric();
        let aq = serde_json::to_vec(&a.node_view(&[]).unwrap()).unwrap(); let cq = serde_json::to_vec(&c.node_view(&[]).unwrap()).unwrap(); assert_eq!(aq, cq);
        std::fs::write(out.join(format!("baseline-{id:02}-query.json")), &aq).unwrap(); std::fs::write(out.join(format!("candidate-{id:02}-query.json")), &cq).unwrap();
        let sa = out.join(format!("baseline-{id:02}-state.save")); let sc = out.join(format!("candidate-{id:02}-state.save")); a.save(sa.to_str().unwrap()).unwrap(); c.save(sc.to_str().unwrap()).unwrap(); same_files(&sa, &sc);
        drop(b); drop(g); drop(a); drop(c);
        let mut a = Solver::load_with_storage(sa.to_str().unwrap(), storage).unwrap(); let mut c = Solver::load_with_storage(sc.to_str().unwrap(), storage).unwrap();
        assert_eq!(a.algo, Algorithm::Dcfr); assert_eq!(c.algo, Algorithm::Dcfr); assert!(a.use_isomorphism && c.use_isomorphism);
        a.algo = algo; c.algo = algo; a.use_isomorphism = iso; c.use_isomorphism = iso;
        assert_eq!(a.algo, algo); assert_eq!(c.algo, algo); assert_eq!(a.use_isomorphism, iso); assert_eq!(c.use_isomorphism, iso);
        cpu_pair(&a, &c, &out, id, "loaded");
        let mut b = baseline::GpuSolver::new(&a).unwrap(); let mut g = candidate::GpuSolver::new(&c).unwrap();
        train(&mut b, &mut g, &out, id, "resumed-train", &mut epoch, &mut witnesses, &mut records);
        for stage in ["resumed-eval-eager", "resumed-eval-capture", "resumed-eval-replay"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "resumed-full-sync", &mut epoch, &mut witnesses, &mut records,&mut readbacks);
        assert_eq!(records.len(), 20); assert_eq!(evs.len(), 9);
        if algo == Algorithm::CfrPlus && !iso {
            for (i, p) in [0usize, 1, 0, 1].into_iter().enumerate() {
                let stage = format!("continuation-{i}-p{p}");
                let own: Vec<f32> = (0..a.spot.hands[p].len()).map(|j| if j % 4 == 0 { 0. } else { (j % 7 + 1) as f32 / 8. }).collect();
                let opp: Vec<f32> = (0..a.spot.hands[1-p].len()).map(|j| if j % 5 == 0 { 0. } else { (j % 5 + 1) as f32 / 6. }).collect();
                poison(&mut g, &out, id, &stage, p, &mut epoch, &mut witnesses);
                let x = b.research_continuation_sweep(p, 100 + (i / 2) as u32, &own, &opp).unwrap(); let y = g.research_continuation_sweep(p, 100 + (i / 2) as u32, &own, &opp).unwrap();
                assert!(x.iter().all(|v| v.is_finite()) && y.iter().all(|v| v.is_finite()));
                let xb: Vec<u32> = x.iter().map(|v| v.to_bits()).collect(); let yb: Vec<u32> = y.iter().map(|v| v.to_bits()).collect(); assert_eq!(xb, yb); roots.push(xb); root_pairs += 1;
                snapshot(&b, &g, &out, id, &stage, p, true, &mut records);
            }
            b.sync_to_cpu(&mut a).unwrap(); readback(&mut g,&mut c,&out,id,"continuation-final",false,&mut readbacks); cpu_pair(&a, &c, &out, id, "continuation-final");
        }
        assert_eq!(witnesses.len(), records.len()); phase_pairs += records.len();
        all.push(json!({"case": id, "storage": format!("{storage:?}"), "algorithm": format!("{algo:?}"), "reverse_ranges": reverse, "isomorphism": iso, "warm_CPU_start": warm, "extra_board": extra_board, "resume_fixture_flags_explicitly_restored": true, "constructor": bc, "readbacks": readbacks, "default_public_fallbacks_silent": true, "clobbers": witnesses, "phases": records, "exploit_bits": evs, "continuation_root_bits": roots, "all_CPU_query_save_files_exact": true}));
        emit(json!({"stage": "case_complete", "case": id, "phases": all.last().unwrap()["phases"].as_array().unwrap().len(), "exact": true}));
    }
    assert_eq!(phase_pairs, 752); assert_eq!(epoch, 752); assert_eq!(root_pairs, 32);
    let metadata = json!({"id": "D155", "cases": all, "case_count": 36, "clobbers": epoch, "phase_pairs": phase_pairs, "constructor_pairs": 36, "exploitability_pairs": 324, "continuation_root_pairs": root_pairs, "performance_measurement": false, "packing_implementation_created": true});
    let mut f = OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap(); f.write_all(serde_json::to_string_pretty(&metadata).unwrap().as_bytes()).unwrap(); f.sync_all().unwrap();
    emit(json!({"stage": "complete", "cases": 36, "clobbers": epoch, "phase_pairs": phase_pairs, "continuation_root_pairs": root_pairs}));
}
