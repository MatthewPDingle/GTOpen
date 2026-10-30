//! Payload planning for the stored bridge; optional small GPU constructor validation.
use serde_json::{json,Value};
use solver::{Spot,SpotConfig,TreeConfig,StreetSizing,parse_sizes,Solver,Algorithm};
use solver::gpu::{stored_capacity_plan,StoredContinuationGpu,StoredWorkspace};
use solver::preflop::equity::class_label;
use std::sync::Arc;
fn main() {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),4,"SUBTREE MANIFEST OUTPUT cpu|device");
    assert!(args[3]=="cpu" || args[3]=="device");let device=args[3]=="device";
    assert!(!std::path::Path::new(&args[2]).exists());
    let read=|p:&str|->Value{serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()};
    let d=read(&args[0]);let m=read(&args[1]);
    assert!(!device || m["boards"].as_array().unwrap().len()<=3,"device validation is bounded to three boards");
    let ranges:Vec<String>=(0..2).map(|p| {
        let w:Vec<f64>=(0..169).map(|c|d["incoming_class_mass"][p][c].as_f64().unwrap()/if c/13==c%13{6.}else if c/13>c%13{4.}else{12.}).collect();
        let max=w.iter().copied().fold(0.,f64::max);
        (0..169).filter(|&c|w[c]/max>=1e-5).map(class_label).collect::<Vec<_>>().join(",")
    }).collect();
    let menu=m["bet_menu"].as_str().unwrap();let mut rows=vec![];
    let sizing=StreetSizing{bet:parse_sizes(menu).unwrap(),raise:parse_sizes("100").unwrap(),donk:parse_sizes(menu).unwrap()};
    let mut workspace=StoredWorkspace::default();let mut games=vec![];let mut remaining=u64::MAX;
    let mut work=[0u64;11];let mut metadata=0;let mut host=0;let mut state=0;
    let mut constructor_gpu_peak=0;let mut max_explicit=0;let mut max_state=0;let mut max_pinned=0;
    for b in m["boards"].as_array().unwrap() {
        let board=b["board"].as_str().unwrap();
        for (pot,stack) in [(39.5,182.),(93.5,155.)] {
            let spot=Arc::new(Spot::new_with_limit(SpotConfig{board:board.into(),range_oop:ranges[0].clone(),range_ip:ranges[1].clone(),
                tree:TreeConfig{starting_pot:pot,effective_stack:stack,rake_pct:0.04,rake_cap:6.,max_raises:1,
                    oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing.clone()],..Default::default()}},Some(2_000_000)).unwrap());
            let mut row=stored_capacity_plan(&spot);
            if device {
                let mut solver=Solver::new(spot.clone());solver.algo=Algorithm::CfrPlus;solver.use_isomorphism=false;
                let game=StoredContinuationGpu::new(&solver,&mut workspace,std::path::Path::new("unused-ram-only"),games.len() as u64,&mut remaining).unwrap();
                assert_eq!(row,game.research_capacity_check());games.push(game);
            }
            let get=|key:&str|row[key].as_u64().unwrap();
            metadata+=get("retained_gpu_payload_bytes");host+=get("host_retained_payload_bytes");state+=get("canonical_state_bytes");
            max_state=max_state.max(get("canonical_state_bytes"));max_explicit=max_explicit.max(get("explicit_state_bytes"));max_pinned=max_pinned.max(get("constructor_pinned_bytes"));
            let components=row["workspace_components_bytes"].as_array().unwrap();
            constructor_gpu_peak=constructor_gpu_peak.max(metadata+work.iter().sum::<u64>()+components.iter().map(|x|x.as_u64().unwrap()).sum::<u64>());
            for (w,x) in work.iter_mut().zip(components) {*w=(*w).max(x.as_u64().unwrap());}
            if device {assert_eq!(workspace.bytes(),work.iter().sum::<u64>());}
            row["board"]=json!(board);row["pot"]=json!(pot);rows.push(row);
            println!("capacity {} {}: {} entries, state {:.3} GB, retained GPU {:.3} GB",board,pot,rows.len(),state as f64/1e9,metadata as f64/1e9);
        }
    }
    let result=json!({"manifest":m,"device_payload_validated":device,"rows":rows,
        "totals":{"canonical_state_bytes":state,"host_retained_payload_bytes":host,"ram_payload_total_bytes":host+state,
            "retained_gpu_payload_bytes":metadata,"shared_gpu_workspace_bytes":work.iter().sum::<u64>(),
            "steady_gpu_payload_bytes":metadata+work.iter().sum::<u64>(),"constructor_gpu_payload_upper_bytes":constructor_gpu_peak,
            "max_explicit_state_bytes":max_explicit,"max_canonical_state_bytes":max_state,"max_constructor_pinned_bytes":max_pinned},
        "note":"No solves or strategy changes. CPU mode never allocates CUDA. One spot planned at a time; totals project simultaneous retention. Payload excludes driver, allocator and process overhead, temporary CPU plans and evaluation scratch. Construction can hold two GPU workspaces. Reserve memory beyond totals; no assertion that the forest fits."});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
