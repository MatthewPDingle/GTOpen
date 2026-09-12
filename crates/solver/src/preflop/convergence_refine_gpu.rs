//! Offline compact GPU branch refinement. Never resumes a global session.
use super::*;
use serde_json::{json,Value};

impl PreflopSolver {
    pub fn research_refine_branch_gpu(&mut self,path:&[usize],iterations:u32,budget_mb:usize)->Result<Value,String> {
        if iterations==0 || iterations>4000 || budget_mb<2 || self.stop_requested(){return Err("bounded unstopped GPU refinement required".into());}
        if self.multiway_equity_model()!="coupled_deck_v1" {return Err("compact GPU research requires the canonical coupled model".into());}
        let plan=self.research_refinement_plan(path)?;
        let (root,mut reaches)=self.walk(path)?;
        for range in &mut reaches {
            let mass:f64=range.iter().map(|&x|x as f64).sum();
            if !mass.is_finite() || mass<=0.0 {return Err("unreachable average prefix".into());}
            for value in range {*value=(*value as f64/mass) as f32;}
        }
        let started=std::time::Instant::now();
        let mut original=Vec::new();let mut pending=vec![root];
        while let Some(node)=pending.pop() {
            original.push(node);
            let nd=&self.nodes[node];
            pending.extend((0..nd.actions.len()).rev().map(|a|self.child(node,a)));
        }
        let mapping:std::collections::HashMap<usize,usize>=original.iter().enumerate().map(|(i,&node)|(node,i)).collect();
        let mut nodes=Vec::new();let mut children=Vec::new();let mut arena_len=0;
        let mut locks=std::collections::HashMap::new();
        for (local,&node) in original.iter().enumerate() {
            let nd=&self.nodes[node];let child_start=children.len() as u32;
            children.extend((0..nd.actions.len()).map(|a|mapping[&self.child(node,a)] as u32));
            nodes.push(PNode{kind:nd.kind,actor:nd.actor,actions:nd.actions.clone(),child_start,
                pot:nd.pot,invested:nd.invested.clone(),live:nd.live,winner:nd.winner,r:nd.r.clone(),data_off:arena_len,
                aggressor:nd.aggressor,posf:nd.posf.clone(),bucket:nd.bucket,raises:nd.raises,raised:nd.raised});
            arena_len+=nd.actions.len()*NUM_CLASSES;
            if let Some(lock)=self.point_locks.get(&(node as u32)){locks.insert(local as u32,lock.clone());}
        }
        let mut compact=PreflopSolver{cfg:self.cfg.clone(),eq:self.eq.clone(),nodes,children,n:self.n,
            regrets:Arena::new(arena_len),strat_sum:Arena::new(arena_len),arena_len,iteration:0,prune:false,
            fit:self.fit.clone(),seat_frozen:self.seat_frozen.clone(),seat_profiles:self.seat_profiles.clone(),hero:self.hero,
            pre_hero_frozen:None,hero_backup:None,point_locks:locks,realization_note:self.realization_note.clone(),
            multiway:self.multiway.clone(),stop_flag:self.stop_flag.clone(),contextual_cache:Default::default()};
        let learning:std::collections::HashSet<usize>=plan["learning_node_indices"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as usize).collect();
        if learning.is_empty(){return Err("no learning decisions in selected subtree".into());}
        for (local,&node) in original.iter().enumerate() {
            if learning.contains(&node){continue;}
            let src=&self.nodes[node];let dst=&compact.nodes[local];let len=src.actions.len()*NUM_CLASSES;
            unsafe {
                compact.regrets.slice_mut()[dst.data_off..dst.data_off+len].copy_from_slice(&self.regrets.slice()[src.data_off..src.data_off+len]);
                compact.strat_sum.slice_mut()[dst.data_off..dst.data_off+len].copy_from_slice(&self.strat_sum.slice()[src.data_off..src.data_off+len]);
            }
        }
        for (local,&node) in original.iter().enumerate() {
            if self.nodes[node].kind==KIND_ACTION && self.forced_sigma(node)!=compact.forced_sigma(local) {
                return Err("compact branch changed a fixed/profile policy".into());
            }
        }
        // Reserve one MB for the tiny additional per-seat root-range buffer.
        let mut engine=gpu::PreflopGpu::new(&compact,(budget_mb-1) as u64)?;
        engine.research_set_root_ranges(reaches)?;
        let setup_seconds=started.elapsed().as_secs_f64();let solve=std::time::Instant::now();
        let stop=self.stop_flag.clone();
        for _ in 0..iterations {
            if self.stop_requested(){return Err("GPU refinement canceled; parent unchanged".into());}
            if !engine.try_iterate(&mut compact,stop.as_deref())? {
                return Err("GPU refinement canceled during iteration; parent unchanged".into());
            }
        }
        let solve_seconds=solve.elapsed().as_secs_f64();
        let (gaps,evs)=engine.gaps_and_evs()?;
        if gaps.iter().chain(&evs).any(|x|!x.is_finite()){return Err("nonfinite compact GPU check".into());}
        engine.sync_to_cpu(&mut compact)?;drop(engine);
        if self.stop_requested(){return Err("GPU refinement canceled before copy; parent unchanged".into());}
        for (local,&node) in original.iter().enumerate() {
            if !learning.contains(&node){continue;}
            let nd=&compact.nodes[local];let span=nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES;
            unsafe {
                if compact.regrets.slice()[span.clone()].iter().any(|x|!x.is_finite())
                    || compact.strat_sum.slice()[span].iter().any(|x|!x.is_finite() || *x<0.0) {
                    return Err("invalid compact learning arenas; parent unchanged".into());
                }
            }
        }
        // The parent is mutated only after a complete, validated device solve.
        for (local,&node) in original.iter().enumerate() {
            if !learning.contains(&node){continue;}
            let src=&compact.nodes[local];let dst=&self.nodes[node];let len=src.actions.len()*NUM_CLASSES;
            unsafe {
                self.regrets.slice_mut()[dst.data_off..dst.data_off+len].copy_from_slice(&compact.regrets.slice()[src.data_off..src.data_off+len]);
                self.strat_sum.slice_mut()[dst.data_off..dst.data_off+len].copy_from_slice(&compact.strat_sum.slice()[src.data_off..src.data_off+len]);
            }
        }
        Ok(json!({"scope":"Offline full-particle compact GPU branch under fixed normalized incoming ranges",
            "path":path,"nodes":compact.nodes.len(),"learning_nodes":learning.len(),"local_iterations":iterations,
            "global_iteration_unchanged":self.iteration,"setup_seconds":setup_seconds,"solve_seconds":solve_seconds,
            "fixed_policy_equivalence":true,
            "seconds":started.elapsed().as_secs_f64(),"conditional_global_gaps":gaps,"conditional_global_evs":evs,
            "normal_global_resume_supported":false}))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture(eq:Arc<equity::EquityTable>,calibrated:bool)->(PreflopSolver,Vec<usize>) {
        let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],"posts":[0,0,0.5,1],"stack":5,
            "limp":true,"open_raises":[2],"raise_mults":[3],"max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,
            "realization":if calibrated {"calibrated"} else {"raw"}})).unwrap();
        let mut s=PreflopSolver::new(cfg,eq).unwrap();
        if calibrated {assert!(s.fit.is_some());}
        let limp=s.nodes[0].actions.iter().position(|a|a.kind=="call").unwrap();
        for a in 0..s.nodes[0].actions.len() {for h in 0..NUM_CLASSES {
            unsafe {s.strat_sum.slice_mut()[a*NUM_CLASSES+h]=if a==limp {0.05+(h%7) as f32} else {1.0};}
        }}
        if calibrated {
            s.seat_frozen[2]=true;
            for nd in &s.nodes {if nd.actor==2 {for a in 0..nd.actions.len() {for h in 0..NUM_CLASSES {
                unsafe {s.strat_sum.slice_mut()[nd.data_off+a*NUM_CLASSES+h]=(a+1) as f32;}
            }}}}
            let root=s.child(0,limp);
            let mut stack=vec![root];let mut locked=None;
            while let Some(node)=stack.pop() {
                let nd=&s.nodes[node];
                if nd.actor==3 && nd.actions.len()>1 {locked=Some(node);break;}
                stack.extend((0..nd.actions.len()).map(|a|s.child(node,a)));
            }
            let node=locked.unwrap();let mut policy=vec![0.0;s.nodes[node].actions.len()*NUM_CLASSES];
            policy[..NUM_CLASSES].fill(1.0);s.point_locks.insert(node as u32,policy);
        }
        s.iteration=17;
        (s,vec![limp])
    }
    #[test]
    fn compact_gpu_matches_cpu_conditional_branch_and_preserves_constraints() {
        let eq=Arc::new(equity::EquityTable::build(8));
        for calibrated in [false,true] {
            let (mut cpu,path)=fixture(eq.clone(),calibrated);
            let (mut gpu,_)=fixture(eq.clone(),calibrated);
            let before=gpu.arena_snapshot();
            let plan=gpu.research_refinement_plan(&path).unwrap();
            let allowed:std::collections::HashSet<usize>=plan["learning_node_indices"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as usize).collect();
            cpu.research_refine_branches(&[path.clone()],50).unwrap();
            let result=gpu.research_refine_branch_gpu(&path,50,512).unwrap();
            assert_eq!(result["global_iteration_unchanged"],17);
            assert!(result["nodes"].as_u64().unwrap()<(gpu.nodes.len() as u64));
            let after=gpu.arena_snapshot();
            let mut worst=0.0f32;
            for (node,nd) in gpu.nodes.iter().enumerate() {
                let span=nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES;
                if !allowed.contains(&node) {
                    assert_eq!(before.0[span.clone()],after.0[span.clone()]);
                    assert_eq!(before.1[span.clone()],after.1[span]);
                } else {
                    for (a,b) in cpu.average_strategy(node).into_iter().zip(gpu.average_strategy(node)) {worst=worst.max((a-b).abs());}
                }
            }
            assert!(worst<=0.005,"conditional policy discrepancy {worst}, calibrated={calibrated}");
            let a=cpu.research_conditioned_action_quality_against(&cpu,&path).unwrap();
            let b=gpu.research_conditioned_action_quality_against(&gpu,&path).unwrap();
            for (a,b) in a["hands"].as_array().unwrap().iter().zip(b["hands"].as_array().unwrap()) {
                for (a,b) in a["action_values_bb"].as_array().unwrap().iter().zip(b["action_values_bb"].as_array().unwrap()) {
                    assert!((a.as_f64().unwrap()-b.as_f64().unwrap()).abs()<=0.005);
                }
            }
            let (root,mut ranges)=gpu.walk(&path).unwrap();
            for range in &mut ranges {let mass:f64=range.iter().map(|&x|x as f64).sum();for x in range {*x=(*x as f64/mass) as f32;}}
            for p in 0..gpu.n {
                let values=gpu.traverse_checkpoint(root,p,&mut ranges.clone(),if gpu.constrained_br(p) {3} else {2},CheckpointNeeds{br:true,avg:true},0).unwrap();
                let br=values.br.unwrap();let avg=values.avg.unwrap();
                let ev:f64=(0..NUM_CLASSES).map(|h|ranges[p][h] as f64*avg[h] as f64).sum();
                let gap:f64=(0..NUM_CLASSES).map(|h|ranges[p][h] as f64*(br[h]-avg[h]) as f64).sum();
                assert!((ev-result["conditional_global_evs"][p].as_f64().unwrap()).abs()<=0.005,"wrong conditional EV weighting");
                assert!((gap-result["conditional_global_gaps"][p].as_f64().unwrap()).abs()<=0.005,"wrong conditional gap weighting");
            }
            let snapshot=gpu.arena_snapshot();let stop=Arc::new(AtomicBool::new(true));
            gpu.set_stop_flag(Some(stop));
            assert!(gpu.research_refine_branch_gpu(&path,50,512).is_err());
            assert_eq!(snapshot,gpu.arena_snapshot());
        }
    }
}
