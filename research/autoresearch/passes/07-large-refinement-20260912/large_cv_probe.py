"""One-iteration storage/runtime probe, not a convergence result."""
from run07 import *
if __name__=='__main__':
    fixture=Path('T:/Dev/GTOpen/research/autoresearch/passes/03-preflop-20260910/user-session.json')
    run('cv-eight-storage-probe',[LAB/'target/release/examples/convergence_bench.exe',fixture,'gamma15','64','42','1','1',LAB/'target/convergence/cv-eight-storage-probe'],180,[fixture],{'CONVERGENCE_CV_REFRESH':'32'})
