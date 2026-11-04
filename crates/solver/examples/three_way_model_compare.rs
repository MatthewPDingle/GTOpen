//! Solve the same 3-handed spots under the coupled-deck model and the exact
//! 3-way table (three_way_table_v1) and print how far the answers move.
//!
//!     cargo run --release -p solver --features gpu --example three_way_model_compare [iterations]
//!
//! The first run builds cache/preflop_eq169x3.bin (a few minutes) unless it
//! exists. Without the gpu feature, solves run on CPU.
use solver::preflop::equity::{class_label, EquityTable, NUM_CLASSES};
use solver::preflop::{PreflopConfig, PreflopSolver};
use std::sync::Arc;

fn solve(cfg: &PreflopConfig, eq: &Arc<EquityTable>, table: bool, iterations: usize) -> (PreflopSolver, &'static str) {
    let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
    if table {
        s.set_multiway_equity_model(solver::preflop::three_way::MODEL).unwrap();
    }
    #[cfg(feature = "gpu")]
    if let Ok(mut g) = solver::preflop::gpu::PreflopGpu::new(&s, 16_000) {
        for _ in 0..iterations { g.iterate(&mut s).unwrap(); }
        g.sync_to_cpu(&mut s).unwrap();
        return (s, "gpu");
    }
    for _ in 0..iterations { s.iterate(); }
    (s, "cpu")
}

/// Action paths of at most `depth` actions, breadth first.
fn paths(s: &PreflopSolver, depth: usize) -> Vec<Vec<usize>> {
    let mut out = vec![vec![]];
    let mut at = 0;
    while at < out.len() {
        let path = out[at].clone();
        at += 1;
        let (node, _) = s.walk(&path).unwrap();
        if path.len() == depth || s.nodes[node].kind != 0 { continue; }
        for a in 0..s.nodes[node].actions.len() {
            let (child, _) = s.walk(&[path.clone(), vec![a]].concat()).unwrap();
            if s.nodes[child].kind == 0 { let mut p = path.clone(); p.push(a); out.push(p); }
        }
    }
    out
}

fn main() {
    let iterations: usize = std::env::args().nth(1).and_then(|v| v.parse().ok()).unwrap_or(600);
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20_000));
    let base = serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2, "add_allin": true,
        "limp": true, "rake_pct": 5.0, "rake_cap": 3.0, "realization": "raw"
    });
    let spot = |patch: serde_json::Value| {
        let mut v = base.clone();
        for (k, x) in patch.as_object().unwrap() { v[k] = x.clone(); }
        serde_json::from_value::<PreflopConfig>(v).unwrap()
    };
    let spots = [
        ("3-handed 15bb", spot(serde_json::json!({"stack": 15.0}))),
        ("3-handed 40bb", spot(serde_json::json!({"stack": 40.0}))),
        ("3-handed 40bb, SB 8bb", spot(serde_json::json!({"stack": 40.0, "stacks": [40.0, 8.0, 40.0]}))),
    ];
    for (name, cfg) in spots {
        let (coupled, engine) = solve(&cfg, &eq, false, iterations);
        let (table, _) = solve(&cfg, &eq, true, iterations);
        let gaps = |s: &PreflopSolver| s.br_gaps().iter().sum::<f64>();
        println!("\n== {name}: {} nodes, {iterations} iterations on {engine}", coupled.nodes.len());
        println!("   BR gap coupled {:.4} / table {:.4} bb", gaps(&coupled), gaps(&table));
        let (ec, et) = (coupled.evs(), table.evs());
        for (p, pos) in cfg.positions.iter().enumerate() {
            println!("   EV {pos:>3}: coupled {:+.4}  table {:+.4}  ({:+.4})", ec[p], et[p], et[p] - ec[p]);
        }
        let mut worst: Vec<(f32, String)> = Vec::new();
        for path in paths(&coupled, 3) {
            let (vc, vt) = (coupled.node_view(&path).unwrap(), table.node_view(&path).unwrap());
            let line: Vec<String> = {
                let mut node = 0;
                path.iter().map(|&a| { let l = coupled.nodes[node].actions[a].label.clone(); node = coupled.child(node, a); l }).collect()
            };
            let who = vc.actor_pos.clone().unwrap_or_default();
            let freqs: Vec<String> = vc.actions.iter().zip(&vt.actions)
                .map(|(c, t)| format!("{} {:.1}%→{:.1}%", c.label, 100.0 * c.freq, 100.0 * t.freq)).collect();
            println!("   [{}] {who}: {}", line.join(" · "), freqs.join(", "));
            let (node, _) = coupled.walk(&path).unwrap();
            let (sc, st) = (coupled.average_strategy(node), table.average_strategy(node));
            for (a, act) in coupled.nodes[node].actions.iter().enumerate() {
                for h in 0..NUM_CLASSES {
                    let d = st[a * NUM_CLASSES + h] - sc[a * NUM_CLASSES + h];
                    if a + 1 < coupled.nodes[node].actions.len() || coupled.nodes[node].actions.len() == 1 {
                        worst.push((d.abs(), format!("[{}] {who} {} {}: {:.0}%→{:.0}%", line.join(" · "), class_label(h), act.label,
                            100.0 * sc[a * NUM_CLASSES + h], 100.0 * st[a * NUM_CLASSES + h])));
                    }
                }
            }
        }
        worst.sort_by(|a, b| b.0.total_cmp(&a.0));
        let moved = worst.iter().filter(|w| w.0 > 0.25).count();
        println!("   hand-level moves over 25 points: {moved}; largest:");
        for (_, w) in worst.iter().take(12) { println!("     {w}"); }
    }
}
