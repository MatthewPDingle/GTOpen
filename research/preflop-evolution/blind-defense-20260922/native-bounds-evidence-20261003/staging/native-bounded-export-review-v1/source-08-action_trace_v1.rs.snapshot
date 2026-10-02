//! Conditional full-action values at each physical-deal decision.
//! Policies still receive only the existing observable key, never hidden cards.
use super::poker_reference_v1::{key, Game, Key};
use super::state::State;
use std::collections::BTreeMap;

pub struct Row {
    pub actor: usize,
    pub n: usize,
    pub actions: [[f64; 2]; 4],
    pub value: [f64; 2],
    pub reach: f64,
}

pub struct Trace<'a, F: Fn(Key, usize) -> [f64; 4]> {
    pub game: &'a Game,
    pub policy: &'a F,
    pub deal: &'a [u8; 9],
    pub equity: f64,
    pub winner: i32,
    pub rows: BTreeMap<Key, Row>,
}

impl<'a, F: Fn(Key, usize) -> [f64; 4]> Trace<'a, F> {
    pub fn new(game: &'a Game, policy: &'a F, deal: &'a [u8; 9], equity: f64) -> Self {
        assert!(equity.is_finite() && (0. ..=1.).contains(&equity));
        let ranks: [u32; 2] = std::array::from_fn(|p| {
            let mut cards = [0; 7];
            cards[..2].copy_from_slice(&deal[p*2..p*2+2]);
            cards[2..].copy_from_slice(&deal[4..]);
            solver::evaluator::evaluate7(&cards)
        });
        Self { game, policy, deal, equity,
            winner: if ranks[0] == ranks[1] { -1 } else { (ranks[1] > ranks[0]) as i32 },
            rows: BTreeMap::new() }
    }

    fn record(&mut self, k: Key, actor: usize, n: usize, p: [f64; 4],
              actions: [[f64; 2]; 4], reach: f64) -> [f64; 2] {
        let value = std::array::from_fn(|i| (0..n).map(|a| p[a]*actions[a][i]).sum());
        assert!(value.iter().all(|x: &f64| x.is_finite()));
        assert!(self.rows.insert(k, Row { actor, n, actions, value, reach }).is_none(),
                "A physical-deal decision must have a unique history key");
        value
    }

    pub fn pre(&mut self, node: usize, reach: f64) -> [f64; 2] {
        let g = self.game;
        match g.kinds[node] {
            1 => [g.offsets[node*2], g.offsets[node*2+1]],
            2 => self.post(node, State::root(&g.configs[node]), 1, reach),
            3 => {
                let cfg = &g.configs[node];
                let amount = cfg.starting_pot/2.;
                let gross = cfg.rake_pct*2.*amount;
                let rake = if cfg.rake_cap > 0. { gross.min(cfg.rake_cap) } else { gross };
                std::array::from_fn(|i| g.offsets[node*2+i]
                    + (if i == 0 { self.equity } else { 1.-self.equity })*(2.*amount-rake)-amount)
            }
            0 => {
                let actor = g.actors[node] as usize;
                let n = g.arities[node] as usize;
                let k = key(self.deal, actor, Some(node), 0, 0, 0);
                let p = (self.policy)(k, n);
                let mut actions = [[0.; 2]; 4];
                // Traverse every action, including zero-policy actions, for conditional targets.
                for a in 0..n { actions[a] = self.pre(g.children[node*4+a] as usize, reach*p[a]); }
                self.record(k, actor, n, p, actions, reach)
            }
            _ => panic!("Invalid preflop node"),
        }
    }

    fn post(&mut self, branch: usize, s: State, history: u64, reach: f64) -> [f64; 2] {
        let cfg = &self.game.configs[branch];
        if s.kind == 1 { return self.post(branch, s.deal(), (history<<3)|5, reach); }
        if s.kind >= 2 {
            let v = s.payouts(cfg);
            return std::array::from_fn(|i| self.game.offsets[branch*2+i] +
                if s.kind == 2 { if i == s.player as usize { v[1] } else { v[0] } }
                else if self.winner < 0 { v[2] }
                else if i == self.winner as usize { v[0] } else { v[1] });
        }
        let legal = s.actions(cfg);
        let n = legal.len();
        let actor = s.player as usize;
        let k = key(self.deal, actor, None, branch, s.street as usize, history);
        let p = (self.policy)(k, n);
        let mut actions = [[0.; 2]; 4];
        for a in 0..n {
            actions[a] = self.post(branch, s.act(cfg, legal[a]), (history<<3)|(a as u64+1), reach*p[a]);
        }
        self.record(k, actor, n, p, actions, reach)
    }
}
