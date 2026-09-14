"""Compile once, then run one fixed native saved-game role at a time."""
import hashlib,json,re,shutil,sys
from pathlib import Path
from run_c23 import HERE,RAW,read,run07
from run_c07 import snapshot
stage=sys.argv[1];assert stage in ['build','control','candidate']
assert read(RAW/'c24-integration-verified.json')['admitted']
exe=run07.LAB/'target/c24-native-benchmark-frozen.exe'
inputs=[Path(__file__),HERE/'C24_PROTOCOL.md',HERE/'C24_TIMING.md',HERE/'c24_benchmark.rs.txt',HERE/'artifacts/c24-benchmark-source-map.json']
if stage=='build':
    name='c24-native-build-v1'
    run07.run(name,['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','--no-run'],300,inputs,{})
    log=(RAW/(name+'.log')).read_text(encoding='utf-8');match=re.search(r'Executable unittests .*?\(([^)]+\.exe)\)',log);assert match
    assert not exe.exists();shutil.copyfile(run07.LAB/match[1],exe)
    (RAW/'c24-native-frozen.json').write_text(json.dumps({'path':str(exe),'sha256':run07.digest(exe)},indent=2)+'\n')
else:
    fixture=read(RAW/'c24-user-fixture.json');source=Path(fixture['frozen']);assert run07.digest(source)==fixture['sha256']
    assert run07.digest(exe)==read(RAW/'c24-native-frozen.json')['sha256']
    if stage=='candidate':
        decision=read(RAW/'c24-native-screen-protocol.json');assert decision['baseline_verified'] and decision['rounds']==3 and decision['cap_seconds']==300
        inputs+=[RAW/'c24-native-screen-protocol.json']
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
    inputs += [source,exe,eq,fit,RAW/'c24-user-fixture.json']
    name=f'c24-current-{stage}-screen1';output=RAW/(name+'-bench.json')
    snapshot(name,'before')
    run07.run(name,[exe,'preflop::gpu::static_cdf::ordinary::tests::frozen_native_benchmark','--exact','--ignored','--nocapture','--test-threads=1'],300,inputs,
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(output),'PREFLOP_GPU_ORDINARY_STATIC_ENABLE':str(int(stage=='candidate')),
         'PREFLOP_GPU_ORDINARY_BUDGET':str(fixture['native_budget_mb']),'PREFLOP_GPU_ORDINARY_BATCH':str(fixture['expected_batch']),
         'PREFLOP_GPU_ORDINARY_ROUNDS':'3','PREFLOP_GPU_ORDINARY_STATIC_OUTPUT':str(RAW/'c24-native-artifacts-v1'),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after')
