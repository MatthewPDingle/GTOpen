"""Prospective resource recovery of the unchanged fourth 78-update training arm.

Original failed results and partial update 56 remain immutable. Replay 49-55
must match exactly before advancing; preserved partial 56 is checked as well.
This command never fabricates the original four-arm success document.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read, load_complete_cache
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK, OTHER
from hu_action_integrated_exact_20260925 import bank_args
from compact_checkpoint_fit_replay_20260926 import require

PREFIX = 'showdown-fourth-arm-continuation-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
LABEL = '9266301-corrected'
CAP = 850_000_000
SECONDS = 3*3600
TRIAL = OUT/'showdown-matched-training-v1-registration.json'
TRIAL_SHA = '73305540181f7be96b5f5d68365408d89643c51d628966d2cb920aa423686eec'


def output(suffix):
    return OUT/f'{PREFIX}-{suffix}.json'


def status(value):
    path = output('status'); temporary = path.with_suffix('.tmp')
    save(temporary, value); temporary.replace(path)


def admission():
    require(idle() and not LOCK.exists() and not OTHER.exists(), 'Research and production must be idle')
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.pid == os.getpid() or 'python' not in (process.info['name'] or '').lower():
            continue
        require(process.info['cmdline'] is not None, 'Cannot determine Python process ownership')
        for arg in process.info['cmdline']:
            name = Path(arg).name
            require(not (name.startswith('retain_completed_showdown_arm_')
                or name.startswith('compact_showdown_training_review_')
                or name in ('completed_retention_readback_20260927.py',
                    'hu_showdown_matched_training_20260926.py',
                    'compact_checkpoint_fit_replay_20260926.py', Path(__file__).name)),
                'Another recovery reader or writer is active')
    require(sha(TRIAL) == TRIAL_SHA, 'Original trial registration changed')
    old_status = read(OUT/'showdown-matched-training-v1-status.json')
    require(old_status['state'] == 'failed' and old_status['exit_code'] != 0, 'Preserved terminal failure required')
    replay = read(OUT/'compact-checkpoint-fit-replay-v1-result.json')
    require(replay['passed'] and read(OUT/'compact-checkpoint-fit-replay-v1-status.json')['state'] == 'complete',
            'Successful exact GPU fit replay required')
    require([(r['arm'], r['replayed_iteration']) for r in replay['cases']] ==
            [('9266201-baseline', 73), ('9266201-corrected', 17)], 'Fixed replay cases changed')
    for row in replay['cases']:
        require(row['exact_scientific_metrics'] and row['exact_native_artifact_hashes']
                and row['exact_initial_policy_values'], 'Replay qualification incomplete')
    audit = read(OUT/'showdown-training-readback-v3-9266301-corrected-0055-result.json')
    require(audit['passed'] and audit['completed_updates'] == 55 and not audit['complete_arm'],
            'Full stopped-prefix audit required')
    return old_status


def worker(reg):
    import torch
    import numpy as np
    from hu_paired_continuation_support_20260925 import setup_cuda
    from checkpoint_overlay_store_v1 import overlay
    from compact_checkpoint_restore_v3 import restore
    from showdown_continuation_recovery_v1 import compare_update, retain_update, equal_states
    import showdown_cadence_training_v1 as training

    setup_cuda()
    started = time.monotonic(); last = last_size = 0.
    def guard():
        nonlocal last, last_size
        now = time.monotonic()
        require(now-started < SECONDS, 'Registered continuation time allowance exhausted')
        if now-last >= 2:
            require(idle() and not OTHER.exists(), 'Production activity or competing research')
            require(LOCK.read_text().strip() == str(os.getppid()), 'Continuation lock lost')
            require(psutil.virtual_memory().available >= 20_000_000_000, 'RAM reserve')
            require(shutil.disk_usage('S:/').free >= 40_000_000_000, 'Disk reserve')
            require(torch.cuda.mem_get_info()[0] >= 3_000_000_000, 'GPU reserve')
            last = now
        if now-last_size >= 5:
            paths = list(STORE.rglob('*')) + list(OUT.glob(PREFIX+'*'))
            require(sum(p.stat().st_size for p in paths if p.is_file()) <= CAP, 'Continuation output cap')
            last_size = now
    records = []; replays = []
    try:
        guard()
        for path, expected in reg['inputs'].items():
            require(sha(path) == expected, 'Registered input changed: '+path)
        trial = read(TRIAL); source = Path(trial['store'])/LABEL
        arm = next(a for a in trial['arms'] if a['name'] == LABEL)
        cfg = arm['config']
        require(cfg == reg['config'] and cfg['max_iterations'] == 78, 'Original fixed budget/configuration changed')
        require(cfg['torch_version'] == torch.__version__ and cfg['numpy_version'] == np.__version__
                and cfg['device_name'] == torch.cuda.get_device_name(), 'Original numerical environment required')
        STORE.mkdir(); token = uuid.uuid4().hex
        save(STORE/'archive-owner.json', dict(format=1, token=token, purpose='new-research-scratch-v1'))
        case = STORE/LABEL; objects = case/'objects'; objects.mkdir(parents=True)
        cp = OUT/'bb-context-candidate.json'; args = bank_args(cp.read_text())
        state, initial_identity = restore(source, 48, treatment='corrected', config=cfg, bank_args=args, guard=guard)
        predecessor = dict(directory=str(source/'objects'), retention_sha256=None)
        # This source was intentionally never retained: its complete and partial
        # objects are bound individually by this continuation's registration.
        require(initial_identity['object_retention_sha256'] is None, 'Original fourth-arm ownership changed')
        kwargs = dict(context_path=cp, catalog_source=args['catalog_source'], matrix_sha256=args['matrix_sha256'],
            matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(), cache=load_complete_cache(),
            executable=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe',
            integration_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
            trace_executable=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe',
            score_executable=ROOT/'target/release/examples/hu_board_outcomes_v1.exe',
            coefficients=read(OUT/'showdown-root-control-coefficients-v1.json'),
            batch_prefix='showdown-matched-training-v1-'+str(arm['seed']), guard=guard)
        for n in range(49, 79):
            guard(); began = time.monotonic()
            if n == 56:
                require([r['iteration'] for r in replays] == list(range(49, 56)),
                        'Every durable replay must pass before advancing')
            due = n % 8 == 0 or n == 78
            with overlay(objects, source/'objects', root=STORE, token=token, guard=guard) as provenance:
                metric = training.update(case/f'iteration-{n:04d}', objects, state, cfg,
                                         checkpoint_due=due, **kwargs)
                if n <= 56:
                    row = compare_update(source, case/f'iteration-{n:04d}', metric,
                                         completed=n <= 55, guard=guard)
                    replays.append(row)
                    save(case/f'exact-replay-{n:04d}.json', row)
                marker = retain_update(case, objects, metric, root=STORE, token=token, guard=guard)
                save(case/f'overlay-{n:04d}.json', provenance)
            if due:
                restored, identity = restore(case, n, treatment='corrected', config=cfg,
                                            bank_args=args, guard=guard, predecessor=predecessor)
                equal_states(state, restored)
                save(case/f'restored-{n:04d}.json', dict(passed=True, identity=identity,
                    exact_arrays_and_random_states=True))
                del restored
            records.append(marker)
            progress = dict(state='running', worker_pid=os.getpid(), arm=LABEL, completed_iterations=n,
                latest_recovery_iteration=n if due else n//8*8,
                replayed_durable_updates=min(n-48, 7), seconds=time.monotonic()-started,
                original_training_seconds=reg['original_training_seconds'], production_modified=False)
            status(progress); print(json.dumps(dict(progress, update_seconds=time.monotonic()-began)), flush=True)
        require(state['completed_iterations'] == 78 and len(state['played_bank']) == 78
                and int(state['root_regret_state'].counts.sum()) == 39936, 'Final training budget mismatch')
        for path, expected in reg['inputs'].items():
            guard(); require(sha(path) == expected, 'Original/registered evidence changed: '+path)
        steps = [read(source/f'retention-{n:04d}.json') for n in range(1, 49)] + records
        result = dict(passed=True, terminal=True, registration_sha256=sha(output('registration')),
            original_registration_sha256=TRIAL_SHA, original_status_remains_failed=True,
            name=LABEL, config=cfg, store=str(case), original_store=str(source), predecessor=predecessor,
            completed_iterations=78, training_deals=39936, played_bank=state['played_bank'],
            final_checkpoint=records[-1]['checkpoint'], final_restore_verified=True,
            initial_restore=initial_identity, steps=steps, exact_replays=replays,
            original_training_seconds=reg['original_training_seconds'], continuation_seconds=time.monotonic()-started,
            total_charged_training_seconds=reg['original_training_seconds']+time.monotonic()-started,
            original_evidence_modified=False, production_modified=False, accuracy_qualified=False,
            independent_composite_audit_complete=False, evaluation_complete=False,
            scope='Recovered fourth training arm only; composite independent audit and fresh payoff evaluation remain required.')
        save(case/'result.json', result); save(output('result'), result)
    except BaseException as exc:
        save(output('result'), dict(passed=False, error=repr(exc), completed_new_updates=len(records),
            exact_replays=replays, registration_sha256=sha(output('registration')),
            seconds=time.monotonic()-started, original_evidence_modified=False))
        raise


def main():
    old_status = admission()
    require(not STORE.exists() and not any(OUT.glob(PREFIX+'*')), 'Continuation artifacts already exist; preserve them')
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    child = None; registered = False; error = None; started = time.monotonic()
    try:
        from hu_root_retained_storage_admitted_study_20260924 import measure, LIMIT, METADATA_RESERVE
        trial = read(TRIAL); source = Path(trial['store'])/LABEL
        arm = next(a for a in trial['arms'] if a['name'] == LABEL)
        require(sorted(int(p.stem.split('-')[1]) for p in source.glob('retention-*.json')) == list(range(1, 56)),
                'Exact stopped prefix changed')
        require((source/'checkpoint-0048.json').exists() and (source/'iteration-0056/metrics.json').exists(),
                'Required original recovery evidence missing')
        require(not (source/'result.json').exists(), 'Fourth arm unexpectedly complete')
        inputs = dict(trial['inputs'])
        for path, expected in inputs.items():
            require(sha(path) == expected, 'Original implementation changed: '+path)
        for p in (ROOT/'tools/research').glob('*.py'):
            inputs[str(p)] = sha(p)
        for p in source.rglob('*'):
            if p.is_file():
                require(not p.lstat().st_file_attributes & 0x400, 'Linked original input')
                inputs[str(p)] = sha(p)
        paths = [TRIAL, OUT/'showdown-matched-training-v1-status.json',
                 OUT/'SHOWDOWN-FOURTH-ARM-CONTINUATION-PLAN.md']
        for prefix in ('compact-checkpoint-fit-replay-v1',
                       'showdown-training-readback-v3-9266301-corrected-0055',
                       'checkpoint-overlay-control-v2', 'checkpoint-archived-overlay-control-v1',
                       'compact-mixed-restore-control-v1'):
            rp = OUT/f'{prefix}-registration.json'; result = OUT/f'{prefix}-result.json'
            value = read(result)
            require(value['passed'] and value.get('registration_sha256', value.get('readback_registration_sha256')) == sha(rp),
                    'Recovery control evidence differs: '+prefix)
            paths.extend([rp, result])
        for p in paths:
            inputs[str(p)] = sha(p)
        inventory = measure()
        require(sum(r['allocated_file_bytes'] for r in inventory)+CAP+METADATA_RESERVE <= LIMIT,
                'Insufficient global storage; retain completed evidence before retry, never raise limit')
        reg = dict(inputs=inputs, arm=LABEL, config=arm['config'], store=str(STORE),
            original_registration_sha256=TRIAL_SHA, original_training_seconds=old_status['seconds'],
            original_maximum_seconds=trial['maximum_seconds'], additional_maximum_seconds=SECONDS,
            cumulative_maximum_training_seconds=old_status['seconds']+SECONDS,
            maximum_output_bytes=CAP, storage_inventory=inventory, global_limit=LIMIT,
            metadata_reserve=METADATA_RESERVE, restore_iteration=48, original_durable_iteration=55,
            exact_required_replay_updates=list(range(49, 56)), compare_partial_update=56, final_iteration=78,
            resource_amendment='Separate 3-hour and 850 MB recovery allowance; original failure/time charge preserved. No new seeds, treatment changes, or outcome-based budget extension.',
            production_modified=False, accuracy_qualified=False)
        save(output('registration'), reg); registered = True
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker'], cwd=ROOT,
                stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            began = time.monotonic()
            while child.poll() is None:
                require(idle() and not OTHER.exists(), 'Production activity or competing research')
                require(time.monotonic()-began < SECONDS+120, 'Continuation worker deadline')
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
        require(child.returncode == 0 and read(output('result'))['passed'], 'Continuation stopped; preserve all evidence')
    except BaseException as exc:
        error = repr(exc); raise
    finally:
        if child is not None and child.poll() is None:
            descendants = psutil.Process(child.pid).children(recursive=True)
            child.terminate()
            for process in descendants:
                try:
                    process.terminate()
                except psutil.NoSuchProcess:
                    pass
            child.wait(timeout=15)
        require(LOCK.read_text().strip() == str(os.getpid()), 'Continuation lock owner changed')
        LOCK.unlink()
        if registered:
            status(dict(state='failed' if error else 'complete', error=error,
                exit_code=child.returncode if child else None, seconds=time.monotonic()-started,
                original_training_seconds=old_status['seconds'], production_modified=False))


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']:
        worker(read(output('registration')))
    else:
        require(sys.argv[1:] == ['--run'], 'Use --run')
        main()
