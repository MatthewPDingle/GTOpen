"""Serial, preregistered repeat and schedule screen using the frozen pass-05 binary."""
from run_experiment import LAB, ROOT, HERE, run
import hashlib

EXE = LAB / 'target/followup-frozen-bin/convergence_bench_pass05.exe'
EXPECTED = '07d9ac1a4ecbf39d343cdb96eb3481d0d970b26da8279349e7016eb1466fe304'
EIGHT = ROOT / 'research/autoresearch/passes/03-preflop-20260910/user-session.json'
MODELED = ROOT / 'target/autoresearch/preflop-20260910/target/fixtures/fresh-coupled-validated.gtop'
SIX = HERE.parent / '05-preflop-convergence-20260911/six-solver.json'

jobs = [(f'followup-eight-s64-{seed}', EIGHT, 'dcfr', 64, seed, 2000, 50, 3600)
        for seed in (314159, 90210)]
jobs += [(f'followup-modeled-s64-{seed}', MODELED, 'dcfr', 64, seed, 1500, 50, 1800)
         for seed in (42, 314159)]
jobs += [(f'followup-six-gamma15-s{k}-{seed}', SIX, 'gamma15', k, seed, 1500, 25, 600)
         for k in (64, 128) for seed in (42, 314159, 90210)]

if __name__ == '__main__':
    for job in jobs:
        if hashlib.sha256(EXE.read_bytes()).hexdigest() != EXPECTED:
            raise RuntimeError('Frozen benchmark executable changed')
        run(*job, executable=EXE)
