//! "Trust the read" in Preflop Lab hero mode on the GPU: device passes and
//! evaluation must match the CPU engine (preflop/rnr.rs), including side
//! pots and ICM games. Needs a CUDA machine:
//!
//!     cargo test --release --features gpu --test preflop_gpu_rnr -- --test-threads=1
#![cfg(feature = "gpu")]

use solver::preflop::equity::EquityTable;
use solver::preflop::gpu::PreflopGpu;
use solver::preflop::{archetypes, IcmConfig, PreflopConfig, PreflopSolver};
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(4000))).clone()
}

/// 3-handed 20bb: BTN opens 2.5 or jams, one re-raise level.
fn base() -> PreflopConfig {
    serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 20.0,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2, "add_allin": true,
        "limp": false, "realization": "raw"
    }))
    .unwrap()
}

fn side_pots() -> PreflopConfig {
    let mut c = base();
    c.stacks = Some(vec![20.0, 6.0, 14.0]);
    c
}

fn icm() -> PreflopConfig {
    let mut c = side_pots();
    c.icm = Some(IcmConfig { payouts: vec![50.0, 30.0, 20.0], field: vec![], field_groups: vec![], stack_off: 1.0 });
    c
}

/// Solved table, SB a maniac and BB a calling station, BTN hero, dial at `t`.
fn hero_vs(cfg: PreflopConfig, t: f32) -> PreflopSolver {
    let mut s = PreflopSolver::new(cfg, table()).unwrap();
    s.prune = false;
    for _ in 0..150 {
        s.iterate();
    }
    let mut profiles = vec![None; 3];
    for (seat, name) in [(1, "Maniac"), (2, "Calling station")] {
        let stats = archetypes().into_iter().find(|(n, _)| *n == name).unwrap().1;
        profiles[seat] = Some(s.generate_profile(seat, &stats, name).unwrap().0);
    }
    s.set_table(vec![false; 3], profiles).unwrap();
    for _ in 0..150 {
        s.iterate();
    }
    s.set_hero(Some(0)).unwrap();
    s.set_trust(Some(t)).unwrap();
    s
}

fn worst(a: &[f32], b: &[f32]) -> f32 {
    a.iter().zip(b).fold(0f32, |w, (x, y)| w.max((x - y).abs()))
}

fn run_equivalence(cfg: PreflopConfig, label: &str) {
    let mut cpu = hero_vs(cfg.clone(), 0.6);
    let mut gs = hero_vs(cfg, 0.6);
    let mut g = PreflopGpu::new(&gs, 8_000).expect("gpu init");
    for _ in 0..5 {
        cpu.iterate();
        g.iterate(&mut gs).unwrap();
    }
    g.sync_to_cpu(&mut gs).unwrap();
    let (cr, cs) = cpu.arena_snapshot();
    let (gr, gss) = gs.arena_snapshot();
    let (wr, ws) = (worst(&cr, &gr), worst(&cs, &gss));
    assert!(wr < 1e-3 && ws < 1e-3, "{label}: main arenas diverge: regrets {wr}, sums {ws}");
    let ruled: Vec<usize> = (0..cpu.nodes.len()).filter(|&i| cpu.nodes[i].kind == 0 && cpu.nodes[i].actor != 0).collect();
    let mut wf = 0f32;
    for &i in &ruled {
        wf = wf.max(worst(&cpu.free_strategy(i).unwrap(), &gs.free_strategy(i).unwrap()));
    }
    assert!(wf < 1e-3, "{label}: free types diverge by {wf}");
    for _ in 0..200 {
        cpu.iterate();
        g.iterate(&mut gs).unwrap();
    }
    g.sync_to_cpu(&mut gs).unwrap();
    let (gc, ec) = cpu.gaps_and_evs();
    let (gd, ed) = g.gaps_and_evs().unwrap();
    let (gh, eh) = gs.gaps_and_evs();
    for q in 0..3 {
        assert!((gc[q] - gd[q]).abs() < 0.02, "{label}: seat {q} gap cpu {} vs device {}", gc[q], gd[q]);
        assert!((ec[q] - ed[q]).abs() < 0.02, "{label}: seat {q} EV cpu {} vs device {}", ec[q], ed[q]);
        assert!((gh[q] - gd[q]).abs() < 1e-3 && (eh[q] - ed[q]).abs() < 1e-3,
            "{label}: device evaluation disagrees with its own synced arenas at seat {q}");
    }
    let rc = cpu.trust_readout().unwrap();
    let rd = g.trust_readout().expect("dial on the device").unwrap();
    let rh = gs.trust_readout().unwrap();
    for (a, b, c, what) in [
        (rc.hero_ev_vs_read, rd.hero_ev_vs_read, rh.hero_ev_vs_read, "read"),
        (rc.hero_ev_vs_mixture, rd.hero_ev_vs_mixture, rh.hero_ev_vs_mixture, "mixture"),
        (rc.hero_ev_vs_adapting, rd.hero_ev_vs_adapting, rh.hero_ev_vs_adapting, "adapting"),
    ] {
        assert!((a - b).abs() < 0.02, "{label}: hero EV vs {what}: cpu {a} vs device {b}");
        assert!((c - b).abs() < 1e-3, "{label}: device readout vs its synced arenas ({what}): {c} vs {b}");
    }
    assert_eq!(rd.seats, vec![1, 2]);
    println!("{label}: cpu {rc:?}\n{label}: gpu {rd:?}");
}

#[test]
fn gpu_trust_dial_matches_cpu() {
    run_equivalence(base(), "chip EV");
}

#[test]
fn gpu_trust_dial_matches_cpu_with_side_pots() {
    let s = PreflopSolver::new(side_pots(), table()).unwrap();
    assert!(s.nodes.iter().any(|n| !n.side_pots.is_empty()));
    run_equivalence(side_pots(), "side pots");
}

#[test]
fn gpu_trust_dial_matches_cpu_in_icm_games() {
    run_equivalence(icm(), "ICM");
}

#[test]
fn gpu_trust_dial_takes_the_normal_plan_and_full_trust_anchors() {
    let gs = hero_vs(base(), 1.0);
    let (mut g, selection) = PreflopGpu::new_throughput(&gs, 8_000).unwrap();
    assert_eq!(selection.mode, "normal_gpu");
    assert_eq!(selection.fallback_reason.as_deref(), Some("the trust dial uses the normal GPU plan"));
    let mut it = gs.iteration;
    for _ in 0..100 {
        g.try_iterate_counter(&mut it, None).unwrap();
    }
    let r = g.trust_readout().unwrap().unwrap();
    assert!((r.hero_ev_vs_read - r.hero_ev_vs_mixture).abs() < 1e-6, "{r:?}");
    assert!(r.hero_ev_vs_adapting < r.hero_ev_vs_read, "{r:?}");
    // no dial: no readout, plain hero mode
    let mut plain = hero_vs(base(), 1.0);
    plain.set_trust(None).unwrap();
    let mut g = PreflopGpu::new(&plain, 8_000).unwrap();
    assert!(g.trust_readout().is_none());
}
