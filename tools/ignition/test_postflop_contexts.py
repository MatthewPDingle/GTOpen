"""Context classification, opportunity denominators, and all-in exclusions."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('postflop_contexts', Path(__file__).with_name('postflop_contexts.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
cp = p.adapter().cp


def hand(actions, total, pre=None, stack='10.00'):
    total = '0'+total if total.startswith('.') else total
    stack = '0'+stack if stack.startswith('.') else stack
    return f"""PokerStars Hand #1: Hold'em No Limit ($0.05/$0.10 USD) - 2025/10/01 00:00:00 ET
Table 'Test' 6-max Seat #1 is the button
Seat 1: BTN (${stack} in chips)
Seat 2: SB (${stack} in chips)
Seat 3: BB (${stack} in chips)
SB: posts small blind $0.05
BB: posts big blind $0.10
*** HOLE CARDS ***
{pre or 'BTN: raises $0.20 to $0.30' + chr(10) + 'SB: folds' + chr(10) + 'BB: calls $0.20'}
*** FLOP *** [Kc Qd 9d]
{actions}
*** SUMMARY ***
Total pot ${total} | Rake $0
"""


class PostflopContextTests(unittest.TestCase):
    def events(self, text):
        cp.replay(text, 10, variant='ignition')
        return p.extract(text, cp)[0]

    def test_flop_donk_denominator_includes_check(self):
        events = self.events(hand('BB: checks\nBTN: checks', '.65'))
        self.assertEqual([(e['kind'], e['bet']) for e in events], [('donk', False), ('initiative', False)])

    def test_donk_bet_size_and_pot_type(self):
        events = self.events(hand('BB: bets $0.20\nBTN: calls $0.20', '1.05'))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['kind'], 'donk')
        self.assertAlmostEqual(events[0]['size_pot'], .2/.65)
        self.assertEqual(events[0]['pot_type'], 'single_raised')

    def test_turn_lead_requires_prior_street_aggression(self):
        events = self.events(hand('BB: checks\nBTN: bets $0.30\nBB: calls $0.30\n*** TURN *** [Kc Qd 9d] [2s]\nBB: bets $0.50\nBTN: calls $0.50', '2.25'))
        self.assertEqual(events[-1]['kind'], 'lead')
        self.assertEqual(events[-1]['street'], 1)

    def test_probe_follows_checked_through_street(self):
        events = self.events(hand('BB: checks\nBTN: checks\n*** TURN *** [Kc Qd 9d] [2s]\nBB: bets $0.30\nBTN: calls $0.30', '1.25'))
        self.assertEqual(events[-1]['kind'], 'probe')

    def test_stab_after_oop_aggressor_checks(self):
        pre = 'BTN: calls $0.10\nSB: folds\nBB: raises $0.20 to $0.30\nBTN: calls $0.20'
        events = self.events(hand('BB: checks\nBTN: bets $0.30\nBB: calls $0.30', '1.25', pre=pre))
        self.assertEqual([e['kind'] for e in events], ['initiative', 'stab'])

    def test_initiative_moves_with_postflop_raise(self):
        events = self.events(hand('BB: bets $0.20\nBTN: raises $0.30 to $0.50\nBB: calls $0.30\n*** TURN *** [Kc Qd 9d] [2s]\nBB: checks\nBTN: checks', '1.65'))
        self.assertEqual(events[-2]['kind'], 'lead')
        self.assertEqual(events[-1]['kind'], 'initiative')

    def test_no_bet_into_allin_opponent(self):
        pre = 'BTN: raises $0.20 to $0.30 and is all-in\nSB: folds\nBB: calls $0.20 and is all-in'
        events = self.events(hand('*** TURN *** [Kc Qd 9d] [2s]\n*** RIVER *** [Kc Qd 9d 2s] [3c]', '.65', pre=pre, stack='.30'))
        self.assertEqual(events, [])

    def test_allin_bet_counts_once_with_no_facing_response(self):
        events = self.events(hand('BB: bets $0.20 and is all-in\nBTN: calls $0.20 and is all-in', '1.05', stack='.50'))
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]['jam'])
        self.assertEqual(p.aggregate(events)[0]['ordinary_sizes'], {})

    def test_hero_not_in_population(self):
        events = self.events(hand('BB: checks\nBTN: checks', '.65').replace('BB', 'BB [ME]'))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['kind'], 'initiative')

    def test_multiway_flop_not_later_reclassified_heads_up(self):
        pre = 'BTN: raises $0.20 to $0.30\nSB: calls $0.25\nBB: calls $0.20'
        events = self.events(hand('SB: checks\nBB: checks\nBTN: bets $0.30\nSB: folds\nBB: calls $0.30\n*** TURN *** [Kc Qd 9d] [2s]\nBB: checks\nBTN: checks', '1.50', pre=pre))
        self.assertEqual(events, [])

    def test_limped_noinitiative_is_explicit_fallback(self):
        pre = 'BTN: calls $0.10\nSB: folds\nBB: checks'
        events = self.events(hand('BB: checks\nBTN: checks', '.25', pre=pre))
        self.assertTrue(all(e['kind'] == 'no_initiative_other' for e in events))
        self.assertTrue(all(e['pot_type'] == 'limped' for e in events))

    def test_threebet_pot_and_river_probe(self):
        pre = 'BTN: raises $0.20 to $0.30\nSB: folds\nBB: raises $0.60 to $0.90\nBTN: calls $0.60'
        events = self.events(hand('BB: checks\nBTN: checks\n*** TURN *** [Kc Qd 9d] [2s]\nBB: checks\nBTN: bets $0.50\nBB: calls $0.50\n*** RIVER *** [Kc Qd 9d 2s] [3c]\nBB: checks\nBTN: checks', '2.85', pre=pre))
        self.assertTrue(all(e['pot_type'] == 'three_bet_plus' for e in events))
        self.assertEqual(events[-2]['kind'], 'lead')
        self.assertEqual(events[-2]['street'], 2)

    def test_incomplete_hand_rejected_before_collection(self):
        with self.assertRaises(cp.Invalid):
            self.events(hand('BB: checks\nBTN: bets $0.30', '.95'))

    def test_chronological_validation_excludes_boundary_sessions(self):
        def event(date, bet):
            return dict(date=date, street=0, kind='donk', pot_type='single_raised', bet=bet, jam=False, size_pot=.33 if bet else None)
        sessions = [dict(events=[event('2025-10-01', False)]),
                    dict(events=[event('2025-11-01', True), event('2025-11-04', True)]),
                    dict(events=[event('2025-11-05', False)]),
                    dict(events=[event('2025-11-06', True)])]
        result = p.validation(sessions)
        self.assertEqual((result['train_sessions'], result['test_sessions'], result['excluded_boundary_sessions']), (1, 2, 1))
        self.assertEqual(result['evaluated_opportunities'], 2)
        self.assertEqual(result['rows'][0]['train_opportunities'], 1)
        self.assertIsNotNone(result['gain_95_session_bootstrap'])


if __name__ == '__main__':
    unittest.main()
