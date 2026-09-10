import copy
import json
import unittest
import tempfile
import subprocess
import sys
from pathlib import Path

import generate as summary


class SummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixed = json.loads((summary.PASS / 'final-performance.json').read_text())
        cls.extended = json.loads((summary.PASS / 'extended-convergence-comparisons.json').read_text())

    def test_existing_frozen_evidence_and_headlines(self):
        report = summary.generate()
        rows = report['gpu_fixed_work']['comparisons']
        self.assertEqual([round(r['iteration_ms']['reduction_percent'], 1) for r in rows], [44.3, 51.5, 51.0, 47.3])
        results = {r['fixture']: r for r in report['gpu_accuracy_targets']['comparisons']}
        self.assertEqual(round(results['modeled']['reduction_percent'], 1), 45.8)
        self.assertEqual(results['eight']['additional_iterations'], 850)
        self.assertEqual(results['eight']['final_native_iteration'], 1024)
        self.assertEqual(round(results['eight']['trajectory_minutes']['original'], 2), 113.56)
        self.assertEqual(round(results['eight']['trajectory_minutes']['final'], 2), 58.85)
        self.assertTrue(report['test_suites']['counts_overlap_not_unique'])

    def test_primary_fail_closed(self):
        cases = [self.fixed[:-1]]
        for field, value in [('exact', False), ('exact', None)]:
            rows = copy.deepcopy(self.fixed); rows[0][field] = value; cases.append(rows)
        rows = copy.deepcopy(self.fixed); rows[0]['iteration_ms']['original'] = float('nan'); cases.append(rows)
        rows = copy.deepcopy(self.fixed); rows[0]['iteration_ms']['reduction_percent'] += 1; cases.append(rows)
        for rows in cases:
            with self.subTest(rows=rows[0].get('control')):
                with self.assertRaises(ValueError): summary.fixed_work(rows)

    def test_extended_fail_closed(self):
        cases = [self.extended[:-1]]
        for field, value in [('exact_trajectory_and_final_state', False), ('final_mismatches', ['gaps'])]:
            rows = copy.deepcopy(self.extended); rows[0][field] = value; cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['original']['result'] = None; cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['matched_checkpoints'].pop(); cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['matched_checkpoints'][0]['exact'] = False; cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['candidate']['checkpoints'][0]['gaps'][0] += 1; cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['candidate']['result']['converged'] = False; cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['candidate']['result']['roundtrip_verified'] = False; cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['candidate']['result']['learning_gap_bb'] = 99; cases.append(rows)
        rows = copy.deepcopy(self.extended); rows[0]['candidate']['error'] = 'timeout'; cases.append(rows)
        for i, rows in enumerate(cases):
            with self.subTest(case=i):
                with self.assertRaises(ValueError): summary.accuracy(rows)

    def test_fresh_miss_remains_a_miss(self):
        rows = json.loads((summary.PASS / 'fresh-eight-comparisons.json').read_text())
        if len(rows) == 2:
            rows.append(copy.deepcopy(rows[1])); rows[-1]['pair'] = 3
        result = summary.fresh_qualifier(rows)
        self.assertTrue(all(not pair['target_reached'] for pair in result['pairs']))
        with self.assertRaises(ValueError): summary.fresh_qualifier(rows[:-1])
        rows[0]['exact_checkpoints_and_native'] = False
        with self.assertRaises(ValueError): summary.fresh_qualifier(rows)

    def test_optional_api_requires_exact_finite_pair(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'api.json'
            value = {'full_native_exact': True, 'fixed_pair_only': True,
                     'first_checkpoint_seconds': {'original': 3.0, 'candidate': 2.0},
                     'first_strategy_response_seconds': {'original': 3.1, 'candidate': 2.1},
                     'interpretation': 'Synthetic unit fixture; never publish these numbers.'}
            path.write_text(json.dumps(value))
            self.assertIn('optional_api', summary.generate(api_summary=path))
            value['full_native_exact'] = False; path.write_text(json.dumps(value))
            with self.assertRaises(ValueError): summary.generate(api_summary=path)
            value['full_native_exact'] = True
            value['first_checkpoint_seconds']['original'] = float('inf'); path.write_text(json.dumps(value))
            with self.assertRaises(ValueError): summary.generate(api_summary=path)

    def test_output_never_overwrites_existing_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'protected.json'; path.write_text('preserve me')
            result = subprocess.run([sys.executable, str(summary.HERE/'generate.py'), '--output', str(path)], capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(path.read_text(), 'preserve me')


if __name__ == '__main__':
    unittest.main()
