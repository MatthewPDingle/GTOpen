// Experimental CPU-encoding equivalence proof only; not used by GpuSolver.
// One 128-thread CTA owns one complete node-like block, including empty blocks.
// Both output types use raw 16-bit words; signed results retain their i16 bits.
typedef unsigned int u32;
typedef unsigned long long u64;

template <bool SIGNED> __device__ void quantize_block(
    const float* src, const u64* offsets, const u32* lengths,
    unsigned short* words, float* scales)
{
    __shared__ float maxima[128];
    const u32 block = blockIdx.x;
    const u32 tid = threadIdx.x;
    const u64 offset = offsets[block];
    const u32 length = lengths[block];
    float maximum = 0.0f;
    for (u32 i = tid; i < length; i += 128) {
        float value = src[offset + i];
        // fmaxf ignores NaNs, as Rust f32::max does. No addition/reassociation.
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
    if (tid == 0) scales[block] = valid ? maximum : 0.0f;
    if (!valid) {
        for (u32 i = tid; i < length; i += 128) words[offset + i] = 0;
        return;
    }

    // Match two separate Rust f32 operations, including overflow of k to +Inf.
    const float k = __fdiv_rn(SIGNED ? 32767.0f : 65535.0f, maximum);
    const float lo = SIGNED ? -32768.0f : 0.0f;
    const float hi = SIGNED ? 32767.0f : 65535.0f;
    for (u32 i = tid; i < length; i += 128) {
        const float value = src[offset + i];
        const float y = __fmul_rn(SIGNED ? value : fmaxf(value, 0.0f), k);
        // Rust round_ties_even() then saturating `as`: NaN -> 0, infinities
        // saturate. In-range integers here are all exactly representable in f32.
        const int q = isnan(y) ? 0
            : y >= hi ? (SIGNED ? 32767 : 65535)
            : y <= lo ? (SIGNED ? -32768 : 0)
            : __float2int_rn(y);
        words[offset + i] = (unsigned short)q;
    }
}

extern "C" __global__ void quantize_i16_proof(
    const float* src, const u64* offsets, const u32* lengths,
    unsigned short* words, float* scales)
{
    quantize_block<true>(src, offsets, lengths, words, scales);
}

extern "C" __global__ void quantize_u16_proof(
    const float* src, const u64* offsets, const u32* lengths,
    unsigned short* words, float* scales)
{
    quantize_block<false>(src, offsets, lengths, words, scales);
}
