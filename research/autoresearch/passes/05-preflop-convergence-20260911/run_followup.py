from run_experiment import run, HERE
import os
if __name__ == '__main__':
    for name,schedule,samples,seed in [
        ('six-native-b','native',1024,42),
        ('six-s128-b','dcfr',128,314159),('six-s128-c','dcfr',128,90210),
        ('six-s64-a','dcfr',64,42),('six-hs15-s128-a','hs15',128,42),
        ('six-gamma15-a','gamma15',1024,42)]:
        run(name,HERE/'six-solver.json',schedule,samples,seed,1000,25,1800)
    os.environ['CONVERGENCE_TARGET']='0.0001'
    run('six-reference-tight-a',HERE/'six-solver.json','native',1024,42,3000,100,1800)
