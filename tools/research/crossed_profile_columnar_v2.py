"""Losslessly predict one probability per row, retaining its exact bit residual.

This never adjusts a probability to force normalization: the signed residual
restores the original binary64 bits even when the four numbers do not sum to
exactly one. Version 1 validates and reproduces the original transport bytes.
"""
import math
import struct
import numpy as np
import crossed_profile_columnar_v1 as original

MAGIC = b'GTOPROF2'


def shuffled(array, width):
    return array.view(np.uint8).reshape(-1, width).T.tobytes()


def unshuffle(data, width, dtype):
    return np.frombuffer(data, dtype=np.uint8).reshape(width, -1).T.copy().view(dtype).reshape(-1)


def decode(data):
    original.check(isinstance(data, bytes) and len(data) <= original.MAX_HEADER + original.MAX_ROWS*128+16
                   and len(data) >= 16 and data[:8] == MAGIC, 'Invalid residual profile stream')
    size = struct.unpack('<Q', data[8:16])[0]
    original.check(0 < size <= original.MAX_HEADER and 16+size < len(data), 'Invalid header size')
    import json
    header = json.loads(data[16:16+size])
    count = len(header['rows'])*4
    original.check(0 < count <= original.MAX_ROWS*4 and len(data) == 16+size+count*29,
                   'Invalid residual profile dimensions')
    offset = 16+size
    selected = np.frombuffer(data, dtype=np.uint8, count=count, offset=offset)
    original.check(np.all(selected < 4), 'Invalid selected component')
    offset += count
    residual = unshuffle(data[offset:offset+count*4], 4, '<i4');offset += count*4
    remaining = unshuffle(data[offset:], 8, '<f8').reshape(count, 3)
    values = np.empty((count, 4), dtype='<f8')
    for i, (chosen, small, delta) in enumerate(zip(selected, remaining, residual)):
        base = 1.0 - math.fsum(map(float, small))
        original.check(math.isfinite(base) and base > 0, 'Invalid probability predictor')
        bits = struct.unpack('<Q', struct.pack('<d', base))[0] + int(delta)
        original.check(0 <= bits < 2**64, 'Invalid bit residual')
        values[i, chosen] = struct.unpack('<d', struct.pack('<Q', bits))[0]
        values[i, [j for j in range(4) if j != chosen]] = small
    reconstructed = original.MAGIC + data[8:16+size] + shuffled(values, 8)
    return original.decode(reconstructed)


def encode(raw):
    first = original.encode(raw)
    size = struct.unpack('<Q', first[8:16])[0]
    values = unshuffle(first[16+size:], 8, '<f8').reshape(-1, 4)
    chosen = np.argmax(values, axis=1).astype(np.uint8)
    remaining = np.empty((len(values), 3), dtype='<f8')
    residual = np.empty(len(values), dtype='<i4')
    for i, (row, selected) in enumerate(zip(values, chosen)):
        small = [float(v) for j, v in enumerate(row) if j != selected]
        base = 1.0 - math.fsum(small)
        original.check(math.isfinite(base) and base > 0, 'Invalid probability predictor')
        delta = (struct.unpack('<Q', struct.pack('<d', row[selected]))[0]
                 - struct.unpack('<Q', struct.pack('<d', base))[0])
        original.check(-2**31 <= delta < 2**31, 'Probability residual exceeds bound')
        remaining[i] = small;residual[i] = delta
    result = MAGIC + first[8:16+size] + chosen.tobytes() + shuffled(residual, 4) + shuffled(remaining, 8)
    original.check(decode(result) == raw, 'Residual reconstruction is not byte-identical')
    return result
