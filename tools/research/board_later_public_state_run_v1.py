"""Validation-only 302 versus 314 input experiment; fixed 512-step fit budget."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import argparse
import concurrent.futures
import gc
import json
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT, OUT, LOCK, OTHER, Guard, inputs, read, sha, verify, prepared_dataset
from board_later_fit_holdout_train_v1 import configure, curve as baseline_curve, Evaluation
from board_later_public_state_features_v1 import lookup, NAMES
from board_later_public_state_fit_v1 import curve as public_curve, PublicEvaluation, control
from board_prefix_publication_v1 import atomic_json

PREFIX = 'board-later-public-state-fit-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def training_and_validation(item):
    data = prepared_dataset(item)
    # Preserve the registered partition identity without allowing test inference.
    del data['raw']['test']
    return data


def fixed_inputs():
    source, prepared, hashes = inputs()
    old_path = OUT/'board-later-fit-holdout-v1-result.json'; old = read(old_path)
    old_registration = OUT/'board-later-fit-holdout-v1-registration.json'
    feature_control = OUT/'board-later-public-state-control-v1.json'; qualified = read(feature_control)
    assert old['passed'] and old['complete'] and old['selection']['selected_steps'] == 512
    assert old['registration_sha256'] == sha(old_registration)
    assert qualified['passed'] and not qualified['training_started'] and not qualified['heldout_loss_scored']
    verify(qualified['inputs']); hashes.update(qualified['inputs'])
    files = [Path(__file__), ROOT/'tools/research/board_later_public_state_fit_v1.py',
             old_path, old_registration, feature_control, OUT/'BOARD-LATER-PUBLIC-STATE-PLAN.md']
    for p in files: hashes[str(p)] = sha(p)
    return source, prepared, hashes, old, lookup(read(OUT/'board-later-public-state-catalog-v1.json'))


def main(mode):
    source, prepared, hashes, old, table = fixed_inputs()
    if mode == 'ready':
        print(json.dumps(dict(ready=True, datasets=4, architectures=[[302, 64, 64, 4], [314, 64, 64, 4]],
                              steps=512, validation_only=True, final_test_closed=True))); return
    guard = Guard(); acquired = False; pool = None
    control_path = OUT/(PREFIX+'-control.json')
    registration_path = OUT/(PREFIX+'-registration.json'); destination = OUT/(PREFIX+'-result.json')
    assert not LOCK.exists() and not OTHER.exists()
    if mode == 'control': assert not control_path.exists()
    else:
        qualification = read(control_path)
        assert qualification['passed'] and qualification['inputs'] == hashes
        hashes[str(control_path)] = sha(control_path)
        assert not registration_path.exists() and not destination.exists() and not STORE.exists()
    try:
        with LOCK.open('x') as f: f.write(str(os.getpid()))
        acquired = True; guard(); assert psutil.cpu_percent(interval=1) < 75
        configure()
        import torch
        assert torch.cuda.is_available() and os.environ.get('CUDA_VISIBLE_DEVICES') != '-1'
        if mode == 'control':
            data = training_and_validation(source['datasets'][0])
            assert data['proof'] == prepared['datasets'][0]['split']
            proof = control(data['train'], data['item']['fit_seed'], guard, table)
            verify(hashes)
            atomic_json(control_path, dict(**proof, inputs=hashes, resource_probes=guard.probes,
                                            seconds=time.monotonic()-guard.started))
            print(json.dumps(proof), flush=True); return
        from global_research_inventory_v2 import measure
        inventory = measure()
        assert sum(r['allocated_file_bytes'] for r in inventory)+100_000_000 < 800_000_000_000
        guard()
        registration = dict(inputs=hashes, datasets=source['datasets'], steps=512,
            architectures={'baseline': [302, 64, 64, 4], 'public_inputs': [314, 64, 64, 4]},
            added_feature_names=NAMES, added_parameters=768,
            initialization='Original fit seed; candidate copies original weights and zeroes the 12 added columns.',
            learning_rate=.003, optimizer='Adam', chunk_size=4096, tf32=False, cpu_preparation_workers=2,
            split='Reuse original salted input-disjoint 70/15/15 partitions and training-only target scale.',
            primary='Equal-dataset mean postflop normalized validation MSE at 512 steps.',
            qualification_threshold='At least 1% lower mean postflop validation loss and improvement in all four datasets.',
            scope='Same validation partition reused for representation selection; not independent confirmation.',
            baseline_check='All four 302-input repeats must reproduce prior weights and validation loss within 1e-7 before candidate fitting.',
            final_test_evaluated=False, final_test_inaccessible_to_scoring=True,
            maximum_seconds=1800, maximum_retained_bytes=100_000_000, maximum_device_bytes=8_000_000_000,
            storage_admission=inventory, resource_sharing='Qualified light-desktop guard: pause own work to probe other GPU load every 30 seconds; yield at 65% or <10GB free.',
            new_deals=0, production_modified=False, accuracy_qualified=False,
            pid=os.getpid(), process_created=psutil.Process().create_time(), created_unix=time.time())
        atomic_json(registration_path, registration); STORE.mkdir(); identity = sha(registration_path)
        atomic_json(STORE/'owner.json', dict(root=str(STORE), registration_sha256=identity))
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('spawn'))
        futures = [pool.submit(training_and_validation, d) for d in source['datasets']]
        data_sets = []
        for i, future in enumerate(futures):
            while True:
                guard()
                try: data = future.result(timeout=2); break
                except concurrent.futures.TimeoutError: pass
            assert data['proof'] == prepared['datasets'][i]['split'] and set(data['raw']) == {'validation'}
            data_sets.append(data)
        pool.shutdown(wait=True); pool = None
        records = [dict(dataset=data['item']['name'], arms={}) for data in data_sets]
        for arm in ('baseline', 'public_inputs'):
            for data, prior, record in zip(data_sets, old['datasets'], records):
                guard.desktop_probe()
                item = data['item']; name = item['name']; assert name == prior['dataset'] == record['dataset']
                if arm == 'baseline': validation = Evaluation(data['raw']['validation'], data['train']['scale'], guard)
                else: validation = PublicEvaluation(data['raw']['validation'], data['train']['scale'], guard, table)
                torch.cuda.reset_peak_memory_stats(); point = {}
                def checkpoint(model, training):
                    assert training['step'] == 512
                    value = validation(model, guard)
                    if arm == 'baseline':
                        previous = prior['checkpoints'][0]
                        assert previous['step'] == 512 and sha(previous['weights']) == previous['weights_sha256']
                        original = torch.load(previous['weights'], weights_only=True, map_location='cpu')
                        difference = max(float((model.state_dict()[k].detach().cpu()-v).abs().max()) for k, v in original.items())
                        loss_error = max(abs(value[k]['normalized_loss']-previous['validation'][k]['normalized_loss']) for k in value)
                        assert difference < 1e-7 and loss_error < 1e-7, (difference, loss_error)
                        point['baseline_reproduction'] = dict(maximum_parameter_difference=difference, maximum_validation_loss_difference=loss_error)
                    path = STORE/(name+'-'+arm+'.pt')
                    with path.open('xb') as f: torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, f)
                    point.update(**training, validation=value, weights=str(path), weights_sha256=sha(path))
                    atomic_json(STORE/(name+'-'+arm+'.json'), point)
                    print(json.dumps(dict(dataset=name, arm=arm, postflop_validation_loss=value['postflop']['normalized_loss'])), flush=True)
                if arm == 'baseline': timing = baseline_curve(data['train'], item['fit_seed'], (512,), checkpoint, guard)
                else: timing = public_curve(data['train'], item['fit_seed'], (512,), checkpoint, guard, table)
                record['arms'][arm] = dict(**point, timing=timing)
                del validation; gc.collect(); torch.cuda.empty_cache()
            atomic_json(STORE/(arm+'-completed.json'), dict(registration_sha256=identity, datasets=records))
        scores = {}
        for phase in ('all', 'postflop', 'preflop', 'flop', 'turn', 'river'):
            base, candidate = [float(np.mean([r['arms'][arm]['validation'][phase]['normalized_loss'] for r in records]))
                               for arm in ('baseline', 'public_inputs')]
            scores[phase] = dict(baseline=base, public_inputs=candidate, relative_change_percent=100*(candidate/base-1))
        improvements = [r['arms']['public_inputs']['validation']['postflop']['normalized_loss'] <
                        r['arms']['baseline']['validation']['postflop']['normalized_loss'] for r in records]
        qualifies = scores['postflop']['relative_change_percent'] <= -1 and all(improvements)
        verify(hashes)
        retained = sum(p.stat().st_size for p in STORE.iterdir() if p.is_file()); assert retained < 100_000_000
        result = dict(passed=True, complete=True, registration_sha256=identity, scores=scores, datasets=records,
            all_four_improved=all(improvements), qualifies_for_policy_comparison=qualifies,
            final_test_evaluated=False, accuracy_qualified=False, production_modified=False,
            seconds=time.monotonic()-guard.started, retained_bytes=retained, resource_probes=guard.probes)
        atomic_json(destination, result)
        print(json.dumps(dict(complete=True, scores=scores, qualifies_for_policy_comparison=qualifies, seconds=result['seconds'])), flush=True)
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive(): p.terminate()
            pool.shutdown(wait=True, cancel_futures=True)
        if acquired and LOCK.read_text() == str(os.getpid()): LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--mode', choices=('ready', 'control', 'run'), default='ready')
    main(parser.parse_args().mode)
