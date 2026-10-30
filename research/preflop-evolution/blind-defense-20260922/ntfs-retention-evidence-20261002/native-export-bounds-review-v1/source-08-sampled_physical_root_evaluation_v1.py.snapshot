"""Fresh-deal root deviations against a frozen played physical-policy bank.

This is a restricted deviation test, not a physical best-response certificate.
The test stream is not drawn until the class responder has been published.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import time

import numpy as np

from sampled_batch_protocol_v2 import policy_document
from sampled_physical_bank_v1 import average
from sampled_physical_checkpoint_v1 import read_object, model_document, verify_bank
from sampled_physical_deals_v1 import PhysicalDeals, digest
from sampled_root_deviation_v1 import learn, differences
from sampled_evaluation_intervals_v1 import Plan, PairedEvaluation

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, document):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(document, separators=(',', ':'), allow_nan=False) + '\n')


def hand_class(cards):
    a, b = cards
    lo, hi = sorted((a // 4, b // 4))
    return hi * 13 + lo if a % 4 == b % 4 or hi == lo else lo * 13 + hi


def batch_values(context_path, batch, objects, checkpoint, folder, guard):
    """Integrate later actions, sharing each complete deal across root choices."""
    folder.mkdir(exist_ok=False)
    batch_path = folder / 'batch.json'
    query_path = folder / 'queries.json'
    profile_path = folder / 'profiles.json'
    native_path = folder / 'native.json'
    save(batch_path, batch)

    def invoke(name, arguments):
        guard()
        completed = subprocess.run(
            [str(ROOT / 'target/release/examples' / (name + '.exe')), *map(str, arguments)],
            cwd=ROOT, timeout=120, capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW)
        if completed.returncode:
            raise RuntimeError(completed.stderr[-2000:])
        guard()

    invoke('hu_sampled_bank_bridge', ['queries', context_path, batch_path, '-', query_path])
    queries = json.loads(query_path.read_text())
    assert queries['context_source'] == context_path.read_text()
    assert queries['batch_source'] == batch_path.read_text()
    played = checkpoint['played_bank']

    def pairs():
        for reference in played:
            yield model_document(objects, reference)['networks']

    policy, support = average(queries, pairs(), [[1.] * len(played)] * 2,
                              device='cpu', guard=guard)
    roots = [i for i, o in enumerate(queries['observations'])
             if o['phase'] == 0 and int(o['hi']) == 1]
    assert roots and all(queries['observations'][i]['actor'] == 0
                         and queries['observations'][i]['n'] == 4 for i in roots)
    byclass = {}
    for i in roots:
        key = int(queries['observations'][i]['lo'])
        c = hand_class([key & 63, (key >> 6) & 63])
        if c in byclass:
            assert np.max(np.abs(byclass[c] - policy[i])) < 1e-12
        byclass[c] = policy[i]
    profiles = [dict(name='baseline', policies=policy_document(queries, policy)['policies'])]
    for action in range(4):
        changed = policy.copy()
        changed[roots] = 0.
        changed[roots, action] = 1.
        profiles.append(dict(name=f'action-{action}', policies=policy_document(queries, changed)['policies']))
    save(profile_path, dict(format=1, context_source=queries['context_source'],
                            batch_source=queries['batch_source'], profiles=profiles))
    invoke('hu_sampled_profile_evaluation', [context_path, batch_path, profile_path, native_path])
    native = json.loads(native_path.read_text())
    values = {p['name']: np.array([d['values'][0] for d in p['deals']]) for p in native['profiles']}
    action_values = np.stack([values[f'action-{a}'] for a in range(4)], axis=1)
    baseline = values['baseline']
    classes = [hand_class(d[:2]) for d in batch['deals']]
    mixes = np.array([byclass[c] for c in classes])
    error = float(np.max(np.abs((mixes * action_values).sum(axis=1) - baseline)))
    context = json.loads(queries['context_source'])
    assert error < 1e-10
    assert np.max(np.abs(action_values[:, 0] + context['nodes'][0]['invested'][0])) < 1e-12
    # Conservative physical-chip bounds derived from stack/dead money, not
    # observed sample extrema. Ante-free equal stacks are required below.
    stack, dead = context['config']['stack'], context['dead_money']
    assert np.all(action_values >= -stack - 1e-10)
    assert np.all(action_values <= stack + dead + 1e-10)
    summary = dict(classes=classes, action_values=action_values.tolist(),
                   baseline_values=baseline.tolist(), root_probabilities=mixes.tolist(),
                   maximum_root_mixture_error=error,
                   zero_own_reach_observations=int(np.count_nonzero(support == 0)),
                   maximum_forward_cashflow_error=native['maximum_forward_cashflow_error'],
                   artifacts={p.name: sha(p) for p in (batch_path, query_path, profile_path, native_path)})
    save(folder / 'summary.json', summary)
    return summary


def run(registration, folder, guard):
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    started = time.monotonic()
    folder = Path(folder)
    folder.mkdir(exist_ok=False)
    context_path = Path(registration['context'])
    source = context_path.read_text()
    context = json.loads(source)
    assert context['nodes'][0]['actor'] == 0 and context['nodes'][0]['kind'] == 0
    assert [a['kind'] for a in context['nodes'][0]['actions']] == ['fold', 'call', 'raise', 'jam']
    assert context['config']['ante'] == 0 and context['dead_money'] >= 0
    objects = Path(registration['objects'])
    checkpoint = json.loads(read_object(objects, registration['checkpoint']))
    assert checkpoint['context_sha256'] == digest(source) and checkpoint['completed_iterations'] > 0
    verify_bank(objects, checkpoint['completed_iterations'], checkpoint['played_bank'], checkpoint['next_model'])
    config = registration['config']
    assert config['train_seed'] != config['test_seed']
    assert all(type(config[k]) is int and config[k] > 0 for k in
               ('training_deals', 'evaluation_deals', 'batch_size', 'minimum_training_deals'))
    assert config['training_deals'] % config['batch_size'] == 0
    assert config['evaluation_deals'] % config['batch_size'] == 0
    train = PhysicalDeals(source, mode='full_deck', seed=config['train_seed'])
    ids, classes, values, baselines = [], [], [], []
    batches = []
    for offset in range(0, config['training_deals'], config['batch_size']):
        guard()
        batch_id = f"{registration['id']}-train-{offset}"
        batch = dict(format=2, batch_id=batch_id, query_limit=100000, seed=0,
                     deals=train.sample(config['batch_size'])['deals'])
        summary = batch_values(context_path, batch, objects, checkpoint, folder / batch_id, guard)
        ids.extend(f'{batch_id}-{i}' for i in range(config['batch_size']))
        classes.extend(summary['classes']); values.extend(summary['action_values'])
        baselines.extend(summary['baseline_values']); batches.append(batch_id)
    response = learn(ids, classes, values, baselines,
                     minimum_training_deals=config['minimum_training_deals'])
    response_path = folder / 'response.json'
    save(response_path, response)
    response_hash = sha(response_path)
    # Only now instantiate/draw the evaluation stream. No test-driven responder
    # selection, checkpoint selection, support threshold or stopping adjustment.
    test = PhysicalDeals(source, mode='full_deck', seed=config['test_seed'])
    width = 2 * context['config']['stack'] + context['dead_money']
    series = ('trained-response', 'always-fold', 'always-call', 'always-raise', 'always-jam')
    plan = Plan(-width, width, series, (config['evaluation_deals'],), alpha=.05)
    estimates = [PairedEvaluation(plan, name) for name in series]
    test_counts = np.zeros(169, dtype=np.int64)
    applied = 0
    for offset in range(0, config['evaluation_deals'], config['batch_size']):
        guard()
        assert sha(response_path) == response_hash
        batch_id = f"{registration['id']}-test-{offset}"
        batch = dict(format=2, batch_id=batch_id, query_limit=100000, seed=0,
                     deals=test.sample(config['batch_size'])['deals'])
        summary = batch_values(context_path, batch, objects, checkpoint, folder / batch_id, guard)
        c = np.array(summary['classes']); a = np.array(summary['action_values'])
        b = np.array(summary['baseline_values'])
        delta = differences(response, [f'{batch_id}-{i}' for i in range(config['batch_size'])], c, a, b)
        matrix = np.column_stack((delta, a - b[:, None]))
        for i, estimator in enumerate(estimates):
            for value in matrix[:, i]: estimator.add_difference(float(value))
        test_counts += np.bincount(c, minlength=169)
        applied += int(np.count_nonzero(np.asarray(response['actions'])[c] >= 0))
        save(folder / batch_id / 'paired.json', dict(series=series, differences=matrix.tolist(),
                                                     response_sha256=response_hash))
        batches.append(batch_id)
    guard()
    assert sha(response_path) == response_hash
    result = dict(terminal=True, registration_id=registration['id'],
                  completed_training_deals=train.draws, completed_evaluation_deals=test.draws,
                  checkpoint=registration['checkpoint'], played_generations=list(range(len(checkpoint['played_bank']))),
                  excluded_unused_generation=checkpoint['next_model']['generation'],
                  response_sha256=response_hash, evaluation_class_counts=test_counts.tolist(),
                  applied_response_deals=applied, fallback_deals=test.draws - applied,
                  intervals={s: e.interval() for s, e in zip(series, estimates)},
                  batch_summary_hashes={b: sha(folder / b / 'summary.json') for b in batches},
                  seconds=time.monotonic() - started, bounds_best_response_above=False,
                  physical_poker_convergence_qualified=False, production_modified=False,
                  scope=registration['scope'])
    save(folder / 'result.json', result)
    return result
