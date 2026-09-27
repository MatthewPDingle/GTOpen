"""Append-only recovery points for one fixed physical-deal comparison.

Publish only after archive workers finish. A restart reads the longest committed
prefix; uncommitted attempts remain evidence but never enter the statistic.
"""
import json
import os
from pathlib import Path
import re
import uuid
from owned_columnar_evaluation_archive_v1 import unlinked, durable, encoded, digest, read_bounded, MAX_HEADER
from sampled_physical_deals_v1 import PhysicalDeals
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from evaluation_resume_routing_20260927 import restore_accumulator

PATTERN = re.compile(r'checkpoint-([0-9]{6})-([0-9a-f]{64})\.json')
HEX = re.compile(r'[0-9a-f]{64}')


def require(value, reason):
    if not value:
        raise ValueError(reason)


def root_path(root):
    root = unlinked(root)
    require(root.parent == Path('S:/GTOpen-research') and root.name.startswith('weighted-complete-'),
            'Explicit new weighted-comparison root required')
    require(root.is_dir(), 'Existing study root required')
    return root


def series_state(comparison):
    return [dict(series=s.series, count=s.count, mean=s.mean, m2=s.m2) for s in comparison.series]


def validate(value, *, root, registration_sha256, bank_identities_sha256, context_source,
             total_deals, guard, verify_archives):
    root = root_path(root)
    require(value['format'] == 1 and value['registration_sha256'] == registration_sha256
            and value['bank_identities_sha256'] == bank_identities_sha256, 'Changed study identity')
    require(HEX.fullmatch(registration_sha256) and HEX.fullmatch(bank_identities_sha256), 'Invalid identity digest')
    require(digest(read_bounded(root / 'bank-identities.json', 64 * 1024**2)) == bank_identities_sha256,
            'Bank identities changed')
    count = value['completed_deals']
    require(type(total_deals) is int and total_deals > 0 and total_deals % 32 == 0
            and value['total_deals'] == total_deals and type(count) is int
            and 0 <= count <= total_deals and count % 32 == 0, 'Invalid fixed deal budget or prefix')
    context = json.loads(context_source)
    comparison = CompletePolicyComparison(stack=context['config']['stack'], dead_money=context['dead_money'], deals=total_deals)
    restore_accumulator(comparison, value['series'], count)
    sampler = PhysicalDeals.restore(value['sampler'], context_source)
    require(sampler.mode == 'full_deck' and sampler.draws == count, 'Sampler count or chance law differs')
    routes = value['routes']
    require(set(routes) == {f'test-{i:06d}' for i in range(0, count, 32)}, 'Missing, duplicated or non-prefix batches')
    for name, route in routes.items():
        guard()
        require(set(route) == {'attempt', 'owner_sha256', 'manifest_sha256', 'summary_sha256'}, 'Unknown archive routing fields')
        require(re.fullmatch(r'attempt-[0-9a-f]{32}', route['attempt']), 'Invalid attempt directory')
        store = unlinked(root / route['attempt'])
        require(store.parent == root, 'Archive routing escapes study')
        owner = read_bounded(store / 'archive-owner.json', 4096)
        require(digest(owner) == route['owner_sha256'] and json.loads(owner)['root'] == str(store), 'Archive owner changed')
        manifest_raw = read_bounded(store / (name + '.manifest.json'), MAX_HEADER)
        require(digest(manifest_raw) == route['manifest_sha256'], 'Manifest changed')
        manifest = json.loads(manifest_raw)
        members = [m for m in manifest['members'] if m['name'] == 'summary.json']
        require(len(members) == 1 and members[0]['raw_sha256'] == route['summary_sha256'], 'Summary identity changed')
        receipt = json.loads(read_bounded(store / '.batch-work' / (name + '.receipt.json'), 4096))
        require(receipt == dict(name=name, owner_sha256=route['owner_sha256'], manifest_sha256=route['manifest_sha256']),
                'Durable publication receipt differs')
        packed = unlinked(store / (name + '.xz'))
        require(packed.stat().st_size == manifest['packed_bytes'], 'Archive size changed')
        if verify_archives:
            require(digest(read_bounded(packed, 128 * 1024**2)) == manifest['packed_sha256'], 'Archive content changed')
    return sampler, comparison


def committed(root):
    """Temporary files from an interrupted publication are never candidates."""
    root = root_path(root)
    found = []
    for path in root.glob('checkpoint-*.json'):
        match = PATTERN.fullmatch(path.name)
        require(match is not None, 'Unexpected committed checkpoint name')
        raw = read_bounded(path, 16 * 1024**2)
        require(digest(raw) == match[2], 'Checkpoint digest changed')
        value = json.loads(raw)
        require(value['completed_deals'] == int(match[1]), 'Checkpoint name/count differs')
        found.append((int(match[1]), path, value))
    found.sort(key=lambda row: row[0])
    require(len({n for n, _, _ in found}) == len(found), 'Conflicting committed prefix')
    return found


def publish(root, *, registration_sha256, bank_identities_sha256, context_source, sampler, comparison, routes, guard):
    root = root_path(root)
    value = dict(format=1, registration_sha256=registration_sha256, bank_identities_sha256=bank_identities_sha256,
                 completed_deals=sampler.draws, total_deals=comparison.plan.looks[-1], sampler=sampler.checkpoint(),
                 series=series_state(comparison), routes=routes)
    require(comparison.plan.looks == (value['total_deals'],) and comparison.plan.alpha == .05, 'Changed evaluation looks')
    validate(value, root=root, registration_sha256=registration_sha256,
             bank_identities_sha256=bank_identities_sha256, context_source=context_source,
             total_deals=value['total_deals'], guard=guard, verify_archives=False)
    earlier = committed(root)
    if earlier:
        _, _, old = earlier[-1]
        require(old['registration_sha256'] == registration_sha256 and old['bank_identities_sha256'] == bank_identities_sha256
                and old['total_deals'] == value['total_deals'], 'Changed checkpoint lineage')
        require(old['completed_deals'] < value['completed_deals'], 'Prefix must advance')
        require(all(routes.get(n) == r for n, r in old['routes'].items()), 'Previously committed routing changed')
    else:
        require(value['completed_deals'] == 0, 'Initial empty checkpoint required')
    raw = encoded(value)
    path = root / f"checkpoint-{sampler.draws:06d}-{digest(raw)}.json"
    temporary = root / ('.checkpoint-' + uuid.uuid4().hex + '.pending')
    require(not path.exists(), 'Preserve existing checkpoint')
    durable(temporary, raw)
    guard()
    os.replace(temporary, path)
    return dict(file=path.name, sha256=digest(raw), completed_deals=sampler.draws)


def restore_latest(root, *, registration_sha256, bank_identities_sha256, context_source, total_deals, seed, guard):
    rows = committed(root)
    require(bool(rows), 'No committed recovery point')
    count, path, value = rows[-1]
    for _, _, prior in rows:
        require(prior['registration_sha256'] == registration_sha256 and prior['bank_identities_sha256'] == bank_identities_sha256
                and prior['total_deals'] == total_deals, 'Recovery history changed')
        require(all(value['routes'].get(n) == r for n, r in prior['routes'].items()), 'Committed history conflicts')
    sampler, comparison = validate(value, root=root, registration_sha256=registration_sha256,
        bank_identities_sha256=bank_identities_sha256, context_source=context_source,
        total_deals=total_deals, guard=guard, verify_archives=True)
    replay = PhysicalDeals(context_source, mode='full_deck', seed=seed)
    for _ in range(0, count, 32):
        guard()
        replay.sample(32)
    require(replay.checkpoint() == sampler.checkpoint(), 'Committed chance stream differs from registered seed')
    return sampler, comparison, value['routes'], dict(file=path.name, sha256=digest(path.read_bytes()), completed_deals=count)
