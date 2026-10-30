//! Oracle: the unchanged single-output traversal, not another paired evaluator.
use super::*;
use std::cell::RefCell;
use std::sync::OnceLock;

#[derive(Default)]
struct Trace { terminals: usize, visits: usize, cancel_at: Option<usize> }
thread_local! { static TRACE: RefCell<Option<Trace>> = const { RefCell::new(None) }; }
pub(super) fn observe_terminal() {
    TRACE.with(|t| { if let Some(t) = t.borrow_mut().as_mut() { t.terminals += 1; } });
}
pub(super) fn observe_checkpoint_visit(s: &PreflopSolver) {
    let cancel = TRACE.with(|t| {
        let mut trace = t.borrow_mut();
        if let Some(t) = trace.as_mut() {
            t.visits += 1;
            t.cancel_at.is_some_and(|n| t.visits >= n)
        } else { false }
    });
    if cancel { s.stop_flag.as_ref().expect("installed test stop flag").store(true, Ordering::Relaxed); }
}
fn table() -> Arc<EquityTable> {
    static TABLE: OnceLock<Arc<EquityTable>> = OnceLock::new();
    // Small deterministic HU fixture table only. Coupled terminals still use
    // the unchanged production 1,024-particle/f64 deck.
    TABLE.get_or_init(|| Arc::new(EquityTable::build(256))).clone()
}
fn fixture(n: usize, legacy: bool) -> PreflopSolver {
    let positions = match n { 2 => vec!["SB","BB"], 3 => vec!["BTN","SB","BB"], _ => vec!["CO","BTN","SB","BB"] };
    let mut posts = vec![0.0; n]; posts[n-2] = 0.5; posts[n-1] = 1.0;
    let cfg = serde_json::from_value(serde_json::json!({
        "positions": positions, "posts": posts, "stack": 5.0,
        "limp": true, "open_raises": [2.0], "raise_mults": [3.0],
        "max_raises": 1, "add_allin": false, "rake_pct": 5.0,
        "rake_cap": 1.0, "realization": "raw"
    })).unwrap();
    let mut s = PreflopSolver::new(cfg, table()).unwrap();
    if legacy { s.set_multiway_equity_model("legacy_product").unwrap(); }
    s
}
fn seed(s: &mut PreflopSolver, sparse: bool) {
    // Exclusive test setup. Whole-zero actions coexist with per-hand zeros;
    // the former may be skipped only by one of the paired outputs.
    let sums = unsafe { s.strat_sum.slice_mut() };
    for (i, nd) in s.nodes.iter().enumerate().filter(|(_,n)| n.kind == KIND_ACTION) {
        for a in 0..nd.actions.len() { for h in 0..NUM_CLASSES {
            sums[nd.data_off+a*NUM_CLASSES+h] = if sparse && nd.actions.len()>1 && a==0 {0.0}
                else { 1.0 + ((i*3 + a*7 + h*11)%19) as f32 };
            if sparse && a>0 && h%7==0 && a+1<nd.actions.len() { sums[nd.data_off+a*NUM_CLASSES+h] = 0.0; }
        }}
    }
    s.iteration = 11;
}
fn f32_bits(v: &[f32]) -> Vec<u32> { v.iter().map(|x|x.to_bits()).collect() }
fn f64_bits(v: &[f64]) -> Vec<u64> { v.iter().map(|x|x.to_bits()).collect() }
fn reference(s: &PreflopSolver) -> (Vec<f64>, Vec<f64>) {
    (0..s.n).map(|p| {
        let br = s.traverse(0,p,&mut s.root_reaches(),if s.constrained_br(p) {3} else {2},0);
        let avg = s.traverse(0,p,&mut s.root_reaches(),1,0);
        let (mut g,mut ev)=(0f64,0f64);
        for h in 0..NUM_CLASSES { let w=class_prob(h) as f64; g+=w*(br[h]-avg[h]) as f64; ev+=w*avg[h] as f64; }
        (g,ev)
    }).unzip()
}
fn parity(s: &PreflopSolver) {
    let before=s.arena_snapshot();
    for p in 0..s.n { for mode in [2,3] {
        let br=s.traverse(0,p,&mut s.root_reaches(),mode,0);
        let avg=s.traverse(0,p,&mut s.root_reaches(),1,0);
        for needs in [CheckpointNeeds{br:true,avg:true},CheckpointNeeds{br:true,avg:false},CheckpointNeeds{br:false,avg:true}] {
            let paired=s.traverse_checkpoint(0,p,&mut s.root_reaches(),mode,needs,0).unwrap();
            if needs.br { assert_eq!(f32_bits(paired.br.as_ref().unwrap()), f32_bits(&br), "BR seat {p}, mode {mode}"); }
            else { assert!(paired.br.is_none()); }
            if needs.avg { assert_eq!(f32_bits(paired.avg.as_ref().unwrap()), f32_bits(&avg), "AVG seat {p}"); }
            else { assert!(paired.avg.is_none()); }
        }
    }
    }
    let old=reference(s); let new=s.gaps_and_evs();
    assert_eq!(f64_bits(&old.0),f64_bits(&new.0)); assert_eq!(f64_bits(&old.1),f64_bits(&new.1));
    let after=s.arena_snapshot();
    assert_eq!(f32_bits(&before.0),f32_bits(&after.0)); assert_eq!(f32_bits(&before.1),f32_bits(&after.1));
}
fn policy(call: f32, raise: f32) -> BucketPolicy {
    BucketPolicy { call:vec![call;NUM_CLASSES],raise:vec![raise;NUM_CLASSES],jam:vec![0.;NUM_CLASSES],
        raise_size:"max".into(),raise_sizes:vec![],raise_multiples:vec![] }
}
fn profile(adaptive: bool) -> SeatProfile {
    SeatProfile { name:"checkpoint fixture".into(),buckets:vec![Some(policy(0.4,0.2));NUM_BUCKETS],
        vs_raise_bands:None,postflop:None,limp_defense:None,response:adaptive.then(||ProfileResponse {
            contextual_reraise:None,limp_unopened:None,adaptive_from:Some(0.25),source_stats:None,
            cold_reraise:None,limp_contexts:vec![] }) }
}
#[test]
fn paired_checkpoint_matches_full_roots_dense_sparse_and_learning() {
    for threads in [1,4] {
        rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap().install(|| {
            for (n,legacy) in [(2,false),(3,false),(4,true)] {
                let mut s=fixture(n,legacy);
                parity(&s); // pristine uniform strategy
                s.iterate(); parity(&s); // real accumulated state
                for sparse in [false,true] { seed(&mut s,sparse); for prune in [false,true] {s.prune=prune;parity(&s);} }
            }
        });
    }
}
#[test]
fn paired_checkpoint_four_seat_coupled_roots_match() {
    let mut s=fixture(4,false);seed(&mut s,true);s.prune=true;parity(&s);
}
#[test]
fn paired_checkpoint_preserves_profiles_locks_frozen_and_hero() {
    let mut s=fixture(3,true); seed(&mut s,true);
    s.set_table_keep(vec![false,true,false],vec![None,None,None]).unwrap(); parity(&s);
    s.set_hero(Some(0)).unwrap(); parity(&s); s.set_hero(None).unwrap();
    s.set_table_keep(vec![false;3],vec![Some(profile(false)),None,None]).unwrap(); parity(&s);
    s.set_table_keep(vec![false;3],vec![Some(profile(true)),None,None]).unwrap();
    assert!(s.constrained_br(0)); parity(&s);
    // Point-lock precedence at root and below a raise, including mode 3.
    s.lock_point(&[],Some(policy(0.,0.))).unwrap(); parity(&s);
    let raise=s.nodes[0].actions.iter().position(|a|a.kind=="raise").unwrap();
    s.lock_point(&[raise],Some(policy(0.5,0.))).unwrap(); parity(&s);
}
#[test]
fn paired_checkpoint_evaluates_each_shared_terminal_once() {
    rayon::ThreadPoolBuilder::new().num_threads(1).build().unwrap().install(|| {
        let mut s=fixture(3,false);seed(&mut s,false);s.prune=false;
        TRACE.with(|t| *t.borrow_mut()=Some(Trace::default()));
        let old=reference(&s);
        let old_count=TRACE.with(|t|t.borrow_mut().take().unwrap().terminals);
        TRACE.with(|t| *t.borrow_mut()=Some(Trace::default()));
        let new=s.gaps_and_evs();
        let new_count=TRACE.with(|t|t.borrow_mut().take().unwrap().terminals);
        assert!(new_count>0);assert_eq!(old_count,2*new_count);
        assert_eq!(f64_bits(&old.0),f64_bits(&new.0));assert_eq!(f64_bits(&old.1),f64_bits(&new.1));
    });
}
#[test]
fn paired_checkpoint_cancellation_cannot_be_a_completed_check() {
    rayon::ThreadPoolBuilder::new().num_threads(1).build().unwrap().install(|| {
        let mut s=fixture(3,false);seed(&mut s,true);
        let stop=Arc::new(AtomicBool::new(true));s.set_stop_flag(Some(stop.clone()));
        let before=s.arena_snapshot();
        assert!(s.checkpoint_gaps_and_evs().is_none());
        // Public compatibility result is never publishable with stop set.
        let canceled=s.gaps_and_evs();assert_eq!(canceled,(vec![0.;3],vec![0.;3]));
        assert!(stop.load(Ordering::Relaxed));
        stop.store(false,Ordering::Relaxed);
        TRACE.with(|t| *t.borrow_mut()=Some(Trace{cancel_at:Some(8),..Trace::default()}));
        assert!(s.checkpoint_gaps_and_evs().is_none());
        let trace=TRACE.with(|t|t.borrow_mut().take().unwrap());assert!(trace.visits>=8);
        assert!(stop.load(Ordering::Relaxed));
        // This is the server's existing post-check publication predicate:
        // a canceled zero gap must not replace a prior non-converged result.
        let mut published=vec![1.0;3]; let mut converged=false;
        let (gaps,_)=s.gaps_and_evs();
        if !stop.load(Ordering::Relaxed) { converged=gaps.iter().sum::<f64>()<0.01;published=gaps; }
        assert_eq!(published,vec![1.;3]);assert!(!converged);
        let after=s.arena_snapshot();assert_eq!(before,after);
        stop.store(false,Ordering::Relaxed);parity(&s);
    });
}

#[test]
fn paired_checkpoint_sequential_roots_restore_nonunit_reaches() {
    let mut s=fixture(3,false);seed(&mut s,true);
    s.set_table_keep(vec![false,true,false],vec![None,None,None]).unwrap();
    for prune in [false,true] { s.prune=prune;
        for p in 0..s.n { for mode in [2,3] {
            let reaches: Vec<Vec<f32>>=(0..s.n).map(|q|(0..NUM_CLASSES).map(|h|
                if (h+q)%11==0 {0.0} else {class_prob(h)*(1.0+((h+q)%5) as f32)}).collect()).collect();
            let old_br=s.traverse(0,p,&mut reaches.clone(),mode,PAR_DEPTH);
            let old_avg=s.traverse(0,p,&mut reaches.clone(),1,PAR_DEPTH);
            for needs in [CheckpointNeeds{br:true,avg:true},CheckpointNeeds{br:true,avg:false},CheckpointNeeds{br:false,avg:true}] {
                let mut actual_reaches=reaches.clone();
                let got=s.traverse_checkpoint(0,p,&mut actual_reaches,mode,needs,PAR_DEPTH).unwrap();
                if needs.br {assert_eq!(f32_bits(got.br.as_ref().unwrap()),f32_bits(&old_br));}
                if needs.avg {assert_eq!(f32_bits(got.avg.as_ref().unwrap()),f32_bits(&old_avg));}
                for q in 0..s.n {assert_eq!(f32_bits(&actual_reaches[q]),f32_bits(&reaches[q]),"restored seat {q}");}
            }
        }}
    }
}

#[test]
fn paired_checkpoint_parallel_cancellation_is_not_completed() {
    let mut s=fixture(4,true);seed(&mut s,true);
    let stop=Arc::new(AtomicBool::new(false));s.set_stop_flag(Some(stop.clone()));
    let before=s.arena_snapshot();
    // Each worker installs its own deterministic trigger. This covers Option
    // collection unwinding with concurrent branches, without timer races.
    let pool=rayon::ThreadPoolBuilder::new().num_threads(4).start_handler(|_| {
        TRACE.with(|t| *t.borrow_mut()=Some(Trace{cancel_at:Some(8),..Trace::default()}));
    }).build().unwrap();
    let result=pool.install(||s.checkpoint_gaps_and_evs());
    assert!(result.is_none());assert!(stop.load(Ordering::Relaxed));
    drop(pool); // retire all instrumented worker TLS before recovery
    assert_eq!(before,s.arena_snapshot());
    stop.store(false,Ordering::Relaxed);
    rayon::ThreadPoolBuilder::new().num_threads(4).build().unwrap().install(||parity(&s));
}

/// Synthetic allocation stress only, NOT a realistic solve-speed benchmark.
/// Run each mode in a separate process under the existing RSS monitor:
/// PREFLOP_CHECKPOINT_STRESS_MODE=original / paired.
#[test]
#[ignore = "manual CPU checkpoint frontier/RSS stress; no learning or GPU"]
fn paired_checkpoint_all_fold_frontier_stress() {
    let mode=std::env::var("PREFLOP_CHECKPOINT_STRESS_MODE").expect("original or paired");
    assert!(mode=="original" || mode=="paired");
    let threads: usize=std::env::var("PREFLOP_CHECKPOINT_STRESS_THREADS").unwrap_or("4".into()).parse().unwrap();
    let mut chosen=None;
    // Size enumeration allocates no solver arenas. Same deterministic first
    // matching fixture in both processes; record config/count in output.
    'search: for max_raises in [2,3] { for opens in [1usize,2,3,4] { for reraises in [1usize,2,3] {
        let cfg: PreflopConfig=serde_json::from_value(serde_json::json!({
            "positions":["UTG","HJ","CO","BTN","SB","BB"],"posts":[0.,0.,0.,0.,0.5,1.],
            "stack":100.,"limp":true,"open_raises":&[2.,2.5,3.,4.][..opens],
            "raise_mults":&[2.5,3.,4.][..reraises],"max_raises":max_raises,
            "add_allin":false,"rake_pct":5.,"rake_cap":2.,"realization":"raw"
        })).unwrap();
        let estimate=estimate_tree(&cfg).unwrap();
        if !estimate.truncated && (100_000..=250_000).contains(&estimate.nodes) {
            chosen=Some((cfg,estimate));break 'search;
        }
    }}}
    let (cfg,estimate)=chosen.expect("bounded six-seat fixture in 100k..250k node range");
    let mut s=PreflopSolver::new(cfg,table()).unwrap();
    // Explicitly zero all non-fold/check actions. Keep pruning OFF so the
    // complete frontier is traversed, including own off-path BR actions.
    let sums=unsafe{s.strat_sum.slice_mut()};sums.fill(0.0);
    for nd in s.nodes.iter().filter(|n|n.kind==KIND_ACTION) {
        let chosen=nd.actions.iter().position(|a|a.kind=="fold")
            .or_else(||nd.actions.iter().position(|a|a.kind=="check")).unwrap_or(0);
        sums[nd.data_off+chosen*NUM_CLASSES..nd.data_off+(chosen+1)*NUM_CLASSES].fill(1.0);
    }
    s.iteration=1;s.prune=false;
    // No arena snapshots: they would inflate/obscure the measured RSS peak.
    let fingerprint=|s:&PreflopSolver|unsafe{
        [s.regrets.slice(),s.strat_sum.slice()].into_iter().map(|a|a.iter().fold(0xcbf29ce484222325u64,
            |acc,x|acc.wrapping_mul(0x100000001b3) ^ x.to_bits() as u64)).collect::<Vec<_>>()
    };
    let before=fingerprint(&s);
    let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
    let start=std::time::Instant::now();
    // Match production's outer per-seat parallelism in BOTH paths. reference()
    // is deliberately serial outside seats, so it is not used for RSS control.
    let result=pool.install(||if mode=="paired" {s.gaps_and_evs()} else {
        (0..s.n).into_par_iter().map(|p|{
            let br=s.traverse(0,p,&mut s.root_reaches(),2,0);
            let avg=s.traverse(0,p,&mut s.root_reaches(),1,0);
            let (mut g,mut ev)=(0f64,0f64);
            for h in 0..NUM_CLASSES {let w=class_prob(h) as f64;g+=w*(br[h]-avg[h]) as f64;ev+=w*avg[h] as f64;}
            (g,ev)
        }).collect::<Vec<_>>().into_iter().unzip()
    });
    let elapsed=start.elapsed().as_secs_f64();assert_eq!(before,fingerprint(&s));
    println!("CHECKPOINT_FRONTIER {}",serde_json::json!({"synthetic":"all-fold/check, prune=false",
        "mode":mode,"threads":threads,"nodes":estimate.nodes,"action_nodes":estimate.action_nodes,
        "arena_bytes":estimate.arena_len*8,"config":s.cfg,"elapsed_seconds":elapsed,
        "gap_bits":f64_bits(&result.0),"ev_bits":f64_bits(&result.1),"arena_fingerprint":before}));
}
