"""Postflop-only conditional-action targets; original visits and exact roots preserved."""
import json
from types import SimpleNamespace
import numpy as np
from exact_initial_training_ingest_v2 import ingest as exact_ingest, digest
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_reservoir_v1 import checked_row

METHOD = 'postflop-conditional-action-targets-v1'


def replacements(queries, updates, policies, trace):
    if trace.get('format') != 2 or trace.get('method') != 'all-node-action-trace-v2':
        raise ValueError('Policy-bound version-2 action trace required')
    for field in ('context_source','batch_source'):
        if trace.get(field) != queries[field]: raise ValueError('Trace input identity changed')
    if not isinstance(trace.get('policy_source'), str) or json.loads(trace['policy_source']) != policies:
        raise ValueError('Trace was not evaluated under the supplied policy')
    p = np.array([r['probabilities'] for r in policies['policies']])
    if policy_document(queries, p) != policies: raise ValueError('Policy transport changed')
    if trace.get('sampled_records') != updates['records'] or trace.get('sampled_roots') != updates['roots']:
        raise ValueError('Original sampled visits or values changed')
    batch = json.loads(queries['batch_source']); obs = queries['observations']
    if len(trace['traces']) != len(batch['deals']): raise ValueError('Physical deal count changed')
    maps=[]
    for did, part in enumerate(trace['traces']):
        if part['deal_index'] != did: raise ValueError('Trace deal order changed')
        rows={}
        for row in part['nodes']:
            qi=row['query']
            if type(qi) is not int or not 0<=qi<len(obs) or qi in rows:
                raise ValueError('Duplicate or invalid physical-deal node')
            if row['actor']!=obs[qi]['actor'] or row['n']!=obs[qi]['n']:
                raise ValueError('Node actor or action count changed')
            rows[qi]=row
        maps.append(rows)
    positives=[i for i,r in enumerate(updates['records']) if r[2]>0]
    if [t['record'] for t in trace['conditional_targets']] != positives:
        raise ValueError('Derived targets must cover original positive records once in order')
    heads=[i for i,r in enumerate(updates['records']) if obs[r[0]]['phase']==0 and obs[r[0]]['hi']=='1']
    if len(heads)!=2*len(maps) or not heads or heads[0]!=0:
        raise ValueError('Original traversal group headers required')
    group=0; result={}; witnesses=[]
    for target in trace['conditional_targets']:
        i=target['record']
        while group+1<len(heads) and i>=heads[group+1]: group+=1
        did, actor=divmod(group,2)
        qi, updater, n, _=updates['records'][i]
        if (target['deal'],target['updater'],target['query'])!=(did,actor,qi) or updater!=actor:
            raise ValueError('Derived target moved between visits or physical deals')
        node=maps[did][qi]
        q=np.array(node['action_values'],dtype=np.float64); value=np.array(node['values'],dtype=np.float64)
        if q.shape!=(4,2) or value.shape!=(2,) or not np.isfinite(q).all() or not np.isfinite(value).all() or np.any(q[n:]):
            raise ValueError('Invalid conditional action values')
        expected=p[qi]@q
        adv=np.zeros(4);adv[:n]=q[:n,actor]-expected[actor]
        supplied=checked_row(obs[qi],target['advantages'])[3]
        if (np.max(abs(expected-value))>1e-9 or np.max(abs(adv-supplied))>1e-9
                or abs(float(p[qi]@supplied))>1e-9):
            raise ValueError('Conditional targets do not match the frozen policy expectation')
        # Preserve every preflop target and all population-integrated overrides.
        if obs[qi]['phase'] in (1,2,3):
            result[i]=supplied.copy()
            witnesses.append(dict(record=i,deal=did,query=qi,updater=actor,advantages=supplied.tolist()))
        elif obs[qi]['phase'] != 0:
            raise ValueError('Unknown observation phase')
    return result,witnesses


def ingest(queries, updates, policies, reservoirs, iteration, cache, targets, trace, *, guard=lambda:None):
    """Validate all derived rows before taking any real reservoir RNG draw."""
    guard(); changed,witnesses=replacements(queries,updates,policies,trace)
    events=[]; receivers=[]
    for r in reservoirs:
        receiver=SimpleNamespace(player=r.player,context_sha256=r.context_sha256,seen=r.seen)
        receiver._insert=lambda row,it,player=r.player: events.append((player,row,it))
        receivers.append(receiver)
    counts,initial_audit=exact_ingest(queries,updates,policies,receivers,iteration,cache,targets,guard=guard)
    positives=[(i,r) for i,r in enumerate(updates['records']) if r[2]>0]
    if len(events)!=len(positives): raise ValueError('Original insertion count changed')
    derived=[]
    for (index,record),(player,row,it) in zip(positives,events):
        if record[1]!=player or it!=iteration: raise ValueError('Original insertion order changed')
        if index in changed: row=(*row[:3],changed[index])
        derived.append((player,row,it))
    audit=dict(format=1,method=METHOD,iteration=iteration,counts=counts,
        queries_sha256=digest(queries),raw_updates_sha256=digest(updates),policies_sha256=digest(policies),
        trace_sha256=digest(trace),initial_audit_sha256=digest(initial_audit),postflop_replacements=witnesses,
        scope='Only positive-tag postflop advantage targets replaced. Original insertion order, sampling, preflop targets and exact initial overrides retained. Not raw native cashflow evidence.')
    guard()
    for player,row,it in derived: reservoirs[player]._insert(row,it)
    return counts,initial_audit,audit
