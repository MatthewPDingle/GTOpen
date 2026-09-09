//! Diagnostics of existing terminal pricing, not a replacement value model.
use super::{PreflopSolver, KIND_POT_SHARE, NUM_CLASSES};
use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub struct ContinuationPlayerValue {
    pub position: String,
    /// Gross-pot-share convention: future play is modeled; preflop sunk
    /// investment is not subtracted. This is not a solved postflop value.
    pub value_bb: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct ContinuationEstimate {
    pub model: String,
    pub players: Vec<ContinuationPlayerValue>,
    pub pot_bb: f64,
    pub total_value_bb: f64,
    /// Pot minus both modeled values. May include approximation error;
    /// never label this as measured or expected rake.
    pub unallocated_bb: f64,
    pub requested_rake_pct: f64,
    pub requested_rake_cap_bb: f64,
    pub rake_on_starting_pot_bb: f64,
    pub requested_rake_applied: bool,
    pub note: String,
}

impl PreflopSolver {
    pub(super) fn continuation_estimate(
        &self, node: usize, reaches: &[Vec<f32>],
    ) -> Option<ContinuationEstimate> {
        let nd = &self.nodes[node];
        if nd.kind != KIND_POT_SHARE || nd.live.count_ones() != 2 { return None; }
        // Normalize every seat, including folded seats, to remove path mass
        // without dividing by a potentially tiny product of path probabilities.
        // terminal_value remains the single source of the pricing formula.
        let mut normalized = Vec::with_capacity(self.n);
        for reach in reaches {
            let mass: f32 = reach.iter().sum();
            if !mass.is_finite() || mass <= 0.0 { return None; }
            normalized.push(reach.iter().map(|v| v / mass).collect::<Vec<_>>());
        }
        let live: Vec<usize> = (0..self.n).filter(|p| nd.live & (1 << p) != 0).collect();
        let left = live.iter().map(|&p| self.cfg.stack - nd.invested[p] + self.cfg.ante)
            .fold(f64::INFINITY, f64::min).max(0.0);
        let all_in = left / nd.pot <= 1e-9;
        let calibrated = self.fit.is_some() && !all_in;
        let model = if all_in { "all_in_equity" } else if calibrated { "calibrated" }
            else if self.cfg.realization == "raw" { "raw" } else { "static" };
        let mut players = Vec::with_capacity(2);
        for p in live {
            let mut values = [0.0; NUM_CLASSES];
            self.terminal_value(node, p, &normalized, &mut values);
            let probability: f64 = normalized.iter().enumerate().filter(|(q, _)| *q != p)
                .map(|(_, r)| r.iter().sum::<f32>() as f64).product();
            let net: f64 = normalized[p].iter().zip(values)
                .map(|(&w, v)| w as f64 * v as f64 / probability).sum();
            let own_mass = normalized[p].iter().map(|&w| w as f64).sum::<f64>();
            players.push(ContinuationPlayerValue {
                position: self.cfg.positions[p].clone(),
                value_bb: net / own_mass + nd.invested[p],
            });
        }
        let total_value_bb = players.iter().map(|p| p.value_bb).sum::<f64>();
        let note = if calibrated {
            "The calibrated model embeds its training rake; this heads-up continuation does not respond to the requested rake. The unallocated amount combines embedded rake and model error, so it is not an expected-rake estimate. Send to postflop setup to solve a selected board with the requested rake."
        } else if all_in {
            "No postflop betting remains. Values use the cached heads-up equity table and the requested rake on the pot. Small accounting differences can come from equity sampling and rounding."
        } else {
            "This approximation deducts the requested rake on the starting pot. It does not model how future betting changes rake; positional adjustments and equity sampling can also affect the total. Send to postflop setup for a selected-board solve."
        };
        Some(ContinuationEstimate {
            model: model.into(), players, pot_bb: nd.pot, total_value_bb,
            unallocated_bb: nd.pot - total_value_bb,
            requested_rake_pct: self.cfg.rake_pct,
            requested_rake_cap_bb: self.cfg.rake_cap,
            rake_on_starting_pot_bb: self.rake_of(nd.pot),
            requested_rake_applied: !calibrated,
            note: note.into(),
        })
    }
}
