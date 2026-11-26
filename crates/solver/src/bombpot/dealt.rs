//! Self-play by dealt hands, for any number of seats the net describes.
//!
//! Whole-range play (`range`, `range3`) weighs every hand of every seat at
//! every decision: exact, but with four or more players a hand's value
//! depends on too many combinations of the others' hands. Here only one
//! seat, the learner, holds every hand at once. The other seats are each
//! dealt one hand, and the turn and river cards are dealt too. The others
//! take one action at each of their decisions, drawn from the strategy; the
//! learner tries all of its actions. Each of the learner's decisions on the
//! way then gives, for every hand it can hold beside the dealt cards, what
//! each action was worth in this one deal: an advantage example. Over many
//! deals the examples at a spot average to what whole-range play works out
//! (the published name is external sampling, with the learner's hands kept
//! together).
//!
//! The mixes the learner plays are recorded on separate walks that try
//! every action of the other seats (or one drawn evenly, for big trees), so
//! that how often a spot is recorded does not depend on what the others
//! play this round: the strategy net then averages the rounds the way the
//! whole-range loop does.

use rayon::prelude::*;
use serde::{Deserialize, Serialize};

use super::abstraction::{strengths, Rng, Runout};
use super::deepcfr::{sample_cards, GameCtx, SampleBuf, THIN};
use super::net::*;
use super::range::{At, Policy};
use super::tree::*;
use crate::cards::{combo_from_index, Card, NUM_COMBOS};

/// How a run deals (`GenSpec::dealt`).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Dealt {
    /// Turn and river cards dealt per game and run for advantage examples.
    pub runouts: usize,
    /// Sets of hands dealt to the other seats on each of them.
    #[serde(default = "one")]
    pub hands: usize,
    /// Turn and river cards dealt per game and run for strategy examples.
    pub strategy_runouts: usize,
    /// A strategy walk tries every action of the other seats (true), or one
    /// drawn evenly at each of their decisions (false).
    #[serde(default = "yes")]
    pub strategy_all: bool,
    /// Share of hands kept as strategy examples at flop, turn and river
    /// decisions (the spec's `keep` when left out; `keep` is then for the
    /// advantage examples, of which a run makes far more).
    #[serde(default)]
    pub strategy_keep: Option<[f32; 3]>,
}

fn one() -> usize {
    1
}
fn yes() -> bool {
    true
}

/// The cards of one deal as each street sees them.
struct Board {
    /// `seen[street]`: the runout with later cards blanked.
    seen: [Runout; 3],
    /// Every board card visible on a street.
    used: [u64; 3],
}

fn deal_board(game: &GameCtx, rng: &mut Rng) -> Board {
    let abs = &game.abs;
    let nb = abs.num_boards();
    let mut deck: Vec<Card> = (0..52u8).filter(|&c| abs.dead >> c & 1 == 0).collect();
    let mut draw = |rng: &mut Rng| deck.swap_remove(rng.below(deck.len() as u32) as usize);
    let mut full: Runout = [[0; 2]; 2];
    for street in 0..2 {
        for row in full.iter_mut().take(nb) {
            row[street] = draw(rng);
        }
    }
    let mut b = Board { seen: [[[0; 2]; 2]; 3], used: [abs.dead; 3] };
    for street in 1..3 {
        for i in 0..nb {
            for st in 0..street {
                b.seen[street][i][st] = full[i][st];
                b.used[street] |= 1u64 << full[i][st];
            }
        }
    }
    b
}

struct DealWalk<'a> {
    game: &'a GameCtx,
    policy: &'a dyn Policy,
    learner: usize,
    board: &'a Board,
    /// Showdown strength of every hand on each board.
    key: &'a [Vec<u32>],
    /// The dealt hand of every other seat.
    held: [usize; MAX_PLAYERS],
    /// The learner's hands that fit beside every dealt card.
    fits: Vec<u16>,
    keep: [f32; 3],
    adv: &'a mut SampleBuf,
    rng: &'a mut Rng,
}

impl DealWalk<'_> {
    /// What the learner's hands get from this node on, in this deal.
    fn walk(&mut self, node_idx: u32) -> Vec<f32> {
        let g = self.game;
        let node = &g.tree.nodes[node_idx as usize];
        let p = self.learner;
        let live = |s: usize| node.live >> s & 1 != 0;
        let mut out = vec![0.0f32; NUM_COMBOS];
        let (board, keys) = (self.board, self.key);
        if node.kind != KIND_ACTION {
            let put = g.tree.put(node_idx, p);
            if !live(p) || node.kind == KIND_FOLD {
                let v = if live(p) { node.pot_net - put } else { -put };
                for &h in &self.fits {
                    out[h as usize] = v;
                }
                return out;
            }
            let win = node.pot_net / keys.len() as f32;
            for &h in &self.fits {
                out[h as usize] = -put;
            }
            for key in keys {
                let rivals = (0..g.tree.players()).filter(|&s| s != p && live(s)).map(|s| key[self.held[s]]);
                let top = rivals.clone().max().unwrap_or(0);
                let tied = rivals.filter(|&k| k == top).count() as f32;
                for &h in &self.fits {
                    let k = key[h as usize];
                    if k > top {
                        out[h as usize] += win;
                    } else if k == top {
                        out[h as usize] += win / (tied + 1.0);
                    }
                }
            }
            return out;
        }
        let actor = node.player as usize;
        let na = node.num_children as usize;
        let street = node.street as usize;
        let at = At { node_idx, runout: &board.seen[street], used: board.used[street], range: None };
        if actor != p {
            let mut probs = [0.0f32; MAX_ACTIONS];
            self.policy.one_hand(&at, self.held[actor], &mut probs);
            let mut x = self.rng.f32() * probs[..na].iter().sum::<f32>();
            let mut pick = na - 1;
            for (a, &pr) in probs[..na].iter().enumerate() {
                if x < pr {
                    pick = a;
                    break;
                }
                x -= pr;
            }
            return self.walk(g.tree.child(node, pick));
        }
        let mut sigma = vec![0.0f32; na * NUM_COMBOS];
        self.policy.strategies(&at, &mut sigma);
        let vals: Vec<Vec<f32>> = (0..na).map(|a| self.walk(g.tree.child(node, a))).collect();
        for &h in &self.fits {
            let h = h as usize;
            out[h] = (0..na).map(|a| sigma[a * NUM_COMBOS + h] * vals[a][h]).sum();
        }
        let slots = &g.pubf.slots[node_idx as usize];
        let mask = slots[..na].iter().fold(0u8, |m, &s| m | 1 << s);
        let mut hf = [0.0f32; HAND];
        for &h in &self.fits {
            if self.rng.f32() >= self.keep[street] {
                continue;
            }
            let h = h as usize;
            hand_feats(&g.abs, street, h, at.runout, None, &mut hf);
            let cards = sample_cards(&g.abs, street, h, at.runout);
            let mut t = [0.0f32; MENU];
            for a in 0..na {
                t[slots[a] as usize] = (vals[a][h] - out[h]) / node.pot;
            }
            self.adv.push(&cards, mask, street as u8, p as u8, 1.0, node_idx, &hf, &t);
        }
        out
    }
}

struct StrategyWalk<'a> {
    game: &'a GameCtx,
    policy: &'a dyn Policy,
    learner: usize,
    board: &'a Board,
    all: bool,
    keep: [f32; 3],
    strat: &'a mut SampleBuf,
    rng: &'a mut Rng,
}

impl StrategyWalk<'_> {
    /// `reach[hand]`: how likely the learner is to be here with the hand.
    fn walk(&mut self, node_idx: u32, reach: &[f32]) {
        let g = self.game;
        let node = &g.tree.nodes[node_idx as usize];
        if node.kind != KIND_ACTION {
            return;
        }
        let na = node.num_children as usize;
        if node.player as usize != self.learner {
            if self.all {
                for a in 0..na {
                    self.walk(g.tree.child(node, a), reach);
                }
            } else {
                let a = self.rng.below(na as u32) as usize;
                self.walk(g.tree.child(node, a), reach);
            }
            return;
        }
        let street = node.street as usize;
        let board = self.board;
        let at = At { node_idx, runout: &board.seen[street], used: board.used[street], range: None };
        let mut sigma = vec![0.0f32; na * NUM_COMBOS];
        self.policy.strategies(&at, &mut sigma);
        let slots = &g.pubf.slots[node_idx as usize];
        let mask = slots[..na].iter().fold(0u8, |m, &s| m | 1 << s);
        let mut hf = [0.0f32; HAND];
        for h in 0..NUM_COMBOS {
            let r = reach[h];
            if r <= 1e-6 || self.rng.f32() >= self.keep[street] * (r / THIN).min(1.0) {
                continue;
            }
            hand_feats(&g.abs, street, h, at.runout, None, &mut hf);
            let cards = sample_cards(&g.abs, street, h, at.runout);
            let mut t = [0.0f32; MENU];
            for a in 0..na {
                t[slots[a] as usize] = sigma[a * NUM_COMBOS + h];
            }
            self.strat.push(&cards, mask, street as u8, self.learner as u8, r.max(THIN), node_idx, &hf, &t);
        }
        for a in 0..na {
            let sa = &sigma[a * NUM_COMBOS..(a + 1) * NUM_COMBOS];
            let child: Vec<f32> = (0..NUM_COMBOS).map(|h| reach[h] * sa[h]).collect();
            if child.iter().any(|&x| x != 0.0) {
                self.walk(g.tree.child(node, a), &child);
            }
        }
    }
}

fn hand_mask(h: usize) -> u64 {
    let (a, b) = combo_from_index(h);
    1u64 << a | 1u64 << b
}

/// Play one game's run and return its examples (advantages, strategies)
/// for the decisions of `learner`.
pub fn play(game: &GameCtx, policy: &dyn Policy, d: &Dealt, keep: [f32; 3], learner: usize, seed: u64) -> Result<(SampleBuf, SampleBuf), String> {
    if game.abs.root_street != 0 {
        return Err("dealt self-play starts on the flop".into());
    }
    let players = game.tree.players();
    let fresh = |kind: u32| {
        let mut b = SampleBuf::new(kind);
        b.pub_rows.extend_from_slice(&game.pubf.rows);
        b
    };
    // Same game throughout: the rows of betting inputs are shared.
    let join = |kind: u32, parts: Vec<SampleBuf>| {
        let mut all = fresh(kind);
        for p in parts {
            all.recs.extend_from_slice(&p.recs);
            all.n += p.n;
        }
        all
    };
    let adv: Vec<SampleBuf> = (0..d.runouts)
        .into_par_iter()
        .map(|i| {
            let mut rng = Rng::new(seed ^ (i as u64 + 1).wrapping_mul(0x9E37_79B9_7F4A_7C15));
            let board = deal_board(game, &mut rng);
            let nb = game.abs.num_boards();
            let all = board.used[2];
            let key: Vec<Vec<u32>> = (0..nb).map(|b| strengths(&game.abs.full_board(b, &board.seen[2]), all)).collect();
            let mut adv = SampleBuf::new(KIND_ADVANTAGE);
            for _ in 0..d.hands.max(1) {
                let mut deck: Vec<Card> = (0..52u8).filter(|&c| all >> c & 1 == 0).collect();
                let mut held = [0usize; MAX_PLAYERS];
                let mut taken = all;
                for (s, slot) in held.iter_mut().enumerate().take(players) {
                    if s != learner {
                        let a = deck.swap_remove(rng.below(deck.len() as u32) as usize);
                        let b = deck.swap_remove(rng.below(deck.len() as u32) as usize);
                        *slot = crate::cards::combo_index(a, b);
                        taken |= 1u64 << a | 1u64 << b;
                    }
                }
                let fits: Vec<u16> = (0..NUM_COMBOS as u16).filter(|&h| hand_mask(h as usize) & taken == 0).collect();
                let mut w = DealWalk { game, policy, learner, board: &board, key: &key, held, fits, keep, adv: &mut adv, rng: &mut rng };
                w.walk(0);
            }
            adv
        })
        .collect();
    let strat: Vec<SampleBuf> = (0..d.strategy_runouts)
        .into_par_iter()
        .map(|i| {
            let mut rng = Rng::new(seed ^ (i as u64 + 1).wrapping_mul(0xD6E8_FEB8_6659_FD93));
            let board = deal_board(game, &mut rng);
            let reach: Vec<f32> = (0..NUM_COMBOS).map(|h| if hand_mask(h) & board.used[2] == 0 { 1.0 } else { 0.0 }).collect();
            let mut strat = SampleBuf::new(KIND_POLICY);
            let keep = d.strategy_keep.unwrap_or(keep);
            let mut w = StrategyWalk { game, policy, learner, board: &board, all: d.strategy_all, keep, strat: &mut strat, rng: &mut rng };
            w.walk(0, &reach);
            strat
        })
        .collect();
    Ok((join(KIND_ADVANTAGE, adv), join(KIND_POLICY, strat)))
}
