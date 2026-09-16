import copy
import unittest
import continuation_candidate_export as export


class ExportTests(unittest.TestCase):
    def test_reproduces_independently_verified_frozen_gpu_source(self):
        path=export.study.night.OUT/'candidate.json'
        actual=export.source(export.study.read(path),export.study.pilot.sha(path))
        expected=(export.study.ROOT/'research/preflop-evolution/continuation/learned-interface-20260916/interface.cu').read_bytes().decode()
        self.assertEqual(actual,expected)

    def test_rejects_unknown_feature_and_invalid_scaling(self):
        model=export.study.read(export.study.night.OUT/'candidate.json')
        broken=copy.deepcopy(model);broken['feature_names'][0]='unknown_feature'
        with self.assertRaises(AssertionError):export.expression(broken)
        broken=copy.deepcopy(model);broken['scale'][0]=0
        with self.assertRaises(AssertionError):export.expression(broken)


if __name__=='__main__':unittest.main()
