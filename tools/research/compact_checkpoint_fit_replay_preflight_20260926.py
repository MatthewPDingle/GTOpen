"""CPU-only negative checks while original training owns the GPU lock."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import compact_checkpoint_fit_replay_20260926 as replay


def main():
    require = replay.require
    require(replay.LOCK.exists(), 'Run this refusal control only while training owns lock')
    owner = int(replay.LOCK.read_text().strip())
    import psutil
    process = psutil.Process(owner)
    require(any(Path(a).name == 'hu_showdown_matched_training_20260926.py' for a in process.cmdline()),
            'Verify a live original controller, not a stale lock')
    before = list(replay.OUT.glob(replay.PREFIX+'*'))
    require(not before and not replay.STORE.exists(), 'Replay must not have started')
    result = subprocess.run([sys.executable, str(Path(replay.__file__).resolve()), '--run'],
        capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
    require(result.returncode != 0 and 'Research owns the GPU; replay deferred' in result.stderr,
            'Run command did not reject live training')
    require(not list(replay.OUT.glob(replay.PREFIX+'*')) and not replay.STORE.exists(),
            'Refusal created replay artifacts')
    require(replay.LOCK.read_text().strip() == str(owner) and process.is_running(), 'Original lock/process changed')
    trial = replay.read(replay.TRIAL); records = []
    for label, n in replay.CASES:
        folder = Path(trial['store'])/label/f'iteration-{n+1:04d}'
        metric = replay.read(folder/'metrics.json'); initial = replay.read(folder/'current-initial-policy.json')
        timing = copy.deepcopy(metric)
        timing['root_integration_seconds'] += 1
        timing['initial_policy_sha256'] = 'separately checked initial file hash'
        for fit in timing['fits']:
            for name in ('setup_seconds', 'optimizer_seconds', 'graph_capture_seconds'):
                fit[name] += 1
        reordered = copy.deepcopy(initial)
        reordered['used_model'] = dict(reversed(list(initial['used_model'].items())))
        replay.compare(metric, timing, initial, reordered)
        rejected = []
        for kind in ('model', 'artifact', 'fit', 'initial', 'unexpected_metric'):
            bad = copy.deepcopy(metric); badi = copy.deepcopy(initial)
            if kind == 'model': bad['next_model']['sha256'] = '0'*64
            if kind == 'artifact': bad['subbatches'][0]['artifacts']['queries'] = '0'*64
            if kind == 'fit': bad['fits'][0]['normalized_grouped_loss_after'] += 1e-9
            if kind == 'initial': badi['root'][0][0] += 1e-9
            if kind == 'unexpected_metric': bad['new_ignored_field'] = True
            try:
                replay.compare(metric, bad, initial, badi)
            except ValueError:
                rejected.append(kind)
            else:
                raise AssertionError('Accepted mutation '+kind)
        records.append(dict(arm=label, rejected_mutations=rejected,
                            original_metrics_sha256=replay.sha(folder/'metrics.json')))
    for path, digest in trial['inputs'].items():
        require(replay.sha(path) == digest, 'Original frozen input changed: '+path)
    dest = replay.OUT/'compact-fit-replay-preflight-v1-result.json'
    require(not dest.exists(), 'Preflight result already exists')
    report = dict(passed=True, live_controller_pid=owner, live_launch_refused=True,
        replay_artifacts_created=False, gpu_used=False, fitted_update_replayed=False,
        source_sha256={str(Path(p).resolve()): replay.sha(p) for p in (__file__, replay.__file__)},
        original_training_sha256=replay.sha(replay.TRIAL), original_inputs_verified=len(trial['inputs']),
        comparator_cases=records, scope='Admission and comparison negative checks only; actual GPU replay remains pending.')
    replay.save(dest, report); print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
