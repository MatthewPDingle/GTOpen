"""Owned new checkpoint writes with authenticated read-only predecessor objects.

Dedicated-process adapter. Previous content-addressed objects are reused without
copying, linking, replacing, or retiring them. Caller must retain the recorded
predecessor dependency; the new directory is deliberately not self-contained.
"""
from contextlib import contextmanager
import hashlib
import io
from pathlib import Path
import re
import threading
from unittest.mock import patch
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
from owned_research_archive_v1 import owner
from owned_columnar_evaluation_archive_v1 import unlinked
import sampled_visible_hybrid_checkpoint_v1 as base
from sampled_physical_reservoir_v1 import PhysicalReservoir

_LOCK = threading.Lock()
_READ = base.read_object
_PUBLISH = base.publish
_LOAD = PhysicalReservoir.load.__func__
_NAME = re.compile(r'[a-z]+-([0-9a-f]{64})\.(json|npz)')


def require(value, message):
    if not value:
        raise ValueError(message)


@contextmanager
def overlay(directory, predecessor, *, root, token, guard):
    require(_LOCK.acquire(blocking=False), 'Concurrent checkpoint overlay is unsupported')
    try:
        require(base.read_object is _READ and base.publish is _PUBLISH
                and PhysicalReservoir.load.__func__ is _LOAD, 'Checkpoint adapters already active')
        guard(); owned = owner(root, token); directory = unlinked(directory)
        require(directory != owned and directory.is_relative_to(owned), 'Writes require an owned child directory')
        predecessor = unlinked(predecessor)
        require(predecessor != directory and not predecessor.is_relative_to(owned),
                'Predecessor must remain outside new writable ownership')
        reader = ReadOnlyCheckpointObjects(predecessor, guard=guard)
        names = set(reader.members) if reader.members is not None else {
            p.name for p in predecessor.iterdir() if p.is_file() and _NAME.fullmatch(p.name)}
        record = dict(predecessor=str(predecessor), directory=str(directory),
            predecessor_retention_sha256=reader.retention_sha256,
            reused_objects={}, published_objects={})
        authenticated = {}

        def location(path):
            require(unlinked(path) == directory, 'Unexpected checkpoint output directory')

        def reference(ref):
            name = ref['file']; match = _NAME.fullmatch(name) if isinstance(name, str) else None
            require(match is not None and match.group(1) == ref['sha256'], 'Invalid content-addressed reference')
            return name

        def read_object(path, ref):
            guard(); location(path); name = reference(ref)
            local = directory/name
            if local.exists():
                unlinked(local); raw = _READ(directory, ref)
                if name in names:
                    require(raw == reader.read(ref), 'Local/predecessor conflict')
            else:
                require(name in names, 'Object missing from overlay and predecessor')
                raw = reader.read(ref); record['reused_objects'][name] = ref['sha256']
            authenticated[name] = ref['sha256']
            return raw

        def publish(path, kind, content, suffix='json'):
            guard(); location(path)
            require(isinstance(kind, str) and re.fullmatch('[a-z]+', kind)
                    and suffix in ('json', 'npz'), 'Invalid object kind or suffix')
            digest = hashlib.sha256(content).hexdigest()
            ref = dict(file=f'{kind}-{digest}.{suffix}', sha256=digest)
            if ref['file'] in names:
                require(reader.read(ref) == content, 'Predecessor bytes differ from publication')
                if (directory/ref['file']).exists():
                    require(read_object(directory, ref) == content, 'Conflicting local object')
                record['reused_objects'][ref['file']] = digest
                return ref
            result = _PUBLISH(directory, kind, content, suffix)
            record['published_objects'][result['file']] = result['sha256']
            return result

        def load_reservoir(path, context_source):
            path = Path(path); location(path.parent)
            require(path.name in authenticated, 'Reservoir must pass object authentication before loading')
            raw = read_object(directory, dict(file=path.name, sha256=authenticated[path.name]))
            return _LOAD(PhysicalReservoir, io.BytesIO(raw), context_source)

        with patch.object(base, 'read_object', read_object), patch.object(base, 'publish', publish), \
                patch.object(PhysicalReservoir, 'load', load_reservoir):
            yield record
    finally:
        _LOCK.release()
