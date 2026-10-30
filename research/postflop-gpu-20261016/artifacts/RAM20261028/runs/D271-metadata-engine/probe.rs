#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
use solver::store::{Store,Storage};
use cudarc::driver::{CudaContext,CudaSlice,CudaStream,DeviceRepr};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf},sync::Arc};
#[path="observed.rs"]mod observed;
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
    o.write_all(b"D150-STATE-v1\0\0\0").unwrap();
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
fn emit(value: Value) { let mut o = std::io::stdout().lock(); writeln!(o, "D150_CONTROL {value}").unwrap(); o.flush().unwrap(); }
fn same_files(a: &Path, b: &Path) { assert_eq!(std::fs::read(a).unwrap(), std::fs::read(b).unwrap(), "{} {}", a.display(), b.display()); }
fn scenario(storage: Storage, algo: Algorithm, reverse: bool, iso: bool, warm: bool, extra_board: Option<&str>) -> (Solver, Solver) {
    let sizing = || StreetSizing { bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![] };
    let mut cfg = SpotConfig { board: extra_board.unwrap_or("KsQs2dJd").into(),
        range_oop: if extra_board.is_some() { "AA,AKs" } else { "AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo" }.into(),
        range_ip: if extra_board.is_some() { "QQ,QJs" } else { "AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo" }.into(),
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
fn poison(g: &mut observed::GpuSolver, out: &Path, id: usize, stage: &str, p: usize, epoch: &mut usize, witnesses: &mut Vec<Value>) {
    *epoch += 1;
    let before = out.join(format!("clobber-{id:02}-{stage}-before.gpu.bin"));
    let after = out.join(format!("clobber-{id:02}-{stage}-after.gpu.bin"));
    let proof = g.d150_clobber(&before, &after, p, *epoch);
    witnesses.push(json!({"stage": stage, "proof": proof}));
}
fn snapshot(b: &observed::GpuSolver, g: &observed::GpuSolver, out: &Path, id: usize, stage: &str, p: usize, cfv_regenerated: bool, records: &mut Vec<Value>) {
    let (x, bi, _) = b.d150_snapshot(&out.join(format!("baseline-{id:02}-{stage}.gpu.bin")), p);
    let (y, gi, _) = g.d150_snapshot(&out.join(format!("clobbered-{id:02}-{stage}.gpu.bin")), p);
    assert_eq!(bi, gi);
    if cfv_regenerated { assert_eq!(x, y, "all state and logical CFV {id}/{stage}"); }
    else { assert_eq!(x[..x.len() - 1], y[..y.len() - 1], "all persistent and nonCFV state {id}/{stage}"); }
    records.push(json!({"stage": stage, "CFV_regenerated": cfv_regenerated, "info": bi, "all65other_device_arrays_exact": true}));
}
fn train(b: &mut observed::GpuSolver, g: &mut observed::GpuSolver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    b.iterate().unwrap(); g.iterate().unwrap();
    snapshot(b, g, out, id, stage, 1, true, records);
}
fn evaluate(b: &mut observed::GpuSolver, g: &mut observed::GpuSolver, a: &Solver, c: &Solver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>, evs: &mut Vec<u64>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    let bx = b.exploitability(a).unwrap(); let gy = g.exploitability(c).unwrap();
    assert!(bx.is_finite() && gy.is_finite()); let x = bx.to_bits(); let y = gy.to_bits();
    assert_eq!(x, y); evs.push(x);
    snapshot(b, g, out, id, stage, 1, true, records);
}
fn cpu_pair(a: &Solver, c: &Solver, out: &Path, id: usize, stage: &str) {
    let x = out.join(format!("baseline-{id:02}-{stage}.cpu.bin")); let y = out.join(format!("clobbered-{id:02}-{stage}.cpu.bin"));
    state_frame(a, &x); state_frame(c, &y); same_files(&x, &y);
}
fn full_sync(b: &mut observed::GpuSolver, g: &mut observed::GpuSolver, a: &mut Solver, c: &mut Solver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    b.sync_to_cpu(a).unwrap(); g.sync_to_cpu(c).unwrap();
    cpu_pair(a, c, out, id, stage);
    snapshot(b, g, out, id, stage, 1, false, records);
}
fn main() {
    let out = PathBuf::from(std::env::args().nth(1).expect("fresh output")); std::fs::create_dir(&out).unwrap(); D271_OUTPUT.set(out.clone()).unwrap();
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
        let mut b = d271_new(0,&a); let mut g = d271_new(1,&c);
        let bp = out.join(format!("baseline-{id:02}-constructor.bin")); let gp = out.join(format!("clobbered-{id:02}-constructor.bin"));
        let bc = b.d150_validate(&a, &bp, !warm); let gc = g.d150_validate(&c, &gp, !warm); assert_eq!(bc, gc); g.d271_same_constructor(&bp,&gp);
        let mut witnesses = Vec::new(); let mut records = Vec::new(); let mut evs = Vec::new(); let mut roots = Vec::new();
        for stage in ["train-first", "train-capture", "train-replay"] { train(&mut b, &mut g, &out, id, stage, &mut epoch, &mut witnesses, &mut records); }
        poison(&mut g, &out, id, "strategy-sync", 1, &mut epoch, &mut witnesses);
        b.sync_strategy(&mut a).unwrap(); g.sync_strategy(&mut c).unwrap(); cpu_pair(&a, &c, &out, id, "strategy-sync"); snapshot(&b, &g, &out, id, "strategy-sync", 1, false, &mut records);
        for stage in ["eval-eager", "eval-capture", "eval-replay"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "full-sync", &mut epoch, &mut witnesses, &mut records);
        train(&mut b, &mut g, &out, id, "train-after-sync", &mut epoch, &mut witnesses, &mut records);
        b.sync_to_cpu(&mut a).unwrap(); g.sync_to_cpu(&mut c).unwrap(); a.ensure_symmetric(); c.ensure_symmetric();
        a.lock_node(&[], LockMode::Freeze, "control".into()).unwrap(); c.lock_node(&[], LockMode::Freeze, "control".into()).unwrap();
        b.update_locks(&a).unwrap(); g.update_locks(&c).unwrap();
        train(&mut b, &mut g, &out, id, "locked-train", &mut epoch, &mut witnesses, &mut records);
        for stage in ["locked-eval-eager", "locked-eval-capture"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        a.clear_locks(); c.clear_locks(); b.update_locks(&a).unwrap(); g.update_locks(&c).unwrap();
        train(&mut b, &mut g, &out, id, "unlocked-train", &mut epoch, &mut witnesses, &mut records);
        evaluate(&mut b, &mut g, &a, &c, &out, id, "unlocked-eval", &mut epoch, &mut witnesses, &mut records, &mut evs);
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "before-save", &mut epoch, &mut witnesses, &mut records);
        a.ensure_symmetric(); c.ensure_symmetric();
        let aq = serde_json::to_vec(&a.node_view(&[]).unwrap()).unwrap(); let cq = serde_json::to_vec(&c.node_view(&[]).unwrap()).unwrap(); assert_eq!(aq, cq);
        std::fs::write(out.join(format!("baseline-{id:02}-query.json")), &aq).unwrap(); std::fs::write(out.join(format!("clobbered-{id:02}-query.json")), &cq).unwrap();
        let sa = out.join(format!("baseline-{id:02}-state.save")); let sc = out.join(format!("clobbered-{id:02}-state.save")); a.save(sa.to_str().unwrap()).unwrap(); c.save(sc.to_str().unwrap()).unwrap(); same_files(&sa, &sc);
        drop(b); drop(g); drop(a); drop(c);
        let mut a = Solver::load_with_storage(sa.to_str().unwrap(), storage).unwrap(); let mut c = Solver::load_with_storage(sc.to_str().unwrap(), storage).unwrap();
        assert_eq!(a.algo, Algorithm::Dcfr); assert_eq!(c.algo, Algorithm::Dcfr); assert!(a.use_isomorphism && c.use_isomorphism);
        a.algo = algo; c.algo = algo; a.use_isomorphism = iso; c.use_isomorphism = iso;
        assert_eq!(a.algo, algo); assert_eq!(c.algo, algo); assert_eq!(a.use_isomorphism, iso); assert_eq!(c.use_isomorphism, iso);
        cpu_pair(&a, &c, &out, id, "loaded");
        let mut b = d271_new(0,&a); let mut g = d271_new(1,&c);
        train(&mut b, &mut g, &out, id, "resumed-train", &mut epoch, &mut witnesses, &mut records);
        for stage in ["resumed-eval-eager", "resumed-eval-capture", "resumed-eval-replay"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "resumed-full-sync", &mut epoch, &mut witnesses, &mut records);
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
            b.sync_to_cpu(&mut a).unwrap(); g.sync_to_cpu(&mut c).unwrap(); cpu_pair(&a, &c, &out, id, "continuation-final");
        }
        assert_eq!(witnesses.len(), records.len()); phase_pairs += records.len();
        all.push(json!({"case": id, "storage": format!("{storage:?}"), "algorithm": format!("{algo:?}"), "reverse_ranges": reverse, "isomorphism": iso, "warm_CPU_start": warm, "extra_board": extra_board, "resume_fixture_flags_explicitly_restored": true, "constructor": bc, "clobbers": witnesses, "phases": records, "exploit_bits": evs, "continuation_root_bits": roots, "all_CPU_query_save_files_exact": true}));
        emit(json!({"stage": "case_complete", "case": id, "phases": all.last().unwrap()["phases"].as_array().unwrap().len(), "exact": true}));
    }
    assert_eq!(phase_pairs, 752); assert_eq!(epoch, 752); assert_eq!(root_pairs, 32);
    assert_eq!(D271_BINDS[0].load(std::sync::atomic::Ordering::SeqCst),72);assert_eq!(D271_BINDS[1].load(std::sync::atomic::Ordering::SeqCst),72);
    d271_extra_lock_controls(&out);
    assert_eq!(D271_BINDS[0].load(std::sync::atomic::Ordering::SeqCst),78);assert_eq!(D271_BINDS[1].load(std::sync::atomic::Ordering::SeqCst),78);
    let metadata = json!({"id": "D150", "cases": all, "case_count": 36, "clobbers": epoch, "phase_pairs": phase_pairs, "constructor_pairs": 36, "exploitability_pairs": 324, "continuation_root_pairs": root_pairs, "performance_measurement": false, "packing_implementation_created": false});
    let mut f = OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap(); f.write_all(serde_json::to_string_pretty(&metadata).unwrap().as_bytes()).unwrap(); f.sync_all().unwrap();
    emit(json!({"stage": "complete", "cases": 36, "clobbers": epoch, "phase_pairs": phase_pairs, "continuation_root_pairs": root_pairs}));
}

static D271_ARM:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(2);
static D271_BINDS:[std::sync::atomic::AtomicUsize;2]=[std::sync::atomic::AtomicUsize::new(0),std::sync::atomic::AtomicUsize::new(0)];
fn d271_ptx(arch:&str)->cudarc::nvrtc::Ptx{
 assert_eq!(arch,"compute_120");let arm=D271_ARM.load(std::sync::atomic::Ordering::SeqCst);assert!(arm<2);
 let call=D271_BINDS[arm].fetch_add(1,std::sync::atomic::Ordering::SeqCst)+1;
 println!("D271_PTX_BIND {}",serde_json::json!({"arm":arm,"call":call,"architecture":arch}));std::io::stdout().flush().unwrap();
 cudarc::nvrtc::Ptx::from_src(if arm==0{include_str!("baseline.ptx")}else{include_str!("candidate.ptx")})
}
fn d271_new(arm:usize,solver:&Solver)->observed::GpuSolver{
 assert!(arm<2);D271_ARM.store(arm,std::sync::atomic::Ordering::SeqCst);
 let result=observed::GpuSolver::new(solver).unwrap();assert_eq!(D271_ARM.load(std::sync::atomic::Ordering::SeqCst),arm);assert_eq!(result.d271_arm(),arm);result
}

trait Encode {fn size(&self)->u64;fn encode(&self,w:&mut impl Write);}
macro_rules! primitive{($t:ty,$n:expr,$f:expr)=>{impl Encode for $t{fn size(&self)->u64{$n}fn encode(&self,w:&mut impl Write){w.write_all(&($f)(*self)).unwrap();}}};}
primitive!(u32,4,|x:u32|x.to_le_bytes());primitive!(i32,4,|x:i32|x.to_le_bytes());primitive!(f32,4,|x:f32|x.to_bits().to_le_bytes());primitive!(u64,8,|x:u64|x.to_le_bytes());primitive!(usize,8,|x:usize|(x as u64).to_le_bytes());primitive!(bool,1,|x:bool|[x as u8]);
impl<T:Encode> Encode for Vec<T>{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(self.len() as u64).encode(w);for x in self{x.encode(w);}}}
impl<T:Encode,const N:usize> Encode for [T;N]{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(N as u64).encode(w);for x in self{x.encode(w);}}}
impl Encode for solver::gpu::plan::LevelSpan{fn size(&self)->u64{8}fn encode(&self,w:&mut impl Write){self.start.encode(w);self.count.encode(w);}}
fn field(w:&mut impl Write,name:&str,v:&impl Encode){assert!(name.len()<256);(name.len() as u32).encode(w);w.write_all(name.as_bytes()).unwrap();let bytes=v.size();assert!(bytes<=2*1024*1024*1024);bytes.encode(w);v.encode(w);}
fn dump_baseline(p:&solver::gpu::plan::GpuPlan,path:&Path){let mut w=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());w.write_all(b"D183_PLAN_RAW1\0\0\0").unwrap();
 field(&mut w,"num_levels",&p.num_levels);
 field(&mut w,"nh",&p.nh);
 field(&mut w,"nh_max",&p.nh_max);
 field(&mut w,"num_nodes",&p.num_nodes);
 field(&mut w,"iso_active",&p.iso_active);
 field(&mut w,"action_nodes",&p.action_nodes);
 field(&mut w,"action_spans",&p.action_spans);
 field(&mut w,"chance_parents",&p.chance_parents);
 field(&mut w,"chance_children",&p.chance_children);
 field(&mut w,"chance_cards",&p.chance_cards);
 field(&mut w,"chance_spans",&p.chance_spans);
 field(&mut w,"chance_nodes",&p.chance_nodes);
 field(&mut w,"chance_node_spans",&p.chance_node_spans);
 field(&mut w,"fold_nodes",&p.fold_nodes);
 field(&mut w,"fold_spans",&p.fold_spans);
 field(&mut w,"show_nodes",&p.show_nodes);
 field(&mut w,"show_spans",&p.show_spans);
 field(&mut w,"cc_start",&p.cc_start);
 field(&mut w,"cc_count",&p.cc_count);
 field(&mut w,"cc_card",&p.cc_card);
 field(&mut w,"cc_child",&p.cc_child);
 field(&mut w,"cc_perm",&p.cc_perm);
 field(&mut w,"hand_perm_flat",&p.hand_perm_flat);
 field(&mut w,"node_player",&p.node_player);
 field(&mut w,"node_na",&p.node_na);
 field(&mut w,"node_data_off",&p.node_data_off);
 field(&mut w,"arena_elements",&p.arena_elements);
 field(&mut w,"node_children_start",&p.node_children_start);
 field(&mut w,"node_twin",&p.node_twin);
 field(&mut w,"node_tlose",&p.node_tlose);
 field(&mut w,"node_ttie",&p.node_ttie);
 field(&mut w,"node_cdiv",&p.node_cdiv);
 field(&mut w,"node_river_slot",&p.node_river_slot);
 field(&mut w,"reach_src",&p.reach_src);
 field(&mut w,"reach_slot",&p.reach_slot);
 field(&mut w,"reach_blocks",&p.reach_blocks);
 field(&mut w,"cfv_slot",&p.cfv_slot);
 field(&mut w,"cfv_blocks",&p.cfv_blocks);
 field(&mut w,"hand_c1",&p.hand_c1);
 field(&mut w,"hand_c2",&p.hand_c2);
 field(&mut w,"hand_mask",&p.hand_mask);
 field(&mut w,"same_combo",&p.same_combo);
 field(&mut w,"weights",&p.weights);
 field(&mut w,"num_slots",&p.num_slots);
 field(&mut w,"riv_off",&p.riv_off);
 field(&mut w,"riv_cnt",&p.riv_cnt);
 field(&mut w,"riv_sorted_idx",&p.riv_sorted_idx);
 field(&mut w,"riv_sorted_str",&p.riv_sorted_str);
 field(&mut w,"riv_lower",&p.riv_lower);
 field(&mut w,"riv_upper",&p.riv_upper);
 field(&mut w,"riv_card_off",&p.riv_card_off);
 field(&mut w,"riv_card_pos",&p.riv_card_pos);
 field(&mut w,"riv_max_cnt",&p.riv_max_cnt);
w.flush().unwrap();w.get_ref().sync_all().unwrap();assert!(w.get_ref().metadata().unwrap().len()<=2*1024*1024*1024);}

// Diagnostic CPU oracle and inverse of actual retained GPU metadata images.
const D271_ROW_FIELDS: &[&str] = &["d_node_player","d_node_na","d_node_data_off","d_node_children_start",
 "d_node_twin","d_node_tlose","d_node_ttie","d_node_cdiv","d_node_river_slot","d_cc_start","d_cc_count",
 "d_rsrc[0]","d_rsrc[1]","d_cfv_slot","d_lock_off"];
const D271_ID_FIELDS: &[&str] = &["d_action_nodes","d_chance_parents","d_chance_children","d_chance_nodes",
 "d_fold_nodes","d_show_nodes","d_cc_child","d_children"];
const D271_INVENTORY: &[&str] = &["d_action_nodes", "d_chance_parents", "d_chance_children", "d_chance_cards", "d_chance_nodes", "d_fold_nodes", "d_show_nodes", "d_node_player", "d_node_na", "d_node_data_off", "d_node_children_start", "d_node_twin", "d_node_tlose", "d_node_ttie", "d_node_cdiv", "d_node_river_slot", "d_cc_start", "d_cc_count", "d_cc_card", "d_cc_child", "d_cc_perm", "d_hand_perm[0]", "d_hand_perm[1]", "d_rsrc[0]", "d_rsrc[1]", "d_children", "d_fold_card_off[0]", "d_fold_card_off[1]", "d_fold_card_idx[0]", "d_fold_card_idx[1]", "d_hand_c1[0]", "d_hand_c1[1]", "d_hand_c2[0]", "d_hand_c2[1]", "d_hand_mask[0]", "d_hand_mask[1]", "d_same[0]", "d_same[1]", "d_weights[0]", "d_weights[1]", "d_riv_off[0]", "d_riv_off[1]", "d_riv_cnt[0]", "d_riv_cnt[1]", "d_riv_idx[0]", "d_riv_idx[1]", "d_riv_lower[0]", "d_riv_lower[1]", "d_riv_upper[0]", "d_riv_upper[1]", "d_riv_card_off[0]", "d_riv_card_off[1]", "d_riv_card_pos[0]", "d_riv_card_pos[1]", "d_lock_off", "d_lock_sigma", "d_regrets[0]", "d_regrets[1]", "d_strat[0]", "d_strat[1]", "d_reach[0]", "d_reach[1]", "d_cfv_slot", "d_cfv", "d_eval_roots", "d_disc"];
static D271_OUTPUT:std::sync::OnceLock<PathBuf>=std::sync::OnceLock::new();

fn d271_cpu_plan(s:&Solver)->solver::gpu::plan::GpuPlan {
 let mut p=solver::gpu::plan::GpuPlan::build(&s.spot,s.use_isomorphism);
 if s.storage==Storage::F32 {
  p.arena_elements=[s.spot.tree.data_size[0]as usize,s.spot.tree.data_size[1]as usize];
  for(i,n)in s.spot.tree.nodes.iter().enumerate(){p.node_data_off[i]=n.data_offset;}
 }
 p
}
fn d271_permutation(p:&solver::gpu::plan::GpuPlan,ordered:bool)->(Vec<u32>,Vec<u32>){
 if !ordered {let v:Vec<u32>=(0..p.num_nodes as u32).collect();return(v.clone(),v);}
 // Separate sort-based oracle, not a call to production metadata::build_map.
 let mut tagged=Vec::new();
 for(level,_)in p.action_spans.iter().enumerate(){
  for(kind,(nodes,spans))in[(&p.action_nodes,&p.action_spans),(&p.chance_nodes,&p.chance_node_spans),
    (&p.fold_nodes,&p.fold_spans),(&p.show_nodes,&p.show_spans)].into_iter().enumerate(){
   let span=spans[level];for ordinal in 0..span.count as usize{
    tagged.push((level,kind,ordinal,nodes[span.start as usize+ordinal]));
   }
  }
 }
 tagged.sort_unstable_by_key(|x|(x.0,x.1,x.2));
 let mut seen=vec![false;p.num_nodes];let mut inverse=Vec::with_capacity(p.num_nodes);
 for(_,_,_,old)in tagged {assert!(!seen[old as usize]);seen[old as usize]=true;inverse.push(old);}
 inverse.extend((0..p.num_nodes).filter(|&n|!seen[n]).map(|n|n as u32));
 assert_eq!(inverse.len(),p.num_nodes);
 let mut forward=vec![u32::MAX;p.num_nodes];for(new,&old)in inverse.iter().enumerate(){forward[old as usize]=new as u32;}
 assert_eq!(forward[0],0);assert_eq!(inverse[0],0);(forward,inverse)
}
fn d271_expected_rows<T:Clone>(v:&[T],inverse:&[u32])->Vec<T>{
 assert_eq!(v.len(),inverse.len());inverse.iter().map(|&old|v[old as usize].clone()).collect()
}
fn d271_expected_ids(v:&[u32],forward:&[u32])->Vec<u32>{
 v.iter().map(|&old|if old==u32::MAX{old}else{forward[old as usize]}).collect()
}
fn d271_normalize(name:&str,v:&[u32],forward:&[u32],inverse:&[u32])->Vec<u32>{
 if D271_ROW_FIELDS.contains(&name){
  let width=if name=="d_node_data_off"||name=="d_lock_off"{2}else{1};
  assert_eq!(v.len(),forward.len()*width);let mut out=vec![0;v.len()];
  for(old,&new)in forward.iter().enumerate(){out[old*width..(old+1)*width].copy_from_slice(&v[new as usize*width..(new as usize+1)*width]);}out
 }else if D271_ID_FIELDS.contains(&name){
  v.iter().map(|&new|if new==u32::MAX{new}else{inverse[new as usize]}).collect()
 }else{v.to_vec()}
}
fn d271_normalize_image(v:&mut[Vec<u32>],forward:&[u32],inverse:&[u32]){
 assert_eq!(v.len(),69);let mut at=3;
 for &name in D271_INVENTORY{if name!="d_cfv"{v[at]=d271_normalize(name,&v[at],forward,inverse);at+=1;}}
 assert_eq!(at,68); // index68 is unchanged current-player physical-layout logical CFV
}
fn d271_normalize_frame(mut bytes:Vec<u8>,forward:&[u32],inverse:&[u32])->Vec<u8>{
 assert_eq!(&bytes[..16],b"D150-FRAME-v1\0\0\0");let mut at=16;
 while at<bytes.len(){
  let kind=u32::from_le_bytes(bytes[at..at+4].try_into().unwrap());let n=u32::from_le_bytes(bytes[at+4..at+8].try_into().unwrap())as usize;at+=8;
  let name=std::str::from_utf8(&bytes[at..at+n]).unwrap().to_string();at+=n;
  let count=u64::from_le_bytes(bytes[at..at+8].try_into().unwrap())as usize;at+=8;
  if kind==0{assert_eq!(&bytes[at..at+4],&[0;4]);at+=4;}
  else{assert_eq!(kind,1);for _ in 0..2{
   let end=at+count*4;let v:Vec<u32>=bytes[at..end].chunks_exact(4).map(|x|u32::from_le_bytes(x.try_into().unwrap())).collect();
   let normalized=d271_normalize(&name,&v,forward,inverse);assert_eq!(normalized.len(),count);
   for(i,value)in normalized.iter().enumerate(){bytes[at+i*4..at+(i+1)*4].copy_from_slice(&value.to_le_bytes());}at=end;
  }}
 }
 assert_eq!(at,bytes.len());bytes
}
fn d271_dump_maps(path:&Path,forward:&[u32],inverse:&[u32]){
 let mut w=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());
 w.write_all(b"D267-MODEL-v1\0\0\0").unwrap();w.write_all(&2u32.to_le_bytes()).unwrap();
 for(name,values)in[("old_to_new",forward),("new_to_old",inverse)]{
  w.write_all(&(name.len()as u32).to_le_bytes()).unwrap();w.write_all(name.as_bytes()).unwrap();
  w.write_all(&4u32.to_le_bytes()).unwrap();w.write_all(&(values.len()as u64).to_le_bytes()).unwrap();
  for v in values{w.write_all(&v.to_le_bytes()).unwrap();}
 }w.flush().unwrap();w.get_ref().sync_all().unwrap();
}

fn d271_extra_snapshot(b:&observed::GpuSolver,g:&observed::GpuSolver,out:&Path,stage:&str)->Value{
 let(x,bi,bp)=b.d150_snapshot(&out.join(format!("baseline-{stage}.gpu.bin")),1);
 let(y,gi,gp)=g.d150_snapshot(&out.join(format!("clobbered-{stage}.gpu.bin")),1);
 assert_eq!(bi,gi);assert_eq!(x,y);assert_eq!(bp,gp,"entire physical CFV in nonpoisoned extra control");
 json!({"stage":stage,"info":bi,"all66_actual_arrays_and_whole_physical_CFV_exact":true})
}
fn d271_extra_lock_controls(out:&Path){
 let cases=[(Storage::Compressed,Algorithm::Dcfr,true,"Ks7s2d"),
  (Storage::Compressed,Algorithm::CfrPlus,true,"Ks7s2d"),
  (Storage::F32,Algorithm::Dcfr,true,"Ks7s2d"),
  (Storage::Compressed,Algorithm::Dcfr,false,"Ks7s2d"),
  (Storage::Compressed,Algorithm::Dcfr,true,"KsQs2dJd"),
  (Storage::Compressed,Algorithm::Dcfr,true,"Ks7s2dQhTc")];
 let extra=out.join("extra");std::fs::create_dir(&extra).unwrap();let mut all=Vec::new();
 for(id,(storage,algo,iso,board))in cases.into_iter().enumerate(){
  let folder=extra.join(id.to_string());std::fs::create_dir(&folder).unwrap();
  let(mut a,mut c)=scenario(storage,algo,false,iso,false,Some(board));
  let mut b=d271_new(0,&a);let mut g=d271_new(1,&c);
  let plan=d271_cpu_plan(&a);let mut records=Vec::new();let mut evs=Vec::new();
  let bp=folder.join("baseline-constructor.bin");let gp=folder.join("clobbered-constructor.bin");
  assert_eq!(b.d150_validate(&a,&bp,true),g.d150_validate(&c,&gp,true));g.d271_same_constructor(&bp,&gp);
  for _ in 0..3{b.iterate().unwrap();g.iterate().unwrap();}
  for _ in 0..3{let x=b.exploitability(&a).unwrap();let y=g.exploitability(&c).unwrap();assert!(x.is_finite()&&y.is_finite());assert_eq!(x.to_bits(),y.to_bits());evs.push(x.to_bits());}
  records.push(d271_extra_snapshot(&b,&g,&folder,"warm"));
  let mut categories=Vec::new();let mut chosen=Vec::new();
  for category in ["root","active_action","inactive_action","chance","fold","show"]{
   let possible:Vec<usize>=a.spot.tree.nodes.iter().enumerate().filter_map(|(i,n)|{
    let yes=match category{
     "root"=>i==0,
     "active_action"=>i>0&&n.kind==tree::KIND_ACTION&&plan.node_data_off[i]!=u64::MAX,
     "inactive_action"=>i>0&&n.kind==tree::KIND_ACTION&&plan.node_data_off[i]==u64::MAX,
     "chance"=>n.kind==tree::KIND_CHANCE,"fold"=>n.kind==tree::KIND_TERM_FOLD,"show"=>n.kind==tree::KIND_TERM_SHOWDOWN,_=>false};
    yes.then_some(i)
   }).collect();
   let selected=possible.iter().copied().find(|&i|g.forward[i]!=i as u32).or_else(||possible.first().copied());
   categories.push(json!({"category":category,"available":possible.len(),"chosen":selected,"changed_ID":selected.map(|i|g.forward[i]!=i as u32).unwrap_or(false)}));
   if let Some(i)=selected{assert!(!chosen.contains(&i));chosen.push(i);let n=&a.spot.tree.nodes[i];
    let sigma=if n.kind==tree::KIND_ACTION{
     let nh=a.spot.hands[n.player as usize].len();let mut v=vec![0.;n.num_children as usize*nh];v[..nh].fill(1.);v
    }else{[0,0x80000000,0x7fc00123,0x7f800123].into_iter().map(f32::from_bits).collect()};
    a.locks.insert(i as u32,sigma);
   }
  }
  if g.selected{
   assert!(categories.iter().any(|x|x["category"]=="active_action"&&x["changed_ID"]==true));
   assert!(categories.iter().any(|x|["chance","fold","show"].contains(&x["category"].as_str().unwrap())&&x["changed_ID"]==true));
  }
  c.locks=a.locks.clone();
  b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();
  let uploaded=d271_extra_snapshot(&b,&g,&folder,"lock-upload");assert_eq!(uploaded["info"]["graphs_present"],false);assert_eq!(uploaded["info"]["eval_graphs_present"],json!([false,false]));records.push(uploaded);
  for _ in 0..3{b.iterate().unwrap();g.iterate().unwrap();}
  for _ in 0..3{let x=b.exploitability(&a).unwrap();let y=g.exploitability(&c).unwrap();assert!(x.is_finite()&&y.is_finite());assert_eq!(x.to_bits(),y.to_bits());evs.push(x.to_bits());}
  records.push(d271_extra_snapshot(&b,&g,&folder,"locked"));
  a.clear_locks();c.clear_locks();b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();
  let unlocked=d271_extra_snapshot(&b,&g,&folder,"unlock-upload");assert_eq!(unlocked["info"]["graphs_present"],false);assert_eq!(unlocked["info"]["eval_graphs_present"],json!([false,false]));records.push(unlocked);
  for _ in 0..3{b.iterate().unwrap();g.iterate().unwrap();}
  for _ in 0..3{let x=b.exploitability(&a).unwrap();let y=g.exploitability(&c).unwrap();assert!(x.is_finite()&&y.is_finite());assert_eq!(x.to_bits(),y.to_bits());evs.push(x.to_bits());}
  records.push(d271_extra_snapshot(&b,&g,&folder,"unlocked"));
  b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();
  let ap=folder.join("baseline-final.cpu.bin");let cp=folder.join("clobbered-final.cpu.bin");state_frame(&a,&ap);state_frame(&c,&cp);same_files(&ap,&cp);
  assert_eq!(records.len(),5);assert_eq!(evs.len(),9);
  all.push(json!({"case":id,"storage":format!("{storage:?}"),"algorithm":format!("{algo:?}"),"iso":iso,"board":board,"selected":g.selected,"categories":categories,"phases":records,"EV_bits":evs,"CPU_state_exact":true}));
  println!("D271_EXTRA {}",json!({"case":id,"selected":g.selected,"phases":5,"EVs":9,"exact":true}));std::io::stdout().flush().unwrap();
 }
 assert!(all.iter().any(|x|x["selected"]==true));assert!(all.iter().any(|x|x["selected"]==false));
 let mut file=OpenOptions::new().create_new(true).write(true).open(out.join("extra-metadata.json")).unwrap();
 file.write_all(serde_json::to_string_pretty(&all).unwrap().as_bytes()).unwrap();file.sync_all().unwrap();
}
