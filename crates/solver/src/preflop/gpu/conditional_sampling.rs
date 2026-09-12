//! Fixed-current-policy sampling diagnostics. No learning or persistent state.
use super::*;
use crate::preflop::convergence_research::Experiment;
use serde_json::{json, Value};

impl PreflopSolver {
    // This workspace never escapes into a solve or a saved game. Positive raw
    // regrets, rather than renormalized probabilities, preserve the 1e-12
    // normalization-floor behavior exactly when read as strategy sums.
    fn sampling_current_workspace(&self) -> Result<Self, String> {
        if self.nodes.len() > 50_000
            || self.arena_len.saturating_mul(8) > 128 * 1024 * 1024
            || self.multiway_equity_model() != "coupled_deck_v1"
            || self.stop_requested()
        {
            return Err("sampling diagnostic requires a stopped bounded canonical game".into());
        }
        let mut w = Self::new(self.cfg.clone(), self.eq.clone())?;
        if w.nodes.len() != self.nodes.len()
            || w.arena_len != self.arena_len
            || w.children != self.children
        {
            return Err("sampling workspace tree changed".into());
        }
        for (a, b) in self.nodes.iter().zip(&w.nodes) {
            if a.kind != b.kind
                || a.actor != b.actor
                || a.actions.len() != b.actions.len()
                || a.child_start != b.child_start
                || a.data_off != b.data_off
                || a.pot != b.pot
                || a.invested != b.invested
                || a.live != b.live
                || a.winner != b.winner
                || a.r != b.r
                || a.aggressor != b.aggressor
                || a.posf != b.posf
                || a.bucket != b.bucket
                || a.raises != b.raises
                || a.raised != b.raised
                || a.actions
                    .iter()
                    .zip(&b.actions)
                    .any(|(a, b)| a.kind != b.kind || a.to != b.to)
            {
                return Err("sampling workspace geometry or payoff changed".into());
            }
        }
        w.fit = self.fit.clone();
        w.realization_note = self.realization_note.clone();
        w.multiway = self.multiway.clone();
        w.seat_profiles = self.seat_profiles.clone();
        w.seat_frozen = self.seat_frozen.clone();
        w.hero = self.hero;
        w.pre_hero_frozen = self.pre_hero_frozen.clone();
        w.hero_backup = self.hero_backup.clone();
        w.point_locks = self.point_locks.clone();
        w.prune = self.prune;
        w.stop_flag = self.stop_flag.clone();
        // SAFETY: source is read-only and the audit workspace is exclusively
        // owned. Its averages alone are evaluated; its regrets stay unused.
        unsafe {
            let r = self.regrets.slice();
            let sums = self.strat_sum.slice();
            if r.iter().chain(sums).any(|v| !v.is_finite()) || sums.iter().any(|v| *v < 0.0) {
                return Err("invalid source histories".into());
            }
            let dst = w.strat_sum.slice_mut();
            dst.copy_from_slice(sums);
            for (i, nd) in self.nodes.iter().enumerate() {
                if nd.kind != KIND_ACTION
                    || self.seat_frozen[nd.actor as usize]
                    || self.forced_sigma(i).is_some()
                {
                    continue;
                }
                for ix in nd.data_off..nd.data_off + nd.actions.len() * NUM_CLASSES {
                    dst[ix] = r[ix].max(0.0);
                }
            }
        }
        for (i, nd) in self.nodes.iter().enumerate() {
            if nd.kind != KIND_ACTION {
                continue;
            }
            let expected = if let Some(p) = self.forced_sigma(i) {
                p
            } else if self.seat_frozen[nd.actor as usize] {
                self.average_strategy(i)
            } else {
                let mut p = vec![0.; nd.actions.len() * NUM_CLASSES];
                self.current_strategy(i, &mut p);
                p
            };
            if w.average_strategy(i) != expected {
                return Err("current-policy snapshot mismatch".into());
            }
        }
        Ok(w)
    }

    /// Enumerate the existing 64-particle cyclic sampler at a fixed current
    /// policy, keeping every action value so independent code can recompute
    /// regret-difference variance and covariance. No optimizer is enabled.
    pub fn research_conditional_sampling_gpu(
        &self,
        paths: &[Vec<usize>],
        budget_mb: u64,
    ) -> Result<Value, String> {
        self.conditional_sampling_gpu(paths, budget_mb, false)
    }

    /// The same frozen-policy diagnostic with the existing pair correction.
    /// This does not install or qualify a normalized learning combination.
    pub fn research_conditional_pair_sampling_gpu(
        &self,
        paths: &[Vec<usize>],
        budget_mb: u64,
    ) -> Result<Value, String> {
        self.conditional_sampling_gpu(paths, budget_mb, true)
    }

    fn conditional_sampling_gpu(
        &self,
        paths: &[Vec<usize>],
        budget_mb: u64,
        pair_control: bool,
    ) -> Result<Value, String> {
        if paths.is_empty()
            || paths.len() > 6
            || paths.iter().any(|p| p.len() > 64)
            || paths.iter().collect::<std::collections::HashSet<_>>().len() != paths.len()
        {
            return Err("sampling diagnostic requires 1..6 distinct bounded paths".into());
        }
        let before = self.arena_snapshot();
        let w = self.sampling_current_workspace()?;
        let mut selected = Vec::new();
        let mut metadata = Vec::new();
        for path in paths {
            let (node, _) = w.walk(path)?;
            let nd = &w.nodes[node];
            if nd.kind != KIND_ACTION {
                return Err("sampling path must be an action node".into());
            }
            selected.push((path.len(), node));
            metadata.push(json!({"path":path,"node":node,"actor":nd.actor,"source":self.research_node_learning_diagnostics(path)?,
                "cpu_reference":w.research_local_action_quality_against(&w,path)?,
                "current_sigma_action_major":w.average_strategy(node)}));
        }
        let ws_before = w.arena_snapshot();
        let mut g = PreflopGpu::new(&w, budget_mb)?;
        g.configure_research(Experiment::new("gamma15", 64, 1000, 42)?)?;
        let pair_extra_bytes = if pair_control {
            g.enable_research_pair_control(1024)?
        } else {
            0
        };
        g.research_tables(false)?;
        g.down(1, -1)?;
        let slots = g.stream.clone_dtoh(&g.d_val_slot).map_err(e)?;
        let reach_src = g.stream.clone_dtoh(&g.d_reach_src).map_err(e)?;
        let masses = g.stream.clone_dtoh(&g.d_reach_mass).map_err(e)?;
        for ((_, node), row) in selected.iter().zip(&mut metadata) {
            let mut denominator = 1f32;
            let p = w.nodes[*node].actor as usize;
            let prefix: Vec<f32> = (0..w.n)
                .map(|q| masses[reach_src[node * w.n + q] as usize])
                .collect();
            for (q, mass) in prefix.iter().enumerate() {
                if q != p {
                    denominator *= mass;
                }
            }
            row["gpu_prefix_mass_by_seat"] = json!(prefix);
            row["normalized_regret_denominator_f32"] = json!(denominator.max(1e-12));
            row["zero_opponent_reach"] = json!(denominator == 0.0);
        }
        let full = g.sampling_action_draw(&w, &selected, &slots)?;
        for (row, values) in metadata.iter().zip(&full) {
            let cpu = &row["cpu_reference"];
            if cpu["status"] == "unreachable_under_reference" {
                continue;
            }
            let mass = cpu["opponent_mass"].as_f64().ok_or("CPU mass missing")?;
            for (h, hand) in cpu["hands"]
                .as_array()
                .ok_or("CPU hands missing")?
                .iter()
                .enumerate()
            {
                for (a, q) in hand["action_values_bb"]
                    .as_array()
                    .ok_or("CPU actions missing")?
                    .iter()
                    .enumerate()
                {
                    let expected = q.as_f64().ok_or("CPU value missing")? * mass;
                    if (values[a * NUM_CLASSES + h] as f64 - expected).abs()
                        > 0.0002 * (1. + expected.abs())
                    {
                        return Err(
                            "full GPU current-policy value differs from CPU reference".into()
                        );
                    }
                }
            }
        }
        let mut draws = vec![Vec::with_capacity(1024); paths.len()];
        for offset in 0..1024 {
            if self.stop_requested() {
                return Err("sampling diagnostic canceled".into());
            }
            g.research.as_mut().unwrap().offset = offset;
            g.research_tables_select(true, false)?;
            let values = g.sampling_action_draw(&w, &selected, &slots)?;
            for (target, value) in draws.iter_mut().zip(values) {
                target.push(value);
            }
        }
        g.research_tables(false)?;
        if g.sampling_action_draw(&w, &selected, &slots)? != full {
            return Err("full restore changed action values".into());
        }
        if g.stream.clone_dtoh(&g.d_regrets).map_err(e)? != ws_before.0
            || g.stream.clone_dtoh(&g.d_strat).map_err(e)? != ws_before.1
            || self.arena_snapshot() != before
            || w.arena_snapshot() != ws_before
        {
            return Err("sampling diagnostic modified histories".into());
        }
        for ((row, values), samples) in metadata.iter_mut().zip(full).zip(draws) {
            row["full_action_values_raw_action_major"] = json!(values);
            row["offset_action_values_raw_action_major"] = json!(samples);
        }
        Ok(
            json!({"nodes":self.nodes.len(),"source_iteration":self.iteration,"samples":64,"offsets":1024,
            "rows":metadata,"source_and_device_histories_unchanged":true,"full_restore_exact":true,
            "pair_control":pair_control,"pair_extra_bytes":pair_extra_bytes,
            "policy":"Frozen current policy, original fixed constraints; no learning or age advance",
            "scope":"Fixed-state action-value sampling evidence only; no convergence or speed qualification"}),
        )
    }
}

impl PreflopGpu {
    fn sampling_action_draw(
        &mut self,
        s: &PreflopSolver,
        selected: &[(usize, usize)],
        slots: &[u32],
    ) -> Result<Vec<Vec<f32>>, String> {
        let mut rows = vec![Vec::new(); selected.len()];
        for p in 0..s.n {
            if !selected
                .iter()
                .any(|(_, node)| s.nodes[*node].actor as usize == p)
            {
                continue;
            }
            self.terminals_masked(p as i32, 0)?;
            for li in (0..self.spans.len()).rev() {
                for (i, (depth, node)) in selected.iter().enumerate() {
                    if *depth != li || s.nodes[*node].actor as usize != p {
                        continue;
                    }
                    for a in 0..s.nodes[*node].actions.len() {
                        let off = slots[s.child(*node, a)] as usize * NUM_CLASSES;
                        rows[i].extend(
                            self.stream
                                .clone_dtoh(&self.d_val.slice(off..off + NUM_CLASSES))
                                .map_err(e)?,
                        );
                    }
                }
                let (start, count) = self.spans[li];
                if count == 0 {
                    continue;
                }
                let (start, count, mode, p) = (start as i32, count as i32, 1i32, p as i32);
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up)
                        .arg(&self.d_act_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&p)
                        .arg(&self.np)
                        .arg(&mode)
                        .arg(&self.d_actor)
                        .arg(&self.d_na)
                        .arg(&self.d_off)
                        .arg(&self.d_cstart)
                        .arg(&self.d_children)
                        .arg(&self.d_src)
                        .arg(&self.d_foff)
                        .arg(&self.d_forced)
                        .arg(&self.d_reach_src)
                        .arg(&self.d_reach)
                        .arg(&mut self.d_regrets)
                        .arg(&mut self.d_strat)
                        .arg(&self.d_val_slot)
                        .arg(&mut self.d_val)
                        .launch(Self::cfg(count as u32))
                        .map_err(e)?;
                }
            }
        }
        if rows
            .iter()
            .any(|r| r.is_empty() || r.iter().any(|v| !v.is_finite()))
        {
            return Err("invalid sampled action values".into());
        }
        Ok(rows)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{equity::EquityTable, PreflopConfig};

    fn fixture() -> PreflopSolver {
        let cfg: PreflopConfig = serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],
            "stack":5,"posts":[0,0,0.5,1],"limp":true,"open_raises":[2],"raise_mults":[],
            "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"}))
        .unwrap();
        let mut s = PreflopSolver::new(cfg, Arc::new(EquityTable::build(8))).unwrap();
        s.research_seed_quality_fixture_averages().unwrap();
        unsafe {
            for (i, r) in s.regrets.slice_mut().iter_mut().enumerate() {
                *r = match i % 7 {
                    0 => -1.,
                    1 => 0.,
                    2 => 1e-14,
                    _ => (1 + i % 13) as f32,
                };
            }
        }
        s.seat_frozen[2] = true;
        // An unreachable subtree and a nonuniform point lock must retain
        // their source meaning in the temporary current-policy workspace.
        let na = s.nodes[0].actions.len();
        let mut locked = vec![0.; na * NUM_CLASSES];
        for a in 1..na {
            locked[a * NUM_CLASSES..(a + 1) * NUM_CLASSES].fill(1. / (na - 1) as f32);
        }
        s.point_locks.insert(0, locked);
        s
    }

    #[test]
    fn sampling_current_workspace_preserves_constraints_and_floor() {
        let mut s = fixture();
        // Explicitly exercise an all-subfloor positive-history decision.
        let node = s.child(0, 1);
        let nd = &s.nodes[node];
        unsafe {
            s.regrets.slice_mut()[nd.data_off..nd.data_off + nd.actions.len() * NUM_CLASSES]
                .fill(1e-14);
        }
        let before = s.arena_snapshot();
        let w = s.sampling_current_workspace().unwrap();
        assert_eq!(before, s.arena_snapshot());
        assert_eq!(w.point_locks, s.point_locks);
        assert_eq!(w.seat_frozen, s.seat_frozen);
        for path in [vec![], vec![0], vec![1]] {
            let d = s.research_node_learning_diagnostics(&path).unwrap();
            let (node, _) = w.walk(&path).unwrap();
            let actual = w.average_strategy(node);
            for (h, hand) in d["hands"].as_array().unwrap().iter().enumerate() {
                for (a, p) in hand["current_probabilities"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .enumerate()
                {
                    assert_eq!(actual[a * NUM_CLASSES + h] as f64, p.as_f64().unwrap());
                }
            }
        }
        s.multiway = None;
        assert!(s.sampling_current_workspace().is_err());
    }

    #[test]
    fn conditional_sampling_gpu_enumeration_matches_full_and_preserves_histories() {
        let s = fixture();
        let before = s.arena_snapshot();
        assert!(s.research_conditional_sampling_gpu(&[], 512).is_err());
        assert!(s
            .research_conditional_sampling_gpu(&[vec![], vec![]], 512)
            .is_err());
        let paths = vec![vec![], vec![0], vec![1], vec![1, 1]];
        let result = s.research_conditional_sampling_gpu(&paths, 512).unwrap();
        assert_eq!(before, s.arena_snapshot());
        assert_eq!(result["source_and_device_histories_unchanged"], true);
        assert_eq!(result["full_restore_exact"], true);
        let mut varying = false;
        for row in result["rows"].as_array().unwrap() {
            let full = row["full_action_values_raw_action_major"]
                .as_array()
                .unwrap();
            let draws = row["offset_action_values_raw_action_major"]
                .as_array()
                .unwrap();
            assert_eq!(draws.len(), 1024);
            for (ix, q) in full.iter().enumerate() {
                let q = q.as_f64().unwrap();
                let mut total = 0.;
                for draw in draws {
                    assert_eq!(draw.as_array().unwrap().len(), full.len());
                    let v = draw[ix].as_f64().unwrap();
                    total += v;
                    varying |= (v - q).abs() > 0.001;
                }
                assert!(
                    (total / 1024. - q).abs() <= 0.0002 * (1. + q.abs()),
                    "cyclic mean differs from full value"
                );
            }
        }
        assert!(
            varying,
            "fixture never exercised sampled multiway variation"
        );
    }

    #[test]
    fn conditional_pair_sampling_gpu_preserves_reference_and_changes_draws() {
        let s = fixture();
        let before = s.arena_snapshot();
        let paths = vec![vec![], vec![0], vec![1], vec![1, 1]];
        let base = s.research_conditional_sampling_gpu(&paths, 512).unwrap();
        let corrected = s
            .research_conditional_pair_sampling_gpu(&paths, 512)
            .unwrap();
        assert_eq!(before, s.arena_snapshot());
        assert_eq!(corrected["pair_control"], true);
        assert!(corrected["pair_extra_bytes"].as_u64().unwrap() > 0);
        assert_eq!(corrected["source_and_device_histories_unchanged"], true);
        assert_eq!(corrected["full_restore_exact"], true);
        let mut changed = false;
        let mut zero_reach = false;
        for (a, b) in base["rows"]
            .as_array()
            .unwrap()
            .iter()
            .zip(corrected["rows"].as_array().unwrap())
        {
            for key in [
                "source",
                "current_sigma_action_major",
                "gpu_prefix_mass_by_seat",
                "full_action_values_raw_action_major",
            ] {
                assert_eq!(a[key], b[key]);
            }
            zero_reach |= b["zero_opponent_reach"] == true;
            let full = b["full_action_values_raw_action_major"].as_array().unwrap();
            let draws = b["offset_action_values_raw_action_major"]
                .as_array()
                .unwrap();
            for (ix, q) in full.iter().enumerate() {
                let mut total = 0.;
                for (offset, draw) in draws.iter().enumerate() {
                    let value = draw[ix].as_f64().unwrap();
                    assert!(value.is_finite());
                    total += value;
                    changed |= (value
                        - a["offset_action_values_raw_action_major"][offset][ix]
                            .as_f64()
                            .unwrap())
                    .abs()
                        > 0.001;
                }
                let q = q.as_f64().unwrap();
                assert!((total / 1024. - q).abs() <= 0.0002 * (1. + q.abs()));
            }
        }
        assert!(changed && zero_reach);
    }
}
