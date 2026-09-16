import unittest
from unittest.mock import patch
import continuation_qualified_gpu_queue as queue


class QualifiedQueueChecks(unittest.TestCase):
    def test_process_identity_is_required_before_waiting(self):
        self.assertFalse(queue.dependency_alive([],12))
        self.assertTrue(queue.dependency_alive([dict(ProcessId=12,Name='python.exe',CommandLine='python continuation_shrunk_queue.py 4')],12))
        with self.assertRaisesRegex(AssertionError,'identity'):
            queue.dependency_alive([dict(ProcessId=12,Name='python.exe',CommandLine='python different.py')],12)

    def test_failed_or_incomplete_accuracy_blocks_handoff(self):
        self.assertFalse(queue.accuracy_ready(dict(stage='checks_complete',accuracy_screen_passed=False),dict(accuracy_screen_passed=False)))
        with self.assertRaises(AssertionError):queue.accuracy_ready(dict(stage='failed'),dict(accuracy_screen_passed=True))
        with self.assertRaises(AssertionError):queue.accuracy_ready(dict(stage='checks_complete',accuracy_screen_passed=False),dict(accuracy_screen_passed=True))

    def test_busy_live_app_prevents_even_a_resumed_child(self):
        with patch.object(queue.study.night,'live_busy',return_value=True):
            with self.assertRaisesRegex(AssertionError,'Live app'):
                queue.child('unused.py',[],'unused',queue.OUT/'unused.json')


if __name__=='__main__':unittest.main()
