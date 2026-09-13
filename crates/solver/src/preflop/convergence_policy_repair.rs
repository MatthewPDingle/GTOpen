//! Offline average-policy edits; never resumes learning from repaired histories.
use super::*;
use serde_json::{json, Value};
use std::collections::BTreeSet;

fn valid_policy(policy: &[f32]) -> bool {
    if policy.is_empty() || policy.len() % NUM_CLASSES != 0
        || policy.iter().any(|x| !x.is_finite() || *x < 0.0 || *x > 1.0) { return false; }
    (0..NUM_CLASSES).all(|h| {
        let sum: f64 = policy.chunks_exact(NUM_CLASSES).map(|a| a[h] as f64).sum();
        (sum - 1.0).abs() <= 1e-6
    })
}

/// Keep current relative mass among equally best actions; otherwise uniform.
/// Q and probabilities are action-major. This does not read acceptance gates.
pub fn best_response_target(policy: &[f32], q: &[f64]) -> Result<Vec<f32>, String> {
    if !valid_policy(policy) || q.len() != policy.len() || q.iter().any(|v| !v.is_finite()) {
        return Err("finite action-major values and normalized policy required".into());
    }
    let na = policy.len() / NUM_CLASSES;
    let mut target = vec![0.0; policy.len()];
    for h in 0..NUM_CLASSES {
        let best = (0..na).map(|a| q[a*NUM_CLASSES+h]).fold(f64::NEG_INFINITY, f64::max);
        let eligible: Vec<_> = (0..na).filter(|&a| best-q[a*NUM_CLASSES+h] <= 1e-8).collect();
        let mass: f64 = eligible.iter().map(|&a| policy[a*NUM_CLASSES+h] as f64).sum();
        for &a in &eligible {
            target[a*NUM_CLASSES+h] = if mass > 0.0 {
                (policy[a*NUM_CLASSES+h] as f64 / mass) as f32
            } else { 1.0 / eligible.len() as f32 };
        }
    }
    if !valid_policy(&target) { return Err("target normalization failed".into()); }
    Ok(target)
}

pub fn mix_policy(policy: &[f32], target: &[f32], alpha: f64) -> Result<Vec<f32>, String> {
    if !alpha.is_finite() || !(0.0..=1.0).contains(&alpha)
        || !valid_policy(policy) || !valid_policy(target) || policy.len() != target.len() {
        return Err("valid normalized mixture endpoints and alpha required".into());
    }
    let mut result: Vec<_> = policy.iter().zip(target).map(|(&a,&b)|
        ((1.0-alpha)*a as f64+alpha*b as f64) as f32).collect();
    for h in 0..NUM_CLASSES {
        let sum: f64 = result.chunks_exact(NUM_CLASSES).map(|a| a[h] as f64).sum();
        for action in result.chunks_exact_mut(NUM_CLASSES) { action[h] = (action[h] as f64/sum) as f32; }
    }
    Ok(result)
}

impl PreflopSolver {
    fn repair_nodes(&self, paths: &[Vec<usize>]) -> Result<Vec<usize>, String> {
        if self.nodes.len() > 2_000_000 || paths.is_empty() || paths.len() > 64 || self.stop_requested() {
            return Err("bounded unstopped non-root batch required".into());
        }
        let mut seen = BTreeSet::new();
        let mut nodes = Vec::new();
        for path in paths {
            if path.is_empty() || path.len() > 64 || !seen.insert(path.clone()) {
                return Err("distinct proper action paths required".into());
            }
            let (node, _) = self.walk(path)?;
            let nd = &self.nodes[node];
            if nd.kind != KIND_ACTION || self.seat_frozen[nd.actor as usize] || self.forced_sigma(node).is_some() {
                return Err("unconstrained action nodes required".into());
            }
            nodes.push(node);
        }
        Ok(nodes)
    }

    /// Atomic validation before writing only the selected average entries.
    /// Regrets, unrelated averages, constraints and global iteration never change.
    pub fn research_set_nonroot_averages(&mut self, paths: &[Vec<usize>], policies: &[Vec<f32>]) -> Result<(), String> {
        let nodes = self.repair_nodes(paths)?;
        if nodes.len() != policies.len() { return Err("one policy per path required".into()); }
        for (&node, policy) in nodes.iter().zip(policies) {
            if policy.len() != self.nodes[node].actions.len()*NUM_CLASSES || !valid_policy(policy) {
                return Err("normalized policy of matching action shape required".into());
            }
        }
        if self.stop_requested() { return Err("canceled before policy mutation".into()); }
        for (&node, policy) in nodes.iter().zip(policies) {
            let start = self.nodes[node].data_off;
            unsafe { self.strat_sum.slice_mut()[start..start+policy.len()].copy_from_slice(policy); }
        }
        Ok(())
    }

    /// Topology/reach selection only, without inspecting action values or gates.
    pub fn research_nonroot_policy_plan(&self, paths: &[Vec<usize>], heldout_count: usize) -> Result<Value, String> {
        let nodes = self.repair_nodes(paths)?;
        if heldout_count > 32 { return Err("held-out path limit exceeded".into()); }
        let mut selected = Vec::new();
        for (path, &node) in paths.iter().zip(&nodes) {
            let plan = self.research_refinement_plan(path)?;
            if plan["prefix_mass_by_seat"].as_array().unwrap().iter().any(|m| m.as_f64().map_or(true, |v| !v.is_finite() || v <= 0.0)) {
                return Err("positive original prefix mass required".into());
            }
            let nd = &self.nodes[node];
            selected.push(json!({"path":path,"node":node,"start":nd.data_off,
                "end":nd.data_off+nd.actions.len()*NUM_CLASSES,"policy":self.average_strategy(node),
                "subtree_nodes":plan["subtree_nodes"]}));
        }
        let excluded: BTreeSet<_> = paths.iter().cloned().collect();
        let mut candidates = BTreeSet::new();
        for path in paths {
            let mut prefix = Vec::new(); let mut node = 0;
            for &taken in path {
                for a in 0..self.nodes[node].actions.len() {
                    if a != taken {
                        let mut sibling = prefix.clone(); sibling.push(a);
                        if !excluded.contains(&sibling) { candidates.insert(sibling); }
                    }
                }
                prefix.push(taken); node = self.child(node, taken);
            }
        }
        let mut candidates: Vec<_> = candidates.into_iter().collect();
        candidates.sort_by(|a,b| a.len().cmp(&b.len()).then_with(|| a.cmp(b)));
        let mut heldout = Vec::new();
        for path in candidates {
            if heldout.len() == heldout_count { break; }
            if self.repair_nodes(&[path.clone()]).is_err() { continue; }
            if let Ok(plan) = self.research_refinement_plan(&path) {
                if plan["prefix_mass_by_seat"].as_array().unwrap().iter().all(|m|
                    m.as_f64().map_or(false, |v| v.is_finite() && v > 0.0)) { heldout.push(path); }
            }
        }
        if heldout.len() != heldout_count { return Err("insufficient independent diagnostic paths".into()); }
        Ok(json!({"selected":selected,"heldout_paths":heldout,
            "selection":"Sibling topology sorted by depth and lexicographic path; positive prefix mass; no action-value selection",
            "normal_global_resume_supported":false}))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> PreflopSolver {
        let cfg: PreflopConfig = serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],
            "stack":5.0,"posts":[0.0,0.0,0.5,1.0],"limp":true,"open_raises":[2.0],
            "raise_mults":[3.0],"max_raises":1,"add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"})).unwrap();
        let mut s = PreflopSolver::new(cfg, Arc::new(EquityTable::build(8))).unwrap();
        s.research_seed_quality_fixture_averages().unwrap(); s.iteration = 17; s
    }
    #[test]
    fn policy_repair_target_and_mixture_are_value_directed() {
        let mut policy = vec![0.0;3*NUM_CLASSES];
        policy[..NUM_CLASSES].fill(0.2); policy[NUM_CLASSES..2*NUM_CLASSES].fill(0.3);
        policy[2*NUM_CLASSES..].fill(0.5);
        let mut q = vec![0.0;policy.len()]; q[NUM_CLASSES..].fill(2.0);
        let target = best_response_target(&policy,&q).unwrap();
        assert_eq!(target[0],0.0); assert!((target[NUM_CLASSES]-0.375).abs()<1e-6);
        assert!((target[2*NUM_CLASSES]-0.625).abs()<1e-6);
        for alpha in [0.0,0.125,0.25,0.5,0.875,1.0] {
            let mix = mix_policy(&policy,&target,alpha).unwrap(); assert!(valid_policy(&mix));
            for h in 0..NUM_CLASSES {
                let ev: f64 = (0..3).map(|a| mix[a*NUM_CLASSES+h] as f64*q[a*NUM_CLASSES+h]).sum();
                assert!((ev-(1.6+0.4*alpha)).abs()<1e-6);
            }
        }
        policy.fill(0.0); policy[..NUM_CLASSES].fill(1.0);
        let target = best_response_target(&policy,&q).unwrap();
        assert_eq!(target[NUM_CLASSES],0.5); assert_eq!(target[2*NUM_CLASSES],0.5);
        q[0]=f64::NAN; assert!(best_response_target(&policy,&q).is_err());
        assert!(mix_policy(&policy,&target,f64::NAN).is_err());
        assert!(mix_policy(&policy,&target,-0.1).is_err());
    }
    #[test]
    fn policy_repair_batch_is_atomic_and_preserves_unselected_state() {
        let mut s = fixture(); let paths = vec![vec![0,0],vec![1,0]];
        let plan = s.research_nonroot_policy_plan(&paths,2).unwrap();
        assert_eq!(plan,s.research_nonroot_policy_plan(&paths,2).unwrap());
        let before = s.arena_snapshot(); let age = s.iteration;
        let original: Vec<Vec<f32>> = plan["selected"].as_array().unwrap().iter().map(|r|
            serde_json::from_value(r["policy"].clone()).unwrap()).collect();
        let mut policies = original.clone();
        for p in &mut policies { p.fill(0.0); p[..NUM_CLASSES].fill(1.0); }
        for invalid in [vec![],vec![f32::NAN;policies[1].len()],vec![0.0;policies[1].len()],vec![2.0;policies[1].len()]] {
            assert!(s.research_set_nonroot_averages(&paths,&[policies[0].clone(),invalid]).is_err());
            assert_eq!(before,s.arena_snapshot());
        }
        for bad_paths in [vec![vec![],vec![1]],vec![vec![0],vec![0]],vec![vec![0],vec![999]],vec![vec![0,0],vec![0,0,0]]] {
            assert!(s.research_set_nonroot_averages(&bad_paths,&policies).is_err());
            assert_eq!(before,s.arena_snapshot());
        }
        s.set_stop_flag(Some(Arc::new(AtomicBool::new(true))));
        assert!(s.research_set_nonroot_averages(&paths,&policies).is_err());
        s.set_stop_flag(None); assert_eq!(before,s.arena_snapshot());
        let locked_node = s.walk(&paths[1]).unwrap().0;
        s.point_locks.insert(locked_node as u32,policies[1].clone());
        assert!(s.research_set_nonroot_averages(&paths,&policies).is_err()); s.point_locks.clear();
        let actor = s.nodes[locked_node].actor as usize; s.seat_frozen[actor]=true;
        assert!(s.research_set_nonroot_averages(&paths,&policies).is_err()); s.seat_frozen[actor]=false;
        assert_eq!(before,s.arena_snapshot());
        s.research_set_nonroot_averages(&paths,&policies).unwrap();
        let after=s.arena_snapshot(); assert_eq!(before.0,after.0); assert_eq!(age,s.iteration);
        let spans: Vec<_> = plan["selected"].as_array().unwrap().iter().map(|r|
            r["start"].as_u64().unwrap() as usize..r["end"].as_u64().unwrap() as usize).collect();
        for (i,(a,b)) in before.1.iter().zip(&after.1).enumerate() {
            if !spans.iter().any(|r|r.contains(&i)) { assert_eq!(a.to_bits(),b.to_bits()); }
        }
        // Normalize, modify, then restore the exact normalized cycle baseline.
        s.research_set_nonroot_averages(&paths,&original).unwrap(); let baseline=s.arena_snapshot();
        s.research_set_nonroot_averages(&paths,&policies).unwrap();
        s.research_set_nonroot_averages(&paths,&original).unwrap(); assert_eq!(baseline,s.arena_snapshot());
        let cpu=s.gaps_and_evs(); let mut gpu=gpu::PreflopGpu::new(&s,512).unwrap();
        let actual=gpu.gaps_and_evs().unwrap(); drop(gpu);
        for (a,b) in cpu.0.iter().chain(&cpu.1).zip(actual.0.iter().chain(&actual.1)) {
            assert!((a-b).abs()<0.005,"policy repair CPU/GPU mismatch");
        }
        let file=std::env::temp_dir().join(format!("gtopen-policy-repair-test-{}.gtop",std::process::id()));
        s.save_game(file.to_str().unwrap()).unwrap();
        let restored=PreflopSolver::load_game(file.to_str().unwrap(),s.eq.clone()).unwrap();
        assert_eq!(baseline,restored.arena_snapshot()); assert_eq!(age,restored.iteration);
        std::fs::remove_file(file).unwrap();
    }
}
