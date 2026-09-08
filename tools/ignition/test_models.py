import importlib.util, sys, unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ig=load('ig_analyze','tools/ignition/analyze.py')
fit=load('ig_fit','tools/ignition/fit.py')

def hand(actions,total='0.25'):
    return '''Ignition Hand #1 TBL#1 HOLDEM No Limit - 2025-08-20 00:00:00
Seat 1: Small Blind ($10 in chips)
Seat 2: Big Blind ($10 in chips)
Seat 3: Dealer [ME] ($10 in chips)
Dealer [ME] : Set dealer [3]
Small Blind : Small Blind $0.05
Big Blind : Big blind $0.10
*** HOLE CARDS ***
Small Blind : Card dealt to a spot [As Ks]
Big Blind : Card dealt to a spot [2c 3d]
Dealer [ME] : Card dealt to a spot [Qh Qd]
'''+actions+'\n*** SUMMARY ***\nTotal Pot($'+total+')\n'

class Tests(unittest.TestCase):
    def test_class_indices_match_rust_reference_labels(self):
        text=(ROOT/'crates/solver/src/preflop/reference.rs').read_text().split('pub const OPEN_SCORE:')[1].split('];')[0]
        import re
        labels=re.findall(r'// ([2-9TJQKA]{2}[so]?)',text)
        self.assertEqual(len(labels),169)
        for i,label in enumerate(labels):
            cards=(label[0]+'s',label[1]+('s' if label.endswith('s') else 'h'))
            self.assertEqual(ig.hand_index(cards),i,label)
        self.assertEqual(fit.COMBOS.sum(),1326)
        self.assertEqual(fit.COMBOS[ig.hand_index(('As','Ks'))],4)

    def test_allin_raise_and_partial_call_are_replayed(self):
        b=hand('''Dealer [ME] : All-in(raise) $10 to $10
Small Blind : Folds
Big Blind : All-in $9.90
*** FLOP *** [4s 5s 6s]
*** TURN *** [4s 5s 6s] [7s]
*** RIVER *** [4s 5s 6s 7s] [8s]''','20.05')
        canonical,cards=ig.convert(b);_,cs=ig.cp.replay(canonical,10,variant='ignition')
        self.assertEqual(cs['Dealer [ME]']['pre/open|raise'],1)
        self.assertEqual(cs['Big Blind']['pre/raise|call'],1)

    def test_unknown_cards_board_collisions_and_bad_delta_rejected(self):
        good=hand('Dealer [ME] : Raises $0.30 to $0.30\nSmall Blind : Folds\nBig Blind : Folds\nDealer [ME] : Return uncalled portion of bet $0.20','0.25')
        ig.cp.replay(ig.convert(good)[0],10,variant='ignition')
        for bad in [good.replace('[As Ks]','[As As]'),good.replace('Raises $0.30','Raises $0.20'),good.replace('*** SUMMARY ***','*** FLOP *** [As 4h 5h]\n*** SUMMARY ***')]:
            with self.assertRaises(ig.cp.Invalid):ig.convert(bad)

    def test_unseen_hand_borrows_training_only_and_probabilities_sum(self):
        sessions=[{'cells':{'6/BTN/168|raise':10,'6/BTN/1|fold':10}}]
        policies,hand,prior=fit.train(sessions,10,5)
        self.assertTrue(np.allclose(policies[(6,0)].sum(1),1))
        self.assertTrue(np.allclose(policies[(6,0)][50],hand[50]))
        self.assertEqual(fit.closest(policies,8,2),(6,0))

if __name__=='__main__':unittest.main()
