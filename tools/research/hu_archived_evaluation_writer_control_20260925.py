"""Existing-fixture replay and failure controls for new owned batch cleanup."""
import json
from pathlib import Path
import shutil
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from owned_batch_archive_v1 import OwnedBatchArchive, ARTIFACTS
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from wider_root_evaluation_v3 import run
from wider_root_readback_v3 import review
from hu_root_retained_storage_admitted_study_20260924 import measure
from reboot_research_idle_v1 import idle

PREFIX = 'archived-evaluation-writer-control-v1'
BASE = Path('T:/GTOpen-research')/PREFIX
PRIOR = 'root-retained-wider-cpu-control-v1'
CAP = 500_000_000


def main():
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 1200 and idle()
        assert psutil.virtual_memory().available >= 20_000_000_000
        assert shutil.disk_usage('T:/').free >= 40_000_000_000
    guard(); assert not BASE.exists()
    rp = OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    old_reg_path = OUT/f'{PRIOR}-registration.json'
    old_result_path = OUT/f'{PRIOR}-result.json'
    reg, previous = read(old_reg_path), read(old_result_path)
    source = Path(reg['store']); context = OUT/'bb-context-candidate.json'
    assert previous['passed'] and previous['registration_sha256'] == sha(old_reg_path)
    assert previous['result_sha256'] == sha(source/'result.json')
    sources = {str(p):sha(p) for p in source.rglob('*') if p.is_file()}
    paths = [Path(__file__).resolve(), old_reg_path, old_result_path, context,
             Path(reg['prior_response_path']), *[ROOT/'tools/research'/n for n in (
                'owned_batch_archive_v1.py','sampled_evidence_archive_v1.py',
                'archived_evaluation_reader_v1.py','wider_root_evaluation_v3.py',
                'wider_root_readback_v3.py')]]
    inputs = {str(p):sha(p) for p in paths}
    roots = measure(); used = sum(x['allocated_file_bytes'] for x in roots)
    assert used+CAP+12_000_000_000+2_000_000_000 <= 800_000_000_000
    save(rp,dict(inputs=inputs,sources=sources,storage_inventory=roots,maximum_new_bytes=CAP,
        reserved_queued_trial_bytes=12_000_000_000,maximum_seconds=1200,
        scope='Replay existing native artifacts only; remove only this control own verified temporary copies.',
        original_sources_unchanged=True,fresh_poker_samples=0,gpu_used=False,production_modified=False))
    BASE.mkdir()
    peak_bytes = 0
    def capacity():
        nonlocal peak_bytes
        guard()
        size = sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())
        peak_bytes = max(peak_bytes,size); assert size <= CAP
    calls = []
    def fixture(context_path,batch,folder,guard,bank,cache):
        original = source/folder.name
        assert batch == read(original/'query-batch.json')
        folder.mkdir(exist_ok=False)
        for name in ARTIFACTS:
            shutil.copy2(original/name,folder/name)
        calls.append(folder.name);capacity()
        return read(folder/'summary.json')
    store = BASE/'evaluation'
    result = run(context,None,None,reg['exact'],reg['config'],store,guard,
        prior_response_path=reg['prior_response_path'],batch_evaluator=fixture)
    reader = ArchivedEvaluationReader(store,result['archive_manifest_hashes'],
        external_files=[context,reg['prior_response_path']],guard=guard)
    audit = review(context,store,reg['config'],reg['exact'],reg['cache_sha256'],guard,
        prior_response_path=reg['prior_response_path'],read_artifact_json=reader.read_json,
        artifact_sha256=reader.sha256)
    assert audit == previous['independent_readback']
    old = read(source/'result.json')
    added = {'archive_manifest_hashes','archive_owner_sha256','storage_encoding'}
    timing = {'seconds','phase_timings'}
    assert {k:v for k,v in result.items() if k not in added|timing} == {k:v for k,v in old.items() if k not in timing}
    assert len(calls) == len(set(calls)) == 30
    assert not any(p.is_dir() for p in (store/'.batch-work').iterdir())
    # Failures use new owned copies, never the original registered fixture.
    failures = BASE/'failure-fixtures'; failures.mkdir()
    writer = OwnedBatchArchive.create(failures,guard=guard)
    template = source/'train-000000'; passed = []
    def create(name):
        scratch = writer.begin(name); shutil.copytree(template,scratch);capacity();return scratch
    def reject(label,fn):
        try:fn()
        except (ValueError,FileNotFoundError,RuntimeError):passed.append(label)
        else:raise AssertionError('Failure did not preserve scratch: '+label)
    scratch = create('train-000000')
    reject('no-receipt-no-cleanup',lambda:writer.release('train-000000'))
    assert {p.name for p in scratch.iterdir()} == ARTIFACTS
    writer.publish('train-000000')
    # Simulate an interruption after the first exact temporary file removal.
    def interrupted_guard():
        guard()
        if scratch.exists() and len(list(scratch.iterdir())) < len(ARTIFACTS):
            raise RuntimeError('Simulated interrupted cleanup')
    writer.guard = interrupted_guard
    reject('interrupted-cleanup',lambda:writer.release('train-000000'))
    assert len(list(scratch.iterdir())) == len(ARTIFACTS)-1
    writer = OwnedBatchArchive(failures,writer.owner_sha256,guard=guard)
    writer.release('train-000000');assert not scratch.exists()
    writer.release('train-000000');passed.append('idempotent-completed-cleanup')
    scratch = create('train-000016');writer.publish('train-000016')
    packed = failures/'train-000016'/'summary.json.gz'
    raw = packed.read_bytes();packed.write_bytes(bytes([raw[0]^1])+raw[1:])
    reject('damaged-archive-no-cleanup',lambda:writer.release('train-000016'))
    assert {p.name for p in scratch.iterdir()} == ARTIFACTS
    scratch = create('train-000032');writer.publish('train-000032')
    (scratch/'summary.json').write_bytes(b'changed temporary file')
    reject('changed-scratch-no-cleanup',lambda:writer.release('train-000032'))
    assert {p.name for p in scratch.iterdir()} == ARTIFACTS
    reject('wrong-owner',lambda:OwnedBatchArchive(failures,'0'*64,guard=guard))
    reject('outside-batch-name',lambda:writer.begin('../outside'))
    reject('existing-batch',lambda:writer.begin('train-000032'))
    # Keep intentionally damaged fixtures; they have no valid completion claim.
    capacity()
    for p,h in {**inputs,**sources}.items():guard();assert sha(p)==h,p
    outputs = {str(p):sha(p) for p in BASE.rglob('*') if p.is_file()}
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
        independent_readback=audit,complete_batches=30,unchanged_original_files=len(sources),
        failure_controls=passed,maximum_observed_file_bytes=peak_bytes,
        retained_file_bytes=sum(Path(p).stat().st_size for p in outputs),output_files=outputs,
        seconds=time.monotonic()-started,original_sources_unchanged=True,gpu_used=False,
        fresh_poker_samples=0,production_modified=False,accuracy_qualified=False,
        scope='Existing fixture replay and new temporary-file lifecycle; native inference integration and power-loss recovery not established.'))
    print(json.dumps(dict(passed=True,batches=30,failure_controls=passed,
        maximum_observed_file_bytes=peak_bytes,seconds=time.monotonic()-started)),flush=True)


if __name__ == '__main__':main()
