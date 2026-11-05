//! "Trust the read" (preflop/rnr.rs) on the GPU, normal plan only.
//!
//! A ruled seat is its read with probability t and its free type otherwise.
//! When it does not traverse, it plays the behavioral mixture of its two
//! types: `pf_rnr_mix` (rnr.cu) writes that mixture into the forced-policy
//! table each pass, so the ordinary down sweep gives the seat the reach
//! t · read + (1 − t) · free at every node and every terminal kernel prices
//! the mixture unchanged (exactly as `mixed_reaches` on the CPU). The read
//! is fixed in hero mode, so its own reach is computed once on the host.
//!
//! The free types' arenas sit after the main arenas in `d_regrets` /
//! `d_strat`, at the CPU's `PfFree` layout. A pass is a "role": its seat
//! modes, forced offsets and arena offsets, swapped into the engine around
//! the shared sweep code:
//! - mixed: every ruled seat plays its mixture (the hero's pass, and the
//!   average evaluation of the hero and the other seats);
//! - learn j: ruled seat j is its free type (learning in its own arenas,
//!   bound by point locks), the others mixed;
//! - read j: ruled seat j is its read (evaluation only).
use super::*;
use crate::preflop::rnr::PfTrustReadout;

const NO_LOCK: u32 = u32::MAX;

struct Role {
    src: CudaSlice<i32>,
    foff: Option<CudaSlice<u32>>,
    free_off: bool,
}

pub(super) struct GpuRnr {
    f_mix: CudaFunction,
    pub(super) trust: f32,
    pub(super) hero: usize,
    pub(super) seats: Vec<usize>,
    free_len: usize,
    /// Arena offsets with the ruled seats' nodes at their free blocks.
    d_off_free: CudaSlice<u32>,
    /// Forced offsets with the ruled seats' unlocked nodes at their mixture.
    d_foff_mixed: CudaSlice<u32>,
    /// [mixed, learn 0..k, read 0..k]
    roles: Vec<Role>,
    d_src_zero: CudaSlice<i32>,
    // ruled-seat action nodes, by tree level, and per-node mix inputs
    d_nodes: CudaSlice<u32>,
    spans: Vec<(u32, u32)>,
    d_loc: CudaSlice<u32>,
    d_lock: CudaSlice<u32>,
    d_mix_off: CudaSlice<u32>,
    d_rs: CudaSlice<f32>,
    d_rf_in: CudaSlice<u32>,
    d_rf_out: CudaSlice<u32>,
    d_rf: CudaSlice<f32>,
}

/// Host tables, built before the engine's own allocations.
pub(super) struct Plan {
    trust: f32,
    hero: usize,
    seats: Vec<usize>,
    pub(super) free_len: usize,
    /// Initial free arenas (the CPU's if it has them, else the seats' table
    /// regrets and empty averages, as `sync_pf_free`).
    pub(super) regrets: Vec<f32>,
    pub(super) strat: Vec<f32>,
    /// Extra forced-table entries for the mixtures.
    pub(super) mix_len: usize,
    off_free: Vec<u32>,
    foff_mixed: Vec<u32>,
    src_mixed: Vec<i32>,
    src_learn: Vec<Vec<i32>>,
    src_read: Vec<Vec<i32>>,
    foff_read: Vec<Vec<u32>>,
    nodes: Vec<u32>,
    spans: Vec<(u32, u32)>,
    loc: Vec<u32>,
    lock: Vec<u32>,
    mix_off: Vec<u32>,
    rs: Vec<f32>,
    rf_in: Vec<u32>,
    rf_out: Vec<u32>,
    rf_blocks: usize,
}

/// The free layout of `PreflopSolver::sync_pf_free`: (local offset per node
/// or u32::MAX, total length).
fn free_layout(s: &PreflopSolver, slot_of: &[Option<usize>]) -> (Vec<u32>, usize) {
    let mut loc = vec![u32::MAX; s.nodes.len()];
    let mut len = 0usize;
    for (i, nd) in s.nodes.iter().enumerate() {
        if nd.kind == KIND_ACTION && slot_of[nd.actor as usize].is_some() {
            loc[i] = len as u32;
            len += nd.actions.len() * NUM_CLASSES;
        }
    }
    (loc, len)
}

/// Device bytes the dial adds, for the VRAM estimate (0 off the dial).
pub(super) fn bytes(s: &PreflopSolver) -> usize {
    if s.rnr_active().is_none() {
        return 0;
    }
    let seats = s.trust_seats();
    let mut slot_of = vec![None; s.n];
    for (j, &q) in seats.iter().enumerate() {
        slot_of[q] = Some(j);
    }
    let (_, free_len) = free_layout(s, &slot_of);
    let ruled = s.nodes.iter().filter(|nd| nd.kind == KIND_ACTION && slot_of[nd.actor as usize].is_some()).count();
    let k = seats.len();
    let n = s.nodes.len();
    // free regrets + strat, read reach, mixtures, free reach blocks
    free_len * 4 * 4 + (k * NUM_CLASSES + free_len) * 4
        // roles: 1 + 2k seat-mode tables, k + 1 forced and one free offset table
        + (1 + 2 * k) * n * 4 + (k + 2) * n * 4 + n * 4
        + ruled * 6 * 4
}

impl Plan {
    pub(super) fn build(
        s: &PreflopSolver, action_nodes: &[u32], spans: &[(u32, u32)],
        off: &[u32], src: &[i32], foff: &[u32], forced_len: usize,
    ) -> Result<Self, String> {
        let (trust, hero) = s.rnr_active().ok_or("trust dial not active")?;
        let seats = s.trust_seats();
        let k = seats.len();
        let n = s.nodes.len();
        let mut slot_of = vec![None; s.n];
        for (j, &q) in seats.iter().enumerate() {
            slot_of[q] = Some(j);
        }
        let (loc_of, free_len) = free_layout(s, &slot_of);
        if s.arena_len.checked_add(free_len).is_none_or(|x| x > u32::MAX as usize) {
            return Err("free arenas beyond the GPU engine's 32-bit arena indexing; solving on CPU".into());
        }
        // initial free arenas
        let (regrets, strat) = match s.pf_free.as_deref() {
            Some(f) if f.hero == hero && f.seats == seats && f.len == free_len => {
                // SAFETY: &PreflopSolver with no traversal running
                unsafe { (f.regrets.slice().to_vec(), f.strat.slice().to_vec()) }
            }
            _ => {
                let mut r = vec![0f32; free_len];
                // SAFETY: as above
                let main = unsafe { s.regrets.slice() };
                for (i, nd) in s.nodes.iter().enumerate() {
                    if loc_of[i] != u32::MAX {
                        let len = nd.actions.len() * NUM_CLASSES;
                        let o = loc_of[i] as usize;
                        r[o..o + len].copy_from_slice(&main[nd.data_off..nd.data_off + len]);
                    }
                }
                (r, vec![0f32; free_len])
            }
        };
        // ruled nodes by level
        let mut nodes = Vec::new();
        let mut rspans = Vec::new();
        for &(start, count) in spans {
            let first = nodes.len() as u32;
            for &nd in &action_nodes[start as usize..(start + count) as usize] {
                if loc_of[nd as usize] != u32::MAX {
                    nodes.push(nd);
                }
            }
            let c = nodes.len() as u32 - first;
            if c > 0 {
                rspans.push((first, c));
            }
        }
        // mixture slots in the forced table, point locks stay as they are
        let mut mix_at = vec![u32::MAX; n];
        let mut mix_len = 0usize;
        for (i, nd) in s.nodes.iter().enumerate() {
            if loc_of[i] == u32::MAX {
                continue;
            }
            if src[i] == 0 {
                return Err("the trust dial needs every ruled seat frozen (hero mode)".into());
            }
            if s.point_locks.contains_key(&(i as u32)) {
                mix_at[i] = foff[i];
            } else {
                mix_at[i] = (forced_len + mix_len) as u32;
                mix_len += nd.actions.len() * NUM_CLASSES;
            }
        }
        if forced_len + mix_len > u32::MAX as usize {
            return Err("forced-strategy table beyond 32-bit indexing; solving on CPU".into());
        }
        // The read's own reach after each of its actions (rs, free layout),
        // and the free reach blocks: slot j's root is block j, a ruled node's
        // children are blocks k + loc / 169 + a. Node indices are top-down.
        let mut rs = vec![0f32; free_len];
        let mut cur = vec![0u32; n * k];
        for j in 0..k {
            cur[j] = j as u32;
        }
        let mut rf_in_of = vec![0u32; n];
        for (i, nd) in s.nodes.iter().enumerate() {
            if nd.kind != KIND_ACTION {
                continue;
            }
            let slot = slot_of[nd.actor as usize];
            if let Some(j) = slot {
                let b = cur[i * k + j];
                rf_in_of[i] = b;
                let sigma = s.average_strategy(i); // forced, else the frozen average
                let o = loc_of[i] as usize;
                for a in 0..nd.actions.len() {
                    for h in 0..NUM_CLASSES {
                        let rin = if (b as usize) < k { class_prob(h) } else { rs[(b as usize - k) * NUM_CLASSES + h] };
                        rs[o + a * NUM_CLASSES + h] = rin * sigma[a * NUM_CLASSES + h];
                    }
                }
            }
            for a in 0..nd.actions.len() {
                let c = s.child(i, a);
                cur.copy_within(i * k..(i + 1) * k, c * k);
                if let Some(j) = slot {
                    cur[c * k + j] = (k + loc_of[i] as usize / NUM_CLASSES + a) as u32;
                }
            }
        }
        let rf_blocks = k + free_len / NUM_CLASSES;
        let per = |f: &dyn Fn(usize) -> u32| nodes.iter().map(|&nd| f(nd as usize)).collect::<Vec<u32>>();
        let loc = per(&|i| loc_of[i]);
        let lock = per(&|i| if s.point_locks.contains_key(&(i as u32)) { foff[i] } else { NO_LOCK });
        let mix_off = per(&|i| mix_at[i]);
        let rf_in = per(&|i| rf_in_of[i]);
        let rf_out = per(&|i| (k + loc_of[i] as usize / NUM_CLASSES) as u32);
        // role tables
        let ruled = |i: usize| loc_of[i] != u32::MAX;
        let mut off_free = off.to_vec();
        let mut src_mixed = src.to_vec();
        let mut foff_mixed = foff.to_vec();
        for i in 0..n {
            if ruled(i) {
                off_free[i] = (s.arena_len + loc_of[i] as usize) as u32;
                src_mixed[i] = 2;
                foff_mixed[i] = mix_at[i];
            }
        }
        let mut src_learn = Vec::with_capacity(k);
        let mut src_read = Vec::with_capacity(k);
        let mut foff_read = Vec::with_capacity(k);
        for &q in &seats {
            let mut learn = src_mixed.clone();
            let mut read = src_mixed.clone();
            let mut fread = foff_mixed.clone();
            for i in 0..n {
                if ruled(i) && s.nodes[i].actor as usize == q {
                    if !s.point_locks.contains_key(&(i as u32)) {
                        learn[i] = 0;
                    }
                    read[i] = src[i];
                    fread[i] = foff[i];
                }
            }
            src_learn.push(learn);
            src_read.push(read);
            foff_read.push(fread);
        }
        Ok(Self {
            trust, hero, seats, free_len, regrets, strat, mix_len, off_free, foff_mixed, src_mixed,
            src_learn, src_read, foff_read, nodes, spans: rspans, loc, lock, mix_off, rs, rf_in, rf_out, rf_blocks,
        })
    }
}

impl GpuRnr {
    pub(super) fn new(ctx: &Arc<CudaContext>, stream: &Arc<CudaStream>, arch: &'static str, p: Plan) -> Result<Self, String> {
        static PTX: std::sync::OnceLock<Result<cudarc::nvrtc::Ptx, String>> = std::sync::OnceLock::new();
        let ptx = PTX
            .get_or_init(|| {
                cudarc::nvrtc::compile_ptx_with_opts(
                    include_str!("rnr.cu"),
                    cudarc::nvrtc::CompileOptions { arch: Some(arch), ..Default::default() },
                )
                .map_err(e)
            })
            .clone()?;
        let module = ctx.load_module(ptx).map_err(e)?;
        let up_u = |v: &[u32]| stream.clone_htod(if v.is_empty() { &[0u32][..] } else { v }).map_err(e);
        let up_i = |v: &[i32]| stream.clone_htod(v).map_err(e);
        let k = p.seats.len();
        let mut roles = vec![Role { src: up_i(&p.src_mixed)?, foff: None, free_off: true }];
        for j in 0..k {
            roles.push(Role { src: up_i(&p.src_learn[j])?, foff: None, free_off: true });
        }
        for j in 0..k {
            roles.push(Role { src: up_i(&p.src_read[j])?, foff: Some(up_u(&p.foff_read[j])?), free_off: false });
        }
        let mut rf = vec![0f32; p.rf_blocks.max(1) * NUM_CLASSES];
        for j in 0..k {
            for h in 0..NUM_CLASSES {
                rf[j * NUM_CLASSES + h] = class_prob(h);
            }
        }
        Ok(Self {
            f_mix: module.load_function("pf_rnr_mix").map_err(e)?,
            trust: p.trust,
            hero: p.hero,
            seats: p.seats,
            free_len: p.free_len,
            d_off_free: up_u(&p.off_free)?,
            d_foff_mixed: up_u(&p.foff_mixed)?,
            roles,
            d_src_zero: stream.alloc_zeros::<i32>(p.src_mixed.len().max(1)).map_err(e)?,
            d_nodes: up_u(&p.nodes)?,
            spans: p.spans,
            d_loc: up_u(&p.loc)?,
            d_lock: up_u(&p.lock)?,
            d_mix_off: up_u(&p.mix_off)?,
            d_rs: stream.clone_htod(if p.rs.is_empty() { &[0f32][..] } else { &p.rs }).map_err(e)?,
            d_rf_in: up_u(&p.rf_in)?,
            d_rf_out: up_u(&p.rf_out)?,
            d_rf: stream.clone_htod(&rf).map_err(e)?,
        })
    }

    fn n_nodes(&self) -> u32 {
        self.spans.iter().map(|s| s.1).sum()
    }
}

impl PreflopGpu {
    /// Recompute every ruled seat's mixture: mode 0 from the free types'
    /// current strategies (learning), else from their averages, at trust t.
    fn rnr_mix(&mut self, r: &mut GpuRnr, mode: i32, t: f32) -> Result<(), String> {
        let base = self.arena_len as u32;
        for &(start, count) in &r.spans {
            let (start, count) = (start as i32, count as i32);
            unsafe {
                self.stream
                    .launch_builder(&r.f_mix)
                    .arg(&r.d_nodes)
                    .arg(&start)
                    .arg(&count)
                    .arg(&self.d_na)
                    .arg(&r.d_loc)
                    .arg(&base)
                    .arg(&self.d_regrets)
                    .arg(&self.d_strat)
                    .arg(&mode)
                    .arg(&r.d_lock)
                    .arg(&r.d_mix_off)
                    .arg(&mut self.d_forced)
                    .arg(&r.d_rs)
                    .arg(&r.d_rf_in)
                    .arg(&r.d_rf_out)
                    .arg(&mut r.d_rf)
                    .arg(&t)
                    .launch(Self::cfg(count as u32))
                    .map_err(e)?;
            }
        }
        Ok(())
    }

    /// Run `f` with role `i`'s tables swapped into the engine.
    fn rnr_with_role<T>(&mut self, r: &mut GpuRnr, i: usize, f: impl FnOnce(&mut Self) -> Result<T, String>) -> Result<T, String> {
        let swap = |g: &mut Self, r: &mut GpuRnr| {
            let role = &mut r.roles[i];
            std::mem::swap(&mut g.d_src, &mut role.src);
            match role.foff.as_mut() {
                Some(fo) => std::mem::swap(&mut g.d_foff, fo),
                None => std::mem::swap(&mut g.d_foff, &mut r.d_foff_mixed),
            }
            if role.free_off {
                std::mem::swap(&mut g.d_off, &mut r.d_off_free);
            }
        };
        swap(self, r);
        let out = f(self);
        swap(self, r);
        out
    }

    /// One iteration of the trust game: the hero's pass, each free type's,
    /// then DCFR discounting of the main and free arenas.
    pub(super) fn try_iterate_rnr(&mut self, iteration: &mut u32, stop: Option<&AtomicBool>) -> Result<bool, String> {
        let stopped = || stop.is_some_and(|f| f.load(Ordering::Relaxed));
        let mut r = self.rnr.take().expect("trust dial engine");
        let result = self.rnr_iterate_with(&mut r, iteration, &stopped);
        self.rnr = Some(r);
        result
    }

    fn rnr_iterate_with(&mut self, r: &mut GpuRnr, iteration: &mut u32, stopped: &dyn Fn() -> bool) -> Result<bool, String> {
        let k = r.seats.len();
        let mut passes = vec![(r.hero as i32, 0usize)];
        passes.extend(r.seats.iter().enumerate().map(|(j, &q)| (q as i32, 1 + j)));
        let trust = r.trust;
        for (p, role) in passes {
            if stopped() {
                self.stream.synchronize().map_err(e)?;
                return Ok(false);
            }
            let pass = |g: &mut Self, r: &mut GpuRnr| -> Result<(), String> {
                g.rnr_mix(r, 0, trust)?;
                g.rnr_with_role(r, role, |g| g.sweep(p, 0))
            };
            // hero and ruled seats are distinct: one graph per seat
            if self.warmed && self.learning_graphs[p as usize].is_none() {
                self.stream.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL).map_err(e)?;
                let result = pass(self, r);
                let graph = self.stream.end_capture(
                    sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH,
                ).map_err(e)?;
                result?;
                self.learning_graphs[p as usize] = Some(graph.ok_or_else(|| "preflop graph capture failed".to_string())?);
            }
            if let Some(graph) = &self.learning_graphs[p as usize] {
                graph.launch().map_err(e)?;
            } else {
                pass(self, r)?;
            }
        }
        debug_assert_eq!(r.roles.len(), 1 + 2 * k);
        if stopped() {
            self.stream.synchronize().map_err(e)?;
            return Ok(false);
        }
        *iteration += 1;
        let t = *iteration as f64;
        let pos = (t.powf(1.5) / (t.powf(1.5) + 1.0)) as f32;
        let neg = 0.5f32;
        let sd = ((t / (t + 1.0)).powi(2)) as f32;
        let n_act = self.n_act as i32;
        let n_free = r.n_nodes() as i32;
        unsafe {
            // main arenas, as try_iterate_counter (frozen sums kept)
            self.stream
                .launch_builder(&self.f_discount)
                .arg(&self.d_act_nodes)
                .arg(&n_act)
                .arg(&self.d_na)
                .arg(&self.d_off)
                .arg(&self.d_src)
                .arg(&mut self.d_regrets)
                .arg(&mut self.d_strat)
                .arg(&pos)
                .arg(&neg)
                .arg(&sd)
                .launch(Self::cfg(n_act as u32))
                .map_err(e)?;
            // free arenas: regrets and sums
            if n_free > 0 {
                self.stream
                    .launch_builder(&self.f_discount)
                    .arg(&r.d_nodes)
                    .arg(&n_free)
                    .arg(&self.d_na)
                    .arg(&r.d_off_free)
                    .arg(&r.d_src_zero)
                    .arg(&mut self.d_regrets)
                    .arg(&mut self.d_strat)
                    .arg(&pos)
                    .arg(&neg)
                    .arg(&sd)
                    .launch(Self::cfg(n_free as u32))
                    .map_err(e)?;
            }
        }
        self.stream.synchronize().map_err(e)?;
        self.warmed = true;
        Ok(true)
    }

    fn root_dot(&self) -> Result<f64, String> {
        let v: Vec<f32> = self.stream.clone_dtoh(&self.d_val.slice(0..NUM_CLASSES)).map_err(e)?;
        Ok((0..NUM_CLASSES).map(|h| class_prob(h) as f64 * v[h] as f64).sum())
    }

    /// Average-strategy evaluation of seats `ps` under role `role` (mixture
    /// at `t` from the free averages already in the forced table): per seat
    /// (best response, average) at the root.
    fn rnr_eval_role(&mut self, r: &mut GpuRnr, role: usize, ps: &[(i32, i32)]) -> Result<Vec<(f64, f64)>, String> {
        self.rnr_with_role(r, role, |g| {
            g.down(1, -1)?;
            let mut out = Vec::with_capacity(ps.len());
            for &(p, br_mode) in ps {
                g.terminals_masked(p, 0)?;
                let br = if br_mode > 0 {
                    g.up(p, br_mode)?;
                    g.root_dot()?
                } else {
                    0.0
                };
                g.up(p, 1)?;
                out.push((br, g.root_dot()?));
            }
            Ok(out)
        })
    }

    /// Gaps and EVs of the trust game, as `PreflopSolver::rnr_gaps_and_evs`.
    pub(super) fn rnr_gaps_and_evs(&mut self) -> Result<(Vec<f64>, Vec<f64>), String> {
        let mut r = self.rnr.take().expect("trust dial engine");
        let result = (|| {
            let np = self.np as usize;
            let k = r.seats.len();
            let t = r.trust;
            self.rnr_mix(&mut r, 1, t)?;
            let mut slot_of = vec![None; np];
            for (j, &q) in r.seats.iter().enumerate() {
                slot_of[q] = Some(j);
            }
            let constrained = self.constrained_br.clone();
            let br_mode = |p: usize| if constrained[p] { 3 } else { 2 };
            let others: Vec<(i32, i32)> = (0..np).filter(|&p| slot_of[p].is_none()).map(|p| (p as i32, br_mode(p))).collect();
            let mut gaps = vec![0f64; np];
            let mut evs = vec![0f64; np];
            for (&(p, _), (br, avg)) in others.iter().zip(self.rnr_eval_role(&mut r, 0, &others)?) {
                gaps[p as usize] = br - avg;
                evs[p as usize] = avg;
            }
            for j in 0..k {
                let q = r.seats[j];
                let read = self.rnr_eval_role(&mut r, 1 + k + j, &[(q as i32, br_mode(q))])?[0];
                let free = self.rnr_eval_role(&mut r, 1 + j, &[(q as i32, 3)])?[0];
                gaps[q] = free.0 - free.1;
                evs[q] = t as f64 * read.1 + (1.0 - t as f64) * free.1;
            }
            Ok((gaps, evs))
        })();
        self.rnr = Some(r);
        result
    }

    /// The trust readout from the device arenas.
    pub(super) fn rnr_readout(&mut self) -> Result<PfTrustReadout, String> {
        let mut r = self.rnr.take().expect("trust dial engine");
        let result = (|| {
            let hero = r.hero as i32;
            let mut ev = [0f64; 3];
            for (i, m) in [1.0f32, r.trust, 0.0].into_iter().enumerate() {
                self.rnr_mix(&mut r, 1, m)?;
                ev[i] = self.rnr_eval_role(&mut r, 0, &[(hero, 0)])?[0].1;
            }
            Ok(PfTrustReadout {
                trust: r.trust as f64,
                hero: r.hero,
                seats: r.seats.clone(),
                hero_ev_vs_read: ev[0],
                hero_ev_vs_mixture: ev[1],
                hero_ev_vs_adapting: ev[2],
            })
        })();
        self.rnr = Some(r);
        result
    }

    /// Download the free arenas into the CPU solver's `PfFree`.
    pub(super) fn rnr_sync_to_cpu(&self, s: &mut PreflopSolver) -> Result<(), String> {
        let Some(r) = self.rnr.as_ref() else { return Ok(()) };
        if r.free_len == 0 {
            return Ok(());
        }
        let span = self.arena_len..self.arena_len + r.free_len;
        let regs = self.stream.clone_dtoh(&self.d_regrets.slice(span.clone())).map_err(e)?;
        let strat = self.stream.clone_dtoh(&self.d_strat.slice(span)).map_err(e)?;
        s.sync_pf_free();
        match s.pf_free.as_deref() {
            Some(f) if f.hero == r.hero && f.seats == r.seats && f.len == r.free_len => {
                // SAFETY: &mut PreflopSolver, no traversal running
                unsafe {
                    f.regrets.slice_mut().copy_from_slice(&regs);
                    f.strat.slice_mut().copy_from_slice(&strat);
                }
                Ok(())
            }
            _ => Err("the trust dial changed under the GPU solve".into()),
        }
    }
}
