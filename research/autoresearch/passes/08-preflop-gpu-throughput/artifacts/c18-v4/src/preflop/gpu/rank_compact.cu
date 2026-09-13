// C18: all 192 threads enter; only compact rank groups compute products.
template<int Q, int O>
__device__ __forceinline__ float pf_rank_compact_sum(
    u32 h, const u32* opponent_bases, const float* cdf,
    const u32* group_lower, const u32* group_upper, const u32* hand_group,
    const u32* group_count, u32 sample_start, u32 sample_count, float initial, float* products)
{
    float sum = initial;
    #pragma unroll 2
    for (u32 local = 0; local < sample_count; local++) {
        u32 sample = sample_start + local;
        if (h < group_count[sample]) {
            u32 lo = group_lower[(size_t)sample * NC + h];
            u32 hi = group_upper[(size_t)sample * NC + h];
            float product[Q];
            #pragma unroll
            for (int t = 0; t < Q; t++) product[t] = 1.f;
            #pragma unroll
            for (int q = 0; q < O; q++) {
                u32 base = opponent_bases[q] + local * (NC + 1);
                float less = cdf[(size_t)(base + lo)];
                float equal = fmaxf(0.f, cdf[(size_t)(base + hi)] - less);
                #pragma unroll
                for (int t = 0; t < Q; t++) {
                    float point = Q == 2 ? PF_MW_T2[t] : Q == 3 ? PF_MW_T3[t] : Q == 4 ? PF_MW_T4[t] : PF_MW_T[t];
                    product[t] *= less + point * equal;
                }
            }
            #pragma unroll
            for (int t = 0; t < Q; t++) products[h * Q + t] = product[t];
        }
        __syncthreads();
        if (h < NC) {
            u32 group = hand_group[(size_t)sample * NC + h];
            #pragma unroll
            for (int t = 0; t < Q; t++) {
                float weight = Q == 2 ? PF_MW_W2[t] : Q == 3 ? PF_MW_W3[t] : Q == 4 ? PF_MW_W4[t] : PF_MW_W[t];
                sum += weight * products[group * Q + t];
            }
        }
        __syncthreads();
    }
    return sum;
}
