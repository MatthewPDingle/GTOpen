extern "C" __global__ void pf_multiway_cdf(
    const u32* __restrict__ work, u32 start,
    const u32* __restrict__ blocks, const u32* __restrict__ order,
    const float* __restrict__ normalized, const float* __restrict__ mass,
    const u32* __restrict__ active, int gate, int compact,
    float* cdf, u32 sample_start, u32 sample_count, u32 batch_capacity)
{
    u32 slot = work[start + blockIdx.x];
    if (gate && !active[slot]) return;
    u32 block = blocks[slot];
    // Uniform exits must precede the block-wide staging barrier. Four warps
    // consume different particle orders over this same normalized reach.
    if (sample_count == 0 || mass[block] <= 0.f) return;
    __shared__ float staged_reach[NC];
    size_t reach_base = (size_t)(compact ? blockIdx.x : slot) * NC;
    for (u32 h = threadIdx.x; h < NC; h += blockDim.x)
        staged_reach[h] = normalized[reach_base + h];
    __syncthreads();
    u32 local = blockIdx.y * 4 + threadIdx.x / 32;
    if (local >= sample_count) return;
    u32 particle = sample_start + local;
    u32 lane = threadIdx.x & 31;
    size_t base = ((size_t)(compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);
    if (lane == 0) cdf[base] = 0.f;
    float carry = 0.f;
    for (u32 tile = 0; tile < NC; tile += 32) {
        u32 index = tile + lane;
        float value = index < NC
            ? staged_reach[order[(size_t)particle * NC + index]] : 0.f;
        #pragma unroll
        for (int step = 1; step < 32; step <<= 1) {
            float add = __shfl_up_sync(0xffffffff, value, step);
            if (lane >= (u32)step) value += add;
        }
        if (index < NC) cdf[base + index + 1] = carry + value;
        carry += __shfl_sync(0xffffffff, value, 31);
    }
}

