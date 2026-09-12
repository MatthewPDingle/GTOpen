//! Research-only per-decision regret update normalization. No payoff change.
use super::*;

impl PreflopGpu {
    pub fn enable_research_normalized_regret(&mut self)->Result<(),String> {
        if self.warmed || self.eval_warmed || self.research_cv.is_some() || self.research_learning_mask
            || self.research_root_ranges.is_some() || self.research_normalized_regret.is_some() {
            return Err("normalized-regret experiment requires a fresh full-tree engine".into());
        }
        let source=[include_str!("../kernels.cu"),include_str!("normalized_regret.cu")].join("\n");
        let module=self._ctx.load_module(cudarc::nvrtc::compile_ptx(source).map_err(e)?).map_err(e)?;
        self.research_normalized_regret=Some(module.load_function("pf_up_normalized_regret").map_err(e)?);
        Ok(())
    }

    pub(super) fn research_normalized_up(&mut self,p:i32,li:usize)->Result<bool,String> {
        let Some(function)=&self.research_normalized_regret else {return Ok(false)};
        let (start,count)=self.spans[li];if count==0 {return Ok(true);}
        let (start,count)=(start as i32,count as i32);
        unsafe {
            self.stream.launch_builder(function).arg(&self.d_act_nodes).arg(&start).arg(&count)
                .arg(&p).arg(&self.np).arg(&self.d_actor).arg(&self.d_na).arg(&self.d_off)
                .arg(&self.d_cstart).arg(&self.d_children).arg(&self.d_src).arg(&self.d_foff)
                .arg(&self.d_forced).arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass)
                .arg(&mut self.d_regrets).arg(&mut self.d_strat).arg(&self.d_val_slot).arg(&mut self.d_val)
                .launch(Self::cfg(count as u32)).map_err(e)?;
        }
        Ok(true)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{equity::EquityTable,PreflopConfig};

    fn fixture()->PreflopSolver {
        let eq=Arc::new(EquityTable::build(8));
        let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({"positions":["CO","BTN","SB","BB"],
            "posts":[0,0,0.5,1],"stack":5,"limp":true,"open_raises":[2],"raise_mults":[3],
            "max_raises":1,"add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"})).unwrap();
        let mut s=PreflopSolver::new(cfg,eq).unwrap();s.research_seed_quality_fixture_averages().unwrap();
        s.seat_frozen[2]=true;
        let mut lock=vec![0.0;s.nodes[0].actions.len()*NUM_CLASSES];lock[..NUM_CLASSES].fill(1.0);
        s.point_locks.insert(0,lock);
        s
    }

    #[test]
    fn normalized_regret_matches_scaled_increments_and_preserves_values() {
        let s=fixture();let mut base=PreflopGpu::new(&s,512).unwrap();
        let mut candidate=PreflopGpu::new(&s,512).unwrap();
        candidate.enable_research_normalized_regret().unwrap();
        assert!(candidate.enable_research_normalized_regret().is_err());
        let p=1;
        let before=base.stream.clone_dtoh(&base.d_regrets).unwrap();
        base.down(0,p).unwrap();base.terminals_masked(p,0).unwrap();base.up(p,0).unwrap();
        candidate.down(0,p).unwrap();candidate.terminals_masked(p,0).unwrap();candidate.up(p,0).unwrap();
        let masses=candidate.stream.clone_dtoh(&candidate.d_reach_mass).unwrap();
        let src=candidate.stream.clone_dtoh(&candidate.d_src).unwrap();
        let reach_src=candidate.stream.clone_dtoh(&candidate.d_reach_src).unwrap();
        let a=base.stream.clone_dtoh(&base.d_regrets).unwrap();
        let b=candidate.stream.clone_dtoh(&candidate.d_regrets).unwrap();
        let mut zero_mass=0;let mut scaled=0;
        for (i,nd) in s.nodes.iter().enumerate() {
            let mut mass=1f32;
            for q in 0..s.n {if q!=p as usize {mass*=masses[reach_src[i*s.n+q] as usize];}}
            let learning=nd.actor as i32==p && src[i]==0;
            if learning && !nd.actions.is_empty() {if mass==0.0 {zero_mass+=1;} else if mass<0.99 {scaled+=1;}}
            for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {
                if learning {
                    let expected=before[ix]+(a[ix]-before[ix])/mass.max(1e-12);
                    assert!(b[ix].is_finite() && (b[ix]-expected).abs()<=2e-5*(1.0+expected.abs()),"incorrect normalized increment at {i}/{ix}");
                } else {assert_eq!(b[ix],a[ix]);}
            }
        }
        assert!(zero_mass>0 && scaled>0);
        assert_eq!(base.stream.clone_dtoh(&base.d_strat).unwrap(),candidate.stream.clone_dtoh(&candidate.d_strat).unwrap());
        let av=base.stream.clone_dtoh(&base.d_val).unwrap();let bv=candidate.stream.clone_dtoh(&candidate.d_val).unwrap();
        assert!(av.iter().zip(&bv).all(|(a,b)|(a-b).abs()<0.0002));
    }

    #[test]
    fn normalized_regret_capture_matches_eager_and_full_checks_stay_native() {
        let mut records=Vec::new();
        for eager in [false,true] {
            let mut s=fixture();let mut gpu=PreflopGpu::new(&s,512).unwrap();
            gpu.enable_research_normalized_regret().unwrap();
            for _ in 0..3 {
                if eager {gpu.warmed=false;for graph in &mut gpu.learning_graphs {*graph=None;}}
                gpu.iterate(&mut s).unwrap();
            }
            assert!(gpu.enable_research_normalized_regret().is_err());
            let (gaps,evs)=gpu.gaps_and_evs().unwrap();gpu.sync_to_cpu(&mut s).unwrap();
            let cpu=s.gaps_and_evs();
            assert!(gaps.iter().chain(&evs).zip(cpu.0.iter().chain(&cpu.1)).all(|(a,b)|(a-b).abs()<0.005));
            records.push((s.arena_snapshot(),gaps,evs));
        }
        assert_eq!(records[0],records[1]);
    }
}
