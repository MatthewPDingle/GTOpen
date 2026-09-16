"""Float32 neural accumulations with double feature normalization and centering."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import importlib.util
import sys
from types import SimpleNamespace
import numpy as np
import continuation_shrunk_gpu as double
import continuation_policy_transfer as transfer

study=double.study
runtime=double.runtime
OUT=double.OUT.parent/'shrunk-mixed-gpu-20260916'


def float_literal(value):
    text=format(float(np.float32(value)),'.9g')
    return text+('' if '.' in text or 'e' in text else '.0')+'f'


def neural_block(model):
    base=model['base'];expressions=double.terms(base)
    weights=np.concatenate([np.array(n['weight']) for n in model['networks']],axis=1)
    bias=np.concatenate([np.array(n['bias']) for n in model['networks']])
    output=np.concatenate([np.array(n['output'])/2 for n in model['networks']])
    assert weights.shape==(104,16) and model['residual_scale']==.75
    lines=[f' float nn{i}={float_literal(v)};' for i,v in enumerate(bias)]
    for k,term in enumerate(expressions):
        lines.append(f' {{float clipped=(float)fmin(6.,fmax(-6.,(({term})-({base["mean"][k]:.17g}))/({base["scale"][k]:.17g})));')
        for i in range(16):
            lines.append(f' nn{i}+=clipped*({float_literal(weights[k,i])});')
        lines.append(' }')
    expression='+'.join(f'(fmaxf(0.f,nn{i})*({float_literal(v)}))' for i,v in enumerate(output))
    return '\n'.join(lines)+'\n',expression


def simulated(c,model):
    base=model['base'];encoded=study.fit.features(c,base['encoder'])
    z=np.clip((encoded['x']-base['mean'])/base['scale'],-6,6).astype(np.float32)
    weights=np.concatenate([np.array(n['weight']) for n in model['networks']],axis=1).astype(np.float32)
    bias=np.concatenate([np.array(n['bias']) for n in model['networks']]).astype(np.float32)
    output=np.concatenate([np.array(n['output'])/2 for n in model['networks']]).astype(np.float32)
    # Explicitly round after each operation, a conservative non-FMA CPU path.
    hidden=np.broadcast_to(bias,z.shape[:-1]+bias.shape).copy()
    for k in range(104):hidden+=z[...,k,None]*weights[k]
    raw=np.zeros(z.shape[:-1],dtype=np.float32)
    for i in range(16):raw+=np.maximum(hidden[...,i],np.float32(0))*output[i]
    raw=raw.astype(float)
    return study.fit.predict(c,base)+raw-(raw*c['mass']).sum()/2


def export():
    double.export();path=double.shrunk.OUT/'candidate.json';model=study.read(path)
    template=(study.ROOT/'tools/research/learned_interface_kernel.cu').read_text()
    marker='  correction[x]=__FEATURE_EXPRESSION__;';assert template.count(marker)==1
    block,neural=neural_block(model);base=double.encoder.expression(dict(model['base'],production_enabled=False))
    serial='// Frozen N15 model; float32 neural arithmetic only.\n'+template.replace(marker,block+'  correction[x]=('+base+')+(double)('+neural+');')
    helper=(study.ROOT/'tools/research/continuation_warp_summary.cuh').read_text()
    files=[OUT/'README.md',study.ROOT/'tools/research/continuation_shrunk_mixed_gpu.py',
        study.ROOT/'tools/research/continuation_policy_transfer.py',double.OUT/'manifest.json']
    hashes=dict(study.read(double.OUT/'manifest.json')['files'])
    for name,source in dict(serial=serial,warp=double.warp.source(serial,helper)).items():
        folder=OUT/name;folder.mkdir(parents=True,exist_ok=True);target=folder/'interface.cu'
        if target.exists():assert target.read_bytes()==source.encode()
        else:target.write_bytes(source.encode())
        files.append(target)
    hashes.update({str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in files})
    study.freeze(OUT/'manifest.json',dict(files=hashes,candidate_sha256=study.pilot.sha(path),production_enabled=False))


def command(args,log,optimized=True,warm=0):
    double.qualified();transfer.require_idle()
    for p in transfer.queue.processes():
        if p['ProcessId']!=os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(x in (p['CommandLine'] or '').lower() for x in ['continuation_shrunk_mixed_gpu.py oracle',
                'continuation_shrunk_mixed_gpu.py benchmark']),'Another mixed-precision GPU controller is active'
    return runtime.command(args,log,optimized=optimized,warm=warm)


def oracle():
    export();double.qualified();assert study.read(double.OUT/'oracle-check.json')['passed']
    differences=[]
    for variant in ['serial','warp']:
        directory=OUT/('oracle-'+variant);directory.mkdir(exist_ok=True)
        source=(OUT/variant/'interface.cu').read_bytes();target=directory/'interface.cu'
        if target.exists():assert target.read_bytes()==source
        else:target.write_bytes(source)
        spec=importlib.util.spec_from_file_location('_mixed_oracle_'+variant,runtime.interface.__file__)
        driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
        driver.OUT=directory;driver.BIN=runtime.BIN;driver.night=SimpleNamespace(OUT=double.shrunk.OUT)
        driver.fit=SimpleNamespace(**study.fit.__dict__);driver.fit.predict=double.shrunk.network.predict
        driver.command=command;driver.oracle()
        for path in directory.glob('oracle-*.json'):
            if path.name=='oracle-check.json':continue
            a=study.read(path);b=study.read(double.OUT/('oracle-'+variant)/path.name);maximum=0.
            assert a['config']==b['config'] and len(a['frontier']['rows'])==len(b['frontier']['rows'])
            for x,y in zip(a['frontier']['rows'],b['frontier']['rows']):
                assert x['node']==y['node'] and x['actor']==y['actor']
                av=np.array([h['action_values_counterfactual_bb'] for h in x['hands']])
                bv=np.array([h['action_values_counterfactual_bb'] for h in y['hands']])
                maximum=max(maximum,float(abs(av-bv).max()))
            assert maximum<2e-4
            differences.append(dict(variant=variant,case=path.stem,max_action_change_bb=maximum))
    assert len(differences)==24
    study.freeze(OUT/'oracle-check.json',dict(passed=True,comparison_to_double=differences,production_enabled=False))


def benchmark():
    export();double.qualified();assert study.read(OUT/'oracle-check.json')['passed']
    timings=study.read(double.OUT/'timing.json')
    variant=min(['serial','warp'],key=lambda v:timings['median_seconds_per_iteration'][v])
    study.freeze(OUT/'variant-selection.json',dict(variant=variant,basis='Fastest N15 double-precision median; no accuracy-based selection',
        timing_sha256=study.pilot.sha(double.OUT/'timing.json')))
    source=study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop';rows=[];comparisons=[]
    for repeat,arms in enumerate([['original','candidate'],['candidate','original'],['original','candidate']]):
        for arm in arms:
            folder=OUT/f'repeat-{repeat}'/arm;folder.mkdir(parents=True,exist_ok=True);path=folder/'iteration-150.json'
            if not path.exists():command(['solve',source,folder,arm,100,OUT/variant/'interface.cu'],folder/'run.log',optimized=arm=='candidate',warm=50)
            result=study.read(path);assert result['start_iteration']==result['warmup_iterations']==50 and result['iteration']==150
            rows.append(dict(repeat=repeat,arm=arm,seconds_per_iteration=result['learning_seconds']/100,sha256=study.pilot.sha(path)))
        root=OUT/f'repeat-{repeat}'
        original=double.warp.saves.compare(runtime.OUT/f'repeat-{repeat}/original/policy.gtop',root/'original/policy.gtop')
        study.night.dump(root/'original-state-parity.json',original);assert original['all_numeric_entries_equal']
        if repeat:
            stable=double.warp.saves.compare(OUT/'repeat-0/candidate/policy.gtop',root/'candidate/policy.gtop')
            study.night.dump(root/'candidate-repeat-parity.json',stable);assert stable['all_numeric_entries_equal']
        arena=double.warp.compare(double.OUT/f'repeat-{repeat}'/variant/'policy.gtop',root/'candidate/policy.gtop')
        study.night.dump(root/'double-arena-comparison.json',arena)
        a=study.read(double.OUT/f'repeat-{repeat}'/variant/'iteration-150.json');b=study.read(root/'candidate/iteration-150.json')
        assert a['config']==b['config'] and [v['path'] for v in a['views']]==[v['path'] for v in b['views']]
        change=max(float(abs(np.array(x['view']['strategy'])-y['view']['strategy']).max()) for x,y in zip(a['views'],b['views']))
        ev_change=float(abs(np.array(a['evs'])-b['evs']).max())
        comparisons.append(dict(repeat=repeat,max_inspected_strategy_change=change,max_player_ev_change_bb=ev_change))
        assert change<=.001 and ev_change<=.001
        print('N16 repeat',repeat+1,'passed numerical limits',flush=True)
    medians={a:float(np.median([r['seconds_per_iteration'] for r in rows if r['arm']==a])) for a in ['original','candidate']}
    study.night.dump(OUT/'timing.json',dict(variant=variant,repeats=rows,median_seconds_per_iteration=medians,
        comparisons=comparisons,overhead_vs_original=medians['candidate']/medians['original']-1,
        within_runtime_target=medians['candidate']<=1.1*medians['original'],production_enabled=False,
        caveat='Fixed-work timing and bounded inspected differences only. Changed-policy validation is still required.'))


if __name__=='__main__':{'export':export,'oracle':oracle,'benchmark':benchmark}[sys.argv[1]]()
