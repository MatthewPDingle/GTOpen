//! Research-only approximation of coupled_deck_v1, not compatible-card equity.
//! A fixed equal-weight mixture of coherent rank particles preserves pot shares.
use solver::preflop::equity::{class_combos, NUM_CLASSES};
use solver::preflop::multiway::{CoupledDeck, SAMPLES};

#[derive(Clone, Debug)]
pub struct Ensemble {
    pub indices: Vec<usize>,
}

impl Ensemble {
    pub fn new(indices: Vec<usize>) -> Result<Self, String> {
        if indices.is_empty() || indices.iter().any(|&i| i >= SAMPLES) {
            return Err("need nonempty particle indices within the source table".into());
        }
        let mut unique = indices.clone();
        unique.sort_unstable();
        unique.dedup();
        if unique.len() != indices.len() {
            return Err("duplicate particles are not supported by this equal-weight model".into());
        }
        Ok(Self { indices })
    }

    pub fn stratified(n: usize) -> Self {
        assert!((1..=SAMPLES).contains(&n));
        Self::new((0..n).map(|i| ((2 * i + 1) * SAMPLES) / (2 * n)).collect()).unwrap()
    }

    /// Same normalized independent-class contract as CoupledDeck::equities.
    /// No own-reach pruning: this is a conditional value for every hero hand.
    pub fn equities(&self, table: &CoupledDeck, opponents: &[Vec<f32>]) -> [f64; NUM_CLASSES] {
        assert!(opponents.len() <= 8);
        let mut sum = [0.0; NUM_CLASSES];
        for &s in &self.indices {
            let values = particle_equities(table, opponents, s);
            for h in 0..NUM_CLASSES {
                sum[h] += values[h];
            }
        }
        for v in &mut sum {
            *v /= self.indices.len() as f64;
        }
        sum
    }
}

pub fn particle_equities(
    table: &CoupledDeck,
    opponents: &[Vec<f32>],
    sample: usize,
) -> [f64; NUM_CLASSES] {
    assert!(sample < SAMPLES && opponents.len() <= 8);
    let (t, w): (&[f64], &[f64]) = match opponents.len() {
        0..=1 => (&[0.5], &[1.0]),
        2..=3 => (&[0.211324865405187, 0.788675134594813], &[0.5, 0.5]),
        4..=5 => (
            &[0.112701665379258, 0.5, 0.887298334620742],
            &[0.277777777777778, 0.444444444444444, 0.277777777777778],
        ),
        6..=7 => (
            &[
                0.069431844202974,
                0.330009478207572,
                0.669990521792428,
                0.930568155797026,
            ],
            &[
                0.173927422568727,
                0.326072577431273,
                0.326072577431273,
                0.173927422568727,
            ],
        ),
        _ => (
            &solver::preflop::multiway::QUAD_T,
            &solver::preflop::multiway::QUAD_W,
        ),
    };
    let base = sample * NUM_CLASSES;
    let mut cdfs = [[0.0; NUM_CLASSES + 1]; 8];
    for (q, dist) in opponents.iter().enumerate() {
        assert_eq!(dist.len(), NUM_CLASSES);
        for i in 0..NUM_CLASSES {
            cdfs[q][i + 1] = cdfs[q][i] + dist[table.order[base + i] as usize] as f64;
        }
    }
    let mut out = [0.0; NUM_CLASSES];
    for h in 0..NUM_CLASSES {
        let lo = table.lower[base + h] as usize;
        let hi = table.upper[base + h] as usize;
        let mut values = [1.0; 5];
        for cdf in &cdfs[..opponents.len()] {
            let less = cdf[lo];
            let equal = cdf[hi] - less;
            for k in 0..t.len() {
                values[k] *= less + t[k] * equal;
            }
        }
        out[h] = values[..t.len()].iter().zip(w).map(|(v, w)| v * w).sum();
    }
    out
}

/// Kernel herding without replacement: greedily minimize squared error of the
/// selected uniform mean against the full source mean. Training only; never
/// supplies physical-equity labels. All hero classes receive combo weighting.
/// Returns a nested selection so 16/32/64 are one predeclared candidate family.
fn training_features(
    table: &CoupledDeck,
    contexts: &[Vec<Vec<f32>>],
) -> (Vec<f64>, Vec<f64>, usize) {
    assert!(!contexts.is_empty());
    let width = contexts.len() * NUM_CLASSES;
    let mut features = vec![0.0; SAMPLES * width];
    let mut mean = vec![0.0; width];
    for s in 0..SAMPLES {
        for (c, opponents) in contexts.iter().enumerate() {
            let values = particle_equities(table, opponents, s);
            for h in 0..NUM_CLASSES {
                let i = c * NUM_CLASSES + h;
                let x = values[h] * (class_combos(h) as f64 / 1326.0).sqrt();
                features[s * width + i] = x;
                mean[i] += x / SAMPLES as f64;
            }
        }
    }
    let mut norm = vec![0.0; SAMPLES];
    for s in 0..SAMPLES {
        for i in 0..width {
            features[s * width + i] -= mean[i];
            norm[s] += features[s * width + i].powi(2);
        }
    }
    (features, norm, width)
}

pub fn representative_indices(
    table: &CoupledDeck,
    contexts: &[Vec<Vec<f32>>],
    count: usize,
) -> Vec<usize> {
    assert!((1..=SAMPLES).contains(&count));
    let (features, norm, width) = training_features(table, contexts);
    let mut residual = vec![0.0; width];
    let mut used = vec![false; SAMPLES];
    let mut selected = Vec::with_capacity(count);
    for _ in 0..count {
        let mut best = (f64::INFINITY, 0);
        for s in 0..SAMPLES {
            if used[s] {
                continue;
            }
            let row = &features[s * width..(s + 1) * width];
            let score = norm[s] + 2.0 * row.iter().zip(&residual).map(|(a, b)| a * b).sum::<f64>();
            if score < best.0 {
                best = (score, s);
            }
        }
        used[best.1] = true;
        selected.push(best.1);
        for i in 0..width {
            residual[i] += features[best.1 * width + i];
        }
    }
    selected
}

#[derive(serde::Serialize)]
pub struct ExchangeSweep {
    pub sweep: usize,
    pub swaps: usize,
    pub training_combo_weighted_mean_squared_error: f64,
}

/// Predeclared v2: deterministic coordinate exchange, same training-only loss.
/// Candidate set size and uniform weights stay fixed. No physical/development
/// data, reweighting or hand-specific correction enters the selection.
pub fn exchange_refinement(
    table: &CoupledDeck,
    contexts: &[Vec<Vec<f32>>],
    initial: &[usize],
    max_sweeps: usize,
) -> (Vec<usize>, Vec<ExchangeSweep>) {
    Ensemble::new(initial.to_vec()).unwrap();
    let (features, norm, width) = training_features(table, contexts);
    exchange_features(&features, &norm, width, initial, max_sweeps, contexts.len())
}

fn exchange_features(
    features: &[f64],
    norm: &[f64],
    width: usize,
    initial: &[usize],
    max_sweeps: usize,
    contexts: usize,
) -> (Vec<usize>, Vec<ExchangeSweep>) {
    let samples = norm.len();
    assert_eq!(features.len(), samples * width);
    let mut selected = initial.to_vec();
    let mut used = vec![false; samples];
    for &s in &selected {
        assert!(!used[s]);
        used[s] = true;
    }
    let mut residual = vec![0.0; width];
    for &s in &selected {
        for i in 0..width {
            residual[i] += features[s * width + i];
        }
    }
    let loss = |residual: &[f64]| {
        residual.iter().map(|x| x * x).sum::<f64>()
            / (selected.len() * selected.len() * contexts) as f64
    };
    let initial_loss = loss(&residual);
    let denominator = (selected.len() * selected.len() * contexts) as f64;
    let mut trace = vec![ExchangeSweep {
        sweep: 0,
        swaps: 0,
        training_combo_weighted_mean_squared_error: initial_loss,
    }];
    let mut without = vec![0.0; width];
    for sweep in 1..=max_sweeps {
        let mut swaps = 0;
        for position in 0..selected.len() {
            let old = selected[position];
            for i in 0..width {
                without[i] = residual[i] - features[old * width + i];
            }
            let score = |s: usize| {
                norm[s]
                    + 2.0
                        * features[s * width..(s + 1) * width]
                            .iter()
                            .zip(&without)
                            .map(|(a, b)| a * b)
                            .sum::<f64>()
            };
            let old_score = score(old);
            let mut best = (old_score, old);
            for s in 0..samples {
                if used[s] {
                    continue;
                }
                let candidate = score(s);
                if candidate < best.0 {
                    best = (candidate, s);
                }
            }
            if old_score - best.0 > 1e-12 * (1.0 + old_score.abs()) {
                selected[position] = best.1;
                used[old] = false;
                used[best.1] = true;
                for i in 0..width {
                    residual[i] = without[i] + features[best.1 * width + i];
                }
                swaps += 1;
            }
        }
        // Re-sum in selected order to limit accumulated cancellation drift.
        residual.fill(0.0);
        for &s in &selected {
            for i in 0..width {
                residual[i] += features[s * width + i];
            }
        }
        let measured = residual.iter().map(|x| x * x).sum::<f64>() / denominator;
        trace.push(ExchangeSweep {
            sweep,
            swaps,
            training_combo_weighted_mean_squared_error: measured,
        });
        if swaps == 0 {
            break;
        }
    }
    (selected, trace)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exchange_uses_training_loss_and_preserves_unique_uniform_selection() {
        // Four centered feature vectors. Initial [0,1] has mean -2;
        // selecting opposite vectors reaches the exact full mean at zero.
        let features = [-3.0, -1.0, 1.0, 3.0];
        let norms = [9.0, 1.0, 1.0, 9.0];
        let (indices, trace) = exchange_features(&features, &norms, 1, &[0, 1], 8, 1);
        assert_eq!(indices, vec![2, 1]);
        assert_eq!(trace[0].training_combo_weighted_mean_squared_error, 4.0);
        assert_eq!(
            trace
                .last()
                .unwrap()
                .training_combo_weighted_mean_squared_error,
            0.0
        );
        assert!(trace
            .windows(2)
            .all(|w| w[1].training_combo_weighted_mean_squared_error
                <= w[0].training_combo_weighted_mean_squared_error));
        assert_eq!(trace.last().unwrap().swaps, 0);
        let (unchanged, short) = exchange_features(&features, &norms, 1, &[0, 1], 0, 1);
        assert_eq!(unchanged, vec![0, 1]);
        assert_eq!(short.len(), 1);
    }

    fn range(q: usize) -> Vec<f32> {
        let mut d = vec![0.0; NUM_CLASSES];
        d[q % NUM_CLASSES] = 0.5;
        d[(q + 53) % NUM_CLASSES] = 0.25;
        d[(q + 107) % NUM_CLASSES] = 0.25;
        d
    }

    #[test]
    fn full_particle_order_is_exact_reference() {
        let table = CoupledDeck::shared();
        let full = Ensemble::new((0..SAMPLES).collect()).unwrap();
        for n in 0..=8 {
            let ds: Vec<_> = (0..n).map(range).collect();
            assert_eq!(full.equities(&table, &ds), table.equities(&ds));
        }
    }

    #[test]
    fn reduced_ensembles_conserve_pot_and_split_ties() {
        let table = CoupledDeck::shared();
        for count in [1, 16, 32, 64] {
            let model = Ensemble::stratified(count);
            for seats in 2..=9 {
                let ds: Vec<_> = (0..seats).map(|q| range(q * 13)).collect();
                let mut pot = 0.0;
                for p in 0..seats {
                    let opponents: Vec<_> = ds
                        .iter()
                        .enumerate()
                        .filter(|(q, _)| *q != p)
                        .map(|(_, d)| d.clone())
                        .collect();
                    let eq = model.equities(&table, &opponents);
                    assert!(eq
                        .iter()
                        .all(|v| v.is_finite() && *v >= 0.0 && *v <= 1.0 + 1e-12));
                    pot += ds[p]
                        .iter()
                        .zip(eq)
                        .map(|(d, v)| *d as f64 * v)
                        .sum::<f64>();
                }
                assert!(
                    (pot - 1.0).abs() < 2e-12,
                    "{count} particles, {seats} seats: {pot}"
                );
                let mut same = vec![0.0; NUM_CLASSES];
                same[168] = 1.0;
                assert!(
                    (model.equities(&table, &vec![same; seats - 1])[168] - 1.0 / seats as f64)
                        .abs()
                        < 2e-12
                );
            }
        }
    }

    #[test]
    fn zero_opponent_mass_is_zero_but_no_own_reach_is_required() {
        let table = CoupledDeck::shared();
        let model = Ensemble::stratified(16);
        assert_eq!(
            model.equities(&table, &[vec![0.0; NUM_CLASSES]]),
            [0.0; NUM_CLASSES]
        );
        assert!(model.equities(&table, &[range(0), range(17)])[168] > 0.0);
        assert!(Ensemble::new(vec![]).is_err());
        assert!(Ensemble::new(vec![0, 0]).is_err());
        assert!(Ensemble::new(vec![SAMPLES]).is_err());
    }
}
