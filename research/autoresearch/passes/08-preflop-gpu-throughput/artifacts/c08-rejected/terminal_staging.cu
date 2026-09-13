// C08: every thread stages rows and reaches every barrier, including h >= NC.
template<int Q, int O>
__device__ __forceinline__ float pf_staged_multiway_sum(
    u32 h, const size_t* opponent_bases, const float* cdf,
    const u32* lower, const u32* upper,
    u32 sample_start, u32 sample_count, float* staged)
{
    float sum = 0.f;
    for (u32 local = 0; local < sample_count; local++) {
        #pragma unroll
        for (int q = 0; q < O; q++) {
            size_t base = opponent_bases[q] + (size_t)local * (NC + 1);
            for (u32 index = threadIdx.x; index < NC + 1; index += blockDim.x)
                staged[q * (NC + 1) + index] = cdf[base + index];
        }
        __syncthreads();
        if (h < NC) {
            size_t hand = (size_t)(sample_start + local) * NC + h;
            u32 lo = lower[hand], hi = upper[hand];
            float product[Q];
            #pragma unroll
            for (int t = 0; t < Q; t++) product[t] = 1.f;
            #pragma unroll
            for (int q = 0; q < O; q++) {
                float less = staged[q * (NC + 1) + lo];
                float equal = fmaxf(0.f, staged[q * (NC + 1) + hi] - less);
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
