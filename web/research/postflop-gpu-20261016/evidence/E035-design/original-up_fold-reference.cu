typedef unsigned int u32;
typedef unsigned long long u64;
#define SENTINEL 0xFFFFFFFFu

extern "C" __global__ void up_fold_reference(
    const u32* __restrict__ nodes, int start, int count, int p,
    const int* __restrict__ node_player,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const u32* __restrict__ rsrc0, const u32* __restrict__ rsrc1,
    const float* __restrict__ reach0, const float* __restrict__ reach1,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    const u32* __restrict__ card_off, const u32* __restrict__ card_idx,
    const u32* __restrict__ same_p,
    const u32* __restrict__ cfv_slot, float* cfv,
    int nh_p, int nh_o, int nh_max)
{
    extern __shared__ float local_reach[];
    __shared__ float s[52];
    __shared__ float total_parts[256];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    const float* global_reach = (p == 0 ? reach1 : reach0)
        + (u64)(p == 0 ? rsrc1[n] : rsrc0[n]) * nh_o;
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x)
        local_reach[j] = global_reach[j];
    __syncthreads();
    const float* ro = local_reach;
    // Card lists preserve opponent hand order; all sums use the existing f32 precision.
    // Each card has one writer, so no atomic order noise or contention.
    for (int card = threadIdx.x; card < 52; card += blockDim.x) {
        float sum = 0.0;
        for (u32 k = card_off[card]; k < card_off[card + 1]; k++)
            sum += (float)ro[card_idx[k]];
        s[card] = sum;
    }
    float partial = 0.0;
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x)
        partial += (float)ro[j];
    total_parts[threadIdx.x] = partial;
    __syncthreads();
    for (int step = blockDim.x >> 1; step > 0; step >>= 1) {
        if (threadIdx.x < (u32)step)
            total_parts[threadIdx.x] += total_parts[threadIdx.x + step];
        __syncthreads();
    }
    float T = total_parts[0];
    float amount = node_player[n] == p ? node_tlose[n] : node_twin[n];
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        u32 sc = same_p[i];
        float same_r = sc != SENTINEL ? ro[sc] : 0.f;
        float valid = (float)(T - s[pc1[i]] - s[pc2[i]]) + same_r;
        cfv[(u64)cfv_slot[n] * nh_max + i] = amount * valid;
    }
}

