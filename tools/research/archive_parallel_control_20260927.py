"""Bounded CPU-only archive throughput experiment on already inspected controls.

Separate subprocesses and temporary owned roots; never modifies live study
inputs, models, archives or GPU state. Outputs are retained for inspection.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import psutil

REPO = Path(__file__).resolve().parents[2]
CONTROL = Path('S:/GTOpen-research/showdown-composite-evaluation-control-v1')
OUT = REPO/'research/preflop-evolution/blind-defense-20260922'


def worker(mode, scratch, batch):
    import owned_columnar_evaluation_archive_v1 as archive
    import crossed_profile_columnar_v1 as base
    import crossed_profile_columnar_v2 as residual
    import crossed_profile_decoder_fast_candidate_20260927 as fast
    mp = CONTROL/(batch+'.manifest.json')
    original = CONTROL/(batch+'.xz')
    parts = archive.restore(original, json.loads(mp.read_text()), guard=lambda: None)
    if mode == 'candidate':
        base.decode = fast.decode_base
        residual.decode = fast.decode
        archive.decode_profiles = fast.decode
    else:
        assert mode == 'baseline'
    scratch = Path(scratch).absolute()
    archive.ROOT = scratch
    writer = archive.OwnedColumnarEvaluationArchive.create(scratch/'archive', guard=lambda: None)
    folder = writer.begin('test-000000'); folder.mkdir()
    for name, raw in parts.items():
        (folder/name).write_bytes(raw)
    started = time.perf_counter()
    identity = writer.publish('test-000000')
    assert writer.release('test-000000') == identity
    seconds = time.perf_counter()-started
    packed = (scratch/'archive/test-000000.xz').read_bytes()
    assert packed == original.read_bytes()
    print(json.dumps(dict(mode=mode, batch=batch, seconds=seconds,
        exact_original_archive=True, sha256=hashlib.sha256(packed).hexdigest())), flush=True)


def run():
    result_path = OUT/'archive-parallel-control-20260927-result.json'
    assert not result_path.exists()
    assert psutil.virtual_memory().available > 20_000_000_000
    assert shutil.disk_usage(tempfile.gettempdir()).free > 5_000_000_000
    scratch = Path(tempfile.mkdtemp(prefix='gtopen-archive-parallel-control-'))
    # Twelve fixed jobs, <= four simultaneous workers; no data-dependent tuning.
    registrations = dict(scratch=str(scratch), batches=['test-000000','test-000032']*2,
        variants=[['baseline',1],['candidate',1],['candidate',4]],
        maximum_seconds=600, maximum_scratch_bytes=1_000_000_000,
        inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__), REPO/'tools/research/crossed_profile_decoder_fast_candidate_20260927.py']},
        production_modified=False, study_modified=False)
    (OUT/'archive-parallel-control-20260927-registration.json').write_text(json.dumps(registrations,indent=2)+'\n')
    results=[]; children=[]; started=time.monotonic()
    try:
        for variant,(mode,parallelism) in enumerate(registrations['variants']):
            pending=list(enumerate(registrations['batches'])); live=[]; rows=[]; began=time.monotonic()
            while pending or live:
                assert time.monotonic()-started < 600
                assert psutil.virtual_memory().available > 20_000_000_000
                assert sum(p.stat().st_size for p in scratch.rglob('*') if p.is_file()) < 1_000_000_000
                while pending and len(live)<parallelism:
                    i,batch=pending.pop(0); job=scratch/f'v{variant}-job{i}';job.mkdir()
                    stream=(job/'worker.log').open('w')
                    child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',mode,str(job),batch],
                        cwd=REPO,stdout=stream,stderr=subprocess.STDOUT,
                        creationflags=subprocess.CREATE_NO_WINDOW)
                    children.append(child);live.append((child,stream,job))
                for child,stream,job in list(live):
                    if child.poll() is not None:
                        stream.close(); assert child.returncode==0,(job/'worker.log').read_text()
                        rows.append(json.loads((job/'worker.log').read_text()));live.remove((child,stream,job))
                if live:time.sleep(.1)
            row=dict(mode=mode,parallelism=parallelism,wall_seconds=time.monotonic()-began,workers=rows)
            results.append(row);print(json.dumps(row),flush=True)
        for p,h in registrations['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
        result=dict(passed=True,results=results,registration_sha256=hashlib.sha256(
            (OUT/'archive-parallel-control-20260927-registration.json').read_bytes()).hexdigest(),
            baseline_to_parallel_wall_ratio=results[0]['wall_seconds']/results[2]['wall_seconds'],
            candidate_serial_to_parallel_wall_ratio=results[1]['wall_seconds']/results[2]['wall_seconds'],
            maximum_scratch_bytes=1_000_000_000, production_modified=False,study_modified=False,
            limitation='CPU archive throughput only; concurrent study running; not end-to-end acceleration qualification.')
        result_path.write_text(json.dumps(result,indent=2)+'\n')
    finally:
        for child in children:
            if child.poll() is None:child.terminate();child.wait(timeout=10)


if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--worker':worker(*sys.argv[2:])
    else:
        assert sys.argv[1:]==['--run']
        run()
