//! Least-exploitable frequency locks.
//!
//! A Range lock (`LockMode::Range`) rakes the solved strategy: every hand's
//! share of the targeted actions is scaled by one common factor. That keeps
//! the solution's shape but ignores which hands are cheapest to move. This
//! module finds the strategy that hits the same aggregate frequencies while
//! giving away the least EV, in two ways:
//!
//! - **Quick** (`LockMode::Fit`): only this node changes. Using each hand's
//!   per-action EV against the current strategies, solve
//!   `max sum_i r_i w_i [sum_a s(a|i) ev_a(i) - tau KL(s_i || prior_i)]`
//!   subject to `sum_i r_i s(a|i) = t_a sum_i r_i`, where r is the player's
//!   own reach (the frequency the lock panel shows), w the card-removal
//!   weight of each hand's EV, and the prior is the solved strategy with a
//!   small uniform floor. The solution is a per-hand softmax with one price
//!   per action; a small temperature makes it close to the exact LP answer
//!   while keeping the solution's own mixes where hands are indifferent.
//!
//! - **Full** (`Solver::add_fit`): the constrained equilibrium of the whole
//!   game. The frequency constraint is linear in sequence form, so Lagrangian
//!   duality applies: there is one price per action (the "virtual bounty")
//!   such that adding it to the player's counterfactual action values at the
//!   node and solving yields the constrained solution. The price is tuned by
//!   dual ascent during the ordinary CFR solve (`fit_dual_step`), centered so
//!   that `sum_a t_a bounty_a = 0`, and never enters reported EVs or the best
//!   response. When the solve ends, `materialize_fits` turns each fit into an
//!   ordinary lock, so undo, saves and re-solves work unchanged.
//!
//! While a fit is running, best responses treat the fitted node as locked to
//! its current average strategy, which is the lock it will become; the usual
//! exploitability readout then measures the game being converged to.

use crate::cfr::Solver;
use crate::query::{normalize_freqs, rake_to_target, PathStep, Walk};
use crate::tree::KIND_ACTION;
use serde::Serialize;
use std::sync::Mutex;

/// Quick-fit temperature, as a fraction of the node's pot: hands whose EV
/// gap is well below this keep their solved mix, larger gaps decide.
pub const QUICK_TAU_POT: f64 = 0.0025;
/// Share of uniform mixed into the solved strategy before the quick fit,
/// so a hand the solution never sent down an action can still be moved.
const PRIOR_FLOOR: f64 = 0.02;
/// Dual ascent step: bounty change in pots per unit of frequency error per
/// iteration (a 10-point miss moves the bounty by 0.5% of pot).
pub const FIT_STEP_POT: f64 = 0.05;
/// Proportional term, in pots per unit of the last iteration's frequency
/// error. Regrets integrate the bounty and the bounty integrates the error;
/// without this extra push that double integrator oscillates for hundreds of
/// iterations on deep nodes.
pub const FIT_PUSH_POT: f64 = 1.0;
/// Bounties are capped at this many pots (an unreachable target would
/// otherwise grow its price without bound).
pub const FIT_BOUNTY_CAP_POT: f64 = 4.0;
/// A fit is on target once every action is within this many points.
pub const FIT_TOLERANCE: f64 = 0.005;

/// One running full fit at an action node.
pub struct FitConstraint {
    /// Canonical path to the node (orbit representative).
    pub path: Vec<PathStep>,
    pub player: usize,
    pub target: Vec<f32>,
    /// Bounty per action, in chips per unit of opponent reach at the node.
    /// The value added to action a's counterfactual values is
    /// `bounty[a] * sum_j reach_o[j]`, the same for every hand.
    pub bounty: Vec<f64>,
    /// Pot at the node (chips), for step size and display.
    pub pot: f64,
    /// Lock label once materialized.
    pub label: String,
    /// Current-iterate frequency seen by the last dual step.
    pub last_freq: Vec<f64>,
    /// Proportional term added on top of the bounty (damps the loop).
    pub(crate) push: Vec<f64>,
    /// Dual steps taken.
    pub steps: u32,
    /// The node's average strategy still holds the old solve; `prepare_fits`
    /// restarts it when the fitting solve begins.
    pub(crate) fresh: bool,
    pub(crate) acc: Mutex<FitAcc>,
}

/// Per-iteration accumulation at the node (one visit per traversal).
#[derive(Default, Clone)]
pub(crate) struct FitAcc {
    pub freq: Vec<f64>,
    pub reach: f64,
}

/// What the UI and status readout show for a running fit.
#[derive(Debug, Clone, Serialize)]
pub struct FitView {
    pub label: String,
    pub path: Vec<PathStep>,
    pub player: usize,
    pub target: Vec<f32>,
    /// Average-strategy aggregate frequency (what the lock will hold).
    pub achieved: Vec<f32>,
    /// Bounty per action, % of pot (centered on the target).
    pub bounty_pct_pot: Vec<f32>,
    /// Largest per-action miss, in frequency points (0..1).
    pub max_error: f32,
    /// The current iterate's frequency in the last iteration (what the
    /// dual ascent steers; the average follows it).
    pub current: Vec<f32>,
}

impl FitConstraint {
    /// The proportional push currently applied on top of the bounty.
    pub fn push_state(&self) -> &[f64] {
        &self.push
    }

    fn new(path: Vec<PathStep>, player: usize, target: Vec<f32>, bounty: Vec<f64>, pot: f64, label: String) -> Self {
        let na = target.len();
        let mut f = FitConstraint {
            path,
            player,
            target,
            bounty,
            pot,
            label,
            last_freq: vec![f64::NAN; na],
            push: vec![0.0; na],
            steps: 0,
            fresh: true,
            acc: Mutex::new(FitAcc { freq: vec![0.0; na], reach: 0.0 }),
        };
        f.center();
        f
    }

    /// Shift the bounty so `sum_a t_a b_a = 0` and clamp it. Once the target
    /// is met the bounty then moves hands between actions without making the
    /// node itself more or less attractive to reach.
    pub(crate) fn center(&mut self) {
        let c: f64 = self.bounty.iter().zip(&self.target).map(|(b, &t)| b * t as f64).sum();
        let cap = FIT_BOUNTY_CAP_POT * self.pot.max(1e-9);
        for b in &mut self.bounty {
            *b = (*b - c).clamp(-cap, cap);
        }
    }

    /// CPU traversal hook at the node, traverser = owner: add the bounty to
    /// the action values and record the current-iterate frequency.
    pub(crate) fn apply(&self, sigma: &[f32], reach_p: &[f32], reach_o: &[f32], vals: &mut [f32], na: usize, nh: usize) {
        let opp: f64 = reach_o.iter().map(|&r| r as f64).sum();
        let mut freq = vec![0f64; na];
        let mut tot = 0f64;
        for i in 0..nh {
            let r = reach_p[i] as f64;
            tot += r;
            for a in 0..na {
                freq[a] += r * sigma[a * nh + i] as f64;
            }
        }
        for a in 0..na {
            let add = ((self.bounty[a] + self.push[a]) * opp) as f32;
            if add != 0.0 {
                for v in &mut vals[a * nh..(a + 1) * nh] {
                    *v += add;
                }
            }
        }
        let mut acc = self.acc.lock().unwrap();
        for a in 0..na {
            acc.freq[a] += freq[a];
        }
        acc.reach += tot;
    }

    /// One dual-ascent step from an accumulated current-iterate frequency.
    pub(crate) fn step_from(&mut self, freq: &[f64], reach: f64) {
        if reach <= 1e-12 {
            return;
        }
        let step = FIT_STEP_POT * self.pot;
        let kp = FIT_PUSH_POT;
        for a in 0..self.target.len() {
            let f = freq[a] / reach;
            self.last_freq[a] = f;
            self.bounty[a] += step * (self.target[a] as f64 - f);
            self.push[a] = kp * self.pot * (self.target[a] as f64 - f);
        }
        self.center();
        let c: f64 = self.push.iter().zip(&self.target).map(|(b, &t)| b * t as f64).sum();
        for b in &mut self.push {
            *b -= c;
        }
        self.steps += 1;
    }
}

/// Least-EV-loss strategy at one node hitting `target` (Quick fit; see the
/// module docs). `evs` holds per-action EVs (chips) laid out `a * nh + i`,
/// NaN where a hand has no compatible opponent holdings; `valid` the
/// card-removal-adjusted opponent mass per hand. Returns the strategy and the
/// per-action price in EV chips (first active action at 0, uncentered).
#[allow(clippy::too_many_arguments)]
pub fn fit_least_loss(
    prior: &[f32],
    evs: &[f64],
    valid: &[f64],
    reach: &[f32],
    target: &[f32],
    tau: f64,
    na: usize,
    nh: usize,
) -> (Vec<f32>, Vec<f64>) {
    let active: Vec<bool> = target.iter().map(|&t| t > 1e-9).collect();
    let n_active = active.iter().filter(|&&a| a).count().max(1);
    let tau = tau.max(1e-9);
    let rsum: f64 = reach.iter().map(|&r| r.max(0.0) as f64).sum();

    // per-hand EV weight relative to the reach-weighted mean
    let (mut wn, mut wd) = (0f64, 0f64);
    for i in 0..nh {
        if valid[i] > 0.0 {
            wn += reach[i] as f64 * valid[i];
            wd += reach[i] as f64;
        }
    }
    let wbar = if wd > 0.0 && wn > 0.0 { wn / wd } else { 1.0 };
    let w: Vec<f64> = (0..nh).map(|i| (valid[i] / wbar).max(1e-6)).collect();

    // log base weights: log prior + EV gap / tau (inactive actions excluded)
    let mut lb = vec![f64::NEG_INFINITY; na * nh];
    for i in 0..nh {
        let mut best = f64::NEG_INFINITY;
        for a in 0..na {
            if active[a] && evs[a * nh + i].is_finite() {
                best = best.max(evs[a * nh + i]);
            }
        }
        let mut psum = 0f64;
        for a in 0..na {
            if active[a] {
                psum += prior[a * nh + i].max(0.0) as f64;
            }
        }
        for a in 0..na {
            if !active[a] {
                continue;
            }
            let p = if psum > 1e-12 { prior[a * nh + i].max(0.0) as f64 / psum } else { 1.0 / n_active as f64 };
            let p = (1.0 - PRIOR_FLOOR) * p + PRIOR_FLOOR / n_active as f64;
            let ev = evs[a * nh + i];
            let gap = if ev.is_finite() && best.is_finite() { ev - best } else { 0.0 };
            lb[a * nh + i] = p.ln() + gap / tau;
        }
    }

    let strategy = |lam: &[f64], out: &mut [f64]| {
        for i in 0..nh {
            let k = 1.0 / (w[i] * tau);
            let mut m = f64::NEG_INFINITY;
            for a in 0..na {
                if active[a] {
                    m = m.max(lb[a * nh + i] + lam[a] * k);
                }
            }
            let mut s = 0f64;
            for a in 0..na {
                let v = if active[a] { (lb[a * nh + i] + lam[a] * k - m).exp() } else { 0.0 };
                out[a * nh + i] = v;
                s += v;
            }
            for a in 0..na {
                out[a * nh + i] /= s;
            }
        }
    };
    // aggregate frequency of action a under prices lam
    let freq_of = |lam: &[f64], a: usize, buf: &mut [f64]| -> f64 {
        strategy(lam, buf);
        let mut f = 0f64;
        for i in 0..nh {
            f += reach[i].max(0.0) as f64 * buf[a * nh + i];
        }
        f / rsum
    };

    let mut lam = vec![0f64; na];
    let mut buf = vec![0f64; na * nh];
    if rsum > 1e-12 && n_active > 1 {
        let first = active.iter().position(|&a| a).unwrap();
        let others: Vec<usize> = (0..na).filter(|&a| active[a] && a != first).collect();
        for _cycle in 0..60 {
            for &a in &others {
                let t = target[a] as f64;
                // bracket the price where the aggregate crosses the target
                let mut lo = lam[a] - tau;
                let mut hi = lam[a] + tau;
                let mut probe = lam.clone();
                for _ in 0..80 {
                    probe[a] = lo;
                    if freq_of(&probe, a, &mut buf) <= t {
                        break;
                    }
                    lo -= (hi - lo) * 2.0;
                }
                for _ in 0..80 {
                    probe[a] = hi;
                    if freq_of(&probe, a, &mut buf) >= t {
                        break;
                    }
                    hi += (hi - lo) * 2.0;
                }
                for _ in 0..60 {
                    let mid = 0.5 * (lo + hi);
                    probe[a] = mid;
                    if freq_of(&probe, a, &mut buf) < t {
                        lo = mid;
                    } else {
                        hi = mid;
                    }
                }
                lam[a] = 0.5 * (lo + hi);
            }
            let mut err = 0f64;
            strategy(&lam, &mut buf);
            for &a in &others {
                let mut f = 0f64;
                for i in 0..nh {
                    f += reach[i].max(0.0) as f64 * buf[a * nh + i];
                }
                err = err.max((f / rsum - target[a] as f64).abs());
            }
            if err < 1e-7 || others.len() == 1 {
                break;
            }
        }
    }
    strategy(&lam, &mut buf);
    let mut sigma: Vec<f32> = buf.iter().map(|&v| v as f32).collect();
    // snap the last f32 rounding onto the target exactly
    rake_to_target(&mut sigma, na, nh, reach, target);
    // prices back in chips of EV (the softmax used lam / (w tau) per hand,
    // i.e. lam / w chips of EV): report lam itself
    (sigma, lam)
}

impl Solver {
    /// Per-hand action EVs at an action node owned by `p`, against the
    /// current strategies (as the node view shows them), plus each hand's
    /// card-removal-adjusted opponent mass. EVs are NaN where that mass is 0.
    pub(crate) fn action_evs(&self, walk: &Walk, p: usize) -> (Vec<f64>, Vec<f64>) {
        let spot = &*self.spot;
        let node = &spot.tree.nodes[walk.node_idx as usize];
        let na = node.num_children as usize;
        let nh = spot.hands[p].len();
        let reach_o = &walk.reach[1 - p];
        let valid = self.valid_opp_sum(p, reach_o);
        let mut evs = vec![f64::NAN; na * nh];
        for a in 0..na {
            let child = spot.tree.children[node.children_start as usize + a];
            let cfv = self.traverse_avg(child, p, reach_o, walk.dealt);
            for i in 0..nh {
                if valid[i] > 1e-9 {
                    evs[a * nh + i] = cfv[i] as f64 / valid[i] + node.put[p];
                }
            }
        }
        (evs, valid)
    }

    /// Quick fit at a walked node: the solved strategy moved onto `target`
    /// with the least EV loss. Returns (strategy, price per action in chips
    /// of per-hand EV, reach-weighted mean opponent mass).
    pub(crate) fn quick_fit(&self, walk: &Walk, target: &[f32]) -> (Vec<f32>, Vec<f64>, f64) {
        let node = &self.spot.tree.nodes[walk.node_idx as usize];
        let p = node.player as usize;
        let na = node.num_children as usize;
        let nh = self.spot.hands[p].len();
        let mut prior = vec![0f32; na * nh];
        self.solved_strategy_into(node, &mut prior);
        let (evs, valid) = self.action_evs(walk, p);
        let pot = node.put[0] + node.put[1];
        let (sigma, lam) = fit_least_loss(&prior, &evs, &valid, &walk.reach[p], target, QUICK_TAU_POT * pot, na, nh);
        let (mut wn, mut wd) = (0f64, 0f64);
        for i in 0..nh {
            if valid[i] > 0.0 {
                wn += walk.reach[p][i] as f64 * valid[i];
                wd += walk.reach[p][i] as f64;
            }
        }
        (sigma, lam, if wd > 0.0 { wn / wd } else { 0.0 })
    }

    /// Start a full (least-exploitable) fit at `path`. The node keeps
    /// learning during the next solve, steered onto `freqs` by a bounty
    /// seeded from the quick fit; `materialize_fits` locks the result. An
    /// existing lock at the node is removed (journaled, so an enclosing
    /// recorded edit can undo it). Returns the canonical node index.
    pub fn add_fit(&mut self, path: &[PathStep], freqs: &[f32], label: String) -> Result<u32, String> {
        let canon = self.canonical_path(path);
        let walk = self.walk_path(&canon)?;
        let node = &self.spot.tree.nodes[walk.node_idx as usize];
        if node.kind != KIND_ACTION {
            return Err("only action nodes can be locked".to_string());
        }
        let na = node.num_children as usize;
        if na > 8 {
            return Err("least-exploitable fits support up to 8 actions".to_string());
        }
        let p = node.player as usize;
        let pot = node.put[0] + node.put[1];
        let target = normalize_freqs(freqs, na)?;
        let (_, lam, wbar) = self.quick_fit(&walk, &target);
        let opp: f64 = walk.reach[1 - p].iter().map(|&r| r as f64).sum();
        // quick price = chips of per-hand EV, i.e. lam * wbar of counterfactual
        // value per hand; the full fit adds bounty * opp
        let scale = if opp > 1e-12 { wbar / opp } else { 0.0 };
        let bounty: Vec<f64> = lam.iter().map(|&l| l * scale).collect();
        let idx = walk.node_idx;
        self.take_lock(idx);
        self.fits.insert(idx, FitConstraint::new(canon, p, target, bounty, pot, label));
        self.mark_sym_dirty();
        Ok(idx)
    }

    /// Restart the cumulative (average) strategy at one node. A fit moves the
    /// node far from the solved strategy; without this the average would
    /// carry the old solve's weight and trail the target for hundreds of
    /// iterations, however fast the bounty settles.
    pub(crate) fn reset_node_average(&mut self, idx: u32) {
        let node = &self.spot.tree.nodes[idx as usize];
        let p = node.player as usize;
        let n = node.num_children as usize * self.spot.hands[p].len();
        let zeros = vec![0f32; n];
        unsafe { self.strat[p].write_f32(idx, node.data_offset, n, &zeros) };
    }

    /// Restart the average strategy of every fit that has not started yet
    /// (see `reset_node_average`). Returns the nodes restarted, so a GPU
    /// solver holding its own arenas can do the same. `iterate` calls this;
    /// call it before handing the solver to a GPU solve.
    pub fn prepare_fits(&mut self) -> Vec<u32> {
        let fresh: Vec<u32> = self.fits.iter().filter(|(_, f)| f.fresh).map(|(&k, _)| k).collect();
        for &idx in &fresh {
            self.reset_node_average(idx);
            self.fits.get_mut(&idx).unwrap().fresh = false;
        }
        fresh
    }

    /// Drop the running fit at `path`, if any.
    pub fn remove_fit(&mut self, path: &[PathStep]) -> Result<bool, String> {
        let walk = self.walk_path(&self.canonical_path(path))?;
        Ok(self.fits.remove(&walk.node_idx).is_some())
    }

    pub fn clear_fits(&mut self) -> usize {
        let n = self.fits.len();
        self.fits.clear();
        n
    }

    pub fn has_fits(&self) -> bool {
        !self.fits.is_empty()
    }

    /// Dual-ascent step for every fit from this iteration's accumulators.
    pub(crate) fn fit_dual_step(&mut self) {
        for fit in self.fits.values_mut() {
            let acc = std::mem::take(&mut *fit.acc.lock().unwrap());
            let na = fit.target.len();
            if acc.freq.len() == na {
                fit.step_from(&acc.freq, acc.reach);
            }
            *fit.acc.lock().unwrap() = FitAcc { freq: vec![0.0; na], reach: 0.0 };
        }
    }

    /// Average-strategy aggregate frequency at a fit node, weighted by the
    /// player's own reach (the lock panel's number).
    fn fit_achieved(&self, fit: &FitConstraint) -> Result<Vec<f32>, String> {
        let walk = self.walk_path(&fit.path)?;
        let node = &self.spot.tree.nodes[walk.node_idx as usize];
        let na = node.num_children as usize;
        let nh = self.spot.hands[fit.player].len();
        let mut s = vec![0f32; na * nh];
        self.solved_strategy_into(node, &mut s);
        let r = &walk.reach[fit.player];
        let tot: f64 = r.iter().map(|&x| x as f64).sum();
        Ok((0..na)
            .map(|a| {
                if tot <= 1e-12 {
                    return 1.0 / na as f32;
                }
                ((0..nh).map(|i| r[i] as f64 * s[a * nh + i] as f64).sum::<f64>() / tot) as f32
            })
            .collect())
    }

    /// The running fit at a (canonical) node, if any.
    pub fn fit_view_at(&self, idx: u32) -> Option<FitView> {
        self.fits.get(&idx).map(|f| self.fit_view(f))
    }

    /// Status of every running fit, sorted by label.
    pub fn fits_view(&self) -> Vec<FitView> {
        let mut v: Vec<FitView> = self.fits.values().map(|f| self.fit_view(f)).collect();
        v.sort_by(|a, b| a.label.cmp(&b.label));
        v
    }

    fn fit_view(&self, f: &FitConstraint) -> FitView {
        let achieved = self.fit_achieved(f).unwrap_or_else(|_| vec![f32::NAN; f.target.len()]);
        let max_error = achieved
            .iter()
            .zip(&f.target)
            .map(|(a, t)| if a.is_finite() { (a - t).abs() } else { 1.0 })
            .fold(0f32, f32::max);
        FitView {
            label: f.label.clone(),
            path: f.path.clone(),
            player: f.player,
            target: f.target.clone(),
            achieved,
            bounty_pct_pot: f.bounty.iter().map(|b| (b / f.pot.max(1e-9) * 100.0) as f32).collect(),
            max_error,
            current: f.last_freq.iter().map(|&x| x as f32).collect(),
        }
    }

    /// Largest per-action frequency miss over all running fits (0 if none).
    pub fn fit_max_error(&self) -> f64 {
        self.fits_view().iter().map(|f| f.max_error as f64).fold(0.0, f64::max)
    }

    /// Turn every running fit into an ordinary lock: the node's average
    /// strategy, raked onto the target to remove the small residual. Call
    /// inside `record_lock_edit` to make it one undoable edit. Returns the
    /// labels locked.
    pub fn materialize_fits(&mut self) -> Result<Vec<String>, String> {
        let fits = std::mem::take(&mut self.fits);
        let mut done = Vec::new();
        let mut items: Vec<(u32, FitConstraint)> = fits.into_iter().collect();
        items.sort_by_key(|(idx, _)| *idx);
        for (idx, fit) in items {
            let walk = self.walk_path(&fit.path)?;
            let node = &self.spot.tree.nodes[walk.node_idx as usize];
            let na = node.num_children as usize;
            let nh = self.spot.hands[fit.player].len();
            let mut s = vec![0f32; na * nh];
            self.solved_strategy_into(node, &mut s);
            rake_to_target(&mut s, na, nh, &walk.reach[fit.player], &fit.target);
            self.put_lock(idx, s, fit.label.clone());
            done.push(fit.label);
        }
        if !done.is_empty() {
            self.mark_sym_dirty();
        }
        Ok(done)
    }

    /// Bounties of the running fits, by node (for GPU upload/download).
    pub fn fit_entries(&self) -> Vec<(u32, &FitConstraint)> {
        let mut v: Vec<(u32, &FitConstraint)> = self.fits.iter().map(|(&k, f)| (k, f)).collect();
        v.sort_by_key(|(k, _)| *k);
        v
    }

    /// Overwrite a fit's dual state from the GPU solver.
    pub fn set_fit_state(&mut self, node: u32, bounty: &[f64], push: &[f64], last_freq: &[f64], steps: u32) {
        if let Some(f) = self.fits.get_mut(&node) {
            f.bounty.copy_from_slice(bounty);
            f.push.copy_from_slice(push);
            f.last_freq.copy_from_slice(last_freq);
            f.steps = steps;
        }
    }

    /// Every action node on each running fit's (canonical) line, the fit
    /// node included: what its readout reads.
    pub fn fit_line_nodes(&self) -> Vec<u32> {
        let mut out = Vec::new();
        for fit in self.fits.values() {
            for i in 0..=fit.path.len() {
                if i < fit.path.len() && !matches!(fit.path[i], PathStep::Action { .. }) {
                    continue;
                }
                if let Ok(w) = self.walk_path(&fit.path[..i]) {
                    if self.spot.tree.nodes[w.node_idx as usize].kind == KIND_ACTION {
                        out.push(w.node_idx);
                    }
                }
            }
        }
        out.sort_unstable();
        out.dedup();
        out
    }
}
