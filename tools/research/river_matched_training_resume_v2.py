"""Explicit execution amendment: guarded waits, same registered pilot science."""
import ast
import json
from pathlib import Path
import sys
import time
import uuid
import psutil
import river_matched_training_pilot_v1 as pilot
from board_training_pipeline_wait_v1 import update as baseline_update
from river_training_pipeline_wait_v1 import update as candidate_update

AMEND = pilot.OUT/'river-matched-training-pilot-v1-execution-v2-registration.json'
PLAN = pilot.OUT/'RIVER-PILOT-WAIT-RECOVERY.md'
CONTROL = pilot.OUT/'guarded-training-future-control-v1-result.json'
ORIGINAL_SPEC = pilot.specification
ORIGINAL_PUBLISH = pilot.atomic_json
AMENDMENT = None


def equivalent_pipeline(old, revised):
    before = old.read_text(); after = revised.read_text()
    assert after.count('guarded_result(future,guard)') == 2
    after = after.replace('from guarded_training_future_v1 import result as guarded_result\n', '')
    after = after.replace('result=guarded_result(future,guard)', 'result=future.result(timeout=120)')
    after = after.replace('board_results.append(guarded_result(future,guard))', 'board_results.append(future.result(timeout=180))')
    assert ast.dump(ast.parse(before)) == ast.dump(ast.parse(after))


def specification():
    proposed, args, cache = ORIGINAL_SPEC()
    original = pilot.read(pilot.REG)
    # The new process imports extra orchestration modules. All scientific
    # fields and all original registered inputs must remain unchanged.
    assert {k: v for k, v in proposed.items() if k != 'inputs'} == {k: v for k, v in original.items() if k != 'inputs'}
    assert all(proposed['inputs'].get(k) == v for k, v in original['inputs'].items())
    pilot.verify(original['inputs'])
    return original, args, cache


def prepare_amendment(run):
    original, args, _ = specification()
    assert not pilot.RESULT.exists()
    current = pilot.read(pilot.STATUS)
    try:
        process = psutil.Process(current['pid'])
        assert not (process.is_running() and process.create_time() == current['process_created']), 'Existing pilot still live'
    except psutil.NoSuchProcess:
        pass
    if AMEND.exists():
        document = pilot.read(AMEND)
        assert document['scientific_registration_sha256'] == pilot.sha(pilot.REG)
        pilot.verify(document['inputs'])
        return document
    assert current['state'] == 'interrupted'
    failurepath = Path(current['evidence']); failure = pilot.read(failurepath)
    assert failure['registration_sha256'] == pilot.sha(pilot.REG)
    assert failure['error'] == 'TimeoutError()' and 'future.result(timeout=120)' in failure['traceback']
    assert not list(pilot.STORE.glob('checkpoint-*.json')), 'Final test evaluation already began'
    a = pilot.read(pilot.STORE/'A-baseline/progress.json')
    b = pilot.read(pilot.STORE/'A-river/progress.json')
    assert a['completed'] == 80 and len(a['updates']) == 2
    assert b['completed'] == 78 and not b['updates']
    oracles = list((pilot.STORE/'A-river').glob('qualification-*/complete/metrics.json'))
    assert len(oracles) == 1
    oracle = oracles[0]; metric = pilot.read(oracle)
    assert metric['iteration'] == 79 and metric['used_model']['generation'] == 78
    paths = [Path(__file__), PLAN, CONTROL, failurepath, oracle, pilot.REG]
    for row in metric['subbatches']:
        for name, digest in row['artifacts'].items():
            p = oracle.parent/f"batch-{row['chunk']:02d}"/name
            assert pilot.sha(p) == digest; paths.append(p)
    control = pilot.read(CONTROL); assert control['passed'] and len(control['checks']) == 6
    pilot.verify(control['inputs'])
    source = pilot.ROOT/'tools/research'
    for old, new in (('board_training_pipeline_v1.py', 'board_training_pipeline_wait_v1.py'),
                     ('river_training_pipeline_v1.py', 'river_training_pipeline_wait_v1.py')):
        equivalent_pipeline(source/old, source/new)
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(pilot.ROOT) and Path(p).suffix == '.py': paths.append(Path(p))
    inputs = dict(original['inputs']); inputs.update({str(p): pilot.sha(p) for p in paths})
    pilot.verify(inputs)
    document = dict(format=1, scientific_registration_sha256=pilot.sha(pilot.REG), inputs=inputs,
        change='Only guarded observation of live worker futures; existing 1200-second worker lifecycle and native-call limits remain.',
        unchanged_science=True, physical_workers=4, board_workers=4, new_test_deals_at_amendment=0,
        source_interruption=str(failurepath), source_interruption_sha256=pilot.sha(failurepath),
        qualification_oracle=str(oracle), qualification_oracle_sha256=pilot.sha(oracle),
        retained_baseline_progress_sha256=pilot.sha(pilot.STORE/'A-baseline/progress.json'),
        qualification_recovery='Fresh replay from published source 78; compare the already-complete qualification update 79. The failed replay never enters training.',
        timing_limit='Original baseline updates retain original orchestration; qualification overhead is separate and incomplete earlier-attempt timing is not reconstructed.',
        production_modified=False)
    if run: ORIGINAL_PUBLISH(AMEND, document)
    return document


def qualify(folder, arm, args, cache, guard):
    proof = folder/'qualification.json'
    if proof.exists():
        value = pilot.read(proof)
        assert value['passed'] and value['registration_sha256'] == pilot.sha(pilot.REG)
        assert value['execution_amendment_sha256'] == pilot.sha(AMEND)
        for filename, digest in value['artifacts'].items(): assert pilot.sha(folder/filename) == digest
        return
    pilot.verify(AMENDMENT['inputs']); guard()
    original_metric_path = Path(AMENDMENT['qualification_oracle'])
    assert pilot.sha(original_metric_path) == AMENDMENT['qualification_oracle_sha256']
    original_metric = pilot.read(original_metric_path)
    objects = folder/'objects'; cfg = arm['config']; model_args = pilot.model_args(args, arm)
    progress = pilot.read(folder/'progress.json')
    assert progress['completed'] == 78 and not progress['updates']
    state = pilot.checkpoint.restore_checkpoint(objects, progress['initial_fork'], cfg, **model_args)
    expected = pilot.checkpoint.restore_checkpoint(objects, original_metric['checkpoint'], cfg, **model_args)
    assert state['completed_iterations'] == 78 and expected['completed_iterations'] == 79
    attempt = folder/('qualification-resume-'+uuid.uuid4().hex[:8]); attempt.mkdir()
    step = pilot.step_arguments(arm, args, cache, guard)
    step['river_executable'] = pilot.EXES['river_executable']
    before = time.monotonic()
    metric = candidate_update(attempt/'replay', objects, state, cfg, **step)
    restored = pilot.checkpoint.restore_checkpoint(objects, metric['checkpoint'], cfg, **model_args)
    pilot.compare_states(state, restored); pilot.compare_states(state, expected)
    assert metric['checkpoint'] == original_metric['checkpoint']
    assert metric['subbatches'] == original_metric['subbatches']
    artifacts = {str(p.relative_to(folder)): pilot.sha(p) for directory in (attempt, original_metric_path.parent)
                 for p in directory.rglob('*') if p.is_file()}
    value = dict(passed=True, registration_sha256=pilot.sha(pilot.REG), execution_amendment_sha256=pilot.sha(AMEND),
        checkpoint=metric['checkpoint'], exact_restart_replay=True, interruption='root-update-complete',
        deliberate_stop_evidence='The preserved v1 run passed its injected stop and caller-state comparison before publishing the complete oracle; its terminal failure was in the subsequent replay wait.',
        completed_metrics=str((attempt/'replay/metrics.json').relative_to(folder)), artifacts=artifacts,
        seconds=time.monotonic()-before, seconds_scope='This recovery replay and readback only.',
        prior_completed_update_seconds=original_metric['seconds'], prior_incomplete_attempt_cost_included=False,
        total_qualification_seconds=None, training_cost_excluded=True)
    ORIGINAL_PUBLISH(proof, value)


def publish(path, value, **kwargs):
    target = Path(path)
    if target == pilot.RESULT or target == pilot.STATUS or target.name.startswith(pilot.NAME+'-interruption-'):
        pilot.verify(AMENDMENT['inputs'])
        value = dict(value, execution_amendment_sha256=pilot.sha(AMEND),
            execution_amendment=str(AMEND), orchestration_revision='guarded-training-future-v1')
    return ORIGINAL_PUBLISH(path, value, **kwargs)


def main(run=False, wait=False):
    global AMENDMENT
    AMENDMENT = prepare_amendment(run)
    if not run:
        print(json.dumps(dict(ready=True, predecessor_terminal=True, scientific_design_unchanged=True,
            complete_baseline_updates_reused=2, candidate_replay_required=True, new_test_deals=0)), flush=True)
        return
    pilot.specification = specification
    pilot.baseline_update = baseline_update
    pilot.candidate_update = candidate_update
    pilot.qualify = qualify
    pilot.atomic_json = publish
    pilot.main(run=True, resume=True, wait=wait)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--wait', action='store_true')
    a = parser.parse_args(); main(a.run, a.wait)
