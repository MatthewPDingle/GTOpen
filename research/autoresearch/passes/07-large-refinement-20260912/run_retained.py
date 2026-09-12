"""Retained-history comparison; run only after joint-v1 is terminal."""
from run07 import *
if __name__ == '__main__':
    for variant in ('sampled', 'native'):
        record=json.loads((RAW/f'large-eight-{variant}-joint-v1-broad-exit.json').read_text())
        if record['returncode'] or record['reason']:
            raise RuntimeError('Baseline final audit must complete before hardware reuse')
    run('retained-history-tests-v1', ['cargo','test','--release','-p','solver','--features',
        'preflop-research','--lib','convergence_','--','--nocapture','--test-threads=1'], 900)
    run('retained-history-build-v1', ['cargo','build','--release','-p','solver','--features',
        'preflop-research','--example','convergence_joint_refine','--example','convergence_audit_paths'])
    exe=LAB/'target/release/examples/convergence_joint_refine.exe'
    auditexe=LAB/'target/release/examples/convergence_audit_paths.exe'
    for variant in ('sampled','native'):
        source=LAB/f'target/convergence/large-eight-{variant}-compact-v1/final.gtop'
        name=f'large-eight-{variant}-joint-retained-v1'
        out=LAB/'target/convergence'/name
        run(name,[exe,source,HERE/'broad-paths.json',out],2400,[source,HERE/'broad-paths.json'],
            {'CONVERGENCE_RETAIN_ANCESTOR_HISTORY':'1'})
        (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        run(name+'-broad',[auditexe,out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],
            600,[out/'final.gtop',HERE/'broad-paths.json'])
