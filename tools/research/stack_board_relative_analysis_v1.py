"""Summarize the completed fixed comparison; no fitting or new evaluation."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
PREFIX = 'stack-board-relative-learning-v1'

def read(path):
    return json.loads(path.read_bytes())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result_path = OUT / f'{PREFIX}-result.json'
readback_path = OUT / f'{PREFIX}-readback-v1.json'
registration_path = OUT / f'{PREFIX}-registration.json'
result, readback, registration = map(read, (result_path, readback_path, registration_path))
assert result['passed'] and result['complete'] and readback['passed']
assert result['registration_sha256'] == sha(registration_path)
assert readback['inputs'][str(result_path)] == sha(result_path)
assert not result['diagnostic_gate_passed']
assert not result['production_modified'] and not readback['production_modified']
assert not Path('T:/Dev/GTOpen/research/preflop-evolution/representative-coverage-20260919/running.lock').exists()

summaries = []
for seed in registration['seeds']:
    tests = {t['width']: t for t in result['tests'] if t['seed'] == seed}
    contexts = {w: {c['stack']: c for c in t['score']['contexts']} for w, t in tests.items()}
    gate = next(g for g in result['diagnostic_gates'] if g['seed'] == seed)
    assert gate['relative_reduction'] >= .2 and not gate['absolute_gate'] and not gate['passed']
    depths = []
    for depth in registration['heldout_depths']:
        a, b = contexts[362][depth], contexts[387][depth]
        depths.append(dict(stack=depth, baseline_mean_bb=a['mean_regret_bb'],
            candidate_mean_bb=b['mean_regret_bb'], required_maximum_bb=depth * .001,
            baseline_p99_bb=a['p99_regret_bb'], candidate_p99_bb=b['p99_regret_bb'],
            baseline_maximum_bb=a['maximum_regret_bb'], candidate_maximum_bb=b['maximum_regret_bb']))
    partitions = {}
    for key in ('hand_groups', 'seats', 'price_bands'):
        items = []
        for index, item in enumerate(contexts[362][60][key]):
            identity = {k: item[k] for k in ('name', 'actor', 'minimum_equity', 'maximum_equity') if k in item}
            measures = {}
            for width in (362, 387):
                pieces = [(contexts[width][d], contexts[width][d][key][index]) for d in registration['heldout_depths']]
                contribution = sum(p.get('mean_regret_bb', 0) * p['rows'] / c['stack'] / c['rows'] / 2 for c, p in pieces)
                measures[str(width)] = dict(rows=sum(p['rows'] for c, p in pieces),
                    contribution_to_equal_depth_normalized_mean=contribution)
            items.append(dict(identity=identity, measures=measures))
        for width in (362, 387):
            expected = gate['baseline' if width == 362 else 'candidate']
            assert abs(sum(x['measures'][str(width)]['contribution_to_equal_depth_normalized_mean'] for x in items) - expected) < 1e-12
        partitions[key] = items
    summaries.append(dict(seed=seed, gate=gate, heldout_depths=depths, partitions=partitions))

base_seconds = sum(f['training_seconds'] for f in result['fits'] if f['width'] == 362)
candidate_seconds = sum(f['training_seconds'] for f in result['fits'] if f['width'] == 387)
analysis = dict(format=1, created_utc=datetime.now(timezone.utc).isoformat(),
    kind='Analysis of completed registered results; no new experiment',
    source_sha256=sha(Path(__file__)),
    inputs={str(p): sha(p) for p in (result_path, readback_path, registration_path)},
    experiment_completed=True, independent_readback_passed=True,
    both_relative_improvement_gates_passed=True, absolute_accuracy_gate_passed=False,
    diagnostic_gate_passed=False, seeds=summaries,
    baseline_fit_seconds=base_seconds, candidate_fit_seconds=candidate_seconds,
    candidate_fit_cost_ratio=candidate_seconds / base_seconds,
    timing_limitation='Sequential single runs including validation/checkpoints, not a speed benchmark',
    rows_replayed=readback['rows_replayed'], verified_files=readback['verified_files'],
    maximum_cpu_cuda_mean_error_bb=readback['maximum_cpu_cuda_mean_regret_error_bb'],
    scope='Terminal river Fold/Call against a uniform legal opponent; not an all-street or preflop accuracy test',
    full_preflop_accuracy_qualified=False, new_training=False, new_test_data=False,
    production_modified=False, promotion=False, next_experiment_launched=False)
analysis_path = OUT / f'{PREFIX}-analysis-v1.json'
with analysis_path.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(analysis, stream, indent=2)
    stream.write('\n')

table = '\n'.join(f"| {s['seed']} | {d['stack']} | {d['baseline_mean_bb']:.5f} | {d['candidate_mean_bb']:.5f} | {d['required_maximum_bb']:.3f} |"
    for s in summaries for d in s['heldout_depths'])
primary = '\n'.join(f"| {s['seed']} | {s['gate']['baseline'] * 100:.5f}% | {s['gate']['candidate'] * 100:.5f}% | {s['gate']['relative_reduction'] * 100:.2f}% | Fail |" for s in summaries)
findings = f"""# Relative hand inputs help, but the accuracy gate still fails

The registered 362-versus-387-input comparison finished successfully, and its
independent CPU readback passed. Giving the model explicit facts about what its
hole cards add to the visible board reduced fresh-test average decision loss by
46.11% and 23.87% in the two paired seeds. Both clear the predeclared 20% relative
improvement requirement. Neither meets the separate absolute accuracy limit.
Preserve these findings as a useful representation result, not a promoted model.

## What was tested

The candidate adds 25 visible-card facts: the board's own hand category and
tiebreak ranks, whether the player merely plays the board or improves it, and
whether zero, one or two private cards are needed. These inputs contain no
opponent cards, equities or target labels. They add 3,200 trainable parameters
across the two player networks; this is not an equal-parameter-count comparison.

Both arms used the same 512 fitting boards, 8,192 updates, optimizer, batches,
targets and two 64/64 networks. Extra input weights started at zero; initial
predictions and common batch draws were exactly paired. Model selection used
only 32 fresh validation boards. All four checkpoint identities were frozen
before labels were prepared for the 64 fresh final-test boards. The 96 new board
groups exclude all 692 earlier groups; all 608 fitting/validation/test groups
are distinct within this comparison.

The reference is a terminal river Fold/Call decision against a uniform legal
opponent hand distribution. It prices the call exactly for this restricted
situation. Depths 20/40/100/200/400bb were fitted; 60/150bb were excluded from
fitting and selection, but their geometries had been studied previously.
Decision rows are correlated combinations of board, hand and public price;
their large count is not a count of independent poker hands or board samples.

## Predeclared outcome

The primary mean weights 60bb and 150bb equally after dividing decision loss by
starting stack. Lower is better. The combined gate also requires mean loss at
most 0.1% of starting stack at each excluded depth.

| Seed | Baseline loss / stack | Candidate loss / stack | Reduction | Combined gate |
| --- | ---: | ---: | ---: | --- |
{primary}

| Seed | Depth, bb | Baseline mean loss, bb | Candidate mean loss, bb | Required maximum, bb |
| --- | ---: | ---: | ---: | ---: |
{table}

These are losses per evaluated terminal decision under the diagnostic's sampling
distribution, not a preflop win rate, bb/100, or whole-game exploitability.
The candidate remains approximately 1.50-1.94 times the absolute error budget.
No threshold, checkpoint selection rule or training budget was changed after
seeing these final results.

## Remaining weaknesses and adverse evidence

At 150bb, the candidate's 99th-percentile losses are 6.72/8.42bb and maxima are
63.62/42.73bb. These improve on the paired baseline tails but remain substantial.
The average improvement does not establish reliable decisions for every hand.

Pair, high-card and two-pair hands contribute most of the remaining aggregate
loss. The second seed's high-card contribution is essentially unchanged, and
some less common categories (including flushes and straights) worsen. These
unfavorable slices remain in the original result and the analysis JSON. Both
actors and all populated price bands improve in aggregate; price bands requiring
40% equity or more have no rows in the two held-out geometries and provide no
support for generalizing to those prices.

The selected candidate has worse validation mean than the selected baseline in
both seeds, despite its improvement on these fresh final boards. The first
baseline selected step4096; the other three selected step8192. This difference
between validation and final-test outcomes, the limited board sample and only
two seeds argue against calling the improvement universal or statistically
settled. Absolute numbers from earlier studies used different fresh boards and
seeds and must not be treated as a paired regression comparison.

## Verification and cost

Independent NumPy CPU inference checked {readback['verified_files']:,} file
identities and reconstructed {readback['rows_replayed']:,} final decision rows.
Maximum CPU/CUDA context-mean difference was
{readback['maximum_cpu_cuda_mean_regret_error_bb']:.8g}bb, below the unchanged
0.0001bb tolerance. The readback also verified board separation, exact paired
initialization and batch generators, validation-only model selection, the frozen
selection before test labels, and both final gate outcomes. It recomputed
context means and gates; it checked partition row coverage but did not
independently recompute every reported tail percentile or subgroup mean.

Main work took {result['total_work_seconds']:.3f} seconds, including
{result['preparation_seconds']:.3f}s of earlier CPU preparation and
{result['gpu_stage_seconds']:.3f}s for the GPU-stage invocation. The latter includes
inventory, fitting, validation, final-test preparation and evaluation. Independent
readback took {readback['seconds']:.3f}s. The preceding GPU admission wait is not
included in those work times.

Baseline fits totaled {base_seconds:.3f}s; candidate fits totaled
{candidate_seconds:.3f}s, approximately 17.3% more. These sequential single runs
include validation/checkpoints and are not an isolated speed benchmark. Peak
CUDA allocation was {result['peak_cuda_allocated_bytes'] / 1e6:.2f}MB, with
{result['peak_cuda_reserved_bytes'] / 1e6:.2f}MB reserved. Main-run evidence used
{result['storage']['allocated_file_bytes'] / 1e6:.2f}MB allocated and
{result['storage']['logical_bytes'] / 1e6:.2f}MB logical storage, before this readback
and analysis. Production on56708 was not changed.

## Implication and recommended next work

Explicit hand-versus-board information is a promising component: it improved
the paired fresh-test average in both runs, whereas merely extending training
did not consistently help in the earlier budget comparison. It is still not
accurate enough to serve as a general continuation model. These diagnostic
weights cover only terminal Fold/Call and must not be installed as an all-street
strategy or described as improved preflop ranges.

The next proposed study should improve and balance training/validation coverage
of hand-versus-board relationships, with particular attention to ordinary
high-card and pair situations as well as rare board-made hands. Keep the two
representations paired and retain independent fresh boards and the original
absolute accuracy target. This is a proposal; no new study has been launched.
This completed final test must remain a test, not become the tuning set.

Only after resolving that accuracy gap should a separately registered comparison
test multiple decisions and realistic action-conditioned opponent ranges, using
the independently checked weighted terminal reference. Demonstrating better
preflop ranges still requires all-street policies, legal betting options,
stack/rake/position variation, and independent whole-game evaluation. This result
does not complete that broader goal.

Evidence: `{PREFIX}-result.json`, `{PREFIX}-readback-v1.json`,
`{PREFIX}-analysis-v1.json`, the unchanged registration and frozen selection.
No new experiment, GitHub push or deployment was performed for this analysis.
"""
findings_path = OUT / 'STACK-BOARD-RELATIVE-LEARNING-FINDINGS.md'
with findings_path.open('x', encoding='utf-8', newline='\n') as stream:
    stream.write(findings)
print(json.dumps(dict(analysis=str(analysis_path), analysis_sha256=sha(analysis_path),
    findings=str(findings_path), findings_sha256=sha(findings_path))))
