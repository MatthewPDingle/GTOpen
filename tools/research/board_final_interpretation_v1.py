"""Post-result descriptive review; no new samples, fitting, or policy selection."""
import datetime
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-final-interpretation-v1'


def main():
    inputs = {}

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def read(name):
        path = OUT / name
        inputs[str(path)] = sha(path)
        return json.loads(path.read_text())

    evidence = read('board-final-report-evidence.json')
    for kind in ('inputs', 'outputs'):
        for path, digest in evidence[kind].items():
            assert sha(Path(path)) == digest, path
    review = read('weighted-complete-board-root-study-v1-independent-review.json')
    result = read('weighted-complete-board-root-study-v1-result.json')
    queue = read('board-status-recovery-v2-result.json')
    assert review['passed'] and result['passed'] and result['complete'] and queue['passed']
    assert review['deals'] == result['deals'] == 65536
    assert result['test_seed'] == 9281101
    assert review['batches'] == len(result['routes']) == 2048
    assert review['source_result_sha256'] == inputs[str(OUT / 'weighted-complete-board-root-study-v1-result.json')]
    rows = read('board-final-all-hand-classes.json')
    assert len(rows) == 169 and {r['native_class_index'] for r in rows} == set(range(169))
    assert len({r['hand'] for r in rows}) == 169
    assert abs(math.fsum(r['entry_mass'] for r in rows) - 1) < 1e-12
    policies = ('first-old', 'first-new', 'replication-old', 'replication-new')
    for row in rows:
        assert row['entry_mass'] > 0 and set(row['policies']) == set(policies)
        for policy in row['policies'].values():
            assert set(policy) == {'fold', 'call', 'raise', 'jam'}
            assert all(math.isfinite(p) and 0 <= p <= 1 for p in policy.values())
            assert abs(math.fsum(policy.values()) - 1) < 1e-12
        for label, names in (('baseline_cross_seed', ('first-old', 'replication-old')),
                             ('candidate_cross_seed', ('first-new', 'replication-new'))):
            a, b = [row['policies'][name] for name in names]
            direct = .5 * math.fsum(abs(a[k] - b[k]) for k in a)
            assert abs(direct - row['total_variation'][label]) < 1e-12

    families = []
    for name, group in [('all', rows), ('pairs', [r for r in rows if len(r['hand']) == 2]),
                        ('suited', [r for r in rows if r['hand'].endswith('s')]),
                        ('offsuit', [r for r in rows if r['hand'].endswith('o')])]:
        mass = math.fsum(r['entry_mass'] for r in group)
        before, after = [math.fsum(r['entry_mass'] * r['total_variation'][key] for r in group) / mass
                         for key in ('baseline_cross_seed', 'candidate_cross_seed')]
        better = [r for r in group if r['total_variation']['candidate_cross_seed'] < r['total_variation']['baseline_cross_seed']]
        families.append(dict(family=name, classes=len(group), entry_mass=mass,
            control_tv=before, candidate_tv=after, difference_pp=100 * (after-before),
            improved_classes=len(better), improved_entry_mass=math.fsum(r['entry_mass'] for r in better),
            worsened_classes=sum(r['total_variation']['candidate_cross_seed'] > r['total_variation']['baseline_cross_seed'] for r in group),
            candidate_classes_above_half_tv=sum(r['total_variation']['candidate_cross_seed'] > .5 for r in group)))

    analysis_path = Path(result['store']) / 'analysis.json'
    assert sha(analysis_path) == result['analysis_sha256']
    inputs[str(analysis_path)] = sha(analysis_path)
    analysis = json.loads(analysis_path.read_text())
    contrasts = analysis['contrasts']
    assert len(contrasts) == 8
    positive = sum(c['lower'] > 0 for c in contrasts)
    negative = sum(c['upper'] < 0 for c in contrasts)
    assert sum(c['mean'] > 0 for c in contrasts) == 7 and sum(c['mean'] < 0 for c in contrasts) == 1
    costs = read('board-final-costs.json')
    failed = read('board-evaluation-resource-wrapper-v1-initial-failure.json')
    summary = families[0]
    family_table = '\n'.join(f"| {r['family']} | {100*r['control_tv']:.2f}% | {100*r['candidate_tv']:.2f}% | {r['difference_pp']:+.2f} pp |"
                             for r in families[1:])
    by_hand = {r['hand']: r for r in rows}
    tt = [100 * by_hand['TT']['policies'][p]['jam'] for p in ('first-new', 'replication-new')]
    eights = [100 * by_hand['88']['policies'][p]['call'] for p in ('first-new', 'replication-new')]
    note = f'''# Board-root comparison: interpretation and next decision

The completed experiment shows a useful reduction in run-to-run range disagreement,
but does not yet establish stronger or sufficiently reliable preflop play. Keep
this method as a research candidate; do not promote it to the production model.

## What the full result supports

Both candidates completed 78 updates. All 65,536 registered evaluation deals and
all 2,048 batches passed readback across both checkpoint attempts. The comparison
and verification used the original registered sample and stopping rule.

Entry-weighted disagreement between the two runs fell from
{100*summary['control_tv']:.2f}% to {100*summary['candidate_tv']:.2f}%:
{abs(summary['difference_pp']):.2f} percentage points, or about
{100*(1-summary['candidate_tv']/summary['control_tv']):.1f}% less disagreement.
This describes these two runs. It is not an accuracy percentage, EV loss,
confidence interval over training seeds, or a general convergence guarantee.

The registered eight payoff intervals establish {positive} gains and {negative}
losses; {8-positive-negative} remain inconclusive. Seven point estimates are
positive and one negative. They share evaluation deals and opponents, so their
signs must not be treated as eight independent replications or a new success test.
The full intervals, including the unfavorable comparison, remain in
[BOARD-FINAL-FINDINGS.md](BOARD-FINAL-FINDINGS.md).

## Descriptive hand-level review

These family summaries were added after seeing the completed results. They are
diagnostics, not new confirmatory tests. All 169 classes remain available in the
bound [complete table](board-final-all-hand-classes.json); families and hands
are correlated through shared training and boards.

| Family | Control disagreement | Candidate disagreement | Change |
| --- | ---: | ---: | ---: |
{family_table}

Disagreement decreased for {summary['improved_classes']}/169 classes, representing
{100*summary['improved_entry_mass']:.1f}% of incoming hand mass. It did not improve
everywhere: {summary['worsened_classes']} classes worsened, and
{summary['candidate_classes_above_half_tv']} still differ by more than 50 percentage
points of total variation between candidate runs.

For concrete examples of the remaining disagreement, TT jams
{tt[0]:.2f}% versus {tt[1]:.2f}%, while 88 calls {eights[0]:.2f}% versus
{eights[1]:.2f}%. These were selected as diagnostic examples after reviewing the
full table, not as separate statistical evidence. Root action-value evidence is
needed to distinguish costly errors from nearly tied actions; appearance alone
cannot settle that question.

## Runtime and verification

Recorded candidate update time was about 58 minutes per arm, similar to the
historical controls. Additional board work overlapped other work. This was not a
controlled speed comparison, and overlapping stage times must not be summed.

The successful resumed scientific evaluation invocation took
{result['seconds_this_invocation']/60:.2f} minutes. The earlier failed wrapper
attempt took {failed['seconds']/60:.2f} minutes and is not included in that number.
The recovery queue also includes waiting and admission overhead; its elapsed time
overlaps the successful invocation and must not be added to it. Full evaluation
readback took {review['seconds']/60:.2f} minutes; complete training readback had
taken {costs['training_audit_seconds']/60:.2f} minutes. These are research workflow
timings, not production solver latency.

Visual review of the generated plot confirmed all eight labeled comparisons,
readable axes and units, and complete error bars crossing zero. The {len(evidence['inputs'])} report
input hashes and four generated artifact hashes were checked. The readback shares
the poker engine and policy representation; this does not independently certify
the poker rules or equilibrium.

## Next research step

First examine the already saved root policies and regrets through all 78 updates
for both candidates, against the existing control trajectories. Report every
class and every transition, with fixed first/middle/last 26-generation windows.
Reproduce the evaluated average exactly and exclude unplayed generation 78 from
it. Generation 78 may appear only as an explicitly labeled movement diagnostic.
This requires no new training deals and does not extend the completed experiment.

The purpose is to distinguish ranges still changing substantially from ranges
that settled early into different answers. Then design a fresh fixed-policy
action-value diagnostic for the complete averaged policies, covering all 169
classes and separating exact preflop terms from postflop continuation estimates.
Do not substitute generation 77 for the evaluated average, smooth charts by hand,
or extend this finished payoff sample because an interval is close to zero.

Only after that evidence should we choose more boards, longer training, or a
change to continuation learning. A separate replication will be needed before
claiming a reliable gain across random seeds. Other positions, stack depths,
bet menus, multiway play, and matched GTO Wizard comparisons remain outstanding.
Production has not been changed.
'''
    md = OUT / 'BOARD-FINAL-INTERPRETATION.md'
    destination = OUT / f'{PREFIX}.json'
    assert not md.exists() and not destination.exists(), 'Preserve completed interpretation'
    with md.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(note)
    inputs[str(Path(__file__))] = sha(Path(__file__))
    payload = dict(format=1, created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        inputs=inputs, report_inputs_verified=len(evidence['inputs']), report_outputs_verified=evidence['outputs'],
        family_diagnostics_posthoc=True, families=families,
        registered_comparisons=dict(positive=positive,negative=negative,inconclusive=8-positive-negative),
        manual_visual_review=dict(completed=True,plot_sha256=evidence['outputs'][str(OUT/'board-final-gains.png')],
            all_eight_comparisons_visible=True,labels_legible=True,intervals_not_clipped=True),
        interpretation_complete=True, accuracy_qualified=False, promoted=False, production_modified=False,
        new_deals=0, training_changed=False, interpretation_sha256=sha(md),
        next_action='Complete saved-history trajectory diagnostic before choosing further training.')
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(payload, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(interpretation_complete=True,all_classes_checked=len(rows),
        positive=positive,negative=negative,inconclusive=8-positive-negative,
        interpretation=str(md),evidence=str(destination),production_modified=False)))


if __name__ == '__main__':
    main()
