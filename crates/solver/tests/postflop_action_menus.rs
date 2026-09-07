//! Frozen action-count and algorithm controls for CUDA specialization.
#![cfg(feature = "gpu")]
use solver::gpu::GpuSolver;
use solver::{Solver, Spot, SpotConfig, TreeConfig, StreetSizing, parse_sizes, LockMode};
use solver::cfr::Algorithm;
use std::sync::Arc;
fn hash(bytes: &[u8]) -> String {
    format!("{:016x}",bytes.iter().fold(0xcbf29ce484222325u64,|h,b|(h ^ *b as u64).wrapping_mul(0x100000001b3)))
}
#[test]
#[ignore = "manual CUDA action-menu and algorithm fingerprints"]
fn postflop_action_menus() {
    let file=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("target/research-fixtures/action-menus.gto");
    std::fs::create_dir_all(file.parent().unwrap()).unwrap();
    for bets in ["", "50", "33 75", "25 50 100", "20 40 60 100", "10 20 30 40 50 60 70 80 90 100"] {
        for algo in [Algorithm::Dcfr, Algorithm::CfrPlus] {
            let sizing=||StreetSizing{bet:parse_sizes(bets).unwrap(),raise:vec![],donk:vec![]};
            let mut s=Solver::new(Arc::new(Spot::new(SpotConfig{
                board:"Ks7h2dQhTc".into(),range_oop:"AA,KK,QQ,JJ,AKs,AQs,AKo,98s".into(),
                range_ip:"AA,QQ,TT,77,AQs,KQs,AQo,JTs".into(),
                tree:TreeConfig{starting_pot:10.0,effective_stack:100.0,rake_pct:0.05,rake_cap:1.0,
                    oop:[sizing(),sizing(),sizing()],ip:[sizing(),sizing(),sizing()],..Default::default()}
            }).unwrap()));
            s.algo=algo;
            let mut gpu=GpuSolver::new(&s).unwrap();
            for _ in 0..40 {gpu.iterate().unwrap();}
            let mut states=Vec::new();
            for locked in [false,true] {
                if locked {
                    s.lock_node(&[],LockMode::Freeze,"menu control".into()).unwrap();
                    gpu.update_locks(&s).unwrap();
                    for _ in 0..17 {gpu.iterate().unwrap();}
                }
                gpu.sync_to_cpu(&mut s).unwrap();
                let exploit_bits=gpu.exploitability(&s).unwrap().to_bits();
                s.save(file.to_str().unwrap()).unwrap();
                states.push(serde_json::json!({"locked":locked,"hash":hash(&std::fs::read(&file).unwrap()),"exploit_bits":exploit_bits}));
            }
            println!("METRIC_JSON {}",serde_json::json!({"metrics":{},"bets":bets,"algorithm":format!("{algo:?}"),
                "root_actions":s.spot.tree.nodes[0].num_children,"menu_states":states}));
        }
    }
}
