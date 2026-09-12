"""GPU global consistency experiment after compact branch refinement."""
from run07 import *
if __name__=='__main__':
    run('research-constraints-tests-v2',['cargo','test','--release','-p','solver','--features','preflop-research','--lib','convergence_','--','--test-threads=1','--nocapture'],600)
    run('reconcile-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_bench','--example','convergence_audit_paths'])
    exe=LAB/'target/release/examples/convergence_bench.exe'
    auditexe=LAB/'target/release/examples/convergence_audit_paths.exe'
    for variant in ('sampled','native'):
        source=LAB/f'target/convergence/large-eight-{variant}-compact-v1/final.gtop'
        name=f'large-eight-{variant}-reconcile-v1'
        out=LAB/'target/convergence'/name
        run(name,[exe,source,'gamma15','64','42','500','50',out],1200,[source],{'CONVERGENCE_RESTART_AVERAGE':'1'})
        (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        run(name+'-broad',[auditexe,out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],600,[out/'final.gtop',HERE/'broad-paths.json'])
