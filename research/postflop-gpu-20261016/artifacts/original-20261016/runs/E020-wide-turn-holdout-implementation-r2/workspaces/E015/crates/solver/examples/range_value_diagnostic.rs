//! Diagnostic reproduction only: prints pot discrepancies instead of enforcing
//! the pot check. Never use these outputs as training references. Optional
//! DIAGNOSTIC_F32 and DIAGNOSTIC_FULL_QUERY isolate extraction differences.
use serde_json::{json,Value};
use solver::{Solver,Spot,SpotConfig,Storage,rank,suit};
use solver::preflop::equity::{NUM_CLASSES,class_index,class_label};
use solver::gpu::GpuSolver;
use std::{sync::Arc,time::Instant};

fn main()->Result<(),String> {
    rayon::ThreadPoolBuilder::new().num_threads(12).build_global().unwrap();
    let args:Vec<_>=std::env::args().collect();
    if args.len()<2 {return Err("range_value_reference MANIFEST [LIMIT]".into());}
    let limit=args.get(2).map_or(usize::MAX,|x|x.parse().unwrap());
    let m:Value=serde_json::from_str(&std::fs::read_to_string(&args[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let root=std::path::Path::new(&args[1]).parent().unwrap();
    std::fs::create_dir_all(root.join("jobs")).map_err(|e|e.to_string())?;
    let mut completed=0;
    for job in m["jobs"].as_array().ok_or("jobs required")? {
        let id=job["id"].as_str().ok_or("id required")?;
        let out=root.join("jobs").join(format!("{id}.json"));
        if out.exists() {
            let old:Value=serde_json::from_str(&std::fs::read_to_string(&out).unwrap()).unwrap();
            if old["job"]!=*job || old["manifest_id"]!=m["id"] {return Err(format!("checkpoint mismatch: {id}"));}
            if old["target_met"]==true {continue;}
        }
        if completed>=limit {break;}
        eprintln!("BUILD {id}");let start=Instant::now();
        let cfg:SpotConfig=serde_json::from_value(job["config"].clone()).map_err(|e|e.to_string())?;
        let pot=cfg.tree.starting_pot;
        let mut host=Solver::with_storage(Arc::new(Spot::new(cfg)?),if std::env::var_os("DIAGNOSTIC_F32").is_some() { Storage::F32 } else { Storage::Compressed });
        let mut gpu=GpuSolver::new_with_budget(&host,12*1024*1024*1024)?;
        let mut trace=Vec::new();let mut gap=f64::INFINITY;let mut iter=0;
        while iter<m["max_iterations"].as_u64().unwrap() {
            for _ in 0..25 {gpu.iterate()?;iter+=1;}
            gap=gpu.exploitability(&host)?/pot*100.;
            trace.push(json!({"iteration":iter,"gap_pct":gap,"seconds":start.elapsed().as_secs_f64()}));
            if gap<=m["target_gap_pct"].as_f64().unwrap() {break;}
        }
        gpu.sync_to_cpu(&mut host)?;drop(gpu);
        if std::env::var_os("DIAGNOSTIC_FULL_QUERY").is_some() {host.ensure_symmetric();host.use_isomorphism=false;}
        let view=host.node_view(&[])?;
        let mut means=[0.;2];let mut masses=[0.;2];let mut rows=Vec::new();
        for p in 0..2 {
            let mut accum=vec![[0f64;5];NUM_CLASSES];
            for h in &view.players[p].hands {
                let k=class_index(rank(h.c1),rank(h.c2),suit(h.c1)==suit(h.c2));
                let w=h.reach as f64*h.valid as f64;
                if w<=0. {continue;}
                accum[k][0]+=w;accum[k][1]+=w*h.ev.unwrap() as f64;accum[k][2]+=w*h.eq.unwrap() as f64;
                means[p]+=w*h.ev.unwrap() as f64;masses[p]+=w;
            }
            for h in &host.exploit_view(&[],p)?.hands {
                let k=class_index(rank(h.c1),rank(h.c2),suit(h.c1)==suit(h.c2));
                let w=h.reach as f64*h.valid as f64;
                if w>0. {accum[k][3]+=w*h.br_ev.unwrap() as f64;accum[k][4]+=w;}
            }
            means[p]/=masses[p];
            rows.push(accum.iter().enumerate().filter(|(_,a)|a[0]>0.).map(|(k,a)|json!({
                "hand":class_label(k),"pair_mass":a[0],"ev_bb":a[1]/a[0],"equity":a[2]/a[0],
                "br_ev_bb":if a[4]>0. {Some(a[3]/a[4])} else {None}
            })).collect::<Vec<_>>());
        }
        eprintln!("DIAGNOSTIC means={means:?} masses={masses:?} pot={pot} defect={} gap={gap} iter={iter}",means[0]+means[1]-pot);
        assert!((masses[0]/masses[1]-1.).abs()<1e-5);
        let result=json!({"manifest_id":m["id"],"job":job,"iterations":iter,"gap_pct":gap,
            "target_met":gap<=m["target_gap_pct"].as_f64().unwrap(),"means_bb":means,"pair_mass":masses[0],
            "hands":rows,"trace":trace,"seconds":start.elapsed().as_secs_f64(),"engine":"CUDA DCFR; both-player CPU BR audit"});
        let tmp=out.with_extension("partial");
        std::fs::write(&tmp,serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())?;
        std::fs::rename(tmp,&out).map_err(|e|e.to_string())?;
        eprintln!("DONE {id}: {iter} iterations, {gap:.4}% gap, {:.1}s",start.elapsed().as_secs_f64());
        completed+=1;
    }
    Ok(())
}
