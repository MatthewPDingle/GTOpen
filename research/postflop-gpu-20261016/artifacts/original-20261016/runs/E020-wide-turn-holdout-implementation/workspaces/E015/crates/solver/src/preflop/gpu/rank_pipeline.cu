// C22: each block owns one terminal; each thread owns one rank group.
template<int Q, int O>
__device__ __forceinline__ void pf_rank_produce(
    u32 group, const u32* bases, const float* cdf,
    const u32* gl, const u32* gu, const u32* gc,
    u32 start, u32 count, u32 groups, u32 quadratures, float* scratch)
{
    #pragma unroll 2
    for (u32 local = 0; local < count; local++) {
        u32 sample = start + local;
        if (group < gc[sample]) {
            u32 lo = gl[(size_t)sample * NC + group];
            u32 hi = gu[(size_t)sample * NC + group];
            float product[Q];
            #pragma unroll
            for (int t = 0; t < Q; t++) product[t] = 1.f;
            #pragma unroll
            for (int opponent = 0; opponent < O; opponent++) {
                u32 base = bases[opponent] + local * (NC + 1);
                float less = cdf[(size_t)(base + lo)];
                float equal = fmaxf(0.f, cdf[(size_t)(base + hi)] - less);
                #pragma unroll
                for (int t = 0; t < Q; t++) {
                    float point = Q == 2 ? PF_MW_T2[t] : Q == 3 ? PF_MW_T3[t] : Q == 4 ? PF_MW_T4[t] : PF_MW_T[t];
                    product[t] *= less + point * equal;
                }
            }
            #pragma unroll
            for (int t = 0; t < Q; t++)
                scratch[((size_t)local * groups + group) * quadratures + t] = product[t];
        }
    }
}

template<int Q>
__device__ __forceinline__ float pf_rank_consume(
    u32 hand, const u32* hg, u32 start, u32 count,
    u32 groups, u32 quadratures, float initial, const float* scratch)
{
    float sum = initial;
    #pragma unroll 2
    for (u32 local = 0; local < count; local++) {
        u32 group = hg[(size_t)(start + local) * NC + hand];
        #pragma unroll
        for (int t = 0; t < Q; t++) {
            float weight = Q == 2 ? PF_MW_W2[t] : Q == 3 ? PF_MW_W3[t] : Q == 4 ? PF_MW_W4[t] : PF_MW_W[t];
            sum += weight * scratch[((size_t)local * groups + group) * quadratures + t];
        }
    }
    return sum;
}
