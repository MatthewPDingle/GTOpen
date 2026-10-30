typedef unsigned int u32;
#define NC 169
extern "C" __global__ void explore_opponent_reach(
    const u32* nodes,int start,int count,int p,int np,
    const int* actors,const int* na,const u32* cstart,const u32* children,
    const int* source,const u32* reach_src,const float* epsilon,float* reach)
{
    if(blockIdx.x >= (u32)count || epsilon[0]<=0.f)return;
    u32 nd=nodes[start+blockIdx.x];int actor=actors[nd];
    if(actor==p || source[nd]!=0)return;
    float e=epsilon[0],uniform=e/(float)na[nd];
    for(int h=threadIdx.x;h<NC;h+=blockDim.x) {
        float parent=reach[(size_t)reach_src[(size_t)nd*np+actor]*NC+h];
        for(int a=0;a<na[nd];a++) {
            u32 child=children[cstart[nd]+a];size_t at=(size_t)reach_src[(size_t)child*np+actor]*NC+h;
            reach[at]=(1.f-e)*reach[at]+uniform*parent;
        }
    }
}
