"""CPU checks for retained-fixture transport and reference-worker plumbing.

Does not score actual final banks, use CUDA, draw new hands or invoke native.
Actual64-bank CUDA/reference agreement remains a separate mandatory gate.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import json
from pathlib import Path
import queue
import sys
import time
import traceback
from unittest.mock import patch
import numpy as np
import stack_context_final_bank_throughput_v1 as runner
from sampled_physical_root_evaluation_v1 import sha,save

NAME='stack-context-final-bank-throughput-v1-check'
OUT=runner.OUT
STORE=Path('S:/GTOpen-research')/NAME


def main():
    attempt,output,failure=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure'))
    runner.require(not any(p.exists() for p in (attempt,output,failure,STORE)), 'Preserve previous check')
    fixture=runner.read(runner.FIXTURE);runner.continuation.legacy.verify(fixture['inputs'])
    integration_path=OUT/'stack-context-evaluation-integration-check-v1-result.json'
    integration=runner.read(integration_path)
    runner.require(integration['passed'] and integration['complete'], 'Existing native integration proof required')
    runner.continuation.legacy.verify(integration['inputs'])
    paths={Path(__file__).resolve(),Path(runner.__file__).resolve(),runner.PLAN,runner.FIXTURE,
        runner.evaluation.EXES['query'],integration_path}
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(runner.continuation.legacy.ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    inputs={str(p):sha(p) for p in paths}
    save(attempt,dict(inputs=inputs,new_fits=False,gpu=False,new_scientific_deals=False,synthetic_reference_values=True))
    STORE.mkdir();began=time.monotonic();negative=[]
    def reject(name,fn):
        try:fn()
        except ValueError:negative.append(name)
        else:raise AssertionError('Accepted '+name)
    try:
        assert len(fixture['deals'])==len({tuple(d) for d in fixture['deals']})==32
        assert fixture['new_physical_deals'] is False and fixture['scientific_test_stream_used'] is False
        original=copy.deepcopy(fixture)
        for depth in runner.evaluation.DEPTHS:
            batch=runner.make_batch(fixture,depth)
            assert set(batch)=={'format','batch_id','seed','query_limit','deals'} and batch['format']==2 and batch['seed']==0
            assert batch['deals']==fixture['deals'] and batch['query_limit']==1_000_000
            batch['deals'][0][0]=63
            assert fixture==original
        reject('unregistered depth',lambda:runner.make_batch(fixture,80))
        fewer=copy.deepcopy(fixture);fewer['deals'].pop()
        reject('smaller retained batch',lambda:runner.make_batch(fewer,20))
        fewer=copy.deepcopy(fixture);fewer['depths'].pop()
        reject('omitted stack depth',lambda:runner.make_batch(fewer,20))
        p=np.array([[.3,.2,.5,0],[.5,.5,0,0],[0,0,0,1.]])
        support=np.array([2080.,0.,1040.])
        assert runner.compare_arrays(p,support,p,support)['maximum_probability_error']==0
        for label,changed_p,changed_s in (
            ('shape',p[:2],support),('different probability',p+1e-6,support),
            ('different reach',p,support+1e-5),('nonfinite',p*np.nan,support),
            ('zero support differs',p,np.array([2080.,1e-12,1040.]))):
            reject(label,lambda changed_p=changed_p,changed_s=changed_s:runner.compare_arrays(changed_p,changed_s,p,support))
        reject('negative reference',lambda:runner.compare_arrays(-p,support,-p,support))
        reject('unnormalized reference',lambda:runner.compare_arrays(p*2,support,p*2,support))
        reject('actual unfinished banks',runner.terminal_banks)
        runner.main()

        # Actual worker control flow and .npy/result binding, with explicitly
        # synthetic model reader/math and guard. Nothing touches training files.
        task=STORE/'query.json';save(task,dict(synthetic=True))
        (STORE/'depth-20').mkdir()
        arm='A-baseline';weights=[list(range(1,65))]*2
        banks={'arms':{arm:dict(weights_by_player=weights,completed_cycles=64)}}
        rt=dict(registry='synthetic registry',resources='synthetic resources')
        fake_docs=[dict(generation=i) for i in range(64)]
        requests=queue.Queue();responses=queue.Queue()
        requests.put((20,'synthetic-key',str(task)));requests.put(None)
        def average(docs,registry,query,**kwargs):
            assert docs is fake_docs and registry==rt['registry'] and query==dict(synthetic=True)
            assert kwargs['device']=='cpu' and kwargs['weights_by_player']==weights and kwargs['context_sha256']=='synthetic-key'
            return p,support
        with patch.object(runner,'STORE',STORE),patch.object(runner,'Guard',return_value=lambda:None), \
             patch.object(runner.continuation,'runtime_for',return_value=rt), \
             patch.object(runner.selection,'load_documents',return_value=fake_docs), \
             patch.object(runner.full,'average',side_effect=average):
            runner.reference_worker(arm,banks,{}, {},requests,responses,time.time())
        ready=responses.get_nowait();answer=responses.get_nowait()
        assert ready['ready'] and ready['arm']==answer['arm']==arm and answer['depth']==20
        prefix=STORE/'depth-20'/arm
        assert answer['probability_sha256']==sha(str(prefix)+'-reference-p.npy')
        assert answer['support_sha256']==sha(str(prefix)+'-reference-s.npy')
        assert np.array_equal(np.load(str(prefix)+'-reference-p.npy',allow_pickle=False),p)
        assert np.array_equal(np.load(str(prefix)+'-reference-s.npy',allow_pickle=False),support)
        live=type('Live',(),{'is_alive':lambda self:True})()
        q=queue.Queue();q.put(answer)
        assert runner.receive(q,{arm:live},lambda:None)==answer
        q=queue.Queue();q.put(dict(failed=True,error='synthetic preserved failure'))
        reject('worker error propagates',lambda:runner.receive(q,{arm:live},lambda:None))
        dead=type('Dead',(),{'is_alive':lambda self:False})()
        reject('dead worker cannot be mistaken for a slow result',lambda:runner.receive(queue.Queue(),{arm:dead},lambda:None))
        runner.continuation.legacy.verify(inputs);assert time.monotonic()-began<120
        result=dict(complete=True,passed=True,seconds=time.monotonic()-began,inputs=inputs,runner_sha256=sha(runner.__file__),
            retained_distinct_deals=32,all_seven_depth_batches_verified=True,reference_worker_cpu_only=True,
            reference_worker_transport_bound=True,negative_cases=negative,actual_final_models=False,
            actual_cuda_qualified=False,parallel_process_runtime_qualified=False,synthetic_reference_values=True,
            new_scientific_deals=False,scientific_fits=False,native_execution=False,gpu=False,production_modified=False,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()})
        save(output,result);print(json.dumps(dict(passed=True,seconds=result['seconds'],negative_cases=len(negative))))
    except BaseException as error:
        save(failure,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True,automatic_retry_allowed=False));raise


if __name__=='__main__':main()
