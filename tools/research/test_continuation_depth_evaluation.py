import unittest
from unittest.mock import patch
import continuation_depth_evaluation as evaluation


class DepthEvaluationChecks(unittest.TestCase):
    def test_source_queries_and_adapter_state_are_isolated(self):
        source=evaluation.adapter(evaluation.SOURCE).checked('prospective')
        self.assertEqual(len(source['jobs']),400)
        self.assertEqual(len(source['cases']),8)
        self.assertEqual(len(source['boards']),50)
        copy=evaluation.adapter()
        self.assertEqual(copy.OUT,evaluation.OUT)
        self.assertNotEqual(evaluation.bridge.OUT,copy.OUT)
        copy.OUT='changed'
        self.assertEqual(evaluation.adapter().OUT,evaluation.OUT)

    def test_registration_rejects_already_generated_source_references(self):
        with patch('pathlib.Path.glob',return_value=iter(['already-exists.json'])):
            with self.assertRaisesRegex(AssertionError,'Source outcomes already exist'):
                evaluation.prepare()


if __name__=='__main__':unittest.main()
