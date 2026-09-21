#![cfg(feature = "preflop-research")]
use solver::{Algorithm, Solver, Spot, SpotConfig, TreeConfig, StreetSizing, parse_sizes, store::Store};
use solver::gpu::{GpuSolver, PagedContinuationGpu, ContinuationWorkspace};
use std::sync::Arc;

fn host(board: &str, ranges: [&str; 2]) -> Solver {
    let size=StreetSizing {bet:parse_sizes("50").unwrap(),raise:vec![],donk:parse_sizes("50").unwrap()};
    let sp=Arc::new(Spot::new(SpotConfig {board:board.into(),range_oop:ranges[0].into(),range_ip:ranges[1].into(),
        tree:TreeConfig {starting_pot:39.5,effective_stack:80.,rake_pct:0.04,rake_cap:6.,max_raises:0,
            oop:[size.clone(),size.clone(),size.clone()],ip:[size.clone(),size.clone(),size],..Default::default()}}).unwrap());
    let mut s=Solver::new(sp);s.algo=Algorithm::CfrPlus;s.use_isomorphism=false;s
}
fn snapshot(s: &Solver) -> Vec<Vec<u32>> {
    s.regrets.iter().chain(&s.strat).map(|store| {
        let Store::F32(a)=store else {panic!()};a.as_slice().iter().map(|x|x.to_bits()).collect()
    }).collect()
}

#[test]
fn paging_preserves_resident_trajectories_and_rejects_invalid_inputs() {
    let mut hosts=vec![host("KsQs2s",["AA,AKs,KQo,88,76s","AA,QQ,AKo,QJs,99"]),
                       host("9c6d3h",["AA,KK,QQ,JJ,AQs,AJs,KQs,55,44","KK,QQ,AKs,AQo,98s,76s,65s"] )];
    let mut reference_hosts:Vec<_>=hosts.iter().map(|h| {
        let mut s=Solver::new(h.spot.clone());s.use_isomorphism=false;s.algo=Algorithm::CfrPlus;s
    }).collect();
    let mut reference:Vec<_>=reference_hosts.iter().map(|h|GpuSolver::new(h).unwrap()).collect();
    let mut pool=ContinuationWorkspace::default();
    let mut paged:Vec<_>=hosts.iter().map(|h|PagedContinuationGpu::new(h,&mut pool).unwrap()).collect();
    let before=snapshot(&hosts[0]);
    assert!(paged[0].sweep(&mut hosts[0],&mut pool,0,1,&[],&[]).is_err());
    assert_eq!(before,snapshot(&hosts[0]));
    for t in 1..=40 {for p in 0..2 {for b in 0..hosts.len() {
        let weights:[Vec<f32>;2]=std::array::from_fn(|q|hosts[b].spot.hands[q].iter().enumerate()
            .map(|(h,_)|if t%7==0 && q==p {0.}else{0.02+((h*7+t as usize*3+q*11)%23) as f32/23.}).collect());
        let expected=reference[b].research_continuation_sweep(p,t,&weights[p],&weights[1-p]).unwrap();
        let actual=paged[b].sweep(&mut hosts[b],&mut pool,p,t,&weights[p],&weights[1-p]).unwrap();
        assert_eq!(expected.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),actual.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),"CFVs board {b} player {p} t {t}");
        reference[b].sync_to_cpu(&mut reference_hosts[b]).unwrap();
        assert_eq!(snapshot(&hosts[b]),snapshot(&reference_hosts[b]),"arenas board {b} player {p} t {t}");
    }}}
    println!("bitwise paging matches: 160 alternating board/player sweeps; workspace={} bytes; transfers={} bytes",
        pool.bytes(),paged.iter().map(|g|g.transferred_bytes).sum::<u64>());
}
