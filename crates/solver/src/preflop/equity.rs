//! 169-class preflop equity: Monte-Carlo pairwise table, disk-cached.
//!
//! The preflop solver works on the 169 canonical hand classes (13 pairs,
//! 78 suited, 78 offsuit). The pairwise table T[i][j] = P(class i beats
//! class j) + ties/2, averaged over compatible deals — so i-vs-j blocker
//! effects are baked in; cross-opponent blockers are not (mean-field, the
//! standard preflop-solver approximation). Multiway equity uses the
//! product approximation: P(i beats everyone) ~= prod of pairwise equities
//! — exact heads-up, approximate 3+-way (documented model error, small
//! relative to the postflop realization model this feeds).

use crate::cards::{make_card, Card};
use crate::evaluator::evaluate7;
use rayon::prelude::*;

pub const NUM_CLASSES: usize = 169;
const RANK_CHARS: [char; 13] = [
    '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A',
];

/// Class index for ranks `a >= b` (0..13, 12 = A): pair `a*13+a`,
/// suited `a*13+b`, offsuit `b*13+a`.
pub fn class_index(a: u8, b: u8, suited: bool) -> usize {
    let (hi, lo) = if a >= b { (a, b) } else { (b, a) };
    if hi == lo {
        (hi as usize) * 13 + hi as usize
    } else if suited {
        (hi as usize) * 13 + lo as usize
    } else {
        (lo as usize) * 13 + hi as usize
    }
}

/// (hi, lo, suited) for a class index.
pub fn class_parts(idx: usize) -> (u8, u8, bool) {
    let r = (idx / 13) as u8;
    let c = (idx % 13) as u8;
    if r == c {
        (r, c, false)
    } else if r > c {
        (r, c, true)
    } else {
        (c, r, false)
    }
}

/// "AKs" / "AKo" / "AA" style label.
pub fn class_label(idx: usize) -> String {
    let (hi, lo, suited) = class_parts(idx);
    if hi == lo {
        format!("{}{}", RANK_CHARS[hi as usize], RANK_CHARS[lo as usize])
    } else {
        format!(
            "{}{}{}",
            RANK_CHARS[hi as usize],
            RANK_CHARS[lo as usize],
            if suited { 's' } else { 'o' }
        )
    }
}

/// Number of concrete combos in a class (6 / 4 / 12).
pub fn class_combos(idx: usize) -> f32 {
    let (hi, lo, suited) = class_parts(idx);
    if hi == lo {
        6.0
    } else if suited {
        4.0
    } else {
        12.0
    }
}

/// Probability weight of each class in a full random deal (combos / 1326).
pub fn class_prob(idx: usize) -> f32 {
    class_combos(idx) / 1326.0
}

/// Deterministic small RNG (SplitMix64) so the table is reproducible.
struct Rng(u64);
impl Rng {
    fn new(seed: u64) -> Self {
        Rng(seed.wrapping_mul(0x9E3779B97F4A7C15).wrapping_add(1))
    }
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E3779B97F4A7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
        z ^ (z >> 31)
    }
    fn below(&mut self, n: u32) -> u32 {
        (self.next() % n as u64) as u32
    }
}

/// Deal a random concrete combo of `class`, rejecting cards in `used`.
fn deal_class(class: usize, used: u64, rng: &mut Rng) -> Option<(Card, Card)> {
    let (hi, lo, suited) = class_parts(class);
    for _ in 0..64 {
        let (c1, c2) = if hi == lo {
            let s1 = rng.below(4) as u8;
            let mut s2 = rng.below(3) as u8;
            if s2 >= s1 {
                s2 += 1;
            }
            (make_card(hi, s1), make_card(hi, s2))
        } else if suited {
            let s = rng.below(4) as u8;
            (make_card(hi, s), make_card(lo, s))
        } else {
            let s1 = rng.below(4) as u8;
            let mut s2 = rng.below(3) as u8;
            if s2 >= s1 {
                s2 += 1;
            }
            (make_card(hi, s1), make_card(lo, s2))
        };
        let m = (1u64 << c1) | (1u64 << c2);
        if used & m == 0 {
            return Some((c1, c2));
        }
    }
    None
}

/// The pairwise class-equity table.
pub struct EquityTable {
    /// t[i * 169 + j] = equity (win + tie/2) of class i vs class j.
    t: Vec<f32>,
    pub samples: u32,
}

impl EquityTable {
    #[inline]
    pub fn eq(&self, i: usize, j: usize) -> f32 {
        self.t[i * NUM_CLASSES + j]
    }

    /// Equity of class `h` against an opponent whose class distribution is
    /// `dist` (must be normalized to sum 1).
    pub fn eq_vs_dist(&self, h: usize, dist: &[f32]) -> f32 {
        let row = &self.t[h * NUM_CLASSES..(h + 1) * NUM_CLASSES];
        row.iter().zip(dist.iter()).map(|(&e, &d)| e * d).sum()
    }

    /// Monte-Carlo estimate of the full table, or a disk-cache load when a
    /// matching file exists. `cache_path` may be e.g. "cache/preflop_eq169.bin".
    pub fn load_or_build(cache_path: &str, samples: u32) -> Self {
        if let Some(t) = Self::try_load(cache_path, samples) {
            return t;
        }
        let t = Self::build(samples);
        t.save(cache_path);
        t
    }

    fn try_load(path: &str, samples: u32) -> Option<Self> {
        let bytes = std::fs::read(path).ok()?;
        let want = 4 + NUM_CLASSES * NUM_CLASSES * 4;
        if bytes.len() != want {
            return None;
        }
        let got_samples = u32::from_le_bytes(bytes[0..4].try_into().ok()?);
        if got_samples != samples {
            return None;
        }
        let mut t = vec![0f32; NUM_CLASSES * NUM_CLASSES];
        for (k, v) in t.iter_mut().enumerate() {
            let o = 4 + k * 4;
            *v = f32::from_le_bytes(bytes[o..o + 4].try_into().ok()?);
        }
        Some(EquityTable { t, samples })
    }

    fn save(&self, path: &str) {
        if let Some(dir) = std::path::Path::new(path).parent() {
            std::fs::create_dir_all(dir).ok();
        }
        let mut bytes = Vec::with_capacity(4 + self.t.len() * 4);
        bytes.extend_from_slice(&self.samples.to_le_bytes());
        for v in &self.t {
            bytes.extend_from_slice(&v.to_le_bytes());
        }
        std::fs::write(path, bytes).ok();
    }

    pub fn build(samples: u32) -> Self {
        // upper triangle (i <= j), mirrored as 1 - eq
        let pairs: Vec<(usize, usize)> = (0..NUM_CLASSES)
            .flat_map(|i| (i..NUM_CLASSES).map(move |j| (i, j)))
            .collect();
        let results: Vec<((usize, usize), f32)> = pairs
            .par_iter()
            .map(|&(i, j)| {
                let mut rng = Rng::new((i * NUM_CLASSES + j) as u64);
                let mut won = 0f64;
                let mut n = 0u32;
                let mut deck = [0u8; 52];
                while n < samples {
                    let Some((a1, a2)) = deal_class(i, 0, &mut rng) else {
                        break;
                    };
                    let used = (1u64 << a1) | (1u64 << a2);
                    let Some((b1, b2)) = deal_class(j, used, &mut rng) else {
                        continue; // e.g. AA vs AA can collide; retry
                    };
                    let used = used | (1u64 << b1) | (1u64 << b2);
                    // board: 5 cards from the remaining 48
                    let mut m = 0usize;
                    for c in 0..52u8 {
                        if used & (1u64 << c) == 0 {
                            deck[m] = c;
                            m += 1;
                        }
                    }
                    let mut board = [0u8; 5];
                    for (k, b) in board.iter_mut().enumerate() {
                        let r = k + rng.below((m - k) as u32) as usize;
                        deck.swap(k, r);
                        *b = deck[k];
                    }
                    let va = evaluate7(&[
                        board[0], board[1], board[2], board[3], board[4], a1, a2,
                    ]);
                    let vb = evaluate7(&[
                        board[0], board[1], board[2], board[3], board[4], b1, b2,
                    ]);
                    if va > vb {
                        won += 1.0;
                    } else if va == vb {
                        won += 0.5;
                    }
                    n += 1;
                }
                ((i, j), if n > 0 { (won / n as f64) as f32 } else { 0.5 })
            })
            .collect();
        let mut t = vec![0f32; NUM_CLASSES * NUM_CLASSES];
        for ((i, j), e) in results {
            t[i * NUM_CLASSES + j] = e;
            t[j * NUM_CLASSES + i] = 1.0 - e;
        }
        EquityTable { t, samples }
    }
}
