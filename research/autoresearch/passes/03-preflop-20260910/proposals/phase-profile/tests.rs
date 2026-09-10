    fn phase_test_equity() -> Arc<crate::preflop::equity::EquityTable> {
        let path = std::env::var("PREFLOP_PHASE_EQ").unwrap_or_else(|_|
            concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin").to_string());
        let bytes = std::fs::read(&path).expect("phase tests require an existing equity cache");
        assert!(bytes.len() >= 4, "invalid equity cache");
        let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
        Arc::new(crate::preflop::equity::EquityTable::load_or_build(&path, samples))
    }

    fn assert_phase_counts(profile: &serde_json::Value, np: usize, batches: usize, average: bool) {
        let count = |phase: &str| -> usize {
            profile["rows"].as_array().unwrap().iter()
                .filter(|r| r["phase"].as_str() == Some(phase))
                .map(|r| r["intervals"].as_u64().unwrap() as usize).sum()
        };
        for phase in ["prepare", "normalize", "ordinary_terminals"] { assert_eq!(count(phase), np, "{phase}"); }
        for phase in ["cdf", "coupled_terminals"] { assert_eq!(count(phase), np*batches, "{phase}"); }
        assert_eq!(count("down"), if average { 1 } else { np });
        assert_eq!(count("up_learn"), if average { 0 } else { np });
        assert_eq!(count("up_average"), if average { np } else { 0 });
        assert_eq!(count("up_br"), if average { np } else { 0 });
        assert_eq!(count("root_copy"), if average { 2*np } else { 0 });
        assert_eq!(count("discount"), if average { 0 } else { 1 });
        let total = profile["gpu_ms"].as_f64().unwrap();
        let sum = profile["interval_sum_ms"].as_f64().unwrap();
        assert!(total.is_finite() && total >= 0.0 && sum.is_finite() && sum >= 0.0);
        // Independent event timestamp differences have finite resolution.
        assert!((total-sum).abs() < 1.0 + total*0.001);
    }

    #[test]
    fn coupled_phase_event_hooks_preserve_solver_bits() {
        let eq = phase_test_equity();
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"], "stack":5.0, "posts":[0.0,0.0,0.5,1.0],
            "limp":true, "open_raises":[2.0], "raise_mults":[3.0], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let mut results = Vec::new();
        for profiling in [false, true] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
            assert!(gpu.use_multiway != 0 && gpu.use_mw_normalized);
            let batches = crate::preflop::multiway::SAMPLES.div_ceil(gpu.mw_batch as usize);
            let mut rounds = Vec::new();
            for _ in 0..2 {
                if profiling { gpu.phase_profile_begin().unwrap(); }
                gpu.iterate(&mut s).unwrap();
                if profiling { assert_phase_counts(&gpu.phase_profile_end().unwrap(), s.n, batches, false); }
                if profiling { gpu.phase_profile_begin().unwrap(); }
                let (gaps, evs) = gpu.gaps_and_evs().unwrap();
                if profiling { assert_phase_counts(&gpu.phase_profile_end().unwrap(), s.n, batches, true); }
                rounds.push((
                    gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            if !profiling { assert!(gpu.eval_graph.is_some()); }
            results.push(rounds);
        }
        assert_eq!(results[0], results[1], "event instrumentation changed numerical outputs");
    }

    /// Supplementary diagnostic only. Does not write/save its input or modify
    /// the frozen benchmark harness. Requires explicit --ignored selection.
    #[test]
    #[ignore = "opt-in eager CUDA phase profiling; requires frozen input and idle GPU"]
    fn profile_coupled_gpu_phases_from_frozen_input() {
        let input = std::env::var("PREFLOP_PHASE_INPUT").expect("set PREFLOP_PHASE_INPUT to a frozen JSON or .gtop file");
        let eq = phase_test_equity();
        let mut s = if input.ends_with(".gtop") {
            PreflopSolver::load_game(&input, eq).unwrap()
        } else {
            let v: serde_json::Value = serde_json::from_slice(&std::fs::read(&input).unwrap()).unwrap();
            let cfg = serde_json::from_value(v.get("config").unwrap_or(&v).clone()).unwrap();
            PreflopSolver::new(cfg, eq).unwrap()
        };
        let number = |name: &str, default: usize| std::env::var(name).map(|x|x.parse::<usize>().expect(name)).unwrap_or(default);
        let budget = number("PREFLOP_PHASE_BUDGET_MB", 23000);
        let warmup = number("PREFLOP_PHASE_WARMUP", 2);
        let repeats = number("PREFLOP_PHASE_REPEATS", 3);
        assert!(repeats > 0 && repeats <= 100 && warmup <= 100);
        let mut gpu = PreflopGpu::new(&s, budget.try_into().unwrap()).unwrap();
        assert_ne!(gpu.use_multiway, 0, "this profile is for coupled multiway");
        println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"metadata","input":input,
            "model":s.multiway_equity_model(),"nodes":s.nodes.len(),"seats":s.n,
            "initial_iteration":s.iteration,"warmup":warmup,"repeats":repeats,"budget_mb":budget,
            "batch":gpu.mw_batch,"normalized":gpu.use_mw_normalized,"compact":gpu.use_mw_compact != 0,
            "cdf_bytes":gpu.d_mw_cdf.len()*4,"normalized_bytes":gpu.d_mw_normalized.len()*4}));
        for _ in 0..warmup { gpu.iterate(&mut s).unwrap(); }
        gpu.gaps_and_evs().unwrap(); // warm evaluation-only kernels too
        for sample in 0..repeats {
            gpu.phase_profile_begin().unwrap();
            let started = std::time::Instant::now();
            gpu.iterate(&mut s).unwrap();
            let wall_ms = started.elapsed().as_secs_f64()*1000.0;
            let phases = gpu.phase_profile_end().unwrap();
            println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"iteration","sample":sample,
                "iteration":s.iteration,"wall_ms":wall_ms,"phases":phases}));
            gpu.phase_profile_begin().unwrap();
            let started = std::time::Instant::now();
            let (gaps,evs) = gpu.gaps_and_evs().unwrap();
            let wall_ms = started.elapsed().as_secs_f64()*1000.0;
            let phases = gpu.phase_profile_end().unwrap();
            println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"average_check","sample":sample,
                "iteration":s.iteration,"wall_ms":wall_ms,"phases":phases,"gaps":gaps,"evs":evs}));
        }
        gpu.sync_to_cpu(&mut s).unwrap();
        let (regret,strategy) = s.arena_snapshot();
        let fingerprint = regret.iter().chain(&strategy).fold(0xcbf29ce484222325u64, |h,x|
            x.to_bits().to_le_bytes().iter().fold(h,|h,b|(h ^ *b as u64).wrapping_mul(0x100000001b3)));
        println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"result","iteration":s.iteration,
            "arena_hash":format!("{fingerprint:016x}"),"execution":"eager_cuda_events"}));
    }
