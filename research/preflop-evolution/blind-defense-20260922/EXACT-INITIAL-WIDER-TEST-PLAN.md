# Prospective wider test of exact-initial training

Prepared while the new training trial is still running. No new candidate
accuracy result is available. The trial must finish all 78 updates, pass its
independent training audit, and meet the previously declared exact-endpoint
screen before this test is admitted. The primary candidate remains the same
complete bank, linearly weighted 1 through 78; unplayed generation 78 is not
included. There is no checkpoint or averaging-schedule search.

## What this tests

The earlier wider test found a profitable class-dependent BB first decision.
The next test checks six fixed alternatives to the new candidate:

1. A newly learned class-dependent response, fitted only on new training deals.
2. Always fold.
3. Always call.
4. Always raise to 6 bb.
5. Always jam.
6. The exact frozen class-dependent response from the previous completed test.

The sixth alternative directly tests whether the known response still profits
against the new candidate. Its file hash is
`73ea827f70d5c6cb055c98e01775ea51d0b95aa23c92e29c3282aa4fec307c2b`.
It is not refitted or adjusted to the new candidate. All later actions remain
those of the new frozen bank, for both players.

All six alternatives reuse the same per-deal four root action payoffs, so the
additional alternative does not require another set of native traversals.
The interval calculation accounts for all six comparisons.

## Fixed sample and inference plan

- New class-balanced response-training stream: seed 354331, 256 decisions per
  each of 169 classes, totaling 43,264 deals. Minimum support 16. Use the first
  maximum among legal action values; unsupported classes retain the baseline.
- Exact conditional fold/shove values, sampled call/raise values. Two halves
  of 128 observations per class measure response stability only; they never
  choose which response or candidate to test.
- Independent population test: seed 354332, 131,072 IID incoming deals,
  64-deal batches. It starts only after the new response, old response and
  residual preparation have been saved and hashed. No earlier 224332 test
  observations are reused for this evaluation.
- Uncentred call/raise residual plus exact fold/shove offset. Bounded empirical
  Bernstein intervals, family error 0.025 across six alternatives, one final
  look at the fixed count. No early strategic stopping or sample extension.

The old and new learned responses are different probes. A smaller gain against
one learned response does not, by itself, establish lower total exploitability.
The previous-response row answers the narrower known-weakness question. Report
all six means and intervals, including negative or inconclusive results.

## Admission, storage and controls

Use the completed candidate-specific 64-deal CPU/CUDA numerical/payoff gate
(seed 354231). It checks all streets and own-action histories against the same
complete bank. Control-fixture mode uses seed 354031 and is explicitly not
admissible as evidence for the full candidate.

The six-alternative pipeline has a completed CPU fixture control: 338 training
deals and 128 population deals, with independent reconstruction of all six
intervals. It also rejected five deliberate corruptions involving the frozen
prior response, its identity, its reported mean, its stored residual and an
under-corrected interval radius. This is numerical evidence, not poker strength.

Use `T:\GTOpen-research\exact-initial-wider-study-v1`; no NTFS compression
savings are assumed. Require 160 GB free at admission: a 120 GB output cap plus
40 GB reserve. A measured 64-deal storage projection with 50% margin must fit
within that cap. Keep 20 GB host RAM and 3 GB GPU memory available. One research
GPU job at a time; production activity stops research without touching the app.

Evaluation cap: 12 hours. Separate readback cap: two hours. Preserve the first
failure and all previous artifacts. No automatic restart, deletion, budget
extension or deployment. The independent reader reconstructs chance streams,
native recorded payoffs, response choices and intervals; it does not rerun the
native engine or neural inference. Those require the separate admission gate.

## Commands after the primary screen passes

```text
tools/research/hu_exact_initial_wider_admission_20260923.py --run
tools/research/hu_exact_initial_wider_study_20260923.py --run
```

A positive lower bound identifies a remaining profitable root deviation.
Failure to find one does not certify a full best response, game convergence,
other positions, other stack sizes, or readiness for production.

## Additional completed integration control

A separate CPU run exercised the full six-alternative pipeline with the real
version-4 exact-initial two-model training fixture, rather than only the older
base-model fixture. Seeds 354041 and 354042; 338 training and 128 population
deals. The scalar readback reconstructed all 30 batches and six intervals;
maximum arithmetic discrepancy was 1.14e-13 bb. It completed in 98.8 seconds,
used no GPU and did not inspect the active 78-update candidate. This gate is
required alongside the eventual full candidate CPU/CUDA admission check.
