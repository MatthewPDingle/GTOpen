"""Same fixed root-deviation protocol with float64 hybrid bank inference.

The preflop tables participate in both action probabilities and own-history
reach. CPU controls use the separate scalar reference averaging path.
"""
import json
from pathlib import Path
import time
import numpy as np
from sampled_physical_root_evaluation_cuda_v1 import ROOT, sha, save, batch_values
from sampled_physical_hybrid_checkpoint_v1 import read_object, model_document, verify_bank, validate_model
from sampled_physical_hybrid_gpu_bank_v2 import HybridCudaBank64 as HybridCudaBank
from sampled_physical_deals_v1 import PhysicalDeals, digest
from sampled_root_deviation_v1 import learn, differences
from sampled_evaluation_intervals_v1 import Plan, PairedEvaluation


from sampled_physical_hybrid_cpu64_v1 import HybridCpuBank64 as HybridCpuBank


def run(registration, folder, guard):
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
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
    verify_bank(objects, checkpoint['completed_iterations'], checkpoint['played_bank'], checkpoint['next_model'], context_source=source)
    played = checkpoint['played_bank']
    bank = HybridCudaBank((model_document(objects, ref, context_source=source) for ref in played),
                    [[1.] * len(played)] * 2, context_source=source, models_per_chunk=8, guard=guard)
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
        reference = registration['cpu_reference_batches'].get(str(offset))
        summary = batch_values(context_path, batch, objects, checkpoint, folder / batch_id, guard, bank, reference)
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
        summary = batch_values(context_path, batch, objects, checkpoint, folder / batch_id, guard, bank)
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
