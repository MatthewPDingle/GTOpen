//! Frozen seat/action-count controls before CUDA specialization trials.
#![cfg(feature = "gpu")]
use solver::preflop::{equity::EquityTable, gpu::PreflopGpu, PreflopConfig, PreflopSolver};
use std::sync::Arc;
fn fingerprint(s: &PreflopSolver) -> String {
    let (r,t)=s.arena_snapshot();
    let h=r.iter().chain(&t).flat_map(|v|v.to_bits().to_le_bytes()).fold(0xcbf29ce484222325u64,|h,b|(h ^ b as u64).wrapping_mul(0x100000001b3));
    format!("{h:016x}")
}
#[test]
#[ignore = "manual exact preflop seat/menu/override controls"]
fn preflop_variants() {
    let eq=Arc::new(EquityTable::load_or_build(concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin"),20000));
    for n in 2..=9 {
        for wide in [false,true] {
            let mut posts=vec![0.0;n];posts[n-2]=0.5;posts[n-1]=1.0;
            let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
                "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
                "stack":40.0,"posts":posts,"limp":false,
                "open_raises":if wide {vec![2.0,2.5,3.0,3.5,4.0]} else {vec![2.5,4.0]},
                "raise_mults":[3.0],"max_raises":1,"add_allin":false,
                "rake_pct":5.0,"rake_cap":3.0,"realization":if n%2==0 {"static"}else{"raw"}
            })).unwrap();
            let mut s=PreflopSolver::new(cfg,eq.clone()).unwrap();
            let mut states=Vec::new();
            for phase in ["plain","frozen","hero_locked"] {
                if phase=="frozen" {
                    let mut frozen=vec![false;n];frozen[n-1]=true;
                    s.set_table_keep(frozen,vec![None;n]).unwrap();
                } else if phase=="hero_locked" {
                    s.lock_point(&[],None).unwrap();
                    s.set_hero(Some(n-2)).unwrap();
                }
                let mut gpu=PreflopGpu::new(&s,20000).unwrap();
                for _ in 0..25 {gpu.iterate(&mut s).unwrap();}
                let (gaps,evs)=gpu.gaps_and_evs().unwrap();
                gpu.sync_to_cpu(&mut s).unwrap();
                states.push(serde_json::json!({"phase":phase,"iteration":s.iteration,"hash":fingerprint(&s),
                    "gap_bits":gaps.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),
                    "ev_bits":evs.iter().map(|v|v.to_bits()).collect::<Vec<_>>()}));
            }
            println!("METRIC_JSON {}",serde_json::json!({"metrics":{},"seats":n,"wide":wide,"variant_states":states}));
        }
    }
}
