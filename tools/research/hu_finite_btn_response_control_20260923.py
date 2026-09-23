"""Compare finite-population sums with previously native-verified deal rows.

Uses the completed four-model fixture, never the running candidate. The 192
deals are a transport fixture, not a representative population or strength test.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import copy
import hashlib
import json
import math
import time
from collections import Counter
from pathlib import Path
import numpy as np
from finite_btn_response_v1 import integrate
from sampled_allin_protocol_v3 import AllinCache, canonical, BOARDS
from sampled_conditional_btn_response_v1 import rows
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_visible_hybrid_checkpoint_v1 import read_object, model_document
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from reboot_research_idle_v1 import idle

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'finite-btn-response-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def main():
    started = time.monotonic()
    def guard():
        assert time.monotonic() - started < 180 and idle()
    guard()
    assert not STORE.exists()
    source_path = OUT / 'bb-context-candidate.json'
    source = source_path.read_text(); context = json.loads(source)
    fixture_result_path = OUT / 'btn-stratified-conditional-control-v1-result.json'
    fixture_registration = OUT / 'btn-stratified-conditional-control-v1-registration.json'
    fixture = json.loads(fixture_result_path.read_text())
    assert fixture['passed'] and fixture['registration_sha256'] == sha(fixture_registration)
    for p, h in json.loads(fixture_registration.read_text())['inputs'].items():
        assert sha(p) == h, p
    fixture_store = Path('S:/GTOpen-research/btn-stratified-conditional-control-v1')
    cache_path = fixture_store / 'cache/cache.json'
    cache = AllinCache(cache_path, fixture['cache_result']['cache_sha256'])
    catalog_result_path = OUT / 'preflop-catalog-control-v1-result.json'
    catalog_result = json.loads(catalog_result_path.read_text())
    assert catalog_result['passed']
    catalog_path = Path(catalog_result['catalog_artifact'])
    assert sha(catalog_path) == catalog_result['catalog_sha256']
    catalog = json.loads(catalog_path.read_text())
    assert catalog['context_source'] == source
    review_path = OUT / 'sampled-visible-hybrid-allin-control-v1-independent-review.json'
    review = json.loads(review_path.read_text()); assert review['passed'] and review['completed_iterations'] == 4
    objects = Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    checkpoint = json.loads(read_object(objects, review['checkpoint']))
    paths = [Path(__file__), source_path, fixture_result_path, fixture_registration,
        cache_path, catalog_result_path, catalog_path, review_path, objects / review['checkpoint']['file'],
        *[objects / r['file'] for r in checkpoint['played_bank']],
        *[ROOT / 'tools/research' / n for n in ('finite_btn_response_v1.py', 'sampled_allin_protocol_v3.py',
            'sampled_conditional_btn_response_v1.py', 'sampled_visible_hybrid_cpu64_v1.py',
            'sampled_visible_hybrid_checkpoint_v1.py', 'reboot_research_idle_v1.py')]]
    inputs = {str(p): sha(p) for p in paths}
    for p, h in fixture['artifacts'].items():
        assert sha(p) == h, p
        inputs[p] = h
    registration = OUT / f'{PREFIX}-registration.json'
    save(registration, dict(inputs=inputs, maximum_seconds=180, played_models=4,
        scope='Finite-population arithmetic control on 192 previously native-verified fixture deals. No candidate inspection, full-population inference or strategic qualification.'))
    STORE.mkdir()
    error = None
    try:
        bank = VisibleHybridCpuBank64([model_document(objects, r, context_source=source) for r in checkpoint['played_bank']], context_source=source)
        ordered = catalog['native_observations']
        policies, support = bank.average(dict(context_source=source, observations=[r['observation'] for r in ordered]), guard=guard)
        assert np.array_equal(support, np.full(len(ordered), 4.))
        root = np.zeros((169, 4)); btn = np.full(169, np.nan)
        for r, p in zip(ordered, policies):
            if r['player'] == 0:
                root[r['hand_class']] = p
            else:
                assert p[2] == p[3] == 0
                btn[r['hand_class']] = p[1]
        deals, reference = [], []
        native_error = 0.
        for offset in range(0, 192, 16):
            folder = fixture_store / f'batch-{offset:04d}'
            batch = json.loads((folder / 'query-batch.json').read_text())
            profile = json.loads((folder / 'profiles.json').read_text())
            native = json.loads((folder / 'native.json').read_text())
            summary = json.loads((folder / 'summary.json').read_text())
            rr, err = rows(context, batch, profile, native, summary, cache)
            native_error = max(native_error, err); reference.extend(rr); deals.extend(batch['deals'])
        counts = Counter(canonical(d[:4]) for d in deals)
        population = dict(context_sha256=sha(source_path), player_roles_fixed=True,
            rows=[dict(private_cards=list(k), probability=n / len(deals)) for k, n in sorted(counts.items())])
        calculated = integrate(source, population, root, btn, cache.rows)
        # Independent ungrouped reconstruction from native-checked per-deal
        # values: math.fsum per class, no vectorized implementation reuse.
        maximum_error = 0.
        for c in range(169):
            rr = [r for r in reference if r['hand_class'] == c]
            f = math.fsum(r['jam_reach'] * r['fold_value'] / 192 for r in rr)
            call = math.fsum(r['jam_reach'] * r['call_value'] / 192 for r in rr)
            baseline = math.fsum(r['jam_reach'] * r['baseline_local_value'] / 192 for r in rr)
            jam = math.fsum(r['jam_reach'] / 192 for r in rr)
            expected = dict(entry_probability=len(rr) / 192, jam_probability=jam,
                fold_value_per_entry=f, call_value_per_entry=call, baseline_value_per_entry=baseline,
                best_value_per_entry=max(f, call), gain_per_entry=max(f, call) - baseline)
            actual = calculated['classes'][c]
            for k, value in expected.items():
                maximum_error = max(maximum_error, abs(actual[k] - value))
            assert actual['best_action'] == (-1 if jam == 0 else int(call > f))
        assert maximum_error < 1e-10
        # Role, ties and rake are tested with deliberately constructed complete
        # integer outcomes. These are synthetic controls, not equity claims.
        one = copy.deepcopy(population); one['rows'] = [dict(population['rows'][0], probability=1.)]
        key = tuple(one['rows'][0]['private_cards'])
        alljam = np.tile([0., 0., 0., 1.], (169, 1)); half = np.full(169, .5)
        node = context['nodes'][context['nodes'][0]['children'][3]]
        called = context['nodes'][node['children'][1]]
        synthetic_checks = 0
        for fraction, cap in ((0., 0.), (.05, 0.), (.05, 3.)):
            alternative = copy.deepcopy(context); alternative['rake_fraction'] = fraction; alternative['rake_cap'] = cap
            text = json.dumps(alternative); p = dict(one, context_sha256=hashlib.sha256(text.encode()).hexdigest())
            rake = min(called['pot'] * fraction, cap) if cap else called['pot'] * fraction
            for w, t, loss, equity in ((BOARDS, 0, 0, 0.), (0, BOARDS, 0, .5), (0, 0, BOARDS, 1.)):
                label = dict(private_cards=list(key), boards=BOARDS, wins=w, ties=t, losses=loss)
                result = integrate(text, p, alljam, half, {key: label})
                total_call = math.fsum(r['call_value_per_entry'] for r in result['classes'])
                assert abs(total_call - (-called['invested'][1] + (called['pot'] - rake) * equity)) < 1e-10
                synthetic_checks += 1
        nojam = np.tile([1., 0., 0., 0.], (169, 1))
        zero = integrate(source, population, nojam, btn, cache.rows)
        assert zero['jam_probability'] == 0 and zero['baseline_call_given_jam'] is None
        assert zero['best_call_given_jam'] is None and all(r['best_action'] == -1 for r in zero['classes'])
        assert all(v == 0 for v in zero['gains_per_entry'].values())
        negative_checks = 0
        def rejects(p=population, r=root, b=btn, labels=cache.rows):
            nonlocal negative_checks
            try:
                integrate(source, p, r, b, labels)
            except ValueError:
                negative_checks += 1
            else:
                raise AssertionError('Invalid finite population admitted')
        rejects(p=dict(population, context_sha256='wrong'))
        rejects(p=dict(population, player_roles_fixed=False))
        rejects(p=dict(population, rows=[]))
        rejects(p=dict(population, rows=population['rows'] + population['rows'][:1]))
        bad = copy.deepcopy(population); bad['rows'][0]['probability'] *= 2; rejects(p=bad)
        bad = copy.deepcopy(population); bad['rows'][0]['probability'] = float('nan'); rejects(p=bad)
        rejects(labels={})
        rejects(r=root * .5)
        bad = root.copy(); bad[0, 0] = float('nan'); rejects(r=bad)
        rejects(b=np.full(169, np.nan))
        bad = copy.deepcopy(cache.rows); bad[key]['boards'] -= 1; rejects(labels=bad)
        bad = copy.deepcopy(cache.rows); bad[key]['wins'] += 1; rejects(labels=bad)
        for p, h in inputs.items():
            assert sha(p) == h, p
        artifact = STORE / 'fixture-population.json'; save(artifact, population)
        result = dict(passed=True, registration_sha256=sha(registration), fixture_deals=192,
            canonical_fixture_pairs=len(counts), complete_played_models=4,
            maximum_native_cashflow_error_bb=native_error, maximum_independent_sum_error_bb=maximum_error,
            synthetic_role_tie_rake_checks=synthetic_checks, zero_reach_checked=True, negative_checks=negative_checks,
            fixture_artifact=str(artifact), fixture_sha256=sha(artifact), seconds=time.monotonic() - started,
            gpu_used=False, production_modified=False, accuracy_qualified=False,
            scope='Arithmetic validation only; the 192 class-balanced fixture deals are not the full population.')
        save(OUT / f'{PREFIX}-result.json', result); print(json.dumps(result))
    except Exception as exc:
        error = repr(exc)
        raise
    finally:
        save(OUT / f'{PREFIX}-status.json', dict(state='stopped' if error else 'complete', error=error, seconds=time.monotonic() - started))


if __name__ == '__main__':
    main()
