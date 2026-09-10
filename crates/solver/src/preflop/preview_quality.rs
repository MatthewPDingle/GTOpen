//! Bounded research-only policy evaluation. Never relabel or resume a candidate's arenas.
//! A fresh workspace receives strategy sums, reference payoffs and identical constraints.
use super::*;
use serde_json::{json, Value};

const MAX_NODES: usize = 20_000;
const MAX_ARENA_BYTES: usize = 128 * 1024 * 1024;

fn same_json<T: Serialize>(a: &T, b: &T) -> Result<bool, String> {
    Ok(serde_json::to_value(a).map_err(|e| e.to_string())?
        == serde_json::to_value(b).map_err(|e| e.to_string())?)
}

fn completed(s: &PreflopSolver) -> Result<(Vec<f64>, Vec<f64>), String> {
    let result = s.checkpoint_gaps_and_evs().ok_or_else(|| "quality evaluation canceled".to_string())?;
    if result.0.iter().chain(&result.1).any(|x| !x.is_finite()) {
        return Err("quality evaluation produced nonfinite values".into());
    }
    Ok(result)
}

fn learning_gap(gaps: &[f64], live: &[bool]) -> f64 {
    gaps.iter().zip(live).filter(|(_, live)| **live).map(|(g, _)| *g).sum()
}

impl PreflopSolver {
    /// Deterministic artificial initial averages for the registered frozen-seat
    /// control. Fresh, bounded research games only; never used for user models.
    pub fn research_seed_quality_fixture_averages(&mut self) -> Result<(), String> {
        if self.iteration != 0 || self.nodes.len() > MAX_NODES || self.arena_len.saturating_mul(8) > MAX_ARENA_BYTES {
            return Err("quality fixture seeding requires a fresh bounded game".into());
        }
        let sums = unsafe { self.strat_sum.slice_mut() };
        if sums.iter().any(|&x|x != 0.0) { return Err("quality fixture already contains strategy mass".into()); }
        for (i, nd) in self.nodes.iter().enumerate().filter(|(_,nd)|nd.kind==KIND_ACTION) {
            for a in 0..nd.actions.len() {for h in 0..NUM_CLASSES {
                sums[nd.data_off+a*NUM_CLASSES+h]=1.0+((i*3+a*7+h*11)%19) as f32;
            }}
        }
        Ok(())
    }

    /// Compare a candidate's frozen average strategy to a full coupled reference.
    /// Inputs remain intact. Only small, identical games are accepted; no save,
    /// learning iteration, or payoff-identity mutation occurs on either input.
    pub fn research_policy_quality_against(&self, reference: &Self) -> Result<Value, String> {
        if self.nodes.len() > MAX_NODES || reference.nodes.len() > MAX_NODES
            || self.arena_len.saturating_mul(8) > MAX_ARENA_BYTES
            || reference.arena_len.saturating_mul(8) > MAX_ARENA_BYTES {
            return Err("quality evaluation is bounded to 20,000 nodes and 128 MiB arenas".into());
        }
        let Some(full) = reference.multiway.as_ref() else {
            return Err("reference must use the full coupled model".into());
        };
        if reference.multiway_equity_model() != "coupled_deck_v1"
            || full.order.len() != 1024 * NUM_CLASSES {
            return Err("reference must retain all 1,024 coupled particles".into());
        }
        if self.stop_requested() || reference.stop_requested() {
            return Err("quality input has a pending stop request".into());
        }
        if !same_json(&self.cfg, &reference.cfg)? || self.n != reference.n
            || self.nodes.len() != reference.nodes.len() || self.arena_len != reference.arena_len
            || !same_json(&self.seat_profiles, &reference.seat_profiles)?
            || self.seat_frozen != reference.seat_frozen || self.hero != reference.hero
            || self.point_locks != reference.point_locks {
            return Err("quality inputs must have identical config, tree, profiles, frozen flags, hero and point locks".into());
        }
        // One cache Arc in the example guarantees identical HU table contents.
        if !Arc::ptr_eq(&self.eq, &reference.eq)
            || format!("{:?}", self.fit) != format!("{:?}", reference.fit) {
            return Err("quality inputs must share the same equity table and realization fit".into());
        }
        // Frozen play is an input constraint. Reject differing pinned averages
        // rather than attributing their change to a learning-policy improvement.
        for (node, nd) in self.nodes.iter().enumerate() {
            if nd.kind == KIND_ACTION {
                let candidate_average = self.average_strategy(node);
                let reference_average = reference.average_strategy(node);
                for strategy in [&candidate_average, &reference_average] {
                    if strategy.iter().any(|x| !x.is_finite() || *x < -1e-7) {
                        return Err(format!("invalid average strategy at node {node}"));
                    }
                    for h in 0..NUM_CLASSES {
                        let sum: f32 = (0..nd.actions.len()).map(|a|strategy[a * NUM_CLASSES + h]).sum();
                        if (sum - 1.0).abs() > 1e-5 {
                            return Err(format!("unnormalized average strategy at node {node}, hand {h}"));
                        }
                    }
                }
                if self.seat_frozen[nd.actor as usize] && candidate_average != reference_average {
                    return Err(format!("frozen average differs at node {node}"));
                }
            }
        }

        let started = std::time::Instant::now();
        let mut workspace = Self::new(reference.cfg.clone(), reference.eq.clone())?;
        if workspace.nodes.len() != reference.nodes.len() || workspace.arena_len != reference.arena_len {
            return Err("reference tree rebuild changed shape".into());
        }
        workspace.fit = reference.fit.clone();
        workspace.realization_note = reference.realization_note.clone();
        workspace.multiway = Some(full.clone());
        workspace.seat_profiles = reference.seat_profiles.clone();
        workspace.seat_frozen = reference.seat_frozen.clone();
        workspace.hero = reference.hero;
        workspace.pre_hero_frozen = reference.pre_hero_frozen.clone();
        workspace.hero_backup = reference.hero_backup.clone();
        workspace.point_locks = reference.point_locks.clone();
        workspace.prune = reference.prune;
        // Propagate an external cancellation request to this workspace too.
        // No flag is reset, and canceled results never become numeric output.
        workspace.stop_flag = reference.stop_flag.clone();
        let live = reference.live_seats();
        let (reference_gaps, reference_evs) = completed(reference)?;

        // SAFETY: workspace is exclusively owned here; no traversal is active.
        // Copy only average-strategy sums. Its fresh zero regrets are never used
        // for learning and the workspace never escapes this method.
        unsafe { workspace.strat_sum.slice_mut().copy_from_slice(self.strat_sum.slice()); }
        workspace.iteration = self.iteration;
        let (candidate_gaps, candidate_evs) = completed(&workspace)?;
        let mut unilateral = Vec::new();
        for p in 0..self.n {
            if !live[p] { continue; }
            unsafe {
                let sums = workspace.strat_sum.slice_mut();
                sums.copy_from_slice(reference.strat_sum.slice());
                for (off, len) in self.seat_blocks(p) {
                    sums[off..off + len].copy_from_slice(&self.strat_sum.slice()[off..off + len]);
                }
            }
            let (_, mixed_evs) = completed(&workspace)?;
            unilateral.push(json!({"seat":p,"position":self.cfg.positions[p],
                "reference_ev_bb":reference_evs[p],"candidate_vs_reference_opponents_ev_bb":mixed_evs[p],
                "signed_loss_bb":reference_evs[p]-mixed_evs[p]}));
        }
        if self.stop_requested() || reference.stop_requested() {
            return Err("quality evaluation canceled before publication".into());
        }
        let losses: Vec<f64> = unilateral.iter().map(|r| r["signed_loss_bb"].as_f64().unwrap().max(0.0)).collect();
        let mean_loss = if losses.is_empty() { 0.0 } else { losses.iter().sum::<f64>() / losses.len() as f64 };
        let worst_loss = losses.iter().copied().fold(0.0, f64::max);
        let ref_gap = learning_gap(&reference_gaps, &live);
        let candidate_gap = learning_gap(&candidate_gaps, &live);
        let ref_converged = ref_gap <= 0.005;
        Ok(json!({"schema":1,"scope":"Frozen policy evaluated under unchanged full coupled payoffs; no physical-deal or full postflop accuracy claim",
            "candidate_model":self.multiway_equity_model(),"reference_model":reference.multiway_equity_model(),
            "candidate_iteration":self.iteration,"reference_iteration":reference.iteration,
            "nodes":self.nodes.len(),"live_seats":live,"elapsed_seconds":started.elapsed().as_secs_f64(),
            "reference_gaps_bb":reference_gaps,"reference_evs_bb":reference_evs,"reference_learning_gap_bb":ref_gap,
            "candidate_full_reference_gaps_bb":candidate_gaps,"candidate_full_reference_evs_bb":candidate_evs,
            "candidate_learning_gap_bb":candidate_gap,"excess_learning_gap_bb":candidate_gap-ref_gap,
            "unilateral_replacements":unilateral,"unilateral_mean_positive_loss_bb":mean_loss,
            "unilateral_max_positive_loss_bb":worst_loss,"reference_converged":ref_converged,
            "thresholds":{"reference_gap_bb":0.005,"excess_gap_bb":0.02,"mean_loss_bb":0.01,"max_loss_bb":0.03},
            "passes_relative_policy_gates":candidate_gap-ref_gap <= 0.02 && mean_loss <= 0.01 && worst_loss <= 0.03,
            "passes_global_policy_gates_with_converged_reference":ref_converged && candidate_gap-ref_gap <= 0.02 && mean_loss <= 0.01 && worst_loss <= 0.03,
            "not_evaluated":["physical equity","local strong-action tails","speedup","preview workflow"]}))
    }

    /// Local action loss under reference arriving ranges and reference future
    /// play. This one-step deviation diagnostic is not a full-subgame BR.
    pub fn research_local_action_quality_against(&self, reference: &Self, path: &[usize]) -> Result<Value, String> {
        if self.nodes.len() > MAX_NODES || reference.nodes.len() > MAX_NODES || path.len() > 64 {
            return Err("local quality requires <=20,000 nodes and path length <=64".into());
        }
        if !same_json(&self.cfg, &reference.cfg)? || !same_json(&self.seat_profiles, &reference.seat_profiles)?
            || self.seat_frozen != reference.seat_frozen || self.hero != reference.hero
            || self.point_locks != reference.point_locks || !Arc::ptr_eq(&self.eq, &reference.eq)
            || format!("{:?}", self.fit) != format!("{:?}", reference.fit)
            || reference.multiway_equity_model() != "coupled_deck_v1"
            || reference.multiway.as_ref().map(|m|m.order.len()) != Some(1024 * NUM_CLASSES) {
            return Err("local quality requires compatible inputs and full coupled reference".into());
        }
        if self.stop_requested() || reference.stop_requested() { return Err("local quality canceled".into()); }
        let (node, reaches) = reference.walk(path)?;
        let (candidate_node, _) = self.walk(path)?;
        let nd = &reference.nodes[node];
        if nd.kind != KIND_ACTION || node != candidate_node { return Err("local quality path must name an identical action node".into()); }
        let p = nd.actor as usize;
        let actor_mass: f64 = reaches[p].iter().map(|&x|x as f64).sum();
        // Match terminal_value's f32 mass sums before f64 product.
        let opponent_mass: f64 = reaches.iter().enumerate().filter(|(q,_)|*q != p)
            .map(|(_,r)|r.iter().sum::<f32>() as f64).product();
        if actor_mass <= 1e-12 || opponent_mass <= 1e-12 {
            return Ok(json!({"path":path,"status":"unreachable_under_reference","actor_mass":actor_mass,"opponent_mass":opponent_mass}));
        }
        let reference_sigma = reference.average_strategy(node);
        let candidate_sigma = self.average_strategy(node);
        if reference_sigma.len() != candidate_sigma.len() || candidate_sigma.iter().any(|x|!x.is_finite() || *x < -1e-7) {
            return Err("invalid local candidate strategy".into());
        }
        let mut action_values = Vec::new();
        for a in 0..nd.actions.len() {
            let mut child_reaches = reaches.clone();
            for h in 0..NUM_CLASSES { child_reaches[p][h] *= reference_sigma[a * NUM_CLASSES + h]; }
            let values = reference.traverse_checkpoint(reference.children[nd.child_start as usize + a] as usize,
                p, &mut child_reaches, 2, CheckpointNeeds{br:false,avg:true}, 0)
                .ok_or_else(||"local quality canceled".to_string())?.avg.unwrap();
            if values.iter().any(|x|!x.is_finite()) { return Err("nonfinite local action value".into()); }
            action_values.push(values);
        }
        let constrained = reference.seat_frozen[p] || reference.forced_sigma(node).is_some();
        let mut rows = Vec::new();
        let mut weighted_loss = 0.0;
        let mut reference_weighted_loss = 0.0;
        let mut worst_relevant_bad_mass = 0.0f64;
        for h in 0..NUM_CLASSES {
            let mass = reaches[p][h] as f64 / actor_mass;
            let q: Vec<f64> = action_values.iter().map(|v|v[h] as f64 / opponent_mass).collect();
            let best = q.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let probabilities: Vec<f64> = (0..nd.actions.len()).map(|a|candidate_sigma[a * NUM_CLASSES + h] as f64).collect();
            if (probabilities.iter().sum::<f64>() - 1.0).abs() > 1e-5 { return Err("unnormalized local candidate".into()); }
            let loss: f64 = q.iter().zip(&probabilities).map(|(v,prob)|prob * (best-v)).sum();
            let reference_loss: f64 = q.iter().enumerate().map(|(a,v)|reference_sigma[a * NUM_CLASSES + h] as f64 * (best-v)).sum();
            let bad_mass: f64 = q.iter().zip(&probabilities).filter(|(v,_)|best-**v > 0.1).map(|(_,p)|*p).sum();
            weighted_loss += mass * loss;
            reference_weighted_loss += mass * reference_loss;
            if mass >= 0.0025 { worst_relevant_bad_mass = worst_relevant_bad_mass.max(bad_mass); }
            rows.push(json!({"class_index":h,"conditional_hand_mass":mass,"action_values_bb":q,
                "candidate_probabilities":probabilities,"expected_action_loss_bb":loss,
                "reference_expected_action_loss_bb":reference_loss,"probability_on_actions_losing_over_0_1bb":bad_mass}));
        }
        if self.stop_requested() || reference.stop_requested() { return Err("local quality canceled before publication".into()); }
        Ok(json!({"path":path,"status":"evaluated","actor":p,"position":reference.cfg.positions[p],
            "scope":"One-action deviation followed by reference play, same reference arriving ranges; excludes physical-deal validation",
            "actor_mass":actor_mass,"opponent_mass":opponent_mass,"joint_reach_independent_model":actor_mass*opponent_mass,
            "actions":nd.actions.iter().map(|a|json!({"label":a.label,"kind":a.kind,"to":a.to})).collect::<Vec<_>>(),
            "weighted_action_loss_bb":weighted_loss,"reference_weighted_action_loss_bb":reference_weighted_loss,
            "weighted_excess_action_loss_bb":weighted_loss-reference_weighted_loss,"forced_or_frozen":constrained,
            "worst_relevant_probability_on_strongly_inferior_actions":worst_relevant_bad_mass,
            "passes_local_tail_gate":if constrained {None} else {Some(worst_relevant_bad_mass<=0.1)},
            "hands":rows}))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn same_policy_quality_is_zero_loss_and_does_not_mutate_inputs() {
        let cfg: PreflopConfig = serde_json::from_value(json!({
            "positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":2,
            "limp":false,"open_raises":[2],"raise_mults":[3],"max_raises":1,
            "add_allin":false,"rake_pct":0,"rake_cap":0,"realization":"raw"
        })).unwrap();
        let mut reference = PreflopSolver::new(cfg, Arc::new(equity::EquityTable::build(8))).unwrap();
        reference.iterate();
        let before = reference.arena_snapshot();
        let result = reference.research_policy_quality_against(&reference).unwrap();
        assert_eq!(result["excess_learning_gap_bb"].as_f64(), Some(0.0));
        assert_eq!(result["unilateral_max_positive_loss_bb"].as_f64(), Some(0.0));
        let local = reference.research_local_action_quality_against(&reference, &[]).unwrap();
        assert_eq!(local["weighted_excess_action_loss_bb"].as_f64(), Some(0.0));
        assert_eq!(local["hands"].as_array().unwrap().len(), NUM_CLASSES);
        assert!(reference.research_local_action_quality_against(&reference, &[usize::MAX]).is_err());
        // A reached BB fold loses its posted1bb, independent of the probability
        // of reaching that history. This catches omission/double-counting of
        // the current opponent mass in conditional Q values.
        let mut pending=vec![(0usize,Vec::<usize>::new())];let mut checked=false;
        while let Some((node,path))=pending.pop() {
            let nd=&reference.nodes[node];if nd.kind!=KIND_ACTION {continue;}
            if nd.actor as usize==2 {
                if let Some(fold)=nd.actions.iter().position(|a|a.kind=="fold") {
                    let local=reference.research_local_action_quality_against(&reference,&path).unwrap();
                    if local["status"]=="evaluated" {
                        for row in local["hands"].as_array().unwrap() {
                            assert!((row["action_values_bb"][fold].as_f64().unwrap()+nd.invested[2]).abs()<1e-6);
                        }
                        checked=true;break;
                    }
                }
            }
            for a in 0..nd.actions.len(){let mut next=path.clone();next.push(a);pending.push((reference.children[nd.child_start as usize+a] as usize,next));}
        }
        assert!(checked,"fixture must contain a reached BB fold");
        assert_eq!(before, reference.arena_snapshot());
        reference.stop_flag = Some(Arc::new(AtomicBool::new(true)));
        assert!(reference.research_policy_quality_against(&reference).is_err());
    }
}
