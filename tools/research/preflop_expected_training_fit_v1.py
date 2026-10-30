"""Dense cumulative preflop targets mixed with sampled postflop advantages.

Separate prospective objective; no change to the original comparison. Source
mass weights the loss, never an already-weighted target a second time. No own
history links are invented for feature-only fitting rows.
"""
import copy
import hashlib
import json
import time
from collections import OrderedDict
from types import SimpleNamespace

import numpy as np

import preflop_expected_training_checkpoint_v1 as checkpoint
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
from sampled_visible_hybrid_checkpoint_v1 import encoded
from weighted_visible_objective_v1 import grouped_rows
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from stack_context_current_policy_v1 import CurrentPolicy
from storage_strategic_common_prior_20260920 import PAIRS, CLASSES
from stack_context_training_fit_v1 import PreparedContextObjective, fresh_network
from stack_context_fit_rows_v1 import METHOD as DELEGATE_METHOD
from sampled_physical_fit_v1 import export_network
from sampled_visible_gradient_graph_fit_v1 import gradient_tensor
from weighted_training_graph_fit_v2 import capture_stream

METHOD = checkpoint.FIT_METHOD


def visible_inputs(registry, key, observations):
    # Reuse only the qualified feature/public-key checks, never infer a policy.
    encoder = SimpleNamespace(context_sha256=key,
        entry=copy.deepcopy(registry._get(key)), width=registry.manifest['representation']['input_width'],
        relative_cache=OrderedDict())
    return CurrentPolicy._features(encoder, observations)[0]


def prepare(registry, contexts, resources, *, player, context_weights, preflop_fraction):
    if type(player) is not int or player not in (0, 1): raise ValueError('Explicit fit actor required')
    keys = set(registry.fit_contexts)
    if set(contexts) != keys or set(resources) != keys or set(context_weights) != keys:
        raise ValueError('All and only fitted contexts required')
    mix = np.array([context_weights[k] for k in registry.fit_contexts])
    if not np.isfinite(mix).all() or np.any(mix <= 0) or abs(float(mix.sum())-1) > 1e-12:
        raise ValueError('Fixed positive normalized context weights required')
    if type(preflop_fraction) not in (int, float) or not 0 < preflop_fraction < 1:
        raise ValueError('Explicit nondegenerate preflop/postflop mixture required')
    xs = []; ys = []; ws = []; all_keys = []; summaries = []; variance = 0.; generations = set()
    classes = {tuple(hand):int(c) for hand, c in zip(PAIRS, CLASSES)}
    for key in registry.fit_contexts:
        local = contexts[key]; state = local['preflop_state']; args = resources[key]
        if not isinstance(state, PreflopExpectedRegrets): raise ValueError('Complete cumulative targets required')
        state = PreflopExpectedRegrets.restore(state.document(), context_source=registry.source(key),
            matrix_source=args['matrix_source'], expected_config=args['expected_config'])
        if not state.steps: raise ValueError('No unlearned initial state may become dense training truth')
        generations.add(state.steps); stack = float(state.context['config']['stack'])
        if not np.isfinite(stack) or stack <= 0: raise ValueError('Positive starting stack required')
        if hashlib.sha256(args['physical_catalog_source'].encode()).hexdigest() != args['physical_catalog_sha256']:
            raise ValueError('Changed complete physical fit catalog')
        catalog = json.loads(args['physical_catalog_source'])
        if catalog['context_source'] != registry.source(key): raise ValueError('Changed fit catalog context')
        index = {}
        for row in catalog['rows']:
            token = (row['node'], classes[tuple(row['hand'])])
            index.setdefault(token, row['observation'])
        observations = []; targets = []; masses = []; identities = []; coverage = {}
        for node in state.nodes:
            if state.specs[node]['actor'] != player: continue
            mass = state.mass[player]; support = (mass > 0)&(state.supported_generations[node] > 0)
            coverage[str(node)] = int(support.sum())
            for c in np.flatnonzero(support):
                o = index[(node, int(c))]; arity = state.specs[node]['arity']
                if (o['actor'], o['phase'], o['n'], o['hi']) != (player, 0, arity, str(node+1)):
                    raise ValueError('Dense canonical fit row disagrees with its node')
                y = np.zeros(4)
                y[:arity] = state.regrets[node][c]/(state.config['generation_scale']*mass[c]*state.steps*stack)
                w = np.zeros(4); w[:arity] = mass[c]
                observations.append(o); targets.append(y); masses.append(w)
                identities.append((key, o['hi'], o['lo']))
        if not observations: raise ValueError('Actor needs supported dense preflop targets')
        pre_x = visible_inputs(registry, key, observations)
        pre_y, pre_w = np.asarray(targets), np.asarray(masses)
        pre_denominator = float(pre_w.sum())
        pre_w *= context_weights[key]*preflop_fraction/pre_denominator
        r = local['reservoirs'][player]
        if (not isinstance(r, WeightedPhysicalReservoir) or r.player != player or r.context_sha256 != key
                or not r.size or np.any(r.keys[:r.size, 0] < 1 << 63)):
            raise ValueError('Nonempty postflop-only reservoir required')
        grouped = grouped_rows(r)
        _, first = np.unique(r.keys[:r.size], axis=0, return_index=True)
        post_observations = []
        for i in first:
            active = r.active[i].astype(int).tolist(); phase = [v-135 for v in active if 135 <= v < 139]
            if len(phase) != 1 or phase[0] not in (1, 2, 3): raise ValueError('Postflop phase required')
            post_observations.append(dict(hi=str(int(r.keys[i, 0])), lo=str(int(r.keys[i, 1])), actor=player,
                phase=phase[0], n=int(r.arity[i]), active_features=active))
        post_x = visible_inputs(registry, key, post_observations)
        post_y = grouped['targets']*(grouped['scale']/stack)
        legal = np.arange(4)[None, :] < grouped['arity'][:, None]
        post_w = legal*grouped['masses'][:, None]*context_weights[key]*(1-preflop_fraction)/grouped['denominator']
        post_variance = grouped['variance']*(grouped['scale']/stack)**2
        variance += context_weights[key]*(1-preflop_fraction)*post_variance
        xs.extend((pre_x, post_x)); ys.extend((pre_y, post_y)); ws.extend((pre_w, post_w))
        all_keys.extend(identities); all_keys.extend((key, o['hi'], o['lo']) for o in post_observations)
        summaries.append(dict(context_sha256=key, player=player, starting_stack=stack,
            mixture_weight=context_weights[key], generation=state.steps, cumulative_state_sha256=state.document()['state_sha256'],
            preflop=dict(rows=len(pre_x), covered_classes_by_node=coverage, normalized_fraction=preflop_fraction,
                raw_weighted_legal_mass=pre_denominator, target_recipe=checkpoint.DENSE_RECIPE),
            postflop=dict(retained_visits=r.size, grouped_rows=len(post_x), normalized_fraction=1-preflop_fraction,
                raw_weighted_legal_mass=grouped['denominator'], normalized_within_observation_variance=post_variance)))
    if len(generations) != 1 or len(set(all_keys)) != len(all_keys):
        raise ValueError('One complete joint generation and unique visible information sets required')
    x, y, w = np.concatenate(xs), np.concatenate(ys), np.concatenate(ws)
    if not all(np.isfinite(a).all() for a in (x, y, w)) or abs(float(w.sum())-1) > 1e-12:
        raise ValueError('Finite complete normalized objective required')
    metadata = dict(method=METHOD, representation=registry.manifest['representation'], registry_sha256=registry.sha256,
        player=player, keys=all_keys, contexts=summaries, target_units=checkpoint.SCALE,
        within_observation_variance=variance, preflop_fraction=preflop_fraction,
        own_history_available=False, generation=next(iter(generations)))
    h = hashlib.sha256(encoded(metadata))
    for a in (x, y, w):
        h.update(str(a.dtype).encode()); h.update(encoded(list(a.shape))); h.update(a.tobytes(order='C'))
    return dict(metadata, features=x, targets=y, weights=w, objective_sha256=h.hexdigest())


class PreparedExpectedObjective(PreparedContextObjective):
    def __init__(self, grouped, device, *, dtype, guard):
        if grouped['method'] != METHOD: raise ValueError('Explicit dense/sampled objective required')
        # Delegate the already-qualified ordered weighted-MSE tensor arithmetic.
        # Its old data-recipe label is internal only; this objective keeps its own identity.
        super().__init__(dict(grouped, method=DELEGATE_METHOD), device, dtype=dtype, guard=guard)
        self.identity = grouped['objective_sha256']


def fit(registry, contexts, resources, config, *, player, generation, collected_against, guard):
    import torch
    checkpoint.require_config(config, registry, resources)
    guard(); began = time.monotonic()
    if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
        raise ValueError('Disable TF32 for the declared math path')
    grouped = prepare(registry, contexts, resources, player=player,
        context_weights=config['context_weights'], preflop_fraction=config['preflop_fraction'])
    if grouped['generation'] != generation: raise ValueError('Fit generation differs from collected targets')
    seed = config['fit_seed_base']+generation*200003+player
    model = fresh_network(seed, registry.manifest['representation']['input_width']).to('cuda')
    objective = PreparedExpectedObjective(grouped, 'cuda', dtype=torch.float32, guard=guard)
    optimizer = torch.optim.Adam(model.parameters(), lr=config['learning_rate'], betas=(.9, .999), eps=1e-8,
                                 weight_decay=0., amsgrad=False, foreach=False, fused=False)
    with torch.no_grad(): before = objective.objective(model, config['chunk_size'], guard)
    stream = capture_stream(torch); stream.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(stream):
        for _ in range(2): model.zero_grad(set_to_none=True); gradient_tensor(objective, model, config['chunk_size'])
    torch.cuda.current_stream().wait_stream(stream); torch.cuda.synchronize(); guard()
    graph = torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph, stream=stream):
        for parameter in model.parameters(): parameter.grad.zero_()
        loss = gradient_tensor(objective, model, config['chunk_size'])
    torch.cuda.synchronize(); guard()
    for _ in range(config['fit_steps']):
        guard(); graph.replay()
        if not np.isfinite(float(loss)): raise ValueError('Nonfinite captured fit loss')
        optimizer.step()
    torch.cuda.synchronize()
    with torch.no_grad(): after = objective.objective(model, config['chunk_size'], guard)
    if any(not bool(torch.isfinite(p).all()) for p in model.parameters()): raise ValueError('Nonfinite fitted parameters')
    network = export_network(model)
    receipt = dict(execution_mode=config['execution_mode'], player=player, generation=generation,
        collected_against=collected_against, registry_sha256=registry.sha256,
        local_fit_identities={k:checkpoint.local_fit_identity(contexts[k]) for k in registry.fit_contexts},
        network_sha256=checkpoint.hash_document(network), objective_method=METHOD,
        fit_runtime=checkpoint.RUNTIME, target_units=checkpoint.SCALE, preflop_fit_recipe=checkpoint.DENSE_RECIPE,
        preflop_fraction=config['preflop_fraction'], context_weights=config['context_weights'],
        seed=seed, steps=config['fit_steps'], learning_rate=config['learning_rate'], chunk_size=config['chunk_size'],
        initialization=checkpoint.INITIALIZATION, optimizer=checkpoint.OPTIMIZER, device='cuda',
        objective_sha256=objective.identity)
    return network, receipt, dict(seconds=time.monotonic()-began, loss_before=before, loss_after=after,
        tensor_bytes=objective.tensor_bytes, rows=len(grouped['keys']), contexts=grouped['contexts'],
        within_observation_variance=grouped['within_observation_variance'])
