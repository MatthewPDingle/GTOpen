# Candidate: route preflop tables only over preflop rows

This separate candidate removes repeated preflop-table scans over postflop rows. It retains the original feature preparation and neural inference, checks the shared action-menu constraint once, preserves original indices and own-action histories, and applies every table in the original order to the rows it can actually change.

CPU qualification passed 76 equivalence cases and 32 malformed-input checks. Cases cover both 362/387-input representations, initial and learned routing models, all seven stack depths, all streets, score-only postflop rows, and every initial hand class in the five fitted contexts. Prepared features, indices, masks, table probabilities and final probabilities were identical. The retained real learned-model query pair also matched its saved original arrays exactly. Validation includes the original one-action postflop rejection despite those rows being skipped by the table loop.

The fixed retained history/selected pair took a median **2.823s originally** and **1.972s with routing**: 30.2% less time, or 1.43 times the scoring throughput. There were two repetitions per implementation in ABBA order with fresh policy caches, one CPU math thread and below-normal process priority. This is a small component timing comparison, not whole-cycle or four-arm throughput; it does not profile the rest of target generation.

The candidate is **not installed in the registered study or production**. The original queued helper, training sources, sample streams, target definitions, fitting schedule and downstream evidence checks remain unchanged. This CPU check does not claim CUDA qualification, a speedup for the native solver, or improved poker accuracy. Before any later adoption, preserve the registered comparison and qualify the actual integration path.

Implementation: `tools/research/stack_context_current_policy_routed_v1.py`.
Evidence: `stack-context-routed-policy-check-v1-result.json`.
