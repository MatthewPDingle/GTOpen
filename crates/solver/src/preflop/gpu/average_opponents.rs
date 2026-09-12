//! Offline learning-target experiment; never used by native evaluation.
use super::*;

impl PreflopGpu {
    pub fn enable_research_average_opponents(&mut self) -> Result<(), String> {
        if self.research_rm_plus.is_some() || self.warmed
            || self.eval_warmed
            || self.research_learning_mask
            || self.research_root_ranges.is_some()
            || self.research_cv.is_some()
            || self.research_history_units.is_some()
            || self.research_exploration.is_some()
            || self.research_average_opponents.is_some()
            || self.research.is_none()
            || self.research_normalized_regret.is_none()
            || self.research_pair_control.is_none()
        {
            return Err(
                "average opponents requires a fresh configured normalized-pair engine".into(),
            );
        }
        let source = [
            include_str!("../kernels.cu"),
            include_str!("average_opponents.cu"),
        ]
        .join("\n");
        let module = self
            ._ctx
            .load_module(cudarc::nvrtc::compile_ptx(source).map_err(e)?)
            .map_err(e)?;
        self.research_average_opponents = Some(
            module
                .load_function("pf_average_opponents_reach")
                .map_err(e)?,
        );
        Ok(())
    }

    pub(super) fn research_average_opponent_reach(
        &mut self,
        start: i32,
        count: i32,
        p: i32,
        mode: i32,
    ) -> Result<(), String> {
        if mode != 0 || p < 0 {
            return Ok(());
        }
        let Some(function) = &self.research_average_opponents else {
            return Ok(());
        };
        unsafe {
            self.stream
                .launch_builder(function)
                .arg(&self.d_act_nodes)
                .arg(&start)
                .arg(&count)
                .arg(&p)
                .arg(&self.np)
                .arg(&self.d_actor)
                .arg(&self.d_na)
                .arg(&self.d_off)
                .arg(&self.d_cstart)
                .arg(&self.d_children)
                .arg(&self.d_src)
                .arg(&self.d_reach_src)
                .arg(&self.d_strat)
                .arg(&mut self.d_reach)
                .launch(Self::cfg(count as u32))
                .map_err(e)?;
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
            "positions":["CO","BTN","SB","BB"], "posts":[0,0,0.5,1],
            "stack":5, "limp":true, "open_raises":[2], "raise_mults":[],
            "max_raises":1, "add_allin":false, "rake_pct":5, "rake_cap":1,
            "realization":if calibrated {"calibrated"} else {"raw"}
        }))
        .unwrap();
        let mut s = PreflopSolver::new(cfg, Arc::new(EquityTable::build(8))).unwrap();
        if calibrated {
            assert!(s.fit.is_some());
        }
        s.research_seed_quality_fixture_averages().unwrap();
        // Deliberately different current and average policies; native current
        // routing drops actions which still have positive average reach.
        for nd in &s.nodes {
            for a in 0..nd.actions.len() {
                for h in 0..NUM_CLASSES {
                    unsafe {
                        s.regrets.slice_mut()[nd.data_off + a * NUM_CLASSES + h] =
                            if a == h % nd.actions.len() { 2.0 } else { -1.0 };
                    }
                }
            }
        }
        s.seat_frozen[2] = true;
        let node = s.child(0, 1);
        let mut lock = vec![0.0; s.nodes[node].actions.len() * NUM_CLASSES];
        lock[..NUM_CLASSES].fill(1.0);
        s.point_locks.insert(node as u32, lock);
        s
    }

    fn configured(s: &PreflopSolver) -> PreflopGpu {
        let mut g = PreflopGpu::new(s, 512).unwrap();
        g.configure_research(Experiment::new("gamma15", 64, 1000, 42).unwrap())
            .unwrap();
        g.enable_research_normalized_pair_control(100).unwrap();
        g
    }

    #[test]
    fn average_opponents_matches_independent_frozen_opponent_sweeps() {
        for calibrated in [false, true] {
            for p in [0, 1, 3] {
                let s = fixture(calibrated);
                let before = s.arena_snapshot();
                let mut reference = fixture(calibrated);
                for q in 0..s.n {
                    if q != p {
                        reference.seat_frozen[q] = true;
                    }
                }
                let mut base = configured(&reference);
                let mut candidate = configured(&s);
                candidate.enable_research_average_opponents().unwrap();
                for g in [&mut base, &mut candidate] {
                    g.research_tables(true).unwrap();
                    g.down(0, p as i32).unwrap();
                }
                assert_eq!(
                    base.stream.clone_dtoh(&base.d_reach).unwrap(),
                    candidate.stream.clone_dtoh(&candidate.d_reach).unwrap()
                );
                assert_eq!(
                    base.stream.clone_dtoh(&base.d_reach_mass).unwrap(),
                    candidate
                        .stream
                        .clone_dtoh(&candidate.d_reach_mass)
                        .unwrap()
                );
                for g in [&mut base, &mut candidate] {
                    g.terminals_masked(p as i32, 0).unwrap();
                    g.up(p as i32, 0).unwrap();
                }
                let br = base.stream.clone_dtoh(&base.d_regrets).unwrap();
                let cr = candidate.stream.clone_dtoh(&candidate.d_regrets).unwrap();
                let ba = base.stream.clone_dtoh(&base.d_strat).unwrap();
                let ca = candidate.stream.clone_dtoh(&candidate.d_strat).unwrap();
                let bv = base.stream.clone_dtoh(&base.d_val).unwrap();
                let cv = candidate.stream.clone_dtoh(&candidate.d_val).unwrap();
                for (x, y) in br
                    .iter()
                    .zip(&cr)
                    .chain(ba.iter().zip(&ca))
                    .chain(bv.iter().zip(&cv))
                {
                    assert!(
                        x.is_finite() && y.is_finite() && (x - y).abs() <= 2e-5 * (1.0 + x.abs())
                    );
                }
                let sources = candidate.stream.clone_dtoh(&candidate.d_src).unwrap();
                let mut changed = 0;
                for (i, nd) in s.nodes.iter().enumerate() {
                    for ix in nd.data_off..nd.data_off + nd.actions.len() * NUM_CLASSES {
                        if nd.actor as usize != p || sources[i] != 0 {
                            assert_eq!(cr[ix], before.0[ix]);
                            assert_eq!(ca[ix], before.1[ix]);
                        } else if cr[ix] != before.0[ix] {
                            changed += 1;
                        }
                    }
                }
                assert!(changed > 0);
            }
        }
    }

    #[test]
    fn average_opponents_capture_and_native_evaluation() {
        let mut records = Vec::new();
        for eager in [false, true] {
            let mut s = fixture(false);
            let before = s.arena_snapshot();
            let mut gpu = PreflopGpu::new(&s, 512).unwrap();
            assert!(gpu.enable_research_average_opponents().is_err());
            gpu.configure_research(Experiment::new("gamma15", 64, 1000, 42).unwrap())
                .unwrap();
            assert!(gpu.enable_research_average_opponents().is_err());
            gpu.enable_research_normalized_pair_control(100).unwrap();
            gpu.enable_research_average_opponents().unwrap();
            assert!(gpu.enable_research_average_opponents().is_err());
            assert!(gpu.enable_research_opponent_exploration(0.01, 250).is_err());
            for _ in 0..4 {
                if eager {
                    gpu.warmed = false;
                    for graph in &mut gpu.learning_graphs {
                        *graph = None;
                    }
                }
                gpu.iterate(&mut s).unwrap();
            }
            assert!(gpu.enable_research_average_opponents().is_err());
            gpu.sync_to_cpu(&mut s).unwrap();
            let snapshot = s.arena_snapshot();
            let sources = gpu.stream.clone_dtoh(&gpu.d_src).unwrap();
            let schedule = Experiment::new("gamma15", 64, 1000, 42).unwrap();
            for (i, nd) in s.nodes.iter().enumerate() {
                if sources[i] != 0 {
                    let end = nd.data_off + nd.actions.len() * NUM_CLASSES;
                    for ix in nd.data_off..end {
                        let (mut regret, mut average) = (before.0[ix], before.1[ix]);
                        for age in 1..=4 {
                            let (positive, negative, averaging) = schedule.factors(age);
                            regret *= if regret > 0.0 { positive } else { negative };
                            if sources[i] != 1 {
                                average *= averaging;
                            }
                        }
                        assert_eq!(snapshot.0[ix], regret);
                        assert_eq!(snapshot.1[ix], average);
                    }
                }
            }
            // An ordinary engine on the same saved histories must evaluate
            // exactly the same game, independent of the learning extension.
            let mut native = PreflopGpu::new(&s, 512).unwrap();
            let actual = gpu.gaps_and_evs().unwrap();
            assert_eq!(actual, native.gaps_and_evs().unwrap());
            let cpu = s.gaps_and_evs();
            assert!(actual
                .0
                .iter()
                .chain(&actual.1)
                .zip(cpu.0.iter().chain(&cpu.1))
                .all(|(a, b)| (a - b).abs() < 0.005));
            gpu.sync_to_cpu(&mut s).unwrap();
            assert_eq!(snapshot, s.arena_snapshot());
            records.push((snapshot, actual));
        }
        assert_eq!(records[0], records[1]);
    }
}
