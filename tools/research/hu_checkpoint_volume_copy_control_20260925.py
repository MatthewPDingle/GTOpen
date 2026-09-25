"""CPU-only checkpoint relocation control on an audited, inactive pilot.

This does not resume, stop, move, or alter either live matched trial. It copies
the complete state dependency closure into a small new S: directory.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import numpy as np
import psutil
from threadpoolctl import threadpool_limits
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from later_action_checkpoint_v1 import restore_checkpoint
from immutable_checkpoint_copy_v1 import inspect_closure, copy_closure

PREFIX = 'checkpoint-volume-copy-control-v1'
TRIAL = 'later-action-joint-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
CAP = 250_000_000


def main():
    start = time.monotonic()
    last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        assert now-start < 600
        if now-last > 2:
            assert idle()
            assert psutil.virtual_memory().available > 20_000_000_000
            assert psutil.disk_usage('S:/').free > 40_000_000_000+CAP
            last = now
    guard(); assert not STORE.exists()
    paths = [OUT/f'{TRIAL}-{part}.json' for part in
             ('registration','result','readback-registration','independent-review')]
    reg, result, rr, audit = map(read, paths)
    assert result['passed'] and result['terminal'] and audit['passed']
    assert result['registration_sha256'] == audit['source_registration_sha256'] == sha(paths[0])
    assert audit['source_result_sha256'] == sha(paths[1])
    assert audit['readback_registration_sha256'] == sha(paths[2])
    assert result['completed_iterations'] == audit['completed_updates'] == 2
    source = Path(result['store'])/'objects'
    checkpoint = result['final_checkpoint']
    closure = inspect_closure(source, checkpoint, maximum_bytes=CAP, guard=guard)
    context = OUT/'bb-context-candidate.json'
    args = bank_args(context.read_text())
    paths.extend([context, Path(__file__).resolve(),
                  ROOT/'tools/research/immutable_checkpoint_copy_v1.py',
                  OUT/'later-action-matched-replication-v1-registration.json'])
    dependencies = dict(reg['inputs'])
    dependencies.update({p:h for p,h in rr['inputs'].items() if Path(p).suffix in ('.py','.rs','.exe')})
    for p,h in dependencies.items(): guard(); assert sha(p) == h,p
    inputs = dict(dependencies, **{str(p):sha(p) for p in paths})
    admission = read(paths[-1])['storage_admission']
    # Its projection already reserves the full live run, later evaluation, and
    # 2 GB metadata. This tiny extra data store is charged on top, not hidden.
    projected = admission['projected_allocated_bytes']+CAP
    assert projected <= admission['limit_bytes'] == 800_000_000_000
    registration = OUT/f'{PREFIX}-registration.json'
    save(registration, dict(inputs=inputs,source=str(source),checkpoint=checkpoint,
        closure=closure,maximum_bytes=CAP,maximum_seconds=600,
        projected_with_copy_cap=projected,baseline_projection_registration=str(paths[-1]),
        gpu_used=False,production_modified=False,live_trial_modified=False,
        scope='Authenticated pilot state transfer T: to new S: directory. Compare restored reservoirs, played history, accumulators and next RNG streams; no live resumption or training.'))
    STORE.mkdir()
    copied = copy_closure(source, STORE/'objects', checkpoint, maximum_bytes=CAP, guard=guard)
    assert copied == closure
    with threadpool_limits(limits=1):
        a = restore_checkpoint(source, checkpoint, config=result['config'], **args)
        b = restore_checkpoint(STORE/'objects', checkpoint, config=result['config'], **args)
        for name in ('completed_iterations','played_bank','next_model','next_model_document'):
            assert a[name] == b[name],name
        checks = []
        for x,y in zip(a['reservoirs'], b['reservoirs']):
            assert x.summary() == y.summary()
            assert x.rng.bit_generator.state == y.rng.bit_generator.state
            for name in ('keys','active','arity','values','iterations'):
                assert getattr(x,name).tobytes() == getattr(y,name).tobytes(),name
            checks.append(x.summary())
        for name in ('exact_btn_state','root_regret_state'):
            assert a[name].document() == b[name].document(),name
        assert a['action_rng'].bit_generator.state == b['action_rng'].bit_generator.state
        assert np.array_equal(a['action_rng'].integers(2**63,size=64),b['action_rng'].integers(2**63,size=64))
        assert a['sampler'].sample(8) == b['sampler'].sample(8)
    for name, identity in closure['objects'].items():
        guard(); assert sha(source/name) == sha(STORE/'objects'/name) == identity['sha256']
    for p,h in inputs.items(): guard(); assert sha(p)==h,p
    completed = dict(passed=True,registration_sha256=sha(registration),objects=len(closure['objects']),
        logical_bytes=closure['logical_bytes'],reservoirs=checks,
        full_restored_state_exact=True,next_action_stream_exact=True,next_pilot_deals_exact=True,
        source_objects_unchanged=True,seconds=time.monotonic()-start,
        gpu_used=False,production_modified=False,live_trial_modified=False,
        full_continuation_qualified=False,accuracy_qualified=False,
        scope='State-copy implementation control only. A stopped-run prefix audit, remaining-budget admission, complete evidence mapping and continuation replay are still required for a resumed trial.')
    save(OUT/f'{PREFIX}-result.json',completed)
    print(json.dumps(completed),flush=True)


if __name__ == '__main__':
    main()
