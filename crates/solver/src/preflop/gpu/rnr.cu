// "Trust the read" on the GPU (see gpu/rnr.rs). A ruled seat is its read
// with probability t and its free type otherwise. Where it does not traverse,
// it plays the behavioral mixture of the two types:
//
//   mix(a, h) = (t * read(a, h) + (1 - t) * free(a, h)) / (t * read_in(h) + (1 - t) * free_in(h))
//
// where read/free are the type's own reach after action a and *_in the reach
// at the node. Its reach under `mix` is then exactly t * read + (1 - t) * free
// at every node, so the ordinary down sweep and every terminal kernel see the
// mixed reach unchanged. One launch per tree level of ruled-seat nodes, top
// down: the free type's own reach flows through rf, block rf_in[r] in and
// rf_out[r] + a out.

typedef unsigned int u32;
#define NC 169
#define MAX_NA 16
#define NO_LOCK 0xffffffffu

__device__ __forceinline__ void rnr_sigma(
    const float* __restrict__ src, u32 off, int na, int h, int regret, float* out)
{
    float sum = 0.f;
    for (int a = 0; a < na; a++) {
        float v = src[off + (u32)a * NC + h];
        if (regret) v = v > 0.f ? v : 0.f;
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

// mode 0: the free type's current (regret-matching) strategy, else its
// average. lock[r] != NO_LOCK: a point lock binds both types; the node's
// forced sigma already is the lock and is left alone.
extern "C" __global__ void pf_rnr_mix(
    const u32* __restrict__ nodes, int start, int count,
    const int* __restrict__ na_arr,
    const u32* __restrict__ loc, u32 base,
    const float* __restrict__ regrets, const float* __restrict__ strat, int mode,
    const u32* __restrict__ lock, const u32* __restrict__ mix_off,
    float* forced, const float* __restrict__ rs,
    const u32* __restrict__ rf_in, const u32* __restrict__ rf_out,
    float* rf, float t)
{
    if (blockIdx.x >= (u32)count) return;
    int r = start + (int)blockIdx.x;
    u32 nd = nodes[r];
    int na = na_arr[nd];
    u32 lo = loc[r];
    u32 lk = lock[r];
    u32 mo = mix_off[r];
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float sf[MAX_NA];
        if (lk != NO_LOCK) {
            for (int a = 0; a < na; a++) sf[a] = forced[lk + (u32)a * NC + h];
        } else if (mode == 0) {
            rnr_sigma(regrets, base + lo, na, h, 1, sf);
        } else {
            rnr_sigma(strat, base + lo, na, h, 0, sf);
        }
        float fin = rf[(size_t)rf_in[r] * NC + h];
        float rin = 0.f;
        for (int a = 0; a < na; a++) rin += rs[lo + (u32)a * NC + h];
        float den = t * rin + (1.f - t) * fin;
        for (int a = 0; a < na; a++) {
            float fo = fin * sf[a];
            rf[(size_t)(rf_out[r] + (u32)a) * NC + h] = fo;
            if (lk == NO_LOCK) {
                forced[mo + (u32)a * NC + h] = den > 1e-37f
                    ? (t * rs[lo + (u32)a * NC + h] + (1.f - t) * fo) / den
                    : sf[a];
            }
        }
    }
}
