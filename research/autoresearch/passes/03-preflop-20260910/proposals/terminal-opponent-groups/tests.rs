    #[test]
    fn opponent_groups_cover_terms_stably_without_extra_device_indices() {
        let live:Vec<i32>=[6u32,3,5,4,3,7,5,4].iter().map(|&n|(1i32<<n)-1).collect();
        let original=vec![7u32,2,1,6,3,0,5,4];let mut terms=original.clone();
        let spans=group_multiway_terms(&mut terms,&live).unwrap();
        assert_eq!(spans,[(0,2),(2,2),(4,2),(6,2)]);
        assert_eq!(terms,vec![1,4,7,3,2,6,0,5]);
        let mut a=original.clone();let mut b=terms.clone();a.sort();b.sort();assert_eq!(a,b);
        for (group,&(start,count)) in spans.iter().enumerate() {
            for &nd in &terms[start as usize..(start+count) as usize] {
                assert_eq!((live[nd as usize].count_ones().min(6)-3) as usize,group);
            }
        }
        assert_eq!(group_multiway_terms(&mut [],&live).unwrap(),[(0,0);4]);
        assert!(group_multiway_terms(&mut [99],&live).is_err());
        assert!(group_multiway_terms(&mut [0],&[3]).is_err()); // only two live players
    }

    #[test]
    fn opponent_group_dispatch_matches_generic_arenas_graphs_and_partial_batches() {
        let eq=phase_test_equity();
        let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
            "positions":["UTG","HJ","CO","BTN","SB","BB"],"stack":2.0,"posts":[0.0,0.0,0.0,0.0,0.5,1.0],
            "limp":true,"open_raises":[],"raise_mults":[3.0],"max_raises":1,"add_allin":false,
            "rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
        })).unwrap();
        let mut results=Vec::new();let mut metadata=Vec::new();
        for grouped in [false,true] {
            let mut s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            let mut gpu=PreflopGpu::new(&s,2000).unwrap();gpu.use_mw_groups=grouped;
            assert!(gpu.use_mw_prepared && gpu.mw_term_groups.iter().all(|&(_,n)|n>0));
            metadata.push((gpu.mw_batch,gpu.use_eq_cache,gpu.d_mw_cdf.len(),gpu.d_mw_normalized.len()));
            let values=ValuePlan::build(&s);
            let terminal_slots:Vec<_>=s.nodes.iter().enumerate().filter(|(_,n)|n.kind!=KIND_ACTION).map(|(nd,_)|values.slots[nd]).collect();
            let unique:std::collections::BTreeSet<_>=terminal_slots.iter().copied().collect();
            assert_eq!(unique.len(),terminal_slots.len(),"terminals must not alias value slots");
            let mut checks=Vec::new();
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();let (g,e)=gpu.gaps_and_evs().unwrap();
                checks.push((gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    g.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),e.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.learning_graphs.iter().any(|g|g.is_some()) && gpu.eval_graph.is_some());
            for g in &mut gpu.learning_graphs {*g=None;}gpu.eval_graph=None;
            let sources=gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let target=s.nodes.iter().position(|n|n.kind==KIND_POT_SHARE && n.live.count_ones()==3 && n.live&1!=0).unwrap();
            let other=(1..s.n).find(|&p|s.nodes[target].live&(1<<p)!=0).unwrap();
            let mut terminal_checks=Vec::new();
            for (batch,gate,zero) in [(32,1,false),(7,1,false),(7,1,true),(7,0,false)] {
                gpu.mw_batch=batch;
                let mut reach=vec![0f32;gpu.d_reach.len()];
                for (block,r) in reach.chunks_exact_mut(NUM_CLASSES).enumerate() {
                    let h=block*17%NUM_CLASSES;r[h]=0.03125;r[(h+53)%NUM_CLASSES]=0.0625;r[(h+107)%NUM_CLASSES]=0.125;
                }
                if zero {let off=sources[target*s.n+other] as usize*NUM_CLASSES;reach[off..off+NUM_CLASSES].fill(0.0);}
                gpu.d_reach=gpu.stream.clone_htod(&reach).unwrap();
                unsafe {gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                    .launch(LaunchConfig{block_dim:(128,1,1),..PreflopGpu::cfg((reach.len()/NUM_CLASSES) as u32)}).unwrap();}
                // Manual reach replacement bypasses down()'s HU cache update.
                let (start,count)=gpu.eq_spans[s.n];
                if gpu.use_eq_cache!=0 && count>0 {unsafe {gpu.stream.launch_builder(&gpu.f_equities)
                    .arg(&gpu.d_eq_work).arg(&start).arg(&gpu.d_eq_blocks).arg(&gpu.d_eq)
                    .arg(&gpu.d_reach).arg(&gpu.d_reach_mass).arg(&mut gpu.d_eq_cache)
                    .launch(PreflopGpu::cfg(count)).unwrap();}}
                gpu.d_mw_cdf=gpu.stream.clone_htod(&vec![f32::NAN;gpu.d_mw_cdf.len()]).unwrap();
                if gpu.use_mw_normalized {gpu.d_mw_normalized=gpu.stream.clone_htod(&vec![f32::NAN;gpu.d_mw_normalized.len()]).unwrap();}
                gpu.d_val=gpu.stream.clone_htod(&vec![123456f32;gpu.d_val.len()]).unwrap();
                gpu.terminals_masked(0,gate).unwrap();let actual=gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let mut bits=Vec::new();
                for (nd,n) in s.nodes.iter().enumerate().filter(|(_,n)|n.kind!=KIND_ACTION) {
                    let _=n;let at=values.slots[nd] as usize*NUM_CLASSES;
                    assert!(actual[at..at+NUM_CLASSES].iter().all(|x|x.is_finite()));
                    bits.extend(actual[at..at+NUM_CLASSES].iter().map(|x|x.to_bits()));
                }
                if zero {let at=values.slots[target] as usize*NUM_CLASSES;assert!(actual[at..at+NUM_CLASSES].iter().all(|x|*x==0.0));}
                terminal_checks.push(bits);
            }
            assert_eq!(terminal_checks[1],terminal_checks[3],"ungated recovery must restore same batch7 values");
            results.push((checks,terminal_checks));
        }
        assert_eq!(metadata[0],metadata[1],"grouping must not change memory, B or HU cache");
        assert_eq!(results[0],results[1]);
    }
