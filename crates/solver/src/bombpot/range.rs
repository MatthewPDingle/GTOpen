//! Two-player play with every hand at once.
//!
//! Walks the betting tree carrying, for each seat, how likely each of the
//! 1326 hands is to have come this far, and returns what each hand of each
//! seat earns against the other seat's whole range. Cards to come are either
//! all tried (exact scoring) or a few are drawn (self-play for a net).
//!
//! The strategies come from a `Policy`: the solver's tables, a net, or
//! anything else that can say how every hand plays a node. A `Recorder`, if
//! given, sees every decision with the value of each action, which is what
//! net training needs. Two players only: with more, the value of a hand
//! depends on every combination of the other seats' hands.

use rayon::prelude::*;

use super::abstraction::{strengths, Abstraction, Rng, Runout};
use super::solver::BpSolver;
use super::tree::*;
use crate::cards::{combo_from_index, Card, NUM_COMBOS};

/// How every hand plays one decision.
pub trait Policy: Sync {
    /// Fill `out[action * 1326 + hand]` with the actor's probabilities at
    /// `node_idx`. Hands that use a card in `used` are never read.
    fn strategies(&self, node_idx: u32, runout: &Runout, used: u64, out: &mut [f32]);
}

/// The average strategy held in a solver's tables.
pub struct TablePolicy<'a>(pub &'a BpSolver);

impl Policy for TablePolicy<'_> {
    fn strategies(&self, node_idx: u32, runout: &Runout, used: u64, out: &mut [f32]) {
        let s = self.0;
        let node = &s.tree.nodes[node_idx as usize];
        let na = node.num_children as usize;
        let street = node.street as usize;
        let mut row = [0.0f32; MAX_ACTIONS];
        for h in 0..NUM_COMBOS {
            let (c1, c2) = combo_from_index(h);
            if (1u64 << c1 | 1u64 << c2) & used != 0 {
                continue;
            }
            s.average(node, s.abs.bucket(street, h, runout), &mut row);
            for a in 0..na {
                out[a * NUM_COMBOS + h] = row[a];
            }
        }
    }
}

/// Every action equally often: what self-play starts from.
pub struct UniformPolicy<'a>(pub &'a BpTree);

impl Policy for UniformPolicy<'_> {
    fn strategies(&self, node_idx: u32, _runout: &Runout, _used: u64, out: &mut [f32]) {
        let na = self.0.nodes[node_idx as usize].num_children as usize;
        out[..na * NUM_COMBOS].fill(1.0 / na as f32);
    }
}

/// Which of the cards to come are tried at each new street.
#[derive(Clone, Copy)]
pub enum Chance {
    /// Every card: exact.
    All,
    /// This many random draws for the turn and for the river.
    Sample { turn: usize, river: usize },
}

/// One decision as a `Recorder` sees it. Vectors are indexed by hand.
pub struct NodeView<'a> {
    pub node_idx: u32,
    pub runout: &'a Runout,
    /// Every card on the boards so far.
    pub used: u64,
    pub actor: usize,
    /// `[action * 1326 + hand]`.
    pub sigma: &'a [f32],
    /// How likely the actor is to be here with each hand.
    pub own_reach: &'a [f32],
    /// For each hand, the summed likelihood of opposing hands that share no
    /// card with it.
    pub opp_mass: &'a [f32],
    /// The actor's value of each action, summed over the opposing range.
    pub action_vals: &'a [Vec<f32>],
    /// The same for the mix the actor plays.
    pub node_val: &'a [f32],
}

pub trait Recorder {
    fn node(&mut self, view: &NodeView);
}

/// Per seat and hand: the value summed over the other seat's range.
pub struct Vals {
    /// Both seats playing their strategies.
    pub avg: [Vec<f32>; 2],
    /// The seat playing a perfect reply (empty unless asked for).
    pub best: [Vec<f32>; 2],
}

/// Hands in rising order of strength on each board, for one full runout.
struct RiverCtx {
    strength: Vec<Vec<u32>>,
    order: Vec<Vec<u16>>,
}

pub struct Walker<'a> {
    pub tree: &'a BpTree,
    pub abs: &'a Abstraction,
    c1: [Card; NUM_COMBOS],
    c2: [Card; NUM_COMBOS],
}

struct Cx<'a> {
    policy: &'a dyn Policy,
    chance: Chance,
    want_best: bool,
}

fn all_zero(v: &[f32]) -> bool {
    v.iter().all(|&x| x == 0.0)
}

impl<'a> Walker<'a> {
    pub fn new(tree: &'a BpTree, abs: &'a Abstraction) -> Result<Walker<'a>, String> {
        if tree.players() != 2 {
            return Err("whole-range play needs exactly two players".into());
        }
        let mut w = Walker { tree, abs, c1: [0; NUM_COMBOS], c2: [0; NUM_COMBOS] };
        for h in 0..NUM_COMBOS {
            let (a, b) = combo_from_index(h);
            w.c1[h] = a;
            w.c2[h] = b;
        }
        Ok(w)
    }

    #[inline]
    fn hits(&self, h: usize, mask: u64) -> bool {
        (1u64 << self.c1[h] | 1u64 << self.c2[h]) & mask != 0
    }

    /// Every hand that fits the starting boards, with weight 1.
    pub fn root_reach(&self) -> Vec<f32> {
        (0..NUM_COMBOS).map(|h| if self.hits(h, self.abs.dead) { 0.0 } else { 1.0 }).collect()
    }

    /// Number of (hand, hand) pairs at the root that do not share a card.
    pub fn root_pairs(&self) -> f64 {
        let reach = self.root_reach();
        let compat = self.compatible(&reach);
        (0..NUM_COMBOS).map(|h| reach[h] as f64 * compat[h] as f64).sum()
    }

    /// Walk the game from the root. `rec` sees every decision; `rng` is used
    /// only when cards are sampled.
    pub fn run(
        &self,
        policy: &dyn Policy,
        chance: Chance,
        want_best: bool,
        mut rec: Option<&mut dyn Recorder>,
        rng: &mut Rng,
    ) -> Vals {
        let cx = Cx { policy, chance, want_best };
        let root = self.abs.root_street as usize;
        let reach = [self.root_reach(), self.root_reach()];
        let runout: Runout = [[0; 2]; 2];
        let ctx = if root == 2 { Some(self.river_ctx(&runout)) } else { None };
        self.eval(&cx, &mut rec, rng, 0, root, &reach, &runout, self.abs.dead, ctx.as_ref())
    }

    /// For each hand, the summed reach of opposing hands that share no card with it.
    pub fn compatible(&self, reach: &[f32]) -> Vec<f32> {
        let mut total = 0.0f64;
        let mut by_card = [0.0f64; 52];
        for h in 0..NUM_COMBOS {
            let r = reach[h] as f64;
            if r != 0.0 {
                total += r;
                by_card[self.c1[h] as usize] += r;
                by_card[self.c2[h] as usize] += r;
            }
        }
        (0..NUM_COMBOS)
            .map(|h| (total - by_card[self.c1[h] as usize] - by_card[self.c2[h] as usize] + reach[h] as f64) as f32)
            .collect()
    }

    fn river_ctx(&self, runout: &Runout) -> RiverCtx {
        let nb = self.abs.num_boards();
        let fulls: Vec<[Card; 5]> = (0..nb).map(|b| self.abs.full_board(b, runout)).collect();
        let used = fulls.iter().flatten().fold(0u64, |m, &c| m | 1u64 << c);
        let mut strength = Vec::new();
        let mut order = Vec::new();
        for full in &fulls {
            let st = strengths(full, used);
            let mut o: Vec<u16> = (0..NUM_COMBOS as u16).filter(|&h| st[h as usize] != 0).collect();
            o.sort_unstable_by_key(|&h| st[h as usize]);
            strength.push(st);
            order.push(o);
        }
        RiverCtx { strength, order }
    }

    #[allow(clippy::too_many_arguments)]
    fn eval(
        &self,
        cx: &Cx,
        rec: &mut Option<&mut dyn Recorder>,
        rng: &mut Rng,
        node_idx: u32,
        have: usize,
        reach: &[Vec<f32>; 2],
        runout: &Runout,
        used: u64,
        ctx: Option<&RiverCtx>,
    ) -> Vals {
        let node = &self.tree.nodes[node_idx as usize];
        let zeros = || vec![0.0f32; NUM_COMBOS];
        if all_zero(&reach[0]) && all_zero(&reach[1]) {
            let best = if cx.want_best { [zeros(), zeros()] } else { [Vec::new(), Vec::new()] };
            return Vals { avg: [zeros(), zeros()], best };
        }
        if node.kind == KIND_FOLD {
            let mut avg = [Vec::new(), Vec::new()];
            for p in 0..2 {
                let put = self.tree.put(node_idx, p);
                let gain = if node.live >> p & 1 != 0 { node.pot_net - put } else { -put };
                let mut v = self.compatible(&reach[1 - p]);
                v.iter_mut().for_each(|x| *x *= gain);
                avg[p] = v;
            }
            let best = if cx.want_best { avg.clone() } else { [Vec::new(), Vec::new()] };
            return Vals { avg, best };
        }
        let need = if node.kind == KIND_SHOWDOWN { 2 } else { node.street as usize };
        if have < need {
            return self.deal_street(cx, rec, rng, node_idx, have, reach, runout, used);
        }
        if node.kind == KIND_SHOWDOWN {
            let ctx = ctx.expect("river context");
            let avg = [
                self.showdown(node_idx, node, 0, &reach[1], ctx),
                self.showdown(node_idx, node, 1, &reach[0], ctx),
            ];
            let best = if cx.want_best { avg.clone() } else { [Vec::new(), Vec::new()] };
            return Vals { avg, best };
        }
        let actor = node.player as usize;
        let other = 1 - actor;
        let na = node.num_children as usize;
        let mut sigma = vec![0.0f32; na * NUM_COMBOS];
        cx.policy.strategies(node_idx, runout, used, &mut sigma);
        let mut avg_actor = zeros();
        let mut avg_other = zeros();
        let mut best_actor = if cx.want_best { vec![f32::NEG_INFINITY; NUM_COMBOS] } else { Vec::new() };
        let mut best_other = if cx.want_best { zeros() } else { Vec::new() };
        let recording = rec.is_some();
        let mut action_vals: Vec<Vec<f32>> = Vec::new();
        let mut child_reach = [Vec::new(), Vec::new()];
        child_reach[other] = reach[other].clone();
        for a in 0..na {
            let sa = &sigma[a * NUM_COMBOS..(a + 1) * NUM_COMBOS];
            let r: Vec<f32> = (0..NUM_COMBOS).map(|h| reach[actor][h] * sa[h]).collect();
            if !cx.want_best && !recording && all_zero(&r) {
                // Never played: adds nothing to either seat's value.
                continue;
            }
            child_reach[actor] = r;
            let v = self.eval(cx, rec, rng, self.tree.child(node, a), have, &child_reach, runout, used, ctx);
            for h in 0..NUM_COMBOS {
                avg_actor[h] += sa[h] * v.avg[actor][h];
                avg_other[h] += v.avg[other][h];
            }
            if cx.want_best {
                for h in 0..NUM_COMBOS {
                    if v.best[actor][h] > best_actor[h] {
                        best_actor[h] = v.best[actor][h];
                    }
                    best_other[h] += v.best[other][h];
                }
            }
            if recording {
                let mut v = v;
                action_vals.push(std::mem::take(&mut v.avg[actor]));
            }
        }
        if let Some(r) = rec.as_deref_mut() {
            let opp_mass = self.compatible(&reach[other]);
            r.node(&NodeView {
                node_idx,
                runout,
                used,
                actor,
                sigma: &sigma,
                own_reach: &reach[actor],
                opp_mass: &opp_mass,
                action_vals: &action_vals,
                node_val: &avg_actor,
            });
        }
        let mut out = Vals { avg: [Vec::new(), Vec::new()], best: [Vec::new(), Vec::new()] };
        out.avg[actor] = avg_actor;
        out.avg[other] = avg_other;
        out.best[actor] = best_actor;
        out.best[other] = best_other;
        out
    }

    /// Deal the next street on every board and average over the cards.
    #[allow(clippy::too_many_arguments)]
    fn deal_street(
        &self,
        cx: &Cx,
        rec: &mut Option<&mut dyn Recorder>,
        rng: &mut Rng,
        node_idx: u32,
        have: usize,
        reach: &[Vec<f32>; 2],
        runout: &Runout,
        used: u64,
    ) -> Vals {
        let nb = self.abs.num_boards();
        let next = have + 1;
        let free: Vec<Card> = (0..52u8).filter(|&c| used >> c & 1 == 0).collect();
        // Cards left once both hands are out of the deck.
        let left = free.len() as f64 - 4.0;
        let prob = if nb == 1 { 1.0 / left } else { 1.0 / (left * (left - 1.0)) };
        let total = if nb == 1 { free.len() } else { free.len() * (free.len() - 1) };
        let want = match cx.chance {
            Chance::All => total,
            Chance::Sample { turn, river } => (if next == 1 { turn } else { river }).max(1),
        };
        let mut draws: Vec<[Card; 2]> = Vec::new();
        if want >= total {
            if nb == 1 {
                draws.extend(free.iter().map(|&c| [c, 0]));
            } else {
                for &a in &free {
                    for &b in &free {
                        if a != b {
                            draws.push([a, b]);
                        }
                    }
                }
            }
        } else if nb == 1 {
            let mut deck = free.clone();
            for i in 0..want {
                let j = i + rng.below((deck.len() - i) as u32) as usize;
                deck.swap(i, j);
                draws.push([deck[i], 0]);
            }
        } else {
            for _ in 0..want {
                let a = rng.below(free.len() as u32) as usize;
                let mut b = rng.below(free.len() as u32 - 1) as usize;
                if b >= a {
                    b += 1;
                }
                draws.push([free[a], free[b]]);
            }
        }
        let scale = (prob * total as f64 / draws.len() as f64) as f32;
        let one = |draw: &[Card; 2], rec: &mut Option<&mut dyn Recorder>, rng: &mut Rng| -> Vals {
            let mut ro = *runout;
            let mut mask = 0u64;
            for b in 0..nb {
                ro[b][next - 1] = draw[b];
                mask |= 1u64 << draw[b];
            }
            let mut r = [reach[0].clone(), reach[1].clone()];
            for h in 0..NUM_COMBOS {
                if self.hits(h, mask) {
                    r[0][h] = 0.0;
                    r[1][h] = 0.0;
                }
            }
            let ctx = if next == 2 { Some(self.river_ctx(&ro)) } else { None };
            let mut v = self.eval(cx, rec, rng, node_idx, next, &r, &ro, used | mask, ctx.as_ref());
            for h in 0..NUM_COMBOS {
                if self.hits(h, mask) {
                    for p in 0..2 {
                        v.avg[p][h] = 0.0;
                        if cx.want_best {
                            v.best[p][h] = 0.0;
                        }
                    }
                }
            }
            v
        };
        let empty = || Vals {
            avg: [vec![0.0f32; NUM_COMBOS], vec![0.0f32; NUM_COMBOS]],
            best: if cx.want_best {
                [vec![0.0f32; NUM_COMBOS], vec![0.0f32; NUM_COMBOS]]
            } else {
                [Vec::new(), Vec::new()]
            },
        };
        let add = |mut acc: Vals, v: Vals| {
            for p in 0..2 {
                for h in 0..NUM_COMBOS {
                    acc.avg[p][h] += v.avg[p][h];
                }
                if !acc.best[p].is_empty() {
                    for h in 0..NUM_COMBOS {
                        acc.best[p][h] += v.best[p][h];
                    }
                }
            }
            acc
        };
        // The first cards dealt fan out over the threads, unless a recorder
        // is listening (it takes the decisions in order).
        let mut sum = if have == self.abs.root_street as usize && rec.is_none() {
            let seeds: Vec<u64> = draws.iter().map(|_| rng.next_u64()).collect();
            draws
                .par_iter()
                .zip(seeds.par_iter())
                .map(|(d, &seed)| one(d, &mut None, &mut Rng::new(seed)))
                .reduce(empty, add)
        } else {
            let mut acc = empty();
            for d in &draws {
                acc = add(acc, one(d, rec, rng));
            }
            acc
        };
        for p in 0..2 {
            sum.avg[p].iter_mut().for_each(|x| *x *= scale);
            sum.best[p].iter_mut().for_each(|x| *x *= scale);
        }
        sum
    }

    fn showdown(&self, node_idx: u32, node: &BpNode, p: usize, reach: &[f32], ctx: &RiverCtx) -> Vec<f32> {
        let nb = self.abs.num_boards();
        let put = self.tree.put(node_idx, p);
        let win = node.pot_net / nb as f32;
        let compat = self.compatible(reach);
        let mut out: Vec<f32> = compat.iter().map(|&c| -put * c).collect();
        let (c1, c2) = (&self.c1, &self.c2);
        for b in 0..nb {
            let order = &ctx.order[b];
            let st = &ctx.strength[b];
            let mut below = 0.0f64;
            let mut below_card = [0.0f64; 52];
            let mut i = 0;
            while i < order.len() {
                let mut j = i;
                let mut tie = 0.0f64;
                let mut tie_card = [0.0f64; 52];
                while j < order.len() && st[order[j] as usize] == st[order[i] as usize] {
                    let h = order[j] as usize;
                    let r = reach[h] as f64;
                    tie += r;
                    tie_card[c1[h] as usize] += r;
                    tie_card[c2[h] as usize] += r;
                    j += 1;
                }
                for &h in &order[i..j] {
                    let h = h as usize;
                    let (a, c) = (c1[h] as usize, c2[h] as usize);
                    let weaker = below - below_card[a] - below_card[c];
                    let tied = tie - tie_card[a] - tie_card[c] + reach[h] as f64;
                    out[h] += win * (weaker + 0.5 * tied) as f32;
                }
                below += tie;
                for c in 0..52 {
                    below_card[c] += tie_card[c];
                }
                i = j;
            }
        }
        out
    }
}
