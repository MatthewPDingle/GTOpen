//! Fixed complete-state controls, added after deterministic folds and before CFV compaction.
#![cfg(feature = "gpu")]
use solver::gpu::GpuSolver;
use solver::{Solver, Spot, SpotConfig, TreeConfig, StreetSizing, parse_sizes, LockMode, PathStep};
use std::sync::Arc;
fn hash(bytes: &[u8]) -> String {
    format!("{:016x}", bytes.iter().fold(0xcbf29ce484222325u64, |h,b| (h ^ *b as u64).wrapping_mul(0x100000001b3)))
}
#[test]
#[ignore = "manual complete postflop state fingerprints"]
fn postflop_states() {
    let file = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("target/research-fixtures/postflop-state.gto");
    std::fs::create_dir_all(file.parent().unwrap()).unwrap();
    for board in ["KsQs2d", "Qs7h2dKh", "AsKsQsJsTs"] {
        for iso in [false, true] {
            for rake in [0.0, 0.05] {
                let sizing = || StreetSizing { bet:parse_sizes("50").unwrap(), raise:vec![], donk:vec![] };
                let mut s = Solver::new(Arc::new(Spot::new(SpotConfig {
                    board:board.into(),
                    range_oop:"AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),
                    range_ip:"AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
                    tree:TreeConfig { starting_pot:10.0,effective_stack:20.0,rake_pct:rake,rake_cap:1.0,
                        oop:[sizing(),sizing(),sizing()],ip:[sizing(),sizing(),sizing()],..Default::default() }
                }).unwrap()));
                s.use_isomorphism=iso;
                let mut gpu=GpuSolver::new(&s).unwrap();
                for _ in 0..40 { gpu.iterate().unwrap(); }
                let mut states=Vec::new();
                for locked in [false,true] {
                    if locked {
                        s.lock_node(&[PathStep::Action{index:0}],LockMode::Freeze,"state control".into()).unwrap();
                        gpu.update_locks(&s).unwrap();
                        for _ in 0..20 {gpu.iterate().unwrap();}
                    }
                    gpu.sync_to_cpu(&mut s).unwrap();
                    let exploit=gpu.exploitability(&s).unwrap();
                    s.save(&file).unwrap();
                    states.push(serde_json::json!({"locked":locked,"hash":hash(&std::fs::read(&file).unwrap()),"exploit_bits":exploit.to_bits()}));
                }
                println!("METRIC_JSON {}",serde_json::json!({"metrics":{},"board":board,"iso":iso,"rake":rake,"states":states}));
            }
        }
    }
}
