//! Betting tree of a bomb pot for 2 to 9 players.
//!
//! Every player has paid the same ante and holds the same stack, so no side
//! pots can form: a player who is all-in has put in exactly what every other
//! live player has. Seats are in postflop action order (seat 0 acts first on
//! every street). The tree holds betting only; cards are dealt by the caller,
//! so a child on a later street simply means "the next card has come".
//!
//! The betting rules mirror `multiway::tree` (bet and raise menus, all-in
//! threshold, raise cap), so a two or three player bomb pot is the same game
//! the exact solvers build.

use crate::tree::{Action, BetSize, StreetSizing};
use serde::{Deserialize, Serialize};

pub const MAX_PLAYERS: usize = 9;
/// Most actions any node may offer.
pub const MAX_ACTIONS: usize = 8;

pub const KIND_ACTION: u8 = 0;
/// One live player left.
pub const KIND_FOLD: u8 = 1;
/// Showdown between two or more live players (river, or an all-in runout).
pub const KIND_SHOWDOWN: u8 = 2;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BpTreeConfig {
    pub players: usize,
    /// What each player pays before the flop. The pot starts at
    /// `players * ante`.
    pub ante: f64,
    /// Chips behind for each player after the ante.
    pub stack: f64,
    #[serde(default)]
    pub rake_pct: f64,
    #[serde(default)]
    pub rake_cap: f64,
    /// Bet and raise menus per street (flop, turn, river), shared by all
    /// seats. `donk` lists are ignored.
    pub sizing: [StreetSizing; 3],
    #[serde(default = "default_allin_threshold")]
    pub allin_threshold: f64,
    #[serde(default)]
    pub add_allin: bool,
    #[serde(default = "default_max_raises")]
    pub max_raises: u8,
}

fn default_allin_threshold() -> f64 {
    0.85
}
fn default_max_raises() -> u8 {
    2
}

impl BpTreeConfig {
    pub fn uniform(players: usize, ante: f64, stack: f64, bets: &[BetSize], raises: &[BetSize]) -> Self {
        let s = StreetSizing { bet: bets.to_vec(), raise: raises.to_vec(), donk: Vec::new() };
        BpTreeConfig {
            players,
            ante,
            stack,
            rake_pct: 0.0,
            rake_cap: 0.0,
            sizing: [s.clone(), s.clone(), s],
            allin_threshold: default_allin_threshold(),
            add_allin: false,
            max_raises: default_max_raises(),
        }
    }

    pub fn starting_pot(&self) -> f64 {
        self.players as f64 * self.ante
    }
}

#[derive(Debug, Clone)]
pub struct BpNode {
    pub kind: u8,
    /// Action node: the seat to act.
    pub player: u8,
    pub street: u8,
    pub num_children: u8,
    /// Bitmask of seats that have not folded.
    pub live: u16,
    pub children_start: u32,
    /// Action node: first slot of this node in the actor's strategy arena
    /// (set by the solver once the hand grouping is known).
    pub info_offset: u64,
    /// Whole pot, antes included.
    pub pot: f32,
    /// What the winners share: the pot after rake.
    pub pot_net: f32,
}

#[derive(Debug, Clone)]
pub struct BpTree {
    pub config: BpTreeConfig,
    pub root_street: u8,
    pub nodes: Vec<BpNode>,
    pub children: Vec<u32>,
    /// One entry per child of an action node, in child order.
    pub actions: Vec<Action>,
    /// Each seat's total contribution at every node, antes included
    /// (`players` entries per node).
    pub puts: Vec<f32>,
    /// Action nodes per street.
    pub action_nodes: [u64; 3],
}

impl BpTree {
    pub fn players(&self) -> usize {
        self.config.players
    }

    #[inline]
    pub fn child(&self, node: &BpNode, i: usize) -> u32 {
        self.children[node.children_start as usize + i]
    }

    #[inline]
    pub fn put(&self, node_idx: u32, p: usize) -> f32 {
        self.puts[node_idx as usize * self.config.players + p]
    }

    pub fn node_actions(&self, node: &BpNode) -> &[Action] {
        let s = node.children_start as usize;
        &self.actions[s..s + node.num_children as usize]
    }
}

#[derive(Clone)]
struct St {
    street: u8,
    to_act: u8,
    put: [f64; MAX_PLAYERS],
    street_bet: [f64; MAX_PLAYERS],
    last_increment: f64,
    num_raises: u8,
    acted: u16,
    live: u16,
    allin: u16,
}

const EPS: f64 = 1e-9;

pub struct BpTreeBuilder<'a> {
    cfg: &'a BpTreeConfig,
    n: usize,
    max_nodes: usize,
    nodes: Vec<BpNode>,
    children: Vec<u32>,
    actions: Vec<Action>,
    puts: Vec<f32>,
    action_nodes: [u64; 3],
}

fn dedupe(v: &mut Vec<f64>) {
    v.sort_by(f64::total_cmp);
    v.dedup_by(|a, b| (*a - *b).abs() < 1e-6);
}

impl<'a> BpTreeBuilder<'a> {
    pub fn build(cfg: &'a BpTreeConfig, root_street: u8, max_nodes: usize) -> Result<BpTree, String> {
        let n = cfg.players;
        if !(2..=MAX_PLAYERS).contains(&n) {
            return Err(format!("players must be 2 to {MAX_PLAYERS}"));
        }
        if !(cfg.ante > 0.0 && cfg.ante.is_finite()) {
            return Err("ante must be a positive finite number".into());
        }
        if !(cfg.stack > 0.0 && cfg.stack.is_finite()) {
            return Err("stack must be a positive finite number".into());
        }
        if !(0.0..1.0).contains(&cfg.rake_pct) || cfg.rake_cap < 0.0 {
            return Err("rake_pct must be a fraction in [0, 1) and rake_cap >= 0".into());
        }
        if root_street > 2 {
            return Err("root street must be flop, turn or river".into());
        }
        for (st, s) in cfg.sizing.iter().enumerate() {
            for (list, what) in [(&s.bet, "bet"), (&s.raise, "raise")] {
                for size in list {
                    let v = match size {
                        BetSize::PotPct(p) => *p,
                        BetSize::PrevMult(m) => *m,
                        BetSize::AllIn => continue,
                    };
                    if !v.is_finite() || v <= 0.0 {
                        return Err(format!("street {st} {what}: size {v} must be a positive finite number"));
                    }
                }
            }
            if s.bet.iter().any(|b| matches!(b, BetSize::PrevMult(_))) {
                return Err(format!("street {st}: 'x' sizes are raise-only"));
            }
        }
        let mut b = BpTreeBuilder {
            cfg,
            n,
            max_nodes,
            nodes: Vec::new(),
            children: Vec::new(),
            actions: Vec::new(),
            puts: Vec::new(),
            action_nodes: [0; 3],
        };
        let mut put = [0.0; MAX_PLAYERS];
        for p in put.iter_mut().take(n) {
            *p = cfg.ante;
        }
        let st = St {
            street: root_street,
            to_act: 0,
            put,
            street_bet: [0.0; MAX_PLAYERS],
            last_increment: 0.0,
            num_raises: 0,
            acted: 0,
            live: (1u16 << n) - 1,
            allin: 0,
        };
        b.action_node(st)?;
        Ok(BpTree {
            config: cfg.clone(),
            root_street,
            nodes: b.nodes,
            children: b.children,
            actions: b.actions,
            puts: b.puts,
            action_nodes: b.action_nodes,
        })
    }

    fn behind(&self, st: &St, p: usize) -> f64 {
        self.cfg.stack - (st.put[p] - self.cfg.ante)
    }

    fn can_act(st: &St, p: usize) -> bool {
        st.live & (1 << p) != 0 && st.allin & (1 << p) == 0
    }

    fn high_bet(&self, st: &St) -> f64 {
        (0..self.n).filter(|&i| st.live & (1 << i) != 0).map(|i| st.street_bet[i]).fold(0.0, f64::max)
    }

    fn legal_actions(&self, st: &St) -> Vec<Action> {
        let me = st.to_act as usize;
        let hi = self.high_bet(st);
        let facing = hi - st.street_bet[me];
        let behind = self.behind(st, me);
        let others_can_act = (0..self.n).any(|i| i != me && Self::can_act(st, i));
        let cover = (0..self.n)
            .filter(|&i| i != me && st.live & (1 << i) != 0)
            .map(|i| st.street_bet[i] + if st.allin & (1 << i) != 0 { 0.0 } else { self.behind(st, i) })
            .fold(0.0, f64::max);
        let own_max = st.street_bet[me] + behind;
        let max_to = own_max.min(cover.max(hi));
        let sizing = &self.cfg.sizing[st.street as usize];
        let pot_now: f64 = st.put[..self.n].iter().sum();
        let mut out = Vec::new();
        if facing > EPS {
            out.push(Action::Fold);
            out.push(Action::Call(hi.min(own_max)));
            let can_raise = behind > facing + EPS
                && st.num_raises < self.cfg.max_raises
                && others_can_act
                && max_to > hi + EPS;
            if can_raise {
                let pot_after_call = pot_now + facing;
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
                let mut cands = Vec::new();
                for s in &sizing.bet {
                    match s {
                        BetSize::PotPct(p) => cands.push(p / 100.0 * pot_now),
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

    fn push(&mut self, kind: u8, st: &St, num_children: u8) -> Result<u32, String> {
        if self.nodes.len() >= self.max_nodes {
            return Err(format!(
                "tree too large: over the budget of {} nodes; reduce sizes or raises",
                self.max_nodes
            ));
        }
        let pot: f64 = st.put[..self.n].iter().sum();
        let mut rake = pot * self.cfg.rake_pct;
        if self.cfg.rake_cap > 0.0 {
            rake = rake.min(self.cfg.rake_cap);
        }
        self.nodes.push(BpNode {
            kind,
            player: st.to_act,
            street: st.street,
            num_children,
            live: st.live,
            children_start: 0,
            info_offset: 0,
            pot: pot as f32,
            pot_net: (pot - rake) as f32,
        });
        self.puts.extend(st.put[..self.n].iter().map(|&x| x as f32));
        Ok((self.nodes.len() - 1) as u32)
    }

    fn action_node(&mut self, st: St) -> Result<u32, String> {
        let acts = self.legal_actions(&st);
        let na = acts.len();
        if na == 0 || na > MAX_ACTIONS {
            return Err(format!("a node offers {na} actions; the most allowed is {MAX_ACTIONS}"));
        }
        let idx = self.push(KIND_ACTION, &st, na as u8)?;
        self.action_nodes[st.street as usize] += 1;
        let mut kids = Vec::with_capacity(na);
        for a in &acts {
            kids.push(self.apply(&st, *a)?);
        }
        let cs = self.children.len();
        self.children.extend(kids);
        // `actions` runs parallel to `children`.
        self.actions.resize(cs, Action::Check);
        self.actions.extend(acts.iter().copied());
        self.nodes[idx as usize].children_start = cs as u32;
        Ok(idx)
    }

    fn apply(&mut self, st0: &St, a: Action) -> Result<u32, String> {
        let mut st = st0.clone();
        let me = st.to_act as usize;
        match a {
            Action::Fold => {
                st.live &= !(1 << me);
                st.acted |= 1 << me;
                if st.live.count_ones() == 1 {
                    return self.push(KIND_FOLD, &st, 0);
                }
            }
            Action::Check => st.acted |= 1 << me,
            Action::Call(to) => {
                st.put[me] += to - st.street_bet[me];
                st.street_bet[me] = to;
                st.acted |= 1 << me;
                if self.behind(&st, me) <= EPS {
                    st.allin |= 1 << me;
                }
            }
            Action::Bet(to) | Action::Raise(to) => {
                let hi = self.high_bet(&st);
                st.last_increment = st.last_increment.max(to - hi);
                if matches!(a, Action::Raise(_)) {
                    st.num_raises += 1;
                }
                st.put[me] += to - st.street_bet[me];
                st.street_bet[me] = to;
                st.acted = 1 << me;
                if self.behind(&st, me) <= EPS {
                    st.allin |= 1 << me;
                }
            }
        }
        if self.street_over(&st) {
            return self.street_end(st);
        }
        match self.next_actor(&st, me) {
            Some(nx) => {
                st.to_act = nx as u8;
                self.action_node(st)
            }
            None => self.street_end(st),
        }
    }

    fn street_over(&self, st: &St) -> bool {
        let hi = self.high_bet(st);
        (0..self.n)
            .all(|i| !Self::can_act(st, i) || (st.acted & (1 << i) != 0 && (st.street_bet[i] - hi).abs() < 1e-7))
    }

    fn next_actor(&self, st: &St, from: usize) -> Option<usize> {
        (1..=self.n).map(|k| (from + k) % self.n).find(|&j| Self::can_act(st, j))
    }

    fn street_end(&mut self, mut st: St) -> Result<u32, String> {
        let active = (0..self.n).filter(|&i| Self::can_act(&st, i)).count();
        if st.street == 2 || active <= 1 {
            // River showdown, or everyone but at most one player is all-in
            // and the remaining cards simply run out.
            return self.push(KIND_SHOWDOWN, &st, 0);
        }
        st.street += 1;
        st.street_bet = [0.0; MAX_PLAYERS];
        st.last_increment = 0.0;
        st.num_raises = 0;
        st.acted = 0;
        st.to_act = self.next_actor(&st, self.n - 1).unwrap() as u8;
        self.action_node(st)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tree::parse_sizes;

    #[test]
    fn three_player_tree_matches_the_exact_solver_tree() {
        use crate::multiway::tree::{MwTreeBuilder, MwTreeConfig, KIND_ACTION as MW_ACTION, KIND_CHANCE};
        for (bets, raises, max_raises, add_allin) in
            [("66", "100", 2u8, false), ("33,100", "60", 1, false), ("50", "2.5x", 2, true)]
        {
            let b = parse_sizes(bets).unwrap();
            let r = parse_sizes(raises).unwrap();
            let mut mw = MwTreeConfig::uniform(6.0, 98.0, &b, &r);
            mw.max_raises = max_raises;
            mw.add_allin = add_allin;
            // River root: the exact tree has no chance nodes, so node counts
            // must agree one for one.
            let board = crate::cards::parse_cards("AsKd7c4h2s").unwrap();
            let mask = board.iter().fold(0u64, |m, &c| m | 1u64 << c);
            let exact = MwTreeBuilder::build(&mw, mask, 2, [100, 100, 100], None).unwrap();
            let mut cfg = BpTreeConfig::uniform(3, 2.0, 98.0, &b, &r);
            cfg.max_raises = max_raises;
            cfg.add_allin = add_allin;
            let ours = BpTreeBuilder::build(&cfg, 2, usize::MAX).unwrap();
            assert_eq!(ours.nodes.len(), exact.nodes.len(), "river tree size for {bets} / {raises}");
            for (a, e) in ours.nodes.iter().zip(&exact.nodes) {
                assert_eq!(a.num_children, e.num_children);
                assert_eq!(a.live as u8, e.live);
            }
            // Turn root: the exact tree repeats the river subtree under every
            // river card. Count action nodes per street on one card's branch.
            let board = crate::cards::parse_cards("AsKd7c4h").unwrap();
            let mask = board.iter().fold(0u64, |m, &c| m | 1u64 << c);
            let exact = MwTreeBuilder::build(&mw, mask, 1, [100, 100, 100], None).unwrap();
            let ours = BpTreeBuilder::build(&cfg, 1, usize::MAX).unwrap();
            let turn_exact = exact.nodes.iter().filter(|n| n.kind == MW_ACTION && n.street == 1).count() as u64;
            let river_exact = exact.nodes.iter().filter(|n| n.kind == MW_ACTION && n.street == 2).count() as u64;
            let chance = exact.nodes.iter().filter(|n| n.kind == KIND_CHANCE).count() as u64;
            assert!(chance > 0);
            assert_eq!(ours.action_nodes[1], turn_exact);
            assert_eq!(ours.action_nodes[2] * 48, river_exact);
        }
    }

    #[test]
    fn live_players_have_matched_at_every_showdown() {
        let b = parse_sizes("33,100").unwrap();
        let r = parse_sizes("100").unwrap();
        let cfg = BpTreeConfig::uniform(6, 2.0, 98.0, &b, &r);
        let t = BpTreeBuilder::build(&cfg, 0, usize::MAX).unwrap();
        let mut showdowns = 0;
        for (i, n) in t.nodes.iter().enumerate() {
            if n.kind != KIND_SHOWDOWN {
                continue;
            }
            showdowns += 1;
            let live: Vec<f32> = (0..6).filter(|&p| n.live & (1 << p) != 0).map(|p| t.put(i as u32, p)).collect();
            assert!(live.len() >= 2);
            assert!(live.iter().all(|&x| (x - live[0]).abs() < 1e-4), "side pot at node {i}");
        }
        assert!(showdowns > 1000);
    }
}
