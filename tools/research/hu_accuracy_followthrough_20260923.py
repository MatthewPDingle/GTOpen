"""One-shot sequential continuation after the currently running audited study.

Never restarts the dependency or a failed stage. No deployment or model selection.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from reboot_research_idle_v1 import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
TD = ROOT/'tools/research'
PREFIX = 'accuracy-followthrough-v1'
DEPENDENCY = 'sampled-visible-hybrid-completion-study-v1'
STAGES = [
    ('comparison', 'hu_visible_hybrid_completion_comparison_20260923.py', []),
    ('equities', 'hu_complete_allin_cache_20260923.py', ['--run']),
    ('equity-audit', 'hu_complete_allin_cache_review_20260923.py', []),
    ('btn-response', 'hu_exhaustive_btn_response_20260923.py', []),
    ('btn-response-audit', 'hu_exhaustive_btn_response_review_20260923.py', []),
]


def read(path):
    return json.loads(Path(path).read_text())


def main():
    assert sys.argv[1:] == ['--run'] and idle()
    began = time.monotonic()
    dependency_path = OUT/f'{DEPENDENCY}-registration.json'
    dependency_status = OUT/f'{DEPENDENCY}-status.json'
    status = read(dependency_status)
    assert status['state'] == 'running'
    owner = psutil.Process(status['controller_pid'])
    command = owner.cmdline()
    assert any(Path(s).name == 'hu_visible_hybrid_completion_study_20260923.py' for s in command)
    identity = dict(pid=owner.pid, created=owner.create_time(), command=command)
    sources = [Path(__file__), dependency_path, TD/'reboot_research_idle_v1.py',
               OUT/'complete-private-allin-cache-v1-registration.json',
               TD/'hu_exhaustive_btn_response_review_20260923.py',
               *[TD/name for _, name, _ in STAGES]]
    inputs = {str(p): sha(p) for p in sources}
    registration = dict(inputs=inputs, dependency=identity, stages=STAGES,
        dependency_wait_cap_seconds=12600, production_modified=False,
        policy='One run only; each stage retains its existing resource, integrity and activity guards. Stop on any failed prerequisite or nonzero stage exit; no retry, model selection or deployment.')
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists()
    save(rp, registration)
    records = []; error = None; child = None

    def write_status(state, **extra):
        p = OUT/f'{PREFIX}-status.json'; tmp = p.with_suffix('.tmp')
        save(tmp, dict(state=state, controller_pid=os.getpid(),
            seconds=time.monotonic()-began, stages=records,
            production_modified=False, **extra))
        tmp.replace(p)

    def verify_inputs():
        for path, expected in inputs.items():
            assert sha(path) == expected, path

    try:
        while owner.is_running():
            assert owner.create_time() == identity['created']
            assert time.monotonic()-began < registration['dependency_wait_cap_seconds']
            s = read(dependency_status)
            assert s['state'] in ('running', 'complete'), 'Dependency stopped; do not retry'
            write_status('waiting', dependency_pid=owner.pid, dependency_stage=s.get('stage'))
            time.sleep(15)
        verify_inputs()
        s = read(dependency_status)
        result_path = OUT/f'{DEPENDENCY}-result.json'; result = read(result_path)
        assert s['state'] == 'complete' and s.get('error') is None
        assert result['passed'] and result['registration_sha256'] == sha(dependency_path)
        expected = read(dependency_path)['stages']
        assert [r['stage'] for r in result['stages']] == [r[0] for r in expected]
        assert all(r['exit_code'] == 0 for r in result['stages'])
        dependency_evidence = {str(p): sha(p) for p in (dependency_status, result_path)}
        env = os.environ.copy()
        env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8', OMP_NUM_THREADS='2',
                   OPENBLAS_NUM_THREADS='2', PYTHONUNBUFFERED='1')
        for label, name, args in STAGES:
            verify_inputs(); assert idle()
            for group in ('representative-coverage-20260919', 'symmetric-bridge-20260919'):
                assert not (ROOT/'research/preflop-evolution'/group/'running.lock').exists()
            started = time.monotonic()
            with (OUT/f'{PREFIX}-{label}.log').open('x') as log:
                child = subprocess.Popen([sys.executable, str(TD/name), *args], cwd=ROOT,
                    env=env, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                write_status('running', stage=label, worker_pid=child.pid)
                code = child.wait()
            records.append(dict(stage=label, exit_code=code, seconds=time.monotonic()-started))
            assert code == 0, f'{label} failed; preserved evidence, no retry'
            print(json.dumps(records[-1]), flush=True)
        verify_inputs()
        save(OUT/f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
            dependency_evidence=dependency_evidence, stages=records,
            seconds=time.monotonic()-began, accuracy_qualified=False,
            production_modified=False, scope='Execution completed; substantive result analysis still required.'))
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        write_status('stopped' if error else 'complete', error=error)


if __name__ == '__main__':
    main()
