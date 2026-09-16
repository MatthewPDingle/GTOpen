# N04: remove overwritten terminal work

Prepared during the reference-data runs. No GPU timing result or production
change is claimed by this protocol. This is a scheduling experiment with the
same frozen older predictor, not an accuracy improvement by itself.

## Observed code path and hypothesis

`PreflopGpu::terminals_masked` first evaluates ordinary terminals, then the
research interface overwrites every terminal assigned a heads-up chance context.
`down` also computes ordinary equity-cache channels used by those overwritten
values. The research interface uses the original equity matrices directly.

Filter the ordinary terminal list to nodes outside the interface's contexts.
Every two-live-player terminal must have a context; assert this before changing
the schedule. With coupled multiway evaluation enabled, remaining live multiway
values are computed by that kernel. Other remaining ordinary values are folds
or sunk costs of folded players and do not read the equity cache. Thus the cache
work can be disabled. Preserve it if uncoupled multiway terminals remain.

Keep the cache allocation for this first minimal change. Preserve all predictor
coefficients, precision, trees, chance anchors, solver iterations and policies.
The new method is research-only and opt-in before CUDA graph capture. The
ordinary application and the default research path remain unchanged.

## Verification and measurements

1. Compile into `target/learned-interface-filtered`; never overwrite either the
   app or the earlier frozen research executable.
2. Run the existing independent physical-card enumeration oracle on 12 dense
   and sparse two-, three- and eight-player cases. Compare action values and
   root EVs to the earlier unfiltered outputs as well. Verify evaluation does
   not mutate stored policies.
3. Only when no reference or other research GPU process is alive, run three
   interleaved repeats of original Balanced, unfiltered frozen predictor and
   filtered identical predictor. Each starts the same eight-player game fresh,
   warms up 50 iterations and times 100 more in the same process. Iterations
   synchronize the CUDA stream; report setup, warm-up and total time separately.
4. Verify identical-predictor policy and EV parity after each repeat. The target
   is no more than 10% median iteration overhead versus original Balanced.
   Full-game accuracy and convergence remain separate requirements.

The old predictor missed a changed-policy accuracy screen. A runtime win here
does not reverse that result or permit deployment. An accuracy-qualified new
predictor must receive its own combined checks. Keep all figures and failures.
Required ordinary CPU/GPU regressions accompany any retained code change.

Use `tools/research/continuation_interface_reuse.py freeze`, then `oracle`, then
`benchmark`. The runner enforces the night-shift deadline, live-app idle check,
and research-process overlap guard. Never change frozen files after `freeze`;
a changed binary or source needs a new study directory.
