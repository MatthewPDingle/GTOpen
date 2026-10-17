//! Bounded reductions of SergMartidi's issue #1 deep-SPR all-in configuration.
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Solver, Spot, SpotConfig, Storage};
use std::sync::Arc;

#[test]
fn zero_opponent_reach_still_accumulates_own_average_strategy() {
    use solver::tree::Action;
    let street = StreetSizing {
        bet: parse_sizes("50").unwrap(),
        raise: vec![],
        donk: vec![],
    };
    let spot = Arc::new(
        Spot::new(SpotConfig {
            board: "AdAc9h2c3h".into(),
            range_oop: "KK".into(),
            range_ip: "22".into(),
            tree: TreeConfig {
                starting_pot: 55.0,
                effective_stack: 975.0,
                oop: [street.clone(), street.clone(), street.clone()],
                ip: [street.clone(), street.clone(), street],
                ..TreeConfig::default()
            },
        })
        .unwrap(),
    );
    let mut s = Solver::with_storage(spot.clone(), Storage::F32);
    let root = &spot.tree.nodes[0];
    let check = spot.tree.actions[root.actions_start as usize..][..root.num_children as usize]
        .iter()
        .position(|a| *a == Action::Check)
        .unwrap();
    let ip_idx = spot.tree.children[root.children_start as usize + check];
    let ip = &spot.tree.nodes[ip_idx as usize];
    let bet = spot.tree.actions[ip.actions_start as usize..][..ip.num_children as usize]
        .iter()
        .position(|a| matches!(a, Action::Bet(_)))
        .unwrap();
    let response_idx = spot.tree.children[ip.children_start as usize + bet];
    // Both players currently check. OOP's response to IP's zero-frequency
    // bet still needs OOP's own-reach average, despite zero opponent reach.
    for (idx, node, p) in [(0, root, 0), (ip_idx, ip, 1)] {
        let nh = spot.hands[p].len();
        let mut r = vec![-1.0; node.num_children as usize * nh];
        let a = spot.tree.actions[node.actions_start as usize..][..node.num_children as usize]
            .iter()
            .position(|a| *a == Action::Check)
            .unwrap();
        r[a * nh..(a + 1) * nh].fill(1.0);
        unsafe {
            s.regrets[p].write_f32(idx, node.data_offset, r.len(), &r);
        }
    }
    s.iterate();
    let response = &spot.tree.nodes[response_idx as usize];
    let mut sums = vec![0.0; response.num_children as usize * spot.hands[0].len()];
    unsafe {
        s.strat[0].read_f32(response_idx, response.data_offset, sums.len(), &mut sums);
    }
    for sum in sums {
        assert!(sum > 0.0, "own average was skipped at zero opponent reach");
    }
}

#[test]
fn deep_allin_compression_does_not_discard_small_regret_updates() {
    let street = StreetSizing {
        bet: parse_sizes("50").unwrap(),
        raise: parse_sizes("100").unwrap(),
        donk: vec![],
    };
    let range = "22+,A2s+,K9s+,Q9s+,J9s+,T9s,ATo+,KTo+,QJo";
    let spot = Arc::new(
        Spot::new(SpotConfig {
            board: "AdAc9h2c3h".into(),
            range_oop: range.into(),
            range_ip: range.into(),
            tree: TreeConfig {
                starting_pot: 55.0,
                effective_stack: 975.0,
                oop: [street.clone(), street.clone(), street.clone()],
                ip: [street.clone(), street.clone(), street],
                add_allin: true,
                ..TreeConfig::default()
            },
        })
        .unwrap(),
    );
    let mut plain = Solver::with_storage(spot.clone(), Storage::F32);
    let mut compressed = Solver::with_storage(spot, Storage::Compressed);
    for _ in 0..2000 {
        plain.iterate();
        compressed.iterate();
    }
    let reference = plain.exploitability() / 55.0 * 100.0;
    let actual = compressed.exploitability() / 55.0 * 100.0;
    assert!(reference < 0.03, "reference {reference}% pot");
    assert!(
        actual < 0.03,
        "compressed {actual}% pot vs f32 {reference}%"
    );
    println!("deep all-in river: f32 {reference}% pot, compressed {actual}% pot");
}
