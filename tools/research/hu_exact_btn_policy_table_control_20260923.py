"""CPU-only policy-table integration control; no active model is changed."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import copy
import json
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from preflop_allin_matrix_v1 import AllinMatrix
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from exact_btn_policy_table_v1 import ExactBtnTable, document
from sampled_physical_preflop_table_v1 import Table
from sampled_physical_hybrid_gpu_bank_v2 import prepare_tables
from sampled_visible_hybrid_checkpoint_v1 import model_document, validate_model
from reboot_research_idle_v1 import idle

PREFIX = 'exact-btn-policy-table-control-v1'


def main():
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 300 and idle()
        assert psutil.virtual_memory().available > 20_000_000_000
    guard()
    cp = OUT/'bb-context-candidate.json'
    source = cp.read_text()
    matrix_result = read(OUT/'preflop-allin-matrix-control-v1-result.json')
    matrix_path = Path(matrix_result['matrix_artifact'])
    matrix_hash = sha(matrix_path)
    assert matrix_result['passed'] and matrix_hash == matrix_result['matrix_sha256']
    matrix = AllinMatrix(read(matrix_path), source)
    catalog_path = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    catalog_source = catalog_path.read_text()
    catalog = json.loads(catalog_source)['native_observations']
    prior = read(OUT/'allin-generation-attribution-v1-result.json')
    policies_path = next(Path(p) for p in prior['artifacts'] if Path(p).name == 'visible_302-generation-policies.json')
    assert sha(policies_path) == prior['artifacts'][str(policies_path)]
    policies = read(policies_path)['policies']
    completed_path = OUT/'wider-root-evaluation-control-v1-registration.json'
    completed = read(completed_path)
    for p, h in completed['inputs'].items():
        assert sha(p) == h
    objects = Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    checkpoint_path = objects/completed['checkpoint']['file']
    assert sha(checkpoint_path) == completed['checkpoint']['sha256']
    checkpoint = read(checkpoint_path)
    base_model = model_document(objects, checkpoint['played_bank'][-1], context_source=source)
    base_table = Table(base_model['preflop_tables'][1], source)
    query_path = Path(completed['store'])/'train-000000/queries.json'
    summary_path = query_path.parent/'summary.json'
    assert sha(query_path) == read(summary_path)['artifacts']['queries.json']
    queries = read(query_path)
    observations = queries['observations']
    assert queries['context_source'] == source
    fallback = np.array([[1/o['n'] if a < o['n'] else 0 for a in range(4)] for o in observations])
    baseline, _ = base_table.apply(observations, fallback)
    paths = [Path(__file__), ROOT/'tools/research/exact_btn_policy_table_v1.py',
        ROOT/'tools/research/exact_btn_regret_accumulator_v1.py', cp, matrix_path,
        OUT/'preflop-allin-matrix-control-v1-result.json', catalog_path, policies_path,
        OUT/'allin-generation-attribution-v1-result.json', completed_path, checkpoint_path,
        objects/checkpoint['played_bank'][-1]['file'], query_path, summary_path]
    inputs = {str(p.resolve()): sha(p) for p in paths}
    rp = OUT/f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, generations=[0,25,51,77], maximum_seconds=300,
        operation='Build distinct exact-state policy tables; compare all catalog classes and actual mixed-street native queries, checkpoint round trips and CUDA table-preparation arrays without launching CUDA.',
        gpu_used=False, training_integration=False, production_modified=False))
    state = ExactBtnRegrets(sha(cp), matrix.btn_mass)
    zero = ExactBtnTable(document(state, context_source=source, catalog_source=catalog_source,
        matrix_sha256=matrix_hash), source, catalog_source, matrix_sha256=matrix_hash, entry_mass=matrix.btn_mass)
    assert not zero.rows
    zero_p, _ = zero.compose(base_table).apply(observations, fallback)
    assert np.array_equal(zero_p, baseline)
    records = []
    for step, generation in enumerate((0,25,51,77), 1):
        guard()
        root = np.zeros((169,4)); calls = np.full(169, np.nan)
        for row, probability in zip(catalog, policies[generation]):
            if row['player'] == 0:
                root[row['hand_class']] = probability
            else:
                calls[row['hand_class']] = probability[1]
        exact = matrix.evaluate(root, calls)
        state.step(step, calls, exact['btn_jam_mass'], exact['btn_fold_entries'], exact['btn_call_entries'])
        value = document(state, context_source=source, catalog_source=catalog_source, matrix_sha256=matrix_hash)
        table = ExactBtnTable(json.loads(json.dumps(value)), source, catalog_source,
            matrix_sha256=matrix_hash, entry_mass=matrix.btn_mass)
        combined = table.compose(base_table)
        actual, _ = combined.apply(observations, fallback)
        expected = baseline.copy()
        expected_rows = []
        class_p = state.probabilities(np.full((169,2), .5))
        for i, o in enumerate(observations):
            if o['actor'] == 1 and o['phase'] == 0 and int(o['hi']) == table.response_hi:
                lo = int(o['lo']); c = hand_class([lo&63, (lo>>6)&63])
                if state.reach[c] > 0:
                    expected[i] = [*class_p[c], 0., 0.]
                    expected_rows.append(i)
        assert expected_rows and np.array_equal(actual, expected)
        ids, values, mask = prepare_tables(queries, [[None, combined]], source)
        from_prepared = fallback.copy()
        from_prepared[ids[mask[0]]] = values[0,mask[0]]
        assert np.array_equal(from_prepared, actual)
        native_catalog = [r['observation'] for r in catalog]
        catalog_fallback = np.array([[1/o['n'] if a<o['n'] else 0 for a in range(4)] for o in native_catalog])
        catalog_p, _ = table.apply(native_catalog, catalog_fallback)
        covered = 0
        for row, p in zip(catalog, catalog_p):
            if row['player'] == 1 and state.reach[row['hand_class']] > 0:
                assert np.array_equal(p, [*class_p[row['hand_class']], 0., 0.]); covered += 1
        assert covered == np.count_nonzero(state.reach)
        records.append(dict(generation=generation, exact_classes=covered,
            native_response_rows=len(expected_rows), other_native_rows_unchanged=len(observations)-len(expected_rows)))
    rejected = []
    def reject(name, fn):
        try:
            fn()
        except (ValueError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError(f'Did not reject {name}')
    reject('old-sampled-table-reader', lambda: Table(value, source))
    reject('old-model-reader', lambda: validate_model(value, source))
    reject('changed-matrix', lambda: ExactBtnTable(value, source, catalog_source, matrix_sha256='0'*64, entry_mass=matrix.btn_mass))
    reject('changed-population', lambda: ExactBtnTable(value, source, catalog_source, matrix_sha256=matrix_hash, entry_mass=np.full(169,1/169)))
    changed = copy.deepcopy(observations)
    changed[expected_rows[0]]['own_history'] = [[0,1]]
    reject('impossible-own-history', lambda: combined.apply(changed, fallback))
    changed_value = copy.deepcopy(value); changed_value['state']['sampled_observations_added'] = 1
    reject('invented-sampled-count', lambda: ExactBtnTable(changed_value, source, catalog_source, matrix_sha256=matrix_hash, entry_mass=matrix.btn_mass))
    for p, h in inputs.items():
        assert sha(p) == h
    guard()
    result = dict(passed=True, registration_sha256=sha(rp), states=records,
        zero_reach_preserves_base=True, roundtrips=4, corruptions_rejected=rejected,
        exact_override_precedes_sampled_rows=True, other_native_probabilities_unchanged=True,
        gpu_table_preparation_matches_cpu_application=True, cuda_execution_tested=False,
        seconds=time.monotonic()-started, gpu_used=False, training_integration=False,
        production_modified=False, accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json', result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
