# Shared-stream weighted gradient capture control

V1 retained an additional 64 MiB after each fit. Test reusing one capture stream per CUDA device across sequential fits; this is not a concurrent fitting interface. The objective, ordered gradient, Adam, seeds and fit count remain unchanged.

Require exact exported weights and numerical fit diagnostics against the direct fitter on both actual pilot reservoirs, 512 steps each. Then run eight further sequential fits and require allocated and reserved memory to plateau after garbage collection, synchronization and empty-cache. Admission and continued checks preserve production activity and free memory. Register source bytes before execution. No accuracy claim or production deployment.
