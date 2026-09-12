//! Offline in-memory branch ownership for fixed-unit global GPU continuation.
//! This is deliberately not an ordinary saved-game resume format.
use super::*;
use serde_json::{json,Value};

pub struct FixedUnitResearchState {
    owner:usize,
    valid:bool,
    expected:u64,
    regret:Vec<f32>,
    average:Vec<f32>,
    branches:Vec<Value>,
    origin_age:u32,
    age:u32,
}

fn word(h:&mut u64,x:u64) {*h=(*h^x).wrapping_mul(0x100000001b3);}
fn bytes(h:&mut u64,b:&[u8]) {word(h,b.len() as u64);for &x in b {word(h,x as u64);}}
fn unit_checksum(r:&[f32],a:&[f32])->String {
    let mut h=0xcbf29ce484222325;for v in r.iter().chain(a) {word(&mut h,v.to_bits() as u64);}format!("{h:016x}")
}

impl FixedUnitResearchState {
    pub fn metadata(&self)->Value {
        json!({"version":"in_memory_fixed_units_v1","valid":self.valid,"branches":self.branches,
            "origin_global_age":self.origin_age,"current_global_age":self.age,
            "unit_checksum":unit_checksum(&self.regret,&self.average),"state_checksum":format!("{:016x}",self.expected),
            "checksum_kind":"FNV word checksum for accidental change detection, not cryptographic",
            "unit_bytes":8*self.regret.len(),"ordinary_resume_supported":false,"persistent_resume_supported":false,
            "schedule":"Native full-particle DCFR at retained global age; compact histories are a synthetic warm start"})
    }
}

impl PreflopSolver {
    fn fixed_unit_fingerprint(&self)->Result<u64,String> {
        let mut h=0xcbf29ce484222325;
        let locks:std::collections::BTreeMap<_,_>=self.point_locks.iter().collect();
        let meta=json!({"config":self.cfg,"age":self.iteration,"frozen":self.seat_frozen,"profiles":self.seat_profiles,
            "locks":locks,"hero":self.hero,"prune":self.prune,"note":self.realization_note,
            "eq_identity":Arc::as_ptr(&self.eq) as usize,"fit":format!("{:?}",self.fit),
            "model":self.multiway_equity_model(),"arena_len":self.arena_len,"players":self.n});
        bytes(&mut h,&serde_json::to_vec(&meta).map_err(|e|e.to_string())?);
        word(&mut h,self.nodes.len() as u64);
        for nd in &self.nodes {
            for x in [nd.kind as u64,nd.actor as u64,nd.child_start as u64,nd.data_off as u64,nd.live as u64,
                nd.winner as u64,nd.aggressor as u64,nd.bucket as u64,nd.raises as u64,nd.raised as u64,nd.pot.to_bits()] {word(&mut h,x);}
            word(&mut h,nd.actions.len() as u64);
            for a in &nd.actions {bytes(&mut h,a.kind.as_bytes());bytes(&mut h,a.label.as_bytes());word(&mut h,a.to.to_bits());}
            for a in [&nd.invested] {word(&mut h,a.len() as u64);for v in a {word(&mut h,v.to_bits());}}
            for a in [&nd.r,&nd.posf] {word(&mut h,a.len() as u64);for v in a {word(&mut h,v.to_bits() as u64);}}
        }
        for &c in &self.children {word(&mut h,c as u64);}
        if let Some(m)=&self.multiway {for a in [&m.order,&m.lower,&m.upper] {word(&mut h,a.len() as u64);for &v in a {word(&mut h,v as u64);}}}
        unsafe {
            for (sum,a) in [(false,self.regrets.slice()),(true,self.strat_sum.slice())] {
                word(&mut h,a.len() as u64);
                for &v in a {if !v.is_finite() || (sum && v<0.0) {return Err("invalid research histories".into());}word(&mut h,v.to_bits() as u64);}
            }
        }
        Ok(h)
    }

    /// Prevalidate every branch before mutation. A later device error requires
    /// discarding this research copy; no usable state is returned on failure.
    pub fn research_refine_with_fixed_units_gpu(&mut self,paths:&[Vec<usize>],iterations:u32,budget_mb:usize)
        ->Result<(FixedUnitResearchState,Value),String> {
        if self.stop_requested() || self.hero.is_some() || self.hero_backup.is_some() || self.pre_hero_frozen.is_some()
            || paths.is_empty() || paths.len()>64 || iterations==0 || iterations>4000 || budget_mb<2
            || self.multiway_equity_model()!="coupled_deck_v1" {
            return Err("bounded disjoint canonical offline refinement required; hero backups unsupported".into());
        }
        for (i,p) in paths.iter().enumerate() {for q in &paths[..i] {
            if p.starts_with(q) || q.starts_with(p) {return Err("overlapping or duplicate refinement roots".into());}
        }}
        let _=self.fixed_unit_fingerprint()?;
        let mut regret=vec![1f32;self.nodes.len()];let mut average=regret.clone();let mut branches=Vec::new();
        let mut owned=std::collections::HashSet::new();
        for path in paths {
            let plan=self.research_refinement_plan(path)?;
            let masses:Vec<f32>=plan["prefix_mass_by_seat"].as_array().unwrap().iter().map(|x|x.as_f64().unwrap() as f32).collect();
            if masses.len()!=self.n || masses.iter().any(|x|!x.is_finite() || *x<=0.0 || *x>1.0) {return Err("invalid or unreachable reference mass".into());}
            let factors:Vec<f32>=(0..self.n).map(|p|(0..self.n).filter(|&q|q!=p).map(|q|masses[q]).product()).collect();
            let learning=plan["learning_node_indices"].as_array().unwrap();if learning.is_empty() {return Err("no learning ownership".into());}
            for node in learning {
                let node=node.as_u64().unwrap() as usize;let actor=self.nodes[node].actor as usize;
                if !owned.insert(node) || !(1e-8..=1.0).contains(&factors[actor]) || !(1e-8..=1.0).contains(&masses[actor]) {
                    return Err("overlapping ownership or out-of-bound history units".into());
                }
                regret[node]=factors[actor];average[node]=masses[actor];
            }
            branches.push(json!({"path":path,"root":plan["root"],"learning_nodes":learning,"reference_masses_f32":masses,
                "reference_masses_f64":plan["prefix_mass_by_seat"],"regret_factors_f32":factors,"local_age":iterations,"global_age_at_refinement":self.iteration}));
        }
        let age=self.iteration;let mut results=Vec::new();
        for path in paths {results.push(self.research_refine_branch_gpu(path,iterations,budget_mb)?);}
        if self.iteration!=age {return Err("compact refinement changed global age; discard research copy".into());}
        let state=FixedUnitResearchState{owner:self as *const Self as usize,valid:true,expected:self.fixed_unit_fingerprint()?,
            regret,average,branches,origin_age:age,age};
        let report=json!({"refinements":results,"metadata":state.metadata(),"qualified":false});
        Ok((state,report))
    }

    /// A state belongs to the exact in-memory research copy, not a .gtop file.
    /// Poison before device work; interruption/failure requires discarding it.
    pub fn research_continue_fixed_units_gpu(&mut self,state:&mut FixedUnitResearchState,iterations:u32,budget_mb:u64)->Result<Value,String> {
        if !state.valid || self.stop_requested() || self.hero.is_some() || self.hero_backup.is_some() || self.pre_hero_frozen.is_some() || state.owner!=self as *const Self as usize
            || self.iteration!=state.age || iterations==0 || iterations>1000
            || self.iteration.checked_add(iterations).is_none() || self.fixed_unit_fingerprint()?!=state.expected {
            return Err("mismatched, canceled or invalid fixed-unit research state".into());
        }
        state.valid=false;let started=std::time::Instant::now();
        let unit_bytes=state.regret.len().checked_mul(8).ok_or("unit budget overflow")?;
        let reserve=(unit_bytes as u64).div_ceil(1_000_000);
        let engine_budget=budget_mb.checked_sub(reserve).filter(|&v|v>0).ok_or("insufficient unit-aware engine budget")?;
        let mut g=gpu::PreflopGpu::new(self,engine_budget)?;
        g.research_set_history_units(&state.regret,&state.average,unit_bytes)?;
        let start_age=self.iteration;let stop=self.stop_flag.clone();
        for _ in 0..iterations {
            if !g.try_iterate(self,stop.as_deref())? {return Err("fixed-unit continuation interrupted; discard research copy".into());}
        }
        let (gaps,evs)=g.gaps_and_evs()?;g.sync_to_cpu(self)?;
        if self.stop_requested() || gaps.iter().chain(&evs).any(|x|!x.is_finite()) {return Err("invalid fixed-unit result; discard research copy".into());}
        state.expected=self.fixed_unit_fingerprint()?;state.age=self.iteration;state.valid=true;
        Ok(json!({"start_global_age":start_age,"end_global_age":self.iteration,"global_gaps":gaps,"global_evs":evs,
            "seconds":started.elapsed().as_secs_f64(),"metadata":state.metadata(),"qualified":false}))
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    fn fixture(eq:Arc<equity::EquityTable>,calibrated:bool)->Box<PreflopSolver> {
        let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],"stack":8,
            "posts":[0,0,0.5,1],"limp":true,"open_raises":[2],"raise_mults":[2],"max_raises":2,
            "add_allin":false,"rake_pct":5,"rake_cap":1,"realization":if calibrated {"calibrated"}else{"raw"}})).unwrap();
        let mut s=Box::new(PreflopSolver::new(cfg,eq).unwrap());s.research_seed_quality_fixture_averages().unwrap();
        s.iteration=17;s.seat_frozen[2]=true;
        let node=s.child(0,1);let mut lock=vec![0.0;s.nodes[node].actions.len()*NUM_CLASSES];lock[..NUM_CLASSES].fill(1.0);
        s.point_locks.insert(node as u32,lock);s
    }

    #[test]
    fn fixed_units_branch_refinement_then_split_continuation() {
        let eq=Arc::new(equity::EquityTable::build(8));let paths=vec![vec![1],vec![2]];
        for calibrated in [false,true] {
            let mut outcomes=Vec::new();
            for split in [false,true] {
                let mut s=fixture(eq.clone(),calibrated);let before=s.arena_snapshot();let locks=s.point_locks.clone();
                let plans:Vec<_>=paths.iter().map(|p|s.research_refinement_plan(p).unwrap()).collect();
                let (mut state,_)=s.research_refine_with_fixed_units_gpu(&paths,3,512).unwrap();
                let after=s.arena_snapshot();assert_ne!(before,after);assert_eq!(s.iteration,17);
                let mut owned=std::collections::HashSet::new();
                for (plan,b) in plans.iter().zip(&state.branches) {
                    assert_eq!(b["reference_masses_f64"],plan["prefix_mass_by_seat"]);
                    let masses:Vec<f32>=b["reference_masses_f32"].as_array().unwrap().iter().map(|x|x.as_f64().unwrap() as f32).collect();
                    for value in plan["learning_node_indices"].as_array().unwrap() {
                        let i=value.as_u64().unwrap() as usize;assert!(owned.insert(i));let actor=s.nodes[i].actor as usize;
                        let factor:f32=(0..s.n).filter(|&q|q!=actor).map(|q|masses[q]).product();
                        assert_eq!(state.regret[i],factor);assert_eq!(state.average[i],masses[actor]);
                    }
                }
                for (i,nd) in s.nodes.iter().enumerate() {if !owned.contains(&i) {
                    assert_eq!(state.regret[i],1.0);assert_eq!(state.average[i],1.0);
                    for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {
                        assert_eq!(before.0[ix],after.0[ix]);assert_eq!(before.1[ix],after.1[ix]);
                    }
                }}
                let initial_units=unit_checksum(&state.regret,&state.average);
                let result=if split {
                    s.research_continue_fixed_units_gpu(&mut state,1,512).unwrap();
                    s.research_continue_fixed_units_gpu(&mut state,1,512).unwrap()
                } else {s.research_continue_fixed_units_gpu(&mut state,2,512).unwrap()};
                assert_eq!(state.age,19);assert_eq!(s.iteration,19);assert!(state.valid);
                assert_eq!(initial_units,unit_checksum(&state.regret,&state.average));assert_eq!(s.point_locks,locks);
                let mut fresh=gpu::PreflopGpu::new(&s,512).unwrap();let evaluation=fresh.gaps_and_evs().unwrap();
                assert_eq!(result["global_gaps"],json!(evaluation.0));assert_eq!(result["global_evs"],json!(evaluation.1));
                outcomes.push((s.arena_snapshot(),evaluation));
            }
            assert_eq!(outcomes[0],outcomes[1]);
            println!("FIXED_UNIT_BRANCH {}",json!({"calibrated":calibrated,"branches":2,"local_age":3,
                "start_global_age":17,"end_global_age":19,"split_continuation_exact":true,"ownership_and_factors_verified":true,
                "outside_copyback_unchanged":true,"units_retained":true,"native_evaluation_equal":true,"qualified":false}));
        }
    }

    #[test]
    fn fixed_units_branch_rejects_mismatch_and_poisoned_state() {
        let eq=Arc::new(equity::EquityTable::build(8));let mut s=fixture(eq.clone(),false);let original=s.arena_snapshot();
        for paths in [vec![],vec![vec![]],vec![vec![1],vec![1]],vec![vec![1],vec![1,0]],vec![vec![99]]] {
            assert!(s.research_refine_with_fixed_units_gpu(&paths,2,512).is_err());assert_eq!(s.arena_snapshot(),original);
        }
        let (mut state,_)=s.research_refine_with_fixed_units_gpu(&[vec![1]],2,512).unwrap();let snapshot=s.arena_snapshot();
        let mut other=fixture(eq,false);assert!(other.research_continue_fixed_units_gpu(&mut state,1,512).is_err());assert!(state.valid);
        let old=s.iteration;s.iteration+=1;assert!(s.research_continue_fixed_units_gpu(&mut state,1,512).is_err());s.iteration=old;
        let rake=s.cfg.rake_pct;s.cfg.rake_pct+=1.0;assert!(s.research_continue_fixed_units_gpu(&mut state,1,512).is_err());s.cfg.rake_pct=rake;
        unsafe {s.regrets.slice_mut()[0]+=1.0;}assert!(s.research_continue_fixed_units_gpu(&mut state,1,512).is_err());
        unsafe {s.regrets.slice_mut()[0]=snapshot.0[0];}
        let child=s.children[0];s.children[0]=0;assert!(s.research_continue_fixed_units_gpu(&mut state,1,512).is_err());s.children[0]=child;
        let flag=Arc::new(AtomicBool::new(true));s.stop_flag=Some(flag.clone());
        assert!(s.research_continue_fixed_units_gpu(&mut state,1,512).is_err());flag.store(false,Ordering::Relaxed);
        assert!(s.research_continue_fixed_units_gpu(&mut state,1,0).is_err());assert!(!state.valid);
        assert_eq!(s.arena_snapshot(),snapshot);assert!(s.research_continue_fixed_units_gpu(&mut state,1,512).is_err());
        println!("FIXED_UNIT_REJECTION {}",json!({"overlap_rejected_before_mutation":true,"changed_state_rejected":true,
            "other_owner_rejected":true,"cancellation_rejected":true,"device_admission_failure_poisons":true,
            "invalid_continuation_preserved_histories":true,"persistent_resume_supported":false}));
    }
}
