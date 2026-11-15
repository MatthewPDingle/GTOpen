//! What the two players' values at a heads-up flop leaf add up to, and
//! holding the leaf net's output to it ("pinning the total").
//!
//! Whatever is played after the flop, the chips the two players take out of
//! a heads-up flop pot add up to the pot minus the rake taken:
//!
//! - no rake: the whole pot;
//! - the rake on the pot as it stands is already at its cap: the pot minus
//!   the cap;
//! - rake below its cap: it depends on how much more goes in. The total is
//!   at most the pot minus the rake on the pot as it stands, and at least
//!   the pot minus the cap (or minus the rake on the largest pot the stacks
//!   allow, when that is less). A net file can carry a rule fitted on exact
//!   solves for these leaves (header key "total_rule").
//!
//! The identity holds when classes are weighted as hands that can be dealt
//! together: a class counts by its share of its player's range times the
//! share of the other range it does not block (the "dealt" sum,
//! [`Blocking`]). The leaf net is trained on exact solves with real cards,
//! so its values are right, or wrong, under that sum.
//!
//! A preflop solve books something else. It multiplies a class's value at a
//! leaf by the other seat's whole reach mass, blocked or not (the "plain"
//! sum). True values add up to more than the pot under the plain sum where
//! the ranges block each other: about 4% of the pot in 4-bet pots on exact
//! solves of real preflop ranges (2026-11), because the classes that are
//! blocked most are worth most. The balanced model has no such surplus (its
//! shares divide one pot under the plain sum); the learned values do.
//!
//! Three research settings, all off by default ([`LeafBooks`]):
//!
//! - the pin shifts every class of both players by the same amount so that
//!   the dealt sum (or, on request, the plain sum) is the total it must be;
//! - blocking at the leaf books a class by how much of the other range can
//!   be dealt against it (relative to its range's average, so the leaf as a
//!   whole is reached as often as before) and the solve's books show the
//!   dealt sum.
//!
//! None of them changes how a total is split between the players.
use super::equity::{class_parts, NUM_CLASSES};
use super::leafnet::POT_TYPES;
use std::sync::OnceLock;

/// Which leaves have their total pinned (env PREFLOP_LEAF_PIN).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum PinTotal {
    /// The net's output is used as it is.
    #[default]
    Off,
    /// The leaves whose total is known exactly: no rake, or the rake on the
    /// pot as it stands is at its cap. Other leaves are left alone.
    Exact,
    /// Those, and raked leaves below the cap that the net file's fitted
    /// rule covers. Leaves outside the rule's fitted inputs are left alone.
    Rule,
}

impl PinTotal {
    /// The total this setting pins a leaf to, if it pins it.
    pub fn target(self, known: LeafTotal) -> Option<f64> {
        match (self, known) {
            (PinTotal::Off, _) | (_, LeafTotal::Unknown) | (PinTotal::Exact, LeafTotal::Rule(_)) => None,
            (_, LeafTotal::Exact(t)) | (PinTotal::Rule, LeafTotal::Rule(t)) => Some(t),
        }
    }
}

/// Which sum the pin holds to the total (env PREFLOP_LEAF_PIN_SUM).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum PinSum {
    /// Hands that can be dealt together: the values end at their true level.
    #[default]
    Dealt,
    /// The sum the solve books. Its books then add up, but where the ranges
    /// block each other every class sits below its true value.
    Plain,
}

/// The research settings for learned leaves. The default changes nothing.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct LeafBooks {
    pub pin: PinTotal,
    pub sum: PinSum,
    /// Count blocking at the leaf (env PREFLOP_LEAF_BLOCKING). Off, a
    /// class's value is weighted by the other seat's whole reach mass, as at
    /// every other terminal. On, by the share of the other range the class
    /// does not block, relative to its player's range average
    /// ([`Blocking::rel`]): the leaf as a whole is reached as often as
    /// before, hands that block the other range count less there, and the
    /// solve's books show the dealt sum.
    pub blocking: bool,
}

impl LeafBooks {
    /// Env PREFLOP_LEAF_PIN (off | exact | rule), PREFLOP_LEAF_PIN_SUM
    /// (dealt | plain) and PREFLOP_LEAF_BLOCKING (off | on). A value
    /// that is none of these is an error: a typo must not run a long solve
    /// with the setting silently off.
    pub fn from_env() -> Result<Self, String> {
        let get = |key: &str| std::env::var(key).map(|v| v.trim().to_ascii_lowercase()).unwrap_or_default();
        Self::parse(&get("PREFLOP_LEAF_PIN"), &get("PREFLOP_LEAF_PIN_SUM"), &get("PREFLOP_LEAF_BLOCKING"))
    }

    /// The three settings from their names ("" is the default).
    pub fn parse(pin: &str, sum: &str, blocking: &str) -> Result<Self, String> {
        let pin = match pin {
            "" | "off" | "0" => PinTotal::Off,
            "exact" => PinTotal::Exact,
            "rule" => PinTotal::Rule,
            other => return Err(format!("PREFLOP_LEAF_PIN must be off, exact or rule, not \"{other}\"")),
        };
        let sum = match sum {
            "" | "dealt" => PinSum::Dealt,
            "plain" => PinSum::Plain,
            other => return Err(format!("PREFLOP_LEAF_PIN_SUM must be dealt or plain, not \"{other}\"")),
        };
        let blocking = match blocking {
            "" | "off" | "0" => false,
            "on" | "1" => true,
            other => return Err(format!("PREFLOP_LEAF_BLOCKING must be off or on, not \"{other}\"")),
        };
        Ok(LeafBooks { pin, sum, blocking })
    }

    /// Settings that contradict each other or need what the net lacks.
    pub fn check(&self, net_has_rule: bool) -> Result<(), String> {
        if self.pin == PinTotal::Rule && !net_has_rule {
            return Err("PREFLOP_LEAF_PIN=rule needs a leaf net file with a \"total_rule\" in its header".into());
        }
        if self.sum == PinSum::Plain && self.pin == PinTotal::Off {
            return Err("PREFLOP_LEAF_PIN_SUM=plain does nothing without PREFLOP_LEAF_PIN".into());
        }
        if self.sum == PinSum::Plain && self.blocking {
            return Err("PREFLOP_LEAF_PIN_SUM=plain and PREFLOP_LEAF_BLOCKING are two different ways to make the books add up: use one".into());
        }
        Ok(())
    }

    pub fn is_default(&self) -> bool {
        *self == LeafBooks::default()
    }
}

/// What is known about a leaf's total, as a fraction of the pot.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum LeafTotal {
    /// No rake, or the cap is reached: the total is this, whatever is played.
    Exact(f64),
    /// Rake below its cap: the fitted rule's value, held to the bounds.
    Rule(f64),
    /// Rake below its cap (or uncapped) and no rule that covers the leaf.
    Unknown,
}

impl LeafTotal {
    pub fn value(self) -> Option<f64> {
        match self {
            LeafTotal::Exact(t) | LeafTotal::Rule(t) => Some(t),
            LeafTotal::Unknown => None,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuleForm {
    /// total = c0 + c1 k + c2 ln(pot) + c3 ln(stack / pot)
    Linear,
    /// total = 1 - rake - (k - rake) clip(c0 + c1 ln(k / rake) + c2 ln(stack / pot) + c3 ln(pot), 0, 1):
    /// the clipped term is the share taken of the room between the rake on
    /// the pot as it stands and the cap.
    Share,
}

/// A fitted rule for the total of a raked leaf below its cap (the net
/// file's header key "total_rule"; `tools/datagen/leafnet_io.py` documents
/// and checks the same layout). k is the rake cap over the pot; pot and
/// stack (the effective stack behind at the flop) are in bb; the rake is a
/// fraction (0.05 = 5%). One row of four coefficients per pot type.
#[derive(Debug, Clone, PartialEq)]
pub struct TotalRule {
    form: RuleForm,
    coef: [[f64; 4]; 4],
    /// The inputs the rule was fitted on, [lowest, highest] each: rake
    /// fraction, cap over pot, pot in bb, stack over pot. Outside them the
    /// rule says nothing.
    valid: [[f64; 2]; 4],
}

const VALID_KEYS: [&str; 4] = ["rake_frac", "cap_over_pot", "pot_bb", "stack_over_pot"];

impl TotalRule {
    /// The rule in a net file's header, if it has one. A rule that cannot be
    /// read is an error (the file was written wrongly), not a missing rule.
    pub fn from_header(header: &serde_json::Value) -> Result<Option<Self>, String> {
        let Some(rule) = header.get("total_rule").filter(|r| !r.is_null()) else { return Ok(None) };
        let form = match rule.get("form").and_then(|v| v.as_str()) {
            Some("linear") => RuleForm::Linear,
            Some("share") => RuleForm::Share,
            other => return Err(format!("total_rule form must be \"linear\" or \"share\", not {other:?}")),
        };
        let numbers = |v: Option<&serde_json::Value>, n: usize, what: &str| -> Result<Vec<f64>, String> {
            v.and_then(|v| v.as_array())
                .filter(|a| a.len() == n)
                .and_then(|a| a.iter().map(|x| x.as_f64().filter(|x| x.is_finite())).collect::<Option<Vec<f64>>>())
                .ok_or_else(|| format!("total_rule {what} must be {n} numbers"))
        };
        let mut coef = [[0f64; 4]; 4];
        for (t, name) in POT_TYPES.iter().enumerate() {
            coef[t].copy_from_slice(&numbers(rule.get("coef").and_then(|c| c.get(name)), 4, &format!("coef.{name}"))?);
        }
        let mut valid = [[0f64; 2]; 4];
        for (i, key) in VALID_KEYS.iter().enumerate() {
            valid[i].copy_from_slice(&numbers(rule.get("valid").and_then(|c| c.get(key)), 2, &format!("valid.{key}"))?);
            if valid[i][0] > valid[i][1] {
                return Err(format!("total_rule valid.{key} must be [lowest, highest]"));
            }
        }
        Ok(Some(TotalRule { form, coef, valid }))
    }

    /// The rule's total (before the bounds) for a raked leaf below its cap,
    /// or None outside the inputs it was fitted on.
    fn total(&self, pot_type: usize, pot_bb: f64, stack_bb: f64, rake_frac: f64, k: f64) -> Option<f64> {
        let spr = stack_bb / pot_bb;
        let inputs = [rake_frac, k, pot_bb, spr];
        if inputs.iter().zip(&self.valid).any(|(v, r)| *v < r[0] - 1e-9 || *v > r[1] + 1e-9) {
            return None;
        }
        let c = &self.coef[pot_type.min(3)];
        let t = match self.form {
            RuleForm::Linear => c[0] + c[1] * k + c[2] * pot_bb.ln() + c[3] * spr.ln(),
            RuleForm::Share => {
                let share = c[0] + c[1] * (k / rake_frac).ln() + c[2] * spr.ln() + c[3] * pot_bb.ln();
                1.0 - rake_frac - (k - rake_frac) * share.clamp(0.0, 1.0)
            }
        };
        t.is_finite().then_some(t)
    }
}

/// What a heads-up flop leaf's two values add up to, as a fraction of the
/// pot. `stack_bb` is the effective stack behind, `rake_cap_bb` = 0 means
/// the rake has no cap, `pot_type` indexes [`POT_TYPES`].
pub fn leaf_total(rule: Option<&TotalRule>, pot_bb: f64, stack_bb: f64, rake_frac: f64, rake_cap_bb: f64,
                  pot_type: usize) -> LeafTotal {
    if !(rake_frac > 0.0) {
        return LeafTotal::Exact(1.0);
    }
    if !(rake_cap_bb > 0.0 && pot_bb > 0.0) {
        return LeafTotal::Unknown; // no cap: the rake taken grows with the final pot, and no rule was fitted for that
    }
    let k = rake_cap_bb / pot_bb;
    if rake_frac >= k {
        return LeafTotal::Exact(1.0 - k);
    }
    // Below the cap: at least the rake on the pot as it stands is taken, at
    // most the cap, and never more than the rake on the largest possible pot.
    let most = k.min(rake_frac * (1.0 + 2.0 * stack_bb / pot_bb));
    match rule.and_then(|r| r.total(pot_type, pot_bb, stack_bb, rake_frac, k)) {
        Some(t) => LeafTotal::Rule(t.clamp(1.0 - most, 1.0 - rake_frac)),
        None => LeafTotal::Unknown,
    }
}

/// For every pair of classes, the share of their combo pairs that share no
/// card: `[h * 169 + g]`. Pocket aces against pocket aces is 1/6, against
/// pocket kings 1.
pub fn disjoint_share() -> &'static [f64] {
    static TABLE: OnceLock<Vec<f64>> = OnceLock::new();
    TABLE.get_or_init(|| {
        let combos: Vec<Vec<u64>> = (0..NUM_CLASSES).map(class_card_masks).collect();
        let mut table = vec![0f64; NUM_CLASSES * NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            for g in h..NUM_CLASSES {
                let free = combos[h].iter().map(|a| combos[g].iter().filter(|&&b| a & b == 0).count()).sum::<usize>();
                let share = free as f64 / (combos[h].len() * combos[g].len()) as f64;
                table[h * NUM_CLASSES + g] = share;
                table[g * NUM_CLASSES + h] = share;
            }
        }
        table
    })
}

/// The combos of a class, each as a bit mask of its two cards.
fn class_card_masks(idx: usize) -> Vec<u64> {
    let (hi, lo, suited) = class_parts(idx);
    let card = |rank: u8, suit: u8| 1u64 << (rank as u32 * 4 + suit as u32);
    let mut out = Vec::new();
    for s1 in 0..4u8 {
        for s2 in 0..4u8 {
            let keep = if hi == lo { s1 < s2 } else if suited { s1 == s2 } else { s1 != s2 };
            if keep {
                out.push(card(hi, s1) | card(lo, s2));
            }
        }
    }
    out
}

/// Any two cards leave 1,225 of the 1,326 combos for the other player.
const DECK: f64 = 1326.0 / 1225.0;

/// How blocking changes how often each class meets the other range.
#[derive(Debug, Clone)]
pub struct Blocking {
    /// Per side (out of position first) and class: the share of the other
    /// range the class does not block, over its player's range average of
    /// that share. 1 for every class when nothing is blocked more than
    /// anything else; classes outside the player's range have a value too.
    pub rel: [Vec<f64>; 2],
    /// How often the two ranges are dealt together, relative to two ranges
    /// dealt from separate decks (the range average of the unblocked share
    /// times 1326/1225). 1 for two full ranges.
    pub together: f64,
}

impl Blocking {
    /// `oop`, `ip`: per-class reach masses on any scale. None when one of
    /// the ranges is empty.
    pub fn of(oop: &[f32], ip: &[f32]) -> Option<Blocking> {
        let table = disjoint_share();
        let (so, si) = (oop.iter().map(|&v| v as f64).sum::<f64>(), ip.iter().map(|&v| v as f64).sum::<f64>());
        if !(so > 0.0 && si > 0.0) {
            return None;
        }
        let mut free = [vec![0f64; NUM_CLASSES], vec![0f64; NUM_CLASSES]];
        for h in 0..NUM_CLASSES {
            let row = &table[h * NUM_CLASSES..(h + 1) * NUM_CLASSES];
            let a = oop[h] as f64 / so;
            let mut sum = 0f64;
            for g in 0..NUM_CLASSES {
                sum += ip[g] as f64 * row[g];
                free[1][g] += a * row[g];
            }
            free[0][h] = sum / si;
        }
        let mean: f64 = (0..NUM_CLASSES).map(|h| oop[h] as f64 / so * free[0][h]).sum();
        if !(mean > 0.0) {
            return None;
        }
        free.iter_mut().flatten().for_each(|v| *v /= mean);
        Some(Blocking { rel: free, together: mean * DECK })
    }

    /// The weights of the dealt sum: each side's add up to 1.
    pub fn weights(&self, oop: &[f32], ip: &[f32]) -> [Vec<f64>; 2] {
        let mut w = [plain_weights(oop), plain_weights(ip)];
        for side in 0..2 {
            w[side].iter_mut().zip(&self.rel[side]).for_each(|(w, r)| *w *= r);
        }
        w
    }
}

/// A range's class shares (adding up to 1): the weights of the plain sum.
pub fn plain_weights(range: &[f32]) -> Vec<f64> {
    let sum: f64 = range.iter().map(|&v| v as f64).sum();
    range.iter().map(|&v| if sum > 0.0 { v as f64 / sum } else { 0.0 }).collect()
}

/// The two players' values (`balanced` plus `corr`, out of position's 169
/// classes then in position's, fractions of the pot) added up with `weights`.
pub fn weighted_total(corr: &[f32], balanced: &[f32], weights: &[Vec<f64>; 2]) -> f64 {
    (0..2).map(|side| {
        let at = side * NUM_CLASSES;
        (0..NUM_CLASSES).map(|h| weights[side][h] * (balanced[at + h] as f64 + corr[at + h] as f64)).sum::<f64>()
    }).sum()
}

/// Shift every class of both players by the same amount so that the values
/// add up to `target`. A class's value stays within what a hand can win or
/// lose (`room` = stack behind over pot); where that stops some classes the
/// rest is shifted again, a few times. Returns the total afterwards.
pub fn pin_total(corr: &mut [f32], balanced: &[f32], weights: &[Vec<f64>; 2], target: f64, room: f32) -> f64 {
    let mut now = weighted_total(corr, balanced, weights);
    for _ in 0..4 {
        let miss = target - now;
        if miss.abs() < 1e-7 {
            break;
        }
        let shift = (miss / 2.0) as f32;
        for (c, &b) in corr.iter_mut().zip(balanced) {
            *c = (*c + shift).clamp(-room - b, 1.0 + room - b);
        }
        now = weighted_total(corr, balanced, weights);
    }
    now
}

/// The sums of one leaf's values, fractions of the pot.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct LeafSums {
    /// The dealt sum of the net's values before any pin (None when it was
    /// not needed and so not computed).
    pub net_dealt: Option<f64>,
    /// The dealt sum of the values after the pin.
    pub dealt: Option<f64>,
    pub pinned: bool,
    /// The plain sum of what the solve prices with: what its books pay the
    /// two players together at this leaf.
    pub booked: f64,
    /// The known total, which is what `booked` would be if the books paid
    /// exactly that (None where the total is not known).
    pub fair: Option<f64>,
}

/// Turn the net's corrections for one leaf (already held to what a hand can
/// win or lose) into what the solve prices with under `books`, and report
/// the leaf's sums. `norm` are the two reaches by class, `invested` what
/// each of the two has put in over the pot, `measure` asks for the dealt
/// sums even where the settings do not need them.
pub fn book_leaf(books: LeafBooks, measure: bool, corr: &mut [f32], balanced: &[f32], norm: [&[f32]; 2], room: f32,
                 invested: [f64; 2], known: LeafTotal) -> LeafSums {
    let plain = [plain_weights(norm[0]), plain_weights(norm[1])];
    let target = books.pin.target(known);
    let need_dealt = measure || books.blocking || (target.is_some() && books.sum == PinSum::Dealt);
    let blocking = if need_dealt { Blocking::of(norm[0], norm[1]) } else { None };
    let dealt_weights = blocking.as_ref().map(|b| b.weights(norm[0], norm[1]));
    let net_dealt = dealt_weights.as_ref().map(|w| weighted_total(corr, balanced, w));
    let mut pinned = false;
    if let Some(t) = target {
        match (books.sum, &dealt_weights) {
            (PinSum::Plain, _) => {
                pin_total(corr, balanced, &plain, t, room);
                pinned = true;
            }
            (PinSum::Dealt, Some(w)) => {
                pin_total(corr, balanced, w, t, room);
                pinned = true;
            }
            (PinSum::Dealt, None) => {}
        }
    }
    let dealt = dealt_weights.as_ref().map(|w| weighted_total(corr, balanced, w));
    // Blocking: book factor x (pot x value - invested) where the solve books
    // (pot x value - invested), by pricing with factor x value + (1 - factor) x invested / pot.
    if let (true, Some(b)) = (books.blocking, &blocking) {
        for side in 0..2 {
            for h in 0..NUM_CLASSES {
                let i = side * NUM_CLASSES + h;
                let factor = b.rel[side][h];
                let value = balanced[i] as f64 + corr[i] as f64;
                corr[i] = (factor * value + (1.0 - factor) * invested[side] - balanced[i] as f64) as f32;
            }
        }
    }
    let booked = weighted_total(corr, balanced, &plain);
    let fair = known.value();
    LeafSums { net_dealt, dealt, pinned, booked, fair }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::equity::{class_combos, class_index};

    fn rule(form: &str) -> TotalRule {
        let coef = if form == "linear" {
            serde_json::json!({
                "limped": [0.848247, -0.005173, 0.029683, 0.003206], "srp": [0.922959, -0.035846, -0.016072, 0.001664],
                "3bet": [0.948199, -0.197748, -0.003144, 0.001279], "4bet": [0.969515, -0.548728, 0.001756, 0.000164]})
        } else {
            serde_json::json!({
                "limped": [0.360482, -0.076927, -0.00048, -0.052659], "srp": [0.541384, -0.163357, 0.007368, -0.009273],
                "3bet": [0.813041, -0.296116, 0.018916, -0.030269], "4bet": [0.275882, -0.078548, -0.046622, 0.096291]})
        };
        let header = serde_json::json!({"total_rule": {"form": form, "coef": coef, "valid": {
            "rake_frac": [0.05, 0.05], "cap_over_pot": [0.02, 2.5], "pot_bb": [2.0, 120.0], "stack_over_pot": [0.2, 100.0]}}});
        TotalRule::from_header(&header).unwrap().unwrap()
    }

    fn noise(seed: u32) -> impl FnMut() -> f32 {
        let mut state = seed;
        move || {
            state = state.wrapping_mul(1664525).wrapping_add(1013904223);
            (state >> 8) as f32 / (1u32 << 24) as f32
        }
    }

    #[test]
    fn the_table_counts_the_pairs_that_can_be_dealt_together() {
        let t = disjoint_share();
        let at = |a: usize, b: usize| t[a * NUM_CLASSES + b];
        let (aa, kk) = (class_index(12, 12, false), class_index(11, 11, false));
        let (aks, ako) = (class_index(12, 11, true), class_index(12, 11, false));
        assert_eq!((at(aa, aa), at(aa, kk), at(aks, aks), at(ako, ako)), (1.0 / 6.0, 1.0, 12.0 / 16.0, 7.0 / 12.0));
        assert!(at(aa, aks) == 0.5 && at(aa, aks) == at(aks, aa));
        // any two cards leave 1,225 of the 1,326 combos for the other player
        for h in 0..NUM_CLASSES {
            let free: f64 = (0..NUM_CLASSES).map(|g| class_combos(g) as f64 * at(h, g)).sum();
            assert!((free - 1225.0).abs() < 1e-9, "class {h}: {free}");
        }
    }

    #[test]
    fn blocking_drops_what_the_other_range_holds() {
        let (aa, kk, qq) = (class_index(12, 12, false), class_index(11, 11, false), class_index(10, 10, false));
        let aks = class_index(12, 11, true);
        // oop: aces and kings; ip: ace-king suited only. Each pair blocks
        // half of the ace-king combos, so both still count the same, and
        // queens (not in the range) would meet that range twice as often.
        let mut oop = vec![0f32; NUM_CLASSES];
        let mut ip = vec![0f32; NUM_CLASSES];
        (oop[aa], oop[kk], ip[aks]) = (3.0, 3.0, 0.2);
        let b = Blocking::of(&oop, &ip).unwrap();
        assert!((b.rel[0][aa] - 1.0).abs() < 1e-9 && (b.rel[0][kk] - 1.0).abs() < 1e-9 && (b.rel[0][qq] - 2.0).abs() < 1e-9);
        assert!((b.rel[1][aks] - 1.0).abs() < 1e-9 && (b.together - 0.5 * 1326.0 / 1225.0).abs() < 1e-9);
        // aces and queens: aces count half as much as queens
        let mut oop = vec![0f32; NUM_CLASSES];
        (oop[aa], oop[qq]) = (0.5, 0.5);
        let b = Blocking::of(&oop, &ip).unwrap();
        let w = b.weights(&oop, &ip);
        assert!((w[0][aa] - 1.0 / 3.0).abs() < 1e-9 && (w[0][qq] - 2.0 / 3.0).abs() < 1e-9 && (w[1][aks] - 1.0).abs() < 1e-9);
        // two full ranges: every class counts as it is, and they meet as often as the deck says
        let full: Vec<f32> = (0..NUM_CLASSES).map(class_combos).collect();
        let b = Blocking::of(&full, &full).unwrap();
        assert!(b.rel.iter().flatten().all(|r| (r - 1.0).abs() < 1e-9) && (b.together - 1.0).abs() < 1e-9);
        assert!(Blocking::of(&vec![0.0; NUM_CLASSES], &ip).is_none());
        // the same two ranges and numbers as tools/datagen/test_total_rule.py (test_dealt_weights)
        let oop: Vec<f32> = (0..NUM_CLASSES).map(|h| if h % 2 == 0 { ((h * 37) % 11 + 1) as f32 } else { 0.0 }).collect();
        let ip: Vec<f32> = (0..NUM_CLASSES).map(|g| ((g * 53) % 7) as f32).collect();
        let b = Blocking::of(&oop, &ip).unwrap();
        let w = b.weights(&oop, &ip);
        for (got, want) in [(w[0][168], 0.0039421507), (w[0][0], 0.0019710754), (w[1][1], 0.0079351133),
                            (w[1][160], 0.0058782930), (b.together, 1.0004269767)] {
            assert!((got - want).abs() < 1e-9, "{got} vs {want}");
        }
        // both sides' weights always add up to 1
        let mut next = noise(5);
        let (oop, ip): (Vec<f32>, Vec<f32>) = (0..NUM_CLASSES).map(|h| (next(), if h % 4 == 0 { 0.0 } else { next() })).unzip();
        let w = Blocking::of(&oop, &ip).unwrap().weights(&oop, &ip);
        assert!(w.iter().all(|side| (side.iter().sum::<f64>() - 1.0).abs() < 1e-9));
    }

    #[test]
    fn the_total_is_exact_without_rake_and_at_the_cap() {
        let r = rule("linear");
        // no rake: the whole pot, with or without a rule
        assert_eq!(leaf_total(None, 6.5, 97.0, 0.0, 0.0, 1), LeafTotal::Exact(1.0));
        assert_eq!(leaf_total(Some(&r), 6.5, 97.0, 0.0, 3.0, 1), LeafTotal::Exact(1.0));
        // 5% of 60 bb is the 3 bb cap: the pot minus the cap
        assert_eq!(leaf_total(None, 60.0, 70.0, 0.05, 3.0, 3), LeafTotal::Exact(1.0 - 3.0 / 60.0));
        assert_eq!(leaf_total(Some(&r), 80.0, 60.0, 0.05, 3.0, 3), LeafTotal::Exact(1.0 - 3.0 / 80.0));
        // below the cap nothing is known without a rule, and nothing at all without a cap
        assert_eq!(leaf_total(None, 6.5, 97.0, 0.05, 3.0, 1), LeafTotal::Unknown);
        assert_eq!(leaf_total(Some(&r), 6.5, 97.0, 0.05, 0.0, 1), LeafTotal::Unknown);
        // the settings: off pins nothing, exact only what is exact
        let below = leaf_total(Some(&r), 6.5, 97.0, 0.05, 3.0, 1);
        assert!(matches!(below, LeafTotal::Rule(_)));
        assert_eq!(PinTotal::Off.target(LeafTotal::Exact(1.0)), None);
        assert_eq!(PinTotal::Exact.target(LeafTotal::Exact(0.95)), Some(0.95));
        assert_eq!(PinTotal::Exact.target(below), None);
        assert_eq!(PinTotal::Rule.target(below), below.value());
        assert_eq!(PinTotal::Rule.target(LeafTotal::Unknown), None);
    }

    /// The same cases as tools/datagen/test_total_rule.py: the rule is
    /// fitted in Python and applied here, so the two must agree.
    #[test]
    fn the_rule_gives_the_numbers_the_python_side_gives() {
        let cases: [(&str, usize, f64, f64, f64, f64, Option<f64>); 12] = [
            ("linear", 1, 6.5, 97.0, 0.05, 3.0, Some(0.8808287)),
            ("linear", 2, 22.0, 89.0, 0.05, 3.0, Some(0.9133026)),
            ("linear", 3, 48.0, 76.0, 0.05, 3.0, Some(0.9420927)),
            ("linear", 0, 2.0, 99.0, 0.05, 1.0, Some(0.8787449)),
            ("linear", 3, 59.0, 41.0, 0.05, 3.0, Some(1.0 - 3.0 / 59.0)), // more rake than the cap allows: held to the cap
            ("share", 1, 6.5, 97.0, 0.05, 3.0, Some(0.8755634)),
            ("share", 2, 22.0, 89.0, 0.05, 3.0, Some(0.9112382)),
            ("share", 0, 2.0, 99.0, 0.05, 1.0, Some(0.8847601)),
            ("share", 3, 48.0, 76.0, 0.05, 3.0, Some(0.9423788)),
            ("share", 1, 10.0, 2.0, 0.05, 3.0, Some(0.93)), // a short stack: at most 5% of the pot plus both stacks
            ("linear", 1, 6.5, 97.0, 0.03, 3.0, None),      // a rake the rule was not fitted on
            ("linear", 1, 150.0, 30.0, 0.05, 30.0, None),   // a pot it was not fitted on
        ];
        for (form, pot_type, pot, stack, rake, cap, want) in cases {
            let got = match leaf_total(Some(&rule(form)), pot, stack, rake, cap, pot_type) {
                LeafTotal::Exact(t) => panic!("{form} {pot_type} {pot}: exact {t}"),
                other => other.value(),
            };
            match (got, want) {
                (Some(g), Some(w)) => assert!((g - w).abs() < 1e-6, "{form} type {pot_type} pot {pot}: {g} vs {w}"),
                (None, None) => {}
                other => panic!("{form} type {pot_type} pot {pot}: {other:?}"),
            }
        }
    }

    #[test]
    fn a_rule_or_setting_that_cannot_be_read_is_refused() {
        assert_eq!(TotalRule::from_header(&serde_json::json!({"sizes": [1, 2]})).unwrap(), None);
        let good = serde_json::json!({"form": "linear",
            "coef": {"limped": [1, 0, 0, 0], "srp": [1, 0, 0, 0], "3bet": [1, 0, 0, 0], "4bet": [1, 0, 0, 0]},
            "valid": {"rake_frac": [0.05, 0.05], "cap_over_pot": [0.0, 1.0], "pot_bb": [1, 100], "stack_over_pot": [0, 50]}});
        assert!(TotalRule::from_header(&serde_json::json!({"total_rule": good})).unwrap().is_some());
        for (path, bad) in [("/form", serde_json::json!("cubic")), ("/coef/srp", serde_json::json!([1, 0, 0])),
                            ("/coef/3bet", serde_json::json!([1, 0, "x", 0])), ("/valid/pot_bb", serde_json::json!([100, 1])),
                            ("/valid", serde_json::json!({}))] {
            let mut rule = good.clone();
            *rule.pointer_mut(path).unwrap() = bad;
            assert!(TotalRule::from_header(&serde_json::json!({"total_rule": rule})).is_err(), "{path}");
        }
        assert_eq!(LeafBooks::parse("", "", "").unwrap(), LeafBooks::default());
        assert!(LeafBooks::default().is_default() && LeafBooks::default().check(false).is_ok());
        let books = LeafBooks::parse("rule", "dealt", "on").unwrap();
        assert_eq!(books, LeafBooks { pin: PinTotal::Rule, sum: PinSum::Dealt, blocking: true });
        assert!(books.check(true).is_ok() && books.check(false).is_err(), "a rule pin needs a rule");
        for bad in [("everywhere", "", ""), ("exact", "booked", ""), ("", "", "deck")] {
            assert!(LeafBooks::parse(bad.0, bad.1, bad.2).is_err(), "{bad:?}");
        }
        assert!(LeafBooks::parse("", "plain", "").unwrap().check(true).is_err(), "nothing to pin");
        assert!(LeafBooks::parse("exact", "plain", "on").unwrap().check(true).is_err(), "two ways at once");
        assert!(LeafBooks::parse("exact", "plain", "").unwrap().check(false).is_ok());
    }

    #[test]
    fn pinning_moves_every_class_alike_and_respects_what_a_hand_can_win() {
        let mut next = noise(12345);
        let oop: Vec<f32> = (0..NUM_CLASSES).map(|_| next()).collect();
        let ip: Vec<f32> = (0..NUM_CLASSES).map(|h| if h % 3 == 0 { 0.0 } else { next() }).collect();
        let weights = Blocking::of(&oop, &ip).unwrap().weights(&oop, &ip);
        let balanced: Vec<f32> = (0..2 * NUM_CLASSES).map(|_| 0.2 + 0.6 * next()).collect();
        let net: Vec<f32> = (0..2 * NUM_CLASSES).map(|_| 0.1 * (next() - 0.4)).collect();
        let before = weighted_total(&net, &balanced, &weights);
        let mut corr = net.clone();
        let after = pin_total(&mut corr, &balanced, &weights, 0.95, 5.0);
        assert!((before - 0.95).abs() > 0.01, "the net's total is off: {before}");
        assert!((after - 0.95).abs() < 1e-6 && (weighted_total(&corr, &balanced, &weights) - after).abs() < 1e-12);
        // one shift for every class of both players, also the ones a range does not hold
        let shift = corr[0] - net[0];
        assert!(((before + 2.0 * shift as f64) - 0.95).abs() < 1e-5);
        assert!(corr.iter().zip(&net).all(|(c, n)| ((c - n) - shift).abs() < 1e-6));
        // a total that is already right is left alone
        let again = corr.clone();
        pin_total(&mut corr, &balanced, &weights, after, 5.0);
        assert_eq!(corr, again);
        // with nothing behind a class is worth between nothing and the pot:
        // classes at that edge stay there and the others make up the rest
        let mut corr: Vec<f32> = balanced.iter().map(|b| if *b > 0.5 { 1.0 - b } else { 0.0 }).collect();
        let before = weighted_total(&corr, &balanced, &weights);
        let after = pin_total(&mut corr, &balanced, &weights, 1.0, 0.0);
        assert!(before > 1.2 && (after - 1.0).abs() < 1e-3, "{before} -> {after}");
        assert!(corr.iter().zip(&balanced).all(|(c, b)| c + b >= -1e-6 && c + b <= 1.0 + 1e-6));
    }

    /// One leaf under every setting: what is pinned, and what the books show.
    #[test]
    fn the_books_of_a_leaf_under_each_setting() {
        // two tight ranges that block each other, as in a 4-bet pot
        let mut next = noise(77);
        let (aa, kk, qq) = (class_index(12, 12, false), class_index(11, 11, false), class_index(10, 10, false));
        let (aks, ako, a5s) = (class_index(12, 11, true), class_index(12, 11, false), class_index(12, 3, true));
        let mut oop = vec![0f32; NUM_CLASSES];
        let mut ip = vec![0f32; NUM_CLASSES];
        for (h, w) in [(aa, 6.0), (kk, 6.0), (qq, 3.0), (aks, 4.0), (ako, 6.0), (a5s, 2.0)] {
            oop[h] = w;
            ip[h] = w * (0.5 + next());
        }
        // values that rise with the class's strength, so the blocked classes are worth most
        let balanced: Vec<f32> = (0..2 * NUM_CLASSES).map(|i| {
            let h = i % NUM_CLASSES;
            if h == aa { 1.1 } else if h == kk { 0.8 } else { 0.3 + 0.1 * next() }
        }).collect();
        let net: Vec<f32> = (0..2 * NUM_CLASSES).map(|_| 0.04 * next()).collect();
        let (room, invested) = (3.0f32, [0.48, 0.5]);
        let run = |books: LeafBooks, known: LeafTotal, measure: bool| {
            let mut corr = net.clone();
            let sums = book_leaf(books, measure, &mut corr, &balanced, [&oop, &ip], room, invested, known);
            (corr, sums)
        };
        let exact = LeafTotal::Exact(0.96);
        let plain = [plain_weights(&oop), plain_weights(&ip)];
        // off: the net's values untouched; the dealt sums only on request
        let (corr, sums) = run(LeafBooks::default(), exact, false);
        assert_eq!(corr, net);
        assert_eq!((sums.net_dealt, sums.dealt, sums.pinned, sums.fair), (None, None, false, Some(0.96)));
        assert!((sums.booked - weighted_total(&net, &balanced, &plain)).abs() < 1e-12);
        let (corr, measured) = run(LeafBooks::default(), exact, true);
        assert_eq!(corr, net);
        let net_dealt = measured.net_dealt.unwrap();
        assert_eq!(measured.dealt, Some(net_dealt));
        // the blocked classes are worth most, so the plain sum is above the dealt one
        assert!(sums.booked > net_dealt + 0.01, "{} vs {net_dealt}", sums.booked);
        // the pin on the dealt sum: values at the right level, the books still above the pot minus rake
        let pin = LeafBooks { pin: PinTotal::Exact, ..Default::default() };
        let (corr, a) = run(pin, exact, false);
        assert!(a.pinned && (a.net_dealt.unwrap() - net_dealt).abs() < 1e-12 && (a.dealt.unwrap() - 0.96).abs() < 1e-6);
        assert!((a.booked - a.fair.unwrap() - (sums.booked - net_dealt)).abs() < 1e-5, "the gap between the sums stays");
        let shift = corr[0] - net[0];
        assert!(corr.iter().zip(&net).all(|(c, n)| ((c - n) - shift).abs() < 1e-6));
        // a leaf whose total is not known is left alone, and so is a ruled one under "exact"
        for known in [LeafTotal::Unknown, LeafTotal::Rule(0.93)] {
            let (corr, s) = run(pin, known, false);
            assert!(corr == net && !s.pinned && s.fair == known.value());
        }
        let (_, ruled) = run(LeafBooks { pin: PinTotal::Rule, ..Default::default() }, LeafTotal::Rule(0.93), false);
        assert!(ruled.pinned && (ruled.dealt.unwrap() - 0.93).abs() < 1e-6);
        // the pin on the plain sum: the books add up, the values sit below their level
        let (_, b) = run(LeafBooks { pin: PinTotal::Exact, sum: PinSum::Plain, ..Default::default() }, exact, true);
        assert!(b.pinned && (b.booked - 0.96).abs() < 1e-6 && b.dealt.unwrap() < 0.95);
        // blocking at the leaf: the books show the dealt sum, pinned or not
        let leaf = LeafBooks { blocking: true, ..Default::default() };
        let (_, c) = run(leaf, exact, false);
        assert!(!c.pinned && (c.booked - net_dealt).abs() < 1e-6 && c.fair == Some(0.96));
        let (corr, c) = run(LeafBooks { pin: PinTotal::Exact, ..leaf }, exact, false);
        assert!(c.pinned && (c.dealt.unwrap() - 0.96).abs() < 1e-6 && (c.booked - 0.96).abs() < 1e-6);
        // a class is booked by its factor: factor x (value - invested) is what the books pay over what was put in
        let blocking = Blocking::of(&oop, &ip).unwrap();
        let (pinned_only, _) = run(pin, exact, false);
        for (side, h) in [(0, aa), (0, a5s), (1, kk), (1, 0)] {
            let i = side * NUM_CLASSES + h;
            let value = (balanced[i] + pinned_only[i]) as f64;
            let booked = (balanced[i] + corr[i]) as f64;
            let want = blocking.rel[side][h] * (value - invested[side]);
            assert!((booked - invested[side] - want).abs() < 1e-5, "side {side} class {h}");
        }
        assert!(blocking.rel[0][aa] < 0.95 && blocking.rel[0][0] > 1.3, "aces meet this range less often than deuces: {} {}",
                blocking.rel[0][aa], blocking.rel[0][0]);
        assert!(blocking.together < 0.95, "these ranges are dealt together less often than two full ranges");
    }
}
