"""Bounded CPU archive subprocesses; callers retain deal order and statistics.

No GPU imports or inference. Each worker owns one disjoint batch. All original
archive publication, readback and release checks still execute. Failed workers
leave their evidence in place and fail the parent rather than retrying.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import json
from pathlib import Path
import subprocess
import sys
import time
import hashlib


def production_available():
    """A closed production port is idle; an open one must pass all API checks."""
    import psutil
    from reboot_research_idle_v1 import idle
    listening = any(c.status == psutil.CONN_LISTEN and c.laddr.port == 56708
                    for c in psutil.net_connections(kind='tcp'))
    return not listening or idle()


def install_fast_decoder():
    import crossed_profile_columnar_v1 as base
    import crossed_profile_columnar_v2 as residual
    import owned_columnar_evaluation_archive_v1 as archive
    import crossed_profile_decoder_fast_candidate_20260927 as fast
    base.decode = fast.decode_base
    residual.decode = fast.decode
    archive.decode_profiles = fast.decode


class ParallelArchives:
    def __init__(self, archive, *, guard, maximum_workers=4, control_root=None):
        assert type(maximum_workers) is int and 1 <= maximum_workers <= 4
        self.archive, self.guard, self.maximum_workers = archive, guard, maximum_workers
        self.control_root = control_root
        self.live = {}; self.completed = {}; self.submitted = set()
        self.closed = False

    def poll(self):
        self.guard()
        for name, (child, log, path, started) in list(self.live.items()):
            if child.poll() is None:
                if time.monotonic()-started > 120:
                    raise TimeoutError('Archive worker exceeded 120 seconds: '+name)
                continue
            log.close()
            if child.returncode != 0:
                raise RuntimeError('Archive worker failed; evidence retained: '+str(path))
            output = json.loads(path.read_text())
            assert output['name'] == name and output['owner_sha256'] == self.archive.owner_sha256
            mp = self.archive.root/(name+'.manifest.json')
            identity = hashlib.sha256(mp.read_bytes()).hexdigest()
            assert output['manifest_sha256'] == identity
            assert not (self.archive.root/'.batch-work'/name).exists()
            self.completed[name] = identity
            del self.live[name]

    def wait_slot(self):
        assert not self.closed
        self.poll()
        while len(self.live) >= self.maximum_workers:
            time.sleep(.05); self.poll()

    def submit(self, name):
        assert not self.closed and name not in self.submitted
        self.wait_slot()
        # Validate the owned path and claim before launching a child.
        source, _, _, claim, _ = self.archive._paths(name)
        self.archive._claim(name, claim)
        assert source.is_dir()
        logpath = self.archive.root/'.batch-work'/(name+'.worker.json')
        log = logpath.open('x')
        command = [sys.executable, str(Path(__file__).resolve()), '--worker',
                   str(self.archive.root), self.archive.owner_sha256, name]
        if self.control_root is not None:
            command += ['--control-root', str(self.control_root)]
        try:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW)
        except BaseException:
            log.close(); raise
        self.live[name] = (child, log, logpath, time.monotonic())
        self.submitted.add(name)

    def drain(self):
        while self.live:
            self.poll()
            if self.live: time.sleep(.05)
        assert set(self.completed) == self.submitted
        return dict(self.completed)

    def close(self):
        for child, log, _, _ in self.live.values():
            if child.poll() is None:
                child.terminate(); child.wait(timeout=10)
            log.close()
        self.closed = True


def worker(root, owner, name, control_root=None):
    import psutil
    import owned_columnar_evaluation_archive_v1 as archive
    install_fast_decoder()
    root = Path(root).absolute()
    if control_root is not None:
        import tempfile
        control_root = Path(control_root).absolute()
        assert control_root.parent == Path(tempfile.gettempdir()).absolute()
        assert control_root.name.startswith('gtopen-parallel-archive-control-')
        archive.ROOT = control_root
    started = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        assert time.monotonic()-started < 120
        if time.monotonic()-last > 2:
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert production_available()
            last = time.monotonic()
    a = archive.OwnedColumnarEvaluationArchive(root, owner, guard=guard)
    identity = a.publish(name)
    assert a.release(name) == identity
    print(json.dumps(dict(name=name, owner_sha256=owner, manifest_sha256=identity,
        seconds=time.monotonic()-started)), flush=True)


if __name__ == '__main__':
    assert sys.argv[1] == '--worker'
    if len(sys.argv) == 5:
        worker(*sys.argv[2:5])
    else:
        assert len(sys.argv) == 7 and sys.argv[5] == '--control-root'
        worker(*sys.argv[2:5], control_root=sys.argv[6])
