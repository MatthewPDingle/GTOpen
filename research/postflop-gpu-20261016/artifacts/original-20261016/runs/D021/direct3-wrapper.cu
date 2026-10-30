extern "C" __global__ void up_action_3(
    const u32* __restrict__ nodes, int start, int count, int p,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    float* regrets_p, float* strat_p,
    const u32* __restrict__ rsrc_p,
    const float* __restrict__ reach_p_buf,
    const long long* __restrict__ lock_off,
    const float* __restrict__ lock_sigma,
    const u32* __restrict__ cfv_slot, float* cfv,
    const float* __restrict__ disc, // [pos, neg, strat] — device-resident so
                                    // captured graphs stay iteration-invariant
    int nh_p, int nh_max)
{
    if (blockIdx.x >= (u32)count) return;
    up_action_impl<3>(nodes, start, count, p, node_player, node_na, node_data_off, node_children_start, children, regrets_p, strat_p, rsrc_p, reach_p_buf, lock_off, lock_sigma, cfv_slot, cfv, disc, nh_p, nh_max);
}
