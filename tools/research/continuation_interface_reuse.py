"""Exact-work removal experiment; no production calls or overlapping GPU jobs."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import datetime as dt
import json
import shutil
import subprocess
import sys
import numpy as np
import continuation_bridge_run as guard
import learned_interface as interface
import continuation_save_parity as save_parity

study=guard.study
OUT=study.ROOT/'research/preflop-evolution/continuation/interface-work-reuse-20260916'
BIN=study.ROOT/'target/learned-interface-filtered/release/examples/learned_interface.exe'
OLD=interface.OUT


def frozen():
    paths=[BIN,OLD/'interface.cu',study.night.OUT/'candidate.json',study.ROOT/'cache/preflop_eq169.bin',
        study.ROOT/'cache/realization_fit.json',study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop',
        study.ROOT/'crates/solver/src/preflop/gpu/learned_interface.rs',study.ROOT/'crates/solver/examples/learned_interface.rs']
    value=dict(files={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},production_enabled=False,
        scope='Identical frozen predictions; skip overwritten ordinary terminals and unused equity work. Runtime evidence alone cannot promote this predictor.')
    study.freeze(OUT/'manifest.json',value)
    return value


def command(args,log,optimized=True,warm=0):
    assert dt.datetime.now(dt.timezone.utc)<guard.DEADLINE,'Night-shift deadline reached'
    assert not guard.other_research(),'Another research controller or GPU child is alive'
    assert not study.night.live_busy(),'Live app is busy'
    env=dict(os.environ)
    env['PATH']=str(study.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    env['GTOPEN_INTERFACE_SKIP_REDUNDANT']='1' if optimized else '0'
    env['GTOPEN_INTERFACE_WARMUP']=str(warm)
    with log.open('w') as f:
        subprocess.run([str(BIN),*map(str,args)],cwd=study.ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)


def oracle():
    frozen();directory=OUT/'oracle';directory.mkdir(exist_ok=True)
    shutil.copyfile(OLD/'interface.cu',directory/'interface.cu')
    interface.OUT=directory;interface.BIN=BIN;interface.command=lambda args,log:command(args,log)
    interface.oracle()
    comparisons=[]
    for p in directory.glob('oracle-*.json'):
        if p.name=='oracle-check.json':continue
        old=study.read(OLD/p.name);new=study.read(p)
        assert new['plan']['optimization']['ordinary_equity_cache_after']==0
        assert old['config']==new['config']
        a=old['frontier']['rows'];b=new['frontier']['rows'];assert len(a)==len(b)
        maximum=0
        for x,y in zip(a,b):
            assert x['node']==y['node'] and x['actor']==y['actor']
            av=np.array([h['action_values_counterfactual_bb'] for h in x['hands']])
            bv=np.array([h['action_values_counterfactual_bb'] for h in y['hands']])
            maximum=max(maximum,float(np.max(abs(av-bv))))
        assert maximum<2e-6,(p.name,maximum)
        np.testing.assert_allclose(old['evs'],new['evs'],atol=2e-6,rtol=0)
        comparisons.append(dict(case=p.stem,max_action_change_bb=maximum,optimization=new['plan']['optimization']))
    assert len(comparisons)==12
    study.night.dump(OUT/'parity.json',dict(passed=True,cases=comparisons,
        independent_oracle=study.read(directory/'oracle-check.json'),production_enabled=False))


def benchmark():
    frozen();assert study.read(OUT/'parity.json')['passed']
    source=study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop'
    orders=[['original','control','filtered'],['filtered','original','control'],['control','filtered','original']]
    results=[]
    for repeat,order in enumerate(orders):
        for arm in order:
            folder=OUT/f'repeat-{repeat}'/arm;folder.mkdir(parents=True,exist_ok=True)
            path=folder/'iteration-150.json'
            if not path.exists():
                command(['solve',source,folder,'original' if arm=='original' else 'candidate',100,OLD/'interface.cu'],
                    folder/'run.log',optimized=arm=='filtered',warm=50)
            r=study.read(path)
            assert r['start_iteration']==50 and r['iteration']==150 and r['warmup_iterations']==50
            results.append(dict(repeat=repeat,arm=arm,seconds_per_iteration=r['learning_seconds']/100,
                setup_seconds=r['setup_seconds'],warmup_seconds=r['warmup_seconds'],total_seconds=r['total_seconds'],
                surrogate_gap=sum(r['gaps']),ev_sum=sum(r['evs']),sha256=study.pilot.sha(path)))
        a=study.read(OUT/f'repeat-{repeat}/control/iteration-150.json')
        b=study.read(OUT/f'repeat-{repeat}/filtered/iteration-150.json')
        assert a['config']==b['config']
        for x,y in zip(a['views'],b['views']):
            assert x['path']==y['path']
            np.testing.assert_allclose(x['view']['strategy'],y['view']['strategy'],atol=2e-6,rtol=0)
        np.testing.assert_allclose(a['evs'],b['evs'],atol=2e-5,rtol=0)
        full=save_parity.compare(OUT/f'repeat-{repeat}/control/policy.gtop',OUT/f'repeat-{repeat}/filtered/policy.gtop')
        study.night.dump(OUT/f'repeat-{repeat}/full-state-parity.json',full)
        assert full['all_numeric_entries_equal'],'Filtering changed the complete learning state'
        print('Repeat',repeat+1,'completed and policy parity passed',flush=True)
    medians={a:float(np.median([r['seconds_per_iteration'] for r in results if r['arm']==a])) for a in orders[0]}
    study.night.dump(OUT/'timing.json',dict(repeats=results,median_seconds_per_iteration=medians,
        speedup_vs_identical_predictor=medians['control']/medians['filtered'],overhead_vs_original=medians['filtered']/medians['original']-1,
        production_enabled=False,caveat='Same frozen older predictor; scheduling benchmark only. New accuracy candidates need their own combined accuracy/runtime checks. Frozen-value BR gaps do not certify full-game convergence.'))


if __name__=='__main__':{'freeze':frozen,'oracle':oracle,'benchmark':benchmark}[sys.argv[1]]()
