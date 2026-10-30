"""Own only explicitly assigned research subprocesses and their descendants.

Windows 8+ nested jobs; no breakaway or UI restrictions. An unnamed,
non-inheritable handle makes coordinator exit close the final job handle.
Sources: https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
"""
import ctypes
from ctypes import wintypes as w
import os


class BasicLimits(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong),
                ('PerJobUserTimeLimit', ctypes.c_longlong), ('LimitFlags', w.DWORD),
                ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', w.DWORD),
                ('Affinity', ctypes.c_size_t), ('PriorityClass', w.DWORD),
                ('SchedulingClass', w.DWORD)]


class IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in
                ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [('BasicLimitInformation', BasicLimits), ('IoInfo', IoCounters),
                ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]


class Accounting(ctypes.Structure):
    _fields_ = [(name, ctypes.c_longlong) for name in
                ('TotalUserTime', 'TotalKernelTime', 'ThisPeriodTotalUserTime', 'ThisPeriodTotalKernelTime')]
    _fields_ += [(name, w.DWORD) for name in
                 ('TotalPageFaultCount', 'TotalProcesses', 'ActiveProcesses', 'TotalTerminatedProcesses')]


class OwnedJob:
    def __init__(self):
        if os.name != 'nt':
            raise RuntimeError('Windows job ownership required')
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        for name, args, result in (
            ('CreateJobObjectW', [ctypes.c_void_p, w.LPCWSTR], w.HANDLE),
            ('SetInformationJobObject', [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD], w.BOOL),
            ('QueryInformationJobObject', [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p], w.BOOL),
            ('AssignProcessToJobObject', [w.HANDLE, w.HANDLE], w.BOOL),
            ('IsProcessInJob', [w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL)], w.BOOL),
            ('GetCurrentProcess', [], w.HANDLE),
            ('CloseHandle', [w.HANDLE], w.BOOL),
        ):
            fn = getattr(self.api, name); fn.argtypes = args; fn.restype = result
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # KILL_ON_JOB_CLOSE only.
        try:
            self._check(self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        except BaseException:
            self.close(); raise

    @staticmethod
    def _check(ok):
        if not ok:
            raise ctypes.WinError(ctypes.get_last_error())

    def assign(self, process):
        """Accept a live Popen handle created by the caller, never a bare PID."""
        if not self.handle or process.poll() is not None:
            raise ValueError('Live owned subprocess and open job required')
        self._check(self.api.AssignProcessToJobObject(self.handle, int(process._handle)))
        inside = w.BOOL()
        self._check(self.api.IsProcessInJob(int(process._handle), self.handle, ctypes.byref(inside)))
        if not inside.value:
            raise RuntimeError('Child job assignment was not confirmed')
        parent_inside = w.BOOL()
        self._check(self.api.IsProcessInJob(self.api.GetCurrentProcess(), self.handle, ctypes.byref(parent_inside)))
        if parent_inside.value:
            raise RuntimeError('Coordinator must not belong to its child job')

    def accounting(self):
        if not self.handle:
            raise ValueError('Job is closed')
        value = Accounting()
        self._check(self.api.QueryInformationJobObject(self.handle, 1, ctypes.byref(value), ctypes.sizeof(value), None))
        return dict(active_processes=value.ActiveProcesses, total_processes=value.TotalProcesses,
                    terminated_processes=value.TotalTerminatedProcesses,
                    user_seconds=value.TotalUserTime/10_000_000,
                    kernel_seconds=value.TotalKernelTime/10_000_000)

    def close(self):
        if self.handle:
            handle, self.handle = self.handle, None
            self._check(self.api.CloseHandle(handle))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
