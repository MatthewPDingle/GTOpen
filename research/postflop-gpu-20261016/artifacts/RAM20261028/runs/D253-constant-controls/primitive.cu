extern "C" { __constant__ float d253_disc[3] = {0.f, 0.f, 0.f}; }
extern "C" __global__ void d253_constant_transport(unsigned int* output, unsigned int base, unsigned int n) {
    unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int stride = gridDim.x * blockDim.x;
    for (; i < n; i += stride) output[base + i] = __float_as_uint(d253_disc[i % 3]);
}
