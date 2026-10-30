"""Shared-context full-gradient fitting with explicit stack-normalized weights.

Fits start from a fresh seeded network and Adam state, as in the existing
continuation trainer. No optimizer state carries across complete joint cycles.
"""
import hashlib
import time
import numpy as np
from stack_context_fit_rows_v1 import prepare, METHOD
from stack_context_inputs_v1 import encoded
from stack_board_relative_model_v1 import fresh
from sampled_physical_fit_v1 import export_network
from sampled_visible_gradient_graph_fit_v1 import gradient_tensor
from weighted_training_graph_fit_v2 import capture_stream

RUNTIME = 'context-weighted-ordered-cuda-gradient-v1'
INITIALIZATION = 'seeded-visible-base-zero-public-and-relative-columns-v1'
OPTIMIZER = dict(name='Adam', betas=[.9,.999], eps=1e-8, weight_decay=0.,
                 amsgrad=False, foreach=False, fused=False,
                 lifecycle='fresh seeded network and optimizer for each player fit')


def fresh_network(seed, width):
    if type(seed) is not int or not 0 <= seed < 2**63 or width not in (362,387):
        raise ValueError('Explicit supported width and nonnegative bounded seed required')
    # Reuse the qualified neutral extension, not any fitted diagnostic weights.
    return fresh(seed, width, 'cpu')[0]


class PreparedContextObjective:
    def __init__(self, grouped, device, *, dtype, guard):
        import torch
        guard()
        if grouped.get('method') != METHOD or grouped.get('target_units') != 'advantage_bb / context_starting_stack':
            raise ValueError('Explicit context-normalized objective required')
        width = grouped['representation']['input_width']
        x,y,w = (np.asarray(grouped[name]) for name in ('features','targets','weights'))
        if (width not in (362,387) or x.ndim != 2 or x.shape[1] != width or not len(x)
                or y.shape != (len(x),4) or w.shape != y.shape
                or not all(np.isfinite(a).all() for a in (x,y,w)) or np.any(w < 0)
                or abs(float(w.sum())-1.) > 1e-12):
            raise ValueError('Invalid normalized input/target/weight arrays')
        legal=w>0; arity=legal.sum(1)
        if np.any(arity<2) or not np.array_equal(legal,np.arange(4)[None,:]<arity[:,None]) or np.any(y[~legal]):
            raise ValueError('Positive weights for legal actions and zero padding required')
        if dtype not in (torch.float32,torch.float64) or torch.device(device).type not in ('cpu','cuda'):
            raise ValueError('Explicit numeric backend required')
        self.x=torch.as_tensor(x,dtype=dtype,device=device)
        self.target=torch.as_tensor(y,dtype=dtype,device=device)
        self.weight=torch.as_tensor(w,dtype=dtype,device=device)
        if (not bool(torch.isfinite(self.target).all()) or not bool(torch.isfinite(self.x).all())
                or not bool(torch.isfinite(self.weight).all())
                or not np.array_equal((self.weight>0).cpu().numpy(),legal)):
            raise ValueError('Target overflow or lost positive weight after numeric conversion')
        self.denominator=1.
        self.tensor_bytes=sum(t.numel()*t.element_size() for t in (self.x,self.target,self.weight))
        h=hashlib.sha256(encoded({k:grouped[k] for k in
            ('method','representation','registry_sha256','player','keys','contexts','target_units','within_observation_variance')}))
        for a in (x,y,w):
            h.update(str(a.dtype).encode());h.update(encoded(list(a.shape)));h.update(a.tobytes(order='C'))
        self.identity=h.hexdigest()
        guard()

    def objective(self, model, chunk_size, guard, backward=False):
        import torch
        if type(chunk_size) is not int or chunk_size < 1:
            raise ValueError('Positive ordered chunk size required')
        parameter=next(model.parameters())
        if parameter.dtype != self.x.dtype or parameter.device != self.x.device:
            raise ValueError('Model and objective backends differ')
        total=torch.zeros((),dtype=torch.float64,device=self.x.device)
        for start in range(0,len(self.x),chunk_size):
            guard();stop=min(start+chunk_size,len(self.x))
            loss=((model(self.x[start:stop])-self.target[start:stop]).square()*self.weight[start:stop]).sum()
            total+=loss.detach().double()
            if backward:loss.backward()
        value=float(total)
        if not np.isfinite(value):raise ValueError('Nonfinite context-weighted objective')
        return value


def fit(registry, reservoirs, *, player, context_weights, seed, steps, device,
        chunk_size, guard, learning_rate=.003, captured=True):
    """Every step accumulates all contexts' gradients before one Adam update."""
    import torch
    if device != 'cuda' or type(steps) is not int or steps < 1 or type(captured) is not bool:
        raise ValueError('CUDA and explicit positive fit count/capture mode required')
    if type(chunk_size) is not int or chunk_size < 1 or not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError('Positive chunk size and learning rate required')
    if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
        raise ValueError('Disable TF32 for the registered numeric path')
    guard();began=time.monotonic()
    grouped=prepare(registry,reservoirs,player=player,context_weights=context_weights)
    model=fresh_network(seed,registry.manifest['representation']['input_width']).to(device)
    prepared=PreparedContextObjective(grouped,device,dtype=torch.float32,guard=guard)
    optimizer=torch.optim.Adam(model.parameters(),lr=learning_rate,betas=tuple(OPTIMIZER['betas']),
        eps=OPTIMIZER['eps'],weight_decay=0.,amsgrad=False,foreach=False,fused=False)
    with torch.no_grad():before=prepared.objective(model,chunk_size,guard)
    setup=time.monotonic()-began;capture_seconds=0.
    if captured:
        start=time.monotonic();stream=capture_stream(torch)
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(2):
                model.zero_grad(set_to_none=True);gradient_tensor(prepared,model,chunk_size)
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize();guard()
        graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph,stream=stream):
            for parameter in model.parameters():parameter.grad.zero_()
            total=gradient_tensor(prepared,model,chunk_size)
        torch.cuda.synchronize();capture_seconds=time.monotonic()-start
    guard();start=time.monotonic()
    for _ in range(steps):
        guard()
        if captured:
            graph.replay();value=float(total)
        else:
            model.zero_grad(set_to_none=True)
            value=prepared.objective(model,chunk_size,guard,backward=True)
        if not np.isfinite(value):raise ValueError('Nonfinite captured gradient loss')
        optimizer.step()
    torch.cuda.synchronize();fit_seconds=time.monotonic()-start
    with torch.no_grad():after=prepared.objective(model,chunk_size,guard)
    if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
        raise ValueError('Nonfinite fitted parameters')
    return export_network(model),dict(runtime=RUNTIME,captured=captured,player=player,device=device,
        registry_sha256=registry.sha256,representation=grouped['representation'],objective_method=METHOD,
        objective_sha256=prepared.identity,target_units=grouped['target_units'],contexts=grouped['contexts'],
        seed=seed,steps=steps,learning_rate=learning_rate,chunk_size=chunk_size,
        initialization=INITIALIZATION,optimizer=OPTIMIZER,grouped_observations=len(grouped['keys']),
        normalized_grouped_loss_before=before,normalized_grouped_loss_after=after,
        normalized_within_observation_variance=grouped['within_observation_variance'],
        prepared_tensor_bytes=prepared.tensor_bytes,setup_seconds=setup,
        graph_capture_seconds=capture_seconds,optimizer_seconds=fit_seconds)
