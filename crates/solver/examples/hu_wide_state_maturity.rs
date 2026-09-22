//! Late-state storage probe with full hand support and a fixed changing-reach schedule.
//! CONTEXT OUTPUT_DIRECTORY REFERENCE_JSON. Engineering data, not a strategic solve.
use serde_json::{json,Value};
use solver::{Algorithm,Solver,Spot,SpotConfig,StreetSizing,TreeConfig,parse_sizes};
use solver::{cards::permute_card,game::Dealt,gpu::{SymmetricContinuationGpu,stored_capacity_plan},store::Store};
use solver::preflop::equity::{class_index,class_label};
use solver::tree::{KIND_ACTION,KIND_CHANCE,SENTINEL};
use std::{fs::{File,OpenOptions},io::{BufWriter,Read,Seek,SeekFrom,Write},path::Path,sync::Arc,time::Instant};

fn reaches(spot:&Spot, weights:&[Vec<f64>;2], t:u32)->[Vec<f32>;2] {
    std::array::from_fn(|p|spot.hands[p].iter().map(|h| {
        let c=class_index(h.c1/4,h.c2/4,h.c1%4==h.c2%4);
        if t==2 && p==0 {0.} else {
            (weights[p][c]*(0.02+((c*7+t as usize*3+p*11)%23) as f64/23.)) as f32
        }
    }).collect())
}

fn canonical_nodes(spot:&Spot)->Vec<usize> {
    let mut nodes=Vec::new();let mut todo=vec![(0u32,Dealt::default())];
    while let Some((i,dealt))=todo.pop() {
        let n=&spot.tree.nodes[i as usize];
        if n.kind==KIND_ACTION {
            nodes.push(i as usize);
            for a in 0..n.num_children as usize {todo.push((spot.tree.children[n.children_start as usize+a],dealt));}
        } else if n.kind==KIND_CHANCE {
            let perms=spot.perms_fixing(&dealt);
            for c in 0..52u8 {
                let child=spot.tree.children[n.children_start as usize+c as usize];
                if child==SENTINEL||dealt.contains(c) {continue;}
                if perms.iter().map(|&k|permute_card(c,&spot.suit_perms[k])).min().unwrap()==c {
                    todo.push((child,dealt.push(c)));
                }
            }
        }
    }
    nodes.sort_unstable();nodes
}

fn snapshot(host:&Solver,path:&Path,nodes:&[usize],expected_bytes:u64)->Result<Value,Box<dyn std::error::Error>> {
    let spot=&host.spot;
    let mut lengths=[0u64;2];
    for &i in nodes {
        let n=&spot.tree.nodes[i];lengths[n.player as usize]+=n.num_children as u64*spot.hands[n.player as usize].len() as u64;
    }
    // This probe is registered for the two-tone fixture where compact action
    // storage is used. Reject other layouts instead of inventing a fallback.
    assert_eq!(8*(lengths[0]+lengths[1]),expected_bytes);
    let mut writer=BufWriter::with_capacity(1024*1024,OpenOptions::new().write(true).create_new(true).open(path)?);
    let mut header=[0x47544f5353440001u64,0,0,host.iteration as u64,lengths[0],lengths[1],lengths[0],lengths[1],0];
    for x in header {writer.write_all(&x.to_le_bytes())?;}
    let mut hash=0xcbf29ce484222325u64;
    assert!(cfg!(target_endian="little"));
    for k in 0..4 {
        let p=k%2;let Store::F32(array)=(if k<2 {&host.regrets[p]} else {&host.strat[p]}) else {panic!("F32 required");};
        for &i in nodes {
            let n=&spot.tree.nodes[i];if n.player as usize!=p {continue;}
            let start=n.data_offset as usize;let len=n.num_children as usize*spot.hands[p].len();
            let values=&array.as_slice()[start..start+len];
            let bytes=unsafe{std::slice::from_raw_parts(values.as_ptr().cast::<u8>(),values.len()*4)};
            writer.write_all(bytes)?;
            for &v in values {hash^=v.to_bits() as u64;hash=hash.wrapping_mul(0x100000001b3);}
        }
    }
    writer.flush()?;writer.seek(SeekFrom::Start(64))?;writer.write_all(&hash.to_le_bytes())?;writer.flush()?;
    header[8]=hash;
    assert_eq!(std::fs::metadata(path)?.len(),expected_bytes+72);
    Ok(json!({"path":path,"header":header,"bytes":expected_bytes+72,"iteration":host.iteration}))
}

fn equal_files(a:&Path,b:&Path)->std::io::Result<()> {
    let mut a=File::open(a)?;let mut b=File::open(b)?;let mut left=vec![0;1024*1024];let mut right=left.clone();
    let mut n=a.metadata()?.len();assert_eq!(n,b.metadata()?.len());
    while n>0 {let take=(n as usize).min(left.len());a.read_exact(&mut left[..take])?;b.read_exact(&mut right[..take])?;
        assert_eq!(left[..take],right[..take],"resident/canonical checkpoint differs");n-=take as u64;}
    Ok(())
}

fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);
    let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let reference:Value=serde_json::from_slice(&std::fs::read(&args[2])?)?;
    let root=Path::new(&args[1]);assert!(root.is_dir()&&std::fs::read_dir(root)?.next().is_none());
    let weights:[Vec<f64>;2]=std::array::from_fn(|p| {
        let mut w:Vec<_>=(0..169).map(|c|context["incoming_class_mass"][p][c].as_f64().unwrap()/
            if c/13==c%13 {6.} else if c/13>c%13 {4.} else {12.}).collect();
        let max=w.iter().copied().fold(0.,f64::max);assert!(max>0.);
        for x in &mut w {*x/=max;if *x<1e-5 {*x=0.;}}w
    });
    let support:[usize;2]=std::array::from_fn(|p|weights[p].iter().filter(|&&v|v>0.).count());assert_eq!(support,[169,96]);
    let ranges:[String;2]=std::array::from_fn(|p|(0..169).filter(|&c|weights[p][c]>0.).map(class_label).collect::<Vec<_>>().join(","));
    let sizing=StreetSizing{bet:parse_sizes("50")?,raise:parse_sizes("100")?,donk:parse_sizes("50")?};
    let leaf=&context["nodes"][2]["leaf"];assert_eq!(leaf["type"],"postflop");
    let spot=Arc::new(Spot::new_with_limit(SpotConfig {board:"KsQd9d".into(),range_oop:ranges[0].clone(),range_ip:ranges[1].clone(),
        tree:TreeConfig{starting_pot:leaf["starting_pot"].as_f64().unwrap(),effective_stack:leaf["effective_stack"].as_f64().unwrap(),
            rake_pct:context["rake_fraction"].as_f64().unwrap(),rake_cap:context["rake_cap"].as_f64().unwrap(),
            max_raises:1,oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing],..Default::default()}},Some(2_000_000))?);
    let plan=stored_capacity_plan(&spot);let expected=plan["canonical_state_bytes"].as_u64().unwrap();
    let nodes=canonical_nodes(&spot);assert_eq!(nodes.len() as u64,plan["canonical_actions"].as_u64().unwrap());
    let mut host=Solver::new(spot.clone());host.algo=Algorithm::CfrPlus;host.use_isomorphism=false;
    let mut gpu=SymmetricContinuationGpu::new_explicit_reference(&host,20*1024*1024*1024)?;
    let began=Instant::now();let mut snapshots=Vec::new();let mut sweep_seconds=0.;let mut export_seconds=0.;
    for t in 1..=2000 {
        let reach=reaches(&spot,&weights,t);let start=Instant::now();
        for p in 0..2 {let v=gpu.sweep(p,t,&reach[p],&reach[1-p])?;assert!(v.iter().all(|x|x.is_finite()));}
        sweep_seconds+=start.elapsed().as_secs_f64();
        if [4,100,500,2000].contains(&t) {
            let start=Instant::now();gpu.sync_to_cpu(&mut host)?;
            let path=root.join(format!("iteration-{t:04}.bin"));let record=snapshot(&host,&path,&nodes,expected)?;
            if t==4 {equal_files(&path,Path::new(reference["path"].as_str().unwrap()))?;println!("MATURITY_REFERENCE_EXACT iteration=4");}
            snapshots.push(record);export_seconds+=start.elapsed().as_secs_f64();
        }
        if t%50==0 {println!("MATURITY_PROGRESS {}",json!({"iteration":t,"seconds":began.elapsed().as_secs_f64()}));}
    }
    let result=json!({"iterations":2000,"player_sweeps":4000,"snapshots":snapshots,"reference_at_four_exact":true,
        "support":support,"board":"KsQd9d","canonical_state_bytes":expected,"allocated_device_arena_bytes":gpu.arena_bytes(),
        "elapsed_seconds":began.elapsed().as_secs_f64(),"sweep_seconds":sweep_seconds,"export_seconds":export_seconds,
        "strategic_accuracy_claim":false,"convergence_claim":false,
        "note":"Registered deterministic changing reaches repeat every 23 iterations, plus zero BB reach at iteration 2. Late-state entropy probe only, not a fixed-game equilibrium or connected preflop training."});
    std::fs::write(root.join("result.json"),serde_json::to_vec_pretty(&result)?)?;println!("MATURITY_DONE {result}");
    Ok(())
}
