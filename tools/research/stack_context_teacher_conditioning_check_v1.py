"""Conditional-history and chance qualification; not a scientific comparison.

Retained native rows, two existing CPU model fixtures, exact entry conventions,
native river posterior parity and deterministic chance-law/stream checks. Values
used for reduction checks are synthetic. No native execution, fitting or CUDA.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_context_teacher_conditioning_v1 as condition
from stack_context_teacher_path_v1 import Binding, encoded
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
import stack_context_policy_v1 as baseline
import stack_context_relative_policy_v1 as relative
import stack_context_full_policy_v1 as full
from stack_context_played_bank_v1 import PlayedBank
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from sampled_physical_deals_v1 import PhysicalDeals
from river_posterior64_v1 import posterior as river_reference
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-teacher-conditioning-check-v1'
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
MODELS = Path('S:/GTOpen-research/stack-context-full-control-v1')
EVALUATION = Path('S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1')


def read(path):return json.loads(path.read_bytes())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def save(path, value):
    with path.open('xb') as stream:stream.write(encoded(value));stream.flush();os.fsync(stream.fileno())
def guard():
    if not production_available() or psutil.virtual_memory().available < 28_000_000_000:
        raise ValueError('Yield to production or memory pressure')


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    attempt, result, failure = (OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure'))
    assert not any(p.exists() for p in (attempt, result, failure));guard()
    native_path = OUT/'river-posterior64-native-control-v1-result.json';native = read(native_path)
    model_path = OUT/'stack-context-full-control-v1-result.json';model_proof = read(model_path)
    model_reg_path = OUT/'stack-context-full-control-v1-registration.json';model_reg = read(model_reg_path)
    eval_path = OUT/'stack-context-evaluation-integration-check-v1-result.json';eval_proof = read(eval_path)
    path_check = OUT/'stack-context-teacher-path-check-v2-result.json';path_proof = read(path_check)
    assert all(p['complete'] and p['passed'] for p in (native, model_proof, eval_proof, path_proof))
    for path, identity in path_proof['inputs'].items():assert sha(path) == identity
    paths = {Path(__file__).resolve(), Path(condition.__file__).resolve(), native_path, model_path, model_reg_path, eval_path, path_check,
        OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md'}
    native_case = native['cases'][0]
    history_path = OUT/'river-posterior64-native-control-v1'/native_case['case']/'new/history-export.json'
    assert sha(history_path) == native_case['artifacts'][str(Path('new/history-export.json'))];paths.add(history_path)
    entries = []
    for depth in (20, 40, 60, 100, 150, 200, 400):
        context, public = GEOMETRY/'fixtures'/f'stack-{depth}-context.json', GEOMETRY/f'stack-{depth}-public.json'
        for path in (context, public):assert sha(path) == model_reg['inputs'][str(path)];paths.add(path)
        entries.append(dict(name=f'{depth}bb', split='heldout' if depth in (60, 150) else 'fit',
            context_source=context.read_text(), public_document=read(public)))
    for width in (362, 387):
        path = MODELS/f'{width}-fixture.json';assert sha(path) == model_proof['artifacts'][str(path)];paths.add(path)
    for depth in (20, 60):
        for name in ('queries.json', 'profiles.json'):
            path = EVALUATION/f'{depth}-cached'/name;assert sha(path) == eval_proof['artifacts'][str(path)];paths.add(path)
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix == '.py':paths.add(Path(path))
    inputs = {str(path):sha(path) for path in paths}
    save(attempt, dict(inputs=inputs, qualification_only=True, retained_native_evidence=True,
        reused_two_model_fixtures=True, synthetic_reduction_values=True, fitting=False, native_execution=False,
        scientific_samples=0, qualification_chance_plans_only=True, gpu=False, cpu_threads=2, cpu_priority='below-normal'))
    began = time.monotonic();negative = [];records = [];river_records = []
    def reject(label, fn):
        try:fn()
        except (ValueError, TypeError, KeyError):negative.append(label)
        else:raise AssertionError('Accepted '+label)
    def rehash(document):
        result = copy.deepcopy(document);result.pop('sha256');result['sha256'] = hashlib.sha256(encoded(result)).hexdigest();return result
    try:
        numpy_before = np.random.get_state();torch_before = torch.get_rng_state().clone()
        fixtures = {}
        for width, registry_type, api in ((362, Registry, baseline), (387, RelativeRegistry, relative)):
            fixture = read(MODELS/f'{width}-fixture.json');registry = registry_type(entries)
            assert registry.manifest == fixture['registry'];model = fixture['model'];initial = copy.deepcopy(model)
            initial['generation'] = 0;initial['shared'] = api.initial(registry)
            for key, state in initial['local_states'].items():
                cfg = dict(fixture['resources'][key]['root_config']);cfg.pop('chance')
                state['board_root_state'] = BoardRootRegrets(**cfg).document()
                state['exact_btn_state'] = ExactBtnRegrets(key, fixture['resources'][key]['entry_mass']).document()
            full.validate(initial, registry, fixture['resources'])
            fixtures[width] = dict(documents=[initial, model], registry=registry, resources=fixture['resources'])
        sampler_checks = 0;future_domains = [];saved_example = None
        for depth in (20, 60):
            query = read(EVALUATION/f'{depth}-cached/queries.json');geometry = Binding(query)
            deal = json.loads(query['batch_source'])['deals'][0];key = hashlib.sha256(query['context_source'].encode()).hexdigest()
            ledger = read(GEOMETRY/f'stack-{depth}-public.json');public = ledger['public_states']
            old_lookup = {(r['hi'], r['lo']):i for i, r in enumerate(query['observations'])}
            transport = read(EVALUATION/f'{depth}-cached/profiles.json')
            old_probabilities = {width:np.asarray([r['probabilities'] for r in transport['profiles'][i]['policies']], dtype=float)
                for width, i in ((362, 0), (387, 3))}
            banks = {}
            for width in (362, 387):
                fixture = fixtures[width];weights = [1, 2] if width == 362 else [2, 1]
                banks[width] = PlayedBank(**fixture, context_sha256=key, weights_by_player=[weights, weights],
                    completed_cycles=2, device='cpu', guard=guard)
            # Exact entry tables must reproduce the legacy sampling convention.
            reference_entry = PhysicalDeals(query['context_source'], mode='full_deck', seed=0)
            current_entry = condition.entry_weights(query['context_source'])
            for actor in (0, 1):assert np.array_equal(np.asarray(list(current_entry[actor].values())), reference_entry.weights[actor])
            for phase in range(4):
                for actor in (0, 1):
                    guard();hi = next(r['hi'] for r in public if r['phase'] == phase and r['actor'] == actor
                        and any(a['kind'] == 'fold' for a in r['actions']))
                    history = condition.history_queries(geometry, target_hi=hi, actor=actor,
                        hand=deal[2*actor:2*actor+2], board=deal[4:4+(0, 3, 4, 5)[phase]])
                    assert len(history['hypotheses']) == (1225, 1081, 1035, 990)[phase]
                    rows = history['queries']['observations'];binding = Binding(history['queries'])
                    assert all(r['phase'] <= phase and set(r) == {'hi', 'lo', 'actor', 'phase', 'n', 'active_features', 'own_history'} for r in rows)
                    assert not any(k in json.loads(history['queries']['batch_source']) for k in ('opponent', 'future', 'deals'))
                    overlap = [(i, old_lookup[(r['hi'], r['lo'])]) for i, r in enumerate(rows) if (r['hi'], r['lo']) in old_lookup]
                    assert overlap
                    for width in (362, 387):
                        guard();p, support = banks[width].average(history['queries'], guard=guard)
                        err = float(max(np.max(abs(p[i]-old_probabilities[width][j])) for i, j in overlap));assert err < 1e-10
                        post = condition.posterior(history, binding.freeze(p));pairs, probability = condition.validate_posterior(post)
                        stream = condition.ConditionalSampler(post, seed=20260930);start = stream.checkpoint();plan = stream.sample(32)
                        split = condition.ConditionalSampler(post, seed=20260930);first = split.sample(11)
                        state = json.loads(encoded(split.checkpoint()));rest = condition.ConditionalSampler.restore(state, post).sample(21)
                        assert plan['deals'] == first['deals']+rest['deals'] and plan['opponent_pair_indices'] == first['opponent_pair_indices']+rest['opponent_pair_indices']
                        condition.audit_plan(post, plan, start)
                        values = np.asarray([[((index % 17)-8)*.25+a*.15 for a in range(post['target']['n'])]
                            for index in plan['opponent_pair_indices']])
                        reduced = condition.sampled_advantage(post, plan, values, start_state=start)
                        assert np.max(abs(reduced['action_values']-values.mean(0))) < 1e-12
                        assert abs(float(np.asarray(post['original_sigma']) @ reduced['advantage'])) < 1e-12
                        for pair in (pairs[0], pairs[-1]):
                            domain = condition.future_domain(post['target']['hand'], pair, post['target']['board'], phase)
                            assert domain['distinct_runouts'] == (34246080, 1980, 44, 1)[phase]
                            assert len(domain['remaining']) == (48, 45, 44, 43)[phase]
                            future_domains.append(dict(depth=depth, width=width, phase=phase, remaining=len(domain['remaining']), runouts=domain['distinct_runouts']))
                        sampler_checks += 1
                        records.append(dict(depth=depth, width=width, actor=actor, phase=phase,
                            hidden_pairs=len(pairs), visible_rows=len(rows), native_overlap_rows=len(overlap), maximum_fixture_policy_error=err,
                            posterior_sha256=post['sha256'], opponent_mass=post['opponent_mass'], own_history_likelihood=post['own_history_likelihood'],
                            teacher_state_supported=post['teacher_state_supported']))
                        if saved_example is None and phase == 3:saved_example = (history, binding.freeze(p), post)
            print(json.dumps(dict(stage='qualification-depth-complete', depth=depth, records=len(records))), flush=True)

        # Independently retained native two-stage river paths, with a synthetic
        # hand-dependent teacher table, must give exactly the old posterior.
        native_history = read(history_path);native_geometry = Binding(native_history['queries'])
        native_rows = native_history['queries']['observations'];native_lookup = {(r['hi'], r['lo']):i for i, r in enumerate(native_rows)}
        p = np.zeros((len(native_rows), 4))
        for i, row in enumerate(native_rows):
            w = np.asarray([1+((int(row['lo'])+3*a+5*row['phase']) % 13) for a in range(row['n'])], dtype=float)
            p[i, :row['n']] = w/w.sum()
        actual_paths = 0
        for doc in native_history['targets']:
            t = doc['target'];history = condition.history_queries(native_geometry, target_hi=t['hi'], actor=t['actor'],
                hand=t['cards'][:2], board=t['cards'][2:])
            mapping = [native_lookup[(r['hi'], r['lo'])] for r in history['queries']['observations']]
            for row, index in zip(history['queries']['observations'], mapping):
                converted = copy.deepcopy(row);converted['own_history'] = [[mapping[i], a, n] for i, a, n in converted['own_history']]
                assert converted == native_rows[index]
            for actual, old in zip(history['hypotheses'], doc['pairs']):
                assert actual['cards'] == old['cards'] and [[mapping[i], a, n] for i, a, n in actual['path']] == old['path'];actual_paths += 1
            post = condition.posterior(history, Binding(history['queries']).freeze(p[mapping]))
            reference, mass, own = river_reference(doc, native_rows, p, condition.entry_weights(native_history['context_source']))
            err = float(np.max(abs(reference-np.asarray(post['probabilities']))))
            assert err < 1e-14 and abs(mass-post['opponent_mass']) < 1e-12 and abs(own-post['own_history_likelihood']) < 1e-12
            river_records.append(dict(hidden_pairs=len(reference), native_rows=len(mapping), maximum_posterior_error=err, exact_opponent_mass=True, exact_own_likelihood=True))
        assert actual_paths == 1980

        history, frozen, post = saved_example
        stream = condition.ConditionalSampler(post, seed=20260930);start = stream.checkpoint();plan = stream.sample(512)
        assert len(set(plan['opponent_pair_indices'])) < 512
        values = np.asarray([[((index % 17)-8)*.25+a*.15 for a in range(post['target']['n'])] for index in plan['opponent_pair_indices']])
        reduced = condition.sampled_advantage(post, plan, values, start_state=start)
        assert np.max(abs(reduced['action_values']-values.mean(0))) < 1e-12
        double = np.average(values, axis=0, weights=np.asarray(post['probabilities'])[plan['opponent_pair_indices']])
        double_error = float(np.max(abs(double-reduced['action_values'])));assert double_error > 1e-6
        # Exhaustively close the small chance domains; for preflop verify all
        # 17,296 physical flops have45*44 equally weighted ordered descendants.
        target = post['target'];pair = condition.hypotheses(target['hand'], [], 0)[0]
        pre = condition.future_domain(target['hand'], pair, [], 0);flops = list(itertools.combinations(pre['remaining'], 3))
        assert len(flops) == 17296 and len(flops)*45*44 == pre['distinct_runouts']
        flop = list(flops[0]);d = condition.future_domain(target['hand'], pair, flop, 1)
        ordered = list(itertools.permutations(d['remaining'], 2));assert len(ordered) == len(set(ordered)) == 1980
        turn = [*flop, ordered[0][0]];d2 = condition.future_domain(target['hand'], pair, turn, 2)
        assert len(set(d2['remaining'])) == 44 and ordered[0][1] in d2['remaining']
        assert condition.future_domain(target['hand'], pair, [*turn, ordered[0][1]], 3)['distinct_runouts'] == 1
        assert pre['distinct_runouts'] == __import__('math').comb(48, 5)*20

        # Corruptions must not become valid targets, posterior laws or restarts.
        damaged = copy.deepcopy(history);damaged['hypotheses'].pop()
        reject('missing hidden hypothesis', lambda:condition.posterior(damaged, frozen))
        damaged = copy.deepcopy(history);damaged['hypotheses'].reverse()
        reject('reordered hidden domain', lambda:condition.posterior(damaged, frozen))
        damaged = copy.deepcopy(history);damaged['hypotheses'][0]['path'][0][1] ^= 1
        reject('changed chronological action', lambda:condition.posterior(damaged, frozen))
        damaged = copy.deepcopy(history);damaged['target']['query_index'] += 1
        reject('hidden-dependent target index', lambda:condition.posterior(damaged, frozen))
        damaged = copy.deepcopy(history);damaged['queries']['context_source'] += ' '
        reject('different context binding', lambda:condition.posterior(damaged, frozen))
        damaged = copy.deepcopy(post);damaged['probabilities'][0] += .01
        reject('posterior identity substitution', lambda:condition.validate_posterior(damaged))
        damaged = copy.deepcopy(post);damaged['probabilities'] = damaged['probabilities'][:-1];damaged = rehash(damaged)
        reject('incomplete posterior vector', lambda:condition.validate_posterior(damaged))
        damaged = copy.deepcopy(post);damaged['probabilities'] = [0.]*len(damaged['probabilities']);damaged = rehash(damaged)
        reject('unsupported posterior', lambda:condition.validate_posterior(damaged))
        damaged = copy.deepcopy(post);damaged['original_sigma'] = [0.]*len(damaged['original_sigma']);damaged = rehash(damaged)
        reject('lost original teacher sigma', lambda:condition.validate_posterior(damaged))
        damaged = copy.deepcopy(post);damaged['target']['phase'] = 0;damaged = rehash(damaged)
        reject('future board as preflop input', lambda:condition.validate_posterior(damaged))
        damaged = copy.deepcopy(post);damaged['entry_rule'] = 'floor every hand';damaged = rehash(damaged)
        reject('invented prior floor', lambda:condition.validate_posterior(damaged))
        damaged = copy.deepcopy(post);damaged['teacher_state_supported'] = not damaged['teacher_state_supported'];damaged = rehash(damaged)
        reject('unsupported teacher state mislabelled', lambda:condition.validate_posterior(damaged))
        damaged = copy.deepcopy(post);damaged['unknown_future_feature'] = True;damaged = rehash(damaged)
        reject('unknown posterior contract', lambda:condition.validate_posterior(damaged))
        reject('negative chance seed', lambda:condition.ConditionalSampler(post, seed=-1))
        reject('boolean chance seed', lambda:condition.ConditionalSampler(post, seed=True))
        reject('negative draw count', lambda:condition.ConditionalSampler(post, seed=0).sample(-1))
        reject('unbounded draw count', lambda:condition.ConditionalSampler(post, seed=0).sample(65537))
        damaged = copy.deepcopy(start);damaged['numpy_version'] = 'wrong'
        reject('changed chance runtime', lambda:condition.ConditionalSampler.restore(damaged, post))
        damaged = copy.deepcopy(start);damaged['posterior_sha256'] = '0'*64
        reject('different restarted posterior', lambda:condition.ConditionalSampler.restore(damaged, post))
        damaged = copy.deepcopy(start);damaged['draws'] = -1
        reject('negative restart counter', lambda:condition.ConditionalSampler.restore(damaged, post))
        damaged = copy.deepcopy(plan);damaged['deals'][0][8] = damaged['deals'][0][0]
        reject('corrupted conditional physical deal', lambda:condition.sampled_advantage(post, damaged, values, start_state=start))
        damaged = copy.deepcopy(plan);damaged['opponent_pair_indices'][0] = (damaged['opponent_pair_indices'][0]+1) % len(post['probabilities'])
        reject('changed hidden chance draw', lambda:condition.sampled_advantage(post, damaged, values, start_state=start))
        damaged = copy.deepcopy(plan);damaged['end_state_sha256'] = '0'*64
        reject('forged chance endpoint', lambda:condition.audit_plan(post, damaged, start))
        reject('missing legal action values', lambda:condition.sampled_advantage(post, plan, values[:, :-1], start_state=start))
        wrong = values.copy();wrong[0, 0] = np.nan
        reject('nonfinite action value', lambda:condition.sampled_advantage(post, plan, wrong, start_state=start))
        wrong = values.copy();wrong[0, 0] = 10000
        reject('outside original chip bounds', lambda:condition.sampled_advantage(post, plan, wrong, start_state=start))
        reject('blocked future hidden pair', lambda:condition.future_domain(target['hand'], target['hand'], target['board'], target['phase']))
        now_numpy = np.random.get_state()
        assert numpy_before[0] == now_numpy[0] and np.array_equal(numpy_before[1], now_numpy[1]) and numpy_before[2:] == now_numpy[2:]
        assert torch.equal(torch_before, torch.get_rng_state())
        for path, identity in inputs.items():assert sha(path) == identity
        guard()
        answer = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            actual_cpu_two_model_fixture_records=records, both_input_widths=True, fit20bb_and_heldout60bb=True,
            native_history_posterior_records=river_records, actual_native_both_player_paths=actual_paths,
            conditional_sampler_restart_checks=sampler_checks, future_domains=future_domains,
            physical_preflop_flops_checked=17296, ordered_flop_runouts_checked=1980, turn_runouts_checked=44,
            retained_draw_multiplicity=True, incorrect_double_weighting_error=double_error,
            chance_plan_replay_authenticated=True, global_numpy_torch_rng_preserved=True,
            negative_cases=negative, qualification_only=True, synthetic_action_values=True,
            scientific_samples=0, fits=0, native_calls=0, gpu=False, production_modified=False,
            actual_fixed64_teacher_available=False, native_integrated_targets_complete=False,
            actual_diagnostic_registered=False, actual_diagnostic_complete=False)
        save(result, answer)
        print(json.dumps(dict(passed=True, seconds=answer['seconds'], fixture_posteriors=len(records),
            native_paths=actual_paths, restart_checks=sampler_checks, negative_cases=len(negative))), flush=True)
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False));raise


if __name__ == '__main__':main()
