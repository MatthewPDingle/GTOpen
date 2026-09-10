    #[test]
    fn terminal_work_budget_keeps_batch_and_normalization_mode() {
        let slots = 1000usize;
        let particle = slots * (NUM_CLASSES + 1) * 4;
        let norm = slots * NUM_CLASSES * 4;
        for available in [particle, norm + particle, norm + 32 * particle] {
            let baseline = multiway_batch_plan(available, slots).unwrap().unwrap();
            assert!(!terminal_work_preserves_plan(available, slots, 4, &baseline).unwrap(),
                "boundary must retain identity kernel indexing");
            assert!(terminal_work_preserves_plan(available + 4096, slots, 4096, &baseline).unwrap());
        }
        let baseline = multiway_batch_plan(particle, slots).unwrap().unwrap();
        assert!(!terminal_work_preserves_plan(0, slots, usize::MAX, &baseline).unwrap());
    }

    #[test]
    fn coupled_live_terminal_work_matches_identity_indexing() {
        let eq = phase_test_equity();
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"], "stack":5.0, "posts":[0.0,0.0,0.5,1.0],
            "limp":true, "open_raises":[2.0], "raise_mults":[3.0], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let mut records = Vec::new();
        for indexed in [false, true] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
            assert_eq!(gpu.use_mw_terminal_work, 1, "fixture must fit the worklist");
            let terms = gpu.stream.clone_dtoh(&gpu.d_mw_terms).unwrap();
            let work = gpu.stream.clone_dtoh(&gpu.d_mw_terminal_work).unwrap();
            let mut selected = 0usize;
            for p in 0..s.n {
                let expected: Vec<u32> = terms.iter().enumerate()
                    .filter(|(_,nd)| s.nodes[**nd as usize].live & (1 << p) != 0)
                    .map(|(i,_)|i as u32).collect();
                let (start,count) = gpu.mw_terminal_spans[p];
                assert_eq!(&work[start as usize..(start+count) as usize], expected.as_slice());
                selected += count as usize;
            }
            assert!(selected < s.n * terms.len(), "fixture must omit folded-seat blocks");
            assert_eq!(selected, terms.iter().map(|&nd|s.nodes[nd as usize].live.count_ones() as usize).sum::<usize>());
            gpu.use_mw_terminal_work = indexed as i32;
            let mut rounds = Vec::new();
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();
                let (gaps,evs) = gpu.gaps_and_evs().unwrap();
                rounds.push((
                    gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.eval_graph.is_some() && gpu.learning_graphs.iter().any(Option::is_some));
            for graph in &mut gpu.learning_graphs { *graph = None; } gpu.eval_graph = None;
            let target = s.nodes.iter().position(|nd|nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 3).unwrap();
            let live: Vec<usize> = (0..s.n).filter(|&p|s.nodes[target].live & (1 << p) != 0).collect();
            let folded = (0..s.n).find(|&p|s.nodes[target].live & (1 << p) == 0).unwrap();
            let (p,other) = (live[0],live[1]);
            let first = s.nodes.iter().position(|nd|nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 3 && nd.live & (1 << p) == 0).unwrap();
            // Target has original index 1 but local work index 0 for p. A
            // mistaken terminal_prob[blockIdx.x] therefore reads the wrong zero.
            gpu.test_set_multiway_terms(&s, &[first as u32, target as u32]);
            gpu.use_mw_terminal_work = indexed as i32;
            let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            let base = slots[target] as usize * NUM_CLASSES;
            let mut terminals = Vec::new();
            for batch in [32u32,7] {
                gpu.mw_batch = batch;
                for (seat,gate,zero) in [(p,1,None),(p,1,Some(p)),(p,1,Some(other)),
                    (p,0,None),(folded,1,None),(p,1,Some(folded)),(p,0,None)] {
                    let mut reach = vec![0f32;gpu.d_reach.len()];
                    for (block,r) in reach.chunks_exact_mut(NUM_CLASSES).enumerate() {
                        r[(block*17)%NUM_CLASSES]=0.125;
                        r[(block*17+53)%NUM_CLASSES]=0.25;
                        r[(block*17+107)%NUM_CLASSES]=0.5;
                    }
                    if let Some(q)=zero {
                        let off=sources[target*s.n+q] as usize*NUM_CLASSES;
                        reach[off..off+NUM_CLASSES].fill(0.0);
                    }
                    gpu.d_reach=gpu.stream.clone_htod(&reach).unwrap();
                    unsafe { gpu.stream.launch_builder(&gpu.f_reach_mass)
                        .arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                        .launch(LaunchConfig {block_dim:(128,1,1),..PreflopGpu::cfg((reach.len()/NUM_CLASSES) as u32)}).unwrap(); }
                    gpu.d_val=gpu.stream.clone_htod(&vec![123456.0f32;gpu.d_val.len()]).unwrap();
                    gpu.d_mw_cdf=gpu.stream.clone_htod(&vec![f32::NAN;gpu.d_mw_cdf.len()]).unwrap();
                    gpu.d_mw_normalized=gpu.stream.clone_htod(&vec![f32::NAN;gpu.d_mw_normalized.len()]).unwrap();
                    gpu.terminals_masked(seat as i32,gate).unwrap();
                    let actual=gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                    let local:Vec<Vec<f32>>=(0..s.n).map(|q|{
                        let off=sources[target*s.n+q] as usize*NUM_CLASSES;
                        reach[off..off+NUM_CLASSES].to_vec()
                    }).collect();
                    let mut expected=vec![0f32;NUM_CLASSES];
                    s.terminal_value(target,seat,&local,&mut expected);
                    for h in 0..NUM_CLASSES {
                        assert!(actual[base+h].is_finite() && (actual[base+h]-expected[h]).abs()<2e-5,
                            "indexed={indexed}, seat={seat}, gate={gate}, zero={zero:?}, batch={batch}, h={h}");
                    }
                    if zero.is_some_and(|q|q!=seat) { assert!(actual[base..base+NUM_CLASSES].iter().all(|&x|x==0.0)); }
                    terminals.push(actual[base..base+NUM_CLASSES].iter().map(|x|x.to_bits()).collect::<Vec<_>>());
                }
            }
            records.push((rounds,terminals));
        }
        assert_eq!(records[0],records[1],"static work indices changed solver or terminal output bits");
    }

