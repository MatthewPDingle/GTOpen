//! Realization "leafnet": the balanced model plus the learned flop correction.
//!
//! Heads-up flop terminals with chips behind are priced as under "balanced",
//! plus a per-class correction (fraction of the pot) predicted by the leaf
//! net (leafnet.rs) from both players' ranges at that terminal. The ranges
//! move while the solve runs, so the corrections are recomputed from the
//! average strategies every few iterations and blended with the previous
//! ones, which keeps the pricing from jumping between refreshes.
use super::equity::{class_prob, NUM_CLASSES};
use super::leafnet::{pot_type_for_raises, LeafNet, LeafSpot};
use super::{PreflopSolver, KIND_ACTION, KIND_POT_SHARE};
use rayon::prelude::*;
use std::sync::Arc;

const NO_SLOT: u32 = u32::MAX;
/// Weight of the newest net output when blending refreshes.
const BLEND: f32 = 0.5;

pub(crate) struct LeafState {
    pub(crate) net: Arc<LeafNet>,
    /// Per node: index of its learned terminal, or NO_SLOT.
    pub(crate) slot: Vec<u32>,
    /// Per learned terminal: its node and its (out of position, in position) seats.
    pub(crate) nodes: Vec<u32>,
    pub(crate) seats: Vec<[u8; 2]>,
    /// Corrections, terminal-major: [terminal][oop, ip][169]. Empty until the
    /// first refresh (pricing is then exactly balanced).
    pub(crate) corr: Vec<f32>,
    pub(crate) refreshes: u32,
    pub(crate) interval: u32,
}

/// Iterations between refreshes (env PREFLOP_LEAF_REFRESH, default 50).
fn refresh_interval() -> u32 {
    std::env::var("PREFLOP_LEAF_REFRESH").ok().and_then(|v| v.parse().ok()).filter(|&v| v > 0).unwrap_or(50)
}

/// Summary of one refresh, for logs and tests.
#[derive(Debug, Clone, Default)]
pub struct LeafRefresh {
    /// Learned terminals that both players reach with positive mass.
    pub priced: usize,
    pub terminals: usize,
    /// Reach-weighted mean |correction| and largest |correction|, fraction of the pot.
    pub mean_abs: f64,
    pub max_abs: f64,
    /// Mean over terminals (weighted by how often both players get there) of
    /// the chips the corrections add to the pot: oop's range-average
    /// correction plus ip's. Zero would mean the net only moves value
    /// between the players; positive means postflop play is worth more
    /// than balanced says to both of them.
    pub mean_excess: f64,
}

impl PreflopSolver {
    /// Load the net and find the learned terminals (called from `new`).
    pub(super) fn install_leaf_model(&mut self) -> Result<(), String> {
        let net = LeafNet::load_default()
            .map_err(|e| format!("the learned realization needs its leaf net ({e}); set LEAF_NET or pick another realization"))?;
        self.install_leaf_net(Arc::new(net))
    }

    /// Use a specific net (tests; research).
    pub fn install_leaf_net(&mut self, net: Arc<LeafNet>) -> Result<(), String> {
        if self.cfg.realization != "leafnet" {
            return Err("the leaf net is only used under realization \"leafnet\"".into());
        }
        if self.cfg.icm.is_some() {
            return Err("the learned realization does not support ICM payouts yet".into());
        }
        if self.fit.is_none() {
            return Err("the learned realization needs the balanced realization fit (cache/realization_fit.json)".into());
        }
        let order = self.postflop_order();
        let mut slot = vec![NO_SLOT; self.nodes.len()];
        let (mut nodes, mut seats) = (Vec::new(), Vec::new());
        for (i, nd) in self.nodes.iter().enumerate() {
            if nd.kind != KIND_POT_SHARE || nd.live.count_ones() != 2 || !nd.side_pots.is_empty() {
                continue;
            }
            let live: Vec<usize> = order.iter().cloned().filter(|&q| nd.live & (1 << q) != 0).collect();
            let left = live.iter().map(|&q| self.cfg.left(q, nd.invested[q])).fold(f64::MAX, f64::min);
            if !(left / nd.pot > 1e-9) {
                continue; // all in: no postflop play to learn
            }
            slot[i] = nodes.len() as u32;
            nodes.push(i as u32);
            seats.push([live[0] as u8, live[1] as u8]);
        }
        self.leaf = Some(Box::new(LeafState { net, slot, nodes, seats, corr: Vec::new(), refreshes: 0,
                                              interval: refresh_interval() }));
        Ok(())
    }

    /// The learned correction for seat `p` at terminal `node`, if any.
    #[inline]
    pub(super) fn leaf_correction(&self, node: usize, p: usize) -> Option<&[f32]> {
        let st = self.leaf.as_ref()?;
        let k = *st.slot.get(node)?;
        if k == NO_SLOT || st.corr.is_empty() {
            return None;
        }
        let side = if st.seats[k as usize][0] as usize == p { 0 } else { 1 };
        let at = (k as usize * 2 + side) * NUM_CLASSES;
        Some(&st.corr[at..at + NUM_CLASSES])
    }

    pub fn leaf_refresh_due(&self, iteration: u32) -> bool {
        self.leaf.as_ref().map_or(false, |st| iteration > 0 && iteration % st.interval == 0)
    }

    /// Learned terminals: node indices, (oop, ip) seats and the current
    /// corrections (empty before the first refresh). For the GPU engine.
    pub fn leaf_terminals(&self) -> Option<(&[u32], &[[u8; 2]], &[f32])> {
        self.leaf.as_ref().map(|st| (st.nodes.as_slice(), st.seats.as_slice(), st.corr.as_slice()))
    }

    /// Number of refreshes so far (the GPU engine re-uploads when it changes).
    pub fn leaf_refreshes(&self) -> u32 {
        self.leaf.as_ref().map_or(0, |st| st.refreshes)
    }

    /// Recompute the corrections from the current average strategies.
    pub fn refresh_leaf_values(&mut self) -> Option<LeafRefresh> {
        let mut st = self.leaf.take()?;
        let fresh = self.leaf_predictions(&st);
        let first = st.corr.is_empty();
        if first {
            st.corr = vec![0f32; st.nodes.len() * 2 * NUM_CLASSES];
        }
        let mut stats = LeafRefresh { terminals: st.nodes.len(), ..Default::default() };
        let (mut weighted, mut weight) = (0f64, 0f64);
        let (mut excess, mut excess_w) = (0f64, 0f64);
        for (k, pred) in fresh.into_iter().enumerate() {
            let Some((new, reach, joint)) = pred else { continue };
            stats.priced += 1;
            let block = &mut st.corr[k * 2 * NUM_CLASSES..(k + 1) * 2 * NUM_CLASSES];
            for (c, n) in block.iter_mut().zip(&new) {
                *c = if first { *n } else { (1.0 - BLEND) * *c + BLEND * n };
                stats.max_abs = stats.max_abs.max(c.abs() as f64);
            }
            let mut added = 0f64;
            for side in 0..2 {
                for h in 0..NUM_CLASSES {
                    let w = reach[side][h] as f64;
                    weighted += joint * w * block[side * NUM_CLASSES + h].abs() as f64;
                    weight += joint * w;
                    added += w * block[side * NUM_CLASSES + h] as f64;
                }
            }
            excess += joint * added;
            excess_w += joint;
        }
        stats.mean_abs = if weight > 0.0 { weighted / weight } else { 0.0 };
        stats.mean_excess = if excess_w > 0.0 { excess / excess_w } else { 0.0 };
        st.refreshes += 1;
        self.leaf = Some(st);
        Some(stats)
    }

    /// Net corrections per learned terminal (None where a player never gets
    /// there), with both seats' normalized reaches and the product of their
    /// reach masses, for weighting. Runs with
    /// `self.leaf` taken, so terminal_value prices plain balanced.
    fn leaf_predictions(&self, st: &LeafState) -> Vec<Option<(Vec<f32>, [Vec<f32>; 2], f64)>> {
        // reaches of both seats at every learned terminal, under the average strategies
        let mut at: Vec<Option<[Vec<f32>; 2]>> = vec![None; st.nodes.len()];
        let mut reaches: Vec<Vec<f32>> = self.root_reaches();
        self.leaf_walk(0, &mut reaches, st, &mut at);
        at.into_par_iter().enumerate().map(|(k, pair)| {
            let pair = pair?;
            let node = st.nodes[k] as usize;
            let nd = &self.nodes[node];
            let mass = [pair[0].iter().sum::<f32>(), pair[1].iter().sum::<f32>()];
            if !(mass[0] > 1e-12 && mass[1] > 1e-12) {
                return None;
            }
            // balanced values with every seat's reach normalized (prob = 1)
            let mut norm: Vec<Vec<f32>> = (0..self.n).map(|_| (0..NUM_CLASSES).map(class_prob).collect()).collect();
            let seats = st.seats[k];
            for side in 0..2 {
                norm[seats[side] as usize] = pair[side].iter().map(|v| v / mass[side]).collect();
            }
            let mut balanced = [vec![0f32; NUM_CLASSES], vec![0f32; NUM_CLASSES]];
            let mut range = [vec![0f32; NUM_CLASSES], vec![0f32; NUM_CLASSES]];
            for side in 0..2 {
                let seat = seats[side] as usize;
                let mut v = [0f32; NUM_CLASSES];
                self.terminal_value(node, seat, &norm, &mut v);
                let inv = nd.invested[seat];
                for h in 0..NUM_CLASSES {
                    balanced[side][h] = ((v[h] as f64 + inv) / nd.pot) as f32;
                    range[side][h] = norm[seat][h] / class_prob(h);
                }
            }
            let stack = seats.iter().map(|&q| self.cfg.left(q as usize, nd.invested[q as usize])).fold(f64::MAX, f64::min);
            let spot = LeafSpot {
                range: [&range[0], &range[1]], balanced: [&balanced[0], &balanced[1]], pot_bb: nd.pot,
                stack_bb: stack, rake_frac: self.cfg.rake_pct / 100.0, rake_cap_bb: self.cfg.rake_cap,
                pot_type: pot_type_for_raises(nd.raises),
            };
            let mut corr = st.net.residual(&LeafNet::features(&spot));
            // A class can lose at most what is behind and win at most the pot
            // plus what is behind: keep balanced + correction in that band.
            let room = (stack / nd.pot) as f32;
            for side in 0..2 {
                for h in 0..NUM_CLASSES {
                    let b = balanced[side][h];
                    let c = &mut corr[side * NUM_CLASSES + h];
                    *c = if c.is_finite() { c.clamp(-room - b, 1.0 + room - b) } else { 0.0 };
                }
            }
            let joint = mass[0] as f64 * mass[1] as f64;
            Some((corr, [norm[seats[0] as usize].clone(), norm[seats[1] as usize].clone()], joint))
        }).collect()
    }

    fn leaf_walk(&self, node: usize, reaches: &mut [Vec<f32>], st: &LeafState, at: &mut [Option<[Vec<f32>; 2]>]) {
        let nd = &self.nodes[node];
        if nd.kind != KIND_ACTION {
            let k = st.slot[node];
            if k != NO_SLOT {
                let s = st.seats[k as usize];
                at[k as usize] = Some([reaches[s[0] as usize].clone(), reaches[s[1] as usize].clone()]);
            }
            return;
        }
        let actor = nd.actor as usize;
        if reaches[actor].iter().all(|&v| v <= 0.0) {
            return; // nothing below is reached
        }
        let sigma = self.average_strategy(node);
        let saved = reaches[actor].clone();
        for a in 0..nd.actions.len() {
            for h in 0..NUM_CLASSES {
                reaches[actor][h] = saved[h] * sigma[a * NUM_CLASSES + h];
            }
            self.leaf_walk(self.child(node, a), reaches, st, at);
        }
        reaches[actor] = saved;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::equity::EquityTable;
    use crate::preflop::leafnet::constant_net;
    use crate::preflop::PreflopConfig;

    fn table() -> Arc<EquityTable> {
        static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
        T.get_or_init(|| Arc::new(EquityTable::build(300))).clone()
    }

    fn game(realization: &str, n: usize) -> PreflopSolver {
        let mut posts = vec![0.0; n];
        posts[n - 2] = 0.5;
        posts[n - 1] = 1.0;
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions": (0..n).map(|p| format!("P{p}")).collect::<Vec<_>>(), "stack": 30.0,
            "posts": posts, "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
            "add_allin": true, "rake_pct": 5.0, "rake_cap": 2.0, "realization": realization,
        })).unwrap();
        PreflopSolver::new(cfg, table()).unwrap()
    }

    /// Different values per class and per side, so a swapped side or class shows.
    pub(crate) fn pattern(scale: f32) -> Vec<f32> {
        (0..2 * NUM_CLASSES).map(|k| scale * (((k * 7) % 11) as f32 - 5.0) / 5.0 + if k < NUM_CLASSES { 0.01 } else { -0.02 }).collect()
    }

    #[test]
    fn a_zero_net_prices_exactly_balanced() {
        let mut bal = game("balanced", 3);
        let mut leaf = game("leafnet", 3);
        leaf.install_leaf_net(Arc::new(constant_net(&vec![0.0; 2 * NUM_CLASSES]))).unwrap();
        leaf.leaf.as_mut().unwrap().interval = 10;
        assert!(leaf.leaf.as_ref().unwrap().nodes.len() > 3, "the game has heads-up flops");
        for _ in 0..40 {
            bal.iterate();
            leaf.iterate();
        }
        assert_eq!(leaf.leaf_refreshes(), 4);
        assert_eq!(bal.arena_snapshot(), leaf.arena_snapshot());
        assert_eq!(bal.gaps_and_evs(), leaf.gaps_and_evs());
    }

    #[test]
    fn corrections_land_on_the_right_seat_and_class() {
        let mut s = game("leafnet", 3);
        let bias = pattern(0.03);
        s.install_leaf_net(Arc::new(constant_net(&bias))).unwrap();
        for _ in 0..20 {
            s.iterate();
        }
        let stats = s.refresh_leaf_values().unwrap();
        assert!(stats.priced > 0 && stats.mean_abs > 0.0);
        let st = s.leaf.as_ref().unwrap();
        let (nodes, seats) = (st.nodes.clone(), st.seats.clone());
        let reaches: Vec<Vec<f32>> = (0..s.n).map(|q| (0..NUM_CLASSES).map(|h| class_prob(h) * (1.0 + 0.1 * q as f32)).collect()).collect();
        for (k, &node) in nodes.iter().enumerate() {
            let nd = &s.nodes[node as usize];
            let prob = |p: usize| (0..s.n).filter(|&q| q != p).map(|q| reaches[q].iter().sum::<f32>() as f64).product::<f64>();
            for side in 0..2 {
                let seat = seats[k][side] as usize;
                let mut with = [0f32; NUM_CLASSES];
                s.terminal_value(node as usize, seat, &reaches, &mut with);
                let saved = s.leaf.take();
                let mut without = [0f32; NUM_CLASSES];
                s.terminal_value(node as usize, seat, &reaches, &mut without);
                s.leaf = saved;
                for h in 0..NUM_CLASSES {
                    let expect = prob(seat) * nd.pot * bias[side * NUM_CLASSES + h] as f64;
                    let got = (with[h] - without[h]) as f64;
                    assert!((got - expect).abs() < 1e-4 * (1.0 + expect.abs()), "leaf {k} side {side} class {h}: {got} vs {expect}");
                }
            }
        }
    }

    #[test]
    fn refreshes_blend_and_stay_in_the_possible_range() {
        let mut s = game("leafnet", 2);
        s.install_leaf_net(Arc::new(constant_net(&vec![0.02; 2 * NUM_CLASSES]))).unwrap();
        for _ in 0..10 {
            s.iterate();
        }
        s.refresh_leaf_values().unwrap();
        s.leaf.as_mut().unwrap().net = Arc::new(constant_net(&vec![0.06; 2 * NUM_CLASSES]));
        s.refresh_leaf_values().unwrap();
        let corr = &s.leaf.as_ref().unwrap().corr;
        assert!(corr.iter().all(|&c| (c - 0.04).abs() < 1e-6), "half old, half new");
        // an absurd net output is held to what a hand can win or lose
        s.leaf.as_mut().unwrap().net = Arc::new(constant_net(&vec![50.0; 2 * NUM_CLASSES]));
        s.leaf.as_mut().unwrap().corr.clear();
        s.refresh_leaf_values().unwrap();
        let st = s.leaf.as_ref().unwrap();
        for (k, &node) in st.nodes.iter().enumerate() {
            let nd = &s.nodes[node as usize];
            let room = st.seats[k].iter().map(|&q| s.cfg.left(q as usize, nd.invested[q as usize])).fold(f64::MAX, f64::min) / nd.pot;
            let block = &st.corr[k * 2 * NUM_CLASSES..(k + 1) * 2 * NUM_CLASSES];
            assert!(block.iter().all(|&c| c > 0.0 && (c as f64) <= 1.0 + room + 1e-6));
        }
    }

    #[test]
    fn the_shipped_net_solves_and_survives_a_save() {
        let mut s = game("leafnet", 2);
        s.leaf.as_mut().unwrap().interval = 25;
        for _ in 0..100 {
            s.iterate();
        }
        assert_eq!(s.leaf_refreshes(), 4);
        let (gaps, evs) = s.gaps_and_evs();
        assert!(gaps.iter().chain(&evs).all(|v| v.is_finite()));
        assert!(s.leaf.as_ref().unwrap().corr.iter().any(|&c| c.abs() > 1e-3), "the net corrects something");
        let path = std::env::temp_dir().join(format!("leafnet_save_{}.bin", std::process::id()));
        let path = path.to_str().unwrap();
        s.save_game(path).unwrap();
        let loaded = PreflopSolver::load_game(path, table()).unwrap();
        std::fs::remove_file(path).ok();
        assert_eq!(loaded.cfg.realization, "leafnet");
        assert_eq!(loaded.leaf_refreshes(), 1, "corrections are recomputed on load");
        assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    }

    #[test]
    fn icm_games_refuse_the_learned_model() {
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions": ["SB", "BB"], "stack": 20.0, "posts": [0.5, 1.0], "open_raises": [2.0],
            "raise_mults": [3.0], "max_raises": 2, "add_allin": true, "realization": "leafnet",
            "icm": {"payouts": [60.0, 40.0], "field": []},
        })).unwrap();
        let err = PreflopSolver::new(cfg, table()).err().expect("ICM + leafnet must fail");
        assert!(err.contains("ICM"), "{err}");
    }
}
