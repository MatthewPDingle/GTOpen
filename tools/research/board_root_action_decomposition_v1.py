"""Root-only action values from authenticated, complete averaged policy archives.

No fitting, fresh deals, policy selection, or changes to the native evaluator.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import time
from owned_columnar_evaluation_archive_v1 import restore, read_bounded, unlinked, ARTIFACTS

ACTIONS = ('fold', 'call', 'raise', 'jam')
NAMES = tuple(f'{seed}:{pair}' for seed in ('first', 'replication') for pair in
    ('oldBB-oldBTN', 'oldBB-newBTN', 'newBB-oldBTN', 'newBB-newBTN'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, separators=(',', ':'), allow_nan=False).encode()


def publish(path, raw):
    require(len(raw) < 128 * 1024**2, 'Bounded control artifact required')
    with Path(path).open('xb') as stream:
        stream.write(raw)


def restore_batch(store, name, route, guard):
    import re
    require(re.fullmatch(r'test-[0-9]{6}', name) is not None, 'Invalid batch name')
    require(set(route) == {'attempt', 'owner_sha256', 'manifest_sha256', 'summary_sha256'}
        and re.fullmatch(r'attempt-[0-9a-f]{32}', route['attempt']) is not None, 'Invalid route')
    store = unlinked(store)
    folder = unlinked(store / route['attempt'])
    require(folder.parent == store, 'Escaping archive route')
    owner = read_bounded(folder / 'archive-owner.json', 4096)
    require(digest(owner) == route['owner_sha256'] and json.loads(owner)['root'] == str(folder),
        'Changed archive owner')
    manifest_raw = read_bounded(folder / (name + '.manifest.json'), 1024**2)
    require(digest(manifest_raw) == route['manifest_sha256'], 'Changed archive manifest')
    receipt = json.loads(read_bounded(folder / '.batch-work' / (name + '.receipt.json'), 4096))
    require(receipt == dict(name=name, owner_sha256=route['owner_sha256'],
        manifest_sha256=route['manifest_sha256']), 'Changed publication receipt')
    members = restore(folder / (name + '.xz'), json.loads(manifest_raw), guard=guard)
    require(set(members) == ARTIFACTS and digest(members['summary.json']) == route['summary_sha256'],
        'Changed archive membership or routed summary')
    summary = json.loads(members['summary.json'])
    require(all(digest(members[n]) == h for n, h in summary['artifacts'].items()),
        'Changed original artifact')
    return members


def root_key(deal):
    require(len(deal) == len(set(deal)) == 9 and all(type(c) is int and 0 <= c < 52 for c in deal),
        'Invalid physical deal')
    # Native observations canonicalize visible cards over all suit relabelings.
    # Hidden opponent cards and future public cards must not affect this key.
    choices = []
    for suits in itertools.permutations(range(4)):
        own = sorted(c//4*4+suits[c % 4] for c in deal[:2])
        cards = [*own, *([63] * 5)]
        choices.append(sum(c << (6*i) for i, c in enumerate(cards)))
    return ('1', str(min(choices)))


def hand_class(cards):
    a, b = cards
    low, high = sorted((a//4, b//4))
    return high*13+low if a % 4 == b % 4 or high == low else low*13+high


def validate_original(members, source):
    context = json.loads(source)
    root = context['nodes'][0]
    require(root['actor'] == 0 and root['kind'] == 0 and
        tuple(a['kind'] for a in root['actions']) == ACTIONS, 'Four-action BB root required')
    raw = json.loads(members['query-batch.json'])
    batch = json.loads(members['conditional-batch.json'])
    query = json.loads(members['queries.json'])
    original = json.loads(members['profiles.json'])
    require(raw['format'] == 2 and batch['format'] == 3 and len(raw['deals']) == 32
        and all(batch[k] == v for k, v in raw.items() if k != 'format'), 'Changed physical batch')
    require(query['context_source'] == original['context_source'] == source
        and query['batch_source'] == members['query-batch.json'].decode()
        and original['batch_source'] == members['conditional-batch.json'].decode()
        and original['format'] == 1, 'Changed exact context or batch source')
    require(tuple(p['name'] for p in original['profiles']) == NAMES, 'Changed original profile order')
    obs = query['observations']
    keys = [(o['hi'], o['lo']) for o in obs]
    require(len(keys) == len(set(keys)), 'Duplicate query identity')
    lookup = {key: i for i, key in enumerate(keys)}
    expected_roots = {root_key(d) for d in raw['deals']}
    actual_roots = {key for key in keys if key[0] == '1'}
    require(actual_roots == expected_roots, 'Root identities do not match the physical deals')
    root_indices = {lookup[k] for k in expected_roots}
    for i in root_indices:
        o = obs[i]
        require(o['actor'] == 0 and o['n'] == 4 and o['phase'] == 0 and o['own_history'] == [],
            'Illegal root actor, arity, phase or own history')
    for profile in original['profiles']:
        require(len(profile['policies']) == len(obs), 'Missing policy rows')
        for o, row in zip(obs, profile['policies'], strict=True):
            require(set(row) == {'hi', 'lo', 'actor', 'n', 'probabilities'}
                and all(row[k] == o[k] for k in ('hi', 'lo', 'actor', 'n')), 'Changed query identity')
            p, n = row['probabilities'], row['n']
            require(n in (2, 3, 4) and row['actor'] in (0, 1) and len(p) == 4
                and all(math.isfinite(x) and 0 <= x <= 1 for x in p)
                and all(x == 0 for x in p[n:]) and abs(math.fsum(p)-1) < 1e-12,
                'Illegal action probabilities')
    return original, root_indices, [lookup[root_key(d)] for d in raw['deals']], raw['deals']


def force_root(original, root_indices):
    profiles = []
    for profile in original['profiles']:
        for a, action in enumerate(ACTIONS):
            rows = [dict(row, probabilities=[float(i == a) for i in range(4)]) if r in root_indices
                else row for r, row in enumerate(profile['policies'])]
            profiles.append(dict(name=f"{profile['name']}:root-{action}", policies=rows))
    return dict(original, profiles=profiles)


def validate_forced(original, forced, root_indices):
    require(set(forced) == set(original) and all(forced[k] == original[k]
        for k in original if k != 'profiles'), 'Changed evaluator inputs')
    require(len(forced['profiles']) == 32, 'Exactly 32 forced profiles required')
    for p, baseline in enumerate(original['profiles']):
        for a, action in enumerate(ACTIONS):
            changed = forced['profiles'][p*4+a]
            require(set(changed) == {'name', 'policies'} and changed['name'] == f"{baseline['name']}:root-{action}"
                and len(changed['policies']) == len(baseline['policies']), 'Changed forced profile identity')
            for i, (row, old) in enumerate(zip(changed['policies'], baseline['policies'], strict=True)):
                if i in root_indices:
                    expected = dict(old, probabilities=[float(x == a) for x in range(4)])
                    require(row == expected, 'Illegal root change')
                else:
                    require(row == old, 'Changed non-root continuation')


def tamper_controls(original, roots):
    cases = []
    ri = min(roots)
    ni = next(i for i in range(len(original['profiles'][0]['policies'])) if i not in roots)
    for case in ('non_root_probability', 'root_actor', 'root_identity', 'batch_source', 'root_mixture'):
        forced = force_root(original, roots)
        if case == 'batch_source':
            forced['batch_source'] += ' '
        else:
            index = ni if case == 'non_root_probability' else ri
            row = dict(forced['profiles'][0]['policies'][index])
            row['probabilities'] = list(row['probabilities'])
            forced['profiles'][0]['policies'][index] = row
            if case == 'root_actor': row['actor'] = 1
            elif case == 'root_identity': row['hi'] = '2'
            elif case == 'root_mixture': row['probabilities'] = [.5, .5, 0., 0.]
            else:
                p = row['probabilities']; k = max(range(row['n']), key=p.__getitem__)
                amount = min(.01, p[k]); p[k] -= amount; p[(k+1) % row['n']] += amount
        try:
            validate_forced(original, forced, roots)
        except ValueError:
            cases.append(case)
        else:
            raise AssertionError('Did not reject '+case)
    return cases


def check_native(document, names, count, dead):
    require(document['format'] == 2 and document['fixed_policy_evaluation_only']
        and not document['bounds_best_response_above']
        and document['terminal_estimator'] == 'conditional-preflop-allin-v1'
        and document['postflop_outcomes'] == 'sampled-board', 'Changed native result meaning')
    require(tuple(p['name'] for p in document['profiles']) == tuple(names), 'Changed native profile order')
    for field in ('maximum_conservation_error', 'maximum_forward_cashflow_error'):
        require(math.isfinite(document[field]) and 0 <= document[field] < 1e-10, field)
    for profile in document['profiles']:
        require(len(profile['deals']) == count, 'Missing native deals')
        for i, row in enumerate(profile['deals']):
            require(row['deal_index'] == i and len(row['values']) == 2
                and all(math.isfinite(v) for v in [*row['values'], row['expected_rake'], row['terminal_mass']])
                and row['expected_rake'] >= 0 and abs(row['terminal_mass']-1) < 1e-12
                and abs(math.fsum([*row['values'], row['expected_rake']])-dead) < 1e-10,
                'Invalid per-deal native accounting')


def compare(saved, replay, forced, original, deal_rows, deals, dead):
    check_native(saved, NAMES, len(deals), dead)
    check_native(replay, NAMES, len(deals), dead)
    names = [f'{name}:root-{action}' for name in NAMES for action in ACTIONS]
    check_native(forced, names, len(deals), dead)
    replay_error = mixture_error = 0.
    compact = []
    for p, name in enumerate(NAMES):
        result_rows = []
        for i, (old, repeated) in enumerate(zip(saved['profiles'][p]['deals'], replay['profiles'][p]['deals'], strict=True)):
            q = [forced['profiles'][p*4+a]['deals'][i] for a in range(4)]
            mix = original['profiles'][p]['policies'][deal_rows[i]]['probabilities']
            old_values = [*old['values'], old['expected_rake']]
            repeated_values = [*repeated['values'], repeated['expected_rake']]
            forced_values = [[*v['values'], v['expected_rake']] for v in q]
            replay_error = max(replay_error, max(abs(x-y) for x,y in zip(old_values, repeated_values)))
            mixture_error = max(mixture_error, max(abs(math.fsum(mix[a]*forced_values[a][k]
                for a in range(4))-old_values[k]) for k in range(3)))
            require(q[0]['values'] == [-1., dead+1.] and q[0]['expected_rake'] == 0., 'Fold baseline changed')
            result_rows.append(dict(deal_index=i, native_class_index=hand_class(deals[i][:2]),
                root_probabilities=mix, action_values=forced_values))
        compact.append(dict(name=name, deals=result_rows))
    require(replay_error < 1e-10 and mixture_error < 1e-10, 'Saved mixture decomposition failed')
    return dict(maximum_replay_error=replay_error, maximum_mixture_error=mixture_error,
        profiles=compact, columns=['BB_bb_per_entry', 'BTN_bb_per_entry', 'expected_rake_bb'])


def invoke(executable, context, batch, policies, output, guard):
    guard()
    began = time.monotonic()
    process = subprocess.Popen([str(p) for p in (executable, context, batch, policies, output)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        while True:
            try:
                stdout, stderr = process.communicate(timeout=1)
                break
            except subprocess.TimeoutExpired:
                guard()
                require(time.monotonic()-began < 120, 'Native batch deadline exceeded')
        require(process.returncode == 0, 'Native evaluation failed: '+stderr.decode(errors='replace')[-2000:])
    except BaseException:
        process.kill(); process.communicate()
        raise
    guard()
    return time.monotonic()-began
