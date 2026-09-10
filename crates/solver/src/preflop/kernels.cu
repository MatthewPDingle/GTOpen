// Preflop solver CUDA kernels: level-synchronous CFR over the 169-class
// lattice, mirroring the CPU traversal in preflop/mod.rs exactly (the
// GPU-vs-CPU equivalence test depends on it).
//
// Layouts:
//  - reach: compact blocks; reach_src[node*np+q] names the current block.
//    Roots use blocks 0..np; each non-root node has one new actor block.
//  - val:   traverser values: val[val_slot[node]*169 + h]; terminals stay
//           persistent, action scratch alternates between tree depths
//  - arenas (regrets/strat): node.data_off + a*169 + h
//
// mode: 0 = update pass (sigma from regrets), 1 = average-strategy
// evaluation, 2 = best response vs the average strategy.

typedef unsigned int u32;
#define NC 169
#define MAX_NA 16

// sigma for one (node, hand) from regrets (mode 0: max(r,0)/sum) or from
// strategy sums (modes 1/2), uniform when the sum vanishes — identical to
// current_strategy()/average_strategy() on the CPU.
__device__ __forceinline__ void node_sigma(
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

__device__ __forceinline__ void node_sigma_regret(
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
// Down sweep over the action nodes of one level: compute sigma for
// this node, then write each child's actor reach. Other seats share their
// unchanged ancestor blocks through reach_src.
// src: 0 = learning node (regrets in the update pass, strategy sums when
// evaluating), 1 = frozen actor (strategy sums always — its average IS its
// play), 2 = forced sigma (point lock / profile) read from forced[foff..].
template<int NA>
__device__ __forceinline__ void pf_down_impl(
    const u32* __restrict__ nodes, int start, int count,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children,
    const float* __restrict__ regrets, const float* __restrict__ strat,
    const int* __restrict__ src_arr, const u32* __restrict__ foff_arr,
    const float* __restrict__ forced,
    const u32* __restrict__ reach_src,
    float* reach, int np, int mode)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[start + blockIdx.x];
    int act = actor_arr[nd];
    const int na = NA == 0 ? na_arr[nd] : NA;
    u32 off = off_arr[nd];
    u32 cs = cstart_arr[nd];
    int src = src_arr[nd];
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float sig[NA == 0 ? MAX_NA : NA];
        if (src == 2) {
            u32 fo = foff_arr[nd];
            for (int a = 0; a < na; a++) sig[a] = forced[fo + (u32)a * NC + h];
        } else if (src == 1 || mode != 0) {
            node_sigma(strat, off, na, h, sig);
        } else {
            node_sigma_regret(regrets, off, na, h, sig);
        }
        for (int a = 0; a < na; a++) {
            u32 c = children[cs + a];
            float r = reach[(size_t)reach_src[(size_t)nd * np + act] * NC + h];
            reach[(size_t)reach_src[(size_t)c * np + act] * NC + h] = r * sig[a];
        }
    }
}

extern "C" __global__ void pf_down(
    const u32* __restrict__ nodes, int start, int count,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children,
    const float* __restrict__ regrets, const float* __restrict__ strat,
    const int* __restrict__ src_arr, const u32* __restrict__ foff_arr,
    const float* __restrict__ forced,
    const u32* __restrict__ reach_src,
    float* reach, int np, int mode)
{
    if (blockIdx.x >= (u32)count) return;
    const int na = na_arr[nodes[start + blockIdx.x]];
    if (na == 2) pf_down_impl<2>(nodes, start, count, actor_arr, na_arr, off_arr, cstart_arr, children, regrets, strat, src_arr, foff_arr, forced, reach_src, reach, np, mode);
    else if (na == 3) pf_down_impl<3>(nodes, start, count, actor_arr, na_arr, off_arr, cstart_arr, children, regrets, strat, src_arr, foff_arr, forced, reach_src, reach, np, mode);
    else if (na == 4) pf_down_impl<4>(nodes, start, count, actor_arr, na_arr, off_arr, cstart_arr, children, regrets, strat, src_arr, foff_arr, forced, reach_src, reach, np, mode);
    else pf_down_impl<0>(nodes, start, count, actor_arr, na_arr, off_arr, cstart_arr, children, regrets, strat, src_arr, foff_arr, forced, reach_src, reach, np, mode);
}

// Compute each reach total using the original 256-lane addition tree.
// Only 169 inputs exist: 128 threads reproduce the first 128 pair sums,
// then perform exactly the same 64/32/.../1 reductions. Launch with 128 lanes.
extern "C" __global__ void pf_reach_mass(
    const float* __restrict__ reach, float* mass)
{
    __shared__ float smem[128];
    u32 h = threadIdx.x;
    float lo = 0.f, hi = 0.f;
    lo += reach[(size_t)blockIdx.x * NC + h];
    if (h + 128 < NC) hi += reach[(size_t)blockIdx.x * NC + h + 128];
    smem[h] = lo + hi;
    __syncthreads();
    for (int step = 64; step > 0; step >>= 1) {
        if (h < (u32)step) smem[h] += smem[h + step];
        __syncthreads();
    }
    if (h == 0) mass[blockIdx.x] = smem[0];
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

// Reset the scratch before each traverser. No host readback or dynamic launch.
extern "C" __global__ void pf_multiway_clear_active(u32* active, u32 count)
{
    u32 slot = blockIdx.x * blockDim.x + threadIdx.x;
    if (slot < count) active[slot] = 0;
}

// Counterfactual probability excludes p, but includes folded opponents.
// Zero own reach MUST NOT prune a counterfactual value/regret update.
extern "C" __global__ void pf_multiway_prepare(
    const u32* __restrict__ terms, u32 count, int p, int np,
    const int* __restrict__ live, const u32* __restrict__ reach_src,
    const float* __restrict__ reach_mass, const u32* __restrict__ slots,
    u32* active, float* terminal_prob)
{
    u32 index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= count) return;
    u32 nd = terms[index];
    int lv = live[nd];
    if (!((lv >> p) & 1)) { terminal_prob[index] = 0.f; return; }
    float prob = 1.f;
    // Identical order and float arithmetic to the former per-batch calculation.
    for (int q = 0; q < np; q++) {
        if (q == p) continue;
        u32 source = reach_src[(size_t)nd * np + q];
        prob *= reach_mass[source];
    }
    terminal_prob[index] = prob;
    if (prob <= 0.f) return;
    for (int q = 0; q < np; q++) {
        if (q == p || !((lv >> q) & 1)) continue;
        u32 source = reach_src[(size_t)nd * np + q];
        // Multiple terminals may need a slot. Atomic writes avoid a data race.
        atomicExch(active + slots[source], 1u);
    }
}

// Inclusive scan in particle rank order, cached as an exclusive 170-entry
// CDF. Four independent warps handle four particles for the same reach.
extern "C" __global__ void pf_multiway_cdf(
    const u32* __restrict__ work, u32 start,
    const u32* __restrict__ blocks, const u32* __restrict__ order,
    const float* __restrict__ reach, const float* __restrict__ mass,
    const u32* __restrict__ active,
    float* cdf, u32 sample_start, u32 sample_count, u32 batch_capacity)
{
    u32 slot = work[start + blockIdx.x];
    if (!active[slot]) return;
    u32 block = blocks[slot];
    u32 local = blockIdx.y * 4 + threadIdx.x / 32;
    if (local >= sample_count || mass[block] <= 0.f) return;
    u32 particle = sample_start + local;
    u32 lane = threadIdx.x & 31;
    size_t base = ((size_t)slot * batch_capacity + local) * (NC + 1);
    if (lane == 0) cdf[base] = 0.f;
    float carry = 0.f;
    for (u32 tile = 0; tile < NC; tile += 32) {
        u32 index = tile + lane;
        float value = index < NC
            ? reach[(size_t)block * NC + order[(size_t)particle * NC + index]] / mass[block] : 0.f;
        #pragma unroll
        for (int step = 1; step < 32; step <<= 1) {
            float add = __shfl_up_sync(0xffffffff, value, step);
            if (lane >= (u32)step) value += add;
        }
        if (index < NC) cdf[base + index + 1] = carry + value;
        carry += __shfl_sync(0xffffffff, value, 31);
    }
}

// Five-point Gauss-Legendre integration on [0,1]. With at most eight
// opponents the product of (strictly-lower mass + t * tied mass) has degree
// at most eight, so this integrates every tied winner's 1/(ties+1) share.
__constant__ float PF_MW_T[5] = {
    0.046910077030668f, 0.230765344947158f, 0.5f,
    0.769234655052842f, 0.953089922969332f
};
__constant__ float PF_MW_W[5] = {
    0.118463442528095f, 0.239314335249683f, 0.284444444444444f,
    0.239314335249683f, 0.118463442528095f
};
__constant__ float PF_MW_T2[2] = {0.211324865405187f, 0.788675134594813f};
__constant__ float PF_MW_W2[2] = {0.5f, 0.5f};
__constant__ float PF_MW_T3[3] = {0.112701665379258f, 0.5f, 0.887298334620742f};
__constant__ float PF_MW_W3[3] = {0.277777777777778f, 0.444444444444444f, 0.277777777777778f};
__constant__ float PF_MW_T4[4] = {0.069431844202974f, 0.330009478207572f, 0.669990521792428f, 0.930568155797026f};
__constant__ float PF_MW_W4[4] = {0.173927422568727f, 0.326072577431273f, 0.326072577431273f, 0.173927422568727f};

template<int Q>
__device__ __forceinline__ float pf_multiway_sum(
    u32 h, int nopponents, const u32* opponent_slots, const float* cdf,
    const u32* lower, const u32* upper,
    u32 sample_start, u32 sample_count, u32 batch_capacity)
{
    float sum = 0.f;
    for (u32 local = 0; local < sample_count; local++) {
        size_t hand = (size_t)(sample_start + local) * NC + h;
        u32 lo = lower[hand], hi = upper[hand];
        float product[Q];
        #pragma unroll
        for (int t = 0; t < Q; t++) product[t] = 1.f;
        for (int q = 0; q < nopponents; q++) {
            size_t base = ((size_t)opponent_slots[q] * batch_capacity + local) * (NC + 1);
            float less = cdf[base + lo];
            float equal = fmaxf(0.f, cdf[base + hi] - less);
            #pragma unroll
            for (int t = 0; t < Q; t++) {
                float point = Q == 2 ? PF_MW_T2[t] : Q == 3 ? PF_MW_T3[t] : Q == 4 ? PF_MW_T4[t] : PF_MW_T[t];
                product[t] *= less + point * equal;
            }
        }
        #pragma unroll
        for (int t = 0; t < Q; t++) {
            float weight = Q == 2 ? PF_MW_W2[t] : Q == 3 ? PF_MW_W3[t] : Q == 4 ? PF_MW_W4[t] : PF_MW_W[t];
            sum += weight * product[t];
        }
    }
    return sum;
}

extern "C" __global__ void pf_multiway_terminal(
    const u32* __restrict__ terms, int p, int np,
    const int* __restrict__ live, const float* __restrict__ pots,
    const float* __restrict__ invested, const u32* __restrict__ reach_src,
    const float* __restrict__ terminal_prob,
    const u32* __restrict__ slots, const float* __restrict__ cdf,
    const u32* __restrict__ lower, const u32* __restrict__ upper,
    u32 sample_start, u32 sample_count, u32 batch_capacity, u32 samples,
    const u32* __restrict__ val_slot, float* val)
{
    u32 nd = terms[blockIdx.x];
    int lv = live[nd];
    if (!((lv >> p) & 1)) return; // already handled by the ordinary terminal
    __shared__ float prob;
    __shared__ u32 opponent_slots[9];
    __shared__ int nopponents;
    if (threadIdx.x == 0) {
        prob = terminal_prob[blockIdx.x];
        nopponents = 0;
        if (!(prob <= 0.f)) {
            for (int q = 0; q < np; q++) {
                if (q == p || !((lv >> q) & 1)) continue;
                u32 source = reach_src[(size_t)nd * np + q];
                opponent_slots[nopponents++] = slots[source];
            }
        }
    }
    __syncthreads();
    for (u32 h = threadIdx.x; h < NC; h += blockDim.x) {
        size_t at = (size_t)val_slot[nd] * NC + h;
        if (prob <= 0.f) { if (sample_start == 0) val[at] = 0.f; continue; }
        // Q-point Gauss is exact through degree 2Q-1. The degree here is the
        // number of opponents, so common 3/4-player pots need only two points.
        float sum = nopponents <= 3
            ? pf_multiway_sum<2>(h, nopponents, opponent_slots, cdf, lower, upper, sample_start, sample_count, batch_capacity)
            : nopponents <= 5
            ? pf_multiway_sum<3>(h, nopponents, opponent_slots, cdf, lower, upper, sample_start, sample_count, batch_capacity)
            : nopponents <= 7
            ? pf_multiway_sum<4>(h, nopponents, opponent_slots, cdf, lower, upper, sample_start, sample_count, batch_capacity)
            : pf_multiway_sum<5>(h, nopponents, opponent_slots, cdf, lower, upper, sample_start, sample_count, batch_capacity);
        float increment = prob * pots[nd] * sum / (float)samples;
        if (sample_start == 0)
            val[at] = increment - prob * invested[(size_t)nd * np + p];
        else
            val[at] += increment;
    }
}

// Terminal values for traverser p. kind: 1 = fold win, 2 = pot share.
// One block per terminal; threads stride over the 169 classes.
// calib[nd] != 0 marks a heads-up pot-share terminal with chips behind
// priced by the calibrated realization fit (terminal_value() on the CPU):
// share = GROSS pot x equity x clamp(cbase[h] * rw, clip_lo, clip_hi) — no
// rake deduction (the fit is net-of-rake already) and no pot cap.
template<int NP>
__device__ __forceinline__ void pf_terminal_impl(
    const u32* __restrict__ terms, int count, int p, int runtime_np,
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
    int use_eq_cache, int use_multiway, const u32* __restrict__ val_slot, float* val)
{
    const int np = NP == 0 ? runtime_np : NP;
    if (blockIdx.x >= (u32)count) return;
    u32 nd = terms[blockIdx.x];
    // Generic seat counts otherwise spill dynamically indexed masses.
    // Keep the faster direct-register path for the specialized 2/6/8 kernels.
    __shared__ float block_mass[10];
    __shared__ float block_prob;
    float private_mass[NP == 0 ? 1 : NP];
    float* mass = NP == 0 ? block_mass : private_mass;
    float prob;
    if (NP == 0) {
        if (threadIdx.x == 0) {
            for (int q = 0; q < np; q++)
                if (q != p) mass[q] = reach_mass[reach_src[(size_t)nd * np + q]];
            float value = 1.f;
            for (int q = 0; q < np; q++)
                if (q != p) value *= mass[q];
            block_prob = value;
        }
        __syncthreads();
        prob = block_prob;
    } else {
        for (int q = 0; q < np; q++)
            if (q != p) mass[q] = reach_mass[reach_src[(size_t)nd * np + q]];
        prob = 1.f;
        for (int q = 0; q < np; q++)
            if (q != p) prob *= mass[q];
    }
    int k = kind_arr[nd];
    int lv = live_arr[nd];
    float invp = inv[(size_t)nd * np + p];
    // The coupled kernel fills live multiway values after each CDF batch.
    if (use_multiway && k == 2 && __popc((u32)lv) >= 3 && ((lv >> p) & 1)) return;
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
        val[(size_t)val_slot[nd] * NC + h] = v;
    }
}

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
    int use_eq_cache, int use_multiway, const u32* __restrict__ val_slot, float* val)
{
    pf_terminal_impl<0>(terms, count, p, np, kind_arr, live_arr, winner_arr, potf, pots, inv, rw, potg, calib, cbase, clip_lo, clip_hi, eqtab, reach_src, reach, reach_mass, eq_slots, eq_cache, use_eq_cache, use_multiway, val_slot, val);
}

extern "C" __global__ void pf_terminal_2(
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
    int use_eq_cache, int use_multiway, const u32* __restrict__ val_slot, float* val)
{
    pf_terminal_impl<2>(terms, count, p, np, kind_arr, live_arr, winner_arr, potf, pots, inv, rw, potg, calib, cbase, clip_lo, clip_hi, eqtab, reach_src, reach, reach_mass, eq_slots, eq_cache, use_eq_cache, use_multiway, val_slot, val);
}

extern "C" __global__ void pf_terminal_6(
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
    int use_eq_cache, int use_multiway, const u32* __restrict__ val_slot, float* val)
{
    pf_terminal_impl<6>(terms, count, p, np, kind_arr, live_arr, winner_arr, potf, pots, inv, rw, potg, calib, cbase, clip_lo, clip_hi, eqtab, reach_src, reach, reach_mass, eq_slots, eq_cache, use_eq_cache, use_multiway, val_slot, val);
}

extern "C" __global__ void pf_terminal_8(
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
    int use_eq_cache, int use_multiway, const u32* __restrict__ val_slot, float* val)
{
    pf_terminal_impl<8>(terms, count, p, np, kind_arr, live_arr, winner_arr, potf, pots, inv, rw, potg, calib, cbase, clip_lo, clip_hi, eqtab, reach_src, reach, reach_mass, eq_slots, eq_cache, use_eq_cache, use_multiway, val_slot, val);
}

// Up sweep over the action nodes of one level (bottom-up): combine child
// values; at the traverser's LEARNING nodes (src == 0) in mode 0 also apply
// the regret and (reach-weighted) strategy-sum updates. Best response
// (mode 2) still maxes at a frozen/forced traverser's nodes: that gap is
// the seat's bleed against its pinned strategy, as on the CPU. Mode 3
// measures adaptive-profile convergence: deviate only at learning nodes.
template<int NA>
__device__ __forceinline__ void pf_up_impl(
    const u32* __restrict__ nodes, int start, int count, int p, int np, int mode,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children, const int* __restrict__ src_arr,
    const u32* __restrict__ foff_arr, const float* __restrict__ forced,
    const u32* __restrict__ reach_src,
    const float* __restrict__ reach,
    float* regrets, float* strat, const u32* __restrict__ val_slot, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[start + blockIdx.x];
    int act = actor_arr[nd];
    const int na = NA == 0 ? na_arr[nd] : NA;
    u32 off = off_arr[nd];
    u32 cs = cstart_arr[nd];
    int src = src_arr[nd];
    int learning = src == 0;
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float out;
        if (act == p) {
            if (mode == 2 || (mode == 3 && learning)) {
                out = -3.0e38f;
                for (int a = 0; a < na; a++) {
                    float v = val[(size_t)val_slot[children[cs + a]] * NC + h];
                    if (v > out) out = v;
                }
            } else {
                // This node's arenas have not been updated yet in the up
                // sweep. Recompute the exact down-sweep probabilities here
                // instead of storing a full arena at every player's sweep.
                float sig[NA == 0 ? MAX_NA : NA];
                if (src == 2) {
                    u32 fo = foff_arr[nd];
                    for (int a = 0; a < na; a++) sig[a] = forced[fo + (u32)a * NC + h];
                } else if (src == 1 || mode != 0) {
                    node_sigma(strat, off, na, h, sig);
                } else {
                    node_sigma_regret(regrets, off, na, h, sig);
                }
                out = 0.f;
                for (int a = 0; a < na; a++)
                    out += sig[a] *
                           val[(size_t)val_slot[children[cs + a]] * NC + h];
                if (mode == 0 && learning) {
                    float rp = reach[(size_t)reach_src[(size_t)nd * np + p] * NC + h];
                    for (int a = 0; a < na; a++) {
                        u32 ix = off + (u32)a * NC + h;
                        regrets[ix] += val[(size_t)val_slot[children[cs + a]] * NC + h] - out;
                        strat[ix] += rp * sig[a];
                    }
                }
            }
        } else {
            out = 0.f;
            for (int a = 0; a < na; a++)
                out += val[(size_t)val_slot[children[cs + a]] * NC + h];
        }
        val[(size_t)val_slot[nd] * NC + h] = out;
    }
}

extern "C" __global__ void pf_up(
    const u32* __restrict__ nodes, int start, int count, int p, int np, int mode,
    const int* __restrict__ actor_arr, const int* __restrict__ na_arr,
    const u32* __restrict__ off_arr, const u32* __restrict__ cstart_arr,
    const u32* __restrict__ children, const int* __restrict__ src_arr,
    const u32* __restrict__ foff_arr, const float* __restrict__ forced,
    const u32* __restrict__ reach_src,
    const float* __restrict__ reach,
    float* regrets, float* strat, const u32* __restrict__ val_slot, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    const int na = na_arr[nodes[start + blockIdx.x]];
    if (na == 2) pf_up_impl<2>(nodes, start, count, p, np, mode, actor_arr, na_arr, off_arr, cstart_arr, children, src_arr, foff_arr, forced, reach_src, reach, regrets, strat, val_slot, val);
    else if (na == 3) pf_up_impl<3>(nodes, start, count, p, np, mode, actor_arr, na_arr, off_arr, cstart_arr, children, src_arr, foff_arr, forced, reach_src, reach, regrets, strat, val_slot, val);
    else if (na == 4) pf_up_impl<4>(nodes, start, count, p, np, mode, actor_arr, na_arr, off_arr, cstart_arr, children, src_arr, foff_arr, forced, reach_src, reach, regrets, strat, val_slot, val);
    else pf_up_impl<0>(nodes, start, count, p, np, mode, actor_arr, na_arr, off_arr, cstart_arr, children, src_arr, foff_arr, forced, reach_src, reach, regrets, strat, val_slot, val);
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
