        let zero_blocks: [[usize;2];2] = std::array::from_fn(|p|
            std::array::from_fn(|which| gpu.arena_layout[p].inactive.iter()
                .filter(|b|b.initial[which]==usize::MAX).count()));
        let explicit_blocks: [[usize;2];2] = std::array::from_fn(|p|
            std::array::from_fn(|which| gpu.arena_layout[p].inactive.iter()
                .filter(|b|b.initial[which]!=usize::MAX).count()));
        let full_calls = if storage==Storage::Compressed {zero_blocks.iter().flatten().sum()} else {0};
        let strategy_calls = if storage==Storage::Compressed {zero_blocks[0][1]+zero_blocks[1][1]} else {0};
        if storage==Storage::Compressed && iso {
            assert!(zero_blocks.iter().flatten().all(|n|*n>0));
            assert!(explicit_blocks.iter().flatten().all(|n|*n>0));
        }
        let sync_full = |g:&mut GpuSolver,s:&mut Solver| -> R<()> {
            let n=E041_ZERO_RESTORES.load(Ordering::SeqCst);
            g.sync_to_cpu(s)?;
            assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst)-n,full_calls);
            Ok(())
        };
        let mut reference = target(&spot,storage,iso);
        let mut candidate = target(&spot,storage,iso);
        let poisoned = host_image(&candidate);
        retain(dir,"poisoned.host.bin",&poisoned,&mut files)?;
        assert_eq!(poisoned,host_image(&reference));
        let count_before=E041_ZERO_RESTORES.load(Ordering::SeqCst);
        legacy_sync(&mut gpu,&mut reference)?;
        assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst),count_before);
        sync_full(&mut gpu,&mut candidate)?;
        let first=host_image(&reference);
        pair(dir,"first.host",first.clone(),host_image(&candidate),&mut files)?;
        pair(dir,"first.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"first",&reference,&candidate,&mut files)?;
        assert_eq!(host_image(&reference),first);assert_eq!(host_image(&candidate),first);
        reference.ensure_symmetric();candidate.ensure_symmetric();
        let materialized=host_image(&reference);
        pair(dir,"materialized.host",materialized.clone(),host_image(&candidate),&mut files)?;
        if iso {assert_ne!(materialized,first);}
        pair(dir,"materialized.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"materialized",&reference,&candidate,&mut files)?;
        legacy_sync(&mut gpu,&mut reference)?;sync_full(&mut gpu,&mut candidate)?;
        pair(dir,"repeat.host",host_image(&reference),host_image(&candidate),&mut files)?;
        assert_eq!(host_image(&candidate),first);
        // Strategy-only readback uses the same inactive writer and must preserve regrets.
        let mut sr=target(&spot,storage,iso);let mut sc=target(&spot,storage,iso);
        let raw_regrets = |s:&Solver| -> Vec<u32> {
            let mut out=Vec::new();
            for store in &s.regrets {
                match store {
                    Store::F32(b) => out.extend(b.as_slice().iter().map(|v|v.to_bits())),
                    Store::I16 {q,scale} => {
                        out.extend(q.as_slice().iter().map(|v|*v as u16 as u32));
                        out.extend(scale.as_slice().iter().map(|v|v.to_bits()));
                    }
                    Store::U16 {q,scale} => {
                        out.extend(q.as_slice().iter().map(|v|*v as u32));
                        out.extend(scale.as_slice().iter().map(|v|v.to_bits()));
                    }
                }
            }
            out
        };
        let regret_before=raw_regrets(&sc);
        let n=E041_ZERO_RESTORES.load(Ordering::SeqCst);
        legacy_strategy(&mut gpu,&mut sr)?;
        assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst),n);
        gpu.sync_strategy(&mut sc)?;
        assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst)-n,strategy_calls);
        assert_eq!(regret_before,raw_regrets(&sc));
        pair(dir,"strategy.host",host_image(&sr),host_image(&sc),&mut files)?;
        pair(dir,"strategy.query",query_image(&sr),query_image(&sc),&mut files)?;
        saves(dir,"strategy",&sr,&sc,&mut files)?;
        sr.ensure_symmetric();sc.ensure_symmetric();
        pair(dir,"strategy_materialized.host",host_image(&sr),host_image(&sc),&mut files)?;
        pair(dir,"strategy_materialized.query",query_image(&sr),query_image(&sc),&mut files)?;
        saves(dir,"strategy_materialized",&sr,&sc,&mut files)?;
        legacy_sync(&mut gpu,&mut sr)?;sync_full(&mut gpu,&mut sc)?;
        pair(dir,"after_strategy_full.host",host_image(&sr),host_image(&sc),&mut files)?;
        assert_eq!(host_image(&sc),first);
        let after=device_image(&gpu)?;
        retain(dir,"final.gpu.bin",&after,&mut files)?;assert_eq!(before,after);
        // Continue the same live GPU learner; readback must also match the fresh later state.
        for _ in 0..2 {gpu.iterate()?;}
        let continued=device_image(&gpu)?;
        retain(dir,"continued_trained.gpu.bin",&continued,&mut files)?;
        assert_ne!(continued,before);
        legacy_sync(&mut gpu,&mut reference)?;sync_full(&mut gpu,&mut candidate)?;
        assert_eq!(candidate.iteration,6);
        pair(dir,"continued.host",host_image(&reference),host_image(&candidate),&mut files)?;
        pair(dir,"continued.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"continued",&reference,&candidate,&mut files)?;
        let continued_after=device_image(&gpu)?;
        retain(dir,"continued_after.gpu.bin",&continued_after,&mut files)?;
        assert_eq!(continued,continued_after);assert_eq!(geometry(&gpu),shape);
        gpu.synchronize()?;drop(gpu);owner.check_err().map_err(e)?;
        let bytes:u64=files.iter().map(|v|v["bytes"].as_u64().unwrap()).sum();
        assert!(bytes<=32*1024*1024);
        Ok(json!({"storage":format!("{storage:?}"),"compact":iso,"nodes":spot.tree.nodes.len(),
            "host_elements":spot.tree.data_size,"device_elements":shape.2,"staging_words":shape.1,
            "zero_blocks":zero_blocks,"explicit_blocks":explicit_blocks,
            "observed_zero_calls_per_full_sync":full_calls,"observed_zero_calls_per_strategy_sync":strategy_calls,
            "training_iterations":[4,6],"full_raw_equality":true,"query_save_exact":true,
            "materialization_changed_host":materialized!=first,"repeat_restores_first":true,
            "strategy_only_preserves_regrets":true,"gpu_learning_unchanged_by_readbacks":true,
            "staging_identity_and_device_lengths_unchanged":true,"cleanup_complete":true,
            "files":files,"output_bytes":bytes}))
    }

    #[test]
    #[ignore = "root-only E041 accepted-writer GPU control; CUDA and fresh E041_CONTROL_DIR required"]
    fn exact_zero_restore_gpu_lifecycle() -> R<()> {
        let dir=PathBuf::from(std::env::var_os("E041_CONTROL_DIR").ok_or("E041_CONTROL_DIR missing")?);
        std::fs::create_dir(&dir).map_err(e)?;let mut cases=Vec::new();
        for (name,storage,iso) in [("compressed-full",Storage::Compressed,false),
            ("compressed-compact",Storage::Compressed,true),("f32-full",Storage::F32,false),
            ("f32-compact",Storage::F32,true)] {
            let path=dir.join(name);std::fs::create_dir(&path).map_err(e)?;
            let result=run_case(&path,storage,iso)?;
            println!("E041_ZERO_CONTROL {}",json!({"stage":"case_complete","name":name,"result":result}));
            cases.push(result);
        }
        let summary=json!({"id":"E041-control","stage":"complete","cases":cases,
            "performance_measured":false,"candidate_accepted":false});
        retain(&dir,"evidence.json",&serde_json::to_vec_pretty(&summary).map_err(e)?,&mut Vec::new())?;
        println!("E041_ZERO_CONTROL {summary}");Ok(())
    }
}
