//! ICM payoffs: chip-EV equivalence under winner-take-all payouts, the
//! ladder value of a folded seat, a heads-up ICM jam/fold oracle, saves and
//! validation.

use super::super::equity::{class_prob, EquityTable, NUM_CLASSES};
use super::super::*;
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(200))).clone()
}

fn cfg(json: serde_json::Value) -> PreflopConfig {
    serde_json::from_value(json).unwrap()
}

fn with_icm(mut c: PreflopConfig, payouts: &[f64], field: &[f64]) -> PreflopConfig {
    c.icm = Some(IcmConfig { payouts: payouts.to_vec(), field: field.to_vec(), field_groups: vec![], stack_off: 1.0 });
    c
}

fn weights(n: usize) -> Vec<Vec<f32>> {
    (0..n)
        .map(|p| (0..NUM_CLASSES).map(|h| class_prob(h) * ((h * 7 + p * 17) % 23 + 1) as f32 / 25.0).collect())
        .collect()
}

/// Winner-take-all prizes are linear in chips, so every terminal of an ICM
/// game must pay exactly its chip-EV value: fold-wins, single pots under
/// each continuation model, multiway pots and side pots alike.
#[test]
fn winner_take_all_reproduces_chip_ev() {
    let games = [
        cfg(serde_json::json!({
            "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
            "stack": 30.0, "stacks": [30.0, 10.0, 30.0],
            "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
            "add_allin": true, "realization": "raw"
        })),
        cfg(serde_json::json!({
            "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0],
            "stack": 30.0, "stacks": [12.0, 30.0, 6.0, 20.0], "ante": 0.1,
            "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
            "add_allin": true, "realization": "static"
        })),
        cfg(serde_json::json!({
            "positions": ["HJ", "CO", "BTN", "SB", "BB"], "posts": [0, 0, 0, 0.5, 1],
            "stack": 20.0, "ante": 0.125, "open_raises": [2.0], "raise_mults": [2.5],
            "max_raises": 2, "add_allin": true, "realization": "balanced"
        })),
    ];
    for c in games {
        let n = c.positions.len();
        let chip = PreflopSolver::new(c.clone(), table()).unwrap();
        let icm = PreflopSolver::new(with_icm(c, &[100.0], &[25.0]), table()).unwrap();
        assert_eq!(chip.nodes.len(), icm.nodes.len());
        let w = weights(n);
        let (mut a, mut b) = ([0f32; NUM_CLASSES], [0f32; NUM_CLASSES]);
        let mut side = 0;
        for node in 0..chip.nodes.len() {
            if chip.nodes[node].kind == KIND_ACTION {
                continue;
            }
            side += usize::from(!chip.nodes[node].side_pots.is_empty());
            for p in 0..n {
                chip.terminal_value(node, p, &w, &mut a);
                icm.terminal_value(node, p, &w, &mut b);
                for h in 0..NUM_CLASSES {
                    assert!(
                        (a[h] - b[h]).abs() <= 2e-4 * a[h].abs().max(1.0),
                        "node {node} seat {p} class {h}: chip {} vs icm {}", a[h], b[h]
                    );
                }
            }
        }
        if n <= 4 {
            assert!(side > 0, "expected side-pot terminals");
        }
        let tables = icm.icm.as_ref().unwrap();
        assert!(tables.terms.iter().any(|t| t.stack_off.is_some()), "expected flop pots with a stack-off");
    }
}

/// Flop pots with chips behind carry the risk of the stacks behind: the
/// share of the pot a heads-up flat needs to break even rises with the
/// stack-off rate.
#[test]
fn stack_off_raises_the_price_of_flop_calls() {
    let break_even = |stack: f64, stack_off: f64| -> (f64, f64) {
        let mut c = with_icm(
            cfg(serde_json::json!({
                "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0], "stack": stack,
                "ante": 0.125, "open_raises": [2.0], "raise_mults": [], "max_raises": 1,
                "add_allin": false, "realization": "raw"
            })),
            &[50.0, 30.0, 20.0],
            &[],
        );
        c.icm.as_mut().unwrap().stack_off = stack_off;
        let s = PreflopSolver::new(c, table()).unwrap();
        // CO folds, BTN opens, SB folds, BB calls: a heads-up flop pot.
        let pick = |node: usize, kind: &str| {
            let a = s.nodes[node].actions.iter().position(|a| a.kind == kind).unwrap();
            s.child(node, a)
        };
        let t = pick(pick(pick(pick(0, "fold"), "raise"), "fold"), "call");
        assert_eq!(s.nodes[t].live.count_ones(), 2);
        let (bb, nd) = (3, &s.nodes[t]);
        let w = weights(4);
        let (mut chip, mut value) = ([0f32; NUM_CLASSES], [0f32; NUM_CLASSES]);
        s.chip_terminal_value(t, bb, &w, &mut chip);
        s.terminal_value(t, bb, &w, &mut value);
        // Value is linear in the chip share b: fit it across classes.
        let prob: f64 = (0..4).filter(|&q| q != bb).map(|q| w[q].iter().sum::<f32>() as f64).product();
        let b: Vec<f64> = chip.iter().map(|&v| (v as f64 / prob + nd.invested[bb]) / nd.pot).collect();
        let (lo, hi) = (0..NUM_CLASSES).fold((0, 0), |(lo, hi), h| {
            (if b[h] < b[lo] { h } else { lo }, if b[h] > b[hi] { h } else { hi })
        });
        let slope = (value[hi] - value[lo]) as f64 / (b[hi] - b[lo]);
        let at_zero = value[lo] as f64 / prob - slope / prob * b[lo];
        (-at_zero / (slope / prob), nd.invested[bb] / nd.pot)
    };
    let ((plain, chip), (half, _), (full, _)) = (break_even(15.0, 0.0), break_even(15.0, 0.5), break_even(15.0, 1.0));
    // ICM already charges a premium on the pot itself.
    assert!(plain > chip + 0.005 && plain < chip + 0.1, "pot lottery break-even {plain} vs chip {chip}");
    assert!(half > plain + 0.005 && full > half + 0.005, "{plain} {half} {full}");
    let short = break_even(8.0, 1.0).0;
    eprintln!("8bb stacks, stack-off 1: {short:.3}");
    eprintln!("BB flat break-even: chip {chip:.3}, pot lottery {plain:.3}, stack-off 0.5 {half:.3}, 1 {full:.3}");
}

/// With equal stacks at a three-handed final table, a folded seat gains a
/// guaranteed pay jump when the other two get all in.
#[test]
fn folded_seat_collects_the_ladder() {
    let c = with_icm(
        cfg(serde_json::json!({
            "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 10.0,
            "open_raises": [], "raise_mults": [], "max_raises": 1, "add_allin": true,
            "realization": "raw"
        })),
        &[50.0, 30.0, 20.0],
        &[],
    );
    let s = PreflopSolver::new(c, table()).unwrap();
    let fold = s.nodes[0].actions.iter().position(|a| a.kind == "fold").unwrap();
    let sb = s.child(0, fold);
    let jam = s.nodes[sb].actions.iter().position(|a| a.kind == "jam").unwrap();
    let bb = s.child(sb, jam);
    let call = s.nodes[bb].actions.iter().position(|a| a.kind == "call").unwrap();
    let t = s.child(bb, call);
    let w = weights(3);
    let mut out = [0f32; NUM_CLASSES];
    s.terminal_value(t, 0, &w, &mut out);
    let prob: f64 = w[1].iter().sum::<f32>() as f64 * w[2].iter().sum::<f32>() as f64;
    // After the hand: BTN 10 vs the winner's 20, the loser takes 3rd (20).
    // BTN's equity 50/3 + 2/3*30 = 36.67 vs 33.33 before: +3.33 prize units,
    // times 30 chips / 100 prize = +1.0 bb equivalent.
    for v in out {
        assert!((v as f64 / prob - 1.0).abs() < 1e-4, "{}", v as f64 / prob);
    }
    let summary = s.icm_summary().unwrap();
    assert!((summary.bb_per_prize - 0.3).abs() < 1e-12);
    assert!(summary.seat_equity.iter().all(|e| (e - 100.0 / 3.0).abs() < 1e-9));
    assert!(summary.field.is_empty());
}

fn brute_icm(stacks: &[f64], payouts: &[f64]) -> Vec<f64> {
    fn rec(st: &[f64], pay: &[f64], left: &mut Vec<usize>, prob: f64, place: usize, out: &mut [f64]) {
        let rest: f64 = left.iter().map(|&i| st[i]).sum();
        for k in 0..left.len() {
            let i = left[k];
            let p = prob * st[i] / rest;
            out[i] += p * pay.get(place).copied().unwrap_or(0.0);
            left.remove(k);
            rec(st, pay, left, p, place + 1, out);
            left.insert(k, i);
        }
    }
    let mut out = vec![0.0; stacks.len()];
    let alive: Vec<usize> = (0..stacks.len()).filter(|&i| stacks[i] > 0.0).collect();
    let mut sub = vec![0.0; alive.len()];
    let st: Vec<f64> = alive.iter().map(|&i| stacks[i]).collect();
    rec(&st, payouts, &mut (0..alive.len()).collect(), 1.0, 0, &mut sub);
    for (k, &i) in alive.iter().enumerate() {
        out[i] = sub[k];
    }
    // One bust per hand in this game: it takes the next place down.
    for i in 0..stacks.len() {
        if stacks[i] <= 0.0 {
            out[i] = payouts.get(alive.len()).copied().unwrap_or(0.0);
        }
    }
    out
}

/// Heads-up jam/fold at 10bb with a 20bb player at another table and
/// 50/30/20 payouts: CFR must match an independent fictitious-play oracle
/// on the same equity table and ICM prizes, and call tighter than chip EV.
#[test]
fn icm_push_fold_matches_oracle() {
    let eq = table();
    let payouts = [50.0, 30.0, 20.0];
    let base = cfg(serde_json::json!({
        "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": 10.0,
        "open_raises": [], "raise_mults": [], "max_raises": 1, "add_allin": true,
        "allin_threshold": 0.85, "realization": "raw"
    }));
    let mut s = PreflopSolver::new(with_icm(base.clone(), &payouts, &[20.0]), eq.clone()).unwrap();
    let mut chip = PreflopSolver::new(base, eq.clone()).unwrap();
    for _ in 0..3000 {
        s.iterate();
        chip.iterate();
    }

    let scale = 40.0 / 100.0;
    let start = brute_icm(&[10.0, 10.0, 20.0], &payouts);
    let u = |st: [f64; 3]| -> [f64; 2] {
        let v = brute_icm(&st, &payouts);
        [(v[0] - start[0]) * scale, (v[1] - start[1]) * scale]
    };
    let sb_fold = u([9.5, 10.5, 20.0]);
    let bb_fold = u([11.0, 9.0, 20.0]);
    let sb_wins = u([20.0, 0.0, 20.0]);
    let bb_wins = u([0.0, 20.0, 20.0]);

    let prob: Vec<f64> = (0..NUM_CLASSES).map(|h| class_prob(h) as f64).collect();
    let total: f64 = prob.iter().sum();
    let mut jam_mix = vec![1f64; NUM_CLASSES];
    let mut call_mix = vec![0f64; NUM_CLASSES];
    let (mut jam_margin, mut call_margin) = (vec![0f64; NUM_CLASSES], vec![0f64; NUM_CLASSES]);
    let normalized = |mix: &[f64]| -> Vec<f32> {
        let mut d: Vec<f32> = (0..NUM_CLASSES).map(|j| (prob[j] * mix[j]) as f32).collect();
        let t: f32 = d.iter().sum();
        if t > 0.0 {
            d.iter_mut().for_each(|x| *x /= t);
        }
        d
    };
    for t in 1..=4000u32 {
        let dist = normalized(&jam_mix);
        let mut call_br = vec![0f64; NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            let e = eq.eq_vs_dist(h, &dist) as f64;
            call_margin[h] = e * bb_wins[1] + (1.0 - e) * sb_wins[1] - bb_fold[1];
            call_br[h] = f64::from(call_margin[h] > 0.0);
        }
        let p_call = (0..NUM_CLASSES).map(|j| prob[j] * call_mix[j]).sum::<f64>() / total;
        let cdist = normalized(&call_mix);
        let mut jam_br = vec![0f64; NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            let e = eq.eq_vs_dist(h, &cdist) as f64;
            let ev = (1.0 - p_call) * bb_fold[0] + p_call * (e * sb_wins[0] + (1.0 - e) * bb_wins[0]);
            jam_margin[h] = ev - sb_fold[0];
            jam_br[h] = f64::from(jam_margin[h] > 0.0);
        }
        let w = 1.0 / t as f64;
        for h in 0..NUM_CLASSES {
            call_mix[h] += w * (call_br[h] - call_mix[h]);
            jam_mix[h] += w * (jam_br[h] - jam_mix[h]);
        }
    }

    let jam_a = s.nodes[0].actions.iter().position(|a| a.kind == "jam").unwrap();
    let bb = s.child(0, jam_a);
    let call_a = s.nodes[bb].actions.iter().position(|a| a.kind == "call").unwrap();
    let (sb_avg, bb_avg) = (s.average_strategy(0), s.average_strategy(bb));
    let mut checked = 0;
    for h in 0..NUM_CLASSES {
        if jam_margin[h].abs() > 0.10 {
            let f = sb_avg[jam_a * NUM_CLASSES + h];
            let want = jam_mix[h] > 0.5;
            assert!(if want { f > 0.85 } else { f < 0.15 },
                "SB {}: oracle jam={want} margin={:.3}, CFR {f:.3}", equity::class_label(h), jam_margin[h]);
            checked += 1;
        }
        if call_margin[h].abs() > 0.10 {
            let f = bb_avg[call_a * NUM_CLASSES + h];
            let want = call_mix[h] > 0.5;
            assert!(if want { f > 0.85 } else { f < 0.15 },
                "BB {}: oracle call={want} margin={:.3}, CFR {f:.3}", equity::class_label(h), call_margin[h]);
            checked += 1;
        }
    }
    assert!(checked > 200, "only {checked} clear decisions");

    let combos = |s: &PreflopSolver, node: usize, a: usize| -> f64 {
        let avg = s.average_strategy(node);
        (0..NUM_CLASSES).map(|h| avg[a * NUM_CLASSES + h] as f64 * prob[h]).sum::<f64>() / total
    };
    let chip_bb = chip.child(0, jam_a);
    let (icm_call, chip_call) = (combos(&s, bb, call_a), combos(&chip, chip_bb, call_a));
    assert!(icm_call < chip_call - 0.05, "ICM calls {icm_call:.3} vs chip EV {chip_call:.3}");
}

#[test]
fn final_table_game_solves() {
    let c = with_icm(
        cfg(serde_json::json!({
            "positions": ["HJ", "CO", "BTN", "SB", "BB"], "posts": [0, 0, 0, 0.5, 1],
            "stack": 25.0, "stacks": [25.0, 12.0, 40.0, 8.0, 18.0], "ante": 0.125,
            "open_raises": [2.0], "raise_mults": [2.5], "max_raises": 2, "add_allin": true,
            "realization": "balanced"
        })),
        &[40.0, 25.0, 16.0, 11.0, 8.0],
        &[],
    );
    let mut s = PreflopSolver::new(c, table()).unwrap();
    let mut first = None;
    for i in 0..60 {
        s.iterate();
        if i == 5 {
            first = Some(s.br_gaps().iter().sum::<f64>());
        }
    }
    let gaps = s.br_gaps();
    assert!(gaps.iter().all(|g| g.is_finite() && *g >= -1e-6), "{gaps:?}");
    assert!(gaps.iter().sum::<f64>() < first.unwrap(), "{gaps:?} vs {first:?}");
    assert!(s.evs().iter().all(|v| v.is_finite()));
}

#[test]
fn icm_saves_use_v6_and_round_trip() {
    let c = with_icm(
        cfg(serde_json::json!({
            "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 15.0,
            "open_raises": [2.0], "raise_mults": [], "max_raises": 2, "add_allin": true,
            "realization": "raw"
        })),
        &[50.0, 30.0, 20.0],
        &[12.0],
    );
    let mut s = PreflopSolver::new(c.clone(), table()).unwrap();
    for _ in 0..3 {
        s.iterate();
    }
    let path = std::env::temp_dir().join(format!("gtopen-icm-save-{}.gtop", std::process::id()));
    let path = path.to_str().unwrap();
    s.save_game(path).unwrap();
    let bytes = std::fs::read(path).unwrap();
    assert_eq!(&bytes[..12], super::super::save::MAGIC_ICM);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert_eq!(loaded.cfg.icm, c.icm);
    assert!(loaded.icm.is_some());
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    // A v6 file whose header lost its payouts must not load as chip EV.
    let end = 12 + bytes[12..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[12..end]).unwrap();
    header["config"].as_object_mut().unwrap().remove("icm");
    let mut out = bytes[..12].to_vec();
    out.extend(serde_json::to_vec(&header).unwrap());
    out.extend_from_slice(&bytes[end..]);
    std::fs::write(path, out).unwrap();
    assert!(PreflopSolver::load_game(path, table()).err().unwrap().contains("v6"));
    std::fs::remove_file(path).unwrap();
}

#[test]
fn icm_config_is_validated() {
    let base = cfg(serde_json::json!({
        "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": 10.0,
        "open_raises": [], "raise_mults": [], "max_raises": 1, "add_allin": true
    }));
    let err = |c: PreflopConfig| PreflopSolver::new(c, table()).err().unwrap();
    let mut raked = with_icm(base.clone(), &[1.0], &[]);
    raked.rake_pct = 5.0;
    assert!(err(raked).contains("rake"));
    assert!(err(with_icm(base.clone(), &[], &[])).contains("payout"));
    let distinct: Vec<f64> = (1..=20).map(|k| k as f64).collect();
    assert!(err(with_icm(base.clone(), &[1.0; 20], &distinct)).contains("too large"));
    assert!(err(with_icm(base.clone(), &[1.0], &[0.0])).contains("field"));
    assert!(err(with_icm(base, &[-1.0], &[])).contains("negative"));
    let bad: Result<PreflopConfig, _> = serde_json::from_value(serde_json::json!({
        "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": 10.0,
        "open_raises": [], "raise_mults": [], "icm": {"payouts": [1.0], "feild": [3.0]}
    }));
    assert!(bad.is_err());
}
