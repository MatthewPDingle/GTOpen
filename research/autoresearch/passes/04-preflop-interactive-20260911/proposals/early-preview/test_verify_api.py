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
    def test_stopped_evaluation_rejects_cancellation_zeros_and_invalid_arrays(self):
        row={'iteration':2,'gaps':[0.1,0.2,0.3],'evs':[-0.5,0.1,0.4]}
        m.validate_small_evaluation(row,2,True)
        for invalid in (dict(row,iteration=3),dict(row,evs=[0,0,0]),
                        dict(row,gaps=[0,0]),dict(row,evs=[0,float('nan'),1]),
                        dict(row,gaps=[0,float('inf'),0]),dict(row,evs=[True,0,1])):
            with self.assertRaises(ValueError): m.validate_small_evaluation(invalid,2,True)

    def test_resume_requires_exact_fifty_new_iterations_and_fresh_accuracy(self):
        row={'iteration':57,'published_iteration':57,'accuracy_iteration':57,'state':'done',
             'gaps':[.1,.2,.3],'evs':[-.5,.1,.4]}
        m.validate_small_resume(row,7)
        for change in ({'iteration':50},{'published_iteration':7},{'accuracy_iteration':7},
                       {'state':'stopped'},{'gpu_note':'fallback'},{'preview_note':'stale'},
                       {'error':'failure'},{'evs':[0,float('inf'),1]}):
            with self.assertRaises(ValueError): m.validate_small_resume(dict(row,**change),7)

    def test_production_cases_are_explicit_reference_only(self):
        self.assertEqual(m.selected_cases(False),list(m.CASES))
        self.assertEqual(m.selected_cases(True),['reference-control','reference-preview','small-api'])
        for case in m.selected_cases(True): self.assertEqual(m.case_model(case,True),m.REFERENCE)
        self.assertEqual(m.case_model('small-api',False),m.FAST)
        with self.assertRaises(ValueError): m.selected_cases(True,['fast-preview'])
        with self.assertRaises(ValueError): m.case_model('fast-preview',True)
        with self.assertRaises(ValueError): m.selected_cases(True,[])
        with self.assertRaises(ValueError): m.selected_cases(True,['small-api','small-api'])

    def test_production_capabilities_and_invalid_models_are_strict(self):
        caps={'early_preview_v1':True,'fresh_build_multiway_models':[m.REFERENCE]}
        m.validate_capabilities(caps,True)
        for models in ([],[m.FAST],[m.REFERENCE,m.FAST],[m.REFERENCE,m.REFERENCE],
                       [m.REFERENCE,'coupled_preview128_v1']):
            with self.assertRaises(ValueError):
                m.validate_capabilities(dict(caps,fresh_build_multiway_models=models),True)
        with self.assertRaises(ValueError): m.validate_capabilities(dict(caps,early_preview_v1=False),True)
        m.validate_capabilities(dict(caps,fresh_build_multiway_models=[m.REFERENCE,m.FAST]),False)
        queries=m.invalid_build_queries(True)
        self.assertIn('multiway_model=coupled_preview64_v1',queries)
        self.assertIn('multiway_model=coupled_preview128_v1',queries)
        self.assertEqual(len(m.invalid_build_queries(False)),3)

    def test_production_source_and_web_are_taken_from_selected_worktree(self):
        with tempfile.TemporaryDirectory() as folder:
            lab,prod=Path(folder)/'lab',Path(folder)/'production'
            for root,content in ((lab,'research'),(prod,'reference-only')):
                (root/'web').mkdir(parents=True)
                (root/'web/app.js').write_text(content)
                (root/'source.rs').write_text(content)
            with patch.object(m,'LAB',lab),patch.object(m,'PRODUCTION',prod),patch.object(m,'SOURCES',('source.rs',)):
                a,b=m.source_record(False),m.source_record(True)
                self.assertEqual(b['source_worktree'],str(prod.resolve()))
                self.assertEqual(b['web_source'],str((prod/'web').resolve()))
                self.assertNotEqual(a['web_sha256'],b['web_sha256'])
                self.assertNotEqual(a['current_worktree_source_sha256'],b['current_worktree_source_sha256'])
                for root in (lab,prod):
                    self.assertEqual(m.validate_production_binary_path(root/'target/release/gto-server.exe'),
                                     (root/'target/release/gto-server.exe').resolve())
                with self.assertRaises(ValueError): m.validate_production_binary_path(Path(folder)/'gto-server.exe')
                with self.assertRaises(ValueError): m.validate_production_binary_path(prod/'target/not-server.exe')

    def test_request_log_freezes_incremental_paths_and_nested_inputs(self):
        path = []
        body = {'path':path,'settings':{'sizes':[2,3]}}
        first = m.recorded_body(body)
        path.append(0)
        second = m.recorded_body(body)
        path.append(1)
        body['settings']['sizes'].append(5)
        self.assertEqual(first, {'path':[], 'settings':{'sizes':[2,3]}})
        self.assertEqual(second, {'path':[0], 'settings':{'sizes':[2,3]}})

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
