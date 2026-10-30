"""CPU-only admission tests; synthetic success is never a scientific result."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import ast
import copy
import hashlib
import json
from pathlib import Path
import time
from unittest.mock import patch
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read, load_complete_cache
from hu_paired_continuation_support_20260925 import LOCK
from reboot_research_idle_v1 import idle
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader
import composite_showdown_bank_v1 as bank
import hu_showdown_composite_evaluation_v1_20260927 as runner
import hu_showdown_composite_evaluation_review_v1_20260927 as review


def synthetic_admission_tests():
    # In-memory metadata only. No real result, audit, object, or registration
    # is created or modified, and no inference or sampling is invoked.
    docs = {}
    op = OUT/'showdown-matched-training-v1-registration.json'
    cr, cp, cs = [OUT/f'showdown-fourth-arm-continuation-v1-{s}.json'
                  for s in ('registration', 'result', 'status')]
    original_store = ROOT/'research/synthetic-not-written/original'
    continuation_store = ROOT/'research/synthetic-not-written/continuation'
    def put(path, value):
        docs[str(path)] = value
    def fake_read(path):
        return copy.deepcopy(docs[str(path)])
    def fake_sha(path):
        if str(path) == str(op):
            return bank.ORIGINAL_SHA
        return hashlib.sha256(json.dumps(docs[str(path)], sort_keys=True).encode()).hexdigest()
    arms = [dict(name=n, treatment='corrected' if n.endswith('corrected') else 'baseline',
                 config=dict(synthetic=True, max_iterations=78, arm=n)) for n in bank.TRAINING]
    put(op, dict(store=str(original_store), arms=arms))
    put(OUT/'showdown-matched-training-v1-status.json', dict(state='failed'))
    finals = []
    for at, arm in enumerate(arms):
        case = (original_store if at < 3 else continuation_store)/arm['name']
        final = dict(name=arm['name'], config=arm['config'], store=str(case),
            completed_iterations=78, final_restore_verified=True,
            played_bank=[dict(generation=n, file=f'synthetic-model-{n}') for n in range(78)],
            final_checkpoint=dict(file='synthetic-checkpoint'))
        finals.append(final)
        if at < 3:
            put(case/'result.json', final)
    put(cr, dict(store=str(continuation_store), arm=arms[-1]['name'], config=arms[-1]['config']))
    final = finals[-1]
    final.update(passed=True, terminal=True, registration_sha256=fake_sha(cr),
        original_registration_sha256=fake_sha(op), training_deals=39936,
        original_store=str(original_store/arms[-1]['name']),
        predecessor=dict(directory=str(original_store/arms[-1]['name']/'objects'), retention_sha256=None))
    put(cp, final); put(Path(final['store'])/'result.json', copy.deepcopy(final))
    put(cs, dict(state='complete', exit_code=0))
    audit_paths = []
    for at, arm in enumerate(arms):
        prefix = (bank.COMPOSITE_AUDIT if at == 3 else
                  f"showdown-training-readback-v2-{arm['name']}-0078")
        ar, ap = [OUT/f'{prefix}-{s}.json' for s in ('registration', 'result')]
        put(ar, dict(arm=arm['name'], completed_iterations=78))
        audit = dict(passed=True, complete_arm=True, completed_updates=78, arm=arm['name'],
            bb_roots_reconstructed=39936, source_registration_sha256=fake_sha(op),
            readback_registration_sha256=fake_sha(ar))
        if at == 3:
            audit.update(composite_completed_arm=True, continuation_registration_sha256=fake_sha(cr),
                continuation_result_sha256=fake_sha(cp))
        put(ap, audit); audit_paths.append((ar, ap))
    rejected = []
    with patch.object(bank, 'read', fake_read), patch.object(bank, 'sha', fake_sha), \
         patch.object(bank.psutil, 'process_iter', return_value=[]), \
         patch.object(review, 'read', fake_read), patch.object(review, 'sha', fake_sha), \
         patch.object(Path, 'exists', return_value=False):
        paths = bank.training_gates()
        bindings = {str(p): fake_sha(p) for p in paths}
        identities = []
        for at, (arm, final, (ar, ap)) in enumerate(zip(arms, finals, audit_paths)):
            identity = dict(arm=arm['name'], treatment=arm['treatment'], purpose='evaluation',
                evaluation_qualified=True, accuracy_qualified=False, production_modified=False,
                admission='three-original-plus-independently-audited-continuation-v1',
                complete_study_bindings=bindings, original_trial_status='failed-preserved',
                registration_sha256=fake_sha(op), audit_sha256=fake_sha(ap),
                readback_registration_sha256=fake_sha(ar), checkpoint=final['final_checkpoint'],
                model_references=final['played_bank'], objects_retention_sha256=None,
                played_generations=list(range(78)), excluded_generation=78, weights=[list(range(1,79))]*2,
                inference_type='showdown-controlled-v8' if arm['treatment']=='corrected' else 'baseline-v7-inner-v6')
            if at == 3:
                identity.update(continuation_result_sha256=fake_sha(cp), predecessor=final['predecessor'])
            else:
                identity['trial_result_sha256'] = None
                legacy = dict(identity, purpose='implementation-control', evaluation_qualified=False)
                identity['original_readback_identity'] = legacy
            identities.append(identity)
        registration = dict(inputs=bindings)
        assert review.verify_composite_identities(identities, registration, lambda: None) == bindings
        def reject(name, action):
            try:
                action()
            except (AssertionError, ValueError, KeyError):
                rejected.append(name)
            else:
                raise AssertionError('Invalid evidence admitted: '+name)
        for name, path, key, value in (
            ('running-continuation', cs, 'state', 'running'),
            ('missing-full-audit', audit_paths[-1][1], 'passed', False),
            ('stale-audit-binding', audit_paths[-1][1], 'continuation_result_sha256', 'wrong'),
            ('partial-fourth-arm', cp, 'completed_iterations', 77),
            ('partial-original-arm', original_store/arms[0]['name']/'result.json', 'completed_iterations', 77),
            ('changed-original-audit-sample-count', audit_paths[0][1], 'bb_roots_reconstructed', 39424),
            ('wrong-continuation-store', cr, 'store', str(ROOT/'research/wrong')),
        ):
            saved = docs[str(path)][key]; docs[str(path)][key] = value
            reject(name, bank.training_gates)
            docs[str(path)][key] = saved
        for name, at, key, value in (
            ('duplicate-played-generation', 3, 'played_generations', [0]*78),
            ('included-unplayed-generation', 3, 'excluded_generation', 79),
            ('wrong-treatment', 3, 'treatment', 'baseline'),
            ('wrong-policy-type', 1, 'inference_type', 'baseline-v7-inner-v6'),
            ('wrong-average-weights', 2, 'weights', [[1]*78]*2),
            ('stale-composite-bindings', 0, 'complete_study_bindings', {}),
            ('wrong-model-history', 0, 'model_references', []),
            ('accuracy-claim', 0, 'accuracy_qualified', True),
        ):
            altered = copy.deepcopy(identities); altered[at][key] = value
            reject(name, lambda: review.verify_composite_identities(altered, registration, lambda: None))
        assert bank.training_gates() == paths
    return rejected


def function_source(path, name):
    source = path.read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)


def main():
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 240 and idle()
    guard()
    prefix = 'composite-showdown-evaluation-preflight-v1'
    rp, pp = [OUT/f'{prefix}-{s}.json' for s in ('registration', 'result')]
    assert not rp.exists() and not pp.exists()
    status = read(OUT/'showdown-fourth-arm-continuation-v1-status.json')
    process = psutil.Process(status['worker_pid'])
    assert process.is_running() and '--worker' in process.cmdline()
    assert any(Path(a).name == 'hu_showdown_fourth_arm_continuation_20260927.py' for a in process.cmdline())
    assert status['state'] == 'running'
    lock_bytes = LOCK.read_bytes()
    scripts = [ROOT/'tools/research'/n for n in (
        'composite_showdown_bank_v1.py', 'hu_showdown_composite_evaluation_v1_20260927.py',
        'hu_showdown_composite_evaluation_review_v1_20260927.py',
        'hu_showdown_complete_evaluation_v2_20260926.py',
        'hu_showdown_complete_evaluation_review_v2_20260926.py')]
    source_result = OUT/'columnar-evaluation-archive-control-v1-result.json'
    control = read(source_result); assert control['passed']
    inputs = {str(p): sha(p) for p in [*scripts, Path(__file__).resolve(), source_result,
        OUT/'SHOWDOWN-COMPOSITE-EVALUATION-ROUTING.md']}
    save(rp, dict(inputs=inputs, maximum_seconds=240, gpu_used=False,
        scope='CPU-only synthetic admission and existing-evidence transport checks; no full-bank or strength qualification.'))
    try:
        for path in scripts:
            compile(path.read_text(), str(path), 'exec')
        assert function_source(scripts[1], 'worker') == function_source(scripts[3], 'worker')
        for name in ('verify_batch', 'verify_stability'):
            assert function_source(scripts[2], name) == function_source(scripts[4], name)
        old_science = scripts[4].read_text().split('    try:\n        source=')[1]
        new_science = scripts[2].read_text().split('    try:\n        source=')[1]
        assert old_science == new_science
        refused = []
        for mode in ('control', 'study'):
            expected = runner.PREFIXES[mode]
            assert not (OUT/f'{expected}-registration.json').exists()
            assert not (Path('S:/GTOpen-research')/expected).exists()
            try:
                runner.run(mode)
            except AssertionError:
                refused.append(mode)
            else:
                raise AssertionError('Evaluation bypassed live training lock')
            assert not (OUT/f'{expected}-registration.json').exists()
            assert not (Path('S:/GTOpen-research')/expected).exists()
        try:
            bank.training_gates()
        except ValueError as exc:
            assert 'remains active' in str(exc)
            refused.append('bank-admission')
        else:
            raise AssertionError('Bank admitted live training')
        synthetic = synthetic_admission_tests()
        store = Path(control['store']); name = 'test-000000'
        reader = ColumnarEvaluationReader(store, {name: control['manifest_sha256']}, guard=guard)
        batch = reader.read_json(store/name/'query-batch.json')
        source = reader.read_json(store/name/'queries.json')['context_source']
        values, observations, digest = review.verify_batch(reader, store/name, batch, source, load_complete_cache())
        assert len(values) == control['scalar_reader_deals'] == 32
        assert observations == control['scalar_reader_observations'] == 14528
        assert digest == control['original_summary_sha256']
        assert LOCK.read_bytes() == lock_bytes and process.is_running()
        for p, h in inputs.items():
            assert sha(p) == h, p
        result = dict(passed=True, registration_sha256=sha(rp), compiled_sources=len(scripts),
            unchanged_scientific_worker=True, unchanged_scalar_review=True,
            refused_while_training=refused, synthetic_invalid_cases_rejected=synthetic,
            synthetic_valid_metadata_checked=True, training_worker_pid=process.pid,
            original_lock_preserved=True, scalar_reader_deals=len(values), scalar_reader_observations=observations,
            original_summary_sha256=digest, seconds=time.monotonic()-started, gpu_used=False,
            fresh_deals_sampled=0, production_modified=False, full_bank_qualified=False, accuracy_qualified=False)
        save(pp, result); print(json.dumps(result))
    except BaseException as exc:
        save(pp, dict(passed=False, error=repr(exc), registration_sha256=sha(rp), seconds=time.monotonic()-started))
        raise


if __name__ == '__main__':
    main()
