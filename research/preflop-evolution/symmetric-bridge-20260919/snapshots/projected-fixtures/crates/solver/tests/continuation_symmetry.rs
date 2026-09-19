#![cfg(feature = "preflop-research")]
use solver::{Algorithm, Solver, Spot, SpotConfig, TreeConfig, StreetSizing, parse_sizes};
use solver::{gpu::{GpuSolver, SymmetricContinuationGpu, plan::GpuPlan}, game::Dealt};
use std::sync::Arc;

fn spot(board: &str) -> Arc<Spot> {
    let size=StreetSizing {bet:parse_sizes("50").unwrap(),raise:vec![],donk:parse_sizes("50").unwrap()};
    Arc::new(Spot::new(SpotConfig {board:board.into(),range_oop:"AA,KK,AQs,KQo,88,76s".into(),
        range_ip:"AA,QQ,AKo,QJs,99".into(),tree:TreeConfig {starting_pot:39.5,effective_stack:80.,
            rake_pct:0.04,rake_cap:6.,max_raises:0,oop:[size.clone(),size.clone(),size.clone()],
            ip:[size.clone(),size.clone(),size],..Default::default()}}).unwrap())
}
fn host(spot: &Arc<Spot>, iso: bool) -> Solver {
    let mut s=Solver::new(spot.clone());s.use_isomorphism=iso;s.algo=Algorithm::CfrPlus;s
}
fn budget(spot:&Spot)->u64 {
    let plan=GpuPlan::build(spot,true);
    plan.staging_bytes()+plan.arena_elements.iter().sum::<usize>() as u64*8+512*1024*1024+spot.tree.nodes.len() as u64*4
}
fn reaches(spot:&Spot,q:usize,t:u32)->Vec<f32> {
    spot.hands[q].iter().map(|h| {
        let class=solver::preflop::equity::class_index(h.c1/4,h.c2/4,h.c1%4==h.c2%4);
        0.02+((class*7+t as usize*3+q*11)%23) as f32/23.
    }).collect()
}
fn maximum(a:&[f32],b:&[f32])->f32 {
    a.iter().zip(b).map(|(x,y)|(x-y).abs()).fold(0.,f32::max)
}

fn policy_symmetry_error(s:&Solver)->(f32,f32) {
    let sp=&s.spot;let mut stack=vec![(0u32,Dealt::default())];let mut worst=(0f32,0f32);
    while let Some((i,d))=stack.pop() {
        let n=&sp.tree.nodes[i as usize];
        if n.kind==solver::tree::KIND_ACTION {
            let p=n.player as usize;let nh=sp.hands[p].len();let perms=sp.perms_fixing(&d);
            if perms.len()>1 {
                let average=s.average_strategy(i,n);let mut current=vec![0.;average.len()];
                unsafe{s.regrets[p].read_f32(i,n.data_offset,current.len(),&mut current);}
                solver::cfr::regret_match_inplace(&mut current,n.num_children as usize,nh);
                for &k in &perms {for a in 0..n.num_children as usize {for h in 0..nh {
                    if d.cards[..d.len as usize].iter().any(|c|sp.hands[p][h].mask&(1u64<<c)!=0) {continue;}
                    let j=sp.hand_perm[p][k][h] as usize;
                    worst.0=worst.0.max((average[a*nh+h]-average[a*nh+j]).abs());
                    worst.1=worst.1.max((current[a*nh+h]-current[a*nh+j]).abs());
                }}}
            }
            for a in 0..n.num_children as usize {stack.push((sp.tree.children[n.children_start as usize+a],d));}
        } else if n.kind==solver::tree::KIND_CHANCE {
            for c in 0..52u8 {
                let child=sp.tree.children[n.children_start as usize+c as usize];
                if child!=solver::tree::SENTINEL && !d.contains(c) {stack.push((child,d.push(c)));}
            }
        }
    }
    worst
}

#[test]
fn symmetric_continuation_matches_uncompressed_values_and_averages() {
    let mut failures=vec![];
    for board in ["KsQs2d","KsQs2s","KsQh2d"] {
        let sp=spot(board);
        let mut iso=host(&sp,true);let mut cpu=host(&sp,true);let mut plain=host(&sp,false);
        let mut gpu=SymmetricContinuationGpu::new_with_budget(&iso,budget(&sp)).unwrap();
        let mut full=SymmetricContinuationGpu::new_explicit_reference(&plain,u64::MAX).unwrap();
        let mut raw_host=host(&sp,false);let mut raw=GpuSolver::new(&raw_host).unwrap();
        let full_bytes=sp.tree.data_size.iter().sum::<u64>()*8;
        if sp.suit_perms.len()>1 {assert!(gpu.arena_bytes()<full_bytes);}
        let (mut cfv,mut root,mut trajectory_cfv,mut gpu_replay)=(0f32,0f32,0f32,0f32);
        for t in 1..=100 {for p in 0..2 {
            cpu.use_isomorphism=true;gpu.sync_to_cpu(&mut cpu).unwrap();cpu.use_isomorphism=false;
            let mut own=reaches(&sp,p,t);let opp=reaches(&sp,1-p,t+13);
            if t%17==0 {own.fill(0.);}
            let mut replay=if t<=2 || t%20==0 {Some(GpuSolver::new(&cpu).unwrap())} else {None};
            let a=cpu.research_continuation_sweep(p,t,&own,&opp).unwrap();
            let b=gpu.sweep(p,t,&own,&opp).unwrap();
            let c=full.sweep(p,t,&own,&opp).unwrap();
            raw.research_continuation_sweep(p,t,&own,&opp).unwrap();
            let mass=opp.iter().sum::<f32>();
            if let Some(g)=replay.as_mut() {
                gpu_replay=gpu_replay.max(maximum(&g.research_continuation_sweep(p,t,&own,&opp).unwrap(),&b)/mass);
            }
            cfv=cfv.max(maximum(&a,&b)/mass);
            trajectory_cfv=trajectory_cfv.max(maximum(&b,&c)/mass);
            if p==0 {
                gpu.sync_to_cpu(&mut iso).unwrap();
                root=root.max(maximum(&cpu.average_strategy(0,&sp.tree.nodes[0]),&iso.average_strategy(0,&sp.tree.nodes[0])));
            }
        }}
        gpu.sync_to_cpu(&mut iso).unwrap();full.sync_to_cpu(&mut plain).unwrap();
        raw.sync_to_cpu(&mut raw_host).unwrap();
        let drift=maximum(&iso.average_strategy(0,&sp.tree.nodes[0]),&plain.average_strategy(0,&sp.tree.nodes[0]));
        let sigma=iso.average_strategy(0,&sp.tree.nodes[0]);
        let mut root_asymmetry=0f32;
        for permutation in &sp.hand_perm[0] {for action in sigma.chunks(sp.hands[0].len()) {
            for (i,&j) in permutation.iter().enumerate() {root_asymmetry=root_asymmetry.max((action[i]-action[j as usize]).abs());}
        }}
        let mut evaluation=0f32;
        let mut quotient_evaluation=0f32;
        for p in 0..2 {
            let opp=reaches(&sp,1-p,777);let mass=opp.iter().sum::<f32>();
            for br in [false,true] {
                let eval=|s:&Solver| if br {s.traverse_br(0,p,&opp,Dealt::default())} else {s.traverse_avg(0,p,&opp,Dealt::default())};
                evaluation=evaluation.max(maximum(&eval(&iso),&eval(&plain))/mass);
                let quotient=eval(&iso);iso.use_isomorphism=false;
                quotient_evaluation=quotient_evaluation.max(maximum(&quotient,&eval(&iso))/mass);
                iso.use_isomorphism=true;
            }
        }
        println!("{board}: full arenas={full_bytes}, compact arenas={}, sweep CFV={cfv}, replay GPU CFV={gpu_replay}, immediate root={root}, trajectory CFV={trajectory_cfv}, root drift={drift}, avg/BR={evaluation}, same-policy quotient evaluation={quotient_evaluation}, root policy asymmetry={root_asymmetry}",gpu.arena_bytes());
        let asymmetry=policy_symmetry_error(&iso);
        println!("{board}: all-node average/current stabilizer asymmetry {asymmetry:?}; projected-vs-raw root policy sensitivity={}",maximum(&iso.average_strategy(0,&sp.tree.nodes[0]),&raw_host.average_strategy(0,&sp.tree.nodes[0])));
        if !(cfv<0.002 && root<0.002 && drift<0.01 && evaluation<0.002 && quotient_evaluation<0.0001 && asymmetry==(0.,0.)) {failures.push(board);}
    }
    assert!(failures.is_empty(),"Original equivalence gates failed on {failures:?}");
}

#[test]
fn symmetric_continuation_rejects_unsupported_inputs_without_mutation() {
    let sp=spot("KsQs2d");let mut s=host(&sp,true);
    let mut gpu=SymmetricContinuationGpu::new_with_budget(&s,budget(&sp)).unwrap();
    let r0=reaches(&sp,0,1);let r1=reaches(&sp,1,1);
    assert!(gpu.sweep(2,1,&r0,&r1).is_err());assert!(gpu.sweep(0,0,&r0,&r1).is_err());
    assert!(gpu.sweep(0,1,&[],&r1).is_err());
    for bad in [f32::NAN,f32::INFINITY,-1.] {
        let mut r=r0.clone();r[0]=bad;assert!(gpu.sweep(0,1,&r,&r1).is_err());
    }
    for q in 0..2 {
        let permutation=&sp.hand_perm[q][1];
        let i=permutation.iter().enumerate().find(|(i,j)|*i!=**j as usize).unwrap().0;
        let mut r=[r0.clone(),r1.clone()];r[q][i]+=0.1;
        assert!(gpu.sweep(0,1,&r[0],&r[1]).unwrap_err().contains("breaks suit symmetry"));
        r[q].fill(0.);r[q][i]=1e-30;
        assert!(gpu.sweep(0,1,&r[0],&r[1]).is_err());
    }
    gpu.sync_to_cpu(&mut s).unwrap();assert_eq!(s.iteration,0);
    // No invalid sweep uploaded weights or updated regrets/averages.
    for store in s.regrets.iter().chain(&s.strat) {
        if let solver::store::Store::F32(a)=store {assert!(a.as_slice().iter().all(|&x|x==0.));} else {panic!();}
    }
    let mut wrong=host(&spot("KsQs2d"),true);assert!(gpu.sync_to_cpu(&mut wrong).is_err());
    s.iteration=1;assert!(SymmetricContinuationGpu::new_with_budget(&s,budget(&sp)).is_err());s.iteration=0;
    s.locks.insert(0,vec![]);assert!(SymmetricContinuationGpu::new_with_budget(&s,budget(&sp)).is_err());s.locks.clear();
    s.use_isomorphism=false;assert!(SymmetricContinuationGpu::new_with_budget(&s,budget(&sp)).is_err());s.use_isomorphism=true;
    s.algo=Algorithm::Dcfr;assert!(SymmetricContinuationGpu::new_with_budget(&s,budget(&sp)).is_err());s.algo=Algorithm::CfrPlus;
    if let solver::store::Store::F32(a)=&mut s.regrets[0] {a.as_mut_slice()[0]=0.5;}
    assert!(SymmetricContinuationGpu::new_with_budget(&s,budget(&sp)).is_err());
}
