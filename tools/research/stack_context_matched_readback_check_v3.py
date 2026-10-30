"""Qualify independent readback on retained native evidence and model fixtures.

No new native execution, scientific draws, training or CUDA. Actual terminal
comparison and its full64-bank reader remain unavailable until training ends.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
from unittest.mock import patch
import numpy as np
import psutil
import stack_context_matched_readback_v3 as reader
import stack_context_independent_chance_audit_v1 as chance
import stack_context_independent_audit_check_v1 as ranges_fixture
import stack_context_policy_v1 as baseline
import stack_context_relative_policy_v1 as relative
import stack_context_parallel_continuation_v2 as continuation
from stack_context_preflop_export_v1 import export,queries_from_catalog
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from sampled_visible_hybrid_checkpoint_v1 import read_object
from owned_columnar_evaluation_archive_v1 import ARTIFACTS,durable

NAME='stack-context-matched-readback-check-v3'
OUT=reader.OUT
INTEGRATION=Path('S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
MODELS=Path('S:/GTOpen-research/stack-context-full-control-v1')


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def clone(parts,name,value):return dict(parts,**{name:encoded(value)})


def main():
    attempt,output,failure=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure'))
    reader.require(not any(p.exists() for p in (attempt,output,failure)), 'Preserve existing readback check')
    reader.require(reader.production_available() and psutil.virtual_memory().available>28_000_000_000, 'Yield to production/memory pressure')
    native_proof_path=OUT/'stack-context-evaluation-integration-check-v1-result.json'
    native_proof=reader.read(native_proof_path);reader.require(native_proof['passed'] and native_proof['complete'], 'Retained native evidence required')
    reader.verify(native_proof['inputs']);reader.verify(native_proof['artifacts'])
    paths={Path(__file__).resolve(),Path(reader.__file__).resolve(),Path(chance.__file__).resolve(),reader.PLAN,
        reader.TRAIN_REG,native_proof_path,reader.AUDIT_CONTROL,OUT/'stack-context-matched-readback-check-v2-failure.json',OUT/'stack-context-complete-allin-cache-v1-readback.json',
        OUT/'stack-context-full-control-v1-result.json',OUT/'stack-context-full-control-v1-registration.json',
        OUT/'stack-context-population-v1-result.json'}
    paths.update(Path(p) for p in native_proof['artifacts'])
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(reader.ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    inputs={str(p):reader.sha(p) for p in paths}
    durable(attempt,encoded(dict(inputs=inputs,retained_native_evidence=True,synthetic_range_policy=True,
        new_scientific_deals=False,fitting=False,native_execution=False,gpu=False)))
    began=time.monotonic();negative=[];records=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,TypeError):negative.append(label)
        else:raise AssertionError('Corruption accepted: '+label)
    try:
        reader.torch.set_num_threads(4)
        reader.torch.use_deterministic_algorithms(True)
        ready=reader.readiness();assert not ready['evaluation_result_present'] and not ready['readback_started']
        reader.main()
        reject('actual unfinished evaluation cannot be read back',lambda:reader.main(run=True))
        cache_proof=reader.read(OUT/'stack-context-complete-allin-cache-v1-readback.json')
        cache=reader.AllinCache(cache_proof['cache_artifact'],cache_proof['cache_sha256'])
        inputs[cache_proof['cache_artifact']]=reader.sha(cache_proof['cache_artifact'])
        old_proof=reader.read(OUT/'stack-context-full-control-v1-result.json')
        old_reg=reader.read(OUT/'stack-context-full-control-v1-registration.json')
        entries=[]
        for depth in reader.DEPTHS:
            context=GEOMETRY/'fixtures'/f'stack-{depth}-context.json';public=GEOMETRY/f'stack-{depth}-public.json'
            for p in (context,public):
                assert reader.sha(p)==old_reg['inputs'][str(p)];inputs[str(p)]=reader.sha(p)
            entries.append(dict(name=f'{depth}bb',split='heldout' if depth in (60,150) else 'fit',
                context_source=context.read_text(),public_document=reader.read(public)))
        fixtures={}
        for width,kind,api in ((362,reader.Registry,baseline),(387,reader.RelativeRegistry,relative)):
            path=MODELS/f'{width}-fixture.json';assert reader.sha(path)==old_proof['artifacts'][str(path)];inputs[str(path)]=reader.sha(path)
            fixture=reader.read(path);registry=kind(entries);assert registry.manifest==fixture['registry']
            model=fixture['model'];initial=copy.deepcopy(model);initial['generation']=0;initial['shared']=api.initial(registry)
            for key,state in initial['local_states'].items():
                config=dict(fixture['resources'][key]['root_config']);config.pop('chance')
                state['board_root_state']=BoardRootRegrets(**config).document()
                state['exact_btn_state']=ExactBtnRegrets(key,fixture['resources'][key]['entry_mass']).document()
            reader.full.validate(initial,registry,fixture['resources'])
            fixtures[width]=dict(documents=[initial,model],registry=registry,resources=fixture['resources'])
        for depth in (20,60):
            parts={name:(INTEGRATION/f'{depth}-cached'/name).read_bytes() for name in ARTIFACTS}
            query,banks,summary=reader.validate_transport(parts,cache)
            key=hashlib.sha256(query['context_source'].encode()).hexdigest();refs=[]
            for width,w in ((362,[1,2]),(387,[2,1]),(362,[1,3]),(387,[3,1])):
                bank=dict(fixtures[width],weights=[w,w]);refs.append(reader.reference_function(bank,key))
            parity=reader.check_reference_policies(query,banks,summary,refs,guard=lambda:None)
            assert len(parity)==4 and all(r['maximum_policy_error']<1e-10 for r in parity)
            records.append(dict(depth=depth,query_rows=len(query['observations']),reference_arms=parity))
            reject(str(depth)+'/missing artifact',lambda:reader.validate_transport({k:v for k,v in parts.items() if k!='native.json'},cache))
            transport=json.loads(parts['profiles.json']);transport['profiles'].reverse()
            reject(str(depth)+'/profile ordering',lambda:reader.validate_transport(clone(parts,'profiles.json',transport),cache))
            transport=json.loads(parts['profiles.json']);transport['profiles'][1]['policies'][0]['hi']='wrong-key'
            reject(str(depth)+'/policy key',lambda:reader.validate_transport(clone(parts,'profiles.json',transport),cache))
            transport=json.loads(parts['profiles.json']);i=next(i for i,o in enumerate(query['observations']) if o['n']>=2)
            row=transport['profiles'][1]['policies'][i];old=row['probabilities']
            row['probabilities']=[0.,1.,0.,0.] if old==[1.,0.,0.,0.] else [1.,0.,0.,0.]
            reject(str(depth)+'/nonself crossing',lambda:reader.validate_transport(clone(parts,'profiles.json',transport),cache))
            transport=json.loads(parts['profiles.json']);i=next(i for i,o in enumerate(query['observations']) if o['n']<4)
            n=query['observations'][i]['n'];bad=[.9/n if j<n else (.1 if j==n else 0.) for j in range(4)]
            transport['profiles'][0]['policies'][i]['probabilities']=bad
            reject(str(depth)+'/illegal action',lambda:reader.validate_transport(clone(parts,'profiles.json',transport),cache))
            coverage=copy.deepcopy(summary);coverage['coverage'].pop()
            reject(str(depth)+'/missing coverage',lambda:reader.validate_transport(clone(parts,'summary.json',coverage),cache))
            raw=json.loads(parts['query-batch.json']);raw['allin_hidden']='not-visible'
            altered=clone(parts,'query-batch.json',raw);q=copy.deepcopy(query);q['batch_source']=altered['query-batch.json'].decode()
            altered=clone(altered,'queries.json',q)
            reject(str(depth)+'/hidden visible-query label',lambda:reader.validate_transport(altered,cache))
            raw=json.loads(parts['query-batch.json']);raw['deals'][0][1]=raw['deals'][0][0]
            altered=clone(parts,'query-batch.json',raw);q=copy.deepcopy(query);q['batch_source']=altered['query-batch.json'].decode()
            altered=clone(altered,'queries.json',q)
            reject(str(depth)+'/duplicate physical card',lambda:reader.validate_transport(altered,cache))
            damaged=[p.copy() for p in banks];damaged[0][0,0]+=.01
            reject(str(depth)+'/reference probability binding',lambda:reader.check_reference_policies(query,damaged,summary,refs,guard=lambda:None))

        # Independent preflop ancestry and physical range-policy binding.
        prepared=reader.read(OUT/'stack-context-population-v1-result.json')
        source=next(r for r in prepared['contexts'].values() if r['depth']==20)
        text=Path(source['context_path']).read_text();context=json.loads(text);catalog=reader.read(source['physical_catalog'])
        matrix=reader.read(source['matrix']);inputs.update(source['artifacts'])
        query=reader.catalog_queries(text,catalog);expected,_=queries_from_catalog(text,catalog)
        assert query['observations']==expected['observations'] and query['context_source']==expected['context_source']
        mixture=ranges_fixture.Mixture();p,support=mixture.average(query,guard=lambda:None)
        result=json.loads(encoded(export(text,catalog,matrix['class_mass'],mixture,guard=lambda:None)))
        binding=reader.bind_range_policy(context,catalog,result,p,support)
        physical=reader.audit_ranges(context,result,guard=lambda:None)
        assert binding['maximum_policy_error']<1e-10 and physical['zero_arrival_nodes']>0
        broken=copy.deepcopy(result);broken['nodes'][0]['action_probabilities_by_class'][0][0]+=.1
        reject('range probability/model binding',lambda:reader.bind_range_policy(context,catalog,broken,p,support))
        broken=copy.deepcopy(result);broken['nodes'][0]['own_history_weighted_model_support_by_class'][0]+=.1
        reject('range reach/model binding',lambda:reader.bind_range_policy(context,catalog,broken,p,support))
        reject('incomplete physical replay',lambda:reader.bind_range_policy(context,catalog,result,p[:-1],support[:-1]))

        # Actual archived cycle-two boards and immutable generation-one parent;
        # no mutable live progress file is made an input pin.
        spec=reader.read(reader.TRAIN_REG);arm='A-baseline';folder=reader.TRAIN/arm
        progress=reader.read(folder/'progress.json');record=progress['updates'][1]
        checkpoint=json.loads(read_object(folder/'objects',record['checkpoint']));ref=checkpoint['played_bank'][1]
        rt=continuation.runtime_for(arm,spec,prepared)
        parent=reader.full.read_model(folder/'objects',ref,rt['registry'],rt['resources'])
        cfg=spec['arms'][arm]['config'];archive=folder/'archive-0002';archive_plan=reader.read(archive/'plan.json')
        plans={};proof=continuation.chance_receipt(arm,2,ref,record['paired_sources'],spec,rt,lambda:None)
        inputs[str(folder/'objects'/ref['file'])]=reader.sha(folder/'objects'/ref['file'])
        inputs[str(folder/'objects'/record['checkpoint']['file'])]=reader.sha(folder/'objects'/record['checkpoint']['file'])
        for key in cfg['context_order']:
            plan=continuation.board_plan(folder/'cycle-0002',archive,key,record['paired_sources'][key+'/board-plan.json'],lambda:None)
            plans[key]=plan
            row=next(j for j in archive_plan['jobs'] if Path(j['source']).name==key and 'board-plan.json' in j['names'])
            for path in (Path(row['destination']),Path(row['destination']).with_suffix('.xz.json')):inputs[str(path)]=reader.sha(path)
            rebuilt=chance.reconstruct(plan,parent['local_states'][key]['board_root_state'],cfg['contexts'][key]['board_root'],1)
            assert rebuilt==proof['board_chance'][key]
            corrupt=copy.deepcopy(plan);corrupt['boards'][0][0]=(corrupt['boards'][0][0]+1)%52
            reject(key+'/changed board',lambda corrupt=corrupt,key=key:chance.reconstruct(corrupt,parent['local_states'][key]['board_root_state'],cfg['contexts'][key]['board_root'],1))
            corrupt=copy.deepcopy(parent['local_states'][key]['board_root_state']);corrupt['regret_sums'][0][0]+=1
            reject(key+'/bad parent seal',lambda corrupt=corrupt,key=key:chance.reconstruct(plans[key],corrupt,cfg['contexts'][key]['board_root'],1))
            reject(key+'/wrong generation',lambda key=key:chance.reconstruct(plans[key],parent['local_states'][key]['board_root_state'],cfg['contexts'][key]['board_root'],2))
        compared=chance.audit_documents(arm,2,record,proof,ref,parent,cfg,plans,registration=reader.sha(reader.TRAIN_REG),
            comparator=reader.sha(reader.ROOT/'tools/research/stack_context_paired_chance_v1.py'))
        assert compared==proof['matched_input_identities']
        # The continuation has not published receipts yet. Mock only that one
        # file's transport; read and authenticate the real immutable archive.
        receipt_path=folder/'chance-0002.json';receipt_bytes=encoded(proof)
        receipt_sha=hashlib.sha256(receipt_bytes).hexdigest()
        original_read,original_sha=chance.read,chance.sha
        def receipt_read(path):
            return copy.deepcopy(proof) if Path(path)==receipt_path else original_read(path)
        def receipt_digest(path):
            return receipt_sha if Path(path)==receipt_path else original_sha(path)
        selected=dict(path=str(receipt_path),sha256=receipt_sha)
        for name in ('index.json','plan.json','retired.json'):
            inputs[str(archive/name)]=reader.sha(archive/name)
        with patch.object(chance,'read',receipt_read),patch.object(chance,'sha',receipt_digest):
            rebuilt=chance.load_cycle(reader.TRAIN,arm,2,record,selected,ref,parent,cfg,
                registration=reader.sha(reader.TRAIN_REG),
                comparator=reader.sha(reader.ROOT/'tools/research/stack_context_paired_chance_v1.py'),
                amendment='not-required-for-original-published-prefix',guard=lambda:None)
            assert rebuilt==compared
            broken=copy.deepcopy(record);broken['archive_index_sha256']='0'*64
            reject('altered archived-cycle index',lambda:chance.load_cycle(reader.TRAIN,arm,2,broken,selected,ref,parent,cfg,
                registration=reader.sha(reader.TRAIN_REG),comparator=proof['comparator_sha256'],amendment='unused',guard=lambda:None))
        corrupt=copy.deepcopy(proof);corrupt['parent_model']=checkpoint['next_model']
        reject('forged receipt parent',lambda:chance.audit_documents(arm,2,record,corrupt,ref,parent,cfg,plans,
            registration=reader.sha(reader.TRAIN_REG),comparator=reader.sha(reader.ROOT/'tools/research/stack_context_paired_chance_v1.py')))
        reader.verify(inputs);assert time.monotonic()-began<900
        answer=dict(complete=True,passed=True,seconds=time.monotonic()-began,inputs=inputs,reader_sha256=reader.sha(reader.__file__),
            retained_native_records=records,range_binding=binding,physical_range_audit=physical,
            independent_seed_parent_reconstructions=5,actual_archived_cycle_binding=True,receipt_transport_mocked=True,
            negative_cases=negative,actual_model_math=True,
            model_fixture_bank_length=2,synthetic_range_policy_generations=64,
            actual_final_64_banks_reviewed=False,actual_scientific_result_reviewed=False,
            new_scientific_deals=False,fitting=False,native_execution=False,gpu=False,production_modified=False)
        durable(output,encoded(answer));print(json.dumps(dict(passed=True,seconds=answer['seconds'],negative_cases=len(negative))))
    except BaseException as error:
        durable(failure,encoded(dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True,automatic_retry_allowed=False)));raise


if __name__=='__main__':main()
