"""Attach source-deal weights to validated native visits, without scaling targets."""
from types import SimpleNamespace
import numpy as np
from later_action_training_ingest_v1 import ingest as original_ingest
from exact_initial_training_ingest_v2 import digest
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_deal_binding_v1 import DealWeightGeneration

METHOD = 'source-deal-weighted-later-action-ingest-v1'


def ingest(queries, updates, policies, reservoirs, iteration, cache, targets, trace,
           *, generation, start, guard=lambda: None):
    guard()
    if (not isinstance(generation, DealWeightGeneration) or len(reservoirs) != 2
            or any(not isinstance(r, WeightedPhysicalReservoir) or r.player != p
                   or r.context_sha256 != generation.context_sha256 for p,r in enumerate(reservoirs))):
        raise ValueError('Validated source and both explicitly weighted reservoirs required')
    binding = generation.bind(queries, start)
    events = []; receivers = []
    for r in reservoirs:
        receiver = SimpleNamespace(player=r.player, context_sha256=r.context_sha256, seen=r.seen)
        receiver._insert = lambda row,it,player=r.player: events.append((player,row,it))
        receivers.append(receiver)
    counts, initial_audit, later_audit = original_ingest(queries, updates, policies, receivers,
        iteration, cache, targets, trace, guard=guard)
    # The original ingester has checked native cashflow, ordered traversal
    # groups, exact root overrides and all conditional postflop targets.
    records = updates['records']; obs = queries['observations']
    heads = [i for i,r in enumerate(records) if obs[r[0]]['phase'] == 0 and int(obs[r[0]]['hi']) == 1]
    if not heads or heads[0] != 0 or len(heads) != 2*len(binding['deal_weights']):
        raise ValueError('Complete ordered traversal headers required')
    derived = []; witnesses = []; group = 0; event = 0
    for i,(query,player,tag,values) in enumerate(records):
        while group+1 < len(heads) and i >= heads[group+1]: group += 1
        deal, updater = divmod(group, 2)
        if player != updater: raise ValueError('Mixed source traversal updater')
        if tag <= 0: continue
        if event >= len(events): raise ValueError('Missing derived visit')
        actor,row,it = events[event]; event += 1
        key = tuple(int(obs[query][k]) for k in ('hi','lo'))
        if actor != player or it != iteration or row[0] != key or row[2] != tag:
            raise ValueError('Derived visit detached from native record')
        weight = binding['deal_weights'][deal]
        derived.append((player,row,it,weight))
        witnesses.append(dict(record=i, deal=deal, source_deal=start+deal, updater=player, weight=weight))
    if event != len(events): raise ValueError('Extra derived visits')
    added = np.bincount([p for p,row,it,w in derived], minlength=2)
    if added.tolist() != counts or any(r.seen+int(n) >= 2**63 for r,n in zip(reservoirs,added)):
        raise ValueError('Visit count mismatch or overflow')
    audit = dict(format=1, method=METHOD, iteration=iteration, binding=binding,
        initial_audit_sha256=digest(initial_audit), later_audit_sha256=digest(later_audit),
        records=witnesses, meaning='Weights attach to visits; advantage values remain unchanged. Apply weights once in fitting and table aggregation.')
    guard()
    for player,row,it,weight in derived:
        reservoirs[player]._insert(row, it, deal_weight=weight)
    return counts, initial_audit, later_audit, audit
