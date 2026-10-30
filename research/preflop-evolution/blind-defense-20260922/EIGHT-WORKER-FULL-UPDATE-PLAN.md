# Complete-update check for wider CPU generation

Prepared before seeing the matched pilot's final evaluation. This is execution
qualification and descriptive timing, not an additional model-quality test.

After the pilot terminates successfully and its independent readback passes,
replay A's update 79 from the original complete state 78 in four separate cases:
baseline with four workers, baseline with eight, river with eight, river with
four. All cases use the same original configurations, random streams and batch
identities. The baseline and river treatment differ as in the registered pilot;
the worker-count comparison within each treatment changes only dispatch.

Require exact checkpoint/model identity, complete restored state equality,
ordered subbatch artifacts, reservoirs and exact BTN updates against the
original scientific four-worker update. The eight-worker fixture check must
already have passed. Board workers stay at four. Every replay is excluded from
the scientific learning bank and uses existing training samples. No evaluation
deals are drawn, and no production code is changed.

Record full update wall time, physical pipeline time, observed worker identities
and external GPU waits. Four/eight order reverses across the two target methods,
but a single pair per method cannot establish a general or statistically precise
speedup. Report caching, order and competing-resource limitations. Use results
to decide whether wider workers are a suitable runtime for later matched work;
do not retrofit the currently running comparison.

The new compressed study store is capped at 6 GB plus 2 GB reserve within the
800 GB global allocated research cap. Run only after a fresh allocation scan,
with no competing research lock, production idle and available CPU/RAM/GPU.
Keep the current light-desktop sharing policy and 4 GB CUDA budget. Limit each
invocation to 90 minutes; preserve partial attempts. Resume only completed,
verified case records, always starting each unfinished replay from boundary 78.

Run `eight_worker_full_update_control_v1.py` for source readiness only;
`--run --wait` registers and begins after prerequisites already exist;
`--run --resume --wait` resumes an existing registration after authoritative
confirmation that its previous process is terminal. Do not launch duplicates.
