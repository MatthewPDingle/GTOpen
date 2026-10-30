"""Exact finite opponent posterior for one fixed visible river history."""
import numpy as np
from storage_strategic_common_prior_20260920 import PAIRS
from sampled_physical_bank_v1 import histories

PAIR_ID={tuple(map(int,p)):i for i,p in enumerate(PAIRS)}


def posterior(document,probabilities,entry_weights):
    obs=document['queries']['observations'];histories(obs)
    p=np.asarray(probabilities,dtype=np.float64);w=np.asarray(entry_weights,dtype=np.float64)
    n=np.array([o['n'] for o in obs]);actor=np.array([o['actor'] for o in obs])
    legal=np.arange(4)[None,:]<n[:,None]
    if (p.shape!=(len(obs),4) or not np.isfinite(p).all() or np.any(p<0)
            or np.any(p[~legal]!=0) or np.max(abs(p.sum(1)-1))>1e-10):raise ValueError('Invalid legal policy')
    if w.shape!=(2,1326) or not np.isfinite(w).all() or np.any(w<0):raise ValueError('Invalid entry weights')
    hero=document['target']['actor'];target=document['target']['query_index'];assert actor[target]==hero
    pairs=np.array([x['cards'] for x in document['pairs']],dtype=int)
    assert pairs.shape==(990,2) and np.all(pairs[:,0]<pairs[:,1])
    assert len({tuple(x) for x in pairs})==990
    visible=set(document['target']['cards']);assert len(visible)==7
    assert all(not visible.intersection(map(int,row)) for row in pairs)
    ids=np.array([PAIR_ID[tuple(map(int,row))] for row in pairs])
    path=np.array([x['path'] for x in document['pairs']],dtype=int)
    assert path.ndim==3 and path.shape[0]==990 and path.shape[2]==3 and path.shape[1]>0
    row,action,arity=path[:,:,0],path[:,:,1],path[:,:,2]
    assert np.all((row>=0)&(row<len(obs))) and np.array_equal(n[row],arity)
    assert np.all((action>=0)&(action<arity)) and np.all(actor[row]==actor[row[0]])
    mine=actor[row[0]]==hero;theirs=~mine
    assert theirs.any() and np.all(row[:,mine]==row[0,mine]) and np.all(action==action[0])
    own_likelihood=np.prod(p[row[:,mine],action[:,mine]],axis=1)
    assert np.all(own_likelihood==own_likelihood[0]);own_likelihood=float(own_likelihood[0])
    opponent_likelihood=np.prod(p[row[:,theirs],action[:,theirs]],axis=1)
    prior=w[1-hero,ids];mass=prior*opponent_likelihood;total=float(mass.sum());base=float(prior.sum())
    g=document['geometry'];outcomes=np.array([x['outcome_loss_tie_win'] for x in document['pairs']],dtype=int)
    assert np.all((0<=outcomes)&(outcomes<=2)) and np.all(np.bincount(outcomes,minlength=3)==document['counts_loss_tie_win'])
    endpoints=np.array(g['endpoints_loss_tie_win']);pot,cost,rake=g['pot'],g['amount_to_call'],g['rake']
    assert np.max(abs(endpoints-np.array([-cost,(pot+cost-rake)/2-cost,pot-rake])))<1e-9
    hero_prior=float(w[hero,PAIR_ID[tuple(sorted(document['target']['cards'][:2]))]])
    supported=total>0
    summary=dict(supported=supported,hero_own_likelihood=own_likelihood,hero_entry_weight=hero_prior,
        hero_on_path=own_likelihood>0 and hero_prior>0,opponent_prior_mass=base,opponent_posterior_mass=total,
        opponent_history_probability=None if base==0 else total/base,
        supported_opponent_combos=int(np.count_nonzero(mass)))
    posterior_weights=np.zeros(990)
    if supported:
        posterior_weights=mass/total;assert abs(posterior_weights.sum()-1)<1e-12
        equity=float(posterior_weights@(outcomes*.5));delta=float(posterior_weights@endpoints[outcomes])
        assert abs(delta-(equity*(pot+cost-rake)-cost))<1e-9
        summary.update(equity=equity,call_minus_fold_bb=delta,effective_opponent_combos=float(1/(posterior_weights@posterior_weights)))
    else:summary.update(equity=None,call_minus_fold_bb=None,effective_opponent_combos=None)
    return summary,dict(pair_ids=ids,opponent_likelihood=opponent_likelihood,posterior=posterior_weights,
        outcomes=outcomes,hero_likelihood=own_likelihood)


def fold_call_readout(probabilities,delta):
    p=np.asarray(probabilities,dtype=float);assert p.shape==(4,) and np.isfinite(p).all() and np.all(p>=0)
    mass=float(p[0]+p[1]);share=None if mass==0 else float(p[1]/mass)
    gain=None if delta is None else float(mass*max(delta,0)-p[1]*delta)
    assert gain is None or gain>=-1e-10
    return dict(fold_probability=float(p[0]),call_probability=float(p[1]),other_action_probability=float(p[2:].sum()),
        fold_call_mass=mass,call_share_within_fold_call=share,restricted_switch_gain_bb=gain,
        scope='Best reallocation of this policy\'s Fold/Call mass, keeping other action probabilities unchanged; not a full best response.')
