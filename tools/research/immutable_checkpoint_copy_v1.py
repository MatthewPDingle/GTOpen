"""Copy only the authenticated objects reachable from a checkpoint.

Source objects remain untouched. No directory links, movement, or partial-state
repair. Callers must separately admit space and validate the restored model.
"""
import json
import os
from pathlib import Path
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_physical_root_evaluation_v1 import sha


def references(value):
    if isinstance(value, dict):
        if 'file' in value and 'sha256' in value:
            yield dict(file=value['file'], sha256=value['sha256'])
        for child in value.values():
            yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)


def inspect_closure(source, checkpoint, *, maximum_bytes, guard):
    source = Path(source).resolve()
    pending = [checkpoint]
    objects = {}
    total = 0
    while pending:
        guard()
        ref = pending.pop()
        # The existing immutable reader validates path syntax and content hash.
        raw = read_object(source, ref)
        name = ref['file']
        if name in objects:
            if objects[name]['sha256'] != ref['sha256']:
                raise ValueError('Conflicting reference')
            continue
        total += len(raw)
        if total > maximum_bytes or len(objects) >= 10000:
            raise ValueError('Checkpoint copy exceeds admitted bound')
        objects[name] = dict(sha256=ref['sha256'], bytes=len(raw))
        if name.endswith('.json'):
            pending.extend(references(json.loads(raw)))
    return dict(checkpoint=checkpoint, objects=objects, logical_bytes=total)


def copy_closure(source, destination, checkpoint, *, maximum_bytes, guard):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if source == destination or destination.exists() or not destination.parent.is_dir():
        raise ValueError('Copy requires a distinct new destination with an existing parent')
    manifest = inspect_closure(source, checkpoint, maximum_bytes=maximum_bytes, guard=guard)
    destination.mkdir()
    for name, identity in manifest['objects'].items():
        guard()
        raw = read_object(source, dict(file=name, sha256=identity['sha256']))
        target = destination/name
        if target.resolve().parent != destination or len(raw) != identity['bytes']:
            raise ValueError('Object identity or path changed')
        with target.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if sha(target) != identity['sha256']:
            raise ValueError('Copied object changed')
    return manifest
