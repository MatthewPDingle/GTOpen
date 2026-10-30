"""Authenticate the fixed-entry resources and quantify the existing sampling cutoff."""
import hashlib
import json
import math
from pathlib import Path
import time
import traceback
import numpy as np
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import CLASSES, COUNTS
from sampled_public_economics_features_v1 import encode_document
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_population_v1 import STORE, GEOMETRY, ENTRY, OUT, LOCK, OTHER, guard

NAME = 'stack-context-population-v1'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':'), allow_nan=False)
        stream.write('\n')


def main():
    result_path = OUT / (NAME + '-result.json')
    registration = OUT / (NAME + '-registration.json')
    output, attempt, failure = (OUT / (NAME + s + '.json') for s in
                               ('-readback', '-readback-attempt', '-readback-failure'))
    if any(p.exists() for p in (output, attempt, failure, LOCK, OTHER)):
        raise ValueError('Existing readback attempt or research owner')
    guard()
    result, spec = read(result_path), read(registration)
    if not result['complete'] or not result['passed'] or result['registration_sha256'] != sha(registration):
        raise ValueError('Successful resource preparation required')
    save(attempt, dict(reader_sha256=sha(__file__), result_sha256=sha(result_path)))
    started = time.monotonic()
    try:
        source_entry = read(ENTRY)
        records = []
        for key, record in result['contexts'].items():
            guard()
            source = Path(record['context_path']).read_text()
            context = json.loads(source)
            original = read(GEOMETRY / 'fixtures' / f"stack-{record['depth']}-context.json")
            if {k for k in context if context[k] != original[k]} != {'incoming_class_mass', 'save'}:
                raise ValueError('Unexpected geometry difference')
            if context['incoming_class_mass'] != source_entry['incoming_class_mass'] or sha(record['context_path']) != key:
                raise ValueError('Entry source or context binding changed')
            matrix, population = read(record['matrix']), read(record['population'])
            mass, bb, btn = [np.asarray(matrix[k], dtype=np.float64) for k in
                             ('class_mass', 'bb_showdown_entries', 'btn_showdown_entries')]
            if (any(a.shape != (169,169) or not np.isfinite(a).all() for a in (mass,bb,btn))
                    or np.any(mass < 0) or abs(math.fsum(mass.ravel())-1) > 1e-12):
                raise ValueError('Invalid saved exact matrix')
            response = context['nodes'][context['nodes'][0]['children'][3]]
            called = context['nodes'][response['children'][1]]
            rake = called['pot'] * context['rake_fraction']
            if context['rake_cap'] > 0:
                rake = min(rake, context['rake_cap'])
            conserved = called['pot'] - sum(called['invested']) - rake
            error = float(np.max(abs(bb+btn-mass*conserved)))
            if error > 1e-11 or matrix['context_sha256'] != key or population['context_sha256'] != key:
                raise ValueError('Saved cashflow or context differs')
            if abs(math.fsum(row['probability'] for row in population['rows'])-1) > 1e-12:
                raise ValueError('Saved physical population mass differs')
            sampler = PhysicalDeals(source, mode='full_deck', seed=0)
            original_mass = np.asarray(context['incoming_class_mass'])
            per_combo = original_mass[:,CLASSES] / COUNTS[CLASSES]
            removed = [float(per_combo[p, sampler.weights[p] == 0].sum()/per_combo[p].sum()) for p in (0,1)]
            support = [len(set(map(int, CLASSES[sampler.weights[p] > 0]))) for p in (0,1)]
            if support != record['incoming_class_support'] or support != [169,96]:
                raise ValueError('Sampler and matrix support differ')
            before = read(GEOMETRY / f"stack-{record['depth']}-public.json")
            after = read(record['public_path'])
            if not np.array_equal(encode_document(before, expected_context_sha256=sha(GEOMETRY / 'fixtures' / f"stack-{record['depth']}-context.json")),
                                  encode_document(after, expected_context_sha256=key)):
                raise ValueError('Public prices changed')
            records.append(dict(depth=record['depth'], context_sha256=key, maximum_cashflow_error=error,
                                effective_class_support=support, removed_entry_mass_fraction=removed))
        entries = read(STORE / 'entries.json')
        registries = [Registry(entries), RelativeRegistry(entries)]
        if sorted(row['depth'] for row in records) != [20,40,60,100,150,200,400]:
            raise ValueError('Missing stack input')
        for registry in registries:
            if len(registry.fit_contexts) != 5:
                raise ValueError('Wrong fitting split')
            for key in registry.fit_contexts:
                if registry._get(key)['context']['config']['stack'] in (60,150):
                    raise ValueError('Transfer context in fitting set')
        identities = {**spec['inputs'], **result['artifacts']}
        for path, expected in identities.items():
            if sha(path) != expected:
                raise ValueError('Retained resource changed: ' + path)
        save(output, dict(complete=True, passed=True, result_sha256=sha(result_path), reader_sha256=sha(__file__),
             checked_identities=len(identities), contexts=records, registry_sha256s=[r.sha256 for r in registries],
             seconds=time.monotonic()-started, training=False,
             cutoff='Existing per-player physical-combo weight below 1e-5 of that player maximum becomes zero',
             scope='Entry/geometry identities, saved mass and cashflow, registry split and effective sampler support; no new native labels'))
        print(json.dumps(dict(passed=True, contexts=len(records), removed_entry_mass_fraction=records[0]['removed_entry_mass_fraction'],
                              seconds=time.monotonic()-started)))
    except BaseException as error:
        save(failure, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        raise


if __name__ == '__main__':
    main()
