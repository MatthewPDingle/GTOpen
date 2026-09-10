//! A fixed, pot-conserving latent showdown game for 3+ live players.
//!
//! Classes share a random deck ordering, but each removes its own sampled hole
//! cards before taking the board. This couples hand strengths without the old
//! independent heads-up product. It is NOT exact compatible-card dealing:
//! overlapping narrow ranges remain a material source of card-removal error.
use super::equity::{class_index, NUM_CLASSES};
use crate::evaluator::evaluate7;
use std::sync::{Arc, OnceLock};

pub const SAMPLES: usize = 1024;
pub const MODEL: &str = "coupled_deck_v1";
pub const QUAD_T: [f64; 5] = [
    0.046910077030668,
    0.230765344947158,
    0.5,
    0.769234655052842,
    0.953089922969332,
];
pub const QUAD_W: [f64; 5] = [
    0.118463442528095,
    0.239314335249683,
    0.284444444444444,
    0.239314335249683,
    0.118463442528095,
];

// Q-point Gauss-Legendre integrates through polynomial degree 2Q-1.
// These are the same two-/three-/four-point constants used by the GPU,
// retained as f64 here; zero or one opponent needs only the midpoint rule.
const QUAD_T1: [f64; 1] = [0.5];
const QUAD_W1: [f64; 1] = [1.0];
const QUAD_T2: [f64; 2] = [0.211324865405187, 0.788675134594813];
const QUAD_W2: [f64; 2] = [0.5, 0.5];
const QUAD_T3: [f64; 3] = [0.112701665379258, 0.5, 0.887298334620742];
const QUAD_W3: [f64; 3] = [0.277777777777778, 0.444444444444444, 0.277777777777778];
const QUAD_T4: [f64; 4] = [0.069431844202974, 0.330009478207572, 0.669990521792428, 0.930568155797026];
const QUAD_W4: [f64; 4] = [0.173927422568727, 0.326072577431273, 0.326072577431273, 0.173927422568727];

pub struct CoupledDeck {
    /// Particle-major ascending class order and strict/inclusive CDF indices.
    pub order: Vec<u32>,
    pub lower: Vec<u32>,
    pub upper: Vec<u32>,
}

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        z ^ (z >> 31)
    }
}

impl CoupledDeck {
    pub fn shared() -> Arc<Self> {
        static TABLE: OnceLock<Arc<CoupledDeck>> = OnceLock::new();
        TABLE.get_or_init(|| Arc::new(Self::build())).clone()
    }

    fn build() -> Self {
        let mut combos = vec![Vec::new(); NUM_CLASSES];
        for a in 0..52u8 {
            for b in a + 1..52u8 {
                combos[class_index(a / 4, b / 4, a % 4 == b % 4)].push([a, b]);
            }
        }
        let mut rng = Rng(90210);
        let mut out = Self {
            order: vec![],
            lower: vec![0; SAMPLES * NUM_CLASSES],
            upper: vec![0; SAMPLES * NUM_CLASSES],
        };
        for sample in 0..SAMPLES {
            let mut deck: Vec<u8> = (0..52).collect();
            for i in (1..52).rev() {
                let j = rng.next() as usize % (i + 1);
                deck.swap(i, j);
            }
            let mut ranks = [0u32; NUM_CLASSES];
            for h in 0..NUM_CLASSES {
                let c = combos[h][rng.next() as usize % combos[h].len()];
                let mut cards = [c[0], c[1], 0, 0, 0, 0, 0];
                let mut i = 2;
                for &card in &deck {
                    if card != c[0] && card != c[1] {
                        cards[i] = card;
                        i += 1;
                        if i == 7 {
                            break;
                        }
                    }
                }
                ranks[h] = evaluate7(&cards);
            }
            let mut order: Vec<usize> = (0..NUM_CLASSES).collect();
            order.sort_by_key(|&h| (ranks[h], h));
            let mut lo = 0;
            while lo < NUM_CLASSES {
                let mut hi = lo + 1;
                while hi < NUM_CLASSES && ranks[order[hi]] == ranks[order[lo]] {
                    hi += 1;
                }
                for &h in &order[lo..hi] {
                    out.lower[sample * NUM_CLASSES + h] = lo as u32;
                    out.upper[sample * NUM_CLASSES + h] = hi as u32;
                }
                lo = hi;
            }
            out.order.extend(order.into_iter().map(|h| h as u32));
        }
        out
    }

    /// All hero classes against normalized independent opponent class weights.
    /// Integrating product(less + t*equal) splits any tied pot exactly.
    /// Use the smallest Gauss rule exact for the number of opponents. This
    /// preserves the latent game and f64 arithmetic, not bitwise rounding.
    pub fn equities(&self, opponents: &[Vec<f32>]) -> [f64; NUM_CLASSES] {
        assert!(opponents.len() <= 8);
        // Keep the original five-point hot body in this public entry point.
        // Smaller rules return through helpers; eight opponents falls through.
        match opponents.len() {
            0..=1 => return self.equities_with_rule(opponents, QUAD_T1, QUAD_W1),
            2..=3 => return self.equities_with_rule(opponents, QUAD_T2, QUAD_W2),
            4..=5 => return self.equities_with_rule(opponents, QUAD_T3, QUAD_W3),
            6..=7 => return self.equities_with_rule(opponents, QUAD_T4, QUAD_W4),
            _ => {},
        }
        let mut sums = [0.0; NUM_CLASSES];
        let mut cdfs = [[0.0f64; NUM_CLASSES + 1]; 8];
        for sample in 0..SAMPLES {
            let base = sample * NUM_CLASSES;
            for (q, dist) in opponents.iter().enumerate() {
                for i in 0..NUM_CLASSES {
                    cdfs[q][i + 1] = cdfs[q][i] + dist[self.order[base + i] as usize] as f64;
                }
            }
            for h in 0..NUM_CLASSES {
                let lo = self.lower[base + h] as usize;
                let hi = self.upper[base + h] as usize;
                let mut values = [1.0; 5];
                for cdf in &cdfs[..opponents.len()] {
                    let less = cdf[lo];
                    let equal = cdf[hi] - less;
                    for k in 0..5 {
                        values[k] *= less + QUAD_T[k] * equal;
                    }
                }
                sums[h] += values.iter().zip(QUAD_W).map(|(v, w)| v * w).sum::<f64>();
            }
        }
        for x in &mut sums {
            *x /= SAMPLES as f64;
        }
        sums
    }

    fn equities_with_rule<const Q: usize>(
        &self, opponents: &[Vec<f32>], points: [f64; Q], weights: [f64; Q],
    ) -> [f64; NUM_CLASSES] {
        let mut sums = [0.0; NUM_CLASSES];
        let mut cdfs = [[0.0f64; NUM_CLASSES + 1]; 8];
        for sample in 0..SAMPLES {
            let base = sample * NUM_CLASSES;
            for (q, dist) in opponents.iter().enumerate() {
                for i in 0..NUM_CLASSES {
                    cdfs[q][i + 1] = cdfs[q][i] + dist[self.order[base + i] as usize] as f64;
                }
            }
            for h in 0..NUM_CLASSES {
                let lo = self.lower[base + h] as usize;
                let hi = self.upper[base + h] as usize;
                let mut values = [1.0; Q];
                for cdf in &cdfs[..opponents.len()] {
                    let less = cdf[lo];
                    let equal = cdf[hi] - less;
                    for k in 0..Q {
                        values[k] *= less + points[k] * equal;
                    }
                }
                sums[h] += values.iter().zip(weights).map(|(v, w)| v * w).sum::<f64>();
            }
        }
        for x in &mut sums {
            *x /= SAMPLES as f64;
        }
        sums
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::equity::{class_prob, EquityTable};
    use crate::preflop::{PreflopConfig, PreflopSolver};


    impl CoupledDeck {
        /// All hero classes against normalized independent opponent class weights.
        /// Integrating product(less + t*equal) splits any tied pot exactly. Five
        /// Gauss points integrate degree <=8 (up to nine seats), without sampling ties.
        fn old_five_point_equities(&self, opponents: &[Vec<f32>]) -> [f64; NUM_CLASSES] {
            assert!(opponents.len() <= 8);
            let mut sums = [0.0; NUM_CLASSES];
            let mut cdfs = [[0.0f64; NUM_CLASSES + 1]; 8];
            for sample in 0..SAMPLES {
                let base = sample * NUM_CLASSES;
                for (q, dist) in opponents.iter().enumerate() {
                    for i in 0..NUM_CLASSES {
                        cdfs[q][i + 1] = cdfs[q][i] + dist[self.order[base + i] as usize] as f64;
                    }
                }
                for h in 0..NUM_CLASSES {
                    let lo = self.lower[base + h] as usize;
                    let hi = self.upper[base + h] as usize;
                    let mut values = [1.0; 5];
                    for cdf in &cdfs[..opponents.len()] {
                        let less = cdf[lo];
                        let equal = cdf[hi] - less;
                        for k in 0..5 {
                            values[k] *= less + QUAD_T[k] * equal;
                        }
                    }
                    sums[h] += values.iter().zip(QUAD_W).map(|(v, w)| v * w).sum::<f64>();
                }
            }
            for x in &mut sums {
                *x /= SAMPLES as f64;
            }
            sums
        }
    }

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

    #[test]
    fn coupled_payoffs_flow_through_cfr_and_charge_rake_once() {
        let cfg = PreflopConfig {
            positions: vec!["BTN".into(), "SB".into(), "BB".into()],
            stack: 4.0,
            posts: vec![0.0, 0.5, 1.0],
            ante: 0.0,
            limp: true,
            open_raises: vec![],
            raise_mults: vec![],
            max_raises: 1,
            add_allin: true,
            allin_threshold: 0.85,
            rake_pct: 5.0,
            rake_cap: 1.0,
            no_flop_no_drop: true,
            realization: "raw".into(),
            call_only_seats: vec![],
            open_raises_by_seat: None,
            raise_mults_by_seat: None,
        };
        let mut s = PreflopSolver::new(cfg, Arc::new(EquityTable::build(8))).unwrap();
        assert_eq!(s.multiway_equity_model(), MODEL);
        let weights: Vec<Vec<f32>> = (0..3)
            .map(|p| {
                (0..169)
                    .map(|h| class_prob(h) * ((h + p * 17) % 23 + 1) as f32 / 25.0)
                    .collect()
            })
            .collect();
        let probability: f64 = weights
            .iter()
            .map(|w| w.iter().sum::<f32>() as f64)
            .product();
        for (node, nd) in
            s.nodes.iter().enumerate().filter(|(_, nd)| {
                nd.kind == super::super::KIND_POT_SHARE && nd.live.count_ones() == 3
            })
        {
            let mut total = 0.0;
            for p in 0..3 {
                let mut values = [0.0; 169];
                s.terminal_value(node, p, &weights, &mut values);
                total += values
                    .iter()
                    .zip(&weights[p])
                    .map(|(v, w)| *v as f64 * *w as f64)
                    .sum::<f64>();
            }
            assert!(
                (total + probability * s.rake_of(nd.pot)).abs() < 1e-6,
                "{total}"
            );
        }
        for _ in 0..30 {
            s.iterate();
        }
        assert!(s.set_multiway_equity_model("legacy_product").is_err());
        let evs = s.evs();
        assert!(evs.iter().all(|v| v.is_finite()));
        assert!(evs.iter().sum::<f64>() <= 1e-5);
        assert!(s.br_gaps().iter().all(|g| g.is_finite() && *g >= -1e-6));
    }

    #[test]
    fn joint_pot_conservation_and_ties() {
        let table = CoupledDeck::shared();
        for n in [3, 4, 9] {
            let weights: Vec<Vec<f32>> = (0..n)
                .map(|p| {
                    let mut w: Vec<f32> = (0..NUM_CLASSES)
                        .map(|h| ((h * (p + 3) + 17) % 59) as f32)
                        .collect();
                    let total: f32 = w.iter().sum();
                    for x in &mut w {
                        *x /= total;
                    }
                    w
                })
                .collect();
            let pot: f64 = (0..n)
                .map(|p| {
                    let others = weights
                        .iter()
                        .enumerate()
                        .filter(|(q, _)| *q != p)
                        .map(|(_, w)| w.clone())
                        .collect::<Vec<_>>();
                    table
                        .equities(&others)
                        .iter()
                        .zip(&weights[p])
                        .map(|(e, w)| e * *w as f64)
                        .sum::<f64>()
                })
                .sum();
            assert!((pot - 1.0).abs() < 1e-6, "{n} players: {pot}");
            let mut same = vec![0.0; NUM_CLASSES];
            same[168] = 1.0;
            assert!((table.equities(&vec![same; n - 1])[168] - 1.0 / n as f64).abs() < 1e-12);
        }
    }
}
