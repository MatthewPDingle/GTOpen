    fn assert_rule_matches_old(table: &CoupledDeck, opponents: &[Vec<f32>], label: &str) {
        let actual = table.equities(opponents);
        let expected = table.old_five_point_equities(opponents);
        for h in 0..NUM_CLASSES {
            assert!(actual[h].is_finite() && (actual[h] - expected[h]).abs() < 2e-12,
                "{label}, opponents {}, hand {h}: {} vs {}", opponents.len(), actual[h], expected[h]);
        }
    }

    // Exact dyadic normalization avoids f32 normalization error obscuring the
    // quadrature comparison. Every dense hand has positive probability.
    fn quadrature_test_range(q: usize, sparse: bool) -> Vec<f32> {
        let mut dist = vec![0.0; NUM_CLASSES];
        if sparse {
            dist[(q * 17) % NUM_CLASSES] = 0.5;
            dist[(q * 17 + 53) % NUM_CLASSES] = 0.25;
            dist[(q * 17 + 107) % NUM_CLASSES] = 0.25;
        } else {
            for i in 0..NUM_CLASSES {
                dist[(i + q * 17) % NUM_CLASSES] = if i < 87 { 2.0 / 256.0 } else { 1.0 / 256.0 };
            }
        }
        dist
    }

    #[test]
    fn smallest_quadrature_matches_original_five_points_for_all_counts() {
        let table = CoupledDeck::shared();
        for n in 0..=8 {
            for sparse in [false, true] {
                let opponents: Vec<Vec<f32>> = (0..n).map(|q| quadrature_test_range(q, sparse)).collect();
                assert_rule_matches_old(&table, &opponents, if sparse { "sparse" } else { "dense" });
            }
            // Every opponent holds the same class; its corresponding hero
            // class ties on every particle and must receive 1/(n+1).
            let mut same = vec![0.0; NUM_CLASSES];
            same[168] = 1.0;
            let opponents = vec![same; n];
            assert_rule_matches_old(&table, &opponents, "same-class ties");
            assert!((table.equities(&opponents)[168] - 1.0 / (n + 1) as f64).abs() < 2e-12);
        }
    }

    #[test]
    fn smallest_quadrature_handles_all_tied_and_grouped_rank_particles() {
        // Synthetic rank tables isolate tie splitting from card generation.
        // Keep all 1024 particles and all169 hero classes; do not use a reduced
        // sample test that might conceal a final averaging regression.
        for group_width in [NUM_CLASSES, 13] {
            let mut table = CoupledDeck { order: vec![], lower: vec![], upper: vec![] };
            for _ in 0..SAMPLES {
                for h in 0..NUM_CLASSES {
                    table.order.push(h as u32);
                    table.lower.push((h / group_width * group_width) as u32);
                    table.upper.push(((h / group_width + 1) * group_width).min(NUM_CLASSES) as u32);
                }
            }
            for n in 0..=8 {
                let opponents: Vec<Vec<f32>> = (0..n).map(|q| quadrature_test_range(q, q % 2 == 0)).collect();
                assert_rule_matches_old(&table, &opponents, "synthetic tie groups");
                if group_width == NUM_CLASSES {
                    let expected = 1.0 / (n + 1) as f64;
                    assert!(table.equities(&opponents).iter().all(|&x| (x - expected).abs() < 2e-12));
                }
            }
        }
    }
