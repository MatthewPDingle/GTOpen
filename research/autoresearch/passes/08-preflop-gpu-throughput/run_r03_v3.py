"""Serial, guarded rollout qualification; never controls the production server."""
import json
import re
import shutil
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=HERE/'raw'

def main():
    stage=sys.argv[1]
    exe=run07.LAB/'target/r03-v3-qualification-frozen.exe'
    if stage=='freeze':
        record=json.loads((run07.RAW/'r03-selection-tests-v3-exit.json').read_text())
        log=(run07.RAW/'r03-selection-tests-v3.log').read_text()
        assert record['returncode']==0 and record['reason'] is None
        assert '3 passed; 0 failed; 1 ignored' in log
        source=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        assert not exe.exists();shutil.copyfile(source,exe);print(exe);return
    fixture,mode=stage.split(':')
    assert fixture in ['small','large'] and mode in ['retained','adaptive','normal','fallback']
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
    name=f'r03-v3-{fixture}-{mode}-v1';out=run07.RAW/(name+'.json')
    snapshot(name,'before')
    run07.run(name,[exe,'preflop::gpu::adaptive_throughput::tests::frozen_saved_game_continuation','--exact','--ignored','--nocapture','--test-threads=1'],240,
        [source,eq,fit,exe,HERE/'R03_PROTOCOL.md',Path(__file__)],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),
         'PREFLOP_GPU_ROLLOUT_MODE':mode,'REALIZATION_FIT':str(fit)})
    snapshot(name,'after')
    result=json.loads(out.read_text())
    print(json.dumps({k:result[k] for k in ['mode','selection','reload_selection','six_step_seconds','arena_fingerprint','continued_fingerprint']}),flush=True)

if __name__=='__main__':main()
