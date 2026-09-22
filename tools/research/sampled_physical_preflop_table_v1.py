"""Direct retained-mean preflop regrets, with neural fallback for missing rows.

An optional research policy representation. It does not change any old model,
checkpoint, trainer or evaluator. Postflop neural probabilities remain untouched.
"""
import hashlib
import json
import numpy as np
from sampled_physical_fit_v1 import grouped_rows
from sampled_physical_reservoir_v1 import checked_row
from sampled_batch_model_v1 import predict
from sampled_physical_bank_v1 import histories


def context_hash(source): return hashlib.sha256(source.encode('utf-8')).hexdigest()


def validate_preflop(row, context, player):
    hi,lo = int(row['hi']),int(row['lo'])
    if not 1 <= hi <= len(context['nodes']) or hi > 16 or not 0 <= lo < 2**43:
        raise ValueError('Invalid preflop key')
    cards = [(lo >> (6*i)) & 63 for i in range(7)]
    if cards[0] >= 52 or cards[1] >= 52 or cards[0] == cards[1] or cards[2:] != [63]*5:
        raise ValueError('Preflop key contains invalid or future cards')
    node = context['nodes'][hi-1]
    if node['kind'] != 0 or node['actor'] != player or (lo>>42) != player:
        raise ValueError('Preflop table actor or decision mismatch')
    if row['actor'] != player or row['n'] != len(node['actions']):
        raise ValueError('Preflop table legal menu mismatch')
    # Reconstruct every visible one-hot feature, including unknown future cards.
    active = []; at = 0
    for c in cards:
        active.append(at+(13 if c == 63 else c//4)); at += 14
        active.append(at+(4 if c == 63 else c%4)); at += 5
    active.append(at+player); at += 2
    active.append(at); at += 4
    active.append(at+hi-1); at += 16
    for _ in range(19): active.append(at); at += 6
    if at != 269 or sorted(row['active_features']) != sorted(active):
        raise ValueError('Preflop features disagree with visible key')
    return hi,lo


def build(reservoir, context_source):
    if reservoir.context_sha256 != context_hash(context_source):
        raise ValueError('Reservoir belongs to another context')
    grouped = grouped_rows(reservoir)
    keys = np.unique(reservoir.keys[:reservoir.size],axis=0)
    context = json.loads(context_source); rows = []
    for i in np.flatnonzero(keys[:,0] < 2**63):
        row = dict(hi=str(int(keys[i,0])),lo=str(int(keys[i,1])),actor=reservoir.player,
            n=int(grouped['arity'][i]),active_features=grouped['active'][i].astype(int).tolist(),
            count=int(grouped['counts'][i]),mean_regret=(grouped['targets'][i]*grouped['scale']).tolist())
        validate_preflop(row,context,reservoir.player); checked_row(row,row['mean_regret']); rows.append(row)
    return dict(format=1,context_sha256=context_hash(context_source),player=reservoir.player,
        source_reservoir=reservoir.summary(),rows=rows,
        meaning='Mean retained sampled advantages per exact visible preflop observation; not action EVs.',
        missing_policy='Preserve neural probabilities for unobserved preflop rows; postflop unchanged')


class Table:
    def __init__(self, document, context_source):
        if document['format'] != 1 or document['context_sha256'] != context_hash(context_source):
            raise ValueError('Preflop table context or format mismatch')
        self.player = document['player']
        if type(self.player) is not int or self.player not in (0,1):
            raise ValueError('Invalid table player')
        context = json.loads(context_source); self.context = context; self.rows = {}
        for row in document['rows']:
            key = validate_preflop(row,context,self.player)
            checked_row(row,row['mean_regret'])
            if type(row['count']) is not int or row['count'] <= 0 or key in self.rows:
                raise ValueError('Duplicate observation or invalid count')
            score = np.asarray(row['mean_regret'],dtype=np.float64)
            probability = np.maximum(score,0.)
            if probability.sum() > 0:
                probability /= probability.sum()
            else:
                probability = np.zeros(4); probability[int(np.argmax(score[:row['n']]))] = 1.
            self.rows[key] = (row['n'],tuple(sorted(row['active_features'])),probability)

    def apply(self, observations, probabilities):
        probabilities = np.asarray(probabilities,dtype=np.float64)
        if probabilities.shape != (len(observations),4):
            raise ValueError('Policy shape mismatch')
        if not np.isfinite(probabilities).all() or np.any(probabilities < 0) or np.max(np.abs(probabilities.sum(1)-1)) > 1e-12:
            raise ValueError('Invalid input probabilities')
        result = probabilities.copy(); matched = []
        for i,o in enumerate(observations):
            if o['actor'] not in (0,1) or o['n'] not in (2,3,4) or np.any(probabilities[i,o['n']:]):
                raise ValueError('Invalid input actor or legal action probabilities')
            if (int(o['hi']) < 2**63) != (o['phase'] == 0):
                raise ValueError('Query phase disagrees with observation key')
            if o['actor'] != self.player: continue
            if o['phase'] != 0: continue
            key = validate_preflop(o,self.context,self.player)
            if key not in self.rows: continue
            n,active,p = self.rows[key]
            if o['n'] != n or tuple(sorted(o['active_features'])) != active:
                raise ValueError('Query disagrees with preflop table observation')
            result[i] = p; matched.append(i)
        return result,matched


def average(queries, models, weights_by_player, *, context_source, device, guard):
    """Reference hybrid averaging: override BEFORE propagating own-history reach.

    Each model has two network dictionaries and two table documents (or None for
    the original uniform model). This is a correctness reference, not a GPU bank.
    """
    if queries['context_source'] != context_source:
        raise ValueError('Queries belong to another game')
    obs = queries['observations']; history = histories(obs)
    weights = np.asarray(weights_by_player,dtype=np.float64)
    if weights.ndim != 2 or weights.shape[0] != 2 or weights.shape[1] == 0 or not np.isfinite(weights).all() or np.any(weights <= 0) or not np.isfinite(weights.sum()):
        raise ValueError('Two positive finite model-weight sequences required')
    numerator = np.zeros((len(obs),4)); denominator = np.zeros(len(obs)); processed = 0
    actors = np.array([o['actor'] for o in obs],dtype=np.int64)
    for m,model in enumerate(models):
        guard()
        if m >= weights.shape[1] or len(model['tables']) != 2:
            raise ValueError('Invalid model bank')
        _,p = predict(obs,model['networks'],device)
        for player,document in enumerate(model['tables']):
            if document is not None:
                table = Table(document,context_source)
                if table.player != player: raise ValueError('Swapped player tables')
                p,_ = table.apply(obs,p)
        reach = weights[actors,m].copy()
        for i,prior in enumerate(history):
            for index,action in prior: reach[i] *= p[index,action]
        numerator += p*reach[:,None]; denominator += reach; processed += 1
    if processed != weights.shape[1]: raise ValueError('Incomplete bank')
    supported = denominator > 0; result = np.zeros_like(numerator)
    result[supported] = numerator[supported]/denominator[supported,None]
    for i in np.flatnonzero(~supported): result[i,:obs[i]['n']] = 1./obs[i]['n']
    if np.max(np.abs(result.sum(1)-1)) > 1e-12: raise ValueError('Invalid averaged policy')
    return result,denominator
