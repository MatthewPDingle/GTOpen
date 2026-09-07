import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import overnight_reports as queue


class OvernightTests(unittest.TestCase):
    def test_unconverged_ranges_are_not_exported(self):
        with patch.object(queue, 'call', return_value={'state': 'done', 'gap_total': .2}):
            with self.assertRaisesRegex(RuntimeError, 'did not converge'):
                queue.solve(3000, target=.05)

    def test_failed_backup_prevents_replacement(self):
        calls = []
        def api(path, body=None):
            calls.append(path)
            if path.endswith('/status'): return {'state': 'done'}
            raise RuntimeError('disk full')
        with patch.object(queue, 'call', side_effect=api):
            with self.assertRaisesRegex(RuntimeError, 'disk full'):
                with queue.preserve_lab('unique-backup'):
                    self.fail('must not replace a session after a failed save')
        self.assertEqual(calls, ['/api/preflop/status', '/api/preflop/save'])

    def test_restores_session_after_preparation_failure(self):
        with patch.object(queue, 'call', return_value={'state': 'idle'}) as api:
            with self.assertRaisesRegex(RuntimeError, 'bad spot'):
                with queue.preserve_lab('unique-backup'):
                    raise RuntimeError('bad spot')
        self.assertEqual(api.call_args.args, ('/api/preflop/load', {'name': 'unique-backup'}))

    def test_saved_settings_are_used_without_old_game_defaults(self):
        scenario = dict(name='My 2/2', players=8, stack=173, ante=.1, limp=True,
                        opens='5,7.5,10', mult='3,5,7', maxRaises=3, allin=True,
                        rakePct=10, rakeCap=9, realization='raw')
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / 'settings.json'
            settings.write_text(json.dumps({'2-2': scenario['name']}))
            with patch.object(queue, 'SETTINGS', settings), patch.object(queue.subprocess, 'run'), \
                    patch.object(queue, 'call', return_value=[scenario]):
                name, config = queue.saved_games(['2-2'])['2-2']
        self.assertEqual(name, scenario['name'])
        self.assertEqual(config['stack'], 173)
        self.assertEqual(config['open_raises'], [5, 7.5, 10])
        self.assertEqual(config['raise_mults'], [3, 5, 7])
        self.assertEqual(config['realization'], 'raw')
        self.assertTrue(config['add_allin'])

    def test_ambiguous_scenario_is_not_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(queue, 'SETTINGS', Path(tmp)/'absent.json'), \
                    patch.object(queue.subprocess, 'run'), \
                    patch.object(queue, 'call', return_value=[{'name':'2/2 A'}, {'name':'2/2 B'}]):
                with self.assertRaisesRegex(ValueError, 'found 2'):
                    queue.saved_games(['2-2'])

    def test_partial_report_is_reported_as_failure(self):
        def api(path, body=None):
            if path.endswith('/status'): return {'running':False, 'name':'report', 'error':''}
            if path.endswith('/get'): return {'complete':False}
            return {'ok':True}
        with patch.object(queue, 'call', side_effect=api):
            with self.assertRaisesRegex(RuntimeError, '1 reports failed'):
                queue.run_reports([('report', {'name':'report'})])

    def test_completion_uses_report_file_not_status_schema(self):
        def api(path, body=None):
            if path.endswith('/status'): return {'running':False, 'name':'report', 'done':184, 'total':184}
            if path.endswith('/get'): return {'complete':True}
            return {'ok':True}
        with patch.object(queue, 'call', side_effect=api):
            queue.run_reports([('report', {'name':'report'})])


if __name__ == '__main__':
    unittest.main()
