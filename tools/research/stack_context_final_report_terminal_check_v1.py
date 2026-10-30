"""Isolated synthetic terminal-file controls for the report admission gate."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import json
from pathlib import Path
import tempfile
import time
import numpy as np
import stack_context_final_report_v1 as report
from stack_context_matched_analysis_v1 import context_analysis, finish, DEPTHS, DEALS
from stack_context_independent_audit_v1 import audit_comparison


def main():
    name = 'stack-context-final-report-terminal-check-v1'
    output = report.OUT/(name+'-result.json'); attempt = report.OUT/(name+'-attempt.json')
    if output.exists() or attempt.exists():
        raise ValueError('Preserve existing software-control evidence')
    inputs = {str(path):report.sha(path) for path in (Path(__file__), Path(report.__file__))}
    attempt.write_text(json.dumps(dict(inputs=inputs, synthetic_only=True)), encoding='utf-8')
    began = time.monotonic(); values = {depth:np.zeros((DEALS, 2, 4, 2)) for depth in DEPTHS}
    comparison = finish([context_analysis(values[depth], depth=depth, dead_money=.5) for depth in DEPTHS])
    arithmetic = audit_comparison(comparison, values)
    original_out, original_locks, original_live = report.OUT, report.LOCKS, report.live
    rejected = 0
    with tempfile.TemporaryDirectory(prefix='gtopen-terminal-report-control-') as folder:
        report.OUT = Path(folder)
        report.LOCKS = tuple(Path(folder)/f'owner-{i}.lock' for i in range(3))
        def write(path, value):
            path.write_text(json.dumps(value, allow_nan=False, sort_keys=True), encoding='utf-8')
        try:
            handoff_path = report.OUT/(report.HANDOFF+'-result.json')
            write(report.OUT/(report.HANDOFF+'-attempt.json'), dict(pid=2147480000, created=1.))
            state = dict(training_complete=True, training_alive=False, failure=[], external_owner=False)
            for index, (phase, name, script) in enumerate((
                    ('throughput', report.THROUGHPUT, 'stack_context_final_bank_throughput_v4.py'),
                    ('evaluation', report.EVALUATION, 'stack_context_matched_evaluation_v5.py'),
                    ('readback', report.READER, 'stack_context_matched_readback_v6.py')), 1):
                state[phase] = dict(started=True, alive=False, complete=True)
                write(report.OUT/(name+'-attempt.json'), dict(pid=2147480000+index, process_created=1.))
                prefix = report.OUT/(report.HANDOFF+'-'+str(index).zfill(3)+'-'+phase)
                start = dict(phase=phase, index=index, pid=2147480000+index, created=1., unix=2.,
                    command=['C:/Program Files/Python312/python.exe', '-B', str(report.ROOT/'tools/research'/script), '--run'])
                write(Path(str(prefix)+'-started.json'), start)
                for stream in ('stdout', 'stderr'):
                    Path(str(prefix)+'-'+stream+'.log').write_bytes(b'SYNTHETIC TERMINAL CONTROL\n')
                write(Path(str(prefix)+'-finished.json'), dict(start, exit_code=0, finished_unix=3.,
                    stdout_sha256=report.sha(Path(str(prefix)+'-stdout.log')),
                    stderr_sha256=report.sha(Path(str(prefix)+'-stderr.log'))))
            write(handoff_path, dict(handoff_complete=True, production_modified=False, unix=4., state=state))
            write(report.OUT/(report.THROUGHPUT+'-result.json'), dict(complete=True, passed=True,
                full_played_banks_64=True, cuda_passed=True, reference_agreement_passed=True))
            registration = report.OUT/(report.EVALUATION+'-registration.json'); write(registration, dict(synthetic=True))
            export_paths = [report.OUT/f'synthetic-range-{i}.json' for i in range(28)]
            for path in export_paths:
                write(path, dict(synthetic=True))
            terminal_path = report.OUT/(report.EVALUATION+'-result.json')
            write(terminal_path, dict(fixed_policy_evaluation_complete=True, production_modified=False,
                registration_sha256=report.sha(registration), comparison=comparison,
                journals={str(d):dict(completed_deals=DEALS) for d in DEPTHS},
                range_exports={str(p):report.sha(p) for p in export_paths}))
            reader_path = report.OUT/(report.READER+'-result.json')
            write(reader_path, dict(complete=True, passed=True, independent_readback_complete=True,
                training_heldout_stack_separation_verified=True, production_modified=False,
                evaluation_result_sha256=report.sha(terminal_path), evaluation_registration_sha256=report.sha(registration),
                original_archive_batches=896, reference_policy_replay_batches=14,
                reference_complete_preflop_range_replays=28, independent_chance_cycles=256,
                strictly_board_disjoint_test=False, native_payoff_oracle_independent=False, arithmetic=arithmetic))
            assert report.final_evidence()[0] == comparison
            def refuse():
                nonlocal rejected
                try:
                    report.final_evidence()
                except ValueError:
                    rejected += 1
                else:
                    raise AssertionError('Malformed terminal binding accepted')
            def changed(path, key, value):
                before = path.read_bytes(); document = report.read(path); document[key] = value
                write(path, document)
                try:
                    refuse()
                finally:
                    path.write_bytes(before)
            before = reader_path.read_bytes(); reader_path.unlink(); refuse(); reader_path.write_bytes(before)
            report.LOCKS[0].write_bytes(b'synthetic owner'); refuse(); report.LOCKS[0].unlink()
            failure = report.OUT/(report.HANDOFF+'-failure.json'); write(failure, {}); refuse(); failure.unlink()
            changed(handoff_path, 'handoff_complete', False)
            report.live = lambda *args:True
            try:
                refuse()
            finally:
                report.live = original_live
            finished = report.OUT/(report.HANDOFF+'-002-evaluation-finished.json')
            changed(finished, 'exit_code', 1)
            log = report.OUT/(report.HANDOFF+'-002-evaluation-stdout.log')
            before = log.read_bytes(); log.write_bytes(b'changed'); refuse(); log.write_bytes(before)
            changed(reader_path, 'evaluation_result_sha256', '0'*64)
            changed(reader_path, 'reference_complete_preflop_range_replays', 27)
            changed(reader_path, 'native_payoff_oracle_independent', True)
            before = export_paths[0].read_bytes(); export_paths[0].write_bytes(b'changed'); refuse(); export_paths[0].write_bytes(before)
            changed(terminal_path, 'fixed_policy_evaluation_complete', False)
            assert report.final_evidence()[0] == comparison
        finally:
            report.OUT, report.LOCKS, report.live = original_out, original_locks, original_live
    assert all(report.sha(path) == digest for path, digest in inputs.items())
    output.write_text(json.dumps(dict(complete=True, passed=True, inputs=inputs,
        seconds=time.monotonic()-began, synthetic_terminal_success_cases=2, negative_controls=rejected,
        live_scientific_evidence_read=False, synthetic_metadata_only=True,
        new_scientific_deals=False, fitting=False, native_execution=False, gpu_used=False,
        production_modified=False, broad_goal_complete=False), sort_keys=True), encoding='utf-8')
    print(json.dumps(dict(passed=True, negative_controls=rejected, seconds=time.monotonic()-began)))


if __name__ == '__main__':
    main()
