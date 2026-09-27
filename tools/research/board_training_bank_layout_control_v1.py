"""CPU-only layout/reference checks on native queries and synthetic saved models."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
from board_training_bank_layout_v1 import prepare_layout,validate_queries,SHAPES
from board_training_policy_v1 import probabilities,average
import board_training_checkpoint_v1 as checkpoint
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_visible_hybrid_gpu_bank_bulk_v1 import prepare_tables
from sampled_visible_features_bulk_v1 import features
from sampled_physical_bank_v1 import histories
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from preflop_allin_matrix_v1 import AllinMatrix
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-training-bank-layout-control-v1'


def packed_cpu(query,layout):
    validate_queries(layout,query);obs=query['observations'];x=features(obs).astype(np.float64)
    actors=np.array([o['actor'] for o in obs]);arity=np.array([o['n'] for o in obs])
    legal=np.arange(4)[None,:]<arity[:,None]
    ids,values,mask=prepare_tables(query,layout['tables'],layout['context_source'])
    history=histories(obs);numerator=np.zeros((len(obs),4));denominator=np.zeros(len(obs));policies=[]
    for generation in range(layout['count']):
        scores=np.zeros((len(obs),4))
        for actor in (0,1):
            index=np.flatnonzero(actors==actor);y=x[index]
            for layer in range(3):
                w=layout['parameters'][f'w{layer}'][generation,actor]
                b=layout['parameters'][f'b{layer}'][generation,actor]
                y=y@w.T+b
                if layer!=2:y=np.maximum(y,0.)
            scores[index]=y
        p=np.maximum(scores,0.)*legal;total=p.sum(1);positive=total>0
        p[positive]/=total[positive,None]
        unsupported=np.flatnonzero(~positive)
        p[unsupported,np.argmax(np.where(legal,scores,-np.inf),axis=1)[unsupported]]=1.
        p[ids]=np.where(mask[generation,:,None],values[generation],p[ids])
        policies.append(p)
        for i,o in enumerate(obs):
            weight=float(layout['weights'][o['actor'],generation])
            for ancestor,action in history[i]:weight*=p[ancestor,action]
            numerator[i]+=weight*p[i];denominator[i]+=weight
    support=denominator>0;result=np.zeros_like(numerator)
    result[support]=numerator[support]/denominator[support,None]
    for i in np.flatnonzero(~support):result[i,:arity[i]]=1./arity[i]
    assert np.isfinite(result).all() and np.max(abs(result.sum(1)-1))<1e-12
    return result,denominator,policies,int(np.count_nonzero(mask))


def main():
    began=time.monotonic();assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>20_000_000_000
    cp=OUT/'bb-context-candidate.json';mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    upstream=OUT/'board-training-checkpoint-control-v2-result.json'
    upstream_reg=upstream.with_name('board-training-checkpoint-control-v2-registration.json')
    result=read(upstream);reg=read(upstream_reg)
    assert result['passed'] and result['synthetic_targets'] and result['synthetic_networks']
    assert result['registration_sha256']==sha(upstream_reg)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    source=cp.read_text();matrix=AllinMatrix(read(mp),source)
    args=dict(context_source=source,catalog_source=cat.read_text(),matrix_sha256=sha(mp),entry_mass=matrix.btn_mass,
        root_config=reg['config']['board_root'])
    objects=Path(reg['store']);saved=json.loads(read_object(objects,result['checkpoints'][-1]))
    assert saved['completed_iterations']==2 and len(saved['played_bank'])==2
    documents=[checkpoint.model_document(objects,r,**args) for r in saved['played_bank']]
    qp=Path('S:/GTOpen-research/board-precision-repeat-v1/private-000/queries.json')
    original=read(qp);query=dict(context_source=source,observations=original['observations'])
    assert original['context_source']==source
    paths=[Path(__file__).resolve(),cp,mp,cat,upstream,upstream_reg,qp,
        *[ROOT/'tools/research'/name for name in ('board_training_bank_layout_v1.py','board_training_gpu_bank_v1.py',
            'board_completed_bank_v1.py','board_training_policy_v1.py','sampled_physical_hybrid_gpu_bank_v2.py')]]
    inputs={str(p):sha(p) for p in paths}
    for r in saved['played_bank']:inputs[str(objects/r['file'])]=r['sha256']
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    save(rp,dict(inputs=inputs,source_checkpoint=result['checkpoints'][-1],maximum_seconds=180,
        scope='CPU composition and own-reach averaging on synthetic model parameters. Not CUDA equivalence or trained playing strength.',
        production_modified=False))
    weights=np.array([[1.,2.],[4.,9.]])
    varied=copy.deepcopy(documents);rng=np.random.default_rng(9281901)
    for model in varied:
        for net in model['networks']:
            for name,shape in SHAPES.items():net[name]=rng.normal(0,.05,int(np.prod(shape))).astype(np.float32).tolist()
    folded=copy.deepcopy(documents)
    for model in folded:
        for net in model['networks']:
            for name,shape in SHAPES.items():net[name]=np.zeros(int(np.prod(shape)),dtype=np.float32).tolist()
            net['b2']=[1.,-1.,-2.,-3.]
    kw={k:v for k,v in args.items() if k!='context_source'};cases=[]
    def guard():
        assert time.monotonic()-began<180 and psutil.virtual_memory().available>20_000_000_000
    for name,models in [('saved-synthetic',documents),('varied-f32-networks',varied),('zero-reach',folded)]:
        layout=prepare_layout(models,weights,completed_iterations=2,guard=guard,**args)
        actual,reach,pp,overrides=packed_cpu(query,layout)
        expected,reference_reach=average(query,models,completed_iterations=2,weights_by_player=weights,
            guard=guard,device='cpu',**kw)
        policy_error=float(np.max(abs(actual-expected)));reach_error=float(np.max(abs(reach-reference_reach)))
        per_model_error=0.
        for model,p in zip(models,pp):
            reference,_=probabilities(query,model,device='cpu',**kw)
            per_model_error=max(per_model_error,float(np.max(abs(p-reference))))
        assert max(policy_error,reach_error,per_model_error)<1e-12 and overrides>0
        zero=int(np.count_nonzero(reach==0))
        if name=='zero-reach':assert zero>0
        cases.append(dict(case=name,observations=len(pp[0]),maximum_policy_error=policy_error,
            maximum_reach_error=reach_error,maximum_per_model_error=per_model_error,zero_reach_rows=zero,table_overrides=overrides))
    rejected=[]
    def reject(name,call):
        try:call()
        except (ValueError,TypeError,KeyError):rejected.append(name)
        else:raise AssertionError('Accepted '+name)
    def pack(models=documents,w=weights,**overrides):
        return prepare_layout(models,w,completed_iterations=2,guard=guard,**dict(args,**overrides))
    reject('reordered models',lambda:pack(models=list(reversed(documents))))
    reject('incomplete bank',lambda:pack(models=documents[:1]))
    reject('unplayed model included',lambda:pack(models=[documents[0],checkpoint.model_document(objects,saved['next_model'],**args)]))
    reject('nonpositive weights',lambda:pack(w=np.zeros((2,2))))
    wrong=copy.deepcopy(args['root_config']);wrong['board_seed']+=1
    reject('changed board seed',lambda:pack(root_config=wrong))
    layout=pack();bad=copy.deepcopy(query)
    root_index=next(i for i,o in enumerate(bad['observations']) if int(o['hi'])==1)
    bad['observations'][root_index]['own_history']=[[root_index,0,4]]
    reject('root ancestor',lambda:validate_queries(layout,bad))
    reject('different game',lambda:validate_queries(layout,dict(query,context_source=source+' ')))
    for p,h in inputs.items():guard();assert sha(p)==h,p
    assert production_available()
    result=dict(passed=True,registration_sha256=sha(rp),cases=cases,negative_checks=rejected,
        seconds=time.monotonic()-began,gpu_used=False,synthetic_models=True,cuda_qualification_pending=True,
        complete_bank_loader_qualification_pending=True,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
