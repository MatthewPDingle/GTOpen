# Reusing prepared GPU training data

The control passed on both final pilot reservoirs. Preparing the inputs once
instead of rebuilding and transferring them during every optimizer step reduced
the measured combined fitting time from **61.922 to 21.797 seconds (2.84x)**.
BB's fit improved from 55.250 to 19.281 seconds; BTN's from 6.672 to 2.516.
These are single-run fitting measurements, not production solver speedups.

Both implementations produced **exactly equal exported weights** after all 512
full-gradient Adam steps, and reproduced the original published generation 78.
Initial loss, gradients, first-step parameters and final loss also matched exactly.
The same 109,558 BB / 13,434 BTN retained examples, grouping, count weights,
normalization, seeds, 4,096-row chunk order and learning rate were preserved.
Generation 78 was unused in the completed poker evaluation; this control does
not replace its tested bank or establish improved poker strength.

Peak measured CUDA tensor allocation was 189 MB (excluding CUDA context).
Inputs and artifacts were hashed; an independent readback compares every
exported weight against both the old fitter and the original model. It does not
rerun gradients or timers. Production and the range preview are unchanged.

This makes a larger fresh-deal training experiment practical. The next candidate
still needs independent training-artifact checks and fresh strength evaluation.
Evidence: `sampled-physical-cached-fit-v1-{registration,result,review,independent-review}.json`.
