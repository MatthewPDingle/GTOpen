// Proposed storage-only gather/scatter. The solver still traverses the full tree.
// Source is a proposal until compiled and checked against resident full arrays.
typedef unsigned int u32;
typedef unsigned long long u64;
extern "C" __global__ void continuation_storage_copy(
    const u32* nodes, int count, const unsigned short* node_attrs,
    const u64* full_offsets, const u64* packed_offsets,
    float* full_regrets, float* full_sums, float* packed_regrets, float* packed_sums,
    int nh, int player, int gather)
{
    int b=blockIdx.x;
    if(b>=count) return;
    u32 node=nodes[b];
    if((node_attrs[node] >> 8)!=player) return;
    u64 full=full_offsets[node], packed=packed_offsets[b];
    int count_values=(node_attrs[node] & 0xff)*nh;
    for(int i=threadIdx.x;i<count_values;i+=blockDim.x) {
        if(gather) {
            packed_regrets[packed+i]=full_regrets[full+i];
            packed_sums[packed+i]=full_sums[full+i];
        } else {
            full_regrets[full+i]=packed_regrets[packed+i];
            full_sums[full+i]=packed_sums[packed+i];
        }
    }
}
