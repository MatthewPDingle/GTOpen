import unittest
import continuation_transfer_audit as audit


class TransferAuditChecks(unittest.TestCase):
    def test_preexisting_labels_are_refused(self):
        with self.assertRaises(AssertionError):audit.verify_time(99.,100.)
        audit.verify_time(100.,100.)

    def test_wrong_manifest_or_model_refused(self):
        frozen=dict(sha256='candidate',evaluation_manifest_id='manifest',references_at_freeze=0,frozen_at='2026-09-16T17:00:00+00:00')
        self.assertGreater(audit.verify_freeze(frozen,{'id':'manifest'},'candidate'),0)
        with self.assertRaises(AssertionError):audit.verify_freeze(frozen,{'id':'other'},'candidate')
        with self.assertRaises(AssertionError):audit.verify_freeze(frozen,{'id':'manifest'},'other')

    def test_nonzero_labels_at_freeze_refused(self):
        frozen=dict(sha256='candidate',evaluation_manifest_id='manifest',references_at_freeze=1,frozen_at='2026-09-16T17:00:00+00:00')
        with self.assertRaises(AssertionError):audit.verify_freeze(frozen,{'id':'manifest'},'candidate')


if __name__=='__main__':unittest.main()
