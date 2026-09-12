"""Bounded GPU root-only repair; serial and guarded against live work."""
from run07 import *
if __name__ == '__main__':
    run('root-repair-tests-v1',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','root_repair_changes','--','--nocapture','--test-threads=1'],600)
    run('root-repair-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research',
        '--example','convergence_root_repair','--example','convergence_audit_paths'],600)
    exe=LAB/'target/release/examples/convergence_root_repair.exe'
    auditexe=LAB/'target/release/examples/convergence_audit_paths.exe'
    for variant in ('sampled','native'):
        source=LAB/f'target/convergence/large-eight-{variant}-compact-v1/final.gtop'
        name=f'large-eight-{variant}-root-repair-v1'
        out=LAB/'target/convergence'/name
        run(name,[exe,source,HERE/'broad-paths.json',out],600,[source,HERE/'broad-paths.json'])
        (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        run(name+'-broad',[auditexe,out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],
            600,[out/'final.gtop',HERE/'broad-paths.json'])
