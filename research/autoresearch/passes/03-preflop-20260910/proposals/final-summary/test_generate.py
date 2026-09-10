import copy
import json
import unittest
import tempfile
import subprocess
import sys
import gzip
from unittest.mock import patch
from pathlib import Path

import generate as summary


class SummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixed = json.loads((summary.PASS / 'final-performance.json').read_text())
        cls.extended = json.loads((summary.PASS / 'extended-convergence-comparisons.json').read_text())

    def setUp(self):
        original_reader = summary.read_json
        def lightweight_reader(path):
            if path.parent.name == 'raw' and path.name.startswith(('api-auto-modeled-b-', 'api-modeled23000-a-')):
                side = 'original' if '-original.' in path.name else 'candidate'
                return {'case': {'side': side}, 'completed': True, 'loaded_native_exact': True, 'error': None,
                        'guard_failures': [], 'timed_out': False, 'loaded_native': {'header': {'iteration': 0}},
                        'native': {'header': {'iteration': 2}}}
            return original_reader(path)
        self.reader_patch = patch.object(summary, 'read_json', side_effect=lightweight_reader)
        self.reader_patch.start()
        self.addCleanup(self.reader_patch.stop)

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

    def test_compressed_json_reader_preserves_exact_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'source.json.gz'
            evidence = {'value': 0.3144274950027466, 'nested': [True, None, {'iteration': 2}]}
            with gzip.open(path, 'wt', encoding='utf-8') as stream: json.dump(evidence, stream)
            self.assertEqual(summary.read_json(path), evidence)

    def test_budget_qualification_rejects_invalid_published_outcomes(self):
        name = 'api-modeled23000-a.json'
        original = json.loads((summary.PASS/name).read_text())
        cases = []
        for field, value in [('full_native_exact', False), ('outcome', 'candidate_only_completed'), ('candidate_requested_budget_mb', 23924)]:
            row = copy.deepcopy(original); row[field] = value; cases.append(row)
        row = copy.deepcopy(original); del row['cases']['original']; cases.append(row)
        for field, value in [('completed', False), ('timed_out', True), ('error', 'timeout'), ('guard_failures', ['owner changed']), ('loaded_native_exact', False)]:
            row = copy.deepcopy(original); row['cases']['original'][field] = value; cases.append(row)
        for field, value in [('multiway_batch', 32), ('hu_equity_cache_enabled', True), ('planned_need_mb', 23001), ('multiway_particles', 512)]:
            row = copy.deepcopy(original); row['candidate_layout'][field] = value; cases.append(row)
        row = copy.deepcopy(original); row['first_checkpoint_seconds']['candidate'] = float('nan'); cases.append(row)
        row = copy.deepcopy(original); row['cases']['original']['publication_interval_lower_seconds'] = 999; cases.append(row)
        row = copy.deepcopy(original); row['original_resolved_budget']['budget_mb'] = 23924; cases.append(row)
        row = copy.deepcopy(original); row['cases']['original']['layout']['multiway_batch'] = 32; cases.append(row)
        row = copy.deepcopy(original); row['start_native_iteration'] = 0; row['final_native_iteration'] = 50; cases.append(row)
        for index, row in enumerate(cases):
            with self.subTest(case=index):
                with self.assertRaises(ValueError): summary.budget_qualifier(row, name)
        raw = {'case': {'side': 'original'}, 'completed': True, 'loaded_native_exact': True, 'error': None,
               'guard_failures': [], 'timed_out': False, 'loaded_native': {'header': {'iteration': 0, 'profiles': [1]}},
               'native': {'header': {'iteration': 2, 'profiles': [1]}}}
        for field, value in [('case', {'side': 'candidate'}), ('completed', False), ('loaded_native_exact', False),
                             ('error', 'failed'), ('timed_out', True), ('guard_failures', ['failure'])]:
            row = copy.deepcopy(raw); row[field] = value
            with self.subTest(raw=field):
                with self.assertRaises(ValueError): summary.budget_raw_case(row, 'original')
        for section, field, value in [('loaded_native', 'iteration', 1), ('native', 'iteration', 50), ('native', 'profiles', [2])]:
            row = copy.deepcopy(raw); row[section]['header'][field] = value
            with self.subTest(section=section, field=field):
                with self.assertRaises(ValueError): summary.budget_raw_case(row, 'original')


if __name__ == '__main__':
    unittest.main()
