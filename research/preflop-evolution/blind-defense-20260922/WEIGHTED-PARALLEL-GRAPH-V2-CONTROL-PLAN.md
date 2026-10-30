# Shared-stream fitter integration control

After V2 fitter exactness and repeat-allocation controls pass, replay pilot generation two using two CPU workers and the shared-stream graph fitter. Require exact checkpoint, model, native artifacts, reservoir arrays, sampler and RNG state versus the original serial replay. Preserve original eight-step config for exact comparison; 512-step fit equivalence is tested separately. Same exclusive research lock, production-idle checks, memory/disk admission and storage budget as V1. No strength or production claim.
