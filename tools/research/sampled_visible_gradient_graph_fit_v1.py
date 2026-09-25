"""Experimental launch-overhead reduction, not admitted for training trials.

Capture one ordered full-gradient calculation. Adam stays outside capture with
its original settings. Exact full-fit replay is required before adoption.
"""
import time
import numpy as np
from sampled_physical_fit_v1 import grouped_rows,export_network
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_hybrid_fit_bulk_v1 import PreparedObjective
from sampled_visible_hybrid_checkpoint_v1 import FEATURE_SPEC


def gradient_tensor(prepared,model,chunk_size):
    import torch
    total=torch.zeros((),dtype=torch.float64,device=prepared.x.device)
    for start in range(0,len(prepared.x),chunk_size):
        stop=min(start+chunk_size,len(prepared.x))
        loss=((model(prepared.x[start:stop])-prepared.target[start:stop]).square()
            *prepared.weight[start:stop]).sum()/prepared.denominator
        total+=loss.detach().double()
        loss.backward()
    return total


def fit(reservoir,*,seed,steps,device,chunk_size,guard,learning_rate=.003):
    import torch
    if device!='cuda' or type(steps) is not int or steps<1:
        raise ValueError('CUDA and positive fit count required')
    if type(chunk_size) is not int or chunk_size<1 or not np.isfinite(learning_rate) or learning_rate<=0:
        raise ValueError('Positive chunk and learning rate required')
    guard();began=time.monotonic();grouped=grouped_rows(reservoir)
    model=fresh_visible_network(seed).to(device)
    prepared=PreparedObjective(grouped,next(model.parameters()).device,guard)
    setup_seconds=time.monotonic()-began
    optimizer=torch.optim.Adam(model.parameters(),lr=learning_rate)
    with torch.no_grad():before=prepared.objective(model,chunk_size,guard)
    guard();capture_started=time.monotonic()
    stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
    # Warm kernels without taking optimizer steps or changing parameter values.
    with torch.cuda.stream(stream):
        for _ in range(2):
            model.zero_grad(set_to_none=True)
            gradient_tensor(prepared,model,chunk_size)
    torch.cuda.current_stream().wait_stream(stream)
    torch.cuda.synchronize();guard()
    graph=torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph,stream=stream):
        # Explicit captured reset prevents replay from accumulating gradients
        # from a previous optimizer step. Fixed addresses are retained.
        for parameter in model.parameters():parameter.grad.zero_()
        total=gradient_tensor(prepared,model,chunk_size)
    torch.cuda.synchronize();capture_seconds=time.monotonic()-capture_started
    guard();fit_started=time.monotonic()
    for _ in range(steps):
        guard();graph.replay()
        if not np.isfinite(float(total)):raise ValueError('Nonfinite graph loss')
        optimizer.step()
    fit_seconds=time.monotonic()-fit_started
    with torch.no_grad():after=prepared.objective(model,chunk_size,guard)
    if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
        raise ValueError('Nonfinite graph-fitted parameters')
    return export_network(model),dict(player=reservoir.player,device=device,steps=steps,
        seed=seed,learning_rate=learning_rate,chunk_size=chunk_size,
        retained_examples=grouped['examples'],grouped_observations=len(grouped['active']),
        legal_target_count=grouped['denominator'],advantage_scale=grouped['scale'],
        normalized_grouped_loss_before=before,normalized_grouped_loss_after=after,
        normalized_within_observation_variance=grouped['variance'],prepared_tensor_bytes=prepared.tensor_bytes,
        representation=FEATURE_SPEC,setup_seconds=setup_seconds,optimizer_seconds=fit_seconds,
        graph_capture_seconds=capture_seconds,prepared_once=True,
        scope='Experimental captured ordered gradient calculation; requires exact replay qualification, no poker-strength claim.')
