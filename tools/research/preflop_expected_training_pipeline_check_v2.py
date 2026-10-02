"""Five-context orchestration checks with explicit synthetic collectors/fits.

Real state/target replay/immutable checkpoints are exercised. No poker native
executable, physical scientific simulation or CUDA fit runs in these controls.
"""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch

import numpy as np

TOOLS=Path(r'T:\Dev\GTOpen\tools\research')
sys.path.append(str(TOOLS))
import preflop_expected_training_pipeline_v1 as pipeline
import preflop_expected_training_control_fixture_v1 as fixture
import preflop_expected_training_checkpoint_v1 as checkpoint
import preflop_expected_training_fit_v1 as fit
import sampled_visible_hybrid_checkpoint_v1 as storage


def main():
    root=Path(sys.argv[1]).resolve(); root.mkdir(parents=True,exist_ok=False)
    width=int(sys.argv[2]); began=time.monotonic(); refused=[]; called=[]
    objects=root/'objects'; registry,resources,config,previous=fixture.fixture(width,directory=objects)
    target=fixture.stage(objects,previous,registry,resources)
    initial=copy.deepcopy(previous); baseline={k:checkpoint.local_fit_identity(v) for k,v in previous['contexts'].items()}
    networks=storage.read_object(objects,previous['next_model'])
    networks=json.loads(networks)['shared']['networks']
    for actor,net in enumerate(networks): net['b2']=[.3+actor,.2,.1,.4]
    receipts=fixture.receipts(target,previous,registry,resources,config,networks)
    # Every imported local research implementation is prospectively pinned.
    config['source_identities'].update(fixture.inputs())
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).suffix=='.py' and Path(path).resolve().parent in (Path(__file__).parent,TOOLS):
            config['source_identities'][str(Path(path).resolve())]=pipeline.sha(path)
    pipeline.verify_sources(config)
    runtime=dict(board=dict(max_worker_seconds=120,native_timeout_seconds=60),
                 river=dict(max_worker_seconds=120,native_timeout_seconds=60,river_native_timeout_seconds=30))
    common=dict(inputs={k:{} for k in registry.fit_contexts},cache=None,
        native={k:Path(__file__) for k in ('bridge','trace','river','board')},guard=lambda:None,
        runtime_limits=runtime,workers=2,board_workers=2,batch_prefix='synthetic-control')
    def collect(folder,local,c,r,args,**kwargs):
        key=kwargs['key']; called.append(('collect',key))
        assert kwargs['used']==previous['next_model'] and kwargs['model_source']==storage.read_object(objects,previous['next_model']).decode()
        local.clear(); local.update(copy.deepcopy(target['contexts'][key]))
        return dict(scope='synthetic collector stub',key=key),copy.deepcopy(target['board_targets'][key])
    def fitting(r,local,args,c,**kwargs):
        actor=kwargs['player']; called.append(('fit',actor))
        assert kwargs['generation']==1 and kwargs['collected_against']==previous['next_model']['sha256']
        assert all(checkpoint.local_fit_identity(local[k])==checkpoint.local_fit_identity(target['contexts'][k]) for k in registry.fit_contexts)
        return copy.deepcopy(networks[actor]),copy.deepcopy(receipts[actor]),dict(scope='synthetic fit stub; no CUDA')
    stages=[]
    with patch.object(pipeline,'collect',collect),patch.object(pipeline,'fit',fitting):
        candidate,reference,metrics=pipeline.update(root/'complete-cycle',objects,previous,config,registry,resources,
            **common,on_stage=lambda stage,key=None:stages.append((stage,key)))
    assert called==[('collect',k) for k in registry.fit_contexts]+[('fit',0),('fit',1)]
    assert candidate['played_bank']==[previous['next_model']] and candidate['next_model']['generation']==1
    restored=checkpoint.restore_checkpoint(objects,reference,config,registry,resources)
    fixture.same_local(candidate['contexts'],restored['contexts'])
    fixture.same_local(previous['contexts'],initial['contexts'])
    assert baseline=={k:checkpoint.local_fit_identity(v) for k,v in previous['contexts'].items()}
    assert metrics==json.loads((root/'complete-cycle'/'metrics.json').read_bytes())
    def refuse(name,**kw):
        before=storage.encoded(previous['next_model']); ids={k:checkpoint.local_fit_identity(v) for k,v in previous['contexts'].items()}
        try:
            with patch.object(pipeline,'collect',kw.pop('collector',collect)),patch.object(pipeline,'fit',kw.pop('fitter',fitting)):
                pipeline.update(root/('refused-'+name),objects,previous,config,registry,resources,**dict(common,**kw))
        except (ValueError,RuntimeError,TypeError,KeyError):
            assert before==storage.encoded(previous['next_model']) and ids=={k:checkpoint.local_fit_identity(v) for k,v in previous['contexts'].items()}
            assert not (root/('refused-'+name)/'metrics.json').exists(); refused.append(name)
        else: raise AssertionError('Invalid cycle accepted '+name)
    refuse('missing-context',inputs={k:{} for k in registry.fit_contexts[:-1]})
    refuse('missing-native',native={k:Path(__file__) for k in ('bridge','trace','river')})
    refuse('missing-limits',runtime_limits={'river':runtime['river']})
    refuse('invalid-runtime',runtime_limits=dict(runtime,river=dict(runtime['river'],native_timeout_seconds=999)))
    def partial(folder,local,c,r,args,**kwargs):
        value,target_record=collect(folder,local,c,r,args,**kwargs)
        if kwargs['key']==registry.fit_contexts[-1]: raise RuntimeError('Synthetic interrupted final context')
        return value,target_record
    refuse('partial-context',collector=partial)
    def partial_fit(*args,**kwargs):
        if kwargs['player']==1: raise RuntimeError('Synthetic interrupted second fit')
        return fitting(*args,**kwargs)
    refuse('partial-fit',fitter=partial_fit)
    result=dict(passed=True,width=width,contexts=list(registry.fit_contexts),heldout=[r['context_sha256'] for r in registry.manifest['contexts'] if r['split']=='heldout'],
        completed_cycles=1,refused=refused,stages=stages,checkpoint=reference,seconds=time.monotonic()-began,
        scope='Synthetic five-context runner orchestration and real immutable state publication/restart only; no native/GPU/science',
        input_identities=fixture.inputs(),implementation_sha256=pipeline.sha(pipeline.__file__))
    pipeline.save(root/'result.json',result); print(json.dumps(dict(passed=True,width=width,seconds=result['seconds'],refusals=len(refused))))


if __name__=='__main__': main()
