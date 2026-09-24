"""Replay a complete existing evaluation through authenticated gzip batches.

CPU-only transport test: no training, new poker samples, original-file changes,
deletions, or interaction with the live trial's sources or stores.
"""
import hashlib
import json
from pathlib import Path
import shutil
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from sampled_evidence_archive_v1 import archive
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from wider_root_readback_v2 import review as old_review
from wider_root_readback_v3 import review
from hu_root_retained_storage_admitted_study_20260924 import measure
from reboot_research_idle_v1 import idle

PREFIX = 'archived-wider-readback-control-v1'
BASE = Path('T:/GTOpen-research') / PREFIX
STORE = BASE / 'evaluation'
PRIOR = 'root-retained-wider-cpu-control-v1'
CAP = 500_000_000


def main():
    started = time.monotonic()
    def guard():
        assert time.monotonic() - started < 1200 and idle()
        assert psutil.virtual_memory().available >= 20_000_000_000
        assert shutil.disk_usage('T:/').free >= 40_000_000_000

    guard()
    assert not BASE.exists()
    rp = OUT / f'{PREFIX}-registration.json'
    assert not rp.exists()
    old_reg_path = OUT / f'{PRIOR}-registration.json'
    old_result_path = OUT / f'{PRIOR}-result.json'
    old_reg, old_result = read(old_reg_path), read(old_result_path)
    assert old_result['passed'] and old_result['independent_readback']['passed']
    assert old_result['registration_sha256'] == sha(old_reg_path)
    source = Path(old_reg['store'])
    assert old_result['result_sha256'] == sha(source / 'result.json')
    context = OUT / 'bb-context-candidate.json'
    prior_response = Path(old_reg['prior_response_path'])
    assert sha(context) == old_reg['exact']['context_sha256']
    assert sha(prior_response) == old_reg['prior_response_sha256']
    sources = {str(p): sha(p) for p in source.rglob('*') if p.is_file()}
    paths = [Path(__file__).resolve(), old_reg_path, old_result_path, context,
             prior_response, *[ROOT / 'tools/research' / name for name in (
                 'sampled_evidence_archive_v1.py', 'archived_evaluation_reader_v1.py',
                 'wider_root_readback_v2.py', 'wider_root_readback_v3.py')]]
    inputs = {str(p): sha(p) for p in paths}
    roots = measure()
    used = sum(x['allocated_file_bytes'] for x in roots)
    # Include the entire queued replication allowance as well as this control.
    assert used + CAP + 12_000_000_000 + 2_000_000_000 <= 800_000_000_000
    save(rp, dict(inputs=inputs, sources=sources, storage_inventory=roots,
         maximum_new_bytes=CAP, reserved_queued_trial_bytes=12_000_000_000,
         maximum_seconds=1200, original_sources_unchanged=True,
         fresh_poker_samples=0, gpu_used=False, production_modified=False))
    STORE.mkdir(parents=True)
    for p in source.iterdir():
        if p.is_file():
            shutil.copy2(p, STORE / p.name)
    result = read(source / 'result.json')
    manifests = {}
    for name in sorted(result['batch_summary_hashes']):
        guard()
        folder = source / name
        names = [p.name for p in folder.iterdir() if p.is_file()]
        assert all(p.endswith('.json') for p in names)
        archive(folder, names, STORE / name, guard=guard)
        manifests[name] = sha(STORE / name / 'manifest.json')
        assert sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file()) <= CAP
    external = [context, prior_response]
    reader = ArchivedEvaluationReader(STORE, manifests, external_files=external, guard=guard)
    kwargs = dict(prior_response_path=prior_response)
    original = old_review(context, source, old_reg['config'], old_reg['exact'],
                          old_reg['cache_sha256'], guard, **kwargs)
    plain = review(context, source, old_reg['config'], old_reg['exact'],
                   old_reg['cache_sha256'], guard, **kwargs)
    archived = review(context, STORE, old_reg['config'], old_reg['exact'],
                      old_reg['cache_sha256'], guard, read_artifact_json=reader.read_json,
                      artifact_sha256=reader.sha256, **kwargs)
    assert original == plain == archived == old_result['independent_readback']
    assert archived['complete_training_deals_replayed'] == 338
    assert archived['complete_population_test_deals_replayed'] == 128
    assert archived['intervals_reconstructed'] == 6
    # Independently compare every decoded artifact, including files that the
    # scalar audit only authenticates rather than interpreting numerically.
    for p, expected in sources.items():
        guard()
        copied = STORE / Path(p).relative_to(source)
        assert reader.read_bytes(copied) == Path(p).read_bytes()
        assert reader.sha256(copied) == expected
    rejected = []
    def rejects(label, fn):
        try:
            fn()
        except (ValueError, FileNotFoundError):
            rejected.append(label)
        else:
            raise AssertionError('Invalid archive accepted: ' + label)
    name = sorted(manifests)[0]
    bad = dict(manifests); bad[name] = '0' * 64
    rejects('manifest-identity', lambda: ArchivedEvaluationReader(
        STORE, bad, external_files=external, guard=guard).read_bytes(STORE/name/'summary.json'))
    rejects('unregistered-batch', lambda: reader.read_bytes(STORE/'train-999999'/'summary.json'))
    rejects('outside-root', lambda: reader.read_bytes(source/name/'summary.json'))
    rejects('parent-path', lambda: reader.read_bytes(STORE/name/'..'/'summary.json'))
    rejects('invalid-batch-name', lambda: ArchivedEvaluationReader(
        STORE, {'../outside': '0'*64}, external_files=external, guard=guard))
    for p, h in {**inputs, **sources}.items():
        guard(); assert sha(p) == h, p
    output_files = {str(p): sha(p) for p in BASE.rglob('*') if p.is_file()}
    stored_bytes = sum(Path(p).stat().st_size for p in output_files)
    assert stored_bytes <= CAP
    save(OUT / f'{PREFIX}-result.json', dict(passed=True,
         registration_sha256=sha(rp), independent_readback=archived,
         files_verified=len(sources), batches=len(manifests), manifest_hashes=manifests,
         output_files=output_files, original_logical_bytes=sum(Path(p).stat().st_size for p in sources),
         archived_file_bytes=stored_bytes, rejected_cases=rejected, seconds=time.monotonic()-started,
         original_sources_unchanged=True, fresh_poker_samples=0, gpu_used=False,
         production_modified=False, accuracy_qualified=False,
         scope='Lossless archived evidence replay only; no compressed evaluation writer or cleanup path deployed.'))
    print(json.dumps(dict(passed=True, batches=len(manifests), files=len(sources),
          archived_file_bytes=stored_bytes, seconds=time.monotonic()-started)), flush=True)


if __name__ == '__main__':
    main()
