// Research-only uniform behavioral constraints. Native learning/evaluation
// kernels are unchanged. Included after kernels.cu for policy helpers.
extern "C" __global__ void behavioral_reach(
    const u32* nodes,int start,int count,int np,const int* actors,const int* na,
    const u32* cstart,const u32* children,const int* source,
    const u32* reach_src,float epsilon,float* reach)
{
    if(blockIdx.x >= (u32)count)return;
    u32 nd=nodes[start+blockIdx.x];if(source[nd]!=0)return;
    int actor=actors[nd];float tau=1.f-epsilon,prior=epsilon/(float)na[nd];
    for(int h=threadIdx.x;h<NC;h+=blockDim.x){
        float parent=reach[(size_t)reach_src[(size_t)nd*np+actor]*NC+h];
        for(int a=0;a<na[nd];a++){
            u32 child=children[cstart[nd]+a];size_t at=(size_t)reach_src[(size_t)child*np+actor]*NC+h;
            reach[at]=tau*reach[at]+prior*parent;
        }
    }
}
extern "C" __global__ void behavioral_up(
    const u32* nodes,int start,int count,int p,int np,int mode,float epsilon,
    const int* actors,const int* na_arr,const u32* offsets,const u32* cstart,
    const u32* children,const int* source,const u32* foff,const float* forced,
    const u32* reach_src,const float* reach,float* regrets,float* strat,
    const u32* slots,float* values)
{
    if(blockIdx.x >= (u32)count)return;
    u32 nd=nodes[start+blockIdx.x],off=offsets[nd],cs=cstart[nd];
    int actor=actors[nd],na=na_arr[nd],src=source[nd];
    float tau=1.f-epsilon,prior=epsilon/(float)na;
    for(int h=threadIdx.x;h<NC;h+=blockDim.x){
        float q[MAX_NA],sig[MAX_NA],out=0.f,mean=0.f;
        for(int a=0;a<na;a++){q[a]=values[(size_t)slots[children[cs+a]]*NC+h];mean+=q[a];}
        if(actor!=p){out=mean;}
        else if(mode==4 && src==0){
            float best=q[0];for(int a=1;a<na;a++)best=fmaxf(best,q[a]);
            out=tau*best+prior*mean;
        }else{
            if(src==2){for(int a=0;a<na;a++)sig[a]=forced[foff[nd]+a*NC+h];}
            else if(src==1 || mode!=0){node_sigma(strat,off,na,h,sig);}
            else{node_sigma_regret(regrets,off,na,h,sig);}
            if(mode==0 && src==0){
                float virtual_mean=0.f;
                for(int a=0;a<na;a++)virtual_mean+=sig[a]*q[a];
                float rp=reach[(size_t)reach_src[(size_t)nd*np+p]*NC+h];
                for(int a=0;a<na;a++){
                    float mu=tau*sig[a]+prior;
                    out+=mu*q[a];
                    regrets[off+a*NC+h]+=tau*(q[a]-virtual_mean);
                    strat[off+a*NC+h]+=rp*mu;
                }
            }else{for(int a=0;a<na;a++)out+=sig[a]*q[a];}
        }
        values[(size_t)slots[nd]*NC+h]=out;
    }
}
