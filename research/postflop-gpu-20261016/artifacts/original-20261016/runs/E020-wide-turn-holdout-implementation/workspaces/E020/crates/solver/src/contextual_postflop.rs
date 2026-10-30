//! Conservative, aggregate history adjustments. Hand selection is still inferred
//! from the solved strategy; these are not learned board/hand policies.
use crate::tree::Action;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PostflopPotType { Limped, SingleRaised, ThreeBetPlus }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BettingKind { Donk, Stab, Lead, Probe }
impl BettingKind {
    pub fn name(self) -> &'static str {
        match self { Self::Donk => "donk", Self::Stab => "stab", Self::Lead => "lead", Self::Probe => "probe" }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ContextualBetCell {
    pub street: u8,
    pub kind: BettingKind,
    pub pot_type: PostflopPotType,
    pub opportunities: u64,
    pub bets: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ContextualBetting {
    pub version: u8,
    pub source: String,
    pub cells: Vec<ContextualBetCell>,
}
impl ContextualBetting {
    pub fn validate(&self) -> Result<(), String> {
        if self.version != 1 { return Err("unsupported contextual betting version".into()); }
        for (i, c) in self.cells.iter().enumerate() {
            if c.street > 2 || c.bets > c.opportunities {
                return Err("invalid contextual betting counts or street".into());
            }
            if (c.kind == BettingKind::Donk && c.street != 0)
                || (matches!(c.kind, BettingKind::Lead | BettingKind::Probe) && c.street == 0) {
                return Err("contextual betting kind does not match street".into());
            }
            if self.cells[..i].iter().any(|p| p.street == c.street && p.kind == c.kind && p.pot_type == c.pot_type) {
                return Err("duplicate contextual betting cell".into());
            }
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct ProfileRootEvidence {
    pub kind: String,
    pub opportunities: u64,
    pub observed: Option<f32>,
    pub target: f32,
    pub achieved: f32,
    pub source: String,
    pub note: String,
}

#[derive(Debug, Clone, Copy)]
pub(crate) struct BettingHistory {
    pub aggressor: Option<usize>,
    pub checked: u8,
    pub bet_this_street: bool,
    pub previous_checked_through: bool,
    pub known: bool,
}
impl BettingHistory {
    pub fn new(aggressor: Option<usize>, root_street: u8) -> Self {
        Self { aggressor, checked: 0, bet_this_street: false,
            previous_checked_through: false, known: root_street == 0 }
    }
    pub fn after(self, actor: usize, action: &Action) -> Self {
        let mut next = self;
        match action {
            Action::Check => next.checked |= 1 << actor,
            Action::Bet(_) | Action::Raise(_) => {
                next.aggressor = Some(actor);
                next.bet_this_street = true;
                next.known = true;
            }
            _ => {}
        }
        next
    }
    pub fn next_street(self) -> Self {
        Self { previous_checked_through: !self.bet_this_street && self.checked == 3,
            checked: 0, bet_this_street: false, ..self }
    }
    pub fn kind(self, actor: usize, street: u8) -> Option<BettingKind> {
        if !self.known || self.bet_this_street { return None; }
        let aggressor = self.aggressor?;
        if actor == aggressor { return None; }
        if self.checked & (1 << aggressor) != 0 { return Some(BettingKind::Stab); }
        if actor != 0 { return None; }
        Some(if street == 0 { BettingKind::Donk }
            else if self.previous_checked_through { BettingKind::Probe }
            else { BettingKind::Lead })
    }
}

/// No movement below 50 observations. Otherwise n/(n+200) shrinks the raw
/// context frequency toward this node's baseline. A common bet:check odds
/// multiplier in [1/4,4] limits amplification and preserves exact zeros/ones
/// and every hand's relative size shares. These are explicit conservative
/// engineering assumptions, not fitted or independently validated constants.
pub(crate) fn adjust_betting(
    sigma: &mut [f32], acts: &[Action], reach: &[f32],
    data: &ContextualBetting, kind: Option<BettingKind>, street: u8,
    pot_type: Option<PostflopPotType>,
) -> ProfileRootEvidence {
    let nh = reach.len();
    let aggressive: Vec<bool> = acts.iter().map(Action::is_aggressive).collect();
    let bets: Vec<f64> = (0..nh).map(|h| acts.iter().enumerate()
        .filter(|(a, _)| aggressive[*a]).map(|(a, _)| sigma[a*nh+h] as f64).sum::<f64>().clamp(0.0, 1.0)).collect();
    let mass = reach.iter().map(|&w| w as f64).sum::<f64>().max(1e-12);
    let frequency = |odds: f64| -> f64 {
        bets.iter().zip(reach).map(|(&b,&w)| w as f64 * (odds*b/(1.0-b+odds*b))).sum::<f64>()/mass
    };
    let baseline = frequency(1.0);
    let cell = data.cells.iter().find(|c| Some(c.kind) == kind && c.street == street && Some(c.pot_type) == pot_type);
    let n = cell.map_or(0, |c| c.opportunities);
    let observed = cell.filter(|c| c.opportunities > 0).map(|c| c.bets as f64/c.opportunities as f64);
    let desired = if n >= 50 {
        let w = n as f64/(n as f64+200.0);
        baseline + w*(observed.unwrap_or(baseline)-baseline)
    } else { baseline };
    let mut note = if n >= 50 {
        "History estimate shrunk toward the solve; per-hand bet odds bounded to 0.25–4×. Solved hand ordering and size shares retained. Safeguards are assumptions; not board-specific evidence."
    } else {
        "Insufficient matching context (minimum 50 opportunities); solved betting strategy retained. No pooled donk/stab target substituted."
    }.to_string();
    if !aggressive.iter().any(|&a| a) {
        note = "No legal bet at this node; solved strategy retained.".into();
    }
    let target = desired.clamp(frequency(0.25), frequency(4.0));
    if n >= 50 && (target-baseline).abs() > 1e-10 {
        let (mut lo, mut hi) = (0.25, 4.0);
        for _ in 0..40 {
            let mid = (lo+hi)*0.5;
            if frequency(mid) < target { lo = mid; } else { hi = mid; }
        }
        let odds = (lo+hi)*0.5;
        for h in 0..nh {
            let denom = 1.0-bets[h]+odds*bets[h];
            for a in 0..acts.len() {
                sigma[a*nh+h] = (sigma[a*nh+h] as f64 * if aggressive[a] { odds } else { 1.0 } / denom) as f32;
            }
        }
    }
    let achieved: f64 = (0..nh).map(|h| reach[h] as f64 * (0..acts.len())
        .filter(|&a| aggressive[a]).map(|a| sigma[a*nh+h] as f64).sum::<f64>()).sum::<f64>()/mass;
    ProfileRootEvidence { kind: kind.map_or("unknown", BettingKind::name).into(), opportunities: n,
        observed: observed.map(|v| (100.0*v) as f32), target: (100.0*target) as f32,
        achieved: (100.0*achieved) as f32, source: data.source.clone(), note }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn data(n: u64, bets: u64) -> ContextualBetting {
        ContextualBetting { version: 1, source: "test".into(), cells: vec![ContextualBetCell {
            street: 0, kind: BettingKind::Donk, pot_type: PostflopPotType::ThreeBetPlus,
            opportunities: n, bets,
        }] }
    }
    fn adjust(sigma: &mut [f32], n: u64, bets: u64) -> ProfileRootEvidence {
        adjust_betting(sigma, &[Action::Check, Action::Bet(3.3), Action::Bet(7.5)], &[1.0, 1.0],
            &data(n, bets), Some(BettingKind::Donk), 0, Some(PostflopPotType::ThreeBetPlus))
    }
    #[test]
    fn distinguishes_donk_stab_lead_and_probe() {
        let h = BettingHistory::new(Some(1), 0);
        assert_eq!(h.kind(0, 0), Some(BettingKind::Donk));
        let stab = BettingHistory::new(Some(0), 0).after(0, &Action::Check);
        assert_eq!(stab.kind(1, 0), Some(BettingKind::Stab));
        let lead = h.after(0, &Action::Check).after(1, &Action::Bet(3.3)).after(0, &Action::Call(3.3)).next_street();
        assert_eq!(lead.kind(0, 1), Some(BettingKind::Lead));
        let probe = h.after(0, &Action::Check).after(1, &Action::Check).next_street();
        assert_eq!(probe.kind(0, 1), Some(BettingKind::Probe));
        // After a checked-through turn the same old initiative is retained.
        assert_eq!(probe.after(0, &Action::Check).after(1, &Action::Check).next_street().kind(0, 2), Some(BettingKind::Probe));
        assert_eq!(h.kind(1, 0), None);
        assert_eq!(BettingHistory::new(None, 0).kind(0, 0), None);
        assert_eq!(BettingHistory::new(Some(1), 1).kind(0, 1), None);
    }
    #[test]
    fn tiny_residual_bets_cannot_become_a_quarter_of_range() {
        let mut sigma = vec![0.9999, 1.0, 0.00005, 0.0, 0.00005, 0.0];
        let out = adjust(&mut sigma, 10000, 2500);
        assert!(out.achieved < 0.03, "{}% must remain small", out.achieved);
        assert_eq!(sigma[1], 1.0);
        assert_eq!(sigma[3], 0.0);
        assert_eq!(sigma[5], 0.0);
        assert!((sigma[2]/sigma[4]-1.0).abs() < 1e-6);
    }
    #[test]
    fn preserves_relative_size_shares_and_hits_bounded_target() {
        let mut sigma = vec![0.8, 0.6, 0.15, 0.1, 0.05, 0.3];
        let out = adjust(&mut sigma, 1000, 600);
        assert!((out.achieved-out.target).abs() < 0.001);
        assert!((sigma[2]/sigma[4]-3.0).abs() < 1e-5);
        assert!((sigma[3]/sigma[5]-1.0/3.0).abs() < 1e-5);
        for h in 0..2 { assert!((sigma[h]+sigma[2+h]+sigma[4+h]-1.0).abs() < 1e-6); }
        assert!(sigma[0] > sigma[1], "hand ordering retained");
    }
    #[test]
    fn sparse_missing_and_mismatched_contexts_preserve_baseline_exactly() {
        let original = vec![0.8, 0.6, 0.15, 0.1, 0.05, 0.3];
        let mut sigma = original.clone();
        adjust(&mut sigma, 49, 49);
        assert_eq!(sigma, original);
        for (kind, street, pot) in [(None, 0, None), (Some(BettingKind::Stab), 0, Some(PostflopPotType::ThreeBetPlus)),
            (Some(BettingKind::Donk), 0, Some(PostflopPotType::SingleRaised))] {
            let out = adjust_betting(&mut sigma, &[Action::Check, Action::Bet(3.3), Action::Bet(7.5)], &[1.0,1.0],
                &data(1000,900), kind, street, pot);
            assert_eq!(sigma, original);
            assert_eq!(out.opportunities, 0);
            assert_eq!(out.observed, None);
        }
    }
    #[test]
    fn exact_always_and_never_bet_hands_remain_fixed() {
        let mut sigma = vec![0.0, 1.0, 0.3, 0.0, 0.7, 0.0];
        let original = sigma.clone();
        adjust(&mut sigma, 1000, 1);
        for (a,b) in sigma.iter().zip(original) { assert!((a-b).abs() < 1e-7); }
    }
    #[test]
    fn invalid_evidence_is_rejected() {
        assert!(data(100,101).validate().is_err());
        let mut d = data(100,10);
        d.cells.push(d.cells[0].clone());
        assert!(d.validate().is_err());
        let mut d = data(100,10);
        d.cells[0].street=1;
        assert!(d.validate().is_err());
        let mut d = data(100,10);
        d.version=2;
        assert!(d.validate().is_err());
    }
}
