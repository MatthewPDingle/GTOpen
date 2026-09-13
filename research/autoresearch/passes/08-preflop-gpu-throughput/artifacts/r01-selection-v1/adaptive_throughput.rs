//! Rollout qualification only: the default constructor remains unchanged.
use super::*;

const FREE_RESERVE: usize = 512 * 1024 * 1024;

#[derive(Debug, Clone, serde::Serialize)]
pub struct ThroughputSelection {
    pub mode: &'static str,
    pub configured_budget_mb: u64,
    pub cohort_limit_mb: Option<u64>,
    pub fallback_reason: Option<String>,
}

fn choose<T>(
    budget_mb: u64,
    free_bytes: Result<usize, String>,
    optimized: impl FnOnce(u64) -> Result<T, String>,
    baseline: impl FnOnce() -> Result<T, String>,
) -> Result<(T, ThroughputSelection), String> {
    let limit = free_bytes.map(|free| {
        (free.saturating_sub(FREE_RESERVE) / 1_000_000) as u64
    }).map(|free_mb| free_mb.min(budget_mb).min(20_500));
    let (cohort_limit_mb, reason) = match limit {
        Ok(limit) if limit > 0 => match optimized(limit) {
            Ok(value) => return Ok((value, ThroughputSelection {
                mode: "retained_cohorts", configured_budget_mb: budget_mb,
                cohort_limit_mb: Some(limit), fallback_reason: None,
            })),
            Err(reason) => (Some(limit), reason),
        },
        Ok(limit) => (Some(limit), "insufficient free GPU memory for optional sharing".into()),
        Err(reason) => (None, format!("free GPU memory unavailable: {reason}")),
    };
    // An Err from the owned constructor has already dropped its partial state.
    let value = baseline().map_err(|error| {
        format!("optional throughput unavailable ({reason}); normal GPU construction failed: {error}")
    })?;
    Ok((value, ThroughputSelection {
        mode: "normal_gpu", configured_budget_mb: budget_mb,
        cohort_limit_mb, fallback_reason: Some(reason),
    }))
}

impl PreflopGpu {
    /// Isolated rollout qualification; not selected by normal app construction.
    pub fn new_research_adaptive_throughput(
        s: &PreflopSolver, budget_mb: u64,
    ) -> Result<(Self, ThroughputSelection), String> {
        let free = CudaContext::new(0).map_err(e)
            .and_then(|ctx| ctx.mem_get_info().map(|(free, _)| free).map_err(e));
        Self::adaptive_with_memory(s, budget_mb, free)
    }

    fn adaptive_with_memory(
        s: &PreflopSolver, budget_mb: u64, free: Result<usize, String>,
    ) -> Result<(Self, ThroughputSelection), String> {
        choose(budget_mb, free,
            |limit| Self::new_with_cohort_limit(s, budget_mb, true, false, true, true, Some(limit)),
            || Self::new(s, budget_mb))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{PreflopConfig, equity::EquityTable};
    use std::cell::Cell;

    #[test]
    fn budget_selection_and_error_paths() {
        for (free, budget, expected) in [(usize::MAX,23_000,20_500), (FREE_RESERVE+4_999_999,23_000,4), (FREE_RESERVE+8_000_000,3,3)] {
            let (value, selection) = choose(budget, Ok(free), |limit| {
                assert_eq!(limit,expected); Ok(42)
            }, || panic!("normal constructor must not run after success")).unwrap();
            assert_eq!(value,42); assert_eq!(selection.mode,"retained_cohorts");
            assert_eq!(selection.configured_budget_mb,budget);
        }
        for free in [Ok(0),Ok(FREE_RESERVE),Err("probe error".into())] {
            let (value, selection) = choose(23_000,free, |_| -> Result<i32,String> {
                panic!("optimized constructor must not run without headroom")
            }, || Ok(7)).unwrap();
            assert_eq!(value,7); assert_eq!(selection.mode,"normal_gpu");
            assert!(selection.fallback_reason.is_some());
        }
        let attempts=Cell::new(0);
        let (_, report)=choose(23_000,Ok(24_000_000_000), |_| -> Result<(),String> {
            attempts.set(1); Err("allocation failed".into())
        }, || {assert_eq!(attempts.get(),1);attempts.set(2);Ok(())}).unwrap();
        assert_eq!(attempts.get(),2); assert_eq!(report.fallback_reason.as_deref(),Some("allocation failed"));
        let error=choose(23_000,Ok(24_000_000_000), |_| -> Result<(),String> {Err("optional failed".into())}, || Err("base failed".into())).unwrap_err();
        assert!(error.contains("optional failed") && error.contains("base failed"));
    }

    fn fixture(n:usize) -> PreflopSolver {
        let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
        let data=std::fs::read(path).unwrap();
        let eq=Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(data[..4].try_into().unwrap())));
        let mut posts=vec![0.;n];posts[n-2]=0.5;posts[n-1]=1.;
        let config:PreflopConfig=serde_json::from_value(serde_json::json!({
            "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
            "stack":10,"posts":posts,"limp":true,"open_raises":[2],"raise_mults":[],
            "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"
        })).unwrap();
        let mut s=PreflopSolver::new(config,eq).unwrap();
        s.research_seed_quality_fixture_averages().unwrap();
        s.seat_frozen[n-2]=true;
        let node=s.child(0,1);
        let mut lock=vec![0.;s.nodes[node].actions.len()*NUM_CLASSES];lock[..NUM_CLASSES].fill(1.);
        s.point_locks.insert(node as u32,lock);
        s
    }

    fn bits(g:&PreflopGpu) -> (Vec<u32>,Vec<u32>,Vec<u32>) {
        (g.stream.clone_dtoh(&g.d_regrets).unwrap().iter().map(|v|v.to_bits()).collect(),
         g.stream.clone_dtoh(&g.d_strat).unwrap().iter().map(|v|v.to_bits()).collect(),
         g.stream.clone_dtoh(&g.d_eval_roots).unwrap().iter().map(|v|v.to_bits()).collect())
    }

    #[test]
    fn selected_and_fallback_engines_preserve_saved_state_math() {
        for n in [2,4] {
            let mut expected=None;
            for mode in 0..4 {
                let mut s=fixture(n);let age=s.iteration;
                let initial=s.arena_snapshot();
                let mut g=if mode==0 {PreflopGpu::new(&s,2000).unwrap()} else {
                    let free=match mode {1=>Ok(2_000_000_000),2=>Ok(FREE_RESERVE+1_000_000),_=>Err("test probe failure".into())};
                    let (g,selection)=PreflopGpu::adaptive_with_memory(&s,2000,free).unwrap();
                    assert_eq!(selection.mode,if n==4 && mode==1 {"retained_cohorts"}else{"normal_gpu"});
                    assert_eq!(selection.configured_budget_mb,2000);g
                };
                let before=bits(&g);
                assert_eq!(before.0,initial.0.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                assert_eq!(before.1,initial.1.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                assert_eq!(s.iteration,age);
                let layout=(g.mw_batch,g.use_eq_cache,g.use_mw_compact);
                let mut rounds=Vec::new();
                for _ in 0..3 {
                    g.iterate(&mut s).unwrap();let (gap,ev)=g.gaps_and_evs().unwrap();
                    rounds.push((bits(&g),gap.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),ev.iter().map(|v|v.to_bits()).collect::<Vec<_>>()));
                }
                assert!(g.eval_graph.is_some());
                let current=bits(&g);let age=s.iteration;
                assert!(!g.try_iterate(&mut s,Some(&AtomicBool::new(true))).unwrap());
                assert_eq!(bits(&g),current);assert_eq!(s.iteration,age);
                g.sync_to_cpu(&mut s).unwrap();let after=s.arena_snapshot();
                assert_eq!(current.0,after.0.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                assert_eq!(current.1,after.1.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                let result=(layout,rounds);
                if let Some(ref expected)=expected {assert_eq!(expected,&result,"n={n} mode={mode}");}else{expected=Some(result);}
            }
        }
    }
}
