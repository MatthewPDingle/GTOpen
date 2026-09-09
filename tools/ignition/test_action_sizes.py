"""Meaningful invariants for independent sizing extraction and safe export."""
import copy,importlib.util,json,math,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
spec=importlib.util.spec_from_file_location('action_sizes',Path(__file__).with_name('action_sizes.py'));a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
cp=a.module('size_cp',a.ROOT/'tools/coinpoker/analyze.py')
class ActionSizingTests(unittest.TestCase):
    def events(self,text,stack='1.00'):
        pre=f"""PokerStars Hand #1: Hold'em No Limit ($0.05/$0.10 USD) - 2025/10/01 00:00:00 ET
Table 'Test' 6-max Seat #4 is the button
Seat 1: UTG (${stack} in chips)
Seat 2: HJ (${stack} in chips)
Seat 3: CO (${stack} in chips)
Seat 4: BTN (${stack} in chips)
Seat 5: SB (${stack} in chips)
Seat 6: BB (${stack} in chips)
SB: posts small blind $0.05
BB: posts big blind $0.10
*** HOLE CARDS ***
"""
        return a.replay_sizes(pre+text,cp)[0]
    def test_iso_total_and_limper_count(self):
        e=self.events('UTG: calls $0.10\nHJ: calls $0.10\nCO: calls $0.10\nBTN: raises $0.50 to $0.60\n')
        self.assertEqual((e[0]['group'],e[0]['amount'],e[0]['basis']),('iso_paid_3',6.,'bb'))
    def test_free_big_blind_iso_context(self):
        e=self.events('UTG: calls $0.10\nBB: raises $0.40 to $0.50\n')
        self.assertEqual(e[0]['group'],'iso_free_1');self.assertEqual(e[0]['amount'],5.)
    def test_reraise_ratio_uses_previous_total_not_increment(self):
        e=self.events('UTG: raises $0.20 to $0.30\nHJ: raises $0.30 to $0.60\nUTG: raises $0.30 to $0.90\n')
        self.assertEqual([r['amount'] for r in e],[2.,1.5]);self.assertFalse(e[1]['jam'])
        self.assertGreater(e[1]['raise_to_bb'],e[1]['remaining_bb'])
    def test_true_jam_uses_added_chips_and_is_excluded(self):
        e=self.events('UTG: raises $0.20 to $0.30\nHJ: raises $0.30 to $0.60\nUTG: raises $0.40 to $1.00\n')
        self.assertTrue(e[1]['jam']);self.assertEqual(len(a.records([dict(events=e)],'reraise')),0)
    def test_squeeze_requires_caller_after_open(self):
        e=self.events('UTG: raises $0.20 to $0.30\nHJ: calls $0.30\nCO: raises $0.60 to $0.90\n')
        self.assertEqual(e[0]['group'],'squeeze');self.assertEqual(e[0]['amount'],3.)
    def test_limp_reraise_is_not_cold_threebet(self):
        e=self.events('UTG: calls $0.10\nHJ: raises $0.20 to $0.30\nUTG: raises $0.60 to $0.90\n')
        self.assertEqual(e[1]['group'],'limp_reraise')
    def test_log_projection_preserves_mass_and_no_menu_floor(self):
        out=a.project({3.:.7,6.:.3},[2.,3.,4.,6.]);np.testing.assert_array_equal(out,[0,.7,0,.3]);self.assertAlmostEqual(out.sum(),1)
        self.assertEqual(np.argmax(a.project({4.:1},[2.,8.])),0)
    def test_unobserved_context_falls_back_to_pool(self):
        ss=[dict(events=[dict(group='threebet',players=6,role=0,amount=3.,jam=False)])]
        model=a.fit(ss,'threebet',30.);np.testing.assert_array_equal(a.predict(model,dict(players=8,role=4),[2,3,4]),[0,1,0])
    def test_iso_broader_group_includes_each_event_once(self):
        ss=[dict(events=[dict(group=g,players=6,role=0,amount=5.,jam=False) for g in ['iso_paid_3','iso_free_3','iso_paid_1']])]
        self.assertEqual(len(a.records(ss,'iso_3')),2);self.assertEqual(len(a.records(ss,'iso_paid_all')),2);self.assertEqual(len(a.records(ss,'iso_all')),3)
    def test_single_session_interval_is_not_claimed(self):
        ss=[dict(events=[dict(group='threebet',players=6,role=0,amount=3.,jam=False)])];model=a.fit(ss,'threebet');self.assertIsNone(a.comparison(ss,'threebet',[model,model])['gain_95_interval'])
    def test_pool_release_gate_is_not_low_count_certainty(self):
        result={'groups':{g:{'pool_supported':False} for g in ['iso_paid_3','iso_3','iso_all']},'distributions':{}}
        self.assertIsNone(a.choose('iso_paid_3',6,0,result))
        result['groups']['iso_3']['pool_supported']=True;result['distributions']['iso_3']=dict(basis='bb',pool=[[5.,1.]],contexts=[])
        self.assertEqual(a.choose('iso_paid_3',6,0,result),('iso_3','bb',[[5.,1.]],False))
    def test_exact_hand_and_opening_preservation_export_fixture(self):
        p=dict(call=[.2]*169,raise_=[.3]*169,jam=[.01]*169,raise_size='max');p['raise']=p.pop('raise_')
        dataset=dict(site='Ignition NL10 regular',rows=[dict(players=6,role=0,opening=copy.deepcopy(p),responses={'raise':0,'squeeze':0})],response_policies=[p],response_notes={})
        before=[dict(name='fixture',stats={'dataset':dataset},source={'assumptions':[]})]
        result=dict(groups={g:dict(pool_supported=True,nonjam=100,sessions=20,release='pooled') for g in ['threebet','squeeze']},distributions={g:dict(basis='previous',pool=[[v,1.]],contexts=[]) for g,v in [('threebet',3.),('squeeze',5.)]})
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);library=root/'source.json';library.write_text(json.dumps(before))
            with patch.object(a,'LIBRARY',library),patch.object(a,'PRIVATE',root/'private'),patch.object(a,'OUT',root/'public'):a.export(result)
            after=json.loads((root/'private/archetypes-candidate.json').read_text())[0]['stats']['dataset'];row=after['rows'][0]
            self.assertEqual(row['opening'],p)
            for key in row['responses']:
                q=after['response_policies'][row['responses'][key]];self.assertEqual(q['call'],p['call']);self.assertEqual(q['raise'],p['raise']);self.assertEqual(q['jam'],p['jam']);self.assertIn('raise_multiples',q);self.assertNotIn('raise_size_basis',q);self.assertNotIn('raise_sizes',q)
            self.assertNotEqual(row['responses']['raise'],row['responses']['squeeze'])
if __name__=='__main__':unittest.main()
