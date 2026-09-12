//! Bounded-memory pair-outcome control variate. Offline research only.
use super::*;
use crate::preflop::multiway::{CoupledDeck,SAMPLES};

pub(super) struct PairControl {
    matrix:CudaSlice<f32>,
    means:CudaSlice<f32>,
    project:CudaFunction,
    correct:CudaFunction,
    bytes:usize,
    pub(super) learning:bool,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{convergence_research::Experiment,equity::{EquityTable,class_parts},PreflopConfig};
    use serde_json::json;

    fn fixture(n:usize,calibrated:bool,push_fold:bool)->PreflopSolver {
        let positions=["UTG","UTG1","MP","HJ","CO","BTN","SB","BB"][8-n..].to_vec();
        let mut posts=vec![0.0;n];posts[n-2]=0.5;posts[n-1]=1.0;
        let cfg:PreflopConfig=serde_json::from_value(json!({"positions":positions,"posts":posts,"stack":5,
            "limp":!push_fold,"open_raises":if push_fold {vec![]} else {vec![2.0]},"raise_mults":[],
            "max_raises":1,"add_allin":push_fold,"rake_pct":5,"rake_cap":1,
            "realization":if calibrated {"calibrated"} else {"raw"}})).unwrap();
        let mut s=PreflopSolver::new(cfg,Arc::new(EquityTable::build(8))).unwrap();
        s.research_seed_quality_fixture_averages().unwrap();
        if calibrated {assert!(s.fit.is_some());}
        s
    }

    fn engine(s:&PreflopSolver,samples:u32)->PreflopGpu {
        let mut g=PreflopGpu::new(s,1024).unwrap();
        g.configure_research(Experiment::new("dcfr",samples,1000,42).unwrap()).unwrap();
        assert!(g.enable_research_pair_control(0).is_err());assert!(g.research_pair_control.is_none());
        g.enable_research_pair_control(1024).unwrap();g
    }

    fn union_layout(g:&mut PreflopGpu) {
        g.use_mw_compact=0;
        g.d_mw_cdf=g.stream.alloc_zeros::<f32>(g.mw_union_slots as usize*g.mw_batch as usize*(NUM_CLASSES+1)).unwrap();
        g.d_mw_normalized=g.stream.alloc_zeros::<f32>(g.mw_union_slots as usize*NUM_CLASSES).unwrap();
    }

    #[test]
    fn pair_control_matrix_matches_canonical_pair_outcomes() {
        let matrix=pair_matrix();let deck=CoupledDeck::shared();
        for h in 0..NUM_CLASSES {
            assert_eq!(matrix[h*NUM_CLASSES+h],0.5);
            for k in 0..NUM_CLASSES {assert_eq!(matrix[k*NUM_CLASSES+h]+matrix[h*NUM_CLASSES+k],1.0);}
        }
        let mut weights:Vec<f64>=(0..NUM_CLASSES).map(|h|(1+(h*37)%53) as f64).collect();
        let total:f64=weights.iter().sum();for w in &mut weights {*w/=total;}
        for h in [0,13,84,156,168] {
            let projected:f64=weights.iter().enumerate().map(|(k,w)|w*matrix[k*NUM_CLASSES+h] as f64).sum();
            let mut direct=0.0;
            for sample in 0..SAMPLES {
                let base=sample*NUM_CLASSES;
                for rank in 0..deck.upper[base+h] as usize {
                    direct+=weights[deck.order[base+rank] as usize]*if rank<(deck.lower[base+h] as usize) {1.0} else {0.5};
                }
            }
            assert!((projected-direct/SAMPLES as f64).abs()<1e-12);
        }
    }

    #[test]
    fn pair_control_full_correction_preserves_payoffs_and_fixed_constraints() {
        for calibrated in [false,true] {for compact in [false,true] {
            let mut s=fixture(4,calibrated,false);s.seat_frozen[2]=true;
            let node=s.child(0,0);let mut lock=vec![0.0;s.nodes[node].actions.len()*NUM_CLASSES];
            lock[..NUM_CLASSES].fill(1.0);s.point_locks.insert(node as u32,lock);
            let before=s.arena_snapshot();let mut g=engine(&s,1024);
            if !compact {union_layout(&mut g);}
            assert!(g.enable_research_pair_control(1024).is_err());
            assert!(g.enable_research_normalized_regret().is_err());
            assert!(g.enable_research_control_variate(1,100).is_err());
            for p in 0..s.n {
                g.research_tables(true).unwrap();g.down(1,-1).unwrap();
                g.research_pair_control.as_mut().unwrap().learning=false;
                g.terminals_masked(p as i32,0).unwrap();let baseline=g.stream.clone_dtoh(&g.d_val).unwrap();
                g.research_pair_control.as_mut().unwrap().learning=true;
                g.terminals_masked(p as i32,0).unwrap();let corrected=g.stream.clone_dtoh(&g.d_val).unwrap();
                assert!(baseline.iter().zip(&corrected).all(|(a,b)|b.is_finite() && (a-b).abs()<0.0002),"full control changed canonical payoff");
            }
            let actual=g.gaps_and_evs().unwrap();assert!(!g.research_pair_control.as_ref().unwrap().learning);
            let expected=s.gaps_and_evs();
            assert!(actual.0.iter().chain(&actual.1).zip(expected.0.iter().chain(&expected.1)).all(|(a,b)|(a-b).abs()<0.005));
            g.sync_to_cpu(&mut s).unwrap();assert_eq!(before,s.arena_snapshot());
        }}
    }

    #[test]
    fn pair_control_capture_matches_eager_and_native_evaluation() {
        for samples in [32,64] {
        let mut records=Vec::new();
        for eager in [false,true] {
            let mut s=fixture(4,false,false);s.seat_frozen[2]=true;
            let mut g=engine(&s,samples);
            for _ in 0..3 {
                if eager {g.warmed=false;for graph in &mut g.learning_graphs {*graph=None;}}
                g.iterate(&mut s).unwrap();
            }
            assert!(g.enable_research_pair_control(1024).is_err());
            let actual=g.gaps_and_evs().unwrap();g.sync_to_cpu(&mut s).unwrap();
            let expected=s.gaps_and_evs();
            assert!(actual.0.iter().chain(&actual.1).zip(expected.0.iter().chain(&expected.1)).all(|(a,b)|(a-b).abs()<0.005));
            records.push((s.arena_snapshot(),actual));
        }
        assert_eq!(records[0],records[1]);
        }
    }

    fn terminal_engine(n:usize,family:usize)->(PreflopSolver,PreflopGpu,usize,Vec<f32>) {
        let s=fixture(n,false,true);let mut g=engine(&s,64);
        let target=s.nodes.iter().position(|nd|nd.kind==KIND_POT_SHARE && nd.live.count_ones() as usize==n).unwrap();
        g.d_mw_terms=g.stream.clone_htod(&[target as u32]).unwrap();g.mw_nterms=1;
        g.down(1,-1).unwrap();
        let sources=g.stream.clone_dtoh(&g.d_reach_src).unwrap();
        let mut reach=g.stream.clone_dtoh(&g.d_reach).unwrap();
        for q in 0..n {
            let mut weights:Vec<f32>=(0..NUM_CLASSES).map(|h| {
                let (hi,lo,suited)=class_parts(h);
                let factor=match family {
                    0=>1.0,
                    1=>if hi==lo {10.0} else if suited {1.0} else {0.1},
                    _=>if (hi>=10 && lo>=8) || (q%2==0 && hi==lo) {8.0} else {0.05},
                };
                class_prob(h)*factor
            }).collect();
            let sum:f64=weights.iter().map(|&x|x as f64).sum();for w in &mut weights {*w=(*w as f64/sum) as f32;}
            let start=sources[target*n+q] as usize*NUM_CLASSES;
            reach[start..start+NUM_CLASSES].copy_from_slice(&weights);
        }
        set_reach(&mut g,&reach);
        (s,g,target,reach)
    }

    fn set_reach(g:&mut PreflopGpu,reach:&[f32]) {
        g.stream.memcpy_htod(reach,&mut g.d_reach).unwrap();
        unsafe {g.stream.launch_builder(&g.f_reach_mass).arg(&g.d_reach).arg(&mut g.d_reach_mass)
            .launch(LaunchConfig{block_dim:(128,1,1),..PreflopGpu::cfg((reach.len()/NUM_CLASSES) as u32)}).unwrap();}
    }

    fn terminal_values(g:&mut PreflopGpu,target:usize)->Vec<f32> {
        let slot=g.stream.clone_dtoh(&g.d_val_slot).unwrap()[target] as usize;
        g.stream.clone_dtoh(&g.d_val.slice(slot*NUM_CLASSES..(slot+1)*NUM_CLASSES)).unwrap()
    }

    #[test]
    fn pair_control_zero_reach_and_reactivation_refresh_means() {
        let (s,mut g,target,reach)=terminal_engine(4,2);
        let sources=g.stream.clone_dtoh(&g.d_reach_src).unwrap();
        let start=sources[target*s.n+1] as usize*NUM_CLASSES;
        let mut zero=reach.clone();zero[start..start+NUM_CLASSES].fill(0.0);
        let len=g.research_pair_control.as_ref().unwrap().means.len();
        g.stream.memcpy_htod(&vec![f32::NAN;len],&mut g.research_pair_control.as_mut().unwrap().means).unwrap();
        set_reach(&mut g,&zero);g.research_tables(true).unwrap();g.multiway_terminals(0,1).unwrap();
        assert!(terminal_values(&mut g,target).iter().all(|&v|v==0.0));
        set_reach(&mut g,&reach);g.multiway_terminals(0,1).unwrap();
        assert!(terminal_values(&mut g,target).iter().all(|v|v.is_finite()));
        let slots=g.stream.clone_dtoh(&g.d_mw_slots).unwrap();let masses=g.stream.clone_dtoh(&g.d_reach_mass).unwrap();
        let means=g.stream.clone_dtoh(&g.research_pair_control.as_ref().unwrap().means).unwrap();let matrix=pair_matrix();
        for q in 1..s.n {
            let block=sources[target*s.n+q] as usize;let slot=slots[block] as usize;
            for h in 0..NUM_CLASSES {
                let expected:f64=(0..NUM_CLASSES).map(|k|reach[block*NUM_CLASSES+k] as f64/masses[block] as f64*matrix[k*NUM_CLASSES+h] as f64).sum();
                assert!((means[slot*NUM_CLASSES+h] as f64-expected).abs()<2e-6);
            }
        }
    }

    #[test]
    fn pair_control_variance_screen() {
        variance_screen(64);
    }

    #[test]
    fn pair_control_variance_screen_32() {
        variance_screen(32);
    }

    fn variance_screen(samples:u32) {
        for n in [3,4,6,8] {for family in 0..3 {
            let (_,mut g,target,_)=terminal_engine(n,family);
            g.research.as_mut().unwrap().samples=samples;
            g.research_tables(false).unwrap();g.multiway_terminals(0,1).unwrap();
            let full=terminal_values(&mut g,target);
            let mut sums=vec![[0f64;2];NUM_CLASSES];let mut squares=sums.clone();
            for offset in 0..SAMPLES {
                g.research.as_mut().unwrap().offset=offset;g.research_tables_select(true,false).unwrap();
                for corrected in [false,true] {
                    g.research_pair_control.as_mut().unwrap().learning=corrected;
                    g.multiway_terminals(0,1).unwrap();let values=terminal_values(&mut g,target);
                    for h in 0..NUM_CLASSES {
                        assert!(values[h].is_finite());let error=values[h] as f64-full[h] as f64;let i=corrected as usize;
                        sums[h][i]+=error;squares[h][i]+=error*error;
                    }
                }
            }
            let mut hands=Vec::new();let mut pooled=[0.0;2];
            for h in 0..NUM_CLASSES {
                let bias=[sums[h][0]/SAMPLES as f64,sums[h][1]/SAMPLES as f64];
                assert!(bias.iter().all(|b|b.abs()<0.0002),"cyclic mean bias exceeds tolerance: {bias:?}");
                let variance=[squares[h][0]/SAMPLES as f64-bias[0]*bias[0],squares[h][1]/SAMPLES as f64-bias[1]*bias[1]];
                for i in 0..2 {pooled[i]+=class_prob(h) as f64*variance[i];}
                hands.push(json!({"class_index":h,"bias_bb":bias,"variance_bb2":variance,
                    "ratio":if variance[0]>1e-10 {Some(variance[1]/variance[0])} else {None}}));
            }
            println!("PAIR_VARIANCE {}",json!({"players":n,"family":family,"samples":samples,"offsets":SAMPLES,
                "extra_bytes":g.research_pair_control_bytes(),"pooled_variance":pooled,"ratio":pooled[1]/pooled[0],"hands":hands}));
        }}
    }
}

fn pair_matrix()->Arc<Vec<f32>> {
    static MATRIX:std::sync::OnceLock<Arc<Vec<f32>>>=std::sync::OnceLock::new();
    MATRIX.get_or_init(|| {
        let deck=CoupledDeck::shared();let mut counts=vec![0u32;NUM_CLASSES*NUM_CLASSES];
        for particle in 0..SAMPLES {
            let base=particle*NUM_CLASSES;
            for rank in 0..NUM_CLASSES {
                let k=deck.order[base+rank] as usize;
                for h in 0..NUM_CLASSES {
                    counts[k*NUM_CLASSES+h]+=if rank<(deck.lower[base+h] as usize) {2}
                        else if rank<(deck.upper[base+h] as usize) {1} else {0};
                }
            }
        }
        Arc::new(counts.into_iter().map(|n|n as f32/(2*SAMPLES) as f32).collect())
    }).clone()
}

impl PreflopGpu {
    /// Cap covers the matrix and union-slot means; no per-terminal reference
    /// values are allocated. Unsupported combined modes are refused up front.
    pub fn enable_research_pair_control(&mut self,extra_limit_mb:usize)->Result<usize,String> {
        if self.warmed || self.eval_warmed || self.research.is_none() || self.use_multiway==0
            || !self.use_mw_prepared || !self.use_mw_normalized || self.research_cv.is_some()
            || self.research_normalized_regret.is_some() || self.research_learning_mask
            || self.research_root_ranges.is_some() || self.research_pair_control.is_some() {
            return Err("pair control requires a fresh canonical prepared research engine".into());
        }
        let len=(self.mw_union_slots as usize).checked_mul(NUM_CLASSES).ok_or("pair mean size overflow")?;
        let bytes=len.checked_add(NUM_CLASSES*NUM_CLASSES).and_then(|x|x.checked_mul(4)).ok_or("pair storage overflow")?;
        if bytes>extra_limit_mb.min(1024).saturating_mul(1024*1024) {return Err(format!("pair control needs {bytes} extra bytes; explicit cap exceeded"));}
        let module=self._ctx.load_module(cudarc::nvrtc::compile_ptx(include_str!("pair_control.cu")).map_err(e)?).map_err(e)?;
        let control=PairControl{matrix:self.stream.clone_htod(pair_matrix().as_slice()).map_err(e)?,
            means:self.stream.alloc_zeros::<f32>(len).map_err(e)?,project:module.load_function("pair_project").map_err(e)?,
            correct:module.load_function("pair_correct").map_err(e)?,bytes,learning:false};
        self.research_pair_control=Some(control);Ok(bytes)
    }

    pub fn research_pair_control_bytes(&self)->Option<usize> {self.research_pair_control.as_ref().map(|c|c.bytes)}

    pub(super) fn research_pair_project(&mut self,p:i32,gate:i32)->Result<(),String> {
        let Some(control)=&mut self.research_pair_control else {return Ok(())};
        if !control.learning {return Ok(());}
        let (start,count)=self.mw_spans[p as usize];if count==0 {return Ok(());}
        unsafe {
            self.stream.launch_builder(&control.project).arg(&self.d_mw_work).arg(&start).arg(&self.d_mw_blocks)
                .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)
                .arg(&control.matrix).arg(&mut control.means)
                .launch(LaunchConfig{grid_dim:(count,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;
        }
        Ok(())
    }

    pub(super) fn research_pair_correct(&mut self,p:i32,start:u32,count:u32,samples:u32)->Result<(),String> {
        let Some(control)=&self.research_pair_control else {return Ok(())};
        if !control.learning {return Ok(());}
        unsafe {
            self.stream.launch_builder(&control.correct).arg(&self.d_mw_terms).arg(&p).arg(&self.np)
                .arg(&self.d_live).arg(&self.d_pots).arg(&self.d_reach_src).arg(&self.d_mw_prob)
                .arg(&self.d_mw_slots).arg(&self.d_mw_compact).arg(&self.mw_union_slots).arg(&self.use_mw_compact)
                .arg(&self.d_mw_cdf).arg(&self.d_mw_lower).arg(&self.d_mw_upper).arg(&control.means)
                .arg(&start).arg(&count).arg(&self.mw_batch).arg(&samples).arg(&self.d_val_slot).arg(&mut self.d_val)
                .launch(LaunchConfig{grid_dim:(self.mw_nterms,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;
        }
        Ok(())
    }
}
