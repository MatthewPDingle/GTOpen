"""Protocol-only controls: no learning, new equity labels, or scientific launch."""
import copy
from itertools import permutations
import json
import unittest
from unittest.mock import patch
import stack_equity_priced_run_v1 as run
from stack_equity_priced_readback_v1 import independently_rebuild_gates
from stack_board_balanced_sampler_v1 import allocation
from stack_price_reference_v1 import board_group


def results(before=.003, after=.0009):
    return [dict(seed=s, arm=a, split='test', score=dict(contexts=[dict(stack=d,
        mean_regret_stack_fraction=v, mean_regret_bb=v * d) for d in (60, 150)]))
        for s in run.SEEDS for a, v in zip(run.comparison.ARMS, (before, after))]


class ProtocolControls(unittest.TestCase):
    def test_board_counts_suit_separation_exclusions_and_stress_quota(self):
        excluded = {board_group([0, 5, 10, 15, 20]), board_group([0, 1, 2, 3, 8])}
        first = run.select_fresh_boards(excluded)
        self.assertEqual(first, run.select_fresh_boards(excluded))
        self.assertEqual(len(first), 320)
        self.assertEqual({s: sum(b['split'] == s for b in first) for s in ('validation', 'test', 'stress')},
                         dict(validation=128, test=128, stress=64))
        groups = set()
        for b in first:
            canonical = min(tuple(sorted(c // 4 * 4 + p[c % 4] for c in b['board'])) for p in permutations(range(4)))
            self.assertEqual(canonical, tuple(b['canonical_group']))
            self.assertNotIn(canonical, excluded | groups)
            groups.add(canonical)
        self.assertEqual({cell: sum(b['split'] == 'stress' and b['cell'] == cell for b in first)
                          for cell in allocation(64)}, allocation(64))

    def test_primary_gate_needs_both_relative_and_per_depth_absolute_pass(self):
        self.assertTrue(all(g['passed'] for g in run.gates(results())))
        self.assertFalse(any(g['passed'] for g in run.gates(results(.0009, .00085))))
        self.assertFalse(any(g['passed'] for g in run.gates(results(.01, .0011))))
        self.assertFalse(any(g['passed'] for g in run.gates(results(0, 0))))
        data = results(.01, 0)
        data[1]['score']['contexts'][0].update(mean_regret_stack_fraction=.0015, mean_regret_bb=.09)
        self.assertFalse(run.gates(data)[0]['passed'])
        self.assertTrue(run.gates(data)[1]['passed'])

    def test_independent_gate_rebuild_and_no_stress_selection(self):
        data = results()
        stress = [dict(t, split='stress') for t in results(.00001, .4)]
        a = run.gates(data + stress)
        b = independently_rebuild_gates(data + stress, run.SEEDS, run.HELDOUT)
        for left, right in zip(a, b):
            for key in ('seed', 'passed', 'absolute_gate'):
                self.assertEqual(left[key], right[key])
            for key in ('baseline', 'candidate'):
                self.assertAlmostEqual(left[key], right[key], places=15)

    def test_missing_depth_is_not_silently_averaged(self):
        data = results()
        data[0]['score']['contexts'].pop()
        with self.assertRaises(AssertionError):
            run.gates(data)
        with self.assertRaises(AssertionError):
            independently_rebuild_gates(data, run.SEEDS, run.HELDOUT)

    def test_preparation_cannot_replace_existing_registration(self):
        with patch.object(run, 'REG', run.ROOT / 'AGENTS.md'):
            with self.assertRaises(AssertionError):
                run.prepare_stage({})

    def test_frozen_spec_cannot_change_at_run(self):
        with patch.object(run, 'read', return_value=dict(seed=1)):
            with self.assertRaises(AssertionError):
                run.run_stage(dict(seed=2))


if __name__ == '__main__':
    unittest.main()
