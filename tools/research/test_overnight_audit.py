import copy
import json
import math
import unittest

import numpy as np
import audit_continuation_overnight as audit
import continuation_overnight as night
import range_value_pilot as pilot


class OvernightAuditTests(unittest.TestCase):
    def test_checkpoint_comparison_accepts_only_round_trip_noise(self):
        expected={'stack':121.73913043478261,'range':'AA:0.1','path':[1,2]}
        actual=copy.deepcopy(expected);actual['stack']=121.7391304347826
        self.assertTrue(audit.same_job(actual,expected))
        actual['stack']=math.nextafter(actual['stack'],-math.inf)
        self.assertFalse(audit.same_job(actual,expected))
        for key,value in [('stack',float('nan')),('stack',120.0),
                          ('range','AA:0.2'),('path',[1,2,0]),('path',[True,2])]:
            actual=copy.deepcopy(expected);actual[key]=value
            self.assertFalse(audit.same_job(actual,expected))
        actual=copy.deepcopy(expected);actual['extra']=0
        self.assertFalse(audit.same_job(actual,expected))

    def test_no_board_matches_independent_concrete_deal_enumeration(self):
        counts,_=pilot.matrices()
        np.testing.assert_array_equal(audit.compatible_counts(''),counts)

    def test_removed_cards_and_suit_permutation(self):
        counts=audit.compatible_counts('AcAdAh')
        aa=pilot.INDEX['AA']
        self.assertFalse(counts[aa].any())
        np.testing.assert_array_equal(counts,audit.compatible_counts('AcAdAs'))
        # Remaining AA is a single concrete combo on an AAx board; it cannot
        # be dealt to both players at once.
        self.assertEqual(audit.compatible_counts('AcAd2h')[aa,aa],0)

    def test_detects_forged_hand_mass_in_a_real_checkpoint(self):
        m=night.checked_manifest();job=m['jobs'][0]
        cases=json.loads((night.OUT/'fixtures.json').read_text())['cases']
        case=next(c for c in cases if c['id']==job['case'])
        result=json.loads((night.OUT/'jobs'/f"{job['id']}.json").read_text())
        audit.check_reference(result,job,m,case)
        bad=copy.deepcopy(result);bad['hands'][0][0]['pair_mass']*=1.1
        with self.assertRaises(AssertionError):audit.check_reference(bad,job,m,case)


if __name__=='__main__':unittest.main()
