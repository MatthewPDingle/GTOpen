    #[test]
    fn coupled_normalized_reach_refreshes_nonunit_inputs_and_ungated_evaluation() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["BTN","SB","BB"], "stack":2.0, "posts":[0.0,0.5,1.0],
            "limp":true, "open_raises":[], "raise_mults":[], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let s = PreflopSolver::new(cfg, eq).unwrap();
        let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
        let target = s.nodes.iter().position(|nd|
            nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 3).unwrap();
        let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
        let value_slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
        let slot_blocks = gpu.stream.clone_dtoh(&gpu.d_mw_blocks).unwrap();
        let work = gpu.stream.clone_dtoh(&gpu.d_mw_work).unwrap();
        gpu.d_mw_terms = gpu.stream.clone_htod(&[target as u32]).unwrap();
        gpu.mw_nterms = 1;
        let (p, other) = (0usize, 1usize);
        let base = value_slots[target] as usize * NUM_CLASSES;
        for batch in [32u32, 7, 1] {
            gpu.mw_batch = batch;
            // Each phase changes both total mass and hand composition. Thus a
            // cached normalized distribution cannot pass merely by rescaling.
            for (phase, gate, zero_opponent, poison) in [
                (0usize, 1i32, false, true),
                (1, 1, true, false),
                (2, 0, false, true), // empty stale active mask must be ignored
                (3, 0, false, false), // old finite normalized values must refresh
                (4, 1, false, true),
                (5, 0, true, false),
                (6, 0, false, true),
            ] {
                let mut reaches = vec![0f32; gpu.d_reach.len()];
                for (block, r) in reaches.chunks_exact_mut(NUM_CLASSES).enumerate() {
                    // Unit weights[1,2,4] divided by32/16/8 give non-unit exact
                    // dyadic masses and nontrivial f32 division by seven.
                    let scale = [1.0f32 / 32.0, 1.0 / 16.0, 1.0 / 8.0][(block + phase) % 3];
                    let h = (block * 17 + phase * 11) % NUM_CLASSES;
                    r[h] = scale;
                    r[(h + 53) % NUM_CLASSES] = 2.0 * scale;
                    r[(h + 107) % NUM_CLASSES] = 4.0 * scale;
                }
                if zero_opponent {
                    let off = sources[target * s.n + other] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].fill(0.0);
                }
                if phase == 2 {
                    assert!(gpu.stream.clone_dtoh(&gpu.d_mw_active).unwrap().iter().all(|&x| x == 0),
                        "preceding gated zero case must leave an empty mask");
                }
                gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
                unsafe {
                    gpu.stream.launch_builder(&gpu.f_reach_mass)
                        .arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                        .launch(LaunchConfig { block_dim: (128,1,1),
                            ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap();
                }
                if poison {
                    gpu.d_mw_normalized = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_normalized.len()]).unwrap();
                }
                gpu.d_mw_cdf = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_cdf.len()]).unwrap();
                gpu.d_val = gpu.stream.clone_htod(&vec![123456.0f32; gpu.d_val.len()]).unwrap();
                gpu.terminals_masked(p as i32, gate).unwrap();
                let mass = gpu.stream.clone_dtoh(&gpu.d_reach_mass).unwrap();
                let active = gpu.stream.clone_dtoh(&gpu.d_mw_active).unwrap();
                let normalized = gpu.stream.clone_dtoh(&gpu.d_mw_normalized).unwrap();
                let (start, count) = gpu.mw_spans[p];
                let mut checked = 0;
                for &slot in &work[start as usize..(start + count) as usize] {
                    let slot = slot as usize;
                    let block = slot_blocks[slot] as usize;
                    if (gate != 0 && active[slot] == 0) || mass[block] <= 0.0 { continue; }
                    assert_ne!(mass[block], 1.0, "non-unit mass fixture required");
                    for h in 0..NUM_CLASSES {
                        let expected = reaches[block * NUM_CLASSES + h] / mass[block];
                        assert_eq!(normalized[slot * NUM_CLASSES + h].to_bits(), expected.to_bits(),
                            "phase {phase}, gate {gate}, batch {batch}, slot {slot}, h {h}");
                    }
                    checked += 1;
                }
                if !zero_opponent { assert!(checked > 0); }
                let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                    let off = sources[target * s.n + q] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].to_vec()
                }).collect();
                let mut expected = vec![0f32; NUM_CLASSES];
                s.terminal_value(target, p, &local, &mut expected);
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                for h in 0..NUM_CLASSES {
                    assert!(actual[base + h].is_finite() && (actual[base + h] - expected[h]).abs() < 2e-5,
                        "phase {phase}, gate {gate}, batch {batch}, h {h}: {} vs {}", actual[base + h], expected[h]);
                }
                if zero_opponent {
                    assert!(actual[base..base + NUM_CLASSES].iter().all(|&x| x == 0.0));
                }
            }
        }
    }

