//! Isolated fixed-opponent sensitivity study. No app connections or save files.
//! Driven by tools/research/behavior_sensitivity.py; four CPU threads at most.
use serde::Deserialize;
use serde_json::{json, Value};
use solver::preflop::{contextual::{self, Entry}, HudStats, PreflopConfig, PreflopSolver, SeatProfile};
use solver::preflop::equity::{class_prob, EquityTable};
use std::{io::{self,Read},sync::Arc,time::Instant};

#[derive(Deserialize)]
struct Scenario { name:String, cfg:PreflopConfig, hero:usize, focal_history:Vec<String> }
#[derive(Deserialize)]
struct Request { scenarios:Vec<Scenario>, source_stats:HudStats, max_iterations:u32, target_gap:f64, cheap_price:f64 }
const WORLDS:[&str;4]=["legacy","contextual","cheap_call_half_odds","cheap_call_double_odds"];
fn weak(h:usize)->bool {h/13<h%13 && h%13<9}

fn hero_fingerprint(s:&PreflopSolver,hero:usize)->u64 {
    let mut hash=14695981039346656037u64;
    for (node,nd) in s.nodes.iter().enumerate() {
        if nd.actions.is_empty() || nd.actor as usize!=hero {continue;}
        for byte in (node as u64).to_le_bytes() {hash^=byte as u64;hash=hash.wrapping_mul(1099511628211);}
        for probability in s.average_strategy(node) {
            for byte in probability.to_bits().to_le_bytes() {hash^=byte as u64;hash=hash.wrapping_mul(1099511628211);}
        }
    }
    hash
}

fn nodes_with_paths(s:&PreflopSolver)->Vec<(usize,Vec<usize>)> {
    let mut stack=vec![(0,vec![])];let mut out=Vec::new();
    while let Some((node,path))=stack.pop() {
        for action in (0..s.nodes[node].actions.len()).rev() {
            let mut next=path.clone();next.push(action);stack.push((s.child(node,action),next));
        }
        if !s.nodes[node].actions.is_empty() {out.push((node,path));}
    }
    out
}
fn relevant(s:&PreflopSolver,node:usize,hero:usize,cheap:f64)->bool {
    if s.nodes[node].actor as usize==hero {return false;}
    let Some(c)=s.contextual_input(node) else{return false};
    if c.entry==Entry::Cold {return false;}
    let call=(c.to_call-c.invested).min(s.cfg.stack-c.invested);
    call/(c.pot+call)<=cheap+1e-10
}
fn profiles(base:&[Option<SeatProfile>],world:usize)->Vec<Option<SeatProfile>> {
    base.iter().map(|p|p.clone().map(|mut p|{
        p.response.as_mut().unwrap().contextual_reraise=(world!=0).then(||contextual::MODEL_ID.into());p
    })).collect()
}
fn install(s:&mut PreflopSolver,base:&[Option<SeatProfile>],world:usize,paths:&[(usize,Vec<usize>)],hero:usize,cheap:f64)->Result<usize,String> {
    for (_,path) in paths {s.unlock_point(path)?;}
    s.set_table_keep(vec![false;s.n],profiles(base,world))?;
    let mut changed=0;
    if world<2 {return Ok(changed);}
    for (node,path) in paths {
        if !relevant(s,*node,hero,cheap) {continue;}
        let c=s.contextual_input(*node).unwrap();
        let mut policy=contextual::predict(contextual::MODEL_ID,&s.cfg,s.nodes[*node].actor as usize,&c)?.policy.ok_or("unsupported scenario")?;
        let size=base[s.nodes[*node].actor as usize].as_ref().unwrap().buckets[4].as_ref().unwrap();
        policy.raise_size=size.raise_size.clone();policy.raise_sizes=size.raise_sizes.clone();
        let can_raise=s.nodes[*node].actions.iter().any(|a|a.kind=="raise"||a.kind=="jam");
        let odds=if world==2 {0.5f64}else{2.0};
        for h in 0..169 {
            if !weak(h) {continue;}
            // Perturb the legal call/fold odds, keeping any legal raise mass.
            if !can_raise {policy.call[h]+=policy.raise[h]+policy.jam[h];policy.raise[h]=0.0;policy.jam[h]=0.0;}
            let call=policy.call[h] as f64;
            let passive=(1.0-policy.raise[h] as f64-policy.jam[h] as f64).max(0.0);
            let fold=(passive-call).max(0.0);
            if fold+odds*call>0.0 {policy.call[h]=(passive*odds*call/(fold+odds*call)) as f32;}
        }
        s.lock_point(path,Some(policy))?;changed+=1;
    }
    Ok(changed)
}
fn focal(s:&PreflopSolver,history:&[String],hero:usize)->Result<Value,String> {
    let mut node=0;let mut path=Vec::new();
    for kind in history {
        let a=s.nodes[node].actions.iter().position(|a|a.kind==*kind).ok_or("focal history unavailable")?;
        path.push(a);node=s.child(node,a);
    }
    if s.nodes[node].actor as usize!=hero {return Err("focal decision not hero".into());}
    let view=s.node_view(&path)?;
    Ok(json!({"path":path,"actions":view.actions,"strategy":s.average_strategy(node),"reach":view.reach,"note":view.strategy_note}))
}
fn target_events(s:&PreflopSolver,paths:&[(usize,Vec<usize>)],hero:usize,cheap:f64)->Result<Value,String> {
    let mut events=0.0;let mut weak_events=0.0;let mut called=0.0;let mut largest=Vec::new();let mut count=0;
    for (node,path) in paths {
        if !relevant(s,*node,hero,cheap) {continue;}
        count+=1;
        let (_,reaches)=s.walk(path)?;let actor=s.nodes[*node].actor as usize;
        let others:f64=reaches.iter().enumerate().filter(|(p,_)|*p!=actor).map(|(_,r)|r.iter().map(|x|*x as f64).sum::<f64>()).product();
        let actor_mass:f64=reaches[actor].iter().map(|x|*x as f64).sum();
        let weak_mass:f64=(0..169).filter(|h|weak(*h)).map(|h|reaches[actor][h] as f64).sum();
        events+=others*actor_mass;weak_events+=others*weak_mass;
        let sigma=s.average_strategy(*node);let pass=s.nodes[*node].actions.iter().position(|a|a.kind=="call").unwrap();
        let call_mass:f64=(0..169).filter(|h|weak(*h)).map(|h|reaches[actor][h] as f64*sigma[pass*169+h] as f64).sum();
        called+=others*call_mass;
        if others*weak_mass>0.0 {largest.push((others*weak_mass,*node,path.clone()));}
    }
    largest.sort_by(|a,b|b.0.total_cmp(&a.0));
    let examples:Vec<_>=largest.into_iter().take(5).map(|(mass,node,path)|json!({"path":path,"actor":s.cfg.positions[s.nodes[node].actor as usize],"weak_events_per_100_hands":mass*100.0,"context":s.contextual_input(node)})).collect();
    Ok(json!({"target_nodes":count,"decisions_per_100_hands":100.0*events,"weak_hand_decisions_per_100_hands":100.0*weak_events,"weak_calls_per_100_hands":100.0*called,"largest_reaching_contexts":examples}))
}
fn run(req:Request)->Result<Value,String> {
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global().map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
    let mut results=Vec::new();
    for scenario in &req.scenarios {
        let started=Instant::now();
        if !contextual::is_supported(&scenario.cfg)||scenario.hero>=scenario.cfg.positions.len() {return Err("unsupported scenario/hero".into());}
        let mut seed=PreflopSolver::new(scenario.cfg.clone(),eq.clone())?;
        if scenario.cfg.realization=="calibrated" && seed.fit.is_none() {return Err("calibrated realization missing".into());}
        seed.iterate();
        let base:Vec<_>=(0..seed.n).map(|seat|{
            if seat==scenario.hero {return Ok(None);}
            let mut p=seed.generate_profile(seat,&req.source_stats,"Sensitivity fixed opponent")?.0;
            let response=p.response.as_mut().ok_or("missing generated response")?;
            response.contextual_reraise=None;response.adaptive_from=None;
            Ok(Some(p))
        }).collect::<Result<_,String>>()?;
        let paths=nodes_with_paths(&seed);let nodes=seed.nodes.len();let arena_mb=seed.arena_mb();
        // All faced amounts lie below production's default adaptive threshold.
        for (node,_) in &paths {
            if let Some(c)=seed.contextual_input(*node) {
                if c.to_call>=scenario.cfg.stack*0.25 {return Err("study reaches adaptive region; redesign fixture".into());}
            }
        }
        drop(seed);
        let mut trained=Vec::new();
        for train_world in 0..4 {
            let start=Instant::now();let mut s=PreflopSolver::new(scenario.cfg.clone(),eq.clone())?;
            let perturbed=install(&mut s,&base,train_world,&paths,scenario.hero,req.cheap_price)?;
            let mut trace=Vec::new();let mut final_gap=f64::INFINITY;
            while s.iteration<req.max_iterations {
                s.iterate();
                if s.iteration==10||s.iteration%25==0||s.iteration==req.max_iterations {
                    let (gap,ev)=s.gaps_and_evs();final_gap=gap[scenario.hero];
                    trace.push(json!({"iterations":s.iteration,"hero_gap_bb_per_hand":final_gap,"hero_ev_bb_per_hand":ev[scenario.hero],"seconds":start.elapsed().as_secs_f64()}));
                    if final_gap<=req.target_gap {break;}
                }
            }
            let own_focal=focal(&s,&scenario.focal_history,scenario.hero)?;
            let own_events=target_events(&s,&paths,scenario.hero,req.cheap_price)?;
            let learned_hero_fingerprint=hero_fingerprint(&s,scenario.hero);
            let iterations=s.iteration;let solve_seconds=start.elapsed().as_secs_f64();let mut cross=Vec::new();
            for evaluate_world in 0..4 {
                install(&mut s,&base,evaluate_world,&paths,scenario.hero,req.cheap_price)?;
                if hero_fingerprint(&s,scenario.hero)!=learned_hero_fingerprint {return Err("opponent replacement changed the learned hero strategy".into());}
                let (gaps,evs)=s.gaps_and_evs();
                if hero_fingerprint(&s,scenario.hero)!=learned_hero_fingerprint {return Err("cross-evaluation changed the learned hero strategy".into());}
                cross.push(json!({"world":WORLDS[evaluate_world],"hero_strategy_preserved":true,"hero_ev_bb_per_hand":evs[scenario.hero],"best_response_gap_bb_per_hand":gaps[scenario.hero],"best_response_ev_bb_per_hand":evs[scenario.hero]+gaps[scenario.hero]}));
            }
            eprintln!("{} / {}: {} iterations, gap {:.6} bb/hand, {:.2}s",scenario.name,WORLDS[train_world],iterations,final_gap,solve_seconds);
            trained.push(json!({"world":WORLDS[train_world],"hero_strategy_fingerprint":format!("{learned_hero_fingerprint:016x}"),"iterations":iterations,"self_gap_bb_per_hand":final_gap,"converged":final_gap<=req.target_gap,"solve_seconds":solve_seconds,"perturbed_nodes":perturbed,"convergence":trace,"focal":own_focal,"target_events":own_events,"cross_evaluation":cross}));
        }
        results.push(json!({"name":scenario.name,"config":scenario.cfg,"hero":scenario.cfg.positions[scenario.hero],"nodes":nodes,"arena_mb":arena_mb,"focal_history":scenario.focal_history,"seconds":started.elapsed().as_secs_f64(),"trained":trained}));
    }
    Ok(json!({"schema":1,"threads":4,"worlds":WORLDS,"target_gap_bb_per_hand":req.target_gap,"max_iterations":req.max_iterations,"cheap_price":req.cheap_price,"class_probability_sum":(0..169).map(class_prob).sum::<f32>(),"scenarios":results}))
}
fn main()->Result<(),String> {
    let mut raw=String::new();io::stdin().read_to_string(&mut raw).map_err(|e|e.to_string())?;
    let req:Request=serde_json::from_str(&raw).map_err(|e|e.to_string())?;
    println!("{}",run(req)?);Ok(())
}
