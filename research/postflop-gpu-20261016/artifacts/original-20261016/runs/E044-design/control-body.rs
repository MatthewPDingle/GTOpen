    fn spot(tiny:bool,iso:bool)->R<Arc<Spot>> {
        let size=StreetSizing {bet:if tiny {vec![]}else{parse_sizes("50")?},raise:vec![],donk:vec![]};
        Ok(Arc::new(Spot::new_with_limit(SpotConfig {
            board:if tiny {"Th9h2c3d4s"}else{"KsQs2dJd"}.into(),
            range_oop:if tiny {"AcAd"}else{"AA,KK,QQ,JJ,AKs,AQs,AKo"}.into(),
            range_ip:if tiny {"KcKd"}else{"AA,QQ,TT,77,AQs,KQs,AQo"}.into(),
            tree:TreeConfig {starting_pot:10.0,effective_stack:20.0,
                rake_pct:if iso {0.05}else{0.0},rake_cap:1.0,
                oop:[size.clone(),size.clone(),size.clone()],ip:[size.clone(),size.clone(),size],..Default::default()},
        },Some(20_000))?))
    }
    fn cpu_target(input:&Solver)->Solver {
        let mut s=target(&input.spot,input.storage,input.use_isomorphism);s.algo=input.algo;
        s.locks=input.locks.clone();s.lock_labels=input.lock_labels.clone();s
    }
    fn gpu_image(g:&GpuSolver)->R<Vec<u8>> {
        g.synchronize()?;let mut out=b"E044GPU1".to_vec();u64_word(&mut out,g.iteration as u64);
        for n in [g.nh[0],g.nh[1],g.nh_max] {u32_word(&mut out,n as u32);}
        for d in [&g.d_regrets[0],&g.d_regrets[1],&g.d_strat[0],&g.d_strat[1],
            &g.d_reach[0],&g.d_reach[1],&g.d_cfv,&g.d_eval_roots,&g.d_disc] {
            let v=g.stream.clone_dtoh(d).map_err(e)?;g.synchronize()?;
            u64_word(&mut out,v.len() as u64);for x in v {u32_word(&mut out,x.to_bits());}
        }
        Ok(out)
    }
    fn run_case(dir:&Path,storage:Storage,iso:bool,tight:bool,tiny:bool,algo:Algorithm)->R<Value> {
        let sp=spot(tiny,iso)?;assert!(sp.tree.data_size.iter().sum::<u64>()<=250_000);
        let mut input=Solver::with_storage(sp.clone(),storage);input.use_isomorphism=iso;input.algo=algo;seed(&mut input,1);
        let plan=GpuPlan::build(&sp,iso);
        let budget=if tight {plan.staging_bytes()+(plan.arena_elements[0]+plan.arena_elements[1]) as u64*8+512*1024*1024}else{u64::MAX};
        let mut reference=GpuSolver::new_with_budget(&input,budget)?;let mut candidate=GpuSolver::new_with_budget(&input,budget)?;
        let bg=geometry(&reference);let cg=geometry(&candidate);assert_eq!(bg.1,cg.1);assert_eq!(bg.2,cg.2);
        let eligible=cg.1>=6;assert_eq!(eligible,!tiny);
        let compact=cg.2[0]<(sp.tree.data_size[0] as usize);assert_eq!(compact,iso&&(storage==Storage::Compressed||tight));
        let mut files=Vec::new();retain(dir,"input.host.bin",&host_image(&input),&mut files)?;
        pair(dir,"initial.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        let mut total=0;
        for (k,batch) in [1usize,2,3,5,8].into_iter().enumerate() {
            for _ in 0..batch {reference.e044_original_iterate()?;}
            for _ in 0..batch {candidate.iterate()?;}
            total+=batch;assert_eq!(reference.discount_stage.used,0);
            assert_eq!(candidate.discount_stage.used,if eligible {(total-1)%2+1}else{0});
            pair(dir,&format!("batch{k}.gpu"),gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        }
        assert_eq!(total,19);
        let bp=reference.e044_original_profiled()?;let cp=candidate.iterate_profiled()?;assert_eq!(bp.launches,cp.launches);
        pair(dir,"profiled.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        let mut bh=cpu_target(&input);let mut ch=cpu_target(&input);
        reference.sync_to_cpu(&mut bh)?;candidate.sync_to_cpu(&mut ch)?;assert_eq!(candidate.discount_stage.used,0);
        assert_eq!(bh.algo,ch.algo);assert_eq!(ch.algo,algo);
        pair(dir,"first.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"first.query",query_image(&bh),query_image(&ch),&mut files)?;saves(dir,"first",&bh,&ch,&mut files)?;
        bh.ensure_symmetric();ch.ensure_symmetric();
        pair(dir,"materialized.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"materialized.query",query_image(&bh),query_image(&ch),&mut files)?;
        let be=reference.exploitability(&bh)?;let ce=candidate.exploitability(&ch)?;assert_eq!(be.to_bits(),ce.to_bits());
        pair(dir,"evaluation.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        // Queue one iteration before lock-table replacement drains and invalidates graphs.
        reference.e044_original_iterate()?;candidate.iterate()?;
        bh.lock_node(&[],LockMode::Freeze,"pipeline-control".into())?;ch.lock_node(&[],LockMode::Freeze,"pipeline-control".into())?;
        reference.update_locks(&bh)?;candidate.update_locks(&ch)?;
        reference.e044_original_iterate()?;candidate.iterate()?;
        pair(dir,"locked.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        reference.sync_strategy(&mut bh)?;candidate.sync_strategy(&mut ch)?;assert_eq!(candidate.discount_stage.used,0);
        pair(dir,"strategy.host",host_image(&bh),host_image(&ch),&mut files)?;
        reference.sync_to_cpu(&mut bh)?;candidate.sync_to_cpu(&mut ch)?;
        pair(dir,"locked_full.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"locked_full.query",query_image(&bh),query_image(&ch),&mut files)?;saves(dir,"locked_full",&bh,&ch,&mut files)?;
        assert!(bh.unlock_node(&[])?&&ch.unlock_node(&[])?);reference.update_locks(&bh)?;candidate.update_locks(&ch)?;
        for _ in 0..2 {reference.e044_original_iterate()?;candidate.iterate()?;}
        pair(dir,"continued.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        reference.sync_to_cpu(&mut bh)?;candidate.sync_to_cpu(&mut ch)?;
        assert_eq!(ch.iteration,24);assert_eq!(candidate.discount_stage.used,0);
        pair(dir,"continued.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"continued.query",query_image(&bh),query_image(&ch),&mut files)?;saves(dir,"continued",&bh,&ch,&mut files)?;
        assert_eq!(geometry(&reference),bg);assert_eq!(geometry(&candidate),cg);
        let bo=reference._ctx.clone();let co=candidate._ctx.clone();drop(reference);drop(candidate);bo.check_err().map_err(e)?;co.check_err().map_err(e)?;
        let bytes:u64=files.iter().map(|f|f["bytes"].as_u64().unwrap()).sum();assert!(bytes<=64*1024*1024);
        Ok(json!({"storage":format!("{storage:?}"),"algorithm":format!("{algo:?}"),"iso":iso,"compact":compact,"tiny":tiny,"tight":tight,
            "pinned_pipeline_eligible":eligible,"staging_words":cg.1,"arena_words":cg.2,"iterations":24,"profiled_iteration":20,
            "unsynchronized_batch_lengths":[1,2,3,5,8],"gpu_raw_exact":true,"cpu_query_save_exact":true,"ev_bits":ce.to_bits(),
            "locks_resume_exact":true,"full_and_strategy_readback_reset_slots":true,"staging_geometry_unchanged":true,
            "cleanup_complete":true,"files":files,"output_bytes":bytes}))
    }
    fn drop_controls()->R<Vec<Value>> {
        let sp=spot(false,false)?;let mut input=Solver::with_storage(sp,Storage::Compressed);input.use_isomorphism=false;seed(&mut input,1);
        let mut outcomes=Vec::new();
        for mode in 0..3 {
            let gpu=GpuSolver::new(&input)?;assert!(gpu.h_staging.len>=6);
            let stream=gpu.stream.clone();let owner=gpu._ctx.clone();
            let before=DISCOUNT_STAGE_DRAINS.load(Ordering::SeqCst);DISCOUNT_STAGE_LAST_QUERY.store(-7,Ordering::SeqCst);
            let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(move ||->R<()> {
                let mut g=gpu;
                if mode==1 {
                    DISCOUNT_STAGE_FAIL_NEXT.store(true,Ordering::SeqCst);
                    assert_eq!(g.iterate().unwrap_err(),"injected discount upload error");
                } else {
                    g.iterate()?;g.iterate()?;
                    if mode==2 {panic!("injected discount staging unwind");}
                }
                Ok(())
            }));
            if mode==2 {assert!(result.is_err());}else{result.unwrap()?;}
            assert_eq!(DISCOUNT_STAGE_DRAINS.load(Ordering::SeqCst)-before,1);
            assert_eq!(DISCOUNT_STAGE_LAST_QUERY.load(Ordering::SeqCst),0);
            // The stored query was inside the first-field guard, before CUDA/pinned fields released.
            stream.synchronize().map_err(e)?;owner.check_err().map_err(e)?;
            outcomes.push(json!({"mode":mode,"drain_calls":1,"stream_ready_before_field_release":true,"cleanup_complete":true}));
        }
        Ok(outcomes)
    }
    #[test]
    #[ignore = "root-only E044 pinned discount lifecycle; CUDA and fresh E044_CONTROL_DIR required"]
    fn exact_two_slot_discount_lifecycle()->R<()> {
        let dir=PathBuf::from(std::env::var_os("E044_CONTROL_DIR").ok_or("E044_CONTROL_DIR missing")?);std::fs::create_dir(&dir).map_err(e)?;
        assert!(std::mem::size_of::<GpuSolver>()<=std::mem::size_of::<OriginalGpuSolverSize>()+32);
        let mut cases=Vec::new();
        for (an,algo) in [("dcfr",Algorithm::Dcfr),("cfr-plus",Algorithm::CfrPlus)] {
            for (label,storage,iso,tight,tiny) in [("compressed-full",Storage::Compressed,false,false,false),
                ("compressed-compact",Storage::Compressed,true,false,false),("f32-full",Storage::F32,false,false,false),
                ("f32-iso-full",Storage::F32,true,false,false),("f32-compact",Storage::F32,true,true,false),
                ("tiny-compressed",Storage::Compressed,false,false,true),("tiny-f32",Storage::F32,false,false,true)] {
                let name=format!("{an}-{label}");let path=dir.join(&name);std::fs::create_dir(&path).map_err(e)?;
                let result=run_case(&path,storage,iso,tight,tiny,algo)?;
                println!("E044_DISCOUNT_CONTROL {}",json!({"stage":"case_complete","name":name,"result":result}));cases.push(json!({"name":name,"result":result}));
            }
        }
        let drops=drop_controls()?;
        let summary=json!({"id":"E044-control","stage":"complete","cases":cases,"drop_controls":drops,
            "original_solver_size":std::mem::size_of::<OriginalGpuSolverSize>(),"candidate_solver_size":std::mem::size_of::<GpuSolver>(),
            "discount_stage_size":std::mem::size_of::<DiscountStage>(),"performance_measured":false,"candidate_accepted":false});
        retain(&dir,"evidence.json",&serde_json::to_vec_pretty(&summary).map_err(e)?,&mut Vec::new())?;
        println!("E044_DISCOUNT_CONTROL {summary}");Ok(())
    }
}
