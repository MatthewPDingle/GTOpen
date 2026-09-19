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


if __name__=='__main__':unittest.main()
