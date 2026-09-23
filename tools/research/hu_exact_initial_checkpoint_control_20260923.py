"""Repack a completed base checkpoint with synthetic exact-state fixtures.

This validates serialization/restart wiring, not a trained exact-policy result.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import copy
import json
import shutil
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from preflop_allin_matrix_v1 import AllinMatrix
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
import sampled_visible_hybrid_checkpoint_v1 as base
import exact_initial_hybrid_checkpoint_v1 as exact_checkpoint
from reboot_research_idle_v1 import idle

PREFIX = 'exact-initial-checkpoint-control-v1'
STORE = Path('T:/GTOpen-research')/PREFIX


def main():
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 600 and idle()
        assert psutil.virtual_memory().available > 20_000_000_000
        assert shutil.disk_usage('T:/').free > 40_000_000_000
    guard()
    assert not STORE.exists()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists()
    cp = OUT/'bb-context-candidate.json'
    source = cp.read_text()
    catalog_path = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    catalog = catalog_path.read_text()
    matrix_result = read(OUT/'preflop-allin-matrix-control-v1-result.json')
    matrix_path = Path(matrix_result['matrix_artifact'])
    matrix_hash = sha(matrix_path)
    assert matrix_result['passed'] and matrix_hash == matrix_result['matrix_sha256']
    matrix = AllinMatrix(read(matrix_path), source)
    old_rp = OUT/'wider-root-evaluation-control-v1-registration.json'
    oldreg = read(old_rp)
    objects = Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    old_ref = oldreg['checkpoint']
    old_cp_path = objects/old_ref['file']
    assert sha(old_cp_path) == old_ref['sha256']
    old_cp = read(old_cp_path)
    old = base.restore_checkpoint(objects, old_ref, context_source=source, config=old_cp['config'])
    assert old['completed_iterations'] == 4
    config = dict(old_cp['config'], **{exact_checkpoint.CONFIG_KEY: exact_checkpoint.POLICY_TYPE})
    paths = [Path(__file__), ROOT/'tools/research/exact_initial_hybrid_checkpoint_v1.py',
        ROOT/'tools/research/exact_btn_policy_table_v1.py',
        ROOT/'tools/research/exact_btn_regret_accumulator_v1.py', cp, catalog_path,
        matrix_path, OUT/'preflop-allin-matrix-control-v1-result.json', old_rp, old_cp_path]
    paths.extend(objects/r['file'] for r in [*old_cp['played_bank'], old_cp['next_model'], *old_cp['reservoirs']])
    inputs = {str(p.resolve()): sha(p) for p in paths}
    save(rp, dict(inputs=inputs, store=str(STORE), maximum_seconds=600,
        fixture='Historical four-update sampled/network base plus separately computed synthetic exact-state progression; not trained together.',
        protocol='Roundtrip complete played bank, next exact state, sampler, action RNG and both reservoirs; compare next draws and exact update.',
        gpu_used=False, training_integration=False, production_modified=False))
    STORE.mkdir()
    state = ExactBtnRegrets(sha(cp), matrix.btn_mass)
    references = []
    kwargs = dict(context_source=source, catalog_source=catalog,
                  matrix_sha256=matrix_hash, entry_mass=matrix.btn_mass)
    for generation, ref in enumerate([*old['played_bank'], old['next_model']]):
        guard()
        if generation:
            root = np.full((169,4), .25)
            calls = np.full(169, .1*generation)
            entries = matrix.evaluate(root, calls)
            state.step(generation, calls, entries['btn_jam_mass'], entries['btn_fold_entries'], entries['btn_call_entries'])
        document = base.model_document(objects, ref, context_source=source)
        references.append(exact_checkpoint.write_model(STORE, document, state, **kwargs))
    saved = exact_checkpoint.save_checkpoint(STORE, completed=4, config=config,
        sampler=old['sampler'], action_rng=old['action_rng'], reservoirs=old['reservoirs'],
        bank=references[:-1], current=references[-1], **kwargs)
    restored = exact_checkpoint.restore_checkpoint(STORE, saved, config=config, **kwargs)
    assert restored['completed_iterations'] == 4
    assert restored['played_bank'] == references[:-1] and restored['next_model'] == references[-1]
    assert restored['exact_btn_state'].document() == state.document()
    assert restored['sampler'].checkpoint() == old['sampler'].checkpoint()
    assert restored['action_rng'].bit_generator.state == old['action_rng'].bit_generator.state
    for a, b in zip(old['reservoirs'], restored['reservoirs']):
        assert a.summary() == b.summary() and a.rng.bit_generator.state == b.rng.bit_generator.state
        for field in ('keys','active','arity','values','iterations'):
            assert np.array_equal(getattr(a,field), getattr(b,field))
    assert restored['sampler'].sample(64) == old['sampler'].sample(64)
    assert np.array_equal(restored['action_rng'].integers(0,2**63,size=64), old['action_rng'].integers(0,2**63,size=64))
    for a, b in zip(old['reservoirs'], restored['reservoirs']):
        assert np.array_equal(a.rng.integers(0,2**63,size=64), b.rng.integers(0,2**63,size=64))
    entries = matrix.evaluate(np.full((169,4),.25), np.full(169,.7))
    for s in (state, restored['exact_btn_state']):
        s.step(5, np.full(169,.7), entries['btn_jam_mass'], entries['btn_fold_entries'], entries['btn_call_entries'])
    assert state.document() == restored['exact_btn_state'].document()
    rejected = []
    def reject(label, fn):
        try:
            fn()
        except (ValueError, KeyError):
            rejected.append(label)
        else:
            raise AssertionError(f'Did not reject {label}')
    reject('old-checkpoint-reader', lambda: base.restore_checkpoint(STORE, saved, context_source=source, config=config))
    reject('old-model-reader', lambda: base.model_document(STORE, references[-1], context_source=source))
    reject('missing-exact-config', lambda: exact_checkpoint.restore_checkpoint(STORE, saved, config=old_cp['config'], **kwargs))
    wrong = dict(kwargs, matrix_sha256='0'*64)
    reject('changed-matrix', lambda: exact_checkpoint.restore_checkpoint(STORE, saved, config=config, **wrong))
    wrong_order = [references[1], references[0], *references[2:-1]]
    reject('reordered-played-bank', lambda: exact_checkpoint.verify_bank(STORE,4,wrong_order,references[-1],**kwargs))
    reject('unplayed-next-in-average', lambda: exact_checkpoint.verify_bank(STORE,4,references,references[-1],**kwargs))
    value = exact_checkpoint.model_document(STORE, references[-1], **kwargs)
    wrong_document = copy.deepcopy(value)
    wrong_document['exact_btn']['state']['completed_updates'] = 3
    reject('state-generation-mismatch', lambda: exact_checkpoint.validate_model(wrong_document, source, catalog, matrix_hash, matrix.btn_mass))
    wrong_ref = dict(references[-1], sha256='0'*64)
    reject('object-hash', lambda: exact_checkpoint.model_document(STORE,wrong_ref,**kwargs))
    stable = state.document()
    reject('duplicate-restored-update', lambda: state.step(5,np.full(169,.7),entries['btn_jam_mass'],entries['btn_fold_entries'],entries['btn_call_entries']))
    assert state.document() == stable
    for p, digest in inputs.items():
        assert sha(p) == digest
    guard()
    result = dict(passed=True, registration_sha256=sha(rp), checkpoint=saved,
        played_generations=[0,1,2,3], next_generation=4,
        reservoir_arrays_and_rngs_identical=True, next_draws_and_exact_update_identical=True,
        rejected=rejected, seconds=time.monotonic()-started,
        gpu_used=False, training_integration=False, accuracy_qualified=False, production_modified=False)
    save(OUT/f'{PREFIX}-result.json', result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
