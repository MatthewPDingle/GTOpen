import unittest
from unittest.mock import patch
import continuation_shrunk_evaluation as evaluation


class ShrunkEvaluationChecks(unittest.TestCase):
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

    def test_rejects_queue_owner_between_gpu_children(self):
        import continuation_night_queue as queue
        with patch.object(queue,'processes',return_value=[dict(ProcessId=-1,Name='python.exe',
                CommandLine='python tools/research/continuation_prior_evaluation.py run')]):
            with self.assertRaisesRegex(AssertionError,'owns the GPU queue'):
                evaluation.require_queue_idle()
        with patch.object(queue,'processes',return_value=[dict(ProcessId=-2,Name='gto-server.exe',CommandLine='gto-server.exe')]):
            evaluation.require_queue_idle()


if __name__=='__main__':unittest.main()
