//! Independent Chip Model (Malmuth–Harville) for tournament payoffs.
//!
//! A player's chance of finishing first is their share of the chips; given
//! the players placed above, the chance of taking the next place is their
//! share of the chips still unplaced. Expected prize is the sum over places
//! of payout times that probability.
//!
//! The exact sum over finishing orders is computed by dynamic programming
//! over who has been placed so far. Players with their own stacks (the table)
//! are tracked individually; players at other tables come in groups of equal
//! stacks, tracked only by how many of each group have been placed. Equal
//! stacks are interchangeable under Malmuth–Harville, so this is exact, and a
//! field of hundreds of equal stacks costs no more than a few dozen places.
//! Only states with fewer players placed than there are paid places matter.

pub mod postflop;

/// Largest dynamic-programming state count priced exactly (table subsets
/// times group placements, capped at the paid places).
pub const MAX_STATES: usize = 1 << 19;

/// Players of equal stacks at other tables.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Group {
    pub stack: f64,
    pub count: usize,
}

/// Number of states [`malmuth_harville_groups`] would use, or None past
/// [`MAX_STATES`].
pub fn state_count(table: usize, groups: &[Group], payouts: usize) -> Option<usize> {
    let players = table + groups.iter().map(|g| g.count).sum::<usize>();
    let places = payouts.min(players);
    let mut states = 1usize.checked_shl(table as u32).filter(|&s| s <= MAX_STATES)?;
    for g in groups {
        states = states.checked_mul(g.count.min(places.saturating_sub(1)) + 1)?;
        if states > MAX_STATES {
            return None;
        }
    }
    Some(states)
}

/// Expected prize of each table player and of each player in each group.
/// Every stack must be > 0; `payouts[k]` is the prize for place k+1, places
/// beyond the number of players are ignored and missing places pay 0.
pub fn malmuth_harville_groups(stacks: &[f64], groups: &[Group], payouts: &[f64]) -> (Vec<f64>, Vec<f64>) {
    let n = stacks.len();
    let groups: Vec<Group> = groups.iter().copied().filter(|g| g.count > 0).collect();
    let mut table = vec![0.0; n];
    let mut field = vec![0.0; groups.len()];
    let players = n + groups.iter().map(|g| g.count).sum::<usize>();
    let places = payouts.len().min(players);
    let total: f64 = stacks.iter().sum::<f64>() + groups.iter().map(|g| g.stack * g.count as f64).sum::<f64>();
    if places == 0 || total <= 0.0 {
        return (table, field);
    }
    let states = state_count(n, &groups, payouts.len()).expect("ICM state space too large");
    let radix: Vec<usize> = groups.iter().map(|g| g.count.min(places - 1) + 1).collect();
    let mut mult = vec![1usize << n; groups.len()];
    for g in 1..groups.len() {
        mult[g] = mult[g - 1] * radix[g - 1];
    }
    let full = 1usize << n;
    let mut sum = vec![0.0f64; full];
    for mask in 1..full {
        let low = mask.trailing_zeros() as usize;
        sum[mask] = sum[mask & (mask - 1)] + stacks[low];
    }
    // f[state]: probability that exactly this placement fills the top places.
    let mut f = vec![0.0f64; states];
    f[0] = 1.0;
    let mut placed_of = vec![0usize; groups.len()];
    for idx in 0..states {
        let pm = f[idx];
        if pm == 0.0 {
            continue;
        }
        let mask = idx & (full - 1);
        let mut placed = mask.count_ones() as usize;
        let mut rest = total - sum[mask];
        for g in 0..groups.len() {
            placed_of[g] = (idx / mult[g]) % radix[g];
            placed += placed_of[g];
            rest -= placed_of[g] as f64 * groups[g].stack;
        }
        if placed >= places || rest <= 0.0 {
            continue;
        }
        let pay = payouts[placed];
        let more = placed + 1 < places;
        for i in 0..n {
            if mask & (1 << i) != 0 {
                continue;
            }
            let p = pm * stacks[i] / rest;
            table[i] += p * pay;
            if more {
                f[idx | (1 << i)] += p;
            }
        }
        for g in 0..groups.len() {
            let left = groups[g].count - placed_of[g];
            if left == 0 {
                continue;
            }
            let p = pm * left as f64 * groups[g].stack / rest;
            field[g] += p * pay;
            if more {
                f[idx + mult[g]] += p;
            }
        }
    }
    for (e, g) in field.iter_mut().zip(&groups) {
        *e /= g.count as f64;
    }
    (table, field)
}

/// Expected prize of each player under Malmuth–Harville, every player
/// tracked individually (see [`malmuth_harville_groups`]).
pub fn malmuth_harville(stacks: &[f64], payouts: &[f64]) -> Vec<f64> {
    malmuth_harville_groups(stacks, &[], payouts).0
}

/// Expected prize of each table player after a hand, and of each player in
/// each field group (whose stacks the hand doesn't change). `before` and
/// `after` are the table players' chips before and after the hand (all
/// `before` > 0). Players who still have chips share the top places;
/// players who busted in this hand finish below them, a larger starting
/// stack finishing higher, with equal starting stacks splitting the places
/// they cover.
pub fn icm_after_hand(before: &[f64], after: &[f64], groups: &[Group], payouts: &[f64]) -> (Vec<f64>, Vec<f64>) {
    let n = before.len();
    assert_eq!(after.len(), n);
    let alive: Vec<usize> = (0..n).filter(|&i| after[i] > 1e-9).collect();
    let mut out = vec![0.0; n];
    let alive_stacks: Vec<f64> = alive.iter().map(|&i| after[i]).collect();
    let (table, field) = malmuth_harville_groups(&alive_stacks, groups, payouts);
    for (k, v) in table.into_iter().enumerate() {
        out[alive[k]] = v;
    }
    let mut busted: Vec<usize> = (0..n).filter(|&i| after[i] <= 1e-9).collect();
    busted.sort_by(|&a, &b| before[b].partial_cmp(&before[a]).unwrap());
    let pay = |place: usize| payouts.get(place).copied().unwrap_or(0.0);
    let mut place = alive.len() + groups.iter().map(|g| g.count).sum::<usize>();
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
    (out, field)
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
        let v = icm_after_hand(&[10.0, 20.0, 30.0], &[60.0, 0.0, 0.0], &[], &payouts).0;
        assert_eq!(v, vec![50.0, 20.0, 30.0]);
        let v = icm_after_hand(&[30.0, 15.0, 15.0], &[60.0, 0.0, 0.0], &[], &payouts).0;
        assert_eq!(v, vec![50.0, 25.0, 25.0]);
        let v = icm_after_hand(&[30.0, 15.0, 15.0], &[30.0, 30.0, 0.0], &[], &payouts).0;
        assert_eq!(v[2], 20.0);
        assert!((v[0] - 40.0).abs() < 1e-12 && (v[1] - 40.0).abs() < 1e-12);
    }

    #[test]
    fn groups_match_individual_players() {
        // Equal stacks are interchangeable: a group must price exactly like
        // listing its players one by one.
        let table = [12.0, 30.0, 7.5];
        let payouts = [40.0, 25.0, 15.0, 10.0, 6.0, 4.0];
        let groups = [Group { stack: 20.0, count: 4 }, Group { stack: 9.0, count: 3 }];
        let (t, f) = malmuth_harville_groups(&table, &groups, &payouts);
        let mut all = table.to_vec();
        all.extend([20.0; 4]);
        all.extend([9.0; 3]);
        let v = malmuth_harville(&all, &payouts);
        for i in 0..3 {
            assert!((t[i] - v[i]).abs() < 1e-9, "{t:?} vs {v:?}");
        }
        assert!((f[0] - v[3]).abs() < 1e-9 && (f[1] - v[7]).abs() < 1e-9, "{f:?} vs {v:?}");
        let paid: f64 = payouts.iter().sum();
        assert!((t.iter().sum::<f64>() + 4.0 * f[0] + 3.0 * f[1] - paid).abs() < 1e-9);
    }

    #[test]
    fn large_field_bubble_is_fast_and_sums_to_the_prizes() {
        // 8 at the table, 144 elsewhere, 150 paid: the bubble.
        let table = [25.0, 25.0, 10.0, 40.0, 25.0, 25.0, 3.0, 25.0];
        let mut payouts: Vec<f64> = (0..150).map(|k| 1.0 / (k as f64 + 1.0).powf(0.9)).collect();
        payouts.iter_mut().for_each(|p| *p = p.max(0.02));
        let groups = [Group { stack: 25.0, count: 144 }];
        assert!(state_count(8, &groups, 150).is_some());
        let t0 = std::time::Instant::now();
        let (t, f) = malmuth_harville_groups(&table, &groups, &payouts);
        assert!(t0.elapsed().as_secs_f64() < 1.0);
        let paid: f64 = payouts.iter().sum();
        assert!((t.iter().sum::<f64>() + 144.0 * f[0] - paid).abs() < 1e-6 * paid);
        // ICM favours the 3bb stack: worth more than its chip share.
        let chip = 3.0 / (178.0 + 144.0 * 25.0) * paid;
        assert!(t[6] > chip, "{} vs {chip}", t[6]);
        assert_eq!(state_count(9, &[Group { stack: 20.0, count: 4000 }], 4000), None);
    }
}
