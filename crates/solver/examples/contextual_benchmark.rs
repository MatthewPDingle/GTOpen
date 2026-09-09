//! Read aggregate fixtures from stdin; emit native timings and probabilities.
//! Run through tools/research/model_benchmark.py. Never contacts the app server.
use serde::Deserialize;
use serde_json::{json, Value};
use solver::preflop::{contextual, BucketPolicy, PreflopConfig, PreflopSolver, ProfileResponse, SeatProfile};
use solver::preflop::equity::EquityTable;
use std::{hint::black_box, io::{self, Read}, sync::Arc, time::Instant};

#[derive(Deserialize)]
struct Trace { name: String, cfg: PreflopConfig, seat: usize, input: contextual::ContextualInput, baseline: BucketPolicy }
#[derive(Deserialize)]
struct Fixture { name: String, cfg: PreflopConfig, policy: BucketPolicy }
#[derive(Deserialize)]
struct Request { traces: Vec<Trace>, games: Vec<Fixture>, repeats: usize }

fn elapsed_us(start: Instant) -> f64 { start.elapsed().as_secs_f64()*1e6 }
fn summary(mut samples: Vec<f64>) -> Value {
    samples.sort_by(f64::total_cmp);
    json!({"median":samples[samples.len()/2], "min":samples[0], "max":samples[samples.len()-1], "samples":samples})
}
fn policy_probs(p: &BucketPolicy) -> Vec<[f32;3]> {
    (0..169).map(|h| [1.0-p.call[h]-p.raise[h]-p.jam[h],p.call[h],p.raise[h]+p.jam[h]]).collect()
}
fn profile(p: &BucketPolicy, contextual_on: bool) -> SeatProfile {
    SeatProfile { name:"Benchmark synthetic aggregate profile".into(), buckets:vec![Some(p.clone());5],
        vs_raise_bands:None, postflop:None, limp_defense:None,
        response:Some(ProfileResponse { contextual_reraise:contextual_on.then(||contextual::MODEL_ID.into()),
            cold_reraise:Some(p.clone()), ..Default::default() }) }
}
fn main() -> Result<(),String> {
    let mut raw=String::new();io::stdin().read_to_string(&mut raw).map_err(|e|e.to_string())?;
    let req:Request=serde_json::from_str(&raw).map_err(|e|e.to_string())?;
    if req.repeats<10 || req.repeats>10000 { return Err("repeats must be 10..10000".into()); }
    let mut traces=Vec::new();
    for t in &req.traces {
        let prediction=contextual::predict(contextual::MODEL_ID,&t.cfg,t.seat,&t.input)?;
        let mut fixed=Vec::new();let mut candidate=Vec::new();
        for round in 0..9 {
            // Alternate measurement order to limit order/temperature bias.
            let mut measure=|on:bool| -> Result<(),String> {
                let start=Instant::now();
                for _ in 0..req.repeats {
                    if on { black_box(contextual::predict(black_box(contextual::MODEL_ID),black_box(&t.cfg),black_box(t.seat),black_box(&t.input))?); }
                    else { black_box(black_box(&t.baseline).clone()); }
                }
                let us=elapsed_us(start)/req.repeats as f64;
                if on { candidate.push(us); } else { fixed.push(us); }
                Ok(())
            };
            if round%2==0 { measure(false)?;measure(true)?; } else {measure(true)?;measure(false)?;}
        }
        traces.push(json!({"name":t.name,"probabilities":prediction.policy.as_ref().map(policy_probs),
            "nominal_price":prediction.nominal_price,"note":prediction.note,
            "fixed_policy_clone_us":summary(fixed),"contextual_predict_us":summary(candidate)}));
    }
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
    let mut games=Vec::new();
    for fixture in &req.games {
        for on in [false,true] {
            let mut build=Vec::new();let mut install=Vec::new();let mut cold_query=Vec::new();let mut warm_query=Vec::new();let mut compile_all=Vec::new();let mut cached_all=Vec::new();
            let mut nodes=0;let mut arena_mb=0.0;let mut checked=0;let mut signature=0u64;let mut cache_entries=0;
            let mut query_cache_entries=0;
            for _ in 0..3 {
                let start=Instant::now();let mut s=PreflopSolver::new(fixture.cfg.clone(),eq.clone())?;build.push(elapsed_us(start));
                nodes=s.nodes.len();arena_mb=s.arena_mb();
                let profiles=vec![Some(profile(&fixture.policy,on));s.n];
                let start=Instant::now();s.set_table(vec![false;s.n],profiles)?;install.push(elapsed_us(start));
                // A bounded traversal gathers actual, legal re-raise nodes.
                let mut stack=vec![(0usize,vec![])];let mut paths=Vec::new();
                while let Some((node,path))=stack.pop() {
                    if s.nodes[node].bucket==4 && !s.nodes[node].actions.is_empty() { paths.push(path.clone());if paths.len()==24 {break;} }
                    for a in (0..s.nodes[node].actions.len()).rev() { let mut next=path.clone();next.push(a);stack.push((s.child(node,a),next)); }
                }
                checked=paths.len();
                let start=Instant::now();
                for path in &paths { black_box(s.node_view(path)?); }
                cold_query.push(elapsed_us(start));
                let start=Instant::now();
                for path in &paths { black_box(s.node_view(path)?); }
                warm_query.push(elapsed_us(start));
                let mut hash=14695981039346656037u64;
                for path in &paths {
                    let view=s.node_view(path)?;
                    let sigma=view.strategy.ok_or("missing strategy")?;
                    if sigma.iter().any(|p| !p.is_finite() || *p < -1e-6) {return Err("illegal strategy probabilities".into());}
                    for h in 0..169 { let total:f32=(0..view.actions.len()).map(|a|sigma[a*169+h]).sum();
                        if (total-1.0).abs()>2e-5 {return Err("strategy does not normalize".into());} }
                    for p in sigma { for byte in p.to_bits().to_le_bytes() {hash^=byte as u64;hash=hash.wrapping_mul(1099511628211);} }
                }
                if signature!=0 && signature!=hash {return Err("query results changed between repeats".into());}signature=hash;
                query_cache_entries=s.contextual_cache_entries();
                for warm in [false,true] {
                    let start=Instant::now();
                    for (node,nd) in s.nodes.iter().enumerate() { if !nd.actions.is_empty() {black_box(s.average_strategy(node));} }
                    if warm {cached_all.push(elapsed_us(start));}else{compile_all.push(elapsed_us(start));}
                }
                cache_entries=s.contextual_cache_entries();
            }
            games.push(json!({"name":fixture.name,"contextual":on,"nodes":nodes,"arena_mb":arena_mb,"queried_nodes":checked,"strategy_fingerprint":format!("{signature:016x}"),
                "query_cache_entries":query_cache_entries,"contextual_cache_entries":cache_entries,"contextual_cache_vector_bytes":cache_entries*169*3*4,
                "build_us":summary(build),"install_profiles_us":summary(install),"first_query_batch_us":summary(cold_query),"cached_query_batch_us":summary(warm_query),
                "materialize_all_policies_us":summary(compile_all),"cached_all_policies_us":summary(cached_all)}));
        }
    }
    println!("{}",json!({"version":contextual::MODEL_ID,"traces":traces,"games":games}));
    Ok(())
}
