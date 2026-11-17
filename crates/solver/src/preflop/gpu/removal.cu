// Blockers (card removal) on the GPU; see preflop/removal.rs for the model
// and the CPU reference (removal_terminal_value).
//
// The ordinary terminal kernels price every terminal with the plain
// product of the other seats' reach masses. With card removal on:
//  1. pf_removal_rank_mass: per reach block, the mass on combos holding one
//     specific card of each rank (13 values).
//  2. pf_removal_heads_up (after pf_terminal): heads-up single-pot showdowns
//     and flop leaves are repriced with the opponent's range conditioned on
//     each hero class's cards, still times the plain reach product.
//  3. pf_removal_scale (after every other terminal kernel): each class's
//     value is rescaled from the plain reach product to its own conditioned
//     one.

typedef unsigned int u32;
#define NC 169
#define NR 13
#define DECK_SCALE (1326.0f / 1225.0f)

extern "C" __global__ void pf_removal_rank_mass(
    const float* __restrict__ reach, u32 blocks, float* rank_mass)
{
    u32 b = blockIdx.x * blockDim.x + threadIdx.x;
    if (b >= blocks) return;
    const float* r = reach + (size_t)b * NC;
    float m[NR];
    for (int i = 0; i < NR; i++) m[i] = 0.f;
    for (int j = 0; j < NC; j++) {
        float x = r[j];
        int a = j / 13, c = j % 13;
        // Combos of this class holding one specific card of a rank, over the
        // class's combos: pairs 3/6, suited 1/4, offsuit 3/12.
        if (a == c) {
            m[a] += 0.5f * x;
        } else {
            m[a] += 0.25f * x;
            m[c] += 0.25f * x;
        }
    }
    for (int i = 0; i < NR; i++) rank_mass[(size_t)b * NR + i] = m[i];
}

// Reach mass of `block` compatible with one combo of hero class h, rescaled
// to the 50-card deck (conditioned_mass on the CPU).
__device__ __forceinline__ float pf_removal_mass(
    const float* __restrict__ reach, const float* __restrict__ reach_mass,
    const float* __restrict__ rank_mass, u32 block, int h)
{
    int a = h / 13, c = h % 13;
    float combos = a == c ? 6.f : (a > c ? 4.f : 12.f);
    const float* m = rank_mass + (size_t)block * NR;
    float compatible = reach_mass[block] - m[a] - m[c] + reach[(size_t)block * NC + h] / combos;
    return fmaxf(0.f, DECK_SCALE * compatible);
}

// One block per heads-up single-pot pot-share terminal; mirrors
// pf_terminal's pricing. eqw is eqtab with every entry [j*NC+h] multiplied
// by the removal weight W[h][j]; the equity cache (when used) was filled
// from it, so cache * mass = sum_j eqw * reach.
extern "C" __global__ void pf_removal_heads_up(
    const u32* __restrict__ terms, int count, int p, int np,
    const int* __restrict__ live_arr, const float* __restrict__ pots,
    const float* __restrict__ inv, const float* __restrict__ rw,
    const float* __restrict__ potg, const int* __restrict__ calib,
    const float* __restrict__ cbase, float clip_lo, float clip_hi,
    const float* __restrict__ eqw,
    const u32* __restrict__ reach_src, const float* __restrict__ reach,
    const float* __restrict__ reach_mass, const float* __restrict__ rank_mass,
    const u32* __restrict__ eq_slots, const float* __restrict__ eq_cache,
    int use_eq_cache, unsigned long long eq_cache_stride,
    const u32* __restrict__ val_slot, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = terms[blockIdx.x];
    int lv = live_arr[nd];
    if (!((lv >> p) & 1)) return; // pf_terminal wrote -invested
    float prob = 1.f;
    u32 block = 0;
    for (int q = 0; q < np; q++) {
        if (q == p) continue;
        u32 b = reach_src[(size_t)nd * np + q];
        prob *= reach_mass[b];
        if ((lv >> q) & 1) block = b;
    }
    float mass = reach_mass[block];
    float invp = inv[(size_t)nd * np + p];
    float w = rw[(size_t)nd * np + p];
    int mode = calib[nd];
    int channel = w < 1.f ? 1 : 2;
    const float* rq = reach + (size_t)block * NC;
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float v = 0.f;
        float cond = pf_removal_mass(reach, reach_mass, rank_mass, block, h);
        if (prob > 0.f && cond > 0.f) {
            float equity, relative = 0.f;
            if (use_eq_cache) {
                equity = eq_cache[(size_t)eq_slots[block] * NC + h] * mass;
                if (mode == 2)
                    relative = eq_cache[(size_t)channel * eq_cache_stride + (size_t)eq_slots[block] * NC + h] * mass;
            } else {
                float d = 0.f;
                for (int j = 0; j < NC; j++) d += eqw[(u32)j * NC + h] * rq[j];
                equity = d;
                if (mode == 2) {
                    const float* table = eqw + channel * NC * NC;
                    float e = 0.f;
                    for (int j = 0; j < NC; j++) e += table[j * NC + h] * rq[j];
                    relative = e;
                }
            }
            equity /= cond;
            float share;
            if (mode == 2) {
                relative /= cond;
                float blend = fminf(fabsf(w - 1.f) / 0.08f, 1.f);
                share = pots[nd] * (equity + blend * (relative - equity));
            } else if (mode) {
                float r = cbase[h] * w;
                r = r < clip_lo ? clip_lo : (r > clip_hi ? clip_hi : r);
                share = potg[nd] * equity * r;
            } else {
                float pe = pots[nd];
                share = pe * equity * w;
                if (share > pe) share = pe;
            }
            v = prob * (share - invp);
        }
        val[(size_t)val_slot[nd] * NC + h] = v;
    }
}

// One block per terminal: plain reach product -> each class's own.
extern "C" __global__ void pf_removal_scale(
    const u32* __restrict__ terms, int count, int p, int np,
    const u32* __restrict__ reach_src, const float* __restrict__ reach,
    const float* __restrict__ reach_mass, const float* __restrict__ rank_mass,
    const u32* __restrict__ val_slot, float* val)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = terms[blockIdx.x];
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float scale = 1.f;
        for (int q = 0; q < np; q++) {
            if (q == p) continue;
            u32 block = reach_src[(size_t)nd * np + q];
            float mass = reach_mass[block];
            scale *= mass > 0.f ? pf_removal_mass(reach, reach_mass, rank_mass, block, h) / mass : 0.f;
        }
        val[(size_t)val_slot[nd] * NC + h] *= scale;
    }
}
