"""Read-only replay of a completed prefix of physical training artifacts.

Replays chance/action RNGs and reservoir insertion, not neural optimizer steps.
This helper alone does not classify a terminal stop or admit an evaluation.
"""
import json
from pathlib import Path
import numpy as np

from sampled_physical_checkpoint_v1 import read_object, model_document, restore_checkpoint
from sampled_physical_deals_v1 import PhysicalDeals, digest
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest
from sampled_physical_root_evaluation_v1 import ROOT, sha

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-pilot-gpu-v1'


def audit(completed, guard):
    assert type(completed) is int and completed > 0
    regpath = OUT / (PREFIX + '-registration.json')
    reg = json.loads(regpath.read_text())
    cfg = reg['config']
    assert completed <= cfg['max_iterations']
    for path, expected in reg['inputs'].items():
        assert sha(ROOT / path) == expected, path
    store = Path(reg['store']); objects = store / 'checkpoint-objects'
    context = (OUT / 'bb-context-candidate.json').read_text()
    sampler = PhysicalDeals(context, mode='full_deck', seed=cfg['sampler_seed'])
    action_rng = np.random.Generator(np.random.PCG64(cfg['action_seed']))
    reservoirs = [PhysicalReservoir(cfg['reservoir_capacity'], p, cfg['reservoir_seeds'][p], context)
                  for p in (0, 1)]
    initial_ref = json.loads((store / 'checkpoint-0000.json').read_text())
    previous = json.loads(read_object(objects, initial_ref))
    assert previous['completed_iterations'] == 0 and previous['played_bank'] == []
    assert previous['sampler'] == sampler.checkpoint()
    assert previous['action_rng'] == action_rng.bit_generator.state
    assert model_document(objects, previous['next_model'])['generation'] == 0
    expected_config = previous['config']
    for name, value in cfg.items(): assert expected_config[name] == value, name
    rows = []; verified_traversals = 0
    for iteration in range(1, completed + 1):
        guard()
        folder = store / f'iteration-{iteration:04d}'
        metricpath = folder / 'metrics.json'
        metric = json.loads(metricpath.read_text())
        assert metric['iteration'] == iteration and metric['deals'] == cfg['deals_per_iteration']
        for name, expected in metric['artifacts'].items():
            assert name in ('batch.json', 'queries.json', 'policies.json', 'updates.json')
            assert sha(folder / name) == expected, str(folder / name)
        assert set(metric['artifacts']) == {'batch.json', 'queries.json', 'policies.json', 'updates.json'}
        batch = json.loads((folder / 'batch.json').read_text())
        assert batch['batch_id'] == f'{PREFIX}-iteration-{iteration}'
        assert batch['seed'] == int(action_rng.integers(0, 2**63))
        assert batch['deals'] == sampler.sample(cfg['deals_per_iteration'])['deals']
        queries = json.loads((folder / 'queries.json').read_text())
        assert queries['context_source'] == context
        assert queries['batch_source'] == (folder / 'batch.json').read_text()
        assert len(queries['observations']) == metric['observations']
        updates = json.loads((folder / 'updates.json').read_text())
        assert updates['verified_traversals'] == 2 * cfg['deals_per_iteration']
        assert updates['maximum_reference_error'] == 0
        counts = ingest(queries, updates, reservoirs, iteration)
        assert counts == metric['advantage_records']
        assert [r.summary() for r in reservoirs] == metric['reservoirs']
        verified_traversals += updates['verified_traversals']
        reference = json.loads((store / f'checkpoint-{iteration:04d}.json').read_text())
        assert reference == metric['checkpoint']
        checkpoint = json.loads(read_object(objects, reference))
        assert checkpoint['completed_iterations'] == iteration
        assert checkpoint['context_sha256'] == digest(context)
        assert checkpoint['config'] == expected_config
        assert checkpoint['sampler'] == sampler.checkpoint()
        assert checkpoint['action_rng'] == action_rng.bit_generator.state
        assert checkpoint['played_bank'] == [*previous['played_bank'], previous['next_model']]
        current = model_document(objects, checkpoint['next_model'])
        assert current['generation'] == iteration
        assert len(metric['fits']) == 2
        for p, fit in enumerate(metric['fits']):
            assert fit['player'] == p and fit['device'] == 'cuda'
            assert fit['steps'] == cfg['fit_steps'] and fit['chunk_size'] == cfg['chunk_size']
            assert fit['seed'] == cfg['fit_seed_base'] + iteration * 200003 + p
            assert fit['learning_rate'] == cfg['learning_rate']
            assert fit['retained_examples'] == reservoirs[p].size
            assert current['advantage_scales'][p] == fit['advantage_scale']
        # Each immutable reservoir object must match its checkpoint hash. The
        # final contents are additionally compared with the full replay below.
        for reservoir_ref in checkpoint['reservoirs']: read_object(objects, reservoir_ref)
        rows.append(dict(iteration=iteration, metrics_sha256=sha(metricpath),
                         checkpoint=reference, observations=metric['observations'],
                         advantage_records=counts, seconds=metric['seconds']))
        previous = checkpoint
    guard()
    restored = restore_checkpoint(objects, reference, context_source=context, config=expected_config)
    for replayed, saved in zip(reservoirs, restored['reservoirs']):
        assert replayed.summary() == saved.summary()
        assert replayed.rng.bit_generator.state == saved.rng.bit_generator.state
        for name in ('keys', 'active', 'arity', 'values', 'iterations'):
            assert np.array_equal(getattr(replayed, name)[:replayed.size],
                                  getattr(saved, name)[:saved.size]), name
    assert restored['sampler'].checkpoint() == sampler.checkpoint()
    assert restored['action_rng'].bit_generator.state == action_rng.bit_generator.state
    for path, expected in reg['inputs'].items(): assert sha(ROOT / path) == expected, path
    return dict(completed_iterations=completed, checkpoint=reference,
                source_registration_sha256=sha(regpath), registered_inputs_verified=len(reg['inputs']),
                fresh_deals_replayed=sampler.draws, verified_traversals=verified_traversals,
                retained_records=[r.size for r in reservoirs], final_reservoir_arrays_and_rng_exact=True,
                played_generations=list(range(completed)), unused_next_generation=completed,
                completed_prefix_verified=True, steps=rows,
                scope='Replayed every sampled deal, action seed and reservoir update; checked native verification evidence and model-bank progression. Neural optimizer steps and GPU forward inference were not rerun. Stop classification and evaluation admission are separate.',
                physical_poker_convergence_qualified=False, production_modified=False)
