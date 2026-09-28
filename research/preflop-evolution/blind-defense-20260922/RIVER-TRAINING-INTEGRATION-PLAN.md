# Research training integration

Freeze K=64 and the qualified river estimator, weighted overlay and stdin/stdout
transport. Add a separate river_training_workers_v1 and river_training_pipeline_v1;
leave the baseline implementation and every executed control unchanged.

Workers bind the full current-model source digest and generation, build CPU
policy engines once per spawned worker, then generate conditional values and
pass them through the qualified overlay ingester. Actual reservoir insertion
stays in the coordinator in source order. Root integration still uses original
full-action values. The pipeline retains both fits, board-root updates, exact
BTN updates, complete played bank and atomic joint checkpoint publication.
Candidate checkpoint config explicitly records method and K=64.

First check the eight existing valid weighted TRAIN slices, under both bound
generation-77 models, with two spawned CPU workers and serial execution. Require
exact event, root-integration, target and ordered reservoir agreement. Compare
base target audits and directly apply the qualified overlay for an insertion
oracle. Reject wrong result order, iteration, visit count, model digest and
played generation without altering real reservoirs. No GPU or fit in this check.
Maximum 360 seconds and 40 MB new evidence; preserve failures under this version.

Then preregister a matched full-update pilot at a verified completed boundary.
The existing branch completed 78 updates; generation 78 is the next model, while
77 was the last played model in previous controls. Restore both arms from the
same complete checkpoint, with identical source/action/fit seeds and budgets.
Retain original configuration except explicit experimental target provenance;
fork configuration by writing a new research checkpoint, never relabel old ones.
Use a new output directory; do not modify the source checkpoint or production.

Quality evaluation requires fresh held-out deals, registered before use, and the
complete full-policy payoff comparison. Measure all elapsed work, including CPU
targets, CUDA fitting, board roots and checkpoint IO. A worker control pass alone
is not a training or poker-quality result. Re-inventory the global 800 GB cap
before admitting the larger run. Share GPU with light desktop use as authorized;
yield to active solves/heavy GPU usage and preserve a resumable full boundary.
