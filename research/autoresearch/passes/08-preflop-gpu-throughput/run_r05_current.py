"""Qualify normal app selection on the frozen batch-four game, without live mutations."""
from pathlib import Path
from run_c23 import HERE,RAW,read,run07
from run_c07 import snapshot
source=Path(read(RAW/'c24-user-fixture.json')['frozen'])
exe=run07.LAB/'target/r05-test-frozen.exe'
assert run07.digest(exe)==read(RAW/'r05-test-frozen.json')['sha256']
name='r05-current-v1';out=RAW/(name+'.json')
snapshot(name,'before')
run07.run(name,[exe,'preflop::gpu::static_cdf::ordinary::tests::frozen_native_benchmark','--exact','--ignored','--nocapture','--test-threads=1'],600,
 [Path(__file__),HERE/'R05_PROTOCOL.md',exe,source],
 {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_ORDINARY_STATIC_ENABLE':'1',
  'PREFLOP_GPU_ORDINARY_BUDGET':'23911','PREFLOP_GPU_ORDINARY_BATCH':'4','PREFLOP_GPU_ORDINARY_ROUNDS':'6',
  'PREFLOP_GPU_ORDINARY_ROLLOUT':'1','PREFLOP_GPU_ORDINARY_STATIC_OUTPUT':str(RAW/'r05-current-artifacts-v1'),
  'REALIZATION_FIT':str(run07.LAB/'cache/realization_fit.json')})
snapshot(name,'after')
x=read(out);old=read(RAW/'c24-current-candidate-full1-bench.json')
for key in ['input','nodes','initial_iteration','iteration','batch','budget_mb','hu_cache','samples','initial_buffers','final_buffers','final_device_bytes','arena_entries','arena_fingerprint','static_cdf']:assert x[key]==old[key],key
assert len(x['rows'])==len(old['rows'])==6
for a,b in zip(x['rows'],old['rows']):
 for key in ['index','iteration','warmup','gaps','evs']:assert a[key]==b[key],key
assert x['selection']['mode']=='normal_gpu' and x['selection']['static_cdf'] and x['selection']['static_cdf_fallback_reason'] is None
print('Current saved game: production selection, all six checkpoints and full arenas exactly match retained C24.',flush=True)
