"""Fresh fixed 32768-update chains with paired short/long validation selection."""
from pathlib import Path
import time
import numpy as np
import torch
from stack_price_learning_fit_v1 import fresh,scores,evaluate,save_models,MODEL_TYPE

CHECKPOINTS=(0,1024,4096,8192,16384,32768)

def fit_chain(seed,train,validation,store,guard,progress):
    start=time.monotonic();models=fresh(seed,362,'cuda')
    generator=torch.Generator(device='cuda');generator.manual_seed(seed+100000)
    optimizer=torch.optim.Adam(models.parameters(),lr=.001,foreach=False)
    checkpoints=[];elapsed_at_step={}
    for step in range(32769):
        if step in CHECKPOINTS:
            guard();metrics=evaluate(models,validation,362,guard,detail=False)
            saved=save_models(Path(store)/f'seed-{seed}-width-362-step-{step}.npz',models)
            checkpoints.append(dict(step=step,validation=metrics,weights=saved))
            elapsed_at_step[step]=time.monotonic()-start
            progress('validation',seed=seed,width=362,step=step,
                mean_normalized_regret=metrics['context_balanced_mean_regret_stack_fraction'])
        if step==32768:break
        if step%64==0:guard()
        x,actors,target=train.sample(4096,362,generator)
        models.train();optimizer.zero_grad(set_to_none=True);pred=scores(models,x,actors)[:,:2]
        loss=(pred[:,0].square()+(pred[:,1]-target).square()).mean()/2
        loss.backward();optimizer.step()
        if step%1024==0:
            measured=float(loss.detach())
            if not np.isfinite(measured):raise ValueError('Nonfinite training loss')
            progress('fitting',seed=seed,width=362,step=step,last_normalized_loss=measured)
    if any(not bool(torch.isfinite(p).all()) for p in models.parameters()):raise ValueError('Nonfinite model')
    torch.cuda.synchronize()
    arms=[]
    for name,limit in (('short',8192),('long',32768)):
        permitted=[c for c in checkpoints if c['step']<=limit]
        selected=min(permitted,key=lambda c:(c['validation']['context_balanced_mean_regret_stack_fraction'],c['step']))
        arms.append(dict(seed=seed,width=362,arm=name,steps=limit,batch_size=4096,learning_rate=.001,
            fitting_boards=512,checkpoints=permitted,selected=selected,training_seconds=elapsed_at_step[limit],
            model_type=MODEL_TYPE,shared_training_prefix=True))
    return dict(seed=seed,steps=32768,training_seconds=time.monotonic()-start,checkpoints=checkpoints,arms=arms)
