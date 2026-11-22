//! Self-play that writes training examples for a net (Deep CFR family).
//!
//! One run plays many games with the current net and writes two files:
//! what each action was worth compared with the mix the net played
//! (advantages), and the mix itself (strategies). A trainer fits the next
//! net to the advantages of every run so far; a final net fitted to the
//! strategies is the one to play.
//!
//! Heads-up games are played with whole ranges (`range::Walker`), so the
//! only luck left in an example is in the cards still to come.
//!
//! Runs take turns: a run records one seat's decisions only, and the next
//! net is fitted before the other seat's run. Plain tables driven the same
//! way get about ten times closer to unbeatable per run than when both
//! seats are recorded at once (see `net_tests`).

use rayon::prelude::*;
use serde::{Deserialize, Serialize};

use super::abstraction::{Abstraction, Rng, Runout};
use super::net::*;
use super::range::{Chance, NodeView, Policy, Recorder, UniformPolicy, Walker};
use super::solver::BpConfig;
use super::tree::*;
use crate::cards::{cards_to_string, combo_from_index, parse_cards, Card, NUM_COMBOS};

/// A game ready for a net: its tree, hand-strength inputs and betting inputs.
pub struct GameCtx {
    pub cfg: BpConfig,
    pub tree: BpTree,
    pub abs: Abstraction,
    pub pubf: PublicFeats,
}

impl GameCtx {
    pub fn new(cfg: &BpConfig) -> Result<GameCtx, String> {
        let boards: Vec<Vec<Card>> = cfg.boards.iter().map(|b| parse_cards(b)).collect::<Result<_, _>>()?;
        let abs = Abstraction::with_features(&boards, &cfg.groups)?;
        let tree = BpTreeBuilder::build(&cfg.tree, abs.root_street, 50_000_000)?;
        let pubf = PublicFeats::build(&tree, boards.len())?;
        Ok(GameCtx { cfg: cfg.clone(), tree, abs, pubf })
    }
}

/// What a run plays.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GenSpec {
    /// The game. With no boards, every game draws its own flop(s).
    pub game: BpConfig,
    /// Boards per game when flops are drawn.
    #[serde(default = "one")]
    pub boards: usize,
    /// Draw each game's ante and stack from these ranges (inclusive).
    #[serde(default)]
    pub ante: Option<[f64; 2]>,
    #[serde(default)]
    pub stack: Option<[f64; 2]>,
    /// Games per run, and walks of each game.
    #[serde(default = "one")]
    pub games: usize,
    #[serde(default = "one")]
    pub walks: usize,
    /// Turn and river cards drawn at each new street of a walk.
    #[serde(default = "three")]
    pub turn_draws: usize,
    #[serde(default = "two")]
    pub river_draws: usize,
    /// Share of hands kept as examples at flop, turn and river decisions.
    #[serde(default = "keep_default")]
    pub keep: [f32; 3],
    /// Flops never drawn (kept back for scoring), in any suit arrangement.
    #[serde(default)]
    pub held_out: Vec<String>,
    /// An advantage example weighs the share of the opposing range that
    /// reaches the spot, to this power. 1 is the textbook rule. Below 1,
    /// spots the opponent rarely enters get more of the net's attention
    /// (they are where a perfect opponent looks for mistakes); plain tables
    /// still converge at 0.5, a little slower.
    #[serde(default = "one_f")]
    pub weight_power: f32,
    /// The walks of a game share the cards to come evenly instead of each
    /// drawing its own (less luck in the examples for the same work).
    #[serde(default)]
    pub spread: bool,
}

fn one() -> usize {
    1
}
fn one_f() -> f32 {
    1.0
}
fn two() -> usize {
    2
}
fn three() -> usize {
    3
}
fn keep_default() -> [f32; 3] {
    [1.0, 0.5, 0.25]
}

/// A flop with its suits renamed to the smallest arrangement, so the same
/// flop in other suits compares equal.
pub fn canon_flop(cards: &[Card]) -> [u8; 3] {
    const PERMS: [[u8; 4]; 24] = {
        let mut out = [[0u8; 4]; 24];
        let mut n = 0;
        let mut a = 0;
        while a < 4 {
            let mut b = 0;
            while b < 4 {
                let mut c = 0;
                while c < 4 {
                    let d = 6 - a - b - c;
                    if a != b && a != c && b != c && d < 4 && d != a && d != b && d != c {
                        out[n] = [a as u8, b as u8, c as u8, d as u8];
                        n += 1;
                    }
                    c += 1;
                }
                b += 1;
            }
            a += 1;
        }
        out
    };
    let mut best = [255u8; 3];
    for pm in PERMS.iter() {
        let mut v = [0u8; 3];
        for (o, &c) in v.iter_mut().zip(cards) {
            *o = (c & !3) | pm[(c & 3) as usize];
        }
        v.sort_unstable();
        if v < best {
            best = v;
        }
    }
    best
}

impl GenSpec {
    /// The game for one of the run's games.
    pub fn draw_game(&self, rng: &mut Rng) -> Result<BpConfig, String> {
        let mut cfg = self.game.clone();
        if let Some([lo, hi]) = self.ante {
            cfg.tree.ante = lo + (hi - lo) * rng.f32() as f64;
        }
        if let Some([lo, hi]) = self.stack {
            cfg.tree.stack = lo + (hi - lo) * rng.f32() as f64;
        }
        if cfg.boards.is_empty() {
            let held: Vec<[u8; 3]> = self
                .held_out
                .iter()
                .map(|f| parse_cards(f).map(|c| canon_flop(&c)))
                .collect::<Result<_, _>>()?;
            'draw: loop {
                let mut deck: Vec<Card> = (0..52).collect();
                let need = 3 * self.boards;
                for i in 0..need {
                    let j = i + rng.below((52 - i) as u32) as usize;
                    deck.swap(i, j);
                }
                let flops: Vec<&[Card]> = deck[..need].chunks(3).collect();
                for f in &flops {
                    if held.contains(&canon_flop(f)) {
                        continue 'draw;
                    }
                }
                cfg.boards = flops.iter().map(|f| cards_to_string(f)).collect();
                break;
            }
        }
        Ok(cfg)
    }
}

/// Examples in memory, in the layout of the file.
pub struct SampleBuf {
    pub kind: u32,
    pub pub_rows: Vec<f32>,
    pub recs: Vec<u8>,
    pub n: u64,
}

pub const SAMPLE_BYTES: usize = 16 + 4 + 4 + HAND * 4 + MENU * 4;
const SAMPLE_MAGIC: &[u8; 4] = b"BPS1";

impl SampleBuf {
    pub fn new(kind: u32) -> SampleBuf {
        SampleBuf { kind, pub_rows: Vec::new(), recs: Vec::new(), n: 0 }
    }

    #[allow(clippy::too_many_arguments)]
    fn push(&mut self, cards: &[u8; 12], mask: u8, street: u8, player: u8, weight: f32, pub_idx: u32, hand: &[f32; HAND], target: &[f32; MENU]) {
        self.recs.extend_from_slice(cards);
        self.recs.extend_from_slice(&[mask, street, player, 0]);
        self.recs.extend_from_slice(&weight.to_le_bytes());
        self.recs.extend_from_slice(&pub_idx.to_le_bytes());
        for v in hand {
            self.recs.extend_from_slice(&v.to_le_bytes());
        }
        for v in target {
            self.recs.extend_from_slice(&v.to_le_bytes());
        }
        self.n += 1;
    }

    /// Append another buffer (its rows of betting inputs move with it).
    pub fn append(&mut self, other: SampleBuf) {
        let shift = (self.pub_rows.len() / PUB) as u32;
        let start = self.recs.len();
        self.pub_rows.extend_from_slice(&other.pub_rows);
        self.recs.extend_from_slice(&other.recs);
        if shift != 0 {
            for r in self.recs[start..].chunks_exact_mut(SAMPLE_BYTES) {
                let idx = u32::from_le_bytes(r[20..24].try_into().unwrap()) + shift;
                r[20..24].copy_from_slice(&idx.to_le_bytes());
            }
        }
        self.n += other.n;
    }

    /// Write the file: a header, the table of betting inputs, the examples.
    pub fn write(&self, path: &str, iter: u32) -> Result<(), String> {
        use std::io::Write;
        let f = std::fs::File::create(path).map_err(|e| format!("{path}: {e}"))?;
        let mut w = std::io::BufWriter::new(f);
        let mut head = Vec::new();
        head.extend_from_slice(SAMPLE_MAGIC);
        for v in [1u32, self.kind, iter] {
            head.extend_from_slice(&v.to_le_bytes());
        }
        head.extend_from_slice(&self.n.to_le_bytes());
        head.extend_from_slice(&((self.pub_rows.len() / PUB) as u64).to_le_bytes());
        for v in [PUB as u32, HAND as u32, MENU as u32, SAMPLE_BYTES as u32] {
            head.extend_from_slice(&v.to_le_bytes());
        }
        let mut body = Vec::with_capacity(self.pub_rows.len() * 4);
        for v in &self.pub_rows {
            body.extend_from_slice(&v.to_le_bytes());
        }
        w.write_all(&head)
            .and_then(|_| w.write_all(&body))
            .and_then(|_| w.write_all(&self.recs))
            .and_then(|_| w.flush())
            .map_err(|e| format!("{path}: {e}"))
    }
}

/// Turns the decisions of a whole-range walk into examples.
pub struct RangeRecorder<'a> {
    game: &'a GameCtx,
    pub adv: SampleBuf,
    pub strat: SampleBuf,
    keep: [f32; 3],
    weight_power: f32,
    /// Record this seat's decisions only.
    only: Option<usize>,
    rng: Rng,
    /// Opposing hands a hand can face at the root: weights are shares of it.
    norm: f32,
}

/// Below this share of the opposing range, an example is kept only that
/// often and counts as this much, so rarely reached spots cost little space.
const THIN: f32 = 0.05;

impl<'a> RangeRecorder<'a> {
    pub fn new(game: &'a GameCtx, keep: [f32; 3], weight_power: f32, only: Option<usize>, seed: u64) -> RangeRecorder<'a> {
        let free = 52.0 - game.abs.dead.count_ones() as f32;
        let mut r = RangeRecorder {
            game,
            adv: SampleBuf::new(KIND_ADVANTAGE),
            strat: SampleBuf::new(KIND_POLICY),
            keep,
            weight_power,
            only,
            rng: Rng::new(seed),
            norm: (free - 2.0) * (free - 3.0) / 2.0,
        };
        // Every decision's betting inputs, so an example can name its node.
        r.adv.pub_rows.extend_from_slice(&game.pubf.rows);
        r.strat.pub_rows.extend_from_slice(&game.pubf.rows);
        r
    }
}

/// The cards of one example: hole cards, then each board's five cards (255
/// where a card is not dealt or there is no second board).
pub fn sample_cards(abs: &Abstraction, street: usize, hand: usize, runout: &Runout) -> [u8; 12] {
    let mut out = [255u8; 12];
    let (c1, c2) = combo_from_index(hand);
    out[0] = c1;
    out[1] = c2;
    for b in 0..abs.num_boards() {
        let o = 2 + b * 5;
        out[o..o + 3].copy_from_slice(&abs.boards[b]);
        for st in 1..=street {
            out[o + 2 + st] = runout[b][st - 1];
        }
    }
    out
}

impl Recorder for RangeRecorder<'_> {
    fn node(&mut self, v: &NodeView) {
        if self.only.is_some_and(|p| p != v.actor) {
            return;
        }
        let g = self.game;
        let node = &g.tree.nodes[v.node_idx as usize];
        let na = node.num_children as usize;
        let street = node.street as usize;
        let slots = &g.pubf.slots[v.node_idx as usize];
        let mask = slots[..na].iter().fold(0u8, |m, &s| m | 1 << s);
        let keep = self.keep[street];
        let range = v.range;
        let mut hf = [0.0f32; HAND];
        for h in 0..NUM_COMBOS {
            let (c1, c2) = combo_from_index(h);
            if (1u64 << c1 | 1u64 << c2) & v.used != 0 {
                continue;
            }
            let mut ready = false;
            let mut cards = [0u8; 12];
            // Advantages, per unit of the opposing range and of the pot.
            let mut w = v.opp_mass[h] / self.norm;
            if w > 1e-6 {
                if self.weight_power != 1.0 {
                    w = w.powf(self.weight_power);
                }
                let p = keep * (w / THIN).min(1.0);
                if self.rng.f32() < p {
                    hand_feats(&g.abs, street, h, v.runout, range, &mut hf);
                    cards = sample_cards(&g.abs, street, h, v.runout);
                    ready = true;
                    let scale = 1.0 / (v.opp_mass[h] * node.pot);
                    let mut t = [0.0f32; MENU];
                    for a in 0..na {
                        t[slots[a] as usize] = (v.action_vals[a][h] - v.node_val[h]) * scale;
                    }
                    self.adv.push(&cards, mask, street as u8, v.actor as u8, w.max(THIN), v.node_idx, &hf, &t);
                }
            }
            // The mix played, weighted by how often the hand gets here.
            let r = v.own_reach[h];
            if r > 1e-6 {
                let p = keep * (r / THIN).min(1.0);
                if self.rng.f32() < p {
                    if !ready {
                        hand_feats(&g.abs, street, h, v.runout, range, &mut hf);
                        cards = sample_cards(&g.abs, street, h, v.runout);
                    }
                    let mut t = [0.0f32; MENU];
                    for a in 0..na {
                        t[slots[a] as usize] = v.sigma[a * NUM_COMBOS + h];
                    }
                    self.strat.push(&cards, mask, street as u8, v.actor as u8, r.max(THIN), v.node_idx, &hf, &t);
                }
            }
        }
    }
}

/// Every action equally often, as a context: it asks for the range inputs
/// so the first run's examples carry them.
struct RangedUniform<'a>(&'a BpTree);

impl Policy for RangedUniform<'_> {
    fn strategies(&self, at: &super::range::At, out: &mut [f32]) {
        UniformPolicy(self.0).strategies(at, out)
    }
    fn wants_range(&self) -> bool {
        true
    }
}

/// The average of the strategies played over the rounds, held exactly in
/// tables for the spots of one sampled walk. Comparing its score with the
/// strategy net's on the same cards shows how much the strategy net loses
/// by being a net.
pub struct Mixture {
    sums: std::collections::HashMap<(u32, [u8; 4]), Vec<f32>>,
}

struct MixRecorder<'a> {
    seat: usize,
    weight: f32,
    into: &'a mut Mixture,
}

fn mix_key(node_idx: u32, runout: &Runout) -> (u32, [u8; 4]) {
    (node_idx, [runout[0][0], runout[0][1], runout[1][0], runout[1][1]])
}

impl Recorder for MixRecorder<'_> {
    fn node(&mut self, v: &NodeView) {
        if v.actor != self.seat {
            return;
        }
        let na = v.action_vals.len();
        let row = self.into.sums.entry(mix_key(v.node_idx, v.runout)).or_insert_with(|| vec![0.0; na * NUM_COMBOS]);
        for a in 0..na {
            for h in 0..NUM_COMBOS {
                row[a * NUM_COMBOS + h] += self.weight * v.own_reach[h] * v.sigma[a * NUM_COMBOS + h];
            }
        }
    }
}

impl Policy for Mixture {
    fn strategies(&self, at: &super::range::At, out: &mut [f32]) {
        let Some(row) = self.sums.get(&mix_key(at.node_idx, at.runout)) else {
            out.fill(1.0);
            return;
        };
        let na = row.len() / NUM_COMBOS;
        for h in 0..NUM_COMBOS {
            let total: f32 = (0..na).map(|a| row[a * NUM_COMBOS + h]).sum();
            for a in 0..na {
                out[a * NUM_COMBOS + h] = if total > 0.0 { row[a * NUM_COMBOS + h] / total } else { 1.0 / na as f32 };
            }
        }
    }
}

impl Mixture {
    /// `nets[j]` is what was played in half round `j + 1` (`None`: every
    /// action equally likely); the seat learning there is `j % 2` and the
    /// round's weight is its number.
    pub fn build(game: &GameCtx, nets: &[Option<&Mlp>], range_on: bool, chance: Chance, seed: u64) -> Result<Mixture, String> {
        let walker = Walker::new(&game.tree, &game.abs)?;
        let parts: Vec<Mixture> = nets
            .par_iter()
            .enumerate()
            .map(|(j, net)| {
                let mut m = Mixture { sums: Default::default() };
                let uniform = UniformPolicy(&game.tree);
                let netp;
                let policy: &dyn Policy = match net {
                    Some(n) => {
                        netp = NetPolicy { tree: &game.tree, abs: &game.abs, pubf: &game.pubf, net: n, range_on };
                        &netp
                    }
                    None => &uniform,
                };
                let mut rec = MixRecorder { seat: j % 2, weight: (j / 2 + 1) as f32, into: &mut m };
                walker.run(policy, None, chance, false, Some(&mut rec), &mut Rng::new(seed));
                m
            })
            .collect();
        let mut all = Mixture { sums: Default::default() };
        for part in parts {
            for (k, row) in part.sums {
                match all.sums.entry(k) {
                    std::collections::hash_map::Entry::Occupied(mut e) => {
                        for (a, b) in e.get_mut().iter_mut().zip(&row) {
                            *a += b;
                        }
                    }
                    std::collections::hash_map::Entry::Vacant(e) => {
                        e.insert(row);
                    }
                }
            }
        }
        Ok(all)
    }
}

/// Plain tables trained the way the nets are (seats take turns, later rounds
/// weigh more) on the cards of one sampled walk. Its score after as many
/// rounds is what a net that fitted every example perfectly would reach.
pub struct TableRun {
    regret: std::collections::HashMap<(u32, [u8; 4]), Vec<f64>>,
    sum: std::collections::HashMap<(u32, [u8; 4]), Vec<f64>>,
}

/// How much round `t` counts: `t^regret` for what is learned, `t^average`
/// for the strategy that is kept (1, 1 is what the net loop does).
#[derive(Clone, Copy)]
pub struct Powers {
    pub regret: f64,
    pub average: f64,
}

/// Each pass sees only part of the cards, like the net loop: `walks` looks,
/// each trying `turn_draws` turn cards and `river_draws` river cards.
#[derive(Clone, Copy)]
pub struct Noisy {
    pub walks: usize,
    pub turn_draws: usize,
    pub river_draws: usize,
}

struct TablePlay(std::collections::HashMap<(u32, [u8; 4]), Vec<f32>>);

impl Policy for TablePlay {
    fn strategies(&self, at: &super::range::At, out: &mut [f32]) {
        match self.0.get(&mix_key(at.node_idx, at.runout)) {
            Some(row) => out[..row.len()].copy_from_slice(row),
            None => out.fill(1.0),
        }
    }
}

struct TableRecorder<'a> {
    seat: usize,
    weight: f64,
    weight_avg: f64,
    into: &'a mut TableRun,
}

impl Recorder for TableRecorder<'_> {
    fn node(&mut self, v: &NodeView) {
        if v.actor != self.seat {
            return;
        }
        let na = v.action_vals.len();
        let key = mix_key(v.node_idx, v.runout);
        let regret = self.into.regret.entry(key).or_insert_with(|| vec![0.0; na * NUM_COMBOS]);
        let sum = self.into.sum.entry(key).or_insert_with(|| vec![0.0; na * NUM_COMBOS]);
        for a in 0..na {
            for h in 0..NUM_COMBOS {
                if v.opp_mass[h] > 0.0 {
                    regret[a * NUM_COMBOS + h] += self.weight * (v.action_vals[a][h] - v.node_val[h]) as f64;
                }
                sum[a * NUM_COMBOS + h] += self.weight_avg * (v.own_reach[h] * v.sigma[a * NUM_COMBOS + h]) as f64;
            }
        }
    }
}

impl TableRun {
    fn play(rows: &std::collections::HashMap<(u32, [u8; 4]), Vec<f64>>) -> TablePlay {
        TablePlay(
            rows.iter()
                .map(|(k, row)| {
                    let na = row.len() / NUM_COMBOS;
                    let mut out = vec![0.0f32; row.len()];
                    for h in 0..NUM_COMBOS {
                        let total: f64 = (0..na).map(|a| row[a * NUM_COMBOS + h].max(0.0)).sum();
                        for a in 0..na {
                            out[a * NUM_COMBOS + h] =
                                if total > 0.0 { (row[a * NUM_COMBOS + h].max(0.0) / total) as f32 } else { 1.0 / na as f32 };
                        }
                    }
                    (*k, out)
                })
                .collect(),
        )
    }

    /// Train for `rounds` and call `report(round, average strategy)` every
    /// `every` rounds.
    pub fn run(
        game: &GameCtx,
        chance: Chance,
        seed: u64,
        powers: Powers,
        noisy: Option<Noisy>,
        rounds: usize,
        every: usize,
        mut report: impl FnMut(usize, &dyn Policy),
    ) -> Result<(), String> {
        let walker = Walker::new(&game.tree, &game.abs)?;
        let mut t = TableRun { regret: Default::default(), sum: Default::default() };
        for round in 1..=rounds {
            for seat in 0..2 {
                let policy = TableRun::play(&t.regret);
                let r = round as f64;
                let (walks, turn, river) = match (noisy, chance) {
                    (Some(n), Chance::Sample { turn, river }) => (n.walks.max(1), [turn, n.turn_draws], [river, n.river_draws]),
                    _ => (1, [0; 2], [0; 2]),
                };
                for walk in 0..walks {
                    let look = match noisy {
                        Some(_) => Chance::Subset { turn, river, pick: Rng::new(seed ^ ((round * 2 + seat) * 1000 + walk) as u64).next_u64() },
                        None => chance,
                    };
                    let mut rec = TableRecorder {
                        seat,
                        weight: r.powf(powers.regret) / walks as f64,
                        weight_avg: r.powf(powers.average) / walks as f64,
                        into: &mut t,
                    };
                    walker.run(&policy, None, look, false, Some(&mut rec), &mut Rng::new(seed));
                }
            }
            if round % every == 0 || round == rounds {
                report(round, &TableRun::play(&t.sum));
            }
        }
        Ok(())
    }
}

/// Play one run and return its examples (advantages, strategies), for one
/// seat's decisions or, with `only` unset, for both. `net` plays (without
/// one, every action is equally likely). With `range_on` the nets read the
/// range inputs; `context`, a strategy net, then sets the ranges they
/// describe (without one, the played ranges).
pub fn generate(
    spec: &GenSpec,
    net: Option<&Mlp>,
    context: Option<&Mlp>,
    range_on: bool,
    only: Option<usize>,
    seed: u64,
) -> Result<(SampleBuf, SampleBuf), String> {
    if spec.game.tree.players != 2 {
        return Err("whole-range self-play needs exactly two players".into());
    }
    let mut rng = Rng::new(seed);
    let games: Vec<(BpConfig, u64)> =
        (0..spec.games).map(|_| spec.draw_game(&mut rng).map(|g| (g, rng.next_u64()))).collect::<Result<_, _>>()?;
    let chance = Chance::Sample { turn: spec.turn_draws, river: spec.river_draws };
    let parts: Vec<Result<(SampleBuf, SampleBuf), String>> = games
        .par_iter()
        .map(|(cfg, gseed)| {
            let game = GameCtx::new(cfg)?;
            let walker = Walker::new(&game.tree, &game.abs)?;
            let uniform = UniformPolicy(&game.tree);
            let netp;
            let policy: &dyn Policy = match net {
                Some(n) => {
                    netp = NetPolicy { tree: &game.tree, abs: &game.abs, pubf: &game.pubf, net: n, range_on };
                    &netp
                }
                None => &uniform,
            };
            let ctxp;
            let ranged = RangedUniform(&game.tree);
            let context: Option<&dyn Policy> = match context {
                Some(n) if range_on => {
                    ctxp = NetPolicy { tree: &game.tree, abs: &game.abs, pubf: &game.pubf, net: n, range_on };
                    Some(&ctxp)
                }
                // No net plays yet, but the examples still need the inputs.
                _ if range_on && net.is_none() => Some(&ranged),
                _ => None,
            };
            let walks: Vec<(SampleBuf, SampleBuf)> = (0..spec.walks)
                .into_par_iter()
                .map(|k| {
                    let s = gseed.wrapping_add(k as u64 * 0x9E37_79B9_7F4A_7C15);
                    let mut rec = RangeRecorder::new(&game, spec.keep, spec.weight_power, only, s ^ 0x5EED);
                    let chance = match spec.spread {
                        true => Chance::Spread { turn: spec.turn_draws, river: spec.river_draws, walk: k, deck: *gseed },
                        false => chance,
                    };
                    walker.run(policy, context, chance, false, Some(&mut rec), &mut Rng::new(s));
                    (rec.adv, rec.strat)
                })
                .collect();
            let mut adv = SampleBuf::new(KIND_ADVANTAGE);
            let mut strat = SampleBuf::new(KIND_POLICY);
            for (i, (a, s)) in walks.into_iter().enumerate() {
                if i == 0 {
                    adv = a;
                    strat = s;
                } else {
                    // Same game: the rows of betting inputs are shared.
                    adv.recs.extend_from_slice(&a.recs);
                    adv.n += a.n;
                    strat.recs.extend_from_slice(&s.recs);
                    strat.n += s.n;
                }
            }
            Ok((adv, strat))
        })
        .collect();
    let mut adv = SampleBuf::new(KIND_ADVANTAGE);
    let mut strat = SampleBuf::new(KIND_POLICY);
    for p in parts {
        let (a, s) = p?;
        adv.append(a);
        strat.append(s);
    }
    Ok((adv, strat))
}
