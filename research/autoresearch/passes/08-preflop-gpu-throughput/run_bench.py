"""Serial paired fixed-work benchmarks; no source changes while active."""
from pathlib import Path
import sys,json,re,statistics
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'

def main():
    prereq=json.loads((run07.RAW/'c01-numerical-v1-exit.json').read_text())
    assert prereq['returncode']==0 and prereq['reason'] is None
    for p,h in prereq['solver_source_files'].items():assert run07.digest(run07.LAB/p)==h,p
    log=(run07.RAW/'c01-numerical-v1.log').read_text()
    assert '2 passed; 0 failed; 1 ignored' in log
    exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    cases={'large':'eight-native-a','small':'behavioral-fixed-e0-v1'}
    for pair in range(1,4):
        for label,save in cases.items():
            # Alternate order to reduce drift bias.
            for enabled in ([False,True] if pair%2 else [True,False]):
                variant='candidate' if enabled else 'control'
                name=f'c01-{label}-{variant}-{pair}'
                source=run07.LAB/'target/convergence'/save/'final.gtop'
                out=run07.RAW/(name+'-bench.json')
                eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
                run07.run(name,[exe,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark',
                    '--exact','--ignored','--nocapture','--test-threads=1'],180,
                    [source,eq,fit,HERE/'program.md',HERE/'D01_RESULTS.md',exe],
                    {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),
                     'PREFLOP_GPU_REUSE_ENABLE':str(int(enabled)),'REALIZATION_FIT':str(fit)})
            a=json.loads((run07.RAW/f'c01-{label}-control-{pair}-bench.json').read_text())
            b=json.loads((run07.RAW/f'c01-{label}-candidate-{pair}-bench.json').read_text())
            for key in ['nodes','iteration','initial_iteration','batch','cdf_bytes','arena_entries','arena_fingerprint']:
                assert a[key]==b[key],(label,pair,key)
            for x,y in zip(a['rows'],b['rows']):
                for key in ['index','warmup','iteration','gaps','evs']:assert x[key]==y[key],(label,pair,key)
            print(json.dumps(dict(pair=pair,fixture=label,numerical_match=True,
                complete_ratio=b['complete_seconds']/a['complete_seconds'])),flush=True)
    print('All paired runs complete; independent verification and retention decision required.',flush=True)

if __name__=='__main__':main()
