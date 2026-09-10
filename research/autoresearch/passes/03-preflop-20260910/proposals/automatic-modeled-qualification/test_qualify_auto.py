import unittest
from pathlib import Path
from qualify_auto import checkpoint, comparable, parse_layout, case_environment, strict_comparator

class AutoTests(unittest.TestCase):
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
