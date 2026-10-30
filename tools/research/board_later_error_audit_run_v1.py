"""CPU-only descriptive readback of saved fits; no final-test inference."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
import json
import multiprocessing
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT, OUT, LOCK, OTHER, inputs, read, sha, verify
from board_later_fit_holdout_data_v1 import prepare
from board_later_error_audit_math_v1 import row_totals, totals, partition, concentration, repetition, public_amounts, control
from weighted_reservoir_bulk_load_v1 import load
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json

PREFIX = 'board-later-error-audit-v1'
PHASES = ('preflop', 'flop', 'turn', 'river')
POT_LABELS = ('under 10 bb', '10-50 bb', '50-100 bb', '100-200 bb', '200+ bb')


class CpuGuard:
    def __init__(self): self.started = time.monotonic(); self.last = 0.
    def __call__(self):
        assert time.monotonic()-self.started < 600, 'Ten-minute readback limit reached'
        if time.monotonic()-self.last < 2: return
        assert psutil.virtual_memory().available > 24_000_000_000
        assert production_available() and not OTHER.exists(), 'Another workload has priority'
        assert psutil.disk_usage('S:/').free > 5_000_000_000 and psutil.disk_usage('T:/').free > 1_000_000_000
        self.last = time.monotonic()


def fixed_inputs():
    source, prepared, hashes = inputs()
    fit_path = OUT/'board-later-public-state-fit-v1-result.json'; fit = read(fit_path)
    fit_registration = OUT/'board-later-public-state-fit-v1-registration.json'
    assert fit['passed'] and fit['complete'] and fit['registration_sha256'] == sha(fit_registration)
    assert not fit['qualifies_for_policy_comparison'] and not fit['final_test_evaluated']
    registered = read(fit_registration); verify(registered['inputs']); hashes.update(registered['inputs'])
    catalog_path = OUT/'board-later-public-state-catalog-v1.json'
    files = [Path(__file__), ROOT/'tools/research/board_later_error_audit_math_v1.py',
             OUT/'BOARD-LATER-ERROR-AUDIT-PLAN.md', fit_path, fit_registration, catalog_path,
             ROOT/'tools/research/bounded_parallel_evaluation_archive_v2.py']
    for row in fit['datasets']:
        checkpoint = row['arms']['baseline']; assert sha(checkpoint['weights']) == checkpoint['weights_sha256']
        files.append(Path(checkpoint['weights']))
    for p in files: hashes[str(p)] = sha(p)
    return source, prepared, fit, read(catalog_path), hashes


def one(item, proof, checkpoint, catalog):
    began = time.monotonic(); guard = CpuGuard(); guard(); verify(item['inputs'])
    reservoir = load(item['reservoir'], Path(item['context']).read_text(), guard=guard)
    n = reservoir.size
    assert n == item['retained_examples'] and reservoir.player == item['player']
    assert int(reservoir.iterations[:n].max()) == 77
    assert abs(reservoir.deal_weights[:n].sum()-item['retained_weight']) < 1e-8
    active, arity, values, weights = reservoir.active[:n], reservoir.arity[:n], reservoir.values[:n], reservoir.deal_weights[:n]
    parts, actual, split = prepare(active, arity, values, weights); assert actual == proof
    scale = parts['train']['scale']; del parts
    # Only training and validation rows are selected below; final-test values
    # are never passed to inference or reported metrics.
    validation = split == 1; guard()
    import torch
    torch.set_num_threads(1)
    assert not torch.cuda.is_initialized()
    model = fresh_visible_network(item['fit_seed'])
    assert sha(checkpoint['weights']) == checkpoint['weights_sha256']
    model.load_state_dict(torch.load(checkpoint['weights'], weights_only=True, map_location='cpu'))
    va, ar = active[validation], arity[validation]
    x = features([dict(active_features=a.tolist()) for a in va]); predictions = []
    with torch.no_grad():
        for start in range(0, len(x), 8192):
            guard(); predictions.append(model(torch.from_numpy(x[start:start+8192])).numpy().astype(np.float64))
    rows = row_totals(np.concatenate(predictions), values[validation], ar, weights[validation], scale)
    phase = va[:, 15].astype(int)-135; all_rows = np.ones(len(va), dtype=bool); post = phase > 0
    output = {'all': totals(rows, all_rows), 'postflop': totals(rows, post)}
    output.update({name: totals(rows, phase == i) for i, name in enumerate(PHASES)})
    errors = {name: abs(record['normalized_loss']-checkpoint['validation'][name]['normalized_loss']) for name, record in output.items()}
    assert max(errors.values()) < 1e-6, errors
    for name, record in output.items():
        assert record['rows'] == checkpoint['validation'][name]['rows']
        assert abs(record['legal_target_mass']-checkpoint['validation'][name]['legal_target_mass']) < 1e-8
    pot, starting = public_amounts(va, ar, catalog)
    assert np.isfinite(pot[post]).all() and np.isnan(pot[~post]).all()
    pot_bin = np.searchsorted([10., 50., 100., 200.], pot, side='right')
    streets = partition(rows, post, [(name, phase == i) for i, name in enumerate(PHASES) if i])
    pots = partition(rows, post, [(label, post & (pot_bin == i)) for i, label in enumerate(POT_LABELS)])
    starts = partition(rows, post, [(f'{value:g} bb', post & (starting == value)) for value in np.unique(starting[post])])
    street_pots = {name: partition(rows, phase == i, [(label, (phase == i) & (pot_bin == j))
        for j, label in enumerate(POT_LABELS)]) for i, name in enumerate(PHASES) if i}
    concentrated = {name: concentration(rows, phase == i) for i, name in enumerate(PHASES)}
    concentrated['postflop'] = concentration(rows, post)
    train = split == 0; train_phase = active[:, 15].astype(int)-135; repeated = {}
    for name, mask in [('postflop', train & (train_phase > 0))]+[(name, train & (train_phase == i)) for i, name in enumerate(PHASES)]:
        repeated[name] = {}
        for within in (False, True):
            guard()
            repeated[name]['within_iteration' if within else 'across_iterations'] = repetition(
                active[mask], arity[mask], values[mask], weights[mask], reservoir.iterations[:n][mask], scale, within_iteration=within)
    verify(item['inputs']); assert sha(checkpoint['weights']) == checkpoint['weights_sha256']
    assert not torch.cuda.is_initialized()
    return dict(dataset=item['name'], rows=n, validation_totals=output, validation_streets=streets,
        validation_pots=pots, validation_starting_pots=starts, validation_street_pots=street_pots,
        largest_error_one_percent=concentrated, training_repetition=repeated,
        baseline_reproduction_absolute_errors=errors, final_test_evaluated=False,
        cuda_initialized=False, seconds=time.monotonic()-began, process_rss_bytes=psutil.Process().memory_info().rss)


def main(mode):
    source, prepared, fit, catalog, hashes = fixed_inputs(); guard = CpuGuard()
    if mode == 'ready':
        print(json.dumps(dict(ready=True, datasets=4, workers=4, device='cpu', final_test_closed=True))); return
    cp = OUT/(PREFIX+'-control.json'); rp = OUT/(PREFIX+'-registration.json'); destination = OUT/(PREFIX+'-result.json')
    if mode == 'control':
        assert not cp.exists(); proof = control()
        atomic_json(cp, dict(**proof, inputs=hashes)); print(json.dumps(proof)); return
    qualification = read(cp); assert qualification['passed'] and qualification['inputs'] == hashes
    hashes[str(cp)] = sha(cp)
    assert not rp.exists() and not destination.exists() and not LOCK.exists() and not OTHER.exists()
    acquired = False; pool = None
    try:
        with LOCK.open('x') as f: f.write(str(os.getpid()))
        acquired = True; guard(); cpu_load = psutil.cpu_percent(interval=1); assert cpu_load < 75
        from global_research_inventory_v2 import measure
        inventory = measure(); guard()
        assert sum(r['allocated_file_bytes'] for r in inventory)+5_000_000 < 800_000_000_000
        registration = dict(inputs=hashes, datasets=source['datasets'], workers=4, numeric_threads_per_worker=1,
            device='cpu', no_cuda=True, no_training=True, new_deals=0, final_test_evaluated=False,
            baseline_loss_absolute_tolerance=1e-6, pot_boundaries_bb=[10, 50, 100, 200],
            partitions=['street', 'current pot', 'starting postflop pot', 'street and current pot'],
            concentration='Largest weighted squared-error 1% of validation rows, rounded upward; descriptive.',
            repeats='Training-only identical input/menu groups, both across and within iteration; coverage and weighted effective counts reported.',
            scope='Reused data; exploratory accounting, not irreducible-noise estimation or fresh confirmation.',
            storage_admission=inventory, maximum_retained_bytes=5_000_000, maximum_seconds=600,
            cpu_admission_percent=cpu_load, production_modified=False, accuracy_qualified=False,
            created_unix=time.time(), pid=os.getpid(), process_created=psutil.Process().create_time())
        atomic_json(rp, registration)
        pool = concurrent.futures.ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn'))
        futures = []
        for item, prior, fitted in zip(source['datasets'], prepared['datasets'], fit['datasets']):
            assert item['name'] == fitted['dataset']
            futures.append(pool.submit(one, item, prior['split'], fitted['arms']['baseline'], catalog))
        records = []
        for future in futures:
            while True:
                guard()
                try: row = future.result(timeout=2); break
                except concurrent.futures.TimeoutError: pass
            records.append(row)
            print(json.dumps(dict(dataset=row['dataset'], seconds=row['seconds'],
                validation_loss=row['validation_totals']['postflop']['normalized_loss'],
                largest_one_percent_error_share=row['largest_error_one_percent']['postflop']['weighted_error_share'],
                postflop_repeated_row_fraction=row['training_repetition']['postflop']['across_iterations']['repeated_row_fraction'])), flush=True)
        pool.shutdown(wait=True); pool = None; verify(hashes)
        result = dict(passed=True, complete=True, registration_sha256=sha(rp), datasets=records,
            seconds=time.monotonic()-guard.started, final_test_evaluated=False, cuda_initialized=False,
            production_modified=False, accuracy_qualified=False)
        assert len(json.dumps(result).encode())+rp.stat().st_size+cp.stat().st_size < 5_000_000
        atomic_json(destination, result); print(json.dumps(dict(complete=True, seconds=result['seconds'], result=str(destination))), flush=True)
    except Exception as error:
        failure = OUT/(PREFIX+'-failure.json')
        if not failure.exists(): atomic_json(failure, dict(type=type(error).__name__, message=str(error),
            traceback=traceback.format_exc(), seconds=time.monotonic()-guard.started, registration_exists=rp.exists()))
        raise
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive(): p.terminate()
            pool.shutdown(wait=True, cancel_futures=True)
        if acquired and LOCK.read_text() == str(os.getpid()): LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--mode', choices=('ready', 'control', 'run'), default='ready')
    main(parser.parse_args().mode)
