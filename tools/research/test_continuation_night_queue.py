"""Process identity is authoritative; a stale status or recycled PID is not."""
import unittest
import continuation_night_queue as queue


class QueueChecks(unittest.TestCase):
    def test_dependency_identity_and_termination(self):
        process=dict(ProcessId=42,Name='python.exe',CommandLine='python tools/research/continuation_bridge_run.py run')
        self.assertTrue(queue.dependency_alive([process],42))
        self.assertFalse(queue.dependency_alive([process],43))
        self.assertFalse(queue.dependency_alive([],42))
        for changed in [dict(process,Name='gto-server.exe'),dict(process,CommandLine='python other-work.py')]:
            with self.assertRaisesRegex(AssertionError,'unexpected identity'):
                queue.dependency_alive([changed],42)


if __name__=='__main__':unittest.main()
