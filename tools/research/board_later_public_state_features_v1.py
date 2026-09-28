"""Twelve redundant public betting inputs; original visible features stay intact."""
import numpy as np
from sampled_visible_initialization_v1 import fresh_visible_network

NAMES=('pot_fraction','remaining_actor_fraction','remaining_opponent_fraction','call_fraction',
    'call_price','bounded_effective_spr','starting_pot_fraction','initial_effective_stack_fraction',
    'action_0_cost_fraction','action_1_cost_fraction','action_2_cost_fraction','action_3_cost_fraction')
WIDTH=len(NAMES)


def lookup(catalog):
    assert catalog['passed'] and catalog['format']==1 and catalog['public_lookup_matches_native_observation']
    result={}
    for row in catalog['rows']:
        key=(row['public_id'],row['actor'],row['phase'],tuple(row['history']))
        assert key not in result
        total=row['starting_pot']+2*row['initial_effective_stack']
        assert total>0 and row['pot']>0
        remaining=row['remaining_actor'];opponent=row['remaining_opponent'];call=row['amount_to_call']
        assert abs(row['pot']+remaining+opponent-total)<1e-7
        assert abs(call-max(0,remaining-opponent))<1e-7
        assert abs(row['call_price']-call/(row['pot']+call))<1e-12
        assert row['effective_remaining']==min(remaining,opponent)
        assert len(row['action_costs'])==4 and 2<=row['legal_actions']<=4
        assert all(x==0 for x in row['action_costs'][row['legal_actions']:])
        values=[row['pot']/total,remaining/total,opponent/total,call/total,row['call_price'],
            min(remaining,opponent)/(row['pot']+min(remaining,opponent)),row['starting_pot']/total,
            row['initial_effective_stack']/total,*[x/total for x in row['action_costs']]]
        values=np.asarray(values,dtype=np.float32)
        assert values.shape==(WIDTH,) and np.isfinite(values).all() and np.all((values>=0)&(values<=1))
        result[key]=(row['legal_actions'],values)
    assert len(result)==catalog['decision_templates']
    return result


def features(active,arity,table):
    active=np.asarray(active);arity=np.asarray(arity)
    assert active.ndim==2 and active.shape[1]==36 and active.dtype.kind in 'iu'
    assert arity.shape==(len(active),) and arity.dtype.kind in 'iu' and np.all((arity>=2)&(arity<=4))
    assert np.all((active>=0)&(active<269)) and np.all(np.diff(active.astype(int),axis=1)>0)
    unique,inverse=np.unique(np.column_stack((active[:,14:],arity)),axis=0,return_inverse=True)
    result=np.zeros((len(unique),WIDTH),dtype=np.float32)
    for i,row in enumerate(unique):
        actor=int(row[0])-133;phase=int(row[1])-135;public=int(row[2])-139
        assert actor in (0,1) and phase in range(4) and public in range(16)
        history=[int(x)-(155+6*j) for j,x in enumerate(row[3:22])]
        assert all(0<=x<=5 for x in history)
        end=next((j for j,x in enumerate(history) if x==0),len(history))
        assert not any(history[end:])
        if phase==0:
            assert end==0
        else:
            expected,values=table[(public,actor,phase,tuple(history[:end]))]
            assert int(row[-1])==expected,'Wrong legal menu for public state'
            result[i]=values
    return result[inverse]


def fresh_public_network(seed):
    import torch
    original=fresh_visible_network(seed)
    with torch.random.fork_rng(devices=[]):
        model=torch.nn.Sequential(torch.nn.Linear(302+WIDTH,64),torch.nn.ReLU(),
            torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
        with torch.no_grad():
            model[0].weight.zero_();model[0].weight[:,:302].copy_(original[0].weight)
            model[0].bias.copy_(original[0].bias)
            for layer in (2,4):model[layer].load_state_dict(original[layer].state_dict())
    return model
