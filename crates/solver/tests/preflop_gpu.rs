//! GPU-vs-CPU equivalence for the preflop engine. These tests need a CUDA
//! machine (RTX 3090 etc.) — run there before trusting GPU output:
//!
//!     cargo test --release --features gpu --test preflop_gpu -- --test-threads=1
//!
//! The GPU engine was written to mirror the CPU traversal exactly; any
//! disagreement beyond float-order noise is a GPU bug.
#![cfg(feature = "gpu")]

use solver::preflop::equity::{class_index, EquityTable, NUM_CLASSES};
use solver::preflop::gpu::PreflopGpu;
use solver::preflop::{
    BucketPolicy, PreflopConfig, PreflopSolver, SeatProfile, BUCKET_VS_RAISE, NUM_BUCKETS,
};
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(4000))).clone()
}

// Historical trajectory/anchor fixtures keep the payoff model they originally
// validated. Dedicated coupled tests below exercise the new default separately.
fn legacy_solver(cfg: PreflopConfig, eq: Arc<EquityTable>) -> Result<PreflopSolver, String> {
    let mut s = PreflopSolver::new(cfg, eq)?;
    s.set_multiway_equity_model("legacy_product")?;
    Ok(s)
}

#[test]
fn gpu_matches_cpu_coupled_three_way() {
    let mut cfg = hu25();
    cfg.positions = vec!["BTN".into(), "SB".into(), "BB".into()];
    cfg.posts = vec![0.0, 0.5, 1.0];
    cfg.stack = 5.0;
    cfg.open_raises = vec![2.0];
    cfg.max_raises = 1;
    cfg.add_allin = false;
    cfg.realization = "raw".into();
    let mut cpu = PreflopSolver::new(cfg.clone(), table()).unwrap();
    let mut gs = PreflopSolver::new(cfg, table()).unwrap();
    cpu.prune = false;
    gs.prune = false;
    assert_eq!(cpu.multiway_equity_model(), solver::preflop::multiway::MODEL);
    run_equivalence(cpu, gs);
}

#[test]
fn gpu_matches_cpu_preview64_three_way() {
    let mut cfg = hu25();
    cfg.positions = vec!["BTN".into(), "SB".into(), "BB".into()];
    cfg.posts = vec![0.0, 0.5, 1.0];
    cfg.stack = 5.0;
    cfg.open_raises = vec![2.0];
    cfg.max_raises = 1;
    cfg.add_allin = false;
    cfg.realization = "raw".into();
    let mut cpu = PreflopSolver::new(cfg.clone(), table()).unwrap();
    let mut gs = PreflopSolver::new(cfg, table()).unwrap();
    for s in [&mut cpu, &mut gs] {
        s.set_multiway_equity_model("coupled_preview64_v1").unwrap();
        s.prune = false;
    }
    run_equivalence(cpu, gs);
}
fn hu25() -> PreflopConfig {
    PreflopConfig {
        positions: vec!["SB".into(), "BB".into()],
        stack: 25.0,
        posts: vec![0.5, 1.0],
        ante: 0.0,
        limp: true,
        open_raises: vec![2.0, 2.5],
        raise_mults: vec![3.0],
        max_raises: 3,
        add_allin: true,
        allin_threshold: 0.85,
        rake_pct: 5.0,
        rake_cap: 1.0,
        no_flop_no_drop: true,
        realization: "static".into(),
        call_only_seats: vec![],
        open_raises_by_seat: None,
        raise_mults_by_seat: None,
    }
}

/// Same game, same iteration count, CPU vs GPU: every action node's average
/// strategy must agree wherever the answer is DECISIVE, and the BR gaps
/// must match. (Trajectory-exact equality is impossible between two f32
/// implementations with different summation orders: near-zero regret
/// crossings flip differently and mixing-region frequencies fork while
/// both remain equally converged — verified 2026-07-07 on an RTX 4090:
/// per-iteration arena diffs stay at float noise (<1e-4) for the first
/// iterations, then knife-edge classes drift apart.)
#[test]
fn gpu_matches_cpu() {
    assert_gpu_matches_cpu(hu25());
}

/// Same equivalence under the CALIBRATED realization model: the kernel's
/// per-class R (gross pot, measured class base x positional weight, clipped)
/// must reproduce terminal_value()'s calibrated branch.
#[test]
fn gpu_matches_cpu_calibrated() {
    let mut cfg = hu25();
    cfg.realization = "calibrated".into();
    let probe = legacy_solver(cfg.clone(), table()).unwrap();
    assert!(
        probe.fit.is_some(),
        "calibrated fit must load for this test to mean anything: {}",
        probe.realization_note
    );
    assert_gpu_matches_cpu(cfg);
}

fn assert_gpu_matches_cpu(cfg: PreflopConfig) {
    let eq = table();
    let mut cpu = legacy_solver(cfg.clone(), eq.clone()).unwrap();
    let mut gs = legacy_solver(cfg, eq).unwrap();
    cpu.prune = false;
    gs.prune = false;
    run_equivalence(cpu, gs);
}

fn flat_policy(call: f32, raise: f32) -> BucketPolicy {
    BucketPolicy { raise_multiples: Vec::new(), raise_sizes: Vec::new(),
        call: vec![call; NUM_CLASSES],
        raise: vec![raise; NUM_CLASSES],
        jam: vec![0.0; NUM_CLASSES],
        raise_size: "max".into(),
    }
}

#[test]
fn gpu_matches_cpu_with_limper_count_policies() {
    use solver::preflop::{archetypes, LimpContextPolicy, ProfileResponse};
    let mut cfg=hu25();cfg.positions=vec!["BTN".into(),"SB".into(),"BB".into()];
    cfg.posts=vec![0.0,0.5,1.0];cfg.open_raises=vec![2.5];cfg.max_raises=2;
    let mut cpu=PreflopSolver::new(cfg.clone(),table()).unwrap();
    let mut gs=PreflopSolver::new(cfg,table()).unwrap();
    for s in [&mut cpu,&mut gs] {
        assert_eq!(s.multiway_equity_model(), "coupled_deck_v1");
        s.prune=false;s.iterate();
        let mut p=s.generate_profile(2,&archetypes()[3].1,"limp responses").unwrap().0;
        p.response=Some(ProfileResponse {limp_contexts:(1..=3).map(|limpers|LimpContextPolicy {
            limpers,free_check:true,policy:flat_policy(1.0-limpers as f32*0.2,limpers as f32*0.2)
        }).collect(),..Default::default()});
        s.set_table(vec![false;3],vec![None,None,Some(p)]).unwrap();
    }
    run_equivalence(cpu,gs);
}

#[test]
fn gpu_matches_cpu_with_contextual_reraise_profiles() {
    use solver::preflop::{archetypes, contextual, ProfileResponse};
    let mut cfg=hu25();cfg.positions=vec!["BTN".into(),"SB".into(),"BB".into()];
    cfg.posts=vec![0.0,0.5,1.0];cfg.stack=100.0;cfg.open_raises=vec![2.5];cfg.max_raises=3;
    let mut cpu=legacy_solver(cfg.clone(),table()).unwrap();
    let mut gs=legacy_solver(cfg,table()).unwrap();
    for s in [&mut cpu,&mut gs] {
        s.prune=false;s.iterate();
        let mut p=s.generate_profile(1,&archetypes()[3].1,"contextual responses").unwrap().0;
        p.response=Some(ProfileResponse {contextual_reraise:Some(contextual::MODEL_ID.into()),adaptive_from:Some(0.25),..Default::default()});
        s.set_table(vec![false;3],vec![None,Some(p.clone()),Some(p)]).unwrap();
        assert!(s.nodes.iter().enumerate().any(|(i,_)|s.contextual_status(i).is_some_and(|v|v.active)));
    }
    run_equivalence(cpu,gs);
}

/// Seat modes and locks (item P5): a profile-ruled bucket plus a point lock
/// at the root. Both solvers get the same 40 CPU iterations first (the lock
/// pins the root to its current average), then the overrides, then the
/// equivalence run.
#[test]
fn gpu_matches_cpu_with_profile_and_lock() {
    let eq = table();
    let mut cpu = legacy_solver(hu25(), eq.clone()).unwrap();
    let mut gs = legacy_solver(hu25(), eq).unwrap();
    for s in [&mut cpu, &mut gs] {
        s.prune = false;
        for _ in 0..40 {
            s.iterate();
        }
        s.lock_point(&[], None).unwrap();
        let mut buckets: Vec<Option<BucketPolicy>> = vec![None; NUM_BUCKETS];
        buckets[BUCKET_VS_RAISE as usize] = Some(flat_policy(0.5, 0.1));
        let station = SeatProfile {
            name: "station".into(),
            buckets,
            vs_raise_bands: None,
            postflop: None,
            limp_defense: None,
            response: None,
        };
        s.set_table(vec![false, false], vec![None, Some(station)]).unwrap();
    }
    assert!(cpu.has_overrides());
    run_equivalence(cpu, gs);
}

/// Frozen seat + hero mode: BB pinned to its solved average, SB re-solving
/// as the hero (max-exploit). The frozen seat's strategy sums must not
/// decay on the device either.
#[test]
fn gpu_matches_cpu_frozen_hero() {
    let eq = table();
    let mut cpu = legacy_solver(hu25(), eq.clone()).unwrap();
    let mut gs = legacy_solver(hu25(), eq).unwrap();
    for s in [&mut cpu, &mut gs] {
        s.prune = false;
        for _ in 0..40 {
            s.iterate();
        }
        s.set_table(vec![false, true], vec![None, None]).unwrap();
        s.set_hero(Some(0)).unwrap();
    }
    assert!(cpu.seat_frozen[1] && cpu.has_overrides());
    run_equivalence(cpu, gs);
}

fn run_equivalence(mut cpu: PreflopSolver, mut gs: PreflopSolver) {
    let mut g = PreflopGpu::new(&gs, 8_000).expect("gpu init");

    // Short horizon: per-iteration math must mirror to float noise before
    // chaos has room to amplify.
    for _ in 0..5 {
        cpu.iterate();
        g.iterate(&mut gs).unwrap();
    }
    g.sync_to_cpu(&mut gs).unwrap();
    let (cr, _) = cpu.arena_snapshot();
    let (gr, _) = gs.arena_snapshot();
    let mut worst_r = 0f32;
    for (x, y) in cr.iter().zip(gr.iter()) {
        worst_r = worst_r.max((x - y).abs());
    }
    assert!(
        worst_r < 1e-3,
        "per-iteration regret math diverges beyond float noise: {worst_r}"
    );

    // Long horizon: both must CONVERGE to the same answer — identical pure
    // decisions, matching gaps — even though mixing frequencies may fork.
    for _ in 0..295 {
        cpu.iterate();
    }
    for _ in 0..295 {
        g.iterate(&mut gs).unwrap();
    }
    g.sync_to_cpu(&mut gs).unwrap();
    assert_eq!(cpu.iteration, gs.iteration);

    let (mut decisive, mut clash) = (0u32, 0u32);
    for i in 0..cpu.nodes.len() {
        if cpu.nodes[i].kind != 0 {
            continue;
        }
        let a = cpu.average_strategy(i);
        let b = gs.average_strategy(i);
        for (x, y) in a.iter().zip(b.iter()) {
            if *x > 0.9 || *x < 0.1 {
                decisive += 1;
                if (x - y).abs() > 0.1 {
                    clash += 1;
                }
            }
        }
    }
    assert!(decisive > 1000, "sanity: expected many decisive entries, got {decisive}");
    assert!(
        (clash as f64) < decisive as f64 * 0.002,
        "pure decisions disagree: {clash} of {decisive} decisive entries"
    );

    let gc: f64 = cpu.br_gaps().iter().sum();
    let gg: f64 = gs.br_gaps().iter().sum();
    assert!(
        (gc - gg).abs() < 0.02,
        "BR gap mismatch: cpu {gc} vs gpu-synced {gg}"
    );

    // the device's own gap computation must agree with the CPU's on the
    // synced arenas
    let (gaps_dev, _evs) = g.gaps_and_evs().unwrap();
    let gd: f64 = gaps_dev.iter().sum();
    assert!(
        (gd - gg).abs() < 0.02,
        "device gap computation disagrees: {gd} vs {gg}"
    );
}

/// The 10bb push/fold anchors must hold when solved entirely on the GPU.
#[test]
fn gpu_push_fold_anchors() {
    let eq = table();
    let cfg = PreflopConfig {
        positions: vec!["SB".into(), "BB".into()],
        stack: 10.0,
        posts: vec![0.5, 1.0],
        ante: 0.0,
        limp: false,
        open_raises: vec![],
        raise_mults: vec![],
        max_raises: 1,
        add_allin: true,
        allin_threshold: 0.85,
        rake_pct: 0.0,
        rake_cap: 0.0,
        no_flop_no_drop: true,
        realization: "raw".into(),
        call_only_seats: vec![],
        open_raises_by_seat: None,
        raise_mults_by_seat: None,
    };
    let mut s = legacy_solver(cfg, eq).unwrap();
    let mut g = PreflopGpu::new(&s, 8_000).expect("gpu init");
    for _ in 0..800 {
        g.iterate(&mut s).unwrap();
    }
    g.sync_to_cpu(&mut s).unwrap();

    let sb = s.average_strategy(0);
    let jam = s.nodes[0].actions.iter().position(|a| a.kind == "jam").unwrap();
    let bb_idx = s.child(0, jam);
    let bb = s.average_strategy(bb_idx);
    let call = s.nodes[bb_idx].actions.iter().position(|a| a.kind == "call").unwrap();
    let aa = class_index(12, 12, false);
    let seven_deuce = class_index(5, 0, false);
    assert!(sb[jam * NUM_CLASSES + aa] > 0.99, "AA must jam");
    assert!(bb[call * NUM_CLASSES + aa] > 0.99, "AA must call");
    assert!(bb[call * NUM_CLASSES + seven_deuce] < 0.05, "72o must fold");
    let gap: f64 = s.br_gaps().iter().sum();
    assert!(gap < 0.02, "GPU solve should converge: gap {gap} bb");
}


#[test]
fn gpu_matches_cpu_with_adaptive_large_bet_responses() {
    use solver::preflop::ProfileResponse;
    let mut cpu = legacy_solver(hu25(), table()).unwrap();
    let mut gs = legacy_solver(hu25(), table()).unwrap();
    for s in [&mut cpu, &mut gs] {
        s.prune = false;
        let p = SeatProfile {
            name: "adaptive station".into(), buckets: vec![Some(flat_policy(0.65, 0.1)); NUM_BUCKETS],
            vs_raise_bands: None, postflop: None, limp_defense: Some(flat_policy(0.7, 0.0)),
            response: Some(ProfileResponse { contextual_reraise: None, limp_unopened: Some(flat_policy(0.6, 0.0)), adaptive_from: Some(0.25), source_stats: None, cold_reraise: None, limp_contexts: vec![] }),
        };
        s.set_table(vec![false; 2], vec![None, Some(p)]).unwrap();
    }
    run_equivalence(cpu, gs);
}


#[test]
fn gpu_matches_cpu_equal_blinds() {
    let mut cfg = hu25(); cfg.posts = vec![1.0, 1.0];
    cfg.realization = "calibrated".into();
    assert_gpu_matches_cpu(cfg);
}

#[test]
fn gpu_matches_cpu_with_distinct_cold_reraise_policy() {
    use solver::preflop::ProfileResponse;
    let mut cfg=hu25();cfg.positions=vec!["BTN".into(),"SB".into(),"BB".into()];cfg.posts=vec![0.0,0.5,1.0];
    cfg.open_raises=vec![2.0];cfg.max_raises=2;
    let mut cpu=legacy_solver(cfg.clone(),table()).unwrap();
    let mut gs=legacy_solver(cfg,table()).unwrap();
    for s in [&mut cpu,&mut gs] {
        s.prune=false;
        let p=SeatProfile{name:"measured responses".into(),buckets:vec![Some(flat_policy(0.3,0.2));NUM_BUCKETS],
            vs_raise_bands:Some(vec![(2.5,flat_policy(0.6,0.1)),(999.0,flat_policy(0.2,0.05))]),
            postflop:None,limp_defense:None,
            response:Some(ProfileResponse{cold_reraise:Some(flat_policy(0.07,0.11)),..Default::default()})};
        s.set_table(vec![false;3],vec![None,None,Some(p)]).unwrap();
    }
    run_equivalence(cpu,gs);
}

#[test]
fn gpu_matches_cpu_with_observed_open_size_distribution() {
    let mut cpu=legacy_solver(hu25(),table()).unwrap();
    let mut gs=legacy_solver(hu25(),table()).unwrap();
    for s in [&mut cpu,&mut gs] {
        s.prune=false;s.iterate();
        let mut pol=flat_policy(0.2,0.5);pol.raise_sizes=vec![(2.0,0.4),(2.5,0.6)];
        let mut buckets=vec![None;NUM_BUCKETS];buckets[0]=Some(pol);
        let profile=SeatProfile{name:"opening size mixture".into(),buckets,vs_raise_bands:None,postflop:None,limp_defense:None,response:None};
        s.set_table(vec![false;2],vec![Some(profile),None]).unwrap();
    }
    run_equivalence(cpu,gs);
}

#[test]
fn gpu_matches_cpu_with_observed_iso_3bet_and_squeeze_sizes() {
    use solver::preflop::{LimpContextPolicy,ProfileResponse,BUCKET_VS_LIMPS,BUCKET_SQUEEZE};
    for (bucket,seat,path,sb) in [
        (BUCKET_VS_LIMPS,1,vec!["call"],0.5),
        (BUCKET_VS_RAISE,1,vec!["raise"],1.0),
        (BUCKET_SQUEEZE,2,vec!["raise","call"],0.5),
    ] {
        let mut cfg=hu25();cfg.positions=vec!["BTN".into(),"SB".into(),"BB".into()];
        cfg.posts=vec![0.0,sb,1.0];cfg.stack=30.0;cfg.ante=0.1;
        cfg.open_raises=vec![2.0,4.0,6.0];cfg.raise_mults=vec![3.0,4.0];cfg.max_raises=2;
        let mut cpu=legacy_solver(cfg.clone(),table()).unwrap();
        let mut gs=legacy_solver(cfg,table()).unwrap();
        for s in [&mut cpu,&mut gs] {
            s.prune=false;
            let mut pol=flat_policy(0.2,0.6);
            if bucket==BUCKET_VS_LIMPS {pol.raise_sizes=vec![(4.0,0.4),(6.0,0.6)];}
            else {pol.raise_multiples=vec![(3.0,0.4),(4.0,0.6)];}
            let mut buckets=vec![None;NUM_BUCKETS];buckets[bucket as usize]=Some(pol.clone());
            let profile=SeatProfile{name:"ordinary raise mixture".into(),buckets,
                vs_raise_bands:if bucket==BUCKET_VS_RAISE {Some(vec![(999.0,pol.clone())])}else{None},
                postflop:None,limp_defense:None,
                response:if bucket==BUCKET_VS_LIMPS {Some(ProfileResponse{
                    limp_contexts:vec![LimpContextPolicy{limpers:1,free_check:sb==1.0,policy:pol}],..Default::default()})}else{None}};
            let mut profiles=vec![None;3];profiles[seat]=Some(profile);
            s.set_table(vec![false;3],profiles).unwrap();
            let mut n=0;
            for kind in &path {let a=s.nodes[n].actions.iter().position(|a|a.kind==*kind).unwrap();n=s.child(n,a);}
            assert_eq!(s.nodes[n].bucket,bucket);
            let sigma=s.average_strategy(n);
            for (size,expected) in if bucket==BUCKET_VS_LIMPS {[(4.0,0.24),(6.0,0.36)]}else{[(6.0,0.24),(8.0,0.36)]} {
                let a=s.nodes[n].actions.iter().position(|a|a.kind=="raise" && a.to==size).unwrap();
                for h in 0..169 {assert!((sigma[a*169+h]-expected).abs()<1e-6);}
            }
        }
        // This fixture tests the uploaded size mixtures. Check each early
        // iteration's full arenas before floating regret crossings can fork
        // this multi-player game's long-horizon mixed strategy. Existing
        // long-horizon convergence/equivalence fixtures remain unchanged.
        let mut g=PreflopGpu::new(&gs,8_000).unwrap();
        for _ in 0..5 {
            cpu.iterate();g.iterate(&mut gs).unwrap();g.sync_to_cpu(&mut gs).unwrap();
            let (cr,cs)=cpu.arena_snapshot();let (gr,gsums)=gs.arena_snapshot();
            for (name,a,b) in [("regret",&cr,&gr),("strategy sum",&cs,&gsums)] {
                let worst=a.iter().zip(b).map(|(x,y)|(x-y).abs()).fold(0.0f32,f32::max);
                assert!(worst<1e-3,"size-mixture {name} mismatch: {worst}");
            }
            for (n,nd) in cpu.nodes.iter().enumerate() {
                if nd.kind==0 && nd.actor as usize==seat && nd.bucket==bucket {
                    assert_eq!(cpu.average_strategy(n),gs.average_strategy(n));
                }
            }
        }
        for _ in 0..295 {cpu.iterate();g.iterate(&mut gs).unwrap();}
        g.sync_to_cpu(&mut gs).unwrap();
        let (cpu_gaps,cpu_evs)=cpu.gaps_and_evs();let (synced_gaps,synced_evs)=gs.gaps_and_evs();
        let (device_gaps,device_evs)=g.gaps_and_evs().unwrap();
        let delta=|a:&[f64],b:&[f64]|a.iter().zip(b).map(|(x,y)|(x-y).abs()).fold(0.0f64,f64::max);
        eprintln!("sizing bucket {bucket}: 300-iteration max CPU/GPU gap delta {:.8}, EV delta {:.8}; device gap {:.8}, EV {:.8} bb",delta(&cpu_gaps,&synced_gaps),delta(&cpu_evs,&synced_evs),delta(&device_gaps,&synced_gaps),delta(&device_evs,&synced_evs));
        assert!((cpu_gaps.iter().sum::<f64>()-synced_gaps.iter().sum::<f64>()).abs()<0.02);
        assert!((device_gaps.iter().sum::<f64>()-synced_gaps.iter().sum::<f64>()).abs()<0.02);
        for seat in 0..cpu_gaps.len() {
            assert!((cpu_gaps[seat]-synced_gaps[seat]).abs()<0.02);
            assert!((device_gaps[seat]-synced_gaps[seat]).abs()<0.02);
            assert!((cpu_evs[seat]-synced_evs[seat]).abs()<0.02);
            assert!((device_evs[seat]-synced_evs[seat]).abs()<0.02);
        }
    }
}
