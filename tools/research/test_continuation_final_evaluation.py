"""Check reserved-board separation and the no-late-selection boundary."""
import copy
import pathlib
import tempfile
import types
import unittest
from unittest.mock import patch
import continuation_final_evaluation as final


class FinalEvaluationChecks(unittest.TestCase):
    def test_fresh_board_pool_and_separate_runner_namespace(self):
        boards,manifests=final.board_pool()
        self.assertEqual(len(boards),50)
        self.assertEqual(len({b['stratum'] for b in boards}),5)
        selected={b['board'] for b in boards}
        for path in manifests:
            m=final.study.read(path)
            self.assertFalse(selected & {b['board'] for b in m.get('boards',m['jobs'])})
        self.assertTrue(all(0<b['inclusion_probability']<=1 for b in boards))
        original=final.bridge.OUT
        self.assertEqual(final.adapter().OUT,final.OUT)
        self.assertEqual(final.bridge.OUT,original)

    def test_cannot_register_before_both_screens_or_after_reference_generation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder)/'evaluation';root.mkdir()
            (root/'prospective/jobs').mkdir(parents=True)
            modelroot=root.parent/'model-a';modelroot.mkdir()
            final.study.night.dump(modelroot/'training-screen.json',dict(selected=None))
            fake=types.SimpleNamespace(checked=lambda partition:dict(id='test',cases=[]))
            with patch.object(final,'OUT',root),patch.object(final,'MODELS',{'A':'model-a','B':'model-b'}),patch.object(final,'adapter',lambda:fake):
                with self.assertRaises(FileNotFoundError):final.register()
                self.assertFalse((root/'registered-models.json').exists())
                (root/'prospective/jobs/premature.json').write_text('{}')
                with self.assertRaisesRegex(AssertionError,'predates'):final.register()

    def test_fixed_gate_does_not_round_away_failure(self):
        families=[dict(improvement_vs_balanced=.15),dict(improvement_vs_balanced=.20)]
        cases=[dict(regression_vs_previous=.10)]
        self.assertTrue(final.accuracy_gate(families,cases))
        bad=copy.deepcopy(families);bad[0]['improvement_vs_balanced']=.149999
        self.assertFalse(final.accuracy_gate(bad,cases))
        self.assertFalse(final.accuracy_gate(families,[dict(regression_vs_previous=.100001)]))


if __name__=='__main__':unittest.main()
