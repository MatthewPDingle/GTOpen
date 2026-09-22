"""End-to-end fresh-deal evaluation using an explicitly unqualified tiny bank."""
import json
import os
from pathlib import Path
import shutil
import time

import numpy as np
import psutil

from loopback_research_validation import idle
from sampled_physical_checkpoint_v1 import read_object
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, run

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-root-evaluation-control-v1'


def main():
    assert idle()
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    prerequisite = OUT / 'sampled-physical-pilot-controller-v1-review.json'
    prior_result = OUT / 'sampled-physical-pilot-controller-v1-result.json'
    review = json.loads(prerequisite.read_text())
    assert review['passed'] and review['result_sha256'] == sha(prior_result)
    previous = json.loads(prior_result.read_text())
    objects = Path(previous['store']) / 'checkpoint-objects'
    reference = previous['checkpoint']
    checkpoint = json.loads(read_object(objects, reference))
    assert checkpoint['completed_iterations'] == 2
    folder = Path('S:/GTOpen-research') / PREFIX
    assert not folder.exists()
    context = OUT / 'bb-context-candidate.json'
    dependencies = [Path(__file__), prerequisite, prior_result, context, objects / reference['file']]
    dependencies += [objects / r['file'] for r in [*checkpoint['played_bank'], checkpoint['next_model']]]
    dependencies += [ROOT / 'tools/research' / name for name in (
        'sampled_physical_root_evaluation_v1.py', 'sampled_root_deviation_v1.py',
        'sampled_evaluation_intervals_v1.py', 'sampled_physical_checkpoint_v1.py',
        'sampled_physical_deals_v1.py', 'sampled_physical_reservoir_v1.py',
        'sampled_physical_bank_v1.py', 'sampled_batch_model_v1.py',
        'sampled_batch_protocol_v2.py', 'storage_strategic_common_prior_20260920.py',
        'storage_phase_run_20260920.py', 'loopback_research_validation.py',
        'paged_continuation_validation.py')]
    dependencies += [ROOT / 'target/release/examples' / name for name in (
        'hu_sampled_bank_bridge.exe', 'hu_sampled_profile_evaluation.exe')]
    dependencies += [ROOT / 'crates/solver/examples' / name for name in (
        'hu_sampled_bank_bridge.rs', 'hu_sampled_profile_evaluation.rs',
        'research_sampled/state.rs', 'research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs', 'research_sampled/policy_bank_v1.rs',
        'research_sampled/batch_queries_v1.rs')]
    reg = dict(id=PREFIX, inputs={str(p): sha(p) for p in dependencies},
               context=str(context), objects=str(objects), checkpoint=reference,
               config=dict(training_deals=32, evaluation_deals=32, batch_size=8,
                           minimum_training_deals=2, train_seed=39101, test_seed=39102),
               maximum_seconds=180, host_reserve_bytes=20_000_000_000,
               disk_reserve_bytes=40_000_000_000, no_gpu=True,
               scope='Pipeline control only: tiny two-generation CPU-trained bank, 32 fresh responder-training deals and 32 fresh evaluation deals. No poker-strength or convergence qualification.',
               production_modified=False)
    regpath = OUT / (PREFIX + '-registration.json')
    save(regpath, reg)
    started = time.monotonic()
    last_check = 0.

    def guard():
        nonlocal last_check
        now = time.monotonic()
        if now - last_check >= 2:
            assert now - started < reg['maximum_seconds'] and idle()
            assert psutil.virtual_memory().available >= reg['host_reserve_bytes']
            assert shutil.disk_usage(folder.parent).free >= reg['disk_reserve_bytes']
            last_check = now

    result = run(reg, folder, guard)
    assert result['terminal'] and result['completed_training_deals'] == 32 and result['completed_evaluation_deals'] == 32
    assert result['played_generations'] == [0, 1] and result['excluded_unused_generation'] == 2
    assert result['applied_response_deals'] + result['fallback_deals'] == 32
    # Independently reconstruct frozen action choices and test differences from
    # retained per-deal native payoff summaries rather than calling learn/differences.
    training = []; testing = []; max_mixture = 0.; max_cashflow = 0.
    for name, h in result['batch_summary_hashes'].items():
        batch_folder = folder / name
        assert sha(batch_folder / 'summary.json') == h
        row = json.loads((batch_folder / 'summary.json').read_text())
        for name2, digest2 in row['artifacts'].items(): assert sha(batch_folder / name2) == digest2
        (training if '-train-' in name else testing).append((batch_folder, row))
        max_mixture = max(max_mixture, row['maximum_root_mixture_error'])
        max_cashflow = max(max_cashflow, row['maximum_forward_cashflow_error'])
    counts = np.zeros(169, dtype=int); totals = np.zeros((169, 4))
    for _, row in training:
        for c, values in zip(row['classes'], row['action_values']):
            counts[c] += 1; totals[c] += values
    choices = np.where(counts >= 2, totals.argmax(axis=1), -1)
    response_path = folder / 'response.json'
    response = json.loads(response_path.read_text())
    assert np.array_equal(choices, response['actions']) and np.array_equal(counts, response['training_counts'])
    differences = []
    for batch_folder, row in testing:
        paired = json.loads((batch_folder / 'paired.json').read_text())
        assert paired['response_sha256'] == sha(response_path)
        expected = []
        for c, values, baseline in zip(row['classes'], row['action_values'], row['baseline_values']):
            chosen = choices[c]
            expected.append([values[chosen] - baseline if chosen >= 0 else 0., *[v - baseline for v in values]])
        assert np.array_equal(expected, paired['differences'])
        differences.extend(expected)
    differences = np.asarray(differences)
    for i, name in enumerate(('trained-response', 'always-fold', 'always-call', 'always-raise', 'always-jam')):
        interval = result['intervals'][name]
        assert abs(differences[:, i].mean() - interval['mean']) < 1e-12
        assert abs(differences[:, i].var(ddof=1) - interval['sample_variance']) < 1e-10
        assert interval['count'] == 32 and interval['lower'] <= interval['mean'] <= interval['upper']
    for path, digest2 in reg['inputs'].items(): assert sha(path) == digest2, path
    guard()
    final = dict(passed=True, inputs_verified=len(reg['inputs']), registration_sha256=sha(regpath),
                 result_sha256=sha(folder / 'result.json'), response_sha256=sha(response_path),
                 fresh_training_deals=32, fresh_evaluation_deals=32,
                 applied_response_deals=result['applied_response_deals'], fallback_deals=result['fallback_deals'],
                 maximum_root_mixture_error=max_mixture, maximum_forward_cashflow_error=max_cashflow,
                 independently_reconstructed_paired_values=160,
                 seconds=time.monotonic() - started, store=str(folder), no_gpu=True,
                 physical_poker_convergence_qualified=False, production_modified=False,
                 scope=reg['scope'])
    save(OUT / (PREFIX + '-review.json'), final)
    save(OUT / (PREFIX + '-result.json'), result)
    save(OUT / (PREFIX + '-response.json'), response)
    print(json.dumps(final, indent=2))


if __name__ == '__main__':
    main()
