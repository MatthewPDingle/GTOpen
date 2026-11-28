//! Three-player flop values: what a flop is worth to each of three players.
//!
//! The Preflop Lab prices a flop with three players in the hand as showdown
//! equity: no position, no betting (`preflop::multiway`). Every example here
//! is one exact three-player flop solve (`crate::multiway`): three random
//! 169-class ranges, a pot, a stack, a rake and a flop go in; each class's
//! solved value (pot-share convention, as a fraction of the starting pot),
//! equity and reach mass for the three players come out. The same idea as
//! the heads-up pool (`crate::datagen`), one player more, and pooled the
//! same way: a game mix with `"players": 3` (`crate::datagen_mix`) has the
//! generator write jobs of these, fully determined by (mix, job, index, cap).

use serde::{Deserialize, Serialize};

use crate::{
    cards::{card_mask, combo_from_index, parse_cards, rank, suit, NUM_COMBOS},
    datagen::{range_text, CHIPS_PER_BB},
    multiway::{
        eval::{compatible_mass, showdown_equity},
        tree::MwTreeBuilder,
        MwSpot, MwSpotConfig, MwTreeConfig, NP,
    },
    preflop::equity::{class_index, NUM_CLASSES},
    tree::{BetSize, StreetSizing},
};

/// Format name written in the header of a three-player job file.
pub const FORMAT3: &str = "gtopen-flop-values-3p";
/// Version of the file layout.
pub const FORMAT3_VERSION: u32 = 1;
/// Name of the fixed postflop bet menu (see [`menu_tree3`]).
pub const MENU3: &str = "lean3-v1";
/// The first generator that solves three-player mixes.
pub const PLAYERS3_GENERATOR: u32 = 7;
/// Default examples per three-player job: these solves take minutes each,
/// and a job only goes up when it is complete.
pub const DEFAULT_PER_JOB3: u32 = 10;

/// Everything that determines one example's solve.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Inputs3 {
    pub job: u64,
    pub index: u32,
    pub board: String,
    /// limped, srp, 3bet or 4bet.
    pub pot_type: String,
    pub pot_bb: f64,
    /// Chips behind at the flop, the same for the three players, in bb.
    pub stack_bb: f64,
    /// Rake as a fraction of the pot (0.05 = 5%).
    pub rake_pct: f64,
    pub rake_cap_bb: f64,
    /// 169-class range weights (preflop class index) in postflop action
    /// order: 0 acts first on every street, 2 last.
    pub range: [Vec<f32>; NP],
    /// Draws rejected before this one (see `datagen::ExampleInputs::attempt`).
    #[serde(default)]
    pub attempt: u32,
    #[serde(default = "one", skip_serializing_if = "is_one")]
    pub pot_scale: f64,
}

fn one() -> f64 {
    1.0
}

fn is_one(x: &f64) -> bool {
    *x == 1.0
}

/// The fixed three-player menu `lean3-v1`: the heads-up pool's `lean-v2`
/// sizes for all three players (one bet size per street: flop 33%, turn and
/// river 75%; raises to 60% of the pot; all-in when a raise commits 85% of a
/// stack), with one raise per street on the flop and the turn and none on
/// the river. A three-player tree is far bigger than a heads-up one: with
/// river raises a 100 bb single-raised pot needs 50 GB at 1,000 hands a
/// player, without them 31 GB, which a 32 GB card holds for ordinary ranges.
pub fn menu_tree3(pot_bb: f64, stack_bb: f64, rake_pct: f64, rake_cap_bb: f64) -> MwTreeConfig {
    let street = |bet: f64, raise: bool| StreetSizing {
        bet: vec![BetSize::PotPct(bet)],
        raise: if raise {
            vec![BetSize::PotPct(60.0)]
        } else {
            Vec::new()
        },
        donk: Vec::new(),
    };
    let streets = [street(33.0, true), street(75.0, true), street(75.0, false)];
    let mut t = MwTreeConfig::uniform(pot_bb * CHIPS_PER_BB, stack_bb * CHIPS_PER_BB, &[], &[]);
    t.rake_pct = rake_pct;
    t.rake_cap = rake_cap_bb * CHIPS_PER_BB;
    t.sizing = std::array::from_fn(|_| streets.clone());
    t.allin_threshold = 0.85;
    t.add_allin = false;
    t.max_raises = 1;
    t
}

impl Inputs3 {
    pub fn spot_config(&self) -> MwSpotConfig {
        MwSpotConfig {
            board: self.board.clone(),
            ranges: std::array::from_fn(|p| range_text(&self.range[p])),
            tree: menu_tree3(self.pot_bb, self.stack_bb, self.rake_pct, self.rake_cap_bb),
            seats: None,
        }
    }

    /// Hands each player holds on the board (combos of its classes that do
    /// not touch a board card).
    pub fn hand_counts(&self) -> Result<[usize; NP], String> {
        let board = parse_cards(&self.board)?;
        let mask = board.iter().fold(0u64, |m, &c| m | card_mask(c));
        let mut n = [0usize; NP];
        for idx in 0..NUM_COMBOS {
            let (c1, c2) = combo_from_index(idx);
            if (card_mask(c1) | card_mask(c2)) & mask != 0 {
                continue;
            }
            let (r1, r2) = (rank(c1), rank(c2));
            let k = class_index(r1.max(r2), r1.min(r2), suit(c1) == suit(c2));
            for p in 0..NP {
                if self.range[p].get(k).copied().unwrap_or(0.0) > 0.0 {
                    n[p] += 1;
                }
            }
        }
        Ok(n)
    }

    /// (decisions x hands over the tree, nodes): what the solve stores, from
    /// the betting tree alone (no solver is built).
    pub fn tree_size(&self) -> Result<(u64, u64), String> {
        let board = parse_cards(&self.board)?;
        if board.len() != 3 {
            return Err("a flop has three cards".into());
        }
        let mask = board.iter().fold(0u64, |m, &c| m | card_mask(c));
        let nh = self.hand_counts()?;
        if nh.iter().any(|&n| n == 0) {
            return Err("a range has no hand left on this flop".into());
        }
        let tree = MwTreeBuilder::build(&self.spot_config().tree, mask, 0, nh, None)?;
        Ok((tree.data_size.iter().sum(), tree.nodes.len() as u64))
    }
}

/// Estimated GPU memory of an example's solve, in bytes: the 16-bit arenas
/// the card must hold (4 bytes per entry and 16 per node), a tenth more for
/// the working buffers of the part being swept, and a fixed gigabyte. A card
/// draws the examples whose estimate fits its cap; `u64::MAX` when the tree
/// cannot be built.
pub fn estimated_vram_bytes3(ex: &Inputs3) -> u64 {
    match ex.tree_size() {
        Ok((entries, nodes)) => {
            let arenas = entries
                .saturating_mul(4)
                .saturating_add(nodes.saturating_mul(16));
            arenas
                .saturating_add(arenas / 10)
                .saturating_add(1_000_000_000)
        }
        Err(_) => u64::MAX,
    }
}

/// Per-class results of one solved example, the three players in order.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Values3 {
    /// Combo mass (range weight after board removal) per class.
    pub reach: [Vec<f32>; NP],
    /// Showdown equity against the other two ranges per class (null when
    /// the class is absent or blocked).
    pub eq: [Vec<Option<f32>>; NP],
    /// Value per class as a fraction of the starting pot, pot-share
    /// convention (the three range averages add up to 1 minus the rake).
    pub value: [Vec<Option<f32>>; NP],
}

fn r5(x: f64) -> f32 {
    ((x * 100_000.0).round() / 100_000.0) as f32
}

/// Per-class values from each player's counterfactual value per hand at the
/// root (`MwSolver::node_values(0, p, weights, ..)` or the GPU solver's
/// `root_values_all`).
pub fn class_values(spot: &MwSpot, cfv: &[Vec<f32>; NP]) -> Values3 {
    let w = &spot.weights;
    let reach_all = [&w[0][..], &w[1][..], &w[2][..]];
    let pot = spot.tree.config.starting_pot;
    let put = spot.tree.root_put();
    let mut reach: [Vec<f32>; NP] = std::array::from_fn(|_| vec![0.0; NUM_CLASSES]);
    let mut eq: [Vec<Option<f32>>; NP] = std::array::from_fn(|_| vec![None; NUM_CLASSES]);
    let mut value: [Vec<Option<f32>>; NP] = std::array::from_fn(|_| vec![None; NUM_CLASSES]);
    for p in 0..NP {
        let nh = spot.hands[p].len();
        let mut mass = vec![0f32; nh];
        compatible_mass(spot, p, reach_all, &mut mass);
        let equity = showdown_equity(spot, 0b111, &[], p, reach_all, &mass);
        let mut cw = vec![0f64; NUM_CLASSES];
        let mut wv = vec![0f64; NUM_CLASSES];
        let mut se = vec![0f64; NUM_CLASSES];
        let mut sv = vec![0f64; NUM_CLASSES];
        for i in 0..nh {
            let h = &spot.hands[p][i];
            let (r1, r2) = (rank(h.c1), rank(h.c2));
            let k = class_index(r1.max(r2), r1.min(r2), suit(h.c1) == suit(h.c2));
            cw[k] += h.weight as f64;
            if !(mass[i] > 0.0) || !equity[i].is_finite() || !cfv[p][i].is_finite() {
                continue;
            }
            // per-hand values are per unit of compatible opponent mass:
            // a class averages them by reach x that mass
            let pw = h.weight as f64 * mass[i] as f64;
            wv[k] += pw;
            se[k] += pw * equity[i] as f64;
            sv[k] += pw * (cfv[p][i] as f64 / mass[i] as f64 + put);
        }
        for k in 0..NUM_CLASSES {
            reach[p][k] = r5(cw[k]);
            if wv[k] > 0.0 {
                eq[p][k] = Some(r5(se[k] / wv[k]));
                value[p][k] = Some(r5(sv[k] / wv[k] / pot));
            }
        }
    }
    Values3 { reach, eq, value }
}

/// One solved example: a line of a three-player job file.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Record3 {
    #[serde(rename = "type")]
    pub kind: String,
    #[serde(flatten)]
    pub inputs: Inputs3,
    #[serde(flatten)]
    pub values: Values3,
    pub iterations: u32,
    /// Mean of the three players' best-response gaps, in % of the pot.
    pub exploit_pct_pot: f64,
    /// Each player's own gap, in % of the pot.
    pub gaps_pct_pot: [f64; NP],
    /// How the solve ended: "target", "iterations" or "time".
    pub ended: String,
    pub seconds: f64,
    /// [`estimated_vram_bytes3`] of the example, drawn again when it is checked.
    pub tree_bytes: u64,
}

/// An example its machine could not solve (its tree did not fit the card
/// beside whatever else was running): a line of a three-player job file in
/// the place of the example, so the job still has one line per index.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Skipped3 {
    #[serde(rename = "type")]
    pub kind: String,
    pub job: u64,
    pub index: u32,
    pub reason: String,
}

/// Mean and largest absolute difference between two solves' class values,
/// in fractions of the pot, over the classes both hold: the mean weighted
/// by reach, the largest among classes with at least 5% of their player's
/// biggest reach (as `datagen::compare_values`).
pub fn compare_values3(a: &Values3, b: &Values3) -> (f64, f64) {
    let (mut sum, mut wsum, mut max) = (0f64, 0f64, 0f64);
    for p in 0..NP {
        let top = a.reach[p].iter().cloned().fold(0f32, f32::max) as f64;
        for k in 0..NUM_CLASSES {
            if let (Some(x), Some(y)) = (a.value[p][k], b.value[p][k]) {
                let d = (x as f64 - y as f64).abs();
                let w = a.reach[p][k] as f64;
                sum += w * d;
                wsum += w;
                if w >= 0.05 * top {
                    max = max.max(d);
                }
            }
        }
    }
    (if wsum > 0.0 { sum / wsum } else { 0.0 }, max)
}

/// Percent of the card a three-player solve plans for at most. A solve takes
/// what it may (a bigger plan is a faster one), the desktop and other
/// programs hold a few GB, and a card filled past its memory spills into
/// system memory, where a solve runs ten times slower (measured on a 32 GB
/// card: 88% left no room and an hour-long solve). `--reserve-gb` is kept
/// out of the memory that is free when the solve starts, so it only lowers
/// the plan where less than that would otherwise stay free.
pub const CARD_SHARE: u64 = 80;

/// Bytes a three-player solve may plan for: the free memory less 1 GB and
/// the reserve, and at most [`CARD_SHARE`] of the card (memory in MB).
pub fn plan_budget(free_mb: u64, total_mb: u64, reserve_gb: f64) -> u64 {
    free_mb
        .saturating_sub(1024 + (reserve_gb * 1000.0) as u64)
        .min(total_mb * CARD_SHARE / 100)
        * 1_000_000
}

/// What the three range averages of a record may add up to, in starting
/// pots: `(lowest, highest)`.
///
/// The averages weigh a class by its reach, which ignores card removal
/// between the ranges, so even without rake they miss the pot, and by more
/// the deeper the stacks (a class's value spans about stack / pot pots):
/// 203 pool solves were off by 0.12 at most, at 40 pots deep. Rake is
/// charged on the pot at the end of the hand, not on the starting pot, so it
/// can take up to its cap, or its share of the pot and all three stacks: a
/// 10% rake capped at 8.5 bb takes more than a 7.9 bb starting pot when the
/// money goes in.
pub fn total_span(ex: &Inputs3) -> (f64, f64) {
    let slack = 0.15 + 0.01 * ex.stack_bb / ex.pot_bb;
    let mut rake = ex.rake_pct * (ex.pot_bb + NP as f64 * ex.stack_bb);
    if ex.rake_cap_bb > 0.0 {
        rake = rake.min(ex.rake_cap_bb);
    }
    (1.0 - rake / ex.pot_bb - slack, 1.0 + slack)
}

/// Checks a record's numbers for plausibility (None = fine).
pub fn sanity3(r: &Record3) -> Option<String> {
    let ex = &r.inputs;
    if !(ex.pot_bb > 0.0 && ex.stack_bb > 0.0) || !(0.0..=0.25).contains(&ex.rake_pct) {
        return Some("pot, stack or rake out of range".into());
    }
    let mut total = 0f64;
    for p in 0..NP {
        let v = &r.values;
        if v.reach[p].len() != NUM_CLASSES
            || v.eq[p].len() != NUM_CLASSES
            || v.value[p].len() != NUM_CLASSES
            || ex.range[p].len() != NUM_CLASSES
        {
            return Some("a list is not 169 long".into());
        }
        let (mut wsum, mut vsum) = (0f64, 0f64);
        for k in 0..NUM_CLASSES {
            let held = ex.range[p][k] > 0.0;
            if (v.reach[p][k] > 0.0) && !held {
                return Some(format!("player {p} class {k}: reach without range weight"));
            }
            if let Some(e) = v.eq[p][k] {
                if !(-1e-4..=1.0001).contains(&(e as f64)) {
                    return Some(format!("player {p} class {k}: equity {e}"));
                }
            }
            if let Some(x) = v.value[p][k] {
                // nobody wins more than the pot plus both other stacks, or loses more than its own stack
                let hi = 1.0 + 2.0 * ex.stack_bb / ex.pot_bb + 1e-3;
                let lo = -ex.stack_bb / ex.pot_bb - 1e-3;
                if !x.is_finite() || (x as f64) > hi || (x as f64) < lo {
                    return Some(format!(
                        "player {p} class {k}: value {x} outside {lo:.3} to {hi:.3}"
                    ));
                }
                wsum += v.reach[p][k] as f64;
                vsum += v.reach[p][k] as f64 * x as f64;
            }
        }
        if !(wsum > 0.0) {
            return Some(format!("player {p} has no values"));
        }
        total += vsum / wsum;
    }
    let (lowest, highest) = total_span(ex);
    if !(lowest..=highest).contains(&total) {
        return Some(format!("the three range values add up to {total:.3} of the pot ({lowest:.3} to {highest:.3} expected)"));
    }
    if !(r.exploit_pct_pot.is_finite() && r.exploit_pct_pot >= 0.0)
        || r.gaps_pct_pot.iter().any(|g| !(g.is_finite() && *g >= 0.0))
    {
        return Some("bad exploitability".into());
    }
    None
}

#[cfg(test)]
mod tests {
    use std::sync::Arc;

    use super::*;
    use crate::{
        multiway::{solver::Dealt, MwSolver},
        store::Storage,
    };

    pub(crate) fn narrow() -> Inputs3 {
        let mut range: [Vec<f32>; NP] = std::array::from_fn(|_| vec![0f32; NUM_CLASSES]);
        for (p, text) in ["AA,AKs,QJs,77", "QQ,KQs,98s,66", "TT,AJs,87s,55"]
            .iter()
            .enumerate()
        {
            let r = crate::range::Range::parse(text).unwrap();
            for idx in 0..NUM_COMBOS {
                if r.weights[idx] > 0.0 {
                    let (c1, c2) = combo_from_index(idx);
                    let (r1, r2) = (rank(c1), rank(c2));
                    range[p][class_index(r1.max(r2), r1.min(r2), suit(c1) == suit(c2))] = 1.0;
                }
            }
        }
        // narrow ranges and a short stack: a tree small enough for a test
        Inputs3 {
            job: 1,
            index: 0,
            board: "Ks7d2c".into(),
            pot_type: "3bet".into(),
            pot_bb: 9.0,
            stack_bb: 4.0,
            rake_pct: 0.0,
            rake_cap_bb: 0.0,
            range,
            attempt: 0,
            pot_scale: 1.0,
        }
    }

    #[test]
    fn menu_has_no_river_raise_and_sizes_follow_the_ranges() {
        let ex = narrow();
        let cfg = ex.spot_config();
        assert_eq!(cfg.tree.max_raises, 1);
        assert!(cfg
            .tree
            .sizing
            .iter()
            .all(|s| !s[0].raise.is_empty() && !s[1].raise.is_empty() && s[2].raise.is_empty()));
        assert_eq!(cfg.tree.starting_pot, ex.pot_bb * CHIPS_PER_BB);
        let spot = MwSpot::new(cfg).unwrap();
        let nh = ex.hand_counts().unwrap();
        assert_eq!(nh, std::array::from_fn(|p| spot.hands[p].len()));
        let (entries, nodes) = ex.tree_size().unwrap();
        assert_eq!(entries, spot.tree.data_size.iter().sum::<u64>());
        assert_eq!(nodes, spot.tree.nodes.len() as u64);
        assert!(estimated_vram_bytes3(&ex) > entries * 4);
        // a wider range makes a bigger tree
        let mut wide = ex.clone();
        wide.range[0] = vec![1.0; NUM_CLASSES];
        assert!(estimated_vram_bytes3(&wide) > estimated_vram_bytes3(&ex));
    }

    #[test]
    fn class_values_share_the_pot() {
        let ex = narrow();
        let spot = Arc::new(MwSpot::new(ex.spot_config()).unwrap());
        let mut s = MwSolver::new(spot.clone(), Storage::F32);
        for _ in 0..15 {
            s.iterate();
        }
        let w = &spot.weights;
        let reach = [&w[0][..], &w[1][..], &w[2][..]];
        let cfv: [Vec<f32>; NP] =
            std::array::from_fn(|p| s.node_values(0, p, reach, Dealt::default(), false));
        let v = class_values(&spot, &cfv);
        // without rake the three range averages add up to the pot
        let (evs, gaps) = s.exploitability();
        let pot = spot.tree.config.starting_pot;
        let total: f64 = evs.iter().map(|e| e + spot.tree.root_put()).sum();
        assert!((total / pot - 1.0).abs() < 1e-3, "{total} of {pot}");
        for p in 0..NP {
            // equities and values exist exactly for the classes in the range
            for k in 0..NUM_CLASSES {
                assert_eq!(v.reach[p][k] > 0.0, ex.range[p][k] > 0.0);
                assert_eq!(v.value[p][k].is_some(), v.reach[p][k] > 0.0);
                if let Some(e) = v.eq[p][k] {
                    assert!((0.0..=1.0).contains(&e));
                }
            }
            let avg = (evs[p] + spot.tree.root_put()) / pot;
            let best = v.value[p]
                .iter()
                .flatten()
                .cloned()
                .fold(f32::MIN, f32::max) as f64;
            let worst = v.value[p]
                .iter()
                .flatten()
                .cloned()
                .fold(f32::MAX, f32::min) as f64;
            assert!(
                worst <= avg + 1e-3 && avg <= best + 1e-3,
                "player {p}: {worst} {avg} {best}"
            );
        }
        let rec = Record3 {
            kind: "example".into(),
            inputs: ex.clone(),
            values: v.clone(),
            iterations: 15,
            exploit_pct_pot: gaps.iter().sum::<f64>() / 3.0 / pot * 100.0,
            gaps_pct_pot: gaps.map(|g| g / pot * 100.0),
            ended: "iterations".into(),
            seconds: 0.0,
            tree_bytes: estimated_vram_bytes3(&ex),
        };
        assert_eq!(sanity3(&rec), None);
        // the record reads back as written
        let back: Record3 = serde_json::from_str(&serde_json::to_string(&rec).unwrap()).unwrap();
        assert_eq!(back.inputs, rec.inputs);
        assert_eq!(compare_values3(&back.values, &rec.values), (0.0, 0.0));
        // a made-up value is caught
        let mut bad = rec.clone();
        let k = (0..NUM_CLASSES)
            .find(|&k| bad.values.value[0][k].is_some())
            .unwrap();
        bad.values.value[0][k] = Some(9.0);
        assert!(sanity3(&bad).is_some());
        assert!(compare_values3(&bad.values, &rec.values).1 > 1.0);
        // values that hand out two pots are caught, each one being possible on its own
        let mut double = rec.clone();
        for p in 0..NP {
            for x in double.values.value[p].iter_mut().flatten() {
                *x += 1.0 / 3.0;
            }
        }
        assert!(
            sanity3(&double).unwrap().contains("add up to"),
            "{:?}",
            sanity3(&double)
        );
    }

    #[test]
    fn a_plan_leaves_a_fifth_of_the_card_and_the_reserve() {
        const GB: u64 = 1_000_000_000;
        // a free 32 GB card (34,190 MB): four fifths of it, whatever is free
        assert_eq!(plan_budget(31_900, 34_190, 0.0), 27_352 * 1_000_000);
        // a reserve below what stays free anyway changes nothing; a bigger one comes out of the free memory
        assert_eq!(plan_budget(31_900, 34_190, 3.0), 27_352 * 1_000_000);
        assert_eq!(
            plan_budget(31_900, 34_190, 6.0),
            (31_900 - 1024 - 6000) * 1_000_000
        );
        // another program already on the card: what is free, less 1 GB
        assert_eq!(
            plan_budget(12_000, 34_190, 0.0),
            (12_000 - 1024) * 1_000_000
        );
        assert_eq!(plan_budget(5_000, 34_190, 6.0), 0);
        assert!(plan_budget(8_000, 8_590, 0.0) > 6 * GB);
    }

    #[test]
    fn the_total_allows_rake_on_the_final_pot_and_deep_stacks() {
        let span = |pot_bb, stack_bb, rake_pct, rake_cap_bb| {
            total_span(&Inputs3 {
                pot_bb,
                stack_bb,
                rake_pct,
                rake_cap_bb,
                ..narrow()
            })
        };
        let inside = |(lo, hi): (f64, f64), x: f64| lo <= x && x <= hi;
        // two finished pool solves the first rule turned away (jobs ...586 and ...587)
        assert!(inside(span(7.94, 55.06, 0.10, 8.5), 0.6855));
        assert!(inside(span(3.39, 135.43, 0.0, 0.0), 1.1229));
        // without rake nothing can be missing beyond the slack, however deep
        let (lo, hi) = span(10.0, 100.0, 0.0, 0.0);
        assert!(
            (lo - 0.75).abs() < 1e-9 && (hi - 1.25).abs() < 1e-9,
            "{lo} {hi}"
        );
        // the cap bounds what rake can take; without a cap it is the share of all the money
        assert!((span(10.0, 100.0, 0.05, 2.0).0 - (0.75 - 0.2)).abs() < 1e-9);
        assert!((span(10.0, 10.0, 0.05, 0.0).0 - (1.0 - 0.2 - 0.16)).abs() < 1e-9);
        // rake never lets the total pass the pot
        assert_eq!(
            span(10.0, 100.0, 0.05, 2.0).1,
            span(10.0, 100.0, 0.0, 0.0).1
        );
    }
}
