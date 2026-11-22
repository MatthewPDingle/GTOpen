//! Exact scoring of a two-player bomb pot strategy.
//!
//! Walks the whole game with every hand at once (no sampling, no hand
//! grouping on the scoring side) and returns what each seat earns under the
//! average strategies, and what each seat could earn with a perfect reply to
//! the other. The gap between the two is how far the strategies are from
//! unbeatable, in chips per hand. Two players only: with more, an exact reply
//! needs every combination of opponents' hands.

use rayon::prelude::*;

use super::abstraction::{strengths, Runout};
use super::solver::BpSolver;
use super::tree::*;
use crate::cards::{combo_from_index, Card, NUM_COMBOS};

#[derive(Clone, Copy, PartialEq)]
enum Mode {
    Average,
    Best,
}

/// Hands in rising order of strength on each board, for one full runout.
struct RiverCtx {
    strength: Vec<Vec<u32>>,
    order: Vec<Vec<u16>>,
}

pub struct ExactValues {
    /// Each seat's result when both play the average strategy.
    pub value: [f64; 2],
    /// Each seat's result with a perfect reply to the other's average strategy.
    pub best: [f64; 2],
}

impl ExactValues {
    /// Average of the two seats' possible gains, in chips per hand.
    pub fn exploitability(&self) -> f64 {
        ((self.best[0] - self.value[0]) + (self.best[1] - self.value[1])) / 2.0
    }
}

struct Cards {
    c1: [Card; NUM_COMBOS],
    c2: [Card; NUM_COMBOS],
}

fn combo_cards() -> Cards {
    let mut c = Cards { c1: [0; NUM_COMBOS], c2: [0; NUM_COMBOS] };
    for h in 0..NUM_COMBOS {
        let (a, b) = combo_from_index(h);
        c.c1[h] = a;
        c.c2[h] = b;
    }
    c
}

pub struct Exact2<'a> {
    s: &'a BpSolver,
    cards: Cards,
}

impl<'a> Exact2<'a> {
    pub fn new(s: &'a BpSolver) -> Result<Exact2<'a>, String> {
        if s.players() != 2 {
            return Err("exact scoring needs exactly two players".into());
        }
        Ok(Exact2 { s, cards: combo_cards() })
    }

    pub fn values(&self) -> ExactValues {
        let s = self.s;
        let root = s.abs.root_street as usize;
        let mut reach = vec![0.0f32; NUM_COMBOS];
        for h in 0..NUM_COMBOS {
            if (1u64 << self.cards.c1[h] | 1u64 << self.cards.c2[h]) & s.abs.dead == 0 {
                reach[h] = 1.0;
            }
        }
        let runout: Runout = [[0; 2]; 2];
        let ctx = if root == 2 { Some(self.river_ctx(&runout)) } else { None };
        // Number of (hand, hand) pairs that do not share a card.
        let compat = self.compatible(&reach);
        let pairs: f64 = (0..NUM_COMBOS).map(|h| reach[h] as f64 * compat[h] as f64).sum();
        let mut out = ExactValues { value: [0.0; 2], best: [0.0; 2] };
        for p in 0..2 {
            for mode in [Mode::Average, Mode::Best] {
                let v = self.eval(0, root, p, &reach, &runout, s.abs.dead, ctx.as_ref(), mode, true);
                let total: f64 = (0..NUM_COMBOS).map(|h| reach[h] as f64 * v[h] as f64).sum();
                match mode {
                    Mode::Average => out.value[p] = total / pairs,
                    Mode::Best => out.best[p] = total / pairs,
                }
            }
        }
        out
    }

    /// For each hand, the summed reach of opposing hands that share no card with it.
    fn compatible(&self, reach: &[f32]) -> Vec<f32> {
        let mut total = 0.0f64;
        let mut by_card = [0.0f64; 52];
        for h in 0..NUM_COMBOS {
            let r = reach[h] as f64;
            if r != 0.0 {
                total += r;
                by_card[self.cards.c1[h] as usize] += r;
                by_card[self.cards.c2[h] as usize] += r;
            }
        }
        (0..NUM_COMBOS)
            .map(|h| {
                (total - by_card[self.cards.c1[h] as usize] - by_card[self.cards.c2[h] as usize] + reach[h] as f64)
                    as f32
            })
            .collect()
    }

    fn river_ctx(&self, runout: &Runout) -> RiverCtx {
        let s = self.s;
        let nb = s.abs.num_boards();
        let fulls: Vec<[Card; 5]> = (0..nb).map(|b| s.abs.full_board(b, runout)).collect();
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
        node_idx: u32,
        have: usize,
        p: usize,
        reach: &[f32],
        runout: &Runout,
        used: u64,
        ctx: Option<&RiverCtx>,
        mode: Mode,
        top: bool,
    ) -> Vec<f32> {
        let s = self.s;
        let node = &s.tree.nodes[node_idx as usize];
        if node.kind == KIND_FOLD {
            let put = s.tree.put(node_idx, p);
            let gain = if node.live >> p & 1 != 0 { node.pot_net - put } else { -put };
            let mut v = self.compatible(reach);
            v.iter_mut().for_each(|x| *x *= gain);
            return v;
        }
        let need = if node.kind == KIND_SHOWDOWN { 2 } else { node.street as usize };
        if have < need {
            return self.deal_street(node_idx, have, p, reach, runout, used, mode, top);
        }
        if node.kind == KIND_SHOWDOWN {
            return self.showdown(node_idx, node, p, reach, ctx.expect("river context"));
        }
        let actor = node.player as usize;
        let na = node.num_children as usize;
        let street = node.street as usize;
        // Average strategy of the actor for every hand.
        let mut sigma = vec![0.0f32; na * NUM_COMBOS];
        let need_sigma = actor != p || mode == Mode::Average;
        if need_sigma {
            let mut row = [0.0f32; MAX_ACTIONS];
            for h in 0..NUM_COMBOS {
                if (1u64 << self.cards.c1[h] | 1u64 << self.cards.c2[h]) & used != 0 {
                    continue;
                }
                s.average(node, s.abs.bucket(street, h, runout), &mut row);
                for a in 0..na {
                    sigma[a * NUM_COMBOS + h] = row[a];
                }
            }
        }
        if actor == p {
            let mut out = vec![if mode == Mode::Best { f32::NEG_INFINITY } else { 0.0 }; NUM_COMBOS];
            for a in 0..na {
                let v = self.eval(s.tree.child(node, a), have, p, reach, runout, used, ctx, mode, false);
                match mode {
                    Mode::Best => {
                        for h in 0..NUM_COMBOS {
                            if v[h] > out[h] {
                                out[h] = v[h];
                            }
                        }
                    }
                    Mode::Average => {
                        for h in 0..NUM_COMBOS {
                            out[h] += sigma[a * NUM_COMBOS + h] * v[h];
                        }
                    }
                }
            }
            out
        } else {
            let mut out = vec![0.0f32; NUM_COMBOS];
            let mut r = vec![0.0f32; NUM_COMBOS];
            for a in 0..na {
                let mut any = false;
                for h in 0..NUM_COMBOS {
                    r[h] = reach[h] * sigma[a * NUM_COMBOS + h];
                    any |= r[h] != 0.0;
                }
                if !any {
                    continue;
                }
                let v = self.eval(s.tree.child(node, a), have, p, &r, runout, used, ctx, mode, false);
                for h in 0..NUM_COMBOS {
                    out[h] += v[h];
                }
            }
            out
        }
    }

    /// Deal the next street on every board and average over the cards.
    #[allow(clippy::too_many_arguments)]
    fn deal_street(
        &self,
        node_idx: u32,
        have: usize,
        p: usize,
        reach: &[f32],
        runout: &Runout,
        used: u64,
        mode: Mode,
        top: bool,
    ) -> Vec<f32> {
        let s = self.s;
        let nb = s.abs.num_boards();
        let next = have + 1;
        let free: Vec<Card> = (0..52u8).filter(|&c| used >> c & 1 == 0).collect();
        // Cards left once both hands are out of the deck.
        let left = free.len() as f64 - 4.0;
        let mut draws: Vec<[Card; 2]> = Vec::new();
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
        let prob = if nb == 1 { 1.0 / left } else { 1.0 / (left * (left - 1.0)) } as f32;
        let one = |draw: &[Card; 2]| -> Vec<f32> {
            let mut ro = *runout;
            let mut mask = 0u64;
            for b in 0..nb {
                ro[b][next - 1] = draw[b];
                mask |= 1u64 << draw[b];
            }
            let mut r = reach.to_vec();
            for h in 0..NUM_COMBOS {
                if (1u64 << self.cards.c1[h] | 1u64 << self.cards.c2[h]) & mask != 0 {
                    r[h] = 0.0;
                }
            }
            let ctx = if next == 2 { Some(self.river_ctx(&ro)) } else { None };
            let mut v = self.eval(node_idx, next, p, &r, &ro, used | mask, ctx.as_ref(), mode, false);
            for h in 0..NUM_COMBOS {
                if (1u64 << self.cards.c1[h] | 1u64 << self.cards.c2[h]) & mask != 0 {
                    v[h] = 0.0;
                }
            }
            v
        };
        let add = |mut acc: Vec<f32>, v: Vec<f32>| {
            for h in 0..NUM_COMBOS {
                acc[h] += v[h];
            }
            acc
        };
        let mut sum = if top {
            draws.par_iter().map(one).reduce(|| vec![0.0f32; NUM_COMBOS], add)
        } else {
            draws.iter().map(one).fold(vec![0.0f32; NUM_COMBOS], add)
        };
        sum.iter_mut().for_each(|x| *x *= prob);
        sum
    }

    fn showdown(&self, node_idx: u32, node: &BpNode, p: usize, reach: &[f32], ctx: &RiverCtx) -> Vec<f32> {
        let s = self.s;
        let nb = s.abs.num_boards();
        let put = s.tree.put(node_idx, p);
        let win = node.pot_net / nb as f32;
        let compat = self.compatible(reach);
        let mut out: Vec<f32> = compat.iter().map(|&c| -put * c).collect();
        let (c1, c2) = (&self.cards.c1, &self.cards.c2);
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
