# Development smoke checks

The first launch compiled the production source successfully but module loading
failed with CUDA error 201, `invalid device context`, before any test kernels
ran. Torch lazy initialization had not made a context current. The adapter now
allocates a one-element CUDA tensor before loading modules. No solver changes
or numerical-tolerance changes were made.

The next smoke passed the random one-sweep comparisons but failed the serial
strategy-sum comparison (maximum absolute difference 1.2874603e-5). The original
CPU reference rounded multiplication and addition separately; NVRTC contracts
the production expressions into fused multiply-add instructions. The CPU
reference now emulates float32 FMA with double intermediates and one rounding.
The fixed tolerance is unchanged. This was a reference implementation change,
not a production-kernel edit.
