// Level-synchronous vector CFR kernels.
//
// Conventions:
//  - reach0/reach1: densely packed reach vectors; rsrc[p][n] is the physical
//    slot of node n's nearest writing ancestor (see plan.rs).
//  - cfv: counterfactual values for the current traverser p, packed by
//    cfv_slot[n]; only visited nodes have physical storage.
//  - Regret matching mirrors the CPU: sigma = max(r,0)/sum, uniform if sum<=1e-12.

typedef unsigned int u32;
typedef unsigned long long u64;

#define SENTINEL 0xFFFFFFFFu

// Initialize the root node's reach with the range weights.
extern "C" __global__ void copy_root(
    const float* __restrict__ w0, const float* __restrict__ w1,
    float* reach0, float* reach1, int nh0, int nh1)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = gridDim.x * blockDim.x;
    for (int k = i; k < nh0; k += stride) reach0[k] = w0[k];
    for (int k = i; k < nh1; k += stride) reach1[k] = w1[k];
}

// Down sweep, action nodes at one level: write each child's actor-side reach
// (parent reach x current sigma). The non-actor side is not copied; children
// read it via reach_src.
template<int NA>
__device__ __forceinline__ void down_action_impl(
    const u32* __restrict__ nodes, int start, int count,
    const int* __restrict__ node_player,
    const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    const u32* __restrict__ rsrc0, const u32* __restrict__ rsrc1,
    const float* __restrict__ regrets0, const float* __restrict__ regrets1,
    const long long* __restrict__ lock_off,
    const float* __restrict__ lock_sigma,
    float* reach0, float* reach1,
    int nh0, int nh1)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int actor = node_player[n];
    const int na = NA == 0 ? node_na[n] : NA;
    u64 doff = node_data_off[n];
    u32 cs = node_children_start[n];
    const float* regs = actor == 0 ? regrets0 : regrets1;
    float* reach_a = actor == 0 ? reach0 : reach1;
    int nh_a = actor == 0 ? nh0 : nh1;
    u32 src = actor == 0 ? rsrc0[n] : rsrc1[n];
    const float* parent_reach = reach_a + (u64)src * nh_a;

    long long loff = lock_off[n];
    if (loff >= 0) {
        // locked node: play the fixed sigma
        const float* sig = lock_sigma + loff;
        for (int i = threadIdx.x; i < nh_a; i += blockDim.x) {
            float pr = parent_reach[i];
            for (int a = 0; a < na; a++) {
                u32 child = children[cs + a];
                reach_a[(u64)(actor == 0 ? rsrc0[child] : rsrc1[child]) * nh_a + i] = pr * sig[a * nh_a + i];
            }
        }
        return;
    }

    float rc[8];
    bool small = na <= 8;
    for (int i = threadIdx.x; i < nh_a; i += blockDim.x) {
        float sum = 0.f;
        for (int a = 0; a < na; a++) {
            float r = regs[doff + (u64)a * nh_a + i];
            if (small) rc[a] = r;
            sum += r > 0.f ? r : 0.f;
        }
        float pr = parent_reach[i];
        float uni = pr / (float)na;
        for (int a = 0; a < na; a++) {
            u32 child = children[cs + a];
            float r = small ? rc[a] : regs[doff + (u64)a * nh_a + i];
            float v;
            if (sum > 1e-12f) {
                v = pr * ((r > 0.f ? r : 0.f) / sum);
            } else {
                v = uni;
            }
            reach_a[(u64)(actor == 0 ? rsrc0[child] : rsrc1[child]) * nh_a + i] = v;
        }
    }
}

extern "C" __global__ void down_action(
    const u32* __restrict__ nodes, int start, int count,
    const int* __restrict__ node_player,
    const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    const u32* __restrict__ rsrc0, const u32* __restrict__ rsrc1,
    const float* __restrict__ regrets0, const float* __restrict__ regrets1,
    const long long* __restrict__ lock_off,
    const float* __restrict__ lock_sigma,
    float* reach0, float* reach1,
    int nh0, int nh1)
{
    if (blockIdx.x >= (u32)count) return;
    const int na = node_na[nodes[start + blockIdx.x]];
    if (na == 2) down_action_impl<2>(nodes, start, count, node_player, node_na, node_data_off, node_children_start, children, rsrc0, rsrc1, regrets0, regrets1, lock_off, lock_sigma, reach0, reach1, nh0, nh1);
    else if (na == 3) down_action_impl<3>(nodes, start, count, node_player, node_na, node_data_off, node_children_start, children, rsrc0, rsrc1, regrets0, regrets1, lock_off, lock_sigma, reach0, reach1, nh0, nh1);
    else if (na == 4) down_action_impl<4>(nodes, start, count, node_player, node_na, node_data_off, node_children_start, children, rsrc0, rsrc1, regrets0, regrets1, lock_off, lock_sigma, reach0, reach1, nh0, nh1);
    else down_action_impl<0>(nodes, start, count, node_player, node_na, node_data_off, node_children_start, children, rsrc0, rsrc1, regrets0, regrets1, lock_off, lock_sigma, reach0, reach1, nh0, nh1);
}

// Down sweep, chance edges at one level: child reach = parent reach with
// hands containing the dealt card zeroed (both players).
extern "C" __global__ void down_chance(
    const u32* __restrict__ parents, const u32* __restrict__ childs,
    const u32* __restrict__ cards, int start, int count,
    const u32* __restrict__ rsrc0, const u32* __restrict__ rsrc1,
    const u64* __restrict__ mask0, const u64* __restrict__ mask1,
    float* reach0, float* reach1, int nh0, int nh1)
{
    int e = blockIdx.x;
    if (e >= count) return;
    u32 pn = parents[start + e], cn = childs[start + e];
    u64 cm = 1ull << cards[start + e];
    const float* pr0 = reach0 + (u64)rsrc0[pn] * nh0;
    const float* pr1 = reach1 + (u64)rsrc1[pn] * nh1;
    for (int i = threadIdx.x; i < nh0; i += blockDim.x)
        reach0[(u64)rsrc0[cn] * nh0 + i] = (mask0[i] & cm) ? 0.f : pr0[i];
    for (int j = threadIdx.x; j < nh1; j += blockDim.x)
        reach1[(u64)rsrc1[cn] * nh1 + j] = (mask1[j] & cm) ? 0.f : pr1[j];
}

// Up sweep, fold terminals: cfv[i] = amount * (compatible opponent reach).
extern "C" __global__ void up_fold(
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

// Up sweep, showdown terminals: sorted-order sweep with card-removal
// corrections, one block per terminal. Strength boundaries are precomputed
// per river; shared memory holds reach values and an inclusive reach prefix.
extern "C" __global__ void up_show(
    const u32* __restrict__ nodes, int start, int count,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const float* __restrict__ node_ttie,
    const int* __restrict__ node_river_slot,
    const u32* __restrict__ rsrc_o,
    const float* __restrict__ reach_o_buf,
    const u32* __restrict__ p_off, const u32* __restrict__ p_cnt,
    const u32* __restrict__ p_idx,
    const u32* __restrict__ p_lower, const u32* __restrict__ p_upper,
    const u32* __restrict__ o_off, const u32* __restrict__ o_cnt,
    const u32* __restrict__ o_idx,
    const u32* __restrict__ o_card_off, const u32* __restrict__ o_card_pos,
    const u32* __restrict__ same_p,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    const u32* __restrict__ cfv_slot, float* cfv,
    int nh_p, int nh_o, int nh_max)
{
    extern __shared__ char shraw[];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int slot = node_river_slot[n];
    int m_o = o_cnt[slot];
    u32 ob = o_off[slot];
    float* ro_sh = (float*)shraw; // nh_o entries, original hand order
    float* reach_sh = (float*)(shraw + sizeof(float) * nh_o);
    float* prefix = (float*)(shraw + sizeof(float) * (nh_o + m_o));
    u32* card_pos_sh = (u32*)(prefix + m_o); // 2*m_o immutable position indices
    u32 card_base = o_card_off[(u64)slot * 53];
    const float* ro_g = reach_o_buf + (u64)rsrc_o[n] * nh_o;

    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];
    for (int j = threadIdx.x; j < 2 * m_o; j += blockDim.x)
        card_pos_sh[j] = o_card_pos[card_base + j];
    __syncthreads();
    const float* ro = ro_sh;
    for (int k = threadIdx.x; k < m_o; k += blockDim.x) {
        reach_sh[k] = ro[o_idx[ob + k]];
    }
    // zero my full cfv span (hands missing from this river's sorted list stay 0)
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x)
        cfv[(u64)cfv_slot[n] * nh_max + i] = 0.f;
    __syncthreads();
    // Blocked inclusive scan: per-thread chunk scan, thread-0 scans chunk
    // totals, then chunk offsets are added back.
    __shared__ float chunk_sum[257];
    {
        int chunk = (m_o + blockDim.x - 1) / blockDim.x;
        int lo_k = threadIdx.x * chunk;
        int hi_k = min(lo_k + chunk, m_o);
        float acc = 0.f;
        for (int k = lo_k; k < hi_k; k++) {
            acc += reach_sh[k];
            prefix[k] = acc;
        }
        chunk_sum[threadIdx.x + 1] = acc;
        __syncthreads();
        if (threadIdx.x == 0) {
            chunk_sum[0] = 0.f;
            for (int t = 1; t <= (int)blockDim.x; t++) chunk_sum[t] += chunk_sum[t - 1];
        }
        __syncthreads();
        float base = chunk_sum[threadIdx.x];
        for (int k = lo_k; k < hi_k; k++) prefix[k] += base;
    }
    __syncthreads();
    float total = m_o > 0 ? prefix[m_o - 1] : 0.f;
    float win = node_twin[n], lose = node_tlose[n], tie = node_ttie[n];

    int m_p = p_cnt[slot];
    u32 pb = p_off[slot];
    for (int k = threadIdx.x; k < m_p; k += blockDim.x) {
        u32 i = p_idx[pb + k];
        u32 lb = p_lower[pb + k], ub = p_upper[pb + k];
        float lower = lb > 0 ? prefix[lb - 1] : 0.f;
        float higher = total - (ub > 0 ? prefix[ub - 1] : 0.f);
        float tot_c = 0.f, lower_c = 0.f, higher_c = 0.f;
        u32 cc[2] = { pc1[i], pc2[i] };
        for (int x = 0; x < 2; x++) {
            u32 c0 = o_card_off[(u64)slot * 53 + cc[x]];
            u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];
            for (u32 t = c0; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                float r = reach_sh[pos];
                tot_c += r;
                if (pos < lb) lower_c += r;
                else if (pos >= ub) higher_c += r;
            }
        }
        u32 sc = same_p[i];
        float same_r = sc != SENTINEL ? ro[sc] : 0.f;
        float valid = total - tot_c + same_r;
        lower -= lower_c;
        higher -= higher_c;
        float tied = valid - lower - higher;
        cfv[(u64)cfv_slot[n] * nh_max + i] = win * lower + lose * higher + tie * tied;
    }
}

// Up sweep, chance nodes: cfv = (1/divisor) * sum over valid cards of the
// orbit-representative child's cfv, gathered through the suit-permutation
// hand table (identity for the representative itself), skipping hands that
// contain the dealt card. Mirrors the CPU chance_node merge exactly.
extern "C" __global__ void up_chance(
    const u32* __restrict__ nodes, int start, int count,
    const u32* __restrict__ cc_start, const u32* __restrict__ cc_count,
    const u32* __restrict__ cc_card, const u32* __restrict__ cc_child,
    const u32* __restrict__ cc_perm,
    const float* __restrict__ node_cdiv,
    const u64* __restrict__ mask_p,
    const u32* __restrict__ hand_perm_p, // perm k at [k*nh_p, (k+1)*nh_p)
    const u32* __restrict__ cfv_slot, float* cfv, int nh_p, int nh_max)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    u32 t0 = cc_start[n];
    u32 t1 = t0 + cc_count[n];
    float inv = node_cdiv[n];
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        u64 hm = mask_p[i];
        float acc = 0.f;
        for (u32 t = t0; t < t1; t++) {
            u64 cm = 1ull << cc_card[t];
            if (hm & cm) continue;
            u32 k = cc_perm[t];
            int idx = k == 0 ? i : (int)hand_perm_p[(u64)k * nh_p + i];
            acc += cfv[(u64)cfv_slot[cc_child[t]] * nh_max + idx];
        }
        cfv[(u64)cfv_slot[n] * nh_max + i] = acc * inv;
    }
}

// Up sweep, action nodes: traverser nodes combine children with the current
// sigma and apply the DCFR/CFR+ update; opponent nodes sum children.
template<int NA>
__device__ __forceinline__ void up_action_impl(
    const u32* __restrict__ nodes, int start, int count, int p,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    float* regrets_p, float* strat_p,
    const u32* __restrict__ rsrc_p,
    const float* __restrict__ reach_p_buf,
    const long long* __restrict__ lock_off,
    const float* __restrict__ lock_sigma,
    const u32* __restrict__ cfv_slot, float* cfv,
    const float* __restrict__ disc, // [pos, neg, strat] — device-resident so
                                    // captured graphs stay iteration-invariant
    int nh_p, int nh_max)
{
    float pos = disc[0], neg = disc[1], ds = disc[2];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    const int na = NA == 0 ? node_na[n] : NA;
    u32 cs = node_children_start[n];
    if (node_player[n] == p) {
        long long loff = lock_off[n];
        if (loff >= 0) {
            // locked: fixed sigma, no regret/strategy update
            const float* sig = lock_sigma + loff;
            for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
                float out = 0.f;
                for (int a = 0; a < na; a++)
                    out += sig[a * nh_p + i] * cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
                cfv[(u64)cfv_slot[n] * nh_max + i] = out;
            }
            return;
        }
        u64 doff = node_data_off[n];
        const float* rp = reach_p_buf + (u64)rsrc_p[n] * nh_p;
        // register-cache regrets and child values for the common small-na case
        float rc[8], vc[8];
        bool small = na <= 8;
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float sum = 0.f;
            for (int a = 0; a < na; a++) {
                float r = regrets_p[doff + (u64)a * nh_p + i];
                if (small) rc[a] = r;
                sum += r > 0.f ? r : 0.f;
            }
            float uni = 1.f / (float)na;
            float reach = rp[i];
            float out = 0.f;
            for (int a = 0; a < na; a++) {
                float r = small ? rc[a] : regrets_p[doff + (u64)a * nh_p + i];
                float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni;
                float v = cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
                if (small) vc[a] = v;
                out += sig * v;
                // Independent of the completed node value: use this action's
                // original sigma while it is already available.
                u64 idx = doff + (u64)a * nh_p + i;
                strat_p[idx] = strat_p[idx] * ds + reach * sig;
            }
            for (int a = 0; a < na; a++) {
                u64 idx = doff + (u64)a * nh_p + i;
                float val = small ? vc[a] : cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
                float r = small ? rc[a] : regrets_p[idx];
                float d = r > 0.f ? pos : neg;
                regrets_p[idx] = r * d + (val - out);
            }
            cfv[(u64)cfv_slot[n] * nh_max + i] = out;
        }
    } else {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float acc = 0.f;
            for (int a = 0; a < na; a++)
                acc += cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
            cfv[(u64)cfv_slot[n] * nh_max + i] = acc;
        }
    }
}

extern "C" __global__ void up_action(
    const u32* __restrict__ nodes, int start, int count, int p,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    float* regrets_p, float* strat_p,
    const u32* __restrict__ rsrc_p,
    const float* __restrict__ reach_p_buf,
    const long long* __restrict__ lock_off,
    const float* __restrict__ lock_sigma,
    const u32* __restrict__ cfv_slot, float* cfv,
    const float* __restrict__ disc, // [pos, neg, strat] — device-resident so
                                    // captured graphs stay iteration-invariant
    int nh_p, int nh_max)
{
    if (blockIdx.x >= (u32)count) return;
    const int na = node_na[nodes[start + blockIdx.x]];
    // Compile-time common action counts keep working arrays in registers.
    // The generic implementation retains arbitrary action-menu support.
    if (na == 2) up_action_impl<2>(nodes, start, count, p, node_player, node_na, node_data_off, node_children_start, children, regrets_p, strat_p, rsrc_p, reach_p_buf, lock_off, lock_sigma, cfv_slot, cfv, disc, nh_p, nh_max);
    else if (na == 3) up_action_impl<3>(nodes, start, count, p, node_player, node_na, node_data_off, node_children_start, children, regrets_p, strat_p, rsrc_p, reach_p_buf, lock_off, lock_sigma, cfv_slot, cfv, disc, nh_p, nh_max);
    else if (na == 4) up_action_impl<4>(nodes, start, count, p, node_player, node_na, node_data_off, node_children_start, children, regrets_p, strat_p, rsrc_p, reach_p_buf, lock_off, lock_sigma, cfv_slot, cfv, disc, nh_p, nh_max);
    else up_action_impl<0>(nodes, start, count, p, node_player, node_na, node_data_off, node_children_start, children, regrets_p, strat_p, rsrc_p, reach_p_buf, lock_off, lock_sigma, cfv_slot, cfv, disc, nh_p, nh_max);
}

// Copy the first n floats (used to extract the root cfv span).
extern "C" __global__ void copy_span(const float* __restrict__ src, float* dst, int n)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = gridDim.x * blockDim.x;
    for (int k = i; k < n; k += stride) dst[k] = src[k];
}

// Evaluation up sweep for action nodes (no updates). mode 0: traverser plays
// a best response (max over children; locked nodes are constraints). mode 1:
// traverser plays the average strategy (normalized cumulative strategy).
// Opponent nodes sum children (their average sigma was folded into reach on
// the way down).
extern "C" __global__ void up_action_eval(
    const u32* __restrict__ nodes, int start, int count, int p, int mode,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    const float* __restrict__ strat_p,
    const long long* __restrict__ lock_off,
    const float* __restrict__ lock_sigma,
    const u32* __restrict__ cfv_slot, float* cfv,
    int nh_p, int nh_max)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int na = node_na[n];
    u32 cs = node_children_start[n];
    if (node_player[n] != p) {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float acc = 0.f;
            for (int a = 0; a < na; a++)
                acc += cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
            cfv[(u64)cfv_slot[n] * nh_max + i] = acc;
        }
        return;
    }
    long long loff = lock_off[n];
    // A running least-exploitable fit (loff == -2) is the lock it will
    // become: its average strategy, fixed for the best responder too.
    if (loff == -2) mode = 1;
    if (loff >= 0) {
        // locked: fixed sigma in both modes (the best responder cannot
        // deviate at locked nodes)
        const float* sig = lock_sigma + loff;
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float out = 0.f;
            for (int a = 0; a < na; a++)
                out += sig[a * nh_p + i] * cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
            cfv[(u64)cfv_slot[n] * nh_max + i] = out;
        }
        return;
    }
    if (mode == 0) {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float best = cfv[(u64)cfv_slot[children[cs]] * nh_max + i];
            for (int a = 1; a < na; a++) {
                float v = cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
                if (v > best) best = v;
            }
            cfv[(u64)cfv_slot[n] * nh_max + i] = best;
        }
    } else {
        u64 doff = node_data_off[n];
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float sum = 0.f;
            for (int a = 0; a < na; a++) {
                float s = strat_p[doff + (u64)a * nh_p + i];
                sum += s > 0.f ? s : 0.f;
            }
            float uni = 1.f / (float)na;
            float out = 0.f;
            for (int a = 0; a < na; a++) {
                float s = strat_p[doff + (u64)a * nh_p + i];
                float sig = sum > 1e-12f ? (s > 0.f ? s : 0.f) / sum : uni;
                out += sig * cfv[(u64)cfv_slot[children[cs + a]] * nh_max + i];
            }
            cfv[(u64)cfv_slot[n] * nh_max + i] = out;
        }
    }
}

// ---------------------------------------------------------------------------
// Least-exploitable fits (see fit.rs). Each fit owns FIT_STRIDE floats:
//   [0,8) target | [8,16) bounty | [16,24) push | [24,32) frequency sums |
//   32 reach sum | [33,41) last frequency | 41 pot | 42 steps | 43 opponent range mass
// Bounty and push are per unit of the opponent's whole range at the node
// (FitConstraint::mass); the value added to every hand's action-a
// counterfactual value is (bounty[a] + push[a]) * mass. Mirrors
// FitConstraint on the CPU.
// ---------------------------------------------------------------------------
#define FIT_STRIDE 48
#define FIT_NA 8
#define FIT_STEP_POT 0.05f
#define FIT_PUSH_POT 1.0f
#define FIT_BOUNTY_CAP_POT 4.0f

// One block per fit owned by traverser p at this level, launched right
// before up_action there: records the current-iterate frequency and biases
// the child values up_action is about to combine.
extern "C" __global__ void fit_apply(
    const u32* __restrict__ fit_order, int start, int count,
    const u32* __restrict__ fit_node, float* fit,
    const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const u32* __restrict__ node_children_start,
    const u32* __restrict__ children,
    const float* __restrict__ regrets_p,
    const u32* __restrict__ rsrc_p, const float* __restrict__ reach_p_buf,
    const u32* __restrict__ cfv_slot, float* cfv,
    int nh_p, int nh_max)
{
    __shared__ float red[FIT_NA + 1][128];
    __shared__ float bias[FIT_NA];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 k = fit_order[start + b];
    u32 n = fit_node[k];
    float* F = fit + (u64)k * FIT_STRIDE;
    int na = node_na[n];
    if (na > FIT_NA) return;
    u64 doff = node_data_off[n];
    u32 cs = node_children_start[n];
    const float* rp = reach_p_buf + (u64)rsrc_p[n] * nh_p;
    int t = threadIdx.x;

    float acc[FIT_NA];
    for (int a = 0; a < FIT_NA; a++) acc[a] = 0.f;
    float rsum = 0.f;
    for (int i = t; i < nh_p; i += blockDim.x) {
        float sum = 0.f;
        for (int a = 0; a < na; a++) {
            float r = regrets_p[doff + (u64)a * nh_p + i];
            sum += r > 0.f ? r : 0.f;
        }
        float r_i = rp[i];
        rsum += r_i;
        for (int a = 0; a < na; a++) {
            float r = regrets_p[doff + (u64)a * nh_p + i];
            float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : 1.f / (float)na;
            acc[a] += r_i * sig;
        }
    }
    for (int a = 0; a < FIT_NA; a++) red[a][t] = acc[a];
    red[FIT_NA][t] = rsum;
    __syncthreads();
    for (int step = blockDim.x >> 1; step > 0; step >>= 1) {
        if (t < step)
            for (int q = 0; q < FIT_NA + 1; q++) red[q][t] += red[q][t + step];
        __syncthreads();
    }
    if (t == 0) {
        for (int a = 0; a < na; a++) F[24 + a] += red[a][0];
        F[32] += red[FIT_NA][0];
    }
    // bounty in chips per unit of the opponent's whole range at the node
    if (t < na) bias[t] = (F[8 + t] + F[16 + t]) * F[43];
    __syncthreads();
    for (int a = 0; a < na; a++) {
        float add = bias[a];
        if (add == 0.f) continue;
        float* v = cfv + (u64)cfv_slot[children[cs + a]] * nh_max;
        for (int i = t; i < nh_p; i += blockDim.x) v[i] += add;
    }
}

// After both sweeps of an iteration: one damped dual-ascent step per fit
// (FitConstraint::step_from), then clear the frequency sums.
extern "C" __global__ void fit_dual(
    float* fit, const u32* __restrict__ fit_node, const int* __restrict__ node_na, int count)
{
    int k = blockIdx.x * blockDim.x + threadIdx.x;
    if (k >= count) return;
    float* F = fit + (u64)k * FIT_STRIDE;
    int na = node_na[fit_node[k]];
    if (na > FIT_NA) return;
    float reach = F[32];
    if (reach > 1e-12f) {
        float pot = F[41];
        float cb = 0.f, cp = 0.f;
        for (int a = 0; a < na; a++) {
            float f = F[24 + a] / reach;
            float err = F[a] - f;
            F[33 + a] = f;
            F[8 + a] += FIT_STEP_POT * pot * err;
            F[16 + a] = FIT_PUSH_POT * pot * err;
            cb += F[8 + a] * F[a];
            cp += F[16 + a] * F[a];
        }
        float cap = FIT_BOUNTY_CAP_POT * fmaxf(pot, 1e-9f);
        for (int a = 0; a < na; a++) {
            F[8 + a] = fminf(fmaxf(F[8 + a] - cb, -cap), cap);
            F[16 + a] -= cp;
        }
        F[42] += 1.f;
    }
    for (int a = 0; a < FIT_NA; a++) F[24 + a] = 0.f;
    F[32] = 0.f;
}

// ---------------------------------------------------------------------------
// "Trust the read" (rnr.rs). The read villain's reach is a second down sweep
// into its own buffer (same slot layout as the villain's reach); before the
// hero's up sweep the villain's (free) reach becomes the reach the hero faces:
//   free = trust * read + (1 - trust) * free.
// Terminal values are linear in the opponent reach, so this is exact.
// ---------------------------------------------------------------------------
extern "C" __global__ void rnr_mix(
    float* free_reach, const float* __restrict__ read, float trust, long long n)
{
    float rest = 1.f - trust;
    long long i = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    long long stride = (long long)gridDim.x * blockDim.x;
    for (long long k = i; k < n; k += stride)
        free_reach[k] = trust * read[k] + rest * free_reach[k];
}

// A new trust level restarts the average strategy (Solver::restart_averages)
// except at locked nodes (lock_off >= 0): nothing learns there, and they keep
// the pre-lock average a re-applied profile rakes from.
extern "C" __global__ void restart_strat(
    const u32* __restrict__ nodes, int count, int p,
    const int* __restrict__ node_player,
    const int* __restrict__ node_na,
    const u64* __restrict__ node_data_off,
    const long long* __restrict__ lock_off,
    float* strat, int nh)
{
    for (int k = blockIdx.x; k < count; k += gridDim.x) {
        const u32 n = nodes[k];
        if (node_player[n] != p || lock_off[n] >= 0) continue;
        const u64 off = node_data_off[n];
        if (off == ~0ull) continue;
        const long long len = (long long)node_na[n] * nh;
        for (long long i = threadIdx.x; i < len; i += blockDim.x) strat[off + i] = 0.f;
    }
}

