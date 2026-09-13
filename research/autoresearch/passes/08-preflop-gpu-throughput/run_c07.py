"""C07 guarded allocation validation and first paired timing screen."""
import json,re,shutil,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'

def snapshot(name,side):
    out=run07.RAW/(name+'-gpu-'+side+'.json');assert not out.exists()
    command=['nvidia-smi','--query-gpu=timestamp,name,memory.total,memory.used,memory.free,clocks.sm,clocks.mem,pstate,power.draw,temperature.gpu','--format=csv']
    try:
        r=subprocess.run(command,capture_output=True,text=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
        data=dict(time=time.time(),command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
    except Exception as e:data=dict(time=time.time(),command=command,error=str(e))
    out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')

def run(name,fixture,layout=False,enabled=True):
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
    exe=run07.LAB/'target/c07-benchmark-frozen.exe'
    out=run07.RAW/(name+('.json' if layout else '-bench.json'))
    test='preflop::gpu::cohort_reuse::tests::cohort_constructor_from_saved_state' if layout else 'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark'
    snapshot(name,'before')
    run07.run(name,[exe,test,'--exact','--ignored','--nocapture','--test-threads=1'],180,
        [source,eq,fit,exe,HERE/'C07_PROTOCOL.md'],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
         'PREFLOP_GPU_COHORT_ENABLE':str(int(enabled)),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after')
    return json.loads(out.read_text())

def main():
    stage=sys.argv[1]
    if stage=='layouts':
        record=json.loads((run07.RAW/'c07-numerical-v1-exit.json').read_text())
        assert record['returncode']==0 and record['reason'] is None
        log=(run07.RAW/'c07-numerical-v1.log').read_text();assert '4 passed; 0 failed; 1 ignored' in log
        exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        frozen=run07.LAB/'target/c07-benchmark-frozen.exe';assert not frozen.exists();shutil.copyfile(exe,frozen)
        for fixture in ['small','large']:run('c07-'+fixture+'-layout-v1',fixture,layout=True)
    elif stage=='screen':
        from check_c07 import check_layouts
        check_layouts()
        a=run('c07-large-control-1','large',enabled=False)
        b=run('c07-large-candidate-1','large')
        for k in ['input','nodes','initial_iteration','iteration','batch','arena_entries','arena_fingerprint','original_cdf_bytes']:assert a[k]==b[k],k
        for x,y in zip(a['rows'],b['rows']):
            for k in ['gaps','evs','index','warmup','iteration']:assert x[k]==y[k],k
        ratio=b['complete_seconds']/a['complete_seconds']
        print(json.dumps(dict(first_pair_ratio=ratio,passed_screen=ratio<.99,numerical_equal=True)),flush=True)
    elif stage=='extended':
        from check_c07 import check_layouts
        check_layouts()
        a=json.loads((run07.RAW/'c07-large-control-1-bench.json').read_text())
        b=json.loads((run07.RAW/'c07-large-candidate-1-bench.json').read_text())
        assert b['complete_seconds']/a['complete_seconds']<.99
        for fixture,pairs in [('large',[2,3]),('small',[1,2,3])]:
            for pair in pairs:
                result={}
                for enabled in ([True,False] if pair%2==0 else [False,True]):
                    role='candidate' if enabled else 'control'
                    result[role]=run(f'c07-{fixture}-{role}-{pair}',fixture,enabled=enabled)
                a,b=result['control'],result['candidate']
                assert a['arena_fingerprint']==b['arena_fingerprint']
                for x,y in zip(a['rows'],b['rows']):
                    for k in ['gaps','evs','index','warmup','iteration']:assert x[k]==y[k],k
                print(json.dumps(dict(fixture=fixture,pair=pair,ratio=b['complete_seconds']/a['complete_seconds'],numerical_equal=True)),flush=True)
    else:raise ValueError(stage)
if __name__=='__main__':main()
