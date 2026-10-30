"""Read-only admission for the full durable prefix of a stopped training arm."""
from pathlib import Path
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from hu_paired_continuation_support_20260925 import LOCK, OTHER


def require(ok, message):
    if not ok:
        raise ValueError(message)


def quiescent():
    require(not LOCK.exists() and not OTHER.exists(), 'Research ownership remains active')
    for process in psutil.process_iter(['pid', 'cmdline']):
        for arg in process.info['cmdline'] or []:
            require(Path(arg).name != 'hu_showdown_matched_training_20260926.py',
                    'Original training process remains live')


def admit(label, completed):
    quiescent()
    require(type(completed) is int and 0 < completed < 78, 'Incomplete integer prefix required')
    registration = OUT/'showdown-matched-training-v1-registration.json'
    status = OUT/'showdown-matched-training-v1-status.json'
    require(read(status)['state'] == 'failed', 'Preserved terminal failure required')
    trial = read(registration)
    arm = next((arm for arm in trial['arms'] if arm['name'] == label), None)
    require(arm is not None, 'Unknown original arm')
    case = Path(trial['store'])/label
    require(not (case/'result.json').exists(), 'Arm already has a final result')
    markers = sorted(case.glob('retention-*.json'))
    require([p.name for p in markers] == [f'retention-{n:04d}.json' for n in range(1, completed+1)],
            'Must audit the entire contiguous durable prefix, without selection')
    inputs = {str(p): sha(p) for p in [registration, status, *markers]}
    for n, path in enumerate(markers, 1):
        marker = read(path)
        metric = case/f'iteration-{n:04d}'/'metrics.json'
        require(marker['iteration'] == n and marker['metrics_sha256'] == sha(metric),
                'Durable prefix metric mismatch')
        inputs[str(metric)] = sha(metric)
    quiescent()
    require(all(sha(p) == digest for p, digest in inputs.items()), 'Prefix changed during admission')
    return inputs


def recheck(inputs):
    quiescent()
    require(all(sha(p) == digest for p, digest in inputs.items()), 'Stopped prefix changed')
