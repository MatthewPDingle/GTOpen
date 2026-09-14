use solver::preflop::{equity::EquityTable, estimate_tree, PreflopConfig, PreflopSolver};
use std::sync::{Arc, OnceLock};
fn eq() -> Arc<EquityTable> {
    static TABLE: OnceLock<Arc<EquityTable>> = OnceLock::new();
    TABLE
        .get_or_init(|| {
            let p = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
            let b = std::fs::read(p).unwrap();
            Arc::new(EquityTable::load_or_build(
                p,
                u32::from_le_bytes(b[..4].try_into().unwrap()),
            ))
        })
        .clone()
}
fn config(n: usize) -> PreflopConfig {
    let mut posts = vec![0.; n];
    posts[0] = 2.;
    posts[n - 2] = 0.5;
    posts[n - 1] = 1.;
    let mut positions: Vec<_> = (0..n).map(|i| format!("P{i}")).collect();
    positions[0] = "UTG".into();
    positions[n - 2] = "SB".into();
    positions[n - 1] = "BB".into();
    serde_json::from_value(serde_json::json!({"positions":positions,"posts":posts,"utg_straddle":true,"stack":12,
  "limp":true,"open_raises":[4],"raise_mults":[2],"max_raises":1,"add_allin":false,"realization":"raw"})).unwrap()
}
fn step(s: &PreflopSolver, path: &mut Vec<usize>, kind: &str, to: f64) {
    let v = s.node_view(path).unwrap();
    let action = v
        .actions
        .iter()
        .position(|a| a.kind == kind && (kind == "fold" || (a.to - to).abs() < 1e-9))
        .unwrap_or_else(|| panic!("missing {kind} {to}: {:?}", v.actions));
    path.push(action);
}
#[test]
fn action_order_straddler_option_and_accounting() {
    for n in [3, 4, 6, 9] {
        let mut cfg = config(n);
        cfg.ante = 0.1;
        let s = PreflopSolver::new(cfg, eq()).unwrap();
        let mut path = vec![];
        for seat in 1..n {
            let v = s.node_view(&path).unwrap();
            assert_eq!(v.actor, Some(seat));
            assert_eq!(s.nodes[s.walk(&path).unwrap().0].raises, 0);
            step(&s, &mut path, "call", 2.);
        }
        let v = s.node_view(&path).unwrap();
        assert_eq!(v.actor, Some(0));
        assert_eq!(s.nodes[s.walk(&path).unwrap().0].raises, 0);
        assert!(v.actions.iter().any(|a| a.kind == "check"));
        assert!(v.actions.iter().any(|a| a.kind == "raise" && a.to == 4.));
        assert!(!v.actions.iter().any(|a| a.kind == "fold"));
        step(&s, &mut path, "check", 2.);
        let v = s.node_view(&path).unwrap();
        assert_eq!(v.kind, "pot_share");
        assert!((v.pot - n as f64 * 2.1).abs() < 1e-6);
        assert_eq!(
            s.postflop_order(),
            (n - 2..n).chain(0..n - 2).collect::<Vec<_>>()
        );
    }
}
#[test]
fn everyone_folds_straddler_wins_without_a_decision() {
    let s = PreflopSolver::new(config(4), eq()).unwrap();
    let mut path = vec![];
    for _ in 1..4 {
        step(&s, &mut path, "fold", 0.);
    }
    let v = s.node_view(&path).unwrap();
    assert_eq!(v.kind, "fold_win");
    assert_eq!(s.nodes[s.walk(&path).unwrap().0].winner, 0);
    assert_eq!(v.pot, 3.5);
}
#[test]
fn straddle_raise_reopens_action_and_does_not_consume_raise_cap() {
    let mut cfg = config(4);
    cfg.max_raises = 2;
    cfg.raise_mults = vec![1.1];
    let s = PreflopSolver::new(cfg, eq()).unwrap();
    let mut path = vec![];
    for _ in 1..4 {
        step(&s, &mut path, "call", 2.);
    }
    step(&s, &mut path, "raise", 4.);
    let v = s.node_view(&path).unwrap();
    assert_eq!(v.actor, Some(1));
    assert_eq!(s.nodes[s.walk(&path).unwrap().0].raises, 1);
    assert!(v.actions.iter().any(|a| a.kind == "raise" && a.to == 6.));
    step(&s, &mut path, "raise", 6.);
    assert_eq!(s.nodes[s.walk(&path).unwrap().0].raises, 2);
    for seat in [2, 3, 0] {
        assert_eq!(s.node_view(&path).unwrap().actor, Some(seat));
        step(&s, &mut path, "call", 6.);
    }
    assert_eq!(s.node_view(&path).unwrap().kind, "pot_share");
}
#[test]
fn postflop_export_keeps_physical_position_and_original_bb() {
    let s = PreflopSolver::new(config(4), eq()).unwrap();
    let mut path = vec![];
    step(&s, &mut path, "fold", 0.);
    step(&s, &mut path, "call", 2.);
    step(&s, &mut path, "fold", 0.);
    step(&s, &mut path, "check", 2.);
    let ex = s.export_spot(&path).unwrap();
    assert_eq!(ex.oop_pos, "SB");
    assert_eq!(ex.ip_pos, "UTG");
    assert_eq!(ex.pot_bb, 5.);
    assert_eq!(ex.eff_stack_bb, 10.);
}
#[test]
fn validates_straddle_layout_and_minimums() {
    let mut too_small = config(4);
    too_small.posts[0] = 1.5;
    let mut extra_post = config(4);
    extra_post.posts[1] = 0.5;
    let mut reversed_blinds = config(4);
    reversed_blinds.posts[2] = 1.5;
    let mut nonfinite = config(4);
    nonfinite.posts[0] = f64::NAN;
    for cfg in [config(2), too_small, extra_post, reversed_blinds, nonfinite] {
        assert!(estimate_tree(&cfg).is_err());
    }
    let mut cfg = config(4);
    cfg.open_raises = vec![3.];
    assert!(estimate_tree(&cfg).unwrap_err().contains("at least 4"));
    cfg.open_raises = vec![4.];
    cfg.open_raises_by_seat = Some(vec![vec![], vec![3.], vec![], vec![]]);
    assert!(estimate_tree(&cfg).is_err());
    cfg.open_raises_by_seat = None;
    cfg.posts[1] = 1.;
    assert!(estimate_tree(&cfg).is_err());
    cfg.posts[1] = 0.;
    cfg.stack = 2.;
    assert!(estimate_tree(&cfg).is_err());
    cfg.stack = 3.;
    cfg.open_raises = vec![3.];
    let s = PreflopSolver::new(cfg, eq()).unwrap();
    assert!(s
        .node_view(&[])
        .unwrap()
        .actions
        .iter()
        .any(|a| a.kind == "jam" && a.to == 3.));
}
#[test]
fn estimator_agrees_and_unstraddled_defaults_keep_order() {
    let cfg = config(4);
    let estimate = estimate_tree(&cfg).unwrap();
    let s = PreflopSolver::new(cfg.clone(), eq()).unwrap();
    assert_eq!(estimate.nodes, s.nodes.len() as u64);
    let mut json = serde_json::to_value(cfg).unwrap();
    json.as_object_mut().unwrap().remove("utg_straddle");
    json["posts"][0] = 0.into();
    let old: PreflopConfig = serde_json::from_value(json).unwrap();
    assert!(!old.utg_straddle);
    assert!(serde_json::to_value(&old)
        .unwrap()
        .get("utg_straddle")
        .is_none());
    let s = PreflopSolver::new(old, eq()).unwrap();
    assert_eq!(s.node_view(&[]).unwrap().actor, Some(0));
}
#[test]
fn versioned_save_reload_preserves_tree_and_continuation() {
    let path = std::env::temp_dir().join(format!("gtopen-straddle-{}.gtop", std::process::id()));
    let mut s = PreflopSolver::new(config(3), eq()).unwrap();
    s.iterate();
    s.save_game(path.to_str().unwrap()).unwrap();
    let bytes = std::fs::read(&path).unwrap();
    assert!(bytes.starts_with(b"GTOPREFLOP3\n"));
    let mut loaded = PreflopSolver::load_game(path.to_str().unwrap(), eq()).unwrap();
    assert!(loaded.cfg.utg_straddle);
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    assert_eq!(loaded.node_view(&[]).unwrap().actor, Some(1));
    s.iterate();
    loaded.iterate();
    assert_eq!(s.arena_snapshot(), loaded.arena_snapshot());
    let mut bad = bytes;
    bad[10] = b'2';
    std::fs::write(&path, bad).unwrap();
    assert!(PreflopSolver::load_game(path.to_str().unwrap(), eq())
        .err()
        .unwrap()
        .contains("v3"));
    std::fs::remove_file(path).unwrap();
}
#[cfg(feature = "gpu")]
#[test]
fn gpu_selected_and_ordinary_paths_agree_with_rotated_actor() {
    use solver::preflop::gpu::PreflopGpu;
    let mut expected = None;
    for optimized in [false, true] {
        let mut s = PreflopSolver::new(config(4), eq()).unwrap();
        let mut gpu = if optimized {
            PreflopGpu::new_throughput(&s, 2000).unwrap().0
        } else {
            PreflopGpu::new(&s, 2000).unwrap()
        };
        let mut rounds = vec![];
        for _ in 0..3 {
            gpu.iterate(&mut s).unwrap();
            let metrics = gpu.gaps_and_evs().unwrap();
            gpu.sync_to_cpu(&mut s).unwrap();
            rounds.push((s.arena_snapshot(), metrics));
        }
        if let Some(ref expected) = expected {
            assert_eq!(&rounds, expected);
        } else {
            expected = Some(rounds);
        }
    }
}

#[test]
fn historical_models_keep_physical_roles_and_distinguish_paid_calls_from_checks() {
    use solver::preflop::{archetypes, evidence::generated_evidence, BucketPolicy};
    let mut s = PreflopSolver::new(config(4), eq()).unwrap();
    s.iterate();
    let policy = |call, raise| BucketPolicy {
        call: vec![call; 169],
        raise: vec![raise; 169],
        jam: vec![0.; 169],
        raise_size: "min".into(),
        raise_sizes: vec![],
        raise_multiples: vec![],
    };
    let rows:Vec<_>=[1,0,-1,-2].into_iter().map(|role|serde_json::json!({
  "players":4,"role":role,"open_raise":if role==-2{0.}else{20.},"open_limp":if role==-2{100.}else{10.},
  "iso_raise":20,"limp_behind":30,"opening":if role==-2{policy(1.,0.)}else{policy(0.1,0.2)},
  "responses":{"limps_paid_1":0,"limps_paid_2":0,"limps_paid_3":0,"limps_free_1":1,"limps_free_2":1,"limps_free_3":1}
 })).collect();
    let mut stats = archetypes()[3].1.clone();
    stats.open_raise = Some(20.);
    stats.open_limp = Some(10.);
    stats.dataset = Some(
        serde_json::from_value(
            serde_json::json!({"site":"Fixture","min_players":4,"max_players":4,
  "ante":false,"small_blind_bb":0.5,"scope":"unstraddled fixture","empirical_opening":true,
  "rows":rows,"response_policies":[policy(0.3,0.4),policy(0.8,0.2)]}),
        )
        .unwrap(),
    );
    let d = stats.dataset.as_ref().unwrap();
    for (seat, role) in [1, 0, -1, -2].into_iter().enumerate() {
        assert_eq!(d.resolve(&s.cfg, seat).unwrap().role, role);
    }
    let profiles: Vec<_> = (0..4)
        .map(|seat| Some(s.generate_profile(seat, &stats, "transferred").unwrap().0))
        .collect();
    let utg = profiles[0].as_ref().unwrap();
    let btn = profiles[1].as_ref().unwrap();
    let bb = profiles[3].as_ref().unwrap();
    let evidence = generated_evidence(&s.cfg, 1, btn);
    assert_eq!(evidence["unopened"].kind, "extrapolated");
    assert!(evidence["unopened"]
        .details
        .iter()
        .any(|x| x.contains("straddle")));
    assert_eq!(
        generated_evidence(&s.cfg, 0, utg)["unopened"].kind,
        "unavailable"
    );
    assert_eq!(
        generated_evidence(&s.cfg, 3, bb)["unopened"].kind,
        "stat_derived"
    );
    assert!(bb.buckets[0]
        .as_ref()
        .unwrap()
        .call
        .iter()
        .any(|&c| c < 0.5));
    s.set_table(vec![false; 4], profiles).unwrap();
    let mut path = vec![];
    step(&s, &mut path, "call", 2.);
    step(&s, &mut path, "fold", 0.);
    let bb_view = s.node_view(&path).unwrap();
    let call = bb_view
        .actions
        .iter()
        .position(|a| a.kind == "call")
        .unwrap();
    assert!((bb_view.strategy.as_ref().unwrap()[call * 169] - 0.3).abs() < 1e-6);
    step(&s, &mut path, "call", 2.);
    let utg_view = s.node_view(&path).unwrap();
    let check = utg_view
        .actions
        .iter()
        .position(|a| a.kind == "check")
        .unwrap();
    assert!((utg_view.strategy.as_ref().unwrap()[check * 169] - 0.8).abs() < 1e-6);
}
