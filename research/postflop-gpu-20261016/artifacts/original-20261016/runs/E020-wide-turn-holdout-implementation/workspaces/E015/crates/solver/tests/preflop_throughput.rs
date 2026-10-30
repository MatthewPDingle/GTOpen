//! Retained-path qualification in the normal GPU build, without research features.
#![cfg(all(feature = "gpu", not(feature = "preflop-research")))]
use solver::preflop::{PreflopConfig,PreflopSolver,equity::EquityTable,gpu::PreflopGpu};
use std::sync::{Arc,atomic::AtomicBool};

#[test]
fn production_selection_matches_reference_and_falls_back_with_small_budget() {
    let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
    let data=std::fs::read(path).unwrap();
    let eq=Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(data[..4].try_into().unwrap())));
    for n in [2,4] {for budget in [128,2000] {
        let mut posts=vec![0.;n];posts[n-2]=0.5;posts[n-1]=1.;
        let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
            "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
            "stack":10,"posts":posts,"limp":true,"open_raises":[2],"raise_mults":[],
            "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"
        })).unwrap();
        let mut expected=None;
        for selected in [false,true] {
            let mut s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            let mut g=if selected {
                let(g,report)=PreflopGpu::new_throughput(&s,budget).unwrap();
                let shared=n==4 && budget==2000;
                assert_eq!(report.mode,if shared{"retained_cohorts"}else{"normal_gpu"});
                assert_eq!(report.narrow_offsets,shared);
                assert_eq!(report.static_cdf,shared);
                assert_eq!(report.static_cdf_fallback_reason.is_some(),n==4 && budget==128);
                assert_eq!(report.fallback_reason.is_none(),shared);
                assert_eq!(report.configured_budget_mb,budget);g
            }else{PreflopGpu::new(&s,budget).unwrap()};
            let mut rounds=Vec::new();
            for _ in 0..3 {
                g.iterate(&mut s).unwrap();let(gaps,evs)=g.gaps_and_evs().unwrap();
                g.sync_to_cpu(&mut s).unwrap();let(a,b)=s.arena_snapshot();
                rounds.push((s.iteration,a.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    b.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            let age=s.iteration;let before=s.arena_snapshot();
            assert!(!g.try_iterate(&mut s,Some(&AtomicBool::new(true))).unwrap());
            g.sync_to_cpu(&mut s).unwrap();assert_eq!(s.iteration,age);assert_eq!(s.arena_snapshot(),before);
            if let Some(ref expected)=expected {assert_eq!(&rounds,expected,"n={n}, budget={budget}");}
            else {expected=Some(rounds);}
        }
    }}
}
