"""Qualify closed-port parallel publication on copies of audited evidence."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
from types import SimpleNamespace
from unittest.mock import patch
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive, restore
from bounded_parallel_evaluation_archive_v2 import ParallelArchives, production_available

PREFIX = 'parallel-evaluation-archive-v2-control'
STORE = Path('S:/GTOpen-research') / PREFIX


def main():
    started = time.monotonic()
    last = 0.
    def guard():
        nonlocal last
        assert time.monotonic() - started < 600
        if time.monotonic() - last > 2:
            assert production_available() and psutil.virtual_memory().available > 24_000_000_000
            assert psutil.disk_usage('S:/').free > 40_000_000_000
            last = time.monotonic()
    guard()
    assert psutil.cpu_percent(interval=1) < 60
    rp, result_path = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not STORE.exists() and not rp.exists() and not result_path.exists()
    source_path = OUT / 'columnar-evaluation-archive-control-v1-result.json'
    source = read(source_path)
    assert source['passed'] and source['scalar_reader_deals'] == 32
    old = Path(source['store'])
    archive = old / 'test-000000.xz'
    manifest = old / 'test-000000.manifest.json'
    assert sha(manifest) == source['manifest_sha256']
    for p in (archive, manifest):
        assert sha(p) == source['artifacts'][str(p)]
    inputs = {str(p): sha(p) for p in [source_path, archive, manifest,
              *Path(__file__).parent.glob('*.py')]}
    save(rp, dict(inputs=inputs, store=str(STORE), workers=3, copied_batches=4,
                  maximum_seconds=600, maximum_output_bytes=100_000_000,
                  gpu_used=False, production_modified=False,
                  scope='Lossless parallel archives and failed-worker preservation; no new test deals.'))
    outcomes = []
    # Independently exercise closed, idle, busy, and indeterminate production.
    with patch('psutil.net_connections', return_value=[]), patch('reboot_research_idle_v1.idle') as probe:
        assert production_available() and not probe.called
        outcomes.append('closed port accepted without HTTP')
    connection = SimpleNamespace(status=psutil.CONN_LISTEN, laddr=SimpleNamespace(port=56708))
    for state in (False, True):
        with patch('psutil.net_connections', return_value=[connection]), patch('reboot_research_idle_v1.idle', return_value=state):
            assert production_available() is state
    outcomes.extend(['busy production rejected', 'verified idle production accepted'])
    with patch('psutil.net_connections', side_effect=psutil.AccessDenied):
        try:
            production_available()
        except psutil.AccessDenied:
            outcomes.append('indeterminate probe fails closed')
        else:
            raise AssertionError('Unknown production activity was accepted')
    parts = restore(archive, read(manifest), guard=guard)
    writer = OwnedColumnarEvaluationArchive.create(STORE, guard=guard)
    names = [f'test-{i:06d}' for i in range(4)]
    for name in names:
        folder = writer.begin(name)
        folder.mkdir()
        for member, raw in parts.items():
            with (folder / member).open('xb') as f:
                f.write(raw)
    # Three real hidden child processes, compared with the original slow decoder.
    queue = ParallelArchives(writer, guard=guard, maximum_workers=3)
    try:
        began = time.monotonic()
        for name in names[:3]:
            queue.submit(name)
        hashes = queue.drain()
        seconds = time.monotonic() - began
    finally:
        queue.close()
    for name in names[:3]:
        assert hashes[name] == source['manifest_sha256']
        assert (STORE / (name + '.xz')).read_bytes() == archive.read_bytes()
        assert restore(STORE / (name + '.xz'), read(STORE / (name + '.manifest.json')), guard=guard) == parts
        assert not (STORE / '.batch-work' / name).exists()
    # Malformed copied input must surface a child failure and preserve all copies.
    failed_name = names[-1]
    failed_folder = STORE / '.batch-work' / failed_name
    (failed_folder / 'profiles.json').write_bytes(b'{malformed')
    before = {p.name: sha(p) for p in failed_folder.iterdir()}
    queue = ParallelArchives(writer, guard=guard, maximum_workers=1)
    try:
        queue.submit(failed_name)
        try:
            queue.drain()
        except RuntimeError as exc:
            assert 'Archive worker failed' in str(exc)
            outcomes.append('failed worker reported and all raw copies preserved')
        else:
            raise AssertionError('Malformed evidence reported success')
    finally:
        queue.close()
    assert {p.name: sha(p) for p in failed_folder.iterdir()} == before
    assert not (STORE / (failed_name + '.manifest.json')).exists()
    for p, h in inputs.items():
        assert sha(p) == h, p
    logical = sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
    assert logical < 100_000_000
    result = dict(passed=True, registration_sha256=sha(rp), store=str(STORE),
                  worker_source_sha256=sha(ROOT / 'tools/research/bounded_parallel_evaluation_archive_v2.py'),
                  parallel_seconds=seconds, successful_batches=3, identical_original_members=21,
                  archive_bytes_identical=True, controls=outcomes, logical_bytes=logical,
                  artifacts={str(p): sha(p) for p in STORE.rglob('*') if p.is_file()},
                  seconds=time.monotonic() - started, gpu_used=False, production_modified=False,
                  accuracy_qualified=False)
    save(result_path, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'artifacts'}), flush=True)


if __name__ == '__main__':
    main()
