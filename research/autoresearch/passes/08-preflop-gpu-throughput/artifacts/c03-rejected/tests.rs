use super::*;
use crate::preflop::{PreflopConfig,equity::EquityTable};
use serde_json::json;
use std::time::Instant;

fn eq()->Arc<EquityTable> {
    let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
    let b=std::fs::read(path).unwrap();
    Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(b[..4].try_into().unwrap())))
}
fn fixture(fixed:bool)->PreflopSolver {
    let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],
        "stack":10,"posts":[0,0,0.5,1],"limp":true,"open_raises":[2],"raise_mults":[3],
        "max_raises":2,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"calibrated"})).unwrap();
    let mut s=PreflopSolver::new(cfg,eq()).unwrap();
    s.research_seed_quality_fixture_averages().unwrap();
    if fixed {s.seat_frozen[2]=true;let node=s.child(0,1);
        let mut lock=vec![0.;s.nodes[node].actions.len()*NUM_CLASSES];lock[..NUM_CLASSES].fill(1.);
        s.point_locks.insert(node as u32,lock);}
    s
}
fn arenas(g:&PreflopGpu)->(Vec<u32>,Vec<u32>) {
    (g.stream.clone_dtoh(&g.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect(),
     g.stream.clone_dtoh(&g.d_strat).unwrap().iter().map(|x|x.to_bits()).collect())
}

#[test]
fn exact_reuse_gpu_classifier_collision_and_overflow_are_safe() {
    let s=fixture(false);let mut g=PreflopGpu::new(&s,2000).unwrap();g.enable_research_exact_cdf_reuse().unwrap();
    let count=37usize;
    let work=g.stream.clone_htod(&(0..count as u32).collect::<Vec<_>>()).unwrap();
    let masses=g.stream.clone_htod(&vec![1f32;count]).unwrap();
    let active=g.stream.clone_htod(&vec![1u32;count]).unwrap();
    for identical in [true,false] {
        let data:Vec<f32>=(0..count*NUM_CLASSES).map(|i|if identical{(i%NUM_CLASSES) as f32}
            else{f32::from_bits(0x3f000000+(i/NUM_CLASSES) as u32)}).collect();
        let normalized=g.stream.clone_htod(&data).unwrap();
        let mut table=g.stream.alloc_zeros::<u32>(1).unwrap();
        let mut aliases=g.stream.alloc_zeros::<u32>(count).unwrap();
        let r=g.research_exact_reuse.as_ref().unwrap();
        unsafe {g.stream.launch_builder(&r.classify).arg(&work).arg(&0u32).arg(&work).arg(&masses)
            .arg(&active).arg(&1i32).arg(&normalized).arg(&mut table).arg(&0u32).arg(&mut aliases)
            .launch(LaunchConfig{grid_dim:(count as u32,1,1),block_dim:(32,1,1),shared_mem_bytes:0}).unwrap();}
        let alias=g.stream.clone_dtoh(&aliases).unwrap();
        for (k,&a) in alias.iter().enumerate() {
            assert!((a as usize)<count);assert_eq!(alias[a as usize],a);
            assert_eq!(&data[k*NUM_CLASSES..(k+1)*NUM_CLASSES],&data[a as usize*NUM_CLASSES..(a as usize+1)*NUM_CLASSES]);
        }
        if identical {assert!(alias.iter().all(|a|*a==alias[0]));}
        else {assert!(alias.iter().enumerate().all(|(k,a)|*a==k as u32));}
    }
}

#[test]
fn exact_reuse_preserves_native_arenas_checks_capture_and_zero_recovery() {
    for fixed in [false,true] {
        for batch in [5,32] {
            let mut runs=Vec::new();
            for variant in [0,1,2] {
                let enabled=variant>0;
                let mut s=fixture(fixed);let mut g=PreflopGpu::new(&s,2000).unwrap();g.mw_batch=batch;
                if variant==2 {g.enable_research_no_tie_products().unwrap();} else if enabled {g.enable_research_exact_cdf_reuse().unwrap();}
                let mut rounds=Vec::new();
                for _ in 0..5 {
                    g.iterate(&mut s).unwrap();let (gaps,evs)=g.gaps_and_evs().unwrap();
                    rounds.push((arenas(&g),gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
                }
                assert!(g.learning_graphs.iter().any(|x|x.is_some()) && g.eval_graph.is_some());
                let before=arenas(&g);let age=s.iteration;
                assert!(!g.try_iterate(&mut s,Some(&AtomicBool::new(true))).unwrap());
                assert_eq!(before,arenas(&g));assert_eq!(age,s.iteration);
                // Change every player's root and descendant reach explicitly.
                // Test zero own, zero live/folded opponent, and ungated recovery.
                let mut terminals=Vec::new();
                let sources=g.stream.clone_dtoh(&g.d_reach_src).unwrap();
                let target=s.nodes.iter().position(|n|n.kind==KIND_POT_SHARE && n.live.count_ones()==3).unwrap();
                let lv=s.nodes[target].live;
                let p=(0..s.n).find(|q|lv&(1<<q)!=0).unwrap();
                let other=(0..s.n).find(|q|*q!=p && lv&(1<<q)!=0).unwrap();
                let folded=(0..s.n).find(|q|lv&(1<<q)==0).unwrap();
                for zero in [None,Some(p),Some(other),Some(folded),None] {
                    g.down(1,p as i32).unwrap();
                    if let Some(q)=zero {
                        let mut reach=g.stream.clone_dtoh(&g.d_reach).unwrap();
                        let at=sources[target*s.n+q] as usize*NUM_CLASSES;reach[at..at+NUM_CLASSES].fill(0.);
                        g.stream.memcpy_htod(&reach,&mut g.d_reach).unwrap();
                        let blocks=g.d_reach_mass.len() as u32;
                        unsafe {g.stream.launch_builder(&g.f_reach_mass).arg(&g.d_reach).arg(&mut g.d_reach_mass)
                            .launch(LaunchConfig{block_dim:(128,1,1),..PreflopGpu::cfg(blocks)}).unwrap();}
                    }
                    g.terminals_masked(p as i32,if terminals.len()==4{0}else{1}).unwrap();
                    let values=g.stream.clone_dtoh(&g.d_val).unwrap();
                    let at=g.stream.clone_dtoh(&g.d_val_slot).unwrap()[target] as usize*NUM_CLASSES;
                    terminals.push(values[at..at+NUM_CLASSES].iter().map(|x|x.to_bits()).collect::<Vec<_>>());
                }
                assert_eq!(terminals[0],terminals[1]);assert_eq!(terminals[0],terminals[4]);
                assert!(terminals[2].iter().chain(&terminals[3]).all(|x|*x==0));
                runs.push((rounds,terminals));
            }
            assert_eq!(runs[0],runs[1],"reuse changed native bits, fixed={fixed}, batch={batch}");
            assert_eq!(runs[1],runs[2],"no tie shortcut changed bits, fixed={fixed}, batch={batch}");
        }
    }
}

#[test]
#[ignore = "frozen GPU throughput benchmark; requires idle GPU and immutable input"]
fn exact_reuse_frozen_benchmark() {
    let input=std::env::var("PREFLOP_GPU_REUSE_INPUT").unwrap();
    let output=std::env::var("PREFLOP_GPU_REUSE_OUTPUT").unwrap();
    let enabled=std::env::var("PREFLOP_GPU_REUSE_ENABLE").unwrap()=="1";
    let no_tie=std::env::var("PREFLOP_GPU_NO_TIE").map_or(false,|v|v=="1");
    assert!(!std::path::Path::new(&output).exists());
    let started=Instant::now();
    let mut s=PreflopSolver::load_game(&input,eq()).unwrap();let initial_age=s.iteration;
    let t=Instant::now();let mut g=PreflopGpu::new(&s,23000).unwrap();
    if no_tie{g.enable_research_no_tie_products().unwrap();} else if enabled{g.enable_research_exact_cdf_reuse().unwrap();}
    let init=t.elapsed().as_secs_f64();let mut rows=Vec::new();
    for i in 0..6 {
        let t=Instant::now();g.iterate(&mut s).unwrap();let iteration_seconds=t.elapsed().as_secs_f64();
        let t=Instant::now();let (gaps,evs)=g.gaps_and_evs().unwrap();let check_seconds=t.elapsed().as_secs_f64();
        let row=json!({"index":i,"warmup":i<2,"iteration":s.iteration,"iteration_seconds":iteration_seconds,
            "check_seconds":check_seconds,"gaps":gaps,"evs":evs});
        println!("EXACT_REUSE_BENCH {}",row);rows.push(row);
    }
    let t=Instant::now();g.sync_to_cpu(&mut s).unwrap();let sync=t.elapsed().as_secs_f64();
    let (regret,strategy)=s.arena_snapshot();
    let fingerprint=regret.iter().chain(&strategy).fold(0xcbf29ce484222325u64,|h,x|
        x.to_bits().to_le_bytes().iter().fold(h,|h,b|(h^*b as u64).wrapping_mul(0x100000001b3)));
    let extra=g.research_exact_reuse.as_ref().map_or(0,|r|(r.table.len()+r.aliases.len())*4);
    let result=json!({"input":input,"enabled":enabled,"no_tie":no_tie,"nodes":s.nodes.len(),"initial_iteration":initial_age,
        "iteration":s.iteration,"batch":g.mw_batch,"cdf_bytes":g.d_mw_cdf.len()*4,"extra_bytes":extra,
        "init_seconds":init,"sync_seconds":sync,"complete_seconds":started.elapsed().as_secs_f64(),
        "arena_fingerprint":format!("{fingerprint:016x}"),"arena_entries":regret.len()+strategy.len(),"rows":rows,
        "scope":"Fixed-work native GPU throughput, not time to conditional qualification"});
    std::fs::write(output,serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}

#[test]
fn exact_reuse_all_opponent_counts_match_terminal_bits() {
    let cfg:PreflopConfig=serde_json::from_value(json!({
        "positions":["UTG","UTG1","UTG2","MP","HJ","CO","BTN","SB","BB"],
        "stack":10,"posts":[0,0,0,0,0,0,0,0.5,1],"limp":true,"open_raises":[],
        "raise_mults":[],"max_raises":0,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"})).unwrap();
    let s=PreflopSolver::new(cfg,eq()).unwrap();
    let mut results=Vec::new();let mut seen=std::collections::HashSet::new();
    for variant in [0,1,2] {
                let enabled=variant>0;
        let mut g=PreflopGpu::new(&s,2000).unwrap();
        if variant==2 {g.enable_research_no_tie_products().unwrap();} else if enabled {g.enable_research_exact_cdf_reuse().unwrap();}
        g.down(0,0).unwrap();
        let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();let mut snapshots=Vec::new();
        for p in 0..s.n {
            g.terminals(p as i32).unwrap();let values=g.stream.clone_dtoh(&g.d_val).unwrap();
            let mut terminal_bits=Vec::new();
            for (i,n) in s.nodes.iter().enumerate() {
                if n.kind!=KIND_POT_SHARE || n.live.count_ones()<3 || (n.live>>p)&1==0 {continue;}
                seen.insert(n.live.count_ones()-1);
                let start=slots[i] as usize*NUM_CLASSES;
                terminal_bits.extend(values[start..start+NUM_CLASSES].iter().map(|x|x.to_bits()));
            }
            snapshots.push(terminal_bits);
        }
        results.push(snapshots);
    }
    assert_eq!(seen,(2..=8).collect());assert_eq!(results[0],results[1]);assert_eq!(results[1],results[2]);
}
