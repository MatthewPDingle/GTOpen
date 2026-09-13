"""D04 read-only cross-player overlap inventory; serial live-app guard."""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW = HERE/'raw'

def main():
    run07.run('d04-identity-v1', ['cargo','test','--release','-p','solver','--features','gpu,preflop-research',
        '--lib','cross_player_inventory_identity','--','--nocapture','--test-threads=1'], 240, [HERE/'D04_PROTOCOL.md'])
    log = (run07.RAW/'d04-identity-v1.log').read_text()
    assert '1 passed; 0 failed' in log
    exe = run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)', log).group(1)
    for fixture, save in [('small','behavioral-fixed-e0-v1'), ('large','eight-native-a')]:
        source = run07.LAB/'target/convergence'/save/'final.gtop'
        eq = run07.LAB/'cache/preflop_eq169.bin'; fit = run07.LAB/'cache/realization_fit.json'
        name = f'd04-{fixture}-v1'; out = run07.RAW/(name+'.json')
        run07.run(name, [exe,'preflop::gpu::cross_player_inventory::cross_player_inventory_from_saved_state',
            '--exact','--ignored','--nocapture','--test-threads=1'], 180,
            [source,eq,fit,HERE/'D04_PROTOCOL.md',exe], {'PREFLOP_GPU_REUSE_INPUT':str(source),
            'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_EQUITY':str(eq),
            'PREFLOP_GPU_LAYOUT_STATS':'1','REALIZATION_FIT':str(fit)})
        result = json.loads(out.read_text())
        print(json.dumps({'fixture':fixture,'best':result['best_pairing'],
            'admitted':result['admitted_pairing'] is not None}), flush=True)

if __name__ == '__main__': main()
