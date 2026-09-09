"""Scientific invariants for the saved-game continuation evaluation."""
import copy, json, math, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import continuation_saved as study

class SavedContinuationTests(unittest.TestCase):
    def test_manifest_frozen_candidate_and_unseen_boards(self):
        m=study.manifest()
        self.assertEqual(len(m['jobs']),150)
        self.assertTrue(set(b['board'] for b in m['boards']).isdisjoint(m['excluded_boards']))
        self.assertEqual(sum(b['population_in_stratum'] for b in m['boards'])/3,1720)
        self.assertEqual(len({b['board'] for b in m['boards']}),15)
        self.assertTrue(all(b['inclusion_probability']==3/b['population_in_stratum'] for b in m['boards']))
        self.assertEqual(m['candidate_sha256'],'19afc4bc76c1aac837654e233639a1bfac6e1450b3a9ae526ac6e2871b8562a7')
    def test_suit_asymmetric_ranges_rejected(self):
        with self.assertRaisesRegex(ValueError,'suit-symmetric'):
            study.validate_suit_symmetric_ranges({'x':{'oop':'AsKs','ip':'AA'}})

    def test_actual_saved_pot_and_stack_arithmetic(self):
        m=study.manifest()
        for c in m['cases']:
            s=m['scenarios'][c['game']]['fields'];op=min(map(float,s['opens'].split(',')));sb=s['smallBlind']/s['bigBlind']
            to=op if c['line']=='iso_call' else op*min(map(float,s['mult'].split(',')))
            self.assertAlmostEqual(c['pot'],2*to+sb+(1 if c['line']=='iso_call' else 0))
            self.assertAlmostEqual(c['stack'],s['stack']-to)
    def test_controls_match_except_rake(self):
        m=study.manifest()
        for game in ['2-2','2-5']:
            original=next(j for j in m['jobs'] if j['case']==f'{game}-iso_call-half_pot')
            control=next(j for j in m['jobs'] if j['case']==f'{game}-iso_call-zero_rake')
            a=copy.deepcopy(original['config']);b=copy.deepcopy(control['config'])
            self.assertGreater(a['tree'].pop('rake_pct'),0)
            self.assertEqual(b['tree'].pop('rake_pct'),0)
            self.assertEqual(a,b)
    def test_manifest_tampering_rejected(self):
        m=study.manifest();m['reference_target_gap_pct']=99
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);(path/'manifest.json').write_text(json.dumps(m))
            with patch.object(study,'OUT',path),self.assertRaisesRegex(ValueError,'manifest altered'):study.manifest()
    def test_checkpoint_fraction_roundtrip_but_no_setting_drift(self):
        m=study.manifest();j=copy.deepcopy(m['jobs'][0]);j['inclusion_probability']+=1e-17
        row=dict(job=j,manifest_id=m['id'],target_met=True,gap_pct_pot=.2,reference_ev_bb=[3,10],reference_expected_rake_bb=1,compatible_pair_mass=123,provenance=dict(binary_sha256='binary',source_sha256={'cache/realization_fit.json':'fit','cache/preflop_eq169.bin':'equity'}))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);(path/'manifest.json').write_text(json.dumps(m));(path/'jobs').mkdir();out=path/'jobs'/(j['id']+'.json');out.write_text(json.dumps(row))
            with patch.object(study,'OUT',path):
                _,rows=study.load();self.assertEqual(rows[0]['job'],m['jobs'][0])
                row['job']['config']['tree']['starting_pot']+=.01;out.write_text(json.dumps(row))
                with self.assertRaisesRegex(ValueError,'checkpoint mismatch'):study.load()
    def test_unconverged_reference_is_rejected(self):
        m=study.manifest();j=m['jobs'][0]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);(path/'manifest.json').write_text(json.dumps(m));(path/'jobs').mkdir()
            (path/'jobs'/(j['id']+'.json')).write_text(json.dumps(dict(job=j,manifest_id=m['id'],target_met=False,gap_pct_pot=.4)))
            with patch.object(study,'OUT',path),self.assertRaisesRegex(ValueError,'reference target not met'):study.load()
    def test_ratio_weight_and_paired_resampling(self):
        case=dict(id='fixture',game='x',line='y',menu='z',pot=20,stack=80)
        rows=[]
        for name,w,ev in [('a',1,[2,18]),('b',3,[10,10])]:
            rows.append(dict(job=dict(case='fixture',board=name,config=dict(tree=dict(starting_pot=20,effective_stack=80,rake_pct=0,rake_cap=3))),weight=w,reference_ev_bb=ev,reference_expected_rake_bb=0,preflop_leaf=dict(equity=[.5,.5],raw_bb=[10,10],static_bb=[10,10],calibrated_bb=[8,8])))
        result=study.aggregate({'cases':[case]},rows)[0]
        np.testing.assert_allclose(result['reference_ev_bb'],[8,12])
        paired=study.aggregate({'cases':[case]},rows,{'a':2,'b':0})[0]
        np.testing.assert_allclose(paired['reference_ev_bb'],[2,18])
        self.assertEqual(paired['mae_bb']['raw'],8)
        rows[1]['preflop_leaf']['raw_bb']=[9,11]
        with self.assertRaisesRegex(ValueError,'preflop input changed across boards'):study.aggregate({'cases':[case]},rows)
    def test_candidate_respects_rake_and_accounting_in_every_case(self):
        m=study.manifest();params=json.loads(study.CANDIDATE.read_text())['parameters']
        for j in m['jobs'][::15]:
            row=dict(job=j,preflop_leaf=dict(equity=[.7,.3]));ev,rake=study.base.predict(row,params);t=j['config']['tree']
            self.assertAlmostEqual(sum(ev)+rake,t['starting_pot'])
            self.assertLessEqual(rake,t['rake_cap']);self.assertGreaterEqual(rake,0)
            if t['rake_pct']==0:self.assertEqual(rake,0)

if __name__=='__main__':unittest.main()
