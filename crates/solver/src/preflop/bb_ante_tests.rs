//! Big blind ante: dead money only the big blind pays. The tree, the pot and
//! the stacks are those of the same total paid a share per seat; only who
//! paid differs. Uncalled chips, rake and side pots compare what the seats
//! bet, never the ante.

use std::sync::{Arc, OnceLock};

use super::{
    equity::{class_prob, EquityTable, NUM_CLASSES},
    *,
};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(200))).clone()
}

fn cfg(json: serde_json::Value) -> PreflopConfig {
    serde_json::from_value(json).unwrap()
}

fn four(ante: f64, bb_ante: f64) -> PreflopConfig {
    cfg(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0], "stack": 30.0,
        "ante": ante, "bb_ante": bb_ante, "limp": true, "open_raises": [2.5], "raise_mults": [3.0],
        "max_raises": 3, "add_allin": true, "realization": "static",
        "rake_pct": 5.0, "rake_cap": 2.0, "no_flop_no_drop": false
    }))
}

fn step(s: &PreflopSolver, node: usize, label: &str) -> usize {
    let nd = &s.nodes[node];
    let a = nd
        .actions
        .iter()
        .position(|a| a.label.starts_with(label))
        .unwrap_or_else(|| {
            panic!(
                "no {label:?} among {:?}",
                nd.actions.iter().map(|a| &a.label).collect::<Vec<_>>()
            )
        });
    s.child(node, a)
}

fn walk(s: &PreflopSolver, path: &[&str]) -> usize {
    path.iter().fold(0, |node, label| step(s, node, label))
}

fn weights(n: usize) -> Vec<Vec<f32>> {
    (0..n)
        .map(|p| {
            (0..NUM_CLASSES)
                .map(|h| class_prob(h) * ((h * 7 + p * 17) % 23 + 1) as f32 / 25.0)
                .collect()
        })
        .collect()
}

#[test]
fn only_the_big_blind_pays_and_it_never_counts_as_a_bet() {
    let c = four(0.0, 1.0);
    assert_eq!(
        (c.ante_of(0), c.ante_of(2), c.ante_of(3), c.ante_total()),
        (0.0, 0.0, 1.0, 1.0)
    );
    let plain = PreflopSolver::new(four(0.0, 0.0), table()).unwrap();
    let s = PreflopSolver::new(c.clone(), table()).unwrap();
    // The ante is paid on top of the stack: everyone still plays 30 bb.
    assert_eq!(s.nodes[0].invested, vec![0.0, 0.0, 0.5, 2.0]);
    assert_eq!(c.left(3, 2.0), 29.0);
    assert_eq!(c.left(2, 0.5), 29.5);
    // The same tree as without it: every menu, every size.
    assert_eq!(s.nodes.len(), plain.nodes.len());
    assert_eq!(estimate_tree(&c).unwrap().nodes as usize, s.nodes.len());
    for (a, b) in s.nodes.iter().zip(&plain.nodes) {
        assert_eq!(a.kind, b.kind);
        assert_eq!(
            a.actions.iter().map(|x| &x.label).collect::<Vec<_>>(),
            b.actions.iter().map(|x| &x.label).collect::<Vec<_>>()
        );
        assert!((a.pot - b.pot - 1.0).abs() < 1e-9);
        assert!(a.side_pots.is_empty(), "equal stacks never make side pots");
        assert!((a.invested[3] - b.invested[3] - 1.0).abs() < 1e-9);
        assert!((0..3).all(|q| a.invested[q] == b.invested[q]));
    }
    // The big blind checks its option after a limp: it owes nothing more.
    let bb = walk(&s, &["Fold", "Limp", "Fold"]);
    assert_eq!(s.nodes[bb].actor, 3);
    assert!(s.nodes[bb].actions.iter().any(|a| a.kind == "check"));
    assert!(s.is_cold(&s.nodes[bb]));
}

#[test]
fn uncalled_chips_and_fold_rake_ignore_the_ante() {
    let s = PreflopSolver::new(four(0.0, 1.0), table()).unwrap();
    // BTN opens to 2.5 and takes it: 1.5 of the open was never called, and
    // the 3.5 that was matched (blinds, ante and 1 of the open) is raked.
    let t = walk(&s, &["Fold", "Raise 2.5", "Fold", "Fold"]);
    let nd = &s.nodes[t];
    assert_eq!((nd.kind, nd.winner, nd.pot), (KIND_FOLD_WIN, 1, 5.0));
    assert!((s.fold_win_rake(nd) - 0.05 * 3.5).abs() < 1e-12);
    // A walk: the big blind's own ante is not an uncalled bet. Only the half
    // blind the small blind did not match comes back before the rake.
    let t = walk(&s, &["Fold", "Fold", "Fold"]);
    let nd = &s.nodes[t];
    assert_eq!((nd.kind, nd.winner, nd.pot), (KIND_FOLD_WIN, 3, 2.5));
    assert!((s.fold_win_rake(nd) - 0.05 * 2.0).abs() < 1e-12);
    // A game with a per-seat ante only is priced exactly as before.
    let each = PreflopSolver::new(four(0.25, 0.0), table()).unwrap();
    let nd = &each.nodes[walk(&each, &["Fold", "Raise 2.5", "Fold", "Fold"])];
    assert_eq!(each.fold_win_rake(nd), each.rake_of(nd.pot - 1.5));
}

/// With learned flop values and blockers on, the leaf net's input used to
/// carry a term in what the seat had put in, so who paid the ante changed
/// the net's answer. The input is the plain pot share: both ways of paying
/// get the same corrections at the same strategies.
#[test]
fn learned_values_with_blockers_do_not_see_who_paid_the_ante() {
    let corrections = |ante: f64, bb_ante: f64| {
        let mut c = four(ante, bb_ante);
        c.realization = "leafnet".into();
        c.card_removal = true;
        let mut s = PreflopSolver::new(c, table()).unwrap();
        // a few steps, so the ranges are no longer the full deal (which blocks nothing)
        for _ in 0..5 {
            s.iterate();
        }
        assert!(s.refresh_leaf_values().unwrap().priced > 3);
        s.leaf_terminals().unwrap().2.to_vec()
    };
    let (each, bb) = (corrections(0.25, 0.0), corrections(0.0, 1.0));
    assert!(
        each.iter().any(|c| c.abs() > 1e-3),
        "the net corrects something"
    );
    // the two solves match step for step to float noise (see the next test)
    let worst = each
        .iter()
        .zip(&bb)
        .map(|(x, y)| (x - y).abs())
        .fold(0f32, f32::max);
    assert!(worst < 1e-4, "corrections differ by {worst} of the pot");
}

/// One bb from the big blind and a quarter from each of four seats build the
/// same pot over the same stacks, so every terminal pays each seat the same
/// up to what that seat paid in, and the solves agree.
#[test]
fn same_game_as_each_seat_paying_a_share() {
    let mut each = PreflopSolver::new(four(0.25, 0.0), table()).unwrap();
    let mut bb = PreflopSolver::new(four(0.0, 1.0), table()).unwrap();
    assert_eq!(each.nodes.len(), bb.nodes.len());
    let w = weights(4);
    let (mut a, mut b) = ([0f32; NUM_CLASSES], [0f32; NUM_CLASSES]);
    for node in 0..each.nodes.len() {
        if each.nodes[node].kind == KIND_ACTION {
            continue;
        }
        assert!((each.nodes[node].pot - bb.nodes[node].pot).abs() < 1e-9);
        for p in 0..4 {
            let prob: f64 = (0..4)
                .filter(|&q| q != p)
                .map(|q| w[q].iter().sum::<f32>() as f64)
                .product();
            // what seat p paid less (or more) in the big blind ante game
            let shift = prob * (0.25 - if p == 3 { 1.0 } else { 0.0 });
            each.terminal_value(node, p, &w, &mut a);
            bb.terminal_value(node, p, &w, &mut b);
            for h in 0..NUM_CLASSES {
                assert!(
                    (a[h] as f64 + shift - b[h] as f64).abs() < 1e-5,
                    "node {node} seat {p} class {h}: {} vs {}",
                    a[h],
                    b[h]
                );
            }
        }
    }
    // Regrets are differences between actions, so what a seat already paid
    // drops out: step for step the two solves match to float noise. (Run
    // long enough, near-zero regrets cross at different moments and mixed
    // frequencies fork, exactly as they do after a change of one
    // ten-millionth of a bb to the ante; this stops well before that.)
    each.prune = false;
    bb.prune = false;
    for _ in 0..20 {
        each.iterate();
        bb.iterate();
    }
    let (ra, rb) = (each.arena_snapshot().0, bb.arena_snapshot().0);
    let worst = ra
        .iter()
        .zip(&rb)
        .map(|(x, y)| (x - y).abs())
        .fold(0.0f32, f32::max);
    assert!(worst < 1e-3, "regrets differ beyond float noise: {worst}");
    for node in (0..each.nodes.len()).filter(|&i| each.nodes[i].kind == KIND_ACTION) {
        let (x, y) = (each.average_strategy(node), bb.average_strategy(node));
        // A class whose regrets sit at zero can tip either way on float
        // noise, so the node is compared as a whole, not class by class.
        let mean = x.iter().zip(&y).map(|(x, y)| (x - y).abs()).sum::<f32>() / x.len() as f32;
        assert!(
            mean < 1e-3,
            "node {node}: strategies differ by {mean} on average"
        );
    }
    // The big blind paid 1 where it used to pay a quarter; the others pay nothing.
    let (x, y) = (each.evs(), bb.evs());
    for p in 0..4 {
        let paid = if p == 3 { 1.0 } else { 0.0 };
        assert!(
            (x[p] + 0.25 - paid - y[p]).abs() < 1e-3,
            "seat {p}: {} vs {}",
            x[p],
            y[p]
        );
    }
}

#[test]
fn side_pots_put_the_ante_in_the_main_pot() {
    let three = |stacks: [f64; 3], opens: &[f64]| {
        cfg(serde_json::json!({
            "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
            "stack": stacks.iter().cloned().fold(0.0, f64::max), "stacks": stacks, "bb_ante": 1.0,
            "open_raises": opens, "raise_mults": [3.0], "max_raises": 3,
            "add_allin": true, "realization": "raw"
        }))
    };
    // Everyone all-in: 10 from each plus the ante in the main pot, the rest
    // between the two deep stacks.
    let s = PreflopSolver::new(three([30.0, 10.0, 30.0], &[2.5]), table()).unwrap();
    let nd = &s.nodes[walk(&s, &["All-in 30", "Call all-in 10", "Call 30"])];
    assert_eq!(nd.invested, vec![30.0, 10.0, 31.0]);
    assert_eq!(nd.side_pots, vec![(31.0, 0b111), (40.0, 0b101)]);
    assert_eq!(nd.pot, 71.0);
    // BB's jam over a folded 20 and a 10 all-in: 30 comes back, the ante stays.
    let s = PreflopSolver::new(three([50.0, 10.0, 50.0], &[20.0]), table()).unwrap();
    let nd = &s.nodes[walk(&s, &["Raise 20", "Call all-in 10", "All-in 50", "Fold"])];
    assert_eq!(nd.invested, vec![20.0, 10.0, 21.0]);
    assert_eq!(nd.side_pots, vec![(31.0, 0b110), (20.0, 0b100)]);
    // Heads-up with a short big blind: the button's extra chips come back.
    let c = cfg(serde_json::json!({
        "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": 40.0, "stacks": [40.0, 25.0],
        "bb_ante": 1.0, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2,
        "add_allin": true, "realization": "raw"
    }));
    let s = PreflopSolver::new(c, table()).unwrap();
    let nd = &s.nodes[walk(&s, &["All-in 25", "Call"])];
    assert_eq!((nd.invested.clone(), nd.pot), (vec![25.0, 26.0], 51.0));
    assert!(nd.side_pots.is_empty());
}

#[test]
fn payoffs_conserve_chips_net_of_rake() {
    let c = cfg(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0],
        "stack": 30.0, "stacks": [12.0, 30.0, 6.0, 20.0], "ante": 0.1, "bb_ante": 0.7,
        "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
        "add_allin": true, "realization": "static",
        "rake_pct": 5.0, "rake_cap": 3.0, "no_flop_no_drop": false
    }));
    let mut s = PreflopSolver::new(c.clone(), table()).unwrap();
    assert_eq!(estimate_tree(&c).unwrap().nodes as usize, s.nodes.len());
    let w = weights(4);
    let probability: f64 = w.iter().map(|w| w.iter().sum::<f32>() as f64).product();
    let (mut layered, mut folds) = (0, 0);
    for (node, nd) in s.nodes.iter().enumerate() {
        if nd.kind == KIND_ACTION {
            continue;
        }
        assert!((nd.invested.iter().sum::<f64>() - nd.pot).abs() < 1e-9);
        let exact = match nd.kind {
            KIND_FOLD_WIN => {
                folds += 1;
                Some(s.fold_win_rake(nd))
            }
            _ if !nd.side_pots.is_empty() => {
                layered += 1;
                let in_pots: f64 = nd.side_pots.iter().map(|p| p.0).sum();
                assert!(
                    (in_pots - nd.pot).abs() < 1e-9,
                    "pots {in_pots} vs {}",
                    nd.pot
                );
                Some(s.rake_of(nd.pot))
            }
            // the static skew on other pots is the model's own approximation
            _ => None,
        };
        let Some(rake) = exact else { continue };
        let mut total = 0.0;
        for p in 0..4 {
            let mut values = [0.0f32; NUM_CLASSES];
            s.terminal_value(node, p, &w, &mut values);
            // fold-win values are one number per seat times the others' reach
            total += values
                .iter()
                .zip(&w[p])
                .map(|(v, w)| *v as f64 * *w as f64)
                .sum::<f64>();
        }
        assert!(
            (total + probability * rake).abs() < 1e-5,
            "node {node}: {total} vs {}",
            -probability * rake
        );
    }
    assert!(
        layered > 10 && folds > 10,
        "{layered} side-pot and {folds} fold terminals"
    );
    for _ in 0..10 {
        s.iterate();
    }
    assert!(s.evs().iter().all(|v| v.is_finite()));
    assert!(s.br_gaps().iter().all(|g| g.is_finite() && *g >= -1e-6));
}

#[test]
fn tournament_payouts_count_the_ante_in_the_big_blinds_stack() {
    let mut c = four(0.0, 1.0);
    (c.rake_pct, c.rake_cap, c.no_flop_no_drop) = (0.0, 0.0, true);
    c.icm = Some(IcmConfig {
        payouts: vec![100.0],
        field: vec![25.0],
        field_groups: vec![],
        stack_off: 1.0,
    });
    let chip = {
        let mut c = c.clone();
        c.icm = None;
        PreflopSolver::new(c, table()).unwrap()
    };
    let icm = PreflopSolver::new(c, table()).unwrap();
    // four 30 bb stacks, the ante the big blind paid on top, and the field
    assert!((icm.icm.as_ref().unwrap().scale - (4.0 * 30.0 + 1.0 + 25.0) / 100.0).abs() < 1e-12);
    // winner-take-all prizes are linear in chips: every terminal pays its chips
    let w = weights(4);
    let (mut a, mut b) = ([0f32; NUM_CLASSES], [0f32; NUM_CLASSES]);
    for node in (0..chip.nodes.len()).filter(|&i| chip.nodes[i].kind != KIND_ACTION) {
        for p in 0..4 {
            chip.terminal_value(node, p, &w, &mut a);
            icm.terminal_value(node, p, &w, &mut b);
            assert!(
                (0..NUM_CLASSES).all(|h| (a[h] - b[h]).abs() <= 2e-4 * a[h].abs().max(1.0)),
                "node {node} seat {p}"
            );
        }
    }
}

#[test]
fn saves_use_v8_and_round_trip() {
    let mut s = PreflopSolver::new(four(0.0, 1.0), table()).unwrap();
    for _ in 0..3 {
        s.iterate();
    }
    let path =
        std::env::temp_dir().join(format!("gtopen-bb-ante-save-{}.gtop", std::process::id()));
    let path = path.to_str().unwrap();
    s.save_game(path).unwrap();
    let bytes = std::fs::read(path).unwrap();
    assert_eq!(&bytes[..12], super::save::MAGIC_BB_ANTE);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert_eq!(loaded.cfg.bb_ante, 1.0);
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    // A v8 file whose header lost the ante must not continue as another game.
    let end = 12 + bytes[12..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[12..end]).unwrap();
    header["config"].as_object_mut().unwrap().remove("bb_ante");
    let mut out = bytes[..12].to_vec();
    out.extend(serde_json::to_vec(&header).unwrap());
    out.extend_from_slice(&bytes[end..]);
    std::fs::write(path, out).unwrap();
    assert!(PreflopSolver::load_game(path, table())
        .err()
        .unwrap()
        .contains("v8"));
    // Without one the config and the file are what they always were.
    let old = PreflopSolver::new(four(0.25, 0.0), table()).unwrap();
    assert!(!serde_json::to_string(&old.cfg).unwrap().contains("bb_ante"));
    old.save_game(path).unwrap();
    assert_ne!(
        &std::fs::read(path).unwrap()[..12],
        super::save::MAGIC_BB_ANTE
    );
    std::fs::remove_file(path).unwrap();
}

#[test]
fn a_bad_big_blind_ante_is_refused() {
    for bad in [-0.5, f64::NAN, f64::INFINITY] {
        let mut c = four(0.0, 1.0);
        c.bb_ante = bad;
        assert!(validate(&c).unwrap_err().contains("bb_ante"));
    }
}
