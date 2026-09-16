import json
from pathlib import Path
import struct
import tempfile
import unittest
import numpy as np
import continuation_save_parity as parity


def write(path,regrets,sums,iteration=150):
    with path.open('wb') as f:
        f.write(b'GTOPREFLOP4\n')
        f.write((json.dumps(dict(iteration=iteration,hero_backup=None,config={'realization':'balanced'}))+'\n').encode())
        for values in [regrets,sums]:
            f.write(struct.pack('<Q',len(values)));f.write(np.asarray(values,dtype='<f4').tobytes())


class SaveParityTests(unittest.TestCase):
    def test_all_entries_including_after_chunk_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'a';b=Path(directory)/'b'
            values=np.arange(1048580,dtype=np.float32)
            write(a,values,[0,1]);write(b,values,[0,1])
            self.assertTrue(parity.compare(a,b)['byte_identical'])
            values[-1]+=1;write(b,values,[0,1])
            result=parity.compare(a,b)
            self.assertFalse(result['all_numeric_entries_equal'])
            self.assertEqual(result['arenas'][0]['changed'],1)
            self.assertEqual(result['arenas'][0]['max_absolute_change'],1)

    def test_malformed_or_different_save_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'a';b=Path(directory)/'b'
            write(a,[1],[2]);write(b,[1],[2],149)
            with self.assertRaises(AssertionError):parity.compare(a,b)
            write(b,[float('nan')],[2])
            with self.assertRaises(AssertionError):parity.compare(a,b)
            write(b,[1],[2]);b.write_bytes(b.read_bytes()[:-1])
            with self.assertRaises(AssertionError):parity.compare(a,b)


if __name__=='__main__':unittest.main()
