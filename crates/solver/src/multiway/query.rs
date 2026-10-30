//! Browsing a three-player solution: walk an action/card path, then
//! summarize the node for the UI (actions, per-hand strategy and EV, the
//! 13x13 class grid and each player's remaining range).

use super::eval::compatible_mass;
use super::solver::{Dealt, MwSolver};
use super::tree::{KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, NP};
use crate::cards::*;
use crate::tree::{Action, SENTINEL};
use serde::{Deserialize, Serialize};

/// One step of a path: an action index at an action node, or a card at a
/// chance node.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum MwStep {
    Action(usize),
    Card(String),
}

#[derive(Debug, Clone, Serialize)]
pub struct MwActionView {
    pub label: String,
    /// fold | check | call | bet | raise
    pub kind: &'static str,
    /// Chips the action adds to the pot.
    pub amount: f64,
    /// Range-weighted frequency of the action at this node.
    pub freq: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct MwHandView {
    pub combo: String,
    pub class: usize,
    /// The actor's reach of this combo at the node (preflop weight times
    /// its own action probabilities so far, 0 if blocked).
    pub weight: f32,
    pub strategy: Vec<f32>,
    /// Expected winnings from here (pot-share convention: folding now = 0,
    /// taking the whole pot without further betting = pot).
    pub ev: Option<f32>,
}

#[derive(Debug, Clone, Serialize)]
pub struct MwClassView {
    pub label: String,
    /// Sum of reach weights over the class's combos.
    pub weight: f32,
    pub combos: u32,
    pub strategy: Vec<f32>,
    pub ev: Option<f32>,
}

#[derive(Debug, Clone, Serialize)]
pub struct MwNodeView {
    pub node: u32,
    /// "action", "chance", "fold" or "showdown".
    pub kind: &'static str,
    pub street: u8,
    pub board: Vec<String>,
    pub pot: f64,
    pub put: [f64; NP],
    pub live: [bool; NP],
    pub actor: Option<usize>,
    pub actions: Vec<MwActionView>,
    pub hands: Vec<MwHandView>,
    pub classes: Vec<MwClassView>,
    /// Weighted combos left in each player's range.
    pub range_combos: [f64; NP],
    /// Chance node: the cards that can come.
    pub cards: Vec<String>,
}

/// Index 0..169 of a combo's hand class: pairs on the diagonal, suited above
/// (row = higher rank), offsuit below; row 0 = aces.
pub fn class_index(c1: Card, c2: Card) -> usize {
    let (r1, r2) = (12 - rank(c1).max(rank(c2)) as usize, 12 - rank(c1).min(rank(c2)) as usize);
    if r1 == r2 {
        r1 * 13 + r1
    } else if suit(c1) == suit(c2) {
        r1 * 13 + r2
    } else {
        r2 * 13 + r1
    }
}

pub fn class_label(k: usize) -> String {
    let (r, c) = (k / 13, k % 13);
    let ch = |i: usize| RANK_CHARS[12 - i];
    if r == c {
        format!("{}{}", ch(r), ch(r))
    } else if r < c {
        format!("{}{}s", ch(r), ch(c))
    } else {
        format!("{}{}o", ch(c), ch(r))
    }
}

/// Reach of every player and the dealt cards after `path`.
pub fn walk(s: &MwSolver, path: &[MwStep]) -> Result<(u32, [Vec<f32>; NP], Dealt), String> {
    let spot = &*s.spot;
    let mut reach: [Vec<f32>; NP] = spot.weights.clone();
    let mut dealt = Dealt::default();
    let mut idx = 0u32;
    for (i, step) in path.iter().enumerate() {
        let node = &spot.tree.nodes[idx as usize];
        match (node.kind, step) {
            (KIND_ACTION, MwStep::Action(a)) => {
                let na = node.num_children as usize;
                if *a >= na {
                    return Err(format!("step {i}: action {a} out of range ({na} actions)"));
                }
                let k = node.player as usize;
                let nh = spot.hands[k].len();
                let sigma = s.average_strategy(idx);
                for j in 0..nh {
                    reach[k][j] *= sigma[a * nh + j];
                }
                idx = spot.tree.child(node, *a);
            }
            (KIND_CHANCE, MwStep::Card(cs)) => {
                let c = card_from_str(cs)?;
                let ch = spot.tree.children[node.children_start as usize + c as usize];
                if ch == SENTINEL || dealt.contains(c) {
                    return Err(format!("step {i}: card {cs} cannot be dealt here"));
                }
                let cm = card_mask(c);
                for k in 0..NP {
                    for (j, h) in spot.hands[k].iter().enumerate() {
                        if h.mask & cm != 0 {
                            reach[k][j] = 0.0;
                        }
                    }
                }
                dealt = dealt.push(c);
                idx = ch;
            }
            _ => return Err(format!("step {i} does not match the node (kind {})", node.kind)),
        }
    }
    Ok((idx, reach, dealt))
}

fn action_label(s: &MwSolver, node_idx: u32, a: usize) -> String {
    let spot = &*s.spot;
    let node = &spot.tree.nodes[node_idx as usize];
    let k = node.player as usize;
    let pot: f64 = node.put.iter().map(|&x| x as f64).sum();
    let child = &spot.tree.nodes[spot.tree.child(node, a) as usize];
    let cfg = &spot.tree.config;
    let all_in = child.put[k] as f64 >= spot.tree.root_put() + cfg.stacks[k] - 1e-6;
    let added = child.put[k] as f64 - node.put[k] as f64;
    let num = |x: f64| if (x - x.round()).abs() < 0.01 { format!("{}", x.round()) } else { format!("{x:.1}") };
    match spot.tree.node_actions(node)[a] {
        Action::Fold => "Fold".into(),
        Action::Check => "Check".into(),
        Action::Call(_) if all_in => format!("Call all-in {}", num(added)),
        Action::Call(_) => format!("Call {}", num(added)),
        Action::Bet(to) if all_in => format!("All-in {}", num(to)),
        Action::Bet(to) => format!("Bet {} ({}%)", num(to), (to / pot * 100.0).round()),
        Action::Raise(to) if all_in => format!("All-in {}", num(to)),
        Action::Raise(to) => format!("Raise to {}", num(to)),
    }
}

/// Summarize the node reached by `path`. `with_ev` runs a traversal of the
/// subtree for the actor's EVs (cheap below the root street, a full
/// iteration's worth of work at the root of a flop tree).
pub fn node_view(s: &MwSolver, path: &[MwStep], with_ev: bool) -> Result<MwNodeView, String> {
    let spot = &*s.spot;
    let (idx, reach, dealt) = walk(s, path)?;
    let node = &spot.tree.nodes[idx as usize];
    let mut board: Vec<String> = spot.board.iter().map(|&c| card_to_string(c)).collect();
    board.extend(dealt.as_slice().iter().map(|&c| card_to_string(c)));
    let put = node.put.map(|x| x as f64);
    let range_combos = std::array::from_fn(|k| reach[k].iter().map(|&x| x as f64).sum());
    let mut view = MwNodeView {
        node: idx,
        kind: match node.kind {
            KIND_ACTION => "action",
            KIND_CHANCE => "chance",
            KIND_TERM_FOLD => "fold",
            _ => "showdown",
        },
        street: node.street,
        board,
        pot: put.iter().sum(),
        put,
        live: std::array::from_fn(|k| node.live & (1 << k) != 0),
        actor: None,
        actions: Vec::new(),
        hands: Vec::new(),
        classes: Vec::new(),
        range_combos,
        cards: Vec::new(),
    };
    match node.kind {
        KIND_CHANCE => {
            for c in 0..52u8 {
                let ch = spot.tree.children[node.children_start as usize + c as usize];
                if ch != SENTINEL && !dealt.contains(c) {
                    view.cards.push(card_to_string(c));
                }
            }
        }
        KIND_ACTION => {
            let k = node.player as usize;
            let na = node.num_children as usize;
            let nh = spot.hands[k].len();
            view.actor = Some(k);
            let sigma = s.average_strategy(idx);
            let total: f64 = reach[k].iter().map(|&x| x as f64).sum();
            for a in 0..na {
                let f: f64 = (0..nh).map(|j| reach[k][j] as f64 * sigma[a * nh + j] as f64).sum();
                let child = &spot.tree.nodes[spot.tree.child(node, a) as usize];
                view.actions.push(MwActionView {
                    label: action_label(s, idx, a),
                    kind: match spot.tree.node_actions(node)[a] {
                        Action::Fold => "fold",
                        Action::Check => "check",
                        Action::Call(_) => "call",
                        Action::Bet(_) => "bet",
                        Action::Raise(_) => "raise",
                    },
                    amount: (child.put[k] - node.put[k]) as f64,
                    freq: if total > 0.0 { f / total } else { 0.0 },
                });
            }
            let ev = if with_ev {
                let rr = [&reach[0][..], &reach[1][..], &reach[2][..]];
                let cfv = s.node_values(idx, k, rr, dealt, false);
                let mut mass = vec![0f32; nh];
                compatible_mass(spot, k, rr, &mut mass);
                Some(
                    (0..nh)
                        .map(|j| if mass[j] > 0.0 { cfv[j] / mass[j] + put[k] as f32 } else { f32::NAN })
                        .collect::<Vec<f32>>(),
                )
            } else {
                None
            };
            let mut cw = vec![0f64; 169];
            let mut cn = vec![0u32; 169];
            let mut cs = vec![0f64; 169 * na];
            let mut cev = vec![0f64; 169];
            let mut cevw = vec![0f64; 169];
            for (j, h) in spot.hands[k].iter().enumerate() {
                let cl = class_index(h.c1, h.c2);
                let w = reach[k][j];
                let strat: Vec<f32> = (0..na).map(|a| sigma[a * nh + j]).collect();
                let e = ev.as_ref().map(|v| v[j]).filter(|x| x.is_finite());
                if dealt.as_slice().iter().any(|&c| h.mask & card_mask(c) != 0) {
                    continue;
                }
                cn[cl] += 1;
                cw[cl] += w as f64;
                for a in 0..na {
                    cs[cl * na + a] += w as f64 * strat[a] as f64;
                }
                if let Some(e) = e {
                    cev[cl] += w as f64 * e as f64;
                    cevw[cl] += w as f64;
                }
                view.hands.push(MwHandView {
                    combo: format!("{}{}", card_to_string(h.c1.max(h.c2)), card_to_string(h.c1.min(h.c2))),
                    class: cl,
                    weight: w,
                    strategy: strat,
                    ev: e,
                });
            }
            for cl in 0..169 {
                view.classes.push(MwClassView {
                    label: class_label(cl),
                    weight: cw[cl] as f32,
                    combos: cn[cl],
                    strategy: (0..na)
                        .map(|a| if cw[cl] > 0.0 { (cs[cl * na + a] / cw[cl]) as f32 } else { 0.0 })
                        .collect(),
                    ev: (cevw[cl] > 0.0).then(|| (cev[cl] / cevw[cl]) as f32),
                });
            }
        }
        _ => {}
    }
    Ok(view)
}
