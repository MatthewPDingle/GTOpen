"""Guarded GPU correctness queue. Run only when previous workload is terminal."""
from run07 import *
if __name__=='__main__':
    run('research-constraints-tests-v1',['cargo','test','--release','-p','solver','--features','preflop-research','--lib','convergence_','--','--test-threads=1','--nocapture'],600)
    run('cv-numerical-v2',['cargo','test','--release','-p','solver','--features','preflop-research','--lib','cv_research::tests','--','--test-threads=1','--nocapture'],600)
