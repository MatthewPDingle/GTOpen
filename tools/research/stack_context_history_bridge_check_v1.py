"""Bounded integration check for native format-3 own-history export.

Retained physical deals, fixed nonuniform policies, no fitting or quality claim.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_bank_v1 import histories
from sampled_visible_hybrid_checkpoint_v1 import read_object
from stack_context_current_policy_v1 import CurrentPolicy
from stack_context_native_cycle_control_v2 import inputs_and_resources
from river_matched_training_pilot_v1 import ROOT, OUT, LOCK, OTHER, available, production_available

NAME = 'stack-context-history-bridge-check-v1'
STORE = Path('S:/GTOpen-research') / NAME
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
OLD_STORE = Path('S:/GTOpen-research/stack-context-native-cycle-control-v2')
REG, ATTEMPT, RESULT, FAILURE = (OUT / (NAME + suffix + '.json')
                                for suffix in ('-registration', '-attempt', '-result', '-failure'))


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, separators=(',', ':'))
        stream.write('\n')


def main():
    if any(p.exists() for p in (STORE, REG, ATTEMPT, RESULT, FAILURE, LOCK, OTHER)):
        raise ValueError('Existing attempt or research owner')
    ready, admission = available()
    if not ready:
        print(json.dumps(dict(deferred=True, admission=admission)), flush=True)
        return
    prepared_path = OUT / 'stack-context-resources-v1-result.json'
    prepared = read(prepared_path)
    prior_registration = OUT / 'stack-context-native-cycle-control-v2-registration.json'
    prior = read(prior_registration)
    # Confirm earlier executed inputs have not been changed by this new helper.
    for path, expected in prior['inputs'].items():
        if sha(path) != expected:
            raise ValueError('Previous executed input changed: ' + path)
    batches = list((OLD_STORE / 'cycle-1').glob('*/batch-000/batch.json'))
    if len(batches) != 1:
        raise ValueError('Exactly one retained first batch required')
    batch = batches[0]
    native = {name: ROOT / 'target/release/examples' / filename for name, filename in dict(
        old='hu_sampled_allin_bridge_v3.exe', new='hu_sampled_allin_history_bridge_v1.exe',
        reference='hu_sampled_bank_bridge.exe').items()}
    paths = {Path(__file__).resolve(), batch, prepared_path, prior_registration,
             OLD_STORE / 'initial.json', *native.values()}
    paths.update(ROOT / 'crates/solver/examples' / (p.stem + '.rs') for p in native.values())
    paths.update((ROOT / 'crates/solver/examples/research_sampled').glob('*.rs'))
    entries = []
    for depth in (20, 40, 60, 100, 150, 200, 400):
        context = GEOMETRY / 'fixtures' / f'stack-{depth}-context.json'
        public = GEOMETRY / f'stack-{depth}-public.json'
        paths.update((context, public))
        entries.append(dict(name=f'{depth}bb', split='heldout' if depth in (60, 150) else 'fit',
                            context_source=context.read_text(), public_document=read(public)))
    registry, resources, _, _ = inputs_and_resources(entries, prepared)
    initial = read(OLD_STORE / 'initial.json')
    model = read_object(OLD_STORE / 'objects', initial['model'])
    paths.add(OLD_STORE / 'objects' / initial['model']['file'])
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix == '.py':
            paths.add(Path(path))
    identities = {str(path): sha(path) for path in sorted(paths)}
    started = time.monotonic()

    def guard():
        if (time.monotonic() - started > 300 or not production_available() or OTHER.exists()
                or psutil.virtual_memory().available < 24_000_000_000
                or psutil.disk_usage('S:/').free < 40_000_000_000):
            raise RuntimeError('Bounded control yields to runtime/resource/production limits')
        if STORE.exists() and sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) > 256_000_000:
            raise RuntimeError('Control storage bound')

    def run(executable, mode, context, input_batch, policy, output):
        guard()
        completed = subprocess.run([str(executable), mode, str(context), str(input_batch), str(policy), str(output)],
                                   capture_output=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
        save(output.with_suffix('.process.json'), dict(returncode=completed.returncode,
             stdout=completed.stdout.decode(errors='replace'), stderr=completed.stderr.decode(errors='replace')))
        completed.check_returncode()
        guard()
        return read(output)

    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        STORE.mkdir()
        save(REG, dict(inputs=identities, depths=[20, 200], maximum_seconds=300,
             maximum_new_bytes=256_000_000, training=False,
             checks=['unchanged query order/features', 'qualified native history reference',
                     'structural ancestor consistency', 'strict full-policy scoring',
                     'exact old/new traversal and cashflow verification']))
        save(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(),
                          registration_sha256=sha(REG), admission=admission))
        records = []
        original_batch = read(batch)
        projection = {name: original_batch[name] for name in ('batch_id', 'seed', 'query_limit', 'deals')}
        projection['format'] = 2
        projected_path = STORE / 'reference-format2-batch.json'
        save(projected_path, projection)
        for depth in (20, 200):
            context = GEOMETRY / 'fixtures' / f'stack-{depth}-context.json'
            old = run(native['old'], 'queries', context, batch, '-', STORE / f'{depth}-old-queries.json')
            new = run(native['new'], 'queries', context, batch, '-', STORE / f'{depth}-new-queries.json')
            reference = run(native['reference'], 'queries', context, projected_path, '-', STORE / f'{depth}-reference-queries.json')
            stripped = dict(new, observations=[{k: v for k, v in row.items() if k != 'own_history'}
                                               for row in new['observations']])
            if stripped != old or new['observations'] != reference['observations']:
                raise ValueError('Query fields/order or native own-history reference differs')
            own = histories(new['observations'])
            phases = sorted({row['phase'] for row in new['observations']})
            if phases != [0, 1, 2, 3] or not any(own):
                raise ValueError('All-street history coverage required')
            engine = CurrentPolicy(model, registry, context_sha256=sha(context), resources=resources)
            scored = engine.infer(engine.prepare(new))
            if not np.isfinite(scored).all() or np.max(abs(scored.sum(1) - 1)) > 1e-12:
                raise ValueError('Strict full model policy scoring failed')
            # Key-dependent nonuniform legal policies exercise existing value calculations.
            probabilities = np.zeros_like(scored)
            for i, row in enumerate(new['observations']):
                n = row['n']
                w = np.array([1 + (int(row['hi']) + int(row['lo']) + 3*a) % 11 for a in range(n)], dtype=float)
                probabilities[i, :n] = w / w.sum()
            policy = STORE / f'{depth}-fixed-policy.json'
            save(policy, policy_document(new, probabilities))
            old_values = run(native['old'], 'verify', context, batch, policy, STORE / f'{depth}-old-values.json')
            new_values = run(native['new'], 'verify', context, batch, policy, STORE / f'{depth}-new-values.json')
            if old_values != new_values or new_values['verified_cashflow_traversals'] != 2*len(original_batch['deals']):
                raise ValueError('Original values/traversal changed or incomplete verification')
            records.append(dict(depth=depth, physical_deals=len(original_batch['deals']),
                observations=len(own), history_edges=sum(map(len, own)), maximum_own_decisions=max(map(len, own)),
                phases=phases, verified_traversals=new_values['verified_cashflow_traversals'],
                query_and_history_reference_equal=True, old_new_values_exactly_equal=True,
                strict_current_policy_passed=True, maximum_cashflow_error=new_values['maximum_cashflow_error']))
            print(json.dumps(records[-1]), flush=True)
        guard()
        for path, expected in identities.items():
            if sha(path) != expected:
                raise ValueError('Registered input changed: ' + path)
        artifacts = {str(p): sha(p) for p in sorted(STORE.rglob('*')) if p.is_file()}
        save(RESULT, dict(complete=True, passed=True, records=records, artifacts=artifacts,
             registration_sha256=sha(REG), elapsed_seconds=time.monotonic()-started,
             training_started=False, full_cycle_qualified=False,
             scope='Native export integration only; no preflop accuracy measurement'))
    except BaseException as error:
        save(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()


if __name__ == '__main__':
    main()
