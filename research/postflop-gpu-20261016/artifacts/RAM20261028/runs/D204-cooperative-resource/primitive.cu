#include <cooperative_groups.h>
typedef unsigned int u32;
typedef unsigned long long u64;
extern "C" __global__ void d204_grid_order(
    u32* state, u32* scratch, int n, int base, int phases, int mode)
{
    cooperative_groups::grid_group grid = cooperative_groups::this_grid();
    if (!grid.is_valid()) {
        if (blockIdx.x == 0 && threadIdx.x == 0) state[0] = 0x0badc0deu;
        return;
    }
    for (int phase = 0; phase < phases; ++phase) {
        for (u64 i = grid.thread_rank(); i < (u32)n; i += grid.size()) {
            u32 next = (u32)((i + 128) % (u32)n);
            u32 value = state[(u64)base + next];
            scratch[(u64)base + i] = mode == 0 ? value : value ^ (0x9e3779b9u + (u32)phase);
        }
        grid.sync();
        for (u64 i = grid.thread_rank(); i < (u32)n; i += grid.size())
            state[(u64)base + i] = scratch[(u64)base + i];
        grid.sync();
    }
}
