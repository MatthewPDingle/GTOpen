import unittest
from fit import merge, fraction, make_model, distributions, loss, Grouping
import numpy as np

class ModelTests(unittest.TestCase):
    def test_pooling_uses_opportunities_not_hand_weighted_percentages(self):
        c=merge([{'pre/raise|fold':9,'pre/raise|call':1,'vpip|no':10000},
                 {'pre/raise|fold':10,'pre/raise|call':90,'vpip|yes':100}])
        self.assertAlmostEqual(fraction(c,'pre/raise','call'),91/110)

    def test_missing_observation_borrows_pool(self):
        pool={'pre/raise|fold':80,'pre/raise|call':15,'pre/raise|raise':5}
        self.assertAlmostEqual(fraction({},'pre/raise',['call','raise'],pool,100),.2)
        probs=distributions({},pool)
        self.assertAlmostEqual(sum(probs['pre/raise']),1)
        self.assertGreater(loss({'pre/raise|raise':1},probs)[0],0)

    def test_squeeze_uses_cold_opportunities_and_discloses_assumptions(self):
        c={'vpip|yes':25,'vpip|no':75,'pfr|yes':18,'pfr|no':82,
           'pre/squeeze|fold':80,'pre/squeeze|call':10,'pre/squeeze|raise':10,
           'pre/3bet_raiser|fold':60,'pre/3bet_raiser|call':30,'pre/3bet_raiser|raise':10}
        m=make_model('NL25','Pool',c,c,{'date_from':'2025-01-01','date_to':'2025-08-01','players':10})
        self.assertEqual(m['stats']['cont_squeeze'],20)
        self.assertEqual(m['stats']['fourbet'],10)
        self.assertIn('post/river/facing',m['source']['low_sample_fields'])
        self.assertTrue(m['source']['assumptions'])

    def test_rare_and_unseen_bands_map_to_supported_groups(self):
        X=np.zeros((62,11)); X[:30,:2]=[.20,.16]; X[30:60,:2]=[.35,.28]; X[60:,:2]=[.60,.45]
        g=Grouping('behavior_bands',7).fit(X,np.zeros((62,2)),np.ones(62))
        self.assertEqual(g.count,2)
        unknown=np.zeros((1,11)); unknown[0,:2]=[.10,.05]
        self.assertLess(g.predict(unknown)[0],g.count)
        # More production data must not resurrect a discarded rare category.
        more=np.concatenate([X,np.tile(X[-1],(50,1))])
        final=Grouping('behavior_bands',7,g.mapping.tolist()).fit(more,np.zeros((len(more),2)),np.ones(len(more)))
        self.assertEqual(final.count,g.count)

if __name__=='__main__': unittest.main()
