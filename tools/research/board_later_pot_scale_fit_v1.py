"""Pot-scaled outputs with unchanged original chip-error weighting."""
import time
import numpy as np
from sampled_visible_initialization_v1 import fresh_visible_network
from weighted_visible_objective_v1 import PreparedWeightedObjective
from sampled_visible_gradient_graph_fit_v1 import gradient_tensor
from weighted_training_graph_fit_v2 import capture_stream
from board_later_fit_holdout_train_v1 import Evaluation
from board_later_error_audit_math_v1 import public_amounts, row_totals, totals, partition


def factors(active, arity, catalog):
    pot, _ = public_amounts(active, arity, catalog)
    post = active[:, 15].astype(int) > 135
    value = np.ones(len(active), dtype=np.float32)
    value[post] = (pot[post]/10.).astype(np.float32)
    assert np.isfinite(value).all() and np.all(value > 0)
    assert np.all(value[~post] == 1)
    return value


def fresh_zero_network(seed):
    import torch
    model = fresh_visible_network(seed)
    with torch.no_grad():
        model[4].weight.zero_(); model[4].bias.zero_()
    return model


class ScaledObjective(PreparedWeightedObjective):
    def __init__(self, data, device, *, dtype, guard, factor=None):
        import torch
        super().__init__(data, device, dtype=dtype, guard=guard)
        if factor is not None:
            factor = np.asarray(factor)
            assert factor.shape == (len(data['active']),) and np.isfinite(factor).all() and np.all(factor > 0)
            g = torch.as_tensor(factor, dtype=dtype, device=device)[:, None]
            self.target = self.target/g
            self.weight = self.weight*g.square()
        # Preserve the original denominator and variance convention. Replacing
        # the denominator with transformed weight mass would change the loss.
        assert self.denominator == data['denominator']
        assert torch.isfinite(self.target).all() and torch.isfinite(self.weight).all()
        guard()


class PotEvaluation(Evaluation):
    def __init__(self, raw, scale, guard, catalog):
        super().__init__(raw, scale, guard)
        self.raw = raw
        self.pot, _ = public_amounts(raw['active'], raw['arity'], catalog)
        self.factor = factors(raw['active'], raw['arity'], catalog).astype(np.float64)

    def score(self, model, guard, *, scaled):
        import torch
        predicted = []
        with torch.no_grad():
            for start in range(0, len(self.x), 8192):
                guard(); predicted.append(model(self.x[start:start+8192]).cpu().numpy().astype(np.float64))
        predicted = np.concatenate(predicted)
        if scaled: predicted *= self.factor[:, None]
        rows = row_totals(predicted, self.raw['values'], self.raw['arity'], self.raw['weights'], self.scale)
        post = self.phase > 0; masks = [('all', np.ones(len(self.x), dtype=bool)), ('postflop', post)]
        masks += [(name, self.phase == i) for i, name in enumerate(('preflop', 'flop', 'turn', 'river'))]
        output = {}
        for name, mask in masks:
            value = totals(rows, mask)
            output[name] = dict(rows=value['rows'], source_weight=value['source_weight'],
                legal_target_mass=value['legal_target_mass'], normalized_loss=value['normalized_loss'],
                raw_scale_loss=value['normalized_loss']*self.scale**2,
                normalized_zero_loss=value['target_energy']/value['legal_target_mass'])
        indices = np.searchsorted([10., 50., 100., 200.], self.pot, side='right')
        buckets = partition(rows, post, [(name, post & (indices == i)) for i, name in enumerate(
            ('under 10 bb', '10-50 bb', '50-100 bb', '100-200 bb', '200+ bb'))])
        return dict(metrics=output, pots=buckets, under_50bb=totals(rows, post & (self.pot < 50)))


def curve(data, seed, checkpoints, callback, guard, *, factor=None, chunk_size=4096, captured=True):
    import torch
    assert sorted(set(checkpoints)) == list(checkpoints) and min(checkpoints) > 0
    started = time.monotonic(); guard()
    model = fresh_zero_network(seed).cuda()
    prepared = ScaledObjective(data, 'cuda', dtype=torch.float32, guard=guard, factor=factor)
    optimizer = torch.optim.Adam(model.parameters(), lr=.003)
    if captured:
        stream = capture_stream(torch); stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(2):
                model.zero_grad(set_to_none=True); gradient_tensor(prepared, model, chunk_size)
        torch.cuda.current_stream().wait_stream(stream); torch.cuda.synchronize(); guard()
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph, stream=stream):
            for parameter in model.parameters(): parameter.grad.zero_()
            total = gradient_tensor(prepared, model, chunk_size)
        torch.cuda.synchronize()
    setup = time.monotonic()-started; fit_started = time.monotonic(); callbacks = 0.
    for step in range(1, max(checkpoints)+1):
        guard()
        if captured: graph.replay()
        else:
            model.zero_grad(set_to_none=True)
            total = prepared.objective(model, chunk_size, guard, backward=True)
        if not np.isfinite(float(total)): raise ValueError('Nonfinite transformed training loss')
        optimizer.step()
        if step in checkpoints:
            with torch.no_grad(): loss = prepared.objective(model, chunk_size, guard)+data['variance']
            assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
            record = dict(step=step, normalized_training_loss=loss, raw_training_loss=loss*data['scale']**2,
                          elapsed_fit_seconds=time.monotonic()-fit_started-callbacks)
            before = time.monotonic(); callback(model, record); callbacks += time.monotonic()-before
    return dict(setup_seconds=setup, fit_seconds=time.monotonic()-fit_started-callbacks,
                callback_seconds=callbacks, peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved())


def policy(scores, arity):
    """Existing bank's legal positive-regret normalization and argmax fallback."""
    legal = np.arange(4)[None, :] < np.asarray(arity)[:, None]
    result = np.maximum(scores, 0)*legal; mass = result.sum(axis=1); positive = mass > 0
    result[positive] /= mass[positive, None]
    for i in np.flatnonzero(~positive): result[i, int(np.argmax(scores[i, :arity[i]]))] = 1
    return result


def algebra_control():
    import torch
    y = torch.tensor([[1., 3., 0., 0.], [3., 1., 0., 0.], [2., 4., 0., 0.]], dtype=torch.float64)
    g = torch.tensor([.5, 2., 10.], dtype=torch.float64)[:, None]
    w = torch.tensor([[1., 1., 0., 0.], [3., 3., 0., 0.], [2., 2., 0., 0.]], dtype=torch.float64)
    gradients = []; losses = []
    for transformed in (False, True):
        f = torch.ones_like(y, requires_grad=True)
        loss = ((f-y/g).square()*w*g.square()).sum()/12 if transformed else ((g*f-y).square()*w).sum()/12
        loss.backward(); gradients.append(f.grad.clone()); losses.append(float(loss.detach()))
    assert abs(losses[0]-212.5/12) < 1e-12
    gradient_error = float((gradients[0]-gradients[1]).abs().max())
    assert gradient_error < 1e-12 and abs(losses[0]-losses[1]) < 1e-12
    assert abs(float(gradients[0][2, 0])-80/3) < 1e-12 and not torch.any(gradients[0][:, 2:])
    scores = np.array([[1., 2., -3., 999.], [-2., -1., -1., 999.], [0., 0., 0., 0.],
                       [-1., 0., 999., 999.], [1., 1., 1., 1.], [-4., -3., -2., -1.]])
    arity = np.array([3, 3, 4, 2, 4, 4]); scales = np.array([.45, 1., 40.05, .5, 13.7, 2.])
    policy_error = float(np.max(np.abs(policy(scores, arity)-policy(scores*scales[:, None], arity))))
    assert policy_error < 1e-12
    return dict(passed=True, hand_calculated_loss=losses[0], algebra_gradient_error=gradient_error,
                legal_masks_and_ties=True, maximum_scaled_policy_difference=policy_error)


def control(data, seed, guard, catalog):
    import torch
    algebra = algebra_control()
    phase = data['active'][:, 15].astype(int)-135; selected = []
    for i in range(4):
        at = np.flatnonzero(phase == i); count = 65 if i == 0 else 64
        selected.extend(at[np.linspace(0, len(at)-1, count, dtype=int)].tolist())
    selected = np.array(sorted(selected)); assert len(np.unique(selected)) == 257
    fixture = dict(data)
    for key in ('active', 'arity', 'masses', 'targets', 'counts'): fixture[key] = data[key][selected].copy()
    fixture.update(denominator=float(np.dot(fixture['masses'], fixture['arity'])), variance=0., examples=257)
    g = factors(fixture['active'], fixture['arity'], catalog)
    assert np.any(g != 1)
    prepared = ScaledObjective(fixture, 'cuda', dtype=torch.float32, guard=guard, factor=g)
    initial = fresh_zero_network(seed).cuda()
    with torch.no_grad(): assert not torch.any(initial(prepared.x))
    initial.zero_grad(set_to_none=True); prepared.objective(initial, 128, guard, backward=True)
    assert float(initial[4].weight.grad.abs().max()) > 0
    # Independent restored-output objective and gradients with nonzero outputs,
    # using float64 to check all layers beyond the zero-output first step.
    gradients = []; losses = []
    for transformed in (False, True):
        model = fresh_visible_network(seed).double()
        raw = PreparedWeightedObjective(fixture, 'cpu', dtype=torch.float64, guard=guard)
        if transformed:
            transformed_objective = ScaledObjective(fixture, 'cpu', dtype=torch.float64, guard=guard, factor=g)
            losses.append(transformed_objective.objective(model, 128, guard, backward=True))
        else:
            value = (((model(raw.x)*torch.as_tensor(g, dtype=torch.float64)[:, None]-raw.target)**2)*raw.weight).sum()/raw.denominator
            value.backward(); losses.append(float(value.detach()))
        gradients.append([p.grad.detach().clone() for p in model.parameters()])
    direct_error = max(float((a-b).abs().max()) for a, b in zip(*gradients))
    assert direct_error < 1e-10 and abs(losses[0]-losses[1]) < 1e-10
    def run(factor, captured=True):
        snapshots = []; records = []
        def callback(model, record):
            snapshots.append({k: v.detach().cpu().clone() for k, v in model.state_dict().items()}); records.append(record)
        curve(fixture, seed, (16, 32, 64), callback, guard, factor=factor, chunk_size=128, captured=captured)
        return snapshots, records
    a, ar = run(g); b, br = run(g, False)
    curve_error = max(float((x[k]-y[k]).abs().max()) for x, y in zip(a, b) for k in x)
    loss_error = max(abs(x['normalized_training_loss']-y['normalized_training_loss']) for x, y in zip(ar, br))
    assert curve_error < 1e-5 and loss_error < 1e-5
    c, cr = run(None); d, dr = run(np.ones(257, dtype=np.float32))
    identity_error = max(float((x[k]-y[k]).abs().max()) for x, y in zip(c, d) for k in x)
    assert identity_error < 1e-7
    assert max(abs(x['normalized_training_loss']-y['normalized_training_loss']) for x, y in zip(cr, dr)) < 1e-7
    model = fresh_zero_network(seed).cuda(); model.load_state_dict(a[-1])
    raw = dict(active=fixture['active'], arity=fixture['arity'], values=fixture['targets']*fixture['scale'], weights=fixture['masses'])
    evaluation = PotEvaluation(raw, fixture['scale'], guard, catalog)
    score = evaluation.score(model, guard, scaled=True)
    evaluation_error = abs(score['metrics']['all']['normalized_loss']-ar[-1]['normalized_training_loss'])
    assert evaluation_error < 1e-5
    return dict(passed=True, algebra=algebra, real_rows=257, phase_rows=[65, 64, 64, 64], steps=64, chunk_size=128,
        factor_min=float(g.min()), factor_max=float(g.max()), zero_initial_function=True, output_layer_receives_gradient=True,
        maximum_real_direct_gradient_difference=direct_error, real_direct_loss_difference=abs(losses[0]-losses[1]),
        maximum_curve_parameter_difference=curve_error, maximum_curve_loss_difference=loss_error,
        factor_one_parameter_difference=identity_error, restored_evaluation_difference=evaluation_error,
        heldout_loss_scored=False)
