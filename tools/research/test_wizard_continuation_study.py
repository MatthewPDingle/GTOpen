import copy
import math
import unittest
import wizard_continuation_study as s


class AuditTests(unittest.TestCase):
    def test_frozen_branch_and_rake_units(self):
        m=s.checked();f=s.read(s.OUT/'fixtures.json');case,=f['cases']
        self.assertEqual(case['path'],[1,2,0,0,0,0,0,0,1])
        self.assertEqual((case['pot'],case['stack']),(39.5,182))
        self.assertEqual(f['config']['rake_pct'],4)
        self.assertEqual({j['config']['tree']['rake_pct'] for j in m['jobs']},{.04})
        self.assertAlmostEqual(sum(case['balanced']['mean_bb']),39.5*(1-.04),places=4)
        self.assertLess(max(case['removed_mass_fraction']),.005)
        self.assertLess(max(case['probe_added_mass_fraction']),.001)

    def test_paired_board_panels(self):
        m=s.read(s.OUT/'manifest.json')
        self.assertEqual(len(m['jobs']),80)
        self.assertEqual(len({j['id'] for j in m['jobs']}),80)
        half=[j['board'] for j in m['jobs'] if j['menu']=='half']
        large=[j['board'] for j in m['jobs'] if j['menu']=='large']
        self.assertEqual(half,large)
        for group in {b['stratum'] for b in m['boards']}:
            self.assertEqual(sum(b['stratum']==group for b in m['boards']),8)

    def test_metadata_tolerance_is_narrow(self):
        j=s.read(s.OUT/'manifest.json')['jobs'][0]
        other=copy.deepcopy(j)
        other['inclusion_probability']=math.nextafter(j['inclusion_probability'],1)
        self.assertTrue(s.same_job(j,other))
        other['config']['tree']['rake_pct']=0
        self.assertFalse(s.same_job(j,other))
        other=copy.deepcopy(j);other['inclusion_probability']*=1.00001
        self.assertFalse(s.same_job(j,other))

    def test_reject_unconverged_reference(self):
        m=s.read(s.OUT/'manifest.json');j=m['jobs'][0]
        r=dict(manifest_id=m['id'],job=j,query_mode='materialized_full_enumeration',target_met=False)
        with self.assertRaises(AssertionError):s.validate(r,j,m)

    def test_terminal_prices_match_saved_call_action(self):
        f=s.read(s.OUT/'fixtures.json');case,=f['cases']
        actions=s.read(s.BASE/'nl25-utg-vs-lj-3bet-action-evs.json')
        for hand in f['probes']:
            gross=next(h['value_bb'] for h in case['original_balanced']['hands'][0] if h['hand']==hand)
            net=next(h['actions'][1]['ev_bb'] for h in actions['hands'] if h['hand']==hand)
            self.assertAlmostEqual(gross-12,net,places=4)

    def test_probe_floor_changes_only_registered_range_weights(self):
        parent=s.read(s.OUT/'manifest.json')
        sensitivity=s.read(s.OUT/'floor-sensitivity/manifest.json')
        self.assertLess(sensitivity['added_mass_fraction'],.005)
        self.assertEqual(len(parent['jobs']),len(sensitivity['jobs']))
        for old,new in zip(parent['jobs'],sensitivity['jobs']):
            original,changed=copy.deepcopy(old),copy.deepcopy(new)
            def weights(text):return dict((h,float(w)) for h,w in (part.split(':') for part in text.split(',')))
            a=weights(original['config'].pop('range_oop'))
            b=weights(changed['config'].pop('range_oop'))
            self.assertEqual(original,changed)
            self.assertEqual(a.keys(),b.keys())
            self.assertEqual({h for h in a if a[h]!=b[h]},{'AA','KQo','55','76s'})
            for h in ('AA','KQo','55','76s'):
                self.assertAlmostEqual(a[h],.001)
                self.assertAlmostEqual(b[h],.01)

    def test_fourbet_call_value_decomposition(self):
        audit=s.read(s.OUT/'premium-branches.json')
        f=s.read(s.OUT/'fourbet-call/fixtures.json');case,=f['cases']
        root=[1,2,0,0,0,0,0,0]
        node=lambda path:next(n for n in audit['nodes'] if n['path']==path)
        def aa_evs(n):return next(h['action_ev_bb'] for h in n['selected_action_values'] if h['hand']=='AA')
        gross=next(h['value_bb'] for h in case['original_balanced']['hands'][0] if h['hand']=='AA')
        reply=node(root+[2]);jam=node(root+[2,2])
        aa=next(i for i,h in enumerate(case['original_balanced']['hands'][0]) if h['hand']=='AA')
        jam_value=sum(jam['view']['strategy'][a*169+aa]*ev for a,ev in enumerate(aa_evs(jam)))
        values=[27.5,gross-39,jam_value-39]
        rebuilt=sum(a['freq']*v for a,v in zip(reply['view']['actions'],values))
        self.assertAlmostEqual(rebuilt,aa_evs(node(root))[2],places=4)
        self.assertLess(f['price_implementation_max_difference_bb'],.0001)
        self.assertEqual((case['pot'],case['stack']),(93.5,155))
        self.assertLess(max(case['removed_mass_fraction']),.005)


if __name__=='__main__':unittest.main()
