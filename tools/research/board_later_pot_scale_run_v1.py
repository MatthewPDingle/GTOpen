"""Registered three-arm fit comparison; no change to chip-error weighting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import concurrent.futures
import gc
import json
import multiprocessing
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT, OUT, LOCK, OTHER, Guard, inputs, read, sha, verify, prepared_dataset
from board_later_fit_holdout_train_v1 import configure, curve as original_curve
from board_later_pot_scale_fit_v1 import factors, curve, PotEvaluation, control
from board_prefix_publication_v1 import atomic_json

PREFIX = 'board-later-pot-scale-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
ARMS = ('original', 'zero_output', 'pot_scaled')


def fixed_inputs():
    source, prepared, hashes = inputs()
    old_path = OUT/'board-later-fit-holdout-v1-result.json'; old = read(old_path)
    old_registration = OUT/'board-later-fit-holdout-v1-registration.json'
    qualified_path = OUT/'board-later-public-state-control-v1.json'; qualified = read(qualified_path)
    assert qualified['passed']; verify(qualified['inputs']); hashes.update(qualified['inputs'])
    assert old['passed'] and old['complete'] and old['selection']['selected_steps'] == 512
    assert old['registration_sha256'] == sha(old_registration)
    files = [Path(__file__), ROOT/'tools/research/board_later_pot_scale_fit_v1.py',
        ROOT/'tools/research/board_later_error_audit_math_v1.py', qualified_path, old_path, old_registration,
        OUT/'BOARD-LATER-POT-SCALE-PLAN.md', OUT/'board-later-error-audit-v1-result.json',
        ROOT/'tools/research/sampled_visible_hybrid_cpu64_v1.py', ROOT/'tools/research/sampled_visible_hybrid_gpu_bank_bulk_v1.py',
        ROOT/'tools/research/bounded_parallel_evaluation_archive_v2.py']
    for row in old['datasets']:
        p = row['checkpoints'][0]; assert p['step'] == 512 and sha(p['weights']) == p['weights_sha256']; files.append(Path(p['weights']))
    for p in files: hashes[str(p)] = sha(p)
    return source, prepared, hashes, old, read(OUT/'board-later-public-state-catalog-v1.json')


def training_and_validation(item, catalog):
    data = prepared_dataset(item)
    del data['raw']['test']
    data['factor'] = factors(data['train']['active'], data['train']['arity'], catalog)
    return data


def main(mode):
    source, prepared, hashes, old, catalog = fixed_inputs()
    if mode == 'ready':
        print(json.dumps(dict(ready=True, datasets=4, arms=ARMS, steps=512, objective_unchanged=True, final_test_closed=True))); return
    guard = Guard(); acquired = False; pool = None
    cp = OUT/(PREFIX+'-control.json'); rp = OUT/(PREFIX+'-registration.json'); destination = OUT/(PREFIX+'-result.json')
    assert not LOCK.exists() and not OTHER.exists()
    if mode == 'control': assert not cp.exists()
    else:
        qualification = read(cp); assert qualification['passed'] and qualification['inputs'] == hashes
        hashes[str(cp)] = sha(cp)
        assert not rp.exists() and not destination.exists() and not STORE.exists()
    try:
        with LOCK.open('x') as f: f.write(str(os.getpid()))
        acquired = True; guard(); assert psutil.cpu_percent(interval=1) < 75
        configure()
        import torch
        assert torch.cuda.is_available() and os.environ.get('CUDA_VISIBLE_DEVICES') != '-1'
        if mode == 'control':
            data = training_and_validation(source['datasets'][0], catalog)
            assert data['proof'] == prepared['datasets'][0]['split']
            proof = control(data['train'], data['item']['fit_seed'], guard, catalog); verify(hashes)
            atomic_json(cp, dict(**proof, inputs=hashes, seconds=time.monotonic()-guard.started, resource_probes=guard.probes))
            print(json.dumps(proof), flush=True); return
        from global_research_inventory_v2 import measure
        inventory = measure(); guard()
        assert sum(r['allocated_file_bytes'] for r in inventory)+100_000_000 < 800_000_000_000
        registration = dict(inputs=hashes, datasets=source['datasets'], arms=ARMS, steps=512, architecture=[302, 64, 64, 4],
            initialization='Original saved seeds. Original arm unchanged; both other arms set only last-layer weights/biases to zero.',
            output_factor='Float32(native current public pot bb / 10) postflop, one preflop.',
            target_transform='y/g', weight_transform='w*g^2', denominator='Original sum of source mass times legal arity; unchanged.',
            objective='Original normalized chip squared error, including original grouped variance constant.',
            evaluation='Restore g*f before computing original-unit validation errors; never compare transformed-unit loss as accuracy.',
            learning_rate=.003, optimizer='Adam', chunk_size=4096, tf32=False, cpu_preparation_workers=4,
            primary='Equal-dataset mean postflop validation MSE in original normalized chip units.',
            threshold='Pot scaling: >=1% lower primary loss than both baselines, lower in every dataset than both, and no under-50bb loss increase in any dataset versus either baseline.',
            secondary='Each street and fixed pot buckets [0,10,50,100,200,infinity); relative to predicting zero.',
            baseline_check='All four original-arm weights and validation losses reproduce within 1e-7 before other arms fit.',
            scope='Exploratory tuning on reused validation data; no independent confirmation or strength claim.',
            final_test_evaluated=False, new_deals=0, production_modified=False, accuracy_qualified=False,
            maximum_seconds=1800, maximum_retained_bytes=100_000_000, maximum_device_bytes=8_000_000_000,
            storage_admission=inventory, resource_sharing='Qualified light-desktop guard; yield to active solves and heavy GPU work.',
            created_unix=time.time(), pid=os.getpid(), process_created=psutil.Process().create_time())
        atomic_json(rp, registration); STORE.mkdir(); identity = sha(rp)
        atomic_json(STORE/'owner.json', dict(root=str(STORE), registration_sha256=identity))
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn'))
        futures = [pool.submit(training_and_validation, item, catalog) for item in source['datasets']]
        datasets = []
        for i, future in enumerate(futures):
            while True:
                guard()
                try: data = future.result(timeout=2); break
                except concurrent.futures.TimeoutError: pass
            assert data['proof'] == prepared['datasets'][i]['split'] and set(data['raw']) == {'validation'}
            datasets.append(data)
        pool.shutdown(wait=True); pool = None
        records = [dict(dataset=data['item']['name'], factor_min=float(data['factor'].min()), factor_max=float(data['factor'].max()), arms={}) for data in datasets]
        for arm in ARMS:
            for data, prior, record in zip(datasets, old['datasets'], records):
                guard.desktop_probe()
                item = data['item']; name = item['name']; assert name == prior['dataset'] == record['dataset']
                evaluation = PotEvaluation(data['raw']['validation'], data['train']['scale'], guard, catalog)
                torch.cuda.reset_peak_memory_stats(); point = {}
                def checkpoint(model, training):
                    assert training['step'] == 512
                    value = evaluation.score(model, guard, scaled=arm == 'pot_scaled')
                    if arm == 'original':
                        previous = prior['checkpoints'][0]; assert sha(previous['weights']) == previous['weights_sha256']
                        original = torch.load(previous['weights'], weights_only=True, map_location='cpu')
                        difference = max(float((model.state_dict()[k].detach().cpu()-v).abs().max()) for k, v in original.items())
                        loss_error = max(abs(value['metrics'][k]['normalized_loss']-previous['validation'][k]['normalized_loss']) for k in value['metrics'])
                        assert difference < 1e-7 and loss_error < 1e-7, (difference, loss_error)
                        point['baseline_reproduction'] = dict(maximum_parameter_difference=difference, maximum_validation_loss_difference=loss_error)
                    path = STORE/(name+'-'+arm+'.pt')
                    with path.open('xb') as f: torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, f)
                    point.update(**training, validation=value['metrics'], pots=value['pots'], under_50bb=value['under_50bb'],
                                 weights=str(path), weights_sha256=sha(path))
                    atomic_json(STORE/(name+'-'+arm+'.json'), point)
                    print(json.dumps(dict(dataset=name, arm=arm, postflop_loss=point['validation']['postflop']['normalized_loss'],
                                          under_50bb_loss=point['under_50bb']['normalized_loss'])), flush=True)
                if arm == 'original': timing = original_curve(data['train'], item['fit_seed'], (512,), checkpoint, guard)
                else: timing = curve(data['train'], item['fit_seed'], (512,), checkpoint, guard, factor=data['factor'] if arm == 'pot_scaled' else None)
                record['arms'][arm] = dict(**point, timing=timing)
                del evaluation; gc.collect(); torch.cuda.empty_cache()
            atomic_json(STORE/(arm+'-completed.json'), dict(registration_sha256=identity, datasets=records))
        scores = {phase: {arm: float(np.mean([r['arms'][arm]['validation'][phase]['normalized_loss'] for r in records]))
                           for arm in ARMS} for phase in ('all', 'postflop', 'preflop', 'flop', 'turn', 'river')}
        comparisons = {}
        for baseline in ('original', 'zero_output'):
            change = 100*(scores['postflop']['pot_scaled']/scores['postflop'][baseline]-1)
            all_lower = all(r['arms']['pot_scaled']['validation']['postflop']['normalized_loss'] < r['arms'][baseline]['validation']['postflop']['normalized_loss'] for r in records)
            small_safe = all(r['arms']['pot_scaled']['under_50bb']['normalized_loss'] <= r['arms'][baseline]['under_50bb']['normalized_loss'] for r in records)
            comparisons[baseline] = dict(mean_postflop_change_percent=change, all_four_lower=all_lower, no_under_50bb_regression=small_safe)
        qualifies = all(v['mean_postflop_change_percent'] <= -1 and v['all_four_lower'] and v['no_under_50bb_regression'] for v in comparisons.values())
        verify(hashes)
        retained = sum(p.stat().st_size for p in STORE.iterdir() if p.is_file()); assert retained < 100_000_000
        result = dict(passed=True, complete=True, registration_sha256=identity, scores=scores, comparisons=comparisons,
            datasets=records, qualifies_for_policy_comparison=qualifies, final_test_evaluated=False,
            accuracy_qualified=False, production_modified=False, seconds=time.monotonic()-guard.started,
            retained_bytes=retained, resource_probes=guard.probes)
        atomic_json(destination, result)
        print(json.dumps(dict(complete=True, comparisons=comparisons, qualifies_for_policy_comparison=qualifies, seconds=result['seconds'])), flush=True)
    except Exception as error:
        failure = OUT/(PREFIX+'-'+mode+'-failure.json')
        if not failure.exists(): atomic_json(failure, dict(type=type(error).__name__, message=str(error), traceback=traceback.format_exc(), seconds=time.monotonic()-guard.started))
        raise
    finally:
        if pool is not None:
            for process in list(pool._processes.values()):
                if process.is_alive(): process.terminate()
            pool.shutdown(wait=True, cancel_futures=True)
        if acquired and LOCK.read_text() == str(os.getpid()): LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--mode', choices=('ready', 'control', 'run'), default='ready')
    main(parser.parse_args().mode)
