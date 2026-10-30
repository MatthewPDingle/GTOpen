// Level-synchronous three-player CFR kernels.
//
// Conventions:
//  - reachK (K = 0, 1, 2): one f32 vector of nhK entries per reach slot;
//    rsK[n] is the slot holding player K's reach at node n.
//  - cfv: counterfactual values of the current traverser p, nh_max floats
//    per slot; cs[n] is node n's slot (levels alternate between two halves,
//    so a level's values live until its parent level has read them).
//  - Arenas are f32, action-major per node: regrets[off + a * nh + i].
//  - Terminal values follow multiway/eval.rs exactly: cfv(h) is a sum of
//    C[X][Y] * M(X, Y)(h) over the cumulative sets L / Q / A of the two
//    opponents, with M computed by inclusion-exclusion over shared cards.

typedef unsigned int u32;
typedef unsigned long long u64;
#define SENT 0xffffffffu

__device__ __forceinline__ float* pick(float* x0, float* x1, float* x2, int k) {
    return k == 0 ? x0 : (k == 1 ? x1 : x2);
}
__device__ __forceinline__ const float* pickc(const float* x0, const float* x1, const float* x2, int k) {
    return k == 0 ? x0 : (k == 1 ? x1 : x2);
}
__device__ __forceinline__ const u32* picku(const u32* x0, const u32* x1, const u32* x2, int k) {
    return k == 0 ? x0 : (k == 1 ? x1 : x2);
}

// Root reach = range weights.
extern "C" __global__ void mw_copy_root(
    const float* __restrict__ w0, const float* __restrict__ w1, const float* __restrict__ w2,
    float* r0, float* r1, float* r2, int nh0, int nh1, int nh2)
{
    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < nh0 + nh1 + nh2; i += gridDim.x * blockDim.x) {
        if (i < nh0) r0[i] = w0[i];
        else if (i < nh0 + nh1) r1[i - nh0] = w1[i - nh0];
        else r2[i - nh0 - nh1] = w2[i - nh0 - nh1];
    }
}

// Strategy of hand i at an action node. mode 0: current (regret matching,
// PCFR+ adds the prediction); mode 1: average (normalized strategy sums).
__device__ __forceinline__ float sigma_sum(
    const float* reg, const float* prd, const float* str, int mode, u64 off, int na, int nh, int i)
{
    float s = 0.f;
    for (int a = 0; a < na; a++) {
        u64 k = off + (u64)a * nh + i;
        float v = mode == 0 ? (prd ? fmaxf(fmaxf(reg[k], 0.f) + prd[k], 0.f) : fmaxf(reg[k], 0.f)) : str[k];
        s += v;
    }
    return s;
}
__device__ __forceinline__ float sigma_at(
    const float* reg, const float* prd, const float* str, int mode, u64 off, int na, int nh, int i, int a, float sum)
{
    if (!(sum > (mode == 0 ? 1e-12f : 0.f))) return 1.f / na;
    u64 k = off + (u64)a * nh + i;
    float v = mode == 0 ? (prd ? fmaxf(fmaxf(reg[k], 0.f) + prd[k], 0.f) : fmaxf(reg[k], 0.f)) : str[k];
    return v / sum;
}

// Down sweep, action nodes: child reach of the actor = reach x sigma.
// only >= 0 restricts the sweep to that player's nodes (its reach is the
// only one that changed since the last sweep).
extern "C" __global__ void mw_down_action(
    const u32* __restrict__ nodes, int start, int count, int mode, int only,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_off, const u32* __restrict__ node_cs,
    const u32* __restrict__ children,
    const u32* __restrict__ rs0, const u32* __restrict__ rs1, const u32* __restrict__ rs2,
    const float* reg0, const float* reg1, const float* reg2,
    const float* prd0, const float* prd1, const float* prd2,
    const float* str0, const float* str1, const float* str2,
    const float* __restrict__ lock_sigma, const long long* __restrict__ lock_off,
    float* reach0, float* reach1, float* reach2,
    int nh0, int nh1, int nh2)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int k = node_player[n];
    if (only >= 0 && k != only) return;
    int na = node_na[n];
    int nh = k == 0 ? nh0 : (k == 1 ? nh1 : nh2);
    const u32* rs = picku(rs0, rs1, rs2, k);
    float* reach = pick(reach0, reach1, reach2, k);
    const float* reg = pickc(reg0, reg1, reg2, k);
    const float* prd = pickc(prd0, prd1, prd2, k);
    const float* str = pickc(str0, str1, str2, k);
    u64 off = node_off[n];
    long long lo = lock_off[n];
    const float* src = reach + (u64)rs[n] * nh;
    for (int i = threadIdx.x; i < nh; i += blockDim.x) {
        float r = src[i];
        float sum = lo >= 0 ? 0.f : sigma_sum(reg, prd, str, mode, off, na, nh, i);
        for (int a = 0; a < na; a++) {
            float sg = lo >= 0 ? lock_sigma[lo + (long long)a * nh + i]
                               : sigma_at(reg, prd, str, mode, off, na, nh, i, a, sum);
            u32 c = children[node_cs[n] + a];
            reach[(u64)rs[c] * nh + i] = r * sg;
        }
    }
}

// Down sweep, chance edges: child reach = parent reach without hands that
// hold the dealt card, for all three players (or only player `only`).
extern "C" __global__ void mw_down_chance(
    const u32* __restrict__ par, const u32* __restrict__ chi, const u32* __restrict__ card,
    int start, int count, int only,
    const u32* __restrict__ rs0, const u32* __restrict__ rs1, const u32* __restrict__ rs2,
    const u64* __restrict__ m0, const u64* __restrict__ m1, const u64* __restrict__ m2,
    float* reach0, float* reach1, float* reach2, int nh0, int nh1, int nh2)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 p = par[start + b], c = chi[start + b];
    u64 cm = 1ull << card[start + b];
    int lo = only < 0 ? 0 : (only == 0 ? 0 : (only == 1 ? nh0 : nh0 + nh1));
    int hi = only < 0 ? nh0 + nh1 + nh2 : (only == 0 ? nh0 : (only == 1 ? nh0 + nh1 : nh0 + nh1 + nh2));
    for (int t = lo + threadIdx.x; t < hi; t += blockDim.x) {
        if (t < nh0) {
            reach0[(u64)rs0[c] * nh0 + t] = (m0[t] & cm) ? 0.f : reach0[(u64)rs0[p] * nh0 + t];
        } else if (t < nh0 + nh1) {
            int i = t - nh0;
            reach1[(u64)rs1[c] * nh1 + i] = (m1[i] & cm) ? 0.f : reach1[(u64)rs1[p] * nh1 + i];
        } else {
            int i = t - nh0 - nh1;
            reach2[(u64)rs2[c] * nh2 + i] = (m2[i] & cm) ? 0.f : reach2[(u64)rs2[p] * nh2 + i];
        }
    }
}

// Block-wide inclusive scan of a[0..n) in shared memory (blockDim <= 256).
__device__ void block_scan(float* a, int n, float* chunk_sum) {
    int chunk = (n + blockDim.x - 1) / blockDim.x;
    int lo = threadIdx.x * chunk;
    int hi = min(lo + chunk, n);
    float acc = 0.f;
    for (int k = lo; k < hi; k++) { acc += a[k]; a[k] = acc; }
    chunk_sum[threadIdx.x + 1] = acc;
    __syncthreads();
    if (threadIdx.x == 0) {
        chunk_sum[0] = 0.f;
        for (int t = 1; t <= (int)blockDim.x; t++) chunk_sum[t] += chunk_sum[t - 1];
    }
    __syncthreads();
    float base = chunk_sum[threadIdx.x];
    for (int k = lo; k < hi; k++) a[k] += base;
    __syncthreads();
}

__device__ float block_sum(float v, float* scratch) {
    scratch[threadIdx.x] = v;
    __syncthreads();
    for (int s = blockDim.x >> 1; s > 0; s >>= 1) {
        if (threadIdx.x < (u32)s) scratch[threadIdx.x] += scratch[threadIdx.x + s];
        __syncthreads();
    }
    float r = scratch[0];
    __syncthreads();
    return r;
}

// Strength-independent terminals: cfv(h) = C_AA * M(A, A)(h).
// Shared: Pq[2704], Pr[2704], Sq[52], Sr[52].
extern "C" __global__ void mw_up_fold(
    const u32* __restrict__ nodes, int start, int count, int p, int q, int r,
    const int* __restrict__ node_class, const float* __restrict__ coef,
    const u32* __restrict__ rsq, const u32* __restrict__ rsr,
    const float* __restrict__ reach_q_buf, const float* __restrict__ reach_r_buf,
    const u32* __restrict__ c1p, const u32* __restrict__ c2p,
    const u32* __restrict__ c1q, const u32* __restrict__ c2q,
    const u32* __restrict__ c1r, const u32* __restrict__ c2r,
    const u32* __restrict__ same_qr,
    const u32* __restrict__ cs, float* cfv, int nh_p, int nh_q, int nh_r, int nh_max)
{
    extern __shared__ float sh[];
    float* Pq = sh;
    float* Pr = sh + 2704;
    __shared__ float Sq[52], Sr[52];
    __shared__ float red[256];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    float amount = coef[((u64)node_class[n] * 3 + p) * 9 + 8];
    const float* rq = reach_q_buf + (u64)rsq[n] * nh_q;
    const float* rr = reach_r_buf + (u64)rsr[n] * nh_r;
    float* out = cfv + (u64)cs[n] * nh_max;
    for (int k = threadIdx.x; k < 2 * 2704; k += blockDim.x) sh[k] = 0.f;
    if (threadIdx.x < 52) { Sq[threadIdx.x] = 0.f; Sr[threadIdx.x] = 0.f; }
    __syncthreads();
    float tq = 0.f, tr = 0.f, kk = 0.f;
    for (int j = threadIdx.x; j < nh_q; j += blockDim.x) {
        float w = rq[j];
        if (w != 0.f) {
            u32 a = c1q[j], c = c2q[j];
            Pq[a * 52 + c] = w; Pq[c * 52 + a] = w;
            atomicAdd(&Sq[a], w); atomicAdd(&Sq[c], w);
            tq += w;
            u32 s = same_qr[j];
            if (s != SENT) kk += w * rr[s];
        }
    }
    for (int j = threadIdx.x; j < nh_r; j += blockDim.x) {
        float w = rr[j];
        if (w != 0.f) {
            u32 a = c1r[j], c = c2r[j];
            Pr[a * 52 + c] = w; Pr[c * 52 + a] = w;
            atomicAdd(&Sr[a], w); atomicAdd(&Sr[c], w);
            tr += w;
        }
    }
    tq = block_sum(tq, red);
    tr = block_sum(tr, red);
    kk = block_sum(kk, red);
    if (tq == 0.f || tr == 0.f || amount == 0.f) {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) out[i] = 0.f;
        return;
    }
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        u32 a = c1p[i], bb = c2p[i];
        const float* qa = Pq + a * 52; const float* qb = Pq + bb * 52;
        const float* ra = Pr + a * 52; const float* rb = Pr + bb * 52;
        float txq = tq - Sq[a] - Sq[bb] + qa[bb];
        float txr = tr - Sr[a] - Sr[bb] + ra[bb];
        float dot = 0.f, z = 0.f;
        for (int c = 0; c < 52; c++) {
            z += qa[c] * ra[c] + qb[c] * rb[c];
            if (c != (int)a && c != (int)bb)
                dot += (Sq[c] - qa[c] - qb[c]) * (Sr[c] - ra[c] - rb[c]);
        }
        out[i] = amount * (txq * txr - dot + kk - z + qa[bb] * ra[bb]);
    }
}

__device__ __forceinline__ int lower_bound_u32(const u32* a, int n, u32 v) {
    int lo = 0, hi = n;
    while (lo < hi) { int m = (lo + hi) >> 1; if (a[m] < v) lo = m + 1; else hi = m; }
    return lo;
}
__device__ __forceinline__ int upper_bound_u32(const u32* a, int n, u32 v) {
    int lo = 0, hi = n;
    while (lo < hi) { int m = (lo + hi) >> 1; if (a[m] <= v) lo = m + 1; else hi = m; }
    return lo;
}
// Number of entries in sorted positions pos[0..n) that are < lim.
__device__ __forceinline__ int count_below(const u32* pos, int n, u32 lim) {
    int lo = 0, hi = n;
    while (lo < hi) { int m = (lo + hi) >> 1; if (pos[m] < lim) lo = m + 1; else hi = m; }
    return lo;
}

// River showdowns. One block per terminal.
// River slot data per player K: srt_offK[slot] .. srt_offK[slot+1] index
// sorted (strength srt_strK, hand srt_idxK) entries; card lists
// cpos_offK[slot*53 + c] .. [+1] hold positions (relative to the slot's
// sorted list) of hands containing card c, ascending.
// Shared: Pq[2704], Pr[2704], preq[mq], kpre[mq], cpreq[2mq], prer[mr], cprer[2mr].
extern "C" __global__ void mw_up_show(
    const u32* __restrict__ nodes, int start, int count, int p, int q, int r,
    const int* __restrict__ node_class, const float* __restrict__ coef,
    const int* __restrict__ node_river,
    const u32* __restrict__ rsq, const u32* __restrict__ rsr,
    const float* __restrict__ reach_q_buf, const float* __restrict__ reach_r_buf,
    const u32* __restrict__ srt_offp, const u32* __restrict__ srt_strp, const u32* __restrict__ srt_idxp,
    const u32* __restrict__ srt_offq, const u32* __restrict__ srt_strq, const u32* __restrict__ srt_idxq,
    const u32* __restrict__ srt_offr, const u32* __restrict__ srt_strr, const u32* __restrict__ srt_idxr,
    const u32* __restrict__ cpos_offq, const u32* __restrict__ cposq,
    const u32* __restrict__ cpos_offr, const u32* __restrict__ cposr,
    const u32* __restrict__ rank_pair,
    const u32* __restrict__ c1p, const u32* __restrict__ c2p,
    const u32* __restrict__ c1q, const u32* __restrict__ c2q,
    const u32* __restrict__ c1r, const u32* __restrict__ c2r,
    const u32* __restrict__ same_qr,
    const u32* __restrict__ cs, float* cfv, int nh_p, int nh_q, int nh_r, int nh_max)
{
    extern __shared__ float sh[];
    __shared__ float chunk_sum[257];
    __shared__ float coefs[9];
    __shared__ int need[6];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int slot = node_river[n];
    const float* rq = reach_q_buf + (u64)rsq[n] * nh_q;
    const float* rr = reach_r_buf + (u64)rsr[n] * nh_r;
    float* out = cfv + (u64)cs[n] * nh_max;
    u32 oq = srt_offq[slot], orr = srt_offr[slot], op = srt_offp[slot];
    int mq = srt_offq[slot + 1] - oq, mr = srt_offr[slot + 1] - orr, mp = srt_offp[slot + 1] - op;
    const u32* strq = srt_strq + oq; const u32* idxq = srt_idxq + oq;
    const u32* strr = srt_strr + orr; const u32* idxr = srt_idxr + orr;
    const u32* cq_off = cpos_offq + (u64)slot * 53; const u32* cr_off = cpos_offr + (u64)slot * 53;
    u32 cq_base = cq_off[0], cr_base = cr_off[0];
    const u32* rk = rank_pair + (u64)slot * 2704;

    float* Pq = sh;
    float* Pr = Pq + 2704;
    float* preq = Pr + 2704;
    float* kpre = preq + mq;
    float* cpreq = kpre + mq;
    float* prer = cpreq + 2 * mq;
    float* cprer = prer + mr;

    if (threadIdx.x < 9) coefs[threadIdx.x] = coef[((u64)node_class[n] * 3 + p) * 9 + threadIdx.x];
    for (int k = threadIdx.x; k < 2 * 2704; k += blockDim.x) sh[k] = 0.f;
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) out[i] = 0.f;
    __syncthreads();
    if (threadIdx.x < 3) {
        int x = threadIdx.x;
        need[x] = (coefs[x * 3] != 0.f) || (coefs[x * 3 + 1] != 0.f) || (coefs[x * 3 + 2] != 0.f);
        need[3 + x] = (coefs[x] != 0.f) || (coefs[3 + x] != 0.f) || (coefs[6 + x] != 0.f);
    }
    for (int k = threadIdx.x; k < mq; k += blockDim.x) {
        u32 j = idxq[k];
        float w = rq[j];
        preq[k] = w;
        u32 s = same_qr[j];
        kpre[k] = (s != SENT) ? w * rr[s] : 0.f;
        if (w != 0.f) { u32 a = c1q[j], c = c2q[j]; Pq[a * 52 + c] = w; Pq[c * 52 + a] = w; }
    }
    for (int k = threadIdx.x; k < mr; k += blockDim.x) {
        u32 j = idxr[k];
        float w = rr[j];
        prer[k] = w;
        if (w != 0.f) { u32 a = c1r[j], c = c2r[j]; Pr[a * 52 + c] = w; Pr[c * 52 + a] = w; }
    }
    __syncthreads();
    // Per-card running sums in card-list order (deterministic, no atomics).
    for (int t = threadIdx.x; t < 104; t += blockDim.x) {
        int c = t % 52;
        bool isq = t < 52;
        const u32* off = isq ? cq_off : cr_off;
        const u32* pos = isq ? cposq : cposr;
        const u32* idx = isq ? idxq : idxr;
        const float* rch = isq ? rq : rr;
        float* dst = isq ? cpreq : cprer;
        u32 base = isq ? cq_base : cr_base;
        float acc = 0.f;
        for (u32 e = off[c]; e < off[c + 1]; e++) {
            acc += rch[idx[pos[e]]];
            dst[e - base] = acc;
        }
    }
    block_scan(preq, mq, chunk_sum);
    block_scan(kpre, mq, chunk_sum);
    block_scan(prer, mr, chunk_sum);
    float tq_all = mq > 0 ? preq[mq - 1] : 0.f;
    float tr_all = mr > 0 ? prer[mr - 1] : 0.f;
    if (tq_all == 0.f || tr_all == 0.f) return;
    float k_all = kpre[mq - 1];
    bool nq0 = need[0], nq1 = need[1], nr0 = need[3], nr1 = need[4];

    for (int k = threadIdx.x; k < mp; k += blockDim.x) {
        u32 i = srt_idxp[op + k];
        u32 s = srt_strp[op + k];
        u32 a = c1p[i], bb = c2p[i];
        int lbq = lower_bound_u32(strq, mq, s), ubq = upper_bound_u32(strq, mq, s);
        int lbr = lower_bound_u32(strr, mr, s), ubr = upper_bound_u32(strr, mr, s);
        float T[2][3], K[3];
        T[0][0] = lbq > 0 ? preq[lbq - 1] : 0.f; T[0][1] = ubq > 0 ? preq[ubq - 1] : 0.f; T[0][2] = tq_all;
        T[1][0] = lbr > 0 ? prer[lbr - 1] : 0.f; T[1][1] = ubr > 0 ? prer[ubr - 1] : 0.f; T[1][2] = tr_all;
        K[0] = lbq > 0 ? kpre[lbq - 1] : 0.f; K[1] = ubq > 0 ? kpre[ubq - 1] : 0.f; K[2] = k_all;
        // Card sums of the opponents' sets at cards a and b (for T') are
        // gathered inside the loop below as Sx[a], Sx[b].
        float Sa[2][3], Sb[2][3];
        float dot[9], z[9];
        for (int t = 0; t < 9; t++) { dot[t] = 0.f; z[t] = 0.f; }
        const float* qa = Pq + a * 52; const float* qb = Pq + bb * 52;
        const float* ra = Pr + a * 52; const float* rb = Pr + bb * 52;
        const u32* ka = rk + a * 52; const u32* kb = rk + bb * 52;
        for (int c = 0; c < 52; c++) {
            // Opponent card sums for each kind at card c.
            float sq[3], sr[3];
            {
                u32 o0 = cq_off[c] - cq_base, o1 = cq_off[c + 1] - cq_base;
                int len = o1 - o0;
                const u32* ps = cposq + cq_off[c];
                sq[2] = len > 0 ? cpreq[o1 - 1] : 0.f;
                if (nq0) { int m = count_below(ps, len, (u32)lbq); sq[0] = m > 0 ? cpreq[o0 + m - 1] : 0.f; } else sq[0] = 0.f;
                if (nq1) { int m = count_below(ps, len, (u32)ubq); sq[1] = m > 0 ? cpreq[o0 + m - 1] : 0.f; } else sq[1] = 0.f;
            }
            {
                u32 o0 = cr_off[c] - cr_base, o1 = cr_off[c + 1] - cr_base;
                int len = o1 - o0;
                const u32* ps = cposr + cr_off[c];
                sr[2] = len > 0 ? cprer[o1 - 1] : 0.f;
                if (nr0) { int m = count_below(ps, len, (u32)lbr); sr[0] = m > 0 ? cprer[o0 + m - 1] : 0.f; } else sr[0] = 0.f;
                if (nr1) { int m = count_below(ps, len, (u32)ubr); sr[1] = m > 0 ? cprer[o0 + m - 1] : 0.f; } else sr[1] = 0.f;
            }
            if (c == (int)a) { for (int x = 0; x < 3; x++) { Sa[0][x] = sq[x]; Sa[1][x] = sr[x]; } }
            if (c == (int)bb) { for (int x = 0; x < 3; x++) { Sb[0][x] = sq[x]; Sb[1][x] = sr[x]; } }
            float wqa = qa[c], wqb = qb[c], wra = ra[c], wrb = rb[c];
            u32 kca = ka[c], kcb = kb[c];
            float xa[3], xb[3], ya[3], yb[3];
            xa[0] = kca < s ? wqa : 0.f; xa[1] = kca <= s ? wqa : 0.f; xa[2] = wqa;
            xb[0] = kcb < s ? wqb : 0.f; xb[1] = kcb <= s ? wqb : 0.f; xb[2] = wqb;
            ya[0] = kca < s ? wra : 0.f; ya[1] = kca <= s ? wra : 0.f; ya[2] = wra;
            yb[0] = kcb < s ? wrb : 0.f; yb[1] = kcb <= s ? wrb : 0.f; yb[2] = wrb;
            bool inh = (c == (int)a) || (c == (int)bb);
            #pragma unroll
            for (int x = 0; x < 3; x++) {
                #pragma unroll
                for (int y = 0; y < 3; y++) {
                    if (coefs[x * 3 + y] == 0.f) continue;
                    z[x * 3 + y] += xa[x] * ya[y] + xb[x] * yb[y];
                    if (!inh) dot[x * 3 + y] += (sq[x] - xa[x] - xb[x]) * (sr[y] - ya[y] - yb[y]);
                }
            }
        }
        float v = 0.f;
        #pragma unroll
        for (int x = 0; x < 3; x++) {
            #pragma unroll
            for (int y = 0; y < 3; y++) {
                float cxy = coefs[x * 3 + y];
                if (cxy == 0.f) continue;
                // P_X[a][b] / P_Y[a][b]: the combo ab itself, filtered by kind.
                u32 kab = ka[bb];
                float pq_ab = qa[bb], pr_ab = ra[bb];
                float pxab = x == 0 ? (kab < s ? pq_ab : 0.f) : (x == 1 ? (kab <= s ? pq_ab : 0.f) : pq_ab);
                float pyab = y == 0 ? (kab < s ? pr_ab : 0.f) : (y == 1 ? (kab <= s ? pr_ab : 0.f) : pr_ab);
                float tx = T[0][x] - Sa[0][x] - Sb[0][x] + pxab;
                float ty = T[1][y] - Sa[1][y] - Sb[1][y] + pyab;
                v += cxy * (tx * ty - dot[x * 3 + y] + K[x < y ? x : y] - z[x * 3 + y] + pxab * pyab);
            }
        }
        out[i] = v;
    }
}

// Up sweep, chance nodes: average over dealt cards of the child values,
// skipping hands that hold the card.
extern "C" __global__ void mw_up_chance(
    const u32* __restrict__ nodes, int start, int count,
    const u32* __restrict__ node_cs, const u32* __restrict__ children,
    const float* __restrict__ node_cdiv, const u64* __restrict__ mp_,
    const u32* __restrict__ cs, float* cfv, int nh_p, int nh_max)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    const u32* ch = children + node_cs[n];
    float inv = node_cdiv[n];
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        u64 hm = mp_[i];
        float v = 0.f;
        for (int c = 0; c < 52; c++) {
            u32 cn = ch[c];
            if (cn == SENT || (hm >> c) & 1ull) continue;
            v += cfv[(u64)cs[cn] * nh_max + i];
        }
        cfv[(u64)cs[n] * nh_max + i] = v * inv;
    }
}

// Up sweep, action nodes. mode 0: CFR (traverser combines children with the
// current sigma and updates regrets / strategy sums); mode 1: best response
// (max over children); mode 2: average strategy. Opponent nodes sum.
extern "C" __global__ void mw_up_action(
    const u32* __restrict__ nodes, int start, int count, int p, int mode,
    const int* __restrict__ node_player, const int* __restrict__ node_na,
    const u64* __restrict__ node_off, const u32* __restrict__ node_cs,
    const u32* __restrict__ children,
    float* reg, float* prd, float* str,
    const float* __restrict__ lock_sigma, const long long* __restrict__ lock_off,
    const u32* __restrict__ rsp, const float* __restrict__ reach_p,
    const float* __restrict__ disc,
    const u32* __restrict__ cs, float* cfv, int nh_p, int nh_max)
{
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int na = node_na[n];
    const u32* ch = children + node_cs[n];
    if (node_player[n] != p) {
        for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
            float v = 0.f;
            for (int a = 0; a < na; a++) v += cfv[(u64)cs[ch[a]] * nh_max + i];
            cfv[(u64)cs[n] * nh_max + i] = v;
        }
        return;
    }
    u64 off = node_off[n];
    long long lo = lock_off[n];
    float dpos = disc[0], dneg = disc[1], dstr = disc[2];
    const float* rp = reach_p + (u64)rsp[n] * nh_p;
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        float v;
        if (mode == 1 && lo < 0) {
            v = -3.0e38f;
            for (int a = 0; a < na; a++) v = fmaxf(v, cfv[(u64)cs[ch[a]] * nh_max + i]);
        } else {
            int smode = mode == 2 ? 1 : 0;
            float sum = lo >= 0 ? 0.f : sigma_sum(reg, prd, str, smode, off, na, nh_p, i);
            v = 0.f;
            for (int a = 0; a < na; a++) {
                float sg = lo >= 0 ? lock_sigma[lo + (long long)a * nh_p + i]
                                   : sigma_at(reg, prd, str, smode, off, na, nh_p, i, a, sum);
                v += sg * cfv[(u64)cs[ch[a]] * nh_max + i];
            }
            if (mode == 0 && lo < 0) {
                float rr = rp[i];
                for (int a = 0; a < na; a++) {
                    u64 k = off + (u64)a * nh_p + i;
                    float sg = sigma_at(reg, prd, str, 0, off, na, nh_p, i, a, sum);
                    float d = cfv[(u64)cs[ch[a]] * nh_max + i] - v;
                    float rg = reg[k];
                    reg[k] = rg * (rg > 0.f ? dpos : dneg) + d;
                    str[k] = str[k] * dstr + rr * sg;
                    if (prd) prd[k] = d;
                }
            }
        }
        cfv[(u64)cs[n] * nh_max + i] = v;
    }
}
