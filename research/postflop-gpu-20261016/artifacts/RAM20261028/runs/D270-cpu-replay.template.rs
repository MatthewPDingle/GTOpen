#[cfg(test)]
mod d270_cpu_replay {
use super::{arena::ArenaLayout, metadata, plan::GpuPlan};
use crate::{Solver, Spot, SpotConfig, store::Storage};
use std::{fs::{File,OpenOptions}, io::{BufWriter,Write}, path::Path, sync::Arc};
use serde_json::{json, Value};

@ENCODER@

fn begin_projection(path: &Path, fields: u32) -> BufWriter<File> {
    let mut w = BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());
    w.write_all(b"D267-MODEL-v1\0\0\0").unwrap(); fields.encode(&mut w); w
}
fn projected<T: Encode>(w: &mut impl Write, name: &str, values: &[T], width: u32) {
    (name.len() as u32).encode(w); w.write_all(name.as_bytes()).unwrap();
    width.encode(w); (values.len() as u64).encode(w);
    for v in values { assert_eq!(v.size(), width as u64); v.encode(w); }
}
fn finish(mut w: BufWriter<File>) { w.flush().unwrap(); w.get_ref().sync_all().unwrap(); }
fn dump_projection(path: &Path, p: &GpuPlan, locks: &[u64], children: &[u32]) {
    let mut w = begin_projection(path, 23);
    macro_rules! row { ($field:ident, $width:expr) => { projected(&mut w, stringify!($field), &p.$field, $width); }; }
    row!(node_player,4); row!(node_na,4); row!(node_data_off,8); row!(node_children_start,4);
    row!(node_twin,4); row!(node_tlose,4); row!(node_ttie,4); row!(node_cdiv,4);
    row!(node_river_slot,4); row!(cc_start,4); row!(cc_count,4); row!(cfv_slot,4);
    projected(&mut w,"reach_slot[0]",&p.reach_slot[0],4);
    projected(&mut w,"reach_slot[1]",&p.reach_slot[1],4);
    projected(&mut w,"d_lock_off",locks,8);
    row!(action_nodes,4); row!(chance_nodes,4); row!(fold_nodes,4); row!(show_nodes,4);
    row!(chance_parents,4); row!(chance_children,4); row!(cc_child,4);
    projected(&mut w,"tree.children",children,4); finish(w);
}
fn read_u64_file(path: &str) -> Vec<u64> {
    let b = std::fs::read(path).unwrap(); assert_eq!(b.len()%8,0);
    b.chunks_exact(8).map(|x|u64::from_le_bytes(x.try_into().unwrap())).collect()
}
fn guarded_scratch(words: &mut [u64], len: usize) -> &mut [f32] {
    assert!(words.len()*2 >= len+64);
    unsafe { std::slice::from_raw_parts_mut(words.as_mut_ptr().add(16).cast(),len) }
}
fn check_scratch(words: &[u64], len: usize, written: usize) -> usize {
    let b = unsafe {std::slice::from_raw_parts(words.as_ptr().cast::<u8>(),words.len()*8)};
    let pattern = 0x7ffd_0123_89ab_cdefu64.to_ne_bytes();
    assert!(written <= len*4);
    let mut checks = 0;
    for (i,&v) in b.iter().enumerate() {
        if i<128 || i>=128+written { assert_eq!(v,pattern[i%8],"scratch byte {i}"); checks+=1; }
    }
    checks
}
fn boundary_checks(p: &mut GpuPlan, layouts: &mut [ArenaLayout;2], scratch: &mut [f32], children: usize, solver: &Solver) -> usize {
    let mut checks = 0;
    let old = p.num_nodes; p.num_nodes=usize::MAX;
    assert!(!metadata::eligible(p,layouts,scratch,children)); checks+=1; p.num_nodes=old;
    assert!(!metadata::eligible(p,layouts,scratch,usize::MAX)); checks+=1;
    let last=p.reach_src[0].pop().unwrap();
    assert!(!metadata::eligible(p,layouts,scratch,children)); checks+=1; p.reach_src[0].push(last);
    let need=(p.num_nodes*2).max(children); assert!(need>0 && need<=scratch.len());
    assert!(!metadata::eligible(p,layouts,&mut scratch[..need-1],children)); checks+=1;
    if scratch.len()>need {
        assert!(!metadata::eligible(p,layouts,&mut scratch[1..],children)); checks+=1;
    }
    let mut full=GpuPlan::build(&solver.spot,solver.use_isomorphism);
    full.use_full_action_arenas(&solver.spot);
    let mut original=[ArenaLayout::new(solver,&full,0),ArenaLayout::new(solver,&full,1)];
    assert!(original.iter().all(|x|!x.is_compact()));
    for player in 0..2 {
        std::mem::swap(&mut layouts[player],&mut original[player]);
        assert!(!metadata::eligible(p,layouts,scratch,children)); checks+=1;
        std::mem::swap(&mut layouts[player],&mut original[player]);
    }
    assert!(!metadata::eligible(p,&original,scratch,children)); checks+=1;
    checks
}

#[test]
fn production_metadata_replay() {
    let fixtures:Vec<Value>=serde_json::from_str(include_str!(r"@FIXTURES@")).unwrap();
    assert_eq!(fixtures.len(),6);
    let output=Path::new(r"@OUTPUT@"); std::fs::create_dir(output).unwrap();
    let exception_bits=[0u32,0x8000_0000,1,0x8000_0001,0x3f80_0000,0xbf80_0000,
        0x7f80_0000,0xff80_0000,0x7fc0_0123,0x7f80_0123,0xffc0_0456,0xff80_0456];
    let mut total_cases=0;
    for f in fixtures {
        let id=f["id"].as_str().unwrap();
        let config:SpotConfig=serde_json::from_value(f["config"].clone()).unwrap();
        let spot=Arc::new(Spot::new(config).unwrap());
        assert_eq!(spot.tree.nodes.len() as u64,f["expected_nodes"].as_u64().unwrap());
        let child_source=std::fs::read(f["children_path"].as_str().unwrap()).unwrap();
        assert_eq!(child_source.len(),spot.tree.children.len()*4);
        assert!(spot.tree.children.iter().zip(child_source.chunks_exact(4)).all(|(&x,b)|x==u32::from_le_bytes(b.try_into().unwrap())));
        let mut solver=Solver::with_storage(spot.clone(),Storage::Compressed);
        solver.use_isomorphism=f["use_iso"].as_bool().unwrap();
        for arm in ["actual","exceptional","selected"] {
            let name=format!("{id}--{arm}");
            let mut p=GpuPlan::build(&spot,solver.use_isomorphism);
            let mut layouts=[ArenaLayout::new(&solver,&p,0),ArenaLayout::new(&solver,&p,1)];
            let compact=layouts.each_ref().map(|x|x.is_compact());
            let nn=p.num_nodes;
            let scratch_len=p.arena_elements[0].max(p.arena_elements[1]);
            let mut words=vec![0x7ffd_0123_89ab_cdefu64;(scratch_len+1)/2+32];
            let boundaries=if arm=="actual" {
                boundary_checks(&mut p,&mut layouts,guarded_scratch(&mut words,scratch_len),spot.tree.children.len(),&solver)
            } else {0};
            dump_baseline(&p,&output.join(format!("{name}.before.plan.bin")));
            for player in 0..2 { layouts[player].d270_dump(&output.join(format!("{name}.p{player}.before.arena.bin"))); }
            let capable=metadata::eligible(&p,&layouts,guarded_scratch(&mut words,scratch_len),spot.tree.children.len());
            assert_eq!(capable,compact[0]&&compact[1]); // canonical scratch is large/aligned, checked above
            let ordered=arm!="selected" || capable;
            let mut lock_bits=if arm=="exceptional" {
                (0..nn).map(|i|if i%3==0 {(i*16)as u64}else{u64::MAX}).collect::<Vec<_>>()
            } else {read_u64_file(f["locks_path"].as_str().unwrap())};
            assert_eq!(lock_bits.len(),nn);
            if arm=="exceptional" {
                for (field,values) in [&mut p.node_twin,&mut p.node_tlose,&mut p.node_ttie,&mut p.node_cdiv].into_iter().enumerate() {
                    for (i,v) in values.iter_mut().enumerate() { *v=f32::from_bits(exception_bits[(i+3*field)%exception_bits.len()]); }
                }
            }
            if ordered {
                // All i64/u64 bit patterns are valid; this view preserves the captured lock bits.
                let locks=unsafe{std::slice::from_raw_parts_mut(lock_bits.as_mut_ptr().cast::<i64>(),lock_bits.len())};
                metadata::prepare(&mut p,&mut layouts,locks,guarded_scratch(&mut words,scratch_len));
            }
            let children=if ordered {
                metadata::children_image(&spot.tree.children,&p.reach_src[0],guarded_scratch(&mut words,scratch_len)).to_vec()
            } else {spot.tree.children.clone()};
            dump_baseline(&p,&output.join(format!("{name}.after.plan.bin")));
            dump_projection(&output.join(format!("{name}.projection.bin")),&p,&lock_bits,&children);
            let identity:Vec<u32>=if ordered {Vec::new()}else{(0..nn as u32).collect()};
            let forward=if ordered {&p.reach_src[0]}else{&identity};
            let inverse=if ordered {&p.reach_src[1]}else{&identity};
            let mut map_out=begin_projection(&output.join(format!("{name}.maps.bin")),2);
            projected(&mut map_out,"old_to_new",forward,4);projected(&mut map_out,"new_to_old",inverse,4);finish(map_out);
            let mut record_checks=0;
            for (node,n) in spot.tree.nodes.iter().enumerate() {
                for player in 0..2 {
                    let actual=layouts[player].device_node(node as u32);
                    let expected=if compact[player] && n.kind==crate::tree::KIND_ACTION && n.player as usize==player {Some(forward[node])}else{None};
                    assert_eq!(actual,expected); record_checks+=1;
                }
            }
            for player in 0..2 { layouts[player].d270_dump(&output.join(format!("{name}.p{player}.after.arena.bin"))); }
            let written=if ordered {(nn*8).max(children.len()*4)}else{0};
            let guard_checks=check_scratch(&words,scratch_len,written);
            println!("\nD270_CASE {}",json!({"id":id,"arm":arm,"ordered":ordered,"capable":capable,"compact":compact,"nodes":nn,"scratch_elements":scratch_len,"boundary_checks":boundaries,"scratch_guard_bytes_checked":guard_checks,"record_lookup_checks":record_checks,"whole_plan_fields":53,"projected_arrays":23,"actual_production_function_calls":if ordered{3}else{1},"CUDA_calls":0,"GPU_solves":0,"speed_samples":0}));
            std::io::stdout().flush().unwrap();total_cases+=1;
        }
    }
    assert_eq!(total_cases,18);
    println!("D270_COMPLETE {}",json!({"cases":total_cases,"CUDA_calls":0,"GPU_solves":0,"speed_samples":0}));
}
}
