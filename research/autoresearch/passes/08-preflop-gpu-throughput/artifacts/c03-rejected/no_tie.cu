// Research-only: same sample and weighted-addition order, uniform no-tie fast path.
template<int Q, int O>
__device__ __forceinline__ float pf_no_tie_sum(
    u32 h, const size_t* opponent_bases, const float* cdf,
    const u32* lower, const u32* upper, u32 sample_start, u32 sample_count)
{
    float sum=0.f;
    for(u32 local=0;local<sample_count;local++) {
        size_t hand=(size_t)(sample_start+local)*NC+h;
        u32 lo=lower[hand],hi=upper[hand];
        float less[O],equal[O]; bool zero=true;
        #pragma unroll
        for(int q=0;q<O;q++) {
            size_t base=opponent_bases[q]+(size_t)local*(NC+1);
            less[q]=cdf[base+lo];equal[q]=fmaxf(0.f,cdf[base+hi]-less[q]);
            zero=zero && equal[q]==0.f;
        }
        if(__all_sync(__activemask(),zero)) {
            float product=1.f;
            #pragma unroll
            for(int q=0;q<O;q++) product*=less[q];
            #pragma unroll
            for(int t=0;t<Q;t++) {
                float weight=Q==2?PF_MW_W2[t]:Q==3?PF_MW_W3[t]:Q==4?PF_MW_W4[t]:PF_MW_W[t];
                sum+=weight*product;
            }
        } else {
            float product[Q];
            #pragma unroll
            for(int t=0;t<Q;t++) product[t]=1.f;
            #pragma unroll
            for(int q=0;q<O;q++) {
                #pragma unroll
                for(int t=0;t<Q;t++) {
                    float point=Q==2?PF_MW_T2[t]:Q==3?PF_MW_T3[t]:Q==4?PF_MW_T4[t]:PF_MW_T[t];
                    product[t]*=less[q]+point*equal[q];
                }
            }
            #pragma unroll
            for(int t=0;t<Q;t++) {
                float weight=Q==2?PF_MW_W2[t]:Q==3?PF_MW_W3[t]:Q==4?PF_MW_W4[t]:PF_MW_W[t];
                sum+=weight*product[t];
            }
        }
    }
    return sum;
}
