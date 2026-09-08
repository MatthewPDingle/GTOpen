import unittest, tempfile
from pathlib import Path
from analyze import replay, Invalid, read_histories, SPLIT

def hand(actions, total, bb_stack='100', table='7', n=5):
    seats='\n'.join(f'Seat {i}: P{i} (${bb_stack if i==2 else "100"} in chips)' for i in range(1,n+1))
    antes='\n'.join(f'P{i}: posts the ante $0.10' for i in range(1,n+1))
    return f"""PokerStars Hand #123: Hold'em No Limit ($0.50/$1.00 USD) - 2025/08/01 01:00:00 ET
Table 'COIP123' {table}-max Seat #5 is the button
{seats}
{antes}
P1: posts small blind $0.50
P2: posts big blind $1
*** HOLE CARDS ***
{actions}
*** SUMMARY ***
Total pot ${total} | Rake $0
"""

class ReplayTests(unittest.TestCase):
    def test_repeated_header_prefix_keeps_individual_hands(self):
        h=hand('P3: folds\nP4: folds\nP5: folds\nP1: folds','2')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hands.txt'
            p.write_text(h+'\n'+h.replace('PokerStars Hand #123','PokerStars PokerStars Hand #124'))
            blocks=[b for b in SPLIT.split(read_histories(p)) if b.strip()]
            self.assertEqual([replay(b)[0]['id'] for b in blocks],['123','124'])

    def test_joint_context_opportunities_retain_actual_position(self):
        _,c=replay(hand('P3: folds\nP4: folds\nP5: folds\nP1: folds','2'))
        self.assertEqual(c['P3']['context/5/HJ/open|fold'],1)
        self.assertEqual(c['P1']['context/5/SB/open|fold'],1)
        self.assertFalse(any(k.startswith('context/') for k in c['P2']))

    def test_raise_cbet_and_return(self):
        _,c=replay(hand('''P3: raises $2 to $3
P4: folds
P5: folds
P1: folds
P2: calls $2
*** FLOP *** [As 7d 2c]
P2: checks
P3: bets $3
P2: folds
Uncalled bet ($3) returned to P3''','7'))
        self.assertEqual(c['P3']['pre/open|raise'],1)
        self.assertEqual(c['P2']['pre/raise|call'],1)
        self.assertEqual(c['P3']['post/flop/initiative|bet'],1)
        self.assertEqual(c['P2']['post/flop/facing|fold'],1)
        self.assertEqual(c['P1']['vpip|no'],1)

    def test_limper_defense_is_not_cold_defense(self):
        _,c=replay(hand('''P3: calls $1
P4: raises $3 to $4
P5: folds
P1: folds
P2: folds
P3: folds
Uncalled bet ($3) returned to P4''','4'))
        self.assertEqual(c['P4']['pre/limps|raise'],1)
        self.assertEqual(c['P3']['pre/limped_raise|fold'],1)
        self.assertEqual(c['P3']['vpip|yes'],1)
        self.assertEqual(c['P3']['pfr|no'],1)

    def test_short_allin_call_is_not_full_call(self):
        _,c=replay(hand('''P3: raises $2 to $3
P4: folds
P5: folds
P1: folds
P2: calls $1 and is all-in
Uncalled bet ($1) returned to P3
*** FLOP *** [As 7d 2c]
*** TURN *** [As 7d 2c] [4h]
*** RIVER *** [As 7d 2c 4h] [9s]''','5',bb_stack='2.10'))
        self.assertEqual(c['P2']['pre/raise|call'],1)
        self.assertFalse(any(k.startswith('post/') for k in c['P2']))

    def test_squeeze_and_original_raiser_4bet(self):
        _,c=replay(hand('''P3: raises $2 to $3
P4: calls $3
P5: raises $9 to $12
P1: folds
P2: folds
P3: raises $18 to $30
P4: folds
P5: folds
Uncalled bet ($18) returned to P3''','29'))
        self.assertEqual(c['P5']['pre/squeeze|raise'],1)
        self.assertEqual(c['P3']['pre/3bet_raiser|raise'],1)
        self.assertEqual(c['P4']['pre/4bet_plus|fold'],1)

    def test_missing_action_and_wrong_pot_rejected(self):
        for actions,total in [('P3: folds\nP5: folds','2'),('P3: folds\nP4: folds\nP5: folds\nP1: folds','99')]:
            with self.assertRaises(Invalid): replay(hand(actions,total))

    def test_free_bb_check_not_vpip(self):
        _,c=replay(hand('''P3: calls $1
P4: folds
P5: folds
P1: folds
P2: checks
*** FLOP *** [As 7d 2c]
P2: checks
P3: checks
*** TURN *** [As 7d 2c] [4h]
P2: checks
P3: checks
*** RIVER *** [As 7d 2c 4h] [9s]
P2: checks
P3: checks''','3'))
        self.assertEqual(c['P2']['pre/free|check'],1)
        self.assertEqual(c['P2']['vpip|no'],1)

    def test_other_formats_and_extra_blinds_rejected(self):
        block=hand('P3: folds\nP4: folds\nP5: folds\nP1: folds','2')
        for bad in [block.replace('7-max','4-max'),block.replace('*** HOLE CARDS ***','P3: posts big blind $1\n*** HOLE CARDS ***')]:
            with self.assertRaises(Invalid): replay(bad)

    def test_bb_walk_counts_as_dealt_without_vpip(self):
        _,c=replay(hand('P3: folds\nP4: folds\nP5: folds\nP1: folds','2'))
        self.assertEqual(c['P2']['vpip|no'],1)
        self.assertFalse(any(k.startswith('pre/') for k in c['P2']))

    def test_implicit_allin_raise_uses_remaining_stack(self):
        _,c=replay(hand('''P3: raises $2 to $3
P4: folds
P5: folds
P1: folds
P2: raises $98.90 and is all-in
P3: folds
Uncalled bet ($96.90) returned to P2''','7'))
        self.assertEqual(c['P2']['pre/raise|raise'],1)
        self.assertEqual(c['P3']['pre/3bet_raiser|fold'],1)

    def test_short_raise_is_explicitly_excluded(self):
        with self.assertRaisesRegex(Invalid,'short_raise'):
            replay(hand('''P3: raises $2 to $3
P4: folds
P5: folds
P1: folds
P2: raises $1 to $4 and is all-in''','0',bb_stack='4.10'))

if __name__=='__main__': unittest.main()
