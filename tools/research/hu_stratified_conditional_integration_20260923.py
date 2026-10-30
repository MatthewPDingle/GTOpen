"""CPU integration of fixed class coverage, visible bank and conditional payoffs.

Uses the completed four-update control model, never the active full trial.
This is transport/accounting validation, not a strength evaluation.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_stratified_response_deals_v1 import sample
from sampled_conditional_cache_builder_v1 import build
from sampled_conditional_root_evaluation_v1 import batch_values
from sampled_visible_hybrid_checkpoint_v1 import read_object, model_document, verify_bank
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_allin_protocol_v3 import AllinCache
from sampled_root_deviation_v1 import learn, differences

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'stratified-conditional-integration-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def main():
    started = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert now-started < 900 and idle()
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free >= 40_000_000_000
            last = now
    guard(); assert not STORE.exists()
    review_path = OUT/'sampled-visible-hybrid-allin-control-v1-independent-review.json'
    review = json.loads(review_path.read_text())
    assert review['passed'] and review['terminal_complete'] and review['completed_iterations'] == 4
    objects = Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    context = OUT/'bb-context-candidate.json'; source = context.read_text()
    checkpoint = json.loads(read_object(objects, review['checkpoint']))
    verify_bank(objects, 4, checkpoint['played_bank'], checkpoint['next_model'], context_source=source)
    cache_review = OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    base = AllinCache.from_review(cache_review)
    paths = [Path(__file__), review_path, context, cache_review, objects/review['checkpoint']['file'],
        *[objects/r['file'] for r in checkpoint['played_bank']],
        *[ROOT/'tools/research'/n for n in ('sampled_stratified_response_deals_v1.py',
            'sampled_conditional_cache_builder_v1.py', 'sampled_conditional_root_evaluation_v1.py',
            'sampled_visible_hybrid_cpu64_v1.py', 'sampled_root_deviation_v1.py')],
        *[ROOT/'target/release/examples'/n for n in ('hu_sampled_bank_bridge.exe',
            'hu_sampled_profile_allin_evaluation_v1.exe', 'hu_allin_board_reference.exe')]]
    reg = dict(inputs={str(p):sha(p) for p in paths}, seed=193925, deals_per_class=2,
        complete_deals=338, maximum_new_keys=338, maximum_seconds=900,
        checkpoint=review['checkpoint'], played_generations=list(range(4)),
        scope='CPU-only integration of BB-stratified training fixtures and conditional payoff evaluation with the completed four-update visible control bank. No current-candidate inspection, GPU work, new confidence claim, or strength result.', production_modified=False)
    rp = OUT/f'{PREFIX}-registration.json'; save(rp, reg); STORE.mkdir()
    error = None
    try:
        sampled = sample(source, seed=reg['seed'], per_class=2, classes=list(range(169)), guard=guard)
        save(STORE/'deals.json', sampled)
        cache, cache_result = build(sampled['deals'], base, STORE/'cache', maximum_new_keys=338, guard=guard)
        bank = VisibleHybridCpuBank64([model_document(objects,r,context_source=source) for r in checkpoint['played_bank']], context_source=source)
        class VisibleOnly:
            calls = 0
            def average(self, q, *, guard):
                b = json.loads(q['batch_source'])
                assert b['format'] == 2 and not any(k.startswith('allin_') or k == 'terminal_estimator' for k in b)
                self.calls += 1
                return bank.average(q, guard=guard)
        visible = VisibleOnly(); classes = []; values = []; baselines = []; summaries = []
        mixture_error = forward_error = 0.
        for offset in range(0, 338, 16):
            guard(); folder = STORE/f'batch-{offset:04d}'
            batch = dict(format=2, batch_id=f'{PREFIX}-{offset}', seed=0, query_limit=100000,
                deals=sampled['deals'][offset:offset+16])
            result = batch_values(context, batch, folder, guard, visible, cache)
            assert result['classes'] == sampled['hand_classes'][offset:offset+16]
            classes.extend(result['classes']); values.extend(result['action_values']); baselines.extend(result['baseline_values'])
            mixture_error = max(mixture_error, result['maximum_root_mixture_error'])
            forward_error = max(forward_error, result['maximum_forward_cashflow_error'])
            summaries.append(dict(path=str(folder/'summary.json'), sha256=sha(folder/'summary.json')))
        assert classes == list(range(169))*2 and visible.calls == 22
        # One observation/class is intentionally only a transport fixture. It
        # is not the planned strategic response-training support requirement.
        response = learn([f'first-{c}' for c in range(169)], classes[:169], values[:169], baselines[:169], minimum_training_deals=1)
        delta = differences(response, [f'second-{c}' for c in range(169)], classes[169:], values[169:], baselines[169:])
        expected = np.array([values[169+c][response['actions'][c]]-baselines[169+c] for c in range(169)])
        assert np.array_equal(delta, expected)
        for p,h in reg['inputs'].items(): assert sha(p) == h,p
        save(OUT/f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
            complete_deals=338, classes=169, played_models=4, unlabelled_policy_calls=visible.calls,
            summaries=summaries, maximum_root_mixture_error=mixture_error,
            maximum_forward_cashflow_error=forward_error, response_transport_exact=True,
            cache_result=cache_result, sample_artifact_sha256=sha(STORE/'deals.json'),
            seconds=time.monotonic()-started, scope=reg['scope'], production_modified=False,
            accuracy_qualified=False))
        print(json.dumps(dict(passed=True, complete_deals=338, maximum_root_mixture_error=mixture_error,
            maximum_forward_cashflow_error=forward_error, seconds=time.monotonic()-started)))
    except Exception as exc:
        error=repr(exc); raise
    finally:
        save(OUT/f'{PREFIX}-status.json', dict(state='stopped' if error else 'complete', error=error,
            seconds=time.monotonic()-started, production_modified=False))


if __name__ == '__main__': main()
