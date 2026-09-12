// Research prototype: fixed representation units; preserve stored policy histories.
extern "C" __global__ void pf_up_fixed_history_units(
    const u32* nodes, int start, int count, int p, int np,
    const int* actor_arr, const int* na_arr, const u32* off_arr,
    const u32* cstart_arr, const u32* children, const int* src_arr,
    const u32* foff_arr, const float* forced, const u32* reach_src,
    const float* reach, const float* regret_units, const float* average_units,
    float* regrets, float* strat, const u32* val_slot, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd=nodes[start+blockIdx.x];
    int act=actor_arr[nd],na=na_arr[nd],src=src_arr[nd];
    u32 off=off_arr[nd],cs=cstart_arr[nd];
    for (int h=threadIdx.x;h<NC;h+=blockDim.x) {
        float out=0.f;
        if (act==p) {
            float sig[MAX_NA];
            if (src==2) {
                u32 fo=foff_arr[nd];
                for (int a=0;a<na;a++) sig[a]=forced[fo+(u32)a*NC+h];
            } else if (src==1) node_sigma(strat,off,na,h,sig);
            else node_sigma_regret(regrets,off,na,h,sig);
            for (int a=0;a<na;a++) out+=sig[a]*val[(size_t)val_slot[children[cs+a]]*NC+h];
            if (src==0) {
                float rp=reach[(size_t)reach_src[(size_t)nd*np+p]*NC+h];
                for (int a=0;a<na;a++) {
                    u32 ix=off+(u32)a*NC+h;
                    regrets[ix]+=(val[(size_t)val_slot[children[cs+a]]*NC+h]-out)/regret_units[nd];
                    strat[ix]+=(rp*sig[a])/average_units[nd];
                }
            }
        } else {
            for (int a=0;a<na;a++) out+=val[(size_t)val_slot[children[cs+a]]*NC+h];
        }
        val[(size_t)val_slot[nd]*NC+h]=out;
    }
}
