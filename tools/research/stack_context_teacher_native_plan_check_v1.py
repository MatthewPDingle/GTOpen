"""Bounded CPU qualification of conditional plans through native payoff code.

Explicit fixture chance plans and an old two-generation baseline teacher only;
no scientific fitting, final-bank selection or diagnostic accuracy claim.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_context_teacher_native_plan_v1 as adapter
import stack_context_teacher_conditioning_v1 as condition
from stack_context_teacher_path_v1 import Binding, encoded
from stack_context_inputs_v1 import Registry
import stack_context_policy_v1 as baseline
import stack_context_full_policy_v1 as full
from stack_context_played_bank_v1 import PlayedBank
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from sampled_allin_protocol_v3 import AllinCache
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-teacher-native-plan-check-v1'
STORE = OUT/NAME
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
MODELS = Path('S:/GTOpen-research/stack-context-full-control-v1')
EVALUATION = Path('S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1')
EXES = [ROOT/'target/release/examples'/s for s in ('hu_sampled_bank_bridge.exe', 'hu_sampled_profile_allin_evaluation_v1.exe')]
MAX_SECONDS = 600
MAX_BYTES = 256_000_000
DRAWS = 8
REPLICATES = 2


def read(path):return json.loads(Path(path).read_bytes())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def save(path, document):adapter.save(path, document)


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    attempt, result, failure = [OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure')]
    assert not any(p.exists() for p in (attempt, result, failure, STORE))
    began = time.monotonic()
    def guard():
        if (time.monotonic()-began > MAX_SECONDS or not production_available()
                or psutil.virtual_memory().available < 28_000_000_000):
            raise ValueError('Yield to production, memory pressure or qualification time limit')
        if STORE.exists() and sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) >= MAX_BYTES:
            raise ValueError('Qualification artifact bound exceeded')
    guard()
    proof_path = OUT/'stack-context-teacher-conditioning-check-v1-result.json'
    checked = read(proof_path);assert checked['complete'] and checked['passed']
    for p, h in checked['inputs'].items():assert sha(p) == h
    eval_path = OUT/'stack-context-evaluation-integration-check-v1-result.json';native_proof = read(eval_path)
    native_path = OUT/'stack-context-teacher-native-check-v1-result.json';path_proof = read(native_path)
    model_path = OUT/'stack-context-full-control-v1-result.json';model_proof = read(model_path)
    model_reg_path = OUT/'stack-context-full-control-v1-registration.json';model_reg = read(model_reg_path)
    cache_path = OUT/'stack-context-complete-allin-cache-v1-readback.json';cache_proof = read(cache_path)
    assert all(p['complete'] and p['passed'] for p in (native_proof, path_proof, model_proof, cache_proof))
    for p in EXES:assert sha(p) == native_proof['inputs'][str(p)]
    assert sha(EXES[1]) == path_proof['inputs'][str(EXES[1])]
    assert sha(cache_proof['cache_artifact']) == cache_proof['cache_sha256']
    paths = {Path(__file__).resolve(), Path(adapter.__file__).resolve(), proof_path, eval_path, native_path,
        model_path, model_reg_path, cache_path, Path(cache_proof['cache_artifact']), *EXES,
        ROOT/'crates/solver/examples/hu_sampled_profile_allin_evaluation_v1.rs',
        OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md'}
    entries = []
    for d in (20, 40, 60, 100, 150, 200, 400):
        context, public = GEOMETRY/'fixtures'/f'stack-{d}-context.json', GEOMETRY/f'stack-{d}-public.json'
        for p in (context, public):assert sha(p) == model_reg['inputs'][str(p)];paths.add(p)
        entries.append(dict(name=f'{d}bb', split='heldout' if d in (60, 150) else 'fit',
            context_source=context.read_text(), public_document=read(public)))
    fixture_path = MODELS/'362-fixture.json'
    assert sha(fixture_path) == model_proof['artifacts'][str(fixture_path)];paths.add(fixture_path)
    for d in (20, 60):
        p = EVALUATION/f'{d}-cached/queries.json';assert sha(p) == native_proof['artifacts'][str(p)];paths.add(p)
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix == '.py':paths.add(Path(p))
    inputs = {str(p):sha(p) for p in paths}
    save(attempt, dict(inputs=inputs, qualification_only=True, fixture_teacher_generations=[0, 1],
        fixture_teacher_width=362, fixture_generation_weights=[1, 2], scientific_teacher_selected=False,
        phases=[0, 1, 2, 3], actors=[0, 1], depths=[20, 60], draws_per_plan=DRAWS,
        replicates_per_information_state=REPLICATES, qualification_seed_rule='2026093000 + depth*100 + phase*10 + actor + replicate*100000',
        maximum_seconds=MAX_SECONDS, maximum_bytes=MAX_BYTES, native_cpu_only=True, cpu_threads=2,
        cpu_priority='below-normal', fits=0, scientific_samples=0, gpu=False, production_modified=False))
    STORE.mkdir();records = [];negative = []
    try:
        registry = Registry(entries);fixture = read(fixture_path);assert registry.manifest == fixture['registry']
        model = fixture['model'];initial = copy.deepcopy(model)
        initial['generation'] = 0;initial['shared'] = baseline.initial(registry)
        for key, state in initial['local_states'].items():
            cfg = dict(fixture['resources'][key]['root_config']);cfg.pop('chance')
            state['board_root_state'] = BoardRootRegrets(**cfg).document()
            state['exact_btn_state'] = ExactBtnRegrets(key, fixture['resources'][key]['entry_mass']).document()
        full.validate(initial, registry, fixture['resources'])
        cache = AllinCache(cache_proof['cache_artifact'], cache_proof['cache_sha256'])
        assert len(cache.rows) == 93769
        teacher_manifest = dict(scope='implementation-fixture-only', width=362, generations=[0, 1],
            generation_weights_by_player=[[1, 2], [1, 2]], completed_cycles=2,
            fixture_sha256=sha(fixture_path), registry_manifest=registry.manifest,
            model_document_sha256=[hashlib.sha256(encoded(d)).hexdigest() for d in (initial, model)],
            original_own_action_reach=True, actual_fixed64_teacher=False)
        saved = None
        for depth in (20, 60):
            guard();query = read(EVALUATION/f'{depth}-cached/queries.json');geometry = Binding(query)
            deal = json.loads(query['batch_source'])['deals'][0]
            key = hashlib.sha256(query['context_source'].encode()).hexdigest();context = json.loads(query['context_source'])
            bank = PlayedBank(documents=[initial, model], registry=registry, resources=fixture['resources'],
                context_sha256=key, weights_by_player=[[1, 2], [1, 2]], completed_cycles=2,
                device='cpu', guard=guard)
            ledger = read(GEOMETRY/f'stack-{depth}-public.json');public = ledger['public_states']
            for phase in range(4):
                for actor in (0, 1):
                    hi = next(r['hi'] for r in public if r['phase'] == phase and r['actor'] == actor
                        and any(a['kind'] == 'fold' for a in r['actions']))
                    state = next(r for r in public if r['hi'] == hi)
                    history = condition.history_queries(geometry, target_hi=hi, actor=actor,
                        hand=deal[2*actor:2*actor+2], board=deal[4:4+(0, 3, 4, 5)[phase]])
                    hp, _ = bank.average(history['queries'], guard=guard)
                    post = condition.posterior(history, Binding(history['queries']).freeze(hp))
                    outputs = [];seeds = []
                    for replicate in range(REPLICATES):
                        guard();seed = 2026093000+depth*100+phase*10+actor+replicate*100000;seeds.append(seed)
                        stream = condition.ConditionalSampler(post, seed=seed);start = stream.checkpoint();plan = stream.sample(DRAWS)
                        folder = STORE/f'{depth}-phase{phase}-actor{actor}-replicate{replicate}'
                        answer = adapter.evaluate_plan(history=history, posterior=post, plan=plan,
                            start_state=start, teacher=bank, teacher_manifest=teacher_manifest, cache=cache,
                            query_executable=EXES[0], evaluation_executable=EXES[1], folder=folder, guard=guard)
                        q = np.asarray(answer['per_draw_action_values']);sigma = np.asarray(post['original_sigma'])
                        assert abs(sigma @ answer['normalized_advantage']) < 1e-12
                        assert np.max(abs(q.mean(0)-answer['action_values'])) < 1e-12
                        fold = next(i for i, a in enumerate(state['actions']) if a['kind'] == 'fold')
                        assert np.max(abs(q[:, fold]+state['invested'][actor])) < 1e-10
                        # Independent union of individual qualified interventions.
                        queries = read(folder/'queries.json');profiles = read(folder/'profiles.json')['profiles']
                        original, _ = bank.average(queries, guard=guard);frozen = Binding(queries).freeze(original)
                        for a in range(post['target']['n']):
                            union = {};targets = set()
                            for d in plan['deals']:
                                one = frozen.intervene(d, hi, a);targets.add(one['target_index'])
                                for index, selected, _ in one['path']:union[index] = selected
                            assert len(targets) == 1
                            expected = frozen.p.copy()
                            for index, selected in union.items():expected[index] = 0.;expected[index, selected] = 1.
                            target = next(iter(targets));expected[target] = 0.;expected[target, a] = 1.
                            actual = np.asarray([r['probabilities'] for r in profiles[a+1]['policies']])
                            assert np.array_equal(expected, actual)
                        outputs.append(dict(result_sha256=sha(folder/'result.json'), folder=str(folder),
                            draws=DRAWS, action_values=answer['action_values'], advantages=answer['normalized_advantage'],
                            per_action_sample_variance=q.var(0, ddof=1).tolist(),
                            fold_cashflow_error=float(np.max(abs(q[:, fold]+state['invested'][actor]))),
                            mixture_error=answer['mixture_error'], history_policy_error=answer['maximum_original_history_policy_error'],
                            future_rows_preserved=answer['unchanged_future_rows_per_action'], native_calls=answer['native_calls']))
                        if saved is None:saved = (history, post, plan, start, bank, folder, answer, context)
                    delta = (np.asarray(outputs[0]['action_values'])-outputs[1]['action_values'])/depth
                    records.append(dict(depth=depth, actor=actor, phase=phase, hi=hi,
                        qualification_seeds=seeds, posterior_sha256=post['sha256'], targets_supported=True,
                        replicates=outputs, label_difference_in_starting_stack_units=delta.tolist(),
                        descriptive_fixture_noise_only=True, accuracy_evidence=False))
                    print(json.dumps(dict(stage='native-plan-target-qualified', depth=depth, phase=phase,
                        actor=actor, records=len(records))), flush=True)
        history, post, plan, start, bank, folder, answer, context = saved
        first_queries = read(folder/'queries.json');first_probability, _ = bank.average(first_queries, guard=guard)
        first_frozen = Binding(first_queries).freeze(first_probability)
        def reject(label, fn):
            try:fn()
            except (ValueError, TypeError, KeyError):negative.append(label)
            else:raise AssertionError('Accepted '+label)
        common = dict(history=history, posterior=post, plan=plan, start_state=start, teacher=bank,
            teacher_manifest=teacher_manifest, cache=cache, query_executable=EXES[0], evaluation_executable=EXES[1],
            folder=folder, guard=guard)
        reject('existing native attempt', lambda:adapter.evaluate_plan(**common))
        reject('illegal shared target action', lambda:adapter.shared_intervention(first_frozen, plan['deals'], post['target']['hi'], 5))
        native = read(folder/'native.json');names = [r['name'] for r in native['profiles']]
        def corrupt(label, mutate):
            changed = copy.deepcopy(native);mutate(changed)
            reject(label, lambda:adapter.checked_values(changed, names, DRAWS, json.loads(post['context_source'])))
        corrupt('native profile order', lambda d:d['profiles'].reverse())
        corrupt('native estimator', lambda d:d.update(terminal_estimator='unknown'))
        corrupt('native forward cashflow', lambda d:d.update(maximum_forward_cashflow_error=.01))
        corrupt('native terminal mass', lambda d:d['profiles'][0]['deals'][0].update(terminal_mass=.5))
        corrupt('native deal order', lambda d:d['profiles'][0]['deals'][0].update(deal_index=1))
        corrupt('native illegal value', lambda d:d['profiles'][0]['deals'][0].update(values=[float('nan'), 0]))
        corrupt('native conservation', lambda d:d['profiles'][0]['deals'][0].update(expected_rake=100))
        corrupt('native partial draws', lambda d:d['profiles'][0]['deals'].pop())
        for p, h in inputs.items():assert sha(p) == h
        guard()
        artifacts = {str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}
        result_doc = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            artifacts=artifacts, artifact_bytes=sum(Path(p).stat().st_size for p in artifacts),
            records=records, native_calls=sum(r['native_calls'] for t in records for r in t['replicates']),
            conditional_plans=len(records)*REPLICATES, qualification_draws=len(records)*REPLICATES*DRAWS,
            independent_replicates_per_target=REPLICATES, negative_cases=negative,
            all_streets_both_actors=True, depth_geometry20_and60=True, shared_interventions_equal_individual_union=True,
            conditional_posterior_and_future_cards_integrated=True, original_teacher_future_policies_preserved=True,
            original_sigma_baseline_verified=True, exact_preflop_allin_counts_reused=True,
            descriptive_fixture_noise_only=True, scientific_label_noise_budget_registered=False,
            qualification_only=True, scientific_samples=0, fits=0, gpu=False, production_modified=False,
            fixture_teacher_width=362, fixture_teacher_generations=[0, 1], actual_fixed64_teacher_available=False,
            actual_diagnostic_registered=False, actual_diagnostic_complete=False, scientific_accuracy_evidence=False)
        save(result, result_doc)
        print(json.dumps(dict(passed=True, seconds=result_doc['seconds'], targets=len(records),
            native_calls=result_doc['native_calls'], bytes=result_doc['artifact_bytes'])), flush=True)
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False));raise


if __name__ == '__main__':main()
