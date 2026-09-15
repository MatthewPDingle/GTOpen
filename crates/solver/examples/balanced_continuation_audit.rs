//! Offline fixed-range continuation audit; never connects to the app.
//! prepare SAVE OUTPUT or run MANIFEST [JOB_LIMIT]. GPU feature required to run.
use serde_json::{json, Value};
use solver::preflop::{PreflopSolver, RealizationFit, equity::{class_index, class_label, class_prob, EquityTable, NUM_CLASSES}};
use solver::{rank, suit, Solver, Spot, SpotConfig, Storage};
use std::{sync::Arc, time::Instant};

const PROBES: [&str; 6] = ["99", "88", "55", "A5s", "QJs", "TT"];
fn dist(weights: &[f32]) -> Vec<f32> {
    let mut d: Vec<f32> = weights.iter().enumerate().map(|(h,w)| w*class_prob(h)).collect();
    let z:f32=d.iter().sum(); assert!(z>0.0);
    for v in &mut d {*v/=z;} d
}
fn prices(weights: &[Vec<f32>], pot:f64, stack:f64, eq:&EquityTable, fit:&RealizationFit) -> Value {
    let d:Vec<_>=weights.iter().map(|w|dist(w)).collect();
    let blend=(stack/pot/8.0).min(1.0) as f32;
    let mut all=Vec::new(); let mut means=[0.0;2];
    for p in 0..2 {
        let mut rows=Vec::new();
        for h in 0..NUM_CLASSES {
            let mut raw=0.0f32; let mut rel=0.0f32;
            for j in 0..NUM_CLASSES {
                let e=if h==j {0.5} else {0.5*(eq.eq(h,j)+1.0-eq.eq(j,h))};
                raw+=d[1-p][j]*e;
                rel+=d[1-p][j]*fit.balanced_share(e,h,j,p==0);
            }
            let value=pot*(raw+blend*(rel-raw)) as f64;
            means[p]+=d[p][h] as f64*value;
            rows.push(json!({"hand":class_label(h),"value_bb":value,"raw_bb":pot*raw as f64}));
        }
        all.push(rows);
    }
    assert!((means.iter().sum::<f64>()-pot).abs()<1e-3);
    json!({"mean_bb":means,"hands":all})
}
fn prepare(save:&str, output:&str) -> Result<(),String> {
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
    let s=PreflopSolver::load_game(save,eq.clone())?;
    assert_eq!(s.cfg.realization,"balanced"); assert_eq!(s.cfg.rake_pct,0.0);
    assert_eq!(s.cfg.posts,vec![2.0,0.0,0.0,0.0,0.0,0.0,0.5,1.0]);
    let fit=s.fit.as_ref().ok_or("missing balanced fit")?;
    let before=s.arena_snapshot(); let mut cases=Vec::new();
    for (name,initial) in [("call",1),("threebet",2)] {
        let mut path=vec![1,initial];
        loop {
            let v=s.node_view(&path)?;
            if v.kind!="action" {break;}
            let kind=if v.actor==Some(1) {"call"} else {"fold"};
            let a=v.actions.iter().position(|a|a.kind==kind).ok_or("expected action missing")?;
            path.push(a);
        }
        let v=s.node_view(&path)?; let ex=s.export_spot(&path)?;
        assert_eq!((ex.oop_pos.as_str(),ex.ip_pos.as_str()),("UTG1","MP"));
        let original=vec![v.reaches_all[1].clone(),v.reaches_all[2].clone()];
        let base=prices(&original,ex.pot_bb,ex.eff_stack_bb,&eq,fit);
        let live_price=v.continuation.as_ref().ok_or("missing terminal estimate")?;
        for p in 0..2 {assert!((base["mean_bb"][p].as_f64().unwrap()-live_price.players[p].value_bb).abs()<2e-4);}
        let mut weights=original.clone(); let mut dropped=Vec::new(); let mut added=Vec::new();
        for p in 0..2 {
            let max=weights[p].iter().copied().fold(0.0f32,f32::max);
            for w in &mut weights[p] {*w/=max;}
            let pre:f32=weights[p].iter().enumerate().map(|(h,w)|class_prob(h)*w).sum();
            let mut removed=0.0;
            for (h,w) in weights[p].iter_mut().enumerate() {if *w<0.005 {removed+=class_prob(h)* *w;*w=0.0;}}
            dropped.push(removed/pre);
            let mut probe_mass=0.0;
            if p==1 {for (h,w) in weights[p].iter_mut().enumerate() {
                if PROBES.contains(&class_label(h).as_str()) && *w<0.0001 {
                    probe_mass+=class_prob(h)*(0.0001-*w); *w=0.0001;
                }
            }}
            added.push(probe_mass/pre);
            assert!(removed/pre<0.005,"range truncation too large");
        }
        let range=|p:usize| weights[p].iter().enumerate().filter(|(_,w)|**w>0.0)
            .map(|(h,w)|format!("{}:{:.9}",class_label(h),w)).collect::<Vec<_>>().join(",");
        cases.push(json!({"id":name,"path":path,"branch_probability":v.branch_probability,
            "pot":ex.pot_bb,"stack":ex.eff_stack_bb,"original_weights":original,"weights":weights,
            "range_oop":range(0),"range_ip":range(1),"removed_mass_fraction":dropped,"probe_added_mass_fraction":added,
            "original_balanced":base,"balanced":prices(&weights,ex.pot_bb,ex.eff_stack_bb,&eq,fit)}));
    }
    assert_eq!(before,s.arena_snapshot());
    let out=json!({"save":save,"iteration":s.iteration,"config":s.cfg,"cases":cases,
        "canonical_flops":solver::canonical_flops(),"probes":PROBES});
    std::fs::write(output,serde_json::to_vec_pretty(&out).unwrap()).map_err(|e|e.to_string())
}
#[cfg(feature="gpu")]
fn run(manifest:&str,limit:usize) -> Result<(),String> {
    use solver::gpu::GpuSolver;
    let m:Value=serde_json::from_str(&std::fs::read_to_string(manifest).map_err(|e|e.to_string())?).unwrap();
    let root=std::path::Path::new(manifest).parent().unwrap();
    std::fs::create_dir_all(root.join("jobs")).map_err(|e|e.to_string())?;
    let mut completed=0;
    for job in m["jobs"].as_array().unwrap() {
        let id=job["id"].as_str().unwrap(); let out=root.join("jobs").join(format!("{id}.json"));
        if out.exists() {
            let old:Value=serde_json::from_str(&std::fs::read_to_string(&out).unwrap()).unwrap();
            if old["job"]!=*job || old["manifest_id"]!=m["id"] {return Err("checkpoint mismatch".into());}
            if old["target_met"]==true {continue;}
        }
        if completed>=limit {break;}
        let cfg:SpotConfig=serde_json::from_value(job["config"].clone()).map_err(|e|e.to_string())?;
        eprintln!("BUILD {id}"); let start=Instant::now(); let pot=cfg.tree.starting_pot;
        let mut host=Solver::with_storage(Arc::new(Spot::new(cfg)?),Storage::Compressed);
        let mut gpu=GpuSolver::new_with_budget(&host,12*1024*1024*1024)?;
        let mut trace=Vec::new(); let mut gap=f64::INFINITY; let mut iter=0;
        while iter<m["max_iterations"].as_u64().unwrap() {
            for _ in 0..25 {gpu.iterate()?;iter+=1;}
            gap=gpu.exploitability(&host)?/pot*100.0;
            trace.push(json!({"iteration":iter,"gap_pct":gap,"seconds":start.elapsed().as_secs_f64()}));
            eprintln!("{id} {iter} gap={gap:.4}% {:.1}s",start.elapsed().as_secs_f64());
            if gap<=m["target_gap_pct"].as_f64().unwrap() {break;}
        }
        gpu.sync_to_cpu(&mut host)?; drop(gpu);
        let view=host.node_view(&[])?;
        let br=host.exploit_view(&[],1)?;
        let mut means=[0.0;2];let mut masses=[0.0;2];let mut rows=Vec::new();
        for p in 0..2 {
            let mut accum=vec![[0.0f64;5];NUM_CLASSES];
            for h in &view.players[p].hands {
                let k=class_index(rank(h.c1),rank(h.c2),suit(h.c1)==suit(h.c2));
                let w=h.reach as f64*h.valid as f64;
                if w<=0.0 {continue;}
                let a=&mut accum[k];a[0]+=w;a[1]+=w*h.ev.unwrap() as f64;a[2]+=w*h.eq.unwrap() as f64;
                means[p]+=w*h.ev.unwrap() as f64;masses[p]+=w;
            }
            if p==1 {for h in &br.hands {
                let k=class_index(rank(h.c1),rank(h.c2),suit(h.c1)==suit(h.c2));
                let w=h.reach as f64*h.valid as f64;
                if w>0.0 {accum[k][3]+=w*h.br_ev.unwrap() as f64;accum[k][4]+=w;}
            }}
            means[p]/=masses[p];
            rows.push(accum.iter().enumerate().filter(|(_,a)|a[0]>0.0).map(|(k,a)|json!({
                "hand":class_label(k),"pair_mass":a[0],"ev_bb":a[1]/a[0],"equity":a[2]/a[0],
                "br_ev_bb":if a[4]>0.0 {Some(a[3]/a[4])} else {None}
            })).collect::<Vec<_>>());
        }
        assert!((means[0]+means[1]-pot).abs()<0.002,"pot accounting failed");
        assert!((masses[0]/masses[1]-1.0).abs()<1e-5);
        let result=json!({"manifest_id":m["id"],"job":job,"iterations":iter,"gap_pct":gap,
            "target_met":gap<=m["target_gap_pct"].as_f64().unwrap(),"means_bb":means,"pair_mass":masses[0],
            "hands":rows,"trace":trace,"seconds":start.elapsed().as_secs_f64(),"engine":"CUDA DCFR / compressed host query"});
        let tmp=out.with_extension("partial");
        std::fs::write(&tmp,serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())?;
        std::fs::rename(tmp,&out).map_err(|e|e.to_string())?;
        eprintln!("DONE {id} {:.1}s",start.elapsed().as_secs_f64());completed+=1;
    }
    Ok(())
}
fn main()->Result<(),String> {
    rayon::ThreadPoolBuilder::new().num_threads(12).build_global().unwrap();
    let a:Vec<_>=std::env::args().collect();
    match a.get(1).map(String::as_str) {
        Some("prepare")=>prepare(&a[2],&a[3]),
        #[cfg(feature="gpu")]
        Some("run")=>run(&a[2],a.get(3).map_or(usize::MAX,|s|s.parse().unwrap())),
        _=>Err("prepare SAVE OUTPUT or run MANIFEST [JOB_LIMIT] (GPU feature)".into())
    }
}
