import datetime as dt
import unittest
import continuation_validation_queue as queue


class QueueChecks(unittest.TestCase):
    def test_all_qualification_parts_required(self):
        status=dict(stage='checks_complete',transfer_accuracy_passed=True)
        evaluation=dict(accuracy_screen_passed=True)
        audit=dict(audited_references=200,physical_bounds_passed=True,all_references_after_freeze=True)
        self.assertTrue(queue.qualified(status,evaluation,audit))
        for key in ['physical_bounds_passed','all_references_after_freeze']:
            self.assertFalse(queue.qualified(status,evaluation,dict(audit,**{key:False})))
        self.assertFalse(queue.qualified(status,dict(accuracy_screen_passed=False),audit))
        self.assertFalse(queue.qualified(status,evaluation,dict(audit,audited_references=199)))

    def test_deadline_does_not_extend(self):
        self.assertTrue(queue.enough_time(queue.DEADLINE-dt.timedelta(minutes=90)))
        self.assertFalse(queue.enough_time(queue.DEADLINE-dt.timedelta(minutes=89,seconds=59)))


if __name__=='__main__':unittest.main()
