"""Explicit format-3 adapter for verified conditional preflop all-in labels.

Uses the existing reservoir layout and per-visit sampling, with new transport
validation. It never relabels a format-3 document as the old format.
"""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from sampled_physical_reservoir_v1 import checked_row

ESTIMATOR='conditional-preflop-allin-v1'
PERMUTATIONS=tuple(itertools.permutations(range(4)))
BOARDS=1712304


def canonical(hole):
    if len(hole)!=4 or len(set(hole))!=4 or any(type(c) is not int or not 0<=c<52 for c in hole):
        raise ValueError('Four distinct physical private cards required')
    return min(tuple(sorted(4*(c//4)+p[c%4] for c in hole[:2])+
                     sorted(4*(c//4)+p[c%4] for c in hole[2:])) for p in PERMUTATIONS)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class AllinCache:
    def __init__(self,path,expected_sha256):
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected_sha256:
            raise ValueError('Exact cache hash mismatch')
        data=json.loads(raw)
        if set(data)!={'format','player_roles_fixed','rows'} or data['format']!=1 or data['player_roles_fixed'] is not True:
            raise ValueError('Unknown exact cache format')
        self.sha256=expected_sha256;self.rows={}
        for row in data['rows']:
            if set(row)!={'private_cards','wins','ties','losses','boards'}:
                raise ValueError('Unknown exact count field')
            key=canonical(row['private_cards'])
            if list(key)!=row['private_cards'] or key in self.rows:
                raise ValueError('Cache keys must be unique and canonical without swapping players')
            if any(type(row[k]) is not int or row[k]<0 for k in ('wins','ties','losses','boards')):
                raise ValueError('Nonnegative integer exact counts required')
            if row['boards']!=BOARDS or sum(row[k] for k in ('wins','ties','losses'))!=BOARDS:
                raise ValueError('Incomplete exact board counts')
            self.rows[key]=dict(row)
        if not self.rows:raise ValueError('Empty exact cache')

    @classmethod
    def from_review(cls,path):
        review=json.loads(Path(path).read_text())
        if review.get('passed') is not True or review.get('source_training_deals')!=39936 or review.get('unique_keys_reconstructed')!=23891:
            raise ValueError('Complete training-cache review required')
        for p,h in review['inputs'].items():
            if sha(p)!=h:raise ValueError('Changed cache review input')
        cache=cls(review['cache_artifact'],review['cache_sha256'])
        if len(cache.rows)!=review['unique_keys_reconstructed']:
            raise ValueError('Reviewed cache count differs')
        return cache

    def labels(self,deals):
        result=[]
        if not isinstance(deals,list) or not deals:raise ValueError('Nonempty physical batch required')
        for d in deals:
            if len(d)!=9 or len(set(d))!=9 or any(type(c) is not int or not 0<=c<52 for c in d):
                raise ValueError('Nine distinct physical cards required')
            key=canonical(d[:4])
            if key not in self.rows:raise ValueError('Private pair missing from exact cache; no fallback')
            result.append(dict(self.rows[key],private_cards=list(d[:4])))
        return result

    def batch(self,old):
        if old.get('format')!=2 or any(k in old for k in ('allin_counts','terminal_estimator','allin_cache_sha256')):
            raise ValueError('Unlabelled format-2 source deal batch required')
        return dict(old,format=3,terminal_estimator=ESTIMATOR,allin_cache_sha256=self.sha256,
                    allin_counts=self.labels(old['deals']))

    def check_batch(self,batch):
        if batch.get('format')!=3 or batch.get('terminal_estimator')!=ESTIMATOR or batch.get('allin_cache_sha256')!=self.sha256:
            raise ValueError('Wrong estimator or cache identity')
        if batch.get('allin_counts')!=self.labels(batch['deals']):
            raise ValueError('Batch labels do not match the verified physical-pair cache')


def policy_document(queries,probabilities):
    if queries.get('format')!=3 or queries.get('terminal_estimator')!=ESTIMATOR:
        raise ValueError('Conditional-all-in query format required')
    if not isinstance(queries.get('context_source'),str) or not isinstance(queries.get('batch_source'),str):
        raise ValueError('Original context and batch source identities required')
    batch=json.loads(queries['batch_source'])
    if batch.get('format')!=3 or batch.get('terminal_estimator')!=ESTIMATOR:
        raise ValueError('Wrong query batch estimator')
    p=np.asarray(probabilities,dtype=float)
    if p.shape!=(len(queries['observations']),4) or not np.isfinite(p).all() or np.any(p<0):
        raise ValueError('Invalid probabilities')
    for o,row in zip(queries['observations'],p):
        n=o['n']
        if type(n) is not int or n not in (2,3,4) or np.any(row[n:]) or abs(row.sum()-1)>1e-12:
            raise ValueError('Illegal or unnormalized policy')
    return dict(format=3,terminal_estimator=ESTIMATOR,context_source=queries['context_source'],
        batch_source=queries['batch_source'],policies=[dict(hi=o['hi'],lo=o['lo'],actor=o['actor'],n=o['n'],
        probabilities=list(map(float,row))) for o,row in zip(queries['observations'],p)])


def ingest(queries, updates, reservoirs, iteration, cache):
    """Validate a whole transport before adding positive-tag advantage visits.

    Negative tags are opponent policy observations, not advantage training data.
    Average strategy is represented separately by the bank of actually played nets.
    No importance/reach multiplier is applied: the traversal already sampled it.
    """
    if type(iteration) is not int or not 1 <= iteration < 2**64:
        raise ValueError('Positive iteration metadata required')
    if (queries['format'] != 3 or updates['format'] != 3
            or queries.get('terminal_estimator') != ESTIMATOR or updates.get('terminal_estimator') != ESTIMATOR
            or updates['policies_frozen_across_updater_passes'] is not True):
        raise ValueError('Unsupported or unfrozen conditional-all-in traversal batch')
    batch = json.loads(queries['batch_source'])
    cache.check_batch(batch)
    if (updates.get('verified_query_lookup_traversals') != 2*len(batch['deals'])
            or updates.get('maximum_query_lookup_error') != 0
            or updates.get('verified_cashflow_traversals') != 2*len(batch['deals'])
            or not isinstance(updates.get('maximum_cashflow_error'), (int,float))
            or not 0 <= updates['maximum_cashflow_error'] < 1e-9):
        raise ValueError('Missing conditional-all-in reference verification')
    if updates['batch_id'] != batch['batch_id'] or updates['observations'] != len(queries['observations']):
        raise ValueError('Traversal batch identity mismatch')
    digest = hashlib.sha256(queries['context_source'].encode('utf-8')).hexdigest()
    if len(reservoirs) != 2 or any(r.player != p or r.context_sha256 != digest for p, r in enumerate(reservoirs)):
        raise ValueError('Reservoir game or player mismatch')
    counts = [0, 0]
    for index, updater, tag, values in updates['records']:
        if (type(index) is not int or not 0 <= index < len(queries['observations'])
                or type(updater) is not int or updater not in (0, 1)
                or type(tag) is not int or abs(tag) not in (2, 3, 4)):
            raise ValueError('Invalid traversal record')
        o = queries['observations'][index]
        _, _, n, v = checked_row(o, values)
        if abs(tag) != n or o['actor'] != (updater if tag > 0 else 1-updater):
            raise ValueError('Record actor or legal menu mismatch')
        if tag < 0 and (np.any(v < 0) or abs(v.sum()-1) > 1e-12):
            raise ValueError('Invalid opponent-policy record')
        if tag > 0:
            counts[updater] += 1
    if any(r.seen+c >= 2**63 for r, c in zip(reservoirs, counts)):
        raise OverflowError('Visit counter exhausted')
    for index, updater, tag, values in updates['records']:
        if tag > 0:
            reservoirs[updater]._insert(checked_row(queries['observations'][index], values), iteration)
    return counts
