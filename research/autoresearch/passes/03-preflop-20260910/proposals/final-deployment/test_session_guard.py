import json
from pathlib import Path
import struct
import tempfile
import unittest

from session_guard import api, native


class NativeGuardTests(unittest.TestCase):
    def write(self, path, magic, header, count):
        with path.open('wb') as f:
            f.write(magic)
            f.write(json.dumps(header).encode() + b'\n')
            for _ in range(count):
                f.write(struct.pack('<Qff', 2, 0.5, -0.25))

    def test_exact_payload_and_lock_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'a', Path(tmp) / 'b'
            h = {'config': {}, 'iteration': 210, 'locks': [[4, [0.25]], [1, [0.75]]], 'lock_labels': []}
            self.write(a, b'GTOSOLVE2\n', h, 4)
            h['locks'].reverse()
            self.write(b, b'GTOSOLVE2\n', h, 4)
            self.assertEqual(native(a), native(b))
            raw = bytearray(b.read_bytes())
            raw[-1] ^= 1
            b.write_bytes(raw)
            self.assertNotEqual(native(a), native(b))

    def test_hero_backup_and_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'a'
            self.write(p, b'GTOPREFLOP2\n', {'iteration': 74, 'hero_backup': [3, 70], 'point_locks': []}, 4)
            self.assertEqual(len(native(p)['arrays']), 4)
            p.write_bytes(p.read_bytes()[:-1])
            with self.assertRaises(ValueError):
                native(p)

    def test_solver_mutation_forbidden(self):
        for route in ['/api/solve', '/api/preflop/solve', '/api/stop', '/api/preflop/stop', '/api/spot']:
            with self.assertRaises(ValueError):
                api(1, route, {})


if __name__ == '__main__':
    unittest.main()
