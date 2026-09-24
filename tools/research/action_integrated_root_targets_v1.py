"""Separately typed root-only targets; do not mutate sampled reservoir updates."""
import hashlib
import json
import math

METHOD='action-integrated-bb-root-targets-v1'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def derive(queries,policies,sampled_audit,profiles,full):
    """Average later actions on fixed cards; retain the admitted exact initial jam.

    The caller runs and hash-binds the native evaluator. This adapter validates
    the exact policy/card transport and mixture, then emits only BB root targets.
    It does not reclassify these values as raw external-sampling updates.
    """
    if (queries.get('format')!=3 or policies.get('format')!=3
            or sampled_audit.get('format')!=1
            or sampled_audit.get('method')!='exact-initial-bb-training-targets-v2'
            or profiles.get('format')!=1 or full.get('format')!=2):
        raise ValueError('Explicit admitted source and integration formats required')
    if any(d.get('terminal_estimator')!='conditional-preflop-allin-v1' for d in (queries,policies,full)):
        raise ValueError('Conditional preflop all-in estimator required')
    if full.get('postflop_outcomes')!='sampled-board':
        raise ValueError('Postflop boards must remain sampled')
    for key in ('context_source','batch_source'):
        if not isinstance(queries.get(key),str) or queries[key]!=policies.get(key) or queries[key]!=profiles.get(key):
            raise ValueError('Changed context or physical batch')
    if (sampled_audit['queries_sha256']!=digest(queries)
            or sampled_audit['policies_sha256']!=digest(policies)):
        raise ValueError('Sampled targets belong to different queries or policy')
    if any(not math.isfinite(full[k]) or full[k]>1e-10 for k in ('maximum_forward_cashflow_error','maximum_conservation_error')):
        raise ValueError('Native action integration failed cashflow checks')
    observations=queries['observations'];base=policies['policies']
    if len(base)!=len(observations):raise ValueError('Incomplete policy')
    names=['baseline',*[f'action-{a}' for a in range(4)]]
    if ([p['name'] for p in profiles['profiles']]!=names or [p['name'] for p in full['profiles']]!=names):
        raise ValueError('Every baseline and forced root action is required')
    if profiles['profiles'][0]['policies']!=base:raise ValueError('Baseline policy changed')
    root_ids={i for i,o in enumerate(observations) if o['phase']==0 and o['hi']=='1'}
    if not root_ids:raise ValueError('Missing BB root')
    for action in range(4):
        rows=profiles['profiles'][action+1]['policies']
        if len(rows)!=len(base):raise ValueError('Incomplete forced-action policy')
        for i,(old,new) in enumerate(zip(base,rows)):
            expected=old if i not in root_ids else dict(old,probabilities=[float(k==action) for k in range(4)])
            if new!=expected:raise ValueError('A forced action changed a later policy')
    batch=json.loads(queries['batch_source']);source=sampled_audit['bb_root_corrections']
    if len(source)!=len(batch['deals']) or [r['deal'] for r in source]!=list(range(len(source))):
        raise ValueError('Exactly one sequential root per physical deal required')
    for p in full['profiles']:
        if len(p['deals'])!=len(source) or [r['deal_index'] for r in p['deals']]!=list(range(len(source))):
            raise ValueError('Native deal order changed')
    derived=[]
    for i,row in enumerate(source):
        qi=row['query']
        if qi not in root_ids or observations[qi]['actor']!=0 or observations[qi]['n']!=4:
            raise ValueError('Wrong source root observation')
        probability=base[qi]['probabilities']
        if len(probability)!=4 or any(not math.isfinite(x) or x<0 for x in probability) or abs(sum(probability)-1)>1e-12:
            raise ValueError('Invalid original root policy')
        values=[p['deals'][i]['values'][0] for p in full['profiles'][1:]]
        if not all(math.isfinite(v) for v in values):raise ValueError('Finite action values required')
        expected=math.fsum(p*v for p,v in zip(probability,values))
        if abs(expected-full['profiles'][0]['deals'][i]['values'][0])>1e-9:
            raise ValueError('Integrated baseline and action mixture disagree')
        if abs(values[0]-(row['advantages'][0]+row['derived_root_value']))>1e-9:
            raise ValueError('Fold payoff changed')
        # Keep the original complete-private-population initial jam expectation,
        # not the native value conditional on just this sampled private pair.
        values[3]=row['exact_conditional_jam_value']
        if not math.isfinite(values[3]):raise ValueError('Finite exact initial jam required')
        expected=math.fsum(p*v for p,v in zip(probability,values))
        advantages=[v-expected for v in values]
        if abs(math.fsum(p*v for p,v in zip(probability,advantages)))>1e-9:
            raise ValueError('Integrated advantages must recenter')
        derived.append(dict(deal=i,query=qi,hand_class=row['hand_class'],
            action_values=values,derived_root_value=expected,advantages=advantages))
    return dict(format=1,method=METHOD,iteration=sampled_audit['iteration'],
        identity=dict(sampled_audit['identity'],root_estimator=METHOD),
        queries_sha256=digest(queries),policies_sha256=digest(policies),
        source_sampled_audit_sha256=digest(sampled_audit),profiles_sha256=digest(profiles),
        full_evaluation_sha256=digest(full),bb_root_corrections=derived,
        scope='Root-only conditional action integration; private cards and boards still sampled. Existing sampled reservoir updates remain unchanged.')
