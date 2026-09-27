"""Interrupt and resume copied old evaluation evidence; no fresh test seed."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
import uuid
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_physical_deals_v1 import PhysicalDeals
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive, restore
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_evaluation_checkpoint_v1 import publish, restore_latest, series_state

PREFIX = 'weighted-complete-checkpoint-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def main():
    started, last = time.monotonic(), 0.
    def guard():
        nonlocal last
        assert time.monotonic() - started < 600
        if time.monotonic() - last > 2:
            assert production_available() and psutil.virtual_memory().available > 24_000_000_000
            assert psutil.disk_usage('S:/').free > 40_000_000_000
            last = time.monotonic()
    guard()
    assert psutil.cpu_percent(interval=1) < 60
    rp, destination = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not rp.exists() and not destination.exists() and not STORE.exists()
    old_result = OUT / 'showdown-pipelined-evaluation-study-v1-result.json'
    old_reg = OUT / 'showdown-pipelined-evaluation-study-v1-registration.json'
    result, reg = read(old_result), read(old_reg)
    assert result['passed'] and result['complete'] and result['registration_sha256'] == sha(old_reg)
    assert reg['test_seed'] == 9267201
    original = Path(reg['original_store'])
    source_path = OUT / 'bb-context-candidate.json'
    source = source_path.read_text()
    bank_path = Path(result['store']) / 'bank-identities.json'
    assert sha(bank_path) == result['bank_identities_sha256']
    batches, paths = [], [old_result, old_reg, source_path, bank_path]
    for offset in (0, 32):
        name = f'test-{offset:06d}'
        mp, ap = original / (name + '.manifest.json'), original / (name + '.xz')
        assert sha(mp) == result['archive_manifest_hashes'][name]
        parts = restore(ap, read(mp), guard=guard)
        assert sha(mp) == reg['original_manifest_hashes'][name]
        batches.append((name, parts))
        paths.extend([mp, ap])
    inputs = {str(p): sha(p) for p in [*paths, *Path(__file__).parent.glob('*.py')]}
    save(rp, dict(inputs=inputs, store=str(STORE), deals=64, reused_seed=9267201,
                  maximum_seconds=600, maximum_output_bytes=30_000_000, gpu_used=False,
                  production_modified=False, scope='Prefix recovery on copied prior study batches; no new policy evaluation.'))
    STORE.mkdir()
    (STORE / 'bank-identities.json').write_bytes(bank_path.read_bytes())
    context = json.loads(source)
    def fresh_comparison():
        return CompletePolicyComparison(stack=context['config']['stack'], dead_money=context['dead_money'], deals=64)
    comparison, uninterrupted = fresh_comparison(), fresh_comparison()
    sampler = PhysicalDeals(source, mode='full_deck', seed=9267201)
    common = dict(registration_sha256=sha(rp), bank_identities_sha256=sha(bank_path), context_source=source, guard=guard)
    recovery = dict(common, total_deals=64, seed=9267201)
    empty = publish(STORE, sampler=sampler, comparison=comparison, routes={}, **common)
    routes, rejected = {}, []
    def reject(label, action):
        try:
            action()
        except (ValueError, AssertionError):
            rejected.append(label)
        else:
            raise AssertionError('Accepted ' + label)
    for index, (name, parts) in enumerate(batches):
        expected = json.loads(parts['query-batch.json'])
        assert sampler.sample(32)['deals'] == expected['deals']
        writer = OwnedColumnarEvaluationArchive.create(STORE / ('attempt-' + uuid.uuid4().hex), guard=guard)
        folder = writer.begin(name)
        folder.mkdir()
        for member, raw in parts.items():
            with (folder / member).open('xb') as f:
                f.write(raw)
        identity = writer.publish(name)
        assert writer.release(name) == identity
        routes[name] = dict(attempt=writer.root.name, owner_sha256=writer.owner_sha256,
                            manifest_sha256=identity, summary_sha256=sha_bytes(parts['summary.json']))
        values = json.loads(parts['summary.json'])['values']
        comparison.add(values)
        uninterrupted.add(values)
        checkpoint = publish(STORE, sampler=sampler, comparison=comparison, routes=routes, **common)
        reloaded_sampler, reloaded_comparison, restored_routes, reference = restore_latest(STORE, **recovery)
        assert reloaded_sampler.checkpoint() == sampler.checkpoint()
        assert series_state(reloaded_comparison) == series_state(comparison)
        assert restored_routes == routes and reference == checkpoint
        sampler, comparison, routes = reloaded_sampler, reloaded_comparison, restored_routes
        if index == 0:
            reject('missing completed batch', lambda: publish(STORE, sampler=sampler,
                   comparison=comparison, routes={}, **common))
            wrong = copy.deepcopy(comparison)
            wrong.series[0].count += 1
            reject('statistic count differs', lambda: publish(STORE, sampler=sampler,
                   comparison=wrong, routes=routes, **common))
            # Neither a partial batch nor a partially written checkpoint is used.
            orphan = STORE / ('attempt-' + uuid.uuid4().hex)
            orphan.mkdir()
            (orphan / 'incomplete-evidence.json').write_text('{interrupted', encoding='utf-8')
            (STORE / '.checkpoint-interrupted.pending').write_text('{interrupted', encoding='utf-8')
            again = restore_latest(STORE, **recovery)
            assert again[-1] == checkpoint and again[0].draws == 32
            assert (orphan / 'incomplete-evidence.json').read_text() == '{interrupted'
    assert comparison.finish() == uninterrupted.finish()
    reject('wrong registration', lambda: restore_latest(STORE, **dict(recovery, registration_sha256='0' * 64)))
    reject('wrong chance seed', lambda: restore_latest(STORE, **dict(recovery, seed=9267202)))
    reject('changed sample budget', lambda: restore_latest(STORE, **dict(recovery, total_deals=96)))
    committed = STORE / checkpoint['file']
    original_bytes = committed.read_bytes()
    committed.write_bytes(original_bytes + b' ')
    reject('corrupted checkpoint', lambda: restore_latest(STORE, **recovery))
    committed.write_bytes(original_bytes)
    packed = writer.root / (name + '.xz')
    original_bytes = packed.read_bytes()
    changed = bytearray(original_bytes)
    changed[-8] ^= 1
    packed.write_bytes(changed)
    reject('corrupted durable archive', lambda: restore_latest(STORE, **recovery))
    packed.write_bytes(original_bytes)
    restored = restore_latest(STORE, **recovery)
    assert restored[1].finish() == uninterrupted.finish() and restored[0].draws == 64
    for path, expected in inputs.items():
        guard()
        assert sha(path) == expected, path
    logical = sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
    assert logical < 30_000_000
    output = dict(passed=True, registration_sha256=sha(rp), store=str(STORE), deals=64,
                  checkpoints=[empty, checkpoint], exact_sampler_and_accumulator_resume=True,
                  incomplete_attempts_preserved_and_excluded=True, rejections=rejected,
                  helper_sha256=sha(ROOT / 'tools/research/weighted_evaluation_checkpoint_v1.py'),
                  logical_bytes=logical, seconds=time.monotonic() - started,
                  gpu_used=False, production_modified=False, accuracy_qualified=False,
                  artifacts={str(p): sha(p) for p in STORE.rglob('*') if p.is_file()})
    save(destination, output)
    print(json.dumps({k: v for k, v in output.items() if k != 'artifacts'}), flush=True)


def sha_bytes(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()


if __name__ == '__main__':
    main()
