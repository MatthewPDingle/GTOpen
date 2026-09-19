// Research-only stabilizer projection. Separate reduce/broadcast launches.
typedef unsigned int u32;
typedef unsigned long long u64;
extern "C" __global__ void continuation_project(
    const u32* nodes, int count, const int* players, const int* na,
    const u64* offsets, const u32* stabilizers, const u32* permutations,
    float* regrets, float* sums, int nh, int player, int broadcast)
{
    int b=blockIdx.x;
    if(b>=count) return;
    u32 n=nodes[b], mask=stabilizers[n];
    if(players[n]!=player || mask==1) return;
    for(int i=threadIdx.x;i<nh;i+=blockDim.x) {
        int canonical=i;
        for(u32 m=mask;m;m&=m-1) {
            int k=__ffs(m)-1;
            int j=permutations[(u64)k*nh+i];
            if(j<canonical) canonical=j;
        }
        if(broadcast) {
            // Canonical threads never write in this launch, so their values
            // are stable while all other orbit members read them.
            if(canonical==i) continue;
            for(int a=0;a<na[n];a++) {
                u64 base=offsets[n]+(u64)a*nh;
                regrets[base+i]=regrets[base+canonical];
                sums[base+i]=sums[base+canonical];
            }
        } else if(canonical==i) {
            // Distinct canonical threads read disjoint orbits. Repeated group
            // images have constant multiplicity, so averaging group elements
            // is the same as averaging unique orbit members.
            for(int a=0;a<na[n];a++) {
                u64 base=offsets[n]+(u64)a*nh;
                double r=0.,s=0.;int size=0;
                for(u32 m=mask;m;m&=m-1) {
                    int k=__ffs(m)-1;
                    u64 j=base+permutations[(u64)k*nh+i];
                    r+=regrets[j];s+=sums[j];size++;
                }
                regrets[base+i]=(float)(r/size);
                sums[base+i]=(float)(s/size);
            }
        }
    }
}

extern "C" __global__ void continuation_transport(
    const u32* nodes, int count, const int* players, const int* na,
    const u64* offsets, const u32* sources, const u32* source_permutations,
    const u32* permutations, float* regrets, float* sums, int nh, int player)
{
    int b=blockIdx.x;
    if(b>=count) return;
    u32 n=nodes[b], source=sources[n];
    // Every source is canonical and therefore never written by this launch.
    if(players[n]!=player || n==source) return;
    u32 k=source_permutations[n];
    for(int i=threadIdx.x;i<nh;i+=blockDim.x) {
        int j=permutations[(u64)k*nh+i];
        for(int a=0;a<na[n];a++) {
            u64 dst=offsets[n]+(u64)a*nh+i,src=offsets[source]+(u64)a*nh+j;
            regrets[dst]=regrets[src];sums[dst]=sums[src];
        }
    }
}
