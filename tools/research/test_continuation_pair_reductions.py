import unittest
from unittest.mock import patch
import numpy as np
import continuation_pair_reductions as reduction


class PairReductionChecks(unittest.TestCase):
    def test_rank_shortcut_matches_physical_pair_compatibility(self):
        pilot=reduction.study.pilot;counts,_=pilot.matrices();k=counts/pilot.COMBOS[:,None]/pilot.COMBOS[None,:]
        rng=np.random.default_rng(20260917)
        for alpha in [.01,.1,1.,100.]:
            for _ in range(10):
                d=rng.dirichlet(np.full(169,alpha),size=2)
                rank=reduction.rank_mass(d[1]);actual=[]
                for h in range(169):
                    a,b=divmod(h,13);incidence=3 if a==b or a<b else 1
                    actual.append(1-4*incidence/pilot.COMBOS[h]*(rank[a]+(rank[b] if b!=a else 0))+d[1,h]/pilot.COMBOS[h])
                np.testing.assert_allclose(actual,k@d[1],atol=2e-15,rtol=0)
                self.assertAlmostEqual(float(d[0]@actual),float(d[0]@k@d[1]),delta=2e-15)

    def test_source_replacement_preserves_every_prediction_term(self):
        helper=(reduction.study.ROOT/'tools/research/continuation_pair_reductions.cuh').read_text()
        for parent in [reduction.double.OUT,reduction.mixed.OUT]:
            before=(parent/'warp/interface.cu').read_text();after=reduction.source(before,helper)
            start='  // Export substitutes dist references';end=' __syncthreads();if(threadIdx.x==0){center=0.;'
            body=before.split(start)[1].split(end)[0]
            self.assertIn(start+body,after)
            self.assertIn('double pair_total=pair_block_sum(pair_value)',after)
            self.assertIn('double center_total=pair_block_sum(center_value)',after)
            self.assertEqual(after.count('extern "C" __global__ void interface_terminal('),1)
            with self.assertRaises(AssertionError):reduction.source(after,helper)

    def test_another_reduction_controller_blocks_launch(self):
        with patch.object(reduction.mixed.transfer.queue,'processes',return_value=[
                dict(ProcessId=-1,Name='python.exe',CommandLine='python continuation_pair_reductions.py benchmark')]):
            with self.assertRaisesRegex(AssertionError,'controller'):reduction.command([],None)


if __name__=='__main__':unittest.main()
