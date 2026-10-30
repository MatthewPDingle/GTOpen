// Explicit research algorithm: respond to accumulated opponent strategies.
// Called only after a learning down-pass level; own and constrained nodes
// retain native reach. Parent blocks already reflect prior corrected levels.
extern "C" __global__ void pf_average_opponents_reach(
    const u32* nodes, int start, int count, int p, int np,
    const int* actors, const int* na, const u32* off,
    const u32* cstart, const u32* children, const int* source,
    const u32* reach_src, const float* strat, float* reach)
{
    if (blockIdx.x >= (u32)count) return;
    u32 nd = nodes[start + blockIdx.x];
    int actor = actors[nd];
    if (actor == p || source[nd] != 0) return;
    for (int h = threadIdx.x; h < NC; h += blockDim.x) {
        float sig[MAX_NA];
        node_sigma(strat, off[nd], na[nd], h, sig);
        float parent = reach[(size_t)reach_src[(size_t)nd*np+actor]*NC+h];
        for (int a = 0; a < na[nd]; a++) {
            u32 child = children[cstart[nd]+a];
            reach[(size_t)reach_src[(size_t)child*np+actor]*NC+h] = parent*sig[a];
        }
    }
}
