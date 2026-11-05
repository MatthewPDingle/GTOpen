// ICM payoffs on the GPU (see preflop/icm.rs and gpu/icm.rs).
//
// A seat's ICM value at a terminal is linear in its chance b[t] of holding
// the best hand among each pot's eligible seats:
//
//     V[j] + sum over t < j of b[t] (V[t] - V[t+1])
//
// where V[t] is its average prize change when it first wins pot t (t = j:
// wins nothing). The chip-EV kernels already compute
// sum of amount[t] b[t] - invested, so before each traverser's terminal pass
// this kernel overwrites, for that traverser only, every terminal's pot
// amounts with the coefficients V[t] - V[t+1] and its investment with -V[j].
// The chip kernels then return ICM values unchanged. The original amounts
// are not needed again: the chip kernels are their only readers.
//
// A pot that sees the flop with chips behind may end all-in for them
// (preflop/icm.rs StackOff): its value blends in the all-in's win-all and
// lose-all values, still linear in the flop pot share.
//
// V[t] weighs how the other pots fall by the other seats' range-against-range
// chances: the product of their heads-up chances, normalized, exactly as
// icm_range_odds() on the CPU.

typedef unsigned int u32;
#define NC 169
#define ICM_SEATS 9
#define ICM_THREADS 128

__device__ __forceinline__ float icm_block_sum(float x, float* scratch)
{
    for (int o = 16; o > 0; o >>= 1) x += __shfl_down_sync(0xffffffffu, x, o);
    int lane = threadIdx.x & 31, warp = threadIdx.x >> 5;
    if (lane == 0) scratch[warp] = x;
    __syncthreads();
    float total = 0.f;
    if (threadIdx.x == 0)
        for (int w = 0; w < ICM_THREADS / 32; w++) total += scratch[w];
    __syncthreads();
    return total; // valid in thread 0 only
}

// Chance that seat w holds the best hand among `cand`.
__device__ __forceinline__ float icm_odds(const float (*pr)[ICM_SEATS], u32 cand, int w, int np)
{
    float total = 0.f, mine = 0.f;
    for (int a = 0; a < np; a++) {
        if (!((cand >> a) & 1)) continue;
        float v = 1.f;
        for (int x = 0; x < np; x++)
            if (x != a && ((cand >> x) & 1)) v *= pr[a][x];
        total += v;
        if (a == w) mine = v;
    }
    return total > 0.f ? mine / total : 1.f / (float)__popc(cand);
}

// The traverser's average prize change when it first wins pot tt of the m
// pots at `masks` (tt = j: wins nothing), as icm_v() on the CPU.
__device__ float icm_v(int tt, int j, int p, int np, const u32* __restrict__ masks, int m,
    const u32* __restrict__ winners, const float* __restrict__ values, u32 o0, u32 o1,
    const float (*pr)[ICM_SEATS])
{
    u32 me = 1u << p;
    float num = 0.f, den = 0.f;
    for (u32 o = o0; o < o1; o++) {
        u32 wbits = winners[o];
        float q = 1.f;
        for (int k = 0; k < m && q > 0.f; k++) {
            u32 mask = masks[k];
            int wk = (wbits >> (4 * k)) & 15;
            if (k > 0) {
                int prev = (wbits >> (4 * (k - 1))) & 15;
                if ((mask >> prev) & 1) {
                    if (wk != prev) q = 0.f;
                    continue;
                }
            }
            u32 cand;
            if (mask & me) {
                if (k == tt) {
                    if (wk != p) q = 0.f;
                    continue;
                }
                if (tt == j) cand = mask & ~me;
                else if (k < tt) cand = mask & ~masks[tt] & ~me;
                else cand = 0; // the traverser already won a larger pot it is in
            } else {
                cand = mask;
            }
            if (!((cand >> wk) & 1)) { q = 0.f; break; }
            if (__popc(cand) > 1) q *= icm_odds(pr, cand, wk, np);
        }
        if (q > 0.f) {
            num += q * values[(size_t)o * np + p];
            den += q;
        }
    }
    return den > 0.f ? num / den : 0.f;
}

// One block of ICM_THREADS per ICM terminal, for traverser p.
// kinds: 0 = fold win, 1 = one pot, 2 = side pots (sp_base[t] is where its
// pots start in the side-pot amount list).
extern "C" __global__ void pf_icm_prepare(
    u32 count, int p, int np,
    const u32* __restrict__ nodes, const int* __restrict__ kinds,
    const u32* __restrict__ pot_start, const u32* __restrict__ masks,
    const u32* __restrict__ sp_base, const u32* __restrict__ out_start,
    const u32* __restrict__ winners, const float* __restrict__ values,
    const float* __restrict__ bal, const int* __restrict__ live,
    const u32* __restrict__ reach_src, const float* __restrict__ reach,
    const float* __restrict__ reach_mass,
    const u32* __restrict__ a_pot_start, const u32* __restrict__ a_masks,
    const u32* __restrict__ a_out_start, const u32* __restrict__ a_winners,
    const float* __restrict__ a_values, const float* __restrict__ weight,
    const float* __restrict__ flop_pot, const float* __restrict__ commit,
    const float* __restrict__ wins,
    float* pots, float* potg, float* invested, float* sp_amount)
{
    u32 t = blockIdx.x;
    if (t >= count) return;
    u32 nd = nodes[t];
    int kind = kinds[t];
    size_t ip = (size_t)nd * np + p;
    u32 o0 = out_start[t];
    if (kind == 0) {
        // Fold wins pay a constant; potf is zeroed once on upload.
        if (threadIdx.x == 0) invested[ip] = -values[(size_t)o0 * np + p];
        return;
    }
    __shared__ float dist[ICM_SEATS][NC];
    __shared__ float pr[ICM_SEATS][ICM_SEATS];
    __shared__ int has[ICM_SEATS];
    __shared__ float scratch[ICM_THREADS / 32];
    __shared__ float vt[ICM_SEATS];
    __shared__ float va[2];
    u32 others = (u32)live[nd] & ~(1u << p);
    if (__popc(others) >= 2) {
        for (int q = 0; q < np; q++) {
            if (!((others >> q) & 1)) continue;
            u32 block = reach_src[(size_t)nd * np + q];
            float m = reach_mass[block];
            if (threadIdx.x == 0) has[q] = m > 0.f;
            const float* r = reach + (size_t)block * NC;
            for (int h = threadIdx.x; h < NC; h += blockDim.x) dist[q][h] = m > 0.f ? r[h] / m : 0.f;
        }
        __syncthreads();
        for (int w = 0; w < np; w++) {
            if (!((others >> w) & 1)) continue;
            for (int x = w + 1; x < np; x++) {
                if (!((others >> x) & 1)) continue;
                if (!has[w] || !has[x]) {
                    if (threadIdx.x == 0) { pr[w][x] = 0.5f; pr[x][w] = 0.5f; }
                    continue;
                }
                // P(w beats x) = sum_j d_x[j] sum_h bal[j][h] d_w[h].
                float part = 0.f;
                for (int j = threadIdx.x; j < NC; j += blockDim.x) {
                    float db = dist[x][j];
                    if (db == 0.f) continue;
                    const float* row = bal + (size_t)j * NC;
                    float s = 0.f;
                    for (int h = 0; h < NC; h++) s += row[h] * dist[w][h];
                    part += db * s;
                }
                float total = icm_block_sum(part, scratch);
                if (threadIdx.x == 0) { pr[w][x] = total; pr[x][w] = 1.f - total; }
            }
        }
    }
    __syncthreads();

    u32 first = pot_start[t];
    int m = (int)(pot_start[t + 1] - first);
    u32 me = 1u << p;
    int j = 0;
    while (j < m && (masks[first + j] & me)) j++;
    // The stack-off all-in of a flop pot (empty range otherwise).
    u32 afirst = a_pot_start[t];
    int am = (int)(a_pot_start[t + 1] - afirst);
    int ja = 0;
    while (ja < am && (a_masks[afirst + ja] & me)) ja++;
    // V[tt] for tt = 0..j, one thread each, as the CPU's icm_v; the all-in's
    // win-all and lose-all values on threads 32 and 33.
    int tt = threadIdx.x;
    if (tt <= j) {
        vt[tt] = icm_v(tt, j, p, np, masks + first, m, winners, values, out_start[t], out_start[t + 1], pr);
    } else if (am > 0 && (tt == 32 || tt == 33)) {
        int at = tt == 32 ? 0 : ja;
        va[tt - 32] = icm_v(at, ja, p, np, a_masks + afirst, am, a_winners, a_values,
            a_out_start[t], a_out_start[t + 1], pr);
    }
    __syncthreads();
    if (threadIdx.x != 0) return;
    // Blend in the stack-off all-in (weight 0 elsewhere), as on the CPU.
    float base = j == 0 ? vt[0] : vt[1];
    float c = j == 0 ? 0.f : vt[0] - vt[1];
    if (am > 0) {
        float w = weight[t];
        if (ja == 0) {
            base = (1.f - w) * base + w * va[0];
        } else {
            size_t tp = (size_t)t * np + p;
            float win = va[0], lose = va[1], all = wins[tp];
            base = (1.f - w) * base + w * (lose + commit[tp] / all * (win - lose));
            c = (1.f - w) * c + w * flop_pot[t] / all * (win - lose);
        }
    }
    if (j == 0) {
        invested[ip] = -base;
    } else if (kind == 1) {
        c = fmaxf(c, 0.f);
        pots[nd] = c;
        potg[nd] = c;
        invested[ip] = -base;
    } else {
        u32 base_at = sp_base[t];
        for (int k = 0; k < j; k++) sp_amount[base_at + k] = vt[k] - vt[k + 1];
        invested[ip] = -vt[j];
    }
}
