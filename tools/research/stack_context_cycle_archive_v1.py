"""Lossless cycle retention inside explicitly owned NEW research scratch.

The source plan and complete archive index are durable before any raw duplicate
is retired. Interrupted retirement can finish without regenerating poker data.
Existing legacy stores are never accepted as an owned source.
"""
import hashlib
import json
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
from owned_research_archive_v1 import owner, unpack, MAX_RAW
from owned_columnar_evaluation_archive_v1 import unlinked, durable, encoded
from parallel_owned_archive_v1 import pack_many

BUNDLE_BYTES = 256 * 1024**2


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def paths(source, destination, root, token):
    root = owner(root, token)
    source, destination = unlinked(source), unlinked(destination)
    if (source == root or destination == root or not source.is_relative_to(root)
            or not destination.is_relative_to(root) or destination.is_relative_to(source)
            or source.is_relative_to(destination)):
        raise ValueError('Separate source/archive descendants of the new owner required')
    return source, destination, root


def make_plan(source, destination, *, root, token, guard):
    source, destination, root = paths(source, destination, root, token)
    if destination.exists():
        raise ValueError('New archive destination required')
    files = sorted(p for p in source.rglob('*') if p.is_file())
    if not files:
        raise ValueError('Nonempty completed cycle required')
    members = []; groups = []; current = []; size = 0; parent = None
    for path in files:
        guard(); unlinked(path)
        if path.suffix not in ('.json', '.npz') or path.stat().st_size > MAX_RAW:
            raise ValueError('Unsupported or oversized cycle member')
        record = dict(path=path.relative_to(source).as_posix(), bytes=path.stat().st_size, sha256=sha(path))
        if current and (path.parent != parent or size + record['bytes'] > BUNDLE_BYTES):
            groups.append(current); current = []; size = 0
        current.append(record); members.append(record); size += record['bytes']; parent = path.parent
    if current:
        groups.append(current)
    destination.mkdir()
    jobs = []
    for index, group in enumerate(groups):
        jobs.append(dict(source=str(source / Path(group[0]['path']).parent),
                         destination=str(destination / f'bundle-{index:05d}.xz'),
                         names=[Path(row['path']).name for row in group], members=group))
    plan = dict(format=1, source=str(source), destination=str(destination), owner=str(root),
                members=members, jobs=jobs, raw_bytes=sum(row['bytes'] for row in members))
    durable(destination / 'plan.json', encoded(plan))
    return plan


def verify_index(destination, *, root, token, guard, workers=4):
    destination = unlinked(destination); owner(root, token)
    plan, index = read(destination / 'plan.json'), read(destination / 'index.json')
    source, destination, root = paths(plan['source'], destination, root, token)
    if (index['plan_sha256'] != sha(destination / 'plan.json') or index['format'] != 1
            or plan['destination'] != str(destination) or plan['owner'] != str(root)
            or len(index['bundles']) != len(plan['jobs'])):
        raise ValueError('Cycle archive binding differs')
    mutex = threading.Lock()
    def checked_guard():
        with mutex:
            guard()
    def check(pair):
        job, record = pair; dest = Path(job['destination'])
        if dest.parent != destination or dest.name != record['archive']:
            raise ValueError('Archive path differs')
        manifest_path = dest.with_suffix('.xz.json')
        if sha(manifest_path) != record['manifest_sha256']:
            raise ValueError('Archive manifest differs')
        manifest = read(manifest_path); restored = unpack(dest, manifest, guard=checked_guard)
        expected = {Path(row['path']).name: row for row in job['members']}
        if set(restored) != set(expected) or len(expected) != len(job['members']):
            raise ValueError('Missing/duplicate original member')
        for name, data in restored.items():
            row = expected[name]
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('Original cycle bytes differ')
        return job['members']
    with ThreadPoolExecutor(max_workers=workers) as pool:
        members = [row for group in pool.map(check, zip(plan['jobs'], index['bundles'])) for row in group]
    if members != plan['members'] or len({row['path'] for row in members}) != len(members):
        raise ValueError('Incomplete archive coverage')
    return plan, index


def finish_retirement(destination, *, root, token, guard, workers=4, on_retired=lambda count: None):
    # Authenticate every archive before removing ANY remaining raw duplicate.
    plan, index = verify_index(destination, root=root, token=token, guard=guard, workers=workers)
    source, destination, root = paths(plan['source'], destination, root, token)
    allowed = {row['path']: row for row in plan['members']}
    remaining = sorted(p for p in source.rglob('*') if p.is_file())
    targets = []
    for path in remaining:
        guard(); unlinked(path)
        key = path.relative_to(source).as_posix()
        if key not in allowed or path.stat().st_size != allowed[key]['bytes'] or sha(path) != allowed[key]['sha256']:
            raise ValueError('Changed or unregistered raw cycle file')
        targets.append(path)
    for count, path in enumerate(targets, 1):
        guard(); unlinked(path)
        # Recheck immediately at the nonrecursive removal boundary.
        if not path.is_relative_to(root) or sha(path) != allowed[path.relative_to(source).as_posix()]['sha256']:
            raise ValueError('Raw duplicate changed before retirement')
        path.unlink()
        on_retired(count)
    complete = dict(format=1, index_sha256=sha(destination / 'index.json'), raw_files_remaining=0,
                    original_files=len(allowed), original_bytes=plan['raw_bytes'])
    marker = destination / 'retired.json'
    if marker.exists():
        if read(marker) != complete:
            raise ValueError('Changed retirement marker')
    else:
        durable(marker, encoded(complete))
    return dict(**complete, packed_bytes=index['packed_bytes'])


def archive_cycle(source, destination, *, root, token, guard, workers=4, retire=True):
    plan = make_plan(source, destination, root=root, token=token, guard=guard)
    pending = list(enumerate(plan['jobs'])); records = {}
    while pending:
        selected = []; sources = set(); later = []
        for item in pending:
            index, job = item
            if len(selected) < workers and job['source'] not in sources:
                selected.append(item); sources.add(job['source'])
            else:
                later.append(item)
        pending = later
        jobs = [{key: job[key] for key in ('source', 'destination', 'names')} for _, job in selected]
        manifests = pack_many(jobs, root=root, token=token, guard=guard, workers=workers)
        for (index, job), manifest in zip(selected, manifests):
            dest = Path(job['destination'])
            records[index] = dict(archive=dest.name, manifest_sha256=sha(dest.with_suffix('.xz.json')),
                                  packed_bytes=manifest['packed_bytes'])
    ordered = [records[i] for i in range(len(plan['jobs']))]
    index = dict(format=1, plan_sha256=sha(Path(destination) / 'plan.json'), bundles=ordered,
                 packed_bytes=sum(row['packed_bytes'] for row in ordered))
    durable(Path(destination) / 'index.json', encoded(index))
    if retire:
        return finish_retirement(destination, root=root, token=token, guard=guard, workers=workers)
    verify_index(destination, root=root, token=token, guard=guard, workers=workers)
    return index
