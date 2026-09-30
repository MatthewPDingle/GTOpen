"""Complete missing archive bundles without rewriting any retained evidence.

The caller supplies immutable plan/source/bundle hashes from its interruption
audit. This is storage transport only: no sampling, fitting or raw retirement.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import threading
from stack_context_cycle_archive_v1 import paths, read, sha, verify_index
from owned_research_archive_v1 import pack, unpack, name
from owned_columnar_evaluation_archive_v1 import durable, encoded, unlinked


def require(ok, message):
    if not ok:
        raise ValueError(message)


def recover(destination, *, root, token, expected, guard, workers=4):
    require(type(workers) is int and 1 <= workers <= 4, 'Bounded workers required')
    destination = unlinked(destination)
    plan_path = destination/'plan.json'
    require(expected.get(str(plan_path)) == sha(plan_path), 'Unbound or changed plan')
    plan = read(plan_path)
    source, destination, root = paths(plan['source'], destination, root, token)
    require(plan['format'] == 1 and plan['destination'] == str(destination)
            and plan['owner'] == str(root), 'Plan identity differs')
    require(not (destination/'index.json').exists() and not (destination/'retired.json').exists(),
            'Recovery requires an unpublished archive')
    members = []; sources = []; outputs = []; complete = []; missing = []
    for i, job in enumerate(plan['jobs']):
        dest = unlinked(job['destination']); src = unlinked(job['source'])
        require(dest == destination/f'bundle-{i:05d}.xz' and src.is_relative_to(source),
                'Escaped or reordered archive job')
        require(job['names'] == [Path(r['path']).name for r in job['members']]
                and len(set(job['names'])) == len(job['names']) and job['names'], 'Duplicate or changed members')
        for key, row in zip(job['names'], job['members']):
            name(key); path = unlinked(src/key)
            require(path == unlinked(source/row['path']) and path.is_relative_to(source), 'Escaped member')
            require(row['sha256'] == expected.get(str(path)) and path.stat().st_size == row['bytes']
                    and sha(path) == row['sha256'], 'Changed or unbound source')
            guard(); sources.append(str(path)); members.append(row)
        outputs.append(str(dest)); manifest = dest.with_suffix('.xz.json')
        require(dest.exists() == manifest.exists(), 'Incomplete bundle pair requires separate review')
        if dest.exists():
            require(expected.get(str(dest)) == sha(dest) and expected.get(str(manifest)) == sha(manifest),
                    'Changed or unbound retained bundle')
            complete.append(i)
        else:
            require(str(dest) not in expected and str(manifest) not in expected, 'Missing retained bundle')
            missing.append(i)
    require(members == plan['members'] and len(sources) == len(set(sources))
            and len(outputs) == len(set(outputs)) and members, 'Incomplete/overlapping coverage')
    require(sum(r['bytes'] for r in members) == plan['raw_bytes'], 'Wrong raw-byte total')
    actual_sources = {str(p) for p in source.rglob('*') if p.is_file()}
    require(actual_sources == set(sources), 'Unplanned or missing raw files')
    allowed = {str(plan_path)} | {p for i in complete for p in
        (outputs[i], str(Path(outputs[i]).with_suffix('.xz.json')))}
    require({str(p) for p in destination.rglob('*') if p.is_file()} == allowed, 'Unplanned archive files')
    mutex = threading.Lock()
    def guarded():
        with mutex:
            guard()
    def record(i, *, create=False):
        job = plan['jobs'][i]; dest = Path(job['destination'])
        if create:
            pack(job['source'], job['names'], dest, root=root, token=token, guard=guarded)
        manifest = read(dest.with_suffix('.xz.json')); restored = unpack(dest, manifest, guard=guarded)
        require(set(restored) == set(job['names']), 'Changed bundle membership')
        for row in job['members']:
            data = restored[Path(row['path']).name]
            require(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'],
                    'Bundle does not reproduce planned raw bytes')
        return dict(archive=dest.name, manifest_sha256=sha(dest.with_suffix('.xz.json')),
                    packed_bytes=manifest['packed_bytes'])
    # Authenticate all retained bundles before creating any new output.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records = dict(zip(complete, pool.map(record, complete)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records.update(zip(missing, pool.map(lambda i: record(i, create=True), missing)))
    ordered = [records[i] for i in range(len(plan['jobs']))]
    for path in sources:
        require(sha(path) == expected[path], 'Source changed while packing')
    for path in allowed:
        require(sha(path) == expected[path], 'Retained archive evidence changed')
    index = dict(format=1, plan_sha256=sha(plan_path), bundles=ordered,
                 packed_bytes=sum(r['packed_bytes'] for r in ordered))
    durable(destination/'index.json', encoded(index))
    verify_index(destination, root=root, token=token, guard=guard, workers=workers)
    return dict(index=index, reused_bundles=len(complete), new_bundles=len(missing),
                raw_files_preserved=len(sources), raw_retired=False)
