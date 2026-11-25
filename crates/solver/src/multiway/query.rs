//! Browsing a three-player solution: walk an action/card path, then
//! summarize the node for the Browse page in the same shape the heads-up
//! solver answers with (`crate::query::NodeView`), for three players.

use super::eval::{compatible_mass, showdown_equity};
use super::solver::{Dealt, MwSolver};
use super::tree::{MwNode, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, NP};
use crate::cards::*;
use crate::query::{ActionView, ExploitHandView, ExploitView, HandView, HistoryStep, PathStep, PlayerView};
use crate::tree::{Action, SENTINEL};
use serde::Serialize;

/// A node of a three-player solve, shaped like the heads-up `NodeView`.
#[derive(Debug, Clone, Serialize)]
pub struct MwNodeView {
    pub node_type: String,
    pub street: u8,
    pub board: Vec<String>,
    pub pot: f64,
    pub put: [f64; NP],
    /// Players who have not folded.
    pub live: [bool; NP],
    pub player: Option<u8>,
    pub actions: Vec<ActionView>,
    /// Chance nodes: cards that can come next.
    pub available_cards: Option<Vec<String>>,
    pub players: [PlayerView; NP],
    pub locked: bool,
    /// One entry per node along the path, plus the current node (chosen=None).
    pub history: Vec<HistoryStep>,
    /// EVs left out because the subtree is too big to evaluate on the CPU
    /// while browsing: "others" (only the player to act has EVs) or "all".
    pub ev_skipped: Option<&'static str>,
}

/// Arena entries above which root-street EVs are skipped while browsing
/// (one CPU pass over a lean flop takes minutes). One pass gives one
/// player's EVs, so all three players get theirs up to a third of this.
const EV_MAX_ENTRIES: u64 = 400_000_000;

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
pub fn walk(s: &MwSolver, path: &[PathStep]) -> Result<(u32, [Vec<f32>; NP], Dealt), String> {
    let spot = &*s.spot;
    let mut reach: [Vec<f32>; NP] = spot.weights.clone();
    let mut dealt = Dealt::default();
    let mut idx = 0u32;
    for (i, step) in path.iter().enumerate() {
        let node = &spot.tree.nodes[idx as usize];
        match (node.kind, step) {
            (KIND_ACTION, PathStep::Action { index: a }) => {
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
            (KIND_CHANCE, PathStep::Card { card: cs }) => {
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

fn node_type(node: &MwNode) -> String {
    match node.kind {
        KIND_ACTION => "action",
        KIND_CHANCE => "chance",
        KIND_TERM_FOLD => "terminal_fold",
        KIND_TERM_SHOWDOWN => "terminal_showdown",
        _ => "?",
    }
    .to_string()
}

/// The node's actions, labelled like the heads-up solver's.
fn action_views(s: &MwSolver, node_idx: u32) -> Vec<ActionView> {
    let spot = &*s.spot;
    let node = &spot.tree.nodes[node_idx as usize];
    if node.kind != KIND_ACTION {
        return Vec::new();
    }
    let k = node.player as usize;
    let pot: f64 = node.put.iter().map(|&x| x as f64).sum();
    let cfg = &spot.tree.config;
    (0..node.num_children as usize)
        .map(|a| {
            let action = spot.tree.node_actions(node)[a];
            let child = &spot.tree.nodes[spot.tree.child(node, a) as usize];
            let all_in = action.is_aggressive() && child.put[k] as f64 >= spot.tree.root_put() + cfg.stacks[k] - 1e-6;
            ActionView {
                label: action.label(pot, all_in),
                kind: match action {
                    Action::Fold => "fold",
                    Action::Check => "check",
                    Action::Call(_) => "call",
                    Action::Bet(_) => "bet",
                    Action::Raise(_) => "raise",
                }
                .to_string(),
                amount: match action {
                    Action::Call(_) => (child.put[k] - node.put[k]) as f64,
                    Action::Bet(x) | Action::Raise(x) => x,
                    _ => 0.0,
                },
            }
        })
        .collect()
}

/// One HistoryStep per node along the path, plus the current node.
fn build_history(s: &MwSolver, path: &[PathStep]) -> Result<Vec<HistoryStep>, String> {
    let spot = &*s.spot;
    let cfg = &spot.tree.config;
    let stack_of = |node: &MwNode, p: usize| cfg.stacks[p] - (node.put[p] as f64 - spot.tree.root_put());
    let pot_of = |node: &MwNode| node.put.iter().map(|&x| x as f64).sum::<f64>();
    let mut history = Vec::with_capacity(path.len() + 1);
    let mut idx = 0u32;
    for step in path {
        let node = &spot.tree.nodes[idx as usize];
        match (node.kind, step) {
            (KIND_ACTION, PathStep::Action { index }) => {
                history.push(HistoryStep {
                    kind: "action".to_string(),
                    player: Some(node.player),
                    stack: stack_of(node, node.player as usize),
                    pot: pot_of(node),
                    street: node.street,
                    actions: action_views(s, idx),
                    chosen: Some(*index),
                    card: None,
                });
                idx = spot.tree.child(node, *index);
            }
            (KIND_CHANCE, PathStep::Card { card }) => {
                let c = card_from_str(card)?;
                history.push(HistoryStep {
                    kind: "card".to_string(),
                    player: None,
                    stack: 0.0,
                    pot: pot_of(node),
                    street: node.street,
                    actions: Vec::new(),
                    chosen: None,
                    card: Some(card_to_string(c)),
                });
                idx = spot.tree.children[node.children_start as usize + c as usize];
            }
            _ => return Err("path step does not match node type".to_string()),
        }
    }
    let node = &spot.tree.nodes[idx as usize];
    let actor = node.kind == KIND_ACTION;
    history.push(HistoryStep {
        kind: match node.kind {
            KIND_ACTION => "action",
            KIND_CHANCE => "card",
            _ => "terminal",
        }
        .to_string(),
        player: actor.then_some(node.player),
        stack: if actor { stack_of(node, node.player as usize) } else { 0.0 },
        pot: pot_of(node),
        street: node.street,
        actions: action_views(s, idx),
        chosen: None,
        card: None,
    });
    Ok(history)
}

/// Which EVs a node view may work out: (the player to act, the others).
/// Below the root street a pass is cheap; on it, one pass per player is a
/// third of an iteration's work each.
fn ev_budget(s: &MwSolver, node: &MwNode) -> (bool, bool) {
    let tree = &s.spot.tree;
    let first_street =
        node.street == tree.root_street || (node.kind == KIND_CHANCE && node.street == tree.root_street + 1);
    let entries: u64 = tree.data_size.iter().sum();
    if !first_street || entries <= EV_MAX_ENTRIES / NP as u64 {
        (true, true)
    } else {
        (entries <= EV_MAX_ENTRIES, false)
    }
}

/// Summarize the node reached by `path` for the Browse page: every
/// player's hands with reach, the card-removal mass (`valid`), showdown
/// equity and EV; the player to act also gets the strategy and an EV per
/// action. A folded player has no equity and no EV.
pub fn node_view(s: &MwSolver, path: &[PathStep]) -> Result<MwNodeView, String> {
    let spot = &*s.spot;
    let (idx, reach, dealt) = walk(s, path)?;
    let node = &spot.tree.nodes[idx as usize];
    let mut board: Vec<String> = spot.board.iter().map(|&c| card_to_string(c)).collect();
    board.extend(dealt.as_slice().iter().map(|&c| card_to_string(c)));
    let put = node.put.map(|x| x as f64);
    let rr = [&reach[0][..], &reach[1][..], &reach[2][..]];
    let (ev_actor, ev_others) = ev_budget(s, node);
    let actor = (node.kind == KIND_ACTION).then_some(node.player as usize);
    let na = node.num_children as usize;

    let available_cards = (node.kind == KIND_CHANCE).then(|| {
        (0..52u8)
            .filter(|&c| spot.tree.children[node.children_start as usize + c as usize] != SENTINEL && !dealt.contains(c))
            .map(card_to_string)
            .collect::<Vec<_>>()
    });

    let mut skipped_actor = false;
    let mut skipped_others = false;
    let players: [PlayerView; NP] = std::array::from_fn(|p| {
        let nh = spot.hands[p].len();
        let live = node.live & (1 << p) != 0;
        let mut mass = vec![0f32; nh];
        compatible_mass(spot, p, rr, &mut mass);
        let eq = showdown_equity(spot, node.live, dealt.as_slice(), p, rr, &mass);
        let ev_of = |cfv: f32, i: usize| (mass[i] > 0.0).then(|| (cfv as f64 / mass[i] as f64 + put[p]) as f32);
        let mut ev: Vec<Option<f32>> = vec![None; nh];
        let mut evs: Option<Vec<Vec<Option<f32>>>> = None;
        let mut sigma: Option<Vec<f32>> = None;
        if actor == Some(p) {
            let sg = s.average_strategy(idx);
            if ev_actor {
                let mut per = vec![vec![None; na]; nh];
                let mut total = vec![0f64; nh];
                for a in 0..na {
                    let cfv = s.node_values(spot.tree.child(node, a), p, rr, dealt, false);
                    for i in 0..nh {
                        if let Some(e) = ev_of(cfv[i], i) {
                            per[i][a] = Some(e);
                            total[i] += sg[a * nh + i] as f64 * e as f64;
                        }
                    }
                }
                for i in 0..nh {
                    ev[i] = (mass[i] > 0.0).then_some(total[i] as f32);
                }
                evs = Some(per);
            } else {
                skipped_actor = true;
            }
            sigma = Some(sg);
        } else if live {
            if ev_others || node.kind == KIND_TERM_FOLD || node.kind == KIND_TERM_SHOWDOWN {
                let cfv = s.node_values(idx, p, rr, dealt, false);
                for i in 0..nh {
                    ev[i] = ev_of(cfv[i], i);
                }
            } else {
                skipped_others = true;
            }
        }
        let hands = (0..nh)
            .map(|i| {
                let h = &spot.hands[p][i];
                HandView {
                    combo: combo_to_string(h.c1, h.c2),
                    c1: h.c1,
                    c2: h.c2,
                    weight: h.weight,
                    reach: reach[p][i],
                    valid: mass[i],
                    eq: (!eq[i].is_nan()).then_some(eq[i]),
                    ev: ev[i],
                    strategy: sigma.as_ref().map(|sg| (0..na).map(|a| sg[a * nh + i]).collect()),
                    evs: evs.as_ref().map(|e| e[i].clone()),
                }
            })
            .collect();
        PlayerView { hands }
    });

    Ok(MwNodeView {
        node_type: node_type(node),
        street: node.street,
        board,
        pot: put.iter().sum(),
        put,
        live: std::array::from_fn(|k| node.live & (1 << k) != 0),
        player: actor.map(|k| k as u8),
        actions: action_views(s, idx),
        available_cards,
        players,
        locked: s.locks.contains_key(&idx),
        history: build_history(s, path)?,
        ev_skipped: if skipped_actor {
            Some("all")
        } else if skipped_others {
            Some("others")
        } else {
            None
        },
    })
}

/// Best response of player `p` from the node reached by `path`, against
/// the other two players' solved strategies: what each of p's hands makes
/// by playing perfectly from here on, next to what the solved strategy
/// makes. Same shape as the heads-up `ExploitView`.
pub fn exploit_view(s: &MwSolver, path: &[PathStep], p: usize) -> Result<ExploitView, String> {
    if p >= NP {
        return Err("exploiter must be 0, 1 or 2".to_string());
    }
    let spot = &*s.spot;
    let (idx, reach, dealt) = walk(s, path)?;
    let node = &spot.tree.nodes[idx as usize];
    let (ev_actor, ev_others) = ev_budget(s, node);
    if !(ev_actor && ev_others) {
        return Err("this spot is too big to work out the best response here; pick a later street".to_string());
    }
    let nh = spot.hands[p].len();
    let rr = [&reach[0][..], &reach[1][..], &reach[2][..]];
    let mut mass = vec![0f32; nh];
    compatible_mass(spot, p, rr, &mut mass);
    let is_actor = node.kind == KIND_ACTION && node.player as usize == p;
    let na = if node.kind == KIND_ACTION { node.num_children as usize } else { 0 };
    let lock = s.locks.get(&idx);

    let mut acfv: Vec<Vec<f32>> = Vec::new();
    let br_cfv: Vec<f32> = if is_actor {
        for a in 0..na {
            acfv.push(s.node_values(spot.tree.child(node, a), p, rr, dealt, true));
        }
        (0..nh)
            .map(|i| match lock {
                Some(l) => (0..na).map(|a| l[a * nh + i] * acfv[a][i]).sum(),
                None => (0..na).map(|a| acfv[a][i]).fold(f32::NEG_INFINITY, f32::max),
            })
            .collect()
    } else {
        s.node_values(idx, p, rr, dealt, true)
    };
    let cur_cfv = s.node_values(idx, p, rr, dealt, false);
    let put = node.put[p] as f64;
    let ev_of = |cfv: f32, i: usize| (mass[i] > 0.0).then(|| (cfv as f64 / mass[i] as f64 + put) as f32);

    let hands: Vec<ExploitHandView> = (0..nh)
        .map(|i| {
            let h = &spot.hands[p][i];
            let br_ev = ev_of(br_cfv[i], i);
            let cur_ev = ev_of(cur_cfv[i], i);
            let (br_strategy, evs) = if is_actor {
                let strat: Vec<f32> = match lock {
                    Some(l) => (0..na).map(|a| l[a * nh + i]).collect(),
                    None => {
                        let m = (0..na).map(|a| acfv[a][i]).fold(f32::NEG_INFINITY, f32::max);
                        let eps = (m.abs() * 1e-5).max(1e-5);
                        let win: Vec<bool> = (0..na).map(|a| m - acfv[a][i] <= eps).collect();
                        let w = win.iter().filter(|&&x| x).count().max(1) as f32;
                        (0..na).map(|a| if win[a] { 1.0 / w } else { 0.0 }).collect()
                    }
                };
                (Some(strat), Some((0..na).map(|a| ev_of(acfv[a][i], i)).collect()))
            } else {
                (None, None)
            };
            ExploitHandView {
                combo: combo_to_string(h.c1, h.c2),
                c1: h.c1,
                c2: h.c2,
                weight: h.weight,
                reach: reach[p][i],
                valid: mass[i],
                br_ev,
                cur_ev,
                gain: br_ev.zip(cur_ev).map(|(b, c)| b - c),
                br_strategy,
                evs,
            }
        })
        .collect();

    // Range averages weight by reach x valid, like every other range EV.
    let mut wsum = 0f64;
    let (mut b, mut c) = (0f64, 0f64);
    for h in &hands {
        if let (Some(be), Some(ce)) = (h.br_ev, h.cur_ev) {
            let w = h.reach as f64 * h.valid as f64;
            if w > 0.0 {
                wsum += w;
                b += w * be as f64;
                c += w * ce as f64;
            }
        }
    }
    let avg = |x: f64| (wsum > 1e-12).then(|| (x / wsum) as f32);
    Ok(ExploitView {
        node_type: node_type(node),
        exploiter: p as u8,
        player: (node.kind == KIND_ACTION).then_some(node.player),
        actions: action_views(s, idx),
        locked: lock.is_some(),
        hands,
        avg_br_ev: avg(b),
        avg_cur_ev: avg(c),
        avg_gain: avg(b - c),
    })
}
