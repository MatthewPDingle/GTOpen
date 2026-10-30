"""Bounded adapter checks. Synthetic targets are not poker-strength evidence."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import argparse
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from exact_initial_training_ingest_v2 import digest
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_deal_binding_v1 import DealWeightGeneration
from weighted_root_accumulator_v1 import WeightedRootRegrets
from action_integrated_root_accumulator_v1 import IntegratedRootRegrets
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from sampled_physical_reservoir_v1 import PhysicalReservoir
from weighted_preflop_table_v1 import build, Table
from sampled_physical_preflop_table_v1 import build as old_build, Table as OldTable

PREFIX = 'weighted-root-table-control-v1'


def main(publish=False):
    started = time.monotonic()
    assert psutil.virtual_memory().available > 20_000_000_000
    assert psutil.cpu_percent(interval=1) < 70
    context_path = OUT/'bb-context-candidate.json'; source = context_path.read_text()
    catalog_path = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    paths = [context_path, catalog_path, *Path(__file__).parent.glob('*.py'), OUT/'WEIGHTED-ROOT-TABLE-CONTROL-PLAN.md']
    bindings = {str(p): sha(p) for p in paths}
    registration = OUT/f'{PREFIX}-registration.json'
    if publish:
        save(registration, dict(inputs=bindings, seed=9273001, deals=512, subbatch_size=32,
            root_iterations=2, tolerance=1e-12, maximum_seconds=180,
            fixture='Stratified physical deals and native catalog observations with synthetic signed targets.',
            native_traversal_qualified=False, training=False, production_modified=False))
    rejected = []
    def rejects(name, call):
        try: call()
        except (ValueError, TypeError): rejected.append(name)
        else: raise AssertionError('Admitted invalid input: '+name)
    sample = ClassStratifiedDeals(source, seed=9273001).sample(512)
    generation = DealWeightGeneration(sample, source)
    # No native calculation is impersonated: these query envelopes and target
    # audits are explicitly synthetic transport fixtures for adapter validation.
    queries = [dict(context_source=source,
        batch_source=json.dumps(dict(deals=sample['deals'][i:i+32])), observations=[])
        for i in range(0, 512, 32)]
    bound = [generation.bind(q, i*32) for i, q in enumerate(queries)]
    matrix = 'a'*64; policy = 'b'*64
    root = WeightedRootRegrets(generation.context_sha256, matrix)
    reference = np.zeros((169, 4)); masses = np.zeros(169); counts = np.zeros(169, dtype=np.int64)
    def audits_for(iteration):
        return [dict(format=1, method='action-integrated-bb-root-targets-v1', iteration=iteration,
            queries_sha256=digest(q), identity=dict(root_estimator='action-integrated-bb-root-targets-v1',
                generation=iteration-1, context_sha256=generation.context_sha256,
                matrix_sha256=matrix, current_initial_policy_sha256=policy),
            bb_root_corrections=[dict(deal=j, hand_class=sample['hand_classes'][32*k+j],
                advantages=[float(((32*k+j+iteration)*(a+1))%17-8) for a in range(4)]) for j in range(32)])
            for k,q in enumerate(queries)]
    args = dict(generation=generation, bindings=bound, expected_deals=512, expected_batches=16)
    for iteration in (1, 2):
        audits = audits_for(iteration)
        root.step(iteration, audits, **args)
        for audit, b in zip(audits, bound):
            for row in audit['bb_root_corrections']:
                c = row['hand_class']; w = b['deal_weights'][row['deal']]
                reference[c] += np.array(row['advantages']) * w
                masses[c] += w; counts[c] += 1
        assert np.array_equal(root.regrets, reference)
        assert np.array_equal(root.masses, masses) and np.array_equal(root.counts, counts)
        if iteration == 1:
            resumed = WeightedRootRegrets.restore(root.document(), context_sha256=generation.context_sha256, matrix_sha256=matrix)
        else:
            resumed.step(iteration, audits, **args)
            assert root.document() == resumed.document()
    fallback = np.full((169, 4), .25)
    assert np.array_equal(root.probabilities(fallback), resumed.probabilities(fallback))
    reordered = WeightedRootRegrets(generation.context_sha256, matrix)
    reordered.step(1, list(reversed(audits_for(1))), **dict(args, bindings=list(reversed(bound))))
    ordered = WeightedRootRegrets(generation.context_sha256, matrix)
    ordered.step(1, audits_for(1), **args)
    assert np.max(abs(reordered.regrets-ordered.regrets)) < 1e-12
    assert np.array_equal(reordered.counts,ordered.counts)
    restore_args = dict(context_sha256=generation.context_sha256, matrix_sha256=matrix)
    rejects('old root reader refuses weighted state', lambda: IntegratedRootRegrets.restore(root.document(), **restore_args))
    rejects('weighted root reader refuses old state', lambda: WeightedRootRegrets.restore(IntegratedRootRegrets(**restore_args).document(), **restore_args))
    for key, change in (
        ('deal_weights', lambda d: d['deal_weights'].__setitem__(0, d['deal_weights'][0]*1.1)),
        ('hand_classes', lambda d: d['hand_classes'].__setitem__(0, (d['hand_classes'][0]+1)%169)),
        ('class_counts', lambda d: d['class_counts'].__setitem__(0, d['class_counts'][0]+1)),
        ('class_mass', lambda d: d['class_mass'].__setitem__(0, d['class_mass'][0]+.001)),
        ('duplicate card', lambda d: d['deals'][0].__setitem__(8, d['deals'][0][0])),
        ('wrong context', lambda d: d.__setitem__('context_sha256', 'c'*64))):
        bad = copy.deepcopy(sample); change(bad)
        rejects(key, lambda: DealWeightGeneration(bad, source))
    reversed_query = copy.deepcopy(queries[0]); batch = json.loads(reversed_query['batch_source'])
    batch['deals'].reverse(); reversed_query['batch_source'] = json.dumps(batch)
    rejects('reordered native deals', lambda: generation.bind(reversed_query, 0))
    for label, mutate in (
        ('swapped source slice', lambda b: b.reverse()),
        ('omitted source slice', lambda b: b.pop()),
        ('changed bound weight', lambda b: b[0]['deal_weights'].__setitem__(0, 1.)),
        ('repeated source slice', lambda b: b.__setitem__(1, copy.deepcopy(b[0])))):
        bad = copy.deepcopy(bound); mutate(bad); before = root.document()
        rejects(label, lambda: root.step(3, audits_for(3), **dict(args, bindings=bad)))
        assert root.document() == before
    bad_audits = audits_for(3); bad_audits[-1]['bb_root_corrections'][-1]['hand_class'] ^= 1
    before = root.document()
    rejects('changed late root class', lambda: root.step(3, bad_audits, **args))
    assert root.document() == before
    bad_state = root.document(); bad_state['importance_mass'][0] = -1
    rejects('negative restored mass', lambda: WeightedRootRegrets.restore(bad_state, **restore_args))

    observations = [copy.deepcopy(r['observation']) for r in read(catalog_path)['native_observations'] if r['player'] == 0][:12]
    weighted = WeightedPhysicalReservoir(256, 0, 9273001, source)
    unit = WeightedPhysicalReservoir(256, 0, 9273001, source)
    old = PhysicalReservoir(256, 0, 9273001, source)
    values_by_key = {}
    for i in range(120):
        o = observations[i%12]; w = (.375, .75, 1., 1.625)[(i//12)%4]
        values = [float(((i+3)*(a+2))%23-11) if a < o['n'] else 0. for a in range(4)]
        weighted.add(o, values, 1, deal_weight=w); unit.add(o, values, 1, deal_weight=1.); old.add(o, values, 1)
        key = (int(o['hi']), int(o['lo']))
        values_by_key.setdefault(key, []).append((w, np.array(values)))
    doc = build(weighted, source); table = Table(doc, source)
    expected_error = 0.
    for row in doc['rows']:
        samples = values_by_key[(int(row['hi']), int(row['lo']))]
        mass = sum(w for w,v in samples)
        expected = sum(w*v for w,v in samples)/mass
        expected_error = max(expected_error, float(np.max(abs(expected - row['mean_regret']))))
        assert row['count'] == len(samples) and abs(row['importance_mass']-mass) < 1e-12
    assert expected_error < 1e-12
    u = build(unit, source); o = old_build(old, source)
    assert len(u['rows']) == len(o['rows'])
    for a,b in zip(u['rows'], o['rows']):
        assert {k:v for k,v in a.items() if k not in ('importance_mass', 'mean_regret')} == {k:v for k,v in b.items() if k != 'mean_regret'}
        assert np.max(abs(np.array(a['mean_regret'])-b['mean_regret'])) < 1e-12
    probabilities = np.array([[1./o['n'] if a < o['n'] else 0. for a in range(4)] for o in observations])
    up, um = Table(u, source).apply(observations, probabilities)
    op, om = OldTable(o, source).apply(observations, probabilities)
    assert um == om and np.max(abs(up-op)) < 1e-12
    rejects('old table reader refuses weighted document', lambda: OldTable(doc, source))
    rejects('weighted table reader refuses old document', lambda: Table(o, source))
    bad = copy.deepcopy(doc); bad['rows'][0]['importance_mass'] = 0
    rejects('zero table mass', lambda: Table(bad, source))
    bad = copy.deepcopy(doc); bad['rows'][0]['importance_mass'] = True
    rejects('boolean table mass', lambda: Table(bad, source))
    assert time.monotonic()-started < 180
    for p,h in bindings.items(): assert sha(p) == h
    result = dict(passed=True, root_weighted_sums_exact=True, root_resume_exact=True,
        root_rejection_transactional=True, table_unit_weight_legacy_equivalence=True,
        maximum_table_weighted_mean_error=expected_error, negative_controls=rejected,
        native_traversal_qualified=False, training_qualified=False, poker_strength_claim=False,
        production_modified=False, seconds=time.monotonic()-started)
    if publish:
        result['registration_sha256'] = sha(registration)
        save(OUT/f'{PREFIX}-result.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--publish', action='store_true')
    main(parser.parse_args().publish)
