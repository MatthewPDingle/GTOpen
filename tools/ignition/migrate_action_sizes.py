"""Conservatively merge measured sizing into a saved SeatProfile.

Pure function: no API calls, input mutation, hand-policy replacement, or file
writes. Existing custom sizing is retained unless its source can be verified.
Source dataset replacement additionally requires semantic equality of every
hand policy and entry-rate/coverage field, ignoring policy-array reindexing.
"""
from copy import deepcopy
import math

SIZE_KEYS = ('raise_sizes', 'raise_multiples')
HAND_KEYS = ('call', 'raise', 'jam')

def _policy_map(profile):
    result = {}
    def add(key, policy):
        if policy is None:
            return
        if not isinstance(policy, dict):
            raise ValueError(f'Invalid policy at {key}')
        if key in result:
            raise ValueError(f'Duplicate policy context {key}')
        result[key] = policy
    for i, policy in enumerate(profile.get('buckets') or []):
        add(f'buckets/{i}', policy)
    for threshold, policy in profile.get('vs_raise_bands') or []:
        add(f'vs_raise_bands/{threshold:g}', policy)
    add('limp_defense', profile.get('limp_defense'))
    response = profile.get('response') or {}
    for field in ('cold_reraise', 'limp_unopened'):
        add(f'response/{field}', response.get(field))
    for context in response.get('limp_contexts') or []:
        key = f"response/limp_contexts/{context['limpers']}/{bool(context['free_check'])}"
        add(key, context.get('policy'))
    return result

def _hands(policy):
    result = []
    for key in HAND_KEYS:
        vector = policy.get(key)
        if not isinstance(vector, list) or len(vector) != 169:
            raise ValueError(f'{key} must contain 169 probabilities')
        if any(not isinstance(x, (int,float)) or not math.isfinite(x) or x < 0 for x in vector):
            raise ValueError(f'Invalid {key} probabilities')
        result.append(vector)
    return result

def _sizes(policy):
    result = []
    for key in SIZE_KEYS:
        values = policy.get(key) or []
        if not isinstance(values, list):
            raise ValueError(f'{key} must be a list')
        for pair in values:
            if not isinstance(pair, (list,tuple)) or len(pair) != 2 or any(
                not isinstance(x, (int,float)) or not math.isfinite(x) or x <= 0 for x in pair):
                raise ValueError(f'Invalid {key} value')
        if not math.isfinite(sum(pair[1] for pair in values)):
            raise ValueError(f'Invalid {key} total')
        result.append(values)
    if all(result):
        raise ValueError('Absolute sizes and multipliers are mutually exclusive')
    return result

def _source_dataset(profile):
    return ((profile.get('response') or {}).get('source_stats') or {}).get('dataset')

def _dataset_semantics(dataset):
    if not isinstance(dataset, dict):
        raise ValueError('Missing source dataset')
    policies = dataset.get('response_policies') or []
    result = {}
    for row in dataset.get('rows') or []:
        key = (row['players'], row['role'])
        if key in result:
            raise ValueError('Duplicate dataset position')
        metadata = {k:v for k,v in row.items() if k not in ('opening','responses')}
        mapped = {}
        if row.get('opening') is not None:
            mapped['opening'] = row['opening']
        for name,index in (row.get('responses') or {}).items():
            if not isinstance(index,int) or not 0 <= index < len(policies):
                raise ValueError('Invalid dataset response reference')
            mapped[name] = policies[index]
        normalized = {}
        for name,policy in mapped.items():
            _hands(policy)
            # Preserve all non-sizing policy fields, including fallback rule.
            normalized[name] = {k:v for k,v in policy.items() if k not in SIZE_KEYS}
        result[key] = (metadata,normalized)
    if not result:
        raise ValueError('Empty source dataset')
    header = {k:v for k,v in dataset.items() if k not in
              ('rows','response_policies','response_notes','scope','contextual_reraise')}
    return header,result

def _verified_old_opening(policy, old_dataset):
    if not isinstance(old_dataset,dict):
        return False
    for row in old_dataset.get('rows') or []:
        source = row.get('opening')
        if source is not None and _hands(source) == _hands(policy) and _sizes(source) == _sizes(policy):
            return True
    return False

def migrate_profile(old_profile, generated_profile):
    """Return (deep-copied upgraded SeatProfile, explicit migration summary).

    Empty old size metadata may be upgraded when all 169 hand action vectors
    match exactly. A nonempty custom mix is never replaced, except an unchanged
    source-verified observed opening mix. Fallback min/max/jam stays unchanged.
    Dataset metadata is replaced only if every existing active policy passed
    and the full source datasets are semantically identical except sizing,
    source notes/scope and contextual version (the OLD version is preserved).
    """
    if not isinstance(old_profile,dict) or not isinstance(generated_profile,dict):
        raise ValueError('Both profiles must be objects')
    upgraded = deepcopy(old_profile)
    old_map = _policy_map(old_profile)
    new_map = _policy_map(generated_profile)
    target_map = _policy_map(upgraded)
    summary = {'updated':[], 'unchanged':[], 'skipped':[], 'new_only':sorted(set(new_map)-set(old_map)),
               'dataset_updated':False, 'dataset_note':''}
    old_dataset = _source_dataset(old_profile)
    new_dataset = _source_dataset(generated_profile)
    for path, old in old_map.items():
        new = new_map.get(path)
        reason = None
        if new is None:
            reason = 'No matching generated policy; existing policy retained.'
        elif _hands(old) != _hands(new):
            reason = 'Hand vectors differ (painted or otherwise changed); retained exactly.'
        else:
            old_sizes,new_sizes = _sizes(old),_sizes(new)
            if old_sizes == new_sizes:
                summary['unchanged'].append(path)
                continue
            if old.get('raise_size','max') == 'jam':
                reason = 'Explicit jam fallback retained; ordinary size mix not installed.'
            elif any(old_sizes) and not (path == 'buckets/0' and _verified_old_opening(old,old_dataset)):
                reason = 'Existing nonempty size mix is not source-verified opening sizing; retained as custom.'
        if reason:
            summary['skipped'].append({'path':path,'reason':reason})
            continue
        target = target_map[path]
        for field in SIZE_KEYS:
            if field in new:
                target[field] = deepcopy(new[field])
            else:
                target.pop(field,None)
        summary['updated'].append(path)
    if summary['skipped'] or summary['new_only']:
        summary['dataset_note'] = 'Source dataset retained because some profile policies were skipped or unmatched.'
    elif old_dataset is None or new_dataset is None:
        summary['dataset_note'] = 'Source dataset retained: both source datasets are required.'
    elif _dataset_semantics(old_dataset) != _dataset_semantics(new_dataset):
        summary['dataset_note'] = 'Source dataset retained: hand policies, entry rates or coverage differ.'
    else:
        # Any preexisting measured mix inside the source dataset must also be
        # unchanged; this prevents replacing manually customized source mixes.
        old_rows = {(r['players'],r['role']):r for r in old_dataset['rows']}
        new_rows = {(r['players'],r['role']):r for r in new_dataset['rows']}
        custom = False
        for key,row in old_rows.items():
            pairs = []
            if row.get('opening') is not None:
                pairs.append((row['opening'],new_rows[key]['opening']))
            for context,index in (row.get('responses') or {}).items():
                pairs.append((old_dataset['response_policies'][index],
                    new_dataset['response_policies'][new_rows[key]['responses'][context]]))
            if any(any(_sizes(a)) and _sizes(a) != _sizes(b) for a,b in pairs):
                custom = True
                break
        if custom:
            summary['dataset_note'] = 'Source dataset retained: a nonempty stored size mix differs.'
        else:
            replacement = deepcopy(new_dataset)
            if 'contextual_reraise' in old_dataset:
                replacement['contextual_reraise'] = deepcopy(old_dataset['contextual_reraise'])
            else:
                replacement.pop('contextual_reraise',None)
            upgraded['response']['source_stats']['dataset'] = replacement
            summary['dataset_updated'] = replacement != old_dataset
            summary['dataset_note'] = 'All logical dataset hand policies and rates match; old contextual version preserved.'
    # Pure contract: only known sizing fields and guarded source dataset change.
    a,b = deepcopy(old_profile),deepcopy(upgraded)
    for profile in (a,b):
        for policy in _policy_map(profile).values():
            for key in SIZE_KEYS:
                policy.pop(key,None)
        response = profile.get('response') or {}
        stats = response.get('source_stats')
        if isinstance(stats,dict):
            stats.pop('dataset',None)
    if a != b:
        raise RuntimeError('Migration attempted to change non-sizing profile content')
    return upgraded,summary
