//! Research-only payload accounting for the exact stored continuation path.
//! Does not allocate CUDA memory. Driver/allocator overhead is deliberately separate.
use super::{plan::GpuPlan, GpuSolver};
use crate::{Spot, TreeConfig};
use serde_json::{json, Value};
use std::mem::size_of;

fn bytes<T>(a: &[T]) -> u64 { (a.len()*size_of::<T>()) as u64 }
fn owned<T>(a: &Vec<T>) -> u64 { (a.capacity()*size_of::<T>()) as u64 }
fn config_owned(c: &TreeConfig) -> u64 {
    c.oop.iter().chain(&c.ip).map(|s|owned(&s.bet)+owned(&s.raise)+owned(&s.donk)).sum()
}
fn spot_owned(s: &Spot) -> u64 {
    let mut n=size_of::<Spot>() as u64+owned(&s.board)+owned(&s.tree.nodes)+owned(&s.tree.children)+owned(&s.tree.actions)
        +s.config.board.capacity() as u64+s.config.range_oop.capacity() as u64+s.config.range_ip.capacity() as u64
        +config_owned(&s.config.tree)+config_owned(&s.tree.config)+owned(&s.suit_perms)+owned(&s.river.entries);
    for p in 0..2 {
        n+=owned(&s.hands[p])+owned(&s.weights[p])+owned(&s.same_combo[p])+owned(&s.hand_perm[p]);
        for perm in &s.hand_perm[p] {n+=owned(perm);}
    }
    for r in s.river.entries.iter().flatten() {
        n+=size_of::<crate::game::RiverBoardEval>() as u64+owned(&r.sorted[0])+owned(&r.sorted[1]);
    }
    n
}

fn metadata(p: &GpuPlan, s: &Spot) -> u64 {
    macro_rules! sum {($($f:ident),*)=>{0u64 $(+bytes(&p.$f))*};}
    let mut n=sum!(action_nodes,chance_parents,chance_children,chance_cards,chance_nodes,fold_nodes,show_nodes,
        node_player,node_na,node_data_off,node_children_start,node_twin,node_tlose,node_ttie,node_cdiv,node_river_slot,
        cc_start,cc_count,cc_card,cc_child,cc_perm,cfv_slot)+bytes(&s.tree.children);
    for q in 0..2 {
        n+=bytes(&p.hand_perm_flat[q])+bytes(&p.reach_slot[q])+bytes(&p.hand_c1[q])+bytes(&p.hand_c2[q])
            +bytes(&p.hand_mask[q])+bytes(&p.same_combo[q])+bytes(&p.weights[q])+bytes(&p.riv_off[q])
            +bytes(&p.riv_cnt[q])+bytes(&p.riv_sorted_idx[q])+bytes(&p.riv_lower[q])+bytes(&p.riv_upper[q])
            +bytes(&p.riv_card_off[q])+bytes(&p.riv_card_pos[q]);
        n+=53*4+(2*p.nh[q]*4) as u64; // fold-card offsets and two entries per hand
    }
    n+(p.num_nodes*8) as u64+4+12+(4*p.nh_max*4) as u64 // unlocked table, sigma, discounts, eval roots
}

/// Actual CUDA slice payloads, excluding the seven borrowed mutable buffers.
pub(super) fn observed_metadata(g: &GpuSolver) -> u64 {
    macro_rules! sum {($($f:ident:$t:ty),*)=>{0u64 $(+(g.$f.len()*size_of::<$t>()) as u64)*};}
    let mut n=sum!(d_action_nodes:u32,d_chance_parents:u32,d_chance_children:u32,d_chance_cards:u32,d_chance_nodes:u32,
        d_fold_nodes:u32,d_show_nodes:u32,d_node_player:i32,d_node_na:i32,d_node_data_off:u64,d_node_children_start:u32,
        d_node_twin:f32,d_node_tlose:f32,d_node_ttie:f32,d_node_cdiv:f32,d_node_river_slot:i32,d_cc_start:u32,
        d_cc_count:u32,d_cc_card:u32,d_cc_child:u32,d_cc_perm:u32,d_children:u32,d_lock_off:i64,d_lock_sigma:f32,
        d_cfv_slot:u32,d_eval_roots:f32,d_disc:f32);
    for q in 0..2 {
        macro_rules! arr {($($f:ident:$t:ty),*)=>{0u64 $(+(g.$f[q].len()*size_of::<$t>()) as u64)*};}
        n+=arr!(d_hand_perm:u32,d_rsrc:u32,d_fold_card_off:u32,d_fold_card_idx:u32,d_hand_c1:u32,d_hand_c2:u32,
            d_hand_mask:u64,d_same:u32,d_weights:f32,d_riv_off:u32,d_riv_cnt:u32,d_riv_idx:u32,d_riv_lower:u32,
            d_riv_upper:u32,d_riv_card_off:u32,d_riv_card_pos:u32);
    }
    n
}

pub fn stored_capacity_plan(s: &Spot) -> Value {
    let mut full=GpuPlan::build(s,false);full.use_full_action_arenas(s);
    let compact=GpuPlan::build(s,true);
    let base=metadata(&full,s);
    let wrapper=(s.tree.nodes.len()*12+compact.action_nodes.len()*12+7*4) as u64;
    let mut work=[0u64;11];
    for q in 0..2 {
        work[q]=full.arena_elements[q] as u64*4;work[q+2]=work[q];
        work[q+4]=(full.reach_blocks[q]*full.nh[q]*4) as u64;
        if compact.iso_active {work[q+7]=compact.arena_elements[q].max(1) as u64*4;work[q+9]=work[q+7];}
    }
    work[6]=(full.cfv_blocks*full.nh_max*4) as u64;
    let state=if compact.iso_active {(compact.arena_elements[0]+compact.arena_elements[1]) as u64*8}
        else {(s.tree.data_size[0]+s.tree.data_size[1])*8};
    let plan_host=owned(&compact.action_nodes)+owned(&compact.node_data_off);
    let spans=owned(&full.action_spans)+owned(&full.chance_spans)+owned(&full.chance_node_spans)+owned(&full.fold_spans)+owned(&full.show_spans);
    let host=spot_owned(s)+plan_host+spans+4; // one-float pinned staging; full ArenaLayouts have no heap
    json!({"canonical_state_bytes":state,"explicit_state_bytes":(s.tree.data_size[0]+s.tree.data_size[1])*8,
        "base_gpu_metadata_bytes":base,"wrapper_gpu_metadata_bytes":wrapper,"retained_gpu_payload_bytes":base+wrapper,
        "workspace_components_bytes":work,"spot_owned_bytes":spot_owned(s),"storage_plan_owned_bytes":plan_host,
        "host_retained_payload_bytes":host,"constructor_pinned_bytes":s.tree.data_size.iter().max().unwrap()*4,
        "node_count":s.tree.nodes.len(),"canonical_actions":compact.action_nodes.len(),"iso_active":compact.iso_active,
        "limitations":"Payload accounting; excludes CUDA context/modules, allocator bookkeeping, driver scratch, process baseline, constructor temporary plans and evaluation recursion scratch. Reserve separately. Construction temporarily holds previous workspace plus this game's workspace. CPU materialization also holds full explicit arrays."})
}
