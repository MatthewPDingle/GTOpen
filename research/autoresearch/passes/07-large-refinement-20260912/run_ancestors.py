"""Full-particle GPU upstream repair, with fresh unrestricted evaluations."""
from run07 import *
if __name__=='__main__':
    record=json.loads((RAW/'ancestor-tests-v3-exit.json').read_text())
    if record['returncode']!=0 or record['reason']:raise RuntimeError('ancestor correctness tests must pass')
    run('ancestor-build-v2',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_repair_ancestors','--example','convergence_audit_paths'])
    exe=LAB/'target/release/examples/convergence_repair_ancestors.exe'
    auditexe=LAB/'target/release/examples/convergence_audit_paths.exe'
    for variant in ('sampled','native'):
        source=LAB/f'target/convergence/large-eight-{variant}-compact-v1/final.gtop'
        name=f'large-eight-{variant}-ancestors-v2'
        out=LAB/'target/convergence'/name
        run(name,[exe,source,HERE/'broad-paths.json','100',out],1200,[source,HERE/'broad-paths.json'])
        (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        run(name+'-broad',[auditexe,out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],600,[out/'final.gtop',HERE/'broad-paths.json'])
