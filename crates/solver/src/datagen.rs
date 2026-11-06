//! Training data for a Preflop Lab leaf-value net (TODO item M6).
//!
//! Every example is one heads-up flop solve: two random 169-class ranges, a
//! pot, a stack, a rake and a canonical flop go in; each class's solved
//! value (pot-share convention, as a fraction of the starting pot), equity
//! and reach mass for both players come out. The postflop solve is exact
//! for whatever ranges go in, so the ranges only decide where a net trained
//! on the data is accurate; they are sampled broadly on purpose.
//!
//! Examples are fully determined by `(job, index)`: anyone can regenerate a
//! job's inputs from its number, which is what lets pooled community
//! uploads be checked (`solve-cli datagen verify`). Bump
//! [`GENERATOR_VERSION`] whenever sampling, the menu or the solver changes
//! the values a job produces, so old and new data are never blended.

use crate::cards::{rank, suit};
use crate::preflop::equity::{class_index, class_label, class_parts, NUM_CLASSES};
use crate::tree::TreeConfig;
use crate::{Solver, SpotConfig};
use serde::{Deserialize, Serialize};

/// Format name written in every file header.
pub const FORMAT: &str = "gtopen-leaf-values";
/// Version of the file layout.
pub const FORMAT_VERSION: u32 = 1;
/// Version of the sampling + menu + solver behaviour. Bump on any change
/// that alters the inputs or values a given job number produces.
pub const GENERATOR_VERSION: u32 = 1;
/// Name of the fixed postflop bet menu (see [`menu_tree`]).
pub const MENU: &str = "m5-srp-v1";
/// Chips per big blind in generated spots (the M5 configs' convention).
pub const CHIPS_PER_BB: f64 = 10.0;
/// Default examples per job.
pub const DEFAULT_PER_JOB: u32 = 100;
/// Jobs per contributor block (contributor blocks never overlap in practice).
const BLOCK_BITS: u32 = 24;

// ------------------------------------------------------------------ rng ----

/// SplitMix64: tiny, fast and identical on every platform.
#[derive(Clone)]
pub struct Rng(u64);

impl Rng {
    pub fn new(seed: u64) -> Self {
        Rng(seed)
    }
    pub fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }
    /// Uniform in [0, 1).
    pub fn f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
    pub fn range(&mut self, lo: f64, hi: f64) -> f64 {
        lo + (hi - lo) * self.f64()
    }
    pub fn log_range(&mut self, lo: f64, hi: f64) -> f64 {
        (lo.ln() + (hi.ln() - lo.ln()) * self.f64()).exp()
    }
    /// Approximately normal(0, 1) (sum of four uniforms, scaled).
    pub fn normal(&mut self) -> f64 {
        let s: f64 = (0..4).map(|_| self.f64()).sum::<f64>() - 2.0;
        s * (3.0f64).sqrt()
    }
    pub fn below(&mut self, n: u64) -> u64 {
        self.next_u64() % n.max(1)
    }
}

/// FNV-1a over bytes, for contributor blocks.
fn fnv1a(bytes: &[u8]) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for b in bytes {
        h ^= *b as u64;
        h = h.wrapping_mul(0x0000_0100_0000_01b3);
    }
    h
}

/// First job number of a contributor's block. Logins are case-insensitive.
pub fn contributor_base(login: &str) -> u64 {
    let h = fnv1a(login.trim().to_lowercase().as_bytes()) % (1u64 << 20);
    h << BLOCK_BITS
}

/// The `k`-th job of a contributor's block.
pub fn contributor_job(login: &str, k: u64) -> u64 {
    contributor_base(login) + (k % (1u64 << BLOCK_BITS))
}

fn example_seed(job: u64, index: u32) -> u64 {
    let mut r = Rng::new(job ^ ((GENERATOR_VERSION as u64) << 56));
    let a = r.next_u64();
    let mut r2 = Rng::new(a ^ (index as u64).wrapping_mul(0xA24B_AED4_963E_E407));
    r2.next_u64()
}

// --------------------------------------------------------------- inputs ----

/// Everything that determines one example's solve.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ExampleInputs {
    pub job: u64,
    pub index: u32,
    pub board: String,
    /// Pot type the pot was drawn from (limped, srp, 3bet, 4bet).
    pub pot_type: String,
    pub pot_bb: f64,
    /// Effective stack behind at the flop, in bb.
    pub stack_bb: f64,
    pub rake_pct: f64,
    pub rake_cap_bb: f64,
    /// 169-class range weights (preflop class index), 0 = OOP, 1 = IP.
    /// Rounded to 3 decimals so the range text round-trips exactly.
    pub range: [Vec<f32>; 2],
}

/// Strength score used only to order classes for range sampling.
fn class_strength(k: usize) -> f64 {
    let (hi, lo, suited) = class_parts(k);
    let (h, l) = (hi as f64, lo as f64);
    if hi == lo {
        return 10.0 + 2.2 * h;
    }
    let gap = (h - l - 1.0).max(0.0);
    let mut s = 1.6 * h + 0.75 * l - 0.9 * gap.min(4.0);
    if suited {
        s += 3.0;
    }
    if hi == 12 {
        s += 2.5; // any ace
    }
    s
}

fn combos(k: usize) -> f64 {
    let (hi, lo, suited) = class_parts(k);
    if hi == lo {
        6.0
    } else if suited {
        4.0
    } else {
        12.0
    }
}

/// Classes ordered strongest first, with per-range noise on the scores.
fn noisy_order(rng: &mut Rng, noise: f64) -> Vec<usize> {
    let mut scored: Vec<(f64, usize)> = (0..NUM_CLASSES)
        .map(|k| (class_strength(k) + noise * rng.normal(), k))
        .collect();
    scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap().then(a.1.cmp(&b.1)));
    scored.into_iter().map(|x| x.1).collect()
}

/// Top `frac` of combos in `order` get weight 1, with a soft edge.
fn threshold_weights(order: &[usize], frac: f64, edge: f64) -> Vec<f64> {
    let total: f64 = order.iter().map(|&k| combos(k)).sum();
    let mut w = vec![0f64; NUM_CLASSES];
    let mut cum = 0.0;
    for &k in order {
        let mid = (cum + combos(k) / 2.0) / total; // position in [0, 1]
        cum += combos(k);
        let x = if edge <= 1e-9 {
            if mid <= frac { 1.0 } else { 0.0 }
        } else {
            (0.5 - (mid - frac) / edge).clamp(0.0, 1.0)
        };
        w[k] = x;
    }
    w
}

/// DeepStack-style recursive split of probability mass over ordered classes.
/// `spread` in (0, 1] scales how lopsided each split may be: 1 is
/// DeepStack's uniform split (spiky ranges), small values give smooth ones.
fn recursive_weights(rng: &mut Rng, order: &[usize]) -> Vec<f64> {
    fn split(rng: &mut Rng, order: &[usize], mass: f64, spread: f64, out: &mut [f64]) {
        if order.len() == 1 {
            out[order[0]] = mass / combos(order[0]);
            return;
        }
        let mid = order.len() / 2;
        let u = 0.5 + (rng.f64() - 0.5) * spread;
        split(rng, &order[..mid], mass * u, spread, out);
        split(rng, &order[mid..], mass * (1.0 - u), spread, out);
    }
    let spread = rng.range(0.15, 1.0);
    let mut w = vec![0f64; NUM_CLASSES];
    split(rng, order, 1.0, spread, &mut w);
    w
}

/// One random 169-class range, normalized so its largest weight is 1.
pub fn sample_range(rng: &mut Rng) -> Vec<f32> {
    let pick = rng.f64();
    let noise = rng.range(0.0, 4.0);
    let order = noisy_order(rng, noise);
    let mut w = if pick < 0.40 {
        // linear or capped "top x%" range
        let frac = rng.log_range(0.03, 0.9);
        let edge = rng.range(0.0, 0.15);
        let mut w = threshold_weights(&order, frac, edge);
        if rng.f64() < 0.4 {
            // capped: thin out the very top (flatting ranges)
            let top = threshold_weights(&order, frac * rng.range(0.05, 0.35), 0.0);
            let keep = rng.range(0.0, 0.5);
            for k in 0..NUM_CLASSES {
                if top[k] > 0.0 {
                    w[k] *= keep;
                }
            }
        }
        w
    } else if pick < 0.80 {
        recursive_weights(rng, &order)
    } else if pick < 0.90 {
        // polarized: a value block plus a bluff block lower down
        let value = rng.log_range(0.03, 0.3);
        let bluff_lo = value + rng.range(0.1, 0.5);
        let bluff_hi = (bluff_lo + rng.range(0.03, 0.2)).min(1.0);
        let a = threshold_weights(&order, value, 0.02);
        let b = threshold_weights(&order, bluff_hi, 0.02);
        let c = threshold_weights(&order, bluff_lo, 0.02);
        let bw = rng.range(0.2, 1.0);
        (0..NUM_CLASSES)
            .map(|k| a[k] + bw * (b[k] - c[k]).max(0.0))
            .collect()
    } else {
        // noisy mixed frequencies inside a threshold
        let frac = rng.log_range(0.1, 1.0);
        let base = threshold_weights(&order, frac, 0.1);
        let p = rng.range(1.0, 4.0);
        (0..NUM_CLASSES).map(|k| base[k] * rng.f64().powf(p)).collect()
    };
    let max = w.iter().cloned().fold(0.0f64, f64::max);
    if max <= 0.0 {
        w = vec![1.0; NUM_CLASSES];
    } else {
        for x in w.iter_mut() {
            *x /= max;
        }
    }
    // Round to 3 decimals; tiny weights become 0 so the range text stays short.
    w.iter()
        .map(|&x| {
            let r = (x * 1000.0).round() / 1000.0;
            if r < 0.005 { 0.0 } else { r as f32 }
        })
        .collect()
}

/// Range text for a 169-class weight vector (classes with weight 0 omitted).
pub fn range_text(w: &[f32]) -> String {
    let mut parts = Vec::new();
    for (k, &x) in w.iter().enumerate() {
        if x <= 0.0 {
            continue;
        }
        if x >= 0.9995 {
            parts.push(class_label(k));
        } else {
            parts.push(format!("{}:{}", class_label(k), x));
        }
    }
    parts.join(",")
}

/// The inputs of example `index` of job `job`.
pub fn example_inputs(job: u64, index: u32) -> ExampleInputs {
    let mut rng = Rng::new(example_seed(job, index));
    // Pot type: (name, probability, pot range in bb)
    let types: [(&str, f64, f64, f64); 4] = [
        ("limped", 0.15, 2.0, 3.5),
        ("srp", 0.45, 4.5, 7.5),
        ("3bet", 0.28, 15.0, 26.0),
        ("4bet", 0.12, 38.0, 55.0),
    ];
    let u = rng.f64();
    let mut acc = 0.0;
    let mut chosen = types[1];
    for t in types {
        acc += t.1;
        if u < acc {
            chosen = t;
            break;
        }
    }
    let pot_bb = round2(rng.range(chosen.2, chosen.3));
    // starting stack (bb) log-uniform; each player put in half the pot
    let mut start = rng.log_range(25.0, 200.0);
    if start - pot_bb / 2.0 < 2.0 {
        start = pot_bb / 2.0 + rng.range(2.0, 20.0);
    }
    let stack_bb = round2(start - pot_bb / 2.0);
    let (rake_pct, rake_cap_bb) = if rng.f64() < 0.5 { (0.0, 0.0) } else { (0.05, 3.0) };
    let canon = crate::cards::canonical_flops();
    let total: u64 = canon.iter().map(|x| x.1 as u64).sum();
    let mut pick = rng.below(total);
    let mut board = canon[0].0.clone();
    for (b, wt) in &canon {
        if pick < *wt as u64 {
            board = b.clone();
            break;
        }
        pick -= *wt as u64;
    }
    let range = [sample_range(&mut rng), sample_range(&mut rng)];
    ExampleInputs {
        job,
        index,
        board,
        pot_type: chosen.0.to_string(),
        pot_bb,
        stack_bb,
        rake_pct,
        rake_cap_bb,
        range,
    }
}

fn round2(x: f64) -> f64 {
    (x * 100.0).round() / 100.0
}

/// The fixed postflop menu: the M5 single-raised-pot menu (flop OOP 33%,
/// IP 33/75%, turn and river 75%, raises 60%).
pub fn menu_tree(pot_bb: f64, stack_bb: f64, rake_pct: f64, rake_cap_bb: f64) -> TreeConfig {
    let json = serde_json::json!({
        "starting_pot": pot_bb * CHIPS_PER_BB,
        "effective_stack": stack_bb * CHIPS_PER_BB,
        "rake_pct": rake_pct,
        "rake_cap": rake_cap_bb * CHIPS_PER_BB,
        "oop": [
            { "bet": [{"PotPct": 33}], "raise": [{"PotPct": 60}], "donk": [] },
            { "bet": [{"PotPct": 75}], "raise": [{"PotPct": 60}], "donk": [] },
            { "bet": [{"PotPct": 75}], "raise": [{"PotPct": 60}], "donk": [] }
        ],
        "ip": [
            { "bet": [{"PotPct": 33}, {"PotPct": 75}], "raise": [{"PotPct": 60}], "donk": [] },
            { "bet": [{"PotPct": 75}], "raise": [{"PotPct": 60}], "donk": [] },
            { "bet": [{"PotPct": 75}], "raise": [{"PotPct": 60}], "donk": [] }
        ],
        "allin_threshold": 0.85,
        "add_allin": false,
        "max_raises": 10
    });
    serde_json::from_value(json).expect("menu json")
}

impl ExampleInputs {
    pub fn spot_config(&self) -> SpotConfig {
        SpotConfig {
            board: self.board.clone(),
            range_oop: range_text(&self.range[0]),
            range_ip: range_text(&self.range[1]),
            tree: menu_tree(self.pot_bb, self.stack_bb, self.rake_pct, self.rake_cap_bb),
        }
    }
}

// -------------------------------------------------------------- outputs ----

/// Per-class results of one solved example, both players.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExampleValues {
    /// Combo mass (range weight after board removal) per class.
    pub reach: [Vec<f32>; 2],
    /// Equity vs the opponent's range per class (null when absent).
    pub eq: [Vec<Option<f32>>; 2],
    /// Value per class as a fraction of the starting pot, pot-share
    /// convention (OOP + IP = 1 minus rake for range averages).
    pub value: [Vec<Option<f32>>; 2],
}

fn r5(x: f64) -> f32 {
    ((x * 100_000.0).round() / 100_000.0) as f32
}

/// Extract per-class values at the root of a solved (symmetric) solver.
pub fn extract_values(solver: &Solver) -> Result<ExampleValues, String> {
    let view = solver.node_view(&[])?;
    let pot = solver.spot.tree.config.starting_pot;
    let mut reach: [Vec<f32>; 2] = [vec![0.0; NUM_CLASSES], vec![0.0; NUM_CLASSES]];
    let mut eq: [Vec<Option<f32>>; 2] = [vec![None; NUM_CLASSES], vec![None; NUM_CLASSES]];
    let mut value: [Vec<Option<f32>>; 2] = [vec![None; NUM_CLASSES], vec![None; NUM_CLASSES]];
    for p in 0..2usize {
        let mut w = vec![0f64; NUM_CLASSES];
        let mut wv = vec![0f64; NUM_CLASSES];
        let mut se = vec![0f64; NUM_CLASSES];
        let mut sv = vec![0f64; NUM_CLASSES];
        for h in &view.players[p].hands {
            let (r1, r2) = (rank(h.c1), rank(h.c2));
            let k = class_index(r1.max(r2), r1.min(r2), suit(h.c1) == suit(h.c2));
            w[k] += h.reach as f64;
            let (e, v) = match (h.eq, h.ev) {
                (Some(a), Some(b)) if a.is_finite() && b.is_finite() => (a as f64, b as f64),
                _ => continue,
            };
            // per-hand values are normalized by valid: aggregate by reach x valid
            let pw = h.reach as f64 * h.valid as f64;
            wv[k] += pw;
            se[k] += pw * e;
            sv[k] += pw * v;
        }
        for k in 0..NUM_CLASSES {
            reach[p][k] = r5(w[k]);
            if wv[k] > 0.0 {
                eq[p][k] = Some(r5(se[k] / wv[k]));
                value[p][k] = Some(r5(sv[k] / wv[k] / pot));
            }
        }
    }
    Ok(ExampleValues { reach, eq, value })
}

/// One line of an output file.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExampleRecord {
    #[serde(rename = "type")]
    pub kind: String,
    #[serde(flatten)]
    pub inputs: ExampleInputs,
    #[serde(flatten)]
    pub values: ExampleValues,
    pub iterations: u32,
    pub exploit_pct_pot: f64,
    pub seconds: f64,
}

/// File header line.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JobHeader {
    #[serde(rename = "type")]
    pub kind: String,
    pub format: String,
    pub format_version: u32,
    pub generator_version: u32,
    pub menu: String,
    pub job: u64,
    pub contributor: String,
    pub examples: u32,
    pub target_pct: f64,
    pub max_iterations: u32,
    pub engine: String,
    pub gtopen_version: String,
}

impl JobHeader {
    pub fn new(job: u64, contributor: &str, examples: u32, target_pct: f64, max_iterations: u32, engine: &str) -> Self {
        JobHeader {
            kind: "header".into(),
            format: FORMAT.into(),
            format_version: FORMAT_VERSION,
            generator_version: GENERATOR_VERSION,
            menu: MENU.into(),
            job,
            contributor: contributor.into(),
            examples,
            target_pct,
            max_iterations,
            engine: engine.into(),
            gtopen_version: env!("CARGO_PKG_VERSION").into(),
        }
    }
}

/// Comparison of a re-solve against an uploaded example.
#[derive(Debug, Clone, Serialize)]
pub struct VerifyResult {
    pub index: u32,
    /// Reach-weighted mean |value difference| over both players, in pot.
    pub mean_abs_diff: f64,
    /// Largest |value difference| among classes with reach >= 5% of the max.
    pub max_abs_diff: f64,
}

/// Compare two value sets (same inputs).
pub fn compare_values(a: &ExampleValues, b: &ExampleValues) -> (f64, f64) {
    let (mut num, mut den, mut max) = (0f64, 0f64, 0f64);
    for p in 0..2 {
        let rmax = a.reach[p].iter().cloned().fold(0f32, f32::max) as f64;
        for k in 0..NUM_CLASSES {
            if let (Some(x), Some(y)) = (a.value[p][k], b.value[p][k]) {
                let r = a.reach[p][k] as f64;
                let d = (x as f64 - y as f64).abs();
                num += r * d;
                den += r;
                if r >= 0.05 * rmax {
                    max = max.max(d);
                }
            }
        }
    }
    (if den > 0.0 { num / den } else { 0.0 }, max)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn inputs_are_deterministic_and_vary() {
        let a = example_inputs(42, 7);
        let b = example_inputs(42, 7);
        assert_eq!(a, b);
        let c = example_inputs(42, 8);
        assert_ne!(a.range, c.range);
        let d = example_inputs(43, 7);
        assert_ne!(a.range, d.range);
    }

    #[test]
    fn ranges_round_trip_through_text() {
        for i in 0..50 {
            let ex = example_inputs(1, i);
            for p in 0..2 {
                let text = range_text(&ex.range[p]);
                let parsed = crate::Range::parse(&text).expect("range parses");
                assert!(!parsed.is_empty(), "empty range for example {i}");
                // every class keeps its weight exactly
                for k in 0..NUM_CLASSES {
                    let (hi, lo, suited) = class_parts(k);
                    let s = if hi == lo {
                        crate::range::Suitedness::Pair
                    } else if suited {
                        crate::range::Suitedness::Suited
                    } else {
                        crate::range::Suitedness::Offsuit
                    };
                    for (c1, c2) in crate::range::class_combo_list(hi, lo, s) {
                        let w = parsed.weights[crate::cards::combo_index(c1, c2)];
                        assert_eq!(w, ex.range[p][k], "class {} example {i}", class_label(k));
                    }
                }
            }
        }
    }

    #[test]
    fn spots_are_valid() {
        for i in 0..20 {
            let ex = example_inputs(9, i);
            assert!(ex.pot_bb > 0.0 && ex.stack_bb > 0.0);
            let spot = crate::Spot::new(ex.spot_config());
            assert!(spot.is_ok(), "example {i}: {:?}", spot.err());
        }
    }

    #[test]
    fn contributor_blocks_differ() {
        assert_ne!(contributor_base("alice"), contributor_base("bob"));
        assert_eq!(contributor_base("Alice"), contributor_base("alice"));
        assert_eq!(contributor_job("alice", 3), contributor_base("alice") + 3);
    }

    #[test]
    fn river_example_values_are_consistent() {
        // A tiny river spot: values for both players must add up to 1 (no rake).
        let cfg = SpotConfig {
            board: "AsKd7c2h3s".into(),
            range_oop: "QQ,JJ,AQs".into(),
            range_ip: "TT,AJs,KQs".into(),
            tree: menu_tree(10.0, 50.0, 0.0, 0.0),
        };
        let spot = std::sync::Arc::new(crate::Spot::new(cfg).unwrap());
        let mut solver = Solver::new(spot);
        let stop = std::sync::atomic::AtomicBool::new(false);
        solver.run(
            &crate::RunOptions { max_iterations: 300, target_exploit_pct: 0.05, check_every: 50 },
            &stop,
            |_| {},
        );
        solver.ensure_symmetric();
        let v = extract_values(&solver).unwrap();
        let mut total = 0.0;
        for p in 0..2 {
            let (mut num, mut den) = (0.0, 0.0);
            for k in 0..NUM_CLASSES {
                if let Some(x) = v.value[p][k] {
                    num += v.reach[p][k] as f64 * x as f64;
                    den += v.reach[p][k] as f64;
                }
            }
            total += num / den;
        }
        // range averages weighted by plain reach are close but not exact
        // (card removal); they should still land near 1
        assert!((total - 1.0).abs() < 0.15, "total {total}");
    }
}
