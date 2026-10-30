typedef unsigned int u32;
#define NC 169
extern "C" __global__ void cv_unit_probability(float* probability,u32 count) {
    u32 i=blockIdx.x*blockDim.x+threadIdx.x;if(i<count)probability[i]=1.f;
}
extern "C" __global__ void cv_zero_mass_prior(float* reach,float* mass,const float* prior) {
    u32 b=blockIdx.x;__shared__ int empty;
    if(threadIdx.x==0)empty=mass[b]<=0.f;__syncthreads();
    if(!empty)return;
    for(u32 h=threadIdx.x;h<NC;h+=blockDim.x)reach[(size_t)b*NC+h]=prior[h];
    __syncthreads();if(threadIdx.x==0)mass[b]=1.f;
}
extern "C" __global__ void cv_store(const u32* terms,const u32* slots,const float* values,float* stored) {
    u32 t=blockIdx.x,nd=terms[t];
    for(u32 h=threadIdx.x;h<NC;h+=blockDim.x)stored[(size_t)t*NC+h]=values[(size_t)slots[nd]*NC+h];
}
extern "C" __global__ void cv_combine(const u32* terms,int p,int np,const int* live,
    const u32* reach_src,const float* mass,const u32* slots,const float* current,const float* reference_full,float* values) {
    u32 t=blockIdx.x,nd=terms[t];if(!((live[nd]>>p)&1))return;
    float probability=1.f;
    for(int q=0;q<np;q++)if(q!=p)probability*=mass[reach_src[(size_t)nd*np+q]];
    for(u32 h=threadIdx.x;h<NC;h+=blockDim.x) {
        size_t at=(size_t)slots[nd]*NC+h,cache=(size_t)t*NC+h;
        // Do not clamp: clipping a control-variate estimate introduces bias.
        values[at]=current[cache]+probability*(reference_full[cache]-values[at]);
    }
}
