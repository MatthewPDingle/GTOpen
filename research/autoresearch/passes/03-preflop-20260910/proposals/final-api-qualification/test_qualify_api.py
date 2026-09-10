import datetime as dt
import hashlib
import unittest
from qualify_api import checkpoint, strict_comparator, zero_hash, require_pair_time, DEADLINE, FIXED_ENV


class QualificationTests(unittest.TestCase):
    def test_pair_deadline_reserves_two_cases_and_comparator(self):
        require_pair_time(DEADLINE - dt.timedelta(seconds=1260))
        require_pair_time(DEADLINE - dt.timedelta(seconds=1261))
        with self.assertRaises(ValueError):
            require_pair_time(DEADLINE - dt.timedelta(seconds=1259.999))

    def test_equity_samples_override_inherited_environment(self):
        env = {'PREFLOP_EQ_SAMPLES': '3'}
        env.update(FIXED_ENV)
        self.assertEqual(env['PREFLOP_EQ_SAMPLES'], '1024')
        self.assertEqual(env['SOLVER_GPU_MEM_MB'], '23000')

    def test_publication_requires_completed_measurement(self):
        good = {'iteration': 50, 'phase': 'iterating', 'gaps': [1.0]*8, 'evs': [1.0]*8}
        self.assertTrue(checkpoint(good))
        for change in [{'iteration':49}, {'phase':'measuring'}, {'gaps':[]}, {'evs':[]}]:
            self.assertFalse(checkpoint({**good, **change}))

    def test_zero_arena_hash(self):
        for n in [0, 1, 169, 300000]:
            self.assertEqual(zero_hash(n), hashlib.sha256(bytes(n*4)).hexdigest())

    def test_exact_acceptance_not_aggregate_tolerance(self):
        stats = {'entries': 3, 'bit_equal':3, 'finite_pairs':3, 'max_abs':0, 'max_ulp':0}
        result = {'headers_identical_after_point_lock_order_canonicalization':True,
                  'all_compared_values_finite':True, 'invalid_effective_entries':0,
                  'invalid_reach_classes':0, 'iteration':50, 'payoff_model':'coupled_deck_v1',
                  'raw_arenas': {'regrets':dict(stats), 'strategy_sums':dict(stats)},
                  'effective_average_strategy':dict(stats), 'raw_arena_normalized_strategy':dict(stats)}
        strict_comparator(result)
        result['effective_average_strategy']['bit_equal'] = 2
        with self.assertRaises(ValueError):
            strict_comparator(result)


if __name__ == '__main__':
    unittest.main()
