// 16-bit learning state for full-game continuations: i16 regrets and u16
// strategy sums with one scale per node (the block's largest magnitude), as
// in store.rs. Regret matching is scale-free within a node, so the down
// sweeps read the integers directly. Updates find each node's new maxima,
// then requantize with unbiased rounding from a counter-based threshold
// (one per node and iteration). No locks: callers refuse them.

typedef unsigned int u32;
typedef unsigned long long u64;
typedef short i16;
typedef unsigned short u16;

#define MAX_NA 16

__device__ __forceinline__ float rounding_uniform(u64 seed) {
    u64 bits = seed + 0x9E3779B97F4A7C15ull;
    bits = (bits ^ (bits >> 30)) * 0xBF58476D1CE4E5B9ull;
    bits = (bits ^ (bits >> 27)) * 0x94D049BB133111EBull;
    bits ^= bits >> 31;
    return (float)(bits >> 40) * (1.0f / 16777216.0f);
}

__device__ __forceinline__ float round_unbiased(float v, float u) {
    float f = floorf(v);
    return f + (u < v - f ? 1.f : 0.f);
}

// Unnormalized weight: positive regret (mode 0) or strategy sum (mode 1).
__device__ __forceinline__ float qweight(const i16* rq, const u16* sq, int mode, u64 k) {
    return mode == 0 ? fmaxf((float)rq[k], 0.f) : (float)sq[k];
}

// Down sweep at one level: each child's actor-side reach.
extern "C" __global__ void down_action_q(
    const u32* __restrict__ nodes, int start, int count, int mode,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off, const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    const u32* __restrict__ rsrc0, const u32* __restrict__ rsrc1,
    const i16* __restrict__ rq0, const i16* __restrict__ rq1,
    const u16* __restrict__ sq0, const u16* __restrict__ sq1,
    float* reach0, float* reach1, int nh0, int nh1)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int actor = node_player[n];
    int na = node_na[n];
    u64 off = node_data_off[n];
    u32 cs = node_children_start[n];
    const i16* rq = actor == 0 ? rq0 : rq1;
    const u16* sq = actor == 0 ? sq0 : sq1;
    float* reach = actor == 0 ? reach0 : reach1;
    const u32* rsrc = actor == 0 ? rsrc0 : rsrc1;
    int nh = actor == 0 ? nh0 : nh1;
    const float* parent = reach + (u64)rsrc[n] * nh;
    for (int i = threadIdx.x; i < nh; i += blockDim.x) {
        float sum = 0.f;
        for (int a = 0; a < na; a++) sum += qweight(rq, sq, mode, off + (u64)a * nh + i);
        float pr = parent[i];
        for (int a = 0; a < na; a++) {
            float sg = sum > 0.f ? qweight(rq, sq, mode, off + (u64)a * nh + i) / sum : 1.f / na;
            reach[(u64)rsrc[children[cs + a]] * nh + i] = pr * sg;
        }
    }
}

__device__ float block_max(float v, float* scratch) {
    scratch[threadIdx.x] = v;
    __syncthreads();
    for (int s = blockDim.x >> 1; s > 0; s >>= 1) {
        if (threadIdx.x < (u32)s) scratch[threadIdx.x] = fmaxf(scratch[threadIdx.x], scratch[threadIdx.x + s]);
        __syncthreads();
    }
    float r = scratch[0];
    __syncthreads();
    return r;
}

// Up sweep at one level for traverser p: node values, and at p's own nodes
// the regret and strategy-sum updates with requantization.
extern "C" __global__ void up_action_q(
    const u32* __restrict__ nodes, int start, int count, int p,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off, const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    i16* rq, u16* sq, float* rsc, float* ssc,
    const u32* __restrict__ rsrc_p, const float* __restrict__ reach_p_buf,
    const u32* __restrict__ cfv_slot, float* cfv,
    const float* __restrict__ disc, u32 iteration, int nh_p, int nh_max)
{
    __shared__ float red[256];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int na = node_na[n];
    const u32* ch = children + node_children_start[n];
    float* out = cfv + (u64)cfv_slot[n] * nh_max;
    if (node_player[n] != p) {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float v = 0.f;
            for (int a = 0; a < na; a++) v += cfv[(u64)cfv_slot[ch[a]] * nh_max + i];
            out[i] = v;
        }
        return;
    }
    u64 off = node_data_off[n];
    float kr = rsc[n] / 32767.f;
    float dpos = disc[0], dneg = disc[1];
    float kss = ssc[n] / 65535.f * disc[2];
    const float* rp = reach_p_buf + (u64)rsrc_p[n] * nh_p;
    float rmax = 0.f, smax = 0.f;
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        float sum = 0.f;
        for (int a = 0; a < na; a++) sum += qweight(rq, sq, 0, off + (u64)a * nh_p + i);
        float v = 0.f;
        for (int a = 0; a < na; a++) {
            float sg = sum > 0.f ? qweight(rq, sq, 0, off + (u64)a * nh_p + i) / sum : 1.f / na;
            v += sg * cfv[(u64)cfv_slot[ch[a]] * nh_max + i];
        }
        float rr = rp[i];
        for (int a = 0; a < na; a++) {
            u64 k = off + (u64)a * nh_p + i;
            float sg = sum > 0.f ? qweight(rq, sq, 0, k) / sum : 1.f / na;
            float q = (float)rq[k];
            float nr = q * kr * (q > 0.f ? dpos : dneg) + (cfv[(u64)cfv_slot[ch[a]] * nh_max + i] - v);
            rmax = fmaxf(rmax, fabsf(nr));
            smax = fmaxf(smax, (float)sq[k] * kss + rr * sg);
        }
        out[i] = v;
    }
    rmax = block_max(rmax, red);
    smax = block_max(smax, red);
    u64 seed = ((u64)iteration << 32) | (u64)n;
    float ur = rounding_uniform(seed);
    float us = rounding_uniform(seed ^ 0xD1B54A32D192ED03ull);
    bool rok = rmax > 0.f && isfinite(rmax), sok = smax > 0.f && isfinite(smax);
    float rk = rok ? 32767.f / rmax : 0.f, sk = sok ? 65535.f / smax : 0.f;
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        float v = out[i];
        float sum = 0.f;
        for (int a = 0; a < na; a++) sum += qweight(rq, sq, 0, off + (u64)a * nh_p + i);
        float rr = rp[i];
        // Every action's new values come from the old ones before any entry
        // of this hand is overwritten.
        float nrs[MAX_NA], ss[MAX_NA];
        for (int a = 0; a < na; a++) {
            u64 k = off + (u64)a * nh_p + i;
            float sg = sum > 0.f ? qweight(rq, sq, 0, k) / sum : 1.f / na;
            float q = (float)rq[k];
            nrs[a] = q * kr * (q > 0.f ? dpos : dneg) + (cfv[(u64)cfv_slot[ch[a]] * nh_max + i] - v);
            ss[a] = (float)sq[k] * kss + rr * sg;
        }
        for (int a = 0; a < na; a++) {
            u64 k = off + (u64)a * nh_p + i;
            float nr = nrs[a], s = ss[a];
            rq[k] = !rok ? 0 : (nr == rmax ? 32767 : (nr == -rmax ? -32767 : (i16)round_unbiased(nr * rk, ur)));
            sq[k] = !sok ? 0 : (s == smax ? 65535 : (u16)round_unbiased(fmaxf(s, 0.f) * sk, us));
        }
    }
    if (threadIdx.x == 0) {
        rsc[n] = rok ? rmax : 0.f;
        ssc[n] = sok ? smax : 0.f;
    }
}

// Evaluation up sweep: mode 0 best response, mode 1 average strategy.
extern "C" __global__ void up_action_eval_q(
    const u32* __restrict__ nodes, int start, int count, int p, int mode,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off, const u32* __restrict__ node_children_start,
    const u32* __restrict__ children, const u16* __restrict__ sq,
    const u32* __restrict__ cfv_slot, float* cfv, int nh_p, int nh_max)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int na = node_na[n];
    const u32* ch = children + node_children_start[n];
    float* out = cfv + (u64)cfv_slot[n] * nh_max;
    bool own = node_player[n] == p;
    u64 off = node_data_off[n];
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        float v;
        if (!own) {
            v = 0.f;
            for (int a = 0; a < na; a++) v += cfv[(u64)cfv_slot[ch[a]] * nh_max + i];
        } else if (mode == 0) {
            v = cfv[(u64)cfv_slot[ch[0]] * nh_max + i];
            for (int a = 1; a < na; a++) v = fmaxf(v, cfv[(u64)cfv_slot[ch[a]] * nh_max + i]);
        } else {
            float sum = 0.f;
            for (int a = 0; a < na; a++) sum += (float)sq[off + (u64)a * nh_p + i];
            v = 0.f;
            for (int a = 0; a < na; a++) {
                float sg = sum > 0.f ? (float)sq[off + (u64)a * nh_p + i] / sum : 1.f / na;
                v += sg * cfv[(u64)cfv_slot[ch[a]] * nh_max + i];
            }
        }
        out[i] = v;
    }
}

// Stabilizer projection of one player's 16-bit state (see
// continuation_projection.cu): orbit averages, rounded to nearest, then
// broadcast. A node's scale is unchanged because an average never exceeds
// the block maximum.
extern "C" __global__ void continuation_project_q(
    const u32* nodes, int count, const int* players, const int* na,
    const u64* offsets, const u32* stabilizers, const u32* permutations,
    i16* rq, u16* sq, int nh, int player, int broadcast)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[b], mask = stabilizers[n];
    if (players[n] != player || mask == 1) return;
    for (int i = threadIdx.x; i < nh; i += blockDim.x) {
        int canonical = i;
        for (u32 m = mask; m; m &= m - 1) {
            int k = __ffs(m) - 1;
            int j = permutations[(u64)k * nh + i];
            if (j < canonical) canonical = j;
        }
        if (broadcast) {
            if (canonical == i) continue;
            for (int a = 0; a < na[n]; a++) {
                u64 base = offsets[n] + (u64)a * nh;
                rq[base + i] = rq[base + canonical];
                sq[base + i] = sq[base + canonical];
            }
        } else if (canonical == i) {
            for (int a = 0; a < na[n]; a++) {
                u64 base = offsets[n] + (u64)a * nh;
                float r = 0.f, s = 0.f;
                int size = 0;
                for (u32 m = mask; m; m &= m - 1) {
                    int k = __ffs(m) - 1;
                    u64 j = base + permutations[(u64)k * nh + i];
                    r += (float)rq[j];
                    s += (float)sq[j];
                    size++;
                }
                rq[base + i] = (i16)rintf(r / size);
                sq[base + i] = (u16)rintf(s / size);
            }
        }
    }
}
