"""Run after verify_constraints.py passes; full-particle compact GPU comparison."""
from run07 import *
if __name__=='__main__':
    evidence=RAW/'research-constraints-tests-v1-exit.json'
    if not evidence.exists() or json.loads(evidence.read_text()).get('returncode')!=0:
        raise RuntimeError('Compact numerical/constraint tests must pass first')
    run('compact-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_refine_large','--example','convergence_audit_paths'])
    exe=LAB/'target/release/examples/convergence_refine_large.exe'
    auditexe=LAB/'target/release/examples/convergence_audit_paths.exe'
    for variant in ('sampled','native'):
        source=LAB/f'target/convergence/large-eight-{variant}-local1000/final.gtop'
        audit=RAW/f'large-eight-{variant}-local1000-broad.json'
        name=f'large-eight-{variant}-compact-v1'
        out=LAB/'target/convergence'/name
        run(name,[exe,source,audit,'4000',out],3600,[source,audit],{'CONVERGENCE_REFINE_ADAPTIVE':'1','CONVERGENCE_REFINE_ENGINE':'gpu'})
        (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        (RAW/(name+'-plan.json')).write_bytes((out/'plan.json').read_bytes())
        run(name+'-broad',[auditexe,out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],600,[out/'final.gtop',HERE/'broad-paths.json'])
