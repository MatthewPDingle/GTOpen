"""Prepare fixed-entry cross-stack continuation inputs, not scientific labels."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil
from stack_context_resources_v1 import population, catalog, independent_matrix
from sampled_allin_protocol_v3 import AllinCache
from preflop_allin_matrix_v1 import build, AllinMatrix
from sampled_physical_root_evaluation_v1 import save, sha
from sampled_visible_hybrid_checkpoint_v1 import encoded
from sampled_public_economics_features_v1 import encode_document
from stack_context_inputs_v1 import digest
from stack_context_relative_inputs_v1 import Registry
from board_study_storage_v1 import create, measure
from global_research_inventory_v3 import measure as inventory
from river_matched_training_pilot_v1 import ROOT, OUT, LOCK, OTHER, production_available

NAME = 'stack-context-population-v1'
STORE = Path('S:/GTOpen-research') / NAME
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
ENTRY = OUT / 'bb-context-candidate.json'
PLAN = OUT / 'STACK-CONTEXT-POPULATION-PLAN.md'
EXE = ROOT / 'target/release/examples/hu_preflop_visible_catalog_v1.exe'
REG, ATTEMPT, RESULT, FAILURE = (OUT / (NAME + x + '.json') for x in
                                ('-registration', '-attempt', '-result', '-failure'))
DEPTHS = (20, 40, 60, 100, 150, 200, 400)


def read(path):
    return json.loads(Path(path).read_bytes())


def guard():
    if (OTHER.exists() or not production_available() or psutil.virtual_memory().available < 24_000_000_000
            or psutil.disk_usage('S:/').free < 40_000_000_000):
        raise RuntimeError('Input preparation yields to production or resource pressure')


def prepare_depth(args):
    depth, cache_path, cache_hash, orbit_path, expected = args
    guard()
    began = time.monotonic()
    for path in (ENTRY, EXE, GEOMETRY / 'fixtures' / f'stack-{depth}-context.json',
                 GEOMETRY / f'stack-{depth}-public.json', Path(orbit_path)):
        if sha(path) != expected[str(path)]:
            raise ValueError('Context preparation input changed')
    folder = STORE / f'stack-{depth}'
    folder.mkdir()
    original = read(GEOMETRY / 'fixtures' / f'stack-{depth}-context.json')
    entry = read(ENTRY)
    context = copy.deepcopy(original)
    context['incoming_class_mass'] = copy.deepcopy(entry['incoming_class_mass'])
    context['save'] = 'Fixed entry from retained 200bb BB/BTN study; stack-varied continuation, not an equilibrium opening range'
    changed = {k for k in set(original) | set(context) if original.get(k) != context.get(k)}
    if changed != {'incoming_class_mass', 'save'} or context['class_base'] is not None:
        raise ValueError('Unexpected geometry/value changes')
    cp = folder / 'context.json'
    cp.write_bytes(encoded(context))
    source, key = cp.read_text(), sha(cp)
    ledger = read(GEOMETRY / f'stack-{depth}-public.json')
    old_prices = encode_document(ledger, expected_context_sha256=digest(ledger['context_source']))
    ledger['context_source'] = source
    new_prices = encode_document(ledger, expected_context_sha256=key)
    if not np.array_equal(new_prices, old_prices):
        raise ValueError('Entry substitution changed public prices')
    save(folder / 'public.json', ledger)
    cache = AllinCache(cache_path, cache_hash)
    keys = sorted(cache.rows)
    orbit = read(orbit_path)
    counts = {tuple(r['private_cards']): r['physical_pairs'] for r in orbit['rows']}
    if set(counts) != set(keys) or sum(counts.values()) != 1624350:
        raise ValueError('Complete authenticated suit-orbit coverage required')
    pop, direct = population(source, keys, np.array([counts[k] for k in keys]))
    save(folder / 'population.json', pop)
    doc = build(source, pop, cache.rows)
    matrix = AllinMatrix(doc, source)
    save(folder / 'matrix.json', doc)
    error = independent_matrix(source, pop, cache, matrix, direct)
    done = subprocess.run([str(EXE), str(cp)], timeout=60, capture_output=True,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    if done.returncode:
        raise RuntimeError(done.stderr.decode(errors='replace')[-2000:])
    (folder / 'physical-catalog.json').write_bytes(done.stdout)
    initial = catalog(source, json.loads(done.stdout), matrix)
    save(folder / 'initial-catalog.json', initial)
    guard()
    return dict(depth=depth, context_path=str(cp), context_sha256=key,
        public_path=str(folder / 'public.json'), matrix=str(folder / 'matrix.json'),
        matrix_sha256=sha(folder / 'matrix.json'), population=str(folder / 'population.json'),
        physical_catalog=str(folder / 'physical-catalog.json'), initial_catalog=str(folder / 'initial-catalog.json'),
        geometry_changed_fields=sorted(changed), public_price_features_unchanged=True,
        canonical_keys=len(pop['rows']), physical_private_pairs=pop['physical_pairs'],
        incoming_class_support=[int(np.count_nonzero(matrix.bb_mass)), int(np.count_nonzero(matrix.btn_mass))],
        maximum_independent_error=error, seconds=time.monotonic()-began,
        artifacts={str(p):sha(p) for p in folder.iterdir()})


def main():
    if any(p.exists() for p in (REG, ATTEMPT, RESULT, FAILURE, STORE, LOCK, OTHER)):
        raise ValueError('Existing attempt or research owner')
    guard()
    accounting = inventory()
    if sum(r['allocated_file_bytes'] for r in accounting) + 256_000_000 > 800_000_000_000:
        raise ValueError('Global research storage budget')
    geometry_path = OUT / 'stack-geometry-control-v1-result.json'
    resource_path = OUT / 'stack-context-resources-v1-result.json'
    review_path = OUT / 'stack-context-complete-allin-cache-v1-readback.json'
    geometry, previous, review = map(read, (geometry_path, resource_path, review_path))
    if not all(doc['passed'] for doc in (geometry, previous, review)):
        raise ValueError('Qualified geometry, resources and exact cache required')
    old = next(r for r in previous['contexts'].values() if r['depth'] == 20)
    orbit_path = Path(old['population'])
    if sha(orbit_path) != old['artifacts'][str(orbit_path)]:
        raise ValueError('Suit-orbit multiplicities changed')
    paths = {Path(__file__).resolve(), ENTRY, PLAN, EXE, orbit_path, geometry_path, resource_path, review_path,
             Path(review['cache_artifact']), ROOT / 'crates/solver/examples/hu_preflop_visible_catalog_v1.rs'}
    for depth in DEPTHS:
        for p in (GEOMETRY / 'fixtures' / f'stack-{depth}-context.json', GEOMETRY / f'stack-{depth}-public.json'):
            if sha(p) != geometry['artifacts'][str(p)]:
                raise ValueError('Geometry evidence changed')
            paths.add(p)
    entry = read(ENTRY)
    if (sha(ENTRY) != '8e79a4666487873e1f3e9626a6c0fc952879b24b2bdcd54cd125860787e8432d'
            or entry['positions'] != ['BB', 'BTN'] or entry['config']['stack'] != 200):
        raise ValueError('Exact retained entry source required')
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix == '.py':
            paths.add(Path(p))
    identities = {str(p):sha(p) for p in paths}
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    began = time.monotonic()
    try:
        create(STORE)
        save(STORE / 'admission.json', accounting)
        save(REG, dict(inputs=identities, depths=list(DEPTHS), workers=4, maximum_seconds=900,
             maximum_new_bytes=256_000_000, entry_source_sha256=sha(ENTRY), fixed_entry_across_stacks=True,
             entry_population_origin='Retained 200bb GTOpen approximation, not player data or Wizard',
             cache_sha256=review['cache_sha256'], training=False, fresh_scientific_test_draws=0))
        save(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(), registration_sha256=sha(REG)))
        records = {}
        with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
            futures = [pool.submit(prepare_depth, (d, review['cache_artifact'], review['cache_sha256'], str(orbit_path), identities)) for d in DEPTHS]
            for future in futures:
                while True:
                    guard()
                    if time.monotonic()-began > 900:
                        raise RuntimeError('Population preparation runtime bound')
                    try:
                        row = future.result(timeout=1)
                        records[row['context_sha256']] = row
                        print(json.dumps(dict(depth=row['depth'], prepared=True)), flush=True)
                        break
                    except TimeoutError:
                        if future.done():
                            future.result()
        entries = [dict(name=f"{row['depth']}bb", split='heldout' if row['depth'] in (60,150) else 'fit',
                        context_source=Path(row['context_path']).read_text(), public_document=read(row['public_path']))
                   for row in sorted(records.values(), key=lambda r:r['depth'])]
        registry = Registry(entries)
        save(STORE / 'entries.json', entries)
        save(STORE / 'registry.json', registry.manifest)
        for path, expected in identities.items():
            if sha(path) != expected:
                raise ValueError('Registered resource input changed')
        guard()
        size = measure(STORE)
        if size['logical_bytes'] > 256_000_000:
            raise ValueError('Input resource storage bound')
        save(RESULT, dict(complete=True, passed=True, registration_sha256=sha(REG), contexts=records,
             cache_sha256=review['cache_sha256'], registry_sha256=registry.sha256,
             entry_source_sha256=sha(ENTRY), storage=size, seconds=time.monotonic()-began,
             artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
             fixed_entry_population=True, stack_specific_opening_ranges=False,
             training_started=False, accuracy_qualified=False, production_modified=False))
    except BaseException as error:
        save(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()


if __name__ == '__main__':
    main()
