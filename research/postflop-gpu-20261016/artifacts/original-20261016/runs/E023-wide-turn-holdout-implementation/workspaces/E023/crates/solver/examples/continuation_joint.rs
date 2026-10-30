//! Pass-two continuation corpus. CPU-only, four threads, per-job checkpoints.
//! python tools/research/continuation_joint.py prepare
//! cargo run --release -p solver --example continuation_joint
use serde_json::{json, Value};
use solver::preflop::equity::{class_index, EquityTable, NUM_CLASSES};
use solver::preflop::RealizationFit;
use solver::{combo_index, rank, suit, Range, Solver, Spot, SpotConfig};
use std::{path::Path, sync::Arc, time::Instant};

const ROOT: &str = "research/preflop-evolution/continuation/pass2";

fn dist(text: &str) -> Vec<f32> {
    let r = Range::parse(text).unwrap();
    let mut d = vec![0.0; NUM_CLASSES];
    for a in 0..52u8 { for b in a+1..52u8 {
        d[class_index(rank(a), rank(b), suit(a)==suit(b))] += r.weights[combo_index(a,b)];
    }}
    let z: f32 = d.iter().sum();
    d.iter_mut().for_each(|v| *v /= z);
    d
}

fn prices(oop: &str, ip: &str, pot: f64, stack: f64, rake: f64, cap: f64, eq: &EquityTable, fit: &RealizationFit) -> Value {
    let d = [dist(oop), dist(ip)];
    let mut raw = [0.0; 2]; let mut static_value = [0.0; 2]; let mut calibrated = [0.0; 2]; let mut equity = [0.0; 2];
    let drain = if cap>0.0 {(pot*rake/100.0).min(cap)} else {pot*rake/100.0};
    for p in 0..2 {
        let posw = (1.0+0.16*(p as f64-0.5)*((stack/pot).min(8.0)/8.0)) as f32 as f64;
        for h in 0..NUM_CLASSES {
            let q = eq.eq_vs_dist(h, &d[1-p]) as f64; let w = d[p][h] as f64;
            equity[p] += q*w;
            raw[p] += w*(pot-drain)*q;
            static_value[p] += w*((pot-drain)*q*posw).min(pot-drain);
            calibrated[p] += w*pot*q*fit.class_r(h,posw);
        }
    }
    json!({"equity":equity,"raw_bb":raw,"static_bb":static_value,"calibrated_bb":calibrated})
}

fn main() -> Result<(),String> {
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global().unwrap();
    let manifest: Value = serde_json::from_str(&std::fs::read_to_string(format!("{ROOT}/manifest.json")).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let jobs = manifest["jobs"].as_array().ok_or("missing jobs")?;
    std::fs::create_dir_all(format!("{ROOT}/jobs")).map_err(|e|e.to_string())?;
    let eq_path = "cache/preflop_eq169.bin";
    let bytes = std::fs::read(eq_path).map_err(|e|e.to_string())?;
    if bytes.len()!=4+NUM_CLASSES*NUM_CLASSES*4 || u32::from_le_bytes(bytes[..4].try_into().unwrap())!=20000 {return Err("existing equity cache required".into());}
    let eq = EquityTable::load_or_build(eq_path,20000);
    let fit = RealizationFit::load_default()?;
    let limit = std::env::var("CONTINUATION_JOB_LIMIT").ok().map(|x|x.parse::<usize>().unwrap()).unwrap_or(usize::MAX);
    let shard = std::env::var("CONTINUATION_SHARD").ok().map(|x|x.parse::<usize>().unwrap()).unwrap_or(0);
    let shards = std::env::var("CONTINUATION_SHARDS").ok().map(|x|x.parse::<usize>().unwrap()).unwrap_or(1);
    if shards==0 || shard>=shards {return Err("invalid worker shard".into());}
    let provenance: Value=std::env::var("CONTINUATION_PROVENANCE").ok().map(|v|serde_json::from_str(&v).unwrap()).unwrap_or(json!({"unrecorded_direct_run":true}));
    let mut completed = 0;
    for (index,job) in jobs.iter().enumerate() {
        if index%shards!=shard {continue;}
        if std::env::var("CONTINUATION_PARTITION").is_ok_and(|partition|job["partition"]!=partition) {continue;}
        let id = job["id"].as_str().ok_or("missing id")?;
        let path = format!("{ROOT}/jobs/{id}.json");
        if Path::new(&path).exists() {
            let existing: Value = serde_json::from_str(&std::fs::read_to_string(&path).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
            if existing["job"]!=*job || existing["manifest_id"]!=manifest["id"] {return Err(format!("checkpoint does not match manifest: {id}"));}
            if existing["target_met"]==true {continue;}
        }
        if completed>=limit {break;}
        let cfg: SpotConfig = serde_json::from_value(job["config"].clone()).map_err(|e|e.to_string())?;
        let pot=cfg.tree.starting_pot;
        let leaf=prices(&cfg.range_oop,&cfg.range_ip,pot,cfg.tree.effective_stack,cfg.tree.rake_pct*100.0,cfg.tree.rake_cap,&eq,&fit);
        eprintln!("continuation {}/{}: {id}",index+1,jobs.len());
        let start=Instant::now();
        let mut s=Solver::new(Arc::new(Spot::new(cfg.clone())?));
        let build_seconds=start.elapsed().as_secs_f64();
        let solve=Instant::now(); let mut trace=Vec::new(); let mut gap=100.0;
        while s.iteration<500 {
            s.iterate();
            if s.iteration%25==0 {
                gap=s.exploitability()/pot*100.0;
                trace.push(json!({"iteration":s.iteration,"gap_pct_pot":gap,"seconds":solve.elapsed().as_secs_f64()}));
                eprintln!("{id}: iteration {}, {gap:.3}% gap, {:.1}s",s.iteration,solve.elapsed().as_secs_f64());
                if gap<=0.3 {break;}
            }
        }
        let solve_seconds=solve.elapsed().as_secs_f64();
        let query=Instant::now(); let view=s.node_view(&[])?;
        let mut ev=[0.0;2]; let mut equity=[0.0;2]; let mut mass=[0.0;2];
        for p in 0..2 {for h in &view.players[p].hands {
            let w=h.reach as f64*h.valid as f64; if w<=0.0 {continue;}
            mass[p]+=w;ev[p]+=w*h.ev.unwrap() as f64;equity[p]+=w*h.eq.unwrap() as f64;
        } ev[p]/=mass[p];equity[p]/=mass[p];}
        if (mass[0]-mass[1]).abs()>1e-3 || (equity[0]+equity[1]-1.0).abs()>1e-4 {return Err("reference pair weighting failed".into());}
        let drain=pot-ev[0]-ev[1];
        let max_rake=if cfg.tree.rake_cap>0.0 {cfg.tree.rake_cap} else {(pot+2.0*cfg.tree.effective_stack)*cfg.tree.rake_pct};
        if drain< -1e-3 || drain>max_rake+1e-3 || (cfg.tree.rake_pct==0.0 && drain.abs()>1e-3) {return Err("reference accounting failed".into());}
        let out=json!({"schema":1,"manifest_id":manifest["id"],"job":job,"provenance":provenance,"preflop_leaf":leaf,
            "reference_ev_bb":ev,"reference_equity":equity,"compatible_pair_mass":mass[0],
            "reference_expected_rake_bb":drain,"iterations":s.iteration,"gap_pct_pot":gap,"target_met":gap<=0.3,
            "build_seconds":build_seconds,"solve_seconds":solve_seconds,"query_seconds":query.elapsed().as_secs_f64(),
            "arena_bytes":s.arena_bytes(),"tree_bytes":s.spot.tree_bytes(),"nodes":s.spot.tree.nodes.len(),"convergence":trace});
        let temporary=format!("{path}.partial");
        std::fs::write(&temporary,serde_json::to_string_pretty(&out).unwrap()).map_err(|e|e.to_string())?;
        std::fs::rename(&temporary,&path).map_err(|e|e.to_string())?;
        completed+=1;
        eprintln!("done {id}: {} iterations, {gap:.3}% gap, {:.1}s",s.iteration,start.elapsed().as_secs_f64());
    }
    Ok(())
}
