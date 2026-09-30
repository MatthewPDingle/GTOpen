"""CPU equivalence and retained timing of routed, batched policy preparation.

No scientific fitting, new deals, native execution, CUDA or study admission.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
from itertools import combinations
import json
from pathlib import Path
import statistics
import time
import traceback
import numpy as np
import psutil
import torch
from threadpoolctl import threadpool_limits
import stack_context_matched_readback_v3 as reader
import stack_context_policy_v1 as baseline
import stack_context_relative_policy_v1 as relative
import stack_context_parallel_continuation_v2 as continuation
from stack_context_current_policy_v1 import CurrentPolicy as Original
from stack_context_current_policy_routed_v1 import CurrentPolicy as Routed
from stack_context_current_policy_batched_v1 import CurrentPolicy as Candidate
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets

OUT=reader.OUT
NAME='stack-context-batched-policy-check-v1'
FIXTURES=Path('S:/GTOpen-research/stack-context-full-control-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES=Path('S:/GTOpen-research/stack-context-model-control-v1')


def write(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,sort_keys=True,allow_nan=False);f.write('\n')


def compare(old,new,query,require_history=True):
    a=old.prepare(query,require_history=require_history);b=new.prepare(query,require_history=require_history)
    assert set(a)==set(b)
    for key in a:
        if key=='owner':continue
        if isinstance(a[key],np.ndarray):assert np.array_equal(a[key],b[key]),key
        else:assert a[key]==b[key],key
    assert list(old.relative_cache)==list(new.relative_cache)
    assert all(np.array_equal(old.relative_cache[k],new.relative_cache[k]) for k in old.relative_cache)
    p=old.infer(a);q=new.infer(b)
    assert np.array_equal(p,q) and np.array_equal(p>0,q>0)
    return dict(rows=len(p),overridden_rows=int(a['mask'].sum()),maximum_probability_error=float(np.max(abs(p-q))))


def main():
    attempt,result,failure=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure'))
    if any(p.exists() for p in (attempt,result,failure)):raise ValueError('Preserve existing check')
    if psutil.cpu_percent(interval=.2)>50 or psutil.virtual_memory().available<28_000_000_000 or not reader.production_available():
        print(json.dumps(dict(deferred=True,started=False,reason='CPU/RAM or production pressure')));return
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    torch.set_num_threads(1);limit=threadpool_limits(limits=1)
    full_proof=reader.read(OUT/'stack-context-full-control-v1-result.json')
    full_reg=reader.read(OUT/'stack-context-full-control-v1-registration.json')
    profile=reader.read(OUT/'stack-context-retained-cpu-profile-v1-result.json')
    assert full_proof['passed'] and profile['passed'];reader.verify(profile['inputs'])
    inputs=dict(profile['inputs']);inputs.update({str(p):reader.sha(p) for p in
        (Path(__file__).resolve(),Path(__file__).with_name('stack_context_current_policy_routed_v1.py'),
         Path(__file__).with_name('stack_context_current_policy_batched_v1.py'),
         Path(__file__).with_name('stack_board_relative_features_bulk_v1.py'),
         OUT/'stack-board-relative-bulk-check-v1-result.json',
         OUT/'stack-context-full-control-v1-result.json',OUT/'stack-context-full-control-v1-registration.json',
         OUT/'stack-context-retained-cpu-profile-v1-result.json')})
    bulk_proof=reader.read(OUT/'stack-board-relative-bulk-check-v1-result.json')
    assert bulk_proof['passed'] and bulk_proof['exact_float32_equality']
    qualified=[h for p,h in bulk_proof['inputs'].items() if Path(p).name=='stack_board_relative_features_bulk_v1.py']
    assert qualified==[reader.sha(Path(__file__).with_name('stack_board_relative_features_bulk_v1.py'))]
    entries=[]
    for depth in reader.DEPTHS:
        cp=GEOMETRY/'fixtures'/f'stack-{depth}-context.json';pp=GEOMETRY/f'stack-{depth}-public.json';qp=QUERIES/f'stack-{depth}-queries.json'
        for p in (cp,pp,qp):
            assert reader.sha(p)==full_reg['inputs'][str(p)];inputs[str(p)]=reader.sha(p)
        entries.append(dict(name=f'{depth}bb',split='heldout' if depth in (60,150) else 'fit',context_source=cp.read_text(),public_document=reader.read(pp)))
    for width in (362,387):
        p=FIXTURES/f'{width}-fixture.json';assert reader.sha(p)==full_proof['artifacts'][str(p)];inputs[str(p)]=reader.sha(p)
    write(attempt,dict(inputs=inputs,device='cpu',maximum_seconds=300,math_threads=1,
        scientific_training=False,new_deals=False,native_execution=False,production_modified=False))
    started=time.monotonic();cases=[];negative=[];bench=[]
    def guard():
        if time.monotonic()-started>300 or psutil.virtual_memory().available<24_000_000_000 or not reader.production_available():
            raise RuntimeError('Implementation check resource/time bound')
    def both_reject(label,old,new,query,**kwargs):
        for engine in (old,new):
            try:engine.prepare(query,**kwargs)
            except (ValueError,KeyError,TypeError):pass
            else:raise AssertionError('Invalid query accepted by '+type(engine).__module__+': '+label)
        negative.append(label)
    try:
        for width,kind,api in ((362,reader.Registry,baseline),(387,reader.RelativeRegistry,relative)):
            fixture=reader.read(FIXTURES/f'{width}-fixture.json');registry=kind(entries);assert fixture['registry']==registry.manifest
            model=fixture['model'];initial=copy.deepcopy(model);initial['generation']=0;initial['shared']=api.initial(registry)
            resources=fixture['resources']
            for key,state in initial['local_states'].items():
                config=dict(resources[key]['root_config']);config.pop('chance')
                state['board_root_state']=BoardRootRegrets(**config).document()
                state['exact_btn_state']=ExactBtnRegrets(key,resources[key]['entry_mass']).document()
            for generation,document in enumerate((initial,model)):
                for depth in reader.DEPTHS:
                    guard();query=reader.read(QUERIES/f'stack-{depth}-queries.json');key=hashlib.sha256(query['context_source'].encode()).hexdigest()
                    args=dict(context_sha256=key,resources=resources,device='cpu')
                    old=Original(document,registry,**args);new=Candidate(document,registry,**args)
                    assert {o['phase'] for o in query['observations']}=={0,1,2,3}
                    cases.append(dict(width=width,generation=generation,depth=depth,mode='all-streets',**compare(old,new,query)))
                    score=dict(context_source=query['context_source'],observations=[{k:v for k,v in o.items() if k!='own_history'} for o in query['observations'] if o['phase']>0])
                    cases.append(dict(width=width,generation=generation,depth=depth,mode='score-only-postflop',**compare(old,new,score,False)))
                    if key in resources:
                        catalog=json.loads(resources[key]['catalog_source'])
                        pre=dict(context_source=query['context_source'],observations=[r['observation'] for r in catalog['native_observations']])
                        cases.append(dict(width=width,generation=generation,depth=depth,mode='all-initial-classes',**compare(old,new,pre)))
                    if width==387 and generation==1 and depth==20:
                        # Synthetic visible-query fixtures, not training or
                        # evaluation deals. Exercise >8192 keys plus eviction
                        # and revisiting evicted rows in the same batch.
                        template=next(o for o in query['observations'] if o['phase']==3)
                        boards=[(0,5,14,27,44),(0,1,14,27,44),(0,1,14,15,44),
                            (0,1,2,27,44),(0,5,10,15,16),(0,8,20,32,44),
                            (0,1,2,12,13),(0,1,2,3,44),(0,4,8,12,16)]
                        rows=[]
                        for board in boards:
                            for hole in combinations([c for c in range(52) if c not in board],2):
                                cards=[*hole,*board];row=copy.deepcopy(template)
                                row['own_history']=[]
                                row['active_features']=[v for i,c in enumerate(cards) for v in
                                    (19*i+c//4,19*i+14+c%4)]+[v for v in template['active_features'] if v>=133]
                                row['lo']=str((row['actor']<<42)|sum(c<<(6*i) for i,c in enumerate(cards)))
                                rows.append(row)
                        rows=rows[:9000]+copy.deepcopy(rows[:64])
                        stress=dict(context_source=query['context_source'],observations=rows)
                        fresh_old=Original(document,registry,**args);fresh_new=Candidate(document,registry,**args)
                        cases.append(dict(width=width,generation=generation,depth=depth,mode='over-capacity-cache-and-revisit',
                            **compare(fresh_old,fresh_new,stress)))
                        assert len(fresh_old.relative_cache)==8192
                        cases.append(dict(width=width,generation=generation,depth=depth,mode='warm-evicting-cache',
                            **compare(fresh_old,fresh_new,stress)))
                    if generation==1 and depth==20:
                        for field,value in [('actor',2),('actor',True),('phase',2),('n',0),('n',5),('n',2.0),('hi','01'),('lo','bad')]:
                            bad=copy.deepcopy(query);bad['observations'][0][field]=value
                            both_reject(str(width)+'/'+field+'/'+str(value),old,new,bad)
                        bad=copy.deepcopy(query);bad['observations'][0]['active_features'][0]=.5
                        both_reject(str(width)+'/noninteger-feature',old,new,bad)
                        bad=copy.deepcopy(query);bad['observations'][0].pop('own_history')
                        both_reject(str(width)+'/missing-history',old,new,bad)
                        bad=copy.deepcopy(query);bad['observations'][0]['own_history']=[[0,0,query['observations'][0]['n']]]
                        both_reject(str(width)+'/self-ancestor',old,new,bad)
                        both_reject(str(width)+'/history-mode-type',old,new,query,require_history=None)
                        both_reject(str(width)+'/score-only-history',old,new,query,require_history=False)
                        bad=dict(context_source=query['context_source'],observations=[])
                        both_reject(str(width)+'/empty-rows',old,new,bad)
                        bad=dict(query,context_source=query['context_source']+' ')
                        both_reject(str(width)+'/wrong-context',old,new,bad)
                        # Keep the old one-action postflop rejection even when
                        # the public menu is deliberately made consistent.
                        bad=dict(context_source=score['context_source'],observations=[copy.deepcopy(score['observations'][0])])
                        bad['observations'][0]['n']=1;hi=bad['observations'][0]['hi']
                        for engine in (old,new):engine.entry['lookup'][hi][0]['actions']=engine.entry['lookup'][hi][0]['actions'][:1]
                        both_reject(str(width)+'/one-action-postflop',old,new,bad,require_history=False)

        # Fixed real learned generation-one fixture from the earlier profile.
        spec=reader.read(reader.TRAIN_REG);prepared=reader.read(OUT/'stack-context-population-v1-result.json')
        folder=reader.TRAIN/'A-relative';metric=reader.read(folder/'cycle-0002'/'metrics.json');c=metric['collections'][0];key=c['context_sha256']
        rt=continuation.runtime_for('A-relative',spec,prepared)
        model=reader.full.read_model(folder/'objects',metric['used_model'],rt['registry'],rt['resources'])
        native=Path(c['subbatches'][0]['path']).parent/'conditional'
        queries={name:reader.read(native/f'chunk-000-{name}-native.json')['queries'] for name in ('history','selected')}
        with np.load(native/'chunk-000-policies.npz',allow_pickle=False) as data:expected={name:data[name] for name in queries}
        for implementation in ('original','routed','candidate','candidate','routed','original'):
            guard();engine=dict(original=Original,routed=Routed,candidate=Candidate)[implementation](model,rt['registry'],context_sha256=key,resources=rt['resources'],device='cpu')
            begin=time.perf_counter();phases=[]
            for name,query in queries.items():
                t=time.perf_counter();ready=engine.prepare(query);mid=time.perf_counter();p=engine.infer(ready);end=time.perf_counter()
                assert np.array_equal(p,expected[name])
                phases.append(dict(phase=name,rows=len(p),prepare_seconds=mid-t,infer_seconds=end-mid,maximum_saved_probability_error=0.))
            bench.append(dict(implementation=implementation,seconds=time.perf_counter()-begin,phases=phases))
        guard();reader.verify(inputs);assert not torch.cuda.is_initialized()
        medians={name:statistics.median(r['seconds'] for r in bench if r['implementation']==name) for name in ('original','routed','candidate')}
        answer=dict(complete=True,passed=True,seconds=time.monotonic()-started,inputs=inputs,cases=cases,negative_cases=negative,
            benchmark=bench,median_fixture_seconds=medians,fixture_scoring_speed_ratio=medians['original']/medians['candidate'],
            benchmark_scope='Two repetitions per implementation, ABCCBA order, fresh cache, one retained chunk pair; not end-to-end throughput',
            installed_in_registered_study=False,cuda_qualified=False,cuda_initialized=False,
            scientific_training=False,new_deals=False,native_execution=False,production_modified=False)
        write(result,answer);print(json.dumps(dict(passed=True,cases=len(cases),negative_cases=len(negative),median_seconds=medians,fixture_scoring_speed_ratio=answer['fixture_scoring_speed_ratio'],seconds=answer['seconds'])))
    except BaseException as error:
        write(failure,dict(error=repr(error),traceback=traceback.format_exc(),scientific_work_untouched=True));raise


if __name__=='__main__':main()
