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
    /// Integrating product(less + t*equal) splits any tied pot exactly. Five
    /// Gauss points integrate degree <=8 (up to nine seats), without sampling ties.
    pub fn equities(&self, opponents: &[Vec<f32>]) -> [f64; NUM_CLASSES] {
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::equity::{class_prob, EquityTable};
    use crate::preflop::{PreflopConfig, PreflopSolver};

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
