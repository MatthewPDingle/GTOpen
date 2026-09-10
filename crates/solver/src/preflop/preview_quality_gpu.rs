//! Research-only large-tree policy audit. No learning, saving or input mutation.
use super::*;
use serde_json::{json, Value};

const MAX_NODES: usize = 2_000_000;
const MAX_ARENA_BYTES: usize = 3 * 1024 * 1024 * 1024;

fn same_json<T: Serialize>(a: &T, b: &T) -> Result<bool, String> {
    Ok(serde_json::to_value(a).map_err(|e| e.to_string())?
        == serde_json::to_value(b).map_err(|e| e.to_string())?)
}

fn validate_tree(a: &PreflopSolver, b: &PreflopSolver) -> Result<(), String> {
    if a.nodes.len() != b.nodes.len() || a.arena_len != b.arena_len || a.children != b.children {
        return Err("quality inputs have different tree layouts".into());
    }
    for (i, (x, y)) in a.nodes.iter().zip(&b.nodes).enumerate() {
        if x.kind != y.kind
            || x.actor != y.actor
            || x.child_start != y.child_start
            || x.pot != y.pot
            || x.invested != y.invested
            || x.live != y.live
            || x.winner != y.winner
            || x.r != y.r
            || x.data_off != y.data_off
            || x.aggressor != y.aggressor
            || x.posf != y.posf
            || x.bucket != y.bucket
            || x.raises != y.raises
            || x.raised != y.raised
            || x.actions.len() != y.actions.len()
            || x.actions
                .iter()
                .zip(&y.actions)
                .any(|(x, y)| x.kind != y.kind || x.to != y.to || x.label != y.label)
        {
            return Err(format!("quality tree metadata differs at node {i}"));
        }
    }
    Ok(())
}

fn stopped(candidate: &PreflopSolver, reference: &PreflopSolver) -> Result<(), String> {
    if candidate.stop_requested() || reference.stop_requested() {
        Err("GPU quality evaluation canceled; no partial result published".into())
    } else {
        Ok(())
    }
}

fn evaluate(
    workspace: &PreflopSolver,
    candidate: &PreflopSolver,
    reference: &PreflopSolver,
    budget_mb: u64,
    label: &str,
) -> Result<(Vec<f64>, Vec<f64>, Value), String> {
    stopped(candidate, reference)?;
    let started = std::time::Instant::now();
    // A new engine rebuilds every fixed/profile policy and average input from
    // this exact workspace. Never synchronize device state into either input.
    let mut engine = gpu::PreflopGpu::new(workspace, budget_mb)?;
    let initialized = started.elapsed().as_secs_f64();
    let result = engine.gaps_and_evs()?;
    drop(engine); // Only one GPU engine exists at a time.
    stopped(candidate, reference)?;
    if result.0.iter().chain(&result.1).any(|x| !x.is_finite()) {
        return Err(format!("nonfinite quality checkpoint: {label}"));
    }
    let metadata = json!({"evaluation":label,"gpu_initialization_seconds":initialized,
        "total_seconds":started.elapsed().as_secs_f64(),"model":workspace.multiway_equity_model(),
        "source_iteration_label":workspace.iteration,"learning_performed":false});
    Ok((result.0, result.1, metadata))
}

impl PreflopSolver {
    /// Large-tree global policy comparison under full coupled payoffs. The two
    /// saved inputs are immutable; a new workspace holds copied averages only.
    /// No native save, source payoff relabel or learning iteration occurs.
    pub fn research_policy_quality_gpu_against(
        &self,
        reference: &Self,
        budget_mb: u64,
    ) -> Result<Value, String> {
        let started = std::time::Instant::now();
        if !(256..=64000).contains(&budget_mb) {
            return Err("GPU quality budget must be256..64000 MB".into());
        }
        for input in [self, reference] {
            if input.nodes.len() > MAX_NODES || input.arena_len.saturating_mul(8) > MAX_ARENA_BYTES
            {
                return Err(
                    "GPU policy quality is bounded to2M nodes and3GiB of arenas per input".into(),
                );
            }
            if input.iteration == 0 {
                return Err("quality inputs must contain completed learning iterations".into());
            }
        }
        let full = reference
            .multiway
            .as_ref()
            .ok_or("reference requires full coupled payoffs")?;
        if reference.multiway_equity_model() != multiway::MODEL || full.sample_count() != 1024 {
            return Err("reference must retain coupled_deck_v1 with1024 particles".into());
        }
        stopped(self, reference)?;
        if !same_json(&self.cfg, &reference.cfg)?
            || self.n != reference.n
            || !same_json(&self.seat_profiles, &reference.seat_profiles)?
            || self.seat_frozen != reference.seat_frozen
            || self.hero != reference.hero
            || self.pre_hero_frozen != reference.pre_hero_frozen
            || self.point_locks != reference.point_locks
            || !Arc::ptr_eq(&self.eq, &reference.eq)
            || format!("{:?}", self.fit) != format!("{:?}", reference.fit)
            || self.realization_note != reference.realization_note
        {
            return Err("GPU quality inputs require identical config, constraints, hero, equity cache and realization fit".into());
        }
        if reference.cfg.realization == "calibrated" && reference.fit.is_none() {
            return Err("calibrated reference fit is missing; no silent fallback".into());
        }
        validate_tree(self, reference)?;
        // Scan raw and effective strategies without full-arena snapshots. Finite
        // raw values alone do not rule out overflow while normalizing an action.
        for input in [self, reference] {
            unsafe {
                if input.regrets.slice().iter().any(|x| !x.is_finite())
                    || input
                        .strat_sum
                        .slice()
                        .iter()
                        .any(|x| !x.is_finite() || *x < 0.0)
                {
                    return Err("quality input contains invalid arena values".into());
                }
            }
        }
        for (node, nd) in self
            .nodes
            .iter()
            .enumerate()
            .filter(|(_, n)| n.kind == KIND_ACTION)
        {
            if node % 8192 == 0 {
                stopped(self, reference)?;
            }
            let candidate = self.average_strategy(node);
            let original = reference.average_strategy(node);
            for values in [&candidate, &original] {
                if values.iter().any(|x| !x.is_finite() || *x < -1e-7) {
                    return Err(format!("invalid effective strategy at node {node}"));
                }
                for h in 0..NUM_CLASSES {
                    let sum: f32 = (0..nd.actions.len())
                        .map(|a| values[a * NUM_CLASSES + h])
                        .sum();
                    if (sum - 1.0).abs() > 1e-5 {
                        return Err(format!(
                            "unnormalized effective strategy at node {node}, hand {h}"
                        ));
                    }
                }
            }
            if self.seat_frozen[nd.actor as usize] && candidate != original {
                return Err(format!("frozen average differs at node {node}"));
            }
        }
        let validation_seconds = started.elapsed().as_secs_f64();
        let live = reference.live_seats();
        let (reference_gaps, reference_evs, reference_timing) =
            evaluate(reference, self, reference, budget_mb, "reference")?;

        let mut workspace = Self::new(reference.cfg.clone(), reference.eq.clone())?;
        validate_tree(&workspace, reference)?;
        workspace.fit = reference.fit.clone();
        workspace.realization_note = reference.realization_note.clone();
        workspace.multiway = Some(full.clone());
        workspace.seat_profiles = reference.seat_profiles.clone();
        workspace.seat_frozen = reference.seat_frozen.clone();
        workspace.hero = reference.hero;
        workspace.pre_hero_frozen = reference.pre_hero_frozen.clone();
        workspace.point_locks = reference.point_locks.clone();
        workspace.prune = reference.prune;
        workspace.stop_flag = reference.stop_flag.clone();
        // Hero backup arenas are undo history, not payoff or policy inputs.
        // They remain only in the immutable sources: this workspace never calls
        // set_hero, set_table, save_game or any learning routine.
        unsafe {
            workspace
                .strat_sum
                .slice_mut()
                .copy_from_slice(self.strat_sum.slice());
        }
        workspace.iteration = self.iteration;
        let (candidate_gaps, candidate_evs, candidate_timing) = evaluate(
            &workspace,
            self,
            reference,
            budget_mb,
            "candidate_full_reference",
        )?;
        let mut timings = vec![reference_timing, candidate_timing];
        let mut unilateral = Vec::new();
        for p in 0..self.n {
            if !live[p] {
                continue;
            }
            unsafe {
                let sums = workspace.strat_sum.slice_mut();
                sums.copy_from_slice(reference.strat_sum.slice());
                // Traverse disjoint actor blocks directly; avoid a large list
                // of offset pairs for million-node trees.
                for nd in &self.nodes {
                    if nd.kind == KIND_ACTION && nd.actor as usize == p {
                        let span = nd.data_off..nd.data_off + nd.actions.len() * NUM_CLASSES;
                        sums[span.clone()].copy_from_slice(&self.strat_sum.slice()[span]);
                    }
                }
            }
            let (_, mixed_evs, timing) = evaluate(
                &workspace,
                self,
                reference,
                budget_mb,
                &format!("unilateral_seat_{p}"),
            )?;
            timings.push(timing);
            unilateral.push(json!({"seat":p,"position":self.cfg.positions[p],
                "reference_ev_bb":reference_evs[p],"candidate_vs_reference_opponents_ev_bb":mixed_evs[p],
                "signed_loss_bb":reference_evs[p] - mixed_evs[p]}));
        }
        stopped(self, reference)?;
        let losses: Vec<_> = unilateral
            .iter()
            .map(|r| r["signed_loss_bb"].as_f64().unwrap().max(0.0))
            .collect();
        let mean_loss = if losses.is_empty() {
            0.0
        } else {
            losses.iter().sum::<f64>() / losses.len() as f64
        };
        let worst_loss = losses.iter().copied().fold(0.0, f64::max);
        let learning_gap = |gaps: &[f64]| {
            gaps.iter()
                .zip(&live)
                .filter(|(_, active)| **active)
                .map(|(g, _)| *g)
                .sum::<f64>()
        };
        let ref_gap = learning_gap(&reference_gaps);
        let candidate_gap = learning_gap(&candidate_gaps);
        let converged = ref_gap <= 0.005;
        Ok(
            json!({"schema":1,"evaluator":"sequential_fresh_gpu_full_reference",
            "scope":"Global frozen-policy quality under the full latent coupled model, not physical poker or local-action validation",
            "candidate_model":self.multiway_equity_model(),"reference_model":reference.multiway_equity_model(),
            "candidate_iteration":self.iteration,"reference_iteration":reference.iteration,
            "nodes":self.nodes.len(),"arena_bytes_per_input":self.arena_len * 8,"budget_mb":budget_mb,
            "live_seats":live,"validation_seconds":validation_seconds,"elapsed_seconds":started.elapsed().as_secs_f64(),"evaluations":timings,
            "reference_gaps_bb":reference_gaps,"reference_evs_bb":reference_evs,"reference_learning_gap_bb":ref_gap,
            "candidate_full_reference_gaps_bb":candidate_gaps,"candidate_full_reference_evs_bb":candidate_evs,
            "candidate_learning_gap_bb":candidate_gap,"excess_learning_gap_bb":candidate_gap-ref_gap,
            "unilateral_replacements":unilateral,"unilateral_mean_positive_loss_bb":mean_loss,"unilateral_max_positive_loss_bb":worst_loss,
            "reference_converged":converged,"thresholds":{"reference_gap_bb":0.005,"excess_gap_bb":0.02,"mean_loss_bb":0.01,"max_loss_bb":0.03},
            "passes_relative_policy_gates":candidate_gap-ref_gap<=0.02 && mean_loss<=0.01 && worst_loss<=0.03,
            "passes_global_policy_gates_with_converged_reference":converged && candidate_gap-ref_gap<=0.02 && mean_loss<=0.01 && worst_loss<=0.03,
            "not_evaluated":["physical equity","local strong-action tails","speedup","preview workflow"],
            "input_mutation":false,"learning_performed":false,"native_save_performed":false}),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn gpu_policy_quality_same_policy_is_zero_and_inputs_remain_unchanged() {
        let cfg = serde_json::from_value(
            json!({"positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":2,
            "limp":false,"open_raises":[2],"raise_mults":[3],"max_raises":1,"add_allin":false,
            "rake_pct":0,"rake_cap":0,"realization":"raw"}),
        )
        .unwrap();
        let mut reference =
            PreflopSolver::new(cfg, Arc::new(equity::EquityTable::build(8))).unwrap();
        reference.iterate();
        let before = reference.arena_snapshot();
        let result = reference
            .research_policy_quality_gpu_against(&reference, 2000)
            .unwrap();
        assert_eq!(result["excess_learning_gap_bb"].as_f64(), Some(0.0));
        assert_eq!(
            result["unilateral_max_positive_loss_bb"].as_f64(),
            Some(0.0)
        );
        assert_eq!(
            result["unilateral_replacements"].as_array().unwrap().len(),
            3
        );
        let cpu = reference
            .research_policy_quality_against(&reference)
            .unwrap();
        for field in ["reference_evs_bb", "reference_gaps_bb"] {
            for (a, b) in result[field]
                .as_array()
                .unwrap()
                .iter()
                .zip(cpu[field].as_array().unwrap())
            {
                assert!((a.as_f64().unwrap() - b.as_f64().unwrap()).abs() < 3e-5);
            }
        }
        assert_eq!(before, reference.arena_snapshot());
        reference.stop_flag = Some(Arc::new(AtomicBool::new(true)));
        assert!(reference
            .research_policy_quality_gpu_against(&reference, 2000)
            .is_err());
    }
}
