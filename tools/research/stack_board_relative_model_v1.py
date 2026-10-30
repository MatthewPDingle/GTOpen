"""Paired 362/387-input diagnostic models with exact neutral extension."""
import hashlib
from pathlib import Path
import time
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from stack_price_learning_fit_v1 import fresh as original_fresh,scores,evaluate,save_models

MODEL_TYPE='conditional-river-relative-board-diagnostic-v1'
CHECKPOINTS=(0,1024,4096,8192)

class RelativeLinear(nn.Linear):
    """Keep the original GEMM shape while adding a trainable zero-start branch."""
    def forward(self,x):
        if x.shape[-1]!=387:raise ValueError('387 visible/public input columns required')
        return (F.linear(x[...,:362].contiguous(),self.weight[:,:362].contiguous(),self.bias)
                +F.linear(x[...,362:].contiguous(),self.weight[:,362:].contiguous(),None))

def fresh(seed,width,device='cpu'):
    if width==362:return original_fresh(seed,362,device)
    if width!=387:raise ValueError('Only the registered 362/387 input widths are legal')
    base=original_fresh(seed,362,'cpu');models=[]
    with torch.random.fork_rng(devices=[]):
        for original in base:
            model=nn.Sequential(RelativeLinear(387,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,4))
            with torch.no_grad():
                model[0].weight.zero_();model[0].weight[:,:362].copy_(original[0].weight)
                model[0].bias.copy_(original[0].bias)
                for layer in (2,4):model[layer].load_state_dict(original[layer].state_dict())
            models.append(model)
    return nn.ModuleList(models).to(device)

def load_models(reference,seed,width,device='cuda'):
    path=Path(reference['file'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=reference['sha256']:raise ValueError('Changed model checkpoint')
    models=fresh(seed,width,device)
    with np.load(path,allow_pickle=False) as z:
        expected={f'p{a}.{k}' for a,m in enumerate(models) for k in m.state_dict()}
        if set(z.files)!=expected:raise ValueError('Checkpoint keys do not match registered model')
        for a,m in enumerate(models):
            state={k:torch.as_tensor(z[f'p{a}.{k}'].copy(),device=device) for k in m.state_dict()}
            if any(not bool(torch.isfinite(v).all()) for v in state.values()):raise ValueError('Nonfinite checkpoint')
            m.load_state_dict(state,strict=True)
    return models

def rng_hash(generator):
    return hashlib.sha256(generator.get_state().cpu().numpy().tobytes()).hexdigest()

def fit(seed,width,train,validation,store,guard,progress):
    started=time.monotonic();models=fresh(seed,width,'cuda')
    generator=torch.Generator(device='cuda');generator.manual_seed(seed+100000)
    optimizer=torch.optim.Adam(models.parameters(),lr=.001,foreach=False)
    checkpoints=[];first_batch=None
    for step in range(8193):
        if step in CHECKPOINTS:
            guard();metrics=evaluate(models,validation,width,guard,detail=False)
            weights=save_models(Path(store)/f'seed-{seed}-width-{width}-step-{step}.npz',models)
            checkpoints.append(dict(step=step,validation=metrics,weights=weights,batch_rng_sha256=rng_hash(generator)))
            progress('validation',seed=seed,width=width,step=step,
                mean_normalized_regret=metrics['context_balanced_mean_regret_stack_fraction'])
        if step==8192:break
        if step%64==0:guard()
        x,actors,target=train.sample(4096,width,generator)
        if step==0:
            digest=hashlib.sha256()
            for v in (x[:,:362],actors,target):digest.update(v.detach().cpu().contiguous().numpy().tobytes())
            first_batch=digest.hexdigest()
        models.train();optimizer.zero_grad(set_to_none=True);pred=scores(models,x,actors)[:,:2]
        loss=(pred[:,0].square()+(pred[:,1]-target).square()).mean()/2
        loss.backward();optimizer.step()
        if step%1024==0:
            measured=float(loss.detach())
            if not np.isfinite(measured):raise ValueError('Nonfinite training loss')
            progress('fitting',seed=seed,width=width,step=step,last_normalized_loss=measured)
    if any(not bool(torch.isfinite(p).all()) for p in models.parameters()):raise ValueError('Nonfinite model')
    selected=min(checkpoints,key=lambda c:(c['validation']['context_balanced_mean_regret_stack_fraction'],c['step']))
    torch.cuda.synchronize()
    return dict(seed=seed,width=width,steps=8192,batch_size=4096,learning_rate=.001,
        training_seconds=time.monotonic()-started,checkpoints=checkpoints,selected=selected,
        first_batch_common_columns_sha256=first_batch,model_type=MODEL_TYPE)
