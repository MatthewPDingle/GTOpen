//! Fixed capacity and initialization controls added before reach-storage trials.
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

fn main() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let eq = Arc::new(EquityTable::load_or_build(path, 20000));
    for n in [6, 8] {
        let mut posts = vec![0.0; n];
        posts[n-2] = 0.5;
        posts[n-1] = 1.0;
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
            "stack":if n==8 {150.0} else {100.0}, "posts":posts, "limp":true,
            "open_raises":[2.5,4.0], "raise_mults":[3.0], "max_raises":if n==8 {2} else {3},
            "allin_threshold":0.85, "add_allin":false, "rake_pct":5.0, "rake_cap":3.0,
            "realization":if n==6 {"static"} else {"calibrated"}
        })).unwrap();
        let start = Instant::now();
        let s = PreflopSolver::new(cfg, eq.clone()).unwrap();
        let build_ms = start.elapsed().as_secs_f64() * 1000.0;
        let nodes=s.nodes.len();
        let mut sources=vec![0usize; nodes*n];
        for q in 0..n {sources[q]=q;}
        for (i,node) in s.nodes.iter().enumerate() {
            if node.kind!=0 {continue;}
            for a in 0..node.actions.len() {
                let c=s.child(i,a);
                sources.copy_within(i*n..(i+1)*n,c*n);
                sources[c*n+node.actor as usize]=n+c-1;
            }
        }
        let mut needed:Vec<std::collections::HashSet<usize>>=(0..n).map(|_|std::collections::HashSet::new()).collect();
        let mut dots=0usize;
        for (i,node) in s.nodes.iter().enumerate() {
            if node.kind!=2 {continue;}
            for p in 0..n {
                if (node.live>>p)&1==0 {continue;}
                for q in 0..n {
                    if q!=p && (node.live>>q)&1!=0 {
                        needed[p].insert(sources[i*n+q]);
                        dots+=1;
                    }
                }
            }
        }
        let union:std::collections::HashSet<_>=needed.iter().flatten().copied().collect();
        println!("seats={n} nodes={nodes} build_ms={build_ms:.2} current_equity_dots={dots} cached_learning_dots={} cached_evaluation_dots={} cache_MB={:.3}",needed.iter().map(|s|s.len()).sum::<usize>(),union.len(),union.len() as f64*169.0*4.0/1e6);
    }
}
