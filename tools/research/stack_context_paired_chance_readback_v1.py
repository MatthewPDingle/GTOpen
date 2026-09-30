"""One-shot read-only diagnosis of the preserved cycle-two matching failure."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import time
import traceback
from stack_context_paired_chance_v1 import matched_board_chance
from owned_research_archive_v1 import unpack
from sampled_visible_hybrid_checkpoint_v1 import read_object
from board_root_accumulator_v1 import BoardRootRegrets

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE = Path('S:/GTOpen-research/stack-context-matched-learning-v1')
NAME = 'stack-context-paired-chance-readback-v1'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def save(path, value):
    with path.open('x', encoding='utf-8') as stream:json.dump(value, stream, sort_keys=True, separators=(',', ':'), allow_nan=False)


def main():
    attempt, output, failure = (OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure'))
    if any(p.exists() for p in (attempt, output, failure)):raise ValueError('Preserve previous diagnosis evidence')
    failed = OUT/'stack-context-matched-learning-v1-failure.json'
    assert read(failed)['error'] == "ValueError('Matched representations did not use identical physical/action/board streams')"
    reg = OUT/'stack-context-matched-learning-v1-registration.json'; spec = read(reg)
    left_progress = read(STORE/'A-baseline/progress.json'); right_progress = read(STORE/'A-relative/progress.json')
    assert left_progress['completed_cycles'] == 2 and right_progress['completed_cycles'] == 1
    raw = STORE/'A-relative/cycle-0002'; metric = read(raw/'metrics.json')
    assert metric['completed_cycles'] == 2
    parent = {}
    inputs = {str(p):sha(p) for p in (Path(__file__).resolve(), Path(__file__).with_name('stack_context_paired_chance_v1.py'),
              reg, failed, STORE/'A-baseline/progress.json', STORE/'A-relative/progress.json', raw/'metrics.json')}
    for arm, progress in (('A-baseline', left_progress), ('A-relative', right_progress)):
        objects = STORE/arm/'objects'; checkpoint_ref = progress['updates'][0]['checkpoint']
        checkpoint = json.loads(read_object(objects, checkpoint_ref)); ref = checkpoint['next_model']
        value = json.loads(read_object(objects, ref)); assert value['generation'] == 1
        parent[arm] = value
        inputs[str(objects/checkpoint_ref['file'])] = sha(objects/checkpoint_ref['file'])
        inputs[str(objects/ref['file'])] = sha(objects/ref['file'])
    archive = STORE/'A-baseline/archive-0002'
    plan = read(archive/'plan.json'); assert sha(archive/'index.json') == left_progress['updates'][1]['archive_index_sha256']
    inputs[str(archive/'plan.json')] = sha(archive/'plan.json')
    inputs[str(archive/'index.json')] = sha(archive/'index.json')
    pairs = left_progress['updates'][1]['paired_sources']; identical = []; different = []
    for name, identity in pairs.items():
        path = raw/name; actual = sha(path); inputs[str(path)] = actual
        (identical if actual == identity else different).append(name)
    assert len(identical) == 70 and len(different) == 5 and all(n.endswith('/board-plan.json') for n in different)
    save(attempt, dict(inputs=inputs, scientific_attempt_restarted=False, files_modified=False,
        source_failure_sha256=sha(failed), purpose='determine whether chance or arm-local state differs'))
    began = time.monotonic()
    try:
        records = []; rejects = []
        def reject(name, left, right, a, b, cfg):
            try:matched_board_chance(left, right, left_parent=a, right_parent=b, expected_config=cfg)
            except ValueError:rejects.append(name)
            else:raise AssertionError('Invalid matched input accepted: '+name)
        for name in different:
            key = name.split('/')[0]
            job = next(j for j in plan['jobs'] if Path(j['source']).name == key and 'board-plan.json' in j['names'])
            path = Path(job['destination']); manifest = path.with_suffix('.xz.json')
            restored = unpack(path, read(manifest), guard=lambda:None)
            left_raw = restored['board-plan.json']; left = json.loads(left_raw); right = read(raw/name)
            assert hashlib.sha256(left_raw).hexdigest() == pairs[name]
            inputs[str(path)] = sha(path); inputs[str(manifest)] = sha(manifest)
            a = parent['A-baseline']['local_states'][key]['board_root_state']
            b = parent['A-relative']['local_states'][key]['board_root_state']
            cfg = spec['arms']['A-baseline']['config']['contexts'][key]['board_root']
            assert cfg == spec['arms']['A-relative']['config']['contexts'][key]['board_root']
            result = matched_board_chance(left, right, left_parent=a, right_parent=b, expected_config=cfg)
            fields = [field for field in left if left[field] != right[field]]
            assert fields == ['parent_state_sha256'] and not result['parents_are_identical']
            records.append(dict(context_sha256=key, differing_fields=fields, **result))
            damaged = copy.deepcopy(right); damaged['boards'][0][0] = (damaged['boards'][0][0]+1) % 52
            reject(key+'/different-board', left, damaged, a, b, cfg)
            reject(key+'/wrong-own-parent', left, right, a, a, cfg)
            damaged = copy.deepcopy(right); damaged['generation'] += 1
            reject(key+'/generation', left, damaged, a, b, cfg)
            damaged = copy.deepcopy(right); damaged['config_sha256'] = '0'*64
            reject(key+'/config-identity', left, damaged, a, b, cfg)
            damaged = copy.deepcopy(b); damaged['regret_sums'][0][0] += 1
            reject(key+'/unsealed-state', left, right, a, damaged, cfg)
            reject(key+'/unrecognized-field', left, dict(right, ignored=True), a, b, cfg)
            # Baseline self-match must remain valid; parent equality is allowed.
            assert matched_board_chance(left, left, left_parent=a, right_parent=a, expected_config=cfg)['parents_are_identical']
        for path, identity in inputs.items():assert sha(path) == identity
        # Validate the unpublished completed checkpoint is readable; no marker
        # is advanced and none of its scientific work is repeated here.
        candidate = json.loads(read_object(STORE/'A-relative/objects', metric['checkpoint']))
        assert candidate['completed_cycles'] == 2 and candidate['played_bank'][-1] == metric['used_model']
        assert candidate['next_model'] == metric['next_model']
        inputs[str(STORE/'A-relative/objects'/metric['checkpoint']['file'])] = sha(STORE/'A-relative/objects'/metric['checkpoint']['file'])
        result = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs, records=records,
            exact_non_board_source_hash_matches=70, board_draw_matches=5, rejected_corruptions=rejects,
            actual_chance_mismatch=False, false_positive_parent_state_comparison=True,
            completed_unpublished_relative_cycle=2, failed_attempt_preserved=True,
            progress_modified=False, scientific_work_repeated=False, permission_to_resume_inferred=False,
            explanation='The original gate compared complete board-plan file hashes, including the arm-specific parent state; actual draws and other chance inputs match.')
        save(output, result)
        print(json.dumps(dict(passed=True, exact_other_source_matches=70, matched_boards=5,
            differing_field='parent_state_sha256', negative_cases=len(rejects), seconds=result['seconds'])))
    except BaseException as error:
        save(failure, dict(error=repr(error), traceback=traceback.format_exc(), preserve_evidence=True))
        raise


if __name__ == '__main__':main()
