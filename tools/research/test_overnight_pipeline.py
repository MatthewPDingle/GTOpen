"""Exercise final training/report plumbing with artificial labels only.

All outputs live in a temporary directory. No held-out GPU labels are read,
and none of these artificial outcomes are evidence of model accuracy.
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import audit_continuation_overnight as audit
import continuation_overnight as night
import continuation_overnight_fit as trainer
import range_value_pilot as pilot


class OvernightPipelineTests(unittest.TestCase):
    def test_training_selection_evaluation_and_final_audit(self):
        manifest=night.checked_manifest()
        fixtures=json.loads((night.OUT/'fixtures.json').read_text())['cases']
        counts,eq=pilot.matrices()
        contexts=[]
        for case in fixtures:
            c=pilot.context(case,counts,eq)
            residual=.1*(c['raw']-.5)
            target=c['raw']+residual
            hands=[]
            for player in range(2):
                hands.append([dict(hand=hand,pair_mass=float(c['mass'][player,k]),
                    ev_bb=float(target[player,k]*case['pot']),
                    equity=float(c['raw'][player,k]),
                    br_ev_bb=float(target[player,k]*case['pot']))
                    for hand,k in pilot.INDEX.items() if c['mass'][player,k]>0])
            # Opposing artificial board effects preserve the aggregate label
            # while giving the independent bootstrap audit nontrivial intervals.
            rows=[]
            for s in range(5):
                for sign in (-1,1):
                    board_hands=copy.deepcopy(hands)
                    for player in range(2):
                        for hand in board_hands[player]:
                            k=pilot.INDEX[hand['hand']]
                            offset=sign*.04*(c['raw'][player,k]-.5)*case['pot']
                            hand['ev_bb']+=offset;hand['br_ev_bb']+=offset
                    rows.append(dict(job=dict(stratum=str(s),iso_weight=1,inclusion_probability=1),
                                     hands=board_hands))
            c.update(case=case,residual=residual,observed=c['mass'].copy(),
                     unadjusted=target,rows=rows,base_x=c['x'].copy(),base_names=list(c['names']))
            contexts.append(c)
        phases=[]
        with tempfile.TemporaryDirectory(prefix='gtopen-pipeline-smoke-') as folder:
            output=Path(folder)
            def load(partition):
                phases.append(partition)
                if partition=='test':
                    self.assertTrue((output/'candidate.json').exists())
                    self.assertTrue((output/'cross-validation.json').exists())
                return [c for c in contexts if c['case']['partition']==partition]
            with patch.object(night,'OUT',output), patch.object(night,'checked_manifest',return_value=manifest), \
                 patch.object(trainer,'load_cases',side_effect=load), contextlib.redirect_stdout(io.StringIO()):
                trainer.train()
                trainer.evaluate()
                self.assertEqual(phases,['train','test'])
                cases={c['id']:c for c in fixtures}
                self.assertTrue(audit.check_artifacts(manifest,cases))
                evaluation=json.loads((output/'evaluation.json').read_text())
                widths=[]
                for row in evaluation['cases']:
                    self.assertAlmostEqual(row['candidate_pot_sum_pct'],100,places=8)
                    self.assertAlmostEqual(row['reference_cv_pot_sum_pct'],100,places=8)
                    self.assertAlmostEqual(row['mean_br_gain_pct_pot'],0,places=8)
                    for bounds in row['paired_improvement_ci95_pct_pot'].values():
                        self.assertGreaterEqual(bounds[1],bounds[0])
                        widths.append(bounds[1]-bounds[0])
                self.assertTrue(any(width>1e-6 for width in widths))
                # A coherently altered case score must fail against observations,
                # even without relying on a mismatch with its family average.
                altered=copy.deepcopy(evaluation)
                altered['cases'][0]['mae_pct_pot']['candidate']+=1
                model=json.loads((output/'candidate.json').read_text())
                with self.assertRaises(AssertionError):
                    audit.check_evaluation_values(model,altered)
                for corruption in ['case_interval','family_interval','mean_quality','probe_value']:
                    with self.subTest(corruption=corruption):
                        altered=copy.deepcopy(evaluation)
                        if corruption=='case_interval':
                            altered['cases'][0]['paired_improvement_ci95_pct_pot']['balanced'][0]+=1
                        elif corruption=='family_interval':
                            altered['families'][0]['paired_improvement_ci95_pct_pot']['raw'][1]+=1
                        elif corruption=='mean_quality':
                            altered['cases'][0]['mean_br_gain_pct_pot']+=1
                        else:
                            altered['cases'][0]['probes'][0]['candidate']+=1
                        with self.assertRaises(AssertionError):
                            audit.check_evaluation_values(model,altered)
                broken=copy.deepcopy(evaluation)
                broken['families'][0]['mae_pct_pot']['candidate']+=1
                night.dump(output/'evaluation.json',broken)
                with self.assertRaises(AssertionError):audit.check_artifacts(manifest,cases)


if __name__=='__main__':unittest.main()
