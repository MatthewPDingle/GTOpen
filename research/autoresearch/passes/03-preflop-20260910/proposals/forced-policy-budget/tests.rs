// Append to gpu.rs after applying the proposal. Host-only tests; no CUDA calls.
#[cfg(test)]
mod forced_budget_tests {
    use super::*;
    use crate::preflop::{BucketPolicy, PreflopConfig, SeatProfile, NUM_BUCKETS};

    fn fixture() -> PreflopSolver {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let cache = std::fs::read(path).expect("existing cache required");
        assert_eq!(cache.len(), 4 + NUM_CLASSES * NUM_CLASSES * 4);
        let samples = u32::from_le_bytes(cache[..4].try_into().unwrap());
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(
            path, samples,
        ));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":6,
            "limp":true,"open_raises":[2],"raise_mults":[2],"max_raises":2,
            "add_allin":true,"realization":"raw"
        }))
        .unwrap();
        PreflopSolver::new(cfg, eq).unwrap()
    }
    fn policy() -> BucketPolicy {
        serde_json::from_value(serde_json::json!({
            "call":vec![0.3;NUM_CLASSES],"raise":vec![0.4;NUM_CLASSES],
            "jam":vec![0.1;NUM_CLASSES],"raise_size":"max"
        }))
        .unwrap()
    }
    fn profile() -> SeatProfile {
        SeatProfile {
            name: "budget fixture".into(),
            buckets: vec![Some(policy()); NUM_BUCKETS],
            vs_raise_bands: None,
            limp_defense: None,
            postflop: None,
            response: None,
        }
    }

    #[test]
    fn forced_count_respects_profiles_frozen_hero_and_point_lock_precedence() {
        let mut s = fixture();
        let empty_estimate = vram_estimate_mb(&s);
        assert_eq!(forced_policy_elements(&s).unwrap(), 0);
        assert_eq!(forced_storage_bytes(0).unwrap(), 4); // CUDA placeholder
        s.seat_frozen[0] = true;
        assert_eq!(forced_policy_elements(&s).unwrap(), 0); // sums, not forced buffer
        s.seat_profiles[0] = Some(profile());
        let expected: usize = s
            .nodes
            .iter()
            .filter(|n| n.kind == KIND_ACTION && n.actor == 0)
            .map(|n| n.actions.len() * NUM_CLASSES)
            .sum();
        assert!(expected > 0);
        assert_eq!(forced_policy_elements(&s).unwrap(), expected); // profile wins over frozen
        assert!(
            (vram_estimate_mb(&s) - empty_estimate - (expected * 4 - 4) as f64 / 1e6).abs() < 1e-9
        );
        s.hero = Some(0); // direct state suffices for read-only route/count inspection
        assert_eq!(forced_policy_elements(&s).unwrap(), 0); // hero exempt from own profile
        s.lock_point(&[], Some(policy())).unwrap();
        let root_elements = s.nodes[0].actions.len() * NUM_CLASSES;
        assert_eq!(forced_policy_elements(&s).unwrap(), root_elements); // point lock beats hero
        s.hero = None;
        assert_eq!(forced_policy_elements(&s).unwrap(), expected); // root isn't double counted
    }

    #[test]
    fn adaptive_nodes_are_not_charged_as_fixed_policies() {
        let mut s = fixture();
        let mut p = profile();
        p.response =
            Some(serde_json::from_value(serde_json::json!({"adaptive_from":0.25})).unwrap());
        s.seat_profiles[0] = Some(p);
        let expected: usize = s
            .nodes
            .iter()
            .enumerate()
            .filter(|(_, n)| n.kind == KIND_ACTION && n.actor == 0)
            .filter(|(i, n)| {
                n.bucket < crate::preflop::BUCKET_VS_RAISE
                    || s.faced_to(*i) + 1e-9 < s.cfg.stack * 0.25
            })
            .map(|(_, n)| n.actions.len() * NUM_CLASSES)
            .sum();
        let all: usize = s
            .nodes
            .iter()
            .filter(|n| n.kind == KIND_ACTION && n.actor == 0)
            .map(|n| n.actions.len() * NUM_CLASSES)
            .sum();
        assert!(expected > 0 && expected < all);
        assert_eq!(forced_policy_elements(&s).unwrap(), expected);
    }

    #[test]
    fn forced_reservation_rejects_over_budget_legacy_and_overflow() {
        assert_eq!(reserve_forced_vram_mb(100.0, 250_000, 101).unwrap(), 101.0);
        assert!(reserve_forced_vram_mb(100.0, 250_001, 101).is_err());
        assert!(reserve_forced_vram_mb(100.0, 0, 100).is_err());
        assert!(forced_storage_bytes(usize::MAX).is_err());
        assert!(reserve_forced_vram_mb(f64::INFINITY, 1, u64::MAX).is_err());
    }

    #[test]
    fn forced_reservation_changes_batch_and_preserves_minimum_fit_fallback() {
        let slots = 1000;
        let particle = slots * (NUM_CLASSES + 1) * 4;
        let normalized = slots * NUM_CLASSES * 4;
        let available = normalized + 2 * particle;
        assert_eq!(
            multiway_batch_plan(available, slots)
                .unwrap()
                .unwrap()
                .batch,
            2
        );
        let forced = forced_storage_bytes(particle / 4).unwrap();
        let reduced = multiway_batch_plan(available - forced, slots)
            .unwrap()
            .unwrap();
        assert_eq!(reduced.batch, 1);
        assert_eq!(reduced.normalized_bytes, normalized);
        let direct = multiway_batch_plan(
            particle + normalized - forced_storage_bytes(1).unwrap(),
            slots,
        )
        .unwrap()
        .unwrap();
        assert_eq!(direct.batch, 1);
        assert_eq!(direct.normalized_bytes, 0);
        assert!(
            multiway_batch_plan(particle - forced_storage_bytes(1).unwrap(), slots)
                .unwrap()
                .is_none()
        );
    }
}
