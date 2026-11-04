//! Per-seat stacks: tree rules (all-in for less, raise caps, incomplete
//! all-ins), uncalled returns, side-pot layering and side-pot payoffs.

use super::equity::{class_index, class_prob, EquityTable, NUM_CLASSES};
use super::*;
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(200))).clone()
}

fn cfg(json: serde_json::Value) -> PreflopConfig {
    serde_json::from_value(json).unwrap()
}

fn three(stacks: [f64; 3], opens: &[f64]) -> PreflopConfig {
    cfg(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
        "stack": stacks.iter().cloned().fold(0.0, f64::max), "stacks": stacks,
        "open_raises": opens, "raise_mults": [3.0], "max_raises": 3,
        "add_allin": true, "realization": "raw"
    }))
}

/// The child reached by the action whose label starts with `label`.
fn step(s: &PreflopSolver, node: usize, label: &str) -> usize {
    let nd = &s.nodes[node];
    let a = nd.actions.iter().position(|a| a.label.starts_with(label)).unwrap_or_else(|| {
        panic!("no {label:?} among {:?}", nd.actions.iter().map(|a| &a.label).collect::<Vec<_>>())
    });
    s.child(node, a)
}

fn labels(s: &PreflopSolver, node: usize) -> Vec<String> {
    s.nodes[node].actions.iter().map(|a| a.label.clone()).collect()
}

fn walk(s: &PreflopSolver, path: &[&str]) -> usize {
    path.iter().fold(0, |node, label| step(s, node, label))
}

#[test]
fn equal_stack_vector_is_the_single_stack_game() {
    let single = cfg(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0], "stack": 15.0,
        "ante": 0.1, "limp": true, "open_raises": [2.0, 2.5], "raise_mults": [2.5], "max_raises": 3,
        "add_allin": true, "realization": "static", "rake_pct": 5.0, "rake_cap": 2.0, "no_flop_no_drop": false
    }));
    let mut vector = single.clone();
    vector.stacks = Some(vec![15.0; 4]);
    let mut a = PreflopSolver::new(single, table()).unwrap();
    let mut b = PreflopSolver::new(vector, table()).unwrap();
    assert_eq!(a.nodes.len(), b.nodes.len());
    assert!(b.nodes.iter().all(|nd| nd.side_pots.is_empty()));
    a.prune = false;
    b.prune = false;
    for _ in 0..4 {
        a.iterate();
        b.iterate();
    }
    let (ra, sa) = a.arena_snapshot();
    let (rb, sb) = b.arena_snapshot();
    assert!(ra.iter().zip(&rb).all(|(x, y)| x.to_bits() == y.to_bits()));
    assert!(sa.iter().zip(&sb).all(|(x, y)| x.to_bits() == y.to_bits()));
}

#[test]
fn validation_checks_each_seat() {
    let mut c = three([20.0, 10.0, 30.0], &[2.5]);
    c.stacks = Some(vec![20.0, 10.0]);
    assert!(validate(&c).unwrap_err().contains("one entry per seat"));
    c.stacks = Some(vec![20.0, 0.5, 30.0]);
    assert!(validate(&c).unwrap_err().contains("must exceed its 0.5 bb post"));
    c.stacks = Some(vec![20.0, f64::NAN, 30.0]);
    assert!(validate(&c).unwrap_err().contains("finite"));
    // An open bigger than a short seat's stack is that seat's jam, not an error.
    c.stacks = Some(vec![2.0, 10.0, 30.0]);
    assert!(validate(&c).is_ok());
    let s = PreflopSolver::new(c, table()).unwrap();
    assert_eq!(labels(&s, 0), ["Fold", "All-in 2"]);
}

#[test]
fn jams_are_capped_by_own_stack_and_by_the_deepest_caller() {
    // BTN covers everyone: its jam only needs to cover the deepest other seat.
    let s = PreflopSolver::new(three([100.0, 10.0, 20.0], &[2.5]), table()).unwrap();
    assert_eq!(labels(&s, 0), ["Fold", "Raise 2.5", "All-in 20"]);
    // SB is short: it can only jam its own 10, and BB may call but not raise
    // behind it once BTN folded (nobody left who could call a raise).
    let sb_jam = walk(&s, &["Fold", "All-in 10"]);
    assert_eq!(labels(&s, sb_jam), ["Fold", "Call 10"]);
    // Facing BTN's 20 bb jam, SB calls all-in for less.
    let facing = walk(&s, &["All-in 20"]);
    assert_eq!(labels(&s, facing), ["Fold", "Call all-in 10"]);
    // BB can still put BTN all-in... BTN is not all-in (it has 80 behind),
    // but BB's call of 20 is its whole stack, so no raise is possible.
    let bb = walk(&s, &["All-in 20", "Call all-in 10"]);
    assert_eq!(labels(&s, bb), ["Fold", "Call 20"]);
}

#[test]
fn incomplete_all_in_does_not_reopen_raising() {
    // BTN opens 2.5 (a 1.5 bb raise), SB calls, BB shoves 3.5: a 1 bb raise,
    // less than a full one. BTN and SB already acted, so they may only call.
    let s = PreflopSolver::new(three([100.0, 100.0, 3.5], &[2.5]), table()).unwrap();
    let btn = walk(&s, &["Raise 2.5", "Call 2.5", "All-in 3.5"]);
    assert_eq!(labels(&s, btn), ["Fold", "Call 3.5"]);
    let sb = step(&s, btn, "Call 3.5");
    assert_eq!(labels(&s, sb), ["Fold", "Call 3.5"]);
    // A full-raise shove (2.5 more) reopens it.
    let s = PreflopSolver::new(three([100.0, 100.0, 5.0], &[2.5]), table()).unwrap();
    let btn = walk(&s, &["Raise 2.5", "Call 2.5", "All-in 5"]);
    assert!(labels(&s, btn).iter().any(|l| l.starts_with("4-bet") || l.starts_with("All-in")));
    // A seat that has not acted yet keeps its raise after an incomplete shove:
    // SB shoves 3 over BTN's 2.5 open; BB never acted and may raise.
    let s = PreflopSolver::new(three([100.0, 3.0, 100.0], &[2.5]), table()).unwrap();
    let bb = walk(&s, &["Raise 2.5", "All-in 3"]);
    assert!(labels(&s, bb).iter().any(|l| l.starts_with("All-in") || l.starts_with("3-bet")));
}

#[test]
fn uncalled_chips_return_and_side_pots_layer_by_all_in_level() {
    let s = PreflopSolver::new(three([30.0, 10.0, 30.0], &[2.5]), table()).unwrap();
    // Everyone all-in: main pot 30 for all three, side pot 40 for BTN and BB.
    let t = walk(&s, &["All-in 30", "Call all-in 10", "Call 30"]);
    let nd = &s.nodes[t];
    assert_eq!(nd.kind, KIND_POT_SHARE);
    assert_eq!(nd.pot, 70.0);
    assert_eq!(nd.side_pots, vec![(30.0, 0b111), (40.0, 0b101)]);
    // BB folds: BTN's 20 bb nobody can call comes back; one pot of 21.
    let t = walk(&s, &["All-in 30", "Call all-in 10", "Fold"]);
    let nd = &s.nodes[t];
    assert_eq!((nd.invested.clone(), nd.pot), (vec![10.0, 10.0, 1.0], 21.0));
    assert!(nd.side_pots.is_empty());

    // Dead money above the short stack: BTN opens 20, SB calls all-in 10,
    // BB shoves 50 and BTN folds. BB gets back what BTN's 20 did not match;
    // BTN's chips above 10 form a side pot only BB can win.
    let s = PreflopSolver::new(three([50.0, 10.0, 50.0], &[20.0]), table()).unwrap();
    let t = walk(&s, &["Raise 20", "Call all-in 10", "All-in 50", "Fold"]);
    let nd = &s.nodes[t];
    assert_eq!(nd.invested, vec![20.0, 10.0, 20.0]);
    assert_eq!(nd.side_pots, vec![(30.0, 0b110), (20.0, 0b100)]);
}

#[test]
fn antes_and_heads_up_exports_use_effective_stacks() {
    let mut c = cfg(serde_json::json!({
        "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": 40.0, "stacks": [40.0, 25.0],
        "ante": 0.2, "limp": false, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2,
        "add_allin": true, "realization": "raw"
    }));
    let mut s = PreflopSolver::new(c.clone(), table()).unwrap();
    // SB's jam only needs to cover BB's 25.
    assert_eq!(labels(&s, 0), ["Fold", "Raise 2.5", "All-in 25"]);
    for _ in 0..3 {
        s.iterate();
    }
    let raise = s.nodes[0].actions.iter().position(|a| a.label == "Raise 2.5").unwrap();
    let call = s.nodes[s.child(0, raise)].actions.iter().position(|a| a.label == "Call 2.5").unwrap();
    let ex = s.export_spot(&[raise, call]).unwrap();
    assert_eq!(ex.eff_stack_bb, 22.5);
    assert_eq!(ex.pot_bb, 5.4);
    // A table with only one deep seat never offers raises past the cover.
    c.stacks = Some(vec![40.0, 2.0]);
    let s = PreflopSolver::new(c, table()).unwrap();
    assert_eq!(labels(&s, 0), ["Fold", "All-in 2"]);
}

/// Point-mass range on one class.
fn only(class: usize) -> Vec<f32> {
    let mut v = vec![0.0; NUM_CLASSES];
    v[class] = class_prob(class);
    v
}

#[test]
fn side_pot_payoffs_pay_each_pot_by_its_own_showdown() {
    let s = PreflopSolver::new(three([30.0, 10.0, 30.0], &[2.5]), table()).unwrap();
    let t = walk(&s, &["All-in 30", "Call all-in 10", "Call 30"]);
    let (aa, kk, qq) = (class_index(12, 12, false), class_index(11, 11, false), class_index(10, 10, false));
    // BTN QQ, SB (short) AA, BB KK.
    let reaches = vec![only(qq), only(aa), only(kk)];
    let prob = |p: usize| -> f64 {
        (0..3).filter(|&q| q != p).map(|q| reaches[q].iter().sum::<f32>() as f64).product()
    };
    let norm = |c: usize| { let mut v = vec![0.0f32; NUM_CLASSES]; v[c] = 1.0; v };
    let model = s.multiway.clone().unwrap();
    let mut out = [0.0f32; NUM_CLASSES];
    // BB: main pot vs AA and QQ, side pot vs QQ alone.
    s.terminal_value(t, 2, &reaches, &mut out);
    let main = model.equities(&[norm(qq), norm(aa)])[kk];
    let side = s.balanced_raw_equity(kk, qq) as f64;
    let want = prob(2) * (30.0 * main + 40.0 * side - 30.0);
    assert!((out[kk] as f64 - want).abs() < 1e-4 * want.abs().max(1.0), "{} vs {want}", out[kk]);
    // SB can only win the main pot.
    s.terminal_value(t, 1, &reaches, &mut out);
    let want = prob(1) * (30.0 * model.equities(&[norm(qq), norm(kk)])[aa] - 10.0);
    assert!((out[aa] as f64 - want).abs() < 1e-4 * want.abs().max(1.0));
}

#[test]
fn side_pot_payoffs_conserve_chips_net_of_rake() {
    let c = cfg(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0],
        "stack": 30.0, "stacks": [12.0, 30.0, 6.0, 20.0], "ante": 0.1,
        "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
        "add_allin": true, "realization": "static",
        "rake_pct": 5.0, "rake_cap": 3.0, "no_flop_no_drop": false
    }));
    let mut s = PreflopSolver::new(c, table()).unwrap();
    let weights: Vec<Vec<f32>> = (0..4)
        .map(|p| (0..NUM_CLASSES).map(|h| class_prob(h) * ((h + p * 17) % 23 + 1) as f32 / 25.0).collect())
        .collect();
    let mut layered = 0;
    for (node, nd) in s.nodes.iter().enumerate() {
        if nd.kind == KIND_ACTION {
            continue;
        }
        let in_pots: f64 = nd.side_pots.iter().map(|p| p.0).sum();
        if !nd.side_pots.is_empty() {
            layered += 1;
            assert!((in_pots - nd.pot).abs() < 1e-9, "pots {in_pots} vs {}", nd.pot);
        }
        if nd.kind != KIND_POT_SHARE {
            continue;
        }
        let mut total = 0.0;
        for p in 0..4 {
            let mut values = [0.0f32; NUM_CLASSES];
            s.terminal_value(node, p, &weights, &mut values);
            total += values.iter().zip(&weights[p]).map(|(v, w)| *v as f64 * *w as f64).sum::<f64>();
        }
        let probability: f64 = weights.iter().map(|w| w.iter().sum::<f32>() as f64).product();
        let expected = -probability * s.rake_of(nd.pot);
        // Two-way pots are exact; the static realization skew on non-all-in
        // multiway pots is the model's own (unchanged) approximation.
        if !nd.side_pots.is_empty() {
            assert!((total - expected).abs() < 1e-5, "node {node}: {total} vs {expected}");
        }
    }
    assert!(layered > 10, "only {layered} side-pot terminals");
    for _ in 0..10 {
        s.iterate();
    }
    assert!(s.evs().iter().all(|v| v.is_finite()));
    assert!(s.br_gaps().iter().all(|g| g.is_finite() && *g >= -1e-6));
}

#[test]
fn estimate_matches_the_built_tree() {
    let c = cfg(serde_json::json!({
        "positions": ["UTG", "HJ", "CO", "BTN", "SB", "BB"], "posts": [0, 0, 0, 0, 0.5, 1],
        "stack": 40.0, "stacks": [8.0, 40.0, 15.5, 22.0, 40.0, 11.0],
        "limp": true, "open_raises": [2.0], "raise_mults": [2.5], "max_raises": 3,
        "add_allin": true, "realization": "raw"
    }));
    let est = estimate_tree(&c).unwrap();
    let s = PreflopSolver::new(c, table()).unwrap();
    assert_eq!(est.nodes as usize, s.nodes.len());
}

#[cfg(feature = "gpu")]
#[test]
fn gpu_declines_side_pot_trees() {
    let s = PreflopSolver::new(three([30.0, 10.0, 30.0], &[2.5]), table()).unwrap();
    let err = gpu::PreflopGpu::new(&s, 2000).err().unwrap();
    assert!(err.contains("side pots"), "{err}");
}


#[test]
fn unequal_stack_saves_use_v5_and_round_trip() {
    let mut s = PreflopSolver::new(three([30.0, 10.0, 30.0], &[2.5]), table()).unwrap();
    for _ in 0..3 {
        s.iterate();
    }
    let path = std::env::temp_dir().join(format!("gtopen-stacks-save-{}.gtop", std::process::id()));
    let path = path.to_str().unwrap();
    s.save_game(path).unwrap();
    let bytes = std::fs::read(path).unwrap();
    assert_eq!(&bytes[..12], super::save::MAGIC_STACKS);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert_eq!(loaded.cfg.stacks, Some(vec![30.0, 10.0, 30.0]));
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    // A v5 file whose header lost its stacks must not rebuild an equal game.
    let end = 12 + bytes[12..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[12..end]).unwrap();
    header["config"].as_object_mut().unwrap().remove("stacks");
    let mut out = bytes[..12].to_vec();
    out.extend(serde_json::to_vec(&header).unwrap());
    out.extend_from_slice(&bytes[end..]);
    std::fs::write(path, out).unwrap();
    assert!(PreflopSolver::load_game(path, table()).err().unwrap().contains("v5"));
    std::fs::remove_file(path).unwrap();
}
