"""Parallel range descriptors without changing the frozen conditional model."""
import importlib.util
import sys
import numpy as np
import continuation_interface_reuse as runtime
import continuation_save_parity as saves
import continuation_moment_evaluation as ownership

study=runtime.study
OUT=study.ROOT/'research/preflop-evolution/continuation/warp-summary-20260916'


def source(original,helper):
    start=original.index(' if(threadIdx.x<2){int s=threadIdx.x;for(int j=0;j<5;j++)desc')
    end=original.index(' for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169;double den=0.,num=0.;',start)
    result=original[:start]+' if(threadIdx.x<64)describe_warp(threadIdx.x/32,threadIdx.x%32,d,desc,summary);\n'+original[end:]
    marker='typedef unsigned int u32;'
    assert result.count(marker)==1
    return result.replace(marker,marker+'\n'+helper)


def export():
    original=runtime.OLD/'interface.cu'
    helper=study.ROOT/'tools/research/continuation_warp_summary.cuh'
    generated=source(original.read_text(),helper.read_text())
    destination=OUT/'interface.cu';OUT.mkdir(exist_ok=True)
    if destination.exists():assert destination.read_bytes()==generated.encode()
    else:destination.write_bytes(generated.encode())
    paths=[original,helper,destination,OUT/'README.md',runtime.BIN,
        study.night.OUT/'candidate.json',study.ROOT/'cache/preflop_eq169.bin',
        study.ROOT/'cache/realization_fit.json',
        study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop',
        study.ROOT/'tools/research/continuation_warp_summary.py',
        study.ROOT/'tools/research/continuation_interface_reuse.py',
        study.ROOT/'tools/research/continuation_moment_evaluation.py',
        study.ROOT/'tools/research/continuation_save_parity.py',
        study.ROOT/'tools/research/learned_interface.py']
    study.freeze(OUT/'manifest.json',dict(files={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},
        production_enabled=False,note='Unchanged old conditional model; only order of range-statistic reduction differs.'))


def command(args,log,optimized=True,warm=0):
    ownership.require_queue_idle()
    return runtime.command(args,log,optimized=optimized,warm=warm)


def oracle():
    export();ownership.require_queue_idle()
    spec=importlib.util.spec_from_file_location('_warp_oracle',runtime.interface.__file__)
    driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
    driver.OUT=OUT;driver.BIN=runtime.BIN;driver.command=command
    driver.oracle()
    result=study.read(OUT/'oracle-check.json')
    assert result['passed'] and len(result['tests'])==12
    assert max(row['max_action_error_bb'] for row in result['tests'])<2e-6
    study.freeze(OUT/'strict-oracle-check.json',dict(passed=True,action_tolerance_bb=2e-6,
        maximum_action_error_bb=max(row['max_action_error_bb'] for row in result['tests']),production_enabled=False))


def compare(left,right):
    a=saves.inspect(left);b=saves.inspect(right)
    assert a[:2]==b[:2] and len(a[2])==len(b[2])
    rows=[]
    for x,y in zip(a[2],b[2]):
        assert x['name']==y['name'] and x['count']==y['count']
        changed=0;maximum=0.;worst=0.
        if x['count']:
            u=np.memmap(left,mode='r',dtype='<f4',offset=x['offset'],shape=(x['count'],))
            v=np.memmap(right,mode='r',dtype='<f4',offset=y['offset'],shape=(y['count'],))
            for start in range(0,x['count'],1048576):
                p=u[start:start+1048576].astype(float);q=v[start:start+1048576].astype(float)
                assert np.isfinite(p).all() and np.isfinite(q).all()
                error=abs(p-q);limit=1e-6+1e-5*np.maximum(abs(p),abs(q))
                changed+=int(np.count_nonzero(error));maximum=max(maximum,float(error.max()))
                worst=max(worst,float((error/limit).max()))
            del p,q,u,v
        rows.append(dict(arena=x['name'],entries=x['count'],changed=changed,max_absolute_change=maximum,worst_tolerance_ratio=worst))
    return dict(passed=all(r['worst_tolerance_ratio']<=1 for r in rows),all_numeric_entries_equal=all(r['changed']==0 for r in rows),
        arenas=rows,absolute_tolerance=1e-6,relative_tolerance=1e-5)


def benchmark():
    export();assert study.read(OUT/'strict-oracle-check.json')['passed'];ownership.require_queue_idle()
    saved=study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop'
    orders=[['original','control','warp'],['warp','original','control'],['control','warp','original']];results=[]
    for repeat,order in enumerate(orders):
        for arm in order:
            folder=OUT/f'repeat-{repeat}'/arm;folder.mkdir(parents=True,exist_ok=True)
            path=folder/'iteration-150.json'
            if not path.exists():
                kernel=(OUT if arm=='warp' else runtime.OLD)/'interface.cu'
                command(['solve',saved,folder,'original' if arm=='original' else 'candidate',100,kernel],
                    folder/'run.log',optimized=arm!='original',warm=50)
            row=study.read(path)
            assert row['start_iteration']==row['warmup_iterations']==50 and row['iteration']==150
            results.append(dict(repeat=repeat,arm=arm,seconds_per_iteration=row['learning_seconds']/100,
                setup_seconds=row['setup_seconds'],warmup_seconds=row['warmup_seconds'],sha256=study.pilot.sha(path)))
        control=OUT/f'repeat-{repeat}/control';candidate=OUT/f'repeat-{repeat}/warp'
        a=study.read(control/'iteration-150.json');b=study.read(candidate/'iteration-150.json')
        assert a['config']==b['config'] and len(a['views'])==len(b['views'])
        for x,y in zip(a['views'],b['views']):
            assert x['path']==y['path']
            np.testing.assert_allclose(x['view']['strategy'],y['view']['strategy'],atol=1e-4,rtol=0)
        np.testing.assert_allclose(a['evs'],b['evs'],atol=2e-5,rtol=0)
        parity=compare(control/'policy.gtop',candidate/'policy.gtop')
        study.night.dump(OUT/f'repeat-{repeat}/full-state-comparison.json',parity);assert parity['passed']
        if repeat:
            stable=saves.compare(OUT/'repeat-0/warp/policy.gtop',candidate/'policy.gtop')
            study.night.dump(OUT/f'repeat-{repeat}/repeat-parity.json',stable);assert stable['all_numeric_entries_equal']
        print('Warp-summary repeat',repeat+1,'passed',flush=True)
    medians={arm:float(np.median([r['seconds_per_iteration'] for r in results if r['arm']==arm])) for arm in orders[0]}
    study.night.dump(OUT/'timing.json',dict(repeats=results,median_seconds_per_iteration=medians,
        speedup_vs_filtered_control=medians['control']/medians['warp'],overhead_vs_original=medians['warp']/medians['original']-1,
        within_runtime_target=medians['warp']<=1.1*medians['original'],production_enabled=False,
        caveat='Same old predictor, different summation order. Does not qualify its accuracy or full-game convergence.'))


if __name__=='__main__':{'export':export,'oracle':oracle,'benchmark':benchmark}[sys.argv[1]]()
