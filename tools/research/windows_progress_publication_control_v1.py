"""Synthetic Windows sharing-conflict controls; no training or poker evaluation."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch
from board_full_followup_queue_v1 import OUT, sha
from board_prefix_publication_v1 import atomic_json
from windows_progress_publication_v1 import publish_progress, status_only


def main():
    assert os.name == 'nt'
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    def open_handle(path, share):
        handle = kernel.CreateFileW(str(path), 0x80000000, share, None, 3, 0, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        return handle
    began = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='gtopen-progress-control-') as name:
        folder = Path(name)
        path = folder / 'control-status.json'
        first, next_value = dict(state='first'), dict(state='next', completed_deals=32)
        assert publish_progress(path, first) == 0
        handle = open_handle(path, 3)  # READ + WRITE; deliberately omit DELETE.
        timer = threading.Timer(.25, lambda: kernel.CloseHandle(handle))
        timer.start()
        try:
            retries = publish_progress(path, next_value)
        finally:
            timer.join()
        assert retries > 0 and json.loads(path.read_text()) == next_value
        # Persistent sharing denial must remain a bounded failure, with evidence.
        handle = open_handle(path, 3)
        start = time.monotonic()
        try:
            try:
                publish_progress(path, first, timeout=.15)
            except OSError as error:
                assert error.winerror in (5, 32, 33)
            else:
                raise AssertionError('Persistent denial silently accepted')
        finally:
            kernel.CloseHandle(handle)
        assert .14 <= time.monotonic()-start < 2
        pending = list(folder.glob('.status-retry-*.pending'))
        assert len(pending) == 1 and json.loads(pending[0].read_text()) == first
        assert json.loads(path.read_text()) == next_value
        # An unrelated I/O failure must not be retried or suppressed.
        error = OSError('synthetic disk failure')
        with patch('windows_progress_publication_v1.os.replace', side_effect=error) as mocked:
            try:
                publish_progress(path, first)
            except OSError as got:
                assert got is error
            else:
                raise AssertionError('Unrelated error suppressed')
            assert mocked.call_count == 1
        original = lambda value: None
        driver = SimpleNamespace(OUT=folder, PREFIX='scoped', write_status=original)
        for fail in (False, True):
            try:
                with status_only(driver):
                    assert driver.write_status is not original
                    driver.write_status(next_value)
                    if fail:
                        raise RuntimeError('synthetic callback failure')
            except RuntimeError as got:
                assert fail and str(got) == 'synthetic callback failure'
            assert driver.write_status is original
        assert json.loads((folder / 'scoped-status.json').read_text()) == next_value
        try:
            publish_progress(folder / 'immutable-result.json', first)
        except ValueError:
            pass
        else:
            raise AssertionError('Result publication accepted')
        assert not (folder / 'immutable-result.json').exists()
        # MoveFileEx may still reject an open target even with DELETE sharing.
        # Qualify recovery when that reader closes; do not assume it cannot block.
        handle = open_handle(path, 7)
        timer = threading.Timer(.25, lambda: kernel.CloseHandle(handle))
        timer.start()
        try:
            shared_retries = publish_progress(path, first)
        finally:
            timer.join()
        assert json.loads(path.read_text()) == first
    paths = [Path(__file__), Path(__file__).with_name('windows_progress_publication_v1.py'),
        Path(__file__).with_name('board_status_recovery_v1.py')]
    value = dict(passed=True, inputs={str(p): sha(p) for p in paths},
        real_sharing_collision_recovered=True, transient_retries=retries,
        persistent_denial_bounded=True, unrelated_error_propagated=True,
        scope_restored_on_success_and_failure=True, non_status_path_rejected=True,
        delete_sharing_reader_retry_qualified=True, delete_sharing_retries=shared_retries,
        synthetic_only=True,
        fresh_test_deals_drawn=0, seconds=time.monotonic()-began)
    atomic_json(OUT / 'windows-progress-publication-control-v1-result.json', value)
    print(json.dumps(value), flush=True)


if __name__ == '__main__':
    main()
