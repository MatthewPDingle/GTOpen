// E063: CPU-only upload representation; public GpuPlan tables retain their meaning.
fn pack_show_bounds(plan: &GpuPlan) -> ([Vec<u32>; 2], [Vec<u32>; 2]) {
    let mut lower = plan.riv_lower.clone();
    let mut upper = plan.riv_upper.clone();
    for p in 0..2 {
        let o = 1 - p;
        for slot in 0..plan.num_slots {
            let begin = plan.riv_off[p][slot] as usize;
            let end = begin + plan.riv_cnt[p][slot] as usize;
            for j in begin..end {
                let i = plan.riv_sorted_idx[p][j] as usize;
                let lb = plan.riv_lower[p][j];
                let ub = plan.riv_upper[p][j];
                debug_assert!(lb <= ub && ub <= 1326);
                for (x, card) in [plan.hand_c1[p][i], plan.hand_c2[p][i]].into_iter().enumerate() {
                    let c = slot * 53 + card as usize;
                    let a = plan.riv_card_off[o][c] as usize;
                    let b = plan.riv_card_off[o][c + 1] as usize;
                    let positions = &plan.riv_card_pos[o][a..b];
                    debug_assert!(positions.len() <= 51);
                    let lo = positions.partition_point(|&pos| pos < lb) as u32;
                    let hi = positions.partition_point(|&pos| pos < ub) as u32;
                    if x == 0 { lower[p][j] |= (lo << 11) | (hi << 17); }
                    else { upper[p][j] |= (lo << 11) | (hi << 17); }
                }
            }
        }
    }
    (lower, upper)
}
