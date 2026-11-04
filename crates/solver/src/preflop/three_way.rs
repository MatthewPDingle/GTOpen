//! Three-way showdown equity by class triple, with the three hands dealt
//! jointly from one deck.
//!
//! For hero class h against opponent classes a and b, the table holds the
//! hero's expected pot share (ties split) over every card-compatible triple
//! of combos and a random board, and the fraction of combo triples that are
//! compatible at all. Against independent opponent class distributions dA,
//! dB the hero's share is then
//!
//!   sum_ab dA[a] dB[b] w[h,a,b] e[h,a,b] / sum_ab dA[a] dB[b] w[h,a,b],
//!
//! so card removal between all three hands is exact at the class level. Shares
//! are Monte-Carlo estimates (`samples` boards per class triple); 4+ way pots
//! keep the coupled-deck model.
use super::equity::{NUM_CLASSES, class_index};
use crate::evaluator::evaluate7;
use rayon::prelude::*;
use std::sync::{Arc, OnceLock};

pub const MODEL: &str = "three_way_table_v1";
pub const CACHE_PATH: &str = "cache/preflop_eq169x3.bin";
pub const DEFAULT_SAMPLES: u32 = 20_000;
const N: usize = NUM_CLASSES;
const MAGIC: &[u8; 8] = b"GTO3WAY1";

pub struct ThreeWayTable {
    /// ew[(h * N + a) * N + b] = w x hero share; w[...] = compatible fraction.
    ew: Vec<f32>,
    w: Vec<f32>,
    pub samples: u32,
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
    fn below(&mut self, n: usize) -> usize {
        (self.next() % n as u64) as usize
    }
}

fn combos() -> Vec<Vec<u64>> {
    let mut out = vec![Vec::new(); N];
    for a in 0..52u8 {
        for b in a + 1..52u8 {
            out[class_index(a / 4, b / 4, a % 4 == b % 4)].push((1u64 << a) | (1u64 << b));
        }
    }
    out
}

/// Every class multiset x <= y <= z, in the order the cache file stores them.
fn triples() -> Vec<[usize; 3]> {
    let mut out = Vec::with_capacity(N * (N + 1) * (N + 2) / 6);
    for x in 0..N {
        for y in x..N {
            for z in y..N {
                out.push([x, y, z]);
            }
        }
    }
    out
}

fn cards(mask: u64) -> [u8; 2] {
    let a = mask.trailing_zeros() as u8;
    [a, (mask & !(1u64 << a)).trailing_zeros() as u8]
}

/// Seat shares [x, y, z] and the compatible fraction for one class multiset.
fn simulate(t: [usize; 3], combos: &[Vec<u64>], samples: u32) -> ([f32; 3], f32) {
    let [x, y, z] = t;
    let mut deals = Vec::new();
    for &cx in &combos[x] {
        for &cy in &combos[y] {
            if cx & cy != 0 { continue; }
            for &cz in &combos[z] {
                if (cx | cy) & cz == 0 { deals.push([cx, cy, cz]); }
            }
        }
    }
    let total = (combos[x].len() * combos[y].len() * combos[z].len()) as f64;
    let w = deals.len() as f64 / total;
    if deals.is_empty() || samples == 0 {
        return ([0.0; 3], 0.0);
    }
    let mut rng = Rng(((x * N + y) * N + z) as u64 ^ 0x3a7_5eed);
    let mut sums = [0f64; 3];
    let mut deck = [0u8; 52];
    for _ in 0..samples {
        let deal = deals[rng.below(deals.len())];
        let used = deal[0] | deal[1] | deal[2];
        let mut m = 0;
        for c in 0..52u8 {
            if used & (1u64 << c) == 0 { deck[m] = c; m += 1; }
        }
        for k in 0..5 {
            let r = k + rng.below(m - k);
            deck.swap(k, r);
        }
        let mut values = [0u32; 3];
        for (seat, &mask) in deal.iter().enumerate() {
            let [a, b] = cards(mask);
            values[seat] = evaluate7(&[deck[0], deck[1], deck[2], deck[3], deck[4], a, b]);
        }
        let best = values.iter().copied().max().unwrap();
        let winners = values.iter().filter(|&&v| v == best).count() as f64;
        for seat in 0..3 {
            if values[seat] == best { sums[seat] += 1.0 / winners; }
        }
    }
    let s = samples as f64;
    ([(sums[0] / s) as f32, (sums[1] / s) as f32, (sums[2] / s) as f32], w as f32)
}

impl ThreeWayTable {
    /// The production table: loaded from the cache, built (minutes) and
    /// cached when missing. PREFLOP_EQ3_SAMPLES overrides the board count.
    pub fn shared() -> Arc<Self> {
        static TABLE: OnceLock<Arc<ThreeWayTable>> = OnceLock::new();
        TABLE.get_or_init(|| {
            let samples = std::env::var("PREFLOP_EQ3_SAMPLES").ok()
                .and_then(|v| v.parse().ok()).unwrap_or(DEFAULT_SAMPLES);
            Arc::new(Self::load_or_build(CACHE_PATH, samples))
        }).clone()
    }

    pub fn load_or_build(path: &str, samples: u32) -> Self {
        if let Some(t) = Self::load(path, samples) {
            return t;
        }
        eprintln!("building the 3-way equity table ({samples} boards per class triple); this takes a few minutes once");
        let t = Self::build(samples);
        if let Err(e) = t.save(path) {
            eprintln!("3-way equity table not cached: {e}");
        }
        t
    }

    pub fn build(samples: u32) -> Self {
        let combos = combos();
        let rows: Vec<([f32; 3], f32)> = triples().par_iter().map(|&t| simulate(t, &combos, samples)).collect();
        Self::from_rows(&rows, samples)
    }

    fn from_rows(rows: &[([f32; 3], f32)], samples: u32) -> Self {
        let mut ew = vec![0f32; N * N * N];
        let mut w = vec![0f32; N * N * N];
        for (t, &(shares, fraction)) in triples().into_iter().zip(rows) {
            // Seats of equal class are the same hero: average their shares.
            for hero in 0..3 {
                let c = t[hero];
                let (mut sum, mut count) = (0f32, 0f32);
                for seat in 0..3 {
                    if t[seat] == c { sum += shares[seat]; count += 1.0; }
                }
                let share = sum / count;
                let others: Vec<usize> = (0..3).filter(|&s| s != hero).map(|s| t[s]).collect();
                for (a, b) in [(others[0], others[1]), (others[1], others[0])] {
                    let at = (c * N + a) * N + b;
                    ew[at] = share * fraction;
                    w[at] = fraction;
                }
            }
        }
        Self { ew, w, samples }
    }

    fn load(path: &str, samples: u32) -> Option<Self> {
        let bytes = std::fs::read(path).ok()?;
        let count = N * (N + 1) * (N + 2) / 6;
        if bytes.len() != 12 + count * 16 || &bytes[..8] != MAGIC {
            return None;
        }
        if u32::from_le_bytes(bytes[8..12].try_into().ok()?) != samples {
            return None;
        }
        let f = |k: usize| f32::from_le_bytes(bytes[12 + 4 * k..16 + 4 * k].try_into().unwrap());
        let rows: Vec<([f32; 3], f32)> = (0..count).map(|i| ([f(4 * i), f(4 * i + 1), f(4 * i + 2)], f(4 * i + 3))).collect();
        Some(Self::from_rows(&rows, samples))
    }

    fn save(&self, path: &str) -> Result<(), String> {
        if let Some(dir) = std::path::Path::new(path).parent() {
            std::fs::create_dir_all(dir).map_err(|e| e.to_string())?;
        }
        let mut bytes = MAGIC.to_vec();
        bytes.extend_from_slice(&self.samples.to_le_bytes());
        for [x, y, z] in triples() {
            let fraction = self.w[(x * N + y) * N + z];
            for (hero, a, b) in [(x, y, z), (y, x, z), (z, x, y)] {
                let at = (hero * N + a) * N + b;
                let share = if fraction > 0.0 { self.ew[at] / fraction } else { 0.0 };
                bytes.extend_from_slice(&share.to_le_bytes());
            }
            bytes.extend_from_slice(&fraction.to_le_bytes());
        }
        // Write then rename, so a reader never sees half a table.
        let tmp = format!("{path}.tmp");
        std::fs::write(&tmp, bytes).map_err(|e| e.to_string())?;
        std::fs::rename(&tmp, path).map_err(|e| e.to_string())
    }

    /// Hero class h's expected share of a 3-way pot against two independent,
    /// normalized opponent class distributions. A hero class that cannot be
    /// dealt alongside any opponent mass gets an even third.
    pub fn shares(&self, a: &[f32], b: &[f32]) -> [f64; N] {
        let mut out = [0f64; N];
        for (h, share) in out.iter_mut().enumerate() {
            let (mut num, mut den) = (0f64, 0f64);
            for (i, &da) in a.iter().enumerate() {
                if da == 0.0 { continue; }
                let row = (h * N + i) * N;
                let (ew, w) = (&self.ew[row..row + N], &self.w[row..row + N]);
                let (mut n, mut d) = (0f32, 0f32);
                for j in 0..N {
                    n += ew[j] * b[j];
                    d += w[j] * b[j];
                }
                num += da as f64 * n as f64;
                den += da as f64 * d as f64;
            }
            *share = if den > 0.0 { num / den } else { 1.0 / 3.0 };
        }
        out
    }

    /// The full (share x compatible fraction, compatible fraction) arrays,
    /// indexed (h * 169 + a) * 169 + b, for the GPU kernels.
    #[cfg_attr(not(feature = "gpu"), allow(dead_code))]
    pub(crate) fn arrays(&self) -> (&[f32], &[f32]) {
        (&self.ew, &self.w)
    }

    /// The compatible fraction of class triple (h, a, b).
    pub fn compatible(&self, h: usize, a: usize, b: usize) -> f32 {
        self.w[(h * N + a) * N + b]
    }

    /// Hero h's share of class triple (h, a, b), when it can be dealt.
    pub fn share(&self, h: usize, a: usize, b: usize) -> f32 {
        let at = (h * N + a) * N + b;
        if self.w[at] > 0.0 { self.ew[at] / self.w[at] } else { 0.0 }
    }
}

#[cfg(test)]
pub(crate) mod tests;
