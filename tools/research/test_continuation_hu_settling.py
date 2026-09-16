import copy
import unittest
from continuation_hu_settling import validate


class HeadsUpChecks(unittest.TestCase):
    def test_hu_root_prior_and_equal_work_required(self):
        s = dict(config={'stack': 40}, model='candidate', iteration=1500,
                 start_iteration=500, warmup_iterations=0, gaps=[.001, .002], evs=[.1, -.1],
                 plan=dict(contexts=1, entries=[0], seats=[1, 0]))
        validate(s, s['config'], 'candidate', 1500)
        for field, value in [('entries', [5]), ('contexts', 2), ('seats', [0, 1])]:
            bad = copy.deepcopy(s); bad['plan'][field] = value
            with self.assertRaises(AssertionError): validate(bad, s['config'], 'candidate', 1500)
        with self.assertRaises(AssertionError): validate(dict(s, warmup_iterations=50), s['config'], 'candidate', 1500)

    def test_nonfinite_and_wrong_fixture_refused(self):
        s = dict(config={'stack': 100}, model='original', iteration=500,
                 start_iteration=0, warmup_iterations=0, gaps=[.01, .02], evs=[.2, -.2])
        validate(s, s['config'], 'original', 500)
        with self.assertRaises(AssertionError): validate(dict(s, gaps=[float('nan'), .02]), s['config'], 'original', 500)
        with self.assertRaises(AssertionError): validate(s, {'stack': 40}, 'original', 500)


if __name__ == '__main__': unittest.main()
