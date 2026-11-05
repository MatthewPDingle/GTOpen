//! "Trust the read": Restricted Nash Response for profiled villains.
//!
//! Today a postflop profile lock (`Solver::lock_profile`) fixes the villain's
//! whole tree and the hero re-adapts: the hero's strategy is a full best
//! response to the read, maximally profitable if the read is right and
//! maximally exploitable if it is wrong. Restricted Nash Response (Johanson,
//! Zinkevich & Bowling, "Computing Robust Counter-Strategies", NIPS 2007)
//! adds one dial, `trust` = p: at the start of the hand a chance node makes
//! the villain the READ (he plays the profile locks) with probability p, or
//! FREE (he plays any strategy, learning against the hero) with probability
//! 1 - p. The villain knows which he is; the hero does not, so the hero's
//! strategy is a best response to the mixture that keeps updating its belief
//! along the hand. If the villain takes a line the profile never takes, the
//! hero knows from then on that he faces the free villain. A per-node blend
//! of the two strategies cannot do that.
//!
//! Exact implementation on the existing engine, with no extra arenas:
//! - Read and free villains share every node that is not profile locked
//!   (the profile covers every node the read reaches, so in practice the
//!   read plays the lock wherever it matters). Manual point locks and fits
//!   bind both: they are facts, not the read.
//! - The free villain's pass is an ordinary CFR pass with the profile locks
//!   ignored (`free = true`): his regrets and average strategy at profile
//!   locked nodes are his own.
//! - The hero's pass carries the villain's reach as two stacked blocks
//!   [read | free] and evaluates terminals against p * read + (1 - p) * free.
//!   Terminal values are linear in the opponent reach, so this is exact and
//!   costs one extra reach vector per villain node, not a second traversal.
//! - p = 1 is today's solve (the dial is inactive); p = 0 is the unlocked
//!   solve, bit for bit.

use crate::cfr::{Discounts, Solver};
use crate::game::{fold_cfv, showdown_cfv, Dealt};
use crate::query::PROFILE_LABEL;
use crate::scratch::Buf;
use crate::tree::{KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};
use serde::Serialize;

/// The dial in force for one solve step.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Trust {
    /// Probability that the villain plays the read (profile locks).
    pub trust: f32,
    /// The profiled player (0 = OOP, 1 = IP); the hero is the other one.
    pub villain: usize,
}

/// What a trust level buys and costs, in chips (pot-share EVs at the root,
/// the Browse convention: EV_OOP + EV_IP = pot without rake).
#[derive(Debug, Clone, Serialize)]
pub struct TrustReadout {
    pub trust: f64,
    pub hero: usize,
    pub villain: usize,
    /// Hero EV when the villain plays the read.
    pub hero_ev_vs_read: f64,
    /// Hero EV against the trust-weighted mixture the hero solved for.
    pub hero_ev_vs_mixture: f64,
    /// The villain's EV when he best-responds to the hero (profile locks
    /// off, manual point locks still on): what a villain who knows the
    /// hero's strategy makes. Compare with the trust = 0 solve to see how
    /// much exploitability the read costs.
    pub villain_best_response_ev: f64,
    /// Hero EV against that best response. Zero-sum games only (no rake, no
    /// ICM); `None` otherwise, where the two EVs need not add up to the pot.
    pub hero_worst_case_ev: Option<f64>,
    /// Convergence of the trust game in chips (what `Solver::run` targets).
    pub exploitability: f64,
}

impl Solver {
    /// Set the "trust the read" dial: `Some(p)` with p in [0, 1], or `None`
    /// for today's behaviour (equivalent to 1). Takes effect from the next
    /// iteration; it only does anything while a profile lock exists.
    pub fn set_trust(&mut self, trust: Option<f32>) -> Result<(), String> {
        if let Some(t) = trust {
            if !t.is_finite() || !(0.0..=1.0).contains(&t) {
                return Err(format!("trust must be between 0 and 1, got {t}"));
            }
        }
        self.trust = trust;
        Ok(())
    }

    pub fn trust(&self) -> Option<f32> {
        self.trust
    }

    /// Whether the lock at `idx` is part of the read (a profile lock).
    #[inline]
    pub(crate) fn is_read_lock(&self, idx: u32) -> bool {
        self.lock_labels.get(&idx).is_some_and(|l| l.starts_with(PROFILE_LABEL))
    }

    /// The profiled player: the owner of the profile locks, if any.
    pub fn read_villain(&self) -> Option<usize> {
        self.lock_labels
            .iter()
            .find(|(_, l)| l.starts_with(PROFILE_LABEL))
            .map(|(&idx, _)| self.spot.tree.nodes[idx as usize].player as usize)
    }

    /// The dial when it changes the solve: trust below 1 and a profile lock
    /// to trust. Otherwise the solver runs exactly as without it.
    pub fn rnr_active(&self) -> Option<Trust> {
        let trust = self.trust?;
        if trust >= 1.0 {
            return None;
        }
        Some(Trust { trust, villain: self.read_villain()? })
    }

    /// One CFR pass for the hero against the read/free mixture.
    pub(crate) fn cfr_rnr_hero(&self, r: &Trust, disc: &Discounts, out: &mut [f32]) {
        let h = 1 - r.villain;
        let ro = stacked(&self.spot.weights[r.villain]);
        self.cfr_mix(0, h, &self.spot.weights[h], &ro, Dealt::default(), disc, r.trust, out);
    }

    /// `cfr()` for the hero `p` with the villain's reach stacked as
    /// [read | free]; see the module docs.
    #[allow(clippy::too_many_arguments)]
    fn cfr_mix(
        &self,
        node_idx: u32,
        p: usize,
        reach_p: &[f32],
        reach_o2: &[f32],
        dealt: Dealt,
        disc: &Discounts,
        trust: f32,
        out: &mut [f32],
    ) {
        let spot = &*self.spot;
        let node = &spot.tree.nodes[node_idx as usize];
        let nh_o = spot.hands[1 - p].len();
        // same zero-reach rule as cfr(): only learning-free subtrees skip
        if matches!(node.kind, KIND_TERM_FOLD | KIND_TERM_SHOWDOWN | KIND_CHANCE)
            && reach_o2.iter().all(|&r| r <= 0.0)
            && (node.kind != KIND_CHANCE || self.action_free_runout(node))
        {
            return;
        }
        match node.kind {
            KIND_TERM_FOLD => {
                let ro = mixed(reach_o2, nh_o, trust);
                let amount = spot.fold_payoff(node_idx, node, p);
                fold_cfv(&spot.hands[p], &spot.hands[1 - p], &ro, &spot.same_combo[p], amount, out);
            }
            KIND_TERM_SHOWDOWN => {
                let ro = mixed(reach_o2, nh_o, trust);
                let (t_win, t_lose, t_tie) = spot.showdown_payoffs(node_idx, node, p);
                showdown_cfv(
                    spot.river.get(&dealt),
                    p,
                    &spot.hands[p],
                    &spot.hands[1 - p],
                    &ro,
                    &spot.same_combo[p],
                    t_win,
                    t_lose,
                    t_tie,
                    out,
                );
            }
            KIND_CHANCE => {
                self.chance_node(node, p, reach_p, reach_o2, dealt, out, |s, c, rp, ro, d, o| {
                    s.cfr_mix(c, p, rp, ro, d, disc, trust, o)
                });
            }
            KIND_ACTION => {
                let na = node.num_children as usize;
                let cs = node.children_start as usize;
                if node.player as usize == p {
                    // the hero's own node: exactly cfr()'s traverser branch
                    let nh = spot.hands[p].len();
                    let locked = self.lock_view(node_idx, false).is_some();
                    let mut sigma = Buf::for_overwrite(na * nh);
                    self.current_strategy(node_idx, node, &mut sigma, false);
                    let mut vals = Buf::zeroed(na * nh);
                    let mut reach_buf = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let sig = &sigma[a * nh..(a + 1) * nh];
                        for i in 0..nh {
                            reach_buf[i] = reach_p[i] * sig[i];
                        }
                        self.cfr_mix(
                            spot.tree.children[cs + a],
                            p,
                            &reach_buf,
                            reach_o2,
                            dealt,
                            disc,
                            trust,
                            &mut vals[a * nh..(a + 1) * nh],
                        );
                    }
                    if !self.fits.is_empty() {
                        if let Some(fit) = self.fits.get(&node_idx) {
                            fit.apply(&sigma, reach_p, &mut vals, na, nh);
                        }
                    }
                    for a in 0..na {
                        let sig = &sigma[a * nh..(a + 1) * nh];
                        let val = &vals[a * nh..(a + 1) * nh];
                        for i in 0..nh {
                            out[i] += sig[i] * val[i];
                        }
                    }
                    if !locked {
                        self.update_node(node_idx, node, p, &sigma, &vals, out, reach_p, disc);
                    }
                } else {
                    // villain node: the read plays any lock, the free villain
                    // ignores profile locks
                    let mut sig_free = Buf::for_overwrite(na * nh_o);
                    self.current_strategy(node_idx, node, &mut sig_free, true);
                    let read_lock = self.lock_view(node_idx, false);
                    let nh = spot.hands[p].len();
                    let mut buf = Buf::for_overwrite(2 * nh_o);
                    let mut child_out = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let sf = &sig_free[a * nh_o..(a + 1) * nh_o];
                        let sr = read_lock.map_or(sf, |l| &l[a * nh_o..(a + 1) * nh_o]);
                        for j in 0..nh_o {
                            buf[j] = reach_o2[j] * sr[j];
                            buf[nh_o + j] = reach_o2[nh_o + j] * sf[j];
                        }
                        child_out.fill(0.0);
                        self.cfr_mix(spot.tree.children[cs + a], p, reach_p, &buf, dealt, disc, trust, &mut child_out);
                        for i in 0..nh {
                            out[i] += child_out[i];
                        }
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    /// Best-response (`best`) or average-strategy values for the hero `p`
    /// against the [read | free] villain mixture, under average strategies.
    #[allow(clippy::too_many_arguments)]
    fn eval_mix_into(
        &self,
        node_idx: u32,
        p: usize,
        reach_o2: &[f32],
        dealt: Dealt,
        best: bool,
        trust: f32,
        out: &mut [f32],
    ) {
        if reach_o2.iter().all(|&r| r <= 0.0) {
            return;
        }
        let spot = &*self.spot;
        let node = &spot.tree.nodes[node_idx as usize];
        let nh = spot.hands[p].len();
        let nh_o = spot.hands[1 - p].len();
        match node.kind {
            KIND_TERM_FOLD => {
                let ro = mixed(reach_o2, nh_o, trust);
                let amount = spot.fold_payoff(node_idx, node, p);
                fold_cfv(&spot.hands[p], &spot.hands[1 - p], &ro, &spot.same_combo[p], amount, out);
            }
            KIND_TERM_SHOWDOWN => {
                let ro = mixed(reach_o2, nh_o, trust);
                let (t_win, t_lose, t_tie) = spot.showdown_payoffs(node_idx, node, p);
                showdown_cfv(
                    spot.river.get(&dealt),
                    p,
                    &spot.hands[p],
                    &spot.hands[1 - p],
                    &ro,
                    &spot.same_combo[p],
                    t_win,
                    t_lose,
                    t_tie,
                    out,
                );
            }
            KIND_CHANCE => {
                let dummy = Buf::filled(nh, 1.0);
                self.chance_node(node, p, &dummy, reach_o2, dealt, out, |s, c, _rp, ro, d, o| {
                    s.eval_mix_into(c, p, ro, d, best, trust, o)
                });
            }
            KIND_ACTION => {
                let na = node.num_children as usize;
                let cs = node.children_start as usize;
                let mut vals = Buf::for_overwrite(nh);
                if node.player as usize == p {
                    // a lock or a running fit is a constraint, as in br_into
                    let constrained = self.locks.contains_key(&node_idx)
                        || (!self.fits.is_empty() && self.fits.contains_key(&node_idx));
                    if best && !constrained {
                        for a in 0..na {
                            vals.fill(0.0);
                            self.eval_mix_into(spot.tree.children[cs + a], p, reach_o2, dealt, best, trust, &mut vals);
                            if a == 0 {
                                out.copy_from_slice(&vals);
                            } else {
                                for i in 0..nh {
                                    if vals[i] > out[i] {
                                        out[i] = vals[i];
                                    }
                                }
                            }
                        }
                    } else {
                        let mut sigma = Buf::for_overwrite(na * nh);
                        self.average_strategy_into(node_idx, node, &mut sigma);
                        for a in 0..na {
                            vals.fill(0.0);
                            self.eval_mix_into(spot.tree.children[cs + a], p, reach_o2, dealt, best, trust, &mut vals);
                            let sig = &sigma[a * nh..(a + 1) * nh];
                            for i in 0..nh {
                                out[i] += sig[i] * vals[i];
                            }
                        }
                    }
                } else {
                    let mut sig_read = Buf::for_overwrite(na * nh_o);
                    let mut sig_free = Buf::for_overwrite(na * nh_o);
                    self.average_strategy_view(node_idx, node, &mut sig_read, false);
                    self.average_strategy_view(node_idx, node, &mut sig_free, true);
                    let mut buf = Buf::for_overwrite(2 * nh_o);
                    for a in 0..na {
                        for j in 0..nh_o {
                            buf[j] = reach_o2[j] * sig_read[a * nh_o + j];
                            buf[nh_o + j] = reach_o2[nh_o + j] * sig_free[a * nh_o + j];
                        }
                        vals.fill(0.0);
                        self.eval_mix_into(spot.tree.children[cs + a], p, &buf, dealt, best, trust, &mut vals);
                        for i in 0..nh {
                            out[i] += vals[i];
                        }
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    /// Range-weighted value of a root cfv vector, per compatible pair (chips,
    /// net of the player's root contribution).
    fn root_value(&self, p: usize, cfv: &[f32], denom: f64) -> f64 {
        self.spot.weights[p].iter().zip(cfv).map(|(&w, &v)| w as f64 * v as f64).sum::<f64>() / denom
    }

    /// Root cfv vectors of the trust game (see `RnrCfvs`). `with_read`
    /// adds the hero's values against the read alone (readouts only).
    fn rnr_root_cfvs(&self, r: &Trust, with_read: bool) -> RnrCfvs {
        let (v, h) = (r.villain, 1 - r.villain);
        let ro = stacked(&self.spot.weights[v]);
        let mix = |best: bool| {
            let mut out = vec![0f32; self.spot.hands[h].len()];
            self.eval_mix_into(0, h, &ro, Dealt::default(), best, r.trust, &mut out);
            out
        };
        let w_h = &self.spot.weights[h];
        RnrCfvs {
            br_hero: mix(true),
            ev_hero: mix(false),
            br_villain: self.traverse_br_view(0, v, w_h, Dealt::default(), true),
            ev_villain: self.traverse_avg_view(0, v, w_h, Dealt::default(), true),
            ev_hero_vs_read: if with_read {
                self.traverse_avg(0, h, &self.spot.weights[v], Dealt::default())
            } else {
                Vec::new()
            },
        }
    }

    /// Exploitability of the trust game from its root values: the hero's
    /// best-response gain against the mixture plus the free villain's gain
    /// (weighted by his chance 1 - p), halved like `exploitability`. At
    /// p = 0 it is the ordinary exploitability of the unlocked game.
    pub fn rnr_exploitability_from(&self, r: &Trust, c: &RnrCfvs) -> f64 {
        let denom = self.pair_weight_sum();
        if denom <= 0.0 {
            return f64::NAN;
        }
        let (v, h) = (r.villain, 1 - r.villain);
        let gap_h = self.root_value(h, &c.br_hero, denom) - self.root_value(h, &c.ev_hero, denom);
        let gap_v = self.root_value(v, &c.br_villain, denom) - self.root_value(v, &c.ev_villain, denom);
        (gap_h + (1.0 - r.trust as f64) * gap_v) / 2.0
    }

    pub(crate) fn rnr_exploitability(&self, r: &Trust) -> f64 {
        let c = self.rnr_root_cfvs(r, false);
        self.rnr_exploitability_from(r, &c)
    }

    /// The dial a readout describes: the current trust (1 when unset) and
    /// the profiled villain.
    pub fn readout_trust(&self) -> Result<Trust, String> {
        let villain = self.read_villain().ok_or("lock a villain profile first")?;
        Ok(Trust { trust: self.trust.unwrap_or(1.0), villain })
    }

    /// Build a readout from root values (CPU or GPU) and the solve's
    /// exploitability.
    pub fn readout_from(&self, r: &Trust, c: &RnrCfvs, exploitability: f64) -> Result<TrustReadout, String> {
        let denom = self.pair_weight_sum();
        if denom <= 0.0 {
            return Err("empty ranges".into());
        }
        let (v, h) = (r.villain, 1 - r.villain);
        let root = &self.spot.tree.nodes[0];
        let villain_br = self.root_value(v, &c.br_villain, denom) + root.put[v];
        Ok(TrustReadout {
            trust: r.trust as f64,
            hero: h,
            villain: v,
            hero_ev_vs_read: self.root_value(h, &c.ev_hero_vs_read, denom) + root.put[h],
            hero_ev_vs_mixture: self.root_value(h, &c.ev_hero, denom) + root.put[h],
            villain_best_response_ev: villain_br,
            hero_worst_case_ev: if self.spot.tree.config.general_sum() {
                None
            } else {
                Some(root.put[0] + root.put[1] - villain_br)
            },
            exploitability,
        })
    }

    /// What the current trust level buys (EV against the read) and costs
    /// (EV a best-responding villain makes). Works at any trust, including
    /// 1 (today's full exploit), once a profile lock exists.
    pub fn trust_readout(&self) -> Result<TrustReadout, String> {
        let r = self.readout_trust()?;
        let c = self.rnr_root_cfvs(&r, true);
        self.readout_from(&r, &c, self.exploitability())
    }
}

/// Root counterfactual values of the trust game, for the hero (h) and the
/// villain (v) under average strategies.
#[derive(Debug, Clone, Default)]
pub struct RnrCfvs {
    /// Hero best response against the read/free mixture.
    pub br_hero: Vec<f32>,
    /// Hero's average strategy against the mixture.
    pub ev_hero: Vec<f32>,
    /// Free villain best response against the hero.
    pub br_villain: Vec<f32>,
    /// Free villain's average strategy against the hero.
    pub ev_villain: Vec<f32>,
    /// Hero's average strategy against the read alone (readouts only).
    pub ev_hero_vs_read: Vec<f32>,
}

/// The villain's root reach stacked twice: [read | free].
fn stacked(w: &[f32]) -> Vec<f32> {
    let mut ro = Vec::with_capacity(2 * w.len());
    ro.extend_from_slice(w);
    ro.extend_from_slice(w);
    ro
}

/// p * read + (1 - p) * free: the reach the hero actually faces.
#[inline]
fn mixed(reach_o2: &[f32], nh_o: usize, trust: f32) -> Buf {
    let mut ro = Buf::for_overwrite(nh_o);
    let (read, free) = reach_o2.split_at(nh_o);
    let rest = 1.0 - trust;
    for j in 0..nh_o {
        ro[j] = trust * read[j] + rest * free[j];
    }
    ro
}
