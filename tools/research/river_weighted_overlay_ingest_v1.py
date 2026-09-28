"""Validated river-only overlay after the existing exact/weighted derivation."""
import hashlib
import math
import numpy as np
from exact_initial_training_ingest_v2 import digest
from sampled_physical_reservoir_v1 import checked_row
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_training_workers_v1 import CollectedVisits
from weighted_later_action_ingest_v1 import ingest as baseline_ingest

METHOD = 'posterior64-visited-river-overlay-v1'


def binding(queries, updates, policies, trace, generation, start, iteration, policy_id):
    return dict(context_sha256=hashlib.sha256(queries['context_source'].encode()).hexdigest(), queries_sha256=digest(queries),
                updates_sha256=digest(updates), policies_sha256=digest(policies), trace_sha256=digest(trace),
                source_generation_sha256=generation.sha256, start=start, iteration=iteration, policy_id=policy_id)


def ingest(queries, updates, policies, reservoirs, iteration, cache, targets, trace, *,
           generation, start, overlay, expected_policy_id, expected_evidence_sha256, guard=lambda:None):
    """Check the complete batch before any real insertion or reservoir RNG draw.

    The separately qualified target generator owns the mathematical evidence.
    This boundary requires its expected identity and binds every replacement
    to the original current-policy record. Unsupported batches reject intact.
    """
    guard()
    if (len(reservoirs)!=2 or any(not isinstance(r,WeightedPhysicalReservoir) or r.player!=p
            or r.context_sha256!=generation.context_sha256 for p,r in enumerate(reservoirs))):
        raise ValueError('Two matching weighted reservoirs required')
    if not isinstance(expected_policy_id,str) or not expected_policy_id:
        raise ValueError('Explicit current policy identity required')
    want=binding(queries,updates,policies,trace,generation,start,iteration,expected_policy_id)
    if (overlay.get('format')!=1 or overlay.get('method')!=METHOD or overlay.get('K')!=64
            or overlay.get('binding')!=want or overlay.get('evidence_sha256')!=expected_evidence_sha256
            or not isinstance(expected_evidence_sha256,str) or len(expected_evidence_sha256)!=64):
        raise ValueError('Overlay source, policy, record or evidence binding changed')
    obs=queries['observations'];records=updates['records']
    selected=[i for i,r in enumerate(records) if r[2]>0 and obs[r[0]]['phase']==3]
    rows=overlay.get('rows')
    if not isinstance(rows,list) or [r.get('record') for r in rows]!=selected:
        raise ValueError('Every positive river visit required once in original order')
    probabilities=np.asarray([r['probabilities'] for r in policies['policies']],dtype=np.float64)
    replacements={}
    for index,row in zip(selected,rows):
        qi,actor,arity,_=records[index];o=obs[qi]
        if (row.get('query')!=qi or row.get('updater')!=actor or row.get('key')!=[o['hi'],o['lo']]
                or actor!=o['actor'] or arity!=o['n'] or row.get('draw_count')!=64):
            raise ValueError('Overlay detached from its native river visit')
        mass=row.get('opponent_mass')
        if isinstance(mass,bool) or not isinstance(mass,(int,float)) or not math.isfinite(mass) or mass<=0:
            raise ValueError('Unsupported opponent posterior; batch remains unchanged')
        validated=checked_row(o,row['advantages']);value=validated[3].copy()
        if abs(float(probabilities[qi]@value))>1e-8:
            raise ValueError('River target is not centered under the current policy')
        replacements[index]=value

    events=[];receivers=[CollectedVisits(p,queries['context_source'],events) for p in (0,1)]
    for r,original in zip(receivers,reservoirs):r.seen=original.seen
    counts,initial,later,weighted=baseline_ingest(queries,updates,policies,receivers,iteration,cache,targets,trace,
        generation=generation,start=start,guard=guard)
    positive=[(i,r) for i,r in enumerate(records) if r[2]>0]
    if len(events)!=len(positive):raise ValueError('Original visit count changed')
    staged=[]
    for (index,record),(actor,row,it,weight) in zip(positive,events):
        qi,player,arity,_=record
        if (actor!=player or it!=iteration or row[0]!=tuple(int(obs[qi][k]) for k in ('hi','lo'))
                or row[2]!=arity):raise ValueError('Original weighted insertion order changed')
        if index in replacements:row=(*row[:3],replacements[index])
        staged.append((actor,row,it,weight))
    if np.bincount([e[0] for e in staged],minlength=2).tolist()!=counts:
        raise ValueError('Actor visit counts changed')
    audit=dict(format=1,method=METHOD,overlay_sha256=digest(overlay),binding=want,counts=counts,
               replacements=selected,initial_audit_sha256=digest(initial),later_audit_sha256=digest(later),
               weighted_audit_sha256=digest(weighted),source_weights='Unchanged, applied once by the original weighted ingester.',
               scope='Only approved river values change; visit order, weighting and preflop/flop/turn derivation preserved.')
    guard()
    for actor,row,it,weight in staged:reservoirs[actor]._insert(row,it,deal_weight=weight)
    return counts,initial,later,weighted,audit
