// C16: local prefix construction preserves the retained warp-scan arithmetic.
template<int O>
__device__ __forceinline__ void pf_fused_stage(
    const u32* bases, const float* normalized, float* local_norm)
{
    for (u32 i = threadIdx.x; i < O * NC; i += blockDim.x)
        local_norm[i] = normalized[(size_t)bases[i / NC] + i % NC];
    __syncthreads();
}

template<int O>
__device__ __forceinline__ void pf_fused_prefix(
    u32 particle, const u32* order, const float* local_norm, float* local_cdf)
{
    u32 lane = threadIdx.x & 31;
    for (u32 q = threadIdx.x / 32; q < O; q += blockDim.x / 32) {
        if (lane == 0) local_cdf[q * (NC + 1)] = 0.f;
        float carry = 0.f;
        for (u32 tile = 0; tile < NC; tile += 32) {
            u32 index = tile + lane;
            float value = index < NC
                ? local_norm[q * NC + order[(size_t)particle * NC + index]] : 0.f;
            #pragma unroll
            for (int step = 1; step < 32; step <<= 1) {
                float add = __shfl_up_sync(0xffffffff, value, step);
                if (lane >= (u32)step) value += add;
            }
            if (index < NC) local_cdf[q * (NC + 1) + index + 1] = carry + value;
            carry += __shfl_sync(0xffffffff, value, 31);
        }
    }
    __syncthreads();
}

template<int Q, int O>
__device__ __forceinline__ float pf_fused_sum(
    u32 h, const u32* bases, const float* normalized, const u32* order,
    const u32* lower, const u32* upper, u32 sample_start, u32 sample_count,
    float* local_norm, float* local_cdf)
{
    pf_fused_stage<O>(bases, normalized, local_norm);
    float sum = 0.f;
    #pragma unroll 2
    for (u32 local = 0; local < sample_count; local++) {
        pf_fused_prefix<O>(sample_start + local, order, local_norm, local_cdf);
        if (h < NC) {
            size_t hand = (size_t)(sample_start + local) * NC + h;
            u32 lo = lower[hand], hi = upper[hand];
            float product[Q];
            #pragma unroll
            for (int t = 0; t < Q; t++) product[t] = 1.f;
            #pragma unroll
            for (int q = 0; q < O; q++) {
                float less = local_cdf[q * (NC + 1) + lo];
                float equal = fmaxf(0.f, local_cdf[q * (NC + 1) + hi] - less);
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
        __syncthreads();
    }
    return sum;
}
