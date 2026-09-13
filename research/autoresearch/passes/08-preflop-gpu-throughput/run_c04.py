"""Serial C04 paired screen and conditional extended benchmark."""
import sys,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
def main():
    prerequisite=json.loads((run07.RAW/'c04-numerical-v1-exit.json').read_text())
    assert prerequisite['returncode']==0 and prerequisite['reason'] is None
    prefix=json.loads((run07.RAW/'c04-prefix-v2-exit.json').read_text())
    assert prefix['returncode']==0 and prefix['reason'] is None
    assert prefix['solver_source_files']==prerequisite['solver_source_files']
    assert '1 passed; 0 failed' in (run07.RAW/'c04-prefix-v2.log').read_text()
    for p,h in prerequisite['solver_source_files'].items():assert run07.digest(run07.LAB/p)==h,p
    log=(run07.RAW/'c04-numerical-v1.log').read_text()
    assert '3 passed; 0 failed; 1 ignored' in log
    exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    for pair in range(1,4):
        for fixture,save in [('large','eight-native-a'),('small','behavioral-fixed-e0-v1')]:
            for queue in ([False,True] if pair%2 else [True,False]):
                variant='candidate' if queue else 'control'; name=f'c04-{fixture}-{variant}-{pair}'
                source=run07.LAB/'target/convergence'/save/'final.gtop'
                eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
                out=run07.RAW/(name+'-bench.json')
                run07.run(name,[exe,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1'],180,
                    [source,eq,fit,HERE/'C04_PROTOCOL.md',exe],
                    {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1','PREFLOP_GPU_RLE':str(int(queue)),'REALIZATION_FIT':str(fit)})
            a=json.loads((run07.RAW/f'c04-{fixture}-control-{pair}-bench.json').read_text());b=json.loads((run07.RAW/f'c04-{fixture}-candidate-{pair}-bench.json').read_text())
            for k in ['input','nodes','iteration','initial_iteration','batch','cdf_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],(fixture,pair,k)
            assert len(a['rows'])==len(b['rows'])==6
            for x,y in zip(a['rows'],b['rows']):
                for k in ['index','iteration','warmup','gaps','evs']:assert x[k]==y[k],(fixture,pair,k)
            ratio=b['complete_seconds']/a['complete_seconds']
            print(json.dumps({'fixture':fixture,'pair':pair,'exact_checkpoints':True,'complete_ratio':ratio}),flush=True)
            if pair==1 and fixture=='large' and ratio>.99:
                verdict={'retained':False,'status':'Rejected - first-pair timing screen','ratio':ratio,'reason':'Less than 1% complete improvement; do not extend. Exact checkpoint and arena fingerprint agreement passed.'}
                (run07.RAW/'c04-verified.json').write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf-8');print(json.dumps(verdict),flush=True);return
    print('C04 paired benchmarks complete; independent verification and regressions required.',flush=True)
if __name__=='__main__':main()
