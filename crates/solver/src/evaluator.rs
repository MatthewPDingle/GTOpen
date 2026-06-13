//! 7-card poker hand evaluator.
//!
//! `evaluate7` returns a `u32` where a higher value is a stronger hand.
//! Encoding: `category << 20 | r0 << 16 | r1 << 12 | r2 << 8 | r3 << 4 | r4`,
//! where r0..r4 are tiebreak ranks (most significant first), zero-padded.
//! Hands in the same category always use the same number of tiebreak slots,
//! so the zero padding never causes incorrect comparisons.

use crate::cards::Card;

pub const CAT_HIGH_CARD: u32 = 0;
pub const CAT_PAIR: u32 = 1;
pub const CAT_TWO_PAIR: u32 = 2;
pub const CAT_TRIPS: u32 = 3;
pub const CAT_STRAIGHT: u32 = 4;
pub const CAT_FLUSH: u32 = 5;
pub const CAT_FULL_HOUSE: u32 = 6;
pub const CAT_QUADS: u32 = 7;
pub const CAT_STRAIGHT_FLUSH: u32 = 8;

#[inline]
fn make_value(cat: u32, ranks: &[u8]) -> u32 {
    let mut v = cat;
    for slot in 0..5 {
        v = (v << 4) | ranks.get(slot).copied().unwrap_or(0) as u32;
    }
    v
}

/// Given a 13-bit rank mask, return the top rank of the best straight, if any.
/// The wheel (A-5) returns rank 3 (the five).
#[inline]
fn straight_top(rank_mask: u16) -> Option<u8> {
    // Shift ranks up by one and put the ace at bit 0 so the wheel is contiguous.
    let m = ((rank_mask as u32) << 1) | ((rank_mask as u32 >> 12) & 1);
    let mut run = 0u32;
    let mut best: Option<u8> = None;
    for i in 0..14 {
        if m & (1 << i) != 0 {
            run += 1;
            if run >= 5 {
                best = Some((i - 1) as u8);
            }
        } else {
            run = 0;
        }
    }
    best
}

/// Top `n` set bits of a rank mask, in descending order.
#[inline]
fn top_ranks(rank_mask: u16, n: usize, out: &mut [u8; 5]) -> usize {
    let mut count = 0;
    for r in (0..13).rev() {
        if rank_mask & (1 << r) != 0 {
            out[count] = r as u8;
            count += 1;
            if count == n {
                break;
            }
        }
    }
    count
}

/// Evaluate the best 5-card hand from 7 cards. Higher return value = stronger.
pub fn evaluate7(cards: &[Card]) -> u32 {
    debug_assert_eq!(cards.len(), 7);
    let mut suit_masks = [0u16; 4];
    let mut rank_counts = [0u8; 13];
    let mut rank_mask = 0u16;
    for &c in cards {
        let r = (c >> 2) as usize;
        suit_masks[(c & 3) as usize] |= 1 << r;
        rank_counts[r] += 1;
        rank_mask |= 1 << r;
    }

    let mut flush_suit: Option<usize> = None;
    for s in 0..4 {
        if suit_masks[s].count_ones() >= 5 {
            flush_suit = Some(s);
            break; // at most one suit can have 5+ cards out of 7
        }
    }

    if let Some(s) = flush_suit {
        if let Some(top) = straight_top(suit_masks[s]) {
            return make_value(CAT_STRAIGHT_FLUSH, &[top]);
        }
    }

    // Collect rank groups (descending rank order).
    let mut quads: Option<u8> = None;
    let mut trips: [u8; 2] = [0; 2];
    let mut n_trips = 0;
    let mut pairs: [u8; 3] = [0; 3];
    let mut n_pairs = 0;
    for r in (0..13).rev() {
        match rank_counts[r] {
            4 => quads = Some(r as u8),
            3 => {
                if n_trips < 2 {
                    trips[n_trips] = r as u8;
                    n_trips += 1;
                }
            }
            2 => {
                if n_pairs < 3 {
                    pairs[n_pairs] = r as u8;
                    n_pairs += 1;
                }
            }
            _ => {}
        }
    }

    if let Some(q) = quads {
        let mut kick = [0u8; 5];
        let kicker_mask = rank_mask & !(1 << q);
        top_ranks(kicker_mask, 1, &mut kick);
        return make_value(CAT_QUADS, &[q, kick[0]]);
    }

    if n_trips >= 1 {
        // Full house: best trips + best remaining pair (which may be a second trips).
        let t = trips[0];
        let pair = if n_trips >= 2 {
            Some(trips[1])
        } else if n_pairs >= 1 {
            Some(pairs[0])
        } else {
            None
        };
        if let Some(p) = pair {
            return make_value(CAT_FULL_HOUSE, &[t, p]);
        }
    }

    if let Some(s) = flush_suit {
        let mut tops = [0u8; 5];
        top_ranks(suit_masks[s], 5, &mut tops);
        return make_value(CAT_FLUSH, &tops);
    }

    if let Some(top) = straight_top(rank_mask) {
        return make_value(CAT_STRAIGHT, &[top]);
    }

    if n_trips >= 1 {
        let t = trips[0];
        let mut kick = [0u8; 5];
        top_ranks(rank_mask & !(1 << t), 2, &mut kick);
        return make_value(CAT_TRIPS, &[t, kick[0], kick[1]]);
    }

    if n_pairs >= 2 {
        let (p1, p2) = (pairs[0], pairs[1]);
        let mut kick = [0u8; 5];
        top_ranks(rank_mask & !(1 << p1) & !(1 << p2), 1, &mut kick);
        return make_value(CAT_TWO_PAIR, &[p1, p2, kick[0]]);
    }

    if n_pairs == 1 {
        let p = pairs[0];
        let mut kick = [0u8; 5];
        top_ranks(rank_mask & !(1 << p), 3, &mut kick);
        return make_value(CAT_PAIR, &[p, kick[0], kick[1], kick[2]]);
    }

    let mut tops = [0u8; 5];
    top_ranks(rank_mask, 5, &mut tops);
    make_value(CAT_HIGH_CARD, &tops)
}

/// Category of an evaluated value (for display / tests).
pub fn category(value: u32) -> u32 {
    value >> 20
}

pub fn category_name(value: u32) -> &'static str {
    match category(value) {
        CAT_HIGH_CARD => "High Card",
        CAT_PAIR => "Pair",
        CAT_TWO_PAIR => "Two Pair",
        CAT_TRIPS => "Trips",
        CAT_STRAIGHT => "Straight",
        CAT_FLUSH => "Flush",
        CAT_FULL_HOUSE => "Full House",
        CAT_QUADS => "Quads",
        CAT_STRAIGHT_FLUSH => "Straight Flush",
        _ => "?",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cards::{card_from_str, parse_cards};

    fn ev(s: &str) -> u32 {
        let cards = parse_cards(s).unwrap();
        evaluate7(&cards)
    }

    // ---- Slow, independent reference evaluator (5-card, then best-of-21) ----

    fn ref_eval5(cards: &[Card]) -> (u32, Vec<u8>) {
        assert_eq!(cards.len(), 5);
        let mut ranks: Vec<u8> = cards.iter().map(|&c| c >> 2).collect();
        ranks.sort_unstable_by(|a, b| b.cmp(a));
        let suits: Vec<u8> = cards.iter().map(|&c| c & 3).collect();
        let is_flush = suits.iter().all(|&s| s == suits[0]);

        // counts per rank
        let mut counts = std::collections::BTreeMap::new();
        for &r in &ranks {
            *counts.entry(r).or_insert(0u8) += 1;
        }
        // groups sorted by (count desc, rank desc)
        let mut groups: Vec<(u8, u8)> = counts.iter().map(|(&r, &c)| (c, r)).collect();
        groups.sort_unstable_by(|a, b| b.cmp(a));

        // straight detection
        let unique: Vec<u8> = {
            let mut u: Vec<u8> = counts.keys().copied().collect();
            u.sort_unstable_by(|a, b| b.cmp(a));
            u
        };
        let straight_high = if unique.len() == 5 {
            if unique[0] - unique[4] == 4 {
                Some(unique[0])
            } else if unique == vec![12, 3, 2, 1, 0] {
                Some(3) // wheel
            } else {
                None
            }
        } else {
            None
        };

        if is_flush {
            if let Some(h) = straight_high {
                return (8, vec![h]);
            }
            return (5, ranks);
        }
        match groups[0].0 {
            4 => return (7, vec![groups[0].1, groups[1].1]),
            3 => {
                if groups[1].0 == 2 {
                    return (6, vec![groups[0].1, groups[1].1]);
                }
                return (3, vec![groups[0].1, groups[1].1, groups[2].1]);
            }
            2 => {
                if groups[1].0 == 2 {
                    return (2, vec![groups[0].1, groups[1].1, groups[2].1]);
                }
                return (
                    1,
                    vec![groups[0].1, groups[1].1, groups[2].1, groups[3].1],
                );
            }
            _ => {}
        }
        if let Some(h) = straight_high {
            return (4, vec![h]);
        }
        (0, ranks)
    }

    fn ref_eval7(cards: &[Card]) -> (u32, Vec<u8>) {
        assert_eq!(cards.len(), 7);
        let mut best: Option<(u32, Vec<u8>)> = None;
        for i in 0..7 {
            for j in (i + 1)..7 {
                let five: Vec<Card> = (0..7)
                    .filter(|&k| k != i && k != j)
                    .map(|k| cards[k])
                    .collect();
                let v = ref_eval5(&five);
                if best.is_none() || v > *best.as_ref().unwrap() {
                    best = Some(v);
                }
            }
        }
        best.unwrap()
    }

    struct XorShift(u64);
    impl XorShift {
        fn next(&mut self) -> u64 {
            let mut x = self.0;
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
            self.0 = x;
            x
        }
    }

    #[test]
    fn known_hands() {
        // Straight flush beats quads
        assert!(ev("AsKsQsJsTs2c2d") > ev("AcAdAhAs2c2d2h"));
        // Wheel straight flush
        assert_eq!(category(ev("As2s3s4s5s9c9d")), CAT_STRAIGHT_FLUSH);
        // Quads with kicker
        assert!(ev("AcAdAhAsKc2d3h") > ev("AcAdAhAsQc2d3h"));
        // Full house: trips+trips picks the better pair
        assert_eq!(category(ev("KcKdKh2c2d2h3s")), CAT_FULL_HOUSE);
        // KKK33 beats KKK22
        assert!(ev("KcKdKh3c3d2h2s") > ev("KcKdKh2c2d4h5s"));
        // Flush beats straight
        assert!(ev("2c4c6c8cTcAdKd") > ev("3c4d5h6s7c2d2h"));
        // Wheel is the lowest straight
        assert!(ev("6c5d4h3s2cKdQd") > ev("Ac5d4h3s2cKdQd"));
        // Two pair kicker
        assert!(ev("AcAdKcKd5h7s2c") > ev("AcAdKcKd4h7s2c") || {
            // both have 7 kicker (5h/4h irrelevant) -> equal
            ev("AcAdKcKd5h7s2c") == ev("AcAdKcKd4h7s2c")
        });
        // Board plays: same value for both
        assert_eq!(
            ev("AsKsQsJsTs2c3d"),
            ev("AsKsQsJsTs4c5d")
        );
    }

    #[test]
    fn full_house_better_pair() {
        // With two trips, the better one forms the pair part: KKK33 vs KKK44.
        let a = ev("KcKdKh3c3d3h9s"); // KKK33 (333 used as pair)
        let b = ev("KcKdKh2c2d4h4s"); // KKK44
        assert!(b > a);
    }

    #[test]
    fn matches_reference_random() {
        let mut rng = XorShift(0x9E3779B97F4A7C15);
        for _ in 0..20000 {
            // Sample 14 distinct cards -> two 7-card hands
            let mut deck: Vec<Card> = (0..52).collect();
            for i in 0..14 {
                let j = i + (rng.next() as usize) % (52 - i);
                deck.swap(i, j);
            }
            let h1 = &deck[0..7];
            let h2 = &deck[7..14];
            let f1 = evaluate7(h1);
            let f2 = evaluate7(h2);
            let r1 = ref_eval7(h1);
            let r2 = ref_eval7(h2);
            assert_eq!(category(f1), r1.0, "category mismatch for {:?}", h1);
            assert_eq!(category(f2), r2.0, "category mismatch for {:?}", h2);
            assert_eq!(
                f1.cmp(&f2),
                r1.cmp(&r2),
                "ordering mismatch: {:?} vs {:?}",
                h1,
                h2
            );
        }
    }

    #[test]
    fn straight_top_works() {
        // exhaustive straight check against naive loop
        for mask in 0u16..(1 << 13) {
            let got = straight_top(mask);
            let mut expected: Option<u8> = None;
            // check straights ending at rank top (top >= 3)
            for top in (3..13u8).rev() {
                let need: u16 = (0..5).map(|i| 1 << (top - i)).sum();
                if mask & need == need {
                    expected = Some(top);
                    break;
                }
            }
            // wheel
            if expected.is_none() {
                let wheel: u16 = (1 << 12) | 0b1111;
                if mask & wheel == wheel {
                    expected = Some(3);
                }
            }
            assert_eq!(got, expected, "mask {mask:013b}");
        }
        let _ = card_from_str("As"); // silence unused import warning paths
    }
}
