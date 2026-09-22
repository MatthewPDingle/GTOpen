"""Post-audit descriptive comparison of dense and direct-preflop policies.

Does not read incomplete evaluations, choose checkpoints, or modify policies.
Fresh but different test streams do not provide a paired improvement estimate.
"""
import json
from pathlib import Path
import time

from hu_sampled_physical_dense_comparison_20260922 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save


def main():
    started = time.monotonic()
    dense = read('sampled-physical-dense-evaluation-v1')
    hybrid = read('sampled-physical-hybrid-evaluation-v2')
    assert dense['test_seed'] != hybrid['test_seed']
    registrations = [json.loads((OUT/(candidate['prefix']+'-registration.json')).read_text())
                     for candidate in (dense, hybrid)]
    assert sha(registrations[0]['context']) == sha(registrations[1]['context'])
    training = [json.loads(Path(reg['training_registration']).read_text())
                for reg in registrations]
    assert training[0]['config'] == training[1]['config']
    assert [reg['selected_iterations'] for reg in registrations] == [78, 78]
    configs = [{k: v for k, v in reg['config'].items() if k not in ('train_seed', 'test_seed')}
               for reg in registrations]
    assert configs[0] == configs[1]
    changes = []
    for old, new in zip(dense['classes'], hybrid['classes']):
        assert old['hand_class'] == new['hand_class']
        assert old['hand'] == new['hand']
        changes.append(dict(
            hand=old['hand'], hand_class=old['hand_class'],
            probability_changes=[b-a for a, b in zip(
                old['baseline_probabilities'], new['baseline_probabilities'])],
            dense_call_minus_fold_bb=old['call_minus_fold_bb'],
            hybrid_call_minus_fold_bb=new['call_minus_fold_bb'],
            dense_test_deals=old['test_deals'], hybrid_test_deals=new['test_deals'],
        ))
    assert len(changes) == 169
    scope = (
        'Descriptive comparison after both independent evaluation audits. '
        'Different test streams and different opponent/continuation policies; '
        'the hybrid uses the audited float64 numerical repair while the dense '
        'baseline used float32 inference. '
        'no paired improvement interval or cross-trial significance claim. '
        'Action mixes are deal-weighted on each complete test stream. '
        'All 169 classes are retained; per-hand values are diagnostics, not '
        'training targets or proposed hand edits. These root-only deviations '
        'do not establish full equilibrium, Wizard parity, or transfer to UTG/LJ. '
        'Neither production nor the preview is modified.'
    )
    result = dict(
        source_sha256=sha(Path(__file__)),
        reader_sha256=sha(Path(__file__).with_name(
            'hu_sampled_physical_dense_comparison_20260922.py')),
        matched_context_sha256=sha(registrations[0]['context']),
        matched_training_config=training[0]['config'],
        dense=dense, hybrid=hybrid, class_changes=changes,
        seconds=time.monotonic()-started, production_modified=False, scope=scope,
    )
    save(OUT/'sampled-physical-hybrid-comparison-v1-result.json', result)
    compact = {
        name: {k: v for k, v in candidate.items() if k not in ('classes', 'evidence')}
        for name, candidate in [('dense', dense), ('hybrid', hybrid)]
    }
    print(json.dumps(dict(candidates=compact, scope=scope)))


if __name__ == '__main__':
    main()
