//! Offline bounded conditional re-solving. Never used by the live server.
use super::*;
use serde_json::{json, Value};

impl PreflopSolver {
    /// Re-solve disjoint selected subtrees against their saved average incoming
    /// distributions. Reset only learning arenas inside those subtrees; preserve
    /// all upstream policies and fixed/profile actions. The caller must discard
    /// this research copy after cancellation; this is not a resumable global
    /// iteration and intentionally leaves the global iteration counter intact.
    pub fn research_refine_branches(&mut self, paths: &[Vec<usize>], iterations: u32) -> Result<Value,String> {
        if self.nodes.len()>50_000 || paths.is_empty() || paths.len()>8 || iterations==0 || iterations>1000 || self.stop_requested() {
            return Err("conditional refinement requires a bounded offline fixture".into());
        }
        let mut branches=Vec::new();
        let mut seen=std::collections::HashSet::new();
        for path in paths {
            if path.is_empty() || path.len()>64 {return Err("refine a proper subtree".into());}
            let (root,mut reaches)=self.walk(path)?;
            if self.nodes[root].kind!=KIND_ACTION {return Err("action root required".into());}
            let masses:Vec<f64>=reaches.iter().map(|r|r.iter().map(|&x|x as f64).sum()).collect();
            for (r,&mass) in reaches.iter_mut().zip(&masses) {
                if !mass.is_finite() || mass<=1e-15 {return Err("unreachable average prefix".into());}
                // A positive constant per seat changes only regret scale, not
                // the conditional game. Fresh local arenas avoid mixing scales.
                for value in r { *value=(*value as f64/mass) as f32; }
            }
            let mut pending=vec![root]; let mut learning=Vec::new(); let mut count=0;
            while let Some(node)=pending.pop() {
                count+=1;
                if count>10_000 || !seen.insert(node) {return Err("overlapping or oversized subtrees".into());}
                let nd=&self.nodes[node];
                if nd.kind!=KIND_ACTION {continue;}
                if !self.seat_frozen[nd.actor as usize] && self.forced_sigma(node).is_none() {learning.push(node);}
                pending.extend((0..nd.actions.len()).map(|a|self.child(node,a)));
            }
            branches.push((root,reaches,masses,learning,count));
        }
        // All structural validation precedes mutation. No traversal is running.
        for (_,_,_,learning,_) in &branches {
            for &node in learning {
                let nd=&self.nodes[node]; let span=nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES;
                unsafe {self.regrets.slice_mut()[span.clone()].fill(0.0); self.strat_sum.slice_mut()[span].fill(0.0);}
            }
        }
        let saved_prune=self.prune; self.prune=false;
        let started=std::time::Instant::now();
        let result=(|| {
            for local_iteration in 1..=iterations {
                for (root,reaches,_,learning,_) in &branches {
                    for p in 0..self.n {
                        if !learning.iter().any(|&i|self.nodes[i].actor as usize==p) {continue;}
                        if self.stop_requested() {return Err("conditional refinement canceled; discard copy".to_string());}
                        self.traverse(*root,p,&mut reaches.clone(),0,0);
                    }
                    let t=local_iteration as f64;
                    let pos=(t.powf(DCFR_ALPHA)/(t.powf(DCFR_ALPHA)+1.0)) as f32;
                    let sd=(t/(t+1.0)).powf(DCFR_GAMMA) as f32;
                    for &node in learning {
                        let nd=&self.nodes[node];let span=nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES;
                        unsafe {
                            for r in &mut self.regrets.slice_mut()[span.clone()] {*r*=if *r>0.0 {pos} else {0.5};}
                            for s in &mut self.strat_sum.slice_mut()[span] {*s*=sd;}
                        }
                    }
                }
            }
            if self.stop_requested() {return Err("conditional refinement canceled; discard copy".into());}
            Ok(json!({"scope":"Fresh local DCFR under fixed saved average incoming ranges; requires global and local revalidation",
                "local_iterations":iterations,"global_iteration_unchanged":self.iteration,"seconds":started.elapsed().as_secs_f64(),
                "branches":branches.iter().zip(paths).map(|((_,_,m,l,c),path)|json!({"path":path,"nodes":c,"learning_nodes":l.len(),"original_prefix_mass_by_seat":m})).collect::<Vec<_>>() }))
        })();
        self.prune=saved_prune;
        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn conditional_resolve_improves_last_actor_without_changing_prefix() {
        let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":2,
            "limp":false,"open_raises":[2],"raise_mults":[3],"max_raises":1,"add_allin":false,"rake_pct":0,"rake_cap":0,"realization":"raw"})).unwrap();
        let mut s=PreflopSolver::new(cfg,Arc::new(equity::EquityTable::build(8))).unwrap();
        let f=s.nodes[0].actions.iter().position(|a|a.kind=="fold").unwrap();
        let sb=s.child(0,f);
        let r=s.nodes[sb].actions.iter().position(|a|a.to==2.0 && a.kind!="call").unwrap();
        let path=vec![f,r];
        let root_before=s.average_strategy(0);let sb_before=s.average_strategy(sb);
        let before=s.research_local_action_quality_against(&s,&path).unwrap();
        let arenas=s.arena_snapshot();
        assert!(s.research_refine_branches(&[path.clone(),path.clone()],10).is_err());
        assert_eq!(arenas,s.arena_snapshot());
        s.research_refine_branches(&[path.clone()],100).unwrap();
        let after=s.research_local_action_quality_against(&s,&path).unwrap();
        assert!(after["weighted_action_loss_bb"].as_f64().unwrap()<before["weighted_action_loss_bb"].as_f64().unwrap()*0.01);
        assert_eq!(after["passes_local_tail_gate"],true);
        assert_eq!(root_before,s.average_strategy(0));assert_eq!(sb_before,s.average_strategy(sb));
        assert_eq!(s.iteration,0);
    }
}
