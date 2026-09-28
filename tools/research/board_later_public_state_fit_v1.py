"""Qualified weighted fitter with explicit, redundant public betting inputs."""
import time
import numpy as np
from board_later_fit_holdout_train_v1 import Evaluation
from board_later_public_state_features_v1 import features as public_features, fresh_public_network
from sampled_visible_features_bulk_v1 import features as visible_features
from sampled_visible_gradient_graph_fit_v1 import gradient_tensor
from weighted_visible_objective_v1 import PreparedWeightedObjective
from weighted_training_graph_fit_v2 import capture_stream


class PublicObjective(PreparedWeightedObjective):
    def __init__(self, data, device, *, dtype, guard, table):
        import torch
        super().__init__(data, device, dtype=dtype, guard=guard)
        extra = public_features(data['active'], data['arity'], table)
        self.x = torch.cat((self.x, torch.as_tensor(extra, dtype=dtype, device=device)), dim=1)
        assert self.x.shape == (len(data['active']), 314)
        guard()


class PublicEvaluation(Evaluation):
    def __init__(self, raw, scale, guard, table):
        import torch
        super().__init__(raw, scale, guard)
        extra = public_features(raw['active'], raw['arity'], table)
        self.x = torch.cat((self.x, torch.as_tensor(extra, device='cuda')), dim=1)
        assert self.x.shape == (len(raw['active']), 314)
        guard()


def curve(data, seed, checkpoints, callback, guard, table, *, chunk_size=4096, captured=True):
    """Same full-gradient Adam trajectory as the frozen 302-input fitter."""
    import torch
    assert sorted(set(checkpoints)) == list(checkpoints) and min(checkpoints) > 0
    started = time.monotonic(); guard()
    model = fresh_public_network(seed).cuda()
    prepared = PublicObjective(data, 'cuda', dtype=torch.float32, guard=guard, table=table)
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
    setup = time.monotonic() - started; fit_started = time.monotonic(); callbacks = 0.
    for step in range(1, max(checkpoints) + 1):
        guard()
        if captured: graph.replay()
        else:
            model.zero_grad(set_to_none=True)
            total = prepared.objective(model, chunk_size, guard, backward=True)
        if not np.isfinite(float(total)): raise ValueError('Nonfinite training loss')
        optimizer.step()
        if step in checkpoints:
            with torch.no_grad(): loss = prepared.objective(model, chunk_size, guard) + data['variance']
            assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
            record = dict(step=step, normalized_training_loss=loss, raw_training_loss=loss*data['scale']**2,
                          elapsed_fit_seconds=time.monotonic()-fit_started-callbacks)
            before = time.monotonic(); callback(model, record); callbacks += time.monotonic()-before
    return dict(setup_seconds=setup, fit_seconds=time.monotonic()-fit_started-callbacks,
                callback_seconds=callbacks, peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved())


def control(data, seed, guard, table):
    """Training-only real-input control spanning preflop and all three streets."""
    import torch
    phase = data['active'][:, 15].astype(int)-135
    selected = []
    for i in range(4):
        choices = np.flatnonzero(phase == i); count = 65 if i == 0 else 64
        assert len(choices) >= count
        selected.extend(choices[np.linspace(0, len(choices)-1, count, dtype=int)].tolist())
    chosen = np.asarray(sorted(selected))
    assert len(chosen) == len(np.unique(chosen)) == 257
    fixture = dict(data)
    for key in ('active', 'arity', 'masses', 'targets', 'counts'): fixture[key] = data[key][chosen].copy()
    fixture.update(denominator=float(np.dot(fixture['masses'], fixture['arity'])), variance=0., examples=257)
    extra = public_features(fixture['active'], fixture['arity'], table)
    assert np.any(extra[phase[chosen] > 0] > 0) and np.all(extra[phase[chosen] == 0] == 0)
    snapshots = []; records = []
    def callback(model, record):
        snapshots.append({k: v.detach().cpu().clone() for k, v in model.state_dict().items()})
        records.append(record)
    curve(fixture, seed, (16, 32, 64), callback, guard, table, chunk_size=128)
    captured = snapshots; captured_records = records; snapshots = []; records = []
    curve(fixture, seed, (16, 32, 64), callback, guard, table, chunk_size=128, captured=False)
    difference = max(float((a[k]-b[k]).abs().max()) for a, b in zip(captured, snapshots) for k in a)
    loss_difference = max(abs(a['normalized_training_loss']-b['normalized_training_loss'])
                          for a, b in zip(captured_records, records))
    assert difference < 1e-5 and loss_difference < 1e-5, (difference, loss_difference)
    assert float(captured[-1]['0.weight'][:, 302:].abs().max()) > 0
    gradients = []; losses = []
    for device in ('cpu', 'cuda'):
        model = fresh_public_network(seed).to(device)
        prepared = PublicObjective(fixture, device, dtype=torch.float32, guard=guard, table=table)
        model.zero_grad(set_to_none=True)
        losses.append(prepared.objective(model, 128, guard, backward=True))
        gradients.append([p.grad.detach().cpu().clone() for p in model.parameters()])
    gradient_difference = max(float((a-b).abs().max()) for a, b in zip(*gradients))
    assert gradient_difference < 1e-5 and abs(losses[0]-losses[1]) < 1e-5
    assert float(gradients[0][0][:, 302:].abs().max()) > 0
    raw = dict(active=fixture['active'], arity=fixture['arity'],
               values=fixture['targets']*fixture['scale'], weights=fixture['masses'])
    evaluation = PublicEvaluation(raw, fixture['scale'], guard, table); scored = evaluation(model, guard)
    visible = visible_features([dict(active_features=a.tolist()) for a in raw['active']])
    full = np.concatenate((visible, extra), axis=1)
    cpu = fresh_public_network(seed)
    with torch.no_grad(): predicted = cpu(torch.from_numpy(full)).numpy().astype(float)
    legal = np.arange(4)[None, :] < raw['arity'][:, None]
    direct = float(((predicted-fixture['targets'])**2*legal*raw['weights'][:, None]).sum()/fixture['denominator'])
    evaluation_difference = abs(direct-scored['all']['normalized_loss'])
    streets = [scored[key] for key in ('preflop', 'flop', 'turn', 'river')]
    phase_total = sum(v['normalized_loss']*v['legal_target_mass'] for v in streets)/sum(v['legal_target_mass'] for v in streets)
    assert evaluation_difference < 1e-5 and abs(phase_total-scored['all']['normalized_loss']) < 1e-12
    return dict(passed=True, real_visible_inputs=257, phase_rows=[65, 64, 64, 64], steps=64,
                checkpoints=[16, 32, 64], chunk_size=128, new_columns_learn=True,
                maximum_curve_parameter_difference=difference, maximum_curve_loss_difference=loss_difference,
                maximum_cpu_gpu_gradient_difference=gradient_difference,
                cpu_gpu_loss_difference=abs(losses[0]-losses[1]),
                direct_evaluation_cpu_gpu_difference=evaluation_difference, street_weighted_loss_identity=True,
                heldout_loss_scored=False)
