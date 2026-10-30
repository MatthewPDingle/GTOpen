"""Read-only routing for the original 1-48 and recovered 49-78 training record.

This does not declare an independent audit successful. It admits only a fully
completed, quiescent continuation and binds both physical evidence locations.
"""
import os
from pathlib import Path
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha
from later_average_support_v1 import OUT, read
from hu_paired_continuation_support_20260925 import LOCK, OTHER
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
from owned_columnar_evaluation_archive_v1 import unlinked

ORIGINAL = 'showdown-matched-training-v1'
CONTINUATION = 'showdown-fourth-arm-continuation-v1'
LABEL = '9266301-corrected'
ORIGINAL_SHA = '73305540181f7be96b5f5d68365408d89643c51d628966d2cb920aa423686eec'


def require(value, message):
    if not value:
        raise ValueError(message)


def quiescent():
    require(not LOCK.exists() and not OTHER.exists(), 'Training/research remains active')
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.pid == os.getpid() or 'python' not in (process.info['name'] or '').lower():
            continue
        require(process.info['cmdline'] is not None, 'Cannot verify Python process ownership')
        for arg in process.info['cmdline']:
            name = Path(arg).name
            require(not (name.startswith('retain_completed_showdown_arm_') or name in (
                'hu_showdown_matched_training_20260926.py',
                'hu_showdown_fourth_arm_continuation_20260927.py',
                'compact_checkpoint_fit_replay_20260926.py')),
                'Training or retention process is still live')


def source_for_iteration(original_case, continuation_case, iteration):
    require(type(iteration) is int and 1 <= iteration <= 78, 'Full fixed-budget iteration required')
    return original_case if iteration <= 48 else continuation_case


def merge_inputs(target, incoming):
    for path, expected in incoming.items():
        require(path not in target or target[path] == expected, 'Conflicting source binding: '+path)
        target[path] = expected


class Evidence:
    def __init__(self, *, guard):
        quiescent(); guard()
        self.guard = guard
        op = OUT/f'{ORIGINAL}-registration.json'
        rp = OUT/f'{CONTINUATION}-registration.json'
        result_path = OUT/f'{CONTINUATION}-result.json'
        status_path = OUT/f'{CONTINUATION}-status.json'
        original_status = OUT/f'{ORIGINAL}-status.json'
        require(sha(op) == ORIGINAL_SHA, 'Original trial changed')
        self.trial, self.registration = read(op), read(rp)
        self.result = read(result_path)
        status = read(status_path)
        require(status['state'] == 'complete' and status['exit_code'] == 0,
                'Continuation must terminate successfully before composite admission')
        require(read(original_status)['state'] == 'failed', 'Original failure must remain preserved')
        require(self.result['passed'] and self.result['terminal']
                and self.result['registration_sha256'] == sha(rp)
                and self.result['original_registration_sha256'] == ORIGINAL_SHA,
                'Continuation result identity differs')
        self.arm = next(a for a in self.trial['arms'] if a['name'] == LABEL)
        require(self.registration['arm'] == self.result['name'] == LABEL
                and self.registration['config'] == self.result['config'] == self.arm['config'],
                'Original arm configuration differs')
        require(self.result['completed_iterations'] == 78 and self.result['training_deals'] == 39936
                and self.result['final_restore_verified'], 'Full original training target required')
        self.original_case = unlinked(Path(self.trial['store'])/LABEL)
        self.continuation_case = unlinked(Path(self.registration['store'])/LABEL)
        require(Path(self.result['store']) == self.continuation_case
                and Path(self.result['original_store']) == self.original_case, 'Result stores differ')
        require(self.result['predecessor'] == dict(directory=str(self.original_case/'objects'), retention_sha256=None),
                'Predecessor identity differs')
        require(not (self.original_case/'result.json').exists(), 'Original failure was overwritten')
        require([p.name for p in sorted(self.original_case.glob('retention-*.json'))] ==
                [f'retention-{n:04d}.json' for n in range(1, 56)], 'Original durable prefix differs')
        require([p.name for p in sorted(self.continuation_case.glob('retention-*.json'))] ==
                [f'retention-{n:04d}.json' for n in range(49, 79)], 'Continuation prefix has gaps or extra updates')
        replays = self.result['exact_replays']
        require([r['iteration'] for r in replays] == list(range(49, 57)), 'Exact recovery comparisons incomplete')
        for row in replays:
            require(row['original_completed'] == (row['iteration'] <= 55)
                    and row['exact_model'] and row['exact_scientific_metrics'] and row['exact_native_artifacts'],
                    'Recovery comparison failed')
            require(read(self.continuation_case/f"exact-replay-{row['iteration']:04d}.json") == row,
                    'Recovery comparison receipt changed')
            require(row['original_metrics_sha256'] == sha(self.original_case/f"iteration-{row['iteration']:04d}/metrics.json"),
                    'Original compared metric changed')
        require(read(self.continuation_case/'result.json') == self.result, 'Continuation result copies differ')
        self.inputs = {}
        merge_inputs(self.inputs, self.trial['inputs'])
        merge_inputs(self.inputs, self.registration['inputs'])
        for p in [op, rp, result_path, status_path, original_status, Path(__file__).resolve(),
                  ROOT/'tools/research/archived_checkpoint_objects_v1.py']:
            merge_inputs(self.inputs, {str(p):sha(p)})
        for p in self.continuation_case.rglob('*'):
            if p.is_file():
                unlinked(p); merge_inputs(self.inputs, {str(p):sha(p)})
        self.terminal_inputs = {str(p):sha(p) for p in (op, rp, result_path, status_path, original_status)}
        steps = self.result['steps']; bank = self.result['played_bank']
        require(len(steps) == len(bank) == 78, 'Complete ordered bank and markers required')
        previous = None
        for n in range(1, 79):
            case = self.case(n)
            marker_path = case/f'retention-{n:04d}.json'
            marker = read(marker_path); metric_path = case/f'iteration-{n:04d}/metrics.json'; metric = read(metric_path)
            require(marker == steps[n-1] and marker['iteration'] == metric['iteration'] == n
                    and marker['metrics_sha256'] == sha(metric_path), 'Composite step binding differs')
            require(bank[n-1] == metric['used_model'] and metric['used_model']['generation'] == n-1
                    and metric['next_model']['generation'] == n, 'Played model history differs')
            require(previous is None or previous == metric['used_model'], 'Composite model chain broken')
            previous = metric['next_model']
            for p in (marker_path, metric_path):
                merge_inputs(self.inputs, {str(p):sha(p)})
                self.terminal_inputs[str(p)] = sha(p)
        require(self.result['final_checkpoint'] == steps[-1]['checkpoint'], 'Final checkpoint differs')
        for path, expected in self.inputs.items():
            guard(); require(sha(path) == expected, 'Registered source changed: '+path)
        self.original_objects = ReadOnlyCheckpointObjects(self.original_case/'objects', guard=guard)
        self.objects = ReadOnlyCheckpointObjects(self.continuation_case/'objects', guard=guard)
        require(self.original_objects.retention_sha256 is None, 'Original predecessor changed retention identity')
        self.recheck_terminal()

    def case(self, iteration):
        return source_for_iteration(self.original_case, self.continuation_case, iteration)

    def recheck_terminal(self):
        quiescent()
        for path, expected in self.terminal_inputs.items():
            self.guard(); require(sha(path) == expected, 'Completed composite evidence changed: '+path)

    def read_object(self, directory, reference):
        require(Path(directory).resolve() == self.objects.directory, 'Unexpected composite object directory')
        name = reference['file']
        # ReadOnlyCheckpointObjects validates path and content hashes on every read.
        present = (name in self.objects.members if self.objects.members is not None
                   else (self.objects.directory/name).exists())
        if present:
            raw = self.objects.read(reference)
            old_present = (name in self.original_objects.members if self.original_objects.members is not None
                           else (self.original_objects.directory/name).exists())
            if old_present:
                require(raw == self.original_objects.read(reference), 'Conflicting predecessor/local bytes')
            return raw
        return self.original_objects.read(reference)
