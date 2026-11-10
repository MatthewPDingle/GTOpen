//! Realization "leafnet": the balanced model plus the learned flop correction.
//!
//! Heads-up flop terminals with chips behind are priced as under "balanced",
//! plus a per-class correction (fraction of the pot) predicted by the leaf
//! net (leafnet.rs) from both players' ranges at that terminal. The ranges
//! move while the solve runs, so the net is run again on the average
//! strategies every few iterations and its output replaces the corrections
//! the solve prices with (or is blended into them, see `refresh_weight`).
//!
//! Accuracy is always measured against the net's output at the strategies
//! being measured (`leaf_measure_begin`), whatever the solve is iterating
//! on, and a finished solve is left priced that way (`leaf_settle`). A save
//! does not store corrections, so this is also what a reload computes: a
//! loaded game shows the EVs and the gap the solve reported.
use super::equity::{class_prob, NUM_CLASSES};
use super::leafnet::{pot_type_for_raises, LeafNet, LeafSpot};
use super::{PreflopSolver, KIND_ACTION, KIND_POT_SHARE};
use rayon::prelude::*;
use std::sync::Arc;

const NO_SLOT: u32 = u32::MAX;
/// Weight of the newest net output at a refresh (None: 2/(k+1) at refresh
/// k, a linearly weighted average of all refreshes so far).
///
/// The default, 1, replaces the corrections with the net's output at the
/// average strategies. On the usual 6-max game with the loop 4 net (GPU)
/// the gap against the net's output at the current strategies then falls
/// steadily: 0.0041 bb at 2,000 iterations, 0.0019 at 4,000, 0.0010 at
/// 8,000. Weights of 0.3 and 0.5 gave 0.011 at 2,000 and 0.006 at 4,000,
/// and 0.3 jumped to 0.019 at 8,000 when one seat's blended values fell
/// behind its ranges. The linear average used before 2026-11 gave 0.033 at
/// 2,000 while the status showed 0.010. On 3-handed CPU games with the v1
/// net (examples/leaf_settle.rs) the weights from 0.3 to 1 end within
/// noise of each other, 0.001 to 0.003 by 6,000 iterations, once pruning
/// is off (see install_leaf_net). Env PREFLOP_LEAF_BLEND: a fixed weight
/// in (0, 1], or "lin" for the linear average.
const REFRESH_WEIGHT: f32 = 1.0;

fn refresh_weight() -> Option<f32> {
    match std::env::var("PREFLOP_LEAF_BLEND") {
        Ok(v) if v.trim() == "lin" => None,
        Ok(v) => Some(v.trim().parse().ok().filter(|w: &f32| *w > 0.0 && *w <= 1.0).unwrap_or(REFRESH_WEIGHT)),
        Err(_) => Some(REFRESH_WEIGHT),
    }
}

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
    /// Weight of the newest net output at a refresh (None: 2/(k+1)).
    pub(crate) weight: Option<f32>,
    /// The net's output at the average strategies of iteration `fresh_at`,
    /// laid out like `corr` (zero where a player does not reach the
    /// terminal). Empty until first computed.
    pub(crate) latest: Vec<f32>,
    pub(crate) fresh_at: Option<u32>,
    /// The blended corrections, put aside while `latest` prices a measurement.
    pub(crate) aside: Option<Vec<f32>>,
    /// Bumped whenever `corr` changes (the GPU engine re-uploads then).
    pub(crate) version: u32,
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
        let net = LeafNet::load_named(self.cfg.leaf_net.as_deref())
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
        // Regret-based pruning (CPU engine) leaves the average strategies
        // inside a line nobody currently takes as they were when it died.
        // The corrections there are then priced from stale ranges, and a
        // best response finds a gain in that line that the solve never
        // sees: a 3-handed 60 bb game stayed at 0.016 bb from iteration
        // 1,000 on (the button's aces, limping), against 0.0016 unpruned.
        // The GPU engine does not prune. PREFLOP_PRUNE=1 forces it here.
        if std::env::var("PREFLOP_PRUNE").is_err() {
            self.prune = false;
        }
        self.leaf = Some(Box::new(LeafState { net, slot, nodes, seats, corr: Vec::new(), refreshes: 0,
                                              interval: refresh_interval(), weight: refresh_weight(), latest: Vec::new(), fresh_at: None, aside: None,
                                              version: 0 }));
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

    /// Iterations between refreshes and the weight of the newest net output
    /// at each (None: 2/(k+1) at refresh k). Research: the defaults are
    /// PREFLOP_LEAF_REFRESH and PREFLOP_LEAF_BLEND.
    pub fn set_leaf_schedule(&mut self, interval: u32, weight: Option<f32>) {
        if let Some(st) = self.leaf.as_mut() {
            st.interval = interval.max(1);
            st.weight = weight;
        }
    }

    /// True when the average strategies have moved on since the net was last
    /// run on them (always false without a learned model).
    pub fn leaf_values_stale(&self) -> bool {
        self.leaf_values_stale_at(self.iteration)
    }

    /// `leaf_values_stale` for the strategies of `iteration` (a GPU engine
    /// can be ahead of the host's snapshot).
    pub fn leaf_values_stale_at(&self, iteration: u32) -> bool {
        self.leaf.as_ref().map_or(false, |st| iteration > 0 && st.fresh_at != Some(iteration))
    }

    /// The net's output at the current average strategies as a corrections
    /// table (zero where a player does not reach the terminal), and how far
    /// the stored corrections are from it: the reach-weighted mean absolute
    /// difference, as a fraction of the pot.
    fn leaf_fresh_table(&self, st: &LeafState) -> (Vec<f32>, f64) {
        let mut table = vec![0f32; st.nodes.len() * 2 * NUM_CLASSES];
        let stored = st.aside.as_ref().unwrap_or(&st.corr);
        let (mut diff, mut weight) = (0f64, 0f64);
        for (k, pred) in self.leaf_predictions(st).into_iter().enumerate() {
            let Some((new, reach, joint)) = pred else { continue };
            let at = k * 2 * NUM_CLASSES;
            for side in 0..2 {
                for h in 0..NUM_CLASSES {
                    let i = side * NUM_CLASSES + h;
                    let w = joint * reach[side][h] as f64;
                    diff += w * (new[i] - stored.get(at + i).copied().unwrap_or(0.0)).abs() as f64;
                    weight += w;
                }
            }
            table[at..at + 2 * NUM_CLASSES].copy_from_slice(&new);
        }
        (table, if weight > 0.0 { diff / weight } else { 0.0 })
    }

    /// Run the net on the current average strategies if it has not been
    /// (the corrections the solve prices with are left as they are).
    fn leaf_bring_latest(&mut self) {
        if !self.leaf_values_stale() {
            return;
        }
        let Some(mut st) = self.leaf.take() else { return };
        st.latest = self.leaf_fresh_table(&st).0;
        st.fresh_at = Some(self.iteration);
        self.leaf = Some(st);
    }

    /// Before an accuracy measurement: price with the net's output at the
    /// current average strategies until `leaf_measure_end`, instead of the
    /// blend of earlier refreshes the solve iterates on. The gap is then
    /// the gap of these strategies under the values the net gives for them,
    /// which is what a reload of this snapshot reports. A GPU engine needs
    /// `upload_leaf_corr` after this and after `leaf_measure_end`. Does
    /// nothing without a learned model.
    pub fn leaf_measure_begin(&mut self) {
        self.leaf_bring_latest();
        if let Some(st) = self.leaf.as_mut() {
            if st.aside.is_none() && !st.latest.is_empty() && st.latest != st.corr {
                st.aside = Some(std::mem::replace(&mut st.corr, st.latest.clone()));
                st.version += 1;
            }
        }
    }

    /// After the measurement: back to the corrections the solve iterates on.
    pub fn leaf_measure_end(&mut self) {
        if let Some(st) = self.leaf.as_mut() {
            if let Some(blend) = st.aside.take() {
                st.corr = blend;
                st.version += 1;
            }
        }
    }

    /// When a solve ends: leave the game priced with the net's output at
    /// its final average strategies, as a reload prices it. `force` runs
    /// the net even when the iteration has not moved (the table's rules may
    /// have changed the strategies).
    pub fn leaf_settle(&mut self, force: bool) {
        self.leaf_measure_end();
        if force {
            if let Some(st) = self.leaf.as_mut() {
                st.fresh_at = None;
            }
        }
        self.leaf_bring_latest();
        if let Some(st) = self.leaf.as_mut() {
            if !st.latest.is_empty() && st.corr != st.latest {
                st.corr = st.latest.clone();
                st.version += 1;
            }
        }
    }

    /// Best-response gaps and EVs measured as a solve reports them (see
    /// `leaf_measure_begin`), and how far the corrections the solve iterates
    /// on are from the net's output at the current strategies (reach-weighted
    /// mean absolute difference, fraction of the pot). The solve's state is
    /// left as it was. None without a learned model. For research
    /// (examples/leaf_settle.rs) and tests.
    pub fn consistent_gaps_and_evs(&mut self) -> Option<(Vec<f64>, Vec<f64>, f64)> {
        let mut st = self.leaf.take()?;
        let (table, drift) = self.leaf_fresh_table(&st);
        st.latest = table;
        st.fresh_at = Some(self.iteration);
        self.leaf = Some(st);
        self.leaf_measure_begin();
        let (gaps, evs) = self.gaps_and_evs();
        self.leaf_measure_end();
        Some((gaps, evs, drift))
    }

    /// Learned terminals: node indices, (oop, ip) seats and the current
    /// corrections (empty before the first refresh). For the GPU engine.
    pub fn leaf_terminals(&self) -> Option<(&[u32], &[[u8; 2]], &[f32])> {
        self.leaf.as_ref().map(|st| (st.nodes.as_slice(), st.seats.as_slice(), st.corr.as_slice()))
    }

    /// Number of refreshes so far.
    pub fn leaf_refreshes(&self) -> u32 {
        self.leaf.as_ref().map_or(0, |st| st.refreshes)
    }

    /// Changes whenever the corrections do (the GPU engine re-uploads then).
    pub fn leaf_version(&self) -> u32 {
        self.leaf.as_ref().map_or(0, |st| st.version)
    }

    /// A scheduled refresh: run the net on the current average strategies
    /// and blend its output into the corrections the solve prices with.
    pub fn refresh_leaf_values(&mut self) -> Option<LeafRefresh> {
        self.leaf_measure_end();
        let mut st = self.leaf.take()?;
        let fresh = self.leaf_predictions(&st);
        let n = st.nodes.len() * 2 * NUM_CLASSES;
        let first = st.corr.is_empty();
        let mut stats = LeafRefresh { terminals: st.nodes.len(), ..Default::default() };
        let w = st.weight.unwrap_or(2.0 / (st.refreshes as f32 + 2.0));
        let replace = first || w >= 1.0;
        if replace {
            // The corrections then depend on the current average strategies
            // alone; a terminal that a player does not reach is plain balanced.
            st.corr = vec![0f32; n];
        }
        let mut latest = vec![0f32; n];
        let (mut weighted, mut weight) = (0f64, 0f64);
        let (mut excess, mut excess_w) = (0f64, 0f64);
        for (k, pred) in fresh.into_iter().enumerate() {
            let Some((new, reach, joint)) = pred else { continue };
            stats.priced += 1;
            latest[k * 2 * NUM_CLASSES..(k + 1) * 2 * NUM_CLASSES].copy_from_slice(&new);
            let block = &mut st.corr[k * 2 * NUM_CLASSES..(k + 1) * 2 * NUM_CLASSES];
            for (c, n) in block.iter_mut().zip(&new) {
                *c = if replace { *n } else { (1.0 - w) * *c + w * n };
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
        st.version += 1;
        st.latest = latest;
        st.fresh_at = Some(self.iteration);
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
        // inputs of every reached terminal
        struct Leaf { k: usize, x: Vec<f32>, balanced: Vec<f32>, room: f32, norm: [Vec<f32>; 2], joint: f64 }
        let leaves: Vec<Leaf> = at.into_par_iter().enumerate().filter_map(|(k, pair)| {
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
            let x = LeafNet::features(&spot);
            let [b0, b1] = balanced;
            let balanced: Vec<f32> = b0.into_iter().chain(b1).collect();
            let norm = [std::mem::take(&mut norm[seats[0] as usize]), std::mem::take(&mut norm[seats[1] as usize])];
            Some(Leaf { k, x, balanced, room: (stack / nd.pot) as f32, norm, joint: mass[0] as f64 * mass[1] as f64 })
        }).collect();
        // the net, in batches (each weight row is read once per batch)
        const BATCH: usize = 32;
        let corrs: Vec<Vec<f32>> = leaves.par_chunks(BATCH).flat_map_iter(|chunk| {
            let xs: Vec<f32> = chunk.iter().flat_map(|l| l.x.iter().cloned()).collect();
            let out = st.net.residual_batch(&xs);
            out.chunks_exact(2 * NUM_CLASSES).map(|c| c.to_vec()).collect::<Vec<_>>()
        }).collect();
        let mut result: Vec<Option<(Vec<f32>, [Vec<f32>; 2], f64)>> = (0..st.nodes.len()).map(|_| None).collect();
        for (leaf, mut corr) in leaves.into_iter().zip(corrs) {
            // A class can lose at most what is behind and win at most the pot
            // plus what is behind: keep balanced + correction in that band.
            for (c, &b) in corr.iter_mut().zip(&leaf.balanced) {
                *c = if c.is_finite() { c.clamp(-leaf.room - b, 1.0 + leaf.room - b) } else { 0.0 };
            }
            result[leaf.k] = Some((corr, leaf.norm, leaf.joint));
        }
        result
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

/// A heads-up flop leaf of a solved game, as the learned model sees it.
#[derive(Debug, Clone, serde::Serialize)]
pub struct FlopLeaf {
    pub node: usize,
    /// Action labels from the root, e.g. "UTG Raise 2.5", "BB Call 2.5".
    pub path: Vec<String>,
    /// Out of position first.
    pub positions: [String; 2],
    pub pot_bb: f64,
    pub stack_bb: f64,
    pub raises: u8,
    /// Per-class frequencies (largest 1), out of position first.
    pub range: [Vec<f32>; 2],
    /// Chance the hand follows this line: every seat's reach mass multiplied,
    /// folded seats included (a line that needs an unlikely fold is unlikely).
    pub reach: f64,
}

impl PreflopSolver {
    /// Every heads-up flop leaf with chips behind and no side pots (the ones
    /// "leafnet" corrects), with both ranges under the average strategies.
    pub fn hu_flop_leaves(&self) -> Vec<FlopLeaf> {
        let order = self.postflop_order();
        let mut out = Vec::new();
        let mut reaches = self.root_reaches();
        let mut path = Vec::new();
        self.flop_leaf_walk(0, &mut reaches, &mut path, &order, &mut out);
        out
    }

    fn flop_leaf_walk(&self, node: usize, reaches: &mut [Vec<f32>], path: &mut Vec<String>, order: &[usize],
                      out: &mut Vec<FlopLeaf>) {
        let nd = &self.nodes[node];
        if nd.kind != KIND_ACTION {
            if nd.kind != KIND_POT_SHARE || nd.live.count_ones() != 2 || !nd.side_pots.is_empty() {
                return;
            }
            let live: Vec<usize> = order.iter().cloned().filter(|&q| nd.live & (1 << q) != 0).collect();
            let stack = live.iter().map(|&q| self.cfg.left(q, nd.invested[q])).fold(f64::MAX, f64::min);
            let mass = [reaches[live[0]].iter().sum::<f32>(), reaches[live[1]].iter().sum::<f32>()];
            if !(stack / nd.pot > 1e-9) || !(mass[0] > 1e-12 && mass[1] > 1e-12) {
                return;
            }
            let range = [0, 1].map(|side| {
                let f: Vec<f32> = (0..NUM_CLASSES).map(|h| reaches[live[side]][h] / class_prob(h)).collect();
                let max = f.iter().cloned().fold(0f32, f32::max);
                f.iter().map(|v| v / max).collect::<Vec<f32>>()
            });
            out.push(FlopLeaf {
                node, path: path.clone(), positions: [0, 1].map(|side| self.cfg.positions[live[side]].clone()),
                pot_bb: nd.pot, stack_bb: stack, raises: nd.raises, range,
                reach: reaches.iter().map(|r| r.iter().sum::<f32>() as f64).product(),
            });
            return;
        }
        let actor = nd.actor as usize;
        if reaches[actor].iter().all(|&v| v <= 0.0) {
            return;
        }
        let sigma = self.average_strategy(node);
        let saved = reaches[actor].clone();
        for a in 0..nd.actions.len() {
            for h in 0..NUM_CLASSES {
                reaches[actor][h] = saved[h] * sigma[a * NUM_CLASSES + h];
            }
            path.push(format!("{} {}", self.cfg.positions[actor], nd.actions[a].label));
            self.flop_leaf_walk(self.child(node, a), reaches, path, order, out);
            path.pop();
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

    /// With pruning on, this solve stays at 0.016 bb: the button's limp dies,
    /// the strategies behind it keep their old averages, and a best response
    /// limps aces into values the solve never sees.
    #[test]
    fn a_dead_line_leaves_no_phantom_gap() {
        assert!(game("balanced", 3).prune, "other models keep pruning");
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions": ["BTN", "SB", "BB"], "stack": 60.0, "posts": [0.0, 0.5, 1.0], "limp": true, "open_raises": [2.5],
            "raise_mults": [3.0], "max_raises": 4, "add_allin": false, "rake_pct": 5.0, "rake_cap": 3.0,
            "no_flop_no_drop": true, "realization": "leafnet",
        })).unwrap();
        // the shipped equity table: the line dies with it
        let eq = EquityTable::load_or_build(concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin"), 20_000);
        let mut s = PreflopSolver::new(cfg, Arc::new(eq)).unwrap();
        assert!(!s.prune);
        for _ in 0..800 {
            s.iterate();
        }
        let (gaps, _, _) = s.consistent_gaps_and_evs().unwrap();
        // pruned: 0.0136 for the button, 0.0178 in all
        assert!(gaps[0] < 0.004 && gaps.iter().sum::<f64>() < 0.01, "{gaps:?}");
    }

    #[test]
    fn a_zero_net_prices_exactly_balanced() {
        let mut bal = game("balanced", 3);
        bal.prune = false; // as the learned model solves (see install_leaf_net)
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
        let two_refreshes = |weight: Option<f32>| {
            let mut s = game("leafnet", 2);
            s.install_leaf_net(Arc::new(constant_net(&vec![0.02; 2 * NUM_CLASSES]))).unwrap();
            s.set_leaf_schedule(50, weight);
            for _ in 0..10 {
                s.iterate();
            }
            s.refresh_leaf_values().unwrap();
            s.leaf.as_mut().unwrap().net = Arc::new(constant_net(&vec![0.06; 2 * NUM_CLASSES]));
            s.refresh_leaf_values().unwrap();
            s
        };
        // a fixed weight on the newest output; 1 replaces
        for (weight, want) in [(Some(0.25f32), 0.03f32), (Some(1.0), 0.06), (None, 0.02 / 3.0 + 0.06 * 2.0 / 3.0)] {
            let s = two_refreshes(weight);
            let st = s.leaf.as_ref().unwrap();
            assert!(st.corr.iter().all(|&c| (c - want).abs() < 1e-6), "weight {weight:?}: {}", st.corr[0]);
            // whatever the blend, the newest output is kept for measurements
            assert!(st.latest.iter().all(|&c| (c - 0.06).abs() < 1e-6));
        }
        let mut s = two_refreshes(Some(1.0));
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
        s.leaf_settle(false); // as a finished solve is left
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
        // the solve refreshed at its last iteration, so the reload prices and measures the same
        assert!(!s.leaf_values_stale() && !loaded.leaf_values_stale());
        assert_eq!(loaded.leaf.as_ref().unwrap().corr, s.leaf.as_ref().unwrap().corr);
        assert_eq!(loaded.gaps_and_evs(), (gaps, evs));
    }

    #[test]
    fn accuracy_is_measured_at_the_current_strategies() {
        for weight in [Some(1.0f32), Some(0.3), None] {
            let mut s = game("leafnet", 3);
            s.set_leaf_schedule(25, weight);
            for _ in 0..90 {
                s.iterate();
            }
            // 15 iterations after the last refresh the net has not seen these strategies
            assert!(s.leaf_values_stale());
            let iterating = s.gaps_and_evs();
            let blend = s.leaf.as_ref().unwrap().corr.clone();
            let version = s.leaf_version();
            // a measurement prices with the net's output at these strategies ...
            s.leaf_measure_begin();
            assert!(!s.leaf_values_stale() && s.leaf_version() > version, "weight {weight:?}");
            let measured = s.gaps_and_evs();
            assert_ne!(measured, iterating);
            // ... and hands the solve back the corrections it was iterating on
            s.leaf_measure_end();
            assert_eq!(s.leaf.as_ref().unwrap().corr, blend);
            assert_eq!(s.gaps_and_evs(), iterating);
            let (gaps, evs, drift) = s.consistent_gaps_and_evs().unwrap();
            assert_eq!((gaps, evs), measured);
            assert!(drift > 0.0);
            assert_eq!(s.leaf.as_ref().unwrap().corr, blend);
            // a finished solve is left priced as it was measured, and its save reloads that way
            s.leaf_settle(false);
            assert_eq!(s.gaps_and_evs(), measured);
            assert_eq!(s.consistent_gaps_and_evs().unwrap().2, 0.0);
            let path = std::env::temp_dir().join(format!("leafnet_gap_{}_{:?}.bin", std::process::id(), weight.map(|w| (w * 10.0) as u32)));
            let path = path.to_str().unwrap();
            s.save_game(path).unwrap();
            let loaded = PreflopSolver::load_game(path, table()).unwrap();
            std::fs::remove_file(path).ok();
            assert_eq!(loaded.leaf.as_ref().unwrap().corr, s.leaf.as_ref().unwrap().corr);
            assert_eq!(loaded.gaps_and_evs(), measured);
        }
    }

    #[test]
    fn a_measurement_right_after_a_replacing_refresh_changes_nothing() {
        let mut s = game("leafnet", 3);
        s.set_leaf_schedule(25, Some(1.0));
        for _ in 0..50 {
            s.iterate();
        }
        let (version, before) = (s.leaf_version(), s.gaps_and_evs());
        s.leaf_measure_begin();
        assert_eq!((s.leaf_version(), s.gaps_and_evs()), (version, before.clone()));
        s.leaf_measure_end();
        s.leaf_settle(false);
        assert_eq!((s.leaf_version(), s.gaps_and_evs()), (version, before));
        // with a blend the corrections are behind even then, and the GPU must be told
        let mut s = game("leafnet", 3);
        s.set_leaf_schedule(25, Some(0.3));
        for _ in 0..50 {
            s.iterate();
        }
        let (version, iterating) = (s.leaf_version(), s.gaps_and_evs());
        s.leaf_measure_begin();
        assert!(s.leaf_version() > version && s.gaps_and_evs() != iterating);
        s.leaf_measure_end();
        assert!(s.leaf_version() > version + 1);
        assert_eq!(s.gaps_and_evs(), iterating);
        // changed rules at the same iteration: only a forced settle looks again
        let fresh_at = s.leaf.as_ref().unwrap().fresh_at;
        s.leaf.as_mut().unwrap().latest.iter_mut().for_each(|c| *c = 9.0);
        s.leaf_settle(false);
        assert!(s.leaf.as_ref().unwrap().corr.iter().all(|&c| c == 9.0));
        s.leaf_settle(true);
        assert!(s.leaf.as_ref().unwrap().corr.iter().all(|&c| c != 9.0));
        assert_eq!(s.leaf.as_ref().unwrap().fresh_at, fresh_at);
    }

    #[test]
    fn flop_leaves_match_the_learned_terminals() {
        let mut s = game("leafnet", 3);
        for _ in 0..20 {
            s.iterate();
        }
        let leaves = s.hu_flop_leaves();
        let st = s.leaf.as_ref().unwrap();
        assert!(!leaves.is_empty() && leaves.len() <= st.nodes.len());
        for l in &leaves {
            let k = st.slot[l.node] as usize;
            assert!(k < st.nodes.len(), "every exported leaf is a learned terminal");
            assert_eq!(l.positions[0], s.cfg.positions[st.seats[k][0] as usize], "out of position first");
            assert!(l.range.iter().all(|r| r.iter().cloned().fold(0f32, f32::max) == 1.0));
            assert!(l.reach > 0.0 && l.pot_bb > 0.0 && l.stack_bb > 0.0 && !l.path.is_empty());
        }
    }

    #[test]
    fn flop_leaf_reach_counts_the_seats_that_folded() {
        let mut s = game("leafnet", 3);
        for _ in 0..20 {
            s.iterate();
        }
        let leaves = s.hu_flop_leaves();
        // Lines are disjoint, so their probabilities add up to at most 1.
        let total: f64 = leaves.iter().map(|l| l.reach).sum();
        assert!(total > 0.0 && total <= 1.0 + 1e-5, "total reach {total}");
        // Replay every leaf's line from the root: the chance of a line is the
        // product over all seats, folded ones included, of the chance that
        // seat's hand takes its actions on the line.
        let mut checked_folds = 0;
        for l in &leaves {
            let mut seat = vec![(0..NUM_CLASSES).map(|h| class_prob(h) as f64).collect::<Vec<f64>>(); 3];
            let mut node = 0;
            for step in &l.path {
                let nd = &s.nodes[node];
                let actor = nd.actor as usize;
                let a = nd.actions.iter()
                    .position(|x| format!("{} {}", s.cfg.positions[actor], x.label) == *step)
                    .expect("path step is an action");
                let sigma = s.average_strategy(node);
                for h in 0..NUM_CLASSES {
                    seat[actor][h] *= sigma[a * NUM_CLASSES + h] as f64;
                }
                node = s.child(node, a);
            }
            assert_eq!(node, l.node);
            let want: f64 = seat.iter().map(|v| v.iter().sum::<f64>()).product();
            assert!((l.reach - want).abs() <= 1e-5 * want.max(1e-9), "{:?}: {} vs {want}", l.path, l.reach);
            checked_folds += l.path.iter().any(|x| x.ends_with("Fold")) as usize;
        }
        assert!(checked_folds > 0, "some leaves follow a fold");
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
