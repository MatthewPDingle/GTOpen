"""Fixed retained deals and batch-independent comparison of visible policy rows."""
import hashlib
import json
from pathlib import Path
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from owned_columnar_evaluation_archive_v1 import restore


def retained_inputs():
    registration = OUT / 'native-query-snapshot-control-v1-registration.json'
    result_path = OUT / 'native-query-snapshot-control-v1-result.json'
    reg, result = read(registration), read(result_path)
    assert result['passed'] and result['registration_sha256'] == sha(registration)
    for path, digest in reg['inputs'].items(): assert sha(path) == digest, path
    checkpoint = next(Path(p) for p in reg['inputs'] if Path(p).name.startswith('checkpoint-'))
    paths = [registration, result_path, checkpoint]
    batches, queries = [], []
    for name in ('test-000000', 'test-000032'):
        route = read(checkpoint)['routes'][name]; folder = checkpoint.parent / route['attempt']
        manifest_path = folder / (name + '.manifest.json'); archive_path = folder / (name + '.xz')
        assert sha(manifest_path) == route['manifest_sha256']
        members = restore(archive_path, read(manifest_path), guard=lambda: None)
        batch, query = json.loads(members['query-batch.json']), json.loads(members['queries.json'])
        assert len(batch['deals']) == 32 and batch['format'] == 2 and batch['seed'] == 0
        assert query['batch_source'].encode() == members['query-batch.json']
        batches.append(batch); queries.append(query); paths.extend((manifest_path, archive_path))
    assert queries[0]['context_source'] == queries[1]['context_source']
    return batches, queries, paths


def joined_batch(batches):
    if len(batches) != 2 or any(len(b['deals']) != 32 or b['format'] != 2 or b['seed'] != 0 for b in batches):
        raise ValueError('Exactly two retained 32-deal batches required')
    if batches[0]['query_limit'] != batches[1]['query_limit']:
        raise ValueError('Query limits differ')
    return dict(format=2, batch_id='weighted-gpu-throughput-retained-64-v1', seed=0,
                query_limit=batches[0]['query_limit'], deals=batches[0]['deals'] + batches[1]['deals'])


def row_identities(query):
    obs = query['observations']; keys = [(int(o['hi']), int(o['lo'])) for o in obs]
    if not keys or len(set(keys)) != len(keys): raise ValueError('Missing or duplicate observation keys')
    signatures = []
    for o in obs:
        history = []
        for index, action, n in o['own_history']:
            if (type(index) is not int or not 0 <= index < len(obs)
                    or type(action) is not int or not 0 <= action < n
                    or n != obs[index]['n'] or o['actor'] != obs[index]['actor']):
                raise ValueError('Invalid own-history link')
            history.append([*keys[index], action, n])
        value = dict(o, own_history=history)
        signatures.append(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False))
    return keys, signatures


def pack(captures):
    """Merge one/two batches, preserving every bank's policy and own reach.

Rows shared across batches must agree too; history links are compared using
native keys rather than batch-local array indices. No outcome selection.
"""
    rows = {}; duplicate_policy = duplicate_reach = 0.; context = None
    for capture in captures:
        query = capture['queries']; keys, signatures = row_identities(query)
        if context is None: context = query['context_source']
        if query['context_source'] != context: raise ValueError('Context changed')
        p, reach = np.asarray(capture['policies']), np.asarray(capture['reaches'])
        if p.shape != (4, len(keys), 4) or reach.shape != (4, len(keys)):
            raise ValueError('Four complete bank captures required')
        if not np.isfinite(p).all() or not np.isfinite(reach).all(): raise ValueError('Nonfinite capture')
        for i, (key, signature) in enumerate(zip(keys, signatures)):
            if key in rows:
                old = rows[key]
                if old[0] != signature: raise ValueError('Shared observation changed')
                duplicate_policy = max(duplicate_policy, float(np.max(abs(old[1] - p[:, i]))))
                duplicate_reach = max(duplicate_reach, float(np.max(abs(old[2] - reach[:, i]))))
            else:
                rows[key] = (signature, p[:, i].copy(), reach[:, i].copy())
    if duplicate_policy > 1e-10 or duplicate_reach > 1e-10:
        raise ValueError('Repeated observation changed policy or reach')
    keys = sorted(rows)
    identity = hashlib.sha256(json.dumps([context, [(k, rows[k][0]) for k in keys]],
                              separators=(',', ':')).encode()).hexdigest()
    return dict(keys=keys, observation_identity_sha256=identity,
                policies=np.stack([rows[k][1] for k in keys], axis=1),
                reaches=np.stack([rows[k][2] for k in keys], axis=1),
                duplicate_policy_error=duplicate_policy, duplicate_reach_error=duplicate_reach)


def compare(reference, candidate):
    if (reference['keys'] != candidate['keys']
            or reference['observation_identity_sha256'] != candidate['observation_identity_sha256']):
        raise ValueError('Observation/history identity changed with batching')
    policy = float(np.max(abs(reference['policies'] - candidate['policies'])))
    reach = float(np.max(abs(reference['reaches'] - candidate['reaches'])))
    if policy > 1e-10 or reach > 1e-10: raise ValueError('Policy or own-action reach changed')
    return dict(unique_observations=len(reference['keys']), maximum_policy_error=policy,
                maximum_reach_error=reach)
