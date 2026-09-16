import unittest
import continuation_chance_control as control


class ChanceControlChecks(unittest.TestCase):
    def test_learned_flag_and_extra_work_are_refused(self):
        snapshot=dict(model='balanced',iteration=500,start_iteration=150,warmup_iterations=0,gaps=[.001,.002],evs=[.1,-.1])
        control.validate(snapshot,500,150)
        with self.assertRaises(AssertionError):control.validate(dict(snapshot,model='candidate'),500,150)
        with self.assertRaises(AssertionError):control.validate(dict(snapshot,warmup_iterations=50),500,150)
        with self.assertRaises(AssertionError):control.validate(dict(snapshot,start_iteration=0),500,150)


if __name__=='__main__':unittest.main()
