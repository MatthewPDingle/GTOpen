"""Registered alternating upstream/downstream GPU experiment."""
from run07 import *
if __name__ == '__main__':
    for test in ('ancestor-tests-v3', 'default-solver-tests-v1', 'gpu-equivalence-tests-v1'):
        record = json.loads((RAW / (test + '-exit.json')).read_text())
        if record['returncode'] or record['reason']:
            raise RuntimeError('Required correctness check failed: ' + test)
    run('joint-build-v1', ['cargo', 'build', '--release', '-p', 'solver', '--features',
        'preflop-research', '--example', 'convergence_joint_refine', '--example', 'convergence_audit_paths'])
    exe = LAB / 'target/release/examples/convergence_joint_refine.exe'
    auditexe = LAB / 'target/release/examples/convergence_audit_paths.exe'
    for variant in ('sampled', 'native'):
        source = LAB / f'target/convergence/large-eight-{variant}-compact-v1/final.gtop'
        name = f'large-eight-{variant}-joint-v1'
        out = LAB / 'target/convergence' / name
        run(name, [exe, source, HERE / 'broad-paths.json', out], 2400,
            [source, HERE / 'broad-paths.json'])
        (RAW / (name + '-result.json')).write_bytes((out / 'result.json').read_bytes())
        run(name + '-broad', [auditexe, out / 'final.gtop', HERE / 'broad-paths.json',
            RAW / (name + '-broad.json')], 600, [out / 'final.gtop', HERE / 'broad-paths.json'])
