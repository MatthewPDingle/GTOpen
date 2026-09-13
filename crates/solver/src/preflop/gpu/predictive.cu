// Dedicated histories; reused native value scratch is only transient workspace.
extern "C" __global__ void pf_prediction_transfer(
    const u32* terms, int count, int p, const int* kind, const int* live,
    const u32* val_slot, const u32* offsets, float* history, float* val,
    int save, int enabled)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd=terms[blockIdx.x];
    size_t off=offsets[(size_t)p*count+blockIdx.x];
    bool vector=kind[nd]==2 && ((live[nd]>>p)&1);
    for (int h=threadIdx.x;h<NC;h+=blockDim.x) {
        size_t v=(size_t)val_slot[nd]*NC+h;
        if (save) {
            if (vector || h==0) history[off+(vector?h:0)]=val[v];
        } else val[v]=enabled?history[off+(vector?h:0)]:0.f;
    }
}

extern "C" __global__ void pf_prediction_up(
    const u32* nodes,int start,int count,int p,int np,int predict,
    const int* actor,const int* na_arr,const u32* off_arr,const u32* cstart,
    const u32* children,const int* src_arr,const u32* foff,const float* forced,
    const u32* reach_src,const float* reach,float* regrets,float* strat,
    float* policy,const u32* val_slot,float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd=nodes[start+blockIdx.x],off=off_arr[nd],cs=cstart[nd];
    int na=na_arr[nd],src=src_arr[nd];
    for (int h=threadIdx.x;h<NC;h+=blockDim.x) {
        float out=0.f;
        if (actor[nd]==p) {
            float sig[MAX_NA],q[MAX_NA];
            if (src==2) for (int a=0;a<na;a++) sig[a]=forced[foff[nd]+(u32)a*NC+h];
            else if (src==1) node_sigma(strat,off,na,h,sig);
            else node_sigma(policy,off,na,h,sig);
            for (int a=0;a<na;a++) {
                q[a]=val[(size_t)val_slot[children[cs+a]]*NC+h];
                out+=sig[a]*q[a];
            }
            if (src==0 && predict) {
                float sum=0.f;
                for (int a=0;a<na;a++) {
                    sig[a]=fmaxf(0.f,regrets[off+(u32)a*NC+h]+q[a]-out);
                    sum+=sig[a];
                }
                out=0.f;
                for (int a=0;a<na;a++) {
                    sig[a]=sum>1e-12f?sig[a]/sum:1.f/na;
                    policy[off+(u32)a*NC+h]=sig[a];
                    out+=sig[a]*q[a];
                }
            } else if (src==0) {
                float rp=reach[(size_t)reach_src[(size_t)nd*np+p]*NC+h];
                for (int a=0;a<na;a++) {
                    u32 ix=off+(u32)a*NC+h;
                    regrets[ix]=fmaxf(0.f,regrets[ix]+q[a]-out);
                    strat[ix]+=rp*sig[a];
                }
            }
        } else for (int a=0;a<na;a++) out+=val[(size_t)val_slot[children[cs+a]]*NC+h];
        val[(size_t)val_slot[nd]*NC+h]=out;
    }
}
