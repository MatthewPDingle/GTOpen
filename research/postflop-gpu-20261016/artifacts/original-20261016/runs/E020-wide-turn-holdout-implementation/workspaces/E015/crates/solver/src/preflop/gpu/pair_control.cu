typedef unsigned int u32;
#define NC 169

// One exact-canonical pair mean per hero class and needed opponent range.
// Matrix is opposing-class major for coalesced reads across hero lanes.
extern "C" __global__ void pair_project(
    const u32* work,u32 start,const u32* blocks,const float* reach,
    const float* mass,const u32* active,int gate,const float* matrix,float* means)
{
    u32 slot=work[start+blockIdx.x],block=blocks[slot];
    if(gate && !active[slot])return;
    __shared__ float weights[NC];
    for(u32 k=threadIdx.x;k<NC;k+=blockDim.x)
        weights[k]=mass[block]>0.f ? reach[(size_t)block*NC+k]/mass[block] : 0.f;
    __syncthreads();
    for(u32 h=threadIdx.x;h<NC;h+=blockDim.x) {
        float sum=0.f;
        for(u32 k=0;k<NC;k++)sum+=weights[k]*matrix[(size_t)k*NC+h];
        means[(size_t)slot*NC+h]=sum;
    }
}

// Subtract a zero-canonical-mean additive pair-outcome control. The original
// kernel computes the actual multiway share and investment exactly as before.
// No clipping: individual corrected samples may be outside [0,1].
extern "C" __global__ void pair_correct(
    const u32* terms,int p,int np,const int* live,const float* pots,
    const u32* reach_src,const float* probability,const u32* slots,
    const u32* compact_slots,u32 union_slots,int compact,const float* cdf,
    const u32* lower,const u32* upper,const float* means,
    u32 sample_start,u32 sample_count,u32 capacity,u32 samples,
    const u32* val_slot,float* values)
{
    u32 nd=terms[blockIdx.x];int lv=live[nd];
    if(!((lv>>p)&1) || probability[blockIdx.x]<=0.f)return;
    __shared__ size_t bases[9];__shared__ u32 mean_slots[9];__shared__ int count;
    if(threadIdx.x==0) {
        count=0;
        for(int q=0;q<np;q++) {
            if(q==p || !((lv>>q)&1))continue;
            u32 source=reach_src[(size_t)nd*np+q],slot=slots[source];
            u32 physical=compact ? compact_slots[(size_t)p*union_slots+slot] : slot;
            bases[count]=(size_t)physical*capacity*(NC+1);mean_slots[count]=slot;count++;
        }
    }
    __syncthreads();
    for(u32 h=threadIdx.x;h<NC;h+=blockDim.x) {
        float mu[9],weight[9];
        for(int q=0;q<count;q++)mu[q]=means[(size_t)mean_slots[q]*NC+h];
        for(int q=0;q<count;q++) {
            float product=1.f;
            for(int j=0;j<count;j++)if(j!=q)product*=mu[j];
            weight[q]=product;
        }
        float correction=0.f;
        for(u32 local=0;local<sample_count;local++) {
            size_t hand=(size_t)(sample_start+local)*NC+h;
            u32 lo=lower[hand],hi=upper[hand];
            for(int q=0;q<count;q++) {
                size_t at=bases[q]+(size_t)local*(NC+1);
                float less=cdf[at+lo],equal=fmaxf(0.f,cdf[at+hi]-less);
                correction+=weight[q]*(less+0.5f*equal-mu[q]);
            }
        }
        values[(size_t)val_slot[nd]*NC+h]-=probability[blockIdx.x]*pots[nd]*correction/(float)samples;
    }
}
