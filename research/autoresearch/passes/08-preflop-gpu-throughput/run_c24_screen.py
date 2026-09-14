"""Bounded C24 GPU prefix/hand qualification, guarded against user work."""
from pathlib import Path
from run_c23 import HERE,RAW,read,run07
assert read(RAW/'d20-verified.json')['admitted']
name='c24-static-v1'
run07.run(name,['cargo','test','--release','-p','solver','--features','gpu,preflop-research',
    '--lib','preflop::gpu::static_cdf::c24_four_sample_prefixes_and_hands',
    '--','--exact','--ignored','--nocapture','--test-threads=1'],300,
    [Path(__file__),HERE/'C24_PROTOCOL.md',HERE/'prepare_c24.py',HERE/'artifacts/c24-source-map.json',RAW/'d20-verified.json'],
    {'PREFLOP_GPU_STATIC_CDF_OUTPUT':str(RAW/name)})
r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None
