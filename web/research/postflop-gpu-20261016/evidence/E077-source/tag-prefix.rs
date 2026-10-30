/// Tag precisely the shared prefixes read by the opposite player's showdown
/// evaluation. This mutates only a constructor-owned plan after its public build;
/// GPU index loads mask bit31, leaving every physical hand index unchanged.
pub(crate) fn tag_prefix_reads(plan: &mut GpuPlan) {
    const NEEDED: u32 = 0x8000_0000;
    for opponent in 0..2 {
        let own = 1 - opponent;
        for slot in 0..plan.num_slots {
            let ob = plan.riv_off[opponent][slot] as usize;
            let count = plan.riv_cnt[opponent][slot] as usize;
            if count != 0 { plan.riv_sorted_idx[opponent][ob + count - 1] |= NEEDED; }
            let begin = plan.riv_off[own][slot] as usize;
            let end = begin + plan.riv_cnt[own][slot] as usize;
            for i in begin..end {
                let lower = plan.riv_lower[own][i] as usize;
                let upper = plan.riv_upper[own][i] as usize;
                if lower != 0 { plan.riv_sorted_idx[opponent][ob + lower - 1] |= NEEDED; }
                if upper != 0 { plan.riv_sorted_idx[opponent][ob + upper - 1] |= NEEDED; }
            }
        }
    }
}

