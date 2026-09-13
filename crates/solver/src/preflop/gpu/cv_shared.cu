// Live-learning terminal cache only. Scalar and folded payoffs stay native.
extern "C" __global__ void cv_shared_store(const u32* terms,const u32* slots,
    const float* values,float* stored,const u32* offsets,u32 nterms,int p) {
    u32 t=blockIdx.x,off=offsets[(size_t)p*nterms+t];if(off==0xffffffffu)return;
    u32 nd=terms[t];
    for(u32 h=threadIdx.x;h<NC;h+=blockDim.x)stored[(size_t)off+h]=values[(size_t)slots[nd]*NC+h];
}
extern "C" __global__ void cv_shared_combine(const u32* terms,int p,int np,
    const u32* reach_src,const float* mass,const u32* slots,const float* current,
    const float* reference_full,float* values,const u32* offsets,u32 nterms) {
    u32 t=blockIdx.x,off=offsets[(size_t)p*nterms+t];if(off==0xffffffffu)return;
    u32 nd=terms[t];float probability=1.f;
    for(int q=0;q<np;q++)if(q!=p)probability*=mass[reach_src[(size_t)nd*np+q]];
    for(u32 h=threadIdx.x;h<NC;h+=blockDim.x) {
        size_t at=(size_t)slots[nd]*NC+h;
        values[at]=current[(size_t)t*NC+h]+probability*(reference_full[(size_t)off+h]-values[at]);
    }
}
