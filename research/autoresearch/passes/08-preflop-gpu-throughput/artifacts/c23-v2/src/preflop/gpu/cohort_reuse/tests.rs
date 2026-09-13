use super::*;
use crate::preflop::{PreflopConfig,equity::EquityTable};
use cudarc::driver::DevicePtr;

#[test]
fn cohort_phase_tracing_preserves_solver_bits() {
    fn counts(v:&serde_json::Value,np:usize,batches:usize,groups:usize,average:bool,restore:bool) {
        let rows=v["rows"].as_array().unwrap();
        let count=|phase:&str|rows.iter().filter(|r|r["phase"]==phase).map(|r|r["intervals"].as_u64().unwrap() as usize).sum::<usize>();
        for phase in ["prepare","ordinary_terminals"] {assert_eq!(count(phase),np,"{phase}");}
        for phase in ["normalize","classify"] {assert_eq!(count(phase),if average{groups}else{np},"{phase}");}
        assert_eq!(count("cdf"),(if average{groups}else{np})*batches);
        assert_eq!(count("coupled_terminals"),np*batches);
        assert_eq!(count("down"),if average{1}else{np});
        assert_eq!(count("up_learn"),if average{0}else{np});
        for phase in ["up_average","up_br"] {assert_eq!(count(phase),if average{np}else{0},"{phase}");}
        assert_eq!(count("root_copy"),if average{2*np}else{0});
        assert_eq!(count("scratch_restore"),usize::from(average&&restore));
        let total=v["gpu_ms"].as_f64().unwrap();let sum=v["interval_sum_ms"].as_f64().unwrap();
        assert!(total.is_finite()&&total>=0.&&(total-sum).abs()<1.+total*0.001);
    }
    for np in [4,7,9] {for fixed in [false,true] {for batch in [5u32,32] {
        let mut results=Vec::new();
        for profile in [false,true] {
            let mut s=fixture(np,fixed);let mut g=PreflopGpu::new_research_cohorts(&s,2000).unwrap();g.mw_batch=batch;
            let c=g.research_cohorts.as_ref().unwrap();
            let groups=c.plan.spans.iter().filter(|(_,count)|*count>0).count();
            let restore=c.plan.groups.iter().find(|ps|ps.contains(&(np as i32-1))).unwrap().len()>1;
            let batches=crate::preflop::multiway::SAMPLES.div_ceil(batch as usize);let mut rounds=Vec::new();
            for _ in 0..3 {
                if profile {g.phase_profile_begin().unwrap();}
                g.iterate(&mut s).unwrap();
                if profile {counts(&g.phase_profile_end().unwrap(),np-usize::from(fixed),batches,groups,false,false);}
                if profile {g.phase_profile_begin().unwrap();}
                let (gaps,evs)=g.gaps_and_evs().unwrap();
                if profile {counts(&g.phase_profile_end().unwrap(),np,batches,groups,true,restore);}
                rounds.push((bits(&g),gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            if !profile {assert!(g.eval_graph.is_some()&&g.learning_graphs.iter().any(|x|x.is_some()));}
            results.push(rounds);
        }
        assert_eq!(results[0],results[1],"tracing altered C07 np={np} fixed={fixed} batch={batch}");
    }}}
}

#[test]
fn cohort_rejects_no_multiway_and_restores_after_errors() {
    let heads_up=fixture(2,false);
    assert!(PreflopGpu::new_research_cohorts(&heads_up,2000).is_err());
    assert!(PreflopGpu::new_research_narrow_cohorts(&heads_up,2000).is_err());
    let s=fixture(4,false);
    let mut g=PreflopGpu::new_research_cohorts(&s,2000).unwrap();
    let val=g.d_val.device_ptr(&g.stream).0;
    let prob=g.d_mw_prob.device_ptr(&g.stream).0;
    let mut c=g.research_cohorts.take().unwrap();
    let other_val=c.values[0].device_ptr(&g.stream).0;
    let other_prob=c.prob[0].device_ptr(&g.stream).0;
    let before=bits(&g);
    let error=g.with_cohort_buffer(&mut c.values,&mut c.prob,1,|swapped| {
        assert_eq!(swapped.d_val.device_ptr(&swapped.stream).0,other_val);
        assert_eq!(swapped.d_mw_prob.device_ptr(&swapped.stream).0,other_prob);
        Err("injected buffer error".to_string())
    });
    assert_eq!(error,Err("injected buffer error".to_string()));
    assert_eq!(g.d_val.device_ptr(&g.stream).0,val);
    assert_eq!(g.d_mw_prob.device_ptr(&g.stream).0,prob);
    assert_eq!(c.values[0].device_ptr(&g.stream).0,other_val);
    assert_eq!(c.prob[0].device_ptr(&g.stream).0,other_prob);
    g.research_cohorts=Some(c);
    let samples=g.research_samples;g.research_samples=1;
    assert!(g.queue_cohort_evaluation().unwrap_err().contains("unchanged native"));
    assert!(g.research_cohorts.is_some());
    assert_eq!(g.d_val.device_ptr(&g.stream).0,val);
    assert_eq!(g.d_mw_prob.device_ptr(&g.stream).0,prob);
    assert_eq!(bits(&g),before);
    g.research_samples=samples;
    g.gaps_and_evs().unwrap();
    assert_eq!(g.d_val.device_ptr(&g.stream).0,val);
    assert_eq!(g.d_mw_prob.device_ptr(&g.stream).0,prob);
}

fn eq()->Arc<EquityTable> {
    let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
    let b=std::fs::read(path).unwrap();
    Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(b[..4].try_into().unwrap())))
}
fn fixture(np:usize,fixed:bool)->PreflopSolver {
    let mut posts=vec![0.;np];posts[np-2]=0.5;posts[np-1]=1.;
    let cfg:PreflopConfig=serde_json::from_value(json!({"positions":(0..np).map(|p|format!("P{p}")).collect::<Vec<_>>(),
        "stack":10,"posts":posts,"limp":true,"open_raises":if np<=5{vec![2]}else{vec![]},"raise_mults":[],
        "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"})).unwrap();
    let mut s=PreflopSolver::new(cfg,eq()).unwrap();s.research_seed_quality_fixture_averages().unwrap();
    if fixed {s.seat_frozen[np-2]=true;let node=s.child(0,1);let mut lock=vec![0.;s.nodes[node].actions.len()*NUM_CLASSES];
        lock[..NUM_CLASSES].fill(1.);s.point_locks.insert(node as u32,lock);}
    s
}
fn bits(g:&PreflopGpu)->(Vec<u32>,Vec<u32>,Vec<u32>,Vec<u32>) {
    (g.stream.clone_dtoh(&g.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect(),
        g.stream.clone_dtoh(&g.d_strat).unwrap().iter().map(|x|x.to_bits()).collect(),
        g.stream.clone_dtoh(&g.d_eval_roots).unwrap().iter().map(|x|x.to_bits()).collect(),
        g.stream.clone_dtoh(&g.d_val.slice(0..NUM_CLASSES)).unwrap().iter().map(|x|x.to_bits()).collect())
}

fn check_last_cohort_prefixes(g:&PreflopGpu) {
    let c=g.research_cohorts.as_ref().unwrap();
    let group=c.plan.groups.iter().position(|p|p.contains(&(g.np-1))).unwrap();
    let (start,count)=c.plan.spans[group];if count==0{return;}
    let mut expected=g.stream.alloc_zeros::<f32>(c.plan.capacity*g.mw_batch as usize*170).unwrap();
    let samples=crate::preflop::multiway::SAMPLES as u32;
    let sample_start=(samples-1)/g.mw_batch*g.mw_batch;let sample_count=samples-sample_start;
    unsafe {g.stream.launch_builder(&g.f_multiway_cdf).arg(&c.work).arg(&start).arg(&g.d_mw_blocks).arg(&g.d_mw_order)
        .arg(&g.d_mw_normalized).arg(&g.d_reach_mass).arg(&g.d_mw_active).arg(&0i32).arg(&1i32)
        .arg(&mut expected).arg(&sample_start).arg(&sample_count).arg(&g.mw_batch)
        .launch(LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();}
    let reference=g.stream.clone_dtoh(&expected).unwrap();let actual=g.stream.clone_dtoh(&g.d_mw_cdf).unwrap();
    let r=g.research_exact_reuse.as_ref().unwrap();let aliases=g.stream.clone_dtoh(&r.aliases).unwrap();
    let blocks=g.stream.clone_dtoh(&g.d_mw_blocks).unwrap();let mass=g.stream.clone_dtoh(&g.d_reach_mass).unwrap();
    let compact=g.static_cdf.as_ref().map(|k|(g.stream.clone_dtoh(&k.prefix).unwrap(),g.stream.clone_dtoh(&k.offsets).unwrap(),k.stride as usize));
    for k in 0..count as usize {
        if mass[blocks[c.plan.work[start as usize+k] as usize] as usize]<=0. {continue;}
        let representative=aliases[k] as usize;assert!(representative<count as usize);
        for sample in 0..sample_count as usize {
            let a=(representative*g.mw_batch as usize+sample)*170;let b=(k*g.mw_batch as usize+sample)*170;
            if let Some((prefix,offsets,stride))=&compact{
                let at=sample_start as usize+sample;let base=representative*stride+(offsets[at]-offsets[sample_start as usize]) as usize;
                for i in 0..170{let packed=prefix[at*170+i];if packed!=u32::MAX{assert_eq!(actual[base+packed as usize].to_bits(),reference[b+i].to_bits());}}
            }else{assert!(actual[a..a+170].iter().zip(&reference[b..b+170]).all(|(a,b)|a.to_bits()==b.to_bits()));}
        }
    }
}
#[test]
fn cohort_all_terminal_bits_zero_recovery_and_prefixes() {
    for np in [4,9] {for batch in [5,32] {
        let s=fixture(np,false);let mut runs=Vec::new();let mut counts=std::collections::HashSet::new();
        for mode in 0..7 {
            let mut g=if mode==6{super::super::static_cdf::new(&s,2000).unwrap()}else if mode==5{PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap()}else if mode>=3{PreflopGpu::new_research_unrolled_cohorts(&s,2000).unwrap()}else if mode==2{PreflopGpu::new_research_cohorts(&s,2000).unwrap()}else{PreflopGpu::new(&s,2000).unwrap()};
            if mode==4 {g.enable_research_narrow_offsets().unwrap();}
            if mode==1 {g.enable_research_exact_cdf_reuse().unwrap();}g.mw_batch=batch;
            let target=s.nodes.iter().position(|n|n.kind==KIND_POT_SHARE&&n.live.count_ones()==3).unwrap();
            let live=s.nodes[target].live;let p=(0..np).find(|q|live&(1<<q)!=0).unwrap();
            let other=(0..np).find(|q|*q!=p&&live&(1<<q)!=0).unwrap();
            let folded=(0..np).find(|q|live&(1<<q)==0).unwrap();
            let sources=g.stream.clone_dtoh(&g.d_reach_src).unwrap();let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();
            let terms=g.stream.clone_dtoh(&g.d_terms).unwrap();let mut rounds=Vec::new();
            for zero in [None,Some(p),Some(other),Some(folded),None] {
                g.down(1,-1).unwrap();
                if let Some(q)=zero {
                    let mut reach=g.stream.clone_dtoh(&g.d_reach).unwrap();let at=sources[target*np+q] as usize*NUM_CLASSES;
                    reach[at..at+NUM_CLASSES].fill(0.);g.stream.memcpy_htod(&reach,&mut g.d_reach).unwrap();
                    let blocks=g.d_reach_mass.len() as u32;
                    unsafe {g.stream.launch_builder(&g.f_reach_mass).arg(&g.d_reach).arg(&mut g.d_reach_mass)
                        .launch(LaunchConfig{block_dim:(128,1,1),..PreflopGpu::cfg(blocks)}).unwrap();}
                }
                let mut snapshots=Vec::new();
                if mode>=2 {
                    let c=g.research_cohorts.as_mut().unwrap();c.audit_terminals=true;c.terminal_audits.clear();
                    g.queue_cohort_evaluation().unwrap();snapshots=std::mem::take(&mut g.research_cohorts.as_mut().unwrap().terminal_audits);
                    check_last_cohort_prefixes(&g);
                } else {
                    for p in 0..np {g.terminals_masked(p as i32,0).unwrap();let values=g.stream.clone_dtoh(&g.d_val).unwrap();
                        snapshots.push((p as i32,terms.iter().flat_map(|nd| {let at=slots[*nd as usize] as usize*NUM_CLASSES;
                            values[at..at+NUM_CLASSES].iter().map(|v|v.to_bits())}).collect()));}
                }
                snapshots.sort_by_key(|x|x.0);rounds.push(snapshots);
            }
            assert_eq!(rounds[0],rounds[4]);runs.push(rounds);
        }
        for nd in &s.nodes {if nd.kind==KIND_POT_SHARE&&nd.live.count_ones()>=3{counts.insert(nd.live.count_ones()-1);}}
        if np==9 {assert_eq!(counts,(2..=8).collect());}
        assert_eq!(runs[0],runs[1],"C01 all terminals");assert_eq!(runs[1],runs[2],"C07 terminals np={np} batch={batch}");
        assert_eq!(runs[2],runs[3],"C09 terminals np={np} batch={batch}");
        assert_eq!(runs[3],runs[4],"C13 terminals np={np} batch={batch}");
        assert_eq!(runs[3],runs[5],"C14 terminals np={np} batch={batch}");
        assert_eq!(runs[5],runs[6],"C23 terminals np={np} batch={batch}");
    }}
}

#[test]
#[ignore="C07 frozen-save allocation validation; guarded idle GPU only"]
fn cohort_constructor_from_saved_state() {
    let input=std::env::var("PREFLOP_GPU_REUSE_INPUT").unwrap();let output=std::env::var("PREFLOP_GPU_REUSE_OUTPUT").unwrap();
    assert!(!std::path::Path::new(&output).exists());let s=PreflopSolver::load_game(&input,eq()).unwrap();
    let unrolled=std::env::var("PREFLOP_GPU_TERMINAL_UNROLL").ok().as_deref()==Some("1");
    let narrow=std::env::var("PREFLOP_GPU_NARROW_OFFSETS").ok().as_deref()==Some("1");
    let compact=std::env::var("PREFLOP_GPU_STATIC_CDF").ok().as_deref()==Some("1");
    let g=if compact{super::super::static_cdf::new(&s,23000).unwrap()}else if narrow{PreflopGpu::new_research_narrow_cohorts(&s,23000).unwrap()}else if unrolled{PreflopGpu::new_research_unrolled_cohorts(&s,23000).unwrap()}else{PreflopGpu::new_research_cohorts(&s,23000).unwrap()};
    let c=g.research_cohorts.as_ref().unwrap();
    let mut buffers=super::super::cross_player_inventory::device_buffer_bytes(&g);
    let compact_report=g.static_cdf.as_ref().map(|k|k.report());
    let reduction=g.static_cdf.as_ref().map_or(0,|k|k.original_bytes-g.d_mw_cdf.len()*4-k.bytes());
    if let Some(k)=g.static_cdf.as_ref(){buffers.insert("static_prefix",k.prefix.len()*4);buffers.insert("static_hand",k.hand.len()*4);buffers.insert("static_offsets",k.offsets.len()*4);}
    let actual=buffers.values().sum::<usize>()+c.plan.extra_bytes;
    assert_eq!(actual,c.plan.total_bytes-reduction);assert!(actual+256*1024*1024<=20_500_000_000);
    let snap=s.arena_snapshot();let gpu=bits(&g);
    assert_eq!(gpu.0,snap.0.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
    assert_eq!(gpu.1,snap.1.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
    let result=json!({"input":input,"nodes":s.nodes.len(),"players":s.n,"iteration":s.iteration,"plan":c.plan.report(),
        "buffer_bytes":buffers,"actual_device_bytes":actual,"batch":g.mw_batch,"hu_cache":g.use_eq_cache,"unrolled":unrolled,
        "arenas_unchanged":true,"narrow_offsets":narrow,"static_cdf":compact_report,"scope":"Allocation validation only; no speed measurement"});
    std::fs::write(output,serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
#[test]
fn cohort_planner_mapping_budget_and_odd_groups() {
    for n in 3..=9 {
        let mut p=EquityCachePlan{blocks:vec![0,1,2,3,4],slots:vec![0,1,2,3,4],work:Vec::new(),spans:Vec::new()};
        for seat in 0..n {let start=p.work.len() as u32;for slot in 0..5 {if slot!=seat%5{p.work.push(slot as u32);}}
            p.spans.push((start,p.work.len() as u32-start));}
        let plan=Plan::build(n,&p,4,1000000,1000,100,1000).unwrap();
        let mut seen=vec![false;n];
        for (i,group) in plan.groups.iter().enumerate() {
            assert!((1..=3).contains(&group.len()));
            let (start,count)=plan.spans[i];let actual=&plan.work[start as usize..(start+count) as usize];
            let mut expected=std::collections::BTreeSet::new();
            for &seat in group {assert!(!seen[seat as usize]);seen[seat as usize]=true;
                let (start,count)=p.spans[seat as usize];expected.extend(p.work[start as usize..(start+count) as usize].iter().copied());}
            assert_eq!(actual,expected.into_iter().collect::<Vec<_>>());
            for (local,&global) in actual.iter().enumerate(){assert_eq!(plan.maps[i*5+global as usize],local as u32);}
        }
        assert!(seen.iter().all(|v|*v));assert!(plan.peak_bytes<=1_000_000_000);
        assert_eq!(plan.report(),Plan::build(n,&p,4,1000000,1000,100,1000).unwrap().report());
        assert!(Plan::build(n,&p,4,1000000,1000,100,1).is_err());
        assert!(Plan::build(n,&p,usize::MAX,usize::MAX,1000,100,1000).is_err());
    }
    assert_eq!(partitions(255).len(),2780);
}
#[test]
fn cohort_full_arenas_roots_capture_frozen_and_stop() {
    for np in [3,4,5,6,7,8,9] {for fixed in [false,true] {for batch in [5,32] {
        let mut runs=Vec::new();
        for mode in 0..7 {
            let mut s=fixture(np,fixed);
            let mut g=if mode==6{super::super::static_cdf::new(&s,2000).unwrap()}else if mode==5{PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap()}else if mode>=3{PreflopGpu::new_research_unrolled_cohorts(&s,2000).unwrap()}else if mode==2{PreflopGpu::new_research_cohorts(&s,2000).unwrap()}else{PreflopGpu::new(&s,2000).unwrap()};
            if mode==4 {g.enable_research_narrow_offsets().unwrap();}
            if mode==1 {g.enable_research_exact_cdf_reuse().unwrap();}
            g.mw_batch=batch;let mut rounds=Vec::new();
            for _ in 0..4 {g.iterate(&mut s).unwrap();let (gaps,evs)=g.gaps_and_evs().unwrap();
                rounds.push((bits(&g),gaps.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),evs.iter().map(|v|v.to_bits()).collect::<Vec<_>>()));}
            assert!(g.eval_graph.is_some());assert!(g.learning_graphs.iter().any(|x|x.is_some()));
            let before=bits(&g);let age=s.iteration;
            assert!(!g.try_iterate(&mut s,Some(&AtomicBool::new(true))).unwrap());assert_eq!(age,s.iteration);assert_eq!(before,bits(&g));
            let check=g.gaps_and_evs().unwrap();assert_eq!(before,bits(&g));assert_eq!(check,g.gaps_and_evs().unwrap());
            g.sync_to_cpu(&mut s).unwrap();let snap=s.arena_snapshot();
            assert_eq!(snap.0.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),before.0);
            assert_eq!(snap.1.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),before.1);
            runs.push(rounds);
        }
        assert_eq!(runs[0],runs[1],"C01 baseline np={np} fixed={fixed} batch={batch}");
        assert_eq!(runs[1],runs[2],"C07 np={np} fixed={fixed} batch={batch}");
        assert_eq!(runs[2],runs[3],"C09 np={np} fixed={fixed} batch={batch}");
        assert_eq!(runs[3],runs[4],"C13 np={np} fixed={fixed} batch={batch}");
        assert_eq!(runs[3],runs[5],"C14 np={np} fixed={fixed} batch={batch}");
        assert_eq!(runs[5],runs[6],"C23 np={np} fixed={fixed} batch={batch}");
    }}}
}

#[test]
fn narrow_offsets_rejects_incompatible_or_captured_state() {
    let s=fixture(4,false);
    let mut plain=PreflopGpu::new(&s,2000).unwrap();
    assert!(plain.enable_research_narrow_offsets().is_err());drop(plain);
    let mut g=PreflopGpu::new_research_unrolled_cohorts(&s,2000).unwrap();
    let before=bits(&g);
    let pointers=(g.d_mw_cdf.device_ptr(&g.stream).0,g.d_val.device_ptr(&g.stream).0,g.d_regrets.device_ptr(&g.stream).0);
    g.warmed=true;assert!(g.enable_research_narrow_offsets().is_err());g.warmed=false;
    g.eval_warmed=true;assert!(g.enable_research_narrow_offsets().is_err());g.eval_warmed=false;
    assert_eq!(bits(&g),before);g.enable_research_narrow_offsets().unwrap();
    assert_eq!(bits(&g),before);
    assert_eq!(pointers,(g.d_mw_cdf.device_ptr(&g.stream).0,g.d_val.device_ptr(&g.stream).0,g.d_regrets.device_ptr(&g.stream).0));
}

#[test]
fn retained_phase_tracing_preserves_solver_bits() {
    fn counts(v:&serde_json::Value,np:usize,batches:usize,groups:usize,average:bool,restore:bool) {
        let rows=v["rows"].as_array().unwrap();
        let count=|phase:&str|rows.iter().filter(|r|r["phase"]==phase).map(|r|r["intervals"].as_u64().unwrap() as usize).sum::<usize>();
        for phase in ["prepare","ordinary_terminals"] {assert_eq!(count(phase),np,"{phase}");}
        for phase in ["normalize","classify"] {assert_eq!(count(phase),if average{groups}else{np},"{phase}");}
        assert_eq!(count("cdf"),(if average{groups}else{np})*batches);
        assert_eq!(count("coupled_terminals"),np*batches);
        assert_eq!(count("down"),if average{1}else{np});
        assert_eq!(count("up_learn"),if average{0}else{np});
        for phase in ["up_average","up_br"] {assert_eq!(count(phase),if average{np}else{0},"{phase}");}
        assert_eq!(count("root_copy"),if average{2*np}else{0});
        assert_eq!(count("scratch_restore"),usize::from(average&&restore));
        let total=v["gpu_ms"].as_f64().unwrap();let sum=v["interval_sum_ms"].as_f64().unwrap();
        assert!(total.is_finite()&&total>=0.&&(total-sum).abs()<1.+total*0.001);
    }
    for np in [4,7,9] {for fixed in [false,true] {for batch in [5u32,32] {
        let mut results=Vec::new();
        for profile in [false,true] {
            let mut s=fixture(np,fixed);let mut g=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();g.mw_batch=batch;
            let c=g.research_cohorts.as_ref().unwrap();
            let groups=c.plan.spans.iter().filter(|(_,count)|*count>0).count();
            let restore=c.plan.groups.iter().find(|ps|ps.contains(&(np as i32-1))).unwrap().len()>1;
            let batches=crate::preflop::multiway::SAMPLES.div_ceil(batch as usize);let mut rounds=Vec::new();
            for _ in 0..3 {
                if profile {g.phase_profile_begin().unwrap();}
                g.iterate(&mut s).unwrap();
                if profile {counts(&g.phase_profile_end().unwrap(),np-usize::from(fixed),batches,groups,false,false);}
                if profile {g.phase_profile_begin().unwrap();}
                let (gaps,evs)=g.gaps_and_evs().unwrap();
                if profile {counts(&g.phase_profile_end().unwrap(),np,batches,groups,true,restore);}
                rounds.push((bits(&g),gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            if !profile {assert!(g.eval_graph.is_some()&&g.learning_graphs.iter().any(|x|x.is_some()));}
            results.push(rounds);
        }
        assert_eq!(results[0],results[1],"tracing altered retained C14 np={np} fixed={fixed} batch={batch}");
    }}}
}


#[test]
fn static_cdf_phase_tracing_preserves_solver_bits() {
    fn counts(v:&serde_json::Value,np:usize,batches:usize,groups:usize,average:bool,restore:bool) {
        let rows=v["rows"].as_array().unwrap();
        let count=|phase:&str|rows.iter().filter(|r|r["phase"]==phase).map(|r|r["intervals"].as_u64().unwrap() as usize).sum::<usize>();
        for phase in ["prepare","ordinary_terminals"] {assert_eq!(count(phase),np,"{phase}");}
        for phase in ["normalize","classify"] {assert_eq!(count(phase),if average{groups}else{np},"{phase}");}
        assert_eq!(count("cdf"),(if average{groups}else{np})*batches);
        assert_eq!(count("coupled_terminals"),np*batches);
        assert_eq!(count("down"),if average{1}else{np});
        assert_eq!(count("up_learn"),if average{0}else{np});
        for phase in ["up_average","up_br"] {assert_eq!(count(phase),if average{np}else{0},"{phase}");}
        assert_eq!(count("root_copy"),if average{2*np}else{0});
        assert_eq!(count("scratch_restore"),usize::from(average&&restore));
        let total=v["gpu_ms"].as_f64().unwrap();let sum=v["interval_sum_ms"].as_f64().unwrap();
        assert!(total.is_finite()&&total>=0.&&(total-sum).abs()<1.+total*0.001);
    }
    for np in [4,7,9] {for fixed in [false,true] {for batch in [5u32,32] {
        let mut results=Vec::new();
        for profile in [false,true] {
            let mut s=fixture(np,fixed);let mut g=super::super::static_cdf::new(&s,2000).unwrap();g.mw_batch=batch;
            let c=g.research_cohorts.as_ref().unwrap();
            let groups=c.plan.spans.iter().filter(|(_,count)|*count>0).count();
            let restore=c.plan.groups.iter().find(|ps|ps.contains(&(np as i32-1))).unwrap().len()>1;
            let batches=crate::preflop::multiway::SAMPLES.div_ceil(batch as usize);let mut rounds=Vec::new();
            for _ in 0..3 {
                if profile {g.phase_profile_begin().unwrap();}
                g.iterate(&mut s).unwrap();
                if profile {counts(&g.phase_profile_end().unwrap(),np-usize::from(fixed),batches,groups,false,false);}
                if profile {g.phase_profile_begin().unwrap();}
                let (gaps,evs)=g.gaps_and_evs().unwrap();
                if profile {counts(&g.phase_profile_end().unwrap(),np,batches,groups,true,restore);}
                rounds.push((bits(&g),gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            if !profile {assert!(g.eval_graph.is_some()&&g.learning_graphs.iter().any(|x|x.is_some()));}
            results.push(rounds);
        }
        assert_eq!(results[0],results[1],"tracing altered C23 np={np} fixed={fixed} batch={batch}");
    }}}
}


#[test]
fn static_cdf_real_allocation_failure_and_retry() {
    let ctx=CudaContext::new(0).unwrap();
    let used=||{ctx.synchronize().unwrap();ctx.bind_to_thread().unwrap();assert!(ctx.has_async_alloc());let mut bytes=0u64;
        unsafe{let pool=cudarc::driver::result::device::get_mem_pool(ctx.cu_device()).unwrap();
            cudarc::driver::result::mem_pool::get_attribute(pool,sys::CUmemPool_attribute::CU_MEMPOOL_ATTR_USED_MEM_CURRENT,(&mut bytes as *mut u64).cast()).unwrap();}bytes};
    let mut s=fixture(4,false);let initial=s.arena_snapshot();
    for stage in [1,2,3]{
        let before=used();super::super::static_cdf::FAIL_STAGE.set(stage);
        let result=super::super::static_cdf::new(&s,2000);assert!(result.is_err());
        assert!(result.err().unwrap().contains(&format!("allocation stage {stage}")));
        assert_eq!(super::super::static_cdf::FAIL_STAGE.get(),0);assert_eq!(used(),before);
        assert_eq!(initial,s.arena_snapshot());
    }
    let mut g=super::super::static_cdf::new(&s,2000).unwrap();g.mw_batch=5;
    let mut observed=Vec::new();for _ in 0..3{g.iterate(&mut s).unwrap();let metric=g.gaps_and_evs().unwrap();observed.push((bits(&g),metric));}drop(g);
    let mut s=fixture(4,false);let mut g=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();g.mw_batch=5;
    let mut expected=Vec::new();for _ in 0..3{g.iterate(&mut s).unwrap();let metric=g.gaps_and_evs().unwrap();expected.push((bits(&g),metric));}
    assert!(observed==expected);
}

#[test]
fn static_cdf_save_reload_and_interrupted_replay() {
    let output=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_STATIC_CDF_INTEGRATED_OUTPUT").unwrap());
    let mut all=Vec::new();
    for compact in [false,true]{
        let mut s=fixture(4,true);
        let mut g=if compact{super::super::static_cdf::new(&s,2000).unwrap()}else{PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap()};g.mw_batch=5;
        for _ in 0..3{g.iterate(&mut s).unwrap();g.gaps_and_evs().unwrap();}
        g.sync_to_cpu(&mut s).unwrap();let saved=output.join(format!("continued-{compact}.gtop"));assert!(!saved.exists());s.save_game(saved.to_str().unwrap()).unwrap();drop(g);
        let mut s=PreflopSolver::load_game(saved.to_str().unwrap(),eq()).unwrap();
        let mut g=if compact{super::super::static_cdf::new(&s,2000).unwrap()}else{PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap()};g.mw_batch=5;
        let mut rounds=Vec::new();for _ in 0..3{g.iterate(&mut s).unwrap();let metrics=g.gaps_and_evs().unwrap();rounds.push((bits(&g),metrics));}all.push(rounds);
    }
    assert!(all[0]==all[1]);assert_eq!(std::fs::read(output.join("continued-false.gtop")).unwrap(),std::fs::read(output.join("continued-true.gtop")).unwrap());
    // Cold eager launches permit a real stop request between queued player sweeps.
    let saved=output.join("continued-true.gtop");let mut s=PreflopSolver::load_game(saved.to_str().unwrap(),eq()).unwrap();
    let mut g=super::super::static_cdf::new(&s,2000).unwrap();g.mw_batch=5;
    let age=s.iteration;let before=bits(&g);let stop=Arc::new(AtomicBool::new(false));let request=stop.clone();
    let signal=std::thread::spawn(move||{std::thread::sleep(std::time::Duration::from_millis(5));request.store(true,Ordering::Relaxed);});
    let completed=g.try_iterate(&mut s,Some(&stop)).unwrap();signal.join().unwrap();
    assert!(!completed,"stop must arrive during the eager sweep");assert_eq!(s.iteration,age);
    let interrupted=bits(&g);assert!((interrupted.0.clone(),interrupted.1.clone())!=(before.0,before.1),"must have completed actual player work");
    g.sync_to_cpu(&mut s).unwrap();let path=output.join("interrupted.gtop");assert!(!path.exists());s.save_game(path.to_str().unwrap()).unwrap();drop(g);
    let original=PreflopSolver::load_game(saved.to_str().unwrap(),eq()).unwrap();let mut replay=PreflopGpu::new_research_narrow_cohorts(&original,2000).unwrap();replay.mw_batch=5;
    let mut matched=None;for p in 0..replay.np{if replay.static_seats[p as usize]{continue;}replay.sweep(p,0).unwrap();replay.stream.synchronize().unwrap();let b=bits(&replay);
        if b.0==interrupted.0&&b.1==interrupted.1{matched=Some(p);break;}}
    assert!(matched.is_some(),"interrupted arenas must match an exact retained sweep prefix");drop(replay);
    let mut resumed=Vec::new();for compact in [false,true]{let mut s=PreflopSolver::load_game(path.to_str().unwrap(),eq()).unwrap();let mut g=if compact{super::super::static_cdf::new(&s,2000).unwrap()}else{PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap()};g.mw_batch=5;
        let mut rounds=Vec::new();for _ in 0..3{g.iterate(&mut s).unwrap();let metrics=g.gaps_and_evs().unwrap();rounds.push((bits(&g),metrics));}resumed.push(rounds);}
    assert!(resumed[0]==resumed[1]);
    std::fs::write(output.join("continuation.json"),serde_json::to_vec_pretty(&json!({"saved_files_identical":true,"continuation_rounds":3,"interrupted_iteration":age,"matched_last_player":matched,"interrupted_continuation_exact":true})).unwrap()).unwrap();
}
