    #[test]
    #[ignore = "targeted one-particle CUDA boundary/parity test; run explicitly in release"]
    fn coupled_minimum_budget_direct_and_normalized_paths_match() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let mut chosen = None;
        // Search only small/medium CPU-built fixtures; no repeated GPU allocation
        // is used to locate the integer-MB boundary.
        for n in [4usize, 5, 6] {
            let mut posts = vec![0.0; n]; posts[n - 2] = 0.5; posts[n - 1] = 1.0;
            let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
                "positions": (0..n).map(|p| format!("P{p}")).collect::<Vec<_>>(),
                "stack":20.0, "posts":posts, "limp":true, "open_raises":[2.0,3.0],
                "raise_mults":[3.0], "max_raises":2, "add_allin":false,
                "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
            })).unwrap();
            let s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            if s.nodes.len() > 250_000 { continue; }
            let sources = reach_sources(&s);
            let mw = EquityCachePlan::multiway(&s, &sources);
            let slots = mw.blocks.len();
            if slots < 3000 { continue; } // >2MB normalization interval
            let terms = s.nodes.iter().filter(|nd|
                nd.kind == KIND_POT_SHARE && nd.live.count_ones() >= 3).count();
            let fixed = mw.metadata_bytes() + terms * 8 + slots * 4
                + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4;
            let base = minimum_vram_mb(&s, ValuePlan::build(&s).blocks) * 1e6 + fixed as f64;
            let particle = slots * (NUM_CLASSES + 1) * 4;
            let normalized = slots * NUM_CLASSES * 4;
            let eq_plan = EquityCachePlan::build(&s, &sources);
            let mut direct = None;
            let first = ((base + particle as f64) / 1e6).ceil() as u64;
            let last = ((base + normalized as f64 + 2.0 * particle as f64) / 1e6).floor() as u64;
            for budget in first..=last {
                let remaining = (budget as f64 * 1e6 - base).max(0.0) as usize;
                let Some(plan) = multiway_batch_plan(remaining, slots).unwrap() else { continue; };
                if plan.batch != 1 { continue; }
                let need = base + (plan.cache_len * 4 + plan.normalized_bytes) as f64;
                let eq_cached = !eq_plan.blocks.is_empty()
                    && need + eq_plan.bytes() as f64 <= budget as f64 * 1e6;
                if plan.normalized_bytes == 0 {
                    direct = Some((budget, eq_cached));
                } else if let Some((direct_budget, direct_eq)) = direct {
                    if eq_cached == direct_eq {
                        chosen = Some((cfg.clone(), direct_budget, budget, slots, s.nodes.len()));
                        break;
                    }
                }
            }
            if chosen.is_some() { break; }
        }
        let (cfg, direct_budget, normalized_budget, slots, nodes) = chosen
            .expect("medium fixture must admit both integer-MB paths with batch1 and identical HU cache mode");
        eprintln!("boundary fixture: {nodes} nodes, {slots} slots, direct {direct_budget}MB, normalized {normalized_budget}MB");
        let mut snapshots = Vec::new();
        let mut terminal_snapshots = Vec::new();
        let mut cache_modes = Vec::new();
        // Sequential construction avoids two simultaneous CUDA engines. Each
        // starts from the same fresh state; neither budget is mocked/overridden.
        for (budget, expect_normalized) in [(direct_budget, false), (normalized_budget, true)] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let mut gpu = PreflopGpu::new(&s, budget).expect("actual constructor must retain minimum fit");
            assert_eq!(gpu.use_mw_normalized, expect_normalized);
            assert_eq!(gpu.mw_batch, 1);
            assert_eq!(gpu.use_multiway, 1);
            cache_modes.push(gpu.use_eq_cache);
            let mut records = Vec::new();
            // First iteration is eager; later iterations exercise captured
            // learning graphs. Repeated checks exercise evaluation graph replay.
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();
                let (gaps, evs) = gpu.gaps_and_evs().unwrap();
                let regret_bits: Vec<u32> = gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x| x.to_bits()).collect();
                let strategy_bits: Vec<u32> = gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x| x.to_bits()).collect();
                records.push((regret_bits, strategy_bits,
                    gaps.iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x| x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.learning_graphs.iter().any(|g| g.is_some()));
            assert!(gpu.eval_graph.is_some());
            snapshots.push(records);
            // Drop captured graphs before replacing any of their input buffers.
            for graph in &mut gpu.learning_graphs { *graph = None; }
            gpu.eval_graph = None;
            let target = s.nodes.iter().position(|nd|
                nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 3).unwrap();
            let live: Vec<usize> = (0..s.n).filter(|&p| s.nodes[target].live & (1 << p) != 0).collect();
            let (p, other) = (live[0], live[1]);
            let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let value_slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            let base = value_slots[target] as usize * NUM_CLASSES;
            gpu.d_mw_terms = gpu.stream.clone_htod(&[target as u32]).unwrap();
            gpu.mw_nterms = 1;
            let mut terminal_records = Vec::new();
            // Exercise the selected direct kernel's zero writes and transition
            // to ungated evaluation; repeat identically on the normalized path.
            for (phase, gate, zero) in [(0usize, 1i32, false), (1, 1, true), (2, 0, false)] {
                let mut reaches = vec![0f32; gpu.d_reach.len()];
                for (block, r) in reaches.chunks_exact_mut(NUM_CLASSES).enumerate() {
                    let scale = [1.0f32 / 32.0, 1.0 / 16.0, 1.0 / 8.0][(block + phase) % 3];
                    let h = (block * 17 + phase * 11) % NUM_CLASSES;
                    r[h] = scale; r[(h + 53) % NUM_CLASSES] = 2.0 * scale;
                    r[(h + 107) % NUM_CLASSES] = 4.0 * scale;
                }
                if zero {
                    let off = sources[target * s.n + other] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].fill(0.0);
                }
                if phase == 2 {
                    assert!(gpu.stream.clone_dtoh(&gpu.d_mw_active).unwrap().iter().all(|&x| x == 0));
                }
                gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
                unsafe {
                    gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                        .launch(LaunchConfig { block_dim: (128,1,1),
                            ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap();
                }
                gpu.d_val = gpu.stream.clone_htod(&vec![123456.0f32; gpu.d_val.len()]).unwrap();
                gpu.d_mw_cdf = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_cdf.len()]).unwrap();
                if expect_normalized {
                    gpu.d_mw_normalized = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_normalized.len()]).unwrap();
                }
                gpu.terminals_masked(p as i32, gate).unwrap();
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                    let off = sources[target * s.n + q] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].to_vec()
                }).collect();
                let mut expected = vec![0f32; NUM_CLASSES];
                s.terminal_value(target, p, &local, &mut expected);
                for h in 0..NUM_CLASSES {
                    assert!(actual[base + h].is_finite() && (actual[base + h] - expected[h]).abs() < 2e-5,
                        "budget {budget}, phase {phase}, h {h}: {} vs {}", actual[base + h], expected[h]);
                }
                if zero { assert!(actual[base..base + NUM_CLASSES].iter().all(|&x| x == 0.0)); }
                terminal_records.push(actual[base..base + NUM_CLASSES].iter().map(|x| x.to_bits()).collect::<Vec<_>>());
            }
            terminal_snapshots.push(terminal_records);
        }
        assert_eq!(cache_modes[0], cache_modes[1], "HU cache mode must not confound the comparison");
        for (step, (a, b)) in snapshots[0].iter().zip(&snapshots[1]).enumerate() {
            for (label, x, y) in [("regrets", &a.0, &b.0), ("strategy", &a.1, &b.1)] {
                assert_eq!(x.len(), y.len());
                if let Some(i) = x.iter().zip(y).position(|(u, v)| u != v) {
                    panic!("{label} differs at iteration {}, index {i}: {:08x} vs {:08x}", step + 1, x[i], y[i]);
                }
            }
            assert_eq!(a.2, b.2, "gap bits differ at iteration {}", step + 1);
            assert_eq!(a.3, b.3, "EV bits differ at iteration {}", step + 1);
        }
        assert_eq!(terminal_snapshots[0], terminal_snapshots[1], "direct stale/zero/ungated terminal behavior must match");
    }
