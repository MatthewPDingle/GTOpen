import copy
import unittest
import continuation_policy_stability as subject


def snapshot():
    view=dict(actor=0,actor_pos='UTG',actions=[dict(label='Fold',freq=.5),dict(label='Raise',freq=.5)],
        reach=[1.]*169,strategy=[.5]*338)
    return dict(config={'players':8},iteration=500,gaps=[.0001]*8,views=[dict(path=[],view=view)])


class StabilityTests(unittest.TestCase):
    def test_solver_class_order_suited_has_four_offsuit_twelve(self):
        a=snapshot();b=copy.deepcopy(a)
        # Internal class order is ascending ranks: row > column is suited.
        for s in [a,b]:
            s['views'][0]['view']['reach']=[0.]*169
            s['views'][0]['view']['reach'][13]=1.
            s['views'][0]['view']['reach'][1]=1.
        b['views'][0]['view']['strategy'][13]=1.
        b['views'][0]['view']['strategy'][182]=0.
        self.assertAlmostEqual(subject.changes(a,b)['nodes'][0]['weighted_hand_total_variation'],.125)

    def test_rare_hand_change_visible_without_dominating_weighted_signal(self):
        a=snapshot();b=copy.deepcopy(a);b['iteration']=1000
        for s in [a,b]:s['views'][0]['view']['reach'][0]=.00001
        b['views'][0]['view']['strategy'][0]=1.
        b['views'][0]['view']['strategy'][169]=0.
        result=subject.changes(a,b)
        self.assertEqual(result['nodes'][0]['max_hand_total_variation'],.5)
        self.assertLess(result['nodes'][0]['weighted_hand_total_variation'],.00001)
        self.assertTrue(result['signal_passed'])

    def test_frequency_and_gap_each_fail_independently(self):
        a=snapshot();b=copy.deepcopy(a);b['iteration']=1000
        b['views'][0]['view']['actions'][0]['freq']=.52
        self.assertFalse(subject.changes(a,b)['signal_passed'])
        b=copy.deepcopy(a);b['gaps']=[.01]
        self.assertFalse(subject.changes(a,b)['signal_passed'])

    def test_changed_action_menu_refused(self):
        a=snapshot();b=copy.deepcopy(a)
        b['views'][0]['view']['actions'][0]['label']='Check'
        with self.assertRaises(AssertionError):subject.changes(a,b)

    def test_absent_range_does_not_count_as_stable(self):
        a=snapshot();b=copy.deepcopy(a)
        for s in [a,b]:s['views'][0]['view']['reach']=[0.]*169
        result=subject.changes(a,b)
        self.assertIsNone(result['nodes'][0]['weighted_hand_total_variation'])
        self.assertFalse(result['signal_passed'])


if __name__=='__main__':unittest.main()
