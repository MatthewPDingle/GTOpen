# Later-action training: joint implementation gate

The September 25 two-update GPU control and independent CPU readback both passed. The new training path is ready for a fixed-budget matched scientific comparison. These checks establish implementation consistency, not better poker strategies.

## What passed

- Two real updates, each using eight batches of 64 physical deals and the original 512 fitting steps. The qualified captured-gradient GPU implementation was used.
- Restoring the first completed checkpoint and replaying update two reproduced the model/checkpoint references, reservoirs, replacement RNGs, chance stream, exact initial accumulators, root accumulators, and native artifacts exactly.
- Generation one reproduced the old matched trial's physical deals, action seeds, policies, and raw sampled records. Its initial policy was unchanged.
- Current CPU/CUDA inference and the complete two-generation played-policy average agreed within the registered tolerance. The unplayed final model was excluded.
- New version-7 model/checkpoint types prevent accidental interchange with the earlier target estimator. Five configuration/type rejection cases passed.
- The independent reader reconstructed 1,024 BB root targets and 22,835 positive postflop target replacements, plus all 24,856 reservoir insertions, sampled visits, RNG states, metadata, and saved arrays. It did not call the training update or new ingestion implementation and did not refit the networks.

The independent reader's largest postflop/reservoir target difference was 5.684e-14; its largest root-state difference was 3.411e-13, and its largest policy difference was 7.251e-13. All were below their registered tolerances.

The GPU control, including restart replay and inference checks, took 265.094 seconds. The independent CPU readback took 130.156 seconds. These are implementation-control timings, not full-trial speed measurements.

## Why this is the next scientific test

The earlier root-only action integration did not improve the two-seed stability diagnostic. The new estimator also removes future-action sampling from postflop targets at each fixed sampled private hand and runout. It leaves uncertainty from sampled cards and function approximation. Policies still receive only information visible at their decision; future cards are used for training target evaluation only.

The next study matches both old trial seed sets, training budgets and averaging rules. It separately measures reproducibility and effectiveness. See `LATER-ACTION-MATCHED-STUDY-PLAN.md` for the prospective comparison. No experimental range has been promoted to production, and port 56708 was not changed.

## Storage and evidence

The frozen pilot occupies 867,339,579 allocated bytes. New long-run stores use NTFS compression, with a 9 GB allocated cap per trial and a fresh combined-root admission. The first admission reserves space for the second trial, 8 GB of subsequent evaluation evidence, and the existing 2 GB reserve within the 800 GB combined ceiling. If any guard fails, preserve the completed checkpoints and partial-attempt evidence.

- `later-action-joint-control-v1-registration.json`: SHA-256 `29d8ca2aeca6b5c8229340a4e16bb3be18bcdf20d168ebda4c078600ce6a733f`.
- `later-action-joint-control-v1-result.json`: SHA-256 `d7757ea2dac9f24f89e835ade8503c2c094f4bffa56f6b4475fb9b5d5a2268fd`.
- `later-action-joint-control-v1-readback-registration.json`: SHA-256 `fbe98692faa057e15d1509aa0d1a3f3cc8a19be8210620d452838fbedc824939`.
- `later-action-joint-control-v1-independent-review.json`: independent reconstruction results.
- `tools/research/hu_later_action_training_review_20260925.py`: independent reader.
- `tools/research/hu_later_action_matched_trial_20260925.py`: bounded matched trial controller.
