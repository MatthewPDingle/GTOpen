//! Registered bounded CPU driver; native model identity preserved at every save.
//! CORPUS.json CASE MODEL EQUITY_CACHE NEW_OUTPUT_DIRECTORY THREADS [CANDIDATE_CAP]
use serde_json::{json, Value};
use solver::preflop::{equity::{EquityTable,NUM_CLASSES},estimate_tree,PreflopConfig,PreflopSolver,BucketPolicy,SeatProfile,ProfileResponse};
use std::{path::PathBuf,sync::Arc,time::Instant};

fn profile(adaptive:bool)->SeatProfile {
    let policy=BucketPolicy{call:vec![0.4;NUM_CLASSES],raise:vec![0.2;NUM_CLASSES],jam:vec![0.0;NUM_CLASSES],
        raise_size:"max".into(),raise_sizes:vec![],raise_multiples:vec![]};
    SeatProfile{name:"synthetic registered quality control".into(),buckets:vec![Some(policy);5],vs_raise_bands:None,
        postflop:None,limp_defense:None,response:adaptive.then(||ProfileResponse{contextual_reraise:None,limp_unopened:None,
            adaptive_from:Some(0.25),source_stats:None,cold_reraise:None,limp_contexts:vec![]})}
}
fn run()->Result<(),String> {
    let args:Vec<_>=std::env::args().skip(1).collect();if !(6..=7).contains(&args.len()) {return Err("CORPUS CASE MODEL CACHE NEW_OUTPUT_DIRECTORY THREADS [CANDIDATE_CAP]".into());}
    let corpus_bytes=std::fs::read(&args[0]).map_err(|e|e.to_string())?;
    let corpus:Value=serde_json::from_slice(&corpus_bytes).map_err(|e|e.to_string())?;
    let case=corpus["small_tree_controls"].as_array().unwrap().iter().find(|c|c["id"]==args[1]).ok_or("unregistered case")?;
    let model=&args[2];if model!="coupled_deck_v1" && model!="coupled_preview64_v1" {return Err("unregistered model".into());}
    let candidate_cap=if args.len()==7 {args[6].parse::<u32>().map_err(|_|"invalid candidate cap")?}else{100};
    if !(1..=500).contains(&candidate_cap) || (model=="coupled_deck_v1" && args.len()==7) {
        return Err("candidate cap must be1..500 and is only valid for preview; reference remains500".into());
    }
    let threads:usize=args[5].parse().map_err(|_|"invalid threads")?;if !(1..=4).contains(&threads) {return Err("threads must be 1..4".into());}
    rayon::ThreadPoolBuilder::new().num_threads(threads).build_global().map_err(|e|e.to_string())?;
    let cfg:PreflopConfig=serde_json::from_value(case["config"].clone()).map_err(|e|e.to_string())?;
    let estimate=estimate_tree(&cfg)?;
    if estimate.truncated || estimate.nodes>20_000 || estimate.arena_len.saturating_mul(8)>128*1024*1024 {
        return Err(format!("registered case exceeds unchanged bounded preflight: {} nodes",estimate.nodes));
    }
    let output=PathBuf::from(&args[4]);if output.exists(){return Err("output directory must be new".into());}
    // Restrict generated artifacts to the current lab's target research subtree.
    let allowed=std::env::current_dir().map_err(|e|e.to_string())?.join("target").join("research-preview");
    std::fs::create_dir_all(&allowed).map_err(|e|e.to_string())?;
    let allowed=allowed.canonicalize().map_err(|e|e.to_string())?;
    let parent=output.parent().ok_or("output parent required")?.canonicalize().map_err(|e|e.to_string())?;
    if !parent.starts_with(&allowed){return Err("output parent must be inside lab target/research-preview".into());}
    std::fs::create_dir(&output).map_err(|e|e.to_string())?;
    let before=std::fs::read(&args[3]).map_err(|e|e.to_string())?;
    if before.len()!=4+NUM_CLASSES*NUM_CLASSES*4 {return Err("invalid equity cache".into());}
    let samples=u32::from_le_bytes(before[..4].try_into().unwrap());if samples==0{return Err("empty equity cache sample count".into());}
    let eq=Arc::new(EquityTable::load_or_build(&args[3],samples));
    let started=Instant::now();let mut s=PreflopSolver::new(cfg,eq)?;s.set_multiway_equity_model(model)?;
    let mut profiles=vec![None;s.n];let frozen:Vec<bool>=serde_json::from_value(case["frozen"].clone()).map_err(|e|e.to_string())?;
    match args[1].as_str(){
        "three-solver-development"=>{},
        "four-fixed-frozen-holdout"=>{s.research_seed_quality_fixture_averages()?;profiles[0]=Some(profile(false));},
        "three-adaptive-holdout"=>profiles[0]=Some(profile(true)),
        _=>return Err("case has no registered profile implementation".into())
    }
    s.set_table_keep(frozen,profiles)?;
    let init_seconds=started.elapsed().as_secs_f64();
    let limit=if model=="coupled_deck_v1"{500}else{candidate_cap};
    let mut checkpoints=Vec::new();let mut convergence=false;let mut iteration_seconds=0.0;let mut check_seconds=0.0;
    println!("SMALL_QUALITY {}",json!({"phase":"init","case":args[1],"model":model,"nodes":s.nodes.len(),
        "arena_mb":s.arena_mb(),"init_seconds":init_seconds,"limit":limit,"target_own_model_gap":0.005,"threads":threads}));
    for done in 1..=limit {
        let t=Instant::now();if !s.try_iterate(){return Err("unexpected canceled research iteration".into());}
        let iter_secs=t.elapsed().as_secs_f64();iteration_seconds+=iter_secs;
        if done%10!=0 && done!=limit && !(model!="coupled_deck_v1" && done==2){continue;}
        let t=Instant::now();let(gaps,evs)=s.gaps_and_evs();let check_secs=t.elapsed().as_secs_f64();check_seconds+=check_secs;
        if gaps.iter().chain(&evs).any(|x|!x.is_finite()){return Err("nonfinite checkpoint".into());}
        let live=s.live_seats();let gap:f64=gaps.iter().zip(&live).filter(|(_,l)|**l).map(|(g,_)|g).sum();
        convergence=gap<0.005;
        let save=convergence||done==limit||(model!="coupled_deck_v1"&&[2,10,30,50,100].contains(&done));
        let path=output.join(format!("checkpoint-{done:03}.gtop"));
        if save {if path.exists(){return Err("checkpoint already exists".into());}s.save_game(path.to_str().ok_or("non-UTF8 output")?)?;}
        let row=json!({"phase":"checkpoint","iteration":done,"gap_own_model_bb":gap,"gaps":gaps,"evs":evs,"live":live,
            "iteration_seconds_cumulative":iteration_seconds,"check_seconds_cumulative":check_seconds,
            "last_iteration_seconds":iter_secs,"check_seconds":check_secs,"elapsed_seconds":started.elapsed().as_secs_f64(),
            "native_save":if save{Some(path.to_string_lossy().to_string())}else{None},"converged_in_own_model":convergence});
        println!("SMALL_QUALITY {row}");checkpoints.push(row);if convergence{break;}
    }
    if std::fs::read(&args[3]).map_err(|e|e.to_string())?!=before || std::fs::read(&args[0]).map_err(|e|e.to_string())?!=corpus_bytes{return Err("research input changed".into());}
    let result=json!({"case":case,"model":model,"status":if convergence{"converged_in_own_model"}else{"not_converged_iteration_limit"},
        "iteration_limit":limit,"target_own_model_gap_bb":0.005,"init_seconds":init_seconds,"checkpoints":checkpoints,
        "quality_not_yet_checked":"Run preflop_preview_quality against the completed full reference. Candidate own-model gap does not establish full-reference quality."});
    std::fs::write(output.join("run.json"),serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())?;
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("small quality: {e}");std::process::exit(1);}}
