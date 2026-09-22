"""CPU reference checks on old observations and synthetic feature-aware banks.

No CUDA work, new deals, outcome labels, or poker-strength claim.
"""
import copy
import json
from pathlib import Path
import time
import numpy as np
from threadpoolctl import threadpool_limits
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_visible_hybrid_checkpoint_v1 import validate_model
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_visible_initialization_v1 import features
from sampled_physical_preflop_table_v1 import Table

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-visible-hybrid-bank-control-v1'


def reference(queries, documents, weights, *, summaries=True):
    """Independent Torch double forward and scalar own-history accumulation."""
    import torch
    obs = queries['observations']; x = features(obs).astype(np.float64)
    if not summaries: x[:,269:] = 0
    policies = []; coverage = 0
    for doc in documents:
        scores = np.zeros((len(obs),4))
        for player, net in enumerate(doc['networks']):
            ids = [i for i,o in enumerate(obs) if o['actor']==player]
            y = torch.from_numpy(x[ids])
            for layer, shape in enumerate(((64,302),(64,64),(4,64))):
                w = torch.from_numpy(np.asarray(net[f'w{layer}'],np.float32).astype(np.float64).reshape(shape))
                b = torch.from_numpy(np.asarray(net[f'b{layer}'],np.float32).astype(np.float64))
                y = torch.nn.functional.linear(y,w,b)
                if layer<2:y = torch.relu(y)
            scores[ids] = y.numpy()
        policy = np.zeros_like(scores)
        for i,o in enumerate(obs):
            n = o['n']; v = np.maximum(scores[i,:n],0)
            if sum(v)>0:policy[i,:n]=v/sum(v)
            else:policy[i,int(np.argmax(scores[i,:n]))]=1
        for player,document in enumerate(doc['preflop_tables']):
            if document is None:continue
            table = Table(document,queries['context_source'])
            for i,o in enumerate(obs):
                if o['actor']!=player or o['phase']!=0:continue
                key = (int(o['hi']),int(o['lo']))
                if key in table.rows:
                    n,active,prob = table.rows[key]
                    assert n==o['n'] and active==tuple(sorted(o['active_features']))
                    policy[i]=prob;coverage+=1
        policies.append(policy)
    totals=np.zeros((len(obs),4));denominator=np.zeros(len(obs))
    for m,policy in enumerate(policies):
        for i,o in enumerate(obs):
            reach=weights[o['actor'],m]
            for prior,action,n in o['own_history']:reach*=policy[prior,action]
            totals[i]+=reach*policy[i];denominator[i]+=reach
    for i,o in enumerate(obs):
        if denominator[i]>0:totals[i]/=denominator[i]
        else:totals[i,:o['n']]=1/o['n']
    return totals,denominator,coverage,policies


def main():
    started=time.monotonic()
    def guard():
        assert time.monotonic()-started<180 and idle()
        assert psutil.virtual_memory().available>=20_000_000_000
    guard()
    previous=OUT/'sampled-visible-hybrid-checkpoint-control-v1-result.json'
    previous_reg=OUT/'sampled-visible-hybrid-checkpoint-control-v1-registration.json'
    result=json.loads(previous.read_text());assert result['passed']
    assert result['registration_sha256']==sha(previous_reg)
    fixture_reg=OUT/'sampled-physical-preflop-table-control-v1-registration.json'
    fixture=Path(json.loads(fixture_reg.read_text())['fixture'])
    for p,h in json.loads(fixture_reg.read_text())['inputs'].items():assert sha(p)==h
    for p,h in json.loads(previous_reg.read_text())['inputs'].items():assert sha(p)==h
    queries=json.loads(fixture.read_text());context=queries['context_source']
    models=[];model_paths=[]
    for path,h in result['artifacts'].items():
        assert sha(path)==h
        if Path(path).name.startswith('visiblemodel-'):
            doc=json.loads(Path(path).read_text())
            validate_model(doc,context)
            if doc['generation'] in (0,1):models.append(doc);model_paths.append(Path(path))
    models.sort(key=lambda d:d['generation']);assert [d['generation'] for d in models]==[0,1]
    third=copy.deepcopy(models[1]);third['generation']=2;models.append(third)
    # Synthetic nonzero feature weights exercise the new columns; no fitting.
    rng=np.random.Generator(np.random.PCG64(93141))
    for doc in models[1:]:
        for net in doc['networks']:
            w=np.asarray(net['w0'],np.float32).reshape(64,302)
            w[:,269:]=rng.normal(0,.15,(64,33)).astype(np.float32)
            net['w0']=w.ravel().tolist()
        validate_model(doc,context)
    inputs=[previous,previous_reg,fixture_reg,fixture,*model_paths,Path(__file__),
        *[ROOT/'tools/research'/name for name in ('sampled_visible_hybrid_cpu64_v1.py',
          'sampled_visible_hybrid_checkpoint_v1.py','sampled_visible_initialization_v1.py',
          'sampled_visible_poker_features_v1.py','sampled_physical_preflop_table_v1.py',
          'sampled_physical_bank_v1.py')]]
    registration=dict(inputs={str(p):sha(p) for p in inputs},seed=93141,maximum_seconds=180,
        scope='CPU reference, old observations and synthetic nonzero feature weights. No new deals, training or accuracy qualification.',production_modified=False)
    reg_path=OUT/f'{PREFIX}-registration.json';save(reg_path,registration)
    models_path=OUT/f'{PREFIX}-models.json';save(models_path,models)
    import torch
    torch.set_num_threads(2);state=torch.random.get_rng_state().clone()
    metrics=[]
    with threadpool_limits(limits=2):
        for weights in (np.ones((2,3)),np.array([[1.,2.,4.],[5.,3.,1.]])):
            bank=VisibleHybridCpuBank64(models,context_source=context,weights_by_player=weights)
            got,reach=bank.average(queries,guard=guard)
            expected,expected_reach,covered,policies=reference(queries,models,weights)
            error=float(np.max(abs(got-expected)));reach_error=float(np.max(abs(reach-expected_reach)))
            assert error<1e-11 and reach_error<1e-11 and covered>0
            naive=sum(policies)/len(policies)
            naive_difference=float(np.max(abs(got-naive)))
            assert naive_difference>1e-4
            ablated,_,_,_=reference(queries,models,weights,summaries=False)
            feature_effect=float(np.max(abs(got-ablated)));assert feature_effect>1e-4
            changed=copy.deepcopy(queries);changed['batch_source']='hidden-outcome-sentinel'
            hidden,hidden_reach=bank.average(changed,guard=guard)
            assert np.array_equal(got,hidden) and np.array_equal(reach,hidden_reach)
            metrics.append(dict(weights=weights.tolist(),maximum_policy_error=error,maximum_reach_error=reach_error,
                covered_preflop_rows=covered,maximum_difference_from_naive_average=naive_difference,
                maximum_visible_feature_effect=feature_effect,hidden_labels_ignored=True))
        assert torch.equal(state,torch.random.get_rng_state())
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,TypeError):rejected.append(label);return
            raise AssertionError('accepted '+label)
        reject('empty-bank',lambda:VisibleHybridCpuBank64([],context_source=context))
        reject('wrong-generation-order',lambda:VisibleHybridCpuBank64(models[::-1],context_source=context))
        for label,w in [('incomplete-weights',[[1],[1]]),('negative-weight',[[1,2,-1],[1,1,1]]),('nonfinite-weight',[[1,2,float('nan')],[1,1,1]])]:
            reject(label,lambda w=w:VisibleHybridCpuBank64(models,context_source=context,weights_by_player=w))
        changed=copy.deepcopy(queries);changed['context_source']='wrong'
        reject('wrong-context',lambda:bank.average(changed,guard=guard))
        changed=copy.deepcopy(queries);changed['observations']=[]
        reject('empty-observations',lambda:bank.average(changed,guard=guard))
        changed=copy.deepcopy(queries);changed['observations'][0]['actor']=True
        reject('noninteger-actor',lambda:bank.average(changed,guard=guard))
        changed=copy.deepcopy(queries);changed['observations'][0]['own_history']=[[0,0,2]]
        reject('cyclic-history',lambda:bank.average(changed,guard=guard))
    for p,h in registration['inputs'].items():assert sha(p)==h
    output=dict(passed=True,registration_sha256=sha(reg_path),observations=len(queries['observations']),
        checks=metrics,rejections=rejected,torch_global_rng_unchanged=True,
        artifacts={str(models_path):sha(models_path)},seconds=time.monotonic()-started,
        cuda_tested=False,accuracy_qualified=False,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',output);print(json.dumps(output),flush=True)


if __name__=='__main__':main()
