"""Prospective GPU control: repeat two existing updates after archived restore.

Never resumes the study itself. Originals are read-only; replay evidence goes
to a new owned directory. Admission must precede CUDA use and artifact creation.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from hu_paired_continuation_support_20260925 import LOCK, OTHER
from reboot_research_idle_v1 import idle

PREFIX = 'compact-checkpoint-fit-replay-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
CASES = [('9266201-baseline', 72), ('9266201-corrected', 16)]
CAP = 400_000_000
SECONDS = 1800
TRIAL = OUT / 'showdown-matched-training-v1-registration.json'
TRIAL_SHA = '73305540181f7be96b5f5d68365408d89643c51d628966d2cb920aa423686eec'


def output(suffix):
    return OUT / f'{PREFIX}-{suffix}.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def admission():
    require(not LOCK.exists() and not OTHER.exists(), 'Research owns the GPU; replay deferred')
    # Also catch an orphaned original worker even if a lock was removed.
    for proc in psutil.process_iter(['pid', 'cmdline']):
        cmd = proc.info['cmdline'] or []
        require(not any(Path(arg).name == 'hu_showdown_matched_training_20260926.py'
                        for arg in cmd), 'Original training process is still live')
    require(read(OUT/'showdown-matched-training-v1-status.json')['state'] in ('complete', 'failed'),
            'Original training must be terminal')
    require(idle(), 'Production solve or reports are active')


def scientific_metrics(value):
    """Only named wall-clock fields and separately checked initial-file hash differ."""
    value = copy.deepcopy(value)
    del value['root_integration_seconds']
    del value['initial_policy_sha256']
    for fit in value['fits']:
        for name in ('setup_seconds', 'optimizer_seconds', 'graph_capture_seconds'):
            del fit[name]
    return value


def compare(original, replay, original_initial, replay_initial):
    require(original_initial == replay_initial, 'Initial policy values differ')
    require(scientific_metrics(original) == scientific_metrics(replay),
            'Replayed scientific metrics, artifact hashes or fitted model differ')
    # No float tolerance: the next model reference includes its complete byte hash.
    require(original['next_model'] == replay['next_model'], 'Model is not byte-identical')


def worker(reg):
    import torch
    import numpy as np
    from hu_paired_continuation_support_20260925 import setup_cuda
    from later_average_support_v1 import load_complete_cache
    from hu_action_integrated_exact_20260925 import bank_args
    from compact_checkpoint_restore_v1 import restore
    from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
    from owned_research_archive_v1 import pack, unpack, retire
    import later_action_cadence_training_v1 as baseline
    import showdown_cadence_training_v1 as corrected

    require(LOCK.read_text().strip() == str(os.getppid()), 'Replay controller must own lock')
    setup_cuda(); start = time.monotonic(); last = last_size = 0.
    def guard():
        nonlocal last, last_size
        now = time.monotonic()
        require(now-start < SECONDS, 'Replay time cap')
        if now-last >= 2:
            require(idle() and not OTHER.exists(), 'Production activity or competing research')
            require(LOCK.read_text().strip() == str(os.getppid()), 'Replay lock lost')
            require(psutil.virtual_memory().available >= 20_000_000_000, 'RAM reserve')
            require(shutil.disk_usage('S:/').free >= 40_000_000_000, 'Disk reserve')
            require(torch.cuda.mem_get_info()[0] >= 3_000_000_000, 'GPU reserve')
            last = now
        if now-last_size >= 5:
            paths = list(STORE.rglob('*')) + list(OUT.glob(PREFIX+'*'))
            require(sum(p.stat().st_size for p in paths if p.is_file()) <= CAP, 'Replay output cap')
            last_size = now
    records = []
    try:
        guard()
        for path, digest in reg['inputs'].items():
            require(sha(path) == digest, 'Frozen input changed: '+path)
        STORE.mkdir(); token = uuid.uuid4().hex
        save(STORE/'archive-owner.json', dict(format=1, token=token, purpose='new-research-scratch-v1'))
        trial = read(TRIAL); source_root = Path(trial['store'])
        cp = OUT/'bb-context-candidate.json'; args = bank_args(cp.read_text())
        cache = load_complete_cache()
        step = dict(context_path=cp, catalog_source=args['catalog_source'], matrix_sha256=args['matrix_sha256'],
            matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(), cache=cache,
            executable=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe',
            integration_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
            trace_executable=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe', guard=guard)
        for label, n in CASES:
            guard(); began = time.monotonic(); source = source_root/label
            arm = next(a for a in trial['arms'] if a['name'] == label); cfg = arm['config']
            require(cfg['torch_version'] == torch.__version__ and cfg['numpy_version'] == np.__version__,
                    'Original numerical library versions required')
            require(cfg['device_name'] == torch.cuda.get_device_name(), 'Original GPU required')
            state, identity = restore(source, n, treatment=arm['treatment'], config=cfg, bank_args=args, guard=guard)
            case = STORE/label; objects = case/'objects'; objects.mkdir(parents=True)
            reader = ReadOnlyCheckpointObjects(source/'objects', guard=guard)
            # The outer document contains the full current policy; previous played
            # generations remain in state but are not loaded by this single update.
            with (objects/state['next_model']['file']).open('xb') as stream:
                stream.write(reader.read(state['next_model']))
            del reader
            kwargs = dict(step, batch_prefix='showdown-matched-training-v1-'+str(arm['seed']))
            module = baseline if arm['treatment'] == 'baseline' else corrected
            if arm['treatment'] != 'baseline':
                kwargs.update(coefficients=read(OUT/'showdown-root-control-coefficients-v1.json'),
                              score_executable=ROOT/'target/release/examples/hu_board_outcomes_v1.exe')
            folder = case/f'iteration-{n+1:04d}'
            replay = module.update(folder, objects, state, cfg, checkpoint_due=False, **kwargs)
            original_folder = source/f'iteration-{n+1:04d}'
            original = read(original_folder/'metrics.json')
            require(sha(original_folder/'metrics.json') == read(source/f'retention-{n+1:04d}.json')['metrics_sha256'],
                    'Original completed-update marker mismatch')
            for metric, directory in ((original, original_folder), (replay, folder)):
                require(sha(directory/'current-initial-policy.json') == metric['initial_policy_sha256'],
                        'Initial policy hash mismatch')
            compare(original, replay, read(original_folder/'current-initial-policy.json'),
                    read(folder/'current-initial-policy.json'))
            marker = read(source/f'retention-{n+1:04d}.json')
            require(len(marker['archives']) == 8, 'Eight original subbatches required')
            for chunk, pointer in enumerate(marker['archives']):
                archive = Path(pointer['path']); mp = archive.with_suffix('.xz.json')
                require(sha(mp) == pointer['manifest_sha256'], 'Original archive manifest changed')
                members = unpack(archive, read(mp), guard=guard)
                part = folder/f'batch-{chunk:02d}'
                require(set(members) == {p.name for p in part.iterdir() if p.is_file()},
                        'Replay artifact set differs')
                for name, raw in members.items():
                    require(raw == (part/name).read_bytes(), 'Original/replay artifact bytes differ: '+name)
                del members
            require(state['completed_iterations'] == n+1 and len(state['played_bank']) == n+1,
                    'Replayed generation mismatch')
            # Retire only new replay duplicates, after comparison and durable readback.
            archives = []
            for chunk in range(8):
                part = folder/f'batch-{chunk:02d}'; dest = case/f'batch-{chunk:02d}.xz'
                manifest = pack(part, [p.name for p in part.iterdir() if p.is_file()], dest,
                                root=STORE, token=token, guard=guard)
                retire(part, dest, manifest, root=STORE, token=token, guard=guard)
                archives.append(dict(path=str(dest), manifest_sha256=sha(dest.with_suffix('.xz.json'))))
            row = dict(arm=label, restored_iteration=n, replayed_iteration=n+1,
                restore_identity=identity, next_model=replay['next_model'], exact_scientific_metrics=True,
                exact_native_artifact_hashes=True, exact_initial_policy_values=True,
                initial_policy_bytes_equal=original['initial_policy_sha256'] == replay['initial_policy_sha256'],
                archives=archives, seconds=time.monotonic()-began)
            save(case/'result.json', row); records.append(row)
            print(json.dumps(dict(arm=label, iteration=n+1, exact_model=True, seconds=row['seconds'])), flush=True)
            del state
        for path, digest in reg['inputs'].items():
            guard(); require(sha(path) == digest, 'Frozen input changed: '+path)
        save(output('result'), dict(passed=True, registration_sha256=sha(output('registration')),
            cases=records, seconds=time.monotonic()-start, production_modified=False,
            original_training_modified=False, study_continuation_qualified=False,
            scope='Exact fit replay for two specified existing updates only; continuation controller and fresh payoff evaluation still required.'))
    except BaseException as exc:
        save(output('result'), dict(passed=False, error=repr(exc), cases=records,
            registration_sha256=sha(output('registration')), seconds=time.monotonic()-start))
        raise


def main():
    admission()  # Refuse a live study before creating any artifact or using CUDA.
    require(not STORE.exists() and not any(OUT.glob(PREFIX+'*')), 'Replay already has artifacts')
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    child = None; registered = False; error = None; start = time.monotonic()
    try:
        from hu_root_retained_storage_admitted_study_20260924 import measure, LIMIT, METADATA_RESERVE
        require(sha(TRIAL) == TRIAL_SHA, 'Original training registration changed')
        trial = read(TRIAL); inputs = dict(trial['inputs'])
        for path, digest in inputs.items():
            require(sha(path) == digest, 'Original source changed: '+path)
        control = OUT/'compact-checkpoint-restore-control-v1-result.json'
        require(read(control)['passed'], 'Archive restore control must pass first')
        inputs.update({str(p): sha(p) for p in (ROOT/'tools/research').glob('*.py')})
        for p in (TRIAL, control, OUT/'compact-checkpoint-restore-source-bindings-v1.json'):
            inputs[str(p)] = sha(p)
        for label, n in CASES:
            case = Path(trial['store'])/label
            for p in (case/f'checkpoint-{n:04d}.json', case/f'retention-{n:04d}.json',
                      case/f'iteration-{n:04d}/metrics.json', case/f'retention-{n+1:04d}.json',
                      case/f'iteration-{n+1:04d}/metrics.json', case/f'iteration-{n+1:04d}/current-initial-policy.json'):
                inputs[str(p)] = sha(p)
            pointer = read(case/f'checkpoint-{n:04d}.json')['reservoir_archive']
            archives = [pointer, *read(case/f'retention-{n+1:04d}.json')['archives']]
            for pointer in archives:
                archive = Path(pointer['path']); mp = archive.with_suffix('.xz.json')
                require(sha(mp) == pointer['manifest_sha256'], 'Original manifest changed')
                inputs[str(mp)] = sha(mp); inputs[str(archive)] = sha(archive)
        inventory = measure()
        require(sum(row['allocated_file_bytes'] for row in inventory)+CAP+METADATA_RESERVE <= LIMIT,
                'Global storage admission failed; do not raise cap')
        reg = dict(inputs=inputs, cases=CASES, store=str(STORE), maximum_seconds=SECONDS,
            maximum_output_bytes=CAP, storage_inventory=inventory, original_training_sha256=TRIAL_SHA,
            comparison='Exact model and native artifact hashes, exact parsed scientific values; named timing fields excluded. Initial JSON key order may differ.',
            scope='Two fixed old-update fit replays; no new study training or evaluation deals.')
        save(output('registration'), reg); registered = True
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker'], cwd=ROOT,
                stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            began = time.monotonic()
            while child.poll() is None:
                require(idle() and not OTHER.exists(), 'Production activity or competing research')
                require(time.monotonic()-began < SECONDS+120, 'Worker deadline')
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
        require(child.returncode == 0 and read(output('result'))['passed'], 'Replay failed; preserve evidence')
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        if child is not None and child.poll() is None:
            descendants = psutil.Process(child.pid).children(recursive=True)
            child.terminate()
            for proc in descendants:
                try:
                    proc.terminate()
                except psutil.NoSuchProcess:
                    pass
            child.wait(timeout=15)
        require(LOCK.read_text().strip() == str(os.getpid()), 'Replay lock owner changed')
        LOCK.unlink()
        if registered:
            save(output('status'), dict(state='failed' if error else 'complete', error=error,
                exit_code=child.returncode if child else None, seconds=time.monotonic()-start,
                production_modified=False))


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']:
        worker(read(output('registration')))
    elif sys.argv[1:] == ['--check-admission']:
        admission(); print('Replay admission passed; no artifacts created and CUDA unused')
    else:
        require(sys.argv[1:] == ['--run'], 'Use --check-admission or --run')
        main()
