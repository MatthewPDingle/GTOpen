"""Storage-only candidate: reconstruct each donor row once, preserving JSON bytes.

Not connected to the running study. Uses the existing residual archive format
and encoder; qualification must compare original decoded bytes independently.
"""
import json
import math
import struct
import numpy as np
import crossed_profile_columnar_v1 as base
import crossed_profile_columnar_v2 as residual


def decode_base(data):
    base.check(isinstance(data, bytes) and len(data) <= base.MAX_HEADER + base.MAX_ROWS*128 + 16,
               'Bounded binary profile stream required')
    base.check(len(data) >= 16 and data[:8] == base.MAGIC, 'Invalid profile magic')
    size = struct.unpack('<Q', data[8:16])[0]
    base.check(0 < size <= base.MAX_HEADER and 16+size <= len(data), 'Invalid profile header size')
    header = json.loads(data[16:16+size])
    base.check(set(header) == {'format', 'context_source', 'batch_source', 'names', 'rows'}, 'Unknown profile header')
    rows = header['rows']; count = len(rows)
    base.check(header['format'] == 1 and 0 < count <= base.MAX_ROWS and len(header['names']) == 8,
               'Invalid profile dimensions')
    base.check(isinstance(header['context_source'], str) and isinstance(header['batch_source'], str)
               and all(isinstance(v, str) for v in header['names']), 'Invalid source identity')
    base.check(len(data) == 16+size+count*128, 'Profile payload length mismatch')
    probabilities = np.frombuffer(data, dtype=np.uint8, offset=16+size).reshape(8, -1).T.copy().view('<f8').reshape(4, count, 4)
    base.check(np.isfinite(probabilities).all() and np.all(probabilities >= 0), 'Invalid probabilities')
    for row in rows:
        base.check(isinstance(row, list) and len(row) == 4 and isinstance(row[0], str)
                   and isinstance(row[1], str) and type(row[2]) is int and row[2] in (0, 1)
                   and type(row[3]) is int and 1 <= row[3] <= 4, 'Invalid observation identity')
    # Every donor is used in two crossings. Validate and serialize it once.
    donors = []
    for bank in probabilities:
        policies = []
        for row, p in zip(rows, bank.tolist()):
            base.check(abs(math.fsum(p)-1) <= 1e-10 and all(v == 0 for v in p[row[3]:]),
                       'Probabilities do not match legal actions')
            policies.append(base.encoded(dict(zip((*base.FIELDS, 'probabilities'), (*row, p))))[:-1])
        donors.append(policies)
    profiles = []
    for k, name in enumerate(header['names']):
        seed, pair = divmod(k, 4); bb, btn = divmod(pair, 2)
        policies = (donors[seed*2 + (bb if row[2] == 0 else btn)][i] for i, row in enumerate(rows))
        profiles.append(b'{"name":' + base.encoded(name)[:-1] + b',"policies":[' + b','.join(policies) + b']}')
    prefix = base.encoded(dict(format=1, context_source=header['context_source'], batch_source=header['batch_source']))[:-2]
    raw = prefix + b',"profiles":[' + b','.join(profiles) + b']}\n'
    base.check(len(raw) <= base.MAX_RAW, 'Restored profiles exceed limit')
    return raw


def decode(data):
    base.check(isinstance(data, bytes) and len(data) <= base.MAX_HEADER + base.MAX_ROWS*128+16
               and len(data) >= 16 and data[:8] == residual.MAGIC, 'Invalid residual profile stream')
    size = struct.unpack('<Q', data[8:16])[0]
    base.check(0 < size <= base.MAX_HEADER and 16+size < len(data), 'Invalid header size')
    header = json.loads(data[16:16+size]); count = len(header['rows'])*4
    base.check(0 < count <= base.MAX_ROWS*4 and len(data) == 16+size+count*29, 'Invalid residual profile dimensions')
    offset = 16+size
    chosen = np.frombuffer(data, dtype=np.uint8, count=count, offset=offset)
    base.check(np.all(chosen < 4), 'Invalid selected component'); offset += count
    delta = residual.unshuffle(data[offset:offset+count*4], 4, '<i4'); offset += count*4
    remaining = residual.unshuffle(data[offset:], 8, '<f8').reshape(count, 3)
    predictor = np.asarray([1.0-math.fsum(row) for row in remaining.tolist()], dtype='<f8')
    base.check(np.isfinite(predictor).all() and np.all(predictor > 0), 'Invalid probability predictor')
    bits = predictor.view('<u8')
    # Keep Python integer bounds checking; never allow unsigned wraparound.
    restored = [int(b)+int(d) for b, d in zip(bits, delta)]
    base.check(all(0 <= b < 2**64 for b in restored), 'Invalid bit residual')
    values = np.empty((count, 4), dtype='<f8')
    mask = np.arange(4)[None, :] != chosen[:, None]
    values[mask] = remaining.ravel()
    values[np.arange(count), chosen] = np.asarray(restored, dtype='<u8').view('<f8')
    return decode_base(base.MAGIC + data[8:16+size] + residual.shuffled(values, 8))
