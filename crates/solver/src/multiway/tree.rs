//! Three-player postflop game tree.
//!
//! Players are indexed in postflop action order: 0 acts first on every
//! street, 2 acts last. A fold with two players left continues the hand
//! heads-up inside the same tree; the folder's reach freezes and only
//! removes cards. Stacks may differ: a short all-in creates side pots, which
//! terminal payoffs resolve from each player's total contribution.

use crate::tree::{Action, BetSize, StreetSizing, SENTINEL};
use serde::{Deserialize, Serialize};

pub const NP: usize = 3;

pub const KIND_ACTION: u8 = 0;
pub const KIND_CHANCE: u8 = 1;
/// One live player left; everyone else folded.
pub const KIND_TERM_FOLD: u8 = 2;
/// River showdown (or all-in runout) between two or three live players.
pub const KIND_TERM_SHOWDOWN: u8 = 3;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MwTreeConfig {
    /// Chips in the pot at the root (split equally into the three players'
    /// contributions; dead money therefore sits in the main pot).
    pub starting_pot: f64,
    /// Chips behind for each player at the root, in action order.
    pub stacks: [f64; NP],
    #[serde(default)]
    pub rake_pct: f64,
    #[serde(default)]
    pub rake_cap: f64,
    /// Sizing per player (action order) and street (flop, turn, river).
    /// `donk` lists are ignored: every player leads with `bet`.
    pub sizing: [[StreetSizing; 3]; NP],
    #[serde(default = "default_allin_threshold")]
    pub allin_threshold: f64,
    #[serde(default)]
    pub add_allin: bool,
    /// Raises per street (an all-in still ends the action anyway).
    #[serde(default = "default_max_raises")]
    pub max_raises: u8,
}

fn default_allin_threshold() -> f64 {
    0.85
}
fn default_max_raises() -> u8 {
    2
}

impl MwTreeConfig {
    /// Same bet and raise menus for every player on every street.
    pub fn uniform(starting_pot: f64, stack: f64, bets: &[BetSize], raises: &[BetSize]) -> Self {
        let s = StreetSizing { bet: bets.to_vec(), raise: raises.to_vec(), donk: Vec::new() };
        MwTreeConfig {
            starting_pot,
            stacks: [stack; NP],
            rake_pct: 0.0,
            rake_cap: 0.0,
            sizing: std::array::from_fn(|_| std::array::from_fn(|_| s.clone())),
            allin_threshold: default_allin_threshold(),
            add_allin: false,
            max_raises: default_max_raises(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MwNode {
    pub kind: u8,
    /// Action node: actor. Unused elsewhere.
    pub player: u8,
    /// Street of the node (chance nodes: the street dealt into).
    pub street: u8,
    pub num_children: u8,
    /// Bitmask of players who have not folded.
    pub live: u8,
    pub children_start: u32,
    pub actions_start: u32,
    pub data_offset: u64,
    /// Each player's total contribution (root share included).
    pub put: [f32; NP],
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MwTree {
    pub config: MwTreeConfig,
    pub root_street: u8,
    pub nodes: Vec<MwNode>,
    /// Action nodes: one entry per action. Chance nodes: 52 slots by card.
    pub children: Vec<u32>,
    pub actions: Vec<Action>,
    /// Arena elements per player (sum of actions x hands over its nodes).
    pub data_size: [u64; NP],
}

impl MwTree {
    pub fn bytes(&self) -> u64 {
        (self.nodes.len() * std::mem::size_of::<MwNode>()
            + self.children.len() * 4
            + self.actions.len() * std::mem::size_of::<Action>()) as u64
    }

    pub fn child(&self, node: &MwNode, i: usize) -> u32 {
        self.children[node.children_start as usize + i]
    }

    pub fn node_actions(&self, node: &MwNode) -> &[Action] {
        let s = node.actions_start as usize;
        &self.actions[s..s + node.num_children as usize]
    }

    /// Initial contribution of each player.
    pub fn root_put(&self) -> f64 {
        self.config.starting_pot / NP as f64
    }
}

#[derive(Clone)]
struct St {
    street: u8,
    to_act: u8,
    put: [f64; NP],
    street_bet: [f64; NP],
    last_increment: f64,
    num_raises: u8,
    acted: [bool; NP],
    live: u8,
    allin: u8,
    /// Cards dealt below the root board (skip their chance slots).
    dealt: u64,
}

pub struct MwTreeBuilder<'a> {
    cfg: &'a MwTreeConfig,
    board_mask: u64,
    max_nodes: Option<usize>,
    nodes: Vec<MwNode>,
    children: Vec<u32>,
    actions: Vec<Action>,
    num_hands: [u64; NP],
    data_size: [u64; NP],
}

const EPS: f64 = 1e-9;

fn validate_sizes(list: &[BetSize], what: &str) -> Result<(), String> {
    for s in list {
        let v = match s {
            BetSize::PotPct(p) => *p,
            BetSize::PrevMult(m) => *m,
            BetSize::AllIn => continue,
        };
        if !v.is_finite() || v <= 0.0 {
            return Err(format!("{what}: size {v} must be a positive finite number"));
        }
    }
    Ok(())
}

impl<'a> MwTreeBuilder<'a> {
    pub fn build(
        cfg: &'a MwTreeConfig,
        board_mask: u64,
        root_street: u8,
        num_hands: [usize; NP],
        max_nodes: Option<usize>,
    ) -> Result<MwTree, String> {
        if !(cfg.starting_pot > 0.0 && cfg.starting_pot.is_finite()) {
            return Err("starting pot must be a positive finite number".into());
        }
        for (i, s) in cfg.stacks.iter().enumerate() {
            if !(*s > 0.0 && s.is_finite()) {
                return Err(format!("stack of player {i} must be a positive finite number"));
            }
        }
        if !(0.0..1.0).contains(&cfg.rake_pct) || cfg.rake_cap < 0.0 {
            return Err("rake_pct must be a fraction in [0, 1) and rake_cap >= 0".into());
        }
        for (p, streets) in cfg.sizing.iter().enumerate() {
            for (st, s) in streets.iter().enumerate() {
                validate_sizes(&s.bet, &format!("player {p} street {st} bet"))?;
                validate_sizes(&s.raise, &format!("player {p} street {st} raise"))?;
                if s.bet.iter().any(|b| matches!(b, BetSize::PrevMult(_))) {
                    return Err(format!("player {p} street {st}: 'x' sizes are raise-only"));
                }
            }
        }
        let mut b = MwTreeBuilder {
            cfg,
            board_mask,
            max_nodes,
            nodes: Vec::new(),
            children: Vec::new(),
            actions: Vec::new(),
            num_hands: num_hands.map(|n| n as u64),
            data_size: [0; NP],
        };
        let share = cfg.starting_pot / NP as f64;
        let st = St {
            street: root_street,
            to_act: 0,
            put: [share; NP],
            street_bet: [0.0; NP],
            last_increment: 0.0,
            num_raises: 0,
            acted: [false; NP],
            live: (1 << NP) - 1,
            allin: 0,
            dealt: 0,
        };
        b.action_node(st)?;
        Ok(MwTree {
            config: cfg.clone(),
            root_street,
            nodes: b.nodes,
            children: b.children,
            actions: b.actions,
            data_size: b.data_size,
        })
    }

    fn check_budget(&self) -> Result<(), String> {
        match self.max_nodes {
            Some(cap) if self.nodes.len() >= cap => Err(format!(
                "tree too large: over the budget of {cap} nodes; reduce sizes, raises or streets"
            )),
            _ => Ok(()),
        }
    }

    fn behind(&self, st: &St, p: usize) -> f64 {
        self.cfg.stacks[p] - (st.put[p] - self.cfg.starting_pot / NP as f64)
    }

    fn can_act(st: &St, p: usize) -> bool {
        st.live & (1 << p) != 0 && st.allin & (1 << p) == 0
    }

    fn legal_actions(&self, st: &St) -> Vec<Action> {
        let me = st.to_act as usize;
        let hi = (0..NP).filter(|&i| st.live & (1 << i) != 0).map(|i| st.street_bet[i]).fold(0.0, f64::max);
        let facing = hi - st.street_bet[me];
        let behind = self.behind(st, me);
        // The most any other player who can still act (or is live) could match.
        let others_can_act = (0..NP).any(|i| i != me && Self::can_act(st, i));
        let cover = (0..NP)
            .filter(|&i| i != me && st.live & (1 << i) != 0)
            .map(|i| st.street_bet[i] + if st.allin & (1 << i) != 0 { 0.0 } else { self.behind(st, i) })
            .fold(0.0, f64::max);
        let own_max = st.street_bet[me] + behind;
        let max_to = own_max.min(cover.max(hi));
        let sizing = &self.cfg.sizing[me][st.street as usize];
        let mut out = Vec::new();
        if facing > EPS {
            out.push(Action::Fold);
            out.push(Action::Call(hi.min(own_max)));
            let can_raise = behind > facing + EPS
                && st.num_raises < self.cfg.max_raises
                && others_can_act
                && max_to > hi + EPS;
            if can_raise {
                let pot_after_call: f64 = st.put.iter().sum::<f64>() + facing;
                let mut cands = Vec::new();
                for s in &sizing.raise {
                    cands.push(match s {
                        BetSize::PotPct(p) => hi + p / 100.0 * pot_after_call,
                        BetSize::PrevMult(m) => hi * m,
                        BetSize::AllIn => max_to,
                    });
                }
                if self.cfg.add_allin {
                    cands.push(max_to);
                }
                let min_to = hi + st.last_increment.max(EPS);
                let mut tos = Vec::new();
                for mut to in cands {
                    if to < min_to {
                        to = min_to;
                    }
                    if to >= max_to - EPS || to >= self.cfg.allin_threshold * own_max - EPS {
                        to = max_to;
                    }
                    if to > hi + EPS {
                        tos.push(to);
                    }
                }
                dedupe(&mut tos);
                out.extend(tos.into_iter().map(Action::Raise));
            }
        } else {
            out.push(Action::Check);
            if behind > EPS && others_can_act && max_to > EPS {
                let pot: f64 = st.put.iter().sum();
                let mut cands = Vec::new();
                for s in &sizing.bet {
                    match s {
                        BetSize::PotPct(p) => cands.push(p / 100.0 * pot),
                        BetSize::AllIn => cands.push(max_to),
                        BetSize::PrevMult(_) => {}
                    }
                }
                if self.cfg.add_allin {
                    cands.push(max_to);
                }
                let mut tos = Vec::new();
                for mut to in cands {
                    if to <= EPS {
                        continue;
                    }
                    if to >= max_to - EPS || to >= self.cfg.allin_threshold * own_max - EPS {
                        to = max_to;
                    }
                    tos.push(to);
                }
                dedupe(&mut tos);
                out.extend(tos.into_iter().map(Action::Bet));
            }
        }
        out
    }

    fn push(&mut self, n: MwNode) -> u32 {
        self.nodes.push(n);
        (self.nodes.len() - 1) as u32
    }

    fn action_node(&mut self, st: St) -> Result<u32, String> {
        self.check_budget()?;
        let acts = self.legal_actions(&st);
        let n = acts.len();
        if n == 0 || n > 250 {
            return Err(format!("invalid action count {n} during tree build"));
        }
        let me = st.to_act as usize;
        let actions_start = self.actions.len() as u32;
        self.actions.extend(acts.iter().copied());
        let data_offset = self.data_size[me];
        self.data_size[me] += n as u64 * self.num_hands[me];
        let idx = self.push(MwNode {
            kind: KIND_ACTION,
            player: st.to_act,
            street: st.street,
            num_children: n as u8,
            live: st.live,
            children_start: 0,
            actions_start,
            data_offset,
            put: st.put.map(|x| x as f32),
        });
        let mut kids = Vec::with_capacity(n);
        for a in &acts {
            kids.push(self.apply(&st, *a)?);
        }
        let cs = self.children.len() as u32;
        self.children.extend(kids);
        self.nodes[idx as usize].children_start = cs;
        Ok(idx)
    }

    fn apply(&mut self, st0: &St, a: Action) -> Result<u32, String> {
        let mut st = st0.clone();
        let me = st.to_act as usize;
        match a {
            Action::Fold => {
                st.live &= !(1 << me);
                st.acted[me] = true;
                if st.live.count_ones() == 1 {
                    return Ok(self.terminal(KIND_TERM_FOLD, &st));
                }
            }
            Action::Check => st.acted[me] = true,
            Action::Call(to) => {
                st.put[me] += to - st.street_bet[me];
                st.street_bet[me] = to;
                st.acted[me] = true;
                if self.behind(&st, me) <= EPS {
                    st.allin |= 1 << me;
                }
            }
            Action::Bet(to) | Action::Raise(to) => {
                let hi = (0..NP).filter(|&i| st.live & (1 << i) != 0).map(|i| st.street_bet[i]).fold(0.0, f64::max);
                st.last_increment = st.last_increment.max(to - hi);
                if matches!(a, Action::Raise(_)) {
                    st.num_raises += 1;
                }
                st.put[me] += to - st.street_bet[me];
                st.street_bet[me] = to;
                st.acted = [false; NP];
                st.acted[me] = true;
                if self.behind(&st, me) <= EPS {
                    st.allin |= 1 << me;
                }
            }
        }
        if self.street_over(&st) {
            return self.street_end(st);
        }
        match self.next_actor(&st, me) {
            Some(n) => {
                st.to_act = n as u8;
                self.action_node(st)
            }
            None => self.street_end(st),
        }
    }

    fn street_over(&self, st: &St) -> bool {
        let hi = (0..NP).filter(|&i| st.live & (1 << i) != 0).map(|i| st.street_bet[i]).fold(0.0, f64::max);
        (0..NP).all(|i| !Self::can_act(st, i) || (st.acted[i] && (st.street_bet[i] - hi).abs() < 1e-7))
    }

    fn next_actor(&self, st: &St, from: usize) -> Option<usize> {
        (1..=NP).map(|k| (from + k) % NP).find(|&j| Self::can_act(st, j))
    }

    fn street_end(&mut self, st: St) -> Result<u32, String> {
        if st.street == 2 {
            return Ok(self.terminal(KIND_TERM_SHOWDOWN, &st));
        }
        self.check_budget()?;
        let active = (0..NP).filter(|&i| Self::can_act(&st, i)).count();
        let next = st.street + 1;
        let idx = self.push(MwNode {
            kind: KIND_CHANCE,
            player: 0,
            street: next,
            num_children: 52,
            live: st.live,
            children_start: 0,
            actions_start: 0,
            data_offset: 0,
            put: st.put.map(|x| x as f32),
        });
        let mut kids = vec![SENTINEL; 52];
        for card in 0..52u8 {
            let m = 1u64 << card;
            if (self.board_mask | st.dealt) & m != 0 {
                continue;
            }
            let mut cs = st.clone();
            cs.street = next;
            cs.street_bet = [0.0; NP];
            cs.last_increment = 0.0;
            cs.num_raises = 0;
            cs.acted = [false; NP];
            cs.dealt |= m;
            kids[card as usize] = if active <= 1 {
                // All-in runout: no more decisions.
                self.street_end(cs)?
            } else {
                cs.to_act = self.next_actor(&cs, NP - 1).unwrap() as u8;
                self.action_node(cs)?
            };
        }
        let start = self.children.len() as u32;
        self.children.extend(kids);
        self.nodes[idx as usize].children_start = start;
        Ok(idx)
    }

    fn terminal(&mut self, kind: u8, st: &St) -> u32 {
        self.push(MwNode {
            kind,
            player: 0,
            street: st.street,
            num_children: 0,
            live: st.live,
            children_start: 0,
            actions_start: 0,
            data_offset: 0,
            put: st.put.map(|x| x as f32),
        })
    }
}

fn dedupe(v: &mut Vec<f64>) {
    v.sort_by(f64::total_cmp);
    v.dedup_by(|a, b| (*a - *b).abs() < 1e-6);
}

/// Payoff table for player `p` at a terminal: `pay[cq][cr]` is p's net chip
/// result given each opponent's hand relative to p's — 0 = the opponent's
/// hand is weaker (p beats it), 1 = tied, 2 = stronger. `q < r` are the
/// other two players. Folded players' categories do not matter (their rows/columns are
/// constant). Side pots are resolved layer by layer from the contributions;
/// rake is charged on the contested pot (uncalled excess is returned) and
/// taken from each contested layer in proportion to its size.
pub fn payoff_table(node: &MwNode, p: usize, rake_pct: f64, rake_cap: f64) -> [[f64; 3]; 3] {
    let put = node.put.map(|x| x as f64);
    let live = node.live;
    let (q, r) = others(p);
    // Distinct contribution levels, ascending.
    let mut levels: Vec<f64> = put.to_vec();
    levels.sort_by(f64::total_cmp);
    levels.dedup_by(|a, b| (*a - *b).abs() < 1e-7);
    // Layers: (amount, contenders mask)
    let mut layers: Vec<(f64, u8)> = Vec::new();
    let mut prev = 0.0;
    for &lv in &levels {
        let payers = (0..NP).filter(|&i| put[i] >= lv - 1e-7).count() as f64;
        let amount = (lv - prev) * payers;
        let mut contenders = 0u8;
        for i in 0..NP {
            if live & (1 << i) != 0 && put[i] >= lv - 1e-7 {
                contenders |= 1 << i;
            }
        }
        if amount > 0.0 {
            layers.push((amount, contenders));
        }
        prev = lv;
    }
    // Contested = layers with 2+ payers and at least one contender; a layer
    // only one player paid into (with nobody else live in it) is returned.
    let total: f64 = layers.iter().map(|l| l.0).sum();
    let returned: f64 = layers
        .iter()
        .zip(levels.iter())
        .filter(|((_, c), &lv)| c.count_ones() <= 1 && (0..NP).filter(|&i| put[i] >= lv - 1e-7).count() == 1)
        .map(|(l, _)| l.0)
        .sum();
    let contested = total - returned;
    let mut rake = rake_pct * contested;
    if rake_cap > 0.0 {
        rake = rake.min(rake_cap);
    }
    let rake_frac = if contested > 0.0 { rake / contested } else { 0.0 };
    let mut pay = [[0.0; 3]; 3];
    for cq in 0..3 {
        for cr in 0..3 {
            let mut won = 0.0;
            for (k, &(amount, cont)) in layers.iter().enumerate() {
                let lv = levels[k];
                let single = (0..NP).filter(|&i| put[i] >= lv - 1e-7).count() == 1 && cont.count_ones() <= 1;
                let net = if single { amount } else { amount * (1.0 - rake_frac) };
                if cont & (1 << p) == 0 {
                    continue;
                }
                // p contends: is p best among contenders, and with how many ties?
                let mut best = true;
                let mut ties = 1.0;
                for (o, c) in [(q, cq), (r, cr)] {
                    if cont & (1 << o) == 0 {
                        continue;
                    }
                    match c {
                        0 => {}
                        1 => ties += 1.0,
                        _ => best = false,
                    }
                }
                if best {
                    won += net / ties;
                }
            }
            pay[cq][cr] = won - put[p];
        }
    }
    pay
}

/// The two players other than `p`, ascending.
#[inline]
pub fn others(p: usize) -> (usize, usize) {
    match p {
        0 => (1, 2),
        1 => (0, 2),
        _ => (0, 1),
    }
}
