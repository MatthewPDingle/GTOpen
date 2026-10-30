"""Research-only joint update: integrate root action paths on every sampled physical deal.

This runner changes no production API or active evaluator. Publication boundaries
require both fits and exactly one exact BTN update. Resume only from a completed
checkpoint; partial native batches and partial fits are never resumed.
"""
import copy
import json
import subprocess
import time
from pathlib import Path
import numpy as np
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from exact_initial_training_ingest_v2 import InitialTargets, ingest
from action_integrated_policy_v1 import probabilities
from action_integrated_root_accumulator_v1 import IntegratedRootRegrets
import action_integrated_checkpoint_v1 as checkpoint
import exact_initial_hybrid_checkpoint_v1 as exact_checkpoint
import sampled_visible_hybrid_checkpoint_v1 as base
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_preflop_table_v1 import build
from sampled_visible_hybrid_fit_v1 import fit
from sampled_physical_root_evaluation_v1 import sha, save
from preflop_allin_matrix_v1 import AllinMatrix
from action_integrated_root_evaluation_v1 import evaluate as integrate_root


def initialize(objects, config, *, context_source, catalog_source, matrix_sha256, entry_mass):
    checkpoint.require_config(config)
    if config.get('current_policy_inference') != 'float64-widened-float32-weights-v1':
        raise ValueError('Explicit float64 current-policy inference required')
    args = dict(context_source=context_source, catalog_source=catalog_source,
                matrix_sha256=matrix_sha256, entry_mass=entry_mass)
    ref = base.write_model(objects, 0, base.uniform_networks(), [1., 1.], [None, None],
                           context_source=context_source)
    exact = ExactBtnRegrets(base.digest(context_source), entry_mass)
    exact_ref = exact_checkpoint.write_model(objects, base.model_document(objects, ref, context_source=context_source), exact, **args)
    root_state = IntegratedRootRegrets(base.digest(context_source), matrix_sha256)
    current = checkpoint.write_model(objects, exact_checkpoint.model_document(objects, exact_ref, **args), root_state, **args)
    return dict(completed_iterations=0,
        sampler=PhysicalDeals(context_source, mode='full_deck', seed=config['sampler_seed']),
        action_rng=np.random.Generator(np.random.PCG64(config['action_seed'])),
        reservoirs=[PhysicalReservoir(config['reservoir_capacity'],p,config['reservoir_seeds'][p],context_source) for p in (0,1)],
        played_bank=[], next_model=current, exact_btn_state=exact, root_regret_state=root_state)


def save_state(objects, state, config, **args):
    return checkpoint.save_checkpoint(objects, completed=state['completed_iterations'],
        config=config, sampler=state['sampler'], action_rng=state['action_rng'],
        reservoirs=state['reservoirs'], bank=state['played_bank'], current=state['next_model'], **args)


def first_action_view(queries, response_hi):
    """Old native transports omit history; these nodes structurally precede it.

    Only the BB initial root and its terminal all-in response may be annotated.
    Ordinary later decision histories are never invented or used for averaging.
    The native document on disk remains untouched.
    """
    observations = []
    for o in queries['observations']:
        if int(o['hi']) in (1, response_hi):
            if o['phase'] != 0 or o.get('own_history', []) != []:
                raise ValueError('Invalid history at structurally initial action')
            o = dict(o, own_history=[])
        observations.append(o)
    return dict(queries, observations=observations)


def update(folder, objects, state, config, *, context_path, catalog_source,
           matrix_source, matrix_sha256, cache, executable, integration_executable, batch_prefix, guard):
    guard()
    context_path = Path(context_path)
    source = context_path.read_text()
    matrix = AllinMatrix(json.loads(matrix_source), source)
    args = dict(context_source=source, catalog_source=catalog_source,
                matrix_sha256=matrix_sha256, entry_mass=matrix.btn_mass)
    checkpoint.require_config(config)
    if config.get('current_policy_inference') != 'float64-widened-float32-weights-v1':
        raise ValueError('Explicit float64 current-policy inference required')
    if config.get('exact_bb_root_targets') != 'exact-initial-bb-training-targets-v2':
        raise ValueError('Explicit corrected BB learning-target configuration required')
    if cache.sha256 != config['allin_cache_sha256']:
        raise ValueError('Current exact traversal cache must match training config')
    generation = state['completed_iterations']
    iteration = generation+1
    used = state['next_model']
    if used['generation'] != generation or len(state['played_bank']) != generation or state['exact_btn_state'].steps != generation or state['root_regret_state'].steps != generation:
        raise ValueError('Training state is not at a complete generation boundary')
    model = checkpoint.model_document(objects, used, **args)
    if model['exact_model']['exact_btn']['state'] != state['exact_btn_state'].document():
        raise ValueError('Current exact state differs from frozen played model')
    if model['integrated_root']['state'] != state['root_regret_state'].document():
        raise ValueError('Current root state differs from frozen played model')
    response_hi = json.loads(source)['nodes'][0]['children'][3]+1
    catalog = json.loads(catalog_source)
    catalog_query = first_action_view(dict(context_source=source,
        observations=[r['observation'] for r in catalog['native_observations']]), response_hi)
    p, coverage = probabilities(catalog_query, model, device=config['device'],
        catalog_source=catalog_source, matrix_sha256=matrix_sha256, entry_mass=matrix.btn_mass)
    root = np.full((169,4), np.nan); calls = np.zeros(169); seen = [set(),set()]
    for item, row in zip(catalog['native_observations'], p):
        player, c = item['player'], item['hand_class']
        if c in seen[player]: raise ValueError('Duplicate class in complete initial catalog')
        seen[player].add(c)
        if player == 0: root[c] = row
        else: calls[c] = row[1]
    if seen[0] != set(range(169)) or seen[1] != set(np.flatnonzero(matrix.btn_mass > 0)):
        raise ValueError('Complete supported initial policies required')
    targets = InitialTargets(matrix_source, source, root, calls,
                             matrix_sha256=matrix_sha256, generation=generation)
    exact_values = matrix.evaluate(root, calls)
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=False)
    initial_path = folder/'current-initial-policy.json'
    save(initial_path, dict(used_model=used, root=root.tolist(), calls=calls.tolist(),
                           target_identity=targets.identity, catalog_coverage=coverage))
    subbatches = []; root_audits = []; integration_seconds = 0.
    for chunk in range(config['subbatches_per_iteration']):
        guard()
        part = folder/f'batch-{chunk:02d}'; part.mkdir()
        batch = cache.batch(dict(format=2, batch_id=f'{batch_prefix}-iteration-{iteration}-batch-{chunk}',
            query_limit=config['query_limit'], seed=int(state['action_rng'].integers(0,2**63)),
            deals=state['sampler'].sample(config['deals_per_subbatch'])['deals']))
        paths = {name:part/f'{name}.json' for name in ('batch','queries','policies','updates','derived-targets')}
        save(paths['batch'], batch)
        def invoke(mode, policy, destination):
            guard()
            result = subprocess.run([str(executable), mode, str(context_path), str(paths['batch']), str(policy), str(destination)],
                timeout=120, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode: raise RuntimeError(result.stderr[-2000:])
        invoke('queries', '-', paths['queries'])
        raw_queries = json.loads(paths['queries'].read_text())
        queries = first_action_view(raw_queries, response_hi)
        p, coverage = probabilities(queries, model, device=config['device'],
            catalog_source=catalog_source, matrix_sha256=matrix_sha256, entry_mass=matrix.btn_mass)
        policies = policy_document(raw_queries, p)
        save(paths['policies'], policies)
        invoke('verify', paths['policies'], paths['updates'])
        updates = json.loads(paths['updates'].read_text())
        counts, audit = ingest(raw_queries, updates, policies, state['reservoirs'], iteration, cache, targets, guard=guard)
        save(paths['derived-targets'], audit)
        # The sampled reservoir ingestion above is deliberately unchanged. Only
        # the separately typed root accumulator receives integrated targets.
        before = time.monotonic()
        integrated = integrate_root(context_path, paths['batch'], raw_queries, policies, audit,
            part, integration_executable, guard)
        integration_seconds += time.monotonic()-before
        root_audits.append(integrated)
        for name in ('integrated-profiles','integrated-native','integrated-targets'):
            paths[name] = part/f'{name}.json'
        subbatches.append(dict(chunk=chunk, used_model=used, counts=counts, coverage=coverage,
            artifacts={name:sha(path) for name,path in paths.items()}))
    trained, fits = [], []
    for player, reservoir in enumerate(state['reservoirs']):
        net, metric = fit(reservoir, seed=config['fit_seed_base']+iteration*200003+player,
            steps=config['fit_steps'], device=config['device'], chunk_size=config['chunk_size'],
            learning_rate=config['learning_rate'], guard=guard)
        trained.append(net); fits.append(metric)
    # The exact state is advanced once, after all frozen-policy subbatches/fits.
    exact = copy.deepcopy(state['exact_btn_state'])
    delta = exact.step(iteration, calls, exact_values['btn_jam_mass'],
                      exact_values['btn_fold_entries'], exact_values['btn_call_entries'])
    base_ref = base.write_model(objects, iteration, trained, [m['advantage_scale'] for m in fits],
                               [build(r,source) for r in state['reservoirs']], context_source=source)
    exact_ref = exact_checkpoint.write_model(objects, base.model_document(objects,base_ref,context_source=source), exact, **args)
    root_state = copy.deepcopy(state['root_regret_state'])
    root_state.step(iteration, root_audits,
        expected_deals=config['subbatches_per_iteration']*config['deals_per_subbatch'],
        expected_batches=config['subbatches_per_iteration'])
    current = checkpoint.write_model(objects, exact_checkpoint.model_document(objects,exact_ref,**args), root_state, **args)
    state.update(completed_iterations=iteration, next_model=current, exact_btn_state=exact, root_regret_state=root_state,
                 played_bank=[*state['played_bank'],used])
    reference = save_state(objects, state, config, **args)
    metrics = dict(iteration=iteration, used_model=used, next_model=current, checkpoint=reference,
        root_integration_seconds=integration_seconds,
        initial_policy_sha256=sha(initial_path), subbatches=subbatches, fits=fits,
        exact_btn_update=dict(completed_updates=exact.steps, regret_delta=delta.tolist(),
            conditional_reach_sums=exact.reach.tolist(), sampled_observations_added=0),
        root_update=dict(completed_updates=root_state.steps,root_samples=int(root_state.counts.sum()),
            covered_classes=int(np.count_nonzero(root_state.counts)),payload_bytes=root_state.counts.nbytes+root_state.regrets.nbytes),
        reservoirs=[r.summary() for r in state['reservoirs']])
    save(folder/'metrics.json', metrics)
    return metrics
