#include <cooperative_groups.h>
namespace cg = cooperative_groups;
typedef unsigned int u32;
extern "C" __global__ void __cluster_dims__(2, 1, 1) d246_cluster_transport(
    const u32* __restrict__ source, u32* output, u32 n, u32 base)
{
    extern __shared__ u32 scratch[];
    cg::cluster_group cluster = cg::this_cluster();
    const u32 block = blockIdx.x;
    const u32 rank = cluster.block_rank();
    for (u32 i = threadIdx.x; i < n; i += blockDim.x)
        scratch[i] = source[(unsigned long long)base + (unsigned long long)block * n + i];
    cluster.sync();
    u32* peer = cluster.map_shared_rank(scratch, rank ^ 1u);
    for (u32 i = threadIdx.x; i < n; i += blockDim.x)
        output[(unsigned long long)base + (unsigned long long)block * n + i] = peer[i];
    // All remote readers finish before any producer block can exit.
    cluster.sync();
}
