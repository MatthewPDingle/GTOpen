//! Multiway preflop solver over a postflop equity-realization model.
//!
//! Solves N-player (2..9) preflop trees EXACTLY at the action level — limps,
//! cold calls, arbitrary raise sizes, antes, rake — with postflop play priced
//! by a model instead of solved: when the flop is reached, each live player's
//! share of the pot is `pot * multiway_equity * R`, where R is a pluggable
//! realization factor (R = 1 when all-in, i.e. those terminals are exact
//! within the equity table's accuracy).
//!
//! Hands are the 169 canonical classes with combo weighting; cross-player
//! blocker effects beyond the pairwise equity table are ignored (mean-field,
//! the standard preflop-solver approximation). Multiway equity uses the
//! product approximation (exact heads-up). CFR is DCFR with the same
//! discounting constants as the postflop engine. For 3+ players CFR yields
//! "an equilibrium", not a unique GTO answer — the convergence report is the
//! per-player best-response gap against the model.

pub mod equity;
pub mod reference;
mod save;
#[cfg(feature = "gpu")]
pub mod gpu;

use equity::{class_combos, class_prob, EquityTable, NUM_CLASSES};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::cell::UnsafeCell;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

const KIND_ACTION: u8 = 0;
const KIND_FOLD_WIN: u8 = 1;
const KIND_POT_SHARE: u8 = 2;

// DCFR constants (match the postflop engine: alpha=1.5, beta=0, gamma=2)
const DCFR_ALPHA: f64 = 1.5;
const DCFR_GAMMA: f64 = 2.0;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PreflopConfig {
    /// Seats in PREFLOP acting order (e.g. UTG,HJ,CO,BTN,SB,BB).
    pub positions: Vec<String>,
    /// Starting stack in bb (v1: must be equal for all seats — no side pots).
    pub stack: f64,
    /// Blind/straddle posted per seat, aligned with `positions` (counts
    /// toward calling); e.g. [0,0,0,0,0.5,1].
    pub posts: Vec<f64>,
    /// Dead ante per seat (goes to the pot, does not count toward calls).
    #[serde(default)]
    pub ante: f64,
    /// Allow open-limps / limps behind (calls with no raise pending).
    #[serde(default)]
    pub limp: bool,
    /// First-raise TO-amounts in bb (e.g. [2.5] or [2.0, 2.5, 3.0]).
    pub open_raises: Vec<f64>,
    /// Re-raise TO-amount as multiples of the current bet (e.g. [3.0]).
    pub raise_mults: Vec<f64>,
    /// Max raises in total (open counts as the first).
    #[serde(default = "default_max_raises")]
    pub max_raises: u8,
    /// Always offer jam as a raise option.
    #[serde(default)]
    pub add_allin: bool,
    /// A raise TO more than this fraction of the stack becomes a jam.
    #[serde(default = "default_allin_threshold")]
    pub allin_threshold: f64,
    /// Rake in percent (e.g. 5.0) with a cap in bb; taken from pots that see
    /// a flop (and from preflop fold-outs too when no_flop_no_drop = false).
    #[serde(default)]
    pub rake_pct: f64,
    #[serde(default)]
    pub rake_cap: f64,
    #[serde(default = "default_true")]
    pub no_flop_no_drop: bool,
    /// "raw" (R = 1) or "static" (positional realization vs SPR).
    #[serde(default = "default_realization")]
    pub realization: String,
    /// Seats that may never raise: their action menus keep fold/limp/call/check
    /// but drop every raise and jam (prop-player / calling-station constraint
    /// studies). Other seats' menus are unaffected.
    #[serde(default)]
    pub call_only_seats: Vec<usize>,
    /// Per-seat size-menu overrides (len n when present; an empty inner list
    /// means "use the global menu"). Lets one seat explore a wide sizing menu
    /// while modeled opponents stay pinned to their observed sizes.
    #[serde(default)]
    pub open_raises_by_seat: Option<Vec<Vec<f64>>>,
    #[serde(default)]
    pub raise_mults_by_seat: Option<Vec<Vec<f64>>>,
}

impl PreflopConfig {
    fn opens_of(&self, actor: usize) -> &[f64] {
        match &self.open_raises_by_seat {
            Some(per) if !per[actor].is_empty() => &per[actor],
            _ => &self.open_raises,
        }
    }
    fn mults_of(&self, actor: usize) -> &[f64] {
        match &self.raise_mults_by_seat {
            Some(per) if !per[actor].is_empty() => &per[actor],
            _ => &self.raise_mults,
        }
    }
}

fn default_max_raises() -> u8 {
    4
}
fn default_allin_threshold() -> f64 {
    0.85
}
fn default_true() -> bool {
    true
}
fn default_realization() -> String {
    "static".to_string()
}

/// One situation bucket of a player profile: per-class mass on the passive
/// action, on a raise (at the chosen size), and on the jam; fold gets the
/// remainder. Actions that don't exist at a node degrade sensibly
/// (raise -> jam -> passive -> fold; fold -> passive when checking is free).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BucketPolicy {
    pub call: Vec<f32>,
    pub raise: Vec<f32>,
    pub jam: Vec<f32>,
    /// "min" | "max" — which raise size this player uses.
    #[serde(default = "default_raise_size")]
    pub raise_size: String,
}
fn default_raise_size() -> String {
    "max".to_string()
}

/// A seat's behavioral model: one optional policy per situation bucket
/// (None = the solver plays that bucket normally).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SeatProfile {
    pub name: String,
    pub buckets: Vec<Option<BucketPolicy>>,
    /// Size-banded VS_RAISE response: ascending (max_faced_to_bb, policy)
    /// pairs. Facing a SINGLE raise, the first band whose threshold covers
    /// the TO-amount the seat must call is applied (anything above the last
    /// threshold uses the last band); `buckets[BUCKET_VS_RAISE]` stays as
    /// the band-less fallback. Squeeze and re-raise buckets are unaffected.
    /// Defaulted so pre-band profiles and game saves keep loading.
    #[serde(default)]
    pub vs_raise_bands: Option<Vec<(f64, BucketPolicy)>>,
    /// Postflop HUD stats carried with the player (used when a lab spot is
    /// sent to the postflop solver: they compile into node locks there).
    /// Defaulted so pre-2026-07-05 saved profiles keep loading.
    #[serde(default)]
    pub postflop: Option<crate::query::PostflopStats>,
    /// How the player defends AFTER LIMPING (or calling) when a raise comes
    /// in: a policy built over its limp range at the measured after-limping
    /// continue rate (`HudStats::cont_vs_raise_limped`). None = the plain
    /// VS RAISE policy applies (built over all hands, so a junk limp range
    /// mostly folds). Defaulted so older profiles keep loading.
    #[serde(default)]
    pub limp_defense: Option<BucketPolicy>,
}

#[derive(Debug, Clone, Serialize)]
pub struct PAction {
    /// "fold" | "check" | "call" | "raise" | "jam"
    pub kind: String,
    /// TO-amount in bb (raises/jams; call amount for calls).
    pub to: f64,
    pub label: String,
}

pub struct PNode {
    pub kind: u8,
    pub actor: u8,
    pub actions: Vec<PAction>,
    pub child_start: u32,
    pub pot: f64,
    pub invested: Vec<f64>,
    pub live: u32,
    pub winner: u8,
    /// pot_share: per-seat realization weight (1.0 under "raw").
    pub r: Vec<f32>,
    /// action nodes: offset into the regret/strategy arenas.
    pub data_off: usize,
    /// Preflop aggressor when this node is reached (255 = limped/unopened).
    pub aggressor: u8,
    /// POT_SHARE terminals: postflop acting order per seat in [-0.5, +0.5]
    /// (empty elsewhere). Feeds the calibrated realization model.
    pub posf: Vec<f32>,
    /// Situation bucket (action nodes; see BUCKET_*).
    pub bucket: u8,
}

struct BuildState {
    invested: Vec<f64>,
    folded: u32,
    allin: u32,
    needs: u32,
    to_call: f64,
    last_raise: f64,
    raises: u8,
    limpers: u8,
    callers: u8,
    next_seat: usize,
    /// Last raiser/jammer so far (255 = nobody — limped or unopened pot).
    aggressor: u8,
}

/// Situation buckets for player profiles (stored per action node).
pub const BUCKET_UNOPENED: u8 = 0;
pub const BUCKET_VS_LIMPS: u8 = 1;
pub const BUCKET_VS_RAISE: u8 = 2;
pub const BUCKET_SQUEEZE: u8 = 3;
/// Facing ANY second-or-later raise: 3-bets, 4-bets, 5-bet jams. One policy
/// (and one fold-to-3bet+ stat) at every re-raise depth.
pub const BUCKET_VS_3BET: u8 = 4;
pub const NUM_BUCKETS: usize = 5;

/// A profile covering every bucket forces the seat's play everywhere —
/// such a seat never needs solved averages.
fn fully_ruled(p: &Option<SeatProfile>) -> bool {
    p.as_ref()
        .map(|prof| (0..NUM_BUCKETS).all(|b| prof.buckets.get(b).map_or(false, |x| x.is_some())))
        .unwrap_or(false)
}

/// The M5-calibrated realization model: R = clip(dot(features)), fitted
/// from this engine's own postflop solves (m5_spots/fit_phase_c.py). All
/// features are evaluable at a POT_SHARE terminal. NOTE: r_obs was measured
/// as net-of-rake EV over GROSS pot, so this R already embeds the postflop
/// rake drain — calibrated terminals must use the gross pot and skip the
/// separate rake deduction (else rake is charged twice).
#[derive(Debug, Clone)]
pub struct RealizationFit {
    spr_edges: Vec<f64>,
    /// Measured per-class realization (v4: role-standardized at a fixed
    /// facing/init reference mix, equity-curve-shrunk, domination-chained —
    /// see the fitter docstring for why raw in-context means invert ladders).
    class_base: Vec<f32>,
    c0: f32,
    b_pos: f32,
    b_spr: Vec<f32>,
    b_range_eq: f32,
    b_init: f32,
    mult_clip: (f32, f32),
    clip: (f32, f32),
}

impl RealizationFit {
    pub fn load(path: &str) -> Result<RealizationFit, String> {
        let text = std::fs::read_to_string(path).map_err(|e| format!("{path}: {e}"))?;
        let v: serde_json::Value =
            serde_json::from_str(&text).map_err(|e| format!("{path}: {e}"))?;
        if v.get("version").and_then(|x| x.as_i64()) != Some(5) {
            return Err(format!("{path}: expected fit table version 5"));
        }
        let ctx = v.get("ctx").ok_or("missing ctx")?;
        let g = |name: &str| -> Result<f32, String> {
            ctx.get(name)
                .and_then(|x| x.as_f64())
                .map(|x| x as f32)
                .ok_or_else(|| format!("missing ctx coef {name}"))
        };
        let spr_edges: Vec<f64> = v
            .get("spr_edges")
            .and_then(|x| x.as_array())
            .ok_or("missing spr_edges")?
            .iter()
            .filter_map(|x| x.as_f64())
            .collect();
        let nb = spr_edges.len() + 1;
        let class_base: Vec<f32> = v
            .get("class_base")
            .and_then(|x| x.as_array())
            .ok_or("missing class_base")?
            .iter()
            .filter_map(|x| x.as_f64().map(|f| f as f32))
            .collect();
        if class_base.len() != NUM_CLASSES {
            return Err("class_base must have 169 entries".into());
        }
        let pair = |key: &str, dflt: (f32, f32)| -> Result<(f32, f32), String> {
            match v.get(key) {
                None => Ok(dflt),
                Some(x) => {
                    // Err (not panic) on a malformed array so the caller's
                    // calibrated->static fallback still works.
                    let a = x
                        .as_array()
                        .filter(|a| a.len() == 2)
                        .ok_or_else(|| format!("{path}: {key} must be a 2-element array"))?;
                    Ok((
                        a[0].as_f64().unwrap_or(dflt.0 as f64) as f32,
                        a[1].as_f64().unwrap_or(dflt.1 as f64) as f32,
                    ))
                }
            }
        };
        Ok(RealizationFit {
            c0: g("c0")?,
            b_pos: g("pos")?,
            b_spr: (0..nb).map(|i| g(&format!("spr{i}"))).collect::<Result<_, _>>()?,
            b_range_eq: g("range_eq")?,
            b_init: g("initiative")?,
            class_base,
            mult_clip: pair("mult_clip", (0.8, 1.25))?,
            clip: pair("clip", (0.2, 2.5))?,
            spr_edges,
        })
    }

    /// Default search: REALIZATION_FIT env, then cache/ from the CWD, then
    /// relative to the crate (tests run from crates/solver).
    pub fn load_default() -> Result<RealizationFit, String> {
        if let Ok(p) = std::env::var("REALIZATION_FIT") {
            return Self::load(&p);
        }
        Self::load("cache/realization_fit.json")
            .or_else(|_| Self::load("../../cache/realization_fit.json"))
    }

    fn spr_bucket(&self, spr: f64) -> usize {
        for (i, e) in self.spr_edges.iter().enumerate() {
            if spr < *e {
                return i;
            }
        }
        self.spr_edges.len()
    }

    /// Class-independent context multiplier for one seat at a terminal.
    /// KEPT FOR ANALYSIS ONLY — see the engine note: initiative/range-eq
    /// are equilibrium correlates and must not feed back into optimization
    /// (the solver learns to buy the aggressor premium).
    pub fn seat_mult(&self, pos_frac: f32, spr: f64, range_eq: f32, init: f32) -> f32 {
        let m = self.c0
            + self.b_pos * pos_frac
            + self.b_spr[self.spr_bucket(spr)]
            + self.b_range_eq * (range_eq - 0.5)
            + self.b_init * init;
        m.clamp(self.mult_clip.0, self.mult_clip.1)
    }

    /// Full R for class k given a seat multiplier (analysis path).
    pub fn eval(&self, seat_mult: f32, k: usize) -> f32 {
        (self.class_base[k] * seat_mult).clamp(self.clip.0, self.clip.1)
    }

    /// Engine path: measured class base x an externally supplied (causally
    /// sane) positional weight, clipped.
    pub fn class_r(&self, k: usize, pos_weight: f64) -> f64 {
        (self.class_base[k] as f64 * pos_weight)
            .clamp(self.clip.0 as f64, self.clip.1 as f64)
    }

    /// Measured per-class realization (169 entries) — the GPU engine uploads
    /// this table and applies `class_r` on-device.
    pub fn class_base(&self) -> &[f32] {
        &self.class_base
    }

    /// (lo, hi) clip applied to the final R.
    pub fn clip(&self) -> (f32, f32) {
        self.clip
    }
}

/// Cold-facing-a-3-bet policy: continue only with the hands the player
/// would 3-bet a single raise with (the VS RAISE raising + jamming slice),
/// and among those split raise vs call the way his VS 3-BET+ policy does.
fn cold_vs_3bet_policy(vs_raise: &BucketPolicy, vs_3bet: &BucketPolicy) -> BucketPolicy {
    let mut out = BucketPolicy {
        call: vec![0.0; NUM_CLASSES],
        raise: vec![0.0; NUM_CLASSES],
        jam: vec![0.0; NUM_CLASSES],
        raise_size: vs_3bet.raise_size.clone(),
    };
    for h in 0..NUM_CLASSES {
        let g = |v: &Vec<f32>| v.get(h).copied().unwrap_or(0.0).max(0.0);
        let entered = (g(&vs_raise.raise) + g(&vs_raise.jam)).min(1.0);
        let (c3, r3, j3) = (g(&vs_3bet.call), g(&vs_3bet.raise), g(&vs_3bet.jam));
        let tot = c3 + r3 + j3;
        let (rs, js) = if tot > 1e-9 { (r3 / tot, j3 / tot) } else { (0.0, 0.0) };
        out.raise[h] = entered * rs;
        out.jam[h] = entered * js;
        out.call[h] = entered * (1.0 - rs - js).max(0.0);
    }
    out
}

fn bucket_of(st: &BuildState) -> u8 {
    match (st.raises, st.limpers, st.callers) {
        (0, 0, _) => BUCKET_UNOPENED,
        (0, _, _) => BUCKET_VS_LIMPS,
        (1, _, 0) => BUCKET_VS_RAISE,
        (1, _, _) => BUCKET_SQUEEZE,
        _ => BUCKET_VS_3BET,
    }
}

/// Shared-write arena for the parallel traversal. Writes are lock-free and
/// sound because concurrently-processed subtrees are disjoint: every action
/// node belongs to exactly one subtree of the parallel fan-out, so its
/// regret/strategy block is touched by exactly one thread, and reads never
/// cross into a sibling's subtree during the parallel section.
struct Arena(UnsafeCell<Vec<f32>>);
unsafe impl Sync for Arena {}
impl Arena {
    fn new(n: usize) -> Self {
        Arena(UnsafeCell::new(vec![0.0; n]))
    }
    #[inline]
    unsafe fn slice(&self) -> &[f32] {
        &*self.0.get()
    }
    #[allow(clippy::mut_from_ref)]
    #[inline]
    unsafe fn slice_mut(&self) -> &mut [f32] {
        &mut *self.0.get()
    }
    #[inline]
    unsafe fn add(&self, i: usize, v: f32) {
        (&mut *self.0.get())[i] += v;
    }
}

/// Fan subtrees across threads down to this depth; below it recursion is
/// sequential (tasks get too small to be worth scheduling).
const PAR_DEPTH: u32 = 7;
/// Regret-based pruning (Brown & Sandholm lineage): zero-mass actions'
/// subtrees are skipped. The traverser's own dead actions still get a full
/// refresh pass every PRUNE_REFRESH iterations so they can revive (DCFR's
/// beta=0 decays their negative regrets toward zero in the meantime).
const PRUNE_REFRESH: u32 = 8;
const PRUNE_WARMUP: u32 = 32;

/// The hero's pre-hero arena blocks (regrets + strategy sums) and the table's
/// iteration count, taken on hero entry so that leaving hero mode — or
/// switching to another hero — puts the seat back on its SOLVED table
/// strategy instead of the max-exploit line it learned while hero.
#[derive(Clone)]
pub(crate) struct HeroBackup {
    pub(crate) seat: usize,
    pub(crate) iteration: u32,
    pub(crate) regrets: Vec<f32>,
    pub(crate) sums: Vec<f32>,
}

pub struct PreflopSolver {
    pub cfg: PreflopConfig,
    pub eq: Arc<EquityTable>,
    pub nodes: Vec<PNode>,
    children: Vec<u32>,
    pub n: usize,
    regrets: Arena,
    strat_sum: Arena,
    arena_len: usize,
    pub iteration: u32,
    /// Regret-based pruning of zero-mass action subtrees (PREFLOP_PRUNE=0
    /// disables; tests that mirror traversals bit-for-bit turn it off).
    pub prune: bool,
    /// Loaded when realization == "calibrated"; None = fall back to static.
    pub fit: Option<Arc<RealizationFit>>,
    /// Frozen seats play their current average strategy and stop adapting.
    pub seat_frozen: Vec<bool>,
    /// Ruled seats play their profile in covered buckets.
    pub seat_profiles: Vec<Option<SeatProfile>>,
    /// Hero seat while hero mode is on. The hero is exempt from its own
    /// seat profile (a fully-ruled hero could never learn an exploit).
    pub hero: Option<usize>,
    /// Frozen flags as they were before hero mode, restored on exit.
    pre_hero_frozen: Option<Vec<bool>>,
    /// The hero's pre-hero arena blocks, taken on hero entry and restored
    /// on hero exit / hero switch (see `set_hero`).
    hero_backup: Option<HeroBackup>,
    /// Spot-specific locks: node -> exact sigma (na x 169).
    point_locks: std::collections::HashMap<u32, Vec<f32>>,
    /// Non-empty when "calibrated" was requested but the fit could not be
    /// loaded and the engine priced leaves with the static model instead —
    /// surfaced through /api/preflop/status so the downgrade is never silent.
    pub realization_note: String,
    /// Cooperative stop for long traversals: checked at the parallel
    /// fan-out nodes (depth < PAR_DEPTH), so a stop request aborts a pass
    /// within a fraction of an iteration instead of after a whole one.
    /// Once observed, the rest of that pass writes nothing (see `traverse`).
    stop_flag: Option<Arc<AtomicBool>>,
}

impl PreflopSolver {
    pub fn new(cfg: PreflopConfig, eq: Arc<EquityTable>) -> Result<Self, String> {
        let mut realization_note = String::new();
        let fit = if cfg.realization == "calibrated" {
            match RealizationFit::load_default() {
                Ok(f) => Some(Arc::new(f)),
                Err(e) => {
                    realization_note =
                        format!("calibrated realization unavailable ({e}) — priced with the static model");
                    eprintln!("calibrated realization unavailable ({e}) — using static");
                    None
                }
            }
        } else {
            None
        };
        let n = validate(&cfg)?;
        // size pre-check with full numbers (build() re-guards as a backstop)
        let est = estimate_tree(&cfg)?;
        let mb = est.arena_len as f64 * 8.0 / 1e6;
        let (lim_n, lim_mb) = (limit_nodes(), limit_arena_mb());
        if est.truncated || est.nodes > lim_n || mb > lim_mb {
            // name the limit that was actually hit and how to raise it
            let which = if est.truncated || est.nodes > lim_n {
                format!(
                    "{}{} nodes exceeds the {lim_n}-node limit (env PREFLOP_MAX_NODES raises it)",
                    if est.truncated { ">" } else { "~" },
                    est.nodes
                )
            } else {
                format!(
                    "{mb:.0} MB of solver arenas exceeds the {lim_mb:.0} MB limit \
                     (env PREFLOP_MAX_ARENA_MB raises it)"
                )
            };
            return Err(format!(
                "preflop tree too large: {which}. Trim open sizes, raise \
                 multipliers, the raise cap, or limps."
            ));
        }
        let mut s = PreflopSolver {
            cfg,
            eq,
            nodes: Vec::new(),
            children: Vec::new(),
            n,
            regrets: Arena::new(0),
            strat_sum: Arena::new(0),
            arena_len: 0,
            iteration: 0,
            prune: std::env::var("PREFLOP_PRUNE").map(|v| v != "0").unwrap_or(true),
            fit,
            seat_frozen: vec![false; n],
            seat_profiles: vec![None; n],
            hero: None,
            pre_hero_frozen: None,
            hero_backup: None,
            point_locks: std::collections::HashMap::new(),
            realization_note,
            stop_flag: None,
        };
        let init = root_state(&s.cfg, n);
        // limits sampled once — reading /proc/meminfo per action node costs
        // seconds on large builds
        s.build(init, lim_n, lim_mb)?;
        s.regrets = Arena::new(s.arena_len);
        s.strat_sum = Arena::new(s.arena_len);
        Ok(s)
    }

    /// Postflop acting order: seats with posts first (SB before BB by post
    /// size), then the rest in seat order (matches standard table layouts).
    /// Heads-up is the exception: the SB IS the button and acts LAST
    /// postflop, so the BB is OOP.
    pub fn postflop_order(&self) -> Vec<usize> {
        if self.n == 2 {
            let mut out = vec![0usize, 1];
            out.sort_by(|&a, &b| self.cfg.posts[b].partial_cmp(&self.cfg.posts[a]).unwrap());
            return out;
        }
        let mut blinds: Vec<usize> = (0..self.n).filter(|&i| self.cfg.posts[i] > 0.0).collect();
        blinds.sort_by(|&a, &b| self.cfg.posts[a].partial_cmp(&self.cfg.posts[b]).unwrap());
        let mut out = blinds.clone();
        out.extend((0..self.n).filter(|i| !blinds.contains(i)));
        out
    }

    fn live_count(&self, live: u32) -> usize {
        live.count_ones() as usize
    }

    /// Postflop acting order per live seat as a fraction in [-0.5, +0.5]
    /// (first to act = -0.5, last = +0.5; dead seats 0).
    fn pos_fracs(&self, live: u32) -> Vec<f32> {
        let mut out = vec![0f32; self.n];
        let order = self.postflop_order();
        let live_order: Vec<usize> =
            order.iter().cloned().filter(|&i| live & (1 << i) != 0).collect();
        let m = live_order.len().max(1);
        for (rank, &seat) in live_order.iter().enumerate() {
            out[seat] = if m < 2 {
                0.0
            } else {
                (rank as f64 / (m - 1) as f64 - 0.5) as f32
            };
        }
        out
    }

    fn realization_weights(&self, live: u32, invested: &[f64], pot: f64) -> Vec<f32> {
        let mut r = vec![0f32; self.n];
        let spr = {
            let mut min_left = f64::MAX;
            for i in 0..self.n {
                if live & (1 << i) != 0 {
                    min_left = min_left.min(self.cfg.stack - invested[i] + self.cfg.ante);
                }
            }
            (min_left / pot).max(0.0)
        };
        let order = self.postflop_order();
        let live_order: Vec<usize> = order.iter().cloned().filter(|&i| live & (1 << i) != 0).collect();
        let m = live_order.len().max(1);
        for (rank, &seat) in live_order.iter().enumerate() {
            let w = if self.cfg.realization == "raw" || spr <= 1e-9 || m < 2 {
                1.0
            } else {
                // positional skew: last to act (IP) over-realizes, first
                // under-realizes; grows with SPR, saturating at 8.
                let frac = rank as f64 / (m - 1) as f64 - 0.5; // -0.5 .. +0.5
                1.0 + 0.16 * frac * (spr.min(8.0) / 8.0)
            };
            r[seat] = w as f32;
        }
        r
    }

    fn next_actor(&self, st: &BuildState) -> Option<usize> {
        next_actor_of(self.n, st)
    }

    fn build(&mut self, st: BuildState, lim_nodes: u64, lim_mb: f64) -> Result<u32, String> {
        let live = ((1u32 << self.n) - 1) & !st.folded;
        let pot: f64 = st.invested.iter().sum();

        // fold-win terminal
        if self.live_count(live) == 1 {
            let winner = live.trailing_zeros() as u8;
            let idx = self.nodes.len() as u32;
            self.nodes.push(PNode {
                kind: KIND_FOLD_WIN,
                actor: winner,
                actions: Vec::new(),
                child_start: 0,
                pot,
                invested: st.invested.clone(),
                live,
                winner,
                r: Vec::new(),
                data_off: 0,
                aggressor: st.aggressor,
                posf: Vec::new(),
                bucket: 0,
            });
            return Ok(idx);
        }

        // action closed -> flop / showdown terminal
        let Some(actor) = self.next_actor(&st) else {
            let idx = self.nodes.len() as u32;
            let r = self.realization_weights(live, &st.invested, pot);
            self.nodes.push(PNode {
                kind: KIND_POT_SHARE,
                actor: 0,
                actions: Vec::new(),
                child_start: 0,
                pot,
                invested: st.invested.clone(),
                live,
                winner: 0,
                r,
                data_off: 0,
                aggressor: st.aggressor,
                posf: self.pos_fracs(live),
                bucket: 0,
            });
            return Ok(idx);
        };

        let acts = legal_actions_of(&self.cfg, &st, actor);

        let idx = self.nodes.len() as u32;
        let na = acts.len();
        self.nodes.push(PNode {
            kind: KIND_ACTION,
            actor: actor as u8,
            actions: acts.clone(),
            child_start: 0,
            pot,
            invested: st.invested.clone(),
            live,
            winner: 0,
            r: Vec::new(),
            data_off: self.arena_len,
            aggressor: st.aggressor,
            posf: Vec::new(),
            bucket: bucket_of(&st),
        });
        self.arena_len += na * NUM_CLASSES;
        if self.nodes.len() as u64 > lim_nodes
            || (self.arena_len as f64 * 8.0 / 1e6) > lim_mb
        {
            return Err("preflop tree too large; reduce sizes/raise cap or limps".into());
        }

        let mut kids: Vec<u32> = Vec::with_capacity(na);
        for a in &acts {
            let ns = next_state_of(&self.cfg, self.n, &st, actor, a);
            kids.push(self.build(ns, lim_nodes, lim_mb)?);
        }
        let cs = self.children.len() as u32;
        self.children.extend(kids);
        self.nodes[idx as usize].child_start = cs;
        Ok(idx)
    }

    // ----- strategies -----

    fn current_strategy(&self, node: usize, sigma: &mut [f32]) {
        let nd = &self.nodes[node];
        let na = nd.actions.len();
        // SAFETY: read-only view; concurrent writers only touch other subtrees
        let regrets = unsafe { self.regrets.slice() };
        for h in 0..NUM_CLASSES {
            let mut sum = 0f32;
            for a in 0..na {
                sum += regrets[nd.data_off + a * NUM_CLASSES + h].max(0.0);
            }
            if sum > 1e-12 {
                for a in 0..na {
                    sigma[a * NUM_CLASSES + h] =
                        regrets[nd.data_off + a * NUM_CLASSES + h].max(0.0) / sum;
                }
            } else {
                let u = 1.0 / na as f32;
                for a in 0..na {
                    sigma[a * NUM_CLASSES + h] = u;
                }
            }
        }
    }

    /// Exact sigma a node is forced to (point lock or seat profile), if any.
    /// The hero is exempt from its own PROFILE (not from point locks): hero
    /// mode computes the seat's free max-exploit line.
    pub(crate) fn forced_sigma(&self, node: usize) -> Option<Vec<f32>> {
        if let Some(l) = self.point_locks.get(&(node as u32)) {
            return Some(l.clone());
        }
        let nd = &self.nodes[node];
        if self.hero == Some(nd.actor as usize) {
            return None;
        }
        if let Some(prof) = &self.seat_profiles[nd.actor as usize] {
            // A seat that LIMPED (or called) and now faces a raise plays its
            // limp-defence policy — built over its limp range at the
            // after-limping continue rate — not the cold VS RAISE policy.
            if (nd.bucket == BUCKET_VS_RAISE || nd.bucket == BUCKET_SQUEEZE) && !self.is_cold(nd) {
                if let Some(ld) = prof.limp_defense.as_ref() {
                    return Some(self.policy_sigma(node, ld));
                }
            }
            // Size-banded VS_RAISE response: facing a single raise, the band
            // covering the CURRENT faced TO-amount supersedes the single
            // bucket policy (real pools tighten vs big opens; a size-blind
            // policy overvalues large hero sizes in max-exploit studies).
            // Squeeze and re-raise buckets keep their single policies.
            if nd.bucket == BUCKET_VS_RAISE {
                if let Some(bands) = prof.vs_raise_bands.as_ref().filter(|b| !b.is_empty())
                {
                    let faced = self.faced_to(node);
                    let pol = bands
                        .iter()
                        .find(|(max_to, _)| faced <= *max_to + 1e-9)
                        .map(|(_, p)| p)
                        .unwrap_or(&bands[bands.len() - 1].1);
                    return Some(self.policy_sigma(node, pol));
                }
            }
            if let Some(pol) = prof
                .buckets
                .get(nd.bucket as usize)
                .and_then(|b| b.as_ref())
            {
                // VS 3-BET+ is written for a player who RAISED and now faces a
                // re-raise ("1 - fold-to-3bet" of the hands he raised with).
                // A seat that has not put a chip in yet and faces a raise plus
                // a re-raise COLD must first have entered: gate the policy by
                // the hands he would 3-bet a single raise with. Applying the
                // flat continue rate to his whole starting range made a 40/30
                // player cold-call 3-bets with 70% of all hands.
                if nd.bucket == BUCKET_VS_3BET && self.is_cold(nd) {
                    if let Some(vr) = prof
                        .buckets
                        .get(BUCKET_VS_RAISE as usize)
                        .and_then(|b| b.as_ref())
                    {
                        return Some(self.policy_sigma(node, &cold_vs_3bet_policy(vr, pol)));
                    }
                }
                return Some(self.policy_sigma(node, pol));
            }
        }
        None
    }

    /// The actor has put nothing in voluntarily yet (blind/ante only).
    fn is_cold(&self, nd: &PNode) -> bool {
        let a = nd.actor as usize;
        nd.invested[a] <= self.cfg.posts[a] + self.cfg.ante + 1e-9
    }

    /// TO-amount (bb) the actor at `node` must call: the call action carries
    /// the build state's `to_call` verbatim. Fallback (a menu with no call
    /// can't occur at a VS_RAISE node, but stay total): the biggest live
    /// investment is the raiser's TO plus the dead ante.
    fn faced_to(&self, node: usize) -> f64 {
        let nd = &self.nodes[node];
        nd.actions
            .iter()
            .find(|a| a.kind == "call")
            .map(|a| a.to)
            .unwrap_or_else(|| {
                nd.invested.iter().cloned().fold(0.0, f64::max) - self.cfg.ante
            })
    }

    /// Compile a bucket policy into this node's concrete action menu.
    fn policy_sigma(&self, node: usize, pol: &BucketPolicy) -> Vec<f32> {
        let nd = &self.nodes[node];
        let na = nd.actions.len();
        let (mut i_fold, mut i_pass, mut i_jam) = (None, None, None);
        let mut raises: Vec<(f64, usize)> = Vec::new();
        for (i, a) in nd.actions.iter().enumerate() {
            match a.kind.as_str() {
                "fold" => i_fold = Some(i),
                "check" | "call" => i_pass = Some(i),
                "raise" => raises.push((a.to, i)),
                _ => i_jam = Some(i),
            }
        }
        raises.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        let i_raise = if raises.is_empty() {
            None
        } else if pol.raise_size == "min" {
            Some(raises[0].1)
        } else {
            Some(raises[raises.len() - 1].1)
        };
        let jam_t = i_jam.or(i_raise).or(i_pass).or(i_fold);
        let raise_t = i_raise.or(i_jam).or(i_pass).or(i_fold);
        let pass_t = i_pass.or(i_fold); // raise-or-fold spot: passive mass folds
        let fold_t = i_fold.or(i_pass); // free check: fold mass checks
        let mut sigma = vec![0f32; na * NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            let mut r = pol.raise.get(h).copied().unwrap_or(0.0).max(0.0);
            let mut j = pol.jam.get(h).copied().unwrap_or(0.0).max(0.0);
            let mut c = pol.call.get(h).copied().unwrap_or(0.0).max(0.0);
            let sum = r + j + c;
            if sum > 1.0 {
                r /= sum;
                j /= sum;
                c /= sum;
            }
            let f = (1.0 - (r + j + c)).max(0.0);
            for (target, mass) in [(raise_t, r), (jam_t, j), (pass_t, c), (fold_t, f)] {
                if let Some(a) = target {
                    if mass > 0.0 {
                        sigma[a * NUM_CLASSES + h] += mass;
                    }
                }
            }
            let tot: f32 = (0..na).map(|a| sigma[a * NUM_CLASSES + h]).sum();
            if tot > 1e-9 {
                for a in 0..na {
                    sigma[a * NUM_CLASSES + h] /= tot;
                }
            } else {
                let a = i_fold.or(i_pass).unwrap_or(0);
                sigma[a * NUM_CLASSES + h] = 1.0;
            }
        }
        sigma
    }

    /// True when any seat is frozen/ruled or a point lock exists.
    pub fn has_overrides(&self) -> bool {
        !self.point_locks.is_empty()
            || self.seat_frozen.iter().any(|&f| f)
            || self.seat_profiles.iter().any(|p| p.is_some())
    }

    /// Seats whose strategy the solve is still learning: not frozen and not
    /// fully ruled by a profile (the hero is exempt from its own profile).
    /// A frozen or ruled seat's best-response gap is its BLEED against its
    /// pinned strategy — it never converges and must not gate a solve.
    pub fn live_seats(&self) -> Vec<bool> {
        (0..self.n)
            .map(|i| {
                !self.seat_frozen[i]
                    && (self.hero == Some(i) || !fully_ruled(&self.seat_profiles[i]))
            })
            .collect()
    }

    /// Apply the table model: which seats are frozen, which play profiles.
    pub fn set_table(
        &mut self,
        frozen: Vec<bool>,
        profiles: Vec<Option<SeatProfile>>,
    ) -> Result<(), String> {
        self.set_table_impl(frozen, profiles, true)
    }

    /// `set_table` that KEEPS the learned strategy sums: for evaluating a
    /// strategy solved against one table against another (cross-exploit
    /// studies). Not for RE-SOLVE, which must start fresh (see below).
    pub fn set_table_keep(
        &mut self,
        frozen: Vec<bool>,
        profiles: Vec<Option<SeatProfile>>,
    ) -> Result<(), String> {
        self.set_table_impl(frozen, profiles, false)
    }

    fn set_table_impl(
        &mut self,
        frozen: Vec<bool>,
        profiles: Vec<Option<SeatProfile>>,
        reset: bool,
    ) -> Result<(), String> {
        if frozen.len() != self.n || profiles.len() != self.n {
            return Err("frozen/profiles must have one entry per seat".into());
        }
        for p in profiles.iter().flatten() {
            if p.buckets.len() != NUM_BUCKETS {
                return Err(format!("profiles need {NUM_BUCKETS} buckets"));
            }
            let shaped = |b: &BucketPolicy| {
                b.call.len() == NUM_CLASSES
                    && b.raise.len() == NUM_CLASSES
                    && b.jam.len() == NUM_CLASSES
            };
            for b in p.buckets.iter().flatten() {
                if !shaped(b) {
                    return Err("bucket policies need 169-class vectors".into());
                }
            }
            if let Some(bands) = &p.vs_raise_bands {
                if bands.is_empty() {
                    return Err("vs_raise_bands must not be empty (omit it instead)".into());
                }
                let mut prev = f64::NEG_INFINITY;
                for (max_to, pol) in bands {
                    if !max_to.is_finite() || *max_to <= 0.0 {
                        return Err(format!(
                            "vs_raise_bands thresholds must be finite bb amounts > 0, got {max_to}"
                        ));
                    }
                    if *max_to <= prev {
                        return Err(format!(
                            "vs_raise_bands thresholds must be strictly ascending, got {max_to} after {prev}"
                        ));
                    }
                    prev = *max_to;
                    if !shaped(pol) {
                        return Err("vs_raise_bands policies need 169-class vectors".into());
                    }
                }
            }
        }
        // The TABLE's own frozen flags and iteration count. While hero mode
        // is on, `seat_frozen` holds the hero-induced mask (everyone but the
        // hero) and `iteration` counts the hero's exploit iterations; the
        // table's flags live in `pre_hero_frozen` and its count in the hero
        // backup. Compare against THOSE, or every tendencies-only re-send
        // made in hero mode (SAVE GAME, SOLVE, a no-op APPLY) reads as a
        // changed table and wipes the whole solve.
        let table_frozen: Vec<bool> = self
            .pre_hero_frozen
            .clone()
            .unwrap_or_else(|| self.seat_frozen.clone());
        // Freezing a seat pins it to its CURRENT average strategy. A seat that
        // a profile ruled never accumulated strategy mass at its forced nodes
        // (forced nodes are not learned), so "Frozen (as solved)" used to pin
        // such a seat to average_strategy's uniform fallback — silently, and
        // every other seat then exploited a random opponent. Pin its forced
        // nodes to what the profile actually played first; a seat with no
        // mass anywhere (never solved as a live seat) is refused, as before.
        for i in 0..self.n {
            if frozen[i] && !table_frozen[i] && self.seat_profiles[i].is_some() {
                self.pin_forced_nodes(i);
            }
        }
        for i in 0..self.n {
            if frozen[i] && !table_frozen[i] && !fully_ruled(&profiles[i]) && !self.seat_has_average(i)
            {
                return Err(format!(
                    "solve first — seat {} has no solved strategy to freeze (freezing it now would pin a uniform random strategy)",
                    self.cfg.positions[i]
                ));
            }
        }
        // Re-applying an UNCHANGED table must not throw work away; a CHANGED
        // one must: without a reset, RE-SOLVE inherits the old table's
        // strategy-sum mass and the displayed averages barely move (DCFR's
        // old weight only decays as (T/(T+k))^2 — from iter 1000, 200 fresh
        // iterations still show 64% of the old strategy). Postflop tendencies
        // ride along for export only — they never touch the preflop solve —
        // and the profile name is cosmetic, so both are compared stripped.
        let strip = |ps: &[Option<SeatProfile>]| -> Vec<Option<SeatProfile>> {
            ps.iter()
                .map(|p| {
                    p.as_ref().map(|p| SeatProfile {
                        name: String::new(),
                        postflop: None,
                        limp_defense: None,
                        ..p.clone()
                    })
                })
                .collect()
        };
        let same = frozen == table_frozen
            && serde_json::to_string(&strip(&profiles)).ok()
                == serde_json::to_string(&strip(&self.seat_profiles)).ok();
        if same {
            // Unchanged table: hero mode (if any) and every arena stay as
            // they are; only the profile copies are refreshed so saves and
            // exports carry the edited tendencies / names.
            self.seat_profiles = profiles;
            return Ok(());
        }
        // A changed table supersedes hero mode. It is left WITHOUT restoring
        // the hero's pre-hero blocks: everything resets below anyway.
        self.hero = None;
        self.pre_hero_frozen = None;
        self.hero_backup = None;
        self.seat_frozen = frozen;
        self.seat_profiles = profiles;
        if reset {
            self.reset_learning();
        }
        Ok(())
    }

    /// Snapshot both arenas (regrets, strategy sums) — debugging and
    /// GPU-equivalence tooling.
    pub fn arena_snapshot(&self) -> (Vec<f32>, Vec<f32>) {
        // SAFETY: &self with no traversal running (callers hold the solver)
        unsafe { (self.regrets.slice().to_vec(), self.strat_sum.slice().to_vec()) }
    }

    /// Wipe the learning state so a changed table converges fresh. Frozen
    /// seats keep their strategy sums — that average IS their play.
    fn reset_learning(&mut self) {
        // SAFETY: &mut self — no traversal is running
        unsafe {
            for r in self.regrets.slice_mut().iter_mut() {
                *r = 0.0;
            }
            let ss = self.strat_sum.slice_mut();
            for node in &self.nodes {
                if node.kind != KIND_ACTION || self.seat_frozen[node.actor as usize] {
                    continue;
                }
                let len = node.actions.len() * NUM_CLASSES;
                for v in &mut ss[node.data_off..node.data_off + len] {
                    *v = 0.0;
                }
            }
        }
        self.iteration = 0;
    }

    /// Freeze everyone but `seat` (hero max-exploit mode). Entering hero
    /// mode backs up the hero's own arena blocks and resets its learning so
    /// the exploit chart converges fresh instead of blending into the old
    /// equilibrium average, and exempts the hero from its own seat profile
    /// (a fully-ruled hero could never learn — the "exploit" would be the
    /// profile itself). Leaving hero mode — or switching to another hero —
    /// restores the previous hero's pre-hero blocks and the table's
    /// iteration count, so that seat is frozen (or solved on) at its SOLVED
    /// table strategy, never at the max-exploit line it learned as hero;
    /// leaving also restores the frozen flags the table had before. A seat
    /// the TABLE froze (pinned "as solved") is refused as hero unless fully
    /// ruled — the entry reset would wipe the pinned average.
    pub fn set_hero(&mut self, seat: Option<usize>) -> Result<(), String> {
        match seat {
            Some(h) if h >= self.n => Err("no such seat".into()),
            // already the hero: nothing to redo (a no-op re-apply must not
            // zero the exploit solve again)
            Some(h) if self.hero == Some(h) => Ok(()),
            Some(h) => {
                // Check the TABLE's flags (pre_hero_frozen while hero mode is
                // active — every villain is hero-frozen, and switching hero
                // must stay legal). A fully-ruled seat is exempt, as in
                // set_table: its profile forces every node.
                let table_frozen: Vec<bool> = self
                    .pre_hero_frozen
                    .clone()
                    .unwrap_or_else(|| self.seat_frozen.clone());
                if table_frozen[h] && !fully_ruled(&self.seat_profiles[h]) {
                    return Err(format!(
                        "seat {} is frozen — unfreeze it before making it hero; hero mode would discard its pinned average",
                        self.cfg.positions[h]
                    ));
                }
                // freezing an unsolved, unmodeled seat = uniform random play.
                // The TABLE's iteration count is what matters: in hero mode
                // `iteration` counts the hero's exploit iterations.
                let table_iter = self
                    .hero_backup
                    .as_ref()
                    .map(|b| b.iteration)
                    .unwrap_or(self.iteration);
                if table_iter == 0 {
                    for i in 0..self.n {
                        if i != h && !table_frozen[i] && !fully_ruled(&self.seat_profiles[i]) {
                            return Err("solve the table first — hero mode freezes the other seats at their CURRENT strategies, which are uniform random before a solve".into());
                        }
                    }
                }
                if self.hero.is_none() {
                    self.pre_hero_frozen = Some(self.seat_frozen.clone());
                } else {
                    // hero switch: the outgoing hero goes back on its solved
                    // table strategy before it is frozen for the new hero
                    self.restore_hero_backup();
                }
                self.hero_backup = Some(self.snapshot_seat(h, table_iter));
                self.seat_frozen = (0..self.n).map(|i| i != h).collect();
                self.hero = Some(h);
                self.zero_seat_blocks(h);
                self.iteration = 0;
                Ok(())
            }
            None => {
                if self.hero.is_some() {
                    // back on the solved table strategy and the table's
                    // iteration count, so RE-SOLVE continues the equilibrium
                    // rather than the exploit line
                    self.restore_hero_backup();
                    self.seat_frozen = self
                        .pre_hero_frozen
                        .take()
                        .unwrap_or_else(|| vec![false; self.n]);
                    self.hero = None;
                }
                Ok(())
            }
        }
    }

    /// True when the seat's strategy sums hold ANY mass — it has been solved
    /// as a live seat at some node. All-zero sums mean average_strategy would
    /// fall back to uniform everywhere.
    fn seat_has_average(&self, seat: usize) -> bool {
        // SAFETY: &self with no traversal running (callers hold the solver)
        unsafe {
            let ss = self.strat_sum.slice();
            self.seat_blocks(seat)
                .iter()
                .any(|&(off, len)| ss[off..off + len].iter().any(|v| *v > 0.0))
        }
    }

    /// Before a ruled seat is frozen "as solved": copy the forced sigma into
    /// the strategy sums of every node the profile (or a point lock) forces
    /// and that never accumulated mass, so the pin reproduces what the seat
    /// actually played there instead of average_strategy's uniform fallback.
    fn pin_forced_nodes(&mut self, seat: usize) {
        let nodes: Vec<usize> = (0..self.nodes.len())
            .filter(|&i| self.nodes[i].kind == KIND_ACTION && self.nodes[i].actor as usize == seat)
            .collect();
        for node in nodes {
            let Some(sig) = self.forced_sigma(node) else { continue };
            let (off, len) = (self.nodes[node].data_off, self.nodes[node].actions.len() * NUM_CLASSES);
            if sig.len() != len {
                continue;
            }
            // SAFETY: &mut self — no traversal is running
            unsafe {
                let ss = self.strat_sum.slice_mut();
                if ss[off..off + len].iter().all(|v| *v <= 0.0) {
                    ss[off..off + len].copy_from_slice(&sig);
                }
            }
        }
    }

    /// (data_off, len) of every action-node block owned by `seat`.
    pub(crate) fn seat_blocks(&self, seat: usize) -> Vec<(usize, usize)> {
        self.nodes
            .iter()
            .filter(|nd| nd.kind == KIND_ACTION && nd.actor as usize == seat)
            .map(|nd| (nd.data_off, nd.actions.len() * NUM_CLASSES))
            .collect()
    }

    fn snapshot_seat(&self, seat: usize, iteration: u32) -> HeroBackup {
        let blocks = self.seat_blocks(seat);
        let total: usize = blocks.iter().map(|b| b.1).sum();
        let (mut regrets, mut sums) = (Vec::with_capacity(total), Vec::with_capacity(total));
        // SAFETY: &self with no traversal running (callers hold the solver)
        unsafe {
            let rs = self.regrets.slice();
            let ss = self.strat_sum.slice();
            for &(off, len) in &blocks {
                regrets.extend_from_slice(&rs[off..off + len]);
                sums.extend_from_slice(&ss[off..off + len]);
            }
        }
        HeroBackup { seat, iteration, regrets, sums }
    }

    /// Restore the backed-up hero blocks (if any) into the arenas and the
    /// table's iteration count. A hero-mode game saved before backups
    /// existed carries none: its hero keeps whatever its blocks hold.
    fn restore_hero_backup(&mut self) {
        let Some(b) = self.hero_backup.take() else { return };
        let blocks = self.seat_blocks(b.seat);
        let total: usize = blocks.iter().map(|x| x.1).sum();
        if b.regrets.len() != total || b.sums.len() != total {
            return; // shape mismatch (foreign save): leave the arenas alone
        }
        let mut pos = 0usize;
        // SAFETY: &mut self — no traversal is running
        unsafe {
            let rs = self.regrets.slice_mut();
            let ss = self.strat_sum.slice_mut();
            for &(off, len) in &blocks {
                rs[off..off + len].copy_from_slice(&b.regrets[pos..pos + len]);
                ss[off..off + len].copy_from_slice(&b.sums[pos..pos + len]);
                pos += len;
            }
        }
        self.iteration = b.iteration;
    }

    fn zero_seat_blocks(&mut self, seat: usize) {
        let blocks = self.seat_blocks(seat);
        // SAFETY: &mut self — no traversal is running
        unsafe {
            let rs = self.regrets.slice_mut();
            let ss = self.strat_sum.slice_mut();
            for &(off, len) in &blocks {
                rs[off..off + len].iter_mut().for_each(|v| *v = 0.0);
                ss[off..off + len].iter_mut().for_each(|v| *v = 0.0);
            }
        }
    }

    pub(crate) fn hero_backup_meta(&self) -> Option<(usize, u32)> {
        self.hero_backup.as_ref().map(|b| (b.seat, b.iteration))
    }

    pub(crate) fn set_hero_backup(&mut self, b: Option<HeroBackup>) {
        self.hero_backup = b;
    }

    /// Spot-specific lock at the node a path leads to. `policy` None freezes
    /// the node exactly as currently solved.
    pub fn lock_point(
        &mut self,
        path: &[usize],
        policy: Option<BucketPolicy>,
    ) -> Result<(), String> {
        let (node, _) = self.walk(path)?;
        if self.nodes[node].kind != KIND_ACTION {
            return Err("only action nodes can be locked".into());
        }
        let sigma = match policy {
            Some(pol) => self.policy_sigma(node, &pol),
            None => {
                // same footgun set_table/set_hero guard against: before any
                // solve the "current" average is uniform random
                if self.iteration == 0 && self.forced_sigma(node).is_none() {
                    return Err(
                        "solve first — locking a node before any solve would pin it to a uniform random strategy".into(),
                    );
                }
                self.average_strategy(node)
            }
        };
        self.point_locks.insert(node as u32, sigma);
        Ok(())
    }

    pub fn unlock_point(&mut self, path: &[usize]) -> Result<bool, String> {
        let (node, _) = self.walk(path)?;
        Ok(self.point_locks.remove(&(node as u32)).is_some())
    }

    pub fn average_strategy(&self, node: usize) -> Vec<f32> {
        if let Some(f) = self.forced_sigma(node) {
            return f;
        }
        let nd = &self.nodes[node];
        let na = nd.actions.len();
        let mut out = vec![0f32; na * NUM_CLASSES];
        // SAFETY: read-only view; concurrent writers only touch other subtrees
        let strat_sum = unsafe { self.strat_sum.slice() };
        for h in 0..NUM_CLASSES {
            let mut sum = 0f32;
            for a in 0..na {
                sum += strat_sum[nd.data_off + a * NUM_CLASSES + h];
            }
            if sum > 1e-12 {
                for a in 0..na {
                    out[a * NUM_CLASSES + h] =
                        strat_sum[nd.data_off + a * NUM_CLASSES + h] / sum;
                }
            } else {
                let u = 1.0 / na as f32;
                for a in 0..na {
                    out[a * NUM_CLASSES + h] = u;
                }
            }
        }
        out
    }

    // ----- traversal -----

    /// Rake on `pot` under the documented convention: cap > 0 caps, cap = 0
    /// means uncapped — same as the postflop engine (tree.rs) and the UI.
    fn rake_of(&self, pot: f64) -> f64 {
        let r = pot * self.cfg.rake_pct / 100.0;
        if self.cfg.rake_cap > 0.0 {
            r.min(self.cfg.rake_cap)
        } else {
            r
        }
    }

    /// Rake charged at a fold-win terminal: nothing under no-flop-no-drop,
    /// otherwise the rake on the MATCHED pot only — the winner's uncalled
    /// chips are returned before the pot is raked (as the postflop fold
    /// terminal and every cardroom do), never raked as if they were called.
    pub fn fold_win_rake(&self, nd: &PNode) -> f64 {
        if self.cfg.no_flop_no_drop {
            return 0.0;
        }
        let w = nd.winner as usize;
        let matched = nd
            .invested
            .iter()
            .enumerate()
            .filter(|(q, _)| *q != w)
            .map(|(_, v)| *v)
            .fold(0.0, f64::max);
        let uncalled = (nd.invested.get(w).copied().unwrap_or(0.0) - matched).max(0.0);
        self.rake_of(nd.pot - uncalled)
    }

    /// Terminal chip deltas for traverser p (per class), times the product of
    /// the other players' reach mass.
    fn terminal_value(&self, node: usize, p: usize, reaches: &[Vec<f32>], out: &mut [f32]) {
        let nd = &self.nodes[node];
        let mut prob = 1f64;
        for q in 0..self.n {
            if q != p {
                let s: f32 = reaches[q].iter().sum();
                prob *= s as f64;
            }
        }
        if prob <= 0.0 {
            out.iter_mut().for_each(|v| *v = 0.0);
            return;
        }
        let inv_p = nd.invested[p];
        match nd.kind {
            KIND_FOLD_WIN => {
                let rake = self.fold_win_rake(nd);
                let delta = if nd.winner as usize == p {
                    nd.pot - rake - inv_p
                } else {
                    -inv_p
                };
                out.iter_mut().for_each(|v| *v = (prob * delta) as f32);
            }
            KIND_POT_SHARE => {
                let rake = self.rake_of(nd.pot);
                let pot_eff = nd.pot - rake;
                if nd.live & (1 << p) == 0 {
                    out.iter_mut().for_each(|v| *v = (prob * -inv_p) as f32);
                    return;
                }
                // normalized opponent class distributions
                let mut dists: Vec<Vec<f32>> = Vec::new();
                for q in 0..self.n {
                    if q != p && nd.live & (1 << q) != 0 {
                        let s: f32 = reaches[q].iter().sum();
                        if s > 0.0 {
                            dists.push(reaches[q].iter().map(|&x| x / s).collect());
                        }
                    }
                }
                // spr at this terminal (0 = everyone effectively all-in:
                // no postflop play, the model is exact and R must be 1)
                let mut min_left = f64::MAX;
                for i in 0..self.n {
                    if nd.live & (1 << i) != 0 {
                        min_left =
                            min_left.min(self.cfg.stack - nd.invested[i] + self.cfg.ante);
                    }
                }
                let spr = (min_left / nd.pot).max(0.0);
                // Calibrated R: HU flop terminals with chips behind, priced as
                // MEASURED per-class realization x the mild positional weight.
                // The fit's context multiplier (initiative, range equity) is
                // deliberately NOT applied: those are equilibrium correlates,
                // and feeding them back causally lets the solver BUY the
                // aggressor premium — validation showed 100% open rates. The
                // fit was measured as net-of-rake EV over GROSS pot, so use
                // the gross pot and skip the rake deduction (no double
                // charge). Multiway terminals keep the static heuristic (the
                // postflop engine that produced the data is HU-only).
                if let (Some(fit), 2, true) =
                    (self.fit.as_ref(), nd.live.count_ones(), spr > 1e-9)
                {
                    let posw = nd.r[p] as f64; // static positional weight
                    for h in 0..NUM_CLASSES {
                        let mut eqp = 1f64;
                        for d in &dists {
                            eqp *= self.eq.eq_vs_dist(h, d) as f64;
                        }
                        let r = fit.class_r(h, posw);
                        let share = nd.pot * eqp * r;
                        out[h] = (prob * (share - inv_p)) as f32;
                    }
                    return;
                }
                let rp = nd.r[p] as f64;
                for h in 0..NUM_CLASSES {
                    let mut eqp = 1f64;
                    for d in &dists {
                        eqp *= self.eq.eq_vs_dist(h, d) as f64;
                    }
                    let share = (pot_eff * eqp * rp).min(pot_eff);
                    out[h] = (prob * (share - inv_p)) as f32;
                }
            }
            _ => unreachable!(),
        }
    }

    /// CFR traversal for traverser `p`. `mode`: 0 = update regrets/strategy
    /// (current strategies), 1 = evaluate average strategies, 2 = best
    /// response vs average strategies.
    ///
    /// Down to PAR_DEPTH the per-action subtrees are processed in parallel:
    /// each action leads into a disjoint subtree, so mode-0 writes (regrets,
    /// strategy sums — always at nodes INSIDE the subtree being traversed)
    /// can never collide, and no traversal reads a node outside its own
    /// subtree. Each task takes its own copy of the reach vectors.
    fn traverse(
        &self,
        node: usize,
        p: usize,
        reaches: &mut [Vec<f32>],
        mode: u8,
        depth: u32,
    ) -> Vec<f32> {
        let kind = self.nodes[node].kind;
        if kind != KIND_ACTION {
            let mut out = vec![0f32; NUM_CLASSES];
            self.terminal_value(node, p, reaches, &mut out);
            return out;
        }
        // Stop check at the fan-out depths only (an atomic load per task,
        // never per node). Returning zeros here is harmless because every
        // ancestor re-checks the flag before writing its regrets, so a pass
        // that observed a stop writes nothing above the abort point.
        if depth < PAR_DEPTH && self.stop_requested() {
            return vec![0f32; NUM_CLASSES];
        }
        let (actor, na, data_off, child_start) = {
            let nd = &self.nodes[node];
            (
                nd.actor as usize,
                nd.actions.len(),
                nd.data_off,
                nd.child_start as usize,
            )
        };
        let forced = self.forced_sigma(node);
        let frozen = self.seat_frozen[actor];
        let mut sigma = vec![0f32; na * NUM_CLASSES];
        match &forced {
            Some(f) => sigma.copy_from_slice(f),
            None if mode == 0 && !frozen => self.current_strategy(node, &mut sigma),
            _ => sigma.copy_from_slice(&self.average_strategy(node)),
        }

        // Regret-based pruning: an action with zero CURRENT mass for every
        // class contributes exactly zero here (every terminal below sees
        // zero reach from this actor, and the traverser's regret deltas
        // inside are zero), so the subtree can be skipped — EXCEPT where
        // the traversal needs it anyway: the traverser's own regret
        // refresh (periodic, so pruned actions can revive) and mode 2,
        // where best response deviates INTO zero-mass actions by design.
        // Strategy sums inside a pruned subtree go stale; those nodes are
        // unreachable under the current strategies (off-path).
        let updates_here = mode == 0 && forced.is_none() && !frozen;
        let skipped: Vec<bool> = if self.prune && na > 1 {
            (0..na)
                .map(|a| {
                    if actor == p {
                        if mode == 2 {
                            return false;
                        }
                        if updates_here
                            && (self.iteration < PRUNE_WARMUP
                                || self.iteration % PRUNE_REFRESH == 0)
                        {
                            return false;
                        }
                    }
                    sigma[a * NUM_CLASSES..(a + 1) * NUM_CLASSES]
                        .iter()
                        .all(|&x| x == 0.0)
                })
                .collect()
        } else {
            vec![false; na]
        };

        // whose reach scales into the children (p at own nodes for the
        // strat-sum weighting; the actor's otherwise)
        let scaled = if actor == p { p } else { actor };
        let vals: Vec<Vec<f32>> = if depth < PAR_DEPTH && na > 1 {
            let base: &[Vec<f32>] = reaches;
            (0..na)
                .into_par_iter()
                .map(|a| {
                    if skipped[a] {
                        return vec![0f32; NUM_CLASSES];
                    }
                    let mut r: Vec<Vec<f32>> = base.to_vec();
                    for h in 0..NUM_CLASSES {
                        r[scaled][h] = base[scaled][h] * sigma[a * NUM_CLASSES + h];
                    }
                    let child = self.children[child_start + a] as usize;
                    self.traverse(child, p, &mut r, mode, depth + 1)
                })
                .collect()
        } else {
            let saved = reaches[scaled].clone();
            let mut vals = Vec::with_capacity(na);
            for a in 0..na {
                if skipped[a] {
                    vals.push(vec![0f32; NUM_CLASSES]);
                    continue;
                }
                for h in 0..NUM_CLASSES {
                    reaches[scaled][h] = saved[h] * sigma[a * NUM_CLASSES + h];
                }
                let child = self.children[child_start + a] as usize;
                vals.push(self.traverse(child, p, reaches, mode, depth + 1));
            }
            reaches[scaled].copy_from_slice(&saved);
            vals
        };

        if actor == p {
            let mut out = vec![0f32; NUM_CLASSES];
            if mode == 2 {
                for h in 0..NUM_CLASSES {
                    let mut best = f32::NEG_INFINITY;
                    for v in &vals {
                        best = best.max(v[h]);
                    }
                    out[h] = best;
                }
                return out;
            }
            for h in 0..NUM_CLASSES {
                let mut v = 0f32;
                for (a, va) in vals.iter().enumerate() {
                    v += sigma[a * NUM_CLASSES + h] * va[h];
                }
                out[h] = v;
            }
            if updates_here && !(depth < PAR_DEPTH && self.stop_requested()) {
                // SAFETY: this node belongs to exactly one subtree of any
                // enclosing parallel fan-out (see Arena)
                unsafe {
                    for (a, va) in vals.iter().enumerate() {
                        if skipped[a] {
                            continue; // pruned: no counterfactual values this pass
                        }
                        for h in 0..NUM_CLASSES {
                            self.regrets
                                .add(data_off + a * NUM_CLASSES + h, va[h] - out[h]);
                            self.strat_sum.add(
                                data_off + a * NUM_CLASSES + h,
                                reaches[p][h] * sigma[a * NUM_CLASSES + h],
                            );
                        }
                    }
                }
            }
            out
        } else {
            let mut out = vec![0f32; NUM_CLASSES];
            for v in &vals {
                for h in 0..NUM_CLASSES {
                    out[h] += v[h];
                }
            }
            out
        }
    }

    fn root_reaches(&self) -> Vec<Vec<f32>> {
        (0..self.n)
            .map(|_| (0..NUM_CLASSES).map(class_prob).collect())
            .collect()
    }

    /// A frozen or fully-ruled seat's own traversal writes nothing (every
    /// regret/strategy update is gated off), so iterate() skips it outright
    /// — exact, and worth ~seat-count x in hero mode where everyone else is
    /// frozen.
    pub(crate) fn seat_static(&self, p: usize) -> bool {
        self.seat_frozen[p]
            || (self.hero != Some(p) && fully_ruled(&self.seat_profiles[p]))
    }

    /// Install (or clear) the cooperative stop flag consulted by `iterate`
    /// and `gaps_and_evs`.
    pub fn set_stop_flag(&mut self, flag: Option<Arc<AtomicBool>>) {
        self.stop_flag = flag;
    }

    #[inline]
    fn stop_requested(&self) -> bool {
        self.stop_flag
            .as_ref()
            .map_or(false, |f| f.load(Ordering::Relaxed))
    }

    pub fn iterate(&mut self) {
        self.try_iterate();
    }

    /// One DCFR iteration. Returns false — with the iteration count and
    /// discounting untouched — when the stop flag was raised part-way: the
    /// seats already swept keep their (complete) updates, the rest just
    /// missed one pass, which CFR absorbs.
    pub fn try_iterate(&mut self) -> bool {
        for p in 0..self.n {
            if self.seat_static(p) {
                continue;
            }
            if self.stop_requested() {
                return false;
            }
            let mut reaches = self.root_reaches();
            self.traverse(0, p, &mut reaches, 0, 0);
        }
        if self.stop_requested() {
            return false;
        }
        self.iteration += 1;
        // DCFR discounting
        let t = self.iteration as f64;
        let pos = (t.powf(DCFR_ALPHA) / (t.powf(DCFR_ALPHA) + 1.0)) as f32;
        let neg = 0.5f32; // beta = 0
        let sd = ((t / (t + 1.0)).powf(DCFR_GAMMA)) as f32;
        // SAFETY: no traversal is running; &mut self guarantees exclusivity
        unsafe {
            for r in self.regrets.slice_mut().iter_mut() {
                *r *= if *r > 0.0 { pos } else { neg };
            }
            if self.seat_frozen.iter().any(|&f| f) {
                // Frozen seats' strategy sums receive no additions — that
                // average IS their play (see reset_learning) — so discounting
                // them would only decay the pinned averages until they
                // underflow average_strategy's 1e-12 floor and flip to
                // uniform. Skip their blocks.
                let ss = self.strat_sum.slice_mut();
                for node in &self.nodes {
                    if node.kind != KIND_ACTION || self.seat_frozen[node.actor as usize] {
                        continue;
                    }
                    let len = node.actions.len() * NUM_CLASSES;
                    for s in &mut ss[node.data_off..node.data_off + len] {
                        *s *= sd;
                    }
                }
            } else {
                for s in self.strat_sum.slice_mut().iter_mut() {
                    *s *= sd;
                }
            }
        }
        true
    }

    /// Per-player best-response gap (bb): how much player p gains by best
    /// responding to everyone else's average strategy. -> convergence metric.
    pub fn br_gaps(&self) -> Vec<f64> {
        self.gaps_and_evs().0
    }

    /// Best-response gaps AND average-strategy EVs in one pass per player
    /// (the separate `evs()` would repeat the average traversal — checkpoint
    /// cost matters on big trees, where this pass is the visible "pause").
    pub fn gaps_and_evs(&self) -> (Vec<f64>, Vec<f64>) {
        // modes 1 and 2 never write the arenas, so the per-player passes are
        // embarrassingly parallel — this is the checkpoint "pause", cut by
        // roughly the seat count
        let pairs: Vec<(f64, f64)> = (0..self.n)
            .into_par_iter()
            .map(|p| {
                let mut reaches = self.root_reaches();
                let br = self.traverse(0, p, &mut reaches, 2, 0);
                let mut reaches = self.root_reaches();
                let avg = self.traverse(0, p, &mut reaches, 1, 0);
                let (mut g, mut v) = (0f64, 0f64);
                for h in 0..NUM_CLASSES {
                    let w = class_prob(h) as f64;
                    g += w * (br[h] - avg[h]) as f64;
                    v += w * avg[h] as f64;
                }
                (g, v)
            })
            .collect();
        pairs.into_iter().unzip()
    }

    /// EV per player (bb) under the average strategy profile.
    pub fn evs(&self) -> Vec<f64> {
        self.gaps_and_evs().1
    }

    // ----- queries -----

    /// Child node index for action `a` of action node `node`.
    pub fn child(&self, node: usize, a: usize) -> usize {
        self.children[self.nodes[node].child_start as usize + a] as usize
    }

    /// Walk a path of action indices, tracking every player's reach under the
    /// average strategies. Returns (node, reaches).
    pub fn walk(&self, path: &[usize]) -> Result<(usize, Vec<Vec<f32>>), String> {
        let mut node = 0usize;
        let mut reaches = self.root_reaches();
        for &a in path {
            let nd = &self.nodes[node];
            if nd.kind != KIND_ACTION || a >= nd.actions.len() {
                return Err("bad path".into());
            }
            let sigma = self.average_strategy(node);
            let actor = nd.actor as usize;
            for h in 0..NUM_CLASSES {
                reaches[actor][h] *= sigma[a * NUM_CLASSES + h];
            }
            node = self.children[nd.child_start as usize + a] as usize;
        }
        Ok((node, reaches))
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct PActionFreq {
    pub label: String,
    pub kind: String,
    pub to: f64,
    /// Combo-weighted aggregate frequency over the actor's reaching range.
    pub freq: f32,
}

/// One node along the walked line, for the Browse-style action ribbon:
/// every available action with its frequency, plus which one was taken.
#[derive(Debug, Clone, Serialize)]
pub struct PfHistoryStep {
    /// "action" | "fold_win" | "pot_share"
    pub kind: String,
    pub actor_pos: String,
    pub pot: f64,
    pub actions: Vec<PActionFreq>,
    pub chosen: Option<usize>,
}

#[derive(Debug, Clone, Serialize)]
pub struct PreflopNodeView {
    /// "action" | "fold_win" | "pot_share"
    pub kind: String,
    pub actor: Option<usize>,
    pub actor_pos: Option<String>,
    pub positions: Vec<String>,
    pub pot: f64,
    pub invested: Vec<f64>,
    pub live: Vec<bool>,
    pub actions: Vec<PActionFreq>,
    /// Action nodes: the actor's average strategy, na x 169 flattened.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub strategy: Option<Vec<f32>>,
    /// Fraction of each class's combos still in the actor's range (0..1).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reach: Option<Vec<f32>>,
    /// pot_share with exactly two live players: exportable to the postflop solver.
    pub exportable: bool,
    /// One entry per node along the path, plus the current node (chosen=None).
    pub history: Vec<PfHistoryStep>,
    /// Per-seat arriving range (fraction of each class's combos still held),
    /// for LIVE seats; empty vectors for folded seats. Lets the UI show the
    /// ranges that reach a terminal (e.g. the flop).
    pub reaches_all: Vec<Vec<f32>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub spr: Option<f64>,
}

#[derive(Debug, Clone, Serialize)]
pub struct PreflopExport {
    pub oop_pos: String,
    pub ip_pos: String,
    pub range_oop: String,
    pub range_ip: String,
    pub pot_bb: f64,
    pub eff_stack_bb: f64,
    /// Carried over so the postflop solve rakes the same game.
    pub rake_pct: f64,
    pub rake_cap: f64,
}

impl PreflopSolver {
    /// Reach-weighted aggregate frequency of each action at `node`.
    fn action_freqs(&self, node: usize, reaches: &[Vec<f32>]) -> Vec<PActionFreq> {
        let nd = &self.nodes[node];
        let actor = nd.actor as usize;
        let sigma = self.average_strategy(node);
        let na = nd.actions.len();
        let mut tot = 0f64;
        let mut freqs = vec![0f64; na];
        for h in 0..NUM_CLASSES {
            let w = reaches[actor][h] as f64;
            tot += w;
            for a in 0..na {
                freqs[a] += w * sigma[a * NUM_CLASSES + h] as f64;
            }
        }
        nd.actions
            .iter()
            .enumerate()
            .map(|(a, act)| PActionFreq {
                label: act.label.clone(),
                kind: act.kind.clone(),
                to: act.to,
                freq: if tot > 1e-12 { (freqs[a] / tot) as f32 } else { 0.0 },
            })
            .collect()
    }

    fn kind_str(kind: u8) -> String {
        match kind {
            KIND_ACTION => "action",
            KIND_FOLD_WIN => "fold_win",
            _ => "pot_share",
        }
        .to_string()
    }

    pub fn node_view(&self, path: &[usize]) -> Result<PreflopNodeView, String> {
        // walk the path, capturing a ribbon entry at every node passed
        let mut node = 0usize;
        let mut reaches = self.root_reaches();
        let mut history: Vec<PfHistoryStep> = Vec::with_capacity(path.len() + 1);
        for &a in path {
            let nd = &self.nodes[node];
            if nd.kind != KIND_ACTION || a >= nd.actions.len() {
                return Err("bad path".into());
            }
            history.push(PfHistoryStep {
                kind: Self::kind_str(nd.kind),
                actor_pos: self.cfg.positions[nd.actor as usize].clone(),
                pot: nd.pot,
                actions: self.action_freqs(node, &reaches),
                chosen: Some(a),
            });
            let sigma = self.average_strategy(node);
            let actor = nd.actor as usize;
            for h in 0..NUM_CLASSES {
                reaches[actor][h] *= sigma[a * NUM_CLASSES + h];
            }
            node = self.child(node, a);
        }
        {
            let nd = &self.nodes[node];
            history.push(PfHistoryStep {
                kind: Self::kind_str(nd.kind),
                actor_pos: if nd.kind == KIND_ACTION {
                    self.cfg.positions[nd.actor as usize].clone()
                } else {
                    String::new()
                },
                pot: nd.pot,
                actions: if nd.kind == KIND_ACTION {
                    self.action_freqs(node, &reaches)
                } else {
                    Vec::new()
                },
                chosen: None,
            });
        }
        let nd = &self.nodes[node];
        let live: Vec<bool> = (0..self.n).map(|i| nd.live & (1 << i) != 0).collect();
        let kind = Self::kind_str(nd.kind);
        let (actions, strategy, reach, actor, actor_pos) = if nd.kind == KIND_ACTION {
            let actor = nd.actor as usize;
            let sigma = self.average_strategy(node);
            let actions = self.action_freqs(node, &reaches);
            let reach: Vec<f32> = (0..NUM_CLASSES)
                .map(|h| (reaches[actor][h] / class_prob(h)).min(1.0))
                .collect();
            (
                actions,
                Some(sigma),
                Some(reach),
                Some(actor),
                Some(self.cfg.positions[actor].clone()),
            )
        } else {
            (Vec::new(), None, None, None, None)
        };
        let exportable = nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 2;
        let spr = if nd.kind == KIND_POT_SHARE {
            let mut min_left = f64::MAX;
            for i in 0..self.n {
                if nd.live & (1 << i) != 0 {
                    min_left = min_left.min(self.cfg.stack - nd.invested[i] + self.cfg.ante);
                }
            }
            Some((min_left / nd.pot).max(0.0))
        } else {
            None
        };
        let reaches_all: Vec<Vec<f32>> = (0..self.n)
            .map(|i| {
                if nd.live & (1 << i) != 0 {
                    (0..NUM_CLASSES)
                        .map(|h| (reaches[i][h] / class_prob(h)).min(1.0))
                        .collect()
                } else {
                    Vec::new()
                }
            })
            .collect();
        Ok(PreflopNodeView {
            kind,
            actor,
            actor_pos,
            positions: self.cfg.positions.clone(),
            pot: nd.pot,
            invested: nd.invested.clone(),
            live,
            actions,
            strategy,
            reach,
            exportable,
            spr,
            history,
            reaches_all,
        })
    }

    /// Conditional ranges + pot/stack for a heads-up flop terminal, in the
    /// postflop solver's spot format.
    pub fn export_spot(&self, path: &[usize]) -> Result<PreflopExport, String> {
        let (node, reaches) = self.walk(path)?;
        let nd = &self.nodes[node];
        if nd.kind != KIND_POT_SHARE || nd.live.count_ones() != 2 {
            return Err("export needs a flop node with exactly two live players".into());
        }
        let order = self.postflop_order();
        let live_seats: Vec<usize> =
            order.into_iter().filter(|&i| nd.live & (1 << i) != 0).collect();
        let (oop, ip) = (live_seats[0], live_seats[1]);
        let range_of = |seat: usize| -> String {
            let mut parts: Vec<String> = Vec::new();
            for h in 0..NUM_CLASSES {
                let w = (reaches[seat][h] / class_prob(h)).min(1.0);
                if w > 0.995 {
                    parts.push(equity::class_label(h));
                } else if w > 0.005 {
                    parts.push(format!("{}:{:.3}", equity::class_label(h), w));
                }
            }
            parts.join(",")
        };
        Ok(PreflopExport {
            oop_pos: self.cfg.positions[oop].clone(),
            ip_pos: self.cfg.positions[ip].clone(),
            range_oop: range_of(oop),
            range_ip: range_of(ip),
            pot_bb: nd.pot,
            eff_stack_bb: self.cfg.stack - nd.invested[oop] + self.cfg.ante,
            rake_pct: self.cfg.rake_pct,
            rake_cap: self.cfg.rake_cap,
        })
    }

    /// Reach-weighted per-seat, per-bucket, per-class propensities under the
    /// current average strategies: (weight, continue-mass, raise-mass). One
    /// full-tree pass; the raw material for equilibrium-distortion profiles.
    fn bucket_summaries(&self) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
        let sz = self.n * NUM_BUCKETS * NUM_CLASSES;
        let mut w = vec![0f64; sz];
        let mut c = vec![0f64; sz];
        let mut r = vec![0f64; sz];
        let mut reaches = self.root_reaches();
        self.sum_walk(0, &mut reaches, &mut w, &mut c, &mut r);
        (w, c, r)
    }

    fn sum_walk(
        &self,
        node: usize,
        reaches: &mut [Vec<f32>],
        w: &mut [f64],
        c: &mut [f64],
        r: &mut [f64],
    ) {
        let nd = &self.nodes[node];
        if nd.kind != KIND_ACTION {
            return;
        }
        let actor = nd.actor as usize;
        let na = nd.actions.len();
        let sigma = self.average_strategy(node);
        let base = (actor * NUM_BUCKETS + nd.bucket as usize) * NUM_CLASSES;
        for h in 0..NUM_CLASSES {
            let wt = reaches[actor][h] as f64;
            if wt <= 0.0 {
                continue;
            }
            let mut fold = 0f64;
            let mut aggr = 0f64;
            for (a, act) in nd.actions.iter().enumerate() {
                let s = sigma[a * NUM_CLASSES + h] as f64;
                match act.kind.as_str() {
                    "fold" => fold += s,
                    "raise" | "jam" => aggr += s,
                    _ => {}
                }
            }
            w[base + h] += wt;
            c[base + h] += wt * (1.0 - fold);
            r[base + h] += wt * aggr;
        }
        let saved = reaches[actor].clone();
        for a in 0..na {
            for h in 0..NUM_CLASSES {
                reaches[actor][h] = saved[h] * sigma[a * NUM_CLASSES + h];
            }
            self.sum_walk(self.child(node, a), reaches, w, c, r);
        }
        reaches[actor].copy_from_slice(&saved);
    }

    /// Generate a profile for `seat` by DISTORTING THE CURRENT EQUILIBRIUM:
    /// classes are ranked by the solve's own propensity to continue/raise in
    /// each bucket (optionally flattened toward the table average for
    /// position-blind players) and filled to the stat targets. Requires a
    /// baseline solve (iteration > 0).
    pub fn generate_profile(
        &self,
        seat: usize,
        stats: &HudStats,
        name: &str,
    ) -> Result<(SeatProfile, ImpliedStats), String> {
        if seat >= self.n {
            return Err("no such seat".into());
        }
        validate_stats(stats)?;
        if self.iteration == 0 {
            return Err("solve the unlocked game first — profiles distort that equilibrium".into());
        }
        let (w, c, _r) = self.bucket_summaries();
        let idx = |s: usize, b: usize, h: usize| (s * NUM_BUCKETS + b) * NUM_CLASSES + h;
        // Per-bucket reach mass for this seat and for the table average: how
        // much the baseline actually visits each bucket. Two failure modes
        // need fallbacks. (1) Structurally impossible seat/bucket pairs (the
        // first seat to act never faces limps; without limps it never faces
        // a single raise): the seat has zero mass while the table has plenty
        // — its share of the blend must go to the table no matter what the
        // naivete dial says. (2) Buckets NOBODY reaches (converged
        // equilibria never open-limp; HU has no squeeze spots): the
        // propensities are exact zeros or float noise, and ranking noise
        // fills ranges bottom-up (class-index order starts at 22/32o) — no
        // equilibrium to distort, so ordering and targets fade to card
        // appeal / human defaults. 1e-3 = ~0.1% of hands ever getting there.
        let mut m_mine = [0f64; NUM_BUCKETS];
        let mut m_table = [0f64; NUM_BUCKETS];
        for b in 0..NUM_BUCKETS {
            for h in 0..NUM_CLASSES {
                m_mine[b] += w[idx(seat, b, h)];
                for q in 0..self.n {
                    m_table[b] += w[idx(q, b, h)];
                }
            }
            m_table[b] /= self.n as f64;
        }
        let mine_conf: Vec<f64> =
            (0..NUM_BUCKETS).map(|b| (m_mine[b] / 1e-3).min(1.0)).collect();
        let mine_share: Vec<f64> =
            (0..NUM_BUCKETS).map(|b| (1.0 - stats.flatten) * mine_conf[b]).collect();
        let bucket_conf: Vec<f64> = (0..NUM_BUCKETS)
            .map(|b| {
                let mass = mine_share[b] * m_mine[b] + (1.0 - mine_share[b]) * m_table[b];
                (mass / 1e-3).min(1.0)
            })
            .collect();
        // per-class propensity, split by source
        let mine_table = |b: usize, h: usize, of: &Vec<f64>| -> (f64, f64) {
            let mine = if w[idx(seat, b, h)] > 1e-12 {
                of[idx(seat, b, h)] / w[idx(seat, b, h)]
            } else {
                0.0
            };
            let (mut tw, mut tv) = (0f64, 0f64);
            for q in 0..self.n {
                tw += w[idx(q, b, h)];
                tv += of[idx(q, b, h)];
            }
            let table = if tw > 1e-12 { tv / tw } else { 0.0 };
            (mine, table)
        };
        // combo-weighted baseline continue% of a bucket at an EXPLICIT
        // seat/table blend — ratios between buckets must compare the same
        // source, or a seat with no vs-raise data of its own ends up with
        // the table's (BB-defense-wide) numerator over its own tight
        // opening-rate denominator and defends more than its VPIP.
        let cont_share = |b: usize, ms: f64| -> f64 {
            let mut num = 0f64;
            for h in 0..NUM_CLASSES {
                let (mine, table) = mine_table(b, h, &c);
                num += class_combos(h) as f64 * (ms * mine + (1.0 - ms) * table);
            }
            num / 1326.0
        };
        let fourbet = stats.fourbet.unwrap_or(stats.threebet * 0.4);
        let mut targets = [(0f64, 0f64); NUM_BUCKETS]; // (continue, raise)
        // Entry buckets: the measured first-in / vs-limpers rates when
        // given; else PFR raises and the VPIP−PFR gap limps — the only
        // reading of VPIP/PFR alone, and a poor one for regs, whose gap is
        // calls (a 17/12 TAG open-limps ~2%, not 5%).
        let gap = ((stats.vpip - stats.pfr) / 100.0).max(0.0);
        let fi_raise = stats.open_raise.map(|v| v / 100.0).unwrap_or(stats.pfr / 100.0);
        let fi_limp = stats.open_limp.map(|v| v / 100.0).unwrap_or(gap);
        targets[BUCKET_UNOPENED as usize] = ((fi_raise + fi_limp).min(1.0), fi_raise.min(1.0));
        let vl_raise = stats.iso_raise.map(|v| v / 100.0).unwrap_or(stats.pfr / 100.0);
        let vl_limp = stats.limp_behind.map(|v| v / 100.0).unwrap_or(gap);
        targets[BUCKET_VS_LIMPS as usize] = ((vl_raise + vl_limp).min(1.0), vl_raise.min(1.0));
        // Continue-vs-aggression targets: the equilibrium's tightening ratio
        // (bucket continue% over unopened continue%, SAME data source for
        // both) applied to the player's VPIP, blended toward a plain human
        // default (a fraction of VPIP) by naiveté — naive players don't
        // tighten the way equilibrium economics say — and by bucket
        // confidence, so an unreached bucket stays sane when the profile is
        // saved and applied to a game where it IS live.
        let gated_cont = |b: u8, dflt_frac: f64, floor: f64| -> f64 {
            let bi = b as usize;
            // Both shares at the SAME seat/table blend, limited by the WEAKER
            // of the two seat-confidences: a seat with no data of its own in
            // either bucket (the last blind never acts in an unopened pot;
            // the first seat never faces limps) must fall back to the table
            // for both, or a real propensity gets divided by a structural
            // zero and the target saturates at 100%.
            let ms = mine_share[bi].min(mine_share[BUCKET_UNOPENED as usize]);
            let ratio = cont_share(bi, ms) / cont_share(BUCKET_UNOPENED as usize, ms).max(0.01);
            let obs = (ratio * stats.vpip / 100.0).min(1.0);
            let dflt = stats.vpip / 100.0 * dflt_frac;
            let w_eq = bucket_conf[bi] * (1.0 - stats.flatten);
            (w_eq * obs + (1.0 - w_eq) * dflt).clamp(floor, 1.0)
        };
        targets[BUCKET_VS_RAISE as usize] = (
            match (stats.cont_vs_raise, &stats.cont_vs_raise_bands) {
                (Some(c), _) => (c / 100.0).clamp(stats.threebet / 100.0, 1.0),
                // Bands without the single stat: anchor the band-less
                // fallback policy at the bands' mean — a mid response —
                // instead of a VPIP blend that never saw the measured data.
                (None, Some(bands)) => {
                    let mean =
                        bands.iter().map(|(_, p)| p).sum::<f64>() / bands.len() as f64;
                    (mean / 100.0).clamp(stats.threebet / 100.0, 1.0)
                }
                (None, None) => gated_cont(BUCKET_VS_RAISE, 0.65, stats.threebet / 100.0),
            },
            stats.threebet / 100.0,
        );
        targets[BUCKET_SQUEEZE as usize] = (
            match stats.cont_squeeze {
                Some(c) => (c / 100.0).clamp(stats.squeeze / 100.0, 1.0),
                None => gated_cont(BUCKET_SQUEEZE, 0.5, stats.squeeze / 100.0),
            },
            stats.squeeze / 100.0,
        );
        targets[BUCKET_VS_3BET as usize] = (
            (1.0 - stats.fold_to_3bet / 100.0).clamp(0.0, 1.0),
            (fourbet / 100.0).clamp(0.0, 1.0),
        );
        // Position: one VPIP/PFR is the player's AVERAGE over the seats. A
        // fixed GTO prior says how much wider each seat opens than the table
        // mean (100bb cash RFI widths: 9-max UTG ~11% ... BTN ~42%, SB ~35%;
        // an n-handed table takes the LAST n-2 non-blind widths, so 6-max
        // UTG ~16%), and naivete says how much of that shape the player has
        // (0 = fully positional, 1 = the same width everywhere). Deliberately
        // NOT read off the baseline: with profiles installed the baseline is
        // seven identical ruled seats plus one exploiting hero, which is no
        // positional shape at all. Applied in full to the first-in bucket
        // and damped (sqrt) to the over-limpers bucket, where the multiway
        // pot flattens position.
        let prior: Vec<f64> = {
            const RFI: [f64; 7] = [11.0, 12.5, 14.0, 16.0, 19.5, 26.0, 42.0]; // 9-max UTG..BTN
            const SB_RFI: f64 = 35.0;
            let non_blind: Vec<usize> =
                (0..self.n).filter(|&q| self.cfg.posts[q] <= 0.0).collect();
            let mut p = vec![f64::NAN; self.n];
            for (j, &q) in non_blind.iter().rev().enumerate() {
                p[q] = RFI[RFI.len().saturating_sub(j + 1)]; // BTN = 42, then 26, ...; extras = 11
            }
            // blinds: a SB raises first-in ~35% when folded to; the last
            // blind (BB) never opens first-in and takes no shape
            let blinds: Vec<usize> =
                (0..self.n).filter(|&q| self.cfg.posts[q] > 0.0).collect();
            for (j, &q) in blinds.iter().enumerate() {
                p[q] = if j + 1 < blinds.len() { SB_RFI } else { f64::NAN };
            }
            let vals: Vec<f64> = p.iter().cloned().filter(|v| !v.is_nan()).collect();
            let mean = if vals.is_empty() {
                1.0
            } else {
                vals.iter().sum::<f64>() / vals.len() as f64
            };
            p.into_iter()
                .map(|v| if v.is_nan() { 1.0 } else { (v / mean).clamp(0.3, 3.0) })
                .collect()
        };
        let pos_factor = |b: usize| -> f64 {
            let pos = if b == BUCKET_VS_LIMPS as usize { prior[seat].sqrt() } else { prior[seat] };
            (1.0 - stats.flatten) * pos + stats.flatten
        };
        for b in [BUCKET_UNOPENED as usize, BUCKET_VS_LIMPS as usize] {
            let (tc, tr) = targets[b];
            let f = pos_factor(b);
            let tc2 = (tc * f).min(1.0);
            let tr2 = (tr * f).min(tc2);
            targets[b] = (tc2, tr2);
        }

        // raw card appeal (equity vs random): how naive players rank hands —
        // high-card heavy, domination-blind
        let strength: Vec<f64> = (0..NUM_CLASSES)
            .map(|h| {
                (0..NUM_CLASSES)
                    .map(|j| class_prob(j) as f64 * self.eq.eq(h, j) as f64)
                    .sum()
            })
            .collect();
        let rank_positions = |score: &dyn Fn(usize) -> f64| -> Vec<f64> {
            let mut idxs: Vec<usize> = (0..NUM_CLASSES).collect();
            idxs.sort_by(|&x, &y| score(y).partial_cmp(&score(x)).unwrap());
            let mut rank = vec![0f64; NUM_CLASSES];
            for (pos, &h) in idxs.iter().enumerate() {
                rank[h] = pos as f64;
            }
            rank
        };
        let rank_str = rank_positions(&|h| strength[h]);

        // One bucket policy at an explicit (continue, raise) target over a
        // REACHING RANGE `weight` (combos of each class that actually reach
        // the bucket: the full deck for cold spots, the player's own raising
        // range when it faces a 3-bet, its limp range when a limp gets
        // raised). Targets are fractions of that range; the policy is the
        // per-class probability given the class is held. Used for every
        // per-bucket policy and again per VS_RAISE size band.
        let build_policy_w = |b: usize, t_cont: f64, t_raise: f64, weight: &[f64]| -> BucketPolicy {
            let total: f64 = weight.iter().sum();
            // Continuing range ordering: blend the equilibrium's playability
            // ranking with raw card appeal by naiveté. Equilibrium defense
            // vs raises is POLARIZED (calls 53s, folds Q9o — domination is
            // priced in); naive players do the opposite, so their ranges
            // must be appeal-ordered or whale call ranges come out absurd.
            // The GTO ordering comes from the reference solve
            // (reference.rs: a clean 9-max 100bb equilibrium), by bucket:
            // what it opens with for the entry buckets, what it defends
            // with (call + 3-bet) facing a raise. NOT the current solve —
            // with profiles installed that is the previous profile's own
            // policy (self-referential) or an exploiting hero, and an
            // unconverged one is noise. Re-raise buckets go by strength: a
            // human continues vs a 3-bet with his strongest hands.
            let vs_reraise = b == BUCKET_VS_3BET as usize;
            let ref_cont = |h: usize| -> f64 {
                match b as u8 {
                    BUCKET_VS_RAISE | BUCKET_SQUEEZE => {
                        (reference::CALL_SCORE[h] + reference::THREEBET_SCORE[h]) as f64
                    }
                    _ => reference::OPEN_SCORE[h] as f64,
                }
            };
            let rank_eq = rank_positions(&|h| ref_cont(h) + 1e-6 * strength[h]);
            let eq_share = if vs_reraise { 0.0 } else { 1.0 - stats.flatten };
            let key = |h: usize| -> f64 {
                eq_share * rank_eq[h] + (1.0 - eq_share) * rank_str[h]
            };
            let mut order: Vec<usize> = (0..NUM_CLASSES).collect();
            order.sort_by(|&x, &y| {
                key(x)
                    .partial_cmp(&key(y))
                    .unwrap()
                    .then(strength[y].partial_cmp(&strength[x]).unwrap())
            });
            let mut cont = vec![0f32; NUM_CLASSES];
            let mut acc = 0f64;
            for &h in &order {
                if acc >= t_cont * total {
                    break;
                }
                let avail = weight[h];
                if avail <= 1e-12 {
                    continue;
                }
                let take = (t_cont * total - acc).min(avail);
                cont[h] = (take / avail) as f32;
                acc += take;
            }
            // Raising slice within the continuing range: the reference
            // solve's opening order for first-in (76s before KTo — a
            // linear-by-equity raise range is what made every generated
            // opening range look the same), its 3-bet order facing a raise,
            // blended toward raw strength by naiveté (a whale raises KJo over
            // 76s). Over limpers only half the GTO order: iso-raising wants
            // domination (KTo) as much as playability. Re-raise buckets by
            // strength: a human 4-bets his strongest hands, full stop.
            let ref_raise = |h: usize| -> f64 {
                match b as u8 {
                    BUCKET_VS_RAISE | BUCKET_SQUEEZE => reference::THREEBET_SCORE[h] as f64,
                    BUCKET_VS_3BET => 0.0,
                    _ => reference::OPEN_SCORE[h] as f64,
                }
            };
            let rank_rr = rank_positions(&|h| ref_raise(h) + 1e-6 * strength[h]);
            // Half the GTO order for iso-raises (domination matters as much
            // as playability) and for 3-bets / squeezes (the reference
            // solve 3-bets JTs and A5s before AQs — fine for a solver, not
            // how micro or live regs build a 3-bet range).
            let r_share = if vs_reraise {
                0.0
            } else if b == BUCKET_UNOPENED as usize {
                1.0 - stats.flatten
            } else {
                0.5 * (1.0 - stats.flatten)
            };
            let key_r = |h: usize| -> f64 { r_share * rank_rr[h] + (1.0 - r_share) * rank_str[h] };
            let mut order_r: Vec<usize> = (0..NUM_CLASSES).collect();
            order_r.sort_by(|&x, &y| {
                key_r(x)
                    .partial_cmp(&key_r(y))
                    .unwrap()
                    .then(strength[y].partial_cmp(&strength[x]).unwrap())
            });
            let mut raise = vec![0f32; NUM_CLASSES];
            let mut racc = 0f64;
            for &h in &order_r {
                if racc >= t_raise * total {
                    break;
                }
                let avail = weight[h] * cont[h] as f64;
                if avail <= 1e-12 {
                    continue;
                }
                let take = (t_raise * total - racc).min(avail);
                raise[h] = (take / weight[h]) as f32;
                racc += take;
            }
            let call: Vec<f32> = (0..NUM_CLASSES).map(|h| (cont[h] - raise[h]).max(0.0)).collect();
            let jam = vec![0f32; NUM_CLASSES];
            let (raise, jam) = if stats.raise_size == "jam" {
                (jam.clone(), raise)
            } else {
                (raise, jam)
            };
            BucketPolicy {
                call,
                raise,
                jam,
                raise_size: if stats.raise_size == "jam" {
                    "max".into()
                } else {
                    stats.raise_size.clone()
                },
            }
        };
        let full: Vec<f64> = (0..NUM_CLASSES).map(|h| class_combos(h) as f64).collect();
        let build_policy = |b: usize, t_cont: f64, t_raise: f64| -> BucketPolicy {
            build_policy_w(b, t_cont, t_raise, &full)
        };
        let mut buckets: Vec<Option<BucketPolicy>> = Vec::with_capacity(NUM_BUCKETS);
        // the player's raising range, for the re-raise bucket: what it raises
        // with in any of the entry buckets (built first — bucket order)
        let mut raise_range = vec![0f64; NUM_CLASSES];
        for b in 0..NUM_BUCKETS {
            let (t_cont, t_raise) = targets[b];
            if b == BUCKET_VS_3BET as usize {
                // HUD "fold to 3-bet" is defined for the FIRST raiser: fill
                // the re-raise policy over the hands this seat OPENS with —
                // first-in or over limpers, weighted by how often the
                // baseline puts the seat in each spot (UTG never faces
                // limps; the BB never opens first-in). A seat that opens
                // nowhere falls back to its cold-raise ranges, then to the
                // deck. Limitation: the same policy serves a 3-bettor facing
                // a 4-bet, whose narrower range sits inside the continue
                // slice, so it rarely folds to 4-bets (fold-to-4-bet as its
                // own stat is a TODO).
                let tiers: [&[u8]; 2] = [
                    &[BUCKET_UNOPENED, BUCKET_VS_LIMPS],
                    &[BUCKET_VS_RAISE, BUCKET_SQUEEZE],
                ];
                for tier in tiers {
                    let mass: Vec<f64> =
                        tier.iter().map(|&eb| m_mine[eb as usize].max(0.0)).collect();
                    let tot: f64 = mass.iter().sum();
                    if tot <= 1e-9 {
                        continue;
                    }
                    for h in 0..NUM_CLASSES {
                        let mut m = 0f64;
                        for (k, &eb) in tier.iter().enumerate() {
                            if let Some(p) = buckets[eb as usize].as_ref() {
                                m += mass[k] / tot * (p.raise[h] + p.jam[h]).min(1.0) as f64;
                            }
                        }
                        raise_range[h] = class_combos(h) as f64 * m;
                    }
                    if raise_range.iter().sum::<f64>() >= 1.0 {
                        break;
                    }
                }
                // "fold to 3-bet" is a share of the hands he RAISED, not of
                // the deck: filled over the raising range (falls back to the
                // deck for a player who never raises)
                let pol = if raise_range.iter().sum::<f64>() >= 1.0 {
                    build_policy_w(b, t_cont, t_raise, &raise_range)
                } else {
                    build_policy(b, t_cont, t_raise)
                };
                buckets.push(Some(pol));
            } else {
                buckets.push(Some(build_policy(b, t_cont, t_raise)));
            }
        }
        // Limp defence: the after-limping continue rate over the limp range
        // (what he limps first-in or behind), limp-raising a sliver.
        let limp_defense = stats.cont_vs_raise_limped.and_then(|pct| {
            let mut wt = vec![0f64; NUM_CLASSES];
            for h in 0..NUM_CLASSES {
                let mut m = 0f32;
                for eb in [BUCKET_UNOPENED, BUCKET_VS_LIMPS] {
                    if let Some(p) = buckets[eb as usize].as_ref() {
                        m = m.max(p.call[h]);
                    }
                }
                wt[h] = class_combos(h) as f64 * m.min(1.0) as f64;
            }
            if wt.iter().sum::<f64>() < 1.0 {
                return None;
            }
            let t_cont = (pct / 100.0).clamp(0.0, 1.0);
            Some(build_policy_w(BUCKET_VS_RAISE as usize, t_cont, (0.03f64).min(t_cont), &wt))
        });
        // Size-banded VS_RAISE: one policy per (max_faced_to_bb, continue%)
        // band, built by the same machinery at that band's continue target
        // (raise share stays the 3-bet stat). The legacy single policy above
        // remains the band-less fallback.
        let vs_raise_bands = stats.cont_vs_raise_bands.as_ref().map(|bands| {
            bands
                .iter()
                .map(|&(max_to, pct)| {
                    let t_cont = (pct / 100.0).clamp(stats.threebet / 100.0, 1.0);
                    (
                        max_to,
                        build_policy(BUCKET_VS_RAISE as usize, t_cont, stats.threebet / 100.0),
                    )
                })
                .collect::<Vec<_>>()
        });

        let combo_pct = |v: &Vec<f32>| -> f64 {
            (0..NUM_CLASSES)
                .map(|h| class_combos(h) as f64 * v[h] as f64)
                .sum::<f64>()
                / 1326.0
                * 100.0
        };
        let bp = |b: u8| buckets[b as usize].as_ref().unwrap();
        let cont_pct = |b: u8| {
            let p = bp(b);
            combo_pct(&p.call) + combo_pct(&p.raise) + combo_pct(&p.jam)
        };
        let aggr_pct = |b: u8| {
            let p = bp(b);
            combo_pct(&p.raise) + combo_pct(&p.jam)
        };
        let cont_vs_3bet = {
            let tot: f64 = raise_range.iter().sum();
            if tot >= 1.0 {
                let p = bp(BUCKET_VS_3BET);
                let c3: f64 = (0..NUM_CLASSES)
                    .map(|h| raise_range[h] * (p.call[h] + p.raise[h] + p.jam[h]) as f64)
                    .sum();
                c3 / tot * 100.0
            } else {
                cont_pct(BUCKET_VS_3BET)
            }
        };
        let implied = ImpliedStats {
            vpip: cont_pct(BUCKET_UNOPENED),
            pfr: aggr_pct(BUCKET_UNOPENED),
            threebet: aggr_pct(BUCKET_VS_RAISE),
            cont_vs_raise: cont_pct(BUCKET_VS_RAISE),
            squeeze: aggr_pct(BUCKET_SQUEEZE),
            cont_vs_3bet,
        };
        Ok((
            SeatProfile {
                name: name.to_string(),
                buckets,
                vs_raise_bands,
                postflop: None,
                limp_defense,
            },
            implied,
        ))
    }

    /// Estimated arena memory in MB (regrets + strategy sums).
    pub fn arena_mb(&self) -> f64 {
        (self.arena_len * 2 * 4) as f64 / 1e6
    }
}

/// Structural checks plus the hard ECONOMIC invariants: every number finite,
/// no chip-minting rake, no over-stack sizes, a sane jam threshold.
///
/// Deliberately NOT enforced: a minimum open size (real-poker min-open =
/// biggest blind + last raise). "Any raise sizes" is an advertised study
/// feature (limps exist, min-raise conventions vary), and the builder handles
/// sub-minimum opens consistently — `next_state_of` recomputes `last_raise`
/// from the actual open and `legal_actions_of` clamps every RE-raise up to a
/// legal increment — so a 1.5bb open is an unusual config, not a broken one.
fn validate(cfg: &PreflopConfig) -> Result<usize, String> {
    let n = cfg.positions.len();
    if !(2..=9).contains(&n) {
        return Err("2..9 positions required".into());
    }
    if cfg.posts.len() != n {
        return Err("posts must align with positions".into());
    }
    // Finiteness before the range checks: NaN passes every ordinary
    // comparison (NaN <= x is false) and would sail through into the tree.
    if !cfg.stack.is_finite() {
        return Err(format!("stack must be a finite bb amount, got {}", cfg.stack));
    }
    if let Some(p) = cfg.posts.iter().find(|p| !p.is_finite() || **p < 0.0) {
        return Err(format!("posts must be finite and >= 0, got {p}"));
    }
    if !cfg.ante.is_finite() || cfg.ante < 0.0 {
        return Err(format!("ante must be finite and >= 0, got {}", cfg.ante));
    }
    let biggest_post = cfg.posts.iter().cloned().fold(0.0, f64::max);
    if cfg.stack <= biggest_post {
        return Err("stack must exceed the biggest blind".into());
    }
    if let Some(&s) = cfg.call_only_seats.iter().find(|&&s| s >= n) {
        return Err(format!("call_only_seats index {s} out of range for {n} seats"));
    }
    for (name, per) in [
        ("open_raises_by_seat", &cfg.open_raises_by_seat),
        ("raise_mults_by_seat", &cfg.raise_mults_by_seat),
    ] {
        if let Some(per) = per {
            if per.len() != n {
                return Err(format!("{name} must have one entry per seat ({n})"));
            }
            for sizes in per {
                if let Some(v) = sizes.iter().find(|v| !v.is_finite() || **v <= 0.0) {
                    return Err(format!("{name} sizes must be finite and > 0, got {v}"));
                }
            }
            if name == "open_raises_by_seat" {
                for sizes in per {
                    if let Some(v) = sizes.iter().find(|v| **v > cfg.stack) {
                        return Err(format!(
                            "{name} size {v} exceeds the {} bb stack (enable add_allin for jams)",
                            cfg.stack
                        ));
                    }
                }
            }
        }
    }
    if cfg.call_only_seats.len() == n && !cfg.limp {
        return Err("all seats call-only with no limp leaves no way to enter a pot".into());
    }
    for &o in &cfg.open_raises {
        if !o.is_finite() || o <= 0.0 {
            return Err(format!("open_raises sizes must be finite and > 0, got {o}"));
        }
        if o > cfg.stack {
            return Err(format!(
                "open_raises size {o} exceeds the {} bb stack (enable add_allin for jams)",
                cfg.stack
            ));
        }
    }
    for &m in &cfg.raise_mults {
        if !m.is_finite() || m <= 0.0 {
            return Err(format!("raise_mults must be finite and > 0, got {m}"));
        }
    }
    // > 1 would let a raise land ABOVE the stack (the jam clamp could no
    // longer catch it): invested chips that don't exist. NaN fails the
    // first comparison.
    if !(cfg.allin_threshold > 0.0 && cfg.allin_threshold <= 1.0) {
        return Err(format!(
            "allin_threshold must be in (0, 1], got {}",
            cfg.allin_threshold
        ));
    }
    // NOTE: preflop rake_pct is a PERCENT (5.0 = 5%), unlike the postflop
    // engine's fraction. Negative rake mints chips at every raked terminal;
    // >= 100% makes effective pots non-positive.
    if !cfg.rake_pct.is_finite() || cfg.rake_pct < 0.0 || cfg.rake_pct >= 100.0 {
        return Err(format!(
            "rake_pct is a percent and must be in [0, 100), got {}",
            cfg.rake_pct
        ));
    }
    if !cfg.rake_cap.is_finite() || cfg.rake_cap < 0.0 {
        return Err(format!("rake_cap must be finite and >= 0, got {}", cfg.rake_cap));
    }
    // Opens at or below the biggest post are silently dropped by
    // `legal_actions_of` (and with max_raises = 0 no raise — jam included —
    // is ever offered); without a limp such a config would build a
    // fold-only root instead of anything the user meant.
    let has_open = cfg.max_raises > 0
        && (cfg.add_allin || cfg.open_raises.iter().any(|&o| o > biggest_post + 1e-9));
    if !cfg.limp && !has_open {
        return Err(
            "no legal opening actions: enable limp, all-in or an open raise above the biggest blind"
                .into(),
        );
    }
    Ok(n)
}

fn root_state(cfg: &PreflopConfig, n: usize) -> BuildState {
    BuildState {
        invested: (0..n).map(|i| cfg.posts[i] + cfg.ante).collect(),
        folded: 0,
        allin: 0,
        needs: (1u32 << n) - 1,
        to_call: cfg.posts.iter().cloned().fold(0.0, f64::max),
        last_raise: cfg.posts.iter().cloned().fold(0.0, f64::max).max(1.0),
        raises: 0,
        limpers: 0,
        callers: 0,
        next_seat: 0,
        aggressor: 255,
    }
}

fn next_actor_of(n: usize, st: &BuildState) -> Option<usize> {
    for k in 0..n {
        let s = (st.next_seat + k) % n;
        let bit = 1u32 << s;
        if st.folded & bit == 0 && st.allin & bit == 0 && st.needs & bit != 0 {
            return Some(s);
        }
    }
    None
}

/// Legal actions for `actor` — the single source of truth shared by the
/// real tree builder and the size estimator (ante is dead money: only
/// invested-minus-ante counts toward matching the bet).
fn legal_actions_of(cfg: &PreflopConfig, st: &BuildState, actor: usize) -> Vec<PAction> {
    let inv_live = st.invested[actor] - cfg.ante;
    let owed = (st.to_call - inv_live).max(0.0);
    let mut acts: Vec<PAction> = Vec::new();
    if owed > 1e-9 {
        acts.push(PAction {
            kind: "fold".into(),
            to: 0.0,
            label: "Fold".into(),
        });
        // call (limp when no raise yet)
        if st.raises > 0 || cfg.limp {
            let label = if st.raises == 0 { "Limp" } else { "Call" };
            acts.push(PAction {
                kind: "call".into(),
                to: st.to_call,
                label: format!("{label} {}", trim(st.to_call)),
            });
        }
    } else {
        acts.push(PAction {
            kind: "check".into(),
            to: st.to_call,
            label: "Check".into(),
        });
    }
    if st.raises < cfg.max_raises && !cfg.call_only_seats.contains(&actor) {
        let mut tos: Vec<f64> = Vec::new();
        if st.raises == 0 {
            tos.extend(cfg.opens_of(actor).iter().cloned());
        } else {
            for m in cfg.mults_of(actor) {
                let to = (st.to_call * m).max(st.to_call + st.last_raise);
                tos.push(to);
            }
        }
        if cfg.add_allin {
            tos.push(cfg.stack);
        }
        let mut seen: Vec<f64> = Vec::new();
        for mut to in tos {
            if to >= cfg.allin_threshold * cfg.stack {
                to = cfg.stack;
            }
            if to <= st.to_call + 1e-9 {
                continue;
            }
            if seen.iter().any(|&x| (x - to).abs() < 1e-9) {
                continue;
            }
            seen.push(to);
            let jam = (to - cfg.stack).abs() < 1e-9;
            acts.push(PAction {
                kind: if jam { "jam" } else { "raise" }.into(),
                to,
                label: if jam {
                    format!("All-in {}", trim(to))
                } else if st.raises == 0 {
                    format!("Raise {}", trim(to))
                } else {
                    format!("{}-bet {}", st.raises + 2, trim(to))
                },
            });
        }
    }
    acts
}

/// State after `actor` takes `a` — shared by builder and estimator.
fn next_state_of(
    cfg: &PreflopConfig,
    n: usize,
    st: &BuildState,
    actor: usize,
    a: &PAction,
) -> BuildState {
    let mut ns = BuildState {
        invested: st.invested.clone(),
        folded: st.folded,
        allin: st.allin,
        needs: st.needs & !(1 << actor),
        to_call: st.to_call,
        last_raise: st.last_raise,
        raises: st.raises,
        limpers: st.limpers,
        callers: st.callers,
        next_seat: (actor + 1) % n,
        aggressor: st.aggressor,
    };
    match a.kind.as_str() {
        "fold" => {
            ns.folded |= 1 << actor;
        }
        "check" | "call" => {
            ns.invested[actor] = st.to_call + cfg.ante;
            if (st.to_call - cfg.stack).abs() < 1e-9 {
                ns.allin |= 1 << actor;
            }
            if a.kind == "call" {
                if st.raises == 0 {
                    ns.limpers += 1;
                } else {
                    ns.callers += 1;
                }
            }
        }
        _ => {
            ns.invested[actor] = a.to + cfg.ante;
            ns.last_raise = a.to - st.to_call;
            ns.aggressor = actor as u8;
            ns.to_call = a.to;
            ns.raises = st.raises + 1;
            ns.callers = 0; // a raise starts a fresh calling round
            if (a.to - cfg.stack).abs() < 1e-9 {
                ns.allin |= 1 << actor;
            }
            // a raise re-opens action for every live player behind
            ns.needs = (((1u32 << n) - 1) & !ns.folded & !ns.allin) & !(1 << actor);
        }
    }
    ns
}

/// Available RAM in MB (Linux MemAvailable / Windows avail_phys; None elsewhere).
fn avail_mem_mb() -> Option<f64> {
    crate::sysmem::avail_mem_mb()
}

/// Tree-size limits, derived from THIS machine: the regret/strategy arenas
/// may take ~40% of currently available RAM (leaving room for the node
/// structures, the equity table, the postflop solver and the OS), and the
/// node cap scales with that (~830 nodes per arena-MB, the measured ratio).
/// PREFLOP_MAX_ARENA_MB / PREFLOP_MAX_NODES override.
pub fn limit_arena_mb() -> f64 {
    if let Some(v) = std::env::var("PREFLOP_MAX_ARENA_MB")
        .ok()
        .and_then(|v| v.parse().ok())
    {
        return v;
    }
    avail_mem_mb().map(|a| a * 0.40).unwrap_or(2000.0)
}
pub fn limit_nodes() -> u64 {
    if let Some(v) = std::env::var("PREFLOP_MAX_NODES")
        .ok()
        .and_then(|v| v.parse().ok())
    {
        return v;
    }
    (limit_arena_mb() * 830.0) as u64
}

#[derive(Debug, Clone, Serialize)]
pub struct TreeEstimate {
    pub nodes: u64,
    pub action_nodes: u64,
    /// f32 entries across both arenas is arena_len * 2; bytes = * 8.
    pub arena_len: u64,
    /// True when the walk stopped early (config absurdly large).
    pub truncated: bool,
}

/// Count the tree a config would build — same enumeration logic as the
/// builder, no allocation. Fast enough to run on every keystroke. The walk
/// stops a little past this machine's node limit (env PREFLOP_MAX_NODES
/// included), so `truncated` always means "over the real limit" — absurd
/// configs still return quickly because counting stops there.
pub fn estimate_tree(cfg: &PreflopConfig) -> Result<TreeEstimate, String> {
    let n = validate(cfg)?;
    let cap = limit_nodes().saturating_add(limit_nodes() / 10).max(3_000_000);
    let mut est = TreeEstimate {
        nodes: 0,
        action_nodes: 0,
        arena_len: 0,
        truncated: false,
    };
    count_walk(cfg, n, root_state(cfg, n), &mut est, cap);
    Ok(est)
}

fn count_walk(cfg: &PreflopConfig, n: usize, st: BuildState, est: &mut TreeEstimate, cap: u64) {
    if est.truncated {
        return;
    }
    est.nodes += 1;
    if est.nodes > cap {
        est.truncated = true;
        return;
    }
    let live = ((1u32 << n) - 1) & !st.folded;
    if live.count_ones() == 1 {
        return; // fold-win terminal
    }
    let Some(actor) = next_actor_of(n, &st) else {
        return; // pot-share terminal
    };
    let acts = legal_actions_of(cfg, &st, actor);
    est.action_nodes += 1;
    est.arena_len += (acts.len() * NUM_CLASSES) as u64;
    for a in &acts {
        count_walk(cfg, n, next_state_of(cfg, n, &st, actor, a), est, cap);
    }
}

/// HUD-style stats driving profile generation (percent units, 0..100).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HudStats {
    pub vpip: f64,
    pub pfr: f64,
    pub threebet: f64,
    pub fold_to_3bet: f64,
    #[serde(default)]
    pub squeeze: f64,
    #[serde(default)]
    pub fourbet: Option<f64>,
    /// Naiveté, 0..1. At 0 ranges are solver-shaped: positional (each seat
    /// distorts its own equilibrium) and ordered by playability (equilibrium
    /// defense prices in domination). At 1 the player "plays his cards":
    /// position-blind AND ordered by raw card appeal (equity vs random) —
    /// a fish calls Q9o long before 43s, the equilibrium does the reverse.
    #[serde(default)]
    pub flatten: f64,
    #[serde(default = "default_raise_size")]
    pub raise_size: String,
    /// Measured continue-vs-raise % (call + re-raise when facing a single
    /// raise). When present it overrides the VPIP-derived blend — the knob
    /// exists because real pools (and sticky limpers in particular) defend
    /// far outside what the blend can express.
    #[serde(default)]
    pub cont_vs_raise: Option<f64>,
    /// Size-banded continue-vs-raise: ascending (max_faced_to_bb,
    /// continue_pct) pairs, e.g. [(3.5, 22.9), (999.0, 17.9)] = continue
    /// 22.9% when the faced raise is TO <= 3.5bb and 17.9% above (the last
    /// band also catches anything past its threshold). When present it
    /// supersedes `cont_vs_raise` for band selection — the single stat (or,
    /// absent that, the bands' mean) still shapes the band-less fallback
    /// policy. Thresholds must be finite and strictly ascending; each
    /// continue% must lie in [threebet, 100]. Real pools tighten vs big
    /// opens; without bands a ruled villain defends a 5x open exactly like
    /// a 2x, overvaluing large hero sizes in max-exploit studies.
    #[serde(default)]
    pub cont_vs_raise_bands: Option<Vec<(f64, f64)>>,
    /// Measured continue % in squeeze spots; same override semantics.
    #[serde(default)]
    pub cont_squeeze: Option<f64>,
    /// Measured continue % facing a raise AFTER LIMPING (as a share of the
    /// limped hands). Limpers are far stickier than cold seats — the 2009
    /// micro pool folds 46% after limping vs 85% cold — so this gets its
    /// own policy over the limp range (`SeatProfile::limp_defense`).
    #[serde(default)]
    pub cont_vs_raise_limped: Option<f64>,
    /// First-in rates (percent of the times it was folded to him):
    /// open-raise and open-limp. Blank = PFR and VPIP − PFR, which
    /// over-limps regs (a 17/12 TAG open-limps ~2%, not 5%: his VPIP−PFR
    /// gap is calls and blind defence, not limps) and under-limps whales.
    #[serde(default)]
    pub open_raise: Option<f64>,
    #[serde(default)]
    pub open_limp: Option<f64>,
    /// Facing limpers with nothing invested: iso-raise and limp-behind
    /// rates (percent). Blank = PFR and VPIP − PFR.
    #[serde(default)]
    pub iso_raise: Option<f64>,
    #[serde(default)]
    pub limp_behind: Option<f64>,
}

/// Input validation for profile generation: every stat finite and in range,
/// errors naming the offending field. Garbage here (NaN percents, a 150%
/// continue) would otherwise flow silently into range fills and clamps.
fn validate_stats(stats: &HudStats) -> Result<(), String> {
    let pct = |name: &str, v: f64| -> Result<(), String> {
        if !v.is_finite() || !(0.0..=100.0).contains(&v) {
            return Err(format!("{name} must be a percent in [0, 100], got {v}"));
        }
        Ok(())
    };
    pct("vpip", stats.vpip)?;
    pct("pfr", stats.pfr)?;
    pct("threebet", stats.threebet)?;
    pct("fold_to_3bet", stats.fold_to_3bet)?;
    pct("squeeze", stats.squeeze)?;
    if let Some(f) = stats.fourbet {
        pct("fourbet", f)?;
    }
    if let Some(c) = stats.cont_vs_raise {
        pct("cont_vs_raise", c)?;
    }
    if let Some(c) = stats.cont_vs_raise_limped {
        pct("cont_vs_raise_limped", c)?;
    }
    for (name, v) in [
        ("open_raise", stats.open_raise),
        ("open_limp", stats.open_limp),
        ("iso_raise", stats.iso_raise),
        ("limp_behind", stats.limp_behind),
    ] {
        if let Some(c) = v {
            pct(name, c)?;
        }
    }
    if let Some(c) = stats.cont_squeeze {
        pct("cont_squeeze", c)?;
    }
    if !stats.flatten.is_finite() || !(0.0..=1.0).contains(&stats.flatten) {
        return Err(format!("flatten must be in [0, 1], got {}", stats.flatten));
    }
    if !matches!(stats.raise_size.as_str(), "min" | "max" | "jam") {
        return Err(format!(
            "raise_size must be \"min\", \"max\" or \"jam\", got {:?}",
            stats.raise_size
        ));
    }
    if let Some(bands) = &stats.cont_vs_raise_bands {
        if bands.is_empty() {
            return Err("cont_vs_raise_bands must not be empty (omit it instead)".into());
        }
        let mut prev = f64::NEG_INFINITY;
        for &(max_to, cont) in bands {
            if !max_to.is_finite() || max_to <= 0.0 {
                return Err(format!(
                    "cont_vs_raise_bands thresholds must be finite bb amounts > 0, got {max_to}"
                ));
            }
            if max_to <= prev {
                return Err(format!(
                    "cont_vs_raise_bands thresholds must be strictly ascending, got {max_to} after {prev}"
                ));
            }
            prev = max_to;
            // below the 3-bet stat the band could not even hold the raises
            if !cont.is_finite() || cont < stats.threebet || cont > 100.0 {
                return Err(format!(
                    "cont_vs_raise_bands continue% must be in [threebet ({}), 100], got {cont}",
                    stats.threebet
                ));
            }
        }
    }
    Ok(())
}

/// Stats the generated profile actually implies (readback for trust).
#[derive(Debug, Clone, Serialize)]
pub struct ImpliedStats {
    pub vpip: f64,
    pub pfr: f64,
    pub threebet: f64,
    pub cont_vs_raise: f64,
    pub squeeze: f64,
    pub cont_vs_3bet: f64,
}

/// Named archetypes: (name, stats). Starting points, all editable.
pub fn archetypes() -> Vec<(&'static str, HudStats)> {
    let mk = |vpip, pfr, threebet, f2b, squeeze, flatten, size: &str| HudStats {
        vpip,
        pfr,
        threebet,
        fold_to_3bet: f2b,
        squeeze,
        fourbet: None,
        flatten,
        raise_size: size.into(),
        cont_vs_raise: None,
        cont_vs_raise_bands: None,
        cont_squeeze: None,
        cont_vs_raise_limped: None,
        open_raise: None,
        open_limp: None,
        iso_raise: None,
        limp_behind: None,
    };
    // measured overrides (cvr = continue vs raise %, csq = continue vs squeeze %)
    let mkm = |vpip, pfr, threebet, f2b, squeeze, flatten, size: &str, cvr, csq| HudStats {
        cont_vs_raise: Some(cvr),
        cont_squeeze: Some(csq),
        ..mk(vpip, pfr, threebet, f2b, squeeze, flatten, size)
    };
    vec![
        ("Whale (loose-passive)", mk(60.0, 8.0, 2.0, 20.0, 2.0, 0.75, "min")),
        ("Nit / OMC", mk(12.0, 1.5, 1.0, 15.0, 0.5, 0.25, "max")),
        ("Calling station", mk(45.0, 10.0, 3.0, 15.0, 3.0, 0.6, "min")),
        ("TAG", mk(24.0, 19.0, 7.0, 55.0, 6.0, 0.1, "min")),
        ("LAG", mk(30.0, 25.0, 11.0, 45.0, 9.0, 0.1, "min")),
        ("Maniac", mk(55.0, 40.0, 20.0, 25.0, 15.0, 0.5, "max")),
        // CoinPoker micro-pool archetypes, measured 2026-07-20 from 10.6k
        // anonymized 6-max NLH hands (NL2-NL10): pool VPIP 29.4 / PFR 18.3 /
        // 3-bet 8.5, fold-to-3bet-as-raiser 47, squeeze 7.5, cont-vs-raise
        // 28.3, squeeze-spot continue 35; limpers limp-CALL 71% (hence the
        // sticky cont overrides); modal sizes 2.5x open, 3x 3-bet.
        ("CP Pool (anon avg)", mkm(29.0, 18.0, 8.5, 47.0, 7.5, 0.55, "min", 28.3, 35.0)),
        ("CP Reg (raise-first)", mkm(23.0, 19.0, 9.0, 47.0, 6.0, 0.25, "min", 24.0, 28.0)),
        ("CP Sticky Limper", mkm(42.0, 6.0, 4.0, 30.0, 4.5, 0.8, "min", 75.0, 72.0)),
        ("CP Aggro 3-Bettor", mkm(32.0, 25.0, 16.0, 42.0, 14.0, 0.4, "max", 45.0, 40.0)),
    ]
}

/// One archetype as shipped to the UI: the built-ins above plus any entry of
/// `cache/archetypes.json` (data-derived player types; see
/// docs/preflop_modeling_research.md and tools/derive_archetypes.py).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Archetype {
    pub name: String,
    pub stats: HudStats,
    pub postflop: crate::query::PostflopStats,
    /// Provenance / one-line description for the UI tooltip.
    #[serde(default)]
    pub note: String,
}

/// Every archetype: the hand-written built-ins, then the data-derived ones
/// from `cache/archetypes.json` (searched from the CWD, then relative to the
/// crate, like the realization fit). A file entry with a built-in's name
/// replaces it.
pub fn archetypes_all() -> Vec<Archetype> {
    let mut out: Vec<Archetype> = archetypes()
        .into_iter()
        .map(|(n, s)| Archetype {
            name: n.to_string(),
            postflop: archetype_postflop(n),
            stats: s,
            note: String::new(),
        })
        .collect();
    let file = std::env::var("ARCHETYPES_JSON")
        .ok()
        .or_else(|| {
            ["cache/archetypes.json", "../../cache/archetypes.json"]
                .iter()
                .find(|p| std::path::Path::new(p).exists())
                .map(|p| p.to_string())
        });
    if let Some(path) = file {
        if let Ok(text) = std::fs::read_to_string(&path) {
            match serde_json::from_str::<Vec<Archetype>>(&text) {
                Ok(list) => {
                    for a in list {
                        if validate_stats(&a.stats).is_err() {
                            eprintln!("archetypes.json: skipping {:?} (invalid stats)", a.name);
                            continue;
                        }
                        if let Some(slot) = out.iter_mut().find(|x| x.name == a.name) {
                            *slot = a;
                        } else {
                            out.push(a);
                        }
                    }
                }
                Err(e) => eprintln!("archetypes.json: {e}"),
            }
        }
    }
    out
}

/// Default postflop tendencies for each archetype, keyed by name prefix —
/// the postflop half of the same player (see `query::PostflopStats`).
pub fn archetype_postflop(name: &str) -> crate::query::PostflopStats {
    use crate::query::PostflopStats;
    let mk = |cbet: [f32; 3], fold_to_bet: [f32; 3], raise_bet: f32, donk: f32, sz: &str| {
        PostflopStats { cbet, fold_to_bet, raise_bet, donk, bet_size: sz.into() }
    };
    if name.starts_with("Whale") {
        // passive and sticky: rarely barrels, near-never folds or raises
        mk([45.0, 34.0, 25.0], [28.0, 32.0, 38.0], 4.0, 16.0, "min")
    } else if name.starts_with("Nit") {
        // honest: bets when strong, folds when bet at, raises only the nuts
        mk([50.0, 38.0, 28.0], [55.0, 60.0, 65.0], 4.0, 5.0, "max")
    } else if name.starts_with("Calling") {
        mk([40.0, 30.0, 22.0], [18.0, 22.0, 30.0], 3.0, 12.0, "min")
    } else if name.starts_with("LAG") {
        mk([75.0, 62.0, 50.0], [35.0, 38.0, 45.0], 13.0, 10.0, "min")
    } else if name.starts_with("Maniac") {
        mk([90.0, 80.0, 70.0], [18.0, 22.0, 28.0], 22.0, 30.0, "max")
    } else {
        // TAG / default: near-solver aggression, honest-ish folds
        mk([65.0, 55.0, 45.0], [42.0, 45.0, 50.0], 9.0, 6.0, "min")
    }
}

fn trim(x: f64) -> String {
    if (x - x.round()).abs() < 1e-9 {
        format!("{}", x.round() as i64)
    } else {
        format!("{:.1}", x)
    }
}
