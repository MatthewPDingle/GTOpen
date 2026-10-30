// Native counterfactual increments have already been observed. Clip only
// the traverser's learning regrets before the next alternating traversal.
extern "C" __global__ void pf_rm_plus_clip(
    const unsigned int* nodes, int count, int p, const int* actor,
    const int* na, const unsigned int* off, const int* src, float* regrets)
{
    if (blockIdx.x >= (unsigned int)count) return;
    unsigned int nd = nodes[blockIdx.x];
    if (actor[nd] != p || src[nd] != 0) return;
    for (int i = threadIdx.x; i < na[nd]*169; i += blockDim.x) {
        unsigned int ix = off[nd] + i;
        regrets[ix] = fmaxf(0.f, regrets[ix]);
    }
}
