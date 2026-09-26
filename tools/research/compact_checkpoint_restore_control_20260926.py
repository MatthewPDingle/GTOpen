"""CPU recovery checks on immutable snapshots and already-played chance streams."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import io
import json
from pathlib import Path
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import unpack
from hu_action_integrated_exact_20260925 import bank_args
from compact_checkpoint_restore_v1 import restore
import sampled_visible_hybrid_checkpoint_v1 as base
import later_action_checkpoint_v1 as baseline
from sampled_physical_reservoir_v1 import PhysicalReservoir

PREFIX = 'compact-checkpoint-restore-control-v1'


def main():
    start = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic(); assert now-start < 900
        assert psutil.virtual_memory().available >= 20_000_000_000
        if now-last > 2: assert idle(); last = now
    guard(); rp, dest = [OUT/f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not rp.exists() and not dest.exists()
    tr = OUT/'showdown-matched-training-v1-registration.json'; trial = read(tr)
    root = Path(trial['store']); args = bank_args((OUT/'bb-context-candidate.json').read_text())
    cases = [('9266201-baseline', 78), ('9266201-baseline', 72), ('9266201-corrected', 16)]
    paths = [tr, Path(__file__).resolve(), ROOT/'tools/research/compact_checkpoint_restore_v1.py',
             ROOT/'tools/research/sampled_visible_hybrid_checkpoint_v1.py',
             ROOT/'tools/research/later_action_checkpoint_v1.py', ROOT/'tools/research/showdown_root_checkpoint_v1.py',
             OUT/'showdown-training-readback-v2-9266201-baseline-0078-result.json']
    assert read(paths[-1])['passed'] and read(paths[-1])['complete_arm']
    for label, n in cases:
        case = root/label
        paths.extend([case/f'checkpoint-{n:04d}.json', case/f'retention-{n:04d}.json',
                      case/f'iteration-{n:04d}/metrics.json'])
        if n < 78:
            paths.extend([case/f'retention-{n+1:04d}.json', case/f'iteration-{n+1:04d}/current-initial-policy.json'])
    inputs = {str(p): sha(p) for p in paths}
    save(rp, dict(inputs=inputs, cases=cases, maximum_seconds=900, gpu_used=False,
        scope='Native restoration from authenticated compact snapshots; final baseline comparison and replay of existing next-update chance streams. No fitting or continuation launch.'))
    original_reader = base.read_object; original_load = PhysicalReservoir.load.__func__
    records = []; rejections = []
    def reject(label, fn):
        try: fn()
        except ValueError: rejections.append(label)
        else: raise AssertionError('Accepted '+label)
    try:
        for label, n in cases:
            guard(); began = time.monotonic(); case = root/label
            arm = next(a for a in trial['arms'] if a['name'] == label)
            cfg = arm['config']; treatment = arm['treatment']
            state, identity = restore(case, n, treatment=treatment, config=cfg, bank_args=args, guard=guard)
            assert base.read_object is original_reader and PhysicalReservoir.load.__func__ is original_load
            assert state['sampler'].draws == n*512
            doc = state['next_model_document']
            assert state['root_regret_state'].document() == doc['integrated_root']['state']
            assert state['exact_btn_state'].document() == doc['exact_model']['exact_btn']['state']
            # Independently read the reservoir arrays retained at this snapshot.
            snap = read(case/f'checkpoint-{n:04d}.json'); pointer = snap['reservoir_archive']
            archive = Path(pointer['path']); manifest = read(archive.with_suffix('.xz.json'))
            assert sha(archive.with_suffix('.xz.json')) == pointer['manifest_sha256']
            members = unpack(archive, manifest, guard=guard)
            matched = set()
            for raw in members.values():
                with np.load(io.BytesIO(raw), allow_pickle=False) as arrays:
                    meta = json.loads(str(arrays['metadata'])); player = meta['player']; actual = state['reservoirs'][player]
                    assert player not in matched; matched.add(player)
                    assert actual.seen == meta['seen'] and actual.rng.bit_generator.state == meta['rng']
                    for key in ('keys','active','arity','values','iterations'):
                        assert np.array_equal(getattr(actual,key)[:actual.size], arrays[key]), key
            assert matched == {0,1}
            record = dict(arm=label, checkpoint=n, identity=identity, exact_reservoir_arrays=True)
            if n == 78:
                native = baseline.restore_checkpoint(case/'objects', snap['checkpoint'], config=cfg, **args)
                for key in ('next_model','played_bank','next_model_document'):
                    assert state[key] == native[key]
                assert state['sampler'].checkpoint() == native['sampler'].checkpoint()
                assert state['action_rng'].bit_generator.state == native['action_rng'].bit_generator.state
                assert state['root_regret_state'].document() == native['root_regret_state'].document()
                assert state['exact_btn_state'].document() == native['exact_btn_state'].document()
                for a,b in zip(state['reservoirs'], native['reservoirs']):
                    assert a.summary() == b.summary() and a.rng.bit_generator.state == b.rng.bit_generator.state
                    for key in ('keys','active','arity','values','iterations'):
                        assert np.array_equal(getattr(a,key)[:a.size],getattr(b,key)[:b.size])
                del native; record['matches_native_raw_restore'] = True
            else:
                initial = read(case/f'iteration-{n+1:04d}/current-initial-policy.json')
                assert initial['used_model'] == state['next_model']
                marker = read(case/f'retention-{n+1:04d}.json')
                checked = 0
                for chunk, pointer in enumerate(marker['archives']):
                    guard(); a = Path(pointer['path']); mp = a.with_suffix('.xz.json')
                    assert sha(mp) == pointer['manifest_sha256']
                    batch = json.loads(unpack(a, read(mp), guard=guard)['batch.json'])
                    assert batch['batch_id'] == f'showdown-matched-training-v1-{arm["seed"]}-iteration-{n+1}-batch-{chunk}'
                    assert batch['seed'] == int(state['action_rng'].integers(0,2**63))
                    assert batch['deals'] == state['sampler'].sample(64)['deals']; checked += 64
                assert checked == 512; record['existing_next_update_deals_replayed'] = checked
            record['seconds'] = time.monotonic()-began; records.append(record)
            print(json.dumps({k:v for k,v in record.items() if k!='identity'}),flush=True)
            del state
        case=root/'9266201-baseline';cfg=trial['arms'][0]['config']
        reject('non-checkpoint boundary',lambda:restore(case,73,treatment='baseline',config=cfg,bank_args=args,guard=guard))
        reject('boolean boundary',lambda:restore(case,True,treatment='baseline',config=cfg,bank_args=args,guard=guard))
        reject('unknown treatment',lambda:restore(case,72,treatment='unknown',config=cfg,bank_args=args,guard=guard))
        reject('changed configuration',lambda:restore(case,72,treatment='baseline',config=dict(cfg,fit_steps=513),bank_args=args,guard=guard))
        assert base.read_object is original_reader and PhysicalReservoir.load.__func__ is original_load
        for p,h in inputs.items(): guard(); assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),cases=records,rejections=rejections,
            reader_adapters_restored=True,files_extracted=0,files_retired=0,training_launched=False,
            native_fit_replay_qualified=False,gpu_used=False,production_modified=False,
            seconds=time.monotonic()-start,scope='Snapshot restoration and unchanged next chance streams only. A separate quiescent continuation controller and fit replay are still required.')
        save(dest,result); print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)
    except BaseException as exc:
        save(dest,dict(passed=False,error=repr(exc),registration_sha256=sha(rp),seconds=time.monotonic()-start))
        raise


if __name__ == '__main__':
    main()
