//! Sampled self-play for bomb pots (external-sampling Monte Carlo CFR).
//!
//! Each pass deals real cards to every seat and to the boards, then lets one
//! seat (the traverser) try every action at each of its decisions while the
//! other seats each play one action drawn from their current strategy. The
//! traverser's regrets are updated from what each action would have earned.
//! Dealing real hands keeps card removal exact for any number of players.
//!
//! Passes are grouped into rounds; round `k` counts `k` times as much as the
//! first, so early, noisy play fades (linear weighting).

use std::sync::atomic::{AtomicU32, AtomicU64, Ordering::Relaxed};

use serde::{Deserialize, Serialize};

use super::abstraction::{AbsConfig, Abstraction, Deal, Rng, MAX_BOARDS};
use super::tree::*;
use crate::cards::Card;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BpConfig {
    /// One or two boards, e.g. `["AsKd7c"]` or `["AsKd7c", "9h8h2d"]`.
    pub boards: Vec<String>,
    pub tree: BpTreeConfig,
    #[serde(default)]
    pub groups: AbsConfig,
}

/// A table of f32 shared by the worker threads without locks. Two threads
/// may occasionally overwrite each other's update of one slot; with millions
/// of updates that loss is noise, and every access stays well defined.
pub struct Table(Vec<AtomicU32>);

impl Table {
    pub fn zeroed(len: usize) -> Table {
        let mut v = std::mem::ManuallyDrop::new(vec![0u32; len]);
        // SAFETY: AtomicU32 has the same size, alignment and bit validity as
        // u32, and the vector's allocation is handed over unchanged.
        Table(unsafe { Vec::from_raw_parts(v.as_mut_ptr() as *mut AtomicU32, v.len(), v.capacity()) })
    }
    #[inline]
    pub fn get(&self, i: usize) -> f32 {
        f32::from_bits(self.0[i].load(Relaxed))
    }
    #[inline]
    pub fn set(&self, i: usize, v: f32) {
        self.0[i].store(v.to_bits(), Relaxed)
    }
    #[inline]
    pub fn add(&self, i: usize, v: f32) {
        self.set(i, self.get(i) + v)
    }
    pub fn len(&self) -> usize {
        self.0.len()
    }
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }
}

/// The same for summed strategy weights, in f64. A busy slot is added to
/// tens of millions of times; in f32 each addition would then be rounded to
/// a few steps of the running total, which bends the average strategy at
/// exactly the most played spots.
pub struct SumTable(Vec<AtomicU64>);

impl SumTable {
    pub fn zeroed(len: usize) -> SumTable {
        let mut v = std::mem::ManuallyDrop::new(vec![0u64; len]);
        // SAFETY: as for `Table`, with AtomicU64 and u64.
        SumTable(unsafe { Vec::from_raw_parts(v.as_mut_ptr() as *mut AtomicU64, v.len(), v.capacity()) })
    }
    #[inline]
    pub fn get(&self, i: usize) -> f64 {
        f64::from_bits(self.0[i].load(Relaxed))
    }
    #[inline]
    pub fn add(&self, i: usize, v: f64) {
        self.0[i].store((self.get(i) + v).to_bits(), Relaxed)
    }
    pub fn len(&self) -> usize {
        self.0.len()
    }
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }
}

/// Regret matching: play each action in proportion to its positive regret.
#[inline]
pub fn regret_match(t: &Table, base: usize, na: usize, out: &mut [f32; MAX_ACTIONS]) {
    let mut sum = 0.0f32;
    for a in 0..na {
        let r = t.get(base + a).max(0.0);
        out[a] = r;
        sum += r;
    }
    if sum > 0.0 {
        let inv = 1.0 / sum;
        for o in out.iter_mut().take(na) {
            *o *= inv;
        }
    } else {
        let u = 1.0 / na as f32;
        for o in out.iter_mut().take(na) {
            *o = u;
        }
    }
}

/// Normalise a row of summed strategy weights into probabilities.
#[inline]
pub fn normalise(t: &SumTable, base: usize, na: usize, out: &mut [f32; MAX_ACTIONS]) {
    let mut raw = [0.0f64; MAX_ACTIONS];
    let mut sum = 0.0f64;
    for a in 0..na {
        raw[a] = t.get(base + a);
        sum += raw[a];
    }
    if sum > 0.0 {
        for a in 0..na {
            out[a] = (raw[a] / sum) as f32;
        }
    } else {
        let u = 1.0 / na as f32;
        for o in out.iter_mut().take(na) {
            *o = u;
        }
    }
}

#[inline]
pub fn sample(probs: &[f32; MAX_ACTIONS], na: usize, rng: &mut Rng) -> usize {
    let mut x = rng.f32();
    for (a, &p) in probs.iter().enumerate().take(na - 1) {
        if x < p {
            return a;
        }
        x -= p;
    }
    na - 1
}

pub struct BpSolver {
    pub tree: BpTree,
    pub abs: Abstraction,
    pub boards: Vec<Vec<Card>>,
    /// Per seat: regrets and summed strategy weights, laid out as
    /// `node.info_offset + slot * actions + action`.
    pub regret: Vec<Table>,
    pub strat: Vec<SumTable>,
    pub rounds: u32,
    pub deals: u64,
}

/// Bytes the two tables of a solve would need (f32 regrets, f64 sums).
pub fn table_bytes(tree: &BpTree, abs: &Abstraction) -> u64 {
    let mut total = 0u64;
    for n in &tree.nodes {
        if n.kind == KIND_ACTION {
            total += abs.slots[n.street as usize] as u64 * n.num_children as u64;
        }
    }
    total * 12
}

impl BpSolver {
    pub fn new(cfg: &BpConfig, max_bytes: u64) -> Result<BpSolver, String> {
        let boards: Vec<Vec<Card>> =
            cfg.boards.iter().map(|b| crate::cards::parse_cards(b)).collect::<Result<_, _>>()?;
        let abs = Abstraction::new(&boards, &cfg.groups)?;
        let need = 2 * cfg.tree.players + boards.len() * (2 - abs.root_street as usize);
        if 52 - abs.dead.count_ones() as usize - need < 1 {
            return Err("not enough cards in the deck for this many players and boards".into());
        }
        let mut tree = BpTreeBuilder::build(&cfg.tree, abs.root_street, 200_000_000)?;
        let bytes = table_bytes(&tree, &abs);
        if bytes > max_bytes {
            return Err(format!(
                "this game needs {:.1} GB of memory, over the limit of {:.1} GB; use fewer bet sizes, raises or hand groups",
                bytes as f64 / 1e9,
                max_bytes as f64 / 1e9
            ));
        }
        let n = cfg.tree.players;
        let mut sizes = vec![0u64; n];
        for node in tree.nodes.iter_mut() {
            if node.kind == KIND_ACTION {
                let p = node.player as usize;
                node.info_offset = sizes[p];
                sizes[p] += abs.slots[node.street as usize] as u64 * node.num_children as u64;
            }
        }
        let regret = sizes.iter().map(|&s| Table::zeroed(s as usize)).collect();
        let strat = sizes.iter().map(|&s| SumTable::zeroed(s as usize)).collect();
        Ok(BpSolver { tree, abs, boards, regret, strat, rounds: 0, deals: 0 })
    }

    pub fn players(&self) -> usize {
        self.tree.config.players
    }

    #[inline]
    pub fn slot_base(&self, node: &BpNode, bucket: u32) -> usize {
        node.info_offset as usize + bucket as usize * node.num_children as usize
    }

    /// What seat `p` wins or loses at a terminal node.
    #[inline]
    pub fn payoff(&self, node_idx: u32, node: &BpNode, p: usize, deal: &Deal) -> f32 {
        let put = self.tree.put(node_idx, p);
        if node.live >> p & 1 == 0 {
            return -put;
        }
        if node.kind == KIND_FOLD {
            return node.pot_net - put;
        }
        let nb = self.abs.num_boards();
        let per_board = node.pot_net / nb as f32;
        let n = self.players();
        let mut won = 0.0f32;
        for b in 0..nb {
            let mine = deal.strength[p][b];
            let mut best = 0u32;
            let mut ties = 0u32;
            for q in 0..n {
                if node.live >> q & 1 == 0 {
                    continue;
                }
                let s = deal.strength[q][b];
                if s > best {
                    best = s;
                    ties = 1;
                } else if s == best {
                    ties += 1;
                }
            }
            if mine == best {
                won += per_board / ties as f32;
            }
        }
        won - put
    }

    /// One traversal for `trav` on a dealt hand. Returns the traverser's
    /// result under the current strategies.
    fn traverse(&self, node_idx: u32, trav: usize, deal: &Deal, rng: &mut Rng, w: f32) -> f32 {
        let node = &self.tree.nodes[node_idx as usize];
        if node.live >> trav & 1 == 0 {
            // Folded: the result is settled, nothing below can change it.
            return -self.tree.put(node_idx, trav);
        }
        if node.kind != KIND_ACTION {
            return self.payoff(node_idx, node, trav, deal);
        }
        let p = node.player as usize;
        let na = node.num_children as usize;
        let base = self.slot_base(node, deal.bucket[p][node.street as usize]);
        let mut sigma = [0.0f32; MAX_ACTIONS];
        regret_match(&self.regret[p], base, na, &mut sigma);
        if p == trav {
            let mut util = [0.0f32; MAX_ACTIONS];
            let mut ev = 0.0f32;
            for a in 0..na {
                util[a] = self.traverse(self.tree.child(node, a), trav, deal, rng, w);
                ev += sigma[a] * util[a];
            }
            let r = &self.regret[p];
            for a in 0..na {
                r.add(base + a, w * (util[a] - ev));
            }
            ev
        } else {
            let s = &self.strat[p];
            for a in 0..na {
                if sigma[a] > 0.0 {
                    s.add(base + a, (w * sigma[a]) as f64);
                }
            }
            let a = sample(&sigma, na, rng);
            self.traverse(self.tree.child(node, a), trav, deal, rng, w)
        }
    }

    /// Run one round of `deals` dealt hands (every seat traverses each deal)
    /// on `threads` threads.
    pub fn run_round(&mut self, deals: u64, threads: usize, seed: u64) {
        self.rounds += 1;
        let w = self.rounds as f32;
        let n = self.players();
        let threads = threads.max(1);
        let this = &*self;
        std::thread::scope(|sc| {
            for t in 0..threads {
                let share = deals / threads as u64 + u64::from((t as u64) < deals % threads as u64);
                let round = this.rounds as u64;
                sc.spawn(move || {
                    let mut rng = Rng::new(seed ^ round.wrapping_mul(0x9E37_79B9) ^ (t as u64) << 40);
                    for _ in 0..share {
                        let deal = this.abs.deal(n, &mut rng);
                        for trav in 0..n {
                            this.traverse(0, trav, &deal, &mut rng, w);
                        }
                    }
                });
            }
        });
        self.deals += deals;
    }

    /// Average strategy of the actor at `node` for one strategy slot.
    #[inline]
    pub fn average(&self, node: &BpNode, bucket: u32, out: &mut [f32; MAX_ACTIONS]) {
        let p = node.player as usize;
        normalise(&self.strat[p], self.slot_base(node, bucket), node.num_children as usize, out);
    }

    /// Follow a line of action indices from the root.
    pub fn walk(&self, line: &[usize]) -> Result<u32, String> {
        let mut idx = 0u32;
        for &a in line {
            let node = &self.tree.nodes[idx as usize];
            if node.kind != KIND_ACTION || a >= node.num_children as usize {
                return Err(format!("line {line:?} leaves the tree"));
            }
            idx = self.tree.child(node, a);
        }
        Ok(idx)
    }
}

/// One seat trained on its own against the other seats' fixed average
/// strategies. It may tell hands apart more finely than the solve did
/// (its own `abs`), which shows what the solve's hand grouping gives away.
pub struct Challenger {
    pub seat: usize,
    pub abs: Abstraction,
    /// First slot of each of the seat's nodes in `regret`.
    offsets: Vec<u64>,
    pub regret: Table,
}

impl Challenger {
    #[inline]
    fn base(&self, node_idx: u32, node: &BpNode, deal: &Deal) -> usize {
        let b = self.abs.bucket(node.street as usize, deal.hand[self.seat] as usize, &deal.runout);
        self.offsets[node_idx as usize] as usize + b as usize * node.num_children as usize
    }
}

impl BpSolver {
    /// Play one dealt hand to the end with every seat drawing from its
    /// average strategy, and add each seat's result to `out`. A challenger
    /// plays its best action so far instead.
    pub fn playout(&self, deal: &Deal, rng: &mut Rng, challenger: Option<&Challenger>, out: &mut [f64]) {
        let mut idx = 0u32;
        loop {
            let node = &self.tree.nodes[idx as usize];
            if node.kind != KIND_ACTION {
                for (p, o) in out.iter_mut().enumerate().take(self.players()) {
                    *o += self.payoff(idx, node, p, deal) as f64;
                }
                return;
            }
            let p = node.player as usize;
            let na = node.num_children as usize;
            let a = match challenger {
                Some(c) if c.seat == p => {
                    // The action with the most summed regret is the one that
                    // has earned the most against the fixed opponents.
                    let base = c.base(idx, node, deal);
                    let mut best = 0;
                    for a in 1..na {
                        if c.regret.get(base + a) > c.regret.get(base + best) {
                            best = a;
                        }
                    }
                    best
                }
                _ => {
                    let base = self.slot_base(node, deal.bucket[p][node.street as usize]);
                    let mut sigma = [0.0f32; MAX_ACTIONS];
                    normalise(&self.strat[p], base, na, &mut sigma);
                    sample(&sigma, na, rng)
                }
            };
            idx = self.tree.child(node, a);
        }
    }

    /// Each seat's average result over `deals` playouts, with its standard error.
    pub fn sampled_values(&self, deals: u64, threads: usize, seed: u64, challenger: Option<&Challenger>) -> Vec<(f64, f64)> {
        let n = self.players();
        let threads = threads.max(1);
        let parts: Vec<(Vec<f64>, Vec<f64>, u64)> = std::thread::scope(|sc| {
            let hs: Vec<_> = (0..threads)
                .map(|t| {
                    let share = deals / threads as u64 + u64::from((t as u64) < deals % threads as u64);
                    sc.spawn(move || {
                        let mut rng = Rng::new(seed ^ 0xABCD_EF01 ^ (t as u64) << 40);
                        let mut sum = vec![0.0f64; n];
                        let mut sq = vec![0.0f64; n];
                        let mut one = vec![0.0f64; n];
                        for _ in 0..share {
                            let deal = self.abs.deal(n, &mut rng);
                            one.iter_mut().for_each(|x| *x = 0.0);
                            self.playout(&deal, &mut rng, challenger, &mut one);
                            for p in 0..n {
                                sum[p] += one[p];
                                sq[p] += one[p] * one[p];
                            }
                        }
                        (sum, sq, share)
                    })
                })
                .collect();
            hs.into_iter().map(|h| h.join().unwrap()).collect()
        });
        let total: u64 = parts.iter().map(|p| p.2).sum();
        (0..n)
            .map(|p| {
                let s: f64 = parts.iter().map(|x| x.0[p]).sum();
                let q: f64 = parts.iter().map(|x| x.1[p]).sum();
                let mean = s / total as f64;
                let var = (q / total as f64 - mean * mean).max(0.0);
                (mean, (var / total as f64).sqrt())
            })
            .collect()
    }

    /// Train one seat against the other seats' fixed average strategies.
    /// `groups` is the challenger's own hand grouping (`None`: the solve's).
    /// Its best actions are an approximate best reply, so what it gains is a
    /// floor on what that seat could gain by changing only its own play.
    pub fn train_challenger(
        &self,
        seat: usize,
        groups: Option<&AbsConfig>,
        deals: u64,
        threads: usize,
        seed: u64,
        max_bytes: u64,
    ) -> Result<Challenger, String> {
        let abs = Abstraction::new(&self.boards, groups.unwrap_or(&self.abs.cfg))?;
        let mut offsets = vec![0u64; self.tree.nodes.len()];
        let mut size = 0u64;
        for (i, node) in self.tree.nodes.iter().enumerate() {
            if node.kind == KIND_ACTION && node.player as usize == seat {
                offsets[i] = size;
                size += abs.slots[node.street as usize] as u64 * node.num_children as u64;
            }
        }
        if size * 4 > max_bytes {
            return Err(format!("the challenger needs {:.1} GB, over the limit", size as f64 * 4.0 / 1e9));
        }
        let c = Challenger { seat, abs, offsets, regret: Table::zeroed(size as usize) };
        let n = self.players();
        let threads = threads.max(1);
        let cref = &c;
        std::thread::scope(|sc| {
            for t in 0..threads {
                let share = deals / threads as u64 + u64::from((t as u64) < deals % threads as u64);
                sc.spawn(move || {
                    let mut rng = Rng::new(seed ^ 0x5151_7777 ^ (t as u64) << 40);
                    for _ in 0..share {
                        let deal = self.abs.deal(n, &mut rng);
                        self.challenge(0, cref, &deal, &mut rng);
                    }
                });
            }
        });
        Ok(c)
    }

    fn challenge(&self, node_idx: u32, c: &Challenger, deal: &Deal, rng: &mut Rng) -> f32 {
        let node = &self.tree.nodes[node_idx as usize];
        let seat = c.seat;
        if node.live >> seat & 1 == 0 {
            return -self.tree.put(node_idx, seat);
        }
        if node.kind != KIND_ACTION {
            return self.payoff(node_idx, node, seat, deal);
        }
        let p = node.player as usize;
        let na = node.num_children as usize;
        let mut sigma = [0.0f32; MAX_ACTIONS];
        if p == seat {
            let base = c.base(node_idx, node, deal);
            regret_match(&c.regret, base, na, &mut sigma);
            let mut util = [0.0f32; MAX_ACTIONS];
            let mut ev = 0.0f32;
            for a in 0..na {
                util[a] = self.challenge(self.tree.child(node, a), c, deal, rng);
                ev += sigma[a] * util[a];
            }
            for a in 0..na {
                c.regret.add(base + a, util[a] - ev);
            }
            ev
        } else {
            let base = self.slot_base(node, deal.bucket[p][node.street as usize]);
            normalise(&self.strat[p], base, na, &mut sigma);
            let a = sample(&sigma, na, rng);
            self.challenge(self.tree.child(node, a), c, deal, rng)
        }
    }
}

/// Unused boards in `Deal` stay zeroed; this keeps the constant referenced.
const _: () = assert!(MAX_BOARDS == 2);
