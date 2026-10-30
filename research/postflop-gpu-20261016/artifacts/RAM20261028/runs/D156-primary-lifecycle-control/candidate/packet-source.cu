// Isolated packet encoding prototype. Not linked into the application.
// Entry contract: 128 threads; checked disjoint packet regions supplied by host.
// Four u32 descriptor words per block: source_lo, source_hi, length, q_word_off.
// Descriptor region [0,4*N), scales [4*N,5*N), packed q words [5*N,...).
typedef unsigned int u32;
typedef unsigned long long u64;

template <bool SIGNED> __device__ unsigned short encode_one(float value, float k) {
    const float y = __fmul_rn(SIGNED ? value : fmaxf(value, 0.0f), k);
    const float lo = SIGNED ? -32768.0f : 0.0f;
    const float hi = SIGNED ? 32767.0f : 65535.0f;
    const int q = isnan(y) ? 0
        : y >= hi ? (SIGNED ? 32767 : 65535)
        : y <= lo ? (SIGNED ? -32768 : 0)
        : __float2int_rn(y);
    return (unsigned short)q;
}

template <bool SIGNED> __device__ void encode_packet(
    const float* source, u32* packet, u32 count)
{
    __shared__ float maxima[128];
    const u32 block = blockIdx.x;
    const u32 tid = threadIdx.x;
    // Host enforces grid=count and a 128-thread CTA. Descriptor/output regions
    // are disjoint, and each CTA owns its own scale and packed word interval.
    const u64 descriptor = 4ull * block;
    const u64 source_offset = (u64)packet[descriptor]
        | ((u64)packet[descriptor + 1] << 32);
    const u32 length = packet[descriptor + 2];
    const u32 qoff = packet[descriptor + 3];
    float maximum = 0.0f;
    // u64 induction avoids wrapping the last +128 for large u32 lengths.
    for (u64 i = tid; i < (u64)length; i += 128ull) {
        const float value = source[source_offset + i];
        maximum = fmaxf(maximum, SIGNED ? fabsf(value) : value);
    }
    maxima[tid] = maximum;
    __syncthreads();
    for (u32 distance = 64; distance != 0; distance >>= 1) {
        if (tid < distance) maxima[tid] = fmaxf(maxima[tid], maxima[tid + distance]);
        __syncthreads();
    }
    maximum = maxima[0];
    const bool valid = maximum > 0.0f && isfinite(maximum);
    if (tid == 0) packet[4ull * count + block] = __float_as_uint(valid ? maximum : 0.0f);
    const float k = valid ? __fdiv_rn(SIGNED ? 32767.0f : 65535.0f, maximum) : 0.0f;
    const u64 packed_count = ((u64)length + 1ull) / 2ull;
    for (u64 w = tid; w < packed_count; w += 128ull) {
        const u64 i = 2ull * w;
        const u32 low = valid ? (u32)encode_one<SIGNED>(source[source_offset + i], k) : 0;
        // Nonzero unused half is deliberate: a host scatter must obey length.
        const u32 high = i + 1 < (u64)length
            ? (valid ? (u32)encode_one<SIGNED>(source[source_offset + i + 1], k) : 0)
            : 0xd00d;
        packet[5ull * count + qoff + w] = low | (high << 16);
    }
}

extern "C" __global__ void packet_quantize_i16(
    const float* source, u32* packet, u32 count)
{
    encode_packet<true>(source, packet, count);
}
extern "C" __global__ void packet_quantize_u16(
    const float* source, u32* packet, u32 count)
{
    encode_packet<false>(source, packet, count);
}
