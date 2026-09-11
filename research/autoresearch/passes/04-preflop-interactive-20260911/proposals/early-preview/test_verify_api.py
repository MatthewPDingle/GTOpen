"""Pure runner gates: no servers, network, solver, GPU, or fixture reads."""
import copy
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('preview_api_runner', Path(__file__).with_name('verify_api.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Gates(unittest.TestCase):
    def test_environment_pins_and_removes_experimental_overrides(self):
        with patch.dict(os.environ, {'PREFLOP_EQ_SAMPLES':'7', 'SOLVER_GPU_MEM_MB':'12',
                                     'PREFLOP_GPU_LAYOUT_STATS':'1', 'PREFLOP_MW_B':'1'}, clear=True):
            env = m.environment(Path('private'), 12345, 20000)
        self.assertEqual(env['PREFLOP_EQ_SAMPLES'], '20000')
        self.assertEqual(env['SOLVER_GPU_MEM_MB'], '23000')
        self.assertEqual(env['SOLVER_THREADS'], '16')
        self.assertEqual(env['PORT'], '12345')
        self.assertNotIn('PREFLOP_GPU_LAYOUT_STATS', env)
        self.assertNotIn('PREFLOP_MW_B', env)

    def test_frozen_sample_header_and_hash_are_exact(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'eq.bin'
            path.write_bytes((20000).to_bytes(4,'little') + bytes(169*169*4))
            a = m.equity_cache_record(path)
            self.assertEqual(a['samples'], 20000)
            self.assertEqual(m.fixed_environment(a['samples'])['PREFLOP_EQ_SAMPLES'], '20000')
            path.write_bytes((1024).to_bytes(4,'little') + bytes(169*169*4))
            b = m.equity_cache_record(path)
            self.assertEqual(b['samples'], 1024)
            self.assertNotEqual(a['sha256'], b['sha256'])
            self.assertNotEqual(a['header_sha256'], b['header_sha256'])
            path.write_bytes((0).to_bytes(4,'little') + bytes(169*169*4))
            with self.assertRaises(ValueError): m.equity_cache_record(path)
            path.write_bytes(b'bad')
            with self.assertRaises(ValueError): m.equity_cache_record(path)

    def test_invalid_frozen_sample_count_is_rejected(self):
        for samples in (0, -1, '20000', 0.5, None):
            with self.assertRaises(ValueError): m.fixed_environment(samples)

    def test_small_config_is_pure_and_resizes_all_seat_arrays(self):
        cfg = {'positions':['a']*8, 'posts':[0]*8, 'call_only_seats':[7],
               'open_raises_by_seat':[[2]]*8, 'raise_mults_by_seat':[[3]]*8, 'rake_pct':5}
        original = copy.deepcopy(cfg)
        out = m.config3(cfg)
        self.assertEqual(cfg, original)
        self.assertEqual(out['positions'], ['BTN','SB','BB'])
        self.assertEqual(out['posts'], [0,.5,1])
        self.assertEqual(out['call_only_seats'], [])
        self.assertIsNone(out['open_raises_by_seat'])
        self.assertIsNone(out['raise_mults_by_seat'])
        self.assertEqual(out['rake_pct'], 5)

    def test_publication_requires_real_model_and_completed_snapshot(self):
        p = {'multiway_model':m.FAST, 'published_iteration':2, 'accuracy_iteration':None, 'converged':False}
        self.assertEqual(m.publication({'publication':p}, m.FAST), p)
        for change in ({'published_iteration':1}, {'multiway_model':m.REFERENCE},
                       {'accuracy_iteration':3}, {'converged':True}):
            with self.assertRaises(ValueError):
                m.publication({'publication':dict(p, **change)}, m.FAST)

    def test_path_never_chooses_zero_reach_or_nonblind_call(self):
        actions = [{'kind':'fold','freq':0,'to':0}, {'kind':'call','freq':1,'to':1}]
        self.assertIsNone(m.blind_action({'actor_pos':'BTN','actions':actions}))
        self.assertEqual(m.blind_action({'actor_pos':'SB','actions':actions}), 1)
        raises = [{'kind':'raise','freq':.1,'to':7}, {'kind':'jam','freq':.8,'to':20},
                  {'kind':'raise','freq':.1,'to':3}]
        self.assertEqual(m.blind_action({'actor_pos':'BB','actions':raises}), 2)

    def test_exact_native_and_checkpoint_gates(self):
        status = {k:50 for k in ('iteration','published_iteration','accuracy_iteration')}
        status.update(gaps=[.1], evs=[1], gap_total=.1, target_gap=.005,
                      stop_reason='iteration_limit', multiway_equity_model=m.REFERENCE)
        a = {'completed':True, 'native':{'header':{'iteration':50}, 'arrays':[{'sha256':'abc'}]}, 'final_status':status}
        b = copy.deepcopy(a)
        b['final_status']['elapsed'] = 999
        self.assertTrue(m.compare_reference(a,b)['native_header_and_all_arena_sha_exact'])
        b['native']['arrays'][0]['sha256'] = 'def'
        with self.assertRaises(ValueError): m.compare_reference(a,b)
        b = copy.deepcopy(a)
        b['final_status']['gaps'] = [.10000000001]
        with self.assertRaises(ValueError): m.compare_reference(a,b)


if __name__ == '__main__':
    unittest.main()
