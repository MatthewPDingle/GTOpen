#![cfg(feature = "preflop-research")]
use solver::{Algorithm, Solver, Spot, SpotConfig, TreeConfig, StreetSizing, parse_sizes};
use solver::gpu::GpuSolver;
use std::sync::Arc;

#[test]
fn externally_reached_gpu_sweeps_match_cpu_on_changing_ranges() {
    let sizing = StreetSizing { bet: parse_sizes("50 75").unwrap(),
        raise: parse_sizes("100").unwrap(), donk: parse_sizes("50").unwrap() };
    // Turn fixture exercises future-card chance as well as betting and blockers.
    let spot = Arc::new(Spot::new(SpotConfig {
        board: "KhQd9d2c".into(), range_oop: "AA,AKs,A5s,KQo,QJs,99,55,76s".into(),
        range_ip: "AA,KK,QQ,AKo,AQs,88".into(),
        tree: TreeConfig { starting_pot: 39.5, effective_stack: 182.,
            rake_pct: 0.04, rake_cap: 6., max_raises: 1,
            oop: [sizing.clone(),sizing.clone(),sizing.clone()],
            ip: [sizing.clone(),sizing.clone(),sizing], ..Default::default() },
    }).unwrap());
    let mut cpu=Solver::new(spot.clone()); let mut host=Solver::new(spot.clone());
    for s in [&mut cpu,&mut host] {s.algo=Algorithm::CfrPlus;s.use_isomorphism=false;}
    let mut gpu=GpuSolver::new(&host).unwrap();
    let mut worst=0f32;
    for t in 1..=120 {
        for p in 0..2 {
            // Compare the same starting policy each sweep. Long independent
            // f32 trajectories can separate near indifferent decisions.
            gpu.sync_to_cpu(&mut cpu).unwrap();
            let reach=|q:usize| spot.weights[q].iter().enumerate().map(|(i,w)|
                w*(0.1+0.9*((i*7+t as usize*3+q*11)%23) as f32/22.)).collect::<Vec<_>>();
            let own=reach(p);let opp=reach(1-p);
            let a=cpu.research_continuation_sweep(p,t,&own,&opp).unwrap();
            let b=gpu.research_continuation_sweep(p,t,&own,&opp).unwrap();
            let mass=opp.iter().sum::<f32>();
            for (x,y) in a.iter().zip(&b) {worst=worst.max((x-y).abs()/mass);}
        }
    }
    assert!(worst<0.002,"maximum per-opponent-mass CFV error {worst}");
    gpu.sync_to_cpu(&mut host).unwrap();
    let mut worst_policy=0f32;
    // Check the reached root. CPU intentionally prunes zero-opponent-reach
    // descendants without discounting their averages; GPU discounts them.
    for (i,n) in spot.tree.nodes.iter().enumerate().take(1) {
        for (a,b) in cpu.average_strategy(i as u32,n).iter().zip(host.average_strategy(i as u32,n)) {
            worst_policy=worst_policy.max((a-b).abs());
        }
    }
    assert!(worst_policy<0.002,"policy error {worst_policy}");
    assert!(gpu.research_continuation_sweep(0,121,&[f32::NAN],&[]).is_err());
    assert!(cpu.research_continuation_sweep(0,121,&[f32::NAN],&[]).is_err());
    println!("bridge CFV error={worst}, policy error={worst_policy}");
}
