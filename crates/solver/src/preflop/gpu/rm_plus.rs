//! Fresh-state regret matching+ with native payoff units and linear averaging.
use super::*;

impl PreflopGpu {
    /// Offline only. Configure sampling and optional pair control first.
    /// Frozen/forced histories may be populated, but learning histories must
    /// start at zero. No ordinary resumed DCFR history is reinterpreted.
    pub fn enable_research_rm_plus(&mut self) -> Result<(), String> {
        if !self.research_rm_plus_fresh || self.warmed || self.eval_warmed
            || self.research_predictive.is_some() || self.research_rm_plus.is_some() || self.research.is_none()
            || self.research_cv.is_some() || self.research_learning_mask
            || self.research_root_ranges.is_some() || self.research_normalized_regret.is_some()
            || self.research_exploration.is_some() || self.research_history_units.is_some()
            || self.research_average_opponents.is_some()
        {
            return Err("RM+ requires a fresh configured native-payoff research engine with zero learning histories".into());
        }
        let module = self._ctx.load_module(
            cudarc::nvrtc::compile_ptx(include_str!("rm_plus.cu")).map_err(e)?
        ).map_err(e)?;
        self.research_rm_plus = Some(module.load_function("pf_rm_plus_clip").map_err(e)?);
        Ok(())
    }

    pub(super) fn research_rm_plus_clip(&mut self, p: i32) -> Result<(), String> {
        let Some(function) = &self.research_rm_plus else { return Ok(()) };
        let count = self.n_act as i32;
        unsafe {
            self.stream.launch_builder(function).arg(&self.d_act_nodes).arg(&count)
                .arg(&p).arg(&self.d_actor).arg(&self.d_na).arg(&self.d_off)
                .arg(&self.d_src).arg(&mut self.d_regrets)
                .launch(Self::cfg(self.n_act)).map_err(e)?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{convergence_research::Experiment, equity::EquityTable, PreflopConfig};

    fn fixture(calibrated: bool) -> PreflopSolver {
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"],"posts":[0,0,0.5,1],
            "stack":5,"limp":true,"open_raises":[2],"raise_mults":[3],
            "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,
            "realization":if calibrated {"calibrated"} else {"raw"}
        })).unwrap();
        let mut s = PreflopSolver::new(cfg, Arc::new(EquityTable::build(8))).unwrap();
        if calibrated { assert!(s.fit.is_some()); }
        s.seat_frozen[2] = true;
        let node = s.child(0, 0);
        let mut lock = vec![0.; s.nodes[node].actions.len()*NUM_CLASSES];
        lock[..NUM_CLASSES].fill(1.);
        s.point_locks.insert(node as u32, lock);
        // Nonzero constrained histories expose accidental clipping/discounting
        // that an all-zero frozen fixture would miss.
        unsafe {
            let r = s.regrets.slice_mut();
            let sums = s.strat_sum.slice_mut();
            for (i, nd) in s.nodes.iter().enumerate() {
                if nd.actor != 2 && i != node { continue; }
                for ix in nd.data_off..nd.data_off + nd.actions.len()*NUM_CLASSES {
                    r[ix] = if ix % 2 == 0 { -0.25 } else { 0.5 };
                    sums[ix] = (1 + ix % 7) as f32 / 10.;
                }
            }
        }
        s
    }

    fn engine(s: &PreflopSolver, samples: u32, plus: bool) -> PreflopGpu {
        let mut g = PreflopGpu::new(s, 512).unwrap();
        g.configure_research(Experiment::new("dcfr", samples, 1000, 42).unwrap()).unwrap();
        if samples == 64 { g.enable_research_pair_control(100).unwrap(); }
        if plus { g.enable_research_rm_plus().unwrap(); }
        g
    }

    fn close(a: &[f32], b: &[f32]) {
        assert_eq!(a.len(), b.len());
        for (i, (&x, &y)) in a.iter().zip(b).enumerate() {
            assert!(x.is_finite() && y.is_finite() && (x-y).abs() <= 2e-6*(1.+y.abs()),
                "entry {i}: {x} != {y}");
        }
    }

    #[test]
    fn rm_plus_matches_host_clipping_and_linear_averages() {
        for calibrated in [false, true] { for samples in [1024, 64] {
            let mut s = fixture(calibrated);
            let mut reference = engine(&s, samples, false);
            let mut candidate = engine(&s, samples, true);
            let src = candidate.stream.clone_dtoh(&candidate.d_src).unwrap();
            let mut clipped = 0;
            for t in 1..=4 {
                // Independent host arithmetic: native unmodified sweep, then
                // clip precisely the updated actor, then explicit t/(t+1).
                for p in 0..s.n {
                    if reference.static_seats[p] { continue; }
                    reference.research_tables(true).unwrap();
                    reference.sweep(p as i32, 0).unwrap();
                    let mut r = reference.stream.clone_dtoh(&reference.d_regrets).unwrap();
                    for (nd, &source) in s.nodes.iter().zip(&src) {
                        if nd.actor as usize != p || source != 0 { continue; }
                        for v in &mut r[nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES] {
                            if *v < 0. { clipped += 1; *v = 0.; }
                        }
                    }
                    reference.stream.memcpy_htod(&r, &mut reference.d_regrets).unwrap();
                }
                let mut sums = reference.stream.clone_dtoh(&reference.d_strat).unwrap();
                let discount = (t as f64 / (t as f64 + 1.)) as f32;
                for (nd, &source) in s.nodes.iter().zip(&src) {
                    if source == 1 { continue; }
                    for v in &mut sums[nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES] { *v *= discount; }
                }
                reference.stream.memcpy_htod(&sums, &mut reference.d_strat).unwrap();
                candidate.iterate(&mut s).unwrap();
                close(&candidate.stream.clone_dtoh(&candidate.d_regrets).unwrap(),
                    &reference.stream.clone_dtoh(&reference.d_regrets).unwrap());
                close(&candidate.stream.clone_dtoh(&candidate.d_strat).unwrap(), &sums);
            }
            assert!(clipped > 0);
            let before = (candidate.stream.clone_dtoh(&candidate.d_regrets).unwrap(),
                candidate.stream.clone_dtoh(&candidate.d_strat).unwrap());
            let actual = candidate.gaps_and_evs().unwrap();
            assert_eq!(before.0, candidate.stream.clone_dtoh(&candidate.d_regrets).unwrap());
            assert_eq!(before.1, candidate.stream.clone_dtoh(&candidate.d_strat).unwrap());
            candidate.sync_to_cpu(&mut s).unwrap();
            let mut native = PreflopGpu::new(&s, 512).unwrap();
            assert_eq!(actual, native.gaps_and_evs().unwrap());
            let cpu = s.gaps_and_evs();
            assert!(actual.0.iter().chain(&actual.1).zip(cpu.0.iter().chain(&cpu.1))
                .all(|(a,b)| a.is_finite() && b.is_finite() && (a-b).abs() < 0.005));
        }}
    }

    #[test]
    fn rm_plus_capture_and_admission() {
        let mut records = Vec::new();
        for eager in [false, true] {
            let mut s = fixture(false);
            let mut g = engine(&s, 64, true);
            assert!(g.enable_research_rm_plus().is_err());
            assert!(g.enable_research_normalized_regret().is_err());
            assert!(g.enable_research_normalized_pair_control(100).is_err());
            assert!(g.enable_research_opponent_exploration(0.01,250).is_err());
            assert!(g.enable_research_control_variate(1,100).is_err());
            assert!(g.enable_research_average_opponents().is_err());
            assert!(g.configure_research(Experiment::new("gamma15",64,1000,42).unwrap()).is_err());
            for _ in 0..4 {
                if eager { g.warmed = false; for graph in &mut g.learning_graphs { *graph = None; } }
                g.iterate(&mut s).unwrap();
            }
            g.sync_to_cpu(&mut s).unwrap();
            records.push(s.arena_snapshot());
            let mut resumed = engine(&s, 64, false);
            assert!(resumed.enable_research_rm_plus().is_err());
            s.iteration = 0; // Resetting age alone must not admit learned arenas.
            let mut dirty = engine(&s, 64, false);
            assert!(dirty.enable_research_rm_plus().is_err());
        }
        assert_eq!(records[0], records[1]);
        let s = fixture(false);
        let mut missing = PreflopGpu::new(&s,512).unwrap();
        assert!(missing.enable_research_rm_plus().is_err());
        let mut normalized = engine(&s,1024,false);
        normalized.enable_research_normalized_regret().unwrap();
        assert!(normalized.enable_research_rm_plus().is_err());
        let mut used = engine(&s,1024,false);
        used.gaps_and_evs().unwrap();
        assert!(used.enable_research_rm_plus().is_err());
    }
}
