//! Offline opponent-reach exploration; native evaluation always bypasses it.
use super::*;

pub(super) struct Exploration {
    function:CudaFunction,
    epsilon:CudaSlice<f32>,
    initial:f32,
    decay:u32,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{PreflopConfig,equity::EquityTable,convergence_research::Experiment};

    fn fixture()->PreflopSolver {
        let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({"positions":["CO","BTN","SB","BB"],
            "posts":[0,0,0.5,1],"stack":5,"limp":true,"open_raises":[2],"raise_mults":[],"max_raises":1,
            "add_allin":false,"rake_pct":5,"rake_cap":1,"realization":"raw"})).unwrap();
        let mut s=PreflopSolver::new(cfg,Arc::new(EquityTable::build(8))).unwrap();
        s.research_seed_quality_fixture_averages().unwrap();s.seat_frozen[2]=true;
        let node=s.child(0,1);let mut lock=vec![0.0;s.nodes[node].actions.len()*NUM_CLASSES];
        lock[..NUM_CLASSES].fill(1.0);s.point_locks.insert(node as u32,lock);s
    }

    #[test]
    fn exploration_reach_matches_independent_recurrence_and_zero_is_native() {
        let s=fixture();let mut base=PreflopGpu::new(&s,512).unwrap();let mut g=PreflopGpu::new(&s,512).unwrap();
        g.enable_research_opponent_exploration(0.02,2).unwrap();
        assert!(g.enable_research_opponent_exploration(0.02,2).is_err());
        assert!(g.enable_research_normalized_regret().is_err());
        let sources=g.stream.clone_dtoh(&g.d_src).unwrap();
        let blocks=g.stream.clone_dtoh(&g.d_reach_src).unwrap();
        let offsets=g.stream.clone_dtoh(&g.d_foff).unwrap();let forced=g.stream.clone_dtoh(&g.d_forced).unwrap();
        let regrets=g.stream.clone_dtoh(&g.d_regrets).unwrap();let average=g.stream.clone_dtoh(&g.d_strat).unwrap();
        let nodes=g.stream.clone_dtoh(&g.d_act_nodes).unwrap();
        let before=s.arena_snapshot();
        for p in 0..s.n {
            g.research_exploration_schedule(0).unwrap();g.down(0,p as i32).unwrap();
            let actual=g.stream.clone_dtoh(&g.d_reach).unwrap();let mut expected=vec![0f32;actual.len()];
            for q in 0..s.n {for h in 0..NUM_CLASSES {expected[q*NUM_CLASSES+h]=class_prob(h);}}
            let mut mixed=0;let mut fixed=0;let mut own=0;let mut impossible=0;
            for &(start,count) in &g.spans {for &idx in &nodes[start as usize..(start+count) as usize] {
                let nd=&s.nodes[idx as usize];let actor=nd.actor as usize;let na=nd.actions.len();
                for h in 0..NUM_CLASSES {
                    let mut sig=vec![0f32;na];
                    if sources[idx as usize]==2 {
                        for a in 0..na {sig[a]=forced[offsets[idx as usize] as usize+a*NUM_CLASSES+h];}
                    } else {
                        for a in 0..na {
                            let v=if sources[idx as usize]==1 {average[nd.data_off+a*NUM_CLASSES+h]} else {regrets[nd.data_off+a*NUM_CLASSES+h].max(0.0)};
                            sig[a]=v;
                        }
                        let sum:f32=sig.iter().sum();for v in &mut sig {*v=if sum>1e-12 {*v/sum} else {1.0/na as f32};}
                    }
                    let parent=expected[blocks[idx as usize*s.n+actor] as usize*NUM_CLASSES+h];
                    for a in 0..na {
                        let child=s.child(idx as usize,a);let at=blocks[child*s.n+actor] as usize*NUM_CLASSES+h;
                        let raw=parent*sig[a];
                        expected[at]=if actor!=p && sources[idx as usize]==0 {(1.0-0.02)*raw+(0.02/na as f32)*parent} else {raw};
                        if sources[idx as usize]!=0 {fixed+=1;if expected[at]==0.0 {impossible+=1;}}
                        else if actor==p {own+=1;} else {mixed+=1;}
                    }
                }
            }}
            assert!(mixed>0 && fixed>0 && impossible>0);if p!=2 {assert!(own>0);}
            assert!(actual.iter().zip(&expected).all(|(a,b)|a.is_finite() && (a-b).abs()<2e-6),"reach mismatch for traverser {p}");
            g.research_exploration_schedule(2).unwrap();g.down(0,p as i32).unwrap();base.down(0,p as i32).unwrap();
            assert_eq!(g.stream.clone_dtoh(&g.d_reach).unwrap(),base.stream.clone_dtoh(&base.d_reach).unwrap());
            // Full evaluation bypasses correction even with a positive scalar.
            g.research_exploration_schedule(0).unwrap();g.down(1,p as i32).unwrap();base.down(1,p as i32).unwrap();
            assert_eq!(g.stream.clone_dtoh(&g.d_reach).unwrap(),base.stream.clone_dtoh(&base.d_reach).unwrap());
        }
        let native=base.gaps_and_evs().unwrap();let evaluated=g.gaps_and_evs().unwrap();assert_eq!(native,evaluated);
        let cpu=s.gaps_and_evs();assert!(cpu.0.iter().chain(&cpu.1).zip(evaluated.0.iter().chain(&evaluated.1)).all(|(a,b)|(a-b).abs()<0.005));
        let mut s=s;g.sync_to_cpu(&mut s).unwrap();assert_eq!(before,s.arena_snapshot());
    }

    #[test]
    fn exploration_capture_decay_and_native_final_check() {
        let mut records=Vec::new();
        for eager in [false,true] {
            let mut s=fixture();let before=s.arena_snapshot();let mut g=PreflopGpu::new(&s,512).unwrap();
            g.configure_research(Experiment::new("gamma15",64,1000,42).unwrap()).unwrap();
            g.enable_research_opponent_exploration(0.02,2).unwrap();
            assert!(g.enable_research_pair_control(1024).is_err());assert!(g.enable_research_control_variate(1,100).is_err());
            for _ in 0..4 {
                if eager {g.warmed=false;for graph in &mut g.learning_graphs {*graph=None;}}
                g.iterate(&mut s).unwrap();
            }
            assert_eq!(g.stream.clone_dtoh(&g.research_exploration.as_ref().unwrap().epsilon).unwrap(),vec![0.0]);
            let actual=g.gaps_and_evs().unwrap();g.sync_to_cpu(&mut s).unwrap();
            let cpu=s.gaps_and_evs();assert!(cpu.0.iter().chain(&cpu.1).zip(actual.0.iter().chain(&actual.1)).all(|(a,b)|(a-b).abs()<0.005));
            let after=s.arena_snapshot();
            for nd in &s.nodes {if nd.actor==2 {let end=nd.data_off+nd.actions.len()*NUM_CLASSES;assert_eq!(&before.1[nd.data_off..end],&after.1[nd.data_off..end]);}}
            records.push((after,actual));
        }
        assert_eq!(records[0],records[1]);
    }
}

impl PreflopGpu {
    pub fn enable_research_opponent_exploration(&mut self,initial:f32,decay:u32)->Result<(),String> {
        if self.warmed || self.eval_warmed || self.research_learning_mask || self.research_root_ranges.is_some()
            || self.research_cv.is_some() || self.research_pair_control.is_some() || self.research_normalized_regret.is_some()
            || self.research_exploration.is_some() || !initial.is_finite() || initial<=0.0 || initial>0.05 || decay==0 || decay>1000 {
            return Err("opponent exploration requires a fresh uncombined engine and bounded schedule".into());
        }
        let module=self._ctx.load_module(cudarc::nvrtc::compile_ptx(include_str!("exploration.cu")).map_err(e)?).map_err(e)?;
        self.research_exploration=Some(Exploration{function:module.load_function("explore_opponent_reach").map_err(e)?,
            epsilon:self.stream.clone_htod(&[initial]).map_err(e)?,initial,decay});Ok(())
    }

    pub fn research_exploration_parameters(&self)->Option<(f32,u32)> {
        self.research_exploration.as_ref().map(|r|(r.initial,r.decay))
    }

    pub(super) fn research_exploration_schedule(&mut self,iteration:u32)->Result<(),String> {
        if let Some(r)=&mut self.research_exploration {
            let epsilon=if iteration>=r.decay {0.0} else {r.initial*(1.0-iteration as f32/r.decay as f32)};
            self.stream.memcpy_htod(&[epsilon],&mut r.epsilon).map_err(e)?;
        }
        Ok(())
    }

    pub(super) fn research_explore_reach(&mut self,start:i32,count:i32,p:i32,mode:i32)->Result<(),String> {
        if mode!=0 || p<0 {return Ok(());}
        let Some(r)=&self.research_exploration else {return Ok(());};
        unsafe {
            self.stream.launch_builder(&r.function).arg(&self.d_act_nodes).arg(&start).arg(&count).arg(&p).arg(&self.np)
                .arg(&self.d_actor).arg(&self.d_na).arg(&self.d_cstart).arg(&self.d_children).arg(&self.d_src)
                .arg(&self.d_reach_src).arg(&r.epsilon).arg(&mut self.d_reach).launch(Self::cfg(count as u32)).map_err(e)?;
        }
        Ok(())
    }
}
