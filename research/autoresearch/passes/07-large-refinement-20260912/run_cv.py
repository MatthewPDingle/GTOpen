"""Registered GPU convergence screen; no concurrent hardware work."""
from run07 import *

if __name__=='__main__':
    run('cv-bench-build-v2',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_bench'])
    exe=LAB/'target/release/examples/convergence_bench.exe'
    fixture=HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    for seed in (42,314159):
        for refresh in (None,32,64):
            name=f'cv-six-{seed}-refresh{refresh or 0}'
            out=LAB/'target/convergence'/name
            env={} if refresh is None else {'CONVERGENCE_CV_REFRESH':str(refresh)}
            run(name,[exe,fixture,'gamma15','64',str(seed),'1000','25',out],600,[fixture],env)
            (RAW/f'{name}-result.json').write_bytes((out/'result.json').read_bytes())
