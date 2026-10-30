
#if !defined(__CUDA_ARCH__) || __CUDA_ARCH__ < 800
#error Scoped priority cleanup requires SM80 or newer
#endif
extern "C" __global__ void normalize_owned_l2(const unsigned char* base, unsigned long long lines) {
    unsigned long long i = (unsigned long long)blockIdx.x * blockDim.x + threadIdx.x;
    unsigned long long stride = (unsigned long long)gridDim.x * blockDim.x;
    for (; i < lines; i += stride) {
        const unsigned char* address = base + 128ull * i;
        asm volatile("{ .reg .u64 g; cvta.to.global.u64 g, %0; "
                     "applypriority.global.L2::evict_normal [g], 128; }" :: "l"(address) : "memory");
    }
}
