//! Offline predictive RM+: persistent compressed counterfactual terminal history.
use super::*;
use serde_json::{json, Value};

#[cfg(test)]
#[path = "predictive_tests.rs"]
mod tests;

struct StoragePlan {
    offsets: Vec<u32>,
    floats: usize,
    vectors: usize,
    scalars: usize,
    policy: usize,
}

impl StoragePlan {
    fn build(kind: &[i32], live: &[i32], terms: &[u32], np: usize, policy: usize) -> Result<Self,String> {
        if kind.len()!=live.len() || !(2..=9).contains(&np) { return Err("invalid prediction geometry".into()); }
        let count=terms.len().checked_mul(np).ok_or("prediction map overflow")?;
        let mut plan=Self { offsets:Vec::with_capacity(count),floats:0,vectors:0,scalars:0,policy };
        for p in 0..np { for &nd in terms {
            let nd=nd as usize;
            if nd>=kind.len() || ![1,2].contains(&kind[nd]) || live[nd]<0 || live[nd]>>np != 0 {
                return Err("invalid prediction terminal".into());
            }
            plan.offsets.push(u32::try_from(plan.floats).map_err(|_|"prediction offset overflow")?);
            let vector=kind[nd]==2 && (live[nd]>>p)&1 != 0;
            if vector { plan.vectors+=1; } else { plan.scalars+=1; }
            plan.floats=plan.floats.checked_add(if vector {NUM_CLASSES} else {1}).ok_or("prediction history overflow")?;
        }}
        plan.bytes()?;
        Ok(plan)
    }
    fn bytes(&self)->Result<usize,String> {
        self.floats.checked_add(self.policy).and_then(|v|v.checked_add(self.offsets.len()))
            .and_then(|v|v.checked_mul(4)).ok_or("prediction storage overflow".into())
    }
    fn report(&self)->Result<Value,String> {
        Ok(json!({"vector_terminals":self.vectors,"scalar_terminals":self.scalars,
            "history_floats":self.floats,"history_bytes":self.floats*4,
            "policy_bytes":self.policy*4,"offset_bytes":self.offsets.len()*4,
            "persistent_extra_bytes":self.bytes()?,"cap_bytes":4usize*1024*1024*1024,
            "fits_four_gib":self.bytes()?<=4usize*1024*1024*1024}))
    }
}

pub(super) struct Predictive {
    pub(super) policy: CudaSlice<f32>,
    history: CudaSlice<f32>,
    offsets: CudaSlice<u32>,
    transfer: CudaFunction,
    up: CudaFunction,
    enabled: i32,
}

impl PreflopSolver {
    /// Read-only allocation inventory; does not construct or run a GPU engine.
    pub fn research_prediction_storage(&self)->Result<Value,String> {
        let kind:Vec<i32>=self.nodes.iter().map(|n|n.kind as i32).collect();
        let live:Vec<i32>=self.nodes.iter().map(|n|n.live as i32).collect();
        let terms:Vec<u32>=self.nodes.iter().enumerate().filter(|(_,n)|n.kind!=KIND_ACTION).map(|(i,_)|i as u32).collect();
        let plan=StoragePlan::build(&kind,&live,&terms,self.n,self.arena_len)?;
        Ok(json!({"nodes":self.nodes.len(),"players":self.n,"terminals":terms.len(),
            "model":self.multiway_equity_model(),"storage":plan.report()?,"read_only":true}))
    }
}

impl PreflopGpu {
    /// Explicit offline admission, before any learning/evaluation graph.
    pub fn enable_research_predictive(&mut self, enabled:bool, extra_limit_mb:usize)->Result<Value,String> {
        if !self.research_rm_plus_fresh || self.warmed || self.eval_warmed || self.research.is_none()
            || self.research_behavioral.is_some() || self.research_predictive.is_some() || self.research_rm_plus.is_some()
            || self.research_cv.is_some() || self.research_normalized_regret.is_some()
            || self.research_learning_mask || self.research_root_ranges.is_some()
            || self.research_exploration.is_some() || self.research_average_opponents.is_some()
            || self.research_history_units.is_some() {
            return Err("predictive RM+ requires fresh configured native-payoff zero learning histories".into());
        }
        let kind=self.stream.clone_dtoh(&self.d_kind).map_err(e)?;
        let live=self.stream.clone_dtoh(&self.d_live).map_err(e)?;
        let terms=self.stream.clone_dtoh(&self.d_terms).map_err(e)?;
        let plan=StoragePlan::build(&kind,&live,&terms,self.np as usize,self.arena_len)?;
        if plan.bytes()?>extra_limit_mb.min(4096).saturating_mul(1024*1024) {
            return Err(format!("prediction needs {} extra bytes; explicit cap exceeded",plan.bytes()?));
        }
        let source=[include_str!("../kernels.cu"),include_str!("predictive.cu")].join("\n");
        let module=self._ctx.load_module(cudarc::nvrtc::compile_ptx(source).map_err(e)?).map_err(e)?;
        let state=Predictive {
            policy:self.stream.alloc_zeros::<f32>(plan.policy).map_err(e)?,
            history:self.stream.alloc_zeros::<f32>(plan.floats).map_err(e)?,
            offsets:self.stream.clone_htod(&plan.offsets).map_err(e)?,
            transfer:module.load_function("pf_prediction_transfer").map_err(e)?,
            up:module.load_function("pf_prediction_up").map_err(e)?, enabled:enabled as i32,
        };
        assert_eq!(4*(state.policy.len()+state.history.len()+state.offsets.len()),plan.bytes()?);
        self.research_predictive=Some(state);
        plan.report()
    }

    fn predictive_transfer(&mut self,p:i32,save:bool)->Result<(),String> {
        let state=self.research_predictive.as_mut().ok_or("missing predictive state")?;
        let count=self.nterms as i32; let save=save as i32;
        unsafe {
            self.stream.launch_builder(&state.transfer).arg(&self.d_terms).arg(&count).arg(&p)
                .arg(&self.d_kind).arg(&self.d_live).arg(&self.d_val_slot).arg(&state.offsets)
                .arg(&mut state.history).arg(&mut self.d_val).arg(&save).arg(&state.enabled)
                .launch(Self::cfg(self.nterms)).map_err(e)?;
        }
        Ok(())
    }

    fn predictive_up(&mut self,p:i32,predict:bool)->Result<(),String> {
        let state=self.research_predictive.as_mut().ok_or("missing predictive state")?;
        let predict=predict as i32;
        for &(start,count) in self.spans.iter().rev() {
            if count==0 {continue;}
            let (start,count)=(start as i32,count as i32);
            unsafe {
                self.stream.launch_builder(&state.up).arg(&self.d_act_nodes).arg(&start).arg(&count)
                    .arg(&p).arg(&self.np).arg(&predict).arg(&self.d_actor).arg(&self.d_na)
                    .arg(&self.d_off).arg(&self.d_cstart).arg(&self.d_children).arg(&self.d_src)
                    .arg(&self.d_foff).arg(&self.d_forced).arg(&self.d_reach_src).arg(&self.d_reach)
                    .arg(&mut self.d_regrets).arg(&mut self.d_strat).arg(&mut state.policy)
                    .arg(&self.d_val_slot).arg(&mut self.d_val).launch(Self::cfg(count as u32)).map_err(e)?;
            }
        }
        Ok(())
    }

    pub(super) fn research_predictive_sweep(&mut self,p:i32,mode:i32)->Result<bool,String> {
        if mode!=0 || self.research_predictive.is_none() {return Ok(false);}
        self.predictive_transfer(p,false)?;
        self.predictive_up(p,true)?;
        self.down(0,p)?;
        self.terminals(p)?;
        self.predictive_transfer(p,true)?;
        self.predictive_up(p,false)?;
        Ok(true)
    }
}
