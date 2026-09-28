"""Factorized, visible-only inputs for independent river decision training.

Factors are NOT complete observations. No own histories are invented and no
inference bank is called. Assemble cards with a checked native public state.
"""
from itertools import combinations,permutations
import hashlib
import json
import numpy as np
from sampled_visible_poker_features_v1 import visible_summaries
from sampled_public_economics_features_v1 import encode_document
from stack_price_reference_v1 import board_group,price

def card_factors(board):
    board_group(board)
    hands=np.asarray(list(combinations([c for c in range(52) if c not in board],2)),dtype=np.int64)
    original=np.column_stack((hands,np.tile(board,(1081,1))))
    minimum=np.full(1081,np.iinfo(np.int64).max(),dtype=np.int64);canonical=np.zeros_like(original)
    for permutation in permutations(range(4)):
        c=original//4*4+np.asarray(permutation)[original%4]
        c[:,:2]=np.sort(c[:,:2],axis=1);c[:,2:5]=np.sort(c[:,2:5],axis=1)
        packed=(c*(1<<np.arange(0,42,6,dtype=np.int64))[None,:]).sum(1)
        better=packed<minimum;minimum[better]=packed[better];canonical[better]=c[better]
    x=np.zeros((1081,362),dtype=np.float32)
    for slot in range(7):
        x[np.arange(1081),19*slot+canonical[:,slot]//4]=1
        x[np.arange(1081),19*slot+14+canonical[:,slot]%4]=1
    for i,c in enumerate(canonical.tolist()):x[i,269:302]=visible_summaries(c[:2],c[2:])
    assert not np.any(x[:,133:269]) and not np.any(x[:,302:])
    return dict(hands=hands,canonical_cards=canonical,lo_actor_zero=minimum,features=x,
                strength_category=np.argmax(x[:,269:278],axis=1))

def public_factors(document):
    source=document['context_source'];key=hashlib.sha256(source.encode()).hexdigest()
    prices=encode_document(document,expected_context_sha256=key)
    stack=json.loads(source)['config']['stack'];rows=[];vectors=[];economics=[]
    for row,public in zip(document['public_states'],prices):
        if row['phase']!=3 or [a['kind'] for a in row['actions']]!=['fold','call']:continue
        hi=int(row['hi']);history=[];encoded=(hi&((1<<63)-1))>>4
        if not hi&(1<<63):raise ValueError('River public identity required')
        while encoded>1:history.append(encoded&7);encoded>>=3
        history.reverse()
        if encoded!=1 or len(history)>19 or history.count(5)!=2 or any(not 1<=a<=5 for a in history):
            raise ValueError('Invalid public history')
        x=np.zeros(362,dtype=np.float32)
        x[133+row['actor']]=1;x[138]=1;x[139+(hi&15)]=1
        for j in range(19):x[155+j*6+(history[j] if j<len(history) else 0)]=1
        x[302:]=public
        g=price(row);economics.append([stack,g['net_pot'],g['call_cost'],row['actor'],g['equity_threshold']])
        rows.append(row);vectors.append(x)
    if not rows:raise ValueError('Native two-action river states required')
    return dict(context_sha256=key,rows=rows,features=np.asarray(vectors),economics=np.asarray(economics),stack=stack)

def qualify_native_inputs(store,geometry):
    from sampled_visible_features_bulk_v1 import features
    raw=json.loads((store/'retained-deals.json').read_bytes())['deals']
    cards=[card_factors(d[4:]) for d in raw]
    checks=0;maximum=0.;contexts=[]
    for depth in (20,40,100,200,400):
        document=json.loads((geometry/f'stack-{depth}-public.json').read_bytes());public=public_factors(document)
        q=json.loads((store/f'stack-{depth}-queries.json').read_bytes())
        assert q['context_source']==document['context_source']
        admitted={r['hi'] for r in public['rows']}
        selected=[o for o in q['observations'] if o['hi'] in admitted]
        original=features(selected);lookup={(o['hi'],o['lo']):(i,o) for i,o in enumerate(selected)}
        expected_count=0
        for state,vector in zip(public['rows'],public['features']):
            actor=state['actor']
            for deal,card in zip(raw,cards):
                hand=sorted(deal[actor*2:actor*2+2]);index=next(i for i,h in enumerate(card['hands'].tolist()) if h==hand)
                lo=str(int(card['lo_actor_zero'][index])|(actor<<42));i,o=lookup[(state['hi'],lo)]
                x=card['features'][index]+vector
                assert o['actor']==actor and o['phase']==3 and o['n']==2
                maximum=max(maximum,float(np.max(abs(x[:302]-original[i]))))
                assert np.array_equal(x[302:],vector[302:])
                assert np.array_equal(np.flatnonzero(x[:269]),o['active_features'])
                checks+=1;expected_count+=1
        assert expected_count==len(selected)
        contexts.append(dict(stack=depth,observations=expected_count))
    if maximum!=0:raise ValueError('Native feature mismatch')
    return dict(passed=True,contexts=contexts,native_observations_checked=checks,
                maximum_visible_feature_error=maximum,no_fabricated_own_histories=True,
                scope='Feature-only conditional-decision adapter, not policy-bank inference')
