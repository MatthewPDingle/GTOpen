import unittest
from pathlib import Path
from qualify_auto import checkpoint, comparable, parse_layout, case_environment, strict_comparator, first_difference, verify_loaded_native, require_requested_budget

class AutoTests(unittest.TestCase):
    def test_profile_diagnostic_retains_exact_values(self):
        a=[{'call':[0.10000000149011612]}];b=[{'call':[0.1]}]
        d=first_difference(a,b)
        self.assertEqual(d['path'],'seat_profiles[0].call[0]')
        self.assertEqual(d['mismatch_type'],'value')
        self.assertEqual(d['api_value'],0.10000000149011612)
        self.assertEqual(d['native_value'],0.1)
        self.assertEqual(first_difference([0],[0.0])['mismatch_type'],'type')
        self.assertIsNone(first_difference(a,a))

    def test_native_gate_rejects_profile_or_arena_change(self):
        x={'header':{'hero':None,'seat_profiles':[{'call':[0.1]}]},'arrays':[{'sha256':'a'}]}
        verify_loaded_native(x,x)
        with self.assertRaises(ValueError):
            verify_loaded_native(x,{**x,'arrays':[{'sha256':'b'}]})
        with self.assertRaises(ValueError):
            verify_loaded_native(x,{**x,'header':{'hero':None,'seat_profiles':[{'call':[0.10000000149011612]}]}})

    def test_explicit_candidate_budget_is_only_frozen23000(self):
        env=case_environment({'SOLVER_GPU_MEM_MB':'19000'},23000,30001,Path('private'))
        self.assertEqual(env['SOLVER_GPU_MEM_MB'],'23000')
        require_requested_budget({'budget_mb':23000},23000)
        with self.assertRaises(ValueError): require_requested_budget({'budget_mb':23924},23000)
        with self.assertRaises(ValueError): require_requested_budget({'budget_mb':19000},19000)
        require_requested_budget({'budget_mb':23924},None)

    def test_original_observed_cap_is_not_replaced_by23000(self):
        env=case_environment({'SOLVER_GPU_MEM_MB':'23000','OTHER_OPTION':'retained'},23924,30002,Path('private'))
        self.assertEqual(env['SOLVER_GPU_MEM_MB'],'23924')
        self.assertEqual(env['OTHER_OPTION'],'retained')

    def test_actual_auto_removes_inherited_cap(self):
        env=case_environment({'SOLVER_GPU_MEM_MB':'19000','PREFLOP_EQ_SAMPLES':'7','PREFLOP_MW_MODEL':'wrong'},None,30001,Path('private'))
        self.assertNotIn('SOLVER_GPU_MEM_MB',env)
        self.assertNotIn('PREFLOP_MW_MODEL',env)
        self.assertEqual(env['PREFLOP_EQ_SAMPLES'],'1024')
        self.assertEqual(env['PREFLOP_GPU_LAYOUT_STATS'],'1')

    def test_original_uses_exact_observed_budget(self):
        env=case_environment({'SOLVER_GPU_MEM_MB':'23000'},23924,30002,Path('private'))
        self.assertEqual(env['SOLVER_GPU_MEM_MB'],'23924')

    def test_checkpoint_needs_six_measured_seats(self):
        x={'iteration':2,'phase':'iterating','gaps':[1]*6,'evs':[1]*6}
        self.assertTrue(checkpoint(x))
        for changes in [{'iteration':1},{'phase':'measuring'},{'gaps':[1]*8}]:
            self.assertFalse(checkpoint({**x,**changes}))

    def test_original_cache_is_explicitly_inferred(self):
        x=parse_layout('preflop gpu: coupled multiway, 1024 particles, 846156 reach CDFs, 32-particle batches, 100 MB CDF scratch','original')
        self.assertEqual(x['multiway_batch'],32)
        self.assertNotIn('hu_equity_cache_enabled',x)

    def test_comparability_requires_all_preservation_evidence(self):
        c={'layout':{'batch_policy':'deployed_prepass','multiway_batch':32,'literal_reference_multiway_batch':32,
             'hu_equity_cache_enabled':True,'literal_reference_hu_cache_enabled':True,'budget_mb':23924}}
        o={'layout':{'multiway_batch':32},'case':{'budget_mb':23924}}
        self.assertTrue(comparable(c,o))
        for change in [{'batch_policy':'corrected_budget_fallback'},{'multiway_batch':31},
                       {'literal_reference_hu_cache_enabled':False},{'literal_reference_hu_cache_enabled':None}]:
            self.assertFalse(comparable({'layout':{**c['layout'],**change}},o))
        self.assertFalse(comparable(c,{'layout':{'multiway_batch':32},'case':{'budget_mb':23000}}))

    def test_ambiguous_layout_rejected(self):
        with self.assertRaises(ValueError):
            parse_layout('preflop gpu layout: {}\npreflop gpu layout: {}','candidate')

    def test_native_gate_is_bit_exact(self):
        stats={'entries':1,'bit_equal':1,'finite_pairs':1,'max_abs':0,'max_ulp':0}
        d={'iteration':2,'payoff_model':'coupled_deck_v1','headers_identical_after_point_lock_order_canonicalization':True,
            'all_compared_values_finite':True,'invalid_effective_entries':0,'invalid_reach_classes':0,
            'raw_arenas':{'regret':dict(stats)},'effective_average_strategy':dict(stats),'raw_arena_normalized_strategy':dict(stats)}
        strict_comparator(d)
        d['raw_arenas']['regret']['max_ulp']=1
        with self.assertRaises(ValueError): strict_comparator(d)

if __name__=='__main__': unittest.main()
