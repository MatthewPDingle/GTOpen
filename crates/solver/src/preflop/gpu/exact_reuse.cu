// One warp per immutable normalized vector. Hash collisions always get a
// complete bitwise comparison. Table entries only reference original vectors,
// so concurrent insertion never needs to wait for another block to finish.
extern "C" __global__ void pf_exact_reuse_classify(
    const u32* work, u32 start, const u32* blocks, const float* mass,
    const u32* active, int gate, const float* normalized,
    u32* table, u32 mask, u32* aliases)
{
    u32 k=blockIdx.x, lane=threadIdx.x;
    if (lane==0) aliases[k]=k;
    u32 slot=work[start+k];
    if ((gate && !active[slot]) || mass[blocks[slot]]<=0.f) return;
    u32 hash=0;
    for (u32 h=lane;h<NC;h+=32) {
        u32 z=__float_as_uint(normalized[(size_t)k*NC+h]) ^ ((h+1)*0x9e3779b9u);
        z^=z>>16;z*=0x85ebca6bu;z^=z>>13;z*=0xc2b2ae35u;z^=z>>16;hash^=z;
    }
    for (int d=16;d>0;d>>=1) hash^=__shfl_xor_sync(0xffffffff,hash,d);
    u32 bucket=hash&mask;
    // Bounded fallback computes the unshared CDF; it never aliases an
    // unequal vector or waits on an insertion lock.
    for (u32 probe=0;probe<64;probe++,bucket=(bucket+1)&mask) {
        u32 old=0;
        if(lane==0) old=atomicCAS(table+bucket,0u,k+1);
        old=__shfl_sync(0xffffffff,old,0);
        if(old==0u || old==k+1) return;
        u32 representative=old-1;
        bool same=true;
        for(u32 h=lane;h<NC;h+=32)
            same= same && (__float_as_uint(normalized[(size_t)k*NC+h])
                ==__float_as_uint(normalized[(size_t)representative*NC+h]));
        if(__all_sync(0xffffffff,same)) {
            if(lane==0) aliases[k]=representative;
            return;
        }
    }
}
