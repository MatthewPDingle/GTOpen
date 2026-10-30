// Supplementary raw-total exposure only; full up_fold is authoritative.
typedef unsigned int u32;
extern "C" __global__ void raw_total(const float* data, const u32* offsets,
    const u32* lengths, u32 count, u32* out) {
    u32 b = blockIdx.x;
    if (b >= count) return;
    int nh_o = lengths[b];
    const float* ro = data + offsets[b];
    __shared__ float total_parts[256];
    float partial = 0.0;
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x)
        partial += (float)ro[j];
    total_parts[threadIdx.x] = partial;
    __syncthreads();
    if (blockDim.x == 128 && blockDim.y == 1 && blockDim.z == 1) {
        for (int step = 64; step >= 32; step >>= 1) {
            if (threadIdx.x < (u32)step)
                total_parts[threadIdx.x] += total_parts[threadIdx.x + step];
            __syncthreads();
        }
        if (threadIdx.x < 32) {
            float v = total_parts[threadIdx.x];
            for (int step = 16; step > 0; step >>= 1) {
                float rhs = __shfl_down_sync(0xffffffffu, v, step);
                if (threadIdx.x < (u32)step) v = v + rhs;
            }
            if (threadIdx.x == 0) total_parts[0] = v;
        }
        __syncthreads();
    } else {
        for (int step = blockDim.x >> 1; step > 0; step >>= 1) {
            if (threadIdx.x < (u32)step)
                total_parts[threadIdx.x] += total_parts[threadIdx.x + step];
            __syncthreads();
        }
    }
    if (threadIdx.x == 0) out[2 + b * 3] = __float_as_uint(total_parts[0]);
}
