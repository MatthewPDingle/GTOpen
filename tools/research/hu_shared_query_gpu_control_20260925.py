"""Deferred full-batch GPU qualification on previously inspected control deals.

Refuses to start before the fresh evaluation worker has completed and released
its research lock. It may overlap the independent CPU reader. No fresh outcomes
are read, no new deals sampled, and no production or live-study source changes.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import gc
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read, load_complete_cache
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK, OTHER, setup_cuda, guard_for
from hu_root_retained_storage_admitted_study_20260924 import measure, LIMIT, METADATA_RESERVE
from hu_action_integrated_exact_20260925 import bank_args
from frozen_complete_trial_bank_v1 import load_completed_trial
from action_integrated_policy_bulk_v1 import ActionIntegratedCudaBankBulk64
from action_integrated_policy_shared_v1 import ActionIntegratedCudaBankShared64
from crossed_complete_policy_batch_v1 import evaluate_batch as original_batch
from crossed_complete_policy_batch_shared_v1 import evaluate_batch as shared_batch
from sampled_evidence_archive_v1 import read_artifact
from owned_batch_archive_gzip6_v1 import OwnedBatchArchive

PREFIX = 'shared-query-gpu-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
SOURCE = 'later-action-recovered-evaluation-control-v1'
STUDY = 'later-action-compact-evaluation-study-v1'
ORDER = ('original', 'shared', 'shared', 'original')
CAP = 100_000_000


def readback():
    # This branch runs in its own CPU-only child, never in the CUDA process.
    from hu_later_action_compact_evaluation_review_20260925 import verify_batch, verify_stability
    from archived_evaluation_reader_v1 import ArchivedEvaluationReader
    started = time.monotonic()
    result_path = OUT/f'{PREFIX}-result.json'
    result = read(result_path)
    reg_path = OUT/f'{PREFIX}-registration.json'
    reg = read(reg_path)
    assert result['passed'] and result['registration_sha256'] == sha(reg_path)
    assert reg['fresh_deals'] is False and reg['distinct_inspected_deals'] == 64
    expected = [(mode, source) for mode in ORDER for source in reg['source_batches']]
    assert [(row['mode'], row['source']) for row in result['jobs']] == expected
    assert [row['name'] for row in result['jobs']] == [f'test-{i:06d}' for i in range(8)]
    assert set(result['archive_manifest_hashes']) == {row['name'] for row in result['jobs']}
    def guard():
        assert time.monotonic()-started < 600 and idle()
    for path, digest in reg['inputs'].items():
        guard(); assert sha(path) == digest, path
    source_result = read(OUT/f'{SOURCE}-result.json')
    source_store = Path(source_result['store'])
    assert sha(source_store/'root-stability.json') == source_result['root_stability_sha256']
    roots = verify_stability(read(source_store/'root-stability.json'),
        read(OUT/'preflop-allin-matrix-control-v1-matrix.json'))
    cache = load_complete_cache()
    reader = ArchivedEvaluationReader(STORE, result['archive_manifest_hashes'],
        external_files=[], guard=guard)
    source = (OUT/'bb-context-candidate.json').read_text()
    observations = 0
    for row in result['jobs']:
        guard()
        folder = source_store/row['source']
        manifest = read(folder/'manifest.json')
        assert sha(folder/'manifest.json') == source_result['archive_manifest_hashes'][row['source']]
        batch = json.loads(read_artifact(folder, manifest, 'query-batch.json', guard=guard))
        _, count, digest = verify_batch(reader, STORE/row['name'], batch, source, cache, roots)
        assert digest == row['summary_sha256']
        observations += count
    for path, digest in reg['inputs'].items():
        guard(); assert sha(path) == digest, path
    save(OUT/f'{PREFIX}-independent-review.json', dict(passed=True,
        source_result_sha256=sha(result_path), registration_sha256=sha(reg_path),
        batches=len(result['jobs']), observations=observations,
        seconds=time.monotonic()-started, gpu_used=False,
        scope='Independent semantic readback of repeated control batches; no new poker evidence.'))


def run():
    assert idle() and not LOCK.exists() and not OTHER.exists()
    status_path = OUT/f'{STUDY}-status.json'
    study_result_path = OUT/f'{STUDY}-result.json'
    status, study = read(status_path), read(study_result_path)
    assert status['state'] == 'complete' and status['exit_code'] == 0 and status['error'] is None
    assert study['passed'] and study['complete'] and study['deals'] == 65536
    # Only completion metadata is used; fresh analysis/outcome files are excluded.
    assert not STORE.exists()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists() and not (OUT/f'{PREFIX}-result.json').exists()
    source_result_path = OUT/f'{SOURCE}-result.json'
    source_review_path = OUT/f'{SOURCE}-independent-review.json'
    source_result, source_review = read(source_result_path), read(source_review_path)
    assert source_result['passed'] and source_result['complete'] and source_review['passed']
    assert source_review['source_result_sha256'] == sha(source_result_path)
    source_reg = read(OUT/f'{SOURCE}-registration.json')
    assert source_result['registration_sha256'] == sha(OUT/f'{SOURCE}-registration.json')
    source_store = Path(source_result['store'])
    identities_path = source_store/'bank-identities.json'
    assert sha(identities_path) == source_result['bank_identities_sha256']
    source_identities = read(identities_path)
    context = OUT/'bb-context-candidate.json'
    query_exe = ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'
    evaluation_exe = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    paths = [status_path, study_result_path, source_result_path, source_review_path,
        OUT/f'{SOURCE}-registration.json', identities_path, context, query_exe, evaluation_exe,
        source_store/'root-stability.json', OUT/'preflop-allin-matrix-control-v1-matrix.json']
    inputs = {str(p): sha(p) for p in (ROOT/'tools/research').glob('*.py')}
    inputs.update(source_reg['inputs'])
    sources = []
    for name in ('test-000000', 'test-000032'):
        folder = source_store/name
        assert sha(folder/'manifest.json') == source_result['archive_manifest_hashes'][name]
        manifest = read(folder/'manifest.json')
        raw = {member: read_artifact(folder, manifest, member, guard=lambda: None)
               for member in manifest['artifacts']}
        sources.append(dict(name=name, batch=json.loads(raw['query-batch.json']),
                            summary=json.loads(raw['summary.json'])))
        paths.extend([folder/'manifest.json', *(folder/item['file'] for item in manifest['artifacts'].values())])
    inputs.update({str(p): sha(p) for p in paths})
    for path, digest in inputs.items(): assert sha(path) == digest, path
    inventory = measure()
    projected = sum(row['allocated_file_bytes'] for row in inventory)+CAP+METADATA_RESERVE
    assert projected <= LIMIT
    reg = dict(prefix=PREFIX, store=str(STORE), inputs=inputs, order=list(ORDER),
        training_prefixes=source_reg['training_prefixes'], source_batches=[s['name'] for s in sources],
        distinct_inspected_deals=64, replayed_batches=8, fresh_deals=False,
        models_per_chunk=8, maximum_seconds=1800, maximum_output_bytes=CAP,
        storage_inventory=inventory, projected_allocated_bytes=projected,
        production_modified=False, live_study_modified=False,
        scope='Exact full-batch equivalence and balanced timing under possible concurrent CPU review. No new range-quality evidence.')
    save(rp, reg)
    started = time.monotonic(); acquired = False; error = None; jobs = []; manifests = {}
    try:
        with LOCK.open('x') as stream: stream.write(str(os.getpid()))
        acquired = True
        assert idle() and not OTHER.exists()
        setup_cuda(); base_guard = guard_for(reg); last_space = 0.
        def guard():
            nonlocal last_space
            base_guard()
            assert time.monotonic()-started < reg['maximum_seconds']
            if time.monotonic()-last_space > 2:
                assert shutil.disk_usage('S:/').free >= 40_000_000_000
                pipeline = read(OUT/'later-action-compact-pipeline-v1-status.json')
                assert pipeline['state'] in ('running', 'complete') and pipeline['error'] is None
                last_space = time.monotonic()
        guard()
        STORE.mkdir()
        args = bank_args(context.read_text())
        original_banks = []; shared_banks = []; identities = []
        for prefix in reg['training_prefixes']:
            models, weights, identity = load_completed_trial(OUT, prefix,
                expected_updates=78, bank_args=args, guard=guard)
            original_banks.append(ActionIntegratedCudaBankBulk64(models, weights,
                completed_iterations=78, models_per_chunk=8, guard=guard, **args))
            shared_banks.append(ActionIntegratedCudaBankShared64(models, weights,
                completed_iterations=78, models_per_chunk=8, guard=guard, **args))
            identities.append(identity); del models
            print(json.dumps(dict(loaded_bank=prefix)), flush=True)
        assert identities == source_identities
        save(STORE/'bank-identities.json', identities)
        cache = load_complete_cache(); archives = OwnedBatchArchive.create(STORE, guard=guard)
        import torch
        for mode in ORDER:
            for source in sources:
                guard(); torch.cuda.synchronize()
                name = f'test-{len(jobs):06d}'; before = time.monotonic()
                folder = archives.begin(name)
                summary = (original_batch if mode == 'original' else shared_batch)(
                    batch=source['batch'], folder=folder, context_path=context,
                    banks=original_banks if mode == 'original' else shared_banks,
                    cache=cache, query_executable=query_exe, evaluation_executable=evaluation_exe, guard=guard)
                assert summary['artifacts'] == source['summary']['artifacts'], 'Native or transport bytes changed'
                assert summary['coverage'] == source['summary']['coverage'], 'Policy or own-reach bytes changed'
                assert summary['values'] == source['summary']['values']
                summary_sha = sha(folder/'summary.json')
                manifests[name] = archives.publish(name)
                assert archives.release(name) == manifests[name]
                elapsed = time.monotonic()-before
                row = dict(name=name, mode=mode, source=source['name'], seconds=elapsed,
                    averaging_seconds=summary['averaging_seconds'], summary_sha256=summary_sha)
                jobs.append(row); print(json.dumps(row), flush=True)
        for path, digest in inputs.items(): guard(); assert sha(path) == digest, path
        totals = {mode: sum(row['seconds'] for row in jobs if row['mode'] == mode) for mode in ('original', 'shared')}
        save(OUT/f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
            jobs=jobs, archive_manifest_hashes=manifests, totals=totals,
            full_batch_speedup=totals['original']/totals['shared'],
            candidate_faster=totals['shared'] < totals['original'],
            seconds=time.monotonic()-started, policies_reaches_transports_native_values_byte_identical=True,
            independent_review_required=True, production_modified=False, accuracy_qualified=False,
            scope='Repeated inspected deals; timing includes preparation through verified archive publication, excludes initial loading and the separate semantic reader.'))
        del original_banks, shared_banks, cache
        gc.collect(); torch.cuda.empty_cache()
        remaining = reg['maximum_seconds']-(time.monotonic()-started)
        assert remaining > 0
        process = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--review'], cwd=ROOT,
            capture_output=True, text=True, timeout=min(650, remaining), creationflags=subprocess.CREATE_NO_WINDOW)
        (OUT/f'{PREFIX}-review.log').write_text(process.stdout+process.stderr)
        assert process.returncode == 0, process.stderr[-2000:]
        review = read(OUT/f'{PREFIX}-independent-review.json')
        assert review['passed'] and review['source_result_sha256'] == sha(OUT/f'{PREFIX}-result.json')
    except BaseException as exc:
        error = repr(exc); raise
    finally:
        if acquired:
            assert LOCK.read_text().strip() == str(os.getpid()); LOCK.unlink()
        save(OUT/f'{PREFIX}-status.json', dict(state='failed' if error else 'complete', error=error,
            completed_batches=len(jobs), seconds=time.monotonic()-started, production_modified=False))


if __name__ == '__main__':
    assert sys.argv[1:] in (['--run'], ['--review'])
    (run if sys.argv[1] == '--run' else readback)()
