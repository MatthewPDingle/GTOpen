"""Lossless representation of the existing canonical eight-profile transport.

Keep four distinct policies, shared row identities, and byte-shuffled binary64
probabilities. Reconstruct the original JSON bytes, including float spellings.
Unrecognized layout or serialization is refused, never rounded or normalized.
This is storage only: all native evaluation still consumes the original JSON.
"""
import json
import math
import struct
import numpy as np

MAGIC = b'GTOPROF1'
MAX_RAW = 64 * 1024**2
MAX_HEADER = 16 * 1024**2
MAX_ROWS = 100000
PURE = (0, 3, 4, 7)
FIELDS = ('hi', 'lo', 'actor', 'n')


def encoded(value):
    return (json.dumps(value, separators=(',', ':'), allow_nan=False) + '\n').encode()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def decode(data):
    check(isinstance(data, bytes) and len(data) <= MAX_HEADER + MAX_ROWS*128 + 16,
          'Bounded binary profile stream required')
    check(data[:8] == MAGIC and len(data) >= 16, 'Invalid profile magic')
    size = struct.unpack('<Q', data[8:16])[0]
    check(0 < size <= MAX_HEADER and 16+size <= len(data), 'Invalid profile header size')
    header = json.loads(data[16:16+size])
    check(set(header) == {'format', 'context_source', 'batch_source', 'names', 'rows'}, 'Unknown profile header')
    rows = header['rows']
    count = len(rows)
    check(header['format'] == 1 and 0 < count <= MAX_ROWS and len(header['names']) == 8,
          'Invalid profile dimensions')
    check(isinstance(header['context_source'], str) and isinstance(header['batch_source'], str)
          and all(isinstance(v, str) for v in header['names']), 'Invalid source identity')
    check(len(data) == 16+size+count*4*4*8, 'Profile payload length mismatch')
    shuffled = np.frombuffer(data, dtype=np.uint8, offset=16+size).reshape(8, -1)
    probabilities = shuffled.T.copy().view('<f8').reshape(4, count, 4)
    check(np.isfinite(probabilities).all() and np.all(probabilities >= 0), 'Invalid probabilities')
    for row in rows:
        check(isinstance(row, list) and len(row) == 4 and isinstance(row[0], str)
              and isinstance(row[1], str) and type(row[2]) is int and row[2] in (0, 1)
              and type(row[3]) is int and 1 <= row[3] <= 4, 'Invalid observation identity')
    profiles = []
    for k, name in enumerate(header['names']):
        seed, pair = divmod(k, 4)
        bb, btn = divmod(pair, 2)
        policies = []
        for i, row in enumerate(rows):
            donor = seed*2 + (bb if row[2] == 0 else btn)
            p = probabilities[donor, i].tolist()
            check(abs(math.fsum(p)-1) <= 1e-10 and all(v == 0 for v in p[row[3]:]),
                  'Probabilities do not match legal actions')
            policies.append(dict(zip((*FIELDS, 'probabilities'), (*row, p))))
        profiles.append(dict(name=name, policies=policies))
    raw = encoded(dict(format=1, context_source=header['context_source'],
                       batch_source=header['batch_source'], profiles=profiles))
    check(len(raw) <= MAX_RAW, 'Restored profiles exceed limit')
    return raw


def encode(raw):
    check(isinstance(raw, bytes) and 0 < len(raw) <= MAX_RAW, 'Bounded original profile bytes required')
    document = json.loads(raw)
    check(isinstance(document, dict) and list(document) == ['format', 'context_source', 'batch_source', 'profiles']
          and document['format'] == 1 and encoded(document) == raw, 'Canonical native-input transport required')
    profiles = document['profiles']
    check(isinstance(profiles, list) and len(profiles) == 8, 'Eight crossed profiles required')
    rows = profiles[0]['policies']
    check(0 < len(rows) <= MAX_ROWS, 'Bounded policy rows required')
    keys = [list(row[k] for k in FIELDS) for row in rows]
    values = []
    for profile in profiles:
        check(list(profile) == ['name', 'policies'] and len(profile['policies']) == len(rows),
              'Inconsistent profile layout')
        for i, row in enumerate(profile['policies']):
            check(list(row) == [*FIELDS, 'probabilities'] and [row[k] for k in FIELDS] == keys[i]
                  and isinstance(row['probabilities'], list) and len(row['probabilities']) == 4,
                  'Shared policy observation identity changed')
        values.append([row['probabilities'] for row in profile['policies']])
    tensor = np.asarray([values[k] for k in PURE], dtype='<f8')
    header = encoded(dict(format=1, context_source=document['context_source'],
                          batch_source=document['batch_source'], names=[p['name'] for p in profiles], rows=keys))
    check(len(header) <= MAX_HEADER, 'Profile header exceeds limit')
    result = MAGIC + struct.pack('<Q', len(header)) + header + tensor.view(np.uint8).reshape(-1, 8).T.tobytes()
    # This catches even signed-zero, integer/float, crossing, or JSON spelling
    # differences that ordinary numeric equality would accidentally ignore.
    check(decode(result) == raw, 'Columnar reconstruction is not byte-identical')
    return result
