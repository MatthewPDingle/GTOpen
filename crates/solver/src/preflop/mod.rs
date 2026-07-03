//! Multiway preflop solver over a postflop equity-realization model.
//!
//! Solves N-player (2..9) preflop trees EXACTLY at the action level — limps,
//! cold calls, arbitrary raise sizes, antes, rake — with postflop play priced
//! by a model instead of solved: when the flop is reached, each live player's
//! share of the pot is `pot * multiway_equity * R`, where R is a pluggable
//! realization factor (R = 1 when all-in, i.e. those terminals are exact
//! within the equity table's accuracy).
//!
//! Hands are the 169 canonical classes with combo weighting; cross-player
//! blocker effects beyond the pairwise equity table are ignored (mean-field,
//! the standard preflop-solver approximation). Multiway equity uses the
//! product approximation (exact heads-up). CFR is DCFR with the same
//! discounting constants as the postflop engine. For 3+ players CFR yields
//! "an equilibrium", not a unique GTO answer — the convergence report is the
//! per-player best-response gap against the model.

pub mod equity;

use equity::{class_prob, EquityTable, NUM_CLASSES};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

const KIND_ACTION: u8 = 0;
const KIND_FOLD_WIN: u8 = 1;
const KIND_POT_SHARE: u8 = 2;

// DCFR constants (match the postflop engine: alpha=1.5, beta=0, gamma=2)
const DCFR_ALPHA: f64 = 1.5;
const DCFR_GAMMA: f64 = 2.0;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PreflopConfig {
    /// Seats in PREFLOP acting order (e.g. UTG,HJ,CO,BTN,SB,BB).
    pub positions: Vec<String>,
    /// Starting stack in bb (v1: must be equal for all seats — no side pots).
    pub stack: f64,
    /// Blind/straddle posted per seat, aligned with `positions` (counts
    /// toward calling); e.g. [0,0,0,0,0.5,1].
    pub posts: Vec<f64>,
    /// Dead ante per seat (goes to the pot, does not count toward calls).
    #[serde(default)]
    pub ante: f64,
    /// Allow open-limps / limps behind (calls with no raise pending).
    #[serde(default)]
    pub limp: bool,
    /// First-raise TO-amounts in bb (e.g. [2.5] or [2.0, 2.5, 3.0]).
    pub open_raises: Vec<f64>,
    /// Re-raise TO-amount as multiples of the current bet (e.g. [3.0]).
    pub raise_mults: Vec<f64>,
    /// Max raises in total (open counts as the first).
    #[serde(default = "default_max_raises")]
    pub max_raises: u8,
    /// Always offer jam as a raise option.
    #[serde(default)]
    pub add_allin: bool,
    /// A raise TO more than this fraction of the stack becomes a jam.
    #[serde(default = "default_allin_threshold")]
    pub allin_threshold: f64,
    /// Rake in percent (e.g. 5.0) with a cap in bb; taken from pots that see
    /// a flop (and from preflop fold-outs too when no_flop_no_drop = false).
    #[serde(default)]
    pub rake_pct: f64,
    #[serde(default)]
    pub rake_cap: f64,
    #[serde(default = "default_true")]
    pub no_flop_no_drop: bool,
    /// "raw" (R = 1) or "static" (positional realization vs SPR).
    #[serde(default = "default_realization")]
    pub realization: String,
}

fn default_max_raises() -> u8 {
    4
}
fn default_allin_threshold() -> f64 {
    0.85
}
fn default_true() -> bool {
    true
}
fn default_realization() -> String {
    "static".to_string()
}

#[derive(Debug, Clone, Serialize)]
pub struct PAction {
    /// "fold" | "check" | "call" | "raise" | "jam"
    pub kind: String,
    /// TO-amount in bb (raises/jams; call amount for calls).
    pub to: f64,
    pub label: String,
}

pub struct PNode {
    pub kind: u8,
    pub actor: u8,
    pub actions: Vec<PAction>,
    pub child_start: u32,
    pub pot: f64,
    pub invested: Vec<f64>,
    pub live: u32,
    pub winner: u8,
    /// pot_share: per-seat realization weight (1.0 under "raw").
    pub r: Vec<f32>,
    /// action nodes: offset into the regret/strategy arenas.
    pub data_off: usize,
}

struct BuildState {
    invested: Vec<f64>,
    folded: u32,
    allin: u32,
    needs: u32,
    to_call: f64,
    last_raise: f64,
    raises: u8,
    next_seat: usize,
}

pub struct PreflopSolver {
    pub cfg: PreflopConfig,
    pub eq: Arc<EquityTable>,
    pub nodes: Vec<PNode>,
    children: Vec<u32>,
    pub n: usize,
    regrets: Vec<f32>,
    strat_sum: Vec<f32>,
    arena_len: usize,
    pub iteration: u32,
}

impl PreflopSolver {
    pub fn new(cfg: PreflopConfig, eq: Arc<EquityTable>) -> Result<Self, String> {
        let n = cfg.positions.len();
        if !(2..=9).contains(&n) {
            return Err("2..9 positions required".into());
        }
        if cfg.posts.len() != n {
            return Err("posts must align with positions".into());
        }
        if cfg.stack <= *cfg.posts.iter().last().unwrap_or(&0.0) {
            return Err("stack must exceed the biggest blind".into());
        }
        if cfg.open_raises.is_empty() && !cfg.limp && !cfg.add_allin {
            return Err("no legal opening actions: enable limp, a raise size or all-in".into());
        }
        let mut s = PreflopSolver {
            cfg,
            eq,
            nodes: Vec::new(),
            children: Vec::new(),
            n,
            regrets: Vec::new(),
            strat_sum: Vec::new(),
            arena_len: 0,
            iteration: 0,
        };
        let init = BuildState {
            invested: (0..n).map(|i| s.cfg.posts[i] + s.cfg.ante).collect(),
            folded: 0,
            allin: 0,
            needs: (1u32 << n) - 1,
            to_call: s.cfg.posts.iter().cloned().fold(0.0, f64::max),
            last_raise: s.cfg.posts.iter().cloned().fold(0.0, f64::max).max(1.0),
            raises: 0,
            next_seat: 0,
        };
        s.build(init)?;
        s.regrets = vec![0.0; s.arena_len];
        s.strat_sum = vec![0.0; s.arena_len];
        Ok(s)
    }

    /// Postflop acting order: seats with posts first (SB before BB by post
    /// size), then the rest in seat order (matches standard table layouts).
    pub fn postflop_order(&self) -> Vec<usize> {
        let mut blinds: Vec<usize> = (0..self.n).filter(|&i| self.cfg.posts[i] > 0.0).collect();
        blinds.sort_by(|&a, &b| self.cfg.posts[a].partial_cmp(&self.cfg.posts[b]).unwrap());
        let mut out = blinds.clone();
        out.extend((0..self.n).filter(|i| !blinds.contains(i)));
        out
    }

    fn live_count(&self, live: u32) -> usize {
        live.count_ones() as usize
    }

    fn realization_weights(&self, live: u32, invested: &[f64], pot: f64) -> Vec<f32> {
        let mut r = vec![0f32; self.n];
        let spr = {
            let mut min_left = f64::MAX;
            for i in 0..self.n {
                if live & (1 << i) != 0 {
                    min_left = min_left.min(self.cfg.stack - invested[i] + self.cfg.ante);
                }
            }
            (min_left / pot).max(0.0)
        };
        let order = self.postflop_order();
        let live_order: Vec<usize> = order.iter().cloned().filter(|&i| live & (1 << i) != 0).collect();
        let m = live_order.len().max(1);
        for (rank, &seat) in live_order.iter().enumerate() {
            let w = if self.cfg.realization == "raw" || spr <= 1e-9 || m < 2 {
                1.0
            } else {
                // positional skew: last to act (IP) over-realizes, first
                // under-realizes; grows with SPR, saturating at 8.
                let frac = rank as f64 / (m - 1) as f64 - 0.5; // -0.5 .. +0.5
                1.0 + 0.16 * frac * (spr.min(8.0) / 8.0)
            };
            r[seat] = w as f32;
        }
        r
    }

    fn next_actor(&self, st: &BuildState) -> Option<usize> {
        for k in 0..self.n {
            let s = (st.next_seat + k) % self.n;
            let bit = 1u32 << s;
            if st.folded & bit == 0 && st.allin & bit == 0 && st.needs & bit != 0 {
                return Some(s);
            }
        }
        None
    }

    fn build(&mut self, st: BuildState) -> Result<u32, String> {
        let live = ((1u32 << self.n) - 1) & !st.folded;
        let pot: f64 = st.invested.iter().sum();

        // fold-win terminal
        if self.live_count(live) == 1 {
            let winner = live.trailing_zeros() as u8;
            let idx = self.nodes.len() as u32;
            self.nodes.push(PNode {
                kind: KIND_FOLD_WIN,
                actor: winner,
                actions: Vec::new(),
                child_start: 0,
                pot,
                invested: st.invested.clone(),
                live,
                winner,
                r: Vec::new(),
                data_off: 0,
            });
            return Ok(idx);
        }

        // action closed -> flop / showdown terminal
        let Some(actor) = self.next_actor(&st) else {
            let idx = self.nodes.len() as u32;
            let r = self.realization_weights(live, &st.invested, pot);
            self.nodes.push(PNode {
                kind: KIND_POT_SHARE,
                actor: 0,
                actions: Vec::new(),
                child_start: 0,
                pot,
                invested: st.invested.clone(),
                live,
                winner: 0,
                r,
                data_off: 0,
            });
            return Ok(idx);
        };

        // enumerate actions (ante is dead money: only invested-minus-ante
        // counts toward matching the bet)
        let inv_live = st.invested[actor] - self.cfg.ante;
        let owed = (st.to_call - inv_live).max(0.0);
        let mut acts: Vec<PAction> = Vec::new();
        if owed > 1e-9 {
            acts.push(PAction {
                kind: "fold".into(),
                to: 0.0,
                label: "Fold".into(),
            });
            // call (limp when no raise yet)
            if st.raises > 0 || self.cfg.limp {
                let label = if st.raises == 0 { "Limp" } else { "Call" };
                acts.push(PAction {
                    kind: "call".into(),
                    to: st.to_call,
                    label: format!("{label} {}", trim(st.to_call)),
                });
            }
        } else {
            acts.push(PAction {
                kind: "check".into(),
                to: st.to_call,
                label: "Check".into(),
            });
        }
        if st.raises < self.cfg.max_raises {
            let mut tos: Vec<f64> = Vec::new();
            if st.raises == 0 {
                tos.extend(self.cfg.open_raises.iter().cloned());
            } else {
                for m in &self.cfg.raise_mults {
                    let to = (st.to_call * m).max(st.to_call + st.last_raise);
                    tos.push(to);
                }
            }
            if self.cfg.add_allin {
                tos.push(self.cfg.stack);
            }
            let mut seen: Vec<f64> = Vec::new();
            for mut to in tos {
                if to >= self.cfg.allin_threshold * self.cfg.stack {
                    to = self.cfg.stack;
                }
                if to <= st.to_call + 1e-9 {
                    continue;
                }
                if seen.iter().any(|&x| (x - to).abs() < 1e-9) {
                    continue;
                }
                seen.push(to);
                let jam = (to - self.cfg.stack).abs() < 1e-9;
                acts.push(PAction {
                    kind: if jam { "jam" } else { "raise" }.into(),
                    to,
                    label: if jam {
                        format!("All-in {}", trim(to))
                    } else if st.raises == 0 {
                        format!("Raise {}", trim(to))
                    } else {
                        format!("{}-bet {}", st.raises + 2, trim(to))
                    },
                });
            }
        }

        let idx = self.nodes.len() as u32;
        let na = acts.len();
        self.nodes.push(PNode {
            kind: KIND_ACTION,
            actor: actor as u8,
            actions: acts.clone(),
            child_start: 0,
            pot,
            invested: st.invested.clone(),
            live,
            winner: 0,
            r: Vec::new(),
            data_off: self.arena_len,
        });
        self.arena_len += na * NUM_CLASSES;
        if self.nodes.len() > 400_000 || self.arena_len > 60_000_000 {
            return Err(
                "preflop tree too large; reduce sizes/raise cap or disable limps".into(),
            );
        }

        let mut kids: Vec<u32> = Vec::with_capacity(na);
        for a in &acts {
            let mut ns = BuildState {
                invested: st.invested.clone(),
                folded: st.folded,
                allin: st.allin,
                needs: st.needs & !(1 << actor),
                to_call: st.to_call,
                last_raise: st.last_raise,
                raises: st.raises,
                next_seat: (actor + 1) % self.n,
            };
            match a.kind.as_str() {
                "fold" => {
                    ns.folded |= 1 << actor;
                }
                "check" | "call" => {
                    ns.invested[actor] = st.to_call + self.cfg.ante;
                    if (st.to_call - self.cfg.stack).abs() < 1e-9 {
                        ns.allin |= 1 << actor;
                    }
                }
                _ => {
                    ns.invested[actor] = a.to + self.cfg.ante;
                    ns.last_raise = a.to - st.to_call;
                    ns.to_call = a.to;
                    ns.raises = st.raises + 1;
                    if (a.to - self.cfg.stack).abs() < 1e-9 {
                        ns.allin |= 1 << actor;
                    }
                    // a raise re-opens action for every live player behind
                    ns.needs = (((1u32 << self.n) - 1) & !ns.folded & !ns.allin) & !(1 << actor);
                }
            }
            kids.push(self.build(ns)?);
        }
        let cs = self.children.len() as u32;
        self.children.extend(kids);
        self.nodes[idx as usize].child_start = cs;
        Ok(idx)
    }

    // ----- strategies -----

    fn current_strategy(&self, node: usize, sigma: &mut [f32]) {
        let nd = &self.nodes[node];
        let na = nd.actions.len();
        for h in 0..NUM_CLASSES {
            let mut sum = 0f32;
            for a in 0..na {
                sum += self.regrets[nd.data_off + a * NUM_CLASSES + h].max(0.0);
            }
            if sum > 1e-12 {
                for a in 0..na {
                    sigma[a * NUM_CLASSES + h] =
                        self.regrets[nd.data_off + a * NUM_CLASSES + h].max(0.0) / sum;
                }
            } else {
                let u = 1.0 / na as f32;
                for a in 0..na {
                    sigma[a * NUM_CLASSES + h] = u;
                }
            }
        }
    }

    pub fn average_strategy(&self, node: usize) -> Vec<f32> {
        let nd = &self.nodes[node];
        let na = nd.actions.len();
        let mut out = vec![0f32; na * NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            let mut sum = 0f32;
            for a in 0..na {
                sum += self.strat_sum[nd.data_off + a * NUM_CLASSES + h];
            }
            if sum > 1e-12 {
                for a in 0..na {
                    out[a * NUM_CLASSES + h] =
                        self.strat_sum[nd.data_off + a * NUM_CLASSES + h] / sum;
                }
            } else {
                let u = 1.0 / na as f32;
                for a in 0..na {
                    out[a * NUM_CLASSES + h] = u;
                }
            }
        }
        out
    }

    // ----- traversal -----

    /// Terminal chip deltas for traverser p (per class), times the product of
    /// the other players' reach mass.
    fn terminal_value(&self, node: usize, p: usize, reaches: &[Vec<f32>], out: &mut [f32]) {
        let nd = &self.nodes[node];
        let mut prob = 1f64;
        for q in 0..self.n {
            if q != p {
                let s: f32 = reaches[q].iter().sum();
                prob *= s as f64;
            }
        }
        if prob <= 0.0 {
            out.iter_mut().for_each(|v| *v = 0.0);
            return;
        }
        let inv_p = nd.invested[p];
        match nd.kind {
            KIND_FOLD_WIN => {
                let rake = if self.cfg.no_flop_no_drop {
                    0.0
                } else {
                    (nd.pot * self.cfg.rake_pct / 100.0).min(self.cfg.rake_cap)
                };
                let delta = if nd.winner as usize == p {
                    nd.pot - rake - inv_p
                } else {
                    -inv_p
                };
                out.iter_mut().for_each(|v| *v = (prob * delta) as f32);
            }
            KIND_POT_SHARE => {
                let rake = (nd.pot * self.cfg.rake_pct / 100.0).min(self.cfg.rake_cap);
                let pot_eff = nd.pot - rake;
                if nd.live & (1 << p) == 0 {
                    out.iter_mut().for_each(|v| *v = (prob * -inv_p) as f32);
                    return;
                }
                // normalized opponent class distributions
                let mut dists: Vec<Vec<f32>> = Vec::new();
                for q in 0..self.n {
                    if q != p && nd.live & (1 << q) != 0 {
                        let s: f32 = reaches[q].iter().sum();
                        if s > 0.0 {
                            dists.push(reaches[q].iter().map(|&x| x / s).collect());
                        }
                    }
                }
                let rp = nd.r[p] as f64;
                for h in 0..NUM_CLASSES {
                    let mut eqp = 1f64;
                    for d in &dists {
                        eqp *= self.eq.eq_vs_dist(h, d) as f64;
                    }
                    let share = (pot_eff * eqp * rp).min(pot_eff);
                    out[h] = (prob * (share - inv_p)) as f32;
                }
            }
            _ => unreachable!(),
        }
    }

    /// CFR traversal for traverser `p`. `mode`: 0 = update regrets/strategy
    /// (current strategies), 1 = evaluate average strategies, 2 = best
    /// response vs average strategies.
    fn traverse(&mut self, node: usize, p: usize, reaches: &mut [Vec<f32>], mode: u8) -> Vec<f32> {
        let kind = self.nodes[node].kind;
        if kind != KIND_ACTION {
            let mut out = vec![0f32; NUM_CLASSES];
            self.terminal_value(node, p, reaches, &mut out);
            return out;
        }
        let (actor, na, data_off, child_start) = {
            let nd = &self.nodes[node];
            (
                nd.actor as usize,
                nd.actions.len(),
                nd.data_off,
                nd.child_start as usize,
            )
        };
        let mut sigma = vec![0f32; na * NUM_CLASSES];
        if mode == 0 {
            self.current_strategy(node, &mut sigma);
        } else {
            sigma.copy_from_slice(&self.average_strategy(node));
        }

        if actor == p {
            // p's own reach must scale into the children so deeper strat_sum
            // updates stay reach-weighted (counterfactual values themselves
            // never include p's reach).
            let saved = reaches[p].clone();
            let mut vals = vec![0f32; na * NUM_CLASSES];
            for a in 0..na {
                for h in 0..NUM_CLASSES {
                    reaches[p][h] = saved[h] * sigma[a * NUM_CLASSES + h];
                }
                let child = self.children[child_start + a] as usize;
                let v = self.traverse(child, p, reaches, mode);
                vals[a * NUM_CLASSES..(a + 1) * NUM_CLASSES].copy_from_slice(&v);
            }
            reaches[p].copy_from_slice(&saved);
            let mut out = vec![0f32; NUM_CLASSES];
            if mode == 2 {
                for h in 0..NUM_CLASSES {
                    let mut best = f32::NEG_INFINITY;
                    for a in 0..na {
                        best = best.max(vals[a * NUM_CLASSES + h]);
                    }
                    out[h] = best;
                }
                return out;
            }
            for h in 0..NUM_CLASSES {
                let mut v = 0f32;
                for a in 0..na {
                    v += sigma[a * NUM_CLASSES + h] * vals[a * NUM_CLASSES + h];
                }
                out[h] = v;
            }
            if mode == 0 {
                for a in 0..na {
                    for h in 0..NUM_CLASSES {
                        self.regrets[data_off + a * NUM_CLASSES + h] +=
                            vals[a * NUM_CLASSES + h] - out[h];
                        self.strat_sum[data_off + a * NUM_CLASSES + h] +=
                            reaches[p][h] * sigma[a * NUM_CLASSES + h];
                    }
                }
            }
            out
        } else {
            let mut out = vec![0f32; NUM_CLASSES];
            let saved = reaches[actor].clone();
            for a in 0..na {
                for h in 0..NUM_CLASSES {
                    reaches[actor][h] = saved[h] * sigma[a * NUM_CLASSES + h];
                }
                let child = self.children[child_start + a] as usize;
                let v = self.traverse(child, p, reaches, mode);
                for h in 0..NUM_CLASSES {
                    out[h] += v[h];
                }
            }
            reaches[actor].copy_from_slice(&saved);
            out
        }
    }

    fn root_reaches(&self) -> Vec<Vec<f32>> {
        (0..self.n)
            .map(|_| (0..NUM_CLASSES).map(class_prob).collect())
            .collect()
    }

    pub fn iterate(&mut self) {
        self.iteration += 1;
        for p in 0..self.n {
            let mut reaches = self.root_reaches();
            self.traverse(0, p, &mut reaches, 0);
        }
        // DCFR discounting
        let t = self.iteration as f64;
        let pos = (t.powf(DCFR_ALPHA) / (t.powf(DCFR_ALPHA) + 1.0)) as f32;
        let neg = 0.5f32; // beta = 0
        let sd = ((t / (t + 1.0)).powf(DCFR_GAMMA)) as f32;
        for r in self.regrets.iter_mut() {
            *r *= if *r > 0.0 { pos } else { neg };
        }
        for s in self.strat_sum.iter_mut() {
            *s *= sd;
        }
    }

    /// Per-player best-response gap (bb): how much player p gains by best
    /// responding to everyone else's average strategy. -> convergence metric.
    pub fn br_gaps(&mut self) -> Vec<f64> {
        let mut gaps = Vec::with_capacity(self.n);
        for p in 0..self.n {
            let mut reaches = self.root_reaches();
            let br = self.traverse(0, p, &mut reaches, 2);
            let mut reaches = self.root_reaches();
            let avg = self.traverse(0, p, &mut reaches, 1);
            let mut g = 0f64;
            for h in 0..NUM_CLASSES {
                g += class_prob(h) as f64 * (br[h] - avg[h]) as f64;
            }
            gaps.push(g);
        }
        gaps
    }

    /// EV per player (bb) under the average strategy profile.
    pub fn evs(&mut self) -> Vec<f64> {
        (0..self.n)
            .map(|p| {
                let mut reaches = self.root_reaches();
                let v = self.traverse(0, p, &mut reaches, 1);
                (0..NUM_CLASSES)
                    .map(|h| class_prob(h) as f64 * v[h] as f64)
                    .sum()
            })
            .collect()
    }

    // ----- queries -----

    /// Child node index for action `a` of action node `node`.
    pub fn child(&self, node: usize, a: usize) -> usize {
        self.children[self.nodes[node].child_start as usize + a] as usize
    }

    /// Walk a path of action indices, tracking every player's reach under the
    /// average strategies. Returns (node, reaches).
    pub fn walk(&self, path: &[usize]) -> Result<(usize, Vec<Vec<f32>>), String> {
        let mut node = 0usize;
        let mut reaches = self.root_reaches();
        for &a in path {
            let nd = &self.nodes[node];
            if nd.kind != KIND_ACTION || a >= nd.actions.len() {
                return Err("bad path".into());
            }
            let sigma = self.average_strategy(node);
            let actor = nd.actor as usize;
            for h in 0..NUM_CLASSES {
                reaches[actor][h] *= sigma[a * NUM_CLASSES + h];
            }
            node = self.children[nd.child_start as usize + a] as usize;
        }
        Ok((node, reaches))
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct PActionFreq {
    pub label: String,
    pub kind: String,
    pub to: f64,
    /// Combo-weighted aggregate frequency over the actor's reaching range.
    pub freq: f32,
}

#[derive(Debug, Clone, Serialize)]
pub struct PreflopNodeView {
    /// "action" | "fold_win" | "pot_share"
    pub kind: String,
    pub actor: Option<usize>,
    pub actor_pos: Option<String>,
    pub positions: Vec<String>,
    pub pot: f64,
    pub invested: Vec<f64>,
    pub live: Vec<bool>,
    pub actions: Vec<PActionFreq>,
    /// Action nodes: the actor's average strategy, na x 169 flattened.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub strategy: Option<Vec<f32>>,
    /// Fraction of each class's combos still in the actor's range (0..1).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reach: Option<Vec<f32>>,
    /// pot_share with exactly two live players: exportable to the postflop solver.
    pub exportable: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub spr: Option<f64>,
}

#[derive(Debug, Clone, Serialize)]
pub struct PreflopExport {
    pub oop_pos: String,
    pub ip_pos: String,
    pub range_oop: String,
    pub range_ip: String,
    pub pot_bb: f64,
    pub eff_stack_bb: f64,
}

impl PreflopSolver {
    pub fn node_view(&self, path: &[usize]) -> Result<PreflopNodeView, String> {
        let (node, reaches) = self.walk(path)?;
        let nd = &self.nodes[node];
        let live: Vec<bool> = (0..self.n).map(|i| nd.live & (1 << i) != 0).collect();
        let kind = match nd.kind {
            KIND_ACTION => "action",
            KIND_FOLD_WIN => "fold_win",
            _ => "pot_share",
        }
        .to_string();
        let (actions, strategy, reach, actor, actor_pos) = if nd.kind == KIND_ACTION {
            let actor = nd.actor as usize;
            let sigma = self.average_strategy(node);
            let na = nd.actions.len();
            let mut tot = 0f64;
            let mut freqs = vec![0f64; na];
            for h in 0..NUM_CLASSES {
                let w = reaches[actor][h] as f64;
                tot += w;
                for a in 0..na {
                    freqs[a] += w * sigma[a * NUM_CLASSES + h] as f64;
                }
            }
            let actions = nd
                .actions
                .iter()
                .enumerate()
                .map(|(a, act)| PActionFreq {
                    label: act.label.clone(),
                    kind: act.kind.clone(),
                    to: act.to,
                    freq: if tot > 1e-12 {
                        (freqs[a] / tot) as f32
                    } else {
                        0.0
                    },
                })
                .collect();
            let reach: Vec<f32> = (0..NUM_CLASSES)
                .map(|h| (reaches[actor][h] / class_prob(h)).min(1.0))
                .collect();
            (
                actions,
                Some(sigma),
                Some(reach),
                Some(actor),
                Some(self.cfg.positions[actor].clone()),
            )
        } else {
            (Vec::new(), None, None, None, None)
        };
        let exportable = nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 2;
        let spr = if nd.kind == KIND_POT_SHARE {
            let mut min_left = f64::MAX;
            for i in 0..self.n {
                if nd.live & (1 << i) != 0 {
                    min_left = min_left.min(self.cfg.stack - nd.invested[i] + self.cfg.ante);
                }
            }
            Some((min_left / nd.pot).max(0.0))
        } else {
            None
        };
        Ok(PreflopNodeView {
            kind,
            actor,
            actor_pos,
            positions: self.cfg.positions.clone(),
            pot: nd.pot,
            invested: nd.invested.clone(),
            live,
            actions,
            strategy,
            reach,
            exportable,
            spr,
        })
    }

    /// Conditional ranges + pot/stack for a heads-up flop terminal, in the
    /// postflop solver's spot format.
    pub fn export_spot(&self, path: &[usize]) -> Result<PreflopExport, String> {
        let (node, reaches) = self.walk(path)?;
        let nd = &self.nodes[node];
        if nd.kind != KIND_POT_SHARE || nd.live.count_ones() != 2 {
            return Err("export needs a flop node with exactly two live players".into());
        }
        let order = self.postflop_order();
        let live_seats: Vec<usize> =
            order.into_iter().filter(|&i| nd.live & (1 << i) != 0).collect();
        let (oop, ip) = (live_seats[0], live_seats[1]);
        let range_of = |seat: usize| -> String {
            let mut parts: Vec<String> = Vec::new();
            for h in 0..NUM_CLASSES {
                let w = (reaches[seat][h] / class_prob(h)).min(1.0);
                if w > 0.995 {
                    parts.push(equity::class_label(h));
                } else if w > 0.005 {
                    parts.push(format!("{}:{:.3}", equity::class_label(h), w));
                }
            }
            parts.join(",")
        };
        Ok(PreflopExport {
            oop_pos: self.cfg.positions[oop].clone(),
            ip_pos: self.cfg.positions[ip].clone(),
            range_oop: range_of(oop),
            range_ip: range_of(ip),
            pot_bb: nd.pot,
            eff_stack_bb: self.cfg.stack - nd.invested[oop] + self.cfg.ante,
        })
    }

    /// Estimated arena memory in MB (regrets + strategy sums).
    pub fn arena_mb(&self) -> f64 {
        (self.arena_len * 2 * 4) as f64 / 1e6
    }
}

fn trim(x: f64) -> String {
    if (x - x.round()).abs() < 1e-9 {
        format!("{}", x.round() as i64)
    } else {
        format!("{:.1}", x)
    }
}
