"""Frozen nonlinear predictor in the isolated GPU continuation interface."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import importlib.util
import re
import sys
from types import SimpleNamespace
import numpy as np
import continuation_shrunk_residual as shrunk
import continuation_shrunk_evaluation as evaluation
import continuation_candidate_export as encoder
import continuation_warp_summary as warp

study=shrunk.study
runtime=warp.runtime
OUT=shrunk.OUT.parent/'shrunk-residual-gpu-20260916'


def terms(base):
    # Reuse the verified encoder's term mapping without changing its source.
    dummy=dict(base,mean=[0.]*104,scale=[1.]*104,coef=[1.]*104,production_enabled=False)
    lines=encoder.expression(dummy).splitlines()[1:]
    assert len(lines)==104
    result=[]
    for line in lines:
        match=re.fullmatch(r'\+\(1\)\*\((.*)\)',line);assert match,line
        result.append(match.group(1))
    return result


def folded_network(model):
    assert model['kind']=='shrunk_nonlinear_residual' and model['residual_scale']==.75
    assert model['width']==8 and model['output_penalty']==.1 and len(model['networks'])==2
    assert model['production_enabled'] is False
    base=model['base'];mean=np.array(base['mean']);scale=np.array(base['scale'])
    weights=np.concatenate([np.array(n['weight']) for n in model['networks']],axis=1)
    bias=np.concatenate([np.array(n['bias']) for n in model['networks']])
    output=np.concatenate([np.array(n['output'])/2 for n in model['networks']])
    assert weights.shape==(104,16) and bias.shape==output.shape==(16,) and (scale>0).all()
    effective=weights/scale[:,None]
    return dict(weights=effective,bias=bias-mean@effective,output=output,low=mean-6*scale,high=mean+6*scale)


def neural_block(model):
    net=folded_network(model);expressions=terms(model['base'])
    lines=[f' double nn{i}={v:.17g};' for i,v in enumerate(net['bias'])]
    for k,term in enumerate(expressions):
        lines.append(f' {{double clipped=fmin({net["high"][k]:.17g},fmax({net["low"][k]:.17g},({term})));')
        for i in range(16):
            if net['weights'][k,i]!=0:lines.append(f' nn{i}+=clipped*({net["weights"][k,i]:.17g});')
        lines.append(' }')
    expression='+'.join(f'(fmax(0.,nn{i})*({v:.17g}))' for i,v in enumerate(net['output']))
    return '\n'.join(lines)+'\n',expression


def sources(model,sha):
    template=(study.ROOT/'tools/research/learned_interface_kernel.cu').read_text()
    marker='  correction[x]=__FEATURE_EXPRESSION__;';assert template.count(marker)==1
    block,neural=neural_block(model)
    base=encoder.expression(dict(model['base'],production_enabled=False))
    serial='// Frozen N15 model '+sha+'\n'+template.replace(marker,block+'  correction[x]=('+base+')+('+neural+');')
    helper=(study.ROOT/'tools/research/continuation_warp_summary.cuh').read_text()
    return dict(serial=serial,warp=warp.source(serial,helper))


def export():
    path=shrunk.OUT/'candidate.json';frozen=study.read(shrunk.OUT/'candidate-freeze.json')
    assert study.pilot.sha(path)==frozen['sha256']
    paths=[path,shrunk.OUT/'candidate-freeze.json',shrunk.OUT/'evaluation-registration.json',runtime.BIN,OUT/'README.md',
        study.ROOT/'tools/research/continuation_shrunk_gpu.py',study.ROOT/'tools/research/continuation_shrunk_evaluation.py',
        study.ROOT/'tools/research/continuation_nonlinear_residual.py',study.ROOT/'tools/research/continuation_candidate_export.py',
        study.ROOT/'tools/research/continuation_warp_summary.py',study.ROOT/'tools/research/continuation_warp_summary.cuh',
        study.ROOT/'tools/research/learned_interface.py',study.ROOT/'tools/research/learned_interface_kernel.cu',
        study.ROOT/'cache/preflop_eq169.bin',study.ROOT/'cache/realization_fit.json',
        study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop']
    for name,source in sources(study.read(path),frozen['sha256']).items():
        folder=OUT/name;folder.mkdir(parents=True,exist_ok=True);target=folder/'interface.cu'
        if target.exists():assert target.read_bytes()==source.encode()
        else:target.write_bytes(source.encode())
        paths.append(target)
    study.freeze(OUT/'manifest.json',dict(files={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},
        candidate_sha256=frozen['sha256'],production_enabled=False,
        note='Frozen N15, 16 double-precision hidden units, original anchored interface; serial and warp summaries. No GPU validation or runtime claim from export.'))


def qualified():
    evaluation.registered()
    result=study.read(shrunk.OUT/'evaluation.json')
    assert result['accuracy_screen_passed'],'N15 must pass registered accuracy before GPU execution'
    assert result['candidate_sha256']==study.pilot.sha(shrunk.OUT/'candidate.json')
    study.freeze(OUT/'accuracy-evidence.json',dict(evaluation_sha256=study.pilot.sha(shrunk.OUT/'evaluation.json'),
        candidate_sha256=result['candidate_sha256'],accuracy_screen_passed=True,production_enabled=False))


def command(args,log,optimized=True,warm=0):
    qualified();evaluation.require_queue_idle()
    # Also refuse a still-live N15 sequencing parent between child stages.
    import continuation_night_queue as queue
    for p in queue.processes():
        if p['ProcessId']!=os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe']:
            command=(p['CommandLine'] or '').lower()
            assert not any(n in command for n in ['continuation_shrunk_queue.py',
                'continuation_shrunk_gpu.py oracle','continuation_shrunk_gpu.py benchmark']), 'Another research GPU controller is active'
    return runtime.command(args,log,optimized=optimized,warm=warm)


def oracle():
    export();qualified()
    for variant in ['serial','warp']:
        directory=OUT/('oracle-'+variant);directory.mkdir(exist_ok=True)
        source=(OUT/variant/'interface.cu').read_bytes();target=directory/'interface.cu'
        if target.exists():assert target.read_bytes()==source
        else:target.write_bytes(source)
        spec=importlib.util.spec_from_file_location('_shrunk_oracle_'+variant,runtime.interface.__file__)
        driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
        driver.OUT=directory;driver.BIN=runtime.BIN;driver.night=SimpleNamespace(OUT=shrunk.OUT)
        driver.fit=SimpleNamespace(**study.fit.__dict__);driver.fit.predict=shrunk.network.predict
        driver.command=command;driver.oracle()
    differences=[]
    for p in (OUT/'oracle-serial').glob('oracle-*.json'):
        if p.name=='oracle-check.json':continue
        a=study.read(p);b=study.read(OUT/'oracle-warp'/p.name);maximum=0.
        assert a['config']==b['config'] and len(a['frontier']['rows'])==len(b['frontier']['rows'])
        for x,y in zip(a['frontier']['rows'],b['frontier']['rows']):
            assert x['node']==y['node'] and x['actor']==y['actor']
            av=np.array([h['action_values_counterfactual_bb'] for h in x['hands']])
            bv=np.array([h['action_values_counterfactual_bb'] for h in y['hands']])
            maximum=max(maximum,float(abs(av-bv).max()))
        assert maximum<2e-6
        differences.append(dict(case=p.stem,max_action_change_bb=maximum))
    assert len(differences)==12
    study.freeze(OUT/'oracle-check.json',dict(passed=True,variant_comparison=differences,production_enabled=False))
    export()


def benchmark():
    export();qualified();assert study.read(OUT/'oracle-check.json')['passed']
    source=study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop';rows=[]
    for repeat,arms in enumerate([['original','serial','warp'],['warp','original','serial'],['serial','warp','original']]):
        for arm in arms:
            folder=OUT/f'repeat-{repeat}'/arm;folder.mkdir(parents=True,exist_ok=True);path=folder/'iteration-150.json'
            if not path.exists():
                kernel=(runtime.OLD if arm=='original' else OUT/arm)/'interface.cu'
                command(['solve',source,folder,'original' if arm=='original' else 'candidate',100,kernel],folder/'run.log',optimized=arm!='original',warm=50)
            result=study.read(path)
            assert result['start_iteration']==result['warmup_iterations']==50 and result['iteration']==150
            rows.append(dict(repeat=repeat,arm=arm,seconds_per_iteration=result['learning_seconds']/100,
                setup_seconds=result['setup_seconds'],warmup_seconds=result['warmup_seconds'],total_seconds=result['total_seconds'],sha256=study.pilot.sha(path)))
        root=OUT/f'repeat-{repeat}'
        original=warp.saves.compare(runtime.OUT/f'repeat-{repeat}/original/policy.gtop',root/'original/policy.gtop')
        study.night.dump(root/'original-state-parity.json',original);assert original['all_numeric_entries_equal']
        parity=warp.compare(root/'serial/policy.gtop',root/'warp/policy.gtop')
        study.night.dump(root/'variant-state-comparison.json',parity);assert parity['passed']
        a=study.read(root/'serial/iteration-150.json');b=study.read(root/'warp/iteration-150.json')
        assert len(a['views'])==len(b['views'])
        for x,y in zip(a['views'],b['views']):
            assert x['path']==y['path']
            np.testing.assert_allclose(x['view']['strategy'],y['view']['strategy'],atol=1e-4,rtol=0)
        np.testing.assert_allclose(a['evs'],b['evs'],atol=2e-5,rtol=0)
        if repeat:
            for arm in ['serial','warp']:
                stable=warp.saves.compare(OUT/f'repeat-0/{arm}/policy.gtop',root/arm/'policy.gtop')
                study.night.dump(root/(arm+'-repeat-parity.json'),stable);assert stable['all_numeric_entries_equal']
        print('N15 GPU repeat',repeat+1,'passed',flush=True)
    medians={a:float(np.median([r['seconds_per_iteration'] for r in rows if r['arm']==a])) for a in ['original','serial','warp']}
    study.night.dump(OUT/'timing.json',dict(repeats=rows,median_seconds_per_iteration=medians,
        overhead_vs_original={a:medians[a]/medians['original']-1 for a in ['serial','warp']},
        within_runtime_target=min(medians[a] for a in ['serial','warp'])<=1.1*medians['original'],production_enabled=False,
        caveat='Fixed-work timing only; changed-policy and full-game approximation checks remain.'))


if __name__=='__main__':{'export':export,'oracle':oracle,'benchmark':benchmark}[sys.argv[1]]()
