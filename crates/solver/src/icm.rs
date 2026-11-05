//! Independent Chip Model (Malmuth–Harville) for tournament payoffs.
//!
//! A player's chance of finishing first is their share of the chips; given
//! the players placed above, the chance of taking the next place is their
//! share of the chips still unplaced. Expected prize is the sum over places
//! of payout times that probability. The exact sum over finishing orders is
//! computed by dynamic programming over the set of players already placed
//! (`2^N * N` work), which is instant for a final table and practical up to
//! [`MAX_EXACT_PLAYERS`].

/// Largest number of players (table plus field) priced exactly.
pub const MAX_EXACT_PLAYERS: usize = 12;

/// Expected prize of each player under Malmuth–Harville. `stacks` holds every
/// player still in the tournament (all > 0); `payouts[k]` is the prize for
/// place k+1. Places beyond the number of players are ignored, and missing
/// places pay 0.
pub fn malmuth_harville(stacks: &[f64], payouts: &[f64]) -> Vec<f64> {
    let n = stacks.len();
    assert!(n <= 20, "exact ICM over {n} players is too large");
    let mut out = vec![0.0; n];
    if n == 0 {
        return out;
    }
    let places = payouts.len().min(n);
    let total: f64 = stacks.iter().sum();
    if places == 0 || total <= 0.0 {
        return out;
    }
    if n == 1 {
        out[0] = payouts[0];
        return out;
    }
    let full = 1usize << n;
    // f[mask]: probability that exactly `mask` occupies the top |mask| places.
    let mut f = vec![0.0f64; full];
    let mut sum = vec![0.0f64; full];
    for mask in 1..full {
        let low = mask.trailing_zeros() as usize;
        sum[mask] = sum[mask & (mask - 1)] + stacks[low];
    }
    f[0] = 1.0;
    for mask in 0..full {
        let pm = f[mask];
        if pm == 0.0 {
            continue;
        }
        let placed = mask.count_ones() as usize;
        if placed >= places {
            continue;
        }
        let rest = total - sum[mask];
        if rest <= 0.0 {
            continue;
        }
        let pay = payouts[placed];
        for i in 0..n {
            if mask & (1 << i) != 0 {
                continue;
            }
            let p = pm * stacks[i] / rest;
            out[i] += p * pay;
            if placed + 1 < places {
                f[mask | (1 << i)] += p;
            }
        }
    }
    out
}

/// Expected prize of each player after a hand. `before` and `after` are
/// every player's chips before and after the hand (all `before` > 0).
/// Players who still have chips share the top places by Malmuth–Harville;
/// players who busted in this hand finish below them, a larger starting
/// stack finishing higher, with equal starting stacks splitting the places
/// they cover.
pub fn icm_after_hand(before: &[f64], after: &[f64], payouts: &[f64]) -> Vec<f64> {
    let n = before.len();
    assert_eq!(after.len(), n);
    let alive: Vec<usize> = (0..n).filter(|&i| after[i] > 1e-9).collect();
    let mut out = vec![0.0; n];
    let alive_stacks: Vec<f64> = alive.iter().map(|&i| after[i]).collect();
    for (k, v) in malmuth_harville(&alive_stacks, payouts).into_iter().enumerate() {
        out[alive[k]] = v;
    }
    let mut busted: Vec<usize> = (0..n).filter(|&i| after[i] <= 1e-9).collect();
    busted.sort_by(|&a, &b| before[b].partial_cmp(&before[a]).unwrap());
    let pay = |place: usize| payouts.get(place).copied().unwrap_or(0.0);
    let mut place = alive.len();
    let mut i = 0;
    while i < busted.len() {
        let mut j = i + 1;
        while j < busted.len() && (before[busted[j]] - before[busted[i]]).abs() <= 1e-9 {
            j += 1;
        }
        let share = (place..place + (j - i)).map(pay).sum::<f64>() / (j - i) as f64;
        for &b in &busted[i..j] {
            out[b] = share;
        }
        place += j - i;
        i = j;
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Brute force over every finishing order.
    fn brute(stacks: &[f64], payouts: &[f64]) -> Vec<f64> {
        fn rec(stacks: &[f64], payouts: &[f64], left: &mut Vec<usize>, prob: f64, place: usize, out: &mut [f64]) {
            if left.is_empty() {
                return;
            }
            let rest: f64 = left.iter().map(|&i| stacks[i]).sum();
            for k in 0..left.len() {
                let i = left[k];
                let p = prob * stacks[i] / rest;
                out[i] += p * payouts.get(place).copied().unwrap_or(0.0);
                left.remove(k);
                rec(stacks, payouts, left, p, place + 1, out);
                left.insert(k, i);
            }
        }
        let mut out = vec![0.0; stacks.len()];
        rec(stacks, payouts, &mut (0..stacks.len()).collect(), 1.0, 0, &mut out);
        out
    }

    #[test]
    fn matches_brute_force() {
        let cases: Vec<(Vec<f64>, Vec<f64>)> = vec![
            (vec![5000.0, 3000.0, 2000.0], vec![50.0, 30.0, 20.0]),
            (vec![10.0, 20.0, 30.0, 40.0, 5.0], vec![40.0, 25.0, 15.0]),
            (vec![12.0, 12.0, 30.0, 7.5, 18.0, 25.0], vec![30.0, 20.0, 14.0, 10.0, 0.0, 0.0]),
            (vec![1.0, 2.0], vec![100.0]),
        ];
        for (stacks, payouts) in cases {
            let a = malmuth_harville(&stacks, &payouts);
            let b = brute(&stacks, &payouts);
            for (x, y) in a.iter().zip(&b) {
                assert!((x - y).abs() < 1e-9, "{stacks:?} {payouts:?}: {a:?} vs {b:?}");
            }
            let paid: f64 = payouts.iter().take(stacks.len()).sum();
            assert!((a.iter().sum::<f64>() - paid).abs() < 1e-9);
        }
    }

    #[test]
    fn known_three_player_value() {
        // 50% / 30% / 20% stacks, 50 / 30 / 20 payouts (hand-checked orders).
        let v = malmuth_harville(&[50.0, 30.0, 20.0], &[50.0, 30.0, 20.0]);
        assert!((v[0] - 38.392857).abs() < 1e-5, "{v:?}");
        assert!((v[1] - 32.75).abs() < 1e-9, "{v:?}");
        assert!((v[2] - 28.857143).abs() < 1e-5, "{v:?}");
    }

    #[test]
    fn winner_take_all_is_linear() {
        let stacks = [3.0, 9.0, 4.5, 13.5];
        let v = malmuth_harville(&stacks, &[1.0]);
        for (x, s) in v.iter().zip(stacks) {
            assert!((x - s / 30.0).abs() < 1e-12);
        }
    }

    #[test]
    fn busted_players_finish_by_starting_stack() {
        // Two players bust in the same hand: the larger starting stack takes
        // the higher place; equal starting stacks split.
        let payouts = [50.0, 30.0, 20.0];
        let v = icm_after_hand(&[10.0, 20.0, 30.0], &[60.0, 0.0, 0.0], &payouts);
        assert_eq!(v, vec![50.0, 20.0, 30.0]);
        let v = icm_after_hand(&[30.0, 15.0, 15.0], &[60.0, 0.0, 0.0], &payouts);
        assert_eq!(v, vec![50.0, 25.0, 25.0]);
        let v = icm_after_hand(&[30.0, 15.0, 15.0], &[30.0, 30.0, 0.0], &payouts);
        assert_eq!(v[2], 20.0);
        assert!((v[0] - 40.0).abs() < 1e-12 && (v[1] - 40.0).abs() < 1e-12);
    }
}
