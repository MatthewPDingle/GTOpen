    #[test]
    fn coupled_minimal_metadata_preserves_graphs_and_counterfactual_values() {
        let eq = phase_test_equity();
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"],"stack":5.0,"posts":[0.0,0.0,0.5,1.0],
            "limp":true,"open_raises":[2.0],"raise_mults":[3.0],"max_raises":1,
            "add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
        })).unwrap();
        let mut results=Vec::new();
        let mut metadata=Vec::new();
        for minimal in [false,true] {
            let mut s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            let mut gpu=PreflopGpu::new_with_layout_mode(&s,2000,true,minimal).unwrap();
            assert_eq!(!gpu.use_mw_prepared,minimal);
            if minimal {
                assert!(!gpu.use_mw_normalized && gpu.use_mw_compact==0);
                assert_eq!((gpu.d_mw_active.len(),gpu.d_mw_prob.len(),gpu.d_mw_normalized.len(),gpu.d_mw_compact.len()),(0,0,0,0));
            }
            metadata.push((gpu.mw_batch,gpu.use_eq_cache));
            let mut checkpoints=Vec::new();
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();
                let (g,e)=gpu.gaps_and_evs().unwrap();
                checkpoints.push((
                    gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    g.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),e.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.learning_graphs.iter().any(|g|g.is_some()) && gpu.eval_graph.is_some());
            for g in &mut gpu.learning_graphs {*g=None;} gpu.eval_graph=None;
            let target=s.nodes.iter().position(|n|n.kind==KIND_POT_SHARE && n.live.count_ones()==3).unwrap();
            let live:Vec<_>=(0..s.n).filter(|p|s.nodes[target].live&(1<<p)!=0).collect();
            let folded=(0..s.n).find(|p|s.nodes[target].live&(1<<p)==0).unwrap();
            let p=live[0];
            let sources=gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let slots=gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            let at=slots[target] as usize*NUM_CLASSES;
            let mut terminals=Vec::new();
            // Same distributions for positive -> own-zero -> live-zero ->
            // folded-zero -> positive. Own zero must not affect counterfactual value.
            for (zero,gate) in [(None,1),(Some(p),1),(Some(live[1]),1),(Some(folded),1),(None,0)] {
                let mut reach=vec![0f32;gpu.d_reach.len()];
                for (block,r) in reach.chunks_exact_mut(NUM_CLASSES).enumerate() {
                    let h=block*17%NUM_CLASSES;
                    r[h]=0.03125;r[(h+53)%NUM_CLASSES]=0.0625;r[(h+107)%NUM_CLASSES]=0.125;
                }
                if let Some(q)=zero {let off=sources[target*s.n+q] as usize*NUM_CLASSES;reach[off..off+NUM_CLASSES].fill(0.0);}
                gpu.d_reach=gpu.stream.clone_htod(&reach).unwrap();
                unsafe {gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                    .launch(LaunchConfig {block_dim:(128,1,1),..PreflopGpu::cfg((reach.len()/NUM_CLASSES) as u32)}).unwrap();}
                gpu.d_mw_cdf=gpu.stream.clone_htod(&vec![f32::NAN;gpu.d_mw_cdf.len()]).unwrap();
                gpu.d_val=gpu.stream.clone_htod(&vec![123456f32;gpu.d_val.len()]).unwrap();
                gpu.terminals_masked(p as i32,gate).unwrap();
                let actual=gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let local:Vec<Vec<f32>>=(0..s.n).map(|q|{let off=sources[target*s.n+q] as usize*NUM_CLASSES;reach[off..off+NUM_CLASSES].to_vec()}).collect();
                let mut expected=vec![0f32;NUM_CLASSES];s.terminal_value(target,p,&local,&mut expected);
                for h in 0..NUM_CLASSES {assert!(actual[at+h].is_finite() && (actual[at+h]-expected[h]).abs()<2e-5);}
                if zero.is_some() && zero!=Some(p) {assert!(actual[at..at+NUM_CLASSES].iter().all(|x|*x==0.0));}
                terminals.push(actual[at..at+NUM_CLASSES].iter().map(|x|x.to_bits()).collect::<Vec<_>>());
            }
            assert_eq!(terminals[0],terminals[1],"own zero must not prune counterfactual values");
            assert_eq!(terminals[0],terminals[4],"ungated positive recovery must discard stale zero state");
            results.push((checkpoints,terminals));
        }
        assert_eq!(metadata[0],metadata[1],"same batch/cache required for exact control");
        assert_eq!(results[0],results[1]);
    }

    #[test]
    #[ignore = "supplementary real integer-MB low-memory constructor boundary"]
    fn coupled_minimal_metadata_retains_former_union_budget_fit() {
        let eq=phase_test_equity();
        let mut chosen=None;
        for n in 4usize..=6 {
            let mut posts=vec![0.0;n];posts[n-2]=0.5;posts[n-1]=1.0;
            let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
                "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
                "stack":20.0,"posts":posts,"limp":true,"open_raises":[2.0,3.0],
                "raise_mults":[3.0],"max_raises":2,"add_allin":false,
                "rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
            })).unwrap();
            let s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            if s.nodes.len()>250000 {continue;}
            let src=reach_sources(&s);let mw=EquityCachePlan::multiway(&s,&src);let hu=EquityCachePlan::build(&s,&src);
            let compact=MultiwayCompactPlan::build(&mw,s.n).unwrap();
            if !compact.enabled {continue;}
            let terms=s.nodes.iter().filter(|n|n.kind==KIND_POT_SHARE && n.live.count_ones()>=3).count();
            let base=minimum_vram_mb(&s,ValuePlan::build(&s).blocks)+forced_storage_bytes(0).unwrap() as f64/1e6;
            let fixed=mw.metadata_bytes()+terms*4+3*crate::preflop::multiway::SAMPLES*NUM_CLASSES*4;
            let extra=terms*4+mw.blocks.len()*4;
            let first=(base+(fixed+mw.blocks.len()*680) as f64/1e6).ceil() as u64;
            let last=(base+(fixed+mw.blocks.len()*680*32) as f64/1e6).ceil() as u64;
            for budget in first..=last {
                let union=compatible_multiway_plan(budget,base,fixed,fixed+extra,mw.blocks.len(),mw.blocks.len(),hu.bytes(),!hu.blocks.is_empty()).unwrap();
                let Some(union)=union else {continue;};
                if !union.minimal_metadata {continue;}
                let compact_plan=compatible_multiway_plan(budget,base,fixed,fixed+extra+compact.bytes,mw.blocks.len(),compact.capacity,hu.bytes(),!hu.blocks.is_empty()).unwrap().unwrap();
                if compact_plan.minimal_metadata {continue;}
                chosen=Some((cfg.clone(),budget,union.storage.batch,union.reference.unwrap().use_eq_cache));break;
            }
            if chosen.is_some(){break;}
        }
        let (cfg,budget,batch,cache)=chosen.expect("bounded fixture must cross an integer-MB metadata boundary");
        let mut results=Vec::new();
        for allow_compact in [false,true] {
            let mut s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            // Normal planner, no forced minimal override: union must automatically
            // retain its old fit while compact may keep the preferred metadata.
            let mut gpu=PreflopGpu::new_with_layout(&s,budget,allow_compact).unwrap();
            assert_eq!(gpu.use_mw_prepared,allow_compact);assert_eq!(gpu.mw_batch as usize,batch);
            assert_eq!(gpu.use_eq_cache!=0,cache);
            gpu.iterate(&mut s).unwrap();let (g,e)=gpu.gaps_and_evs().unwrap();
            results.push((gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                g.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),e.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
        }
        assert_eq!(results[0],results[1]);
        eprintln!("minimal metadata boundary: {budget} MB, batch {batch}, HU cache {cache}");
    }
    #[test]
    fn coupled_hu_cached_and_direct_terminal_bits_match() {
        let eq=phase_test_equity();
        let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"],"stack":5.0,"posts":[0.0,0.0,0.5,1.0],
            "limp":true,"open_raises":[2.0],"raise_mults":[3.0],"max_raises":1,
            "add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
        })).unwrap();
        let s=PreflopSolver::new(cfg,eq).unwrap();
        let mut gpu=PreflopGpu::new(&s,2000).unwrap();
        assert_eq!(gpu.use_eq_cache,1);
        let mut reach=vec![0f32;gpu.d_reach.len()];
        for (block,r) in reach.chunks_exact_mut(NUM_CLASSES).enumerate() {
            for (h,x) in r.iter_mut().enumerate() {*x=if (block+h)%7==0 {0.0} else {((h*13+block*3)%31+1) as f32/4096.0};}
        }
        gpu.d_reach=gpu.stream.clone_htod(&reach).unwrap();
        unsafe {gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
            .launch(LaunchConfig {block_dim:(128,1,1),..PreflopGpu::cfg((reach.len()/NUM_CLASSES) as u32)}).unwrap();}
        // Manual reach replacement bypasses down(), which normally refreshes
        // the HU cache. Populate the all-seat span before comparing dispatches.
        let (start,count)=gpu.eq_spans[s.n];assert!(count>0);
        unsafe {gpu.stream.launch_builder(&gpu.f_equities)
            .arg(&gpu.d_eq_work).arg(&start).arg(&gpu.d_eq_blocks).arg(&gpu.d_eq)
            .arg(&gpu.d_reach).arg(&gpu.d_reach_mass).arg(&mut gpu.d_eq_cache)
            .launch(PreflopGpu::cfg(count)).unwrap();}
        let slots=gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
        for p in 0..s.n {
            let mut answers=Vec::new();
            // Only dispatch changes. Cache allocation remains valid and no graph
            // exists; all reaches, masses, terminals and coupled grouping are fixed.
            for enabled in [1,0] {
                gpu.use_eq_cache=enabled;
                gpu.terminals(p as i32).unwrap();
                let values=gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let mut hu=Vec::new();
                for (nd,n) in s.nodes.iter().enumerate().filter(|(_,n)|n.kind==KIND_POT_SHARE && n.live.count_ones()==2) {
                    let _=n;let at=slots[nd] as usize*NUM_CLASSES;
                    hu.extend(values[at..at+NUM_CLASSES].iter().map(|x|x.to_bits()));
                }
                assert!(!hu.is_empty());answers.push(hu);
            }
            assert_eq!(answers[0],answers[1],"HU cache changes terminal bits for seat {p}");
        }
    }
