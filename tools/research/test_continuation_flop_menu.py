import copy
import unittest
import continuation_flop_menu as experiment


class MenuChecks(unittest.TestCase):
    def test_expansion_is_nested_and_only_changes_flop(self):
        case=dict(range_oop='AA',range_ip='KK',pot=20,stack=200)
        before=copy.deepcopy(case)
        a=experiment.config(case,'AcKd2s','control');b=experiment.config(case,'AcKd2s','expanded')
        for player in ['oop','ip']:
            self.assertEqual(a['tree'][player][1:],b['tree'][player][1:])
            self.assertEqual(b['tree'][player][0]['bet'],[{'PotPct':33},{'PotPct':50},{'PotPct':75}])
            self.assertEqual(a['tree'][player][0]['raise'],b['tree'][player][0]['raise'])
            for action in ['bet','donk']:
                self.assertTrue(all(v in b['tree'][player][0][action] for v in a['tree'][player][0][action]))
        self.assertEqual(case,before)
        b['tree']['oop'][0]['bet'].append({'PotPct':99})
        self.assertNotEqual(b['tree']['oop'],b['tree']['ip'])

    def test_every_context_is_required(self):
        rows=[dict(case=str(i),mae_pct_pot=dict(candidate=8,balanced=10),regression_vs_previous=.09) for i in range(8)]
        self.assertTrue(experiment.gate(rows))
        rows[-1]['mae_pct_pot']['candidate']=8.6
        self.assertFalse(experiment.gate(rows))
        with self.assertRaises(AssertionError):experiment.gate(rows[:-1])

    def test_boards_are_disjoint_deterministic_and_stratified(self):
        fixtures=experiment.study.read(experiment.study.pilot.AUDIT/'fixtures.json')['canonical_flops']
        excluded={b for b,i in fixtures[:100]}
        a=experiment.board_sample(fixtures,excluded)
        self.assertEqual(a,experiment.board_sample(list(reversed(fixtures)),excluded))
        self.assertFalse(excluded.intersection(r['board'] for r in a))
        self.assertEqual(set(__import__('collections').Counter(r['stratum'] for r in a).values()),{4})


if __name__=='__main__':unittest.main()
