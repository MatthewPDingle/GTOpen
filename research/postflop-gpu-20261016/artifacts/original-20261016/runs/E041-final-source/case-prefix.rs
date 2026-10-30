    fn run_case(dir: &Path, storage: Storage, iso: bool) -> R<Value> {
        let size = StreetSizing { bet:parse_sizes("50")?,raise:vec![],donk:vec![] };
        let spot = Arc::new(Spot::new_with_limit(SpotConfig {
            board:"KsQs2dJd".into(),range_oop:"AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
            range_ip:"AA,QQ,TT,77,AQs,KQs,AQo".into(),
            tree:TreeConfig { starting_pot:10.0,effective_stack:20.0,
                oop:[size.clone(),size.clone(),size.clone()],ip:[size.clone(),size.clone(),size],
                ..Default::default() },
        },Some(20_000))?);
        assert!(spot.tree.data_size.iter().sum::<u64>() <= 250_000);
        let mut input = Solver::with_storage(spot.clone(),storage);
        input.use_isomorphism = iso; seed(&mut input,1);
        let plan = GpuPlan::build(&spot,iso);
        if iso {
            let mut inactive_ordinal = [0usize;2];
            for (i,node) in spot.tree.nodes.iter().enumerate() {
                if node.kind == KIND_ACTION && plan.node_data_off[i] == u64::MAX {
                    let p = node.player as usize;
                    inactive_ordinal[p] += 1;
                    if inactive_ordinal[p] % 2 != 0 { continue; }
                    let count = node.num_children as usize * spot.hands[p].len();
                    for store in [&input.regrets[p],&input.strat[p]] {
                        unsafe { store.write_f32(i as u32,node.data_offset,count,&vec![0.0;count]); }
                    }
                    if let Store::F32(b) = &input.regrets[p] {
                        unsafe { b.write_at(node.data_offset as usize,-0.0); }
                    }
                }
            }
        }
        let budget = if storage == Storage::F32 && iso {
            plan.staging_bytes() + (plan.arena_elements[0]+plan.arena_elements[1]) as u64 * 8 + 512*1024*1024
        } else { u64::MAX };
        let mut gpu = DrainOnDrop(GpuSolver::new_with_budget(&input,budget)?);
        let owner = gpu._ctx.clone();
        for p in 0..2 {
            assert_eq!(gpu.arena_layout[p].compact,iso);
            if iso {
                assert!(!gpu.arena_layout[p].inactive.is_empty());
                assert!(!gpu.arena_layout[p].initial[0].is_empty());
                assert!(!gpu.arena_layout[p].initial[1].is_empty());
                assert!(gpu.arena_layout[p].inactive.iter().any(|b| b.initial[1] == usize::MAX));
            }
        }
        let shape = geometry(&gpu);
        let mut files = Vec::new();
        retain(dir,"input.host.bin",&host_image(&input),&mut files)?;
        for _ in 0..4 { gpu.iterate()?; }
        let before = device_image(&gpu)?;
        retain(dir,"trained.gpu.bin",&before,&mut files)?;
