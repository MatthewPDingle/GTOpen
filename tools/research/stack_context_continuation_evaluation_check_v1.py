"""CPU qualification of corrected provenance and unchanged evaluation methods.

Synthetic 64-cycle metadata tests selection. Retained actual cycle-one models
and archives test receipt reconstruction with only the unpublished receipt
transport mocked. No fits, fresh deals, GPU scoring or native reruns.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
from unittest.mock import patch
import psutil
import stack_context_final_bank_v2 as selection
import stack_context_final_bank_check_v1 as fixtures
import stack_context_matched_evaluation_v1 as original
import stack_context_matched_evaluation_v2 as controller
import stack_context_parallel_continuation_v2 as continuation
from stack_context_inputs_v1 import encoded
from sampled_physical_root_evaluation_v1 import sha,save
from sampled_visible_hybrid_checkpoint_v1 import read_object

OUT=continuation.legacy.OUT
NAME='stack-context-continuation-evaluation-check-v1'


def digest(value):return hashlib.sha256(encoded(value)).hexdigest()


def metadata(spec,entries,registration,comparator):
    result,checkpoints=fixtures.synthetic(spec,entries,registration)
    amendment='a'*64; failure='f'*64; receipts={}
    result.update(continuation_amendment_sha256=amendment,original_failure_sha256=failure)
    for arm in selection.BANK_ORDER:
        receipts[arm]=[]; cfg=spec['arms'][arm]['config']
        for i,record in enumerate(result['arms'][arm]['updates']):
            cycle=i+1; raw={}; chance={}
            for key in cfg['context_order']:
                raw[key+'/source-generation.json']=digest([arm[0],cycle,key,'source'])
                for b in range(13):raw[key+f'/batch-{b:03d}/batch.json']=digest([arm[0],cycle,key,b])
                raw[key+'/board-plan.json']=digest([arm,cycle,key,'distinct-learned-parent'])
                chance[key]=dict(generation=i,boards=[[0,4,8,12,16]],config_sha256=digest(cfg['contexts'][key]['board_root']),
                    parent_state_sha256=digest([arm,i,key]),chance_sha256=digest([arm[0],i,key,'shared-draw']))
            compared=dict(raw)
            for key,row in chance.items():compared[key+'/board-plan.json']=row['chance_sha256']
            document=dict(format=1,arm=arm,cycle=cycle,registration_sha256=registration,
                parent_model=checkpoints[arm]['played_bank'][i],original_source_hashes=raw,board_chance=chance,
                matched_input_identities=compared,own_parent_validated=True,comparator_sha256=comparator)
            evidence=dict(document=document,path='synthetic/'+arm+f'/chance-{cycle:04d}.json',sha256=digest(document))
            receipts[arm].append(evidence);record['paired_sources']=raw
            if cycle>selection.ORIGINAL_PREFIX[arm]:
                record.update(chance_receipt_sha256=evidence['sha256'],continuation_amendment_sha256=amendment,
                    recovered_without_scientific_repeat=arm=='A-relative' and cycle==2)
    return result,checkpoints,receipts,amendment,failure


def main():
    attempt,output,failure=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure'))
    if any(p.exists() for p in (attempt,output,failure)):raise ValueError('Preserve existing qualification evidence')
    if not continuation.legacy.production_available() or psutil.virtual_memory().available<28_000_000_000:
        print(json.dumps(dict(deferred=True,check_started=False)));return
    spec=controller.read(controller.TRAIN_REG); registration=sha(controller.TRAIN_REG)
    comparator_path=Path(__file__).with_name('stack_context_paired_chance_v1.py'); comparator=sha(comparator_path)
    paths={Path(__file__).resolve(),Path(controller.__file__).resolve(),Path(selection.__file__).resolve(),
        Path(original.__file__).resolve(),controller.PLAN,original.PLAN,controller.TRAIN_REG,controller.POPULATION/'entries.json',
        comparator_path,OUT/'stack-context-evaluation-integration-check-v1-result.json',
        OUT/'stack-context-final-bank-check-v1-result.json',continuation.DIAGNOSIS,continuation.legacy.FAILURE}
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(continuation.legacy.ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    inputs={str(p):sha(p) for p in paths}
    save(attempt,dict(inputs=inputs,synthetic_terminal_metadata=True,retained_real_archives=True,new_fits=False,
        new_scientific_deals=False,gpu=False,native_rerun=False))
    began=time.monotonic(); negative=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,FileNotFoundError):negative.append(label)
        else:raise AssertionError('Accepted '+label)
    try:
        old_ast=ast.parse(Path(original.__file__).read_text());new_ast=ast.parse(Path(controller.__file__).read_text())
        transferred=[]
        for name in ('Guard','evaluate','main'):
            a=next(n for n in old_ast.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
            b=next(n for n in new_ast.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
            assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
            transferred.append(name)
        for name in ('load_documents','collect','export','finish','PlayedBank','EvaluationJournal','AllinCache','resources_for'):
            assert getattr(controller,name) is getattr(original,name)
        assert controller.DEPTHS==original.DEPTHS and controller.DEALS==original.DEALS==4096
        assert controller.EXES==original.EXES and controller.BANK_ORDER==original.BANK_ORDER
        integration=controller.read(OUT/'stack-context-evaluation-integration-check-v1-result.json')
        assert integration['complete'] and integration['passed'] and integration['controller_sha256']==sha(original.__file__)
        controller.verify(integration['inputs'])
        ready=controller.readiness(); assert not ready['training_complete'] and ready['original_failed_attempt_preserved']
        controller.main()
        reject('unfinished actual training cannot evaluate',controller.specification)

        entries=controller.read(controller.POPULATION/'entries.json')
        result,checkpoints,receipts,amendment,old_failure=metadata(spec,entries,registration,comparator)
        def choose(result=result,checkpoints=checkpoints,receipts=receipts,spec=spec):
            return selection.select_terminal(result,checkpoints,spec,training_registration_sha256=registration,
                receipts=receipts,amendment_sha256=amendment,original_failure_sha256=old_failure,comparator_sha256=comparator)
        chosen=choose()
        assert chosen['raw_source_hashes_preserved'] and chosen['board_plans_validated_against_own_parents']
        for arm,row in chosen['arms'].items():
            assert [r['generation'] for r in row['played']]==list(range(64))
            assert row['excluded_unplayed']['generation']==64 and row['weights_by_player']==[list(range(1,65))]*2
        assert chosen['arms']['A-baseline']['matched_streams_by_cycle']!=chosen['arms']['A-relative']['matched_streams_by_cycle']
        assert chosen['arms']['A-baseline']['matched_chance_by_cycle']==chosen['arms']['A-relative']['matched_chance_by_cycle']
        for name,mutate in (
            ('missing receipt',lambda rows:rows.pop()),
            ('changed parent',lambda rows:rows[3]['document'].__setitem__('parent_model',checkpoints['A-relative']['next_model'])),
            ('changed raw source',lambda rows:rows[3]['document']['original_source_hashes'].__setitem__('unexpected','0'*64)),
            ('changed action/deal input',lambda rows:rows[3]['document']['matched_input_identities'].__setitem__(next(iter(rows[3]['document']['original_source_hashes'])),'0'*64)),
            ('changed comparator',lambda rows:rows[3]['document'].__setitem__('comparator_sha256','0'*64)),
            ('wrong board generation',lambda rows:next(iter(rows[3]['document']['board_chance'].values())).__setitem__('generation',5)),
            ('unvalidated parent',lambda rows:rows[3]['document'].__setitem__('own_parent_validated',False)),
            ('wrong receipt arm',lambda rows:rows[3]['document'].__setitem__('arm','B-relative')),
            ('unknown receipt field',lambda rows:rows[3]['document'].__setitem__('ignore_this',True))):
            bad=copy.deepcopy(receipts);mutate(bad['A-relative'])
            reject(name,lambda bad=bad:choose(receipts=bad))
        # A consistently rehashed actual change of chance must still fail the
        # cross-arm equality check, not merely the local receipt-hash check.
        bad=copy.deepcopy(receipts);res=copy.deepcopy(result)
        row=bad['A-relative'][3];key=next(iter(row['document']['board_chance']))
        row['document']['board_chance'][key]['chance_sha256']='0'*64
        row['document']['matched_input_identities'][key+'/board-plan.json']='0'*64
        row['sha256']=digest(row['document']);res['arms']['A-relative']['updates'][3]['chance_receipt_sha256']=row['sha256']
        reject('rehash cannot hide genuinely different chance',lambda:choose(result=res,receipts=bad))
        for field,value in (('training_complete',False),('continuation_amendment_sha256','0'*64),('original_failure_sha256','0'*64)):
            reject(field,lambda field=field,value=value:choose(result=dict(result,**{field:value})))
        for name,mutate in (
            ('truncated cycle horizon',lambda r:r['arms']['A-relative'].__setitem__('completed_cycles',63)),
            ('unbound post-correction cycle',lambda r:r['arms']['A-relative']['updates'][3].pop('continuation_amendment_sha256')),
            ('invented recovery',lambda r:r['arms']['B-relative']['updates'][3].__setitem__('recovered_without_scientific_repeat',True))):
            bad=copy.deepcopy(result);mutate(bad);reject(name,lambda bad=bad:choose(result=bad))
        changed=copy.deepcopy(spec);changed['cycles']=63
        reject('changed registered cycle budget',lambda:choose(spec=changed))

        # Actual archived bytes/models. Only receipt transport is mocked because
        # the live continuation has not yet published these append-only receipts.
        arm='A-baseline';train=controller.TRAIN;folder=train/arm
        progress=controller.read(folder/'progress.json')
        cp=json.loads(read_object(folder/'objects',progress['updates'][1]['checkpoint']))
        prepared=controller.read(OUT/'stack-context-population-v1-result.json')
        rt=continuation.runtime_for(arm,spec,prepared)
        document=continuation.chance_receipt(arm,1,cp['played_bank'][0],progress['updates'][0]['paired_sources'],spec,rt,lambda:None)
        receipt_path=folder/'chance-0001.json';old_read=selection.read;old_sha=selection.sha
        supplied=copy.deepcopy(document)
        def read_receipt(p):return supplied if Path(p)==receipt_path else old_read(p)
        def sha_receipt(p):return digest(supplied) if Path(p)==receipt_path else old_sha(p)
        with patch.object(selection,'read',side_effect=read_receipt),patch.object(selection,'sha',side_effect=sha_receipt):
            evidence,files=selection.authenticate_cycle(train,arm,1,progress,cp,spec,rt,guard=lambda:None)
            assert evidence['document']==document
            supplied['parent_model']=cp['next_model']
            reject('forged parent rejected by actual model/board reconstruction',lambda:selection.authenticate_cycle(train,arm,1,progress,cp,spec,rt,guard=lambda:None))
            supplied=copy.deepcopy(document);key=next(iter(supplied['board_chance']))
            supplied['board_chance'][key]['boards'][0][0]=51
            reject('forged board rejected despite updated receipt digest',lambda:selection.authenticate_cycle(train,arm,1,progress,cp,spec,rt,guard=lambda:None))
        inputs.update({str(p):sha(p) for p in files if p!=receipt_path})
        inputs[str(OUT/'stack-context-population-v1-result.json')]=sha(OUT/'stack-context-population-v1-result.json')
        inputs.update(prepared['artifacts'])
        controller.verify(inputs);assert time.monotonic()-began<900
        answer=dict(complete=True,passed=True,seconds=time.monotonic()-began,inputs=inputs,
            controller_sha256=sha(controller.__file__),selection_sha256=sha(selection.__file__),
            unchanged_evaluation_functions_verified=True,unchanged_AST_definitions=transferred,
            original_native_integration_result_sha256=sha(OUT/'stack-context-evaluation-integration-check-v1-result.json'),
            synthetic_64_cycle_selection=True,selected_generations=list(range(64)),excluded_generation=64,
            retained_actual_cycle_authenticated=True,receipt_transport_mocked=True,negative_cases=negative,
            new_fits=False,new_scientific_deals=False,native_rerun=False,gpu=False,actual_final_banks_available=False,
            scientific_accuracy_qualified=False,production_modified=False)
        save(output,answer)
        print(json.dumps(dict(passed=True,seconds=answer['seconds'],negative_cases=len(negative),new_scientific_work=False)))
    except BaseException as error:
        save(failure,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True,automatic_retry_allowed=False))
        raise


if __name__=='__main__':main()
