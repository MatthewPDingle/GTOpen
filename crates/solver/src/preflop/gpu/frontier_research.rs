//! Read-only average-continuation action values for large-tree diagnostics.
use super::*;
use serde_json::{json,Value};

impl PreflopGpu {
    /// Values include actual opponent prefix mass. Gains use actual actor reach.
    /// Node gains overlap and must not be summed as a full-BR decomposition.
    pub fn research_frontier_action_values(&mut self,s:&PreflopSolver,paths:&[Vec<usize>])->Result<Value,String> {
        if self.research_predictive.is_some() || self.research_rm_plus.is_some() || self.warmed || self.research_learning_mask || self.research_root_ranges.is_some()
            || paths.is_empty() || paths.len()>256 || s.nodes.len()>2_000_000
            || self.d_val_slot.len()!=s.nodes.len() || self.np as usize!=s.n
            || s.multiway_equity_model()!="coupled_deck_v1" || s.stop_requested() {
            return Err("fresh unmasked bounded canonical parent engine required".into());
        }
        let mut selected=Vec::new();
        let mut seen=std::collections::HashSet::new();
        for path in paths {
            if path.len()>64 || !seen.insert(path.clone()) {return Err("invalid frontier paths".into());}
            let (node,reaches)=s.walk(path)?;
            if s.nodes[node].kind!=KIND_ACTION {return Err("frontier must contain action nodes".into());}
            selected.push((path,node,reaches));
        }
        self.research_tables(false)?;
        self.down(1,-1)?;
        let slots=self.stream.clone_dtoh(&self.d_val_slot).map_err(e)?;
        let mut rows=Vec::new();
        for p in 0..s.n {
            if !selected.iter().any(|(_,node,_)|s.nodes[*node].actor as usize==p) {continue;}
            if s.stop_requested() {return Err("frontier canceled".into());}
            self.terminals_masked(p as i32,0)?;
            // Action value storage is reused between nonadjacent levels.
            // Capture child values immediately before their parent level is
            // evaluated, rather than after the complete upward traversal.
            for li in (0..self.spans.len()).rev() {
            for (path,node,reaches) in &selected {
                let nd=&s.nodes[*node];if nd.actor as usize!=p || path.len()!=li {continue;}
                let mut values=Vec::new();
                for a in 0..nd.actions.len() {
                    let child=s.child(*node,a);let off=slots[child] as usize*NUM_CLASSES;
                    values.push(self.stream.clone_dtoh(&self.d_val.slice(off..off+NUM_CLASSES)).map_err(e)?);
                }
                let sigma=s.average_strategy(*node);
                let mut gain=0.0f64;let mut hands=Vec::new();
                for h in 0..NUM_CLASSES {
                    let q:Vec<f64>=values.iter().map(|v|v[h] as f64).collect();
                    let probabilities:Vec<f64>=(0..nd.actions.len()).map(|a|sigma[a*NUM_CLASSES+h] as f64).collect();
                    if q.iter().chain(&probabilities).any(|v|!v.is_finite()) {return Err("nonfinite frontier values".into());}
                    let best=q.iter().copied().fold(f64::NEG_INFINITY,f64::max);
                    let loss:f64=q.iter().zip(&probabilities).map(|(v,w)|(best-v)*w).sum();
                    gain+=reaches[p][h] as f64*loss;
                    hands.push(json!({"class_index":h,"action_values_counterfactual_bb":q,
                        "average_probabilities":probabilities,"actor_reach":reaches[p][h]}));
                }
                let constrained=s.seat_frozen[p] || s.forced_sigma(*node).is_some();
                rows.push(json!({"path":path,"node":node,"actor":p,"position":s.cfg.positions[p],
                    "actions":nd.actions.iter().map(|a|&a.label).collect::<Vec<_>>(),"forced_or_frozen":constrained,
                    "full_parent_one_step_gain_bb":if constrained {None} else {Some(gain)},"hands":hands}));
            }
            self.research_frontier_up_level(p as i32,li)?;
            }
        }
        Ok(json!({"rows":rows,"scope":"One-step deviations under average continuation and actual prefix reach; overlapping gains are not an additive full-BR decomposition"}))
    }

    fn research_frontier_up_level(&mut self,p:i32,li:usize)->Result<(),String> {
        let (start,count)=self.spans[li];
        if count==0 {return Ok(());}
        let (start,count,mode)=(start as i32,count as i32,1i32);
        unsafe {
            self.stream.launch_builder(&self.f_up)
                .arg(&self.d_act_nodes).arg(&start).arg(&count).arg(&p).arg(&self.np).arg(&mode)
                .arg(&self.d_actor).arg(&self.d_na).arg(&self.d_off).arg(&self.d_cstart)
                .arg(&self.d_children).arg(&self.d_src).arg(&self.d_foff).arg(&self.d_forced)
                .arg(&self.d_reach_src).arg(&self.d_reach).arg(&mut self.d_regrets)
                .arg(&mut self.d_strat).arg(&self.d_val_slot).arg(&mut self.d_val)
                .launch(Self::cfg(count as u32)).map_err(e)?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{equity::EquityTable,PreflopConfig};
    #[test]
    fn frontier_gpu_values_match_independent_cpu_actions_without_learning() {
        let eq=Arc::new(EquityTable::build(8));
        let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],
            "stack":5.0,"posts":[0.0,0.0,0.5,1.0],"limp":true,"open_raises":[2.0],
            "raise_mults":[3.0],"max_raises":1,"add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"})).unwrap();
        let mut s=PreflopSolver::new(cfg,eq).unwrap();
        s.research_seed_quality_fixture_averages().unwrap();s.seat_frozen[2]=true;
        let locked=s.child(0,0);
        let mut policy=vec![0.0;s.nodes[locked].actions.len()*NUM_CLASSES];
        policy[..NUM_CLASSES].fill(1.0);s.point_locks.insert(locked as u32,policy);
        let mut paths=vec![vec![]];
        for a in 0..s.nodes[0].actions.len() {if s.nodes[s.child(0,a)].kind==KIND_ACTION {paths.push(vec![a]);}}
        // A locked-out branch must report zero raw counterfactual values,
        // rather than normalize a nonexistent arriving opponent range.
        if s.nodes[locked].actions.len()>1 && s.nodes[s.child(locked,1)].kind==KIND_ACTION {paths.push(vec![0,1]);}
        let before=s.arena_snapshot();let mut gpu=PreflopGpu::new(&s,512).unwrap();
        let report=gpu.research_frontier_action_values(&s,&paths).unwrap();
        for row in report["rows"].as_array().unwrap() {
            let path:Vec<usize>=serde_json::from_value(row["path"].clone()).unwrap();
            let cpu=s.research_local_action_quality_against(&s,&path).unwrap();
            if cpu["status"]=="unreachable_under_reference" {
                assert_eq!(cpu["opponent_mass"],0.0);
                for hand in row["hands"].as_array().unwrap() {
                    assert!(hand["action_values_counterfactual_bb"].as_array().unwrap().iter().all(|q|q.as_f64()==Some(0.0)));
                }
                continue;
            }
            let mass=cpu["opponent_mass"].as_f64().unwrap();
            for (a,b) in row["hands"].as_array().unwrap().iter().zip(cpu["hands"].as_array().unwrap()) {
                for (x,y) in a["action_values_counterfactual_bb"].as_array().unwrap().iter().zip(b["action_values_bb"].as_array().unwrap()) {
                    assert!((x.as_f64().unwrap()-y.as_f64().unwrap()*mass).abs()<0.0002,"frontier action value discrepancy");
                }
            }
            if !row["forced_or_frozen"].as_bool().unwrap() {
                let expected=cpu["weighted_action_loss_bb"].as_f64().unwrap()*mass*cpu["actor_mass"].as_f64().unwrap();
                assert!((row["full_parent_one_step_gain_bb"].as_f64().unwrap()-expected).abs()<0.0002);
            }
        }
        gpu.sync_to_cpu(&mut s).unwrap();assert_eq!(before,s.arena_snapshot());
    }
}
