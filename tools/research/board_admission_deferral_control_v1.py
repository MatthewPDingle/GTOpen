"""Synthetic qualification of the exact pre-admission deferral boundary."""
import json
from pathlib import Path
from board_status_recovery_v2 import early_gpu_rejection, admissions
from board_full_followup_queue_v1 import OUT, sha
from board_prefix_publication_v1 import atomic_json


def main():
    filename = str(Path(__file__).with_name('board_complete_evaluation_study_v1.py'))
    def get_error(line, name='run', kind='AssertionError', file=filename):
        namespace = {}
        code = f'def {name}():\n' + '\n' * (line - 2) + f'    raise {kind}()\n'
        exec(compile(code, file, 'exec'), namespace)
        try:
            namespace[name]()
        except BaseException as error:
            return error
    matching = get_error(110)
    assert early_gpu_rejection(matching, filename)
    negatives = [get_error(111), get_error(109), get_error(110, name='other'),
        get_error(110, kind='ValueError'), get_error(110, file=filename+'.other'), AssertionError()]
    assert all(not early_gpu_rejection(error, filename) for error in negatives)
    calls, deferred, waits = [], [], []
    def invoke(index):
        calls.append(index)
        if index == 1:
            raise matching
        return 'completed'
    result = admissions(invoke, lambda: waits.append(True),
        lambda error, index: early_gpu_rejection(error, filename), deferred.append)
    assert result == (2, 'completed') and calls == [1,2] and deferred == [1] and len(waits) == 2
    for error in negatives:
        called = []
        def fail(index):
            called.append(index)
            raise error
        try:
            admissions(fail, lambda: None, lambda e, i: early_gpu_rejection(e, filename), lambda i: None)
        except BaseException as observed:
            assert observed is error and called == [1]
        else:
            raise AssertionError('Non-admission failure retried')
    called = []; deferred = []
    def always(index):
        called.append(index)
        raise matching
    try:
        admissions(always, lambda: None, lambda e, i: early_gpu_rejection(e, filename), deferred.append, limit=3)
    except AssertionError as error:
        assert error is matching and called == deferred == [1,2,3]
    else:
        raise AssertionError('Admission retry limit ignored')
    paths = [Path(__file__), Path(__file__).with_name('board_status_recovery_v2.py'),
        Path(__file__).with_name('board_status_recovery_v1.py'), Path(filename),
        OUT / 'windows-progress-publication-control-v1-result.json']
    result = dict(passed=True, inputs={str(p):sha(p) for p in paths},
        only_exact_prelock_gpu_assertion_accepted=True, successful_admission_runs_once=True,
        other_errors_not_retried=True, retry_limit_enforced=True, synthetic_only=True,
        fresh_test_deals_drawn=0, rejected_error_cases=len(negatives))
    atomic_json(OUT / 'board-admission-deferral-control-v1-result.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
