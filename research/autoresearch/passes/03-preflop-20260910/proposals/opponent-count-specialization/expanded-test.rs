    #[test]
    fn coupled_terminal_matches_cpu_across_particle_batches() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["BTN","SB","BB"], "stack":5.0, "posts":[0.0,0.5,1.0],
            "limp":true, "open_raises":[2.0], "raise_mults":[3.0], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        // Exercise every exact opponent-count specialization O=2..8.
        for n in 3usize..=9 {
            let mut cfg = cfg.clone();
            if n != 3 {
                cfg.positions = (0..n).map(|p| format!("P{p}")).collect();
                cfg.positions[n-2] = "SB".into(); cfg.positions[n-1] = "BB".into();
                cfg.posts = vec![0.0; n]; cfg.posts[n-2] = 0.5; cfg.posts[n-1] = 1.0;
                cfg.open_raises.clear(); cfg.stack = 2.0;
            }
            let s = PreflopSolver::new(cfg, eq.clone()).unwrap();
            assert_eq!(s.multiway_equity_model(), "coupled_deck_v1");
            let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
            assert_eq!(gpu.use_multiway, 1);
            let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            let target = s.nodes.iter().position(|n| n.kind == KIND_POT_SHARE && n.live.count_ones() as usize == s.n).unwrap();
            gpu.down(1, 0).unwrap();
            let mut reaches = gpu.stream.clone_dtoh(&gpu.d_reach).unwrap();
            // Unit counterfactual mass keeps a strict absolute tolerance meaningful
            // even at the nine-seat terminal after many preceding calls.
            for r in reaches.chunks_exact_mut(NUM_CLASSES) {
                let mass: f32 = r.iter().sum(); if mass > 0.0 { for x in r { *x /= mass; } }
            }
            gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
            unsafe { gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                .launch(LaunchConfig { block_dim: (128,1,1), ..PreflopGpu::cfg((reaches.len()/NUM_CLASSES) as u32) }).unwrap(); }
            let local: Vec<Vec<f32>> = (0..s.n).map(|p| {
                let base = sources[target * s.n + p] as usize * NUM_CLASSES;
                reaches[base..base + NUM_CLASSES].to_vec()
            }).collect();
            // Seven exercises a partial final batch; one verifies bounded scratch
            // never silently switches to the old equity formula.
            for batch in [32u32, 7, 1] {
                gpu.mw_batch = batch;
                let mut terminal_bits = Vec::<Vec<u32>>::new();
                for p in 0..s.n {
                    gpu.terminals(p as i32).unwrap();
                    let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                    let mut expected = vec![0.; NUM_CLASSES];
                    s.terminal_value(target, p, &local, &mut expected);
                    let base = slots[target] as usize * NUM_CLASSES;
                    for h in 0..NUM_CLASSES {
                        assert!((actual[base + h] - expected[h]).abs() < 2e-5,
                            "n {n}, batch {batch}, p {p}, h {h}: {} vs {}", actual[base + h], expected[h]);
                    }
                    terminal_bits.push(actual[base..base + NUM_CLASSES].iter().map(|x| x.to_bits()).collect());
                }
                // Optional exact GPU-control evidence: run this same test patch
                // before/after kernel specialization and compare every f32 bit.
                // Different batch sizes may legitimately round differently, so
                // compare control/candidate only at the same (n, batch).
                if std::env::var("PREFLOP_MW_TERMINAL_BITS").as_deref() == Ok("1") {
                    println!("PREFLOP_MW_TERMINAL_BITS {}", serde_json::json!({
                        "seats": n, "opponents": n-1, "batch": batch,
                        "model": s.multiway_equity_model(), "bits_by_seat": terminal_bits,
                    }));
                }
            }
        }
    }
