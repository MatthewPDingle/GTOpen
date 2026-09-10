template<int Q, int O>
__device__ __forceinline__ float pf_multiway_sum(
    u32 h, const size_t* opponent_bases, const float* cdf,
    const u32* lower, const u32* upper,
    u32 sample_start, u32 sample_count)
{
    float sum = 0.f;
    for (u32 local = 0; local < sample_count; local++) {
        size_t hand = (size_t)(sample_start + local) * NC + h;
        u32 lo = lower[hand], hi = upper[hand];
        float product[Q];
        #pragma unroll
        for (int t = 0; t < Q; t++) product[t] = 1.f;
        #pragma unroll
        for (int q = 0; q < O; q++) {
            size_t base = opponent_bases[q] + (size_t)local * (NC + 1);
            float less = cdf[base + lo];
            float equal = fmaxf(0.f, cdf[base + hi] - less);
            #pragma unroll
            for (int t = 0; t < Q; t++) {
                float point = Q == 2 ? PF_MW_T2[t] : Q == 3 ? PF_MW_T3[t] : Q == 4 ? PF_MW_T4[t] : PF_MW_T[t];
                product[t] *= less + point * equal;
            }
        }
        #pragma unroll
        for (int t = 0; t < Q; t++) {
            float weight = Q == 2 ? PF_MW_W2[t] : Q == 3 ? PF_MW_W3[t] : Q == 4 ? PF_MW_W4[t] : PF_MW_W[t];
            sum += weight * product[t];
        }
    }
    return sum;
}

extern "C" __global__ void pf_multiway_terminal(
    const u32* __restrict__ terms, int p, int np,
    const int* __restrict__ live, const float* __restrict__ pots,
    const float* __restrict__ invested, const u32* __restrict__ reach_src,
    const float* __restrict__ terminal_prob,
    const u32* __restrict__ slots, const u32* __restrict__ compact_slots,
    u32 union_slots, int compact, const float* __restrict__ cdf,
    const u32* __restrict__ lower, const u32* __restrict__ upper,
    u32 sample_start, u32 sample_count, u32 batch_capacity, u32 samples,
    const u32* __restrict__ val_slot, float* val)
{
    u32 nd = terms[blockIdx.x];
    int lv = live[nd];
    if (!((lv >> p) & 1)) return; // already handled by the ordinary terminal
    __shared__ float prob;
    __shared__ size_t opponent_bases[9];
    __shared__ int nopponents;
    if (threadIdx.x == 0) {
        prob = terminal_prob[blockIdx.x];
        nopponents = 0;
        if (!(prob <= 0.f)) {
            for (int q = 0; q < np; q++) {
                if (q == p || !((lv >> q) & 1)) continue;
                u32 source = reach_src[(size_t)nd * np + q];
                u32 global_slot = slots[source];
                u32 cdf_slot = compact
                    ? compact_slots[(size_t)p * union_slots + global_slot] : global_slot;
                // Cast before multiplying: large CDF caches exceed 32-bit offsets.
                opponent_bases[nopponents++] = (size_t)cdf_slot * batch_capacity * (NC + 1);
            }
        }
    }
    __syncthreads();
    for (u32 h = threadIdx.x; h < NC; h += blockDim.x) {
        size_t at = (size_t)val_slot[nd] * NC + h;
        if (prob <= 0.f) { if (sample_start == 0) val[at] = 0.f; continue; }
        // Q-point Gauss is exact through degree 2Q-1. The degree here is the
        // number of opponents, so common 3/4-player pots need only two points.
        // Live multiway terminals have exactly 2..8 opponents. The switch
        // is block-uniform; each specialization preserves ascending q order.
        float sum;
        switch (nopponents) {
            case 2: sum = pf_multiway_sum<2, 2>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count); break;
            case 3: sum = pf_multiway_sum<2, 3>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count); break;
            case 4: sum = pf_multiway_sum<3, 4>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count); break;
            case 5: sum = pf_multiway_sum<3, 5>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count); break;
            case 6: sum = pf_multiway_sum<4, 6>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count); break;
            case 7: sum = pf_multiway_sum<4, 7>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count); break;
            default: sum = pf_multiway_sum<5, 8>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count); break; // eight opponents
        }
        float increment = prob * pots[nd] * sum / (float)samples;
        if (sample_start == 0)
            val[at] = increment - prob * invested[(size_t)nd * np + p];
        else
            val[at] += increment;
    }
}

