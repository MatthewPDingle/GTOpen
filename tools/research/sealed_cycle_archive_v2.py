"""Lossless, seekable archive for closed research payloads.

Creates a new archive without modifying sources. It is deliberately independent
of the poker learner: no sampling, fitting, policy changes or file retirement.
All members use independently authenticated 1 MiB frames, so JSON, NPY and NPZ
readers can use the same bytes without unpacking the full cycle onto disk.
"""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import struct
import threading
import time
import zlib

FRAME = 1048576
ROW = struct.Struct('<IIB32s')
MAGIC = b'GTOARC1\0'


def member_name(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Member names must be relative POSIX paths')
    p = PurePosixPath(value)
    if p.is_absolute() or any(v in ('', '.', '..') for v in value.split('/')):
        raise ValueError('Unsafe archive member')
    return value


def digest(path, check=lambda: None):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(FRAME), b''):
            check()
            h.update(chunk)
    return h.hexdigest()


def _encode(root, item, identity, max_file_bytes, check):
    check()
    name = member_name(item['name'])
    path = root.joinpath(*name.split('/')).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError('Source escapes archive root')
    before = identity(path)
    if before != item['identity'] or item['bytes'] > max_file_bytes:
        raise ValueError('Source identity or size changed')
    result = bytearray()
    frames = []
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as f:
        while chunk := f.read(FRAME):
            check()
            size += len(chunk)
            if size > item['bytes']:
                raise ValueError('Source grew')
            h.update(chunk)
            compressed = zlib.compress(chunk, 6)
            codec = int(len(compressed) < len(chunk))
            payload = compressed if codec else chunk
            frames.append([len(result), len(chunk), len(payload), codec,
                           hashlib.sha256(chunk).hexdigest()])
            result.extend(ROW.pack(len(chunk), len(payload), codec,
                                   hashlib.sha256(chunk).digest()))
            result.extend(payload)
    if size != item['bytes'] or h.hexdigest() != item['sha256'] or identity(path) != before:
        raise ValueError('Original bytes or identity changed')
    check()
    return item, result, frames


def create(root, output, items, *, identity, guard=lambda: None, workers=8,
           max_file_bytes=256000000, max_raw_bytes=6500000000,
           max_pack_bytes=1000000000, max_seconds=600):
    """Exclusive new output. A failed partial archive is kept, never accepted.

    Bounded in-flight queue plus completed results: at most two whole encoded
    members per worker while the coordinator drains a completion group.
    Sources may contain only the caller's authenticated closed member list.
    """
    root = Path(root).resolve(strict=True)
    output = Path(output).resolve()
    if output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('Source and archive namespaces overlap')
    items = list(items)
    names = [member_name(v['name']) for v in items]
    if len(set(names)) != len(names) or not 0 < len(items) <= 10000:
        raise ValueError('Duplicate or excessive archive members')
    if any(not isinstance(v['bytes'], int) or v['bytes'] < 0 or
           v['bytes'] > max_file_bytes for v in items):
        raise ValueError('Member size bound')
    raw_total = sum(v['bytes'] for v in items)
    if raw_total > max_raw_bytes or not 1 <= workers <= 8:
        raise ValueError('Archive input bound')
    guard()
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    cancelled = threading.Event()
    def check():
        if cancelled.is_set():
            raise RuntimeError('Archive operation cancelled')
        if time.monotonic()-started > max_seconds:
            raise TimeoutError('Archive deadline')
    pack_path = output / 'payload.gta'
    packed = len(MAGIC)
    rows = []
    pending = set()
    iterator = iter(items)
    try:
        with pack_path.open('xb') as pack, ThreadPoolExecutor(max_workers=workers) as pool:
            pack.write(MAGIC)
            def submit():
                item = next(iterator, None)
                if item is not None:
                    pending.add(pool.submit(_encode, root, item, identity, max_file_bytes, check))
            for _ in range(workers):
                submit()
            try:
                while pending:
                    check(); guard()
                    done, pending = wait(pending, timeout=1, return_when=FIRST_COMPLETED)
                    for future in done:
                        item, payload, frames = future.result()
                        if packed + len(payload) > max_pack_bytes:
                            raise ValueError('Archive output bound')
                        offset = packed
                        pack.write(payload)
                        packed += len(payload)
                        rows.append(dict(**item, offset=offset, stored_bytes=len(payload), frames=frames))
                        del payload
                        submit()
            except BaseException:
                cancelled.set()
                for future in pending: future.cancel()
                raise
            pack.flush()
            os.fsync(pack.fileno())
        document = dict(format=1, method='closed-cycle-seekable-zlib6-archive-v1',
                        source_root=str(root), payload='payload.gta',
                        payload_bytes=packed, payload_sha256=digest(pack_path,check),
                        raw_bytes=raw_total, frame_bytes=FRAME, workers=workers,
                        seconds=time.monotonic()-started,
                        files=sorted(rows, key=lambda v: v['name']))
        manifest = json.dumps(document, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        if len(manifest) > 8000000:
            raise ValueError('Manifest bound')
        with (output / 'manifest.json').open('xb') as f:
            f.write(manifest)
            f.flush()
            os.fsync(f.fileno())
        check(); guard()
        archive = Archive(output, hashlib.sha256(manifest).hexdigest(),check=check,
                          _preseal_verification=True)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            checks = {pool.submit(archive.verify, name,check) for name in names}
            try:
                while checks:
                    check(); guard()
                    done, checks = wait(checks, timeout=1, return_when=FIRST_COMPLETED)
                    for future in done: future.result()
            except BaseException:
                cancelled.set()
                for future in checks: future.cancel()
                raise
        check(); guard()
        with (output / 'verified.json').open('x') as f:
            json.dump(dict(manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                           all_members_verified=True, files=len(items), raw_bytes=raw_total,
                           seconds=time.monotonic()-started, original_files_retired=False), f)
        check(); guard()
        return document
    except BaseException as error:
        for future in pending:
            future.cancel()
        with (output / 'failure.json').open('x') as f:
            json.dump(dict(error=repr(error), completed_members=len(rows),
                           seconds=time.monotonic()-started, accepted=False), f)
        raise


class Archive:
    def __init__(self, root, manifest_sha256,check=lambda:None,
                 _preseal_verification=False):
        self.root = Path(root).resolve(strict=True)
        if (self.root / 'failure.json').exists():
            raise ValueError('Failed archive is not admissible')
        path = self.root / 'manifest.json'
        if path.stat().st_size > 8000000 or digest(path,check) != manifest_sha256:
            raise ValueError('Manifest identity changed')
        self.manifest = json.loads(path.read_bytes())
        doc = self.manifest
        if not _preseal_verification:
            seal = self.root/'verified.json'
            if not seal.is_file() or seal.stat().st_size>8192:
                raise ValueError('Archive has no bounded completion seal')
            accepted = json.loads(seal.read_bytes())
            if (accepted.get('manifest_sha256')!=manifest_sha256
                    or accepted.get('all_members_verified') is not True
                    or accepted.get('files')!=len(doc['files'])
                    or accepted.get('raw_bytes')!=doc['raw_bytes']):
                raise ValueError('Archive completion seal mismatch')
        if doc['format'] != 1 or doc['frame_bytes'] != FRAME or doc['payload'] != 'payload.gta':
            raise ValueError('Archive format')
        self.payload = self.root / 'payload.gta'
        if self.payload.stat().st_size != doc['payload_bytes'] or digest(self.payload,check) != doc['payload_sha256']:
            raise ValueError('Payload identity changed')
        with self.payload.open('rb') as f:
            if f.read(len(MAGIC)) != MAGIC:
                raise ValueError('Payload magic')
        self.files = {}
        intervals = []
        for item in doc['files']:
            check()
            name = member_name(item['name'])
            if name in self.files or item['bytes'] < 0 or item['bytes'] > 256000000:
                raise ValueError('Invalid member declaration')
            stored = raw = 0
            for frame_number, (offset, n, c, codec, h) in enumerate(item['frames']):
                if offset != stored or not 0 < n <= FRAME or not 0 < c <= n or codec not in (0, 1):
                    raise ValueError('Invalid frame geometry')
                if len(bytes.fromhex(h)) != 32 or (codec == 0 and c != n):
                    raise ValueError('Invalid frame identity')
                if frame_number < len(item['frames'])-1 and n != FRAME:
                    raise ValueError('Only the final frame may be short')
                stored += ROW.size + c
                raw += n
            if stored != item['stored_bytes'] or raw != item['bytes']:
                raise ValueError('Invalid member geometry')
            intervals.append((item['offset'], item['offset'] + stored))
            self.files[name] = item
        position = len(MAGIC)
        for start, end in sorted(intervals):
            if start != position or end < start:
                raise ValueError('Member gaps, overlaps or aliases')
            position = end
        if position != doc['payload_bytes'] or sum(v['bytes'] for v in self.files.values()) != doc['raw_bytes']:
            raise ValueError('Archive totals')

    def open(self, name, expected_sha256=None):
        item = self.files[member_name(name)]
        if expected_sha256 is not None and expected_sha256 != item['sha256']:
            raise ValueError('Original reference hash mismatch')
        return io.BufferedReader(Member(self.payload, item))

    def read_json(self, name, expected_sha256=None):
        with self.open(name, expected_sha256) as f:
            return json.load(f)

    def verify(self, name,check=lambda:None):
        h = hashlib.sha256()
        with self.open(name) as f:
            for chunk in iter(lambda: f.read(FRAME), b''):
                check()
                h.update(chunk)
        if h.hexdigest() != self.files[name]['sha256']:
            raise ValueError('Member checksum mismatch')
        return self.files[name]['bytes']


class Member(io.RawIOBase):
    def __init__(self, payload, item):
        self.stream = Path(payload).open('rb')
        self.item = item
        self.position = 0
        self.cached = (-1, b'')

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if self.closed: raise ValueError('Closed member')
        base = {io.SEEK_SET: 0, io.SEEK_CUR: self.position, io.SEEK_END: self.item['bytes']}
        if whence not in base or base[whence]+offset < 0:
            raise ValueError('Invalid seek')
        self.position = base[whence]+offset
        return self.position

    def _frame(self, number):
        if self.cached[0] == number:
            return self.cached[1]
        offset, n, c, codec, h = self.item['frames'][number]
        self.stream.seek(self.item['offset']+offset)
        header = self.stream.read(ROW.size)
        if len(header) != ROW.size or ROW.unpack(header) != (n, c, codec, bytes.fromhex(h)):
            raise ValueError('Frame header changed')
        payload = self.stream.read(c)
        if len(payload) != c:
            raise ValueError('Truncated frame')
        if codec:
            decoder = zlib.decompressobj()
            data = decoder.decompress(payload, n+1)
            if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                raise ValueError('Invalid compressed frame')
        else:
            data = payload
        if len(data) != n or hashlib.sha256(data).hexdigest() != h:
            raise ValueError('Frame checksum mismatch')
        self.cached = (number, data)
        return data

    def readinto(self, buffer):
        if self.closed: raise ValueError('Closed member')
        available = max(0, min(len(buffer), self.item['bytes']-self.position))
        out = memoryview(buffer)
        written = 0
        while written < available:
            number, inside = divmod(self.position, FRAME)
            frame = self._frame(number)
            n = min(available-written, len(frame)-inside)
            out[written:written+n] = frame[inside:inside+n]
            self.position += n
            written += n
        return written

    def close(self):
        if not self.closed:
            self.stream.close()
        super().close()
