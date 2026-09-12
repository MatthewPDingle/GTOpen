//! Numerical identity tests only; no new public continuation or copyback path.
use super::*;
use crate::preflop::{PreflopConfig,equity::EquityTable};
use serde_json::json;

fn fixture(calibrated:bool)->PreflopSolver {
    let cfg:PreflopConfig=serde_json::from_value(json!({"positions":["CO","BTN","SB","BB"],"stack":8,
        "posts":[0,0,0.5,1],"limp":true,"open_raises":[2],"raise_mults":[2],"max_raises":2,
        "add_allin":false,"rake_pct":5,"rake_cap":1,"realization":if calibrated {"calibrated"} else {"raw"}})).unwrap();
    let mut s=PreflopSolver::new(cfg,Arc::new(EquityTable::build(8))).unwrap();
    if calibrated {assert!(s.fit.is_some());}
    s.research_seed_quality_fixture_averages().unwrap();let average=s.arena_snapshot().1;
    unsafe {s.regrets.slice_mut().copy_from_slice(&average);}
    for nd in &s.nodes {for a in 1..nd.actions.len() {for h in 0..NUM_CLASSES {
        if a%2==1 && h%3==0 {unsafe {s.regrets.slice_mut()[nd.data_off+a*NUM_CLASSES+h]*=-1.0;}}
    }}}
    s.seat_frozen[2]=true;
    let node=s.child(0,1);let mut lock=vec![0.0;s.nodes[node].actions.len()*NUM_CLASSES];
    lock[..NUM_CLASSES].fill(1.0);s.point_locks.insert(node as u32,lock);s
}

fn normalized_ranges()->Vec<Vec<f32>> {
    (0..4).map(|q| {
        let mut r:Vec<f32>=(0..NUM_CLASSES).map(|h|class_prob(h)*(1+(h*37+q*11)%53) as f32).collect();
        let sum:f64=r.iter().map(|&v|v as f64).sum();for v in &mut r {*v=(*v as f64/sum) as f32;}r
    }).collect()
}

fn up_level(g:&mut PreflopGpu,p:i32,li:usize) {
    let (start,count)=g.spans[li];if count==0 {return;}
    let (start,count,mode)=(start as i32,count as i32,0i32);
    unsafe {
        g.stream.launch_builder(&g.f_up).arg(&g.d_act_nodes).arg(&start).arg(&count).arg(&p).arg(&g.np).arg(&mode)
            .arg(&g.d_actor).arg(&g.d_na).arg(&g.d_off).arg(&g.d_cstart).arg(&g.d_children).arg(&g.d_src)
            .arg(&g.d_foff).arg(&g.d_forced).arg(&g.d_reach_src).arg(&g.d_reach).arg(&mut g.d_regrets)
            .arg(&mut g.d_strat).arg(&g.d_val_slot).arg(&mut g.d_val).launch(PreflopGpu::cfg(count as u32)).unwrap();
    }
}

#[test]
fn history_units_counterfactual_and_average_scaling() {
    for calibrated in [false,true] {for masses in [[0.03125f32,0.125,0.5,0.25],[0.037f32,0.173,0.61,0.83]] {
        let s=fixture(calibrated);let ranges=normalized_ranges();
        let factors:Vec<f32>=(0..4).map(|p|(0..4).filter(|&q|q!=p).map(|q|masses[q]).product()).collect();
        let (initial_r,initial_s)=s.arena_snapshot();
        let mut local=PreflopGpu::new(&s,512).unwrap();let mut global=PreflopGpu::new(&s,512).unwrap();
        local.research_set_root_ranges(ranges.clone()).unwrap();global.research_set_root_ranges(ranges.clone()).unwrap();
        // Test-only injection of unnormalized incoming ranges models the units
        // at a reached full-game branch. The public setter correctly refuses
        // such ranges; this does not add a public unnormalized-root API.
        let raw:Vec<f32>=ranges.iter().enumerate().flat_map(|(q,r)|r.iter().map(move |&v|v*masses[q])).collect();
        global.stream.memcpy_htod(&raw,&mut global.research_root_ranges.as_mut().unwrap().1).unwrap();
        let source=local.stream.clone_dtoh(&local.d_src).unwrap();
        let nodes=local.stream.clone_dtoh(&local.d_act_nodes).unwrap();
        let slots=local.stream.clone_dtoh(&local.d_val_slot).unwrap();
        let mut scaled_r=initial_r.clone();let mut scaled_s=initial_s.clone();
        for (i,nd) in s.nodes.iter().enumerate() {if source[i]==0 {
            let p=nd.actor as usize;
            for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {scaled_r[ix]*=factors[p];scaled_s[ix]*=masses[p];}
        }}
        let mut value_worst=0.0f64;let mut regret_worst=0.0f64;let mut average_worst=0.0f64;
        let mut action_values=0usize;let mut increments=0usize;let mut folded_leaves=0usize;
        for p in 0..s.n {
            local.stream.memcpy_htod(&initial_r,&mut local.d_regrets).unwrap();local.stream.memcpy_htod(&initial_s,&mut local.d_strat).unwrap();
            global.stream.memcpy_htod(&scaled_r,&mut global.d_regrets).unwrap();global.stream.memcpy_htod(&scaled_s,&mut global.d_strat).unwrap();
            local.down(0,p as i32).unwrap();global.down(0,p as i32).unwrap();
            local.terminals_masked(p as i32,0).unwrap();global.terminals_masked(p as i32,0).unwrap();
            for li in (0..local.spans.len()).rev() {
                // Child values are compared before each parent level consumes
                // them, since action scratch storage is reused across depths.
                let lv=local.stream.clone_dtoh(&local.d_val).unwrap();let gv=global.stream.clone_dtoh(&global.d_val).unwrap();
                let (start,count)=local.spans[li];
                for &node in &nodes[start as usize..(start+count) as usize] {
                    for a in 0..s.nodes[node as usize].actions.len() {
                        let child=s.child(node as usize,a);let offset=slots[child] as usize*NUM_CLASSES;
                        if s.nodes[child].actions.is_empty() && s.nodes[child].live.count_ones()<s.n as u32 {folded_leaves+=1;}
                        for h in 0..NUM_CLASSES {
                            let error=(gv[offset+h] as f64/factors[p] as f64-lv[offset+h] as f64).abs();
                            assert!(error.is_finite() && error<0.0002,"value unit mismatch at {node}/{a}/{h}: {error}");
                            value_worst=value_worst.max(error);action_values+=1;
                        }
                    }
                }
                up_level(&mut local,p as i32,li);up_level(&mut global,p as i32,li);
            }
            let lr=local.stream.clone_dtoh(&local.d_regrets).unwrap();let gr=global.stream.clone_dtoh(&global.d_regrets).unwrap();
            let ls=local.stream.clone_dtoh(&local.d_strat).unwrap();let gs=global.stream.clone_dtoh(&global.d_strat).unwrap();
            for (i,nd) in s.nodes.iter().enumerate() {
                for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {
                    if nd.actor as usize==p && source[i]==0 {
                        let re=((gr[ix] as f64-scaled_r[ix] as f64)/factors[p] as f64-(lr[ix] as f64-initial_r[ix] as f64)).abs();
                        let se=((gs[ix] as f64-scaled_s[ix] as f64)/masses[p] as f64-(ls[ix] as f64-initial_s[ix] as f64)).abs();
                        assert!(re<0.0002 && se<0.000002,"increment unit mismatch at {i}/{ix}: {re}/{se}");
                        regret_worst=regret_worst.max(re);average_worst=average_worst.max(se);increments+=1;
                    } else {
                        assert_eq!(lr[ix],initial_r[ix]);assert_eq!(gr[ix],scaled_r[ix]);
                        assert_eq!(ls[ix],initial_s[ix]);assert_eq!(gs[ix],scaled_s[ix]);
                    }
                }
            }
        }
        assert_eq!(action_values,s.n*(s.nodes.len()-1)*NUM_CLASSES);
        assert!(increments>0 && folded_leaves>0 && local.spans.len()>3);
        println!("HISTORY_UNITS {}",json!({"calibrated":calibrated,"incoming_masses":masses,"counterfactual_factors":factors,
            "nodes":s.nodes.len(),"levels":local.spans.len(),"action_values_checked":action_values,"learning_entries_checked":increments,
            "folded_leaf_visits":folded_leaves,"worst_conditional_value_error_bb":value_worst,
            "worst_conditional_regret_increment_error_bb":regret_worst,"worst_average_increment_error":average_worst,
            "fixed_and_other_actor_histories_unchanged":true}));
    }}
}

#[test]
fn history_units_scaling_can_cross_native_policy_floor() {
    let s=fixture(false);let mut g=PreflopGpu::new(&s,512).unwrap();let ranges=normalized_ranges();
    for bad in [vec![vec![0.0;NUM_CLASSES];4],vec![vec![f32::NAN;NUM_CLASSES];4],ranges.iter().map(|r|r.iter().map(|v|v*0.5).collect()).collect()] {
        assert!(g.research_set_root_ranges(bad).is_err());assert!(g.research_root_ranges.is_none());
    }
    let sources=g.stream.clone_dtoh(&g.d_reach_src).unwrap();let root=&s.nodes[0];let na=root.actions.len();assert!(na>1);
    let child=s.child(0,0);let slot=sources[child*s.n] as usize*NUM_CLASSES;
    for mode in [0,1] {
        let mut observed=Vec::new();
        for scale in [1.0,0.001] {
            let mut arena=s.arena_snapshot().0;
            arena[root.data_off..root.data_off+na*NUM_CLASSES].fill(0.0);
            arena[root.data_off..root.data_off+NUM_CLASSES].fill(1e-11*scale);
            if mode==0 {g.stream.memcpy_htod(&arena,&mut g.d_regrets).unwrap();} else {g.stream.memcpy_htod(&arena,&mut g.d_strat).unwrap();}
            g.down(mode,0).unwrap();let reach=g.stream.clone_dtoh(&g.d_reach).unwrap();observed.push(reach[slot]/class_prob(0));
        }
        assert_eq!(observed[0],1.0);assert!((observed[1]-1.0/na as f32).abs()<1e-6);
        println!("HISTORY_FLOOR {}",json!({"mode":mode,"actions":na,"before_probability":observed[0],"after_probability":observed[1],
            "history_scale":0.001,"conversion_must_not_claim_policy_preservation":true}));
    }
}


// Standalone arithmetic/capture proof. No public continuation path is enabled.
fn fixed_up(g:&mut PreflopGpu,f:&CudaFunction,r:&CudaSlice<f32>,a:&CudaSlice<f32>,p:i32) {
    for li in (0..g.spans.len()).rev() {
        let (start,count)=g.spans[li];if count==0 {continue;}
        let (start,count)=(start as i32,count as i32);
        unsafe {
            g.stream.launch_builder(f).arg(&g.d_act_nodes).arg(&start).arg(&count)
                .arg(&p).arg(&g.np).arg(&g.d_actor).arg(&g.d_na).arg(&g.d_off)
                .arg(&g.d_cstart).arg(&g.d_children).arg(&g.d_src).arg(&g.d_foff)
                .arg(&g.d_forced).arg(&g.d_reach_src).arg(&g.d_reach).arg(r).arg(a)
                .arg(&mut g.d_regrets).arg(&mut g.d_strat).arg(&g.d_val_slot).arg(&mut g.d_val)
                .launch(PreflopGpu::cfg(count as u32)).unwrap();
        }
    }
}

#[test]
fn history_units_fixed_kernel_arithmetic_and_capture() {
    for calibrated in [false,true] {for unequal in [false,true] {
        let s=fixture(calibrated);let (initial_r,initial_s)=s.arena_snapshot();
        let mut base=PreflopGpu::new(&s,512).unwrap();let mut g=PreflopGpu::new(&s,512).unwrap();
        let source=g.stream.clone_dtoh(&g.d_src).unwrap();
        let mut ru=vec![1f32;s.nodes.len()];let mut au=ru.clone();
        if unequal {for i in 0..s.nodes.len() {if source[i]==0 {
            ru[i]=[0.001,0.037,0.125,0.61,1.0][i%5];au[i]=[0.173,0.25,0.83,1.0][i%4];
        }}}
        let dr=g.stream.clone_htod(&ru).unwrap();let da=g.stream.clone_htod(&au).unwrap();
        let module=g._ctx.load_module(cudarc::nvrtc::compile_ptx(
            [include_str!("../kernels.cu"),include_str!("fixed_history_units.cu")].join("\n")).unwrap()).unwrap();
        let f=module.load_function("pf_up_fixed_history_units").unwrap();
        let mut worst_r=0f64;let mut worst_s=0f64;let mut worst_v=0f64;let mut entries=0;
        for p in 0..s.n {
            base.stream.memcpy_htod(&initial_r,&mut base.d_regrets).unwrap();
            base.stream.memcpy_htod(&initial_s,&mut base.d_strat).unwrap();
            base.down(0,p as i32).unwrap();base.terminals_masked(p as i32,0).unwrap();base.up(p as i32,0).unwrap();
            let br=base.stream.clone_dtoh(&base.d_regrets).unwrap();let bs=base.stream.clone_dtoh(&base.d_strat).unwrap();
            let bv=base.stream.clone_dtoh(&base.d_val).unwrap();
            let mut outputs=Vec::new();
            // Warm launches, then capture the same stable buffers and replay.
            for captured in [false,true] {
                g.stream.memcpy_htod(&initial_r,&mut g.d_regrets).unwrap();g.stream.memcpy_htod(&initial_s,&mut g.d_strat).unwrap();
                g.down(0,p as i32).unwrap();g.terminals_masked(p as i32,0).unwrap();
                if captured {
                    g.stream.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL).unwrap();
                    fixed_up(&mut g,&f,&dr,&da,p as i32);
                    let graph=g.stream.end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH).unwrap().unwrap();
                    graph.launch().unwrap();
                } else {fixed_up(&mut g,&f,&dr,&da,p as i32);}
                let gr=g.stream.clone_dtoh(&g.d_regrets).unwrap();let gs=g.stream.clone_dtoh(&g.d_strat).unwrap();
                let gv=g.stream.clone_dtoh(&g.d_val).unwrap();
                if !unequal {assert_eq!(br,gr);assert_eq!(bs,gs);assert_eq!(bv,gv);}
                for (i,nd) in s.nodes.iter().enumerate() {
                    for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {
                        if source[i]==0 && nd.actor as usize==p {
                            let er=initial_r[ix] as f64+(br[ix] as f64-initial_r[ix] as f64)/ru[i] as f64;
                            let es=initial_s[ix] as f64+(bs[ix] as f64-initial_s[ix] as f64)/au[i] as f64;
                            let re=(gr[ix] as f64-er).abs();let se=(gs[ix] as f64-es).abs();
                            assert!(re.is_finite() && se.is_finite() && re<0.002 && se<0.002,"fixed increment at {i}/{ix}: {re}/{se}");
                            worst_r=worst_r.max(re);worst_s=worst_s.max(se);entries+=1;
                        } else {assert_eq!(gr[ix],initial_r[ix]);assert_eq!(gs[ix],initial_s[ix]);}
                    }
                }
                for (a,b) in bv.iter().zip(&gv) {let e=(*a as f64-*b as f64).abs();assert!(e<0.0002);worst_v=worst_v.max(e);}
                outputs.push((gr,gs,gv));
            }
            assert_eq!(outputs[0],outputs[1]);
        }
        // Units do not modify histories or down-pass probabilities, even near
        // the native normalization floor that breaks naive array rescaling.
        let root=&s.nodes[0];let child=s.child(0,0);
        let reach_src=g.stream.clone_dtoh(&g.d_reach_src).unwrap();let slot=reach_src[child*s.n] as usize*NUM_CLASSES;
        for mode in [0,1] {
            let mut tiny=initial_r.clone();tiny[root.data_off..root.data_off+root.actions.len()*NUM_CLASSES].fill(0.0);
            tiny[root.data_off..root.data_off+NUM_CLASSES].fill(1e-11);
            if mode==0 {g.stream.memcpy_htod(&tiny,&mut g.d_regrets).unwrap();} else {g.stream.memcpy_htod(&tiny,&mut g.d_strat).unwrap();}
            g.down(mode,0).unwrap();let reach=g.stream.clone_dtoh(&g.d_reach).unwrap();assert_eq!(reach[slot]/class_prob(0),1.0);
        }
        println!("FIXED_HISTORY_KERNEL {}",json!({"calibrated":calibrated,"unequal":unequal,"nodes":s.nodes.len(),
            "levels":g.spans.len(),"learning_entries_checked":entries,"worst_regret_error":worst_r,"worst_average_error":worst_s,
            "worst_value_error_bb":worst_v,"extra_device_bytes":(dr.len()+da.len())*4,
            "capture_eager_bitwise_equal":true,"fixed_histories_preserved":true,"tiny_initial_policy_preserved":true,
            "continuation_qualified":false}));
    }}
}


#[test]
fn history_units_full_iterations_native_and_capture() {
    for calibrated in [false,true] {for unequal in [false,true] {
        let mut outcomes=Vec::new();
        for eager in [false,true] {
            let mut s=fixture(calibrated);s.iteration=17;let initial=s.arena_snapshot();
            let mut g=PreflopGpu::new(&s,512).unwrap();let sources=g.stream.clone_dtoh(&g.d_src).unwrap();
            let mut ru=vec![1.0;s.nodes.len()];let mut au=ru.clone();
            for (i,nd) in s.nodes.iter().enumerate() {if unequal && sources[i]==0 && nd.kind==KIND_ACTION {
                ru[i]=[0.001,0.037,0.125,0.61,1.0][i%5];au[i]=[0.173,0.25,0.83,1.0][i%4];
            }}
            assert_eq!(g.research_set_history_units(&ru,&au,8*s.nodes.len()).unwrap(),8*s.nodes.len());
            for _ in 0..4 {
                if eager {g.warmed=false;for graph in &mut g.learning_graphs {*graph=None;}}
                g.iterate(&mut s).unwrap();
            }
            assert_eq!(s.iteration,21);let checked=g.gaps_and_evs().unwrap();g.sync_to_cpu(&mut s).unwrap();
            let final_histories=s.arena_snapshot();assert!(final_histories.0.iter().chain(&final_histories.1).all(|x|x.is_finite()));
            for (i,nd) in s.nodes.iter().enumerate() {if sources[i]!=0 {
                for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {
                    let mut er=initial.0[ix];let mut es=initial.1[ix];
                    for age in 18..=21 {let t=age as f64;let pos=(t.powf(1.5)/(t.powf(1.5)+1.0)) as f32;
                        er*=if er>0.0 {pos}else{0.5};if sources[i]!=1 {es*=(t/(t+1.0)).powi(2) as f32;}}
                    assert_eq!(er,final_histories.0[ix]);assert_eq!(es,final_histories.1[ix]);
                }
            }}
            let mut fresh=PreflopGpu::new(&s,512).unwrap();assert_eq!(checked,fresh.gaps_and_evs().unwrap());
            if !unequal {
                let mut native_s=fixture(calibrated);native_s.iteration=17;
                let mut native=PreflopGpu::new(&native_s,512).unwrap();
                for _ in 0..4 {native.iterate(&mut native_s).unwrap();}
                assert_eq!(checked,native.gaps_and_evs().unwrap());native.sync_to_cpu(&mut native_s).unwrap();
                assert_eq!(final_histories,native_s.arena_snapshot());
            }
            outcomes.push((final_histories,checked));
        }
        assert_eq!(outcomes[0],outcomes[1]);
        println!("FIXED_HISTORY_ITERATION {}",json!({"calibrated":calibrated,"unequal":unequal,
            "start_iteration":17,"end_iteration":21,"capture_eager_equal":true,"native_final_evaluation_equal":true,
            "fixed_bookkeeping_matches_native":true,"histories_finite":true,"continuation_qualified":false}));
    }}
}

#[test]
fn history_units_admission_and_discount() {
    let s=fixture(false);let n=s.nodes.len();let one=vec![1.0;n];
    let mut g=PreflopGpu::new(&s,512).unwrap();let before=s.arena_snapshot();
    for value in [0.0,-1.0,1e-9,1.01,f32::NAN,f32::INFINITY] {
        let mut bad=one.clone();bad[0]=value;
        for (r,a) in [(&bad,&one),(&one,&bad)] {assert!(g.research_set_history_units(r,a,8*n).is_err());}
        assert!(g.research_history_units.is_none());
    }
    assert!(g.research_set_history_units(&one[..n-1],&one,8*n).is_err());
    assert!(g.research_set_history_units(&one,&one[..n-1],8*n).is_err());
    assert!(g.research_set_history_units(&one,&one,8*n-1).is_err());
    let sources=g.stream.clone_dtoh(&g.d_src).unwrap();
    for (i,nd) in s.nodes.iter().enumerate() {if sources[i]!=0 || nd.kind!=KIND_ACTION {
        let mut bad=one.clone();bad[i]=0.5;assert!(g.research_set_history_units(&bad,&one,8*n).is_err());
    }}
    assert!(g.research_history_units.is_none());
    assert_eq!(g.stream.clone_dtoh(&g.d_regrets).unwrap(),before.0);
    assert_eq!(g.stream.clone_dtoh(&g.d_strat).unwrap(),before.1);
    for mode in 0..5 {
        let mut other_s=fixture(false);let mut other=PreflopGpu::new(&other_s,512).unwrap();
        match mode {
            0=>other.enable_research_normalized_regret().unwrap(),
            1=>other.enable_research_opponent_exploration(0.01,250).unwrap(),
            2=>other.research_set_root_ranges(normalized_ranges()).unwrap(),
            3=>other.iterate(&mut other_s).unwrap(),
            _=>{other.gaps_and_evs().unwrap();}
        }
        assert!(other.research_set_history_units(&one,&one,8*n).is_err());assert!(other.research_history_units.is_none());
    }
    let mut ru=one.clone();let mut au=one.clone();
    for (i,nd) in s.nodes.iter().enumerate() {if sources[i]==0 && nd.kind==KIND_ACTION {ru[i]=0.037;au[i]=0.173;}}
    g.research_set_history_units(&ru,&au,8*n).unwrap();
    assert!(g.research_set_history_units(&one,&one,8*n).is_err());
    assert!(g.enable_research_normalized_regret().is_err());assert!(g.enable_research_opponent_exploration(0.01,250).is_err());
    assert!(g.research_set_root_ranges(normalized_ranges()).is_err());
    assert!(g.configure_research(crate::preflop::convergence_research::Experiment::new("dcfr",64,1000,42).unwrap()).is_err());
    assert!(g.research_restrict_learning(&s,&[0usize].into_iter().collect()).is_err());
    assert!(g.enable_research_pair_control(100).is_err());assert!(g.enable_research_control_variate(32,100).is_err());
    // Independent host discount applied to GPU sequential sweep outputs.
    for p in 0..s.n {if !g.static_seats[p] {g.sweep(p as i32,0).unwrap();}}
    let mut er=g.stream.clone_dtoh(&g.d_regrets).unwrap();let mut es=g.stream.clone_dtoh(&g.d_strat).unwrap();
    let t=18f64;let pos=(t.powf(1.5)/(t.powf(1.5)+1.0)) as f32;let sd=(t/(t+1.0)).powi(2) as f32;
    for (i,nd) in s.nodes.iter().enumerate() {if nd.kind==KIND_ACTION {
        for ix in nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES {er[ix]*=if er[ix]>0.0 {pos}else{0.5};if sources[i]!=1 {es[ix]*=sd;}}
    }}
    let mut actual_s=fixture(false);actual_s.iteration=17;let mut actual=PreflopGpu::new(&actual_s,512).unwrap();
    actual.research_set_history_units(&ru,&au,8*n).unwrap();actual.iterate(&mut actual_s).unwrap();
    for (i,(a,b)) in er.iter().zip(actual.stream.clone_dtoh(&actual.d_regrets).unwrap()).enumerate() {assert_eq!(*a,b,"regret discount at {i}");}
    for (i,(a,b)) in es.iter().zip(actual.stream.clone_dtoh(&actual.d_strat).unwrap()).enumerate() {assert_eq!(*a,b,"average discount at {i}");}
    assert!(actual.research_set_history_units(&one,&one,8*n).is_err());
    println!("FIXED_HISTORY_ADMISSION {}",json!({"nodes":n,"invalid_inputs_preserved_state":true,
        "host_discount_bitwise_equal":true,"incompatible_modes_rejected":true,"continuation_qualified":false}));
}
