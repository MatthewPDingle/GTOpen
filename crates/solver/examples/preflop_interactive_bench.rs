//! Isolated fresh-game GPU workflow timings. No live API or implicit payoff changes.
//! INPUT.json MODEL ITERATIONS OUTPUT.gtop [PREVIEW_EVERY]
use serde_json::{json, Value};
use solver::preflop::{equity::EquityTable, gpu::PreflopGpu, PreflopConfig, PreflopSolver};
use std::{sync::Arc, time::Instant};

fn main() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len()<4 || args.len()>5 { return Err("INPUT.json MODEL ITERATIONS OUTPUT.gtop [PREVIEW_EVERY]".into()); }
    let count:u32=args[2].parse().map_err(|_| "invalid count")?;
    if count==0 || count>5000 { return Err("count must be1..5000".into()); }
    let preview_every:u32=args.get(4).map_or(Ok(10),|x|x.parse()).map_err(|_|"invalid preview cadence")?;
    if std::path::Path::new(&args[3]).exists() { return Err("output exists".into()); }
    let input:Value=serde_json::from_slice(&std::fs::read(&args[0]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let cfg:PreflopConfig=serde_json::from_value(input.get("config").unwrap_or(&input).clone()).map_err(|e|e.to_string())?;
    let started=Instant::now();
    let bytes=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let samples=u32::from_le_bytes(bytes[..4].try_into().unwrap());
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",samples));
    let mut s=PreflopSolver::new(cfg,eq.clone())?;
    s.set_multiway_equity_model(&args[1])?;
    if s.cfg.realization=="calibrated" && s.fit.is_none() { return Err("missing calibrated fit".into()); }
    let built=started.elapsed().as_secs_f64();
    let mut g=PreflopGpu::new(&s,23000)?;
    println!("INTERACTIVE {}",json!({"phase":"initialized","model":s.multiway_equity_model(),"nodes":s.nodes.len(),"build_seconds":built,"elapsed_seconds":started.elapsed().as_secs_f64()}));
    let mut iterations=Vec::new();
    for done in 1..=count {
        let t=Instant::now();g.iterate(&mut s)?;
        iterations.push(t.elapsed().as_secs_f64());
        if done==2 || (preview_every>0 && done%preview_every==0) {
            let t=Instant::now();g.sync_to_cpu(&mut s)?;
            let root=s.node_view(&[])?;
            println!("INTERACTIVE {}",json!({"phase":"preview","iteration":s.iteration,"elapsed_seconds":started.elapsed().as_secs_f64(),"sync_and_node_seconds":t.elapsed().as_secs_f64(),"root":root,"accuracy_measured":false}));
        }
        println!("INTERACTIVE {}",json!({"phase":"iterate","iteration":s.iteration,"seconds":iterations.last(),"elapsed_seconds":started.elapsed().as_secs_f64()}));
    }
    let t=Instant::now();let(gaps,evs)=g.gaps_and_evs()?;let check_seconds=t.elapsed().as_secs_f64();
    g.sync_to_cpu(&mut s)?;drop(g);
    let solver_seconds=started.elapsed().as_secs_f64();
    s.save_game(&args[3])?;
    let roundtrip=PreflopSolver::load_game(&args[3],eq)?;
    if roundtrip.multiway_equity_model()!=s.multiway_equity_model() || roundtrip.iteration!=s.iteration || roundtrip.arena_snapshot()!=s.arena_snapshot() { return Err("native roundtrip mismatch".into()); }
    println!("INTERACTIVE {}",json!({"phase":"result","model":s.multiway_equity_model(),"iteration":s.iteration,"iteration_seconds":iterations,"check_seconds":check_seconds,"solver_seconds":solver_seconds,"total_seconds":started.elapsed().as_secs_f64(),"gaps":gaps,"evs":evs,"output":args[3],"roundtrip_exact":true}));
    Ok(())
}
