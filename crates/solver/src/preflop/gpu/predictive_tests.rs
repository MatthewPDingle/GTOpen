use super::*;
use crate::preflop::{convergence_research::Experiment,equity::EquityTable,PreflopConfig};

fn fixture(calibrated:bool)->PreflopSolver {
    let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],
        "posts":[0,0,0.5,1],"stack":5,"limp":true,"open_raises":[2],"raise_mults":[3],
        "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,
        "realization":if calibrated {"calibrated"} else {"raw"}})).unwrap();
    let mut s=PreflopSolver::new(cfg,Arc::new(EquityTable::build(8))).unwrap();
    if calibrated {assert!(s.fit.is_some());}
    s.seat_frozen[2]=true;
    let locknode=s.child(0,0);
    let mut lock=vec![0.;s.nodes[locknode].actions.len()*NUM_CLASSES];lock[..NUM_CLASSES].fill(1.);
    s.point_locks.insert(locknode as u32,lock);
    unsafe {
        let r=s.regrets.slice_mut(); let a=s.strat_sum.slice_mut();
        for (i,nd) in s.nodes.iter().enumerate() {
            if nd.actor!=2 && i!=locknode {continue;}
            for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {
                r[ix]=if ix%2==0 {-0.25} else {0.5}; a[ix]=(1+ix%7) as f32/10.;
            }
        }
    }
    s
}

fn base(s:&PreflopSolver,samples:u32)->PreflopGpu {
    let mut g=PreflopGpu::new(s,512).unwrap();
    g.configure_research(Experiment::new("dcfr",samples,1000,42).unwrap()).unwrap();
    if samples==64 {g.enable_research_pair_control(100).unwrap();}
    g
}

fn near(a:&[f32],b:&[f32],tol:f32,label:&str) {
    assert_eq!(a.len(),b.len());
    for (i,(&a,&b)) in a.iter().zip(b).enumerate() {
        assert!(a.is_finite()&&b.is_finite()&&(a-b).abs()<=tol*(1.+b.abs()),"{label} {i}: {a} != {b}");
    }
}

fn normalize(mut a:Vec<f32>)->Vec<f32> {
    let sum:f32=a.iter().sum();let n=a.len();
    for v in &mut a {*v=if sum>1e-12 {*v/sum} else {1./n as f32};} a
}

// Full-node host storage, not the reused GPU slots. Descendant strategies are
// selected before parent predictions, and counterfactual weights stay native.
fn host_up(s:&PreflopSolver,p:usize,values:&mut [Vec<f32>],policy:&mut [f32],r:&mut [f32],a:&mut [f32],
    src:&[i32],forced:&[f32],foff:&[u32],reach:&[f32],rs:&[u32],predict:bool) {
    for node in (0..s.nodes.len()).rev() {
        let nd=&s.nodes[node];let na=nd.actions.len();if nd.kind!=KIND_ACTION {continue;}
        assert!((0..na).all(|action|s.child(node,action)>node));
        for h in 0..NUM_CLASSES {
            let q:Vec<f32>=(0..na).map(|action|values[s.child(node,action)][h]).collect();
            if nd.actor as usize!=p {values[node][h]=q.iter().sum();continue;}
            let mut sigma=match src[node] {
                2=>(0..na).map(|x|forced[foff[node] as usize+x*NUM_CLASSES+h]).collect(),
                1=>normalize((0..na).map(|x|a[nd.data_off+x*NUM_CLASSES+h]).collect()),
                _=>normalize((0..na).map(|x|policy[nd.data_off+x*NUM_CLASSES+h]).collect()),
            };
            let out:f32=sigma.iter().zip(&q).map(|(x,v)|x*v).sum();
            if src[node]==0 && predict {
                sigma=normalize((0..na).map(|x|(r[nd.data_off+x*NUM_CLASSES+h]+q[x]-out).max(0.)).collect());
                for x in 0..na {policy[nd.data_off+x*NUM_CLASSES+h]=sigma[x];}
                values[node][h]=sigma.iter().zip(&q).map(|(x,v)|x*v).sum();
            } else {
                values[node][h]=out;
                if src[node]==0 {
                    let rp=reach[rs[node*s.n+p] as usize*NUM_CLASSES+h];
                    for x in 0..na {
                        let ix=nd.data_off+x*NUM_CLASSES+h;
                        r[ix]=(r[ix]+q[x]-out).max(0.);a[ix]+=rp*sigma[x];
                    }
                }
            }
        }
    }
}

#[test]
fn predictive_history_compression_is_exact() {
    for cal in [false,true] {for samples in [1024,64] {
        let s=fixture(cal);let mut g=base(&s,samples);
        assert!(g.enable_research_predictive(true,0).is_err());assert!(g.research_predictive.is_none());
        let report=g.enable_research_predictive(true,100).unwrap();
        assert_eq!(report,s.research_prediction_storage().unwrap()["storage"]);
        assert!(report["vector_terminals"].as_u64().unwrap()>0 && report["scalar_terminals"].as_u64().unwrap()>0);
        let terms=g.stream.clone_dtoh(&g.d_terms).unwrap();let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();
        let mut dense=Vec::new();
        for p in 0..s.n {
            g.research_tables(true).unwrap();g.down(0,p as i32).unwrap();g.terminals(p as i32).unwrap();
            let v=g.stream.clone_dtoh(&g.d_val).unwrap();
            dense.push(terms.iter().map(|&nd|v[slots[nd as usize] as usize*NUM_CLASSES..(slots[nd as usize] as usize+1)*NUM_CLASSES].to_vec()).collect::<Vec<_>>());
            g.predictive_transfer(p as i32,true).unwrap();
        }
        assert!(dense.iter().flatten().flatten().any(|x|*x==0.));
        assert!(dense.iter().flatten().flatten().any(|x|*x!=0.));
        for p in 0..s.n {
            let junk=vec![123.0;g.d_val.len()];g.stream.memcpy_htod(&junk,&mut g.d_val).unwrap();
            g.predictive_transfer(p as i32,false).unwrap();let v=g.stream.clone_dtoh(&g.d_val).unwrap();
            for (i,&nd) in terms.iter().enumerate() {
                let offset=slots[nd as usize] as usize*NUM_CLASSES;
                assert_eq!(v[offset..offset+NUM_CLASSES].iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    dense[p][i].iter().map(|x|x.to_bits()).collect::<Vec<_>>());
            }
        }
    }}
}

#[test]
fn predictive_matches_independent_host_recursion() {
    for cal in [false,true] {for samples in [1024,64] {for enabled in [false,true] {
        let mut s=fixture(cal);let mut g=base(&s,samples);g.enable_research_predictive(enabled,100).unwrap();
        let mut reference=base(&s,samples);
        let (mut r,mut a)=s.arena_snapshot();let mut policy=vec![0.;r.len()];
        let src=g.stream.clone_dtoh(&g.d_src).unwrap();let forced=g.stream.clone_dtoh(&g.d_forced).unwrap();
        let foff=g.stream.clone_dtoh(&g.d_foff).unwrap();let rs=g.stream.clone_dtoh(&g.d_reach_src).unwrap();
        let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();
        let mut histories=vec![vec![vec![0.;NUM_CLASSES];s.nodes.len()];s.n];
        for t in 1..=4 {
            for p in 0..s.n {
                if reference.static_seats[p] {continue;}
                let mut predicted=if enabled {histories[p].clone()} else {vec![vec![0.;NUM_CLASSES];s.nodes.len()]};
                host_up(&s,p,&mut predicted,&mut policy,&mut r,&mut a,&src,&forced,&foff,&[],&rs,true);
                reference.stream.memcpy_htod(&policy,&mut reference.d_regrets).unwrap();
                reference.stream.memcpy_htod(&a,&mut reference.d_strat).unwrap();
                reference.research_tables(true).unwrap();reference.down(0,p as i32).unwrap();reference.terminals(p as i32).unwrap();
                let v=reference.stream.clone_dtoh(&reference.d_val).unwrap();
                let reach=reference.stream.clone_dtoh(&reference.d_reach).unwrap();
                for (i,nd) in s.nodes.iter().enumerate() {
                    if nd.kind==KIND_ACTION {continue;}
                    histories[p][i].copy_from_slice(&v[slots[i] as usize*NUM_CLASSES..(slots[i] as usize+1)*NUM_CLASSES]);
                }
                let mut observed=histories[p].clone();
                host_up(&s,p,&mut observed,&mut policy,&mut r,&mut a,&src,&forced,&foff,&reach,&rs,false);
            }
            let discount=(t as f64/(t as f64+1.)).powi(2) as f32;
            for (i,nd) in s.nodes.iter().enumerate() {if src[i]!=1 {
                for v in &mut a[nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES] {*v*=discount;}
            }}
            g.iterate(&mut s).unwrap();
            near(&g.stream.clone_dtoh(&g.d_regrets).unwrap(),&r,2e-5,"regrets");
            near(&g.stream.clone_dtoh(&g.d_strat).unwrap(),&a,2e-5,"averages");
            let pred=g.research_predictive.as_ref().unwrap();
            near(&g.stream.clone_dtoh(&pred.policy).unwrap(),&policy,1e-4,"policy");
            let hist=g.stream.clone_dtoh(&pred.history).unwrap();let offsets=g.stream.clone_dtoh(&pred.offsets).unwrap();
            let terms=g.stream.clone_dtoh(&g.d_terms).unwrap();
            for p in 0..s.n {for (i,&nd) in terms.iter().enumerate() {
                let nd=nd as usize;let off=offsets[p*terms.len()+i] as usize;
                let count=if s.nodes[nd].kind==KIND_POT_SHARE && s.nodes[nd].live&(1<<p)!=0 {NUM_CLASSES} else {1};
                near(&hist[off..off+count],&histories[p][nd][..count],2e-5,"terminal history");
            }}
        }
    }}}
}

#[test]
fn predictive_capture_evaluation_and_admission() {
    let mut records=Vec::new();
    for eager in [false,true] {
        let mut s=fixture(true);let mut g=base(&s,64);g.enable_research_predictive(true,100).unwrap();
        assert!(g.enable_research_predictive(true,100).is_err());
        assert!(g.enable_research_rm_plus().is_err());assert!(g.enable_research_normalized_regret().is_err());
        assert!(g.enable_research_normalized_pair_control(100).is_err());
        assert!(g.enable_research_opponent_exploration(0.01,250).is_err());
        assert!(g.enable_research_control_variate(1,100).is_err());assert!(g.enable_research_average_opponents().is_err());
        assert!(g.configure_research(Experiment::new("dcfr",64,1000,42).unwrap()).is_err());
        for _ in 0..4 {
            if eager {g.warmed=false;for graph in &mut g.learning_graphs {*graph=None;}}
            g.iterate(&mut s).unwrap();
        }
        let before=(g.stream.clone_dtoh(&g.d_regrets).unwrap(),g.stream.clone_dtoh(&g.d_strat).unwrap(),
            g.stream.clone_dtoh(&g.research_predictive.as_ref().unwrap().policy).unwrap(),
            g.stream.clone_dtoh(&g.research_predictive.as_ref().unwrap().history).unwrap());
        let actual=g.gaps_and_evs().unwrap();
        assert_eq!(before.0,g.stream.clone_dtoh(&g.d_regrets).unwrap());
        assert_eq!(before.1,g.stream.clone_dtoh(&g.d_strat).unwrap());
        assert_eq!(before.2,g.stream.clone_dtoh(&g.research_predictive.as_ref().unwrap().policy).unwrap());
        assert_eq!(before.3,g.stream.clone_dtoh(&g.research_predictive.as_ref().unwrap().history).unwrap());
        g.sync_to_cpu(&mut s).unwrap();let mut native=PreflopGpu::new(&s,512).unwrap();
        assert_eq!(actual,native.gaps_and_evs().unwrap());let cpu=s.gaps_and_evs();
        assert!(actual.0.iter().chain(&actual.1).zip(cpu.0.iter().chain(&cpu.1)).all(|(a,b)|(a-b).abs()<0.005));
        let mut resumed=base(&s,64);assert!(resumed.enable_research_predictive(true,100).is_err());
        records.push(before);
    }
    assert_eq!(records[0],records[1]);
    let s=fixture(false);let mut missing=PreflopGpu::new(&s,512).unwrap();assert!(missing.enable_research_predictive(true,100).is_err());
    let mut rm=base(&s,64);rm.enable_research_rm_plus().unwrap();assert!(rm.enable_research_predictive(true,100).is_err());
    let mut evaluated=base(&s,64);evaluated.gaps_and_evs().unwrap();assert!(evaluated.enable_research_predictive(true,100).is_err());
    assert!(StoragePlan::build(&[0],&[3],&[0],2,1).is_err());
    assert!(StoragePlan::build(&[2],&[8],&[0],2,1).is_err());
    assert!(StoragePlan::build(&[2],&[3],&[0],2,usize::MAX).is_err());
}
