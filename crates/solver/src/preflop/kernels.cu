// Preflop solver CUDA kernels: level-synchronous CFR over the 169-class
// lattice, mirroring the CPU traversal in preflop/mod.rs exactly (the
// GPU-vs-CPU equivalence test depends on it).
//
// Layouts:
//  - reach: node-major, then player: reach[(node*np + q)*169 + h]
//  - val:   per-node traverser values: val[node*169 + h]
//  - arenas (regrets/strat/sigma cache): node.data_off + a*169 + h
//
// mode: 0 = update pass (sigma from regrets), 1 = average-strategy
// evaluation, 2 = best response vs the average strategy.

typedef unsigned int u32;
#define NC 169
#define MAX_NA 16

// sigma for one (node, hand) from regrets (mode 0: max(r,0)/sum) or from
// strategy sums (modes 1/2), uniform when the sum vanishes — identical to
// current_strategy()/average_strategy() on the CPU.
__device__ void node_sigma(
    const float* __restrict__ src, u32 off, int na, int h, float* out)
{
    float sum = 0.f;
    for (int a = 0; a < na; a++) {
        float v = src[off + (u32)a * NC + h];
        out[a] = v;
        sum += v;
    }
    if (sum > 1e-12f) {
        for (int a = 0; a < na; a++) out[a] /= sum;
    } else {
        float u = 1.f / (float)na;
        for (int a = 0; a < na; a++) out[a] = u;
    }
}

__device__ void node_sigma_regret(
    const float* __restrict__ regrets, u32 off, int na, int h, float* out)
{
    float sum = 0.f;
    for (int a = 0; a < na; a++) {
        float v = regrets[off + (u32)a * NC + h];
        v = v > 0.f ? v : 0.f;
        out[a] = v;
        sum += v;
    }
    if (sum > 1e-12f) {
        for (int a = 0; a < na; a++) out[a] /= sum;
    } else {
        float u = 1.f / (float)na;
        for (int a = 0; a < na; a++) out[a] = u;
    }
}

// Root reach = class probability for every player.
extern "C" __global__ void pf_init_root(
    const float* __restrict__ cprob, float* reach, int np)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = gridDim.x * blockDim.x;
    int tot = np * NC;
    for (int k = i; k < tot; k += stride) reach[k] = cprob[k % NC];
}

// Down sweep over the action nodes of one level: compute + cache sigma for
// this node, then write every child's full reach block (actor row scaled).
extern "C" __global__ void pf_down(
    const u32* __restrict__ nodes, int start, int count,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children,
    const float* __restrict__ regrets, const float* __restrict__ strat,
    float* sigma_cache, float* reach, int np, int mode)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[start + blockIdx.x];
    int act = actor_arr[nd];
    int na = na_arr[nd];
    u32 off = off_arr[nd];
    u32 cs = cstart_arr[nd];
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float sig[MAX_NA];
        if (mode == 0) node_sigma_regret(regrets, off, na, h, sig);
        else node_sigma(strat, off, na, h, sig);
        for (int a = 0; a < na; a++) sigma_cache[off + (u32)a * NC + h] = sig[a];
        for (int a = 0; a < na; a++) {
            u32 c = children[cs + a];
            for (int q = 0; q < np; q++) {
                float r = reach[((u32)nd * np + q) * NC + h];
                if (q == act) r *= sig[a];
                reach[((u32)c * np + q) * NC + h] = r;
            }
        }
    }
}

// Terminal values for traverser p. kind: 1 = fold win, 2 = pot share.
// One block per terminal; blockDim must be a power of two >= 169.
extern "C" __global__ void pf_terminal(
    const u32* __restrict__ terms, int count, int p, int np,
    const int* __restrict__ kind_arr, const int* __restrict__ live_arr,
    const int* __restrict__ winner_arr,
    const float* __restrict__ potf, const float* __restrict__ pots,
    const float* __restrict__ inv, const float* __restrict__ rw,
    const float* __restrict__ eqtab,
    const float* __restrict__ reach, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = terms[blockIdx.x];
    __shared__ float mass[10];
    __shared__ float smem[256];
    for (int q = 0; q < np; q++) {
        float s = 0.f;
        for (int h = threadIdx.x; h < NC; h += blockDim.x)
            s += reach[((u32)nd * np + q) * NC + h];
        smem[threadIdx.x] = s;
        __syncthreads();
        for (int step = blockDim.x >> 1; step > 0; step >>= 1) {
            if (threadIdx.x < (u32)step) smem[threadIdx.x] += smem[threadIdx.x + step];
            __syncthreads();
        }
        if (threadIdx.x == 0) mass[q] = smem[0];
        __syncthreads();
    }
    float prob = 1.f;
    for (int q = 0; q < np; q++)
        if (q != p) prob *= mass[q];
    int k = kind_arr[nd];
    int lv = live_arr[nd];
    float invp = inv[(u32)nd * np + p];
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float v;
        if (prob <= 0.f) {
            v = 0.f;
        } else if (k == 1) {
            v = prob * ((winner_arr[nd] == p) ? (potf[nd] - invp) : -invp);
        } else if (!((lv >> p) & 1)) {
            v = prob * (-invp);
        } else {
            float eqp = 1.f;
            const float* row = eqtab + (u32)h * NC;
            for (int q = 0; q < np; q++) {
                if (q == p || !((lv >> q) & 1) || mass[q] <= 0.f) continue;
                const float* rq = reach + ((u32)nd * np + q) * NC;
                float d = 0.f;
                for (int j = 0; j < NC; j++) d += row[j] * rq[j];
                eqp *= d / mass[q];
            }
            float pe = pots[nd];
            float share = pe * eqp * rw[(u32)nd * np + p];
            if (share > pe) share = pe;
            v = prob * (share - invp);
        }
        val[(u32)nd * NC + h] = v;
    }
}

// Up sweep over the action nodes of one level (bottom-up): combine child
// values; at the traverser's nodes in mode 0 also apply the regret and
// (reach-weighted) strategy-sum updates.
extern "C" __global__ void pf_up(
    const u32* __restrict__ nodes, int start, int count, int p, int np, int mode,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children,
    const float* __restrict__ sigma_cache, const float* __restrict__ reach,
    float* regrets, float* strat, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[start + blockIdx.x];
    int act = actor_arr[nd];
    int na = na_arr[nd];
    u32 off = off_arr[nd];
    u32 cs = cstart_arr[nd];
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float out;
        if (act == p) {
            if (mode == 2) {
                out = -3.0e38f;
                for (int a = 0; a < na; a++) {
                    float v = val[(u32)children[cs + a] * NC + h];
                    if (v > out) out = v;
                }
            } else {
                out = 0.f;
                for (int a = 0; a < na; a++)
                    out += sigma_cache[off + (u32)a * NC + h] *
                           val[(u32)children[cs + a] * NC + h];
                if (mode == 0) {
                    float rp = reach[((u32)nd * np + p) * NC + h];
                    for (int a = 0; a < na; a++) {
                        u32 ix = off + (u32)a * NC + h;
                        regrets[ix] += val[(u32)children[cs + a] * NC + h] - out;
                        strat[ix] += rp * sigma_cache[ix];
                    }
                }
            }
        } else {
            out = 0.f;
            for (int a = 0; a < na; a++)
                out += val[(u32)children[cs + a] * NC + h];
        }
        val[(u32)nd * NC + h] = out;
    }
}

// DCFR discounting over both arenas (matches iterate() on the CPU).
extern "C" __global__ void pf_discount(
    float* regrets, float* strat, u32 len, float pos, float neg, float sd)
{
    u32 i = blockIdx.x * blockDim.x + threadIdx.x;
    u32 stride = gridDim.x * blockDim.x;
    for (u32 k = i; k < len; k += stride) {
        float r = regrets[k];
        regrets[k] = r * (r > 0.f ? pos : neg);
        strat[k] *= sd;
    }
}
