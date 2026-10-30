# D036 R3 emitted PTX supplement

The emitted up_fold PTX supports the source mechanism: four fewer dynamically executed block barriers for a valid CTA reaching the reduction with shape 128 x 1 x 1. This is code-generation evidence, not a timing result or performance acceptance.

Baseline lines 351-370 contain a common partial-store barrier followed by the halving reduction loop. At blockDim.x=128 the loop visits 64,32,16,8,4,2,1, executing its barrier seven times. Candidate lines 352-360 test x=128,y=1,z=1. The selected branch (380-432) executes the shared64 barrier at388, shared32 barrier at397, then final publication barrier at432. Thus reduction phase barriers, including the common partial-store barrier, are 8 versus4. Including the common local-reach preload barrier at101, full active CTA paths have9 versus5. Count0/excess CTAs that return early are excluded from these path counts.

Static bar.sync instruction sites are3 baseline versus6 candidate because the original loop remains as fallback, alongside the specialized branch. Static instruction totals must not be substituted for executed path counts. The non128 branch retains the same shared-load, add, store, halving and barrier sequence.

In the specialization every lane of warp0 reaches all five full-mask shfl.sync.down operations at offsets16,8,4,2,1. Threads32-127 skip that warp-local work and rendezvous at the final block barrier. The generated adds execute speculatively before selp for steps16/8/4/2; selp preserves each inactive lane's previous value. This retains the selected dependency tree. After step1 only lane0 writes total_parts[0], followed by the unconditional block barrier before all threads read the total.

The retained shared64/32 steps add higher-slot then lower-slot values, matching the baseline emitted order. The warp tail expresses local then shuffled operands; the baseline shared loop emitted the reversed pair. This is the previously documented NaN payload caveat, not a proof of unrestricted NaN identity. Both entries lack an explicit .ftz modifier. The finite/signed-zero/subnormal/overflow corpus and full-kernel guards have separate native differential evidence; no universal input claim is inferred from code inspection.

No build, GPU execution, production change or timing measurement was performed by this reviewer. The complete native evidence audit remains separate.
