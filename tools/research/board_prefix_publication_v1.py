"""Measured storage boundaries and atomic Windows research completion markers.

Call storage_boundary only when this study's workers have finished writing.
These are admission/publication checks, not an operating-system disk quota.
Failed temporary writes remain as evidence and count toward measured storage.
"""
import hashlib
import json
import os
from pathlib import Path
import uuid
from board_study_storage_v1 import measure


def storage_boundary(store, registration, stage, *, reserve_bytes=0, guard=lambda: None):
    if type(reserve_bytes) is not int or reserve_bytes < 0:
        raise ValueError('Nonnegative byte reserve required')
    value = measure(store, guard=guard)
    for key, limit_key in (('allocated_file_bytes', 'maximum_allocated_bytes'),
                           ('logical_bytes', 'maximum_logical_bytes')):
        limit = registration[limit_key]
        if type(limit) is not int or limit <= 0:
            raise ValueError('Positive storage limit required')
        if value[key] + reserve_bytes > limit:
            raise RuntimeError(f'{stage}: {key} {value[key]} + reserve {reserve_bytes} exceeds {limit}')
    return dict(stage=stage, reserve_bytes=reserve_bytes, **value)


def atomic_json(path, value, *, replace=False):
    """Write/flush complete JSON before an atomic same-directory publication.

New markers use Windows rename's no-overwrite behavior. Progress replacement
is explicit. A failed write or publication preserves its uniquely named file.
File flushing plus rename is not a guarantee against all power-loss failures.
"""
    if os.name != 'nt':
        raise ValueError('Windows publication semantics required')
    path = Path(path)
    if not replace and path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f'.partial-{path.name}-{uuid.uuid4().hex}')
    with temporary.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, separators=(',', ':'), allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    if replace:
        os.replace(temporary, path)
    else:
        os.rename(temporary, path)


def completion(path, registration_sha256, *, resume=False, recovered=None):
    """Read a completion marker; explicit resume preserves malformed legacy JSON.

The caller must validate the registration and its sources before calling.
Semantic disagreement is never treated as an interrupted write. Progress
checkpoints are deliberately outside this recovery mechanism.
"""
    path = Path(path)
    if not path.exists():
        return None
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        if not resume:
            raise ValueError(f'Malformed completion marker requires explicit resume: {path}')
        preserved = path.with_name(f'.invalid-{path.name}-{uuid.uuid4().hex}')
        os.rename(path, preserved)
        if recovered is not None:
            recovered.append(dict(original_path=str(path), preserved_path=str(preserved),
                                  sha256=hashlib.sha256(raw).hexdigest()))
        return None
    if not isinstance(value, dict) or value.get('passed') is not True:
        raise ValueError(f'Non-passing completion marker: {path}')
    if value.get('registration_sha256') != registration_sha256:
        raise ValueError(f'Completion registration mismatch: {path}')
    return value
