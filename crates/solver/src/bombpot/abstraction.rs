//! Cards for bomb pot self-play: dealing, hand strength, and the grouping of
//! similar hands on later streets.
//!
//! On the street the solve starts on, the board is fixed, so every hand keeps
//! its own strategy (1326 slots, one per two-card hand). On later streets the
//! number of possible boards is too large for that, so hands are grouped:
//!
//! * River: by how many other hands the hand beats on that board.
//! * Turn: by the average of that figure over the rivers to come, and by how
//!   much it swings from river to river (made hand or draw).
//!
//! With two boards a hand's group is the pair (group on board A, group on
//! board B). `lossless` keeps every hand apart on every board instead, which
//! only fits small games and exists to check the solver against exact solves.

use crate::cards::{combo_from_index, combo_index, Card, NUM_COMBOS};
use crate::evaluator::evaluate7;
use serde::{Deserialize, Serialize};

use super::tree::MAX_PLAYERS;

pub const MAX_BOARDS: usize = 2;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AbsConfig {
    /// River groups per board.
    #[serde(default = "default_river")]
    pub river_groups: usize,
    /// Turn groups per board by strength.
    #[serde(default = "default_turn_strength")]
    pub turn_strength_groups: usize,
    /// Turn groups per board by how much the hand swings on the river.
    #[serde(default = "default_turn_draw")]
    pub turn_draw_groups: usize,
    /// Above 1, strong hands get narrower groups than weak ones: a hand that
    /// beats the share `q` of other hands lands in group `groups * q^top`.
    #[serde(default = "default_top")]
    pub top: f64,
    /// Keep every hand apart on every board (small games only).
    #[serde(default)]
    pub lossless: bool,
}

fn default_river() -> usize {
    60
}
fn default_turn_strength() -> usize {
    30
}
fn default_turn_draw() -> usize {
    3
}
fn default_top() -> f64 {
    3.0
}

impl Default for AbsConfig {
    fn default() -> Self {
        AbsConfig {
            river_groups: default_river(),
            turn_strength_groups: default_turn_strength(),
            turn_draw_groups: default_turn_draw(),
            top: default_top(),
            lossless: false,
        }
    }
}

/// Small fast generator (xoshiro256++), seeded through splitmix64.
#[derive(Clone)]
pub struct Rng([u64; 4]);

impl Rng {
    pub fn new(seed: u64) -> Rng {
        let mut z = seed;
        let mut next = || {
            z = z.wrapping_add(0x9E37_79B9_7F4A_7C15);
            let mut x = z;
            x = (x ^ (x >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
            x = (x ^ (x >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
            x ^ (x >> 31)
        };
        Rng([next(), next(), next(), next()])
    }

    #[inline]
    pub fn next_u64(&mut self) -> u64 {
        let s = &mut self.0;
        let result = s[0].wrapping_add(s[3]).rotate_left(23).wrapping_add(s[0]);
        let t = s[1] << 17;
        s[2] ^= s[0];
        s[3] ^= s[1];
        s[1] ^= s[2];
        s[0] ^= s[3];
        s[2] ^= t;
        s[3] = s[3].rotate_left(45);
        result
    }

    /// Uniform in [0, 1).
    #[inline]
    pub fn f32(&mut self) -> f32 {
        (self.next_u64() >> 40) as f32 * (1.0 / (1u64 << 24) as f32)
    }

    /// Uniform in 0..n.
    #[inline]
    pub fn below(&mut self, n: u32) -> u32 {
        ((self.next_u64() >> 32) * n as u64 >> 32) as u32
    }
}

/// The cards still to come on each board: `[turn, river]`. Entries for
/// streets not yet dealt, or already on the board at the root, are unused.
pub type Runout = [[Card; 2]; MAX_BOARDS];

/// One sampled deal: every seat's hand, the cards to come, and what the
/// solver needs from them.
#[derive(Clone)]
pub struct Deal {
    pub cards: [[Card; 2]; MAX_PLAYERS],
    pub hand: [u16; MAX_PLAYERS],
    pub runout: Runout,
    /// Strategy slot of each seat's hand on each street.
    pub bucket: [[u32; 3]; MAX_PLAYERS],
    /// Showdown strength of each seat's hand on each board.
    pub strength: [[u32; MAX_BOARDS]; MAX_PLAYERS],
}

pub struct Abstraction {
    pub cfg: AbsConfig,
    pub root_street: u8,
    /// The boards as given at the root (3, 4 or 5 cards each).
    pub boards: Vec<Vec<Card>>,
    /// Every card on a root board.
    pub dead: u64,
    /// The cards a deal draws from.
    deck: Vec<Card>,
    /// Strategy slots per street.
    pub slots: [usize; 3],
    /// Groups per board on the turn and river (grouped mode).
    turn_groups: usize,
    river_groups: usize,
    /// Flop root: `[board][turn card * 1326 + hand]`.
    turn_tab: Vec<Vec<u16>>,
    /// Flop root: `[board][combo(turn, river) * 1326 + hand]`.
    /// Turn root: `[board][river card * 1326 + hand]`.
    river_tab: Vec<Vec<u16>>,
}

fn mask_of(cards: &[Card]) -> u64 {
    cards.iter().fold(0u64, |m, &c| m | 1u64 << c)
}

/// Showdown strength of every two-card hand on a five-card board (0 for
/// hands that use a board card or a card in `dead`).
pub fn strengths(board5: &[Card], dead: u64) -> Vec<u32> {
    let blocked = mask_of(board5) | dead;
    let mut out = vec![0u32; NUM_COMBOS];
    let mut seven = [0u8; 7];
    seven[..5].copy_from_slice(board5);
    for hi in 1..52u8 {
        if blocked >> hi & 1 != 0 {
            continue;
        }
        for lo in 0..hi {
            if blocked >> lo & 1 != 0 {
                continue;
            }
            seven[5] = hi;
            seven[6] = lo;
            // +1 so a real hand is never 0.
            out[combo_index(hi, lo)] = evaluate7(&seven) + 1;
        }
    }
    out
}

/// Share of the other possible hands each hand beats on a five-card board
/// (ties count half). Negative for hands that cannot be held.
fn river_percentiles(board5: &[Card], dead: u64) -> Vec<f32> {
    let st = strengths(board5, dead);
    let mut order: Vec<u16> = (0..NUM_COMBOS as u16).filter(|&h| st[h as usize] != 0).collect();
    order.sort_unstable_by_key(|&h| st[h as usize]);
    let n = order.len();
    let mut out = vec![-1.0f32; NUM_COMBOS];
    let mut i = 0;
    while i < n {
        let mut j = i;
        while j < n && st[order[j] as usize] == st[order[i] as usize] {
            j += 1;
        }
        let q = (i as f32 + 0.5 * (j - i - 1) as f32) / (n as f32 - 1.0).max(1.0);
        for &h in &order[i..j] {
            out[h as usize] = q;
        }
        i = j;
    }
    out
}

fn group_of(q: f32, groups: usize, top: f64) -> u16 {
    let g = ((q.clamp(0.0, 1.0) as f64).powf(top) * groups as f64) as usize;
    g.min(groups - 1) as u16
}

impl Abstraction {
    pub fn new(boards: &[Vec<Card>], cfg: &AbsConfig) -> Result<Abstraction, String> {
        if boards.is_empty() || boards.len() > MAX_BOARDS {
            return Err("give one or two boards".into());
        }
        let len = boards[0].len();
        if !(3..=5).contains(&len) || boards.iter().any(|b| b.len() != len) {
            return Err("every board needs the same number of cards: 3, 4 or 5".into());
        }
        let all: Vec<Card> = boards.iter().flatten().copied().collect();
        let dead = mask_of(&all);
        if dead.count_ones() as usize != all.len() {
            return Err("a card appears twice on the boards".into());
        }
        if cfg.river_groups == 0 || cfg.turn_strength_groups == 0 || cfg.turn_draw_groups == 0 {
            return Err("group counts must be at least 1".into());
        }
        if !(cfg.top.is_finite() && cfg.top > 0.0) {
            return Err("top must be a positive number".into());
        }
        let root_street = (len - 3) as u8;
        let nb = boards.len();
        let deck: Vec<Card> = (0..52u8).filter(|&c| dead >> c & 1 == 0).collect();
        let turn_groups = cfg.turn_strength_groups * cfg.turn_draw_groups;
        let river_groups = cfg.river_groups;
        let mut slots = [0usize; 3];
        for st in root_street as usize..3 {
            let later = st - root_street as usize;
            slots[st] = if later == 0 {
                NUM_COMBOS
            } else if cfg.lossless {
                // One slot per hand and per sequence of cards dealt since the root.
                let cards_dealt = later * nb;
                let seqs = 52usize.checked_pow(cards_dealt as u32).ok_or("lossless game too large")?;
                seqs.checked_mul(NUM_COMBOS).ok_or("lossless game too large")?
            } else {
                let per_board = if st == 1 { turn_groups } else { river_groups };
                per_board.pow(nb as u32)
            };
        }
        let mut a = Abstraction {
            cfg: cfg.clone(),
            root_street,
            boards: boards.to_vec(),
            dead,
            deck,
            slots,
            turn_groups,
            river_groups,
            turn_tab: Vec::new(),
            river_tab: Vec::new(),
        };
        if !cfg.lossless && root_street < 2 {
            a.build_tables();
        }
        Ok(a)
    }

    fn build_tables(&mut self) {
        use rayon::prelude::*;
        let top = self.cfg.top;
        let rg = self.river_groups;
        for b in 0..self.boards.len() {
            let board = &self.boards[b];
            let dead = self.dead;
            if self.root_street == 1 {
                // Turn root: one table row per river card.
                let rows: Vec<Vec<u16>> = (0..52u8)
                    .into_par_iter()
                    .map(|r| {
                        let mut row = vec![0u16; NUM_COMBOS];
                        if dead >> r & 1 != 0 {
                            return row;
                        }
                        let mut b5 = board.clone();
                        b5.push(r);
                        let q = river_percentiles(&b5, dead);
                        for h in 0..NUM_COMBOS {
                            if q[h] >= 0.0 {
                                row[h] = group_of(q[h], rg, top);
                            }
                        }
                        row
                    })
                    .collect();
                self.river_tab.push(rows.concat());
                continue;
            }
            // Flop root. Raw river figures for every pair of cards to come.
            let pct: Vec<Vec<f32>> = (0..NUM_COMBOS)
                .into_par_iter()
                .map(|pair| {
                    let (t, r) = combo_from_index(pair);
                    if dead >> t & 1 != 0 || dead >> r & 1 != 0 {
                        return Vec::new();
                    }
                    let mut b5 = board.clone();
                    b5.push(t);
                    b5.push(r);
                    river_percentiles(&b5, dead)
                })
                .collect();
            let mut river = vec![0u16; NUM_COMBOS * NUM_COMBOS];
            for (pair, q) in pct.iter().enumerate() {
                for (h, &v) in q.iter().enumerate() {
                    if v >= 0.0 {
                        river[pair * NUM_COMBOS + h] = group_of(v, rg, top);
                    }
                }
            }
            self.river_tab.push(river);
            // Turn: average river figure and its spread over the rivers.
            let sg = self.cfg.turn_strength_groups;
            let dg = self.cfg.turn_draw_groups;
            let rows: Vec<Vec<u16>> = (0..52u8)
                .into_par_iter()
                .map(|t| {
                    let mut row = vec![0u16; NUM_COMBOS];
                    if dead >> t & 1 != 0 {
                        return row;
                    }
                    let mut feats: Vec<(usize, f32, f32)> = Vec::new();
                    for h in 0..NUM_COMBOS {
                        let (c1, c2) = combo_from_index(h);
                        let hm = 1u64 << c1 | 1u64 << c2;
                        if hm & (dead | 1u64 << t) != 0 {
                            continue;
                        }
                        let (mut s1, mut s2, mut n) = (0.0f64, 0.0f64, 0.0f64);
                        for r in 0..52u8 {
                            if r == t || (dead | hm) >> r & 1 != 0 {
                                continue;
                            }
                            let v = pct[combo_index(t, r)][h] as f64;
                            s1 += v;
                            s2 += v * v;
                            n += 1.0;
                        }
                        let mean = s1 / n;
                        let sd = (s2 / n - mean * mean).max(0.0).sqrt();
                        feats.push((h, mean as f32, sd as f32));
                    }
                    let n = feats.len();
                    // Rank by average strength, then by spread.
                    let mut by_mean: Vec<usize> = (0..n).collect();
                    by_mean.sort_by(|&a, &b| feats[a].1.total_cmp(&feats[b].1));
                    let mut by_sd: Vec<usize> = (0..n).collect();
                    by_sd.sort_by(|&a, &b| feats[a].2.total_cmp(&feats[b].2));
                    let mut sgroup = vec![0u16; n];
                    let mut dgroup = vec![0u16; n];
                    for (rank, &i) in by_mean.iter().enumerate() {
                        sgroup[i] = group_of(rank as f32 / (n as f32 - 1.0).max(1.0), sg, top);
                    }
                    for (rank, &i) in by_sd.iter().enumerate() {
                        dgroup[i] = ((rank * dg) / n).min(dg - 1) as u16;
                    }
                    for i in 0..n {
                        row[feats[i].0] = sgroup[i] * dg as u16 + dgroup[i];
                    }
                    row
                })
                .collect();
            self.turn_tab.push(rows.concat());
        }
    }

    pub fn num_boards(&self) -> usize {
        self.boards.len()
    }

    /// Strategy slot of a hand on a street, given the cards dealt so far.
    #[inline]
    pub fn bucket(&self, street: usize, hand: usize, runout: &Runout) -> u32 {
        let root = self.root_street as usize;
        if street == root {
            return hand as u32;
        }
        let nb = self.boards.len();
        if self.cfg.lossless {
            // Sequence of cards dealt since the root, boards in order.
            let mut seq = 0usize;
            for st in root + 1..=street {
                for b in runout.iter().take(nb) {
                    seq = seq * 52 + b[st - 1] as usize;
                }
            }
            return (seq * NUM_COMBOS + hand) as u32;
        }
        let mut g = 0usize;
        if street == 1 {
            for b in 0..nb {
                g = g * self.turn_groups + self.turn_tab[b][runout[b][0] as usize * NUM_COMBOS + hand] as usize;
            }
        } else {
            for b in 0..nb {
                let row = if root == 0 {
                    combo_index(runout[b][0], runout[b][1])
                } else {
                    runout[b][1] as usize
                };
                g = g * self.river_groups + self.river_tab[b][row * NUM_COMBOS + hand] as usize;
            }
        }
        g as u32
    }

    /// The five cards of board `b` once the runout is complete.
    pub fn full_board(&self, b: usize, runout: &Runout) -> [Card; 5] {
        let mut out = [0u8; 5];
        let base = &self.boards[b];
        out[..base.len()].copy_from_slice(base);
        for i in base.len()..5 {
            out[i] = runout[b][i - 3];
        }
        out
    }

    /// Deal hands to `players` seats and the remaining board cards.
    pub fn deal(&self, players: usize, rng: &mut Rng) -> Deal {
        let nb = self.boards.len();
        let root = self.root_street as usize;
        let to_come = 2 - root;
        let need = 2 * players + nb * to_come;
        let mut deck = [0u8; 52];
        let n = self.deck.len();
        deck[..n].copy_from_slice(&self.deck);
        for i in 0..need {
            let j = i + rng.below((n - i) as u32) as usize;
            deck.swap(i, j);
        }
        let mut d = Deal {
            cards: [[0; 2]; MAX_PLAYERS],
            hand: [0; MAX_PLAYERS],
            runout: [[0; 2]; MAX_BOARDS],
            bucket: [[0; 3]; MAX_PLAYERS],
            strength: [[0; MAX_BOARDS]; MAX_PLAYERS],
        };
        let mut k = 0;
        for p in 0..players {
            d.cards[p] = [deck[k], deck[k + 1]];
            d.hand[p] = combo_index(deck[k], deck[k + 1]) as u16;
            k += 2;
        }
        for st in root..2 {
            for b in 0..nb {
                d.runout[b][st] = deck[k];
                k += 1;
            }
        }
        let mut seven = [0u8; 7];
        for b in 0..nb {
            seven[..5].copy_from_slice(&self.full_board(b, &d.runout));
            for p in 0..players {
                seven[5] = d.cards[p][0];
                seven[6] = d.cards[p][1];
                d.strength[p][b] = evaluate7(&seven) + 1;
            }
        }
        for p in 0..players {
            for st in root..3 {
                d.bucket[p][st] = self.bucket(st, d.hand[p] as usize, &d.runout);
            }
        }
        d
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cards::parse_cards;

    #[test]
    fn groups_follow_strength_on_the_river() {
        let boards = vec![parse_cards("AsKd7c").unwrap()];
        let a = Abstraction::new(&boards, &AbsConfig::default()).unwrap();
        assert_eq!(a.slots, [1326, 90, 60]);
        let c = |s: &str| parse_cards(s).unwrap();
        let run: Runout = [[c("4h")[0], c("2s")[0]], [0, 0]];
        let hand = |s: &str| {
            let v = c(s);
            combo_index(v[0], v[1])
        };
        let set = a.bucket(2, hand("AhAd"), &run);
        let top_pair = a.bucket(2, hand("AhQd"), &run);
        let air = a.bucket(2, hand("9h8d"), &run);
        // Only the wheel (5-3) beats top set on this board.
        assert!(set >= 55);
        assert!(set > top_pair && top_pair > air, "{set} {top_pair} {air}");
        // Same river reached through the other turn card: same group.
        let run2: Runout = [[c("2s")[0], c("4h")[0]], [0, 0]];
        assert_eq!(a.bucket(2, hand("AhQd"), &run2), top_pair);
        // A flush draw swings more than a made pair of similar strength.
        let run3: Runout = [[c("4s")[0], 0], [0, 0]];
        let draw = a.bucket(1, hand("QsJs"), &run3) % 3;
        let made = a.bucket(1, hand("KhQh"), &run3) % 3;
        assert!(draw > made, "draw {draw} made {made}");
    }

    #[test]
    fn deals_never_repeat_a_card_and_two_boards_get_pair_groups() {
        let boards = vec![parse_cards("AsKd7c").unwrap(), parse_cards("9h8h2d").unwrap()];
        let cfg = AbsConfig { river_groups: 12, turn_strength_groups: 6, turn_draw_groups: 2, ..Default::default() };
        let a = Abstraction::new(&boards, &cfg).unwrap();
        assert_eq!(a.slots, [1326, 144, 144]);
        let mut rng = Rng::new(7);
        for _ in 0..20_000 {
            let d = a.deal(6, &mut rng);
            let mut seen = a.dead;
            for p in 0..6 {
                for c in d.cards[p] {
                    assert_eq!(seen >> c & 1, 0);
                    seen |= 1 << c;
                }
                assert!(d.bucket[p][1] < 144 && d.bucket[p][2] < 144);
                assert!(d.strength[p][0] > 0 && d.strength[p][1] > 0);
            }
            for b in 0..2 {
                for c in d.runout[b] {
                    assert_eq!(seen >> c & 1, 0);
                    seen |= 1 << c;
                }
            }
        }
    }
}
