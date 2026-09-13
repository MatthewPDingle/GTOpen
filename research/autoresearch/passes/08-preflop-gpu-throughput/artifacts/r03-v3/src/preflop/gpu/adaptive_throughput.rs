//! Memory-aware selection of retained GPU throughput optimizations.
use super::*;

const FREE_RESERVE: usize = 512 * 1024 * 1024;

#[derive(Debug, Clone, serde::Serialize)]
pub struct ThroughputSelection {
    pub mode: &'static str,
    pub configured_budget_mb: u64,
    pub cohort_limit_mb: Option<u64>,
    pub fallback_reason: Option<String>,
    pub narrow_offsets: bool,
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
                cohort_limit_mb: Some(limit), fallback_reason: None, narrow_offsets: false,
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
        cohort_limit_mb, fallback_reason: Some(reason), narrow_offsets: false,
    }))
}

impl PreflopGpu {
    /// Prefer shared GPU evaluation when it fits; preserve the normal GPU plan otherwise.
    pub fn new_throughput(
        s: &PreflopSolver, budget_mb: u64,
    ) -> Result<(Self, ThroughputSelection), String> {
        // Keep the primary context alive while the selected constructor acquires it.
        // Dropping the probe first tears it down and repeats CUDA initialization.
        let probe = CudaContext::new(0);
        let free = match &probe {
            Ok(ctx) => ctx.mem_get_info().map(|(free, _)| free).map_err(e),
            Err(error) => Err(e(error)),
        };
        let result = Self::adaptive_with_offsets(s, budget_mb, free, true);
        drop(probe);
        result
    }

    #[cfg(feature = "preflop-research")]
    pub fn new_research_adaptive_throughput(
        s: &PreflopSolver, budget_mb: u64,
    ) -> Result<(Self, ThroughputSelection), String> {
        Self::new_throughput(s, budget_mb)
    }

    fn adaptive_with_offsets(
        s: &PreflopSolver, budget_mb: u64, free: Result<usize, String>, narrow: bool,
    ) -> Result<(Self, ThroughputSelection), String> {
        let (g,mut report)=choose(budget_mb, free,
            |limit| Self::new_with_kernel_offsets(s, budget_mb, true, false, true, true, Some(limit), narrow),
            || Self::new(s, budget_mb))?;
        report.narrow_offsets=g.throughput_narrow;
        Ok((g,report))
    }

    #[cfg(all(test, feature = "preflop-research"))]
    fn adaptive_with_memory(
        s: &PreflopSolver, budget_mb: u64, free: Result<usize, String>,
    ) -> Result<(Self, ThroughputSelection), String> {
        Self::adaptive_with_offsets(s,budget_mb,free,false)
    }

}

#[cfg(all(test, feature = "preflop-research"))]
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

    pub(super) fn fixture(n:usize) -> PreflopSolver {
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

    pub(super) fn bits(g:&PreflopGpu) -> (Vec<u32>,Vec<u32>,Vec<u32>) {
        (g.stream.clone_dtoh(&g.d_regrets).unwrap().iter().map(|v|v.to_bits()).collect(),
         g.stream.clone_dtoh(&g.d_strat).unwrap().iter().map(|v|v.to_bits()).collect(),
         g.stream.clone_dtoh(&g.d_eval_roots).unwrap().iter().map(|v|v.to_bits()).collect())
    }

    #[test]
    fn selected_and_fallback_engines_preserve_saved_state_math() {
        for n in [2,4] {
            let mut expected=None;
            for mode in 0..5 {
                let mut s=fixture(n);let age=s.iteration;
                let initial=s.arena_snapshot();
                let mut g=if mode==0 {PreflopGpu::new(&s,2000).unwrap()} else {
                    let free=match mode {1|4=>Ok(2_000_000_000),2=>Ok(FREE_RESERVE+1_000_000),_=>Err("test probe failure".into())};
                    let (g,selection)=PreflopGpu::adaptive_with_offsets(&s,2000,free,mode==4).unwrap();
                    assert_eq!(selection.mode,if n==4 && (mode==1 || mode==4) {"retained_cohorts"}else{"normal_gpu"});
                    assert_eq!(selection.configured_budget_mb,2000);
                    assert_eq!(selection.narrow_offsets,n==4 && mode==4);g
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

    #[test]
    #[ignore = "R01 immutable saved-game rollout qualification, guarded idle GPU only"]
    fn frozen_saved_game_continuation() {
        use serde_json::json;
        use std::time::Instant;
        let input=std::env::var("PREFLOP_GPU_REUSE_INPUT").unwrap();
        let output=std::env::var("PREFLOP_GPU_REUSE_OUTPUT").unwrap();
        let mode=std::env::var("PREFLOP_GPU_ROLLOUT_MODE").unwrap();
        assert!(!std::path::Path::new(&output).exists());
        let save=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../target")
            .join(format!("{}.gtop",std::path::Path::new(&output).file_stem().unwrap().to_str().unwrap()));
        assert!(!save.exists());
        let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
        let data=std::fs::read(path).unwrap();
        let eq=Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(data[..4].try_into().unwrap())));
        let mut s=PreflopSolver::load_game(&input,eq.clone()).unwrap();
        let metadata=|s:&PreflopSolver| json!({"config":s.cfg,"model":s.multiway_equity_model(),
            "frozen":s.seat_frozen,"profiles":s.seat_profiles,"locks":s.point_locks,"hero":s.hero});
        let original_meta=metadata(&s);let initial_age=s.iteration;
        let construct=|s:&PreflopSolver| match mode.as_str() {
            "retained" => (PreflopGpu::new_research_narrow_cohorts(s,23000).unwrap(),None),
            "normal" => (PreflopGpu::new(s,23000).unwrap(),None),
            "adaptive" => {let(g,r)=PreflopGpu::new_throughput(s,23000).unwrap();(g,Some(r))},
            "fallback" => {let(g,r)=PreflopGpu::adaptive_with_memory(s,23000,Ok(FREE_RESERVE+1_000_000)).unwrap();(g,Some(r))},
            _=>panic!("unknown rollout mode"),
        };
        let started=Instant::now();let(g,selection)=construct(&s);let mut g=g;
        let init_seconds=started.elapsed().as_secs_f64();
        let layout=json!({"batch":g.mw_batch,"hu_cache":g.use_eq_cache,"narrow_offsets":g.throughput_narrow,"cohort":g.research_cohorts.as_ref().map(|c|c.plan.report())});
        let mut rows=Vec::new();
        for i in 0..6 {
            let t=Instant::now();g.iterate(&mut s).unwrap();let iteration_seconds=t.elapsed().as_secs_f64();
            let t=Instant::now();let(gaps,evs)=g.gaps_and_evs().unwrap();let check_seconds=t.elapsed().as_secs_f64();
            let row=json!({"index":i,"iteration":s.iteration,"gaps":gaps,"evs":evs,"iteration_seconds":iteration_seconds,"check_seconds":check_seconds});
            println!("R03_CHECK {row}");rows.push(row);
        }
        g.sync_to_cpu(&mut s).unwrap();
        let fingerprint=|s:&PreflopSolver| {
            let (regret,strategy)=s.arena_snapshot();
            let hash=regret.iter().chain(&strategy).fold(0xcbf29ce484222325u64,|h,x|
                x.to_bits().to_le_bytes().iter().fold(h,|h,b|(h^*b as u64).wrapping_mul(0x100000001b3)));
            format!("{hash:016x}")
        };
        let arena_fingerprint=fingerprint(&s);
        let six_step_seconds=started.elapsed().as_secs_f64();
        assert_eq!(metadata(&s),original_meta);
        s.save_game(save.to_str().unwrap()).unwrap();drop(g);
        let mut reloaded=PreflopSolver::load_game(save.to_str().unwrap(),eq).unwrap();
        assert_eq!(metadata(&reloaded),original_meta);assert_eq!(reloaded.iteration,s.iteration);
        {
            let(a,b)=s.arena_snapshot();let(c,d)=reloaded.arena_snapshot();
            assert_eq!(a.len(),c.len());assert_eq!(b.len(),d.len());
            assert!(a.iter().zip(&c).all(|(x,y)|x.to_bits()==y.to_bits()));
            assert!(b.iter().zip(&d).all(|(x,y)|x.to_bits()==y.to_bits()));
        }
        drop(s);
        let(mut g,reload_selection)=construct(&reloaded);
        g.iterate(&mut reloaded).unwrap();let(gaps,evs)=g.gaps_and_evs().unwrap();
        g.sync_to_cpu(&mut reloaded).unwrap();let continued_fingerprint=fingerprint(&reloaded);
        let result=json!({"mode":mode,"input":input,"save":save,"nodes":reloaded.nodes.len(),"initial_iteration":initial_age,
            "selection":selection,"reload_selection":reload_selection,"layout":layout,"init_seconds":init_seconds,
            "six_step_seconds":six_step_seconds,"rows":rows,"arena_fingerprint":arena_fingerprint,
            "continued_iteration":reloaded.iteration,"continued_fingerprint":continued_fingerprint,"continued_gaps":gaps,"continued_evs":evs,
            "metadata_preserved":true,"save_reload_arenas_bitwise_equal":true,
            "scope":"Saved-state rollout qualification; timing is diagnostic, not a new optimization gain."});
        std::fs::write(output,serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    }
}

#[cfg(all(test, feature = "preflop-research"))]
pub(super) mod allocation_recovery;
