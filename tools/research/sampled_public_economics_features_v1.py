"""Public stack/price descriptors for future multi-context research.

Not integrated into any trained model. A context hash is mandatory; public-node
IDs alone are not cross-context identities. Equal-stack HU contexts only.
"""
import hashlib
import json
import math
import numpy as np

KINDS=('fold','check','call','bet','raise')
BASE=('own_start','opponent_start','own_remaining','opponent_remaining',
      'own_invested','opponent_invested','pot','call_cost','dead_money',
      'effective_start','effective_remaining','spr','spr_after_call',
      'call_price_fraction','rake_fraction','rake_cap')
ACTION=('legal',*KINDS,'all_in','increment','pot_fraction','remaining_fraction')
NAMES=(*('phase_'+str(i) for i in range(4)),*BASE,
       *(f'action_{a}_{name}' for a in range(4) for name in ACTION))
SPEC=dict(id='public-economics-v1',width=len(NAMES),names=list(NAMES),
          units='bb, money/SPR log1p divided by log1p(1000); fractions unchanged',
          scope='Public numeric descriptors only. Equal-stack HU. Not a trained model.')


def nonnegative(x):
    if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or x<0:
        raise ValueError('Finite nonnegative number required')
    return float(x)


def encode_document(document,*,expected_context_sha256):
    if document.get('format')!=1:raise ValueError('Public ledger format required')
    source=document['context_source'];digest=hashlib.sha256(source.encode()).hexdigest()
    if digest!=expected_context_sha256:raise ValueError('Mismatched game context')
    context=json.loads(source);stack=nonnegative(context['config']['stack'])
    if not stack:raise ValueError('Positive starting stack required')
    result=[];keys=set()
    def same(a,b):
        if not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-8):raise ValueError('Public ledger mismatch')
    log=lambda x:math.log1p(x)/math.log1p(1000.)
    for row in document['public_states']:
        key=(digest,row['hi'])
        if key in keys:raise ValueError('Duplicate public state')
        keys.add(key)
        actor=row['actor'];phase=row['phase']
        if type(actor)is not int or actor not in (0,1) or type(phase)is not int or phase not in range(4):
            raise ValueError('Invalid actor/street')
        vectors=[]
        for name in ('starting_stacks','invested','remaining'):
            values=row[name]
            if len(values)!=2:raise ValueError('Two players required')
            vectors.append([nonnegative(v) for v in values])
        starts,invested,remaining=vectors
        for i in range(2):same(starts[i],stack);same(invested[i]+remaining[i],starts[i])
        pot=nonnegative(row['pot']);dead=nonnegative(row['dead_money']);call=nonnegative(row['call_cost'])
        if not pot:raise ValueError('Positive pot required')
        same(dead,context['dead_money']);same(sum(invested)+dead,pot)
        same(call,max(0.,invested[1-actor]-invested[actor]))
        if call>remaining[actor]+1e-8:raise ValueError('Side pots/unequal effective stacks unsupported')
        rake=nonnegative(row['rake_fraction']);cap=nonnegative(row['rake_cap'])
        same(rake,context['rake_fraction']);same(cap,context['rake_cap'])
        if rake>1:raise ValueError('Invalid rake')
        own,opp=remaining[actor],remaining[1-actor]
        money=[starts[actor],starts[1-actor],own,opp,invested[actor],invested[1-actor],pot,call,dead,
               min(starts),min(remaining),min(remaining)/pot,min(max(0.,own-call),opp)/(pot+call)]
        features=[float(i==phase) for i in range(4)]+[log(x) for x in money]+[call/(pot+call),rake,log(cap)]
        actions=row['actions']
        if not 1<=len(actions)<=4:raise ValueError('Unsupported action menu')
        for a in range(4):
            if a>=len(actions):features.extend([0.]*len(ACTION));continue
            action=actions[a];kind=action['kind'];increment=nonnegative(action['increment'])
            if kind=='jam':kind='raise'
            if kind not in KINDS or type(action['all_in'])is not bool:raise ValueError('Invalid action')
            if increment>own+1e-8:raise ValueError('Action exceeds remaining stack')
            if kind in ('fold','check'):same(increment,0.)
            if kind=='check' and call>1e-8:raise ValueError('Check facing a bet')
            if kind=='call':same(increment,call)
            if kind in ('bet','raise') and increment<=call+1e-8:raise ValueError('Non-increasing raise')
            allin=increment>0 and math.isclose(increment,own,abs_tol=1e-8,rel_tol=1e-10)
            if action['all_in']!=allin:raise ValueError('All-in flag mismatch')
            features += [1.,*[float(kind==k) for k in KINDS],float(allin),log(increment),increment/(pot+increment),increment/own if own else 0.]
        assert len(features)==len(NAMES)
        result.append(features)
    matrix=np.asarray(result,dtype=np.float32).reshape((-1,len(NAMES)))
    if not np.isfinite(matrix).all():raise ValueError('Nonfinite encoded feature')
    return matrix
