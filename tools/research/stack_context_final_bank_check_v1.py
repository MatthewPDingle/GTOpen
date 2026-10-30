"""CPU selection checks on synthetic completion metadata and real frozen config.

No model scores, training examples, scientific test hands, fits or native runs.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import time
import traceback
import stack_context_final_bank_v1 as selection
from stack_context_inputs_v1 import Registry,encoded
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from owned_columnar_evaluation_archive_v1 import durable,digest

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='stack-context-final-bank-check-v1'
REG=OUT/'stack-context-matched-learning-v1-registration.json'
ENTRIES=Path('S:/GTOpen-research/stack-context-population-v1/entries.json')
TRAIN=Path('S:/GTOpen-research/stack-context-matched-learning-v1')


def ref(kind,label,generation=None):
    identity=hashlib.sha256(label.encode()).hexdigest()
    result=dict(file=kind+'-'+identity+'.json',sha256=identity)
    if generation is not None:
        result['generation']=generation
    return result


def synthetic(spec,entries,registration):
    checkpoints={};progress={}
    for arm in selection.BANK_ORDER:
        cfg=spec['arms'][arm]['config']
        registry=(RelativeRegistry if arm.endswith('relative') else Registry)(entries)
        assert registry.sha256==cfg['registry_sha256']
        cp=dict(format=1,checkpoint_type=selection.TYPE,completed_cycles=64,config=cfg,
            config_sha256=selection.sha_value(cfg),registry=registry.manifest,registry_sha256=registry.sha256,
            contexts={key:{'synthetic_metadata_only':True} for key in registry.fit_contexts},
            played_bank=[ref('fullstackmodel',arm+str(g),g) for g in range(64)],
            next_model=ref('fullstackmodel',arm+'64',64))
        cp_hash=selection.sha_value(cp)
        cp_ref=dict(file='jointcontextcheckpoint-'+cp_hash+'.json',sha256=cp_hash)
        updates=[dict(cycle=g,checkpoint=ref('jointcontextcheckpoint',arm+'checkpoint'+str(g)),
                      paired_sources={'sentinel-source':digest((arm[0]+str(g)).encode())}) for g in range(1,65)]
        updates[-1]['checkpoint']=cp_ref
        progress[arm]=dict(completed_cycles=64,registration_sha256=registration,checkpoint=cp_ref,updates=updates)
        checkpoints[arm]=cp
    result=dict(training_complete=True,registration_sha256=registration,production_modified=False,arms=progress)
    return result,checkpoints


def main():
    attempt=OUT/(NAME+'-attempt.json');output=OUT/(NAME+'-result.json');failure=OUT/(NAME+'-failure.json')
    if any(p.exists() for p in (attempt,output,failure)):
        raise ValueError('Preserve existing started or completed check')
    module=Path(__file__).with_name('stack_context_final_bank_v1.py')
    inputs={str(p):digest(p.read_bytes()) for p in (Path(__file__).resolve(),module,REG,ENTRIES)}
    durable(attempt,encoded(dict(inputs=inputs,synthetic_complete_metadata=True,actual_model_values=False)))
    began=time.monotonic();negative=[]
    try:
        spec=json.loads(REG.read_bytes());registration=digest(REG.read_bytes());entries=json.loads(ENTRIES.read_bytes())
        result,checkpoints=synthetic(spec,entries,registration)
        chosen=selection.select_terminal(result,checkpoints,spec,training_registration_sha256=registration)
        assert chosen['bank_order']==['A-baseline','A-relative','B-baseline','B-relative']
        for arm,row in chosen['arms'].items():
            assert [m['generation'] for m in row['played']]==list(range(64))
            assert row['excluded_unplayed']['generation']==64
            assert row['weights_by_player']==[list(range(1,65))]*2
            assert sum(row['weights_by_player'][0])==2080
        def rejected(label,fn):
            try:fn()
            except ValueError:negative.append(label)
            else:raise AssertionError('Accepted '+label)
        def check(result=result,checkpoints=checkpoints,spec=spec):
            return selection.select_terminal(result,checkpoints,spec,training_registration_sha256=registration)
        for key,value in (('training_complete',False),('registration_sha256','0'*64),('production_modified',True)):
            rejected(key,lambda key=key,value=value:check(result=dict(result,**{key:value})))
        reduced=copy.deepcopy(result);del reduced['arms']['B-relative']
        rejected('missing replication',lambda:check(result=reduced))
        for name,mutate in (
            ('incomplete arm',lambda p:p.__setitem__('completed_cycles',63)),
            ('missing cycle',lambda p:p['updates'].pop(7)),
            ('changed streams',lambda p:p['updates'][4]['paired_sources'].__setitem__('sentinel-source','0'*64)),
            ('changed final ref',lambda p:p.__setitem__('checkpoint',p['updates'][0]['checkpoint']))):
            bad=copy.deepcopy(result);mutate(bad['arms']['A-relative'])
            rejected(name,lambda bad=bad:check(result=bad))
        # Rehash each altered synthetic document and its final reference so
        # rejection tests the actual semantic boundary, not only its digest.
        for name,mutate in (
            ('final unplayed substituted',lambda cp:cp['played_bank'].__setitem__(63,cp['next_model'])),
            ('missing played model',lambda cp:cp['played_bank'].pop(3)),
            ('swapped generation',lambda cp:cp['played_bank'].reverse()),
            ('wrong excluded generation',lambda cp:cp['next_model'].__setitem__('generation',63)),
            ('wrong model path',lambda cp:cp['played_bank'][2].__setitem__('file','../outside.json')),
            ('missing fitted context',lambda cp:cp['contexts'].pop(next(iter(cp['contexts'])))),
            ('heldout context fitted',lambda cp:cp['contexts'].__setitem__(next(r['context_sha256'] for r in cp['registry']['contexts'] if r['split']=='heldout'),{}))):
            cp=copy.deepcopy(checkpoints);res=copy.deepcopy(result);mutate(cp['A-baseline'])
            h=selection.sha_value(cp['A-baseline']);r=dict(file='jointcontextcheckpoint-'+h+'.json',sha256=h)
            res['arms']['A-baseline']['checkpoint']=r;res['arms']['A-baseline']['updates'][-1]['checkpoint']=r
            rejected(name,lambda res=res,cp=cp:check(result=res,checkpoints=cp))
        changed=copy.deepcopy(spec);changed['cycles']=63
        rejected('changed fixed training budget',lambda:check(spec=changed))
        changed=copy.deepcopy(spec);changed['arms']['B-relative']['replication']=0
        rejected('swapped replication identity',lambda:check(spec=changed))
        changed=copy.deepcopy(spec);changed['arms']['B-relative']['representation']=362
        rejected('swapped representation',lambda:check(spec=changed))
        cp=copy.deepcopy(checkpoints);cp['A-baseline']['boundary']='changed bytes'
        rejected('changed checkpoint bytes',lambda:check(checkpoints=cp))

        # Read only the live progress counter: an actually unfinished arm must
        # be refused before trying to treat any model as final.
        live=json.loads((TRAIN/'A-baseline/progress.json').read_bytes())
        assert live['completed_cycles']<64
        rejected('actual still-training arm',lambda:selection.select('A-baseline',live,{},spec,
                                             training_registration_sha256=registration))

        # Validate loader routing separately with an explicitly synthetic reader.
        # This records which immutable references would be read, not model math.
        original=selection.read_model;reads=[]
        def mock_reader(directory,item,registry,resources):
            reads.append(copy.deepcopy(item));return dict(generation=item['generation'],synthetic=True)
        selection.read_model=mock_reader
        try:
            registry=Registry(entries)
            documents=selection.load_documents(Path('unused-synthetic-read-root'),chosen['arms']['A-baseline'],registry,{},guard=lambda:None)
        finally:
            selection.read_model=original
        assert len(documents)==64 and [d['generation'] for d in documents]==list(range(64))
        assert [r['generation'] for r in reads]==list(range(65))
        assert all(digest(Path(p).read_bytes())==h for p,h in inputs.items())
        value=dict(complete=True,passed=True,seconds=time.monotonic()-began,negative_cases=negative,
            arms=4,selected_generations=list(range(64)),excluded_generation=64,actor_weight_sum=2080,
            loader_route_model_count=64,loader_authenticated_reference_count=65,
            actual_unfinished_arm_refused_at_cycles=live['completed_cycles'],synthetic_metadata_only=True,
            actual_model_values=False,new_scientific_deals=False,new_labels=False,fits=False,gpu=False,inputs=inputs)
        durable(output,encoded(value))
        print(json.dumps(dict(passed=True,seconds=value['seconds'],negative_cases=len(negative),actual_cycle=live['completed_cycles'])))
    except Exception:
        durable(failure,encoded(dict(passed=False,seconds=time.monotonic()-began,traceback=traceback.format_exc())))
        raise


if __name__=='__main__':main()
