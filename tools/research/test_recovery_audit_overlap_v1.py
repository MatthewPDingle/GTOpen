"""Completion is gated by the exact prefix audit, including failure/disappearance."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,Mock
import psutil
from sampled_physical_root_evaluation_v1 import ROOT
from hu_later_action_volume_continuation_20260925 import prefix_audit_state


class PrefixGate(unittest.TestCase):
    def setUp(self):
        self.base=(ROOT/'target/recovery-gate-unit-tests').resolve();self.base.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=self.base);self.root=Path(self.temp.name).resolve()
        assert self.root.is_relative_to(self.base)
        self.path=self.root/'audit.json'
        self.reg=dict(prefix_review_path=str(self.path),prefix_registration_sha256='registration',
            prefix_result_sha256='result',prefix_readback_registration_sha256='reader',
            prefix_completed_iterations=52,resume_checkpoint={'sha256':'checkpoint'},
            prefix_reader_pid=123,prefix_reader_create_time=456.)
        self.good=dict(passed=True,source_registration_sha256='registration',source_result_sha256='result',
            readback_registration_sha256='reader',completed_updates=52,final_checkpoint={'sha256':'checkpoint'})

    def tearDown(self):
        assert Path(self.temp.name).resolve().is_relative_to(self.base);self.temp.cleanup()

    def test_exact_live_audit_is_pending_not_complete(self):
        process=Mock();process.is_running.return_value=True;process.create_time.return_value=456.
        process.cmdline.return_value=['python','hu_later_action_prefix_audit_20260925.py','--run']
        with patch('hu_later_action_volume_continuation_20260925.psutil.Process',return_value=process):
            self.assertFalse(prefix_audit_state(self.reg))

    def test_success_requires_all_bound_identities(self):
        self.path.write_text(json.dumps(self.good));self.assertTrue(prefix_audit_state(self.reg))
        for key in ('source_registration_sha256','source_result_sha256','readback_registration_sha256',
                    'completed_updates','final_checkpoint'):
            self.path.write_text(json.dumps(dict(self.good,**{key:'wrong'})))
            with self.assertRaises(AssertionError):prefix_audit_state(self.reg)

    def test_failed_audit_refused(self):
        self.path.write_text(json.dumps({'passed':False,'error':'corrupt evidence'}))
        with self.assertRaises(AssertionError):prefix_audit_state(self.reg)

    def test_missing_process_refused(self):
        with patch('hu_later_action_volume_continuation_20260925.psutil.Process',side_effect=psutil.NoSuchProcess(123)):
            with self.assertRaises(psutil.NoSuchProcess):prefix_audit_state(self.reg)

    def test_reused_pid_refused(self):
        process=Mock();process.is_running.return_value=True;process.create_time.return_value=999.
        with patch('hu_later_action_volume_continuation_20260925.psutil.Process',return_value=process):
            with self.assertRaises(AssertionError):prefix_audit_state(self.reg)


if __name__=='__main__':unittest.main()
