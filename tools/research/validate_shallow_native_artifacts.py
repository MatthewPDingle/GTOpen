"""Verify frozen inputs, completed references and published research artifacts."""
import hashlib
import subprocess
import shallow_native_feedback as study


def validate():
    m = study.checked()
    e = study.read(study.OUT / 'evaluation.json')
    assert e['manifest_id'] == m['id']
    for j in m['jobs']:
        path = study.OUT / 'jobs' / (j['id'] + '.json')
        row = study.read(path)
        study.native.previous.old.validate(row, j, m)
        assert study.pilot.sha(path) == e['job_sha256'][j['id']]
    audit = study.read(study.OUT / 'dependency-audit.json')
    for d in audit['dependencies']:
        committed = subprocess.check_output(['git', 'show', audit['baseline_commit'] + ':' + d['path']], cwd=study.ROOT)
        assert hashlib.sha256(committed).hexdigest() == d['sha256'] == study.pilot.sha(study.ROOT / d['path'])
    assert study.read(study.OUT / 'call-interim.json')['report'] == e['leaf_reports']['call']
    for name in ['probe-check.json', 'guard-check.json', 'tree-boundary-check.json']:
        assert study.read(study.OUT / name)['passed'], name
    assert all(s['passed'] for s in study.read(study.OUT / 'stability.json').values())
    failed = [k for k, v in e['gates'].items() if not v]
    assert failed == ['call_vs_raise_direct_nonregression']
    assert not e['primary_feedback_pass'] and not e['production_enabled']
    diagnostic = study.read(study.OUT / 'branch-diagnostic.json')
    assert diagnostic['manifest_id'] == m['id']
    assert max(v['reconstruction_error_bb'] for v in diagnostic['estimators'].values()) < 1e-10
    result = dict(checked_at=study.now(), manifest_id=m['id'], passed=True,
                  reference_jobs_verified=len(m['jobs']), supplemental_dependencies_verified=len(audit['dependencies']),
                  interim_matches_final=True, correctness_and_stability_passed=True,
                  primary_accuracy_screen_passed=False, failed_accuracy_gates=failed,
                  note='Artifact validity and numerical correctness passed; the primary accuracy screen did not.',
                  production_enabled=False,
                  artifact_sha256={p.name: study.pilot.sha(p) for p in study.OUT.iterdir()
                                   if p.is_file() and p.name != 'validation.json'})
    study.write(study.OUT / 'validation.json', result)
    print('Verified frozen sources, all 150 reference labels, numerical checks and failed-screen reporting.')


if __name__ == '__main__':
    validate()
