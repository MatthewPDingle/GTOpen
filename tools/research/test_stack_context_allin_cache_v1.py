"""Role-reversal and exact-count transport checks using tiny synthetic records."""
import copy
import itertools
import unittest
from stack_context_allin_cache_v1 import expand,reverse_key,native_row,BOARDS,canonical
from stack_context_allin_cache_readback_v1 import orbit
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown


class AllinExtensionTests(unittest.TestCase):
    def test_reversal_involution_and_suit_equivalence(self):
        for cards in ([0,1,4,5],[0,5,10,15],[0,4,1,8],[48,49,0,4]):
            key=canonical(cards);reverse=reverse_key(key)
            self.assertEqual(reverse,min(orbit(key[2:]+key[:2])))
            self.assertEqual(reverse_key(reverse),key)
            for p in itertools.permutations(range(4)):
                relabeled=[4*(c//4)+p[c%4] for c in cards]
                self.assertEqual(canonical(relabeled),key)

    def test_integer_counts_reverse_and_reject_conflicts(self):
        key=canonical([0,1,48,49]);other=reverse_key(key)
        row=dict(private_cards=list(key),wins=123,ties=456,losses=BOARDS-579,boards=BOARDS)
        result=expand({key:row})
        self.assertEqual(result[other]['wins'],row['losses'])
        self.assertEqual(result[other]['losses'],row['wins'])
        self.assertEqual(expand(result),result)
        bad=copy.deepcopy(result);bad[other]['wins']+=1
        with self.assertRaises(ValueError):expand(bad)

    def test_native_transport_rejects_bad_identity_counts_and_sample_score(self):
        key=canonical([0,1,48,49]);board=[2,3,4,5,6]
        winner=showdown(list(key)+board);score=1 if winner<0 else 2 if winner==0 else 0
        case=dict(private_cards=list(key),sampled_boards=[board])
        row=dict(private_cards=list(key),wins=123,ties=456,losses=BOARDS-579,exact_boards=BOARDS,
                 equity=(123+.5*456)/BOARDS,sampled_scores=[score])
        self.assertEqual(native_row(case,row)['boards'],BOARDS)
        for field,value in (('private_cards',[0,2,48,49]),('wins',124),('sampled_scores',[(score+1)%3])):
            bad=dict(row,**{field:value})
            with self.assertRaises(ValueError):native_row(case,bad)


if __name__=='__main__':unittest.main()
