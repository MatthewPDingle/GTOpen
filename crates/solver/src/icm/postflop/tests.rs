//! Postflop ICM: winner-take-all is chip EV, and a bubble river jam spot
//! solves to tighter calls than chip EV.
use super::*;
use crate::cfr::Solver;
use crate::game::{Spot, SpotConfig};
use crate::tree::{BetSize, StreetSizing, TreeConfig, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};
use std::sync::Arc;

fn sizing(bet: &[f64], raise: &[f64]) -> [StreetSizing; 3] {
    let s = StreetSizing {
        bet: bet.iter().map(|&p| BetSize::PotPct(p)).collect(),
        raise: raise.iter().map(|&p| BetSize::PotPct(p)).collect(),
        donk: vec![],
    };
    [s.clone(), s.clone(), s]
}

fn spot(board: &str, oop: &str, ip: &str, tree: TreeConfig) -> Arc<Spot> {
    Arc::new(Spot::new(SpotConfig { board: board.into(), range_oop: oop.into(), range_ip: ip.into(), tree }).unwrap())
}

#[test]
fn winner_take_all_pays_chips() {
    let tree = TreeConfig {
        starting_pot: 12.0,
        effective_stack: 30.0,
        oop: sizing(&[50.0], &[100.0]),
        ip: sizing(&[33.0, 75.0], &[100.0]),
        add_allin: true,
        max_raises: 2,
        icm: Some(PostflopIcm {
            payouts: vec![100.0],
            behind: Some(vec![30.0, 47.5]),
            others: vec![20.0, 15.0],
            field_groups: vec![FieldGroup { stack: 25.0, count: 4 }],
        }),
        ..TreeConfig::default()
    };
    let s = spot("Ks7d2c4h", "AA,KQ,76s", "QQ,AK,98s", tree);
    let icm = s.icm.as_ref().unwrap();
    let (mut folds, mut shows) = (0, 0);
    for (ni, node) in s.tree.nodes.iter().enumerate() {
        let close = |a: f32, b: f64| assert!((a as f64 - b).abs() < 1e-4, "node {ni}: icm {a} vs chips {b}");
        match node.kind {
            KIND_TERM_FOLD => {
                folds += 1;
                for p in 0..2 {
                    let chips = if node.player as usize == p { node.t_lose } else { node.t_win };
                    close(s.fold_payoff(ni as u32, node, p), chips);
                }
            }
            KIND_TERM_SHOWDOWN => {
                shows += 1;
                for p in 0..2 {
                    let (w, l, t) = s.showdown_payoffs(ni as u32, node, p);
                    close(w, node.t_win);
                    close(l, node.t_lose);
                    close(t, node.t_tie);
                }
            }
            _ => {}
        }
    }
    assert!(folds > 3 && shows > 3, "{folds} folds, {shows} showdowns");
    // Bigger stacks hold more of a winner-take-all prize.
    assert!(icm.start_equity[1] > icm.start_equity[0]);
}

#[test]
fn bad_icm_configs_are_rejected() {
    let base = PostflopIcm { payouts: vec![50.0, 30.0, 20.0], behind: None, others: vec![10.0], field_groups: vec![] };
    assert!(base.validate(2, 20.0, 0.0).is_ok());
    assert!(base.validate(2, 20.0, 0.05).is_err());
    let short = PostflopIcm { behind: Some(vec![20.0, 15.0]), ..base.clone() };
    assert!(short.validate(2, 20.0, 0.0).is_err());
    let negative = PostflopIcm { payouts: vec![50.0, -1.0], ..base.clone() };
    assert!(negative.validate(2, 20.0, 0.0).is_err());
    let empty = PostflopIcm { others: vec![0.0], ..base };
    assert!(empty.validate(2, 20.0, 0.0).is_err());
}

/// IP's chance of calling OOP's river jam with its range, and the solve's
/// exploitability.
fn jam_call_rate(icm: Option<PostflopIcm>) -> (f64, f64) {
    let tree = TreeConfig {
        starting_pot: 10.0,
        effective_stack: 20.0,
        oop: sizing(&[], &[]),
        ip: sizing(&[], &[]),
        add_allin: true,
        icm,
        ..TreeConfig::default()
    };
    let s = spot("AsKd7c4h2s", "AA,KK,77,QJs,JTs,T9s,98s,65s", "AQ,AJ,AT,KQ", tree);
    let mut solver = Solver::new(s.clone());
    for _ in 0..1500 {
        solver.iterate();
    }
    let expl = solver.exploitability();
    // Root: OOP checks or jams; IP then calls or folds the jam.
    let tree = &s.tree;
    let root = &tree.nodes[0];
    let jam = (0..root.num_children as usize)
        .find(|&a| matches!(tree.actions[root.actions_start as usize + a], crate::tree::Action::Bet(_)))
        .unwrap();
    let facing = &tree.nodes[tree.children[root.children_start as usize + jam] as usize];
    let call = (0..facing.num_children as usize)
        .find(|&a| matches!(tree.actions[facing.actions_start as usize + a], crate::tree::Action::Call(_)))
        .unwrap();
    let nh = s.hands[1].len();
    let mut sigma = vec![0f32; facing.num_children as usize * nh];
    solver.solved_strategy_into(facing, &mut sigma);
    let (mut called, mut mass) = (0f64, 0f64);
    for (i, h) in s.hands[1].iter().enumerate() {
        called += h.weight as f64 * sigma[call * nh + i] as f64;
        mass += h.weight as f64;
    }
    (called / mass, expl)
}

#[test]
fn bubble_calls_tighter_than_chips() {
    let (chips, chip_expl) = jam_call_rate(None);
    // Three left, two paid, the third player covers neither: losing the
    // all-in busts on the bubble.
    let bubble = PostflopIcm { payouts: vec![50.0, 50.0], behind: None, others: vec![30.0], field_groups: vec![] };
    let (icm, icm_expl) = jam_call_rate(Some(bubble));
    eprintln!("call rate vs river jam: chips {chips:.3} (expl {chip_expl:.4}), bubble {icm:.3} (expl {icm_expl:.4})");
    assert!(icm_expl.is_finite() && icm_expl < 0.05, "bubble exploitability {icm_expl}");
    assert!(icm < chips - 0.05, "bubble call rate {icm} vs chips {chips}");
}
