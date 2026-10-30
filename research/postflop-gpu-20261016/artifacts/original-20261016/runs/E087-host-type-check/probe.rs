#![allow(dead_code,unused_imports,unused_mut)]
pub use solver::*;
mod gpu {
 use solver::{Solver,store::Store};
 use rayon::prelude::*;
 pub mod plan { pub use solver::gpu::plan::*; }
 fn e(err:impl std::fmt::Debug)->String {format!("cuda: {err:?}")}
fn write_arena(solver: &Solver, which_strat: bool, p: usize, data: &[f32]) {
    let store = if which_strat {
        &solver.strat[p]
    } else {
        &solver.regrets[p]
    };
    match store {
        Store::F32(b) => unsafe { b.slice(0, data.len()) }.copy_from_slice(data),
        _ => {
            let nh = solver.spot.hands[p].len();
            // Every node owns disjoint entries and its own scale factor.
            solver.spot.tree.nodes.par_iter().enumerate().for_each(|(idx, node)| {
                if node.kind == crate::tree::KIND_ACTION && node.player as usize == p {
                    let cnt = node.num_children as usize * nh;
                    let off = node.data_offset as usize;
                    unsafe {
                        store.write_f32(idx as u32, node.data_offset, cnt, &data[off..off + cnt]);
                    }
                }
            });
        }
    }
}
 #[path = r"S:\GTOpen-research\postflop-gpu-20261016\runs\E087-source\candidate\arena.rs"] mod arena;
}
