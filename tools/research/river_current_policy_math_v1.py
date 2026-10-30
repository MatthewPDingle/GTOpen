"""Full-vector external-sampling moments and prepared single-policy inference."""
import itertools
import math
import numpy as np
from board_training_checkpoint_v1 import validate_model
from board_training_policy_v1 import RootTable
from weighted_preflop_table_v1 import Table
from shared_visible_query_arrays_v1 import prepare
from board_river_bounds_math_v1 import policy


class CurrentPolicy:
    """One current model pair, no average, smoothing or action projection."""
    def __init__(self,model,context_source,*,guard,**args):
        import torch
        root,_,exact=validate_model(model,context_source=context_source,**args)
        self.context_source=context_source
        self.tables=[Table(t,context_source) for t in model['preflop_tables'] if t is not None]
        self.tables.extend([exact,RootTable(root,context_source,args['catalog_source'])])
        self.weights=[]
        for net in model['networks']:
            layers=[]
            for layer,shape in enumerate(((64,302),(64,64),(4,64))):
                w=np.asarray(net[f'w{layer}'],dtype=np.float32).astype(np.float64).reshape(shape)
                b=np.asarray(net[f'b{layer}'],dtype=np.float32).astype(np.float64)
                guard();layers.append((torch.tensor(w,device='cuda'),torch.tensor(b,device='cuda')))
            self.weights.append(layers)

    def prepare(self,queries):
        if queries['context_source']!=self.context_source:raise ValueError('Current policy context mismatch')
        arrays=prepare(queries);obs=queries['observations']
        table=arrays.legal.astype(np.float64);table/=table.sum(1,keepdims=True)
        mask=np.zeros(len(obs),dtype=bool)
        # Each table preserves previous overrides on unmatched rows. A legal
        # uniform placeholder satisfies its contract; only matched rows apply.
        for t in self.tables:
            table,ids=t.apply(obs,table);mask[np.asarray(ids,dtype=int)]=True
        return dict(queries=queries,arrays=arrays,table=table,mask=mask,
                    arity=np.asarray([o['n'] for o in obs],dtype=int))

    def infer(self,prepared,*,guard):
        import torch
        guard();a=prepared['arrays'];scores=np.zeros((len(a.actors),4))
        with torch.no_grad():
            for actor in (0,1):
                ids=np.flatnonzero(a.actors==actor)
                if not len(ids):continue
                y=torch.tensor(a.features[ids],device='cuda')
                for layer,(w,b) in enumerate(self.weights[actor]):
                    y=y@w.T+b
                    if layer<2:y=torch.relu(y)
                scores[ids]=y.cpu().numpy()
        p=policy(scores,prepared['arity']);mask=prepared['mask'];p[mask]=prepared['table'][mask]
        assert np.isfinite(p).all() and np.all(p>=0) and np.max(abs(p.sum(1)-1))<1e-12
        assert not np.any(p[~a.legal]);return p


def moments(doc,p,posterior):
    """Conditional on this visible target; updater expands, opponent samples.

    Opponent private hand is shared by the entire sampled subtree. Independent
    action draws in distinct branches match the ideal external-sampling law.
    No source-deal proposal weights or earlier visit probabilities are inferred
    here: those belong to the later native integration experiment.
    """
    p=np.asarray(p,dtype=np.float64);weights=np.asarray(posterior,dtype=np.float64)
    assert weights.shape==(990,) and np.all(weights>=0) and abs(weights.sum()-1)<1e-12
    hero=doc['target']['actor'];nodes=doc['nodes'];n=doc['target']['n']
    mu=np.zeros(len(nodes));variance=np.zeros(len(nodes));visits=np.zeros(len(nodes));terms=np.zeros(len(nodes))
    for i,node in enumerate(nodes):
        if node['kind']!='decision':mu[i]=node['payoff'];terms[i]=1.;continue
        c=np.asarray(node['children']);sigma=p[node['query_index'],:len(c)];assert np.all(c<i)
        mu[i]=sigma@mu[c]
        if node['actor']==hero:
            variance[i]=(sigma*sigma)@variance[c];visits[i]=1+visits[c].sum();terms[i]=terms[c].sum()
        else:
            variance[i]=sigma@(variance[c]+(mu[c]-mu[i])**2)
            visits[i]=1+sigma@visits[c];terms[i]=sigma@terms[c]
    q=np.asarray([[mu[c] for c in nodes[pair['root']]['children']] for pair in doc['pairs']])
    within=np.asarray([[variance[c] for c in nodes[pair['root']]['children']] for pair in doc['pairs']])
    mean=weights@q;centered=q-mean
    hand_cov=(centered*weights[:,None]).T@centered
    action_cov=np.diag(weights@within);total=hand_cov+action_cov
    sigma=p[doc['target']['query_index'],:n];transform=np.eye(n)-np.ones((n,1))*sigma[None,:]
    regret_cov=transform@total@transform.T
    hand_regret=transform@hand_cov@transform.T
    action_regret=transform@action_cov@transform.T
    for a in (hand_cov,action_cov,total,regret_cov):
        assert np.max(abs(a-a.T))<1e-8 and np.linalg.eigvalsh(a).min()>-1e-8
    trace=float(np.trace(regret_cov));hand=float(np.trace(hand_regret));action=float(np.trace(action_regret))
    assert abs(trace-hand-action)<1e-8
    return dict(action_means=mean.tolist(),sampled_action_covariance=total.tolist(),
        private_hand_action_covariance=hand_cov.tolist(),continuation_action_covariance=action_cov.tolist(),
        sampled_regret_covariance=regret_cov.tolist(),sampled_regret_variance_sum=trace,
        private_hand_regret_variance_sum=hand,continuation_regret_variance_sum=action,
        private_hand_variance_fraction=None if trace<=1e-12 else hand/trace,
        sampled_return_variance=float(sigma@total@sigma),
        sixteen_independent_samples_regret_variance_sum=trace/16,
        exact_full_conditional_regret_variance_sum=0.,
        expected_decision_visits=float(weights@visits[[pair['root'] for pair in doc['pairs']]]),
        expected_terminal_visits=float(weights@terms[[pair['root'] for pair in doc['pairs']]]))


def distribution_control(doc,p,pair_index):
    """Independent exact enumeration of sampled root-action value vectors."""
    hero=doc['target']['actor'];nodes=doc['nodes'];root=nodes[doc['pairs'][pair_index]['root']]
    def dist(i):
        node=nodes[i]
        if node['kind']!='decision':return [(1.,float(node['payoff']))]
        sigma=p[node['query_index'],:len(node['children'])];children=[dist(c) for c in node['children']]
        if node['actor']!=hero:
            return [(float(sigma[a])*w,v) for a,child in enumerate(children) for w,v in child if sigma[a]*w>0]
        result=[]
        for combo in itertools.product(*children):
            w=math.prod(x[0] for x in combo)
            if w>0:result.append((w,math.fsum(float(s)*x[1] for s,x in zip(sigma,combo))))
        assert len(result)<=4096;return result
    child=[dist(c) for c in root['children']];rows=[]
    for combo in itertools.product(*child):
        w=math.prod(x[0] for x in combo)
        if w>0:rows.append((w,[x[1] for x in combo]))
    assert len(rows)<=4096 and abs(math.fsum(w for w,_ in rows)-1)<1e-12
    weights=np.asarray([w for w,_ in rows]);values=np.asarray([v for _,v in rows]);mean=weights@values
    diff=values-mean;cov=(diff*weights[:,None]).T@diff
    fixed=np.zeros(990);fixed[pair_index]=1.;reference=moments(doc,p,fixed)
    mean_error=float(np.max(abs(mean-reference['action_means'])))
    covariance_error=float(np.max(abs(cov-reference['sampled_action_covariance'])))
    assert mean_error<1e-9 and covariance_error<1e-8
    return dict(pair_index=pair_index,enumerated_outcomes=len(rows),mean_error=mean_error,covariance_error=covariance_error)


def cached_sample(doc,p,pair_index,rng):
    """Timing only: complete cached table is already available; excludes inference."""
    hero=doc['target']['actor'];nodes=doc['nodes'];calls=[0,0]
    def walk(i):
        node=nodes[i]
        if node['kind']!='decision':calls[1]+=1;return node['payoff']
        calls[0]+=1;sigma=p[node['query_index'],:len(node['children'])]
        if node['actor']==hero:
            return math.fsum(float(sigma[a])*walk(c) for a,c in enumerate(node['children']))
        u=rng.random();acc=0.;selected=len(sigma)-1
        for a,v in enumerate(sigma):
            acc+=float(v)
            if u<acc:selected=a;break
        return walk(node['children'][selected])
    root=nodes[doc['pairs'][pair_index]['root']];values=np.asarray([walk(c) for c in root['children']])
    sigma=p[root['query_index'],:len(values)];regrets=values-float(sigma@values)
    return regrets,calls
