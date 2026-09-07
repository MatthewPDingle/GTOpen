// Preflop solver CUDA kernels: level-synchronous CFR over the 169-class
// lattice, mirroring the CPU traversal in preflop/mod.rs exactly (the
// GPU-vs-CPU equivalence test depends on it).
//
// Layouts:
//  - reach: compact blocks; reach_src[node*np+q] names the current block.
//    Roots use blocks 0..np; each non-root node has one new actor block.
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

// Per-node reach/value blocks are addressed in 64-bit (size_t): n * np * 169
// floats passes 2^32 on 40 GB cards long before the VRAM budget refuses the
// tree. Arena offsets stay u32 (the host refuses arenas beyond 2^32 entries).
// Down sweep over the action nodes of one level: compute + cache sigma for
// this node, then write each child's actor reach. Other seats share their
// unchanged ancestor blocks through reach_src.
// src: 0 = learning node (regrets in the update pass, strategy sums when
// evaluating), 1 = frozen actor (strategy sums always — its average IS its
// play), 2 = forced sigma (point lock / profile) read from forced[foff..].
extern "C" __global__ void pf_down(
    const u32* __restrict__ nodes, int start, int count,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children,
    const float* __restrict__ regrets, const float* __restrict__ strat,
    const int* __restrict__ src_arr, const u32* __restrict__ foff_arr,
    const float* __restrict__ forced,
    float* sigma_cache, const u32* __restrict__ reach_src,
    float* reach, int np, int mode)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[start + blockIdx.x];
    int act = actor_arr[nd];
    int na = na_arr[nd];
    u32 off = off_arr[nd];
    u32 cs = cstart_arr[nd];
    int src = src_arr[nd];
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float sig[MAX_NA];
        if (src == 2) {
            u32 fo = foff_arr[nd];
            for (int a = 0; a < na; a++) sig[a] = forced[fo + (u32)a * NC + h];
        } else if (src == 1 || mode != 0) {
            node_sigma(strat, off, na, h, sig);
        } else {
            node_sigma_regret(regrets, off, na, h, sig);
        }
        for (int a = 0; a < na; a++) sigma_cache[off + (u32)a * NC + h] = sig[a];
        for (int a = 0; a < na; a++) {
            u32 c = children[cs + a];
            float r = reach[(size_t)reach_src[(size_t)nd * np + act] * NC + h];
            reach[(size_t)reach_src[(size_t)c * np + act] * NC + h] = r * sig[a];
        }
    }
}

// Compute each distinct reach block's mass once per down sweep. The same
// 256-thread reduction tree as pf_terminal preserves every addition's order.
extern "C" __global__ void pf_reach_mass(
    const float* __restrict__ reach, float* mass)
{
    __shared__ float smem[256];
    float sum = 0.f;
    for (int h = threadIdx.x; h < NC; h += blockDim.x)
        sum += reach[(size_t)blockIdx.x * NC + h];
    smem[threadIdx.x] = sum;
    __syncthreads();
    for (int step = blockDim.x >> 1; step > 0; step >>= 1) {
        if (threadIdx.x < (u32)step) smem[threadIdx.x] += smem[threadIdx.x + step];
        __syncthreads();
    }
    if (threadIdx.x == 0) mass[blockIdx.x] = smem[0];
}

// One normalized equity vector per distinct required opponent reach block.
// Each hero dot product keeps the original opponent-class accumulation order.
extern "C" __global__ void pf_equities(
    const u32* __restrict__ work, u32 start,
    const u32* __restrict__ blocks, const float* __restrict__ eqtab,
    const float* __restrict__ reach, const float* __restrict__ mass,
    float* cache)
{
    u32 slot = work[start + blockIdx.x];
    u32 block = blocks[slot];
    __shared__ float rq[NC];
    for (int j = threadIdx.x; j < NC; j += blockDim.x)
        rq[j] = reach[(size_t)block * NC + j];
    __syncthreads();
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float value = 0.f;
        if (mass[block] > 0.f) {
            float d = 0.f;
            for (int j = 0; j < NC; j++) d += eqtab[(u32)j * NC + h] * rq[j];
            value = d / mass[block];
        }
        cache[(size_t)slot * NC + h] = value;
    }
}

// Terminal values for traverser p. kind: 1 = fold win, 2 = pot share.
// One block per terminal; blockDim must be a power of two >= 169.
// calib[nd] != 0 marks a heads-up pot-share terminal with chips behind
// priced by the calibrated realization fit (terminal_value() on the CPU):
// share = GROSS pot x equity x clamp(cbase[h] * rw, clip_lo, clip_hi) — no
// rake deduction (the fit is net-of-rake already) and no pot cap.
extern "C" __global__ void pf_terminal(
    const u32* __restrict__ terms, int count, int p, int np,
    const int* __restrict__ kind_arr, const int* __restrict__ live_arr,
    const int* __restrict__ winner_arr,
    const float* __restrict__ potf, const float* __restrict__ pots,
    const float* __restrict__ inv, const float* __restrict__ rw,
    const float* __restrict__ potg, const int* __restrict__ calib,
    const float* __restrict__ cbase, float clip_lo, float clip_hi,
    const float* __restrict__ eqtab,
    const u32* __restrict__ reach_src,
    const float* __restrict__ reach,
    const float* __restrict__ reach_mass,
    const u32* __restrict__ eq_slots, const float* __restrict__ eq_cache,
    int use_eq_cache, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = terms[blockIdx.x];
    float mass[10];
    for (int q = 0; q < np; q++)
        if (q != p) mass[q] = reach_mass[reach_src[(size_t)nd * np + q]];
    float prob = 1.f;
    for (int q = 0; q < np; q++)
        if (q != p) prob *= mass[q];
    int k = kind_arr[nd];
    int lv = live_arr[nd];
    float invp = inv[(size_t)nd * np + p];
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
            for (int q = 0; q < np; q++) {
                if (q == p || !((lv >> q) & 1) || mass[q] <= 0.f) continue;
                u32 block = reach_src[(size_t)nd * np + q];
                float equity;
                if (use_eq_cache) {
                    equity = eq_cache[(size_t)eq_slots[block] * NC + h];
                } else {
                    const float* rq = reach + (size_t)block * NC;
                    float d = 0.f;
                    for (int j = 0; j < NC; j++) d += eqtab[(u32)j * NC + h] * rq[j];
                    equity = d / mass[q];
                }
                eqp *= equity;
            }
            float w = rw[(size_t)nd * np + p];
            float share;
            if (calib[nd]) {
                float r = cbase[h] * w;
                r = r < clip_lo ? clip_lo : (r > clip_hi ? clip_hi : r);
                share = potg[nd] * eqp * r;
            } else {
                float pe = pots[nd];
                share = pe * eqp * w;
                if (share > pe) share = pe;
            }
            v = prob * (share - invp);
        }
        val[(size_t)nd * NC + h] = v;
    }
}

// Up sweep over the action nodes of one level (bottom-up): combine child
// values; at the traverser's LEARNING nodes (src == 0) in mode 0 also apply
// the regret and (reach-weighted) strategy-sum updates. Best response
// (mode 2) still maxes at a frozen/forced traverser's nodes: that gap is
// the seat's bleed against its pinned strategy, as on the CPU.
extern "C" __global__ void pf_up(
    const u32* __restrict__ nodes, int start, int count, int p, int np, int mode,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children, const int* __restrict__ src_arr,
    const float* __restrict__ sigma_cache, const u32* __restrict__ reach_src,
    const float* __restrict__ reach,
    float* regrets, float* strat, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[start + blockIdx.x];
    int act = actor_arr[nd];
    int na = na_arr[nd];
    u32 off = off_arr[nd];
    u32 cs = cstart_arr[nd];
    int learning = src_arr[nd] == 0;
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float out;
        if (act == p) {
            if (mode == 2) {
                out = -3.0e38f;
                for (int a = 0; a < na; a++) {
                    float v = val[(size_t)children[cs + a] * NC + h];
                    if (v > out) out = v;
                }
            } else {
                out = 0.f;
                for (int a = 0; a < na; a++)
                    out += sigma_cache[off + (u32)a * NC + h] *
                           val[(size_t)children[cs + a] * NC + h];
                if (mode == 0 && learning) {
                    float rp = reach[(size_t)reach_src[(size_t)nd * np + p] * NC + h];
                    for (int a = 0; a < na; a++) {
                        u32 ix = off + (u32)a * NC + h;
                        regrets[ix] += val[(size_t)children[cs + a] * NC + h] - out;
                        strat[ix] += rp * sigma_cache[ix];
                    }
                }
            }
        } else {
            out = 0.f;
            for (int a = 0; a < na; a++)
                out += val[(size_t)children[cs + a] * NC + h];
        }
        val[(size_t)nd * NC + h] = out;
    }
}

// DCFR discounting, one block per action node (matches iterate() on the
// CPU): regrets always; strategy sums except at a frozen actor's nodes,
// whose sums receive no additions and ARE its play — decaying them would
// underflow the average to uniform.
extern "C" __global__ void pf_discount_nodes(
    const u32* __restrict__ nodes, int count,
    const int* __restrict__ na_arr, const u32* __restrict__ off_arr,
    const int* __restrict__ src_arr,
    float* regrets, float* strat, float pos, float neg, float sd)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[blockIdx.x];
    int len = na_arr[nd] * NC;
    u32 off = off_arr[nd];
    int frozen = src_arr[nd] == 1;
    for (int k = threadIdx.x; k < len; k += blockDim.x) {
        float r = regrets[off + k];
        regrets[off + k] = r * (r > 0.f ? pos : neg);
        if (!frozen) strat[off + k] *= sd;
    }
}
