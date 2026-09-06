//! Generate `crates/solver/src/preflop/reference.rs`: GTO reference
//! propensities per hand class (open first-in, defend vs an open by calling,
//! 3-bet) from one clean 9-max 100bb no-limp solve. The profile generator
//! orders its ranges by these instead of by the current (possibly ruled,
//! possibly unconverged) solve. Run from the repo root:
//!
//!   cargo run --release -p solver --example reference_order -- [iterations]
use solver::preflop::equity::{class_label, class_prob, EquityTable, NUM_CLASSES};
use solver::preflop::{PreflopConfig, PreflopSolver};
use std::fmt::Write as _;
use std::sync::Arc;

fn main() {
    let iters: u32 = std::env::args().nth(1).and_then(|v| v.parse().ok()).unwrap_or(600);
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20_000));
    let positions = ["UTG", "UTG1", "UTG2", "LJ", "HJ", "CO", "BTN", "SB", "BB"];
    let cfg = PreflopConfig {
        positions: positions.iter().map(|s| s.to_string()).collect(),
        stack: 100.0,
        posts: vec![0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0],
        ante: 0.0,
        limp: false,
        open_raises: vec![2.5],
        raise_mults: vec![3.0],
        max_raises: 3,
        add_allin: true,
        allin_threshold: 0.85,
        rake_pct: 0.0,
        rake_cap: 0.0,
        no_flop_no_drop: true,
        realization: "calibrated".into(),
        call_only_seats: vec![],
        open_raises_by_seat: None,
        raise_mults_by_seat: None,
    };
    let mut s = PreflopSolver::new(cfg, eq.clone()).expect("build tree");
    eprintln!("nodes {} · calibrated fit loaded: {}", s.nodes.len(), s.fit.is_some());
    let t0 = std::time::Instant::now();
    let mut gap_total = f64::NAN;
    for i in 1..=iters {
        s.iterate();
        if i % 50 == 0 || i == iters {
            let gaps = s.br_gaps();
            gap_total = gaps.iter().sum::<f64>();
            eprintln!("iter {i} · BR gap total {gap_total:.4} bb · {:.0}s", t0.elapsed().as_secs_f64());
        }
    }

    let n = positions.len();
    let is_raise = |kind: &str| !matches!(kind, "fold" | "call" | "check");
    let act = |s: &PreflopSolver, node: usize, kind: &str| {
        s.nodes[node].actions.iter().position(|a| a.kind == kind)
    };
    let mut open = vec![0f64; NUM_CLASSES];
    let mut call = vec![0f64; NUM_CLASSES];
    let mut three = vec![0f64; NUM_CLASSES];
    let (mut open_n, mut def_n) = (0usize, 0usize);
    let mut rfi_lines = Vec::new();
    let mut node = 0usize; // first-in node of seat q (q prior folds)
    for q in 0..n - 1 {
        let nd = &s.nodes[node];
        assert_eq!(nd.actor as usize, q, "first-in node actor");
        let sigma = s.average_strategy(node);
        let raise_is: Vec<usize> =
            nd.actions.iter().enumerate().filter(|(_, a)| is_raise(&a.kind)).map(|(i, _)| i).collect();
        let mut pct = 0f64;
        for h in 0..NUM_CLASSES {
            let p: f64 = raise_is.iter().map(|&a| sigma[a * NUM_CLASSES + h] as f64).sum();
            open[h] += p;
            pct += p * class_prob(h) as f64;
        }
        open_n += 1;
        rfi_lines.push(format!("{} {:.1}%", positions[q], pct * 100.0));
        // cold defenders vs this open: d = q+1.. with everyone between folding
        let raise_first = act(&s, node, "raise").expect("open raise");
        let mut dnode = s.child(node, raise_first);
        let mut def_pcts = Vec::new();
        for d in q + 1..n {
            let dn = &s.nodes[dnode];
            assert_eq!(dn.actor as usize, d, "defender node actor");
            let sig = s.average_strategy(dnode);
            let call_i = act(&s, dnode, "call").expect("call vs open");
            let raise_is: Vec<usize> =
                dn.actions.iter().enumerate().filter(|(_, a)| is_raise(&a.kind)).map(|(i, _)| i).collect();
            let (mut cp, mut rp) = (0f64, 0f64);
            for h in 0..NUM_CLASSES {
                let c = sig[call_i * NUM_CLASSES + h] as f64;
                let r: f64 = raise_is.iter().map(|&a| sig[a * NUM_CLASSES + h] as f64).sum();
                call[h] += c;
                three[h] += r;
                cp += c * class_prob(h) as f64;
                rp += r * class_prob(h) as f64;
            }
            def_n += 1;
            def_pcts.push(format!("{} call {:.1}/3b {:.1}", positions[d], cp * 100.0, rp * 100.0));
            if d + 1 < n {
                let fold_i = act(&s, dnode, "fold").expect("fold vs open");
                dnode = s.child(dnode, fold_i);
            }
        }
        rfi_lines.push(format!("   vs {} open: {}", positions[q], def_pcts.join(" · ")));
        let fold_i = act(&s, node, "fold").expect("fold first-in");
        node = s.child(node, fold_i);
    }
    for h in 0..NUM_CLASSES {
        open[h] /= open_n as f64;
        call[h] /= def_n as f64;
        three[h] /= def_n as f64;
    }
    // strength = equity vs a random hand (card appeal), for the printout
    let strength: Vec<f64> = (0..NUM_CLASSES)
        .map(|h| (0..NUM_CLASSES).map(|j| class_prob(j) as f64 * eq.eq(h, j) as f64).sum())
        .collect();

    println!("RFI by seat:");
    for l in &rfi_lines {
        println!("  {l}");
    }
    let mut order: Vec<usize> = (0..NUM_CLASSES).collect();
    order.sort_by(|&a, &b| open[b].partial_cmp(&open[a]).unwrap().then(strength[b].partial_cmp(&strength[a]).unwrap()));
    println!("\nopen order (mean P(open|class) over 8 first-in seats), with 3-bet / call means:");
    for (k, &h) in order.iter().enumerate() {
        if k % 6 == 0 {
            println!();
        }
        print!("{:>4} {:.2}/{:.2}/{:.2}  ", class_label(h), open[h], three[h], call[h]);
    }
    println!();

    let mut out = String::new();
    writeln!(out, "//! GENERATED by `cargo run --release -p solver --example reference_order` — do not edit.").unwrap();
    writeln!(out, "//!").unwrap();
    writeln!(out, "//! GTO reference propensities per hand class (index = class index, see").unwrap();
    writeln!(out, "//! equity.rs) from a clean 9-max 100bb no-limp solve: 2.5x open, 3x").unwrap();
    writeln!(out, "//! re-raises, 3-raise cap + jam, no rake, calibrated realization,").unwrap();
    writeln!(out, "//! {iters} DCFR iterations, total best-response gap {gap_total:.4} bb.").unwrap();
    writeln!(out, "//!").unwrap();
    writeln!(out, "//! - OPEN_SCORE: mean over the 8 first-in seats (UTG..SB) of P(open-raise | class)").unwrap();
    writeln!(out, "//! - CALL_SCORE / THREEBET_SCORE: mean over every (opener, cold defender) pair").unwrap();
    writeln!(out, "//!   of P(call | class) / P(3-bet or jam | class)").unwrap();
    writeln!(out, "//!").unwrap();
    writeln!(out, "//! The profile generator orders its ranges by these (blended toward raw card").unwrap();
    writeln!(out, "//! appeal by naiveté) instead of by the current solve.").unwrap();
    for (name, v) in [("OPEN_SCORE", &open), ("CALL_SCORE", &call), ("THREEBET_SCORE", &three)] {
        writeln!(out, "\n#[rustfmt::skip]\npub const {name}: [f32; {NUM_CLASSES}] = [").unwrap();
        for h in 0..NUM_CLASSES {
            writeln!(out, "    {:.4}, // {}", v[h], class_label(h)).unwrap();
        }
        writeln!(out, "];").unwrap();
    }
    std::fs::write("crates/solver/src/preflop/reference.rs", out).expect("write reference.rs");
    eprintln!("wrote crates/solver/src/preflop/reference.rs");
}
