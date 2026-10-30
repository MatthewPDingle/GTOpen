"""Context-bound weighted fit rows, separate from policy own-reach evaluation.

Reservoirs retain visible keys/features, not native ancestor query indices.
Encoding a fit row therefore validates its encoded public history directly; it
never constructs an empty or invented own-history chain for policy averaging.
"""
import numpy as np
from sampled_visible_features_bulk_v1 import features
from stack_board_relative_features_v1 import relative_features
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_visible_objective_v1 import grouped_rows

METHOD = 'context-balanced-stack-normalized-weighted-objective-v1'


def encode_rows(registry, reservoir, indices):
    if not isinstance(reservoir, WeightedPhysicalReservoir):
        raise ValueError('Explicit source-weighted visit reservoir required')
    entry = registry._get(reservoir.context_sha256)
    if entry['split'] != 'fit':
        raise ValueError('Held-out contexts cannot enter fitting')
    width = registry.manifest['representation']['input_width']
    if width not in (362, 387):
        raise ValueError('Versioned context representation required')
    ids = np.asarray(indices)
    if ids.ndim != 1 or ids.dtype.kind not in 'iu' or not len(ids) or np.any(ids < 0) or np.any(ids >= reservoir.size):
        raise ValueError('Nonempty retained reservoir indices required')
    x = features([dict(active_features=reservoir.active[i].astype(int).tolist()) for i in ids])
    public = []; extra = []; keys = []
    for i, visible in zip(ids, x):
        hi, lo = map(int, reservoir.keys[i]); actor = int(np.argmax(visible[133:135]))
        phase = int(np.argmax(visible[135:139])); node = int(np.argmax(visible[139:155]))
        if actor != reservoir.player or str(hi) not in entry['lookup']:
            raise ValueError('Unknown public key or different actor')
        row, price = entry['lookup'][str(hi)]
        if (actor, phase, int(reservoir.arity[i])) != (row['actor'], row['phase'], len(row['actions'])):
            raise ValueError('Fit row disagrees with native public ledger')
        cards = []
        for position in range(7):
            offset = 19 * position
            rank = int(np.argmax(visible[offset:offset+14]))
            suit = int(np.argmax(visible[offset+14:offset+19]))
            cards.append(63 if rank == 13 else rank*4+suit)
        encoded_lo = (actor << 42) | sum(c << (6*j) for j,c in enumerate(cards))
        tokens = [int(np.argmax(visible[155+6*j:161+6*j])) for j in range(19)]
        length = next((j for j,a in enumerate(tokens) if a == 0), 19)
        if any(tokens[length:]):
            raise ValueError('Malformed public-history padding')
        tokens = tokens[:length]
        if phase == 0:
            if tokens:
                raise ValueError('Postflop history in a preflop fit row')
            encoded_hi = node + 1
        else:
            if tokens.count(5) != phase-1:
                raise ValueError('Fit row street/history mismatch')
            history = 1
            for token in tokens:
                history = (history << 3) | token
            if history >= 2**59:
                raise ValueError('Public-history key overflow')
            encoded_hi = (1 << 63) | (history << 4) | node
        if (hi,lo) != (encoded_hi,encoded_lo):
            raise ValueError('Stored fit keys and visible features disagree')
        public.append(price); keys.append((reservoir.context_sha256, str(hi), str(lo)))
        if width == 387:
            extra.append(relative_features(cards[:2],cards[2:]) if phase == 3 else np.zeros(25,np.float32))
    parts = [x, np.asarray(public, dtype=np.float32)]
    if width == 387:
        parts.append(np.asarray(extra, dtype=np.float32))
    encoded = np.concatenate(parts, axis=1)
    if encoded.shape != (len(ids),width) or not np.isfinite(encoded).all():
        raise ValueError('Invalid context-bound fit features')
    return encoded, keys


def prepare(registry, reservoirs, *, player, context_weights):
    """Exact grouped MSE mixture; positive source weights multiply the loss.

Every fitting context must supply one nonempty reservoir for this actor. Each
context's loss is normalized by its own weighted legal-action count, then mixed
with the explicit fixed context weight. Targets use bb / starting stack, and
the within-observation variance is retained for objective equivalence checks.
"""
    required = set(registry.fit_contexts)
    if type(player) is not int or player not in (0,1):
        raise ValueError('Explicit actor required')
    if set(reservoirs) != required or set(context_weights) != required:
        raise ValueError('Exactly all fitting contexts must contribute')
    weights = np.asarray([context_weights[k] for k in sorted(required)], dtype=np.float64)
    if not np.isfinite(weights).all() or np.any(weights <= 0) or abs(float(weights.sum())-1.) > 1e-12:
        raise ValueError('Explicit positive normalized context weights required')
    xs = []; ys = []; ws = []; keys = []; summaries = []; variance = 0.
    for key, weight in zip(sorted(required),weights):
        reservoir = reservoirs[key]
        if (not isinstance(reservoir,WeightedPhysicalReservoir) or reservoir.context_sha256 != key
                or reservoir.player != player or not reservoir.size):
            raise ValueError('Nonempty matching actor/context reservoir required')
        grouped = grouped_rows(reservoir)
        # np.unique ordering is the same ordering used by grouped_rows.
        _, first = np.unique(reservoir.keys[:reservoir.size], axis=0, return_index=True)
        x, identity = encode_rows(registry,reservoir,first)
        stack = float(registry._get(key)['context']['config']['stack'])
        if not np.isfinite(stack) or stack <= 0:
            raise ValueError('Finite positive starting stack required')
        factor = grouped['scale']/stack
        target = grouped['targets'] * factor
        legal = np.arange(4)[None,:] < grouped['arity'][:,None]
        row_weights = legal * grouped['masses'][:,None] * (weight/grouped['denominator'])
        if not np.isfinite(target).all() or not np.isfinite(row_weights).all():
            raise ValueError('Nonfinite context objective')
        part_variance = grouped['variance'] * factor**2
        variance += weight * part_variance
        xs.append(x); ys.append(target); ws.append(row_weights); keys.extend(identity)
        summaries.append(dict(context_sha256=key,player=player,starting_stack=stack,
            mixture_weight=float(weight),examples=reservoir.size,groups=len(x),
            weighted_legal_target_mass=grouped['denominator'],within_observation_variance=part_variance))
    if len(set(keys)) != len(keys):
        raise ValueError('Context-bound grouping must be unique')
    x,y,w = np.concatenate(xs),np.concatenate(ys),np.concatenate(ws)
    if abs(float(w.sum())-1.) > 1e-12 or not np.isfinite(variance):
        raise ValueError('Invalid complete mixture normalization')
    return dict(method=METHOD,representation=registry.manifest['representation'],
        registry_sha256=registry.sha256,player=player,features=x,targets=y,weights=w,
        keys=keys,contexts=summaries,within_observation_variance=float(variance),
        target_units='advantage_bb / context_starting_stack',own_history_available=False)
