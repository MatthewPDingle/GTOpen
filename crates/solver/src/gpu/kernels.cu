// Level-synchronous vector CFR kernels.
//
// Conventions:
//  - reach0/reach1: per-node reach vectors, node n's slot is [n*nh_p, (n+1)*nh_p).
//    A node's actual reach lives at its reach_src owner's slot (see plan.rs).
//  - cfv: per-node counterfactual values for the current traverser p,
//    node n's slot is [n*nh_max, ...+nh_p).
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
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int actor = node_player[n];
    int na = node_na[n];
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
                reach_a[(u64)child * nh_a + i] = pr * sig[a * nh_a + i];
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
            reach_a[(u64)child * nh_a + i] = v;
        }
    }
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
        reach0[(u64)cn * nh0 + i] = (mask0[i] & cm) ? 0.f : pr0[i];
    for (int j = threadIdx.x; j < nh1; j += blockDim.x)
        reach1[(u64)cn * nh1 + j] = (mask1[j] & cm) ? 0.f : pr1[j];
}

// Up sweep, fold terminals: cfv[i] = amount * (compatible opponent reach).
extern "C" __global__ void up_fold(
    const u32* __restrict__ nodes, int start, int count, int p,
    const int* __restrict__ node_player,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const u32* __restrict__ rsrc0, const u32* __restrict__ rsrc1,
    const float* __restrict__ reach0, const float* __restrict__ reach1,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    const u32* __restrict__ oc1, const u32* __restrict__ oc2,
    const u32* __restrict__ same_p,
    float* cfv,
    int nh_p, int nh_o, int nh_max)
{
    __shared__ float s[52];
    __shared__ float T;
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    const float* ro = (p == 0 ? reach1 : reach0)
        + (u64)(p == 0 ? rsrc1[n] : rsrc0[n]) * nh_o;
    if (threadIdx.x < 52) s[threadIdx.x] = 0.f;
    if (threadIdx.x == 0) T = 0.f;
    __syncthreads();
    float t_local = 0.f;
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) {
        float r = ro[j];
        if (r != 0.f) {
            atomicAdd(&s[oc1[j]], r);
            atomicAdd(&s[oc2[j]], r);
            t_local += r;
        }
    }
    atomicAdd(&T, t_local);
    __syncthreads();
    float amount = node_player[n] == p ? node_tlose[n] : node_twin[n];
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        u32 sc = same_p[i];
        float same_r = sc != SENTINEL ? ro[sc] : 0.f;
        float valid = T - s[pc1[i]] - s[pc2[i]] + same_r;
        cfv[(u64)n * nh_max + i] = amount * valid;
    }
}

// Up sweep, showdown terminals: sorted-order sweep with card-removal
// corrections, one block per terminal. Shared memory holds the opponent's
// sorted strengths, reach values and an inclusive reach prefix.
extern "C" __global__ void up_show(
    const u32* __restrict__ nodes, int start, int count,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const float* __restrict__ node_ttie,
    const int* __restrict__ node_river_slot,
    const u32* __restrict__ rsrc_o,
    const float* __restrict__ reach_o_buf,
    const u32* __restrict__ p_off, const u32* __restrict__ p_cnt,
    const u32* __restrict__ p_idx, const u32* __restrict__ p_str,
    const u32* __restrict__ o_off, const u32* __restrict__ o_cnt,
    const u32* __restrict__ o_idx, const u32* __restrict__ o_str,
    const u32* __restrict__ o_card_off, const u32* __restrict__ o_card_pos,
    const u32* __restrict__ same_p,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    float* cfv,
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
    u32* str_sh = (u32*)(shraw + sizeof(float) * nh_o);
    float* reach_sh = (float*)(shraw + sizeof(float) * nh_o + sizeof(u32) * m_o);
    float* prefix =
        (float*)(shraw + sizeof(float) * nh_o + (sizeof(u32) + sizeof(float)) * m_o);
    const float* ro_g = reach_o_buf + (u64)rsrc_o[n] * nh_o;

    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];
    __syncthreads();
    const float* ro = ro_sh;
    for (int k = threadIdx.x; k < m_o; k += blockDim.x) {
        str_sh[k] = o_str[ob + k];
        reach_sh[k] = ro[o_idx[ob + k]];
    }
    // zero my full cfv span (hands missing from this river's sorted list stay 0)
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x)
        cfv[(u64)n * nh_max + i] = 0.f;
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
        u32 m = p_str[pb + k];
        // lb: first opp index with strength >= m; ub: first with strength > m
        int lo = 0, hi = m_o;
        while (lo < hi) { int mid = (lo + hi) >> 1; if (str_sh[mid] < m) lo = mid + 1; else hi = mid; }
        int lb = lo;
        hi = m_o;
        while (lo < hi) { int mid = (lo + hi) >> 1; if (str_sh[mid] <= m) lo = mid + 1; else hi = mid; }
        int ub = lo;
        float lower = lb > 0 ? prefix[lb - 1] : 0.f;
        float higher = total - (ub > 0 ? prefix[ub - 1] : 0.f);
        float tot_c = 0.f, lower_c = 0.f, higher_c = 0.f;
        u32 cc[2] = { pc1[i], pc2[i] };
        for (int x = 0; x < 2; x++) {
            u32 c0 = o_card_off[(u64)slot * 53 + cc[x]];
            u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];
            for (u32 t = c0; t < c1; t++) {
                u32 pos = o_card_pos[t];
                float r = reach_sh[pos];
                u32 s = str_sh[pos];
                tot_c += r;
                if (s < m) lower_c += r;
                else if (s > m) higher_c += r;
            }
        }
        u32 sc = same_p[i];
        float same_r = sc != SENTINEL ? ro[sc] : 0.f;
        float valid = total - tot_c + same_r;
        lower -= lower_c;
        higher -= higher_c;
        float tied = valid - lower - higher;
        cfv[(u64)n * nh_max + i] = win * lower + lose * higher + tie * tied;
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
    float* cfv, int nh_p, int nh_max)
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
            acc += cfv[(u64)cc_child[t] * nh_max + idx];
        }
        cfv[(u64)n * nh_max + i] = acc * inv;
    }
}

// Up sweep, action nodes: traverser nodes combine children with the current
// sigma and apply the DCFR/CFR+ update; opponent nodes sum children.
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
    float* cfv,
    const float* __restrict__ disc, // [pos, neg, strat] — device-resident so
                                    // captured graphs stay iteration-invariant
    int nh_p, int nh_max)
{
    float pos = disc[0], neg = disc[1], ds = disc[2];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int na = node_na[n];
    u32 cs = node_children_start[n];
    if (node_player[n] == p) {
        long long loff = lock_off[n];
        if (loff >= 0) {
            // locked: fixed sigma, no regret/strategy update
            const float* sig = lock_sigma + loff;
            for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
                float out = 0.f;
                for (int a = 0; a < na; a++)
                    out += sig[a * nh_p + i] * cfv[(u64)children[cs + a] * nh_max + i];
                cfv[(u64)n * nh_max + i] = out;
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
            float out = 0.f;
            for (int a = 0; a < na; a++) {
                float r = small ? rc[a] : regrets_p[doff + (u64)a * nh_p + i];
                float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni;
                float v = cfv[(u64)children[cs + a] * nh_max + i];
                if (small) vc[a] = v;
                out += sig * v;
            }
            float reach = rp[i];
            for (int a = 0; a < na; a++) {
                u64 idx = doff + (u64)a * nh_p + i;
                float val = small ? vc[a] : cfv[(u64)children[cs + a] * nh_max + i];
                float r = small ? rc[a] : regrets_p[idx];
                float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni;
                float d = r > 0.f ? pos : neg;
                regrets_p[idx] = r * d + (val - out);
                strat_p[idx] = strat_p[idx] * ds + reach * sig;
            }
            cfv[(u64)n * nh_max + i] = out;
        }
    } else {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float acc = 0.f;
            for (int a = 0; a < na; a++)
                acc += cfv[(u64)children[cs + a] * nh_max + i];
            cfv[(u64)n * nh_max + i] = acc;
        }
    }
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
    float* cfv,
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
                acc += cfv[(u64)children[cs + a] * nh_max + i];
            cfv[(u64)n * nh_max + i] = acc;
        }
        return;
    }
    long long loff = lock_off[n];
    if (loff >= 0) {
        // locked: fixed sigma in both modes (the best responder cannot
        // deviate at locked nodes)
        const float* sig = lock_sigma + loff;
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float out = 0.f;
            for (int a = 0; a < na; a++)
                out += sig[a * nh_p + i] * cfv[(u64)children[cs + a] * nh_max + i];
            cfv[(u64)n * nh_max + i] = out;
        }
        return;
    }
    if (mode == 0) {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float best = cfv[(u64)children[cs] * nh_max + i];
            for (int a = 1; a < na; a++) {
                float v = cfv[(u64)children[cs + a] * nh_max + i];
                if (v > best) best = v;
            }
            cfv[(u64)n * nh_max + i] = best;
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
                out += sig * cfv[(u64)children[cs + a] * nh_max + i];
            }
            cfv[(u64)n * nh_max + i] = out;
        }
    }
}
