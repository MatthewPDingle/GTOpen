"""Freeze standalone accepted-planner slot lookup headroom diagnostic."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();ar.refuse_active(ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D080-river-slot-headroom';H.mkdir()
anchor=old.read(ROOT/'runs/E020C1/report.json')
fixtures=[{'id':x['fixture_id'],'config':x['config'],'expected_nodes':x['nodes'],'primary_iso':x['use_isomorphism']} for x in anchor['results']]
old.save(H/'fixtures.json',fixtures)
source=r'''use std::{collections::HashMap,fs,hint::black_box,io::Write,path::Path,time::Instant};
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
'''
(H/'probe.rs').write_text(source,encoding='utf-8')
manifest=old.read(ROOT/'binaries/SG-E020-postflop_autoresearch.manifest.json')
dep=manifest['dependency_artifact_sha256'];solver=[Path(p) for p in dep if Path(p).name.startswith('libsolver-') and Path(p).suffix=='.rlib'];assert len(solver)==1
deps=solver[0].parent
jsonlib=[Path(p) for p in dep if Path(p).name.startswith('libserde_json-') and Path(p).suffix=='.rlib'];assert len(jsonlib)==1
command=['rustc','--edition=2021',str(H/'probe.rs'),'--crate-name','d080_slot_headroom','--crate-type','bin','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1','--extern','solver='+str(solver[0]),'--extern','serde_json='+str(jsonlib[0]),'-L','dependency='+str(deps),'-o',str(H/'probe.exe')]
paths=[H/'probe.rs',H/'fixtures.json',ROOT/'binaries/SG-E020-postflop_autoresearch.manifest.json',ROOT/'runs/E020C1/report.json',ROOT/'comparisons/E049-three-pair-comparison/report.json',old.REPO/'crates/solver/src/gpu/plan.rs',old.REPO/'crates/solver/src/game.rs',ROOT/'runs/D041-initialization-source-audit/README.md']
old.save(H/'protocol.json',{'id':'D080','at':old.now(),'status':'FROZEN_PRE_COMPILE','scope':'Accepted E020 library; CPU-only Spot/GpuPlan and original versus indexed slot loop. No Solver/GPU context/kernel/solve, production activation or timing qualification.','command':command,'pairs':9,'fixed_pair_orders':['OI','IO','OI','IO','OI','IO','OI','IO','OI'],'warmups_per_arm':1,'cases':6,'raw_complete_keys_and_both_slot_maps_retained':True,'cpu_input_sha256':{str(x):old.sha(x) for x in paths},'dependency_artifact_sha256':{p:h for p,h in dep.items() if Path(p).suffix in ['.rlib','.lib']},'existing_complete_anchor_ms':old.read(ROOT/'comparisons/E049-three-pair-comparison/report.json')['performance']['baseline_full_cycle_ms'],'headroom_rule':'Report current isolated original and saved loop medians relative to historical B146-148 full-cycle anchor only as a scale diagnostic. If even full loop removal has no1% evidence, decline full candidate. No isolated speed claim is complete-cycle qualification.','limits':'Derived keys use original DFS/key expressions; actual accepted GpuPlan slot-map equality is required before timing. Compiled standalone loops can differ from integrated optimization. Root replay is not external independent review.'})
published={}
for name in ['probe.rs','fixtures.json','protocol.json']:
 src=H/name;key=H.name+'/'+name;dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-compile-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);st.update(state='running',stage='D080 bounded river-slot headroom diagnostic',activity='Measure accepted planner HashMap slot lookup against an exact direct index before admitting a full candidate. No new gain.',updated_at=ar.now());st['evidence'].append({'label':'D080 fixed CPU headroom protocol','url':'evidence/D080-river-slot-headroom/protocol.json'});ar.atomic_json(ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'solver_rlib':str(solver[0]),'published':len(published)}),flush=True)
