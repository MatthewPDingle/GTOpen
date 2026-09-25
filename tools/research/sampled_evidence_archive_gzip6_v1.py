"""Lossless, independently verifiable research artifacts; never removes sources.

New archive format only. Existing native and evaluation formats are unchanged.
Consumers verify compressed and uncompressed hashes before parsing any bytes.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re


MAX_ARTIFACT_BYTES = 64 * 1024 * 1024


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def valid_name(name):
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*\.json', name):
        raise ValueError('A single JSON artifact filename is required')
    return name


def read_artifact(directory, manifest, name, *, guard):
    """Return the original bytes, after bounded decompression and both hashes."""
    guard(); valid_name(name)
    if manifest.get('format') != 1 or manifest.get('encoding') != 'gzip':
        raise ValueError('Unsupported archive format')
    item = manifest['artifacts'][name]
    if item['file'] != name + '.gz':
        raise ValueError('Archive member name mismatch')
    n, packed_n = item['raw_bytes'], item['compressed_bytes']
    if (type(n) is not int or not 0 <= n <= MAX_ARTIFACT_BYTES
            or type(packed_n) is not int or not 0 < packed_n <= MAX_ARTIFACT_BYTES + 65536):
        raise ValueError('Invalid bounded artifact size')
    path = Path(directory) / item['file']
    if path.is_symlink() or path.stat().st_size != packed_n:
        raise ValueError('Archive size or file type mismatch')
    packed = path.read_bytes()
    if digest(packed) != item['compressed_sha256']:
        raise ValueError('Compressed artifact hash mismatch')
    with gzip.GzipFile(fileobj=io.BytesIO(packed), mode='rb') as stream:
        raw = stream.read(n + 1)
    if len(raw) != n or digest(raw) != item['raw_sha256']:
        raise ValueError('Original artifact size or hash mismatch')
    guard()
    return raw


def archive(directory, names, destination, *, guard):
    """Write a new archive, verifying readback; source files stay untouched."""
    source, destination = Path(directory).resolve(), Path(destination).resolve()
    names = list(names)
    if not names or len(set(names)) != len(names):
        raise ValueError('Distinct nonempty artifact list required')
    for name in names: valid_name(name)
    if source == destination or destination.is_relative_to(source):
        raise ValueError('Archive must be separate from source directory')
    guard(); destination.mkdir(exist_ok=False)
    manifest = dict(format=1, encoding='gzip', compression_level=6,
                    source_directory=str(source), artifacts={})
    for name in sorted(names):
        guard(); path = source / name
        if path.is_symlink() or path.stat().st_size > MAX_ARTIFACT_BYTES:
            raise ValueError('Invalid source size or file type')
        raw = path.read_bytes()
        if len(raw) > MAX_ARTIFACT_BYTES:
            raise ValueError('Source grew beyond size limit')
        packed = gzip.compress(raw, compresslevel=6, mtime=0)
        item = dict(file=name+'.gz', raw_bytes=len(raw), raw_sha256=digest(raw),
                    compressed_bytes=len(packed), compressed_sha256=digest(packed))
        with (destination / item['file']).open('xb') as stream: stream.write(packed)
        manifest['artifacts'][name] = item
        if read_artifact(destination, manifest, name, guard=guard) != raw:
            raise ValueError('Archive readback mismatch')
        if digest(path.read_bytes()) != item['raw_sha256']:
            raise ValueError('Source changed during archival')
    guard()
    # Publish a manifest only after every member is completely written/verified.
    # A partial failed folder has no manifest and cannot be treated as complete.
    encoded = (json.dumps(manifest, sort_keys=True, separators=(',', ':'))+'\n').encode()
    with (destination / 'manifest.json').open('xb') as stream: stream.write(encoded)
    return manifest
