use super::*;
use crate::preflop::{PreflopConfig,equity::EquityTable};
fn eq()->Arc<EquityTable>{
    let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
    let b=std::fs::read(path).unwrap();Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(b[..4].try_into().unwrap())))
}
fn fixture(np:usize,fixed:bool)->PreflopSolver{
    let mut posts=vec![0.;np];posts[np-2]=0.5;posts[np-1]=1.;
    let cfg:PreflopConfig=serde_json::from_value(json!({"positions":(0..np).map(|p|format!("P{p}")).collect::<Vec<_>>(),
        "stack":10,"posts":posts,"limp":true,"open_raises":if np<=5{vec![2]}else{vec![]},"raise_mults":[],
        "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"})).unwrap();
    let mut s=PreflopSolver::new(cfg,eq()).unwrap();s.research_seed_quality_fixture_averages().unwrap();
    if fixed{s.seat_frozen[np-2]=true;let node=s.child(0,1);let mut lock=vec![0.;s.nodes[node].actions.len()*NUM_CLASSES];
        lock[..NUM_CLASSES].fill(1.);s.point_locks.insert(node as u32,lock);}
    s
}
fn engine(s:&PreflopSolver,batch:u32,packed:bool)->PreflopGpu{
    let mut g=PreflopGpu::new(s,2000).unwrap();assert!(g.exact_reuse_compatible());
    // Test fixtures explicitly compare identical sample schedules. Real saves
    // will use the native planner's batch without this fixture-only override.
    let capacity=g.d_mw_normalized.len()/NUM_CLASSES;
    g.mw_batch=batch;let empty=g.stream.null::<f32>().unwrap();drop(std::mem::replace(&mut g.d_mw_cdf,empty));
    g.d_mw_cdf=g.stream.alloc_zeros::<f32>(capacity*batch as usize*170).unwrap();
    if packed{promote(g,s,2000).unwrap()}else{g}
}
fn bits(g:&PreflopGpu)->(Vec<u32>,Vec<u32>,Vec<u32>){
    (g.stream.clone_dtoh(&g.d_regrets).unwrap().iter().map(|v|v.to_bits()).collect(),
     g.stream.clone_dtoh(&g.d_strat).unwrap().iter().map(|v|v.to_bits()).collect(),
     g.stream.clone_dtoh(&g.d_eval_roots).unwrap().iter().map(|v|v.to_bits()).collect())
}
fn output()->std::path::PathBuf{std::path::PathBuf::from(std::env::var("PREFLOP_GPU_ORDINARY_STATIC_OUTPUT").unwrap())}

#[test]
fn complete_states_graphs_policies_and_batches(){
    let mut cases=Vec::new();
    for np in [3,4,7,9]{for fixed in [false,true]{for batch in [1,4,5,32]{
        let mut expected=None;
        for packed in [false,true]{
            let mut s=fixture(np,fixed);let initial=s.arena_snapshot();let mut g=engine(&s,batch,packed);
            assert_eq!(initial,s.arena_snapshot());assert!(g.research_cohorts.is_none()&&g.research_exact_reuse.is_none());
            let mut rounds=Vec::new();
            for _ in 0..3{g.iterate(&mut s).unwrap();let metrics=g.gaps_and_evs().unwrap();rounds.push((bits(&g),metrics));}
            assert!(g.eval_graph.is_some());assert!(g.learning_graphs.iter().any(|x|x.is_some()));
            let before=bits(&g);let age=s.iteration;
            assert!(!g.try_iterate(&mut s,Some(&AtomicBool::new(true))).unwrap());assert_eq!(age,s.iteration);assert_eq!(before,bits(&g));
            g.sync_to_cpu(&mut s).unwrap();let arena=s.arena_snapshot();
            assert_eq!(arena.0.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),before.0);
            assert_eq!(arena.1.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),before.1);
            if let Some(ref expected)=expected{assert!(&rounds==expected,"np={np} fixed={fixed} batch={batch}");}else{expected=Some(rounds);}
        }
        cases.push(json!({"players":np,"fixed":fixed,"batch":batch,"rounds":3,"exact":true}));
    }}}
    std::fs::write(output().join("states.json"),serde_json::to_vec_pretty(&cases).unwrap()).unwrap();
}

#[test]
fn terminals_zero_mass_recovery(){
    for np in [4,9]{for batch in [4,5]{
        let s=fixture(np,false);let mut expected=None;
        let target=s.nodes.iter().position(|n|n.kind==KIND_POT_SHARE&&n.live.count_ones()==3).unwrap();
        let live=s.nodes[target].live;let p=(0..np).find(|q|live&(1<<q)!=0).unwrap();
        let other=(0..np).find(|q|*q!=p&&live&(1<<q)!=0).unwrap();let folded=(0..np).find(|q|live&(1<<q)==0).unwrap();
        for packed in [false,true]{
            let mut g=engine(&s,batch,packed);let sources=g.stream.clone_dtoh(&g.d_reach_src).unwrap();
            let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();let terms=g.stream.clone_dtoh(&g.d_terms).unwrap();
            let mut rounds=Vec::new();
            for zero in [None,Some(p),Some(other),Some(folded),None]{
                g.down(1,-1).unwrap();
                if let Some(q)=zero{
                    let mut reach=g.stream.clone_dtoh(&g.d_reach).unwrap();let at=sources[target*np+q] as usize*NUM_CLASSES;
                    reach[at..at+NUM_CLASSES].fill(0.);g.stream.memcpy_htod(&reach,&mut g.d_reach).unwrap();let count=g.d_reach_mass.len() as u32;
                    unsafe{g.stream.launch_builder(&g.f_reach_mass).arg(&g.d_reach).arg(&mut g.d_reach_mass)
                        .launch(LaunchConfig{block_dim:(128,1,1),..PreflopGpu::cfg(count)}).unwrap();}
                }
                for gate in [0,1]{for seat in 0..np{
                    g.ordinary_terminals(seat as i32).unwrap();g.multiway_terminals(seat as i32,gate).unwrap();
                    let values=g.stream.clone_dtoh(&g.d_val).unwrap();let snapshot:Vec<u32>=terms.iter().flat_map(|&t|{
                        let at=slots[t as usize] as usize*NUM_CLASSES;values[at..at+NUM_CLASSES].iter().map(|v|v.to_bits())}).collect();
                    rounds.push(snapshot);
                }}
            }
            if let Some(ref expected)=expected{assert!(&rounds==expected,"np={np} batch={batch}");}else{expected=Some(rounds);}
        }
    }}
    std::fs::write(output().join("zero-recovery.json"),"{\"exact\":true,\"fixtures\":4,\"zero_states\":5,\"gates\":2}").unwrap();
}

#[test]
fn save_reload_and_actual_stop(){
    let folder=output();let mut expected=None;
    for packed in [false,true]{
        let mut s=fixture(4,true);let mut g=engine(&s,4,packed);
        for _ in 0..3{g.iterate(&mut s).unwrap();g.gaps_and_evs().unwrap();}
        g.sync_to_cpu(&mut s).unwrap();let file=folder.join(format!("saved-{packed}.gtop"));assert!(!file.exists());s.save_game(file.to_str().unwrap()).unwrap();drop(g);
        let mut s=PreflopSolver::load_game(file.to_str().unwrap(),eq()).unwrap();let mut g=engine(&s,4,packed);let mut rounds=Vec::new();
        for _ in 0..3{g.iterate(&mut s).unwrap();let m=g.gaps_and_evs().unwrap();rounds.push((bits(&g),m));}
        if let Some(ref expected)=expected{assert!(&rounds==expected);}else{expected=Some(rounds);}
    }
    assert_eq!(std::fs::read(folder.join("saved-false.gtop")).unwrap(),std::fs::read(folder.join("saved-true.gtop")).unwrap());
    let saved=folder.join("saved-true.gtop");let mut s=PreflopSolver::load_game(saved.to_str().unwrap(),eq()).unwrap();let mut g=engine(&s,4,true);
    let age=s.iteration;let before=bits(&g);let stop=Arc::new(AtomicBool::new(false));let request=stop.clone();
    let signal=std::thread::spawn(move||{std::thread::sleep(std::time::Duration::from_millis(5));request.store(true,Ordering::Relaxed);});
    let done=g.try_iterate(&mut s,Some(&stop)).unwrap();signal.join().unwrap();assert!(!done);assert_eq!(age,s.iteration);
    let interrupted=bits(&g);assert!(interrupted.0!=before.0||interrupted.1!=before.1);
    g.sync_to_cpu(&mut s).unwrap();let file=folder.join("interrupted.gtop");assert!(!file.exists());s.save_game(file.to_str().unwrap()).unwrap();drop(g);
    let original=PreflopSolver::load_game(saved.to_str().unwrap(),eq()).unwrap();let mut replay=engine(&original,4,false);let mut matched=None;
    for p in 0..replay.np{if replay.static_seats[p as usize]{continue;}replay.sweep(p,0).unwrap();replay.stream.synchronize().unwrap();let b=bits(&replay);
        if b.0==interrupted.0&&b.1==interrupted.1{matched=Some(p);break;}}
    assert!(matched.is_some());drop(replay);
    let mut expected=None;
    for packed in [false,true]{let mut s=PreflopSolver::load_game(file.to_str().unwrap(),eq()).unwrap();let mut g=engine(&s,4,packed);let mut rounds=Vec::new();
        for _ in 0..3{g.iterate(&mut s).unwrap();let m=g.gaps_and_evs().unwrap();rounds.push((bits(&g),m));}
        if let Some(ref expected)=expected{assert!(&rounds==expected);}else{expected=Some(rounds);}
    }
    std::fs::write(folder.join("continuation.json"),serde_json::to_vec_pretty(&json!({"saved_exact":true,"reload_rounds":3,"actual_stop":true,"matched_player":matched,"replay_exact":true})).unwrap()).unwrap();
}

#[test]
fn allocation_failures_drop_private_engine(){
    let ctx=CudaContext::new(0).unwrap();
    let used=||{ctx.synchronize().unwrap();ctx.bind_to_thread().unwrap();let mut bytes=0u64;
        unsafe{let pool=cudarc::driver::result::device::get_mem_pool(ctx.cu_device()).unwrap();
            cudarc::driver::result::mem_pool::get_attribute(pool,sys::CUmemPool_attribute::CU_MEMPOOL_ATTR_USED_MEM_CURRENT,(&mut bytes as *mut u64).cast()).unwrap();}bytes};
    let s=fixture(4,false);let initial=s.arena_snapshot();
    for stage in [1,2,3]{let before=used();let g=engine(&s,4,false);FAIL_STAGE.set(stage);let error=promote(g,&s,2000).err().unwrap();
        assert!(error.contains(&format!("allocation stage {stage}")));assert_eq!(FAIL_STAGE.get(),0);assert_eq!(used(),before);assert_eq!(initial,s.arena_snapshot());}
    let before=used();let g=engine(&s,4,false);assert!(promote(g,&s,1).err().unwrap().contains("reserved budget"));assert_eq!(used(),before);
    let mut a=fixture(4,false);let mut b=fixture(4,false);let mut reference=engine(&a,4,false);let mut recovered=engine(&b,4,true);
    for _ in 0..3{reference.iterate(&mut a).unwrap();recovered.iterate(&mut b).unwrap();assert_eq!(reference.gaps_and_evs().unwrap(),recovered.gaps_and_evs().unwrap());assert_eq!(bits(&reference),bits(&recovered));}
    std::fs::write(output().join("allocation.json"),"{\"actual_oom_stages\":[1,2,3],\"leaked_bytes\":0,\"recovery_rounds\":3}").unwrap();
}

#[test]
#[ignore="guarded native saved-game C24 timing only"]
fn frozen_native_benchmark(){
    use std::time::Instant;
    let input=std::env::var("PREFLOP_GPU_REUSE_INPUT").unwrap();
    let output=std::env::var("PREFLOP_GPU_REUSE_OUTPUT").unwrap();assert!(!std::path::Path::new(&output).exists());
    let packed=std::env::var("PREFLOP_GPU_ORDINARY_STATIC_ENABLE").unwrap()=="1";
    let budget=std::env::var("PREFLOP_GPU_ORDINARY_BUDGET").unwrap().parse::<u64>().unwrap();
    let expected_batch=std::env::var("PREFLOP_GPU_ORDINARY_BATCH").unwrap().parse::<u32>().unwrap();
    let repeats=std::env::var("PREFLOP_GPU_ORDINARY_ROUNDS").unwrap().parse::<usize>().unwrap();assert!(repeats==3||repeats==6);
    let started=Instant::now();let mut s=PreflopSolver::load_game(&input,eq()).unwrap();let initial_age=s.iteration;
    let t=Instant::now();let g=PreflopGpu::new(&s,budget).unwrap();
    assert_eq!(g.mw_batch,expected_batch);assert!(g.exact_reuse_compatible());assert_eq!(g.use_eq_cache,1);
    let initial_buffers=super::super::super::cross_player_inventory::device_buffer_bytes(&g);
    let rollout=std::env::var("PREFLOP_GPU_ORDINARY_ROLLOUT").ok().as_deref()==Some("1");
    let mut selection=None;
    let mut g=if rollout {
        assert!(packed);drop(g);let (engine,report)=PreflopGpu::new_throughput(&s,budget).unwrap();
        assert_eq!(report.mode,"normal_gpu");assert!(report.static_cdf);assert!(!report.narrow_offsets);
        assert!(report.static_cdf_fallback_reason.is_none());selection=Some(report);engine
    }else if packed{promote(g,&s,budget).unwrap()}else{g};let init=t.elapsed().as_secs_f64();
    assert_eq!(g.mw_batch,expected_batch);
    let final_buffers=super::super::super::cross_player_inventory::device_buffer_bytes(&g);
    let final_bytes=final_buffers.values().sum::<usize>()+g.static_cdf.as_ref().map_or(0,|k|k.bytes());
    println!("C24_NATIVE_LAYOUT {}",json!({"packed":packed,"batch":g.mw_batch,"nodes":s.nodes.len(),"init_seconds":init,"device_bytes":final_bytes}));
    let mut rows=Vec::new();
    for i in 0..repeats{
        let t=Instant::now();g.iterate(&mut s).unwrap();let iteration_seconds=t.elapsed().as_secs_f64();
        let t=Instant::now();let(gaps,evs)=g.gaps_and_evs().unwrap();let check_seconds=t.elapsed().as_secs_f64();
        assert!(gaps.iter().chain(&evs).all(|x|x.is_finite()));
        let row=json!({"index":i,"warmup":i<2,"iteration":s.iteration,"iteration_seconds":iteration_seconds,"check_seconds":check_seconds,"gaps":gaps,"evs":evs});
        println!("C24_NATIVE_ROW {}",row);rows.push(row);
    }
    let t=Instant::now();g.sync_to_cpu(&mut s).unwrap();let sync=t.elapsed().as_secs_f64();
    let(regret,strategy)=s.arena_snapshot();let fingerprint=regret.iter().chain(&strategy).fold(0xcbf29ce484222325u64,|h,x|
        x.to_bits().to_le_bytes().iter().fold(h,|h,b|(h^*b as u64).wrapping_mul(0x100000001b3)));
    let result=json!({"input":input,"selection":selection,"packed":packed,"budget_mb":budget,"batch":g.mw_batch,"hu_cache":g.use_eq_cache,
        "samples":g.research_samples,"nodes":s.nodes.len(),"initial_iteration":initial_age,"iteration":s.iteration,"rows":rows,
        "init_seconds":init,"sync_seconds":sync,"complete_seconds":started.elapsed().as_secs_f64(),
        "arena_entries":regret.len()+strategy.len(),"arena_fingerprint":format!("{fingerprint:016x}"),
        "initial_buffers":initial_buffers,"final_buffers":final_buffers,"final_device_bytes":final_bytes,
        "static_cdf":g.static_cdf.as_ref().map(|k|k.report()),"scope":"Native saved-game fixed-work throughput; not convergence or retention qualification"});
    std::fs::write(output,serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
