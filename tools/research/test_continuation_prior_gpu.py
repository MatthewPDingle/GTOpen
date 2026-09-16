import re
import unittest
import numpy as np
import continuation_prior_gpu as gpu


class CachedPriorChecks(unittest.TestCase):
    def test_serialized_matrix_order_and_float32_roundtrip(self):
        model=gpu.study.read(gpu.prior.OUT/'candidate.json')
        source=gpu.source(model,'test')
        body=source.split('prior_shares[57122] = {\n',1)[1].split('\n};',1)[0]
        numbers=np.array([float(t.rstrip('f')) for t in re.split(r',\s*',body)],dtype=np.float32)
        np.testing.assert_array_equal(numbers,gpu.cached_shares(model))
        _,eq=gpu.study.pilot.matrices();q=np.array(model['class_base'])
        for side in range(2):
            p=.92 if side==0 else 1.08
            for h,j in [(0,168),(168,0),(40,90),(35,35)]:
                a=eq[h,j]*q[h]*p;b=(1-eq[h,j])*q[j]*(2-p)
                self.assertEqual(numbers[side*169*169+j*169+h],np.float32(a/(a+b)))
        self.assertNotIn('__FEATURE_EXPRESSION__',source)
        self.assertNotIn('summary[16]',source)


if __name__=='__main__':unittest.main()
