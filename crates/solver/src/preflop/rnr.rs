//! "Trust the read" in Preflop Lab hero mode: Restricted Nash Response
//! with an independent type per ruled seat.
//!
//! In hero mode every other seat is frozen: a seat with a profile plays it
//! (its "read"), the rest play their solved table strategy. With the dial
//! at p, each ruled seat is, independently, its read with probability p and
//! otherwise a FREE type that ignores its profile and keeps learning against
//! the hero (and the other seats as they are). The hero solves against that
//! mixture without knowing which types he faces. The free types start from
//! their seat's table regrets and learn in their own arenas.
//!
//! Engine. The traversal carries one extra reach vector per free type
//! (`reaches[n + j]` for the j-th ruled seat) next to the seats' own; at a
//! ruled seat's node the read reach follows the read's sigma and the free
//! reach the free type's. Terminals see, for every ruled seat other than the
//! traverser, the mixed reach p · read + (1 - p) · free. That is exact when
//! the terminal value is multilinear in the opponents' reaches: fold wins,
//! heads-up pots, the coupled-deck and legacy multiway models and side pots
//! (chip EV) all are. The jointly dealt 3-way table and ICM normalize the
//! ranges they combine, so there the mixture is priced as one range: an
//! approximation that matters only where two ruled seats meet in one pot.
//!
//! Anchors: an unset dial is hero mode exactly. At p = 1 the hero solves
//! today's max exploit while the free types learn a best response to it
//! (they carry no weight in the hero's values), which is what gives the
//! readout its "if the reads are wrong" number at every level.

use super::equity::{class_prob, NUM_CLASSES};
use super::{Arena, PreflopSolver, DCFR_ALPHA, DCFR_GAMMA, KIND_ACTION, PAR_DEPTH, PRUNE_REFRESH, PRUNE_WARMUP};
use rayon::prelude::*;
use serde::Serialize;

/// The free types' own arenas. Only the ruled seats' action nodes have a
/// block (`off[node]`, `u32::MAX` elsewhere), laid out like the main arenas.
pub(crate) struct PfFree {
    pub hero: usize,
    /// Ruled seats with a free type, ascending; slot j = reaches[n + j].
    pub seats: Vec<usize>,
    pub slot_of: Vec<Option<usize>>,
    pub off: Vec<u32>,
    pub regrets: Arena,
    pub strat: Arena,
    pub len: usize,
}

/// What a trust level buys and costs for the hero, in bb.
#[derive(Debug, Clone, Serialize)]
pub struct PfTrustReadout {
    pub trust: f64,
    pub hero: usize,
    /// The ruled seats the dial applies to.
    pub seats: Vec<usize>,
    /// Hero EV when every ruled seat plays its read.
    pub hero_ev_vs_read: f64,
    /// Hero EV against the trust-weighted mixture he solved for.
    pub hero_ev_vs_mixture: f64,
    /// Hero EV when every ruled seat is its free type instead: the reads
    /// are wrong and those seats adapt to the hero. With 3+ players a free
    /// seat maximizes its own EV, not the hero's loss, so this is "EV
    /// against seats that adapt", not a strict worst case.
    pub hero_ev_vs_adapting: f64,
}

impl PreflopSolver {
    /// Set the "trust the read" dial for hero mode: `Some(p)` with p in
    /// [0, 1], or `None` for plain hero mode. It applies while hero mode is
    /// on and another seat plays a profile. A new level changes the game,
    /// so (in hero mode) the hero's average strategy restarts from its
    /// current regrets, like hero entry.
    pub fn set_trust(&mut self, trust: Option<f32>) -> Result<(), String> {
        if let Some(t) = trust {
            if !t.is_finite() || !(0.0..=1.0).contains(&t) {
                return Err(format!("trust must be between 0 and 1, got {t}"));
            }
        }
        let changed = self.trust.unwrap_or(1.0) != trust.unwrap_or(1.0);
        self.trust = trust;
        if changed && self.hero.is_some() {
            self.restart_hero_average();
        }
        Ok(())
    }

    pub fn trust(&self) -> Option<f32> {
        self.trust
    }

    /// Seats the dial applies to: every other seat with a profile.
    pub fn trust_seats(&self) -> Vec<usize> {
        let Some(h) = self.hero else { return Vec::new() };
        (0..self.n).filter(|&i| i != h && self.seat_profiles[i].is_some()).collect()
    }

    /// (trust, hero) when the dial shapes the solve: hero mode, a dial set
    /// (even at 1, where the free types still learn for the readout) and
    /// at least one ruled seat.
    pub(crate) fn rnr_active(&self) -> Option<(f32, usize)> {
        let t = self.trust?;
        let h = self.hero?;
        (!self.trust_seats().is_empty()).then_some((t, h))
    }

    /// Clear the hero's average and the free types' averages, keep the
    /// regrets, and start the discount schedule again.
    fn restart_hero_average(&mut self) {
        let Some(h) = self.hero else { return };
        let blocks = self.seat_blocks(h);
        // SAFETY: &mut self, no traversal running
        unsafe {
            let ss = self.strat_sum.slice_mut();
            for (off, len) in blocks {
                ss[off..off + len].iter_mut().for_each(|v| *v = 0.0);
            }
            if let Some(f) = self.pf_free.as_ref() {
                f.strat.slice_mut().iter_mut().for_each(|v| *v = 0.0);
            }
        }
        self.iteration = 0;
        self.trust_epoch = self.trust_epoch.wrapping_add(1);
    }

    /// Give the free types their arenas while the dial is active (copies of
    /// the seats' table regrets, empty averages); drop them otherwise.
    pub(crate) fn sync_pf_free(&mut self) {
        let Some((_, hero)) = self.rnr_active() else {
            self.pf_free = None;
            return;
        };
        let seats = self.trust_seats();
        if self.pf_free.as_ref().is_some_and(|f| f.hero == hero && f.seats == seats) {
            return;
        }
        let mut slot_of = vec![None; self.n];
        for (j, &q) in seats.iter().enumerate() {
            slot_of[q] = Some(j);
        }
        let mut off = vec![u32::MAX; self.nodes.len()];
        let mut len = 0usize;
        for (i, nd) in self.nodes.iter().enumerate() {
            if nd.kind == KIND_ACTION && slot_of[nd.actor as usize].is_some() {
                off[i] = len as u32;
                len += nd.actions.len() * NUM_CLASSES;
            }
        }
        let regrets = Arena::new(len);
        // SAFETY: fresh arenas; &mut self, no traversal running
        unsafe {
            let src = self.regrets.slice();
            let dst = regrets.slice_mut();
            for (i, nd) in self.nodes.iter().enumerate() {
                if off[i] != u32::MAX {
                    let n = nd.actions.len() * NUM_CLASSES;
                    let o = off[i] as usize;
                    dst[o..o + n].copy_from_slice(&src[nd.data_off..nd.data_off + n]);
                }
            }
        }
        self.pf_free = Some(Box::new(PfFree { hero, seats, slot_of, off, regrets, strat: Arena::new(len), len }));
    }

    /// The seat a traverser index belongs to (n + j: slot j's free type).
    #[inline]
    fn seat_of(&self, f: &PfFree, tp: usize) -> usize {
        if tp < self.n { tp } else { f.seats[tp - self.n] }
    }

    fn free_current(&self, f: &PfFree, node: usize, sigma: &mut [f32]) {
        let na = self.nodes[node].actions.len();
        let o = f.off[node] as usize;
        // SAFETY: read-only view of a block only this subtree writes
        let r = unsafe { f.regrets.slice() };
        for h in 0..NUM_CLASSES {
            let mut sum = 0f32;
            for a in 0..na {
                sum += r[o + a * NUM_CLASSES + h].max(0.0);
            }
            for a in 0..na {
                sigma[a * NUM_CLASSES + h] = if sum > 1e-12 {
                    r[o + a * NUM_CLASSES + h].max(0.0) / sum
                } else {
                    1.0 / na as f32
                };
            }
        }
    }

    fn free_average(&self, f: &PfFree, node: usize, sigma: &mut [f32]) {
        let na = self.nodes[node].actions.len();
        let o = f.off[node] as usize;
        // SAFETY: as free_current
        let s = unsafe { f.strat.slice() };
        for h in 0..NUM_CLASSES {
            let mut sum = 0f32;
            for a in 0..na {
                sum += s[o + a * NUM_CLASSES + h];
            }
            for a in 0..na {
                sigma[a * NUM_CLASSES + h] = if sum > 1e-12 {
                    s[o + a * NUM_CLASSES + h] / sum
                } else {
                    1.0 / na as f32
                };
            }
        }
    }

    /// The free type's sigma at its seat's node: a point lock binds it too,
    /// its profile does not. `learn`: current (regret-matching) strategy.
    fn free_sigma(&self, f: &PfFree, node: usize, learn: bool) -> Vec<f32> {
        if let Some(l) = self.point_locks.get(&(node as u32)) {
            return l.clone();
        }
        let mut sigma = vec![0f32; self.nodes[node].actions.len() * NUM_CLASSES];
        if learn {
            self.free_current(f, node, &mut sigma);
        } else {
            self.free_average(f, node, &mut sigma);
        }
        sigma
    }

    /// The seats' reaches at a terminal for traverser seat `ps`: every ruled
    /// seat but the traverser's own mixes its two types.
    fn mixed_reaches(&self, f: &PfFree, ps: usize, reaches: &[Vec<f32>], mix: &[f32]) -> Vec<Vec<f32>> {
        let mut out: Vec<Vec<f32>> = reaches[..self.n].to_vec();
        for (j, &q) in f.seats.iter().enumerate() {
            if q == ps {
                continue;
            }
            let mix = mix[j];
            let free = &reaches[self.n + j];
            for h in 0..NUM_CLASSES {
                out[q][h] = mix * reaches[q][h] + (1.0 - mix) * free[h];
            }
        }
        out
    }

    fn rnr_root_reaches(&self, f: &PfFree) -> Vec<Vec<f32>> {
        (0..self.n + f.seats.len()).map(|_| (0..NUM_CLASSES).map(class_prob).collect()).collect()
    }

    /// One learning pass for traverser `tp` (the hero, or n + j for slot j's
    /// free type): `traverse` mode 0 with the type split.
    #[allow(clippy::too_many_arguments)]
    fn traverse_rnr(&self, f: &PfFree, node: usize, tp: usize, reaches: &mut [Vec<f32>], mix: &[f32], depth: u32) -> Vec<f32> {
        let ps = self.seat_of(f, tp);
        let nd = &self.nodes[node];
        if nd.kind != KIND_ACTION {
            let mut out = vec![0f32; NUM_CLASSES];
            let mixed = self.mixed_reaches(f, ps, reaches, mix);
            self.terminal_value(node, ps, &mixed, &mut out);
            return out;
        }
        if depth < PAR_DEPTH && self.stop_requested() {
            return vec![0f32; NUM_CLASSES];
        }
        let (actor, na, data_off, cs) = (nd.actor as usize, nd.actions.len(), nd.data_off, nd.child_start as usize);
        let slot = f.slot_of[actor];
        // the read type (the seat itself): as traverse()
        let forced = self.forced_sigma(node);
        let learning = forced.is_none() && !self.seat_frozen[actor];
        let mut sigma = vec![0f32; na * NUM_CLASSES];
        match &forced {
            Some(fs) => sigma.copy_from_slice(fs),
            None if learning => self.current_strategy(node, &mut sigma),
            None => sigma.copy_from_slice(&self.average_strategy(node)),
        }
        // the free type, learning at every node it owns
        let own_free = slot.is_some_and(|j| tp == self.n + j);
        let sig_free = slot.map(|_| self.free_sigma(f, node, true));
        let free_learns = own_free && !self.point_locks.contains_key(&(node as u32));
        let own = if own_free { sig_free.as_ref().unwrap() } else { &sigma };
        let updates = (actor == tp && learning) || free_learns;
        // prune actions no type plays, except the traverser's refresh passes
        let refresh = updates && (self.iteration < PRUNE_WARMUP || self.iteration % PRUNE_REFRESH == 0);
        let skipped: Vec<bool> = (0..na)
            .map(|a| {
                if !self.prune || na == 1 || (actor == ps && refresh) {
                    return false;
                }
                let zero = |s: &[f32]| s[a * NUM_CLASSES..(a + 1) * NUM_CLASSES].iter().all(|&x| x == 0.0);
                if actor == ps {
                    zero(own)
                } else {
                    zero(&sigma) && sig_free.as_ref().is_none_or(|s| zero(s))
                }
            })
            .collect();
        let free_ix = slot.map(|j| self.n + j);
        let (base_read, base_free) = (reaches[actor].clone(), free_ix.map(|k| reaches[k].clone()));
        let scale = |r: &mut [Vec<f32>], a: usize| {
            scale_types(r, actor, &base_read, &sigma, free_ix.zip(base_free.as_ref()).zip(sig_free.as_ref()), a)
        };
        let vals: Vec<Vec<f32>> = if depth < PAR_DEPTH && na > 1 {
            let base: &[Vec<f32>] = reaches;
            (0..na)
                .into_par_iter()
                .map(|a| {
                    if skipped[a] {
                        return vec![0f32; NUM_CLASSES];
                    }
                    let mut r = base.to_vec();
                    scale(&mut r, a);
                    self.traverse_rnr(f, self.children[cs + a] as usize, tp, &mut r, mix, depth + 1)
                })
                .collect()
        } else {
            let mut vals = Vec::with_capacity(na);
            for a in 0..na {
                if skipped[a] {
                    vals.push(vec![0f32; NUM_CLASSES]);
                    continue;
                }
                scale(reaches, a);
                vals.push(self.traverse_rnr(f, self.children[cs + a] as usize, tp, reaches, mix, depth + 1));
            }
            reaches[actor].copy_from_slice(&base_read);
            if let (Some(k), Some(b)) = (free_ix, base_free.as_ref()) {
                reaches[k].copy_from_slice(b);
            }
            vals
        };
        let mut out = vec![0f32; NUM_CLASSES];
        if actor != ps {
            for v in &vals {
                for h in 0..NUM_CLASSES {
                    out[h] += v[h];
                }
            }
            return out;
        }
        for h in 0..NUM_CLASSES {
            out[h] = (0..na).map(|a| own[a * NUM_CLASSES + h] * vals[a][h]).sum();
        }
        if updates && !(depth < PAR_DEPTH && self.stop_requested()) {
            let rp = &reaches[tp];
            // SAFETY: this node's block belongs to one subtree of any
            // enclosing parallel fan-out (see Arena)
            unsafe {
                let (regrets, strat, off) = if own_free {
                    (&f.regrets, &f.strat, f.off[node] as usize)
                } else {
                    (&self.regrets, &self.strat_sum, data_off)
                };
                for a in 0..na {
                    if skipped[a] {
                        continue;
                    }
                    for h in 0..NUM_CLASSES {
                        regrets.add(off + a * NUM_CLASSES + h, vals[a][h] - out[h]);
                        strat.add(off + a * NUM_CLASSES + h, rp[h] * own[a * NUM_CLASSES + h]);
                    }
                }
            }
        }
        out
    }

    /// Average-strategy (`.1`) and best-response (`.0`) values for traverser
    /// `tp`, with the ruled seats mixed at `mix`. The best response deviates
    /// at the traverser's nodes except where a point lock (or, for a read
    /// type, its profile) binds it, as `traverse_checkpoint` mode 2.
    fn eval_rnr(&self, f: &PfFree, node: usize, tp: usize, reaches: &mut [Vec<f32>], mix: &[f32], depth: u32) -> Option<(Vec<f32>, Vec<f32>)> {
        let ps = self.seat_of(f, tp);
        let nd = &self.nodes[node];
        if nd.kind != KIND_ACTION {
            let mut out = vec![0f32; NUM_CLASSES];
            let mixed = self.mixed_reaches(f, ps, reaches, mix);
            self.terminal_value(node, ps, &mixed, &mut out);
            return Some((out.clone(), out));
        }
        if depth < PAR_DEPTH && self.stop_requested() {
            return None;
        }
        let (actor, na, cs) = (nd.actor as usize, nd.actions.len(), nd.child_start as usize);
        let slot = f.slot_of[actor];
        let forced = self.forced_sigma(node);
        let sigma = forced.clone().unwrap_or_else(|| self.average_strategy(node));
        let own_free = slot.is_some_and(|j| tp == self.n + j);
        let sig_free = slot.map(|_| self.free_sigma(f, node, false));
        let own = if own_free { sig_free.as_ref().unwrap() } else { &sigma };
        // traverse_checkpoint's rule for a seat (mode 2 maxes even where it
        // is frozen or forced: that is its bleed; mode 3 for adaptive
        // profiles only at learning nodes); a free type is bound only by
        // point locks
        let maximize = actor == ps
            && if own_free {
                !self.point_locks.contains_key(&(node as u32))
            } else {
                !self.constrained_br(ps) || (forced.is_none() && !self.seat_frozen[actor])
            };
        let free_ix = slot.map(|j| self.n + j);
        let skipped: Vec<bool> = (0..na)
            .map(|a| {
                if !self.prune || na == 1 || (actor == ps && maximize) {
                    return false;
                }
                let zero = |s: &[f32]| s[a * NUM_CLASSES..(a + 1) * NUM_CLASSES].iter().all(|&x| x == 0.0);
                if actor == ps { zero(own) } else { zero(&sigma) && sig_free.as_ref().is_none_or(|s| zero(s)) }
            })
            .collect();
        let (base_read, base_free) = (reaches[actor].clone(), free_ix.map(|k| reaches[k].clone()));
        let scale = |r: &mut [Vec<f32>], a: usize| {
            scale_types(r, actor, &base_read, &sigma, free_ix.zip(base_free.as_ref()).zip(sig_free.as_ref()), a)
        };
        let restore = |r: &mut [Vec<f32>]| {
            r[actor].copy_from_slice(&base_read);
            if let (Some(k), Some(b)) = (free_ix, base_free.as_ref()) {
                r[k].copy_from_slice(b);
            }
        };
        let zero = || (vec![0f32; NUM_CLASSES], vec![0f32; NUM_CLASSES]);
        let vals: Vec<(Vec<f32>, Vec<f32>)> = if depth < PAR_DEPTH && na > 1 {
            let base: &[Vec<f32>] = reaches;
            (0..na)
                .into_par_iter()
                .map(|a| {
                    if skipped[a] {
                        return Some(zero());
                    }
                    let mut r = base.to_vec();
                    scale(&mut r, a);
                    self.eval_rnr(f, self.children[cs + a] as usize, tp, &mut r, mix, depth + 1)
                })
                .collect::<Option<Vec<_>>>()?
        } else {
            let mut vals = Vec::with_capacity(na);
            for a in 0..na {
                if skipped[a] {
                    vals.push(zero());
                    continue;
                }
                scale(reaches, a);
                let v = self.eval_rnr(f, self.children[cs + a] as usize, tp, reaches, mix, depth + 1);
                match v {
                    Some(v) => vals.push(v),
                    None => {
                        restore(reaches);
                        return None;
                    }
                }
            }
            restore(reaches);
            vals
        };
        let (mut br, mut avg) = zero();
        if actor != ps {
            for (b, v) in &vals {
                for h in 0..NUM_CLASSES {
                    br[h] += b[h];
                    avg[h] += v[h];
                }
            }
        } else {
            for h in 0..NUM_CLASSES {
                avg[h] = (0..na).map(|a| own[a * NUM_CLASSES + h] * vals[a].1[h]).sum();
                br[h] = if maximize {
                    vals.iter().map(|v| v.0[h]).fold(f32::NEG_INFINITY, f32::max)
                } else {
                    (0..na).map(|a| own[a * NUM_CLASSES + h] * vals[a].0[h]).sum()
                };
            }
        }
        Some((br, avg))
    }

    /// One iteration of the trust game: the hero's pass, then each free
    /// type's, then DCFR discounting of both arena sets. False when stopped.
    pub(crate) fn try_iterate_rnr(&mut self) -> bool {
        self.sync_pf_free();
        let Some((mix, hero)) = self.rnr_active() else { return true };
        let f = self.pf_free.take().expect("synced above");
        let mix = vec![mix; f.seats.len()];
        let mix = &mix[..];
        let mut passes = vec![hero];
        passes.extend((0..f.seats.len()).map(|j| self.n + j));
        for tp in passes {
            if self.stop_requested() {
                self.pf_free = Some(f);
                return false;
            }
            let mut reaches = self.rnr_root_reaches(&f);
            self.traverse_rnr(&f, 0, tp, &mut reaches, mix, 0);
        }
        if self.stop_requested() {
            self.pf_free = Some(f);
            return false;
        }
        self.iteration += 1;
        let t = self.iteration as f64;
        let pos = (t.powf(DCFR_ALPHA) / (t.powf(DCFR_ALPHA) + 1.0)) as f32;
        let neg = 0.5f32;
        let sd = ((t / (t + 1.0)).powf(DCFR_GAMMA)) as f32;
        // SAFETY: no traversal running; &mut self
        unsafe {
            for r in self.regrets.slice_mut().iter_mut() {
                *r *= if *r > 0.0 { pos } else { neg };
            }
            let ss = self.strat_sum.slice_mut();
            for nd in &self.nodes {
                if nd.kind == KIND_ACTION && !self.seat_frozen[nd.actor as usize] {
                    let len = nd.actions.len() * NUM_CLASSES;
                    ss[nd.data_off..nd.data_off + len].iter_mut().for_each(|s| *s *= sd);
                }
            }
            for r in f.regrets.slice_mut().iter_mut() {
                *r *= if *r > 0.0 { pos } else { neg };
            }
            for s in f.strat.slice_mut().iter_mut() {
                *s *= sd;
            }
        }
        self.pf_free = Some(f);
        true
    }

    fn root_value(v: &[f32]) -> f64 {
        (0..NUM_CLASSES).map(|h| class_prob(h) as f64 * v[h] as f64).sum()
    }

    /// Gaps and EVs of the trust game, per seat: the hero's against the
    /// mixture, a ruled seat's gap is its free type's (the part that
    /// learns) and its EV the trust-weighted EV of its two types; other
    /// seats as `gaps_and_evs` (bleed against their pinned play).
    pub(crate) fn rnr_gaps_and_evs(&self) -> Option<(Vec<f64>, Vec<f64>)> {
        let (mix, _) = self.rnr_active()?;
        let f = self.pf_free.as_deref()?;
        let k = f.seats.len();
        let mixes = vec![mix; k];
        let per: Vec<(f64, f64)> = (0..self.n + k)
            .into_par_iter()
            .map(|tp| {
                let mut r = self.rnr_root_reaches(f);
                let (br, avg) = self.eval_rnr(f, 0, tp, &mut r, &mixes, 0)?;
                let gap: f64 = (0..NUM_CLASSES).map(|h| class_prob(h) as f64 * (br[h] - avg[h]) as f64).sum();
                Some((gap, Self::root_value(&avg)))
            })
            .collect::<Option<Vec<_>>>()?;
        let mut gaps: Vec<f64> = per[..self.n].iter().map(|x| x.0).collect();
        let mut evs: Vec<f64> = per[..self.n].iter().map(|x| x.1).collect();
        for (j, &q) in f.seats.iter().enumerate() {
            let (g, e) = per[self.n + j];
            gaps[q] = g;
            evs[q] = mix as f64 * evs[q] + (1.0 - mix as f64) * e;
        }
        if self.stop_requested() {
            return None;
        }
        Some((gaps, evs))
    }

    /// The hero's EV against the reads, the mixture and the free types.
    pub fn trust_readout(&self) -> Result<PfTrustReadout, String> {
        let (mix, hero) = self.rnr_active().ok_or("set HERO, a seat profile and the trust dial first")?;
        let f = self.pf_free.as_deref().ok_or("solve first")?;
        let ev = |m: f32| self.hero_ev_with_types(&vec![m; f.seats.len()]);
        Ok(PfTrustReadout {
            trust: mix as f64,
            hero,
            seats: f.seats.clone(),
            hero_ev_vs_read: ev(1.0)?,
            hero_ev_vs_mixture: ev(mix)?,
            hero_ev_vs_adapting: ev(0.0)?,
        })
    }

    /// Hero EV with ruled seat `trust_seats()[j]` playing its read with
    /// probability `mix[j]` (and its free type otherwise).
    pub fn hero_ev_with_types(&self, mix: &[f32]) -> Result<f64, String> {
        let (_, hero) = self.rnr_active().ok_or("set HERO, a seat profile and the trust dial first")?;
        let f = self.pf_free.as_deref().ok_or("solve first")?;
        if mix.len() != f.seats.len() {
            return Err(format!("{} mixes for {} ruled seats", mix.len(), f.seats.len()));
        }
        let mut r = self.rnr_root_reaches(f);
        let (_, avg) = self.eval_rnr(f, 0, hero, &mut r, mix, 0).ok_or("stopped")?;
        Ok(Self::root_value(&avg))
    }

    /// Seats still learning under the dial: the hero and every free type.
    pub(crate) fn rnr_live(&self) -> Option<Vec<bool>> {
        self.rnr_active()?;
        let seats = self.trust_seats();
        Some((0..self.n).map(|i| self.hero == Some(i) || seats.contains(&i)).collect())
    }

    /// The free types' average strategy at a node (None off the dial or at
    /// another seat's node): what the seat plays if the read is wrong.
    pub fn free_strategy(&self, node: usize) -> Option<Vec<f32>> {
        let f = self.pf_free.as_deref()?;
        f.slot_of[self.nodes.get(node)?.actor as usize]?;
        Some(self.free_sigma(f, node, false))
    }
}

/// Child reaches for action `a`: the seat's read reach by its sigma, its
/// free type's (if any) by the free sigma.
fn scale_types(
    r: &mut [Vec<f32>],
    actor: usize,
    base_read: &[f32],
    sigma: &[f32],
    free: Option<((usize, &Vec<f32>), &Vec<f32>)>,
    a: usize,
) {
    for h in 0..NUM_CLASSES {
        r[actor][h] = base_read[h] * sigma[a * NUM_CLASSES + h];
    }
    if let Some(((k, base), sf)) = free {
        for h in 0..NUM_CLASSES {
            r[k][h] = base[h] * sf[a * NUM_CLASSES + h];
        }
    }
}
