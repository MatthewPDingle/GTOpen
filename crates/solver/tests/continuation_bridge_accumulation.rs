#![cfg(feature = "preflop-research")]
use solver::{Algorithm,Solver,Spot,SpotConfig,TreeConfig,StreetSizing,parse_sizes,gpu::GpuSolver};
use std::sync::Arc;

#[test]
fn changing_own_reach_updates_gpu_average_like_cpu() {
    let sizing=StreetSizing {bet:parse_sizes("50 75").unwrap(),raise:parse_sizes("100").unwrap(),donk:vec![]};
    let spot=Arc::new(Spot::new(SpotConfig {board:"KhQd9d2c7s".into(),range_oop:"AA,KK,A5s,KQo,76s".into(),
        range_ip:"AA,QQ,AKo,JTs,88".into(),tree:TreeConfig {starting_pot:39.5,effective_stack:182.,
            rake_pct:0.04,rake_cap:6.,max_raises:1,oop:[sizing.clone(),sizing.clone(),sizing.clone()],
            ip:[sizing.clone(),sizing.clone(),sizing],..Default::default()}}).unwrap());
    let mut cpu=Solver::new(spot.clone());let mut host=Solver::new(spot.clone());
    for s in [&mut cpu,&mut host]{s.use_isomorphism=false;s.algo=Algorithm::CfrPlus;}
    let mut gpu=GpuSolver::new(&host).unwrap();let mut worst=0f32;
    for t in 1..=100 {
        for p in 0..2 {
            gpu.sync_to_cpu(&mut cpu).unwrap();
            let own:Vec<_>=spot.weights[p].iter().enumerate().map(|(i,w)|
                if t%5==0 {0.} else {w*(0.01+((i+t as usize)%13) as f32/13.)}).collect();
            let opp=spot.weights[1-p].clone();
            cpu.research_continuation_sweep(p,t,&own,&opp).unwrap();
            gpu.research_continuation_sweep(p,t,&own,&opp).unwrap();
            if p==0 {
                gpu.sync_to_cpu(&mut host).unwrap();let root=&spot.tree.nodes[0];
                // Compare immediately after the root owner's update, including
                // iterations when own reach vanishes but opponent reach does not.
                for (a,b) in cpu.average_strategy(0,root).iter().zip(host.average_strategy(0,root)){
                    worst=worst.max((a-b).abs());
                }
            }
        }
    }
    assert!(worst<0.00002,"root average discrepancy {worst}");
    println!("changing-own-reach average discrepancy={worst}");
}
