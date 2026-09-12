"""Serial correctness regression checks, not CPU performance experiments."""
from run07 import *
if __name__=='__main__':
    run('default-solver-tests-v1',['cargo','test','--release','-p','solver'],1800)
    run('gpu-equivalence-tests-v1',['cargo','test','--release','--features','gpu','--test','gpu','--test','preflop_gpu','--','--test-threads=1'],1800)
