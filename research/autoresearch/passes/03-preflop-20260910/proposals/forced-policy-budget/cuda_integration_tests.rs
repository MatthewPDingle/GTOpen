// Append to gpu.rs. Real CUDA test; run only in the parent's exclusive GPU slot.
#[cfg(test)]
mod forced_budget_cuda_tests {
    use super::*;
    use crate::preflop::{BucketPolicy, PreflopConfig, SeatProfile, NUM_BUCKETS};

    fn cached_equity() -> Arc<crate::preflop::equity::EquityTable> {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let bytes = std::fs::read(path).expect("existing equity cache required");
        assert_eq!(bytes.len(), 4 + NUM_CLASSES * NUM_CLASSES * 4);
        let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
        Arc::new(crate::preflop::equity::EquityTable::load_or_build(
            path, samples,
        ))
    }

    fn modeled(
        cfg: PreflopConfig,
        eq: Arc<crate::preflop::equity::EquityTable>,
        model: &str,
    ) -> PreflopSolver {
        let mut s = PreflopSolver::new(cfg, eq).unwrap();
        s.set_multiway_equity_model(model).unwrap();
        let policy: BucketPolicy = serde_json::from_value(serde_json::json!({
            "call":vec![0.3;NUM_CLASSES],"raise":vec![0.4;NUM_CLASSES],
            "jam":vec![0.1;NUM_CLASSES],"raise_size":"max"
        }))
        .unwrap();
        let profiles = s
            .cfg
            .positions
            .iter()
            .map(|position| {
                (position != "BTN").then(|| SeatProfile {
                    name: "GPU budget test".into(),
                    buckets: vec![Some(policy.clone()); NUM_BUCKETS],
                    vs_raise_bands: None,
                    limp_defense: None,
                    postflop: None,
                    response: None,
                })
            })
            .collect();
        s.set_table(vec![false; s.n], profiles).unwrap();
        s
    }

    // Find a tiny real tree whose forced payload crosses an integer-MB boundary.
    // Constructor budgets are whole MB; do not mock or perturb the byte planner.
    fn boundary_fixture(eq: Arc<crate::preflop::equity::EquityTable>) -> (PreflopConfig, u64) {
        for opens in [vec![2.0], vec![2.0, 3.0], vec![2.0, 3.0, 4.0]] {
            for max_raises in [2, 3] {
                let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
                    "positions":["CO","BTN","SB","BB"],"posts":[0,0,0.5,1],
                    "stack":12,"limp":true,"open_raises":opens,"raise_mults":[2,3],
                    "max_raises":max_raises,"add_allin":true,"realization":"raw"
                }))
                .unwrap();
                let s = modeled(cfg.clone(), eq.clone(), "legacy_product");
                assert!(s.nodes.len() < 250_000, "budget test must remain small");
                let base = minimum_vram_mb(&s, ValuePlan::build(&s).blocks);
                let elements = forced_policy_elements(&s).unwrap();
                let need = base + forced_storage_bytes(elements).unwrap() as f64 / 1e6;
                let bad_budget = base.ceil() as u64;
                if (bad_budget as f64) < need {
                    return (cfg, bad_budget);
                }
            }
        }
        panic!("no small real fixture crossed a whole-MB forced-payload boundary");
    }

    #[test]
    fn real_cuda_forced_allocation_and_budget_refusal_legacy_and_coupled() {
        let eq = cached_equity();
        let (cfg, bad_budget) = boundary_fixture(eq.clone());
        for model in ["legacy_product", "coupled_deck_v1"] {
            let mut s = modeled(cfg.clone(), eq.clone(), model);
            let expected_elements: usize = s
                .nodes
                .iter()
                .filter(|nd| nd.kind == KIND_ACTION && s.cfg.positions[nd.actor as usize] != "BTN")
                .map(|nd| nd.actions.len() * NUM_CLASSES)
                .sum();
            assert_eq!(forced_policy_elements(&s).unwrap(), expected_elements);
            let expected_bytes = expected_elements * std::mem::size_of::<f32>();
            assert_eq!(
                forced_storage_bytes(expected_elements).unwrap(),
                expected_bytes
            );
            assert!(expected_bytes > 0);
            let estimate = vram_estimate_mb(&s);
            assert!(
                estimate < 1000.0,
                "tiny fixture must fit below 1 GB estimate"
            );
            let good_budget = estimate.ceil() as u64 + 1;
            let mut gpu = PreflopGpu::new(&s, good_budget).expect("real modeled GPU allocation");
            assert_eq!(
                gpu.d_forced.len() * std::mem::size_of::<f32>(),
                expected_bytes
            );
            assert_eq!(gpu.use_multiway != 0, model == "coupled_deck_v1");
            let uploaded = gpu.stream.clone_dtoh(&gpu.d_forced).unwrap();
            let expected: Vec<f32> = s
                .nodes
                .iter()
                .enumerate()
                .filter(|(_, nd)| nd.kind == KIND_ACTION)
                .flat_map(|(i, _)| s.forced_sigma(i).unwrap_or_default())
                .collect();
            assert_eq!(uploaded.len(), expected.len());
            for (a, b) in uploaded.iter().zip(&expected) {
                assert_eq!(a.to_bits(), b.to_bits());
            }
            gpu.iterate(&mut s)
                .expect("materialized forced policies must execute");
            drop(gpu);

            // Base alone fits, but base+forced does not. Both models must fail
            // at the explicit forced reservation, not a later CUDA OOM/CDF check.
            let base = minimum_vram_mb(&s, ValuePlan::build(&s).blocks);
            assert!(base <= bad_budget as f64);
            assert!(base + expected_bytes as f64 / 1e6 > bad_budget as f64);
            let err = match PreflopGpu::new(&s, bad_budget) {
                Err(err) => err,
                Ok(_) => panic!("constructor accepted a budget omitting forced policy storage"),
            };
            assert!(err.contains("forced policies"), "wrong refusal: {err}");
            eprintln!(
                "FORCED_BUDGET_CUDA {}",
                serde_json::json!({
                    "model":model,"nodes":s.nodes.len(),"forced_elements":expected_elements,
                    "actual_forced_bytes":expected_bytes,"good_budget_mb":good_budget,
                    "base_mb":base,"refused_budget_mb":bad_budget,"iteration_executed":s.iteration
                })
            );
        }
    }
}
