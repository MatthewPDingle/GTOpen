"""Fixed 65,536-deal comparison with immutable resumable batch prefixes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import json
import math
from pathlib import Path
import subprocess
import time
import uuid
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from weighted_complete_evaluation_support_v1 import (ARMS, CONTEXT, MATRIX, LOCK, OTHER, TEST_DEALS, TEST_SEED,
    complete_training_paths, load_banks, setup_cuda, catalog_roots)
from weighted_evaluation_runtime_v2 import runtime_guard
from weighted_evaluation_checkpoint_v1 import publish, restore_latest, committed
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive, durable, encoded
from bounded_parallel_evaluation_archive_v2 import ParallelArchives, production_available
from sampled_physical_deals_v1 import PhysicalDeals
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from crossed_complete_policy_batch_shared_v1 import evaluate_batch
from complete_bank_root_stability_v1 import summarize
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2')

PREFIX = 'weighted-complete-evaluation-study-v1'
CONTROL = 'weighted-complete-evaluation-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
REG = OUT / f'{PREFIX}-registration.json'


def qualification():
    paths = complete_training_paths()
    cr, cp, ca = [OUT / f'{CONTROL}-{s}.json' for s in ('registration', 'result', 'independent-review')]
    control, audit = read(cp), read(ca)
    assert control['passed'] and control['complete'] and control['control_only'] and control['deals'] == 64
    assert control['registration_sha256'] == sha(cr)
    assert audit['passed'] and audit['deals'] == 64 and audit['source_result_sha256'] == sha(cp)
    assert audit['source_registration_sha256'] == sha(cr)
    assert len(control['cpu_checks']) == 8 and len(control['root_cpu_checks']) == 4
    for row in control['cpu_checks'] + control['root_cpu_checks']:
        assert 0 <= row['maximum_policy_error'] < 1e-10 and 0 <= row['maximum_reach_error'] < 1e-10
    rr = OUT / f'{CONTROL}-readback-registration.json'
    assert audit['readback_registration_sha256'] == sha(rr)
    paths.extend([cr, cp, ca, rr])
    recovery_prefix = 'weighted-complete-checkpoint-control-v1'
    er, ep = [OUT / f'{recovery_prefix}-{s}.json' for s in ('registration', 'result')]
    recovery = read(ep)
    assert recovery['passed'] and recovery['registration_sha256'] == sha(er)
    assert recovery['exact_sampler_and_accumulator_resume'] and recovery['incomplete_attempts_preserved_and_excluded']
    assert recovery['helper_sha256'] == sha(ROOT / 'tools/research/weighted_evaluation_checkpoint_v1.py')
    paths.extend([er, ep, OUT / 'WEIGHTED-COMPLETE-EVALUATION-PLAN.md'])
    return paths, control


def immutable_json(path, value):
    raw = encoded(value)
    if path.exists():
        assert path.read_bytes() == raw, 'Previously published result changed: ' + str(path)
    else:
        temporary = path.with_name('.publish-' + uuid.uuid4().hex + '.pending')
        durable(temporary, raw)
        os.replace(temporary, path)


def run(resume=False, max_batches=None, check_ready=False):
    paths, control = qualification()
    if check_ready:
        print(json.dumps(dict(ready=True, arms=ARMS, deals=TEST_DEALS, seed=TEST_SEED)), flush=True)
        return
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    assert psutil.cpu_percent(interval=1) < 50 and psutil.virtual_memory().available > 24_000_000_000
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
    assert gpu.returncode == 0
    utilization, free = map(float, gpu.stdout.strip().splitlines()[0].split(','))
    assert utilization < 20 and free > 6000
    result_path = OUT / f'{PREFIX}-result.json'
    assert not result_path.exists(), 'Preserve completed study'
    if resume:
        reg = read(REG)
        assert STORE.is_dir() and reg['store'] == str(STORE)
    else:
        assert not REG.exists() and not STORE.exists()
        # Archive projection plus bounded live scratch, identities and checkpoints.
        projection = math.ceil(control['archive_bytes'] * TEST_DEALS / 64 * 1.25) + 128_000_000
        assert projection < 2_500_000_000, 'Rework retention before drawing fresh deals'
        assert psutil.disk_usage('S:/').free > 40_000_000_000 + projection
        paths += [ROOT / 'target/release/examples/hu_sampled_bank_bridge.exe',
                  ROOT / 'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe']
        inputs = dict(read(OUT / f'{CONTROL}-registration.json')['inputs'])
        inputs.update({str(p): sha(p) for p in [*paths, *Path(__file__).parent.glob('*.py')]})
        reg = dict(inputs=inputs, prefix=PREFIX, mode='study', store=str(STORE), arms=ARMS,
                   deals=TEST_DEALS, test_seed=TEST_SEED, batch_size=32, checkpoint_batches=32,
                   archive_workers=4, maximum_output_bytes=projection, maximum_invocation_seconds=43200,
                   original_control_result_sha256=sha(OUT / f'{CONTROL}-result.json'),
                   stopping='One fixed final look; resource/user interruption resumes identical committed chance prefix.',
                   production_modified=False, accuracy_qualified=False)
        save(REG, reg)
        STORE.mkdir()
    assert reg['prefix'] == PREFIX and reg['mode'] == 'study' and tuple(reg['arms']) == ARMS
    assert reg['deals'] == TEST_DEALS and reg['test_seed'] == TEST_SEED and reg['batch_size'] == 32
    assert reg['checkpoint_batches'] == 32 and reg['archive_workers'] == 4
    for p, h in reg['inputs'].items():
        assert sha(p) == h, p
    acquired, pool, error = False, None, None
    started = time.monotonic()
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True
        setup_cuda()
        guard = runtime_guard(STORE, maximum_seconds=reg['maximum_invocation_seconds'],
                              maximum_bytes=reg['maximum_output_bytes'])
        guard()
        save(OUT / f'{PREFIX}-status.json', dict(state='loading audited banks', pid=os.getpid(), registration_sha256=sha(REG)))
        banks, _, identities, load_seconds, args = load_banks(guard=guard)
        assert identities == read(Path(control['store']) / 'bank-identities.json')
        immutable_json(STORE / 'bank-identities.json', identities)
        bank_sha = sha(STORE / 'bank-identities.json')
        roots, _ = catalog_roots(banks, [], args, guard=guard)
        masses = np.asarray(read(MATRIX)['class_mass']).sum(1)
        masses /= masses.sum()
        stability = summarize(roots, masses)
        assert stability == read(Path(control['store']) / 'root-stability.json')
        immutable_json(STORE / 'root-stability.json', stability)
        source = args['context_source']
        context = json.loads(source)
        common = dict(registration_sha256=sha(REG), bank_identities_sha256=bank_sha, context_source=source, guard=guard)
        if committed(STORE):
            sampler, comparison, routes, checkpoint = restore_latest(STORE, total_deals=TEST_DEALS, seed=TEST_SEED, **common)
        else:
            sampler = PhysicalDeals(source, mode='full_deck', seed=TEST_SEED)
            comparison = CompletePolicyComparison(stack=context['config']['stack'], dead_money=context['dead_money'], deals=TEST_DEALS)
            routes = {}
            checkpoint = publish(STORE, sampler=sampler, comparison=comparison, routes=routes, **common)
        initial = PhysicalDeals(source, mode='full_deck', seed=TEST_SEED).checkpoint()
        immutable_json(STORE / 'sampler-initial.json', initial)
        before = sampler.draws
        stop = TEST_DEALS if max_batches is None else min(TEST_DEALS, before + max_batches * 32)
        cache = load_complete_cache()
        metadata = {}
        if before < stop:
            archive = OwnedColumnarEvaluationArchive.create(STORE / ('attempt-' + uuid.uuid4().hex), guard=guard)
            pool = ParallelArchives(archive, guard=guard, maximum_workers=reg['archive_workers'])
            for offset in range(before, stop, 32):
                guard()
                pool.wait_slot()
                name = f'test-{offset:06d}'
                batch = dict(format=2, batch_id=f'{PREFIX}-{name}', seed=0, query_limit=100000, deals=sampler.sample(32)['deals'])
                folder = archive.begin(name)
                summary = evaluate_batch(batch=batch, folder=folder, context_path=CONTEXT, banks=banks,
                    cache=cache, guard=guard,
                    query_executable=ROOT / 'target/release/examples/hu_sampled_bank_bridge.exe',
                    evaluation_executable=ROOT / 'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe')
                comparison.add(summary['values'])
                metadata[name] = dict(attempt=archive.root.name, owner_sha256=archive.owner_sha256,
                                      summary_sha256=sha(folder / 'summary.json'))
                pool.submit(name)
                if ((offset - before) // 32 + 1) % reg['checkpoint_batches'] == 0 or offset + 32 == stop:
                    for batch_name, identity in pool.drain().items():
                        routes[batch_name] = dict(metadata[batch_name], manifest_sha256=identity)
                    checkpoint = publish(STORE, sampler=sampler, comparison=comparison, routes=routes, **common)
                    status = dict(state='running', pid=os.getpid(), completed_deals=sampler.draws,
                                  total_deals=TEST_DEALS, checkpoint=checkpoint, seconds=time.monotonic() - started)
                    save(OUT / f'{PREFIX}-status.json', status)
                    print(json.dumps(status), flush=True)
            pool.close()
            pool = None
        if sampler.draws < TEST_DEALS:
            save(OUT / f'{PREFIX}-status.json', dict(state='checkpointed invocation limit', pid=os.getpid(),
                                                    completed_deals=sampler.draws, checkpoint=checkpoint))
            return
        analysis = comparison.finish()
        analysis['control_only'] = False
        immutable_json(STORE / 'analysis.json', analysis)
        immutable_json(STORE / 'sampler-final.json', sampler.checkpoint())
        for p, h in reg['inputs'].items():
            guard()
            assert sha(p) == h, p
        guard()
        result = dict(passed=True, complete=True, mode='study', store=str(STORE), arms=ARMS,
                      registration_sha256=sha(REG), deals=TEST_DEALS, test_seed=TEST_SEED,
                      checkpoint=checkpoint, routes=routes, load_seconds_this_invocation=load_seconds,
                      analysis_sha256=sha(STORE / 'analysis.json'), bank_identities_sha256=bank_sha,
                      root_stability_sha256=sha(STORE / 'root-stability.json'),
                      sampler_initial_sha256=sha(STORE / 'sampler-initial.json'),
                      sampler_final_sha256=sha(STORE / 'sampler-final.json'),
                      seconds_this_invocation=time.monotonic() - started, independent_review_required=True,
                      accuracy_qualified=False, production_modified=False)
        save(result_path, result)
        save(OUT / f'{PREFIX}-status.json', dict(state='evaluation complete; independent review pending', pid=os.getpid()))
    except BaseException as exc:
        error = repr(exc)
        save(OUT / f'{PREFIX}-status.json', dict(state='interrupted', pid=os.getpid(), error=error,
             resume='Restore longest committed checkpoint with --resume; preserve partial attempt folders.'))
        raise
    finally:
        if pool is not None:
            pool.close()
        if acquired:
            assert LOCK.read_text() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--check-ready', action='store_true')
    parser.add_argument('--max-batches', type=int)
    options = parser.parse_args()
    if options.max_batches is not None and options.max_batches < 1:
        parser.error('Positive invocation batch limit required')
    run(options.resume, options.max_batches, options.check_ready)
