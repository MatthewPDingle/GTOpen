"""CPU software controls: synthetic zero support on retained legal query rows.

Temporary in-memory table overrides are control fixtures, not scientific model
fits or saved learned banks. The actual registered study is untouched.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1',
                  OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import json
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
import torch
from threadpoolctl import threadpool_limits
import stack_context_played_bank_routed_check_v1 as control
from board_training_policy_v1 import RootTable
from sampled_physical_preflop_table_v1 import validate_preflop

OUT = control.OUT
NAME = 'stack-context-played-bank-zero-support-check-v1'


def main():
    attempt,result,failure=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure'))
    if any(path.exists() for path in (attempt,result,failure)):
        raise ValueError('Preserve existing zero-support control evidence')
    if (psutil.cpu_percent(interval=.2)>50 or psutil.virtual_memory().available<28_000_000_000
            or not control.production_available()):
        print(json.dumps(dict(deferred=True,started=False)));return
    proof_path=OUT/'stack-context-played-bank-routed-check-v1-result.json'
    proof=control.read(proof_path)
    assert proof['complete'] and proof['passed'] and not proof['cuda_initialized']
    inputs=dict(proof['inputs']);inputs[str(proof_path)]=control.sha(proof_path)
    inputs[str(Path(__file__).resolve())]=control.sha(__file__)
    for path,digest in inputs.items():
        assert control.sha(path)==digest,path
    torch.set_num_threads(1);limits=threadpool_limits(limits=1)
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    control.save(attempt,dict(inputs=inputs,pid=os.getpid(),process_created=psutil.Process().create_time(),
        maximum_seconds=300,math_threads=1,device='cpu',synthetic_in_memory_overrides=True,
        scientific_fitting=False,new_deals=False,native_execution=False,gpu_used=False,
        production_modified=False))
    started=time.monotonic();cases=[]
    def guard():
        if (time.monotonic()-started>300 or psutil.virtual_memory().available<24_000_000_000
                or not control.production_available()):
            raise RuntimeError('Zero-support control resource/time bound')
    try:
        entries=[]
        for depth in control.DEPTHS:
            source=(control.GEOMETRY/'fixtures'/f'stack-{depth}-context.json').read_text()
            public=control.read(control.GEOMETRY/f'stack-{depth}-public.json')
            entries.append(dict(name=f'{depth}bb',split='heldout' if depth in (60,150) else 'fit',
                                context_source=source,public_document=public))
        query=control.read(control.QUERIES/'stack-20-queries.json')
        key=control.hashlib.sha256(query['context_source'].encode()).hexdigest()
        for width,kind,api in ((362,control.Registry,control.base),(387,control.RelativeRegistry,control.relative)):
            fixture=control.read(control.OLD/f'{width}-fixture.json');registry=kind(entries)
            assert fixture['registry']==registry.manifest
            resources,model=fixture['resources'],fixture['model']
            initial=copy.deepcopy(model);initial['generation']=0;initial['shared']=api.initial(registry)
            for context,state in initial['local_states'].items():
                config=dict(resources[context]['root_config']);config.pop('chance')
                state['board_root_state']=control.BoardRootRegrets(**config).document()
                state['exact_btn_state']=control.ExactBtnRegrets(context,resources[context]['entry_mass']).document()
            args=dict(context_sha256=key,resources=resources,weights_by_player=[[1.,2.],[3.,4.]],
                      completed_cycles=2,device='cpu',guard=guard)
            for blocked in ((0,1),(1,)):
                guard();banks=[cls([initial,model],registry,**args) for cls in (control.Original,control.Candidate)]
                ready=banks[0].engines[0].prepare(query)
                first=banks[0].engines[0].infer(ready)
                selected=None
                for child,history in enumerate(ready['own_history']):
                    if not history or not all(first[parent,action]>0 for parent,action in history):continue
                    for parent,action in history:
                        observation=query['observations'][parent]
                        parent_key=(int(observation['hi']),int(observation['lo']))
                        if observation['phase']==0 and observation['actor']==0 and parent_key[0]==1 and any(
                                type(table) is RootTable
                                for table in banks[0].engines[0].tables):
                            selected=(child,parent,action,parent_key);break
                    if selected is not None:break
                assert selected is not None,'Retained fixture needs a supported root ancestor'
                child,parent,action,parent_key=selected
                affected=[i for i,history in enumerate(ready['own_history']) if (parent,action) in history]
                assert child in affected and affected
                arity=int(ready['arity'][parent]);alternative=(action+1)%arity
                replacement=np.zeros(4);replacement[alternative]=1.
                for bank in banks:
                    for generation in blocked:
                        matched=0
                        for table in bank.engines[generation].tables:
                            if type(table) is RootTable:
                                observation=query['observations'][parent]
                                assert validate_preflop(observation,table.context,table.player)==parent_key
                                n=observation['n'];active=tuple(sorted(observation['active_features']))
                                assert n==arity
                                table.rows[parent_key]=(n,active,replacement.copy());matched+=1
                        assert matched==1
                p,reach=banks[0].average(query,guard=guard)
                q,support=banks[1].average(query,guard=guard)
                assert np.array_equal(p,q) and np.array_equal(reach,support)
                zero=np.flatnonzero(support==0)
                if blocked==(0,1):
                    assert len(zero)>0 and np.all(support[affected]==0)
                    legal=ready['legal'][zero].astype(np.float64)/ready['arity'][zero,None]
                    assert np.array_equal(q[zero],legal)
                else:
                    assert support[child]>0,'A surviving generation must still provide support'
                cases.append(dict(width=width,depth=20,blocked_generations=list(blocked),
                    parent_row=parent,parent_key=list(parent_key),blocked_action=action,alternative_action=alternative,
                    descendant_rows=len(affected),zero_support_rows=len(zero),selected_child_support=float(support[child]),
                    original_probability_error=0.,original_reach_error=0.,uniform_fallback_verified=blocked==(0,1)))
        guard()
        for path,digest in inputs.items():assert control.sha(path)==digest,path
        assert not torch.cuda.is_initialized()
        answer=dict(complete=True,passed=True,seconds=time.monotonic()-started,inputs=inputs,cases=cases,
            scope='Four CPU controls on two-model fixtures at20bb; in-memory legal root overrides eliminate own-history support or leave one generation supported',
            math_threads=1,cuda_initialized=False,synthetic_in_memory_overrides=True,
            actual_64_generation_banks_qualified=False,cuda_qualified=False,full_runtime_speedup_measured=False,
            scientific_fitting=False,new_deals=False,native_execution=False,
            installed_in_registered_study=False,production_modified=False)
        control.save(result,answer)
        print(json.dumps(dict(passed=True,cases=len(cases),zero_support_rows=[c['zero_support_rows'] for c in cases],seconds=answer['seconds'])))
    except BaseException as error:
        control.save(failure,dict(error=repr(error),traceback=traceback.format_exc(),
                                 preserve_evidence=True,automatic_retry_allowed=False))
        raise


if __name__=='__main__':main()
