use super::*;
use crate::game::SpotConfig;
use crate::tree::{Action, TreeConfig};

fn fixture(board: &str) -> Arc<Spot> {
    Arc::new(
        Spot::new(SpotConfig {
            board: board.into(),
            range_oop: "KhKd".into(),
            range_ip: "QhQd".into(),
            tree: TreeConfig {
                starting_pot: 55.0,
                effective_stack: 975.0,
                add_allin: true,
                ..TreeConfig::default()
            },
        })
        .unwrap(),
    )
}

fn take(spot: &Spot, idx: u32, choose: impl Fn(&Action) -> bool) -> u32 {
    let node = &spot.tree.nodes[idx as usize];
    let start = node.actions_start as usize;
    let a = spot.tree.actions[start..start + node.num_children as usize]
        .iter()
        .position(choose)
        .unwrap();
    spot.tree.children[node.children_start as usize + a]
}

fn has_action(spot: &Spot, idx: u32) -> bool {
    let node = &spot.tree.nodes[idx as usize];
    match node.kind {
        KIND_ACTION => true,
        KIND_CHANCE => {
            let start = node.children_start as usize;
            spot.tree.children[start..start + node.num_children as usize]
                .iter()
                .any(|&c| c != SENTINEL && has_action(spot, c))
        }
        _ => false,
    }
}

fn allin_runout(board: &str) {
    let spot = fixture(board);
    let jam = take(&spot, 0, |a| matches!(a, Action::Bet(_)));
    let runout = take(&spot, jam, |a| matches!(a, Action::Call(_)));
    assert_eq!(spot.tree.nodes[runout as usize].kind, KIND_CHANCE);
    for storage in [Storage::F32, Storage::Compressed] {
        let mut s = Solver::with_storage(spot.clone(), storage);
        s.use_isomorphism = false;
        if storage == Storage::F32 {
            for (idx, node) in spot.tree.nodes.iter().enumerate() {
                if node.kind == KIND_CHANCE {
                    assert_eq!(s.action_free_runout(node), !has_action(&spot, idx as u32));
                }
            }
        }
        let zero = vec![0.0; spot.hands[1].len()];
        let mut out = vec![0.0; spot.hands[0].len()];
        s.cfr(
            runout,
            0,
            &spot.weights[0],
            &zero,
            Dealt::default(),
            &Discounts::for_iteration(Algorithm::Dcfr, 1),
            &mut out,
        );
        let visits = s.traversal_visits.load(Ordering::Relaxed);
        println!("{board} {storage:?}: zero-reach all-in visits = {visits}");
        assert_eq!(out, vec![0.0; out.len()]);
        assert_eq!(
            visits, 1,
            "action-free runout descendants must not be visited"
        );

        // A live opponent still requires normal enumeration and the same CFVs
        // as the independent read-only average-strategy traversal.
        let reference = s.traverse_avg(runout, 0, &spot.weights[1], Dealt::default());
        s.traversal_visits.store(0, Ordering::Relaxed);
        out.fill(0.0);
        s.cfr(
            runout,
            0,
            &spot.weights[0],
            &spot.weights[1],
            Dealt::default(),
            &Discounts::for_iteration(Algorithm::Dcfr, 1),
            &mut out,
        );
        assert!(s.traversal_visits.load(Ordering::Relaxed) > 1);
        for (actual, expected) in out.iter().zip(reference) {
            assert!((*actual - expected).abs() < 1e-5);
        }
    }
}

#[test]
fn flop_zero_reach_allin_skips_both_runout_streets() {
    allin_runout("AdAc9h");
}

#[test]
fn turn_zero_reach_allin_skips_the_river_runout() {
    allin_runout("AdAc9h2c");
}

#[test]
fn zero_reach_betting_chance_keeps_own_averages() {
    for board in ["AdAc9h", "AdAc9h2c"] {
        let spot = fixture(board);
        let ip = take(&spot, 0, |a| *a == Action::Check);
        let chance = take(&spot, ip, |a| *a == Action::Check);
        let nd = &spot.tree.nodes[chance as usize];
        let child = spot.tree.children[nd.children_start as usize..][..nd.num_children as usize]
            .iter()
            .copied()
            .find(|&c| c != SENTINEL)
            .unwrap();
        assert_eq!(spot.tree.nodes[child as usize].kind, KIND_ACTION);
        let s = Solver::new(spot.clone());
        let zero = vec![0.0; spot.hands[1].len()];
        let mut out = vec![0.0; spot.hands[0].len()];
        s.cfr(
            chance,
            0,
            &spot.weights[0],
            &zero,
            Dealt::default(),
            &Discounts::for_iteration(Algorithm::Dcfr, 1),
            &mut out,
        );
        assert!(s.traversal_visits.load(Ordering::Relaxed) > 1);
        let mut total = 0.0;
        for (idx, n) in spot.tree.nodes.iter().enumerate() {
            if n.kind == KIND_ACTION && n.player == 0 {
                let mut sums = vec![0.0; n.num_children as usize * spot.hands[0].len()];
                unsafe {
                    s.strat[0].read_f32(idx as u32, n.data_offset, sums.len(), &mut sums);
                }
                total += sums.iter().sum::<f32>();
            }
        }
        assert!(
            total > 0.0,
            "betting chance descendants still need own averages"
        );
    }
}
