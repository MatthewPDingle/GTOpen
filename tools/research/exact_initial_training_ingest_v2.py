"""Separate derived BB root targets; immutable native traversal evidence.

The caller supplies the admitted matrix and the complete CURRENT played policy
once per generation. This is not an average-policy target, sampled BTN update,
or new native cashflow verification. No production trainer imports this module.
"""
import hashlib
import json
from types import SimpleNamespace
import numpy as np
from initial_allin_targets_v1 import bb_correction
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import ingest as native_ingest, policy_document
from sampled_physical_preflop_table_v1 import validate_preflop
from sampled_physical_root_evaluation_v1 import hand_class


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


class InitialTargets:
    def __init__(self, matrix_source, context_source, root_policy, btn_calls, *,
                 matrix_sha256, generation):
        if type(generation) is not int or generation < 0:
            raise ValueError('Nonnegative played generation required')
        if hashlib.sha256(matrix_source.encode()).hexdigest() != matrix_sha256:
            raise ValueError('Admitted matrix bytes changed')
        self.context_source = context_source
        self.context = json.loads(context_source)
        root = self.context['nodes'][0]
        if (root['actor'] != 0 or root['kind'] != 0 or
                [a['kind'] for a in root['actions']] != ['fold', 'call', 'raise', 'jam']):
            raise ValueError('Fixed BB first-action fold/call/raise/jam geometry required')
        self.response_hi = root['children'][3] + 1
        response = self.context['nodes'][self.response_hi-1]
        if (response['actor'] != 1 or response['kind'] != 0 or
                [a['kind'] for a in response['actions']] != ['fold', 'call'] or
                any(self.context['nodes'][i]['kind'] == 0 for i in response['children'])):
            raise ValueError('Initial BTN fold/call response must end preflop play')
        self.matrix = AllinMatrix(json.loads(matrix_source), context_source)
        self.root = np.array(root_policy, dtype=np.float64, copy=True)
        self.calls = np.array(btn_calls, dtype=np.float64, copy=True)
        exact = self.matrix.evaluate(self.root, self.calls)
        self.calls[self.matrix.btn_mass == 0] = 0.
        self.jam = np.full(169, np.nan)
        np.divide(exact['bb_jam_entries'], exact['bb_entries'], out=self.jam,
                  where=exact['bb_entries'] > 0)
        self.generation = generation
        self.identity = dict(generation=generation, matrix_sha256=matrix_sha256,
            context_sha256=hashlib.sha256(context_source.encode()).hexdigest(),
            current_initial_policy_sha256=digest(dict(root=self.root.tolist(), calls=self.calls.tolist())))
        for a in (self.root, self.calls, self.jam):
            a.flags.writeable = False


def ingest(queries, updates, policies, reservoirs, iteration, cache, targets, *, guard=lambda: None):
    """Validate and derive ALL rows before any reservoir mutation/RNG draw."""
    guard()
    if queries['context_source'] != targets.context_source or iteration != targets.generation+1:
        raise ValueError('Targets must belong to this game and current played generation')
    p = np.asarray([r['probabilities'] for r in policies['policies']], dtype=np.float64)
    if policies != policy_document(queries, p):
        raise ValueError('Original frozen policy document required')
    obs = queries['observations']
    for o, row in zip(obs, p):
        if int(o['hi']) not in (1, targets.response_hi):
            continue
        actor = 0 if int(o['hi']) == 1 else 1
        _, lo = validate_preflop(o, targets.context, actor)
        if o.get('own_history', []) != []:
            raise ValueError('Initial action cannot have own-action ancestors')
        c = hand_class([lo & 63, (lo >> 6) & 63])
        mass = targets.matrix.bb_mass[c] if actor == 0 else targets.matrix.btn_mass[c]
        expected = targets.root[c] if actor == 0 else np.array([1-targets.calls[c], targets.calls[c], 0., 0.])
        if mass <= 0 or np.max(abs(row-expected)) > 1e-12:
            raise ValueError('Queries disagree with complete current initial policy or incoming population')

    events = []
    receivers = []
    for r in reservoirs:
        receiver = SimpleNamespace(player=r.player, context_sha256=r.context_sha256, seen=r.seen)
        receiver._insert = lambda row, it, player=r.player: events.append((player, row, it))
        receivers.append(receiver)
    counts = native_ingest(queries, updates, receivers, iteration, cache)
    records = updates['records']
    batch = json.loads(queries['batch_source'])
    heads = [i for i, r in enumerate(records) if obs[r[0]]['phase'] == 0 and int(obs[r[0]]['hi']) == 1]
    roots = updates['roots']
    if len(heads) != len(roots) or len(roots) != 2*len(batch['deals']) or not heads or heads[0] != 0:
        raise ValueError('One ordered native root per deal and updater required')
    replacements = {}
    witnesses = []
    for k, (deal_id, updater, value) in enumerate(roots):
        if (type(deal_id) is not int or type(updater) is not int or
                (deal_id, updater) != divmod(k, 2) or not np.isfinite(value)):
            raise ValueError('Invalid native root header')
        start, end = heads[k], heads[k+1] if k+1 < len(heads) else len(records)
        group = records[start:end]
        if any(r[1] != updater for r in group):
            raise ValueError('Mixed updater traversal group')
        qi, _, tag, values = group[0]
        o = obs[qi]
        lo = int(o['lo'])
        c = hand_class(batch['deals'][deal_id][:2])
        if hand_class([lo & 63, (lo >> 6) & 63]) != c or tag != (4 if updater == 0 else -4):
            raise ValueError('Wrong root hand class or updater tag')
        for index, _, record_tag, record_values in group:
            if record_tag < 0 and np.max(abs(np.asarray(record_values)-p[index])) > 1e-12:
                raise ValueError('Native opponent observation differs from frozen policy')
        if updater != 0:
            continue
        old = np.asarray(values, dtype=np.float64)
        if abs(old @ p[qi]) > 1e-9 or abs(old[0]+value-targets.matrix.bb_fold) > 1e-9:
            raise ValueError('Native root value and signed advantages disagree')
        sampled_jam = float(old[3]+value)
        value_delta, delta = bb_correction(p[qi], sampled_jam, targets.jam[c])
        corrected = old+delta
        if not np.isfinite(corrected).all() or abs(corrected @ p[qi]) > 1e-9:
            raise ValueError('Derived root advantages do not recenter')
        replacements[start] = corrected
        witnesses.append(dict(record=start, query=qi, deal=deal_id, hand_class=c,
            sampled_root_value=float(value), sampled_jam_value=sampled_jam,
            exact_conditional_jam_value=float(targets.jam[c]),
            derived_root_value=float(value+value_delta), advantages=corrected.tolist()))

    # Preserve original global order (and hence each player's insertion order).
    e = 0
    derived = []
    for i, (_, player, tag, _) in enumerate(records):
        if tag <= 0:
            continue
        actual_player, row, it = events[e]
        if actual_player != player or it != iteration:
            raise ValueError('Checked insertion event order changed')
        if i in replacements:
            row = (*row[:3], replacements[i])
        derived.append((player, row, it))
        e += 1
    if e != len(events) or len(witnesses) != len(batch['deals']):
        raise ValueError('Derived insertion count mismatch')
    audit = dict(format=1, method='exact-initial-bb-training-targets-v2',
        identity=targets.identity, iteration=iteration, counts=counts,
        queries_sha256=digest(queries), raw_updates_sha256=digest(updates), policies_sha256=digest(policies),
        bb_root_corrections=witnesses,
        scope='Derived learning targets only; original native cashflow verification applies solely to unmodified raw updates. BTN sampled visits and every non-root row unchanged.')
    guard()
    for player, row, it in derived:
        reservoirs[player]._insert(row, it)
    return counts, audit
