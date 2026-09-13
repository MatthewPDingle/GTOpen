// Exact run encoding of the ORIGINAL scan outputs, not the sparse input.
extern "C" __global__ void pf_rle_cdf(
    const u32* work,u32 start,const u32* blocks,const u32* order,
    const float* normalized,const float* mass,const u32* active,int gate,int compact,
    float* cdf,u32 sample_start,u32 sample_count,u32 batch_capacity,
    const u32* aliases,u32* masks)
{
    if(aliases[blockIdx.x]!=blockIdx.x)return;
    u32 slot=work[start+blockIdx.x];if(gate&&!active[slot])return;
    u32 block=blocks[slot],local=blockIdx.y*4+threadIdx.x/32;
    if(local>=sample_count||mass[block]<=0.f)return;
    u32 particle=sample_start+local,lane=threadIdx.x&31;
    size_t row=(size_t)(compact?blockIdx.x:slot)*batch_capacity+local;
    size_t base=row*(NC+1);float carry=0.f;u32 emitted=0;
    for(u32 tile=0;tile<NC;tile+=32){
        u32 index=tile+lane;
        float value=index<NC?normalized[(size_t)(compact?blockIdx.x:slot)*NC+order[(size_t)particle*NC+index]]:0.f;
        #pragma unroll
        for(int step=1;step<32;step<<=1){
            float add=__shfl_up_sync(0xffffffff,value,step);
            if(lane>=(u32)step)value+=add;
        }
        float prefix=carry+value;
        float previous=__shfl_up_sync(0xffffffff,prefix,1);
        if(lane==0)previous=carry;
        bool changed=index<NC && __float_as_uint(prefix)!=__float_as_uint(previous);
        u32 mask=__ballot_sync(0xffffffff,changed);
        if(lane==0)masks[row*6+tile/32]=mask;
        u32 before=lane==0?0u:mask&((1u<<lane)-1u);
        if(changed)cdf[base+emitted+__popc(before)]=prefix;
        emitted+=__popc(mask);
        carry+=__shfl_sync(0xffffffff,value,31);
    }
}
__device__ __forceinline__ float pf_rle_read(const float* cdf,const u32* masks,size_t base,u32 logical){
    if(logical==0)return 0.f;
    u32 rank=logical-1,word=rank/32,bit=rank&31,n=0;
    size_t mbase=base/(NC+1)*6;
    #pragma unroll
    for(u32 w=0;w<6;w++){
        u32 mask=masks[mbase+w];
        if(w<word)n+=__popc(mask);
        else if(w==word)n+=__popc(mask&(0xffffffffu>>(31-bit)));
    }
    return n?cdf[base+n-1]:0.f;
}
// Only used by the direct prefix test; writes every logical prefix for comparison.
extern "C" __global__ void pf_rle_decode_test(
    const u32* work,u32 start,const u32* blocks,const float* mass,const u32* active,
    int gate,int compact,const float* cdf,const u32* masks,float* decoded,
    u32 sample_count,u32 batch_capacity)
{
    u32 slot=work[start+blockIdx.x];if(gate&&!active[slot])return;
    if(mass[blocks[slot]]<=0.f)return;
    u32 local=blockIdx.y;if(local>=sample_count)return;
    size_t base=((size_t)(compact?blockIdx.x:slot)*batch_capacity+local)*(NC+1);
    for(u32 i=threadIdx.x;i<=NC;i+=blockDim.x)decoded[base+i]=pf_rle_read(cdf,masks,base,i);
}
