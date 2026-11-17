//! Blockers (card removal): terminal values against a count over real
//! cards, and a heads-up solve checked card by card.

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

/// Every two-card combo as (class, card, card), cards as rank*4+suit.
fn combos() -> &'static [(usize, u8, u8)] {
    static C: OnceLock<Vec<(usize, u8, u8)>> = OnceLock::new();
    C.get_or_init(|| {
        let mut v = Vec::new();
        for a in 0..52u8 {
            for b in (a + 1)..52 {
                let (ra, sa, rb, sb) = (a / 4, a % 4, b / 4, b % 4);
                v.push((class_index(ra, rb, sa == sb && ra != rb), a, b));
            }
        }
        v
    })
}

fn disjoint(x: &(usize, u8, u8), y: &(usize, u8, u8)) -> bool {
    x.1 != y.1 && x.1 != y.2 && x.2 != y.1 && x.2 != y.2
}

/// Chip delta for seat p holding class h against class j at a heads-up
/// terminal (raw realization: linear in the pairwise equity).
fn payoff(s: &PreflopSolver, node: usize, p: usize, h: usize, j: usize) -> f64 {
    let nd = &s.nodes[node];
    let inv = nd.invested[p];
    match nd.kind {
        KIND_FOLD_WIN => {
            if nd.winner as usize == p { nd.pot - s.fold_win_rake(nd) - inv } else { -inv }
        }
        _ if nd.live & (1 << p) == 0 => -inv,
        _ => {
            assert_eq!(nd.r[p], 1.0, "raw realization");
            (nd.pot - s.rake_of(nd.pot)) * s.eq.eq(h, j) as f64 - inv
        }
    }
}

fn heads_up(stack: f64, extra: serde_json::Value) -> PreflopConfig {
    let mut v = serde_json::json!({
        "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": stack,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3, "add_allin": true,
        "limp": true, "realization": "raw", "rake_pct": 5.0, "rake_cap": 1.0, "card_removal": true
    });
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    cfg(v)
}

#[test]
fn heads_up_terminals_match_a_count_over_real_cards() {
    let s = PreflopSolver::new(heads_up(20.0, serde_json::json!({})), table()).unwrap();
    let reaches: Vec<Vec<f32>> = (0..2)
        .map(|p| (0..NUM_CLASSES).map(|h| class_prob(h) * (((h * 7 + p * 29) % 13) as f32 / 12.0)).collect())
        .collect();
    let mut checked = 0;
    for node in 0..s.nodes.len() {
        if s.nodes[node].kind == KIND_ACTION {
            continue;
        }
        for p in 0..2 {
            let q = 1 - p;
            let mut out = [0f32; NUM_CLASSES];
            s.terminal_value(node, p, &reaches, &mut out);
            for h in (0..NUM_CLASSES).step_by(7) {
                let hero = combos().iter().find(|c| c.0 == h).unwrap();
                let mut want = 0f64;
                for o in combos().iter().filter(|o| disjoint(hero, o)) {
                    let j = o.0;
                    // The opponent's chance of reaching here with this combo,
                    // given the hero's two cards are out of the deck.
                    let reach = reaches[q][j] as f64 / class_prob(j) as f64 / 1225.0;
                    want += reach * payoff(&s, node, p, h, j);
                }
                let got = out[h] as f64;
                assert!((got - want).abs() < 1e-4 * want.abs().max(1.0), "node {node} seat {p} class {h}: {got} vs {want}");
                checked += 1;
            }
        }
    }
    assert!(checked > 100);
}

#[test]
fn full_ranges_fold_out_the_same_with_or_without_blockers() {
    let mut c = cfg(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 30.0,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3, "add_allin": true,
        "realization": "static", "rake_pct": 5.0, "rake_cap": 2.0
    }));
    let plain = PreflopSolver::new(c.clone(), table()).unwrap();
    c.card_removal = true;
    let blockers = PreflopSolver::new(c, table()).unwrap();
    let full: Vec<Vec<f32>> = (0..3).map(|_| (0..NUM_CLASSES).map(class_prob).collect()).collect();
    let mut folds = 0;
    for node in 0..plain.nodes.len() {
        if plain.nodes[node].kind != KIND_FOLD_WIN {
            continue;
        }
        folds += 1;
        for p in 0..3 {
            let (mut a, mut b) = ([0f32; NUM_CLASSES], [0f32; NUM_CLASSES]);
            plain.terminal_value(node, p, &full, &mut a);
            blockers.terminal_value(node, p, &full, &mut b);
            for h in 0..NUM_CLASSES {
                assert!((a[h] - b[h]).abs() < 1e-4, "node {node} seat {p} class {h}: {} vs {}", a[h], b[h]);
            }
        }
    }
    assert!(folds > 3);
}

#[test]
fn blockers_give_each_hand_its_own_fold_chance() {
    // BTN opens; SB and BB fold most hands but continue with aces and
    // kings. Holding an ace makes their continuing hands rarer.
    let s = PreflopSolver::new(cfg(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 30.0,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2,
        "realization": "static", "card_removal": true
    })), table()).unwrap();
    let open = s.nodes[0].actions.iter().position(|a| a.kind == "raise").unwrap();
    let after_open = s.child(0, open);
    let sb_fold = s.nodes[after_open].actions.iter().position(|a| a.kind == "fold").unwrap();
    let after_sb = s.child(after_open, sb_fold);
    let bb_fold = s.nodes[after_sb].actions.iter().position(|a| a.kind == "fold").unwrap();
    let won = s.child(after_sb, bb_fold);
    assert_eq!(s.nodes[won].kind, KIND_FOLD_WIN);
    let strong = |h: usize| { let (hi, lo, _) = equity::class_parts(h); hi >= 11 && lo >= 11 };
    let folds: Vec<f32> = (0..NUM_CLASSES).map(|h| class_prob(h) * if strong(h) { 0.0 } else { 1.0 }).collect();
    let reaches = vec![(0..NUM_CLASSES).map(class_prob).collect::<Vec<_>>(), folds.clone(), folds];
    let mut out = [0f32; NUM_CLASSES];
    s.terminal_value(won, 0, &reaches, &mut out);
    let (aa, aks, t2o, s32) = (class_index(12, 12, false), class_index(12, 11, true),
                               class_index(8, 0, false), class_index(1, 0, true));
    // Blockers to the continuing hands get through more often than hands
    // without them, and every hand differs from the plain average.
    assert!(out[aa] > out[t2o] && out[aks] > out[t2o], "{} {} {}", out[aa], out[aks], out[t2o]);
    assert!((out[t2o] - out[s32]).abs() < 0.02 * out[t2o].abs());
    assert!(out[aa] / out[t2o] > 1.01, "{} vs {}", out[aa], out[t2o]);
}

/// Card-level best-response gap (bb, summed over both seats) of the solver's
/// average strategy in a heads-up game, dealing real cards. Payoffs use the
/// same class equity table, so the only difference from the solver's own
/// view is card removal.
fn card_level_gap(s: &PreflopSolver) -> f64 {
    let all = combos();
    let n = all.len();
    let strategies: Vec<Vec<f32>> = (0..s.nodes.len())
        .map(|node| if s.nodes[node].kind == KIND_ACTION { s.average_strategy(node) } else { Vec::new() })
        .collect();
    // value(node, weights over opponent combos) for one hero combo.
    fn walk(s: &PreflopSolver, strategies: &[Vec<f32>], node: usize, p: usize, h: usize,
            opp: &[f64], br: bool) -> f64 {
        let nd = &s.nodes[node];
        if nd.kind != KIND_ACTION {
            let all = combos();
            return all.iter().zip(opp).filter(|(_, w)| **w > 0.0)
                .map(|(o, w)| w * payoff(s, node, p, h, o.0)).sum();
        }
        let na = nd.actions.len();
        let sigma = &strategies[node];
        if nd.actor as usize == p {
            let values: Vec<f64> = (0..na).map(|a| walk(s, strategies, s.child(node, a), p, h, opp, br)).collect();
            if br {
                values.into_iter().fold(f64::MIN, f64::max)
            } else {
                (0..na).map(|a| sigma[a * NUM_CLASSES + h] as f64 * values[a]).sum()
            }
        } else {
            (0..na).map(|a| {
                let next: Vec<f64> = combos().iter().zip(opp)
                    .map(|(o, w)| w * sigma[a * NUM_CLASSES + o.0] as f64).collect();
                walk(s, strategies, s.child(node, a), p, h, &next, br)
            }).sum()
        }
    }
    let mut gap = 0.0;
    for p in 0..2 {
        let mut total = 0.0;
        for hero in all {
            let opp: Vec<f64> = all.iter().map(|o| if disjoint(hero, o) { 1.0 / 1225.0 } else { 0.0 }).collect();
            let best = walk(s, &strategies, 0, p, hero.0, &opp, true);
            let played = walk(s, &strategies, 0, p, hero.0, &opp, false);
            total += best - played;
        }
        gap += total / n as f64;
    }
    gap
}

#[test]
fn heads_up_game_with_blockers_is_unexploitable_card_by_card() {
    let game = |blockers: bool| {
        let c = heads_up(20.0, serde_json::json!({
            "open_raises": [2.5], "max_raises": 3, "limp": false, "add_allin": true,
            "rake_pct": 0.0, "card_removal": blockers
        }));
        let mut s = PreflopSolver::new(c, table()).unwrap();
        s.prune = false;
        for _ in 0..3000 {
            s.iterate();
        }
        let own: f64 = s.br_gaps().iter().sum();
        (own, card_level_gap(&s))
    };
    let (own_b, cards_b) = game(true);
    let (own_p, cards_p) = game(false);
    eprintln!("blockers: own gap {own_b:.5}, card-level gap {cards_b:.5}; plain: own {own_p:.5}, card-level {cards_p:.5}");
    // With blockers the solver's own gap is the real one, dealing real cards.
    assert!((own_b - cards_b).abs() < 2e-3, "{own_b} vs {cards_b}");
    assert!(cards_b < 0.01, "{cards_b}");
    // Without them the real-card gap is larger than the solver believes.
    assert!(cards_p > own_p, "{cards_p} vs {own_p}");
}
