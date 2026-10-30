# Combined physical CUDA pipeline check

Status: completed and passed after the finite GPU comparison released the GPU.
This control closes the remaining combined-device integration gap; it does not
train or validate a new poker equilibrium.

The registered sequence exports all queries from the 16-deal fixture, evaluates
both fixed player networks on CUDA, and transports their legal probabilities into
32 independently checked physical traversals. The resulting advantage visits feed
capacity-257 per-player reservoirs. Three copies exercise replacement/duplicates;
they do not constitute fresh training data.

The control compares the chunked CPU and CUDA gradients at identical initial
weights, fits each network for 64 CUDA Adam steps with chunks of 31, reloads the
fitted weights in the Rust reference, and compares scores and legal probabilities
on every exported observation. It finally consumes those new CUDA probabilities
in another 32 independently checked traversals. This last step tests that a fit
can feed the next traversal; it is not a multi-iteration self-play study.

Float32 is explicit, TF32 is disabled and deterministic algorithms are enabled.
Scores must agree within 2e-5, policies within 1e-4, and initial CPU/CUDA gradients
within 1e-5 absolute. The bridge's cached versus on-demand traversal comparisons
must remain exact. No claim is made that CPU and GPU training trajectories are
identical: small arithmetic differences can change future sampling decisions.

The controller waits only behind a live research-lock owner, for at most four
hours. It does not clear stale locks. It cancels on production activity or changed
registered inputs. Once admitted, it reserves the shared GPU research lock and
enforces a five-minute execution cap, 20 GB free RAM and 3 GB free VRAM. It stops
only its own worker/descendants if a guard fails, preserves available evidence,
and does not automatically retry. The full expected runtime is a short control,
not another long strategic run.

The completed control covered 7,277 visible observations and 64 verified
traversals. CPU/CUDA teacher scores differed by at most 1.43e-6 and probabilities
by 4.63e-6; the initial gradient difference was 2.98e-8. Reloading the fitted CUDA
weights into Rust gave maximum score/probability differences of 1.67e-6 and
7.20e-6. All registered tolerances passed, and caller RNG states were preserved.

The worker took 5.03 seconds after queueing and peaked at 74.21 MB of allocated
GPU tensors, excluding the CUDA context. TF32 stayed disabled. Both the
controller review and an independent readback verified all 20 frozen inputs
and seven artifact hashes. This qualifies the combined data path only. The
finite strategic comparison did not pass all four cases, and physical training,
fresh evaluation and upstream-range limitations need separate evidence before
changing the preview or production.

Controller: `tools/research/hu_sampled_physical_pipeline_gpu_control_20260922.py --wait`.
Evidence prefix: `sampled-physical-pipeline-gpu-v1`.
