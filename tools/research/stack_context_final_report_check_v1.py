"""Synthetic-only report controls; never read interim scientific values."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import time
import numpy as np
import stack_context_final_report_v1 as report
from stack_context_matched_analysis_v1 import context_analysis, finish, DEPTHS, DEALS
from stack_context_independent_audit_v1 import audit_comparison


def main():
    name = 'stack-context-final-report-check-v1'
    output = report.OUT/(name+'-result.json')
    attempt = report.OUT/(name+'-attempt.json')
    preview = report.OUT/(name+'-synthetic-preview.png')
    table = report.OUT/(name+'-synthetic-preview.md')
    if any(path.exists() for path in (output, attempt, preview, table)):
        raise ValueError('Prior software-control evidence must be preserved')
    source = Path(report.__file__)
    inputs = {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in
              (Path(__file__), source, source.with_name('stack_context_matched_analysis_v1.py'),
               source.with_name('stack_context_independent_audit_v1.py'))}
    attempt.write_text(json.dumps(dict(inputs=inputs, synthetic_only=True)), encoding='utf-8')
    began = time.monotonic(); values_by_depth = {}; contexts = []
    for depth in DEPTHS:
        values = np.empty((DEALS, 2, 4, 2))
        common = np.linspace(-.002, .002, DEALS)*depth
        for seed in range(2):
            bb_gain = (.06+.005*seed)*depth+common/10
            btn_gain = (.05+.005*seed)*depth-common/10
            for pairing, (bb, btn) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
                values[:, seed, pairing, 0] = common+bb*bb_gain-btn*btn_gain
                values[:, seed, pairing, 1] = .5-values[:, seed, pairing, 0]
        values_by_depth[depth] = values
        contexts.append(context_analysis(values, depth=depth, dead_money=.5))
    comparison = finish(contexts)
    audit = audit_comparison(comparison, values_by_depth)
    report.validate_comparison(comparison, audit)
    text = report.markdown(comparison, synthetic=True)
    assert 'SYNTHETIC SOFTWARE CONTROL' in text
    assert text.count('| A |')+text.count('| B |') == 8+7*24
    assert all(f'### {depth}bb' in text for depth in DEPTHS)
    assert text.count('— held out from fitting') == 2
    assert '0.05, one final look' in text and 'a negative loss is a gain' in text
    assert 'not cash-game win rates or equilibrium/exploitability estimates' in text
    assert report.labels(0) == ('A', 'BB', 'baseline BTN')
    assert report.labels(7) == ('B', 'BTN', 'candidate BB')
    assert 'criterion is met' in report.verdict(comparison)
    changed = copy.deepcopy(contexts)
    changed[0]['contrasts'][0].update(mean=-.001, lower=-.1, upper=.1)
    adverse = finish(changed)
    assert 'negative mean gain' in report.verdict(adverse)
    changed = copy.deepcopy(contexts)
    for context in changed:
        context['contrasts'][0]['lower'] = -context['depth']
    uncertain = finish(changed)
    assert 'bounded intervals do not establish' in report.verdict(uncertain)
    rejected = 0
    def refuse(function):
        nonlocal rejected
        try:
            function()
        except ValueError:
            rejected += 1
        else:
            raise AssertionError('Invalid/interim presentation accepted')
    for field, value in (('registered_policy_improvement_criterion_met', False),
                         ('preflop_accuracy_qualified', True), ('production_promotion', True)):
        changed = copy.deepcopy(comparison); changed[field] = value
        refuse(lambda: report.validate_comparison(changed, audit))
    for field, value in (('passed', False), ('contrasts', 55), ('independent_primary_gate', False)):
        changed_audit = copy.deepcopy(audit); changed_audit[field] = value
        refuse(lambda: report.validate_comparison(comparison, changed_audit))
    for field, value in (('split', 'fit'), ('dead_money', 0)):
        changed = copy.deepcopy(comparison); changed['contexts'][2][field] = value
        refuse(lambda: report.validate_comparison(changed, audit))
    changed = copy.deepcopy(comparison); changed['contexts'][0]['contrasts'][0]['mean'] = float('nan')
    refuse(lambda: report.validate_comparison(changed, audit))
    changed = copy.deepcopy(comparison); changed['contexts'].pop()
    refuse(lambda: report.validate_comparison(changed, audit))
    # Isolated empty folder: no current scientific result is opened by this check.
    original_out = report.OUT
    with tempfile.TemporaryDirectory(prefix='gtopen-final-report-control-') as folder:
        report.OUT = Path(folder)
        try:
            refuse(report.final_evidence)
        finally:
            report.OUT = original_out
    report.figure(comparison, preview, synthetic=True)
    table.write_text(text, encoding='utf-8')
    assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest for path, digest in inputs.items())
    result = dict(complete=True, passed=True, inputs=inputs, seconds=time.monotonic()-began,
        synthetic_comparisons=56, synthetic_pooled_comparisons=8, rendered_data_rows=176,
        negative_controls=rejected, outputs={str(path):hashlib.sha256(path.read_bytes()).hexdigest()
                                            for path in (preview, table)},
        independent_synthetic_arithmetic=audit, live_result_values_read=False,
        new_scientific_deals=False, fitting=False, native_execution=False, gpu_used=False,
        production_modified=False, broad_goal_complete=False)
    output.write_text(json.dumps(result, allow_nan=False, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    print(json.dumps(dict(passed=True, seconds=result['seconds'], negative_controls=rejected,
                         preview=str(preview), table=str(table))))


if __name__ == '__main__':
    main()
