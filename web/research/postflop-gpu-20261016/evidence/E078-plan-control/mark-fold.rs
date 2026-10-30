/// Mark only constructor-owned reached fold entries in the existing upload.
/// Public GpuPlan values and all vector lengths/capacities remain unchanged.
fn mark_fold_producers(plan: &mut GpuPlan) {
    for &node in &plan.fold_nodes {
        plan.node_na[node as usize] = -1;
    }
}

