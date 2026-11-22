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

/// Inputs per hand that describe how it stands against the ranges at a
/// decision: per board, the share of the other seat's range it beats and
/// its place in its own seat's range; then the share of the other seat's
/// range still here, and how often the hand itself gets here.
pub const RANGE: usize = 6;

/// One decision as a `Policy` sees it.
pub struct At<'a> {
    pub node_idx: u32,
    pub runout: &'a Runout,
    /// Every card on the boards so far.
    pub used: u64,
    /// `[hand * RANGE ..]`, when the policy asked for it and the game was
    /// built with hand-strength inputs.
    pub range: Option<&'a [f32]>,
}

/// How every hand plays one decision.
pub trait Policy: Sync {
    /// Fill `out[action * 1326 + hand]` with the actor's probabilities.
    /// Hands that use a card in `at.used` are never read.
    fn strategies(&self, at: &At, out: &mut [f32]);
    /// Whether `strategies` reads `at.range`.
    fn wants_range(&self) -> bool {
        false
    }
}

/// The average strategy held in a solver's tables.
pub struct TablePolicy<'a>(pub &'a BpSolver);

impl Policy for TablePolicy<'_> {
    fn strategies(&self, at: &At, out: &mut [f32]) {
        let s = self.0;
        let (runout, used) = (at.runout, at.used);
        let node = &s.tree.nodes[at.node_idx as usize];
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
    fn strategies(&self, at: &At, out: &mut [f32]) {
        let na = self.0.nodes[at.node_idx as usize].num_children as usize;
        out[..na * NUM_COMBOS].fill(1.0 / na as f32);
    }
}

/// Which of the cards to come are tried at each new street.
#[derive(Clone, Copy)]
pub enum Chance {
    /// Every card: exact.
    All,
    /// This many random draws for the turn and for the river. Every betting
    /// line of a walk gets the same cards (a walk plays a few whole boards).
    Sample { turn: usize, river: usize },
    /// As `Sample`, but the walks of one run share a shuffled deck at every
    /// spot and each takes the next cards from it, so together they cover
    /// the cards evenly instead of by luck. One board only (with two, the
    /// same as `Sample`).
    Spread { turn: usize, river: usize, walk: usize, deck: u64 },
    /// The draws of `Sample` with the first number of each pair, of which
    /// only the second number are tried, picked by `pick`: a noisy look at
    /// the game that `Sample` plays in full.
    Subset { turn: [usize; 2], river: [usize; 2], pick: u64 },
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
    /// The range inputs (see `At::range`), when a policy asked for them.
    pub range: Option<&'a [f32]>,
}

pub trait Recorder {
    fn node(&mut self, view: &NodeView);
}

/// Per seat and hand: the value summed over the other seat's range.
pub struct Vals {
    /// Both seats playing their strategies.
    pub avg: [Vec<f32>; 2],
    /// The seat playing a perfect reply (empty unless asked for): from the
    /// first street on, from the turn on only, and on the river only. Before
    /// the street a reply starts on, the seat plays its own strategy.
    pub best: [[Vec<f32>; 2]; 3],
}

fn no_best() -> [[Vec<f32>; 2]; 3] {
    Default::default()
}

fn best_like(avg: &[Vec<f32>; 2], want: bool) -> [[Vec<f32>; 2]; 3] {
    if want {
        [avg.clone(), avg.clone(), avg.clone()]
    } else {
        no_best()
    }
}

/// Hands in rising order of strength on each board, for the cards dealt so
/// far: showdown strength on the river, average strength over the cards to
/// come before it. A key of 0 marks a hand that cannot be held.
struct StreetCtx {
    key: Vec<Vec<u32>>,
    order: Vec<Vec<u16>>,
}

pub struct Walker<'a> {
    pub tree: &'a BpTree,
    pub abs: &'a Abstraction,
    c1: [Card; NUM_COMBOS],
    c2: [Card; NUM_COMBOS],
    /// Opposing hands a hand can face at the root.
    pub root_norm: f32,
}

struct Cx<'a> {
    policy: &'a dyn Policy,
    chance: Chance,
    want_best: bool,
    want_range: bool,
    /// The strategy whose ranges the range inputs describe, when it is not
    /// the one being played.
    context: Option<&'a dyn Policy>,
    /// Sampled cards depend on this, the spot and the cards so far only, so
    /// two walks with one seed see the same cards whatever is played.
    seed: u64,
}

fn all_zero(v: &[f32]) -> bool {
    v.iter().all(|&x| x == 0.0)
}

impl<'a> Walker<'a> {
    pub fn new(tree: &'a BpTree, abs: &'a Abstraction) -> Result<Walker<'a>, String> {
        if tree.players() != 2 {
            return Err("whole-range play needs exactly two players".into());
        }
        let free = 52.0 - abs.dead.count_ones() as f32;
        let mut w =
            Walker { tree, abs, c1: [0; NUM_COMBOS], c2: [0; NUM_COMBOS], root_norm: (free - 2.0) * (free - 3.0) / 2.0 };
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
    /// only when cards are sampled. With a `context`, the range inputs
    /// describe the ranges that strategy would arrive with, not the played
    /// one's: self-play hands it the slow-moving average strategy, so a
    /// spot's inputs do not jump about from one round to the next.
    pub fn run(
        &self,
        policy: &dyn Policy,
        context: Option<&dyn Policy>,
        chance: Chance,
        want_best: bool,
        mut rec: Option<&mut dyn Recorder>,
        rng: &mut Rng,
    ) -> Vals {
        let want_range = policy.wants_range() || context.is_some_and(|c| c.wants_range());
        let cx = Cx { policy, chance, want_best, want_range, context, seed: rng.next_u64() };
        let root = self.abs.root_street as usize;
        let reach = [self.root_reach(), self.root_reach()];
        let runout: Runout = [[0; 2]; 2];
        let ctx = self.street_ctx(root, &runout, self.abs.dead);
        let fr = context.map(|_| reach.clone());
        self.eval(&cx, &mut rec, rng, 0, root, &reach, fr.as_ref(), &runout, self.abs.dead, ctx.as_ref())
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

    /// The strength order of the hands on a street. Before the river it
    /// needs the game's hand-strength inputs (`None` without them).
    fn street_ctx(&self, street: usize, runout: &Runout, used: u64) -> Option<StreetCtx> {
        let nb = self.abs.num_boards();
        let mut key = Vec::new();
        if street == 2 {
            let fulls: Vec<[Card; 5]> = (0..nb).map(|b| self.abs.full_board(b, runout)).collect();
            let all = fulls.iter().flatten().fold(0u64, |m, &c| m | 1u64 << c);
            for full in &fulls {
                key.push(strengths(full, all));
            }
        } else {
            let f = self.abs.feats.as_ref()?;
            for b in 0..nb {
                let avg = |h: usize| {
                    if street == 0 {
                        f.flop[b][h * 2]
                    } else {
                        f.turn[b][(runout[b][0] as usize * NUM_COMBOS + h) * 2]
                    }
                };
                key.push(
                    (0..NUM_COMBOS).map(|h| if self.hits(h, used) { 0 } else { (avg(h) * 1e6) as u32 + 1 }).collect(),
                );
            }
        }
        let order = key
            .iter()
            .map(|k| {
                let mut o: Vec<u16> = (0..NUM_COMBOS as u16).filter(|&h| k[h as usize] != 0).collect();
                o.sort_unstable_by_key(|&h| k[h as usize]);
                o
            })
            .collect();
        Some(StreetCtx { key, order })
    }

    /// For each hand, the summed reach of the hands in `reach` that it beats
    /// in this order, plus half of those it ties, counting only hands that
    /// share no card with it.
    fn beaten(&self, key: &[u32], order: &[u16], reach: &[f32]) -> Vec<f32> {
        let (c1, c2) = (&self.c1, &self.c2);
        let mut out = vec![0.0f32; NUM_COMBOS];
        let mut below = 0.0f64;
        let mut below_card = [0.0f64; 52];
        let mut i = 0;
        while i < order.len() {
            let mut j = i;
            let mut tie = 0.0f64;
            let mut tie_card = [0.0f64; 52];
            while j < order.len() && key[order[j] as usize] == key[order[i] as usize] {
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
                out[h] = (weaker + 0.5 * tied) as f32;
            }
            below += tie;
            for c in 0..52 {
                below_card[c] += tie_card[c];
            }
            i = j;
        }
        out
    }

    /// The range inputs of every hand of the seat to act.
    fn range_feats(&self, ctx: &StreetCtx, own: &[f32], opp: &[f32]) -> Vec<f32> {
        let mut out = vec![0.0f32; NUM_COMBOS * RANGE];
        let opp_mass = self.compatible(opp);
        let own_mass = self.compatible(own);
        for b in 0..ctx.key.len() {
            let vs_opp = self.beaten(&ctx.key[b], &ctx.order[b], opp);
            let in_own = self.beaten(&ctx.key[b], &ctx.order[b], own);
            for &h in &ctx.order[b] {
                let h = h as usize;
                out[h * RANGE + b * 2] = if opp_mass[h] > 1e-9 { vs_opp[h] / opp_mass[h] } else { 0.5 };
                out[h * RANGE + b * 2 + 1] = if own_mass[h] > 1e-9 { in_own[h] / own_mass[h] } else { 0.5 };
            }
        }
        for h in 0..NUM_COMBOS {
            out[h * RANGE + 4] = opp_mass[h] / self.root_norm;
            out[h * RANGE + 5] = own[h];
        }
        out
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
        fr: Option<&[Vec<f32>; 2]>,
        runout: &Runout,
        used: u64,
        ctx: Option<&StreetCtx>,
    ) -> Vals {
        let node = &self.tree.nodes[node_idx as usize];
        let zeros = || vec![0.0f32; NUM_COMBOS];
        if all_zero(&reach[0]) && all_zero(&reach[1]) {
            let avg = [zeros(), zeros()];
            let best = best_like(&avg, cx.want_best);
            return Vals { avg, best };
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
            let best = best_like(&avg, cx.want_best);
            return Vals { avg, best };
        }
        let need = if node.kind == KIND_SHOWDOWN { 2 } else { node.street as usize };
        if have < need {
            return self.deal_street(cx, rec, rng, node_idx, have, reach, fr, runout, used);
        }
        if node.kind == KIND_SHOWDOWN {
            let ctx = ctx.expect("river context");
            let avg = [
                self.showdown(node_idx, node, 0, &reach[1], ctx),
                self.showdown(node_idx, node, 1, &reach[0], ctx),
            ];
            let best = best_like(&avg, cx.want_best);
            return Vals { avg, best };
        }
        let actor = node.player as usize;
        let other = 1 - actor;
        let na = node.num_children as usize;
        let mut sigma = vec![0.0f32; na * NUM_COMBOS];
        let seen = fr.unwrap_or(reach);
        let range = match ctx {
            Some(c) if cx.want_range => Some(self.range_feats(c, &seen[actor], &seen[other])),
            _ => None,
        };
        let at = At { node_idx, runout, used, range: range.as_deref() };
        cx.policy.strategies(&at, &mut sigma);
        // The context strategy's own play here moves its ranges on.
        let mut context_sigma = Vec::new();
        let mut child_fr: Option<[Vec<f32>; 2]> = None;
        if let (Some(f), Some(c)) = (fr, cx.context) {
            context_sigma = vec![0.0f32; na * NUM_COMBOS];
            c.strategies(&at, &mut context_sigma);
            let mut pair = [Vec::new(), Vec::new()];
            pair[other] = f[other].clone();
            child_fr = Some(pair);
        }
        let mut avg_actor = zeros();
        let mut avg_other = zeros();
        // A reply that starts on a later street plays the mix here.
        let street = node.street as usize;
        let mut best = no_best();
        if cx.want_best {
            for (k, b) in best.iter_mut().enumerate() {
                b[actor] = if street >= k { vec![f32::NEG_INFINITY; NUM_COMBOS] } else { zeros() };
                b[other] = zeros();
            }
        }
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
            if let (Some(pair), Some(f)) = (child_fr.as_mut(), fr) {
                let ca = &context_sigma[a * NUM_COMBOS..(a + 1) * NUM_COMBOS];
                pair[actor] = (0..NUM_COMBOS).map(|h| f[actor][h] * ca[h]).collect();
            }
            let child = self.tree.child(node, a);
            let v = self.eval(cx, rec, rng, child, have, &child_reach, child_fr.as_ref(), runout, used, ctx);
            for h in 0..NUM_COMBOS {
                avg_actor[h] += sa[h] * v.avg[actor][h];
                avg_other[h] += v.avg[other][h];
            }
            if cx.want_best {
                for (k, b) in best.iter_mut().enumerate() {
                    for h in 0..NUM_COMBOS {
                        if street >= k {
                            if v.best[k][actor][h] > b[actor][h] {
                                b[actor][h] = v.best[k][actor][h];
                            }
                        } else {
                            b[actor][h] += sa[h] * v.best[k][actor][h];
                        }
                        b[other][h] += v.best[k][other][h];
                    }
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
                range: range.as_deref(),
            });
        }
        let mut out = Vals { avg: [Vec::new(), Vec::new()], best };
        out.avg[actor] = avg_actor;
        out.avg[other] = avg_other;
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
        fr: Option<&[Vec<f32>; 2]>,
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
            Chance::Spread { turn, river, .. } => (if next == 1 { turn } else { river }).max(1),
            Chance::Subset { turn, river, .. } => (if next == 1 { turn[0] } else { river[0] }).max(1),
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
            let spot = (have as u64) << 60
                | runout.iter().flatten().enumerate().fold(0u64, |m, (i, &c)| m | (c as u64) << (i * 8));
            let mut deck = free.clone();
            if let Chance::Spread { walk, deck: shared, .. } = cx.chance {
                let rng = &mut Rng::new(shared ^ spot.wrapping_mul(0x9E37_79B9_7F4A_7C15));
                for i in 0..deck.len() - 1 {
                    let j = i + rng.below((deck.len() - i) as u32) as usize;
                    deck.swap(i, j);
                }
                let start = walk * want % deck.len();
                draws.extend((0..want).map(|j| [deck[(start + j) % deck.len()], 0]));
            } else {
                let rng = &mut Rng::new(cx.seed ^ spot.wrapping_mul(0x9E37_79B9_7F4A_7C15));
                for i in 0..want {
                    let j = i + rng.below((deck.len() - i) as u32) as usize;
                    deck.swap(i, j);
                    draws.push([deck[i], 0]);
                }
            }
        } else {
            let spot = (have as u64) << 60
                | runout.iter().flatten().enumerate().fold(0u64, |m, (i, &c)| m | (c as u64) << (i * 8));
            let rng = &mut Rng::new(cx.seed ^ spot.wrapping_mul(0x9E37_79B9_7F4A_7C15));
            for _ in 0..want {
                let a = rng.below(free.len() as u32) as usize;
                let mut b = rng.below(free.len() as u32 - 1) as usize;
                if b >= a {
                    b += 1;
                }
                draws.push([free[a], free[b]]);
            }
        }
        if let Chance::Subset { turn, river, pick } = cx.chance {
            let take = (if next == 1 { turn[1] } else { river[1] }).max(1);
            if take < draws.len() {
                let spot = (have as u64) << 60
                    | runout.iter().flatten().enumerate().fold(0u64, |m, (i, &c)| m | (c as u64) << (i * 8));
                let rng = &mut Rng::new(pick ^ spot.wrapping_mul(0xD6E8_FEB8_6659_FD93));
                for i in 0..take {
                    let j = i + rng.below((draws.len() - i) as u32) as usize;
                    draws.swap(i, j);
                }
                draws.truncate(take);
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
            let mut f = fr.cloned();
            for h in 0..NUM_COMBOS {
                if self.hits(h, mask) {
                    r[0][h] = 0.0;
                    r[1][h] = 0.0;
                    if let Some(f) = f.as_mut() {
                        f[0][h] = 0.0;
                        f[1][h] = 0.0;
                    }
                }
            }
            let ctx = self.street_ctx(next, &ro, used | mask);
            let mut v = self.eval(cx, rec, rng, node_idx, next, &r, f.as_ref(), &ro, used | mask, ctx.as_ref());
            for h in 0..NUM_COMBOS {
                if self.hits(h, mask) {
                    for p in 0..2 {
                        v.avg[p][h] = 0.0;
                        if cx.want_best {
                            for b in v.best.iter_mut() {
                                b[p][h] = 0.0;
                            }
                        }
                    }
                }
            }
            v
        };
        let empty = || {
            let avg = [vec![0.0f32; NUM_COMBOS], vec![0.0f32; NUM_COMBOS]];
            let best = best_like(&avg, cx.want_best);
            Vals { avg, best }
        };
        let add = |mut acc: Vals, v: Vals| {
            for p in 0..2 {
                for h in 0..NUM_COMBOS {
                    acc.avg[p][h] += v.avg[p][h];
                }
                if cx.want_best {
                    for (a, b) in acc.best.iter_mut().zip(&v.best) {
                        for h in 0..NUM_COMBOS {
                            a[p][h] += b[p][h];
                        }
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
            for b in sum.best.iter_mut() {
                b[p].iter_mut().for_each(|x| *x *= scale);
            }
        }
        sum
    }

    fn showdown(&self, node_idx: u32, node: &BpNode, p: usize, reach: &[f32], ctx: &StreetCtx) -> Vec<f32> {
        let nb = self.abs.num_boards();
        let put = self.tree.put(node_idx, p);
        let win = node.pot_net / nb as f32;
        let compat = self.compatible(reach);
        let mut out: Vec<f32> = compat.iter().map(|&c| -put * c).collect();
        for b in 0..nb {
            let won = self.beaten(&ctx.key[b], &ctx.order[b], reach);
            for h in 0..NUM_COMBOS {
                out[h] += win * won[h];
            }
        }
        out
    }
}
