import unittest
import continuation_shrunk_queue as queue


class ShrunkQueueChecks(unittest.TestCase):
    def test_checks_dependency_identity_instead_of_trusting_a_reused_pid(self):
        self.assertFalse(queue.dependency_alive([],42))
        self.assertTrue(queue.dependency_alive([dict(ProcessId=42,Name='python.exe',CommandLine='python continuation_night_queue.py 39132')],42))
        with self.assertRaisesRegex(AssertionError,'changed identity'):
            queue.dependency_alive([dict(ProcessId=42,Name='python.exe',CommandLine='python unrelated.py')],42)
        with self.assertRaises(AssertionError):
            queue.dependency_alive([dict(ProcessId=42,Name='not-python.exe',CommandLine='continuation_night_queue.py')],42)


if __name__=='__main__':unittest.main()
