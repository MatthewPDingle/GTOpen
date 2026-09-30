"""Qualify fixed-teacher path plumbing on retained native query evidence.

Actual both-player river paths and all-street native own-history links are reused.
Synthetic payoff trees prove intervention algebra; no new native calls, deals,
fits, CUDA, fixed64-bank teacher or scientific accuracy result.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
import stack_context_teacher_path_v1 as teacher

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-teacher-path-check-v2'
NATIVE = OUT/'river-posterior64-native-control-v1'
EVALUATION = Path('S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1')


def read(path):return json.loads(path.read_bytes())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False);stream.write('\n')


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    attempt, result, failure = (OUT/(NAME+suffix+'.json') for suffix in ('-attempt', '-result', '-failure'))
    assert not any(p.exists() for p in (attempt, result, failure))
    eval_proof = OUT/'stack-context-evaluation-integration-check-v1-result.json'
    river_proof = OUT/'river-posterior64-native-control-v1-result.json'
    eproof, rproof = read(eval_proof), read(river_proof)
    assert all(p['passed'] and p['complete'] for p in (eproof, rproof))
    paths = {Path(__file__).resolve(), Path(teacher.__file__).resolve(), eval_proof, river_proof,
        OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md',
        OUT/'stack-context-teacher-path-check-v1-attempt.json',
        OUT/'stack-context-teacher-path-check-v1-failure.json',
        ROOT/'tools/research/stack_context_teacher_path_check_v1.py',
        ROOT/'crates/solver/examples/hu_sampled_profile_allin_evaluation_v1.rs',
        ROOT/'crates/solver/examples/research_sampled/observation_v1.rs',
        ROOT/'crates/solver/examples/research_sampled/policy_bank_v1.rs'}
    for depth in (20, 60):
        for name in ('queries.json', 'profiles.json', 'query-batch.json', 'conditional-batch.json'):
            path = EVALUATION/f'{depth}-cached'/name
            assert sha(path) == eproof['artifacts'][str(path)];paths.add(path)
    # One immutable native case contains 990 complete BOTH-player paths for
    # each of two targets. Its export itself is bound by the original result.
    case = rproof['cases'][0];history_path = NATIVE/case['case']/'new/history-export.json'
    assert sha(history_path) == case['artifacts'][str(Path('new/history-export.json'))]
    paths.add(history_path)
    inputs = {str(path):sha(path) for path in paths}
    save(attempt, dict(inputs=inputs, qualification_only=True, reused_native_queries=True,
        synthetic_payoff_tree=True, cpu_priority='below-normal', cpu_workers=1,
        new_scientific_deals=False, fitting=False, native_execution=False, gpu=False))
    began = time.monotonic();negative = [];records = [];interventions = 0;invariance = 0
    def reject(label, fn):
        try:fn()
        except (ValueError, KeyError, TypeError):negative.append(label)
        else:raise AssertionError('Accepted '+label)
    try:
        for depth in (20, 60):
            query = read(EVALUATION/f'{depth}-cached/queries.json');binding = teacher.Binding(query)
            transport = read(EVALUATION/f'{depth}-cached/profiles.json')
            assert transport['context_source'] == query['context_source']
            raw_path = EVALUATION/f'{depth}-cached/query-batch.json'
            conditional_path = EVALUATION/f'{depth}-cached/conditional-batch.json'
            assert query['batch_source'] == raw_path.read_text() and transport['batch_source'] == conditional_path.read_text()
            raw, labelled = read(raw_path), read(conditional_path)
            assert raw['format'] == 2 and labelled['format'] == 3
            assert not any(k.startswith('allin_') or k == 'terminal_estimator' for k in raw)
            assert all(labelled[k] == v for k, v in raw.items() if k != 'format')
            p = np.asarray([row['probabilities'] for row in transport['profiles'][0]['policies']], dtype=np.float64)
            assert [(r['hi'], r['lo'], r['actor'], r['n']) for r in transport['profiles'][0]['policies']] == [
                (r['hi'], r['lo'], r['actor'], r['n']) for r in query['observations']]
            frozen = binding.freeze(p);original = p.copy();old_query = teacher.encoded(query)
            deals = sorted(set(map(tuple, json.loads(query['batch_source'])['deals'])))
            phases = [0]*4;both = 0
            for deal in deals:
                for hi in binding.public:
                    target, path = binding.trace(deal, hi);row = query['observations'][target]
                    phases[row['phase']] += 1;indices = {i for i, _, _ in path}
                    if {query['observations'][i]['actor'] for i in indices} == {0, 1}:both += 1
                    for action in range(row['n']):
                        got = frozen.intervene(deal, hi, action);profile = got['probabilities']
                        assert got['path'] == path and got['target_index'] == target
                        assert np.array_equal(got['original_sigma'], original[target])
                        altered = indices | {target};others = [i for i in range(len(p)) if i not in altered]
                        assert np.array_equal(profile[others], original[others])
                        assert np.array_equal(profile[target], np.eye(4)[action])
                        for index, a, _ in path:assert np.array_equal(profile[index], np.eye(4)[a])
                        likelihood = [1., 1.]
                        for index, a, _ in path:likelihood[query['observations'][index]['actor']] *= float(original[index, a])
                        assert got['original_path_likelihood_by_actor'] == likelihood
                        assert not profile.flags.writeable;interventions += 1
                    # Change every hidden future board slot, leaving the actual
                    # past and target inputs byte-identical. Do not change any
                    # source batch, or sample/retain new diagnostic deals.
                    visible = (0, 3, 4, 5)[row['phase']]
                    if visible < 5:
                        retained = list(deal[:4+visible]);available = [c for c in range(51, -1, -1) if c not in retained]
                        altered_deal = retained+available[:5-visible]
                        assert binding.trace(altered_deal, hi) == (target, path);invariance += 1
                    hand, board = binding.cards[target]
                    assert teacher.card_key(hand, board, row['actor']) == row['lo']
            assert np.array_equal(p, original) and np.array_equal(frozen.p, original) and teacher.encoded(query) == old_query
            # Caller mutation after construction must not change the teacher.
            p[:] = 0.;assert np.array_equal(frozen.p, original)
            records.append(dict(depth=depth, distinct_retained_deals=len(deals), native_rows=len(original),
                targets_by_phase=phases, targets_with_both_players_in_past=both,
                original_native_own_links_checked=sum(len(r['own_history']) for r in query['observations'])))

        history = read(history_path);river = teacher.Binding(history['queries']);river_paths = 0
        for doc in history['targets']:
            t = doc['target'];hero = t['actor'];cards = t['cards']
            for pair in doc['pairs']:
                deal = ([*cards[:2], *pair['cards']] if hero == 0 else [*pair['cards'], *cards[:2]])+cards[2:]
                target, path = river.trace(deal, t['hi'])
                assert target == t['query_index'] and path == pair['path'];river_paths += 1
        assert river_paths == 1980

        # A synthetic forward payoff tree on a real native query/path proves
        # that target-only forcing or dividing root value by arrival is wrong.
        query = read(EVALUATION/'60-cached/queries.json');binding = teacher.Binding(query)
        deal = json.loads(query['batch_source'])['deals'][0]
        hi = next(hi for hi in binding.public if binding.public[hi]['n'] == 2 and
            len(binding.trace(deal, hi)[1]) >= 2 and
            {query['observations'][i]['actor'] for i, _, _ in binding.trace(deal, hi)[1]} == {0, 1})
        target, path = binding.trace(deal, hi);used = {i for i, _, _ in path} | {target}
        future = next(i for i, r in enumerate(query['observations']) if i not in used and r['n'] == 2)
        p = np.zeros((len(query['observations']), 4))
        for i, r in enumerate(query['observations']):p[i, :r['n']] = 1/r['n']
        p[target] = [.2, .8, 0., 0.];p[future] = [.75, .25, 0., 0.];frozen = binding.freeze(p)
        def reverse(profile):
            value = profile[target, 0]*5+profile[target, 1]*(profile[future, 0]*(-4)+profile[future, 1]*8)
            for j, (index, chosen, n) in reversed(list(enumerate(path))):
                value = profile[index, chosen]*value+sum(profile[index, a]*(20+j+a) for a in range(n) if a != chosen)
            return value
        def forward(profile):
            mass = 1.;values = []
            for j, (index, chosen, n) in enumerate(path):
                values.extend(mass*profile[index, a]*(20+j+a) for a in range(n) if a != chosen)
                mass *= profile[index, chosen]
            values.extend((mass*profile[target, 0]*5, mass*profile[target, 1]*profile[future, 0]*(-4),
                mass*profile[target, 1]*profile[future, 1]*8))
            return sum(values)
        q = [5., -1.];errors = [];shortcuts = []
        arrival = float(np.prod([p[i, a] for i, a, _ in path]))
        for action in range(2):
            forced = frozen.intervene(deal, hi, action)['probabilities']
            assert abs(reverse(forced)-forward(forced)) < 1e-12
            errors.append(abs(forward(forced)-q[action]));assert errors[-1] < 1e-12
            target_only = p.copy();target_only[target] = np.eye(4)[action]
            own_only = target_only.copy()
            for i, a, _ in path:
                if query['observations'][i]['actor'] == query['observations'][target]['actor']:own_only[i] = np.eye(4)[a]
            assert abs(forward(target_only)-q[action]) > .1
            assert abs(forward(target_only)/arrival-q[action]) > .1
            assert abs(forward(own_only)-q[action]) > .1
            shortcuts.append(dict(action=action, correct=q[action], target_only=forward(target_only),
                divided_by_arrival=forward(target_only)/arrival, own_only=forward(own_only)))
        values = teacher.advantage(q, p[target, :2], starting_stack=60.)
        assert abs(values['value']-.2) < 1e-12 and abs(float(p[target, :2] @ values['advantage'])) < 1e-12
        assert np.array_equal(values['advantage'], (np.asarray(q)-.2)/60)

        # Structural corruption, illegal forcing and incomplete teacher policies.
        reject('noncanonical public key', lambda:teacher.public_key('01'))
        reject('reserved public history token', lambda:teacher.public_key(str(2**63+(14 << 4)+2)))
        reject('preflop outside native range', lambda:teacher.public_key('17'))
        reject('boolean physical card', lambda:teacher.card_key([True, 4], [], 0))
        reject('future/incomplete board', lambda:teacher.card_key([0, 4], [8], 0))
        reject('duplicate visible card', lambda:teacher.card_key([0, 4], [0, 8, 12], 0))
        reject('illegal target action', lambda:frozen.intervene(deal, hi, 2))
        reject('boolean target action', lambda:frozen.intervene(deal, hi, True))
        reject('duplicate physical deal card', lambda:binding.trace([deal[0], deal[0], *deal[2:]], hi))
        reject('missing physical deal card', lambda:binding.trace(deal[:-1], hi))
        reject('unknown target public key', lambda:binding.trace(deal, '16'))
        reject('missing teacher row', lambda:binding.freeze(p[:-1]))
        bad = p.copy();bad[0, 0] = np.nan;reject('nonfinite teacher', lambda:binding.freeze(bad))
        bad = p.copy();bad[0] = 0.;reject('unnormalized teacher', lambda:binding.freeze(bad))
        bad = p.copy();bad[target] = [0., .5, .5, 0.];reject('illegal teacher action', lambda:binding.freeze(bad))
        damaged = copy.deepcopy(query);row = next(r for r in damaged['observations'] if r['own_history']);row['own_history'].pop()
        reject('lost original own ancestor', lambda:teacher.Binding(damaged))
        damaged = copy.deepcopy(query);row = next(r for r in damaged['observations'] if r['own_history']);row['own_history'][0][0] = True
        reject('boolean ancestor index', lambda:teacher.Binding(damaged))
        damaged = copy.deepcopy(query);row = next(r for r in damaged['observations'] if r['phase'] == 0);row['lo'] = str(int(row['lo']) & ~(63 << 12))
        reject('preflop hidden future card', lambda:teacher.Binding(damaged))
        damaged = copy.deepcopy(query);damaged['observations'][0]['active_features'][0] += 1
        reject('key/feature mismatch', lambda:teacher.Binding(damaged))
        damaged = copy.deepcopy(query);row = next(r for r in damaged['observations'] if r['phase'] > 0);row['n'] = 3 if row['n'] == 2 else 2
        reject('public menu disagreement', lambda:teacher.Binding(damaged))
        damaged = copy.deepcopy(query);context = json.loads(damaged['context_source']);context['nodes'][0]['children'][0] = 0;damaged['context_source'] = json.dumps(context)
        reject('cyclic context', lambda:teacher.Binding(damaged))
        reject('unbounded stack normalization', lambda:teacher.advantage(q, [.2, .8], starting_stack=0))
        reject('boolean stack normalization', lambda:teacher.advantage(q, [.2, .8], starting_stack=True))
        reject('changed teacher baseline', lambda:teacher.advantage(q, [.5, .8], starting_stack=60))
        for path, identity in inputs.items():assert sha(path) == identity
        answer = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            native_all_street_records=records, actual_both_player_river_paths=river_paths,
            legal_interventions_checked=interventions, hidden_future_invariance_checks=invariance,
            synthetic_action_value_errors=errors, rejected_shortcut_examples=shortcuts,
            negative_cases=negative, original_teacher_probabilities_frozen=True,
            preserved_failed_check_v1=True, corrected_visible_and_conditional_batch_binding=True,
            new_scientific_deals=0, native_calls=0, fits=0, gpu=False, production_modified=False,
            actual_fixed64_teacher_available=False, conditional_hidden_future_targets_qualified=False,
            full_native_intervention_payoff_run_qualified=False, scientific_accuracy_evidence=False,
            actual_diagnostic_registered=False, actual_diagnostic_complete=False)
        save(result, answer)
        print(json.dumps(dict(passed=True, seconds=answer['seconds'], all_street_rows=sum(r['native_rows'] for r in records),
            actual_both_player_river_paths=river_paths, interventions=interventions, negative_cases=len(negative))), flush=True)
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False));raise


if __name__ == '__main__':main()
