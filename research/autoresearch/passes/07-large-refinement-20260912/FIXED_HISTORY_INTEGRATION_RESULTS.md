# Fixed history units: complete GPU iteration mechanics

Research-only checkpoint. Port 56708 remains untouched. No claim of faster
convergence, successful large-game refinement, or production resume support.

## Engine integration

An internal preflop-research API validates unit dimensions, finite bounds
[1e-8, 1], unit-one metadata for fixed/terminal nodes and an explicit extra-byte
allocation cap. It rejects prior learning/evaluation and incompatible research
modes before publishing state. It allocates two immutable f32 vectors and
keeps their addresses stable for captured learning. Evaluation bypasses the
new up-kernel and uses native full-particle evaluation. Discounting and the
global iteration counter retain native semantics.

Unit-one nodes call the exact native action-count-specialized pf_up_impl;
unequal nodes divide regret/average increments by their fixed unit factors.
The internal setter is not yet connected to any public continuation API.
Callers cannot infer branch ownership or safe persistence from raw arrays.

## Evidence and corrections

All five history-unit tests passed in v4 (80.391 seconds including compilation).
The original numerical conversion and floor tests, standalone kernel tests,
complete-iteration tests and admission/discount tests were rerun together.
The independent verifier checks four complete-iteration cases: raw/calibrated
continuations crossed with unit-one/unequal metadata, each at age 17 through 21.

- Complete captured and eager iterations matched bit for bit.
- Unit-one complete iterations matched native histories and evaluation.
- Fresh ordinary-GPU evaluation of resulting histories matched the integrated
  engine's native final evaluation exactly.
- Histories remained finite. Fixed-node bookkeeping matched native discounting.
- Independent host discount of sequential GPU sweep outputs matched bitwise.
- Invalid dimensions, bounds, memory cap and non-unit fixed/terminal metadata
  were rejected without history mutation. Repeat/late configuration and
  incompatible modes were rejected; opposite-order coverage includes normalized
  regret, exploration and custom roots.

Retained failed predecessors explain actual changes:

1. v1 incorrectly assumed native discount preserved every fixed-node array.
   Native code decays all regrets and forced-node averages; frozen averages
   remain unchanged. Those unused histories are separate from fixed policies.
   Tests were corrected to native bookkeeping; production discount was not edited.
2. v2 found a unit-one full-iteration evaluation difference of about 1e-9 bb.
3. v3 showed explicit native arithmetic expressions alone did not fix it.
   Fusion alone was therefore not established as the cause. v4 routes unit-one
   nodes through native action-count specializations; strict equality now passes.

Standard regression results are recorded separately in raw/fixed-history-*
regressions-v1-exit.json and corresponding logs. These are correctness checks,
not CPU performance research.

## Next required experiment

Build checked branch ownership and reference-mass metadata around compact
copyback, with disjoint roots, global/local ages and hashes tied to the exact
research save. Reject missing/mismatched metadata and poison interrupted state.
Ordinary saved-game resume remains unsupported. Then run a pre-registered
matched small refinement-plus-full-continuation screen, followed by the large
case if justified. Global gap <=0.005 bb at two canonical checks and all 27
conditional-path quality gates remain unchanged and unqualified.

## Completed regression checks

- fixed-history-gpu-regressions-v1: 19 tests passed across 2 result blocks; 59.500 seconds including build.
- fixed-history-default-regressions-v1: 181 tests passed across 37 result blocks; 126.515 seconds including build.
