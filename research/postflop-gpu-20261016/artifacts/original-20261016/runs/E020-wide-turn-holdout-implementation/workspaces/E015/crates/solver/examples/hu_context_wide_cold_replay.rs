//! Full-support cold recovery control. CONTEXT BOARD OUTPUT_DIRECTORY [AUDIT_FILES...]
//! Reference and candidate run sequentially. No tree/range reduction or production use.
use serde_json::{json, Value};
use solver::{Algorithm, Solver, Spot, SpotConfig, StreetSizing, TreeConfig, parse_sizes};
use solver::gpu::{StoredContinuationGpu, StoredWorkspace};
use solver::preflop::equity::{class_index, class_label};
use std::{fs::File, io::Read, path::{Path,PathBuf}, sync::Arc, time::Instant};

fn files_equal(a: &Path, b: &Path) -> std::io::Result<()> {
    let mut a=File::open(a)?;let mut b=File::open(b)?;
    assert_eq!(a.metadata()?.len(),b.metadata()?.len());
    let mut left=vec![0u8;1024*1024];let mut right=vec![0u8;1024*1024];
    let mut remaining=a.metadata()?.len();
    while remaining>0 {
        let take=(remaining as usize).min(left.len());
        a.read_exact(&mut left[..take])?;b.read_exact(&mut right[..take])?;
        assert_eq!(left[..take],right[..take],"checkpoint byte mismatch");
        remaining-=take as u64;
    }
    Ok(())
}

fn reaches(spot:&Spot, weights:&[Vec<f64>;2], t:u32)->[Vec<f32>;2] {
    std::array::from_fn(|p|spot.hands[p].iter().map(|h| {
        let c=class_index(h.c1/4,h.c2/4,h.c1%4==h.c2%4);
        if t==2 && p==0 {0.} else {
            (weights[p][c]*(0.02+((c*7+t as usize*3+p*11)%23) as f64/23.)) as f32
        }
    }).collect())
}

fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();assert!(args.len()>=3);
    for p in &args[3..] {assert!(Path::new(p).is_file(),"audit input missing");}
    let data:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    assert_eq!(data["schema"],"hu-context-v1");
    assert_eq!(data["positions"],json!(["BB","BTN"]));
    let root=PathBuf::from(&args[2]);
    assert!(root.is_dir() && std::fs::read_dir(&root)?.next().is_none(),"empty dedicated output directory required");
    let leaf=&data["nodes"][2]["leaf"];assert_eq!(leaf["type"],"postflop");
    let weights:[Vec<f64>;2]=std::array::from_fn(|p| {
        let mut w:Vec<_>=(0..169).map(|c|data["incoming_class_mass"][p][c].as_f64().unwrap()/
            if c/13==c%13 {6.} else if c/13>c%13 {4.} else {12.}).collect();
        let max=w.iter().copied().fold(0.,f64::max);assert!(max>0.);
        for x in &mut w {*x/=max;if *x<1e-5 {*x=0.;}}
        w
    });
    let support:[usize;2]=std::array::from_fn(|p|weights[p].iter().filter(|&&v|v>0.).count());
    assert_eq!(support,[169,96]);
    let ranges:[String;2]=std::array::from_fn(|p|(0..169).filter(|&c|weights[p][c]>0.).map(class_label).collect::<Vec<_>>().join(","));
    let sizing=StreetSizing{bet:parse_sizes("50")?,raise:parse_sizes("100")?,donk:parse_sizes("50")?};
    let spot=Arc::new(Spot::new_with_limit(SpotConfig {
        board:args[1].clone(),range_oop:ranges[0].clone(),range_ip:ranges[1].clone(),
        tree:TreeConfig {starting_pot:leaf["starting_pot"].as_f64().unwrap(),
            effective_stack:leaf["effective_stack"].as_f64().unwrap(),
            rake_pct:data["rake_fraction"].as_f64().unwrap(),rake_cap:data["rake_cap"].as_f64().unwrap(),
            max_raises:1,oop:[sizing.clone(),sizing.clone(),sizing.clone()],
            ip:[sizing.clone(),sizing.clone(),sizing],..Default::default()},
    },Some(2_000_000))?);
    let began=Instant::now();let mut bytes_written=0u64;
    let mut expected_values=Vec::new();let mut descriptors=Vec::new();
    let mut reconstruct_seconds=0.;let mut candidate_sweep_seconds=0.;let mut save_seconds=0.;
    let mut max_workspace=0;
    {
        let mut host=Solver::new(spot.clone());host.algo=Algorithm::CfrPlus;host.use_isomorphism=false;
        let mut workspace=StoredWorkspace::default();let mut ram=u64::MAX;
        let mut reference=StoredContinuationGpu::new(&host,&mut workspace,&root,0,&mut ram)?;
        drop(host);
        for t in 1..=4 {for p in 0..2 {
            let r=reaches(&spot,&weights,t);
            expected_values.push(reference.sweep(&mut workspace,p,t,&r[p],&r[1-p])?);
            let step=expected_values.len()-1;
            let dest=root.join(format!("reference-step-{step:02}"));
            assert!(bytes_written+reference.storage_bytes+72<=64*1024*1024*1024,"write budget");
            std::fs::create_dir(&dest)?;
            descriptors.push(reference.checkpoint_export(&dest,0,t)?);
            bytes_written+=reference.storage_bytes+72;
            println!("WIDE_REFERENCE {}",json!({"step":step,"iteration":t,"player":p,"elapsed":began.elapsed().as_secs_f64()}));
        }}
        max_workspace=max_workspace.max(workspace.bytes());
    }
    // The entire reference GPU object and workspace are gone before this phase.
    let mut previous:Option<(PathBuf,u32,[u64;8])>=None;
    for t in 1..=4 {for p in 0..2 {
        let step=(t as usize-1)*2+p;
        let start=Instant::now();
        let mut host=Solver::new(spot.clone());host.algo=Algorithm::CfrPlus;host.use_isomorphism=false;
        let mut workspace=StoredWorkspace::default();let mut ram=u64::MAX;
        let mut candidate=StoredContinuationGpu::new(&host,&mut workspace,&root,0,&mut ram)?;
        drop(host);
        if let Some((path,iteration,descriptor))=&previous {candidate.checkpoint_import(path,0,*iteration,*descriptor)?;}
        reconstruct_seconds+=start.elapsed().as_secs_f64();
        let r=reaches(&spot,&weights,t);let start=Instant::now();
        let actual=candidate.sweep(&mut workspace,p,t,&r[p],&r[1-p])?;
        candidate_sweep_seconds+=start.elapsed().as_secs_f64();
        assert_eq!(actual.len(),expected_values[step].len());
        assert!(actual.iter().zip(&expected_values[step]).all(|(a,b)|a.to_bits()==b.to_bits()),"CFV mismatch");
        let dest=root.join(format!("candidate-step-{step:02}"));
        assert!(bytes_written+candidate.storage_bytes+72<=64*1024*1024*1024,"write budget");
        std::fs::create_dir(&dest)?;let start=Instant::now();
        let descriptor=candidate.checkpoint_export(&dest,0,t)?;
        save_seconds+=start.elapsed().as_secs_f64();
        bytes_written+=candidate.storage_bytes+72;
        assert_eq!(descriptor,descriptors[step]);
        files_equal(&root.join(format!("reference-step-{step:02}/entry-0-generation-0.bin")),&dest.join("entry-0-generation-0.bin"))?;
        max_workspace=max_workspace.max(workspace.bytes());
        previous=Some((dest,t,descriptor));
        drop(candidate);drop(workspace);
        println!("WIDE_COLD_PASS {}",json!({"step":step,"iteration":t,"player":p,"passed":true,"elapsed":began.elapsed().as_secs_f64()}));
    }}
    let result=json!({"passes":8,"board":args[1],"preflop_leaf":2,"entry_support":support,
        "postflop_tree":spot.config.tree,"postflop_hands":[spot.hands[0].len(),spot.hands[1].len()],
        "all_values_bitwise_equal":true,"all_checkpoint_bytes_equal":true,
        "reference_and_candidate_gpu_sequential":true,"includes_zero_reach_and_reentry":true,
        "max_workspace_bytes":max_workspace,"bytes_written":bytes_written,
        "candidate_reconstruction_seconds":reconstruct_seconds,"candidate_sweep_seconds":candidate_sweep_seconds,
        "candidate_save_seconds":save_seconds,"elapsed_seconds":began.elapsed().as_secs_f64(),
        "full_forest_admitted":false,"strategic_result":false,
        "note":"Actual full-support single call continuation and unchanged action menu. Four-iteration recovery control only, not converged play or proof of other branches/full panel capacity."});
    std::fs::write(root.join("result.json"),serde_json::to_vec_pretty(&result)?)?;
    println!("WIDE_COLD_SUMMARY {result}");
    Ok(())
}
