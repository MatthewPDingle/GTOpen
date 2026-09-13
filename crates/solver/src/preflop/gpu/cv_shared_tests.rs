use super::*;
use crate::preflop::{PreflopConfig,convergence_research::Experiment,equity::EquityTable};
fn fixture(calibrated:bool)->PreflopSolver{
    let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
    let bytes=std::fs::read(path).unwrap();
    let eq=Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(bytes[..4].try_into().unwrap())));
    let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],
        "stack":10.0,"posts":[0.0,0.0,0.5,1.0],"limp":true,"open_raises":[2.0],"raise_mults":[3.0],
        "max_raises":2,"add_allin":false,"rake_pct":5.0,"rake_cap":1.0,
        "realization":if calibrated{"calibrated"}else{"raw"}})).unwrap();
    let mut s=PreflopSolver::new(cfg,eq).unwrap();
    s.research_seed_quality_fixture_averages().unwrap();s.seat_frozen[2]=true;
    let node=s.child(0,1);let mut policy=vec![0.0;s.nodes[node].actions.len()*NUM_CLASSES];
    policy[..NUM_CLASSES].fill(1.0);s.point_locks.insert(node as u32,policy);
    s
}
fn gpu(s:&PreflopSolver,samples:u32,shared:Option<u32>)->PreflopGpu{
    let mut g=PreflopGpu::new(s,2000).unwrap();
    g.configure_research(Experiment::new("dcfr",samples,1000,42).unwrap()).unwrap();
    if let Some(interval)=shared{g.enable_research_shared_control_variate(interval,100).unwrap();}g
}
fn bits(v:Vec<f32>)->Vec<u32>{v.into_iter().map(f32::to_bits).collect()}
fn arenas(g:&PreflopGpu)->(Vec<u32>,Vec<u32>){
    (bits(g.stream.clone_dtoh(&g.d_regrets).unwrap()),bits(g.stream.clone_dtoh(&g.d_strat).unwrap()))
}
fn state(g:&PreflopGpu)->Vec<Vec<u32>>{
    let c=g.research_cv.as_ref().unwrap().shared.as_ref().unwrap();
    let (r,a)=arenas(g);vec![r,a,bits(g.stream.clone_dtoh(&c.reach).unwrap()),
        bits(g.stream.clone_dtoh(&c.mass).unwrap()),bits(g.stream.clone_dtoh(&c.full).unwrap())]
}
#[test]
fn shared_cv_storage_and_live_cache_are_exact(){
    for calibrated in [false,true]{
        let s=fixture(calibrated);let mut g=gpu(&s,64,None);
        assert!(g.enable_research_shared_control_variate(2,0).is_err());assert!(g.research_cv.is_none());
        let report=g.enable_research_shared_control_variate(2,100).unwrap();
        assert_eq!(report,s.research_shared_cv_storage().unwrap()["storage"]);
        let cv=g.research_cv.as_ref().unwrap();let r=cv.shared.as_ref().unwrap();
        assert_eq!(report["persistent_extra_bytes"].as_u64().unwrap() as usize,
            4*(r.reach.len()+r.mass.len()+r.full.len()+r.offsets.len()+cv.current.len()));
        let mut cv=g.research_cv.take().unwrap();g.shared_refresh(0,0,&mut cv).unwrap();
        let before=cv.shared.as_ref().unwrap().last_refresh;g.shared_refresh(1,0,&mut cv).unwrap();
        assert_eq!(cv.refreshes,1);assert_eq!(before,cv.shared.as_ref().unwrap().last_refresh);
        g.research_tables_select(false,false).unwrap();
        let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();let terms=g.stream.clone_dtoh(&g.d_mw_terms).unwrap();
        let live=g.stream.clone_dtoh(&g.d_live).unwrap();
        let r=cv.shared.as_mut().unwrap();let offsets=g.stream.clone_dtoh(&r.offsets).unwrap();
        let cache=g.stream.clone_dtoh(&r.full).unwrap();let mut seen=std::collections::HashSet::new();
        for p in 0..g.np as usize{
            if !g.static_seats[p]{g.shared_reference_values(p as i32,r).unwrap();}
            let values=g.stream.clone_dtoh(&g.d_val).unwrap();
            for (t,&nd) in terms.iter().enumerate(){
                let off=offsets[p*terms.len()+t];let valid=!g.static_seats[p] && live[nd as usize]&(1<<p)!=0;
                assert_eq!(off!=u32::MAX,valid);
                if valid{assert!(seen.insert(off));for h in 0..NUM_CLASSES{
                    assert_eq!(cache[off as usize+h].to_bits(),values[slots[nd as usize] as usize*NUM_CLASSES+h].to_bits());
                }}
            }
        }
        assert_eq!(seen.len()*NUM_CLASSES,cache.len());g.research_cv=Some(cv);
    }
    assert!(Plan::build(&[1],&[15],&[0],&[false;4],169,1).is_err());
    assert!(Plan::build(&[2],&[3],&[0],&[false;4],169,1).is_err());
    assert!(Plan::build(&[2],&[31],&[0],&[false;4],169,1).is_err());
    assert!(Plan::build(&[2],&[15],&[1],&[false;4],169,1).is_err());
    assert!(Plan::build(&[2],&[15],&[0],&[false;4],usize::MAX,usize::MAX).is_err());
}
#[test]
fn shared_cv_full_particles_cancel_and_capture_is_exact(){
    for calibrated in [false,true]{
        let mut s=fixture(calibrated);let mut a=gpu(&s,1024,None);let mut b=gpu(&s,1024,Some(2));
        let mut counter=s.iteration;
        for _ in 0..5{a.iterate(&mut s).unwrap();b.try_iterate_counter(&mut counter,None).unwrap();assert_eq!(arenas(&a),arenas(&b));}
        assert_eq!(a.gaps_and_evs().unwrap(),b.gaps_and_evs().unwrap());drop(a);drop(b);
        let s=fixture(calibrated);let mut a=gpu(&s,64,Some(2));let mut b=gpu(&s,64,Some(2));
        let(mut ca,mut cb)=(s.iteration,s.iteration);
        for _ in 0..6{
            a.warmed=false;a.try_iterate_counter(&mut ca,None).unwrap();b.try_iterate_counter(&mut cb,None).unwrap();
            assert_eq!(state(&a),state(&b));
        }
        assert_eq!(a.research_shared_control_variate_stats().unwrap()["refresh_epochs"],3);
        assert_eq!(b.research_shared_control_variate_stats().unwrap()["captured_sweeps"],3);
        let before=state(&b);assert_eq!(a.gaps_and_evs().unwrap(),b.gaps_and_evs().unwrap());assert_eq!(before,state(&b));
        assert!(b.enable_research_shared_control_variate(2,100).is_err());
    }
    let s=fixture(false);let mut g=PreflopGpu::new(&s,2000).unwrap();
    assert!(g.enable_research_shared_control_variate(2,100).is_err());
    g.configure_research(Experiment::new("dcfr",64,1000,42).unwrap()).unwrap();
    assert!(g.enable_research_shared_control_variate(0,100).is_err());
    g.gaps_and_evs().unwrap();assert!(g.enable_research_shared_control_variate(2,100).is_err());drop(g);
    let mut g=gpu(&s,64,Some(2));let mut n=0;let before=state(&g);
    assert!(g.configure_research(Experiment::new("dcfr",64,1000,7).unwrap()).is_err());
    assert!(g.research_restrict_learning(&s,&std::collections::HashSet::from([0usize])).is_err());
    assert!(g.research_set_root_ranges(vec![vec![1.0/NUM_CLASSES as f32;NUM_CLASSES];s.n]).is_err());
    assert!(g.research_frontier_action_values(&s,&[vec![]]).is_err());
    assert!(g.enable_research_control_variate(2,100).is_err());
    assert_eq!(before,state(&g));
    assert!(!g.try_iterate_counter(&mut n,Some(&AtomicBool::new(true))).unwrap());assert_eq!(n,0);assert_eq!(before,state(&g));
}
#[test]
fn shared_cv_stale_reference_cohort_mean_matches_full_payoff(){
    for calibrated in [false,true]{
        let s=fixture(calibrated);let mut g=gpu(&s,64,Some(64));
        let mut regrets=g.stream.clone_dtoh(&g.d_regrets).unwrap();
        let na=s.nodes[0].actions.len();regrets[..na*NUM_CLASSES].fill(0.0);regrets[..NUM_CLASSES].fill(1.0);
        g.stream.memcpy_htod(&regrets,&mut g.d_regrets).unwrap();
        let mut cv=g.research_cv.take().unwrap();g.shared_refresh(0,0,&mut cv).unwrap();
        let masses=g.stream.clone_dtoh(&g.d_reach_mass).unwrap();assert!(masses.iter().any(|&m|m==0.0));
        let prior=g.stream.clone_dtoh(&cv.shared.as_ref().unwrap().mass).unwrap();assert!(prior.iter().all(|&m|m>0.0));
        // A stale reference with zero reach becomes reachable under the current policy.
        for a in 0..na{for h in 0..NUM_CLASSES{regrets[a*NUM_CLASSES+h]=(1+(h*17+a*29)%19) as f32;}}
        g.stream.memcpy_htod(&regrets,&mut g.d_regrets).unwrap();
        let terms=g.stream.clone_dtoh(&g.d_mw_terms).unwrap();let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();
        let live=g.stream.clone_dtoh(&g.d_live).unwrap();let mut max_error=0.0f64;let mut count=0;let mut min_correction=0.0f32;let mut max_correction=0.0f32;
        for p in 0..g.np{
            if g.static_seats[p as usize]{continue;}
            g.research_tables_select(false,false).unwrap();g.down(0,p).unwrap();g.terminals(p).unwrap();
            let full=g.stream.clone_dtoh(&g.d_val).unwrap();let mut means=vec![0.0f64;terms.len()*NUM_CLASSES];
            for cohort in 0..16{
                g.research.as_mut().unwrap().offset=cohort*64;g.research_tables_select(true,false).unwrap();
                g.down(0,p).unwrap();g.shared_correct_terminals(p,&mut cv).unwrap();
                let values=g.stream.clone_dtoh(&g.d_val).unwrap();
                let uncorrected=g.stream.clone_dtoh(&cv.current).unwrap();
                for (t,&nd) in terms.iter().enumerate(){if live[nd as usize]&(1<<p)!=0{for h in 0..NUM_CLASSES{
                    let value=values[slots[nd as usize] as usize*NUM_CLASSES+h];assert!(value.is_finite());
                    let correction=value-uncorrected[t*NUM_CLASSES+h];
                    min_correction=min_correction.min(correction);max_correction=max_correction.max(correction);
                    means[t*NUM_CLASSES+h]+=value as f64/16.0;
                }}}
            }
            for (t,&nd) in terms.iter().enumerate(){if live[nd as usize]&(1<<p)!=0{for h in 0..NUM_CLASSES{
                let expected=full[slots[nd as usize] as usize*NUM_CLASSES+h] as f64;
                let error=(means[t*NUM_CLASSES+h]-expected).abs()/(1.0+expected.abs());max_error=max_error.max(error);count+=1;
                assert!(error<=2e-4,"biased shared correction: {error}");
            }}}
        }
        assert!(min_correction < -1e-7 && max_correction > 1e-7,"stale test did not exercise signed nonzero correction");
        eprintln!("shared CV stale-cohort calibrated={calibrated} entries={count} maximum normalized error={max_error} correction_range=[{min_correction},{max_correction}]");
        g.research_cv=Some(cv);
    }
}
