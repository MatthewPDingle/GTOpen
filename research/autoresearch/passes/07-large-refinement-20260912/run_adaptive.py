from run07 import *
if __name__=='__main__':
    run('adaptive-build-v3',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_refine_large','--example','convergence_audit_paths'])
    exe=LAB/'target/release/examples/convergence_refine_large.exe'
    auditexe=LAB/'target/release/examples/convergence_audit_paths.exe'
    for variant in ('sampled','native'):
        source=LAB/f'target/convergence/large-eight-{variant}-local1000/final.gtop'
        audit=RAW/f'large-eight-{variant}-local1000-broad.json'
        name=f'large-eight-{variant}-adaptive-v3'
        out=LAB/'target/convergence'/name
        planout=LAB/'target/convergence'/(name+'-inventory')
        run(name+'-inventory',[exe,source,audit,'0',planout],180,[source,audit])
        (RAW/(name+'-inventory.json')).write_bytes((planout/'plan.json').read_bytes())
        run(name+'-before',[auditexe,source,HERE/'broad-paths.json',RAW/(name+'-before.json')],600,[source,HERE/'broad-paths.json'])
        run(name,[exe,source,audit,'4000',out],3600,[source,audit],{'CONVERGENCE_REFINE_ADAPTIVE':'1'})
        (RAW/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
        (RAW/(name+'-plan.json')).write_bytes((out/'plan.json').read_bytes())
        run(name+'-broad',[auditexe,out/'final.gtop',HERE/'broad-paths.json',RAW/(name+'-broad.json')],600,[out/'final.gtop',HERE/'broad-paths.json'])
    run('default-solver-tests-v1',['cargo','test','--release','-p','solver'],1800)
    run('gpu-equivalence-tests-v1',['cargo','test','--release','--features','gpu','--test','gpu','--test','preflop_gpu','--','--test-threads=1'],1800)
