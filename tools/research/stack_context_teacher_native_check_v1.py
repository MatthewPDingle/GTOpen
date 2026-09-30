"""CPU native replay of forced paths on two retained fixture deals per depth.

No new scientific deal, training or model selection. This verifies transport,
same-teacher action-value mixing and actual chip accounting on fixed boards.
It does not qualify hidden-card/future-board integration or a64-bank teacher.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import hashlib
import json
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
import psutil
from bounded_parallel_evaluation_archive_v2 import production_available
import stack_context_teacher_path_v1 as teacher

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-teacher-native-check-v1'
STORE = OUT/NAME
FIXTURES = Path('S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1')
EXE = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
MAX_BYTES = 24_000_000


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path):return json.loads(path.read_bytes())
def save(path, raw):
    if not isinstance(raw, bytes):raw = teacher.encoded(raw)
    with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
def guard():
    if not production_available() or psutil.virtual_memory().available < 28_000_000_000:
        raise ValueError('Yield to production or memory pressure')
    if STORE.exists() and sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) >= MAX_BYTES:
        raise ValueError('Qualification storage bound exceeded')


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    attempt, result, failure = (OUT/(NAME+suffix+'.json') for suffix in ('-attempt', '-result', '-failure'))
    assert not any(p.exists() for p in (attempt, result, failure, STORE));guard()
    path_check = OUT/'stack-context-teacher-path-check-v2-result.json';checked = read(path_check)
    assert checked['passed'] and checked['complete']
    for path, identity in checked['inputs'].items():assert sha(path) == identity
    native_check = OUT/'stack-context-evaluation-integration-check-v1-result.json';proof = read(native_check)
    geometry_registration = OUT/'stack-context-full-control-v1-registration.json'
    geometry = read(geometry_registration)
    assert proof['passed'] and proof['complete'] and sha(EXE) == proof['inputs'][str(EXE)]
    paths = {Path(__file__).resolve(), Path(teacher.__file__).resolve(), path_check, native_check, geometry_registration, EXE,
        ROOT/'crates/solver/examples/hu_sampled_profile_allin_evaluation_v1.rs',
        OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md'}
    for depth in (20, 60):
        for name in ('queries.json', 'profiles.json', 'conditional-batch.json', 'native.json'):
            path = FIXTURES/f'{depth}-cached'/name
            assert sha(path) == proof['artifacts'][str(path)];paths.add(path)
        path = Path(f'S:/GTOpen-research/stack-geometry-control-v1/stack-{depth}-public.json')
        assert sha(path) == geometry['inputs'][str(path)];paths.add(path)
    inputs = {str(path):sha(path) for path in paths}
    save(attempt, dict(inputs=inputs, qualification_only=True, cpu_priority='below-normal', cpu_workers=1,
        retained_native_fixture_only=True, new_scientific_deals=0, fitting=False, gpu=False,
        native_evaluator_readonly=True, main_scientific_inputs_modified=False))
    STORE.mkdir();began = time.monotonic();records = [];calls = 0
    try:
        for depth in (20, 60):
            guard();folder = STORE/str(depth);folder.mkdir()
            query = read(FIXTURES/f'{depth}-cached/queries.json');binding = teacher.Binding(query)
            context = json.loads(query['context_source'])
            conditional_raw = (FIXTURES/f'{depth}-cached/conditional-batch.json').read_bytes()
            conditional = json.loads(conditional_raw);raw = json.loads(query['batch_source'])
            assert conditional['format'] == 3 and raw['format'] == 2
            assert all(conditional[k] == v for k, v in raw.items() if k != 'format')
            assert len(raw['deals']) == 32 and len(set(map(tuple, raw['deals']))) == 2
            deal = raw['deals'][0];transport = read(FIXTURES/f'{depth}-cached/profiles.json')
            assert transport['context_source'] == query['context_source'] and transport['batch_source'] == conditional_raw.decode()
            old_rows = transport['profiles'][0]['policies']
            assert [(r['hi'], r['lo'], r['actor'], r['n']) for r in old_rows] == [
                (r['hi'], r['lo'], r['actor'], r['n']) for r in query['observations']]
            p = np.asarray([r['probabilities'] for r in old_rows], dtype=np.float64);frozen = binding.freeze(p)
            ledger = read(Path(f'S:/GTOpen-research/stack-geometry-control-v1/stack-{depth}-public.json'))
            assert ledger['context_source'] == query['context_source']
            public = {r['hi']:r for r in ledger['public_states']};profiles = [];targets = []
            def append(name, probability):
                rows = [dict(hi=o['hi'], lo=o['lo'], actor=o['actor'], n=o['n'], probabilities=row.tolist())
                    for o, row in zip(query['observations'], probability)]
                profiles.append(dict(name=name, policies=rows))
            append('unforced-original-fixture', frozen.p)
            for phase in range(4):
                for actor in (0, 1):
                    hi = next(hi for hi, row in public.items() if row['phase'] == phase and row['actor'] == actor
                        and any(a['kind'] == 'fold' for a in row['actions']))
                    index, path = binding.trace(deal, hi);row = public[hi]
                    name = f'phase{phase}-actor{actor}'
                    forced = frozen.intervene(deal, hi, 0)['probabilities'].copy();forced[index] = frozen.p[index]
                    append(name+'-original-target-mix', forced)
                    for action in range(len(row['actions'])):
                        append(name+'-action'+str(action), frozen.intervene(deal, hi, action)['probabilities'])
                    targets.append(dict(name=name, hi=hi, actor=actor, phase=phase, index=index,
                        path=path, n=len(row['actions']), sigma=frozen.p[index, :len(row['actions'])].tolist(),
                        fold_action=next(i for i, a in enumerate(row['actions']) if a['kind'] == 'fold'),
                        own_invested=row['invested'][actor]))
            context_path, batch_path = folder/'context.json', folder/'conditional-batch.json'
            save(context_path, query['context_source'].encode());save(batch_path, conditional_raw)
            answers = {};maximum_cashflow = 0.;maximum_conservation = 0.
            for start in range(0, len(profiles), 32):
                guard();profile_path = folder/f'profiles-{start}.json';output = folder/f'native-{start}.json'
                save(profile_path, dict(format=1, context_source=query['context_source'],
                    batch_source=conditional_raw.decode(), profiles=profiles[start:start+32]))
                done = subprocess.run([str(EXE), str(context_path), str(batch_path), str(profile_path), str(output)],
                    capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
                save(folder/f'process-{start}.json', dict(code=done.returncode, stdout=done.stdout, stderr=done.stderr))
                calls += 1;assert done.returncode == 0 and output.exists(), done.stderr
                native = read(output);assert native['terminal_estimator'] == 'conditional-preflop-allin-v1'
                maximum_cashflow = max(maximum_cashflow, native['maximum_forward_cashflow_error'])
                maximum_conservation = max(maximum_conservation, native['maximum_conservation_error'])
                assert [r['name'] for r in native['profiles']] == [r['name'] for r in profiles[start:start+32]]
                for profile in native['profiles']:
                    assert profile['name'] not in answers and len(profile['deals']) == 32
                    for i, r in enumerate(profile['deals']):
                        assert r['deal_index'] == i and abs(r['terminal_mass']-1) < 1e-12
                        assert abs(sum(r['values'])+r['expected_rake']-context['dead_money']) < 1e-10
                    answers[profile['name']] = profile['deals']
            old = read(FIXTURES/f'{depth}-cached/native.json')['profiles'][0]['deals']
            assert np.max(abs(np.asarray([r['values'] for r in old])-
                np.asarray([r['values'] for r in answers['unforced-original-fixture']]))) < 1e-12
            cases = []
            for target in targets:
                name, actor = target['name'], target['actor']
                q = [answers[name+'-action'+str(a)][0]['values'][actor] for a in range(target['n'])]
                mixed = answers[name+'-original-target-mix'][0]['values'][actor]
                got = teacher.advantage(q, target['sigma'], starting_stack=depth)
                mixture_error = abs(got['value']-mixed)
                fold_error = abs(q[target['fold_action']]+target['own_invested'])
                assert mixture_error < 1e-10 and fold_error < 1e-10
                assert abs(float(np.asarray(target['sigma']) @ got['advantage'])) < 1e-12
                cases.append(dict(target, action_values=q, original_target_mix_value=mixed,
                    normalized_advantage=got['advantage'].tolist(), mixture_error=mixture_error, fold_cashflow_error=fold_error))
            assert maximum_cashflow < 1e-10 and maximum_conservation < 1e-10
            records.append(dict(depth=depth, targets=cases, native_profile_count=len(profiles), retained_deals=32,
                distinct_retained_deals=2, original_fixture_value_replayed=True,
                maximum_forward_cashflow_error=maximum_cashflow, maximum_conservation_error=maximum_conservation,
                frozen_teacher_sha256=frozen.identity))
        guard()
        for path, identity in inputs.items():assert sha(path) == identity
        answer = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}, native_calls=calls,
            records=records, cpu_only=True, qualification_only=True, new_scientific_deals=0, fits=0, gpu=False,
            production_modified=False, full_native_intervention_payoff_run_qualified=True,
            fixed_board_conditional_labels_only=True, inherited_preflop_allin_terms_exact=True,
            conditional_hidden_card_future_board_integration_qualified=False, actual_fixed64_teacher_available=False,
            actual_diagnostic_complete=False, scientific_accuracy_evidence=False)
        save(result, answer)
        print(json.dumps(dict(passed=True, seconds=answer['seconds'], native_calls=calls,
            targets=sum(len(r['targets']) for r in records), scientific_work=False)), flush=True)
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False));raise


if __name__ == '__main__':main()
