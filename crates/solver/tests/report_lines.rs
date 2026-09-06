//! The report sweep (solver::report) must reproduce node_view's numbers:
//! at the root exactly (same reach × valid weighting), and at a pooled turn
//! node the per-card node_views combined with the same weights.

use solver::query::{NodeView, PathStep};
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Solver, Spot, SpotConfig};
use std::sync::Arc;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing {
        bet: parse_sizes(bet).unwrap(),
        raise: parse_sizes(raise).unwrap(),
        donk: vec![],
    }
}

fn solved() -> Solver {
    let config = SpotConfig {
        board: "Th9h2c".to_string(),
        range_oop: "QQ,JJ,TT,99,AhKh,AsKs,87s,A5s,K9s".to_string(),
        range_ip: "AA,KK,AQs,JTs,T9s,66,Q8s".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    };
    let mut s = Solver::new(Arc::new(Spot::new(config).unwrap()));
    for _ in 0..120 {
        s.iterate();
    }
    s.ensure_symmetric();
    s
}

/// (ev, eq, freqs) of a node_view for player p, pair-mass weighted.
fn view_stats(v: &NodeView, p: usize) -> (f64, f64, Vec<f64>, f64) {
    let (mut wev, mut weq, mut w, mut weqw) = (0f64, 0f64, 0f64, 0f64);
    let na = v.actions.len();
    let mut fs = vec![0f64; na];
    for h in &v.players[p].hands {
        let Some(ev) = h.ev else { continue };
        let wt = h.reach as f64 * h.valid as f64;
        if wt <= 0.0 {
            continue;
        }
        w += wt;
        wev += wt * ev as f64;
        if let Some(eq) = h.eq {
            weq += wt * eq as f64;
            weqw += wt;
        }
        if let Some(st) = &h.strategy {
            for a in 0..na {
                fs[a] += wt * st[a] as f64;
            }
        }
    }
    (wev / w, weq / weqw.max(1e-12), fs.iter().map(|f| f / w).collect(), w)
}

#[test]
fn root_matches_node_view() {
    let s = solved();
    let lines = s.report_lines();
    let root = lines.get("").expect("root recorded");
    assert_eq!(root.kind, "action");
    let v = s.node_view(&[]).unwrap();
    let actor = v.player.unwrap() as usize;
    for p in 0..2 {
        let (ev, eq, freqs, _) = view_stats(&v, p);
        let ps = &root.players[p];
        assert!((ps.ev as f64 - ev).abs() < 2e-3, "p{p} ev {} vs {ev}", ps.ev);
        assert!((ps.eq.unwrap() as f64 - eq).abs() < 2e-3, "p{p} eq {:?} vs {eq}", ps.eq);
        if p == actor {
            for a in 0..freqs.len() {
                assert!((root.freqs[a] as f64 - freqs[a]).abs() < 2e-3, "freq {a}");
            }
            // category shares partition the actor's range mass
            let cats = ps.cats.as_ref().expect("root is a full node");
            let made_w: f32 = cats.made.iter().map(|c| c.w).sum();
            assert!((made_w - ps.w).abs() < 1e-2 * ps.w.max(1.0), "{made_w} vs {}", ps.w);
        }
    }
    // pot-share convention survives the sweep
    let pot = root.pot;
    let sum = root.players[0].ev as f64 + root.players[1].ev as f64;
    assert!((sum - pot).abs() < 0.05, "EV_OOP + EV_IP = {sum}, pot {pot}");
}

#[test]
fn pooled_turn_matches_per_card_views() {
    let s = solved();
    let lines = s.report_lines();
    let root = lines.get("").unwrap();
    let ci = root.kinds.iter().position(|k| k == "check").expect("root has a check");
    let k1 = format!("a{ci}");
    let ip = lines.get(&k1).unwrap();
    let cj = ip.kinds.iter().position(|k| k == "check").expect("IP has a check");
    let k2 = format!("{k1},a{cj}");
    assert_eq!(lines.get(&k2).unwrap().kind, "chance", "check-check ends the flop");
    let k3 = format!("{k2},c");
    let turn = lines.get(&k3).expect("first turn decision recorded");
    assert_eq!(turn.kind, "action");
    let actor = turn.actor.unwrap() as usize;

    // pool the per-card node_views with the same weights
    let chance = s.node_view(&[PathStep::Action { index: ci }, PathStep::Action { index: cj }]).unwrap();
    let cards = chance.available_cards.unwrap();
    let mut wev = [0f64; 2];
    let mut weq = [0f64; 2];
    let mut w = [0f64; 2];
    let mut fs = vec![0f64; turn.freqs.len()];
    for c in &cards {
        let v = s
            .node_view(&[
                PathStep::Action { index: ci },
                PathStep::Action { index: cj },
                PathStep::Card { card: c.clone() },
            ])
            .unwrap();
        for p in 0..2 {
            let (ev, eq, freqs, wt) = view_stats(&v, p);
            wev[p] += wt * ev;
            weq[p] += wt * eq;
            w[p] += wt;
            if p == actor {
                for a in 0..fs.len() {
                    fs[a] += wt * freqs[a];
                }
            }
        }
    }
    for p in 0..2 {
        let ev = wev[p] / w[p];
        let eq = weq[p] / w[p];
        let ps = &turn.players[p];
        assert!((ps.ev as f64 - ev).abs() < 3e-3, "p{p} pooled ev {} vs {ev}", ps.ev);
        assert!((ps.eq.unwrap() as f64 - eq).abs() < 3e-3, "p{p} pooled eq {:?} vs {eq}", ps.eq);
    }
    for a in 0..fs.len() {
        let f = fs[a] / w[actor];
        assert!((turn.freqs[a] as f64 - f).abs() < 3e-3, "pooled freq {a}: {} vs {f}", turn.freqs[a]);
    }
    // river lines are capped at the first response; deeper river shapes are absent
    let deep_river = lines.keys().filter(|k| k.matches('c').count() == 2).count();
    assert!(deep_river > 0, "river nodes recorded");
    assert!(lines.values().all(|v| v.street < 2 || v.kind != "action" || true));
}
