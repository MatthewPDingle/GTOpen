import importlib.util
import unittest, tempfile, json
from unittest.mock import patch
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('calling_audit',Path(__file__).with_name('calling_audit.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
cp=a.load_module('calling_cp',a.ROOT/'tools/coinpoker/analyze.py')

class CallingAuditTests(unittest.TestCase):
    def rows(self,actions):
        pre="""PokerStars Hand #1: Hold'em No Limit ($0.05/$0.10 USD) - 2025/10/01 00:00:00 ET
Table 'Test' 6-max Seat #4 is the button
Seat 1: UTG ($10.00 in chips)
Seat 2: HJ ($10.00 in chips)
Seat 3: CO ($10.00 in chips)
Seat 4: BTN ($10.00 in chips)
Seat 5: SB ($10.00 in chips)
Seat 6: BB ($10.00 in chips)
SB: posts small blind $0.05
BB: posts big blind $0.10
*** HOLE CARDS ***
"""
        return a.extract(pre+actions,{p:['As','Ah'] for p in ['UTG','HJ','CO','BTN','SB','BB']},cp,lambda _:168)
    def test_limp_entry_remains_distinct_after_limp_reraise(self):
        z=self.rows('UTG: calls $0.10\nHJ: raises $0.30 to $0.40\nCO: raises $0.80 to $1.20\nUTG: raises $2.00 to $3.20\nHJ: raises $3.20 to $6.40\nUTG: calls $3.20\n')
        self.assertEqual([r['kind'] for r in z],['limp','iso_raise','limp'])
        self.assertEqual(z[0]['row'][2],1)
        self.assertEqual(z[-1]['row'][2],2)
        self.assertEqual(z[-1]['row'][3],1)
    def test_open_and_cold_call_are_separate(self):
        z=self.rows('UTG: raises $0.20 to $0.30\nHJ: calls $0.30\nCO: raises $0.70 to $1.00\nUTG: calls $0.70\nHJ: calls $0.70\n')
        self.assertEqual([r['kind'] for r in z],['open_raise','cold_call'])
        self.assertEqual([r['row'][2] for r in z],[2,1])
        self.assertAlmostEqual(z[0]['row'][4],.7/(.15+.3+.3+1+.7),places=6)
    def test_direct_reraise_and_cold_are_distinct(self):
        z=self.rows('UTG: raises $0.20 to $0.30\nHJ: raises $0.70 to $1.00\nCO: raises $1.50 to $2.50\nBTN: folds\nHJ: calls $1.50\n')
        self.assertEqual([r['kind'] for r in z],['cold','cold','reraise_entry'])
    def test_zero_support_exactly_retains_offset(self):
        r=np.array([[6,0,1,0,.1,1,99,5.]])
        weights=a.blend_weights(r,np.array([0]),r,np.array([1]))
        p=np.array([[.7,.2,.1]]);q=np.array([[.1,.7,.2]])
        np.testing.assert_array_equal(a.blend(p,q,weights),p)
    def test_support_counts_use_only_supplied_training_rows(self):
        r=np.array([[6,0,1,0,.2,1,99,5.]])
        weights=a.blend_weights(np.repeat(r,30,axis=0),np.zeros(30,int),np.repeat(r,500,axis=0),np.zeros(500,int))
        np.testing.assert_array_equal(weights,np.full(500,.5))
    def test_blend_preserves_simplex_and_rejects_invalid_weights(self):
        p=np.array([[.7,.2,.1]]);q=np.array([[.1,.7,.2]])
        self.assertAlmostEqual(a.blend(p,q,np.array([.4])).sum(),1.)
        for w in [float('nan'),-1.,1.1]:
            with self.assertRaises(ValueError):a.blend(p,q,np.array([w]))
    def test_single_session_interval_is_not_claimed(self):
        y=np.eye(3)[[0,1]];p=np.array([[.6,.3,.1],[.2,.7,.1]])
        self.assertIsNone(a.metrics(y,p,p,np.array([0,0]))['gain_95_interval'])
    def test_context_correction_keeps_hand_aware_offset_separate(self):
        r=np.array([[6,0,1,0,.2,1,99,5.],[6,0,1,0,.2,1,99,168.]])
        self.assertEqual(a.extra(r,np.array([2,2])).shape,(2,24))
        # Corrections share context; the hand-aware contextual offset stays intact.
        np.testing.assert_array_equal(a.extra(r,np.array([2,2]))[0],a.extra(r,np.array([2,2]))[1])
    def test_provenance_rejects_changed_observations(self):
        manifest={'dependencies_sha256':{q:a.digest(a.ROOT/q) for q in a.DEPENDENCIES},'observations_sha256':'expected'}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'manifest.json').write_text(json.dumps(manifest));(root/'observations.json').write_text('{}')
            with patch.object(a,'PRIVATE',root), self.assertRaisesRegex(ValueError,'Observation hash mismatch'):a.verify_inputs()
    def test_provenance_rejects_helper_changes(self):
        manifest={'dependencies_sha256':{q:a.digest(a.ROOT/q) for q in a.DEPENDENCIES},'observations_sha256':'expected'};manifest['dependencies_sha256']['tools/ignition/smoothing.py']='changed'
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'manifest.json').write_text(json.dumps(manifest))
            with patch.object(a,'PRIVATE',root), self.assertRaisesRegex(ValueError,'dependency changed'):a.verify_inputs()
    def test_published_evidence_has_complete_counts_and_no_private_ids(self):
        meta=json.loads((a.OUT/'evidence-metadata.json').read_text())
        self.assertEqual(sum(c['decisions'] for c in meta['contexts']),12463)
        self.assertEqual(meta['model_sha256'],a.digest(a.ARTIFACT))
        for c in meta['contexts']:
            self.assertTrue(0<c['observed_classes']<=169)
            self.assertTrue(0<c['sessions']<=c['decisions'])
            self.assertEqual(set(c),{'players','role','entry','depth','decisions','sessions','observed_classes'})
if __name__=='__main__':unittest.main()
