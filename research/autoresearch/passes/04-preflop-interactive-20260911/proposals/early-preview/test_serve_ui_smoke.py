"""Pure UI ownership/lifecycle gates; never launches a child or accesses an API."""
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('ui_smoke', Path(__file__).with_name('serve_ui_smoke.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SmokeGuards(unittest.TestCase):
    def test_private_paths_reject_root_and_escape(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.assertEqual(m.bounded_path(root/'run', root), (root/'run').resolve())
            for path in (root, root/'..'/'elsewhere'):
                with self.assertRaises(ValueError): m.bounded_path(path, root)

    def test_listener_identity_and_live_port_rejected(self):
        process = Mock(pid=12)
        process.poll.return_value = None
        row = {'pid':12, 'sha256':'abc', 'exe':str(Path('private.exe').resolve()), 'created':'first'}
        self.assertEqual(m.check_owner(row, process, 12345, 'private.exe', 'abc'), row)
        for altered in (dict(row,pid=13), dict(row,sha256='def'), dict(row,exe='else.exe')):
            with self.assertRaises(ValueError): m.check_owner(altered,process,12345,'private.exe','abc')
        with self.assertRaises(ValueError): m.check_owner(row,process,56708,'private.exe','abc')
        with self.assertRaises(ValueError):
            m.check_owner(row,process,12345,'private.exe','abc',dict(row,created='different'))
        process.poll.return_value = 0
        with self.assertRaises(ValueError): m.check_owner(row,process,12345,'private.exe','abc')

    def test_timeout_stop_and_uncertain_live_activity_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as name:
            stop = Path(name)/'stop'
            live = Mock()
            self.assertEqual(m.guard_reason(300,0,300,stop,live),'timeout')
            live.assert_not_called()
            stop.touch()
            self.assertEqual(m.guard_reason(1,0,300,stop,live),'owner_stop_file')
            stop.unlink()
            with patch.object(m.v,'DEADLINE',dt.datetime.max.replace(tzinfo=dt.timezone.utc)):
                self.assertIsNone(m.guard_reason(1,0,300,stop,live))
                live.side_effect = OSError('live unreadable')
                self.assertEqual(m.guard_reason(1,0,300,stop,live),'live_guard: live unreadable')

    def test_stop_cli_only_writes_matching_owned_sentinel(self):
        with tempfile.TemporaryDirectory() as name:
            area = Path(name)
            private = area/'run'
            private.mkdir()
            owner = private/'owner.json'
            stop = private/'stop-secret'
            owner.write_text(json.dumps({'token':'secret','port':12345,'stop_file':str(stop)}))
            with patch.object(m,'AREA',area):
                with self.assertRaises(ValueError): m.request_stop(owner,'wrong')
                self.assertFalse(stop.exists())
                m.request_stop(owner,'secret')
                self.assertTrue(stop.exists())
                stop.unlink()
                owner.write_text(json.dumps({'token':'secret','port':56708,'stop_file':str(stop)}))
                with self.assertRaises(ValueError): m.request_stop(owner,'secret')
                self.assertFalse(stop.exists())


if __name__ == '__main__':
    unittest.main()
