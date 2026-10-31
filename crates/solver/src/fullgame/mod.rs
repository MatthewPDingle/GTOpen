//! Heads-up preflop-to-river games: the Preflop Lab's two-player tree, a
//! weighted panel of flops, and one GPU postflop continuation per (called
//! preflop line, flop), all updated by the same CFR+ iterations.
//!
//! Chance: both hands come from a full deck, then a flop is drawn from the
//! panel. A hand pair and flop occur with probability proportional to the
//! flop's weight times card compatibility, normalized once at the root, so
//! preflop folds and all-ins see the same deal distribution as the flops.
//! Preflop strategies are per hand class (the game is suit-symmetric, so a
//! symmetric equilibrium exists and canonical flops stand for their suit
//! orbits); postflop strategies are per combo.
//!
//! Seeded support: a continuation holds only the classes a baseline Preflop
//! Lab solve brings to that pot. A pair with either hand outside the support
//! checks down (full-runout equity over the panel), so no preflop action is
//! forbidden; `Evaluation::outside_support` reports how much play that
//! approximation covers.
//!
//! Seat 0 (SB) acts first preflop and is out of position postflop.

pub mod equity;

use crate::cards::{combo_from_index, combo_index, rank, suit, NUM_COMBOS};
use crate::cfr::{Algorithm, Discounts, Solver};
use crate::gpu::{SharedScratch, SharedState, SymmetricContinuationGpu};
use crate::preflop::equity::{class_combos, class_index, class_label, class_prob, EquityTable, NUM_CLASSES};
use crate::preflop::{PreflopConfig, PreflopSolver, KIND_ACTION, KIND_FOLD_WIN, KIND_POT_SHARE};
use crate::tree::{StreetSizing, TreeConfig};
use crate::{Spot, SpotConfig};
use equity::PairTables;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::sync::Arc;

const N: usize = NUM_COMBOS;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FullGameConfig {
    /// Two seats, ["SB", "BB"]; sizes, limps, rake and stack as in the Preflop Lab.
    pub preflop: PreflopConfig,
    /// Canonical flops and their relative weights (normalized on build).
    pub flops: Vec<(String, f64)>,
    /// Postflop sizing per street: SB (out of position) and BB.
    pub oop: [StreetSizing; 3],
    pub ip: [StreetSizing; 3],
    #[serde(default = "default_max_raises")]
    pub max_raises: u8,
    #[serde(default = "default_allin_threshold")]
    pub allin_threshold: f64,
    #[serde(default)]
    pub add_allin: bool,
    /// Keep postflop learning state in f32 instead of 16 bits per entry.
    #[serde(default)]
    pub f32_state: bool,
    /// Park every panel flop from this index on in host memory. By default
    /// continuations stay on the GPU until it is nearly full.
    #[serde(default)]
    pub resident_flops: Option<usize>,
    /// None keeps every class in every continuation.
    #[serde(default)]
    pub support: Option<SupportSeed>,
}

fn default_max_raises() -> u8 { 1 }
fn default_allin_threshold() -> f64 { 0.85 }

/// Continuation ranges from a quick Preflop Lab solve of the same tree.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SupportSeed {
    pub iterations: u32,
    /// A class joins a pot when the baseline sends at least this fraction
    /// of its combos there.
    pub min_freq: f64,
    /// Iterations after which the support grows to the classes the full
    /// game itself sends to each pot (see `FullGame::expand_support`).
    #[serde(default)]
    pub expand_at: Vec<u32>,
}

#[derive(Clone)]
enum Node {
    Action { actor: usize, data: usize, children: Vec<usize> },
    Fold { winner: usize, pot: f64, rake: f64, inv: [f64; 2] },
    AllIn { net: f64, inv: [f64; 2] },
    Flop { leaf: usize, net: f64, inv: [f64; 2] },
}

struct Continuation {
    gpu: SymmetricContinuationGpu,
    flop: usize,
    /// Continuation hand index -> combo index, per player.
    combos: [Vec<u16>; 2],
}

/// One called preflop line that sees a flop.
pub struct FlopLeaf {
    pub path: Vec<usize>,
    pub line: String,
    pub pot: f64,
    pub behind: f64,
    /// Per class: whether the continuations hold it, per seat.
    pub support: [Vec<bool>; 2],
    conts: Vec<Continuation>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Evaluation {
    pub iteration: u32,
    /// Average-strategy EV per seat, bb per hand.
    pub evs: [f64; 2],
    /// Best-response value per seat against the other's average strategy.
    pub best_responses: [f64; 2],
    pub gaps: [f64; 2],
    pub gap_total: f64,
    /// Probability that a flop is played with a hand outside the support
    /// (settled by check-down instead of the continuation).
    pub outside_support: f64,
}

/// GPU workspaces shared by every continuation of a game.
#[derive(Default)]
struct Device {
    scratch: SharedScratch,
    state: SharedState,
    /// Largest single continuation state seen, for the parking reserve.
    largest: u64,
    parking: bool,
}

pub struct FullGame {
    pub config: FullGameConfig,
    /// The Preflop Lab tree this game was built from (shape, sizes, labels).
    tree: PreflopSolver,
    nodes: Vec<Node>,
    labels: Vec<Vec<String>>,
    regrets: Vec<f64>,
    strat: Vec<f64>,
    pub leaves: Vec<FlopLeaf>,
    flops: Vec<(String, f64)>,
    tables: PairTables,
    dev: Device,
    class_of: Vec<usize>,
    /// First combo of each class (class reach is shared by its combos).
    class_rep: Vec<usize>,
    z: f64,
    pub iteration: u32,
}

fn rake_of(cfg: &PreflopConfig, pot: f64) -> f64 {
    let r = pot * cfg.rake_pct / 100.0;
    if cfg.rake_cap > 0.0 { r.min(cfg.rake_cap) } else { r }
}

fn class_of_combo(c: usize) -> usize {
    let (a, b) = combo_from_index(c);
    class_index(rank(a), rank(b), suit(a) == suit(b))
}

fn range_string(support: &[bool]) -> String {
    (0..NUM_CLASSES).filter(|&h| support[h]).map(class_label).collect::<Vec<_>>().join(",")
}

/// One continuation per panel flop for a called line, holding the supported
/// classes. Empty when either seat has no supported class: every pair then
/// checks down.
fn build_continuations(config: &FullGameConfig, flops: &[(String, f64)], pot: f64, behind: f64,
    support: &[Vec<bool>; 2], dev: &mut Device) -> Result<Vec<Continuation>, String> {
    if support.iter().any(|s| !s.iter().any(|&x| x)) {
        return Ok(Vec::new());
    }
    let pf = &config.preflop;
    let mut conts = Vec::with_capacity(flops.len());
    for (f, (board, _)) in flops.iter().enumerate() {
        let spot = Arc::new(Spot::new(SpotConfig {
            board: board.clone(),
            range_oop: range_string(&support[0]),
            range_ip: range_string(&support[1]),
            tree: TreeConfig {
                starting_pot: pot,
                effective_stack: behind,
                rake_pct: pf.rake_pct / 100.0,
                rake_cap: pf.rake_cap,
                oop: config.oop.clone(),
                ip: config.ip.clone(),
                allin_threshold: config.allin_threshold,
                add_allin: config.add_allin,
                max_raises: config.max_raises,
                carry_aggressor_through_checks: None,
            },
        })?);
        let mut host = Solver::new(spot.clone());
        host.algo = Algorithm::CfrPlus;
        host.use_isomorphism = true;
        if spot.tree.nodes.iter().any(|n| n.kind == crate::tree::KIND_ACTION && n.num_children > 16) {
            return Err("postflop nodes may have at most 16 actions".into());
        }
        let mut gpu = SymmetricContinuationGpu::new_resident(&host, &mut dev.scratch, !config.f32_state)?;
        drop(host);
        // Keep continuations on the GPU while there is room; after that, park
        // each one in pinned host memory and stream it through one shared slot.
        if !config.f32_state {
            dev.largest = dev.largest.max(gpu.arena_bytes());
            let reserve_mb = 3000 + 2 * dev.largest / 1_000_000;
            if !dev.parking && crate::gpu::vram_info_mb().is_some_and(|(free, _)| free < reserve_mb) {
                dev.parking = true;
            }
            if dev.parking || config.resident_flops.is_some_and(|n| f >= n) {
                if crate::sysmem::avail_mem_mb().is_some_and(|m| m < 16_000.0) {
                    return Err(format!("out of host memory parking {board}; use fewer flops or a smaller menu"));
                }
                gpu.park(&mut dev.state)?;
            }
        }
        let combos = std::array::from_fn(|p| {
            spot.hands[p].iter().map(|h| combo_index(h.c1, h.c2) as u16).collect()
        });
        conts.push(Continuation { gpu, flop: f, combos });
        if let Some((free, _)) = crate::gpu::vram_info_mb() {
            if free < 1500 {
                return Err(format!(
                    "out of GPU memory building {board} ({free} MB free); \
                     use fewer flops, a smaller menu or a higher support threshold"
                ));
            }
        }
    }
    Ok(conts)
}

impl FullGame {
    /// Builds the preflop tree, the pair tables and every continuation.
    /// `log` receives one line per progress step.
    pub fn build(config: FullGameConfig, log: &mut dyn FnMut(&str)) -> Result<FullGame, String> {
        let pf = &config.preflop;
        if pf.positions.len() != 2 {
            return Err("a full game has exactly two seats (SB, BB)".into());
        }
        if pf.ante != 0.0 || pf.utg_straddle {
            return Err("full games support blinds only (no ante or straddle)".into());
        }
        if config.flops.is_empty() {
            return Err("the flop panel is empty".into());
        }
        let total: f64 = config.flops.iter().map(|f| f.1).sum();
        if !(total > 0.0) || config.flops.iter().any(|f| !(f.1 >= 0.0)) {
            return Err("flop weights must be non-negative with a positive sum".into());
        }
        let flops: Vec<(String, f64)> = config.flops.iter().map(|(b, w)| (b.clone(), w / total)).collect();

        let eq169 = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20_000));
        let tree = PreflopSolver::new(pf.clone(), eq169.clone())?;
        let mut nodes = Vec::with_capacity(tree.nodes.len());
        let mut labels: Vec<Vec<String>> = Vec::with_capacity(tree.nodes.len());
        let mut leaf_nodes = Vec::new();
        let mut arena = 0usize;
        for (i, nd) in tree.nodes.iter().enumerate() {
            let inv = [nd.invested[0], nd.invested[1]];
            labels.push(nd.actions.iter().map(|a| a.label.clone()).collect());
            nodes.push(match nd.kind {
                KIND_ACTION => {
                    arena = arena.max(nd.data_off + nd.actions.len() * NUM_CLASSES);
                    Node::Action {
                        actor: nd.actor as usize,
                        data: nd.data_off,
                        children: (0..nd.actions.len()).map(|a| tree.child(i, a)).collect(),
                    }
                }
                KIND_FOLD_WIN => Node::Fold { winner: nd.winner as usize, pot: nd.pot, rake: tree.fold_win_rake(nd), inv },
                KIND_POT_SHARE => {
                    if (inv[0] - inv[1]).abs() > 1e-9 {
                        return Err("unequal investments at a called leaf are not supported".into());
                    }
                    let net = nd.pot - rake_of(pf, nd.pot);
                    let behind = pf.stack - inv[0];
                    if behind > 1e-9 {
                        leaf_nodes.push((i, nd.pot, behind));
                        Node::Flop { leaf: leaf_nodes.len() - 1, net, inv }
                    } else {
                        Node::AllIn { net, inv }
                    }
                }
                k => return Err(format!("unknown preflop node kind {k}")),
            });
        }
        // Paths to the flop leaves.
        let mut paths = vec![None; nodes.len()];
        let mut stack = vec![(0usize, Vec::new())];
        while let Some((i, path)) = stack.pop() {
            if let Node::Action { children, .. } = &nodes[i] {
                for (a, &c) in children.iter().enumerate() {
                    let mut p = path.clone();
                    p.push(a);
                    stack.push((c, p));
                }
            }
            paths[i] = Some(path);
        }

        let supports: Vec<[Vec<bool>; 2]> = match &config.support {
            None => leaf_nodes.iter().map(|_| [vec![true; NUM_CLASSES], vec![true; NUM_CLASSES]]).collect(),
            Some(seed) => {
                log(&format!("seeding support: {} baseline iterations", seed.iterations));
                let mut base = pf.clone();
                base.realization = "balanced".into();
                let mut s = PreflopSolver::new(base, eq169)?;
                for _ in 0..seed.iterations {
                    s.iterate();
                }
                leaf_nodes
                    .iter()
                    .map(|&(i, _, _)| {
                        let (_, reaches) = s.walk(paths[i].as_ref().unwrap())?;
                        Ok(std::array::from_fn(|seat| {
                            (0..NUM_CLASSES)
                                .map(|h| reaches[seat][h] as f64 / class_prob(h) as f64 >= seed.min_freq)
                                .collect()
                        }))
                    })
                    .collect::<Result<_, String>>()?
            }
        };

        log(&format!("pair tables over {} flops", flops.len()));
        let tables = PairTables::build(&flops)?;
        let z: f64 = tables.mass.iter().map(|&m| m as f64).sum();

        let mut dev = Device::default();
        let mut leaves = Vec::with_capacity(leaf_nodes.len());
        for (k, &(i, pot, behind)) in leaf_nodes.iter().enumerate() {
            let path = paths[i].clone().unwrap();
            let mut node = 0;
            let mut line = Vec::new();
            for &a in &path {
                line.push(labels[node][a].clone());
                if let Node::Action { children, .. } = &nodes[node] {
                    node = children[a];
                }
            }
            let support = supports[k].clone();
            let conts = build_continuations(&config, &flops, pot, behind, &support, &mut dev)?;
            log(&format!("{}: pot {pot} behind {behind}, {} continuations", line.join(" "), conts.len()));
            leaves.push(FlopLeaf { path, line: line.join(" "), pot, behind, support, conts });
        }

        let class_of: Vec<usize> = (0..N).map(class_of_combo).collect();
        let mut class_rep = vec![usize::MAX; NUM_CLASSES];
        for c in 0..N {
            if class_rep[class_of[c]] == usize::MAX {
                class_rep[class_of[c]] = c;
            }
        }
        Ok(FullGame {
            config,
            tree,
            nodes,
            labels,
            regrets: vec![0.0; arena],
            strat: vec![0.0; arena],
            leaves,
            flops,
            tables,
            dev,
            class_of,
            class_rep,
            z,
            iteration: 0,
        })
    }

    /// Per flop line and seat: the fraction of each class's combos that the
    /// average strategies send there.
    pub fn leaf_frequencies(&self) -> Vec<[Vec<f64>; 2]> {
        let mut out = vec![[vec![0.0; NUM_CLASSES], vec![0.0; NUM_CLASSES]]; self.leaves.len()];
        let mut stack = vec![(0usize, [vec![1.0; NUM_CLASSES], vec![1.0; NUM_CLASSES]])];
        while let Some((node, reach)) = stack.pop() {
            match &self.nodes[node] {
                Node::Action { actor, data, children } => {
                    let sigma = self.average(*data, children.len());
                    for (a, &child) in children.iter().enumerate() {
                        let mut r = reach.clone();
                        for h in 0..NUM_CLASSES {
                            r[*actor][h] *= sigma[a * NUM_CLASSES + h];
                        }
                        stack.push((child, r));
                    }
                }
                Node::Flop { leaf, .. } => out[*leaf] = reach,
                _ => {}
            }
        }
        out
    }

    /// Adds every class the current average strategies send to a flop line at
    /// least `min_freq` of the time, and rebuilds the continuations of the
    /// lines that changed. Their postflop learning restarts; preflop learning
    /// is kept. Returns the lines rebuilt.
    pub fn expand_support(&mut self, min_freq: f64, log: &mut dyn FnMut(&str)) -> Result<Vec<usize>, String> {
        let freqs = self.leaf_frequencies();
        let mut rebuilt = Vec::new();
        for (k, freq) in freqs.iter().enumerate() {
            let old = &self.leaves[k].support;
            let new: [Vec<bool>; 2] = std::array::from_fn(|s| {
                (0..NUM_CLASSES).map(|h| old[s][h] || freq[s][h] >= min_freq).collect()
            });
            if new == *old {
                continue;
            }
            let added: Vec<usize> = (0..2).map(|s| (0..NUM_CLASSES).filter(|&h| new[s][h] && !old[s][h]).count()).collect();
            // Free the old continuations before allocating their replacements,
            // and let the replacements use the GPU room that frees.
            self.leaves[k].conts = Vec::new();
            self.dev.parking = false;
            let (pot, behind) = (self.leaves[k].pot, self.leaves[k].behind);
            self.leaves[k].conts = build_continuations(&self.config, &self.flops, pot, behind, &new, &mut self.dev)?;
            self.leaves[k].support = new;
            log(&format!("{}: support +{} SB / +{} BB classes, rebuilt", self.leaves[k].line, added[0], added[1]));
            rebuilt.push(k);
        }
        Ok(rebuilt)
    }

    pub fn leaf_device_bytes(&self, leaf: usize) -> u64 {
        self.leaves[leaf].conts.iter().map(|c| c.gpu.arena_bytes()).sum()
    }

    /// Host bytes of the parked continuations.
    pub fn host_bytes(&self) -> u64 {
        self.leaves.iter().flat_map(|l| &l.conts).map(|c| c.gpu.host_bytes()).sum()
    }

    /// Parked continuations (streamed from host memory each sweep).
    pub fn parked(&self) -> usize {
        self.leaves.iter().flat_map(|l| &l.conts).filter(|c| c.gpu.host_bytes() > 0).count()
    }

    /// Shared device workspaces: traversal scratch plus the parked-state slot.
    pub fn scratch_bytes(&self) -> u64 {
        self.dev.scratch.bytes() + self.dev.state.bytes()
    }

    pub fn continuations(&self) -> usize {
        self.leaves.iter().map(|l| l.conts.len()).sum()
    }

    pub fn device_bytes(&self) -> u64 {
        self.scratch_bytes() + self.leaves.iter().flat_map(|l| &l.conts).map(|c| c.gpu.arena_bytes()).sum::<u64>()
    }

    /// One alternating CFR+ iteration over the whole game.
    pub fn iterate(&mut self) -> Result<(), String> {
        self.iteration += 1;
        let t = self.iteration;
        for p in 0..2 {
            let reach = [vec![1.0; N], vec![1.0; N]];
            self.cfr(p, 0, &reach, t)?;
        }
        Ok(())
    }

    fn sigma(regrets: &[f64], na: usize) -> Vec<f64> {
        let mut s = vec![0.0; na * NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            let sum: f64 = (0..na).map(|a| regrets[a * NUM_CLASSES + h].max(0.0)).sum();
            for a in 0..na {
                s[a * NUM_CLASSES + h] =
                    if sum > 0.0 { regrets[a * NUM_CLASSES + h].max(0.0) / sum } else { 1.0 / na as f64 };
            }
        }
        s
    }

    /// Current strategy at an action node (na x 169, action-major).
    fn current(&self, data: usize, na: usize) -> Vec<f64> {
        Self::sigma(&self.regrets[data..data + na * NUM_CLASSES], na)
    }

    /// Average strategy at an action node (na x 169, action-major).
    fn average(&self, data: usize, na: usize) -> Vec<f64> {
        Self::sigma(&self.strat[data..data + na * NUM_CLASSES], na)
    }

    fn terminal(&self, p: usize, node: &Node, reach_q: &[f64]) -> Vec<f64> {
        match *node {
            Node::Fold { winner, pot, rake, inv } => {
                let u = if winner == p { pot - rake - inv[p] } else { -inv[p] };
                PairTables::apply(&self.tables.mass, reach_q).into_iter().map(|m| u * m).collect()
            }
            Node::AllIn { net, inv } => {
                let e = PairTables::apply(&self.tables.eq, reach_q);
                let m = PairTables::apply(&self.tables.mass, reach_q);
                e.iter().zip(&m).map(|(e, m)| net * e - inv[p] * m).collect()
            }
            _ => unreachable!(),
        }
    }

    /// Check-down value of every pair with a hand outside the leaf's support.
    fn outside_value(&self, p: usize, leaf: usize, net: f64, inv: f64, reach_q: &[f64]) -> Vec<f64> {
        let l = &self.leaves[leaf];
        let (sp, sq) = (&l.support[p], &l.support[1 - p]);
        let all_p = sp.iter().all(|&x| x) && !l.conts.is_empty();
        let all_q = sq.iter().all(|&x| x) && !l.conts.is_empty();
        if all_p && all_q {
            return vec![0.0; N];
        }
        let value = |r: &[f64]| -> Vec<f64> {
            let e = PairTables::apply(&self.tables.eq, r);
            let m = PairTables::apply(&self.tables.mass, r);
            e.iter().zip(&m).map(|(e, m)| net * e - inv * m).collect()
        };
        let full = value(reach_q);
        let no_conts = l.conts.is_empty();
        let out_q: Vec<f64> = (0..N)
            .map(|o| if no_conts || !sq[self.class_of[o]] { reach_q[o] } else { 0.0 })
            .collect();
        let part = value(&out_q);
        (0..N).map(|c| if no_conts || !sp[self.class_of[c]] { full[c] } else { part[c] }).collect()
    }

    fn cfr(&mut self, p: usize, node: usize, reach: &[Vec<f64>; 2], t: u32) -> Result<Vec<f64>, String> {
        let q = 1 - p;
        match self.nodes[node].clone() {
            Node::Action { actor, data, children } => {
                let na = children.len();
                let sigma = self.current(data, na);
                if actor == p {
                    let mut vals = Vec::with_capacity(na);
                    for (a, &child) in children.iter().enumerate() {
                        let mut r = reach.clone();
                        for c in 0..N {
                            r[p][c] *= sigma[a * NUM_CLASSES + self.class_of[c]];
                        }
                        vals.push(self.cfr(p, child, &r, t)?);
                    }
                    let mut v = vec![0.0; N];
                    for c in 0..N {
                        let h = self.class_of[c];
                        v[c] = (0..na).map(|a| sigma[a * NUM_CLASSES + h] * vals[a][c]).sum();
                    }
                    let mut delta = vec![0.0; na * NUM_CLASSES];
                    for c in 0..N {
                        let h = self.class_of[c];
                        for a in 0..na {
                            delta[a * NUM_CLASSES + h] += vals[a][c] - v[c];
                        }
                    }
                    let disc = Discounts::for_iteration(Algorithm::CfrPlus, t).strat as f64;
                    for h in 0..NUM_CLASSES {
                        let own = reach[p][self.class_rep[h]];
                        for a in 0..na {
                            let k = data + a * NUM_CLASSES + h;
                            self.regrets[k] = (self.regrets[k] + delta[a * NUM_CLASSES + h]).max(0.0);
                            self.strat[k] = self.strat[k] * disc + own * sigma[a * NUM_CLASSES + h];
                        }
                    }
                    Ok(v)
                } else {
                    let mut v = vec![0.0; N];
                    for (a, &child) in children.iter().enumerate() {
                        let mut r = reach.clone();
                        for c in 0..N {
                            r[q][c] *= sigma[a * NUM_CLASSES + self.class_of[c]];
                        }
                        let w = self.cfr(p, child, &r, t)?;
                        v.iter_mut().zip(&w).for_each(|(x, y)| *x += y);
                    }
                    Ok(v)
                }
            }
            Node::Flop { leaf, net, inv } => {
                let mut v = self.outside_value(p, leaf, net, inv[p], &reach[q]);
                let FullGame { leaves, dev, flops, .. } = self;
                for cont in &mut leaves[leaf].conts {
                    let own: Vec<f32> = cont.combos[p].iter().map(|&c| reach[p][c as usize] as f32).collect();
                    let opp: Vec<f32> = cont.combos[q].iter().map(|&c| reach[q][c as usize] as f32).collect();
                    let vals = cont.gpu.sweep_shared(&mut dev.scratch, &mut dev.state, p, t, &own, &opp)?;
                    let w = flops[cont.flop].1;
                    for (i, &c) in cont.combos[p].iter().enumerate() {
                        v[c as usize] += w * vals[i] as f64;
                    }
                }
                Ok(v)
            }
            ref term => Ok(self.terminal(p, term, &reach[q])),
        }
    }

    /// Whole-game best responses and average-strategy values for both seats.
    pub fn evaluate(&mut self) -> Result<Evaluation, String> {
        let reach = [vec![1.0; N], vec![1.0; N]];
        let mut outside = 0.0;
        let v = self.eval(0, &reach, &mut outside)?;
        let sum = |x: &[f64]| x.iter().sum::<f64>() / self.z;
        let evs = [sum(&v[0][1]), sum(&v[1][1])];
        let best_responses = [sum(&v[0][0]), sum(&v[1][0])];
        let gaps = [best_responses[0] - evs[0], best_responses[1] - evs[1]];
        Ok(Evaluation {
            iteration: self.iteration,
            evs,
            best_responses,
            gaps,
            gap_total: gaps[0] + gaps[1],
            outside_support: outside / self.z,
        })
    }

    /// values[p][mode]: mode 0 = best response of p, 1 = p's average play.
    fn eval(&mut self, node: usize, reach: &[Vec<f64>; 2], outside: &mut f64) -> Result<[[Vec<f64>; 2]; 2], String> {
        match self.nodes[node].clone() {
            Node::Action { actor, data, children } => {
                let na = children.len();
                let sigma = self.average(data, na);
                let mut kids = Vec::with_capacity(na);
                for (a, &child) in children.iter().enumerate() {
                    let mut r = reach.clone();
                    for c in 0..N {
                        r[actor][c] *= sigma[a * NUM_CLASSES + self.class_of[c]];
                    }
                    kids.push(self.eval(child, &r, outside)?);
                }
                let mut out: [[Vec<f64>; 2]; 2] = Default::default();
                for p in 0..2 {
                    for mode in 0..2 {
                        let mut v = vec![0.0; N];
                        if p != actor {
                            for k in &kids {
                                v.iter_mut().zip(&k[p][mode]).for_each(|(x, y)| *x += y);
                            }
                        } else if mode == 1 {
                            for c in 0..N {
                                let h = self.class_of[c];
                                v[c] = (0..na).map(|a| sigma[a * NUM_CLASSES + h] * kids[a][p][1][c]).sum();
                            }
                        } else {
                            let mut class_val = vec![vec![0.0; NUM_CLASSES]; na];
                            for a in 0..na {
                                for c in 0..N {
                                    class_val[a][self.class_of[c]] += kids[a][p][0][c];
                                }
                            }
                            let best: Vec<usize> = (0..NUM_CLASSES)
                                .map(|h| (0..na).fold(0, |b, a| if class_val[a][h] > class_val[b][h] { a } else { b }))
                                .collect();
                            for c in 0..N {
                                v[c] = kids[best[self.class_of[c]]][p][0][c];
                            }
                        }
                        out[p][mode] = v;
                    }
                }
                Ok(out)
            }
            Node::Flop { leaf, net, inv } => {
                let mut out: [[Vec<f64>; 2]; 2] = Default::default();
                for p in 0..2 {
                    let o = self.outside_value(p, leaf, net, inv[p], &reach[1 - p]);
                    out[p] = [o.clone(), o];
                }
                // Probability of pairs settled outside the continuations.
                let l = &self.leaves[leaf];
                let masked: Vec<f64> = (0..N)
                    .map(|o| if l.conts.is_empty() || !l.support[1][self.class_of[o]] { reach[1][o] } else { 0.0 })
                    .collect();
                let all = PairTables::apply(&self.tables.mass, &reach[1]);
                let part = PairTables::apply(&self.tables.mass, &masked);
                for c in 0..N {
                    let inside = !l.conts.is_empty() && l.support[0][self.class_of[c]];
                    *outside += reach[0][c] * if inside { part[c] } else { all[c] };
                }
                let FullGame { leaves, dev, flops, .. } = self;
                for cont in &mut leaves[leaf].conts {
                    let r: [Vec<f32>; 2] = std::array::from_fn(|q| {
                        cont.combos[q].iter().map(|&c| reach[q][c as usize] as f32).collect()
                    });
                    let vals = cont.gpu.evaluate_shared(&mut dev.scratch, &mut dev.state, [&r[0], &r[1]])?;
                    let w = flops[cont.flop].1;
                    for p in 0..2 {
                        for mode in 0..2 {
                            for (i, &c) in cont.combos[p].iter().enumerate() {
                                out[p][mode][c as usize] += w * vals[p][mode][i] as f64;
                            }
                        }
                    }
                }
                Ok(out)
            }
            ref term => {
                let v0 = self.terminal(0, term, &reach[1]);
                let v1 = self.terminal(1, term, &reach[0]);
                Ok([[v0.clone(), v0], [v1.clone(), v1]])
            }
        }
    }

    /// Average strategy at the action node reached by `path`: labels and
    /// per-class frequencies (action-major, 169 per action), plus the actor.
    pub fn strategy(&self, path: &[usize]) -> Result<(usize, Vec<String>, Vec<f64>), String> {
        let mut node = 0;
        for &a in path {
            match &self.nodes[node] {
                Node::Action { children, .. } if a < children.len() => node = children[a],
                _ => return Err("bad path".into()),
            }
        }
        match &self.nodes[node] {
            Node::Action { actor, data, children } => {
                Ok((*actor, self.labels[node].clone(), self.average(*data, children.len())))
            }
            _ => Err("path does not end at a decision".into()),
        }
    }
}

impl FullGame {
    /// The node at the end of `path`, shaped like /api/preflop/node: actions
    /// with combo-weighted frequencies, the actor's average strategy and
    /// arriving range, the line's history, and at a flop line the panel.
    pub fn node_view(&self, path: &[usize]) -> Result<Value, String> {
        let cfg = &self.config.preflop;
        let mut node = 0usize;
        let mut reach = [vec![1.0f64; NUM_CLASSES], vec![1.0f64; NUM_CLASSES]];
        let mut history = Vec::new();
        let actions_of = |i: usize, reach: &[Vec<f64>; 2]| -> (Vec<Value>, Option<Vec<f64>>) {
            let nd = &self.tree.nodes[i];
            let Node::Action { actor, data, children } = &self.nodes[i] else { return (Vec::new(), None) };
            let sigma = self.average(*data, children.len());
            let total: f64 = (0..NUM_CLASSES).map(|h| class_combos(h) as f64 * reach[*actor][h]).sum();
            let acts = nd.actions.iter().enumerate().map(|(a, act)| {
                let mass: f64 = (0..NUM_CLASSES).map(|h| class_combos(h) as f64 * reach[*actor][h] * sigma[a * NUM_CLASSES + h]).sum();
                json!({"label": act.label, "kind": act.kind, "to": act.to,
                       "freq": if total > 0.0 { mass / total } else { 0.0 }})
            }).collect();
            (acts, Some(sigma))
        };
        let kind_of = |i: usize| match self.tree.nodes[i].kind {
            KIND_ACTION => "action", KIND_FOLD_WIN => "fold_win", _ => "pot_share",
        };
        for &a in path {
            let Node::Action { actor, children, .. } = &self.nodes[node] else { return Err("bad path".into()) };
            if a >= children.len() { return Err("bad path".into()); }
            let (acts, sigma) = actions_of(node, &reach);
            history.push(json!({"strategy_note": null, "kind": "action", "actor_pos": cfg.positions[*actor],
                "pot": self.tree.nodes[node].pot, "actions": acts, "chosen": a}));
            let sigma = sigma.unwrap();
            for h in 0..NUM_CLASSES { reach[*actor][h] *= sigma[a * NUM_CLASSES + h]; }
            node = children[a];
        }
        let nd = &self.tree.nodes[node];
        let (acts, sigma) = actions_of(node, &reach);
        let actor = match &self.nodes[node] { Node::Action { actor, .. } => Some(*actor), _ => None };
        history.push(json!({"strategy_note": null, "kind": kind_of(node),
            "actor_pos": actor.map(|a| cfg.positions[a].clone()).unwrap_or_default(), "pot": nd.pot, "actions": acts, "chosen": null}));
        let live: Vec<bool> = (0..2).map(|s| nd.live & (1 << s) != 0).collect();
        let flop = match &self.nodes[node] {
            Node::Flop { leaf, .. } => {
                let l = &self.leaves[*leaf];
                Some(json!({"leaf": leaf, "line": l.line, "pot": l.pot, "behind": l.behind,
                    "solved": !l.conts.is_empty(),
                    "flops": self.flops.iter().map(|(b, w)| json!({"board": b, "weight": w})).collect::<Vec<_>>(),
                    "support": l.support.iter().map(|s| s.iter().filter(|&&x| x).count()).collect::<Vec<_>>()}))
            }
            _ => None,
        };
        let behind = cfg.stack - nd.invested[0].max(nd.invested[1]);
        Ok(json!({
            "kind": kind_of(node),
            "actor": actor,
            "actor_pos": actor.map(|a| cfg.positions[a].clone()),
            "positions": cfg.positions,
            "posts": cfg.posts,
            "pot": nd.pot,
            "invested": nd.invested,
            "live": live,
            "actions": history.last().unwrap()["actions"].clone(),
            "strategy": sigma,
            "reach": actor.map(|a| reach[a].clone()),
            "strategy_note": null,
            "exportable": flop.as_ref().is_some_and(|f| f["solved"] == true),
            "spr": flop.as_ref().map(|_| behind / nd.pot),
            "history": history,
            "reaches_all": reach.to_vec(),
            "branch_probability": 1.0,
            "low_reach": false,
            "path": path,
            "fullgame": flop,
        }))
    }

    /// A CPU postflop solver holding flop `flop` of flop line `leaf`, with
    /// the line's arriving ranges as weights, for Browse.
    pub fn flop_solver(&mut self, leaf: usize, flop: usize) -> Result<Solver, String> {
        let freq = self.leaf_frequencies().into_iter().nth(leaf).ok_or("no such flop line")?;
        let l = self.leaves.get(leaf).ok_or("no such flop line")?;
        if flop >= l.conts.len() {
            return Err("that flop has no postflop solve (no supported hands reach it)".into());
        }
        let range = |s: usize| -> String {
            (0..NUM_CLASSES).filter(|&h| l.support[s][h])
                .map(|h| format!("{}:{:.6}", class_label(h), freq[s][h].clamp(1e-6, 1.0)))
                .collect::<Vec<_>>().join(",")
        };
        let mut config = l.conts[flop].gpu.spot().config.clone();
        config.range_oop = range(0);
        config.range_ip = range(1);
        let spot = Arc::new(Spot::new(config)?);
        let mut host = Solver::with_storage(spot, crate::store::Storage::Compressed);
        host.algo = Algorithm::CfrPlus;
        self.leaves[leaf].conts[flop].gpu.export_to_cpu(&mut host)?;
        Ok(host)
    }
}

#[cfg(test)]
mod tests;
