import json
import struct
import tempfile
import unittest
from pathlib import Path
import numpy as np
import continuation_warp_summary as model


class WarpSummaryChecks(unittest.TestCase):
    def save(self,path,values,iteration=150):
        with path.open('wb') as stream:
            stream.write(b'GTOPREFLOP4\n')
            stream.write((json.dumps(dict(iteration=iteration))+'\n').encode())
            for array in values:
                stream.write(struct.pack('<Q',len(array)))
                stream.write(np.array(array,dtype='<f4').tobytes())

    def test_full_save_comparison_distinguishes_tolerance_from_exactness(self):
        with tempfile.TemporaryDirectory() as folder:
            a=Path(folder)/'a';b=Path(folder)/'b'
            self.save(a,[[1.,0.,-10.],[2.,3.,4.]])
            self.save(b,[[1.000002,0.,-10.],[2.,3.,4.]])
            result=model.compare(a,b)
            self.assertTrue(result['passed']);self.assertFalse(result['all_numeric_entries_equal'])
            self.assertEqual(sum(r['changed'] for r in result['arenas']),1)
            self.assertTrue(model.compare(a,a)['all_numeric_entries_equal'])
            self.save(b,[[1.001,0.,-10.],[2.,3.,4.]])
            self.assertFalse(model.compare(a,b)['passed'])

    def test_full_save_comparison_rejects_metadata_or_nonfinite_values(self):
        with tempfile.TemporaryDirectory() as folder:
            a=Path(folder)/'a';b=Path(folder)/'b'
            self.save(a,[[1.],[2.]]);self.save(b,[[1.],[2.]],iteration=151)
            with self.assertRaises(AssertionError):model.compare(a,b)
            self.save(b,[[float('nan')],[2.]])
            with self.assertRaises(AssertionError):model.compare(a,b)

    def test_export_retains_feature_and_chance_math(self):
        original=(model.runtime.OLD/'interface.cu').read_text()
        helper=(model.study.ROOT/'tools/research/continuation_warp_summary.cuh').read_text()
        generated=model.source(original,helper)
        # Entire raw-equity and correction suffix must be unchanged.
        marker=' for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169;double den=0.,num=0.;'
        self.assertEqual(original.split(marker,1)[1],generated.split(marker,1)[1])
        self.assertIn('if(threadIdx.x<64)describe_warp',generated)
        self.assertNotIn('if(threadIdx.x<2){int s=threadIdx.x;for(int j=0;j<5;j++)desc',generated)


if __name__=='__main__':unittest.main()
