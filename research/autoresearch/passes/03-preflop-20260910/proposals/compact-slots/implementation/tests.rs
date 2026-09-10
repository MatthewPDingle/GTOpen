    #[test]
    fn compact_slot_map_is_bijective_and_preserves_minimum_fit() {
        let rows = [vec![0u32,2,3,6,7,9], vec![1,2,5,7], vec![0,1,3,8,9]];
        let mut work = Vec::new(); let mut spans = Vec::new();
        for row in &rows { spans.push((work.len() as u32, row.len() as u32)); work.extend(row); }
        spans.push((work.len() as u32, 10)); work.extend(0..10u32);
        let plan = EquityCachePlan { slots: (0..10).collect(), blocks: (0..10).collect(), work, spans };
        let compact = MultiwayCompactPlan::build(&plan, 3).unwrap();
        assert!(compact.enabled);
        assert_eq!(compact.capacity, 6, "trailing union span is not a simultaneous traverser");
        assert_eq!(compact.bytes, 3 * 10 * 4);
        for p in 0..3 {
            for global in 0..10 {
                let expected = rows[p].iter().position(|&x| x == global as u32).map(|x| x as u32).unwrap_or(u32::MAX);
                assert_eq!(compact.map[p * 10 + global], expected);
            }
        }
        let old_minimum = 10 * (NUM_CLASSES + 1) * 4;
        let new_minimum = compact.bytes + compact.capacity * (NUM_CLASSES + 1) * 4;
        assert!(new_minimum < old_minimum);
        assert!(multiway_batch_plan(old_minimum - compact.bytes, compact.capacity).unwrap().is_some());
        let dense = EquityCachePlan {
            slots: (0..10).collect(), blocks: (0..10).collect(),
            work: (0..3).flat_map(|_| 0..10u32).collect(), spans: vec![(0,10),(10,10),(20,10)],
        };
        let fallback = MultiwayCompactPlan::build(&dense, 3).unwrap();
        assert!(!fallback.enabled, "do not spend mapping memory when minimum fit worsens");
        assert_eq!(fallback.capacity, 10); assert_eq!(fallback.bytes, 0);
        assert_eq!(fallback.map.len(), 1);
    }

    #[test]
    fn coupled_compact_and_union_storage_have_identical_outputs() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"], "stack":5.0, "posts":[0.0,0.0,0.5,1.0],
            "limp":true, "open_raises":[2.0], "raise_mults":[3.0], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let mut results = Vec::new();
        let mut metadata = Vec::new();
        for allow_compact in [false, true] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let sources = reach_sources(&s);
            let plan = EquityCachePlan::multiway(&s, &sources);
            let mapping = MultiwayCompactPlan::build(&plan, s.n).unwrap();
            assert!(mapping.enabled, "fixture must exercise compact storage");
            // Validate every actual terminal/seat reference against the inverse
            // work-span mapping before involving a CUDA kernel.
            for (nd, node) in s.nodes.iter().enumerate().filter(|(_, n)|
                n.kind == KIND_POT_SHARE && n.live.count_ones() >= 3) {
                for p in 0..s.n {
                    if node.live & (1 << p) == 0 { continue; }
                    for q in 0..s.n {
                        if p == q || node.live & (1 << q) == 0 { continue; }
                        let global = plan.slots[sources[nd * s.n + q] as usize] as usize;
                        let local = mapping.map[p * plan.blocks.len() + global] as usize;
                        let (start, count) = plan.spans[p];
                        assert!(local < count as usize && local < mapping.capacity);
                        assert_eq!(plan.work[start as usize + local] as usize, global);
                    }
                }
            }
            let mut gpu = PreflopGpu::new_with_layout(&s, 2000, allow_compact).unwrap();
            assert_eq!(gpu.use_mw_compact != 0, allow_compact);
            assert_eq!(gpu.mw_batch, 32); assert!(gpu.use_mw_normalized);
            metadata.push((gpu.use_eq_cache, gpu.d_mw_cdf.len(), gpu.d_mw_normalized.len()));
            let mut snapshots = Vec::new();
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();
                let (gaps, evs) = gpu.gaps_and_evs().unwrap();
                snapshots.push((
                    gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    gaps.iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x| x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.eval_graph.is_some());
            for graph in &mut gpu.learning_graphs { *graph = None; } gpu.eval_graph = None;
            // Alternate differently sized seat spans. Poisoning the same compact
            // capacity catches stale reads beyond the new seat's populated span.
            let mut terminal_values = Vec::new();
            for (p, gate) in [(0usize,1i32),(3,0),(1,1),(0,0)] {
                gpu.d_mw_cdf = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_cdf.len()]).unwrap();
                gpu.d_mw_normalized = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_normalized.len()]).unwrap();
                gpu.d_val = gpu.stream.clone_htod(&vec![123456.0f32; gpu.d_val.len()]).unwrap();
                gpu.terminals_masked(p as i32, gate).unwrap();
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                assert!(actual.iter().all(|x| x.is_finite()), "compact stale read: p {p}, gate {gate}");
                terminal_values.push(actual.iter().map(|x| x.to_bits()).collect::<Vec<_>>());
            }
            results.push((snapshots, terminal_values));
        }
        assert_eq!(metadata[0].0, metadata[1].0);
        assert!(metadata[1].1 < metadata[0].1 && metadata[1].2 < metadata[0].2);
        for (step, (a,b)) in results[0].0.iter().zip(&results[1].0).enumerate() {
            for (label,x,y) in [("regret",&a.0,&b.0),("strategy",&a.1,&b.1)] {
                assert_eq!(x.len(),y.len());
                if let Some(i)=x.iter().zip(y).position(|(u,v)|u!=v) {
                    panic!("{label} differs at iteration {}, index {i}: {:08x} vs {:08x}",step+1,x[i],y[i]);
                }
            }
            assert_eq!(a.2,b.2,"gap bits differ at step {step}");
            assert_eq!(a.3,b.3,"EV bits differ at step {step}");
        }
        for (state,(a,b)) in results[0].1.iter().zip(&results[1].1).enumerate() {
            assert_eq!(a.len(),b.len());
            if let Some(i)=a.iter().zip(b).position(|(u,v)|u!=v) {
                panic!("terminal storage differs at state {state}, index {i}: {:08x} vs {:08x}",a[i],b[i]);
            }
        }
    }

