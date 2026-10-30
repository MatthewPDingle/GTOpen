"""Durable, lossless evaluation bundles; retire only verified new owned copies."""
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import struct
import uuid
from crossed_profile_columnar_v2 import encode as encode_profiles, decode as decode_profiles

ROOT = Path('S:/GTOpen-research').absolute()
MAGIC = b'GTOEVAL1'
ARTIFACTS = frozenset(('query-batch.json', 'conditional-batch.json', 'queries.json',
                      'profiles.json', 'native.json', 'residuals.json', 'summary.json'))
MAX_MEMBER = 64*1024**2
MAX_RAW = 512*1024**2
MAX_PACKED = 128*1024**2
MAX_HEADER = 1024**2


def check(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def unlinked(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.exists() or part.is_symlink():
            check(not part.is_symlink() and not (part.lstat().st_file_attributes & 0x400), 'Linked evidence path')
    check(path.resolve() == path, 'Aliased evidence path')
    return path


def durable(path, raw):
    path = unlinked(path)
    with path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())


def read_bounded(path, limit):
    path = unlinked(path)
    check(path.is_file() and path.stat().st_size <= limit, 'Oversized or missing evidence file')
    with path.open('rb') as stream:
        data = stream.read(limit+1)
    check(len(data) <= limit, 'Evidence exceeded size bound')
    return data


def restore(path, manifest, *, guard):
    guard()
    check(manifest.get('format') == 1 and manifest.get('codec') == 'xz-columnar-crossed-v1', 'Wrong archive type')
    packed = read_bounded(path, MAX_PACKED)
    check(len(packed) == manifest['packed_bytes'] and digest(packed) == manifest['packed_sha256'],
          'Compressed evidence identity changed')
    decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=128*1024**2)
    raw = decoder.decompress(packed, max_length=MAX_RAW+MAX_HEADER+17)
    check(decoder.eof and not decoder.unused_data and len(raw) <= MAX_RAW+MAX_HEADER+16
          and raw[:8] == MAGIC and len(raw) >= 16, 'Invalid bounded archive stream')
    size = struct.unpack('<Q', raw[8:16])[0]
    check(0 < size <= MAX_HEADER and 16+size <= len(raw), 'Invalid member header')
    members = json.loads(raw[16:16+size]);offset = 16+size
    check(members == manifest['members'] and len(members) == len(ARTIFACTS)
          and {m['name'] for m in members} == ARTIFACTS, 'Unexpected archive members')
    result = {};total = 0
    for item in members:
        guard()
        check(type(item['bytes']) is int and 0 <= item['bytes'] <= MAX_MEMBER
              and type(item['raw_bytes']) is int and 0 <= item['raw_bytes'] <= MAX_MEMBER,
              'Invalid original or stored member size')
        total += item['raw_bytes'];check(total <= MAX_RAW, 'Original batch exceeds bound')
        name = item['name']
        codec = 'columnar-profiles-v2' if name == 'profiles.json' else 'raw'
        check(item['codec'] == codec, 'Unexpected member codec')
        data = raw[offset:offset+item['bytes']];offset += item['bytes']
        check(len(data) == item['bytes'], 'Truncated member')
        original = decode_profiles(data) if name == 'profiles.json' else data
        check(len(original) == item['raw_bytes'] and digest(original) == item['raw_sha256'],
              'Original evidence identity changed')
        result[name] = original
    check(offset == len(raw), 'Trailing member bytes')
    return result


class OwnedColumnarEvaluationArchive:
    @classmethod
    def create(cls, root, *, guard):
        guard();root = unlinked(root)
        check(root != ROOT and root.is_relative_to(ROOT), 'New research descendant required')
        check(not root.exists(), 'Preserve existing evidence directory')
        root.mkdir();(root/'.batch-work').mkdir()
        owner = encoded(dict(format=1, token=uuid.uuid4().hex, root=str(root),
                             purpose='new-columnar-evaluation-scratch-only'))
        durable(root/'archive-owner.json', owner)
        return cls(root, digest(owner), guard=guard)

    def __init__(self, root, owner_sha256, *, guard):
        self.root = Path(root).absolute();self.owner_sha256 = owner_sha256;self.guard = guard
        self._owner()

    def _owner(self):
        self.guard();root = unlinked(self.root)
        check(root != ROOT and root.is_relative_to(ROOT), 'Outside owned research root')
        raw = read_bounded(root/'archive-owner.json', 4096);value = json.loads(raw)
        check(digest(raw) == self.owner_sha256 and value['format'] == 1 and value['root'] == str(root)
              and value['purpose'] == 'new-columnar-evaluation-scratch-only', 'Ownership identity changed')

    def _paths(self, name):
        self._owner();check(isinstance(name, str) and re.fullmatch(r'test-[0-9]{6}', name), 'Invalid batch name')
        return tuple(unlinked(p) for p in (
            self.root/'.batch-work'/name, self.root/(name+'.xz'), self.root/(name+'.manifest.json'),
            self.root/'.batch-work'/(name+'.claim.json'), self.root/'.batch-work'/(name+'.receipt.json')))

    def _claim(self, name, path):
        check(json.loads(read_bounded(path,4096)) == dict(name=name,owner_sha256=self.owner_sha256),
              'Batch claim mismatch')

    def begin(self, name):
        paths = self._paths(name)
        check(not any(p.exists() for p in paths), 'Preserve existing batch or failed attempt')
        durable(paths[3],encoded(dict(name=name,owner_sha256=self.owner_sha256)))
        return paths[0]  # Native generation creates the directory.

    def publish(self, name):
        source, destination, mp, claim, receipt = self._paths(name);self._claim(name,claim)
        check({p.name for p in source.iterdir()} == ARTIFACTS, 'Unexpected scratch files')
        parts = {n:read_bounded(source/n,MAX_MEMBER) for n in sorted(ARTIFACTS)}
        check(sum(map(len,parts.values())) <= MAX_RAW, 'Oversized scratch batch')
        stored = dict(parts);stored['profiles.json'] = encode_profiles(parts['profiles.json'])
        members = [dict(name=n,codec='columnar-profiles-v2' if n=='profiles.json' else 'raw',
            bytes=len(stored[n]),raw_bytes=len(parts[n]),raw_sha256=digest(parts[n])) for n in sorted(parts)]
        header = encoded(members);check(len(header) <= MAX_HEADER, 'Oversized archive header')
        payload = b''.join(stored[n] for n in sorted(stored));check(len(payload) <= MAX_RAW, 'Oversized transformed batch')
        packed = lzma.compress(MAGIC+struct.pack('<Q',len(header))+header+payload,preset=6)
        check(len(packed) <= MAX_PACKED, 'Oversized packed batch');self.guard()
        manifest = dict(format=1,codec='xz-columnar-crossed-v1',packed_bytes=len(packed),
                        packed_sha256=digest(packed),members=members)
        durable(destination,packed)
        check(restore(destination,manifest,guard=self.guard) == parts, 'Archive roundtrip failed')
        for n,raw in parts.items():
            check(read_bounded(source/n,MAX_MEMBER) == raw, 'Source changed during publication')
        manifest_raw = encoded(manifest);durable(mp,manifest_raw);identity = digest(manifest_raw)
        durable(receipt,encoded(dict(name=name,owner_sha256=self.owner_sha256,manifest_sha256=identity)))
        return identity

    def release(self, name):
        source,destination,mp,claim,receipt = self._paths(name);self._claim(name,claim)
        proof = json.loads(read_bounded(receipt,4096))
        check(proof['name'] == name and proof['owner_sha256'] == self.owner_sha256, 'Release receipt mismatch')
        manifest_raw = read_bounded(mp,MAX_HEADER)
        check(digest(manifest_raw) == proof['manifest_sha256'], 'Durable manifest changed')
        restored = restore(destination,json.loads(manifest_raw),guard=self.guard)
        if not source.exists():
            return proof['manifest_sha256']
        remaining = {p.name for p in source.iterdir()}
        check(remaining <= ARTIFACTS, 'Unexpected scratch member; preserve all files')
        # Validate every remaining file before deleting any; interruptions may
        # leave a subset, each still backed by the complete authenticated archive.
        for n in sorted(remaining):
            check(read_bounded(source/n,MAX_MEMBER) == restored[n], 'Changed scratch; preserve all files')
        for n in sorted(remaining):
            self._owner();target=unlinked(source/n)
            check(target.parent == source and source.parent == self.root/'.batch-work'
                  and read_bounded(target,MAX_MEMBER) == restored[n], 'Unsafe or changed retirement target')
            target.unlink()
        unlinked(source).rmdir()  # Empty newly owned batch only; never recursive.
        return proof['manifest_sha256']


class ColumnarEvaluationReader:
    """Original virtual filenames for existing scalar/native readback routines."""
    def __init__(self, root, manifest_hashes, *, external_files=(), guard):
        self.root=unlinked(root);self.manifest_hashes=dict(manifest_hashes)
        check(self.manifest_hashes and all(re.fullmatch(r'test-[0-9]{6}',n) for n in self.manifest_hashes),
              'Explicit batch manifest identities required')
        self.external={Path(p).absolute() for p in external_files};self.guard=guard;self.cache=None

    def read_bytes(self,path):
        self.guard();path=unlinked(path)
        if path in self.external or path.parent == self.root:
            return read_bounded(path,MAX_MEMBER)
        check(path.parent.parent == self.root and path.parent.name in self.manifest_hashes
              and path.name in ARTIFACTS and not path.exists(), 'Unregistered or ambiguous evidence path')
        name=path.parent.name;mp=self.root/(name+'.manifest.json');archive=self.root/(name+'.xz')
        raw=read_bounded(mp,MAX_HEADER);identity=digest(raw)
        check(identity == self.manifest_hashes[name], 'Registered manifest changed')
        manifest=json.loads(raw)
        check(digest(read_bounded(archive,MAX_PACKED)) == manifest['packed_sha256'], 'Archive changed')
        if self.cache is None or self.cache[:2] != (name,identity):
            self.cache=(name,identity,restore(archive,manifest,guard=self.guard))
        return self.cache[2][path.name]

    def read_json(self,path):
        return json.loads(self.read_bytes(path))

    def sha256(self,path):
        return digest(self.read_bytes(path))
