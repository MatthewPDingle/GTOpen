//! Offline GPU ancestor repair: INPUT PATHS ITERATIONS OUTPUT.
use solver::preflop::{equity::EquityTable,gpu::PreflopGpu,PreflopSolver};
use std::{sync::Arc,time::Instant};
use serde_json::json;
fn main()->Result<(),String> {
    let a:Vec<_>=std::env::args().skip(1).collect();
    if a.len()!=4 {return Err("INPUT PATHS ITERATIONS OUTPUT".into());}
    let iterations:u32=a[2].parse().map_err(|_|"iterations")?;
    if iterations==0 || iterations>1000 {return Err("iteration cap".into());}
    let out=std::path::Path::new(&a[3]);if out.exists(){return Err("output exists".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let start=Instant::now();
    let bytes=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(bytes[..4].try_into().unwrap())));
    let mut s=PreflopSolver::load_game(&a[0],eq.clone())?;
    if s.multiway_equity_model()!="coupled_deck_v1" {return Err("canonical coupled model required".into());}
    let paths:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&a[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let repair=s.research_refine_ancestors_gpu(&paths,iterations)?;
    println!("REPAIRED {repair}");
    let mut gpu=PreflopGpu::new(&s,23000)?;
    let (gaps,evs)=gpu.gaps_and_evs()?;drop(gpu);
    if gaps.iter().chain(&evs).any(|v|!v.is_finite()){return Err("nonfinite unmasked check".into());}
    std::fs::create_dir_all(out).map_err(|e|e.to_string())?;
    let save=out.join("final.gtop");s.save_game(save.to_str().ok_or("path")?)?;
    let reload=PreflopSolver::load_game(save.to_str().unwrap(),eq)?;
    if reload.arena_snapshot()!=s.arena_snapshot(){return Err("roundtrip mismatch".into());}
    let result=json!({"input":a[0],"nodes":s.nodes.len(),"repair":repair,"global_gaps":gaps,"global_evs":evs,
        "unmasked_final_check":true,"roundtrip_exact":true,"seconds":start.elapsed().as_secs_f64(),"normal_global_resume_supported":false});
    std::fs::write(out.join("result.json"),serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())
}
