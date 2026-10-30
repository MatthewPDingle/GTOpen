//! Bounded research-only policy evaluation. Never relabel or resume a candidate's arenas.
//! A fresh workspace receives strategy sums, reference payoffs and identical constraints.
use super::*;
use serde_json::{json, Value};

const MAX_NODES: usize = 50_000;
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
    /// Conservative structural screen for exact temporal reuse of multiway
    /// conditional equities. This does not install a cache or skip any work.
    pub fn research_static_terminal_reuse(&self) -> Result<Value, String> {
        if self.nodes.len()>2_000_000 || self.stop_requested() {
            return Err("static reuse screen requires a bounded, unstopped game".into());
        }
        let mut pairs=vec![0usize;self.n];
        let mut reusable=vec![0usize;self.n];
        let mut dynamic_folded_mass=0usize;
        let mut pending=vec![(0usize,0u32)];
        let mut visited=0usize;
        while let Some((node,mutable_prefix))=pending.pop() {
            visited+=1;
            if visited>self.nodes.len() || (visited%4096==0 && self.stop_requested()) {
                return Err("static reuse traversal canceled or invalid".into());
            }
            let nd=&self.nodes[node];
            if nd.kind==KIND_ACTION {
                let actor=nd.actor as usize;
                let mutable=if self.seat_frozen[actor] || self.forced_sigma(node).is_some() {
                    mutable_prefix
                } else { mutable_prefix | (1<<actor) };
                for a in 0..nd.actions.len() {pending.push((self.child(node,a),mutable));}
            } else if nd.kind==KIND_POT_SHARE && nd.live.count_ones()>=3 {
                for p in 0..self.n {
                    if nd.live & (1<<p)==0 {continue;}
                    pairs[p]+=1;
                    let live_opponents=nd.live & !(1<<p);
                    if mutable_prefix & live_opponents==0 {
                        reusable[p]+=1;
                        if mutable_prefix & !nd.live & !(1<<p)!=0 {dynamic_folded_mass+=1;}
                    }
                }
            }
        }
        let total: usize=pairs.iter().sum();
        let reusable_total: usize=reusable.iter().sum();
        Ok(json!({"scope":"Structural upper opportunity for fixed live-opponent conditional equities; no cached solver or speed claim",
            "multiway_terminal_traverser_pairs":total,"reusable_conditional_pairs":reusable_total,
            "pairs_by_traverser":pairs,"reusable_by_traverser":reusable,
            "reusable_with_dynamic_folded_mass":dynamic_folded_mass,
            "dense_conditional_vector_bytes":reusable_total*NUM_CLASSES*std::mem::size_of::<f32>(),
            "note":"Only conditional equity may be reused. Always apply current counterfactual mass, including folded opponents. Frozen/profile state must remain unchanged."}))
    }

    /// Read-only learning-scale diagnostics. No payoff evaluation or arena edits.
    /// Current and average prefix reaches are reported separately; neither is
    /// silently substituted for the other in a convergence claim.
    pub fn research_node_learning_diagnostics(&self, path: &[usize]) -> Result<Value, String> {
        if self.nodes.len() > 2_000_000 || path.len() > 64 || self.stop_requested() {
            return Err("diagnostics require a bounded, unstopped game".into());
        }
        let (node, average_reaches) = self.walk(path)?;
        let nd = &self.nodes[node];
        if nd.kind != KIND_ACTION { return Err("diagnostics require an action node".into()); }
        let current_sigma = |i: usize| {
            if let Some(forced) = self.forced_sigma(i) { return forced; }
            if self.seat_frozen[self.nodes[i].actor as usize] { return self.average_strategy(i); }
            let mut sigma = vec![0f32; self.nodes[i].actions.len() * NUM_CLASSES];
            self.current_strategy(i, &mut sigma);
            sigma
        };
        let mut current_reaches = self.root_reaches();
        let mut prefix = 0;
        for &action in path {
            let actor = self.nodes[prefix].actor as usize;
            let sigma = current_sigma(prefix);
            for h in 0..NUM_CLASSES { current_reaches[actor][h] *= sigma[action * NUM_CLASSES + h]; }
            prefix = self.child(prefix, action);
        }
        let average = self.average_strategy(node);
        let current = current_sigma(node);
        let average_mass: Vec<f64> = average_reaches.iter().map(|r|r.iter().sum::<f32>() as f64).collect();
        let current_mass: Vec<f64> = current_reaches.iter().map(|r|r.iter().sum::<f32>() as f64).collect();
        let actor = nd.actor as usize;
        let forced = self.forced_sigma(node).is_some();
        let frozen = self.seat_frozen[actor];
        // SAFETY: read-only offline inspection; the caller cannot mutate the
        // solver during this shared borrow.
        let (regrets, sums) = unsafe { (self.regrets.slice(), self.strat_sum.slice()) };
        let mut hands = Vec::new();
        for h in 0..NUM_CLASSES {
            let r: Vec<f32> = (0..nd.actions.len()).map(|a|regrets[nd.data_off + a * NUM_CLASSES + h]).collect();
            let s: Vec<f32> = (0..nd.actions.len()).map(|a|sums[nd.data_off + a * NUM_CLASSES + h]).collect();
            if r.iter().chain(&s).any(|x| !x.is_finite()) { return Err("nonfinite diagnostic arena".into()); }
            let positive_regret_sum: f32 = r.iter().map(|v|v.max(0.0)).sum();
            let strategy_sum: f32 = s.iter().sum();
            hands.push(json!({"hand":equity::class_label(h),"class_index":h,
                "average_conditional_hand_mass":if average_mass[actor]>0.0 {average_reaches[actor][h] as f64/average_mass[actor]} else {0.0},
                "current_conditional_hand_mass":if current_mass[actor]>0.0 {current_reaches[actor][h] as f64/current_mass[actor]} else {0.0},
                "positive_regret_sum":positive_regret_sum,"strategy_sum":strategy_sum,
                "regrets":r,"strategy_sums":s,
                "current_uniform_fallback":!forced && !frozen && positive_regret_sum<=1e-12,
                "average_uniform_fallback":!forced && strategy_sum<=1e-12,
                "current_probabilities":(0..nd.actions.len()).map(|a|current[a*NUM_CLASSES+h]).collect::<Vec<_>>(),
                "average_probabilities":(0..nd.actions.len()).map(|a|average[a*NUM_CLASSES+h]).collect::<Vec<_>>()}));
        }
        Ok(json!({"path":path,"position":self.cfg.positions[actor],"actor":actor,
            "iteration":self.iteration,"forced":forced,"frozen":frozen,
            "actions":nd.actions.iter().map(|a|a.label.clone()).collect::<Vec<_>>(),
            "average_prefix_mass_by_seat":average_mass,"current_prefix_mass_by_seat":current_mass,
            "average_counterfactual_prefix_mass":average_mass.iter().enumerate().filter(|(p,_)|*p!=actor).map(|(_,v)|*v).product::<f64>(),
            "current_counterfactual_prefix_mass":current_mass.iter().enumerate().filter(|(p,_)|*p!=actor).map(|(_,v)|*v).product::<f64>(),
            "hands":hands}))
    }

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
        self.research_action_quality_impl(reference,path,false)
    }

    /// Condition on positive incoming ranges before evaluating tiny branches.
    /// Retain raw reach metadata and the historical audit separately.
    pub fn research_conditioned_action_quality_against(&self, reference:&Self, path:&[usize])->Result<Value,String> {
        self.research_action_quality_impl(reference,path,true)
    }

    fn research_action_quality_impl(&self, reference:&Self, path:&[usize], conditioned:bool)->Result<Value,String> {
        if self.nodes.len() > 2_000_000 || reference.nodes.len() > 2_000_000 || path.len() > 64 {
            return Err("local quality requires <=2,000,000 nodes and path length <=64".into());
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
        let (node, mut reaches) = reference.walk(path)?;
        let (candidate_node, _) = self.walk(path)?;
        let nd = &reference.nodes[node];
        // Large games are allowed only for bounded selected subtrees.
        let mut pending = vec![node]; let mut visited = 0;
        while let Some(i) = pending.pop() {
            visited += 1;
            if visited > 50_000 { return Err("local audit subtree exceeds 50,000 nodes".into()); }
            let n = &reference.nodes[i];
            pending.extend((0..n.actions.len()).map(|a| reference.children[n.child_start as usize+a] as usize));
        }
        if nd.kind != KIND_ACTION || node != candidate_node { return Err("local quality path must name an identical action node".into()); }
        let p = nd.actor as usize;
        let actor_mass: f64 = reaches[p].iter().map(|&x|x as f64).sum();
        // Match terminal_value's f32 mass sums before f64 product.
        let opponent_mass: f64 = reaches.iter().enumerate().filter(|(q,_)|*q != p)
            .map(|(_,r)|r.iter().sum::<f32>() as f64).product();
        let raw_masses:Vec<f64>=reaches.iter().map(|r|r.iter().map(|&x|x as f64).sum()).collect();
        if (!conditioned && (actor_mass <= 1e-12 || opponent_mass <= 1e-12))
            || (conditioned && raw_masses.iter().any(|m|!m.is_finite() || *m<=0.0)) {
            return Ok(json!({"path":path,"status":"unreachable_under_reference","actor_mass":actor_mass,"opponent_mass":opponent_mass}));
        }
        if conditioned {
            for (r,m) in reaches.iter_mut().zip(&raw_masses) {for value in r {*value=(*value as f64/m) as f32;}}
        }
        let evaluation_actor_mass:f64=reaches[p].iter().map(|&x|x as f64).sum();
        let evaluation_opponent_mass:f64=reaches.iter().enumerate().filter(|(q,_)|*q!=p)
            .map(|(_,r)|r.iter().sum::<f32>() as f64).product();
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
            let mass = reaches[p][h] as f64 / evaluation_actor_mass;
            let q: Vec<f64> = action_values.iter().map(|v|v[h] as f64 / evaluation_opponent_mass).collect();
            let best = q.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let probabilities: Vec<f64> = (0..nd.actions.len()).map(|a|candidate_sigma[a * NUM_CLASSES + h] as f64).collect();
            if (probabilities.iter().sum::<f64>() - 1.0).abs() > 1e-5 { return Err("unnormalized local candidate".into()); }
            let loss: f64 = q.iter().zip(&probabilities).map(|(v,prob)|prob * (best-v)).sum();
            let reference_loss: f64 = q.iter().enumerate().map(|(a,v)|reference_sigma[a * NUM_CLASSES + h] as f64 * (best-v)).sum();
            let bad_mass: f64 = q.iter().zip(&probabilities).filter(|(v,_)|best-**v > 0.1).map(|(_,p)|*p).sum();
            weighted_loss += mass * loss;
            reference_weighted_loss += mass * reference_loss;
            if mass >= 0.0025 { worst_relevant_bad_mass = worst_relevant_bad_mass.max(bad_mass); }
            rows.push(json!({"class_index":h,"hand":equity::class_label(h),"conditional_hand_mass":mass,"action_values_bb":q,
                "candidate_probabilities":probabilities,"expected_action_loss_bb":loss,
                "reference_probabilities":(0..nd.actions.len()).map(|a|reference_sigma[a * NUM_CLASSES+h]).collect::<Vec<_>>(),
                "reference_expected_action_loss_bb":reference_loss,"probability_on_actions_losing_over_0_1bb":bad_mass}));
        }
        if self.stop_requested() || reference.stop_requested() { return Err("local quality canceled before publication".into()); }
        Ok(json!({"path":path,"status":"evaluated","actor":p,"position":reference.cfg.positions[p],
            "scope":"One-action deviation followed by reference play, same reference arriving ranges; excludes physical-deal validation",
            "actor_mass":actor_mass,"opponent_mass":opponent_mass,"joint_reach_independent_model":actor_mass*opponent_mass,
            "conditioned_before_evaluation":conditioned,
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
    fn conditioned_audit_preserves_values_at_tiny_positive_reach() {
        let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":2,
            "limp":false,"open_raises":[2],"raise_mults":[3],"max_raises":1,"add_allin":false,"rake_pct":0,"rake_cap":0,"realization":"raw"})).unwrap();
        let s=PreflopSolver::new(cfg,Arc::new(equity::EquityTable::build(8))).unwrap();
        let f=s.nodes[0].actions.iter().position(|a|a.kind=="fold").unwrap();
        let sb=s.child(0,f);
        let r=s.nodes[sb].actions.iter().position(|a|a.to==2.0 && a.kind!="call").unwrap();
        let path=vec![f,r];
        let baseline=s.research_local_action_quality_against(&s,&path).unwrap();
        let normalized=s.research_conditioned_action_quality_against(&s,&path).unwrap();
        let compare=|a:&Value,b:&Value| {
            for (left,right) in a["hands"].as_array().unwrap().iter().zip(b["hands"].as_array().unwrap()) {
                for (x,y) in left["action_values_bb"].as_array().unwrap().iter().zip(right["action_values_bb"].as_array().unwrap()) {
                    assert!((x.as_f64().unwrap()-y.as_f64().unwrap()).abs()<0.0001);
                }
            }
        };
        compare(&baseline,&normalized);
        for (node,selected) in [(0,f),(sb,r)] {
            let nd=&s.nodes[node];
            for a in 0..nd.actions.len() {for h in 0..NUM_CLASSES {
                unsafe {s.strat_sum.slice_mut()[nd.data_off+a*NUM_CLASSES+h]=if a==selected {1e-8} else {1.0};}
            }}
        }
        assert_eq!(s.research_local_action_quality_against(&s,&path).unwrap()["status"],"unreachable_under_reference");
        let tiny=s.research_conditioned_action_quality_against(&s,&path).unwrap();
        assert_eq!(tiny["status"],"evaluated");
        compare(&baseline,&tiny);
        for h in 0..NUM_CLASSES {unsafe {s.strat_sum.slice_mut()[s.nodes[0].data_off+f*NUM_CLASSES+h]=0.0;}}
        assert_eq!(s.research_conditioned_action_quality_against(&s,&path).unwrap()["status"],"unreachable_under_reference");
    }

    #[test]
    fn local_call_and_fold_match_direct_heads_up_payoffs() {
        let cfg: PreflopConfig = serde_json::from_value(json!({
            "positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":2,
            "limp":false,"open_raises":[2],"raise_mults":[3],"max_raises":1,
            "add_allin":false,"rake_pct":0,"rake_cap":0,"realization":"raw"
        })).unwrap();
        let reference = PreflopSolver::new(cfg, Arc::new(equity::EquityTable::build(8))).unwrap();
        let btn_fold = reference.nodes[0].actions.iter().position(|a| a.kind == "fold").unwrap();
        let sb = reference.child(0, btn_fold);
        let sb_raise = reference.nodes[sb].actions.iter()
            .position(|a| a.to == 2.0 && a.kind != "call").unwrap();
        let bb = reference.child(sb, sb_raise);
        assert_eq!(reference.nodes[bb].actor, 2);
        let fold = reference.nodes[bb].actions.iter().position(|a| a.kind == "fold").unwrap();
        let call = reference.nodes[bb].actions.iter().position(|a| a.kind == "call").unwrap();
        assert_eq!(reference.nodes[bb].actions.len(), 2);
        let called = &reference.nodes[reference.child(bb, call)];
        assert_eq!(called.kind, KIND_POT_SHARE);
        assert_eq!(called.pot, 4.0);
        assert_eq!(called.invested[2], 2.0);
        assert_eq!(called.r[2], 1.0);
        // Fresh exclusively owned fixture: give SB a nonuniform raising range
        // and BB an explicit 25% call / 75% fold policy. No learning is run.
        unsafe {
            let sums = reference.strat_sum.slice_mut();
            for h in 0..NUM_CLASSES {
                for a in 0..reference.nodes[sb].actions.len() {
                    sums[reference.nodes[sb].data_off + a * NUM_CLASSES + h] =
                        if a == sb_raise { (h % 7 + 1) as f32 } else { 1.0 };
                }
                sums[reference.nodes[bb].data_off + call * NUM_CLASSES + h] = 1.0;
                sums[reference.nodes[bb].data_off + fold * NUM_CLASSES + h] = 3.0;
                let regrets = reference.regrets.slice_mut();
                regrets[reference.nodes[bb].data_off + call * NUM_CLASSES + h] = if h==0 {1e-14} else {3.0};
                regrets[reference.nodes[bb].data_off + fold * NUM_CLASSES + h] = if h==0 {1e-14} else {1.0};
            }
        }
        let path = [btn_fold, sb_raise];
        let (_, reaches) = reference.walk(&path).unwrap();
        let before_diagnostics = reference.arena_snapshot();
        let diagnostics = reference.research_node_learning_diagnostics(&path).unwrap();
        assert_eq!(before_diagnostics, reference.arena_snapshot());
        assert_eq!(diagnostics["hands"][0]["current_uniform_fallback"], true);
        assert_eq!(diagnostics["hands"][0]["current_probabilities"][call].as_f64(), Some(0.5));
        assert_eq!(diagnostics["hands"][1]["current_uniform_fallback"], false);
        assert_eq!(diagnostics["hands"][1]["current_probabilities"][call].as_f64(), Some(0.75));
        assert_eq!(diagnostics["hands"][1]["average_probabilities"][call].as_f64(), Some(0.25));
        assert_ne!(diagnostics["average_prefix_mass_by_seat"], diagnostics["current_prefix_mass_by_seat"]);
        let sb_mass: f64 = reaches[1].iter().map(|&v| v as f64).sum();
        let result = reference.research_local_action_quality_against(&reference, &path).unwrap();
        let rows = result["hands"].as_array().unwrap();
        assert_eq!(rows.len(), NUM_CLASSES);
        for (h, row) in rows.iter().enumerate() {
            // Direct one-opponent equity sum, independently of the local
            // traversal and its counterfactual reach normalization.
            let equity: f64 = (0..NUM_CLASSES).map(|j|
                reference.eq.eq(h, j) as f64 * reaches[1][j] as f64 / sb_mass).sum();
            let call_value = 4.0 * equity - 2.0;
            let fold_value = -1.0;
            assert!((row["action_values_bb"][call].as_f64().unwrap() - call_value).abs() < 1e-5);
            assert!((row["action_values_bb"][fold].as_f64().unwrap() - fold_value).abs() < 1e-6);
            let expected_loss = call_value.max(fold_value) - (0.25 * call_value + 0.75 * fold_value);
            assert!((row["expected_action_loss_bb"].as_f64().unwrap() - expected_loss).abs() < 1e-5);
        }
    }

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
        let diagnostics = reference.research_node_learning_diagnostics(&[]).unwrap();
        assert_eq!(diagnostics["hands"].as_array().unwrap().len(), NUM_CLASSES);
        assert_eq!(diagnostics["average_prefix_mass_by_seat"], diagnostics["current_prefix_mass_by_seat"]);
        assert!(reference.research_node_learning_diagnostics(&[usize::MAX]).is_err());
        assert_eq!(reference.research_static_terminal_reuse().unwrap()["reusable_conditional_pairs"].as_u64(),Some(0));
        let frozen_before=reference.seat_frozen.clone();
        reference.seat_frozen.fill(true);
        let fixed_reuse=reference.research_static_terminal_reuse().unwrap();
        assert!(fixed_reuse["multiway_terminal_traverser_pairs"].as_u64().unwrap()>0);
        assert_eq!(fixed_reuse["reusable_conditional_pairs"],fixed_reuse["multiway_terminal_traverser_pairs"]);
        reference.seat_frozen=frozen_before;
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
