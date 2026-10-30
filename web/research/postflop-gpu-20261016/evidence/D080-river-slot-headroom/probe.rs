use std::{collections::HashMap,fs,hint::black_box,io::Write,path::Path,time::Instant};
use serde_json::{json,Value};
use solver::{Spot,SpotConfig};
use solver::game::Dealt;
use solver::tree::{KIND_ACTION,KIND_CHANCE,KIND_TERM_SHOWDOWN,SENTINEL};

#[inline(never)]
fn original(keys: &[usize], _domain: usize) -> (Vec<i32>,Vec<usize>) {
    let mut slot_of_key = HashMap::new();
    let mut node_river_slot = vec![-1i32; keys.len()];
    let mut slots = Vec::new();
    for ni in 0..keys.len() {
        if keys[ni] != usize::MAX {
            let next = slot_of_key.len();
            let s = *slot_of_key.entry(keys[ni]).or_insert(next);
            if s == slots.len() { slots.push(keys[ni]); }
            node_river_slot[ni] = s as i32;
        }
    }
    (node_river_slot,slots)
}
#[inline(never)]
fn indexed(keys: &[usize], domain: usize) -> (Vec<i32>,Vec<usize>) {
    let mut slot_by_key = vec![usize::MAX;domain];
    let mut node_river_slot = vec![-1i32;keys.len()];
    let mut slots = Vec::new();
    for ni in 0..keys.len() {
        if keys[ni] != usize::MAX {
            let entry = &mut slot_by_key[keys[ni]];
            if *entry == usize::MAX { *entry = slots.len(); slots.push(keys[ni]); }
            node_river_slot[ni] = *entry as i32;
        }
    }
    (node_river_slot,slots)
}
fn keys(spot:&Spot,use_iso:bool)->Vec<usize> {
    let mut out=vec![usize::MAX;spot.tree.nodes.len()];
    let iso_active=use_iso&&spot.suit_perms.len()>1;
    let mut stack=vec![(0u32,Dealt::default())];
    while let Some((id,dealt))=stack.pop() {
        let n=&spot.tree.nodes[id as usize];
        match n.kind {
            KIND_ACTION=>for a in 0..n.num_children as usize {
                stack.push((spot.tree.children[n.children_start as usize+a],dealt));
            },
            KIND_CHANCE=>{
                let valid=if iso_active {spot.perms_fixing(&dealt)}else{vec![0]};
                for c in 0..52u8 {
                    let child=spot.tree.children[n.children_start as usize+c as usize];
                    if child==SENTINEL||dealt.contains(c) {continue;}
                    let mut rep=c;
                    for &k in &valid {let pc=solver::cards::permute_card(c,&spot.suit_perms[k]);if pc<rep {rep=pc;}}
                    if c==rep {stack.push((child,dealt.push(c)));}
                }
            },
            KIND_TERM_SHOWDOWN=>{
                out[id as usize]=match spot.board.len() {
                    5=>0,4=>dealt.cards[0] as usize,
                    3=>dealt.cards[0].min(dealt.cards[1]) as usize*52+dealt.cards[0].max(dealt.cards[1]) as usize,
                    _=>unreachable!(),
                };
            },_=>{}
        }
    }
    out
}
fn dump_keys(path:&Path,words:&[usize]) {
    let mut f=fs::File::create(path).unwrap();
    for &v in words {f.write_all(&(v as u64).to_le_bytes()).unwrap();}
}
fn dump_slots(path:&Path,words:&[i32]) {
    let mut f=fs::File::create(path).unwrap();
    for &v in words {f.write_all(&v.to_le_bytes()).unwrap();}
}
fn main() {
    let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);
    let fixtures:Vec<Value>=serde_json::from_slice(&fs::read(&args[1]).unwrap()).unwrap();
    let out=Path::new(&args[2]);fs::create_dir(out).unwrap();
    for f in fixtures {
        let cfg:SpotConfig=serde_json::from_value(f["config"].clone()).unwrap();
        let spot=Spot::new(cfg).unwrap();assert_eq!(spot.tree.nodes.len() as u64,f["expected_nodes"].as_u64().unwrap());
        let domain=match spot.board.len(){3=>2704,4=>52,5=>1,_=>unreachable!()};
        for iso in [true,false] {
            let id=format!("{}-{}",f["id"].as_str().unwrap(),if iso{"iso"}else{"full"});
            let key=keys(&spot,iso);assert!(key.iter().all(|&k| k==usize::MAX||k<domain));
            let plan=solver::gpu::plan::GpuPlan::build(&spot,iso);
            let a=original(&key,domain);let b=indexed(&key,domain);
            assert_eq!(a,b);assert_eq!(a.0,plan.node_river_slot);assert_eq!(a.1.len(),plan.num_slots);
            dump_keys(&out.join(format!("{id}.keys.u64")),&key);
            dump_slots(&out.join(format!("{id}.original.i32")),&a.0);
            dump_slots(&out.join(format!("{id}.indexed.i32")),&b.0);
            dump_keys(&out.join(format!("{id}.ordered-keys.u64")),&a.1);
            drop(a);drop(b);drop(plan);
            // One predeclared warm-up per arm, excluded from timed samples.
            black_box(original(black_box(&key),domain));black_box(indexed(black_box(&key),domain));
            let mut samples=Vec::new();
            for pair in 0..9 {
                let order=if pair%2==0 {["original","indexed"]}else{["indexed","original"]};
                let mut values=serde_json::Map::new();
                for arm in order {
                    let start=Instant::now();
                    let result=if arm=="original"{original(black_box(&key),domain)}else{indexed(black_box(&key),domain)};
                    let ms=start.elapsed().as_secs_f64()*1000.0;
                    black_box(&result);drop(result);
                    values.insert(arm.to_owned(),json!(ms));
                }
                samples.push(json!({"pair":pair+1,"order":order,"ms":values}));
            }
            println!("D080_RESULT {}",json!({"id":id,"fixture":f["id"],"isomorphism":iso,"primary_iso":f["primary_iso"],"nodes":key.len(),"show_keys":key.iter().filter(|&&x|x!=usize::MAX).count(),"domain":domain,"indexed_temporary_bytes":domain*std::mem::size_of::<usize>(),"samples":samples,"full_original_plan_agreement":true}));
        }
    }
}
