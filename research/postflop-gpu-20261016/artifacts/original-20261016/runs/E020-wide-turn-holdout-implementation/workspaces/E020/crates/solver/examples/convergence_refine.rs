//! Offline local re-solving screen: INPUT.gtop ITERATIONS OUTPUT_DIRECTORY.
use solver::preflop::{equity::EquityTable,PreflopSolver};
use std::sync::Arc;
fn main()->Result<(),String>{
    let a:Vec<_>=std::env::args().skip(1).collect();
    if a.len()!=3 && a.len()!=4 {return Err("INPUT ITERATIONS OUTPUT_DIRECTORY [nested]".into());}
    if a.len()==4 && a[3]!="nested" {return Err("unknown refinement mode".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let started=std::time::Instant::now();
    let out=std::path::Path::new(&a[2]);
    if out.exists(){return Err("output already exists".into());}
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(b[..4].try_into().unwrap())));
    let mut s=PreflopSolver::load_game(&a[0],eq)?;
    if s.cfg.positions!=["UTG","HJ","CO","BTN","SB","BB"] {return Err("registered small six-player fixture only".into());}
    // Two disjoint proper subtrees cover the six registered local audit paths.
    // The main tree and all actions through the BTN decision remain intact.
    let iterations=a[1].parse().map_err(|_|"invalid iterations")?;
    let mut result=Vec::new();
    if a.len()==4 {
        // Each deeper call conditions on the updated parent's saved average.
        // Recheck all paths afterward: child changes may affect earlier values.
        for path in [vec![2,0,0],vec![2,0,0,1],vec![2,0,0,1,1],vec![2,0,0,0,0],vec![1,0,0],vec![1,0,0,0,0]] {
            result.push(s.research_refine_branches(&[path],iterations)?);
        }
    } else {
        result.push(s.research_refine_branches(&[vec![2,0,0],vec![1,0,0]],iterations)?);
    }
    let (gaps,evs)=s.gaps_and_evs();
    if gaps.iter().chain(&evs).any(|v|!v.is_finite()) {return Err("nonfinite revalidation".into());}
    std::fs::create_dir_all(out).map_err(|e|e.to_string())?;
    s.save_game(out.join("final.gtop").to_str().ok_or("output path")?)?;
    let result=serde_json::json!({"input":a[0],"refinement":result,"global_gaps":gaps,"global_evs":evs,
        "elapsed_including_load_revalidation_save_seconds":started.elapsed().as_secs_f64()});
    std::fs::write(out.join("result.json"),serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())
}
