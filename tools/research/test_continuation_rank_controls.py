import itertools
import unittest
import numpy as np
import continuation_rank_controls as run


class RankMomentTests(unittest.TestCase):
    def test_moments_against_all_physical_flops(self):
        # Concrete private cards: AA/KK, AK/AQ, 22/23, KQ/KQ with no overlap.
        fixtures=[([48,49],[44,45]),([48,45],[49,42]),([0,1],[2,4]),([44,40],[45,41])]
        for hero,opponent in fixtures:
            excluded=set(hero+opponent);deck=[c for c in range(52) if c not in excluded]
            hi=max(c//4 for c in hero);lo=min(c//4 for c in hero)
            ranks=np.bincount([c//4 for c in deck],minlength=13)
            counts=np.zeros(8);n=0
            for board in itertools.combinations(deck,3):
                counts+=run.board_features([c//4 for c in board],hi,lo);n+=1
            self.assertEqual(n,17296)
            np.testing.assert_allclose(counts/n,run.expected_concrete(ranks,hi,lo),atol=2e-15,rtol=0)

    def test_range_moments_reduce_to_single_opponent_class(self):
        moments=run.moments();counts,_=run.study.pilot.matrices()
        k=run.study.pilot.INDEX['AKs'];weights=np.zeros(169);weights[k]=1
        compatible=counts*weights[None,:]
        actual=np.einsum('hk,hkf->hf',compatible,moments)/compatible.sum(axis=1)[:,None]
        np.testing.assert_allclose(actual,moments[:,k],atol=2e-15,rtol=0)
        self.assertTrue(np.isfinite(moments).all() and (moments>=0).all() and (moments<=1).all())


if __name__=='__main__':unittest.main()
