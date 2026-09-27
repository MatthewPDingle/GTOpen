"""Exact accumulator restoration and disjoint composite archive routing."""
import math
from pathlib import Path
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader


def restore_accumulator(comparison, states, expected_count):
    assert len(states) == len(comparison.series) == 8
    assert type(expected_count) is int and 0 <= expected_count <= comparison.plan.looks[-1]
    for target, state in zip(comparison.series, states):
        assert set(state) == {'series', 'count', 'mean', 'm2'}
        assert state['series'] == target.series and type(state['count']) is int
        assert state['count'] == expected_count
        assert math.isfinite(state['mean']) and comparison.plan.lower <= state['mean'] <= comparison.plan.upper
        assert math.isfinite(state['m2']) and state['m2'] >= 0
    for target, state in zip(comparison.series, states):
        target.count, target.mean, target.m2 = state['count'], state['mean'], state['m2']


def validate_partition(manifests, original, total_deals):
    assert type(total_deals) is int and total_deals > 0 and total_deals % 32 == 0
    expected = [f'test-{i:06d}' for i in range(0,total_deals,32)]
    assert set(manifests) == set(expected)
    assert 0 < len(original) < len(manifests)
    assert set(original) == set(expected[:len(original)])
    assert all(isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v) for v in manifests.values())
    assert all(manifests[n] == h for n,h in original.items())
    return {n:manifests[n] for n in expected[len(original):]}


class CompositeEvaluationReader:
    def __init__(self, root, manifests, *, original_store, original_hashes, total_deals, guard):
        self.root, self.original_store = Path(root).absolute(), Path(original_store).absolute()
        assert self.root != self.original_store
        suffix = validate_partition(manifests, original_hashes, total_deals)
        self.original_hashes = original_hashes
        self.old = ColumnarEvaluationReader(self.original_store, original_hashes, external_files=[], guard=guard)
        self.new = ColumnarEvaluationReader(self.root, suffix, external_files=[], guard=guard)

    def read_bytes(self, path):
        path = Path(path).absolute()
        assert path.parent.parent == self.root
        if path.parent.name in self.original_hashes:
            return self.old.read_bytes(self.original_store/path.parent.name/path.name)
        return self.new.read_bytes(path)


def verify_continuation(reg, result):
    from sampled_physical_root_evaluation_v1 import sha
    from later_average_support_v1 import OUT, read
    old = 'showdown-composite-evaluation-study-v1'
    assert reg['batch_id_prefix'] == old
    original_rp = OUT/f'{old}-registration.json'
    assert sha(original_rp) == reg['original_registration_sha256']
    original = read(original_rp)
    assert reg['original_store'] == original['store']
    for field in ('training_arms','training_admission','deals','test_seed','batch_size','mode'):
        assert reg[field] == original[field]
    for path,h in original['inputs'].items():
        assert reg['inputs'][path] == h and sha(path) == h
    status = read(OUT/f'{old}-status.json')
    assert status['state']=='failed' and status['exit_code'] != 0
    assert not (OUT/f'{old}-result.json').exists()
    assert result['original_registration_sha256'] == sha(original_rp)
    assert result['original_completed_deals'] == 32*len(reg['original_manifest_hashes'])
    validate_partition(result['archive_manifest_hashes'],reg['original_manifest_hashes'],reg['deals'])
    control_path=Path(reg['store'])/'migration-control-result.json'
    assert sha(control_path)==result['migration_control_sha256']
    control=read(control_path)
    assert control['passed'] and control['deals']==64 and len(control['checks'])==2
    assert all(c['profiles_byte_identical'] and c['native_profile_values_identical'] for c in control['checks'])
    assert control['original_control_result_sha256']==sha(OUT/'showdown-composite-evaluation-control-v1-result.json')
