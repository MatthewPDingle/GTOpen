"""Qualify pressure provenance and unchanged evaluation/readback algorithms.

Only synthetic metadata, retained immutable proofs and AST comparisons are
used. No worker, fit, scientific sample, native subprocess or GPU is launched.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import ast
import copy
import hashlib
import json
from pathlib import Path
import time
import traceback
from unittest.mock import patch
import psutil
import stack_context_pressure_provenance_v1 as pressure
import stack_context_final_bank_v4 as selector
import stack_context_final_bank_v3 as old_selector
import stack_context_final_bank_v2 as old_basis
import stack_context_matched_evaluation_v4 as evaluator
import stack_context_matched_evaluation_v3 as old_evaluator
import stack_context_final_bank_throughput_v3 as throughput
import stack_context_final_bank_throughput_v2 as old_throughput
import stack_context_matched_readback_v5 as reader
import stack_context_matched_readback_v4 as old_reader
import stack_context_continuation_evaluation_check_v2 as fixture

NAME='stack-context-pressure-consumer-check-v2'
OUT=pressure.OUT


def defs(module):
    return {n.name:n for n in ast.parse(Path(module.__file__).read_text()).body
        if isinstance(n,(ast.FunctionDef,ast.ClassDef))}


def compare(old,new,names):
    a,b=defs(old),defs(new)
    for name in names:assert ast.dump(a[name],include_attributes=False)==ast.dump(b[name],include_attributes=False),name
    return list(names)


def main():
    attempt,failed=(OUT/(NAME+s+'.json') for s in ('-attempt','-failure'))
    pressure.require(not any(p.exists() for p in (attempt,failed,pressure.QUALIFICATION)), 'Existing qualification')
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    paths={Path(__file__).resolve(),*(Path(m.__file__).resolve() for m in
        (pressure,selector,old_selector,old_basis,evaluator,old_evaluator,throughput,old_throughput,reader,old_reader,fixture)),
        evaluator.PLAN,throughput.PLAN,reader.PLAN}
    proofs=['stack-context-continuation-evaluation-check-v2-result.json',
        'stack-context-final-bank-throughput-v2-check-result.json','stack-context-matched-readback-check-v4-result.json',
        'stack-context-evaluation-integration-check-v1-result.json','stack-context-independent-audit-check-v1-result.json']
    for name in proofs:
        p=OUT/name;record=pressure.read(p);assert record['complete'] and record['passed']
        pressure.continuation.legacy.verify(record['inputs']);paths.add(p);paths.update(map(Path,record['inputs']))
    paths.update(OUT/('stack-context-pressure-consumer-check-v1'+s+'.json') for s in ('-attempt','-failure'))
    paths.add(Path(__file__).with_name('stack_context_pressure_consumer_check_v1.py'))
    inputs={str(p):pressure.sha(p) for p in paths}
    pressure.coordinator.save(attempt,dict(inputs=inputs,scientific_workers_launched=0,scientific_fits=0,native_calls=0))
    began=time.monotonic();negative=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,FileNotFoundError,KeyError,TypeError):negative.append(label)
        else:raise AssertionError('Accepted '+label)
    try:
        unchanged={}
        unchanged['evaluation']=compare(old_evaluator,evaluator,
            ('read','verify','readiness','status','specification','Guard','evaluate','main'))
        throughput_defs=defs(old_throughput)
        unchanged['throughput']=compare(old_throughput,throughput,[n for n in throughput_defs if n not in ('terminal_banks','main')])
        a,b=defs(old_throughput)['terminal_banks'],defs(throughput)['terminal_banks']
        class ReplacePressure(ast.NodeTransformer):
            def visit_Attribute(self,node):
                node=self.generic_visit(node)
                if isinstance(node.value,ast.Name) and node.value.id=='pressure' and node.attr in ('RESULT','FAILURE'):
                    node.value.id='continuation'
                return node
        assert ast.dump(a,include_attributes=False)==ast.dump(ReplacePressure().visit(b),include_attributes=False)
        a,b=defs(old_throughput)['main'],defs(throughput)['main']
        assert ast.dump(a,include_attributes=False)==ast.dump(ReplacePressure().visit(b),include_attributes=False)
        unchanged['throughput'].extend(['terminal_banks except exact result/failure namespace','main except training-readiness result namespace'])
        unchanged['reader']=compare(old_reader,reader,[n for n in defs(old_reader) if n not in ('verify_correction','main')])
        # Prior-basis copy retains all old checks except the single absence guard.
        a=copy.deepcopy(defs(old_basis)['verify_correction']);b=copy.deepcopy(defs(pressure)['verify_prior_basis']);b.name=a.name
        removed=[n for n in a.body if isinstance(n,ast.Expr) and 'A new continuation failure has no approved correction' in ast.unparse(n)]
        assert len(removed)==1;a.body.remove(removed[0])
        assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
        a=copy.deepcopy(defs(old_selector)['verify_correction']);b=copy.deepcopy(defs(selector)['verify_correction'])
        class ReplacePrior(ast.NodeTransformer):
            def visit_Attribute(self,node):
                node=self.generic_visit(node)
                if isinstance(node.value,ast.Name) and node.value.id=='pressure' and node.attr=='verify_prior_correction':
                    node.value.id='original';node.attr='verify_correction'
                return node
        assert ast.dump(a,include_attributes=False)==ast.dump(ReplacePrior().visit(b),include_attributes=False)
        for name in ('collect','export','finish','PlayedBank','EvaluationJournal','AllinCache','resources_for','load_documents'):
            assert getattr(evaluator,name) is getattr(old_evaluator,name)
        assert evaluator.DEALS==old_evaluator.DEALS==4096 and evaluator.DEPTHS==old_evaluator.DEPTHS
        assert evaluator.EXES==old_evaluator.EXES and evaluator.BANK_ORDER==old_evaluator.BANK_ORDER
        assert selector.authenticate_cycle is old_selector.authenticate_cycle
        assert throughput.FIXTURE==old_throughput.FIXTURE
        actual_identity,actual_paths=pressure.verify_pressure()
        paths.update(actual_paths);paths.update(pressure.verify_prior_correction())
        paths.update(selector.verify_correction())
        reject('actual incomplete bank cannot run throughput',throughput.terminal_banks)
        reject('actual incomplete bank cannot admit evaluation',evaluator.specification)
        reject('synthetic terminal cannot substitute for actual result',lambda:pressure.verify_pressure({'training_complete':True}))
        # Synthetic 64-cycle selection reuses the already qualified original
        # selector and exact recovery metadata. Only proof transport is mocked.
        spec=pressure.read(evaluator.TRAIN_REG);registration=pressure.sha(evaluator.TRAIN_REG)
        entries=pressure.read(evaluator.POPULATION/'entries.json')
        comparator=pressure.sha(Path(__file__).with_name('stack_context_paired_chance_v1.py'))
        result,checkpoints,receipts,amendment,legacy_failure,recovery_identity,recovery_outcome=fixture.metadata(spec,entries,registration,comparator)
        pressure_identity=copy.deepcopy(actual_identity)
        pressure_identity['complete_prefix_sha256']={a:pressure.coordinator.prefix_hash(result['arms'][a],n)
            for a,n in pressure.coordinator.COUNTS.items()}
        result.update(resource_pressure_failure_sha256=pressure_identity['pressure_failure_sha256'],
            resource_pressure_review_sha256=pressure_identity['boundary_review_sha256'],
            operational_admission_sha256=pressure_identity['operational_admission_sha256'],
            original_scientific_worker_unchanged=True,cycles_retried=False)
        kwargs=dict(training_registration_sha256=registration,receipts=receipts,
            amendment_sha256=amendment,original_failure_sha256=legacy_failure,comparator_sha256=comparator)
        def original_selection(r,c,s,**values):
            return old_selector._select_with_recovery(r,c,s,recovery_identity=recovery_identity,
                recovery_outcome=recovery_outcome,**values)
        with patch.object(selector.original,'select_terminal',side_effect=original_selection):
            chosen=selector._select_with_pressure(result,checkpoints,spec,pressure_identity=pressure_identity,**kwargs)
            legacy=original_selection(result,checkpoints,spec,**kwargs)
            expected=copy.deepcopy(legacy);expected.update(format=4,resource_pressure=pressure_identity,recognized_clean_pressure_stop_only=True)
            assert chosen==expected
            for arm in evaluator.BANK_ORDER:
                assert [r['generation'] for r in chosen['arms'][arm]['played']]==list(range(64))
                assert chosen['arms'][arm]['weights_by_player']==[list(range(1,65))]*2
                assert chosen['arms'][arm]['excluded_unplayed']['generation']==64
                damaged=copy.deepcopy(result);damaged['arms'][arm]['updates'][0]['ignored_change']='changed'
                reject(arm+' changed frozen pressure prefix',lambda d=damaged:selector._select_with_pressure(d,checkpoints,spec,pressure_identity=pressure_identity,**kwargs))
            for field,value in [('resource_pressure_failure_sha256','0'*64),('resource_pressure_review_sha256','0'*64),
                ('operational_admission_sha256','0'*64),('original_scientific_worker_unchanged',False),('cycles_retried',True)]:
                reject(field,lambda f=field,v=value:selector._select_with_pressure(dict(result,**{f:v}),checkpoints,spec,pressure_identity=pressure_identity,**kwargs))
            damaged=copy.deepcopy(checkpoints);damaged['A-relative']['played_bank'].pop()
            reject('missing model',lambda:selector._select_with_pressure(result,damaged,spec,pressure_identity=pressure_identity,**kwargs))
            changed=copy.deepcopy(spec);changed['cycles']=63
            reject('changed registered horizon',lambda:selector._select_with_pressure(result,checkpoints,changed,pressure_identity=pressure_identity,**kwargs))
            changed=copy.deepcopy(spec);changed['arms']['A-relative']['config']['unregistered_change']=True
            reject('changed registered scientific config',lambda:selector._select_with_pressure(result,checkpoints,changed,pressure_identity=pressure_identity,**kwargs))
        for field,value in [('recognized_pressure_stop_only',False),('scientific_cycles_retried',True),
            ('scientific_selection_and_gates_unchanged',False),('original_registration_sha256','0'*64)]:
            reject('pressure identity '+field,lambda f=field,v=value:pressure.validate_prefixes(result['arms'],dict(pressure_identity,**{f:v})))
        # Independently compute the same synthetic prefix hashes using only
        # the reader's JSON encoding contract, rather than the selector helper.
        independent={}
        for arm,n in pressure.coordinator.COUNTS.items():
            p=result['arms'][arm];prefix=dict(p,completed_cycles=n,checkpoint=p['updates'][n-1]['checkpoint'],updates=p['updates'][:n])
            independent[arm]=hashlib.sha256((json.dumps(prefix,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
        assert independent==pressure_identity['complete_prefix_sha256']
        # Exercise the entire independently implemented reader proof, using
        # explicitly synthetic transport and successful worker outcome metadata.
        # The underlying original 64-generation selection above remains real code.
        documents={}
        review=copy.deepcopy(pressure.read(pressure.REVIEW));review['inputs']={}
        for arm in pressure.coordinator.COUNTS:review['boundaries'][arm]['progress_sha256']=independent[arm]
        documents[pressure.REVIEW]=review
        def toy_sha(path):
            p=Path(path)
            if p in documents:return hashlib.sha256(pressure.coordinator.encoded(documents[p])).hexdigest()
            return old_sha(path)
        audit=copy.deepcopy(pressure.read(pressure.READBACK));audit['inputs']={};audit['review_sha256']=toy_sha(pressure.REVIEW)
        documents[pressure.READBACK]=audit
        admission=copy.deepcopy(pressure.read(pressure.ADMISSION));admission['inputs']={}
        admission.update(boundary_review_sha256=toy_sha(pressure.REVIEW),readback_sha256=toy_sha(pressure.READBACK))
        documents[pressure.ADMISSION]=admission
        attempt_data=copy.deepcopy(pressure.read(pressure.coordinator.ATTEMPT));attempt_data['admission_sha256']=toy_sha(pressure.ADMISSION)
        documents[pressure.coordinator.ATTEMPT]=attempt_data
        synthetic_terminal=copy.deepcopy(result)
        synthetic_terminal.update(resource_pressure_review_sha256=toy_sha(pressure.REVIEW),operational_admission_sha256=toy_sha(pressure.ADMISSION))
        documents[reader.TRAIN_RESULT]=synthetic_terminal
        toy_identity=copy.deepcopy(pressure_identity)
        toy_identity.update(boundary_review_sha256=toy_sha(pressure.REVIEW),boundary_readback_sha256=toy_sha(pressure.READBACK),
            operational_admission_sha256=toy_sha(pressure.ADMISSION),training_result_sha256=toy_sha(reader.TRAIN_RESULT))
        synthetic_selection=copy.deepcopy(chosen);synthetic_selection['resource_pressure']=toy_identity
        for i,(arm,n) in enumerate(pressure.coordinator.COUNTS.items()):
            start_path=OUT/(pressure.coordinator.NAME+'-'+arm+'-started.json')
            outcome_path=reader.TRAIN/('stack-context-parallel-continuation-v2-'+attempt_data['invocation']+'-'+arm+'.json')
            progress_path=reader.TRAIN/arm/'progress.json';documents[progress_path]=synthetic_terminal['arms'][arm]
            documents[start_path]=dict(arm=arm,pid=1000+i,process_created=1.+i,
                starts_after_complete_cycle=n,invocation=attempt_data['invocation'])
            documents[outcome_path]=dict(arm=arm,pid=1000+i,process_created=1.+i,complete=True,
                stopped_at_complete_boundary=False,progress_sha256=toy_sha(progress_path))
        old_read,old_sha=reader.read,reader.sha
        def toy_read(path):return copy.deepcopy(documents[Path(path)]) if Path(path) in documents else old_read(path)
        with patch.object(reader,'read',side_effect=toy_read),patch.object(reader,'sha',side_effect=toy_sha):
            assert reader.verify_independent_pressure(synthetic_terminal,synthetic_selection)
            for arm in pressure.coordinator.COUNTS:
                outcome_path=reader.TRAIN/('stack-context-parallel-continuation-v2-'+attempt_data['invocation']+'-'+arm+'.json')
                pristine=copy.deepcopy(documents[outcome_path]);documents[outcome_path]['complete']=False
                reject('reader '+arm+' incomplete worker',lambda:reader.verify_independent_pressure(synthetic_terminal,synthetic_selection))
                documents[outcome_path]=pristine
                damaged=copy.deepcopy(synthetic_terminal);damaged['arms'][arm]['updates'][0]['other']='changed'
                reject('reader '+arm+' changed historical prefix',lambda d=damaged:reader.verify_independent_pressure(d,synthetic_selection))
            damaged=copy.deepcopy(synthetic_selection);damaged['resource_pressure']['recognized_pressure_stop_only']=False
            reject('reader unknown pressure identity',lambda:reader.verify_independent_pressure(synthetic_terminal,damaged))
            documents[pressure.coordinator.ATTEMPT]=dict(attempt_data,invocation='other')
            reject('reader mismatched actual attempt',lambda:reader.verify_independent_pressure(synthetic_terminal,synthetic_selection))
            documents[pressure.coordinator.ATTEMPT]=attempt_data
        pressure.continuation.legacy.verify(inputs)
        inputs.update({str(p):pressure.sha(p) for p in paths})
        answer=dict(complete=True,passed=True,inputs=inputs,seconds=time.monotonic()-began,
            pressure_provenance_sha256=pressure.sha(pressure.__file__),controller_sha256=pressure.sha(evaluator.__file__),
            runner_sha256=pressure.sha(throughput.__file__),reader_sha256=pressure.sha(reader.__file__),
            selection_sha256=pressure.sha(selector.__file__),unchanged_scientific_functions_verified=True,
            unchanged_AST_definitions=unchanged,prior_basis_exact_except_replaced_absence_guard=True,
            exact_reviewed_pressure_boundary_verified=actual_identity,synthetic_64_cycle_selection=True,
            original_selection_and_weights_unchanged=True,selected_generations=list(range(64)),excluded_generation=64,
            separate_pressure_proof_transport=True,negative_cases=negative,
            independent_prefix_arithmetic_controls=4,independent_reader_pressure_transport_control=True,
            synthetic_proof_transport_only=True,scientific_workers_launched=0,native_calls=0,scientific_fits=0,
            new_scientific_deals=0,gpu=False,actual_final_banks_available=False,actual_cuda_qualified=False,
            scientific_accuracy_qualified=False,production_modified=False)
        revision=OUT/(NAME+'-result.json');pressure.coordinator.save(revision,answer)
        receipt=dict(answer,qualification_revision=2,prior_failed_qualification_preserved=True,
            qualification_result_sha256=pressure.sha(revision),inputs=dict(inputs,**{str(revision):pressure.sha(revision)}))
        pressure.coordinator.save(pressure.QUALIFICATION,receipt)
        print(json.dumps({k:v for k,v in answer.items() if k not in ('inputs','unchanged_AST_definitions','exact_reviewed_pressure_boundary_verified','negative_cases','selected_generations')}))
    except BaseException as error:
        pressure.coordinator.save(failed,dict(error=repr(error),traceback=traceback.format_exc(),inputs=inputs,preserve_evidence=True));raise


if __name__=='__main__':main()
