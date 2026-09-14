"""Guarded initial R04 normal-selection qualification."""
import sys
from pathlib import Path
from run_c23 import HERE, RAW, read, run07

stage=sys.argv[1]
commands={
    'selection':['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','adaptive_throughput::tests::','--','--nocapture','--test-threads=1'],
    'cohorts':['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','cohort_reuse::tests::','--','--nocapture','--test-threads=1'],
    'native':['cargo','test','--release','-p','solver','--features','gpu','--test','gpu','--test','preflop_gpu','--test','preflop_throughput','--','--test-threads=1'],
}
run07.run('r04-'+stage+'-v1',commands[stage],300,
    [Path(__file__),HERE/'R04_PROTOCOL.md',HERE/'prepare_r04.py',HERE/'artifacts/r04-before-source-map.json'],
    {'PREFLOP_GPU_STATIC_CDF_INTEGRATED_OUTPUT':str(RAW/'r04-integrated-v1')})
r=read(RAW/('r04-'+stage+'-v1-exit.json'))
assert r['returncode']==0 and r['reason'] is None
