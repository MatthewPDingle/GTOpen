"""Retained-fixture native integration and separate fixed-budget driver checks.

The models are routing controls, not the currently trained scientific banks.
Repeated original fixture hands are not independent accuracy observations.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import stack_context_full_policy_v1 as full
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
import stack_context_evaluation_driver_v1 as driver
import stack_context_matched_evaluation_v1 as controller
from stack_context_inputs_v1 import Registry,encoded
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_played_bank_v1 import PlayedBank
from stack_context_evaluation_journal_v1 import EvaluationJournal
from stack_context_matched_analysis_v1 import context_analysis
from sampled_allin_protocol_v3 import AllinCache
from crossed_complete_policy_batch_v1 import evaluate_batch
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from owned_columnar_evaluation_archive_v1 import ARTIFACTS,durable,digest

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-evaluation-integration-check-v1'
STORE=Path('S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1')
OLD=Path('S:/GTOpen-research/stack-context-full-control-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES=Path('S:/GTOpen-research/stack-context-model-control-v1')
CONTROLLER=ROOT/'tools/research/stack_context_matched_evaluation_v1.py'
EXES=[ROOT/'target/release/examples'/n for n in ('hu_sampled_bank_bridge.exe','hu_sampled_profile_allin_evaluation_v1.exe')]


def read(path):return json.loads(Path(path).read_bytes())


class ReferenceBank:
    def __init__(self,documents,registry,key,resources,weights):
        self.args=dict(documents=documents,registry=registry,context_sha256=key,resources=resources,
                       weights_by_player=weights,device='cpu')
    def average(self,query,*,guard):
        return full.average(queries=query,guard=guard,**self.args)


def driver_check(values,batch):
    """No native calls here; journal recovery itself has its own passed check."""
    class Journal:
        plan={'depth':20}
        def __init__(self):self.count=0;self.pending=False;self.complete=False;self.full_reads=0
        def prefix(self,*,verify_archives=False):
            self.full_reads+=int(verify_archives)
            return dict(completed_deals=self.count,previous_commit_sha256='synthetic-prefix',
                        values=np.tile(values,(self.count//32,1,1,1)))
        def recover_next(self,*,retire):
            assert retire
            if not self.pending:return None
            if not self.complete:raise ValueError('Synthetic incomplete native batch')
            self.count+=32;self.pending=self.complete=False
            return dict(completed_deals=self.count)
        def begin(self):
            assert not self.pending and self.count<4096
            self.pending=True
            return copy.deepcopy(batch),Path('synthetic-in-memory-folder')
    journal=Journal();calls=[];original=driver.evaluate_batch
    def fake(**kwargs):
        assert len(kwargs['batch']['deals'])==32
        assert journal.pending and not journal.complete
        calls.append(journal.count);journal.complete=True
    driver.evaluate_batch=fake
    args=dict(context_path='synthetic',banks=['synthetic']*4,cache='synthetic',
              query_executable='never-invoked',evaluation_executable='never-invoked',guard=lambda:None)
    try:
        stopped=driver.collect(journal,**args,stop_requested=lambda:journal.count==64)
        assert not stopped['complete'] and stopped['completed_deals']==64 and calls==[0,32]
        assert 'analysis' not in stopped
        complete=driver.collect(journal,**args)
        assert complete['complete'] and complete['completed_deals']==4096 and calls==list(range(0,4096,32))
        expected=context_analysis(np.tile(values,(128,1,1,1)),depth=20,dead_money=.5)
        assert complete['analysis']==expected and journal.full_reads==3
        before=len(calls);again=driver.collect(journal,**args)
        assert again==complete and len(calls)==before
        incomplete=Journal();incomplete.pending=True
        try:driver.collect(incomplete,**args)
        except ValueError:pass
        else:raise AssertionError('Driver retried partial work')
        assert len(calls)==before
    finally:
        driver.evaluate_batch=original
    return dict(batch_calls=len(calls),deals=4096,normal_boundary_resume=True,partial_work_refused=True,
                final_full_archive_verification=True,final_analysis_exact=True,scientific_payoffs=False)


def main():
    attempt=OUT/(NAME+'-attempt.json');output=OUT/(NAME+'-result.json');failure=OUT/(NAME+'-failure.json')
    if any(p.exists() for p in (STORE,attempt,output,failure)):
        raise ValueError('Preserve existing started or completed check')
    old_result=read(OUT/'stack-context-full-control-v1-result.json')
    old_reg=read(OUT/'stack-context-full-control-v1-registration.json')
    assert old_result['passed'] and old_result['complete']
    entries=[];paths={Path(__file__).resolve(),CONTROLLER,*EXES,
        OUT/'stack-context-full-control-v1-result.json',OUT/'stack-context-full-control-v1-registration.json',
        OUT/'stack-context-complete-allin-cache-v1-readback.json'}
    for depth in (20,40,60,100,150,200,400):
        context=GEOMETRY/'fixtures'/f'stack-{depth}-context.json';public=GEOMETRY/f'stack-{depth}-public.json'
        for p in (context,public):
            assert digest(p.read_bytes())==old_reg['inputs'][str(p)]
            paths.add(p)
        entries.append(dict(name=f'{depth}bb',split='heldout' if depth in (60,150) else 'fit',
                            context_source=context.read_text(),public_document=read(public)))
    for width in (362,387):
        p=OLD/f'{width}-fixture.json';assert digest(p.read_bytes())==old_result['artifacts'][str(p)];paths.add(p)
    for depth in (20,60):
        p=QUERIES/f'stack-{depth}-queries.json';assert digest(p.read_bytes())==old_reg['inputs'][str(p)];paths.add(p)
    reviewed=read(OUT/'stack-context-complete-allin-cache-v1-readback.json')
    assert reviewed['passed'];paths.add(Path(reviewed['cache_artifact']))
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    inputs={str(p):digest(p.read_bytes()) for p in paths}
    durable(attempt,encoded(dict(inputs=inputs,store=str(STORE),maximum_seconds=600,maximum_logical_bytes=512000000,
        device='cpu',trained_scientific_banks=False,new_scientific_test_hands=False,retained_fixture_deals_repeated=True)))
    STORE.mkdir();began=time.monotonic()
    try:
        readiness=controller.readiness()
        assert not readiness['training_complete'] and readiness['research_owner_present']
        controller.main()  # Read-only default; no registration, sampling or CUDA.
        try:controller.specification()
        except ValueError:pass
        else:raise AssertionError('Premature scientific evaluation was admitted')
        def guard():
            if (time.monotonic()-began>600 or psutil.virtual_memory().available<24000000000
                    or psutil.disk_usage('S:/').free<40000000000):
                raise RuntimeError('Implementation check resource bound')
        cache=AllinCache(reviewed['cache_artifact'],reviewed['cache_sha256'])
        fixtures={}
        for width,kind,api in ((362,Registry,base),(387,RelativeRegistry,relative)):
            registry=kind(entries);fixture=read(OLD/f'{width}-fixture.json')
            assert registry.manifest==fixture['registry']
            model=fixture['model'];initial=copy.deepcopy(model)
            initial['generation']=0;initial['shared']=api.initial(registry)
            for key,state in initial['local_states'].items():
                cfg=dict(fixture['resources'][key]['root_config']);cfg.pop('chance')
                state['board_root_state']=BoardRootRegrets(**cfg).document()
                state['exact_btn_state']=ExactBtnRegrets(key,fixture['resources'][key]['entry_mass']).document()
            full.validate(initial,registry,fixture['resources'])
            fixtures[width]=(registry,fixture['resources'],[initial,model])
        records=[];driver_evidence=None
        for depth in (20,60):
            guard();context_path=GEOMETRY/'fixtures'/f'stack-{depth}-context.json';source=context_path.read_text();key=digest(source.encode())
            retained=read(QUERIES/f'stack-{depth}-queries.json');original_batch=json.loads(retained['batch_source'])
            assert retained['context_source']==source and len(original_batch['deals'])==2
            batch=dict(format=2,batch_id=NAME+'/'+str(depth),seed=original_batch['seed'],query_limit=1000000,
                       deals=copy.deepcopy(original_batch['deals']*16))
            cached=[];reference=[]
            for width,w in ((362,[1,2]),(387,[2,1]),(362,[1,3]),(387,[3,1])):
                registry,resources,documents=fixtures[width];weights=[w,w]
                cached.append(PlayedBank(documents,registry,context_sha256=key,resources=resources,
                    weights_by_player=weights,completed_cycles=2,device='cpu',guard=guard))
                reference.append(ReferenceBank(documents,registry,key,resources,weights))
            answers=[]
            for label,banks in (('cached',cached),('reference',reference)):
                answers.append(evaluate_batch(batch=batch,folder=STORE/f'{depth}-{label}',context_path=context_path,
                    banks=banks,cache=cache,query_executable=EXES[0],evaluation_executable=EXES[1],guard=guard))
            query=read(STORE/f'{depth}-cached'/'queries.json');policy_error=reach_error=0.
            for a,b in zip(cached,reference):
                p,s=a.average(query,guard=guard);q,t=b.average(query,guard=guard)
                policy_error=max(policy_error,float(np.max(abs(p-q))));reach_error=max(reach_error,float(np.max(abs(s-t))))
            value_error=float(np.max(abs(np.asarray(answers[0]['values'])-answers[1]['values'])))
            assert policy_error<1e-10 and reach_error<1e-10 and value_error<1e-9
            # Authenticate actual native artifacts without drawing the journal's
            # prospective test stream. Intent here identifies retained fixture hands.
            parent=STORE/f'journal-{depth}';parent.mkdir()
            journal=EvaluationJournal.create(parent/f'stack-{depth}',context_source=source,
                registration_sha256='1'*64,bank_identities_sha256='2'*64,cache_sha256=cache.sha256,guard=guard)
            for label in ('cached','reference'):
                parts={name:(STORE/f'{depth}-{label}'/name).read_bytes() for name in ARTIFACTS}
                assert journal._evidence(parts,dict(batch=batch))['deals']==32
            if depth==20:
                driver_evidence=driver_check(np.asarray(answers[0]['values']),batch)
            records.append(dict(depth=depth,original_unique_deals=2,transport_deals=32,
                query_rows=len(query['observations']),maximum_policy_error=policy_error,maximum_reach_error=reach_error,
                maximum_native_payoff_error=value_error,actual_native_journal_identity_checks=2))
            print(json.dumps(dict(stage='context-passed',**records[-1])),flush=True)
        guard();assert all(digest(Path(p).read_bytes())==h for p,h in inputs.items())
        files={str(p):digest(p.read_bytes()) for p in STORE.rglob('*') if p.is_file()}
        logical=sum(Path(p).stat().st_size for p in files);assert logical<512000000
        result=dict(complete=True,passed=True,seconds=time.monotonic()-began,records=records,driver=driver_evidence,
            logical_bytes=logical,artifacts=files,inputs=inputs,controller_sha256=digest(CONTROLLER.read_bytes()),
            controller_readonly_default_checked=True,unfinished_training_admission_refused=True,
            actual_model_math=True,actual_native_evaluation=True,synthetic_routing_models=True,played_bank_length=2,
            long_64_model_throughput_measured=False,new_scientific_test_hands=False,scientific_accuracy_evidence=False,
            scientific_training=False,gpu=False,production_modified=False)
        durable(output,encoded(result));print(json.dumps(dict(passed=True,seconds=result['seconds'],logical_bytes=logical)))
    except Exception:
        durable(failure,encoded(dict(passed=False,seconds=time.monotonic()-began,traceback=traceback.format_exc())))
        raise


if __name__=='__main__':main()
