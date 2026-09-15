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
            # Two identical artificial observations in each stratum keep the
            # bootstrap deterministic while exercising its full output path.
            rows=[dict(job=dict(stratum=str(s),iso_weight=1,inclusion_probability=1),
                       hands=hands) for s in range(5) for _ in range(2)]
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
                for row in evaluation['cases']:
                    self.assertAlmostEqual(row['candidate_pot_sum_pct'],100,places=8)
                    self.assertAlmostEqual(row['reference_cv_pot_sum_pct'],100,places=8)
                    self.assertAlmostEqual(row['mean_br_gain_pct_pot'],0,places=8)
                    for bounds in row['paired_improvement_ci95_pct_pot'].values():
                        self.assertAlmostEqual(bounds[0],bounds[1],places=8)
                broken=copy.deepcopy(evaluation)
                broken['families'][0]['mae_pct_pot']['candidate']+=1
                night.dump(output/'evaluation.json',broken)
                with self.assertRaises(AssertionError):audit.check_artifacts(manifest,cases)


if __name__=='__main__':unittest.main()
