//! Private GPU metadata row projection; CPU tree and physical arenas stay fixed.
use super::{arena::ArenaLayout, plan::GpuPlan};

pub(super) fn eligible(plan: &GpuPlan, layouts: &[ArenaLayout; 2], scratch: &mut [f32], children: usize) -> bool {
    let Some(node_bytes) = plan.num_nodes.checked_mul(8) else { return false; };
    let Some(child_bytes) = children.checked_mul(4) else { return false; };
    let Some(scratch_bytes) = scratch.len().checked_mul(4) else { return false; };
    layouts.iter().all(ArenaLayout::is_compact)
        && plan.reach_src.iter().all(|v| v.len() == plan.num_nodes)
        && node_bytes.max(child_bytes) <= scratch_bytes
        && (scratch.as_mut_ptr() as usize) % 8 == 0
}

// These CPU-only reach-owner vectors are dead after the original plan builder
// creates dense reach_slot. Reuse them as constructor-local forward/inverse maps.
pub(super) fn build_map(plan: &mut GpuPlan) {
    let [forward, inverse] = &mut plan.reach_src;
    forward.fill(u32::MAX);
    let mut next = 0;
    for level in 0..plan.num_levels {
        for (nodes, spans) in [(&plan.action_nodes, &plan.action_spans),
            (&plan.chance_nodes, &plan.chance_node_spans),
            (&plan.fold_nodes, &plan.fold_spans), (&plan.show_nodes, &plan.show_spans)] {
            let span = spans[level];
            for &old in &nodes[span.start as usize..(span.start + span.count) as usize] {
                assert_eq!(forward[old as usize], u32::MAX);
                forward[old as usize] = next as u32;
                inverse[next] = old;
                next += 1;
            }
        }
    }
    for old in 0..plan.num_nodes {
        if forward[old] == u32::MAX {
            forward[old] = next as u32;
            inverse[next] = old as u32;
            next += 1;
        }
    }
    assert_eq!(next, plan.num_nodes);
    assert_eq!(forward[0], 0);
}

// Private calls use only u32/i32/u64/i64/f32, each admitting all bit patterns.
// Scratch is disjoint pinned memory with checked length and 8-byte alignment.
fn rows<T: Copy>(values: &mut [T], inverse: &[u32], scratch: &mut [f32]) {
    assert_eq!(values.len(), inverse.len());
    assert!(values.len().checked_mul(std::mem::size_of::<T>()).unwrap() <= scratch.len() * 4);
    assert_eq!((scratch.as_mut_ptr() as usize) % std::mem::align_of::<T>(), 0);
    unsafe {
        let ptr = scratch.as_mut_ptr().cast::<T>();
        for (new, &old) in inverse.iter().enumerate() {
            ptr.add(new).write(values[old as usize]);
        }
        std::ptr::copy_nonoverlapping(ptr, values.as_mut_ptr(), values.len());
    }
}

pub(super) fn prepare(plan: &mut GpuPlan, layouts: &mut [ArenaLayout; 2], lock_off: &mut [i64], scratch: &mut [f32]) {
    build_map(plan);
    let [forward, inverse] = &plan.reach_src;
    for layout in layouts { layout.set_device_nodes(forward); }
    rows(&mut plan.node_player, inverse, scratch);
    rows(&mut plan.node_na, inverse, scratch);
    rows(&mut plan.node_data_off, inverse, scratch);
    rows(&mut plan.node_children_start, inverse, scratch);
    rows(&mut plan.node_twin, inverse, scratch);
    rows(&mut plan.node_tlose, inverse, scratch);
    rows(&mut plan.node_ttie, inverse, scratch);
    rows(&mut plan.node_cdiv, inverse, scratch);
    rows(&mut plan.node_river_slot, inverse, scratch);
    rows(&mut plan.cc_start, inverse, scratch);
    rows(&mut plan.cc_count, inverse, scratch);
    rows(&mut plan.cfv_slot, inverse, scratch);
    rows(&mut plan.reach_slot[0], inverse, scratch);
    rows(&mut plan.reach_slot[1], inverse, scratch);
    rows(lock_off, inverse, scratch);
    for values in [&mut plan.action_nodes, &mut plan.chance_nodes, &mut plan.fold_nodes,
        &mut plan.show_nodes, &mut plan.chance_parents, &mut plan.chance_children, &mut plan.cc_child] {
        for old in values {
            if *old != u32::MAX { *old = forward[*old as usize]; }
        }
    }
}

pub(super) fn children_image<'a>(children: &[u32], forward: &[u32], scratch: &'a mut [f32]) -> &'a [u32] {
    assert!(children.len() <= scratch.len());
    unsafe {
        let ptr = scratch.as_mut_ptr().cast::<u32>();
        for (i, &old) in children.iter().enumerate() {
            ptr.add(i).write(if old == u32::MAX { old } else { forward[old as usize] });
        }
        std::slice::from_raw_parts(ptr, children.len())
    }
}
