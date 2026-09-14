"""Saved-fixture continuation through the frozen normal-selection path."""
import sys
from pathlib import Path
from run_c23 import HERE, RAW, read, run07
from run_c07 import snapshot

fixture=sys.argv[1];assert fixture in ['small','large']
assert read(RAW/'r04-overhead-verified.json')['passed']
run07.idle()
source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
exe=run07.LAB/'target/r04-benchmark-frozen.exe';eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
name=f'r04-{fixture}-adaptive-v1';out=RAW/(name+'.json')
snapshot(name,'before')
run07.run(name,[exe,'preflop::gpu::adaptive_throughput::tests::frozen_saved_game_continuation','--exact','--ignored','--nocapture','--test-threads=1'],180,
    [exe,source,eq,fit,HERE/'R04_PROTOCOL.md',Path(__file__),RAW/'r04-initial-verified.json'],
    {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_ROLLOUT_MODE':'adaptive','REALIZATION_FIT':str(fit)})
snapshot(name,'after');r=read(RAW/(name+'-exit.json'))
assert r['returncode']==0 and r['reason'] is None
