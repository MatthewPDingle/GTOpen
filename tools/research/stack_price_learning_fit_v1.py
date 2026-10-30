"""Fixed-budget CUDA supervised diagnostic; not a preflop policy checkpoint."""
import hashlib
from pathlib import Path
import time
import numpy as np
import torch
from sampled_visible_initialization_v1 import fresh_visible_network
from stack_price_reference_v1 import decision_regret

MODEL_TYPE='conditional-river-price-diagnostic-v1'
PRICE_EDGES=np.asarray([0.,.1,.2,.3,.4,.5,1.01])
CATEGORIES=('high_card','pair','two_pair','trips','straight','flush','full_house','quads','straight_flush')

def fresh(seed,width,device):
    if width not in (302,362):raise ValueError('Registered feature widths only')
    models=[]
    for actor in (0,1):
        base=fresh_visible_network(seed+1000*actor)
        if width==302:model=base
        else:
            with torch.random.fork_rng(devices=[]):
                model=torch.nn.Sequential(torch.nn.Linear(362,64),torch.nn.ReLU(),
                    torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
                with torch.no_grad():
                    model[0].weight.zero_();model[0].weight[:,:302].copy_(base[0].weight)
                    model[0].bias.copy_(base[0].bias)
                    for layer in (2,4):model[layer].load_state_dict(base[layer].state_dict())
        models.append(model)
    return torch.nn.ModuleList(models).to(device)

def scores(models,x,actors):
    # Both heads run in one batch; avoid per-step dynamic nonzero/CPU synchronization.
    return torch.where(actors[:,None]==0,models[0](x),models[1](x))

class Dataset:
    def __init__(self,boards,contexts):
        self.board_count=len(boards);self.contexts=contexts
        self.card_np=np.concatenate([b['features'] for b in boards])
        counts=np.concatenate([b['counts'] for b in boards])
        self.equity_np=(counts[:,0]+counts[:,1]/2)/990
        self.category_np=np.argmax(self.card_np[:,269:278],axis=1)
        self.economics_np=np.concatenate([p['economics'] for p in contexts])
        state=np.concatenate([p['features'] for p in contexts])
        self.lengths=np.asarray([len(p['rows']) for p in contexts],dtype=np.int64)
        self.offsets=np.r_[0,np.cumsum(self.lengths)[:-1]]
        self.cards=torch.as_tensor(self.card_np,device='cuda');self.public=torch.as_tensor(state,device='cuda')
        self.equity=torch.as_tensor(self.equity_np,device='cuda');self.economics=torch.as_tensor(self.economics_np,device='cuda')
        self.lengths_gpu=torch.as_tensor(self.lengths,device='cuda');self.offsets_gpu=torch.as_tensor(self.offsets,device='cuda')

    def assemble(self,states,cards,width):
        x=(self.cards[cards,:width]+self.public[states,:width]).contiguous()
        e=self.economics[states]
        target=(self.equity[cards]*e[:,1]-e[:,2])/e[:,0]
        return x,e[:,3].to(torch.long),target.to(torch.float32)

    def sample(self,n,width,generator):
        context=torch.randint(len(self.contexts),(n,),device='cuda',generator=generator)
        u=torch.rand(n,device='cuda',generator=generator,dtype=torch.float64)
        states=self.offsets_gpu[context]+torch.floor(u*self.lengths_gpu[context]).to(torch.long)
        cards=torch.randint(len(self.card_np),(n,),device='cuda',generator=generator)
        return self.assemble(states,cards,width)

def probabilities(raw):
    x=np.asarray(raw,dtype=np.float64)[:,:2]
    if not np.isfinite(x).all():raise ValueError('Nonfinite learned scores')
    positive=np.maximum(x,0);total=positive.sum(1)
    p=np.divide(positive[:,1],total,out=np.zeros(len(x)),where=total>0)
    zero=total<=0;p[zero]=np.argmax(x[zero],axis=1)
    return p

def evaluate(models,data,width,guard,*,detail):
    records=[];models.eval();nc=len(data.card_np)
    with torch.no_grad():
        for context_id,context in enumerate(data.contexts):
            offset=int(data.offsets[context_id]);nstates=int(data.lengths[context_id]);n=nc*nstates
            raw=np.empty((n,2),dtype=np.float32)
            for lo in range(0,n,8192):
                guard();hi=min(n,lo+8192);idx=torch.arange(lo,hi,device='cuda')
                x,actor,_=data.assemble(offset+idx//nc,idx%nc,width)
                raw[lo:hi]=scores(models,x,actor)[:,:2].cpu().numpy()
            e=data.economics_np[offset:offset+nstates]
            stack=float(context['stack'])
            d=(e[:,1,None]*data.equity_np[None,:]-e[:,2,None]).reshape(-1)
            p=probabilities(raw);regret=decision_regret(p,d)
            value_error=(raw[:,1].astype(np.float64)*stack-d)**2+(raw[:,0].astype(np.float64)*stack)**2
            mask_near=abs(d)>1e-4*stack
            mistakes=((d>0)!=(p>=.5))&mask_near
            def summary(mask):
                count=int(np.count_nonzero(mask))
                if not count:return dict(rows=0)
                v=regret[mask];close=mask_near[mask]
                return dict(rows=count,mean_regret_bb=float(v.mean()),mean_regret_stack_fraction=float(v.mean()/stack),
                    p95_regret_bb=float(np.quantile(v,.95)),p99_regret_bb=float(np.quantile(v,.99)),
                    maximum_regret_bb=float(v.max()),mean_legal_value_squared_error_bb=float(value_error[mask].mean()/2),
                    decisions_outside_indifference_band=int(close.sum()),
                    majority_action_error_rate=float(mistakes[mask].sum()/close.sum()) if close.sum() else None,
                    always_fold_regret_bb=float(np.maximum(d[mask],0).mean()),
                    always_call_regret_bb=float(np.maximum(-d[mask],0).mean()))
            if detail:
                record=dict(stack=stack,**summary(np.ones(n,dtype=bool)))
                actors=np.repeat(e[:,3].astype(int),nc)
                price_band=np.repeat(np.searchsorted(PRICE_EDGES,e[:,4],side='right')-1,nc)
                category=np.tile(data.category_np,nstates)
                record['seats']=[dict(actor=a,**summary(actors==a)) for a in (0,1)]
                record['price_bands']=[dict(minimum_equity=float(PRICE_EDGES[b]),maximum_equity=float(PRICE_EDGES[b+1]),
                    **summary(price_band==b)) for b in range(len(PRICE_EDGES)-1)]
                record['hand_groups']=[dict(name=name,**summary(category==j)) for j,name in enumerate(CATEGORIES)]
            else:record=dict(stack=stack,rows=n,mean_regret_bb=float(regret.mean()),mean_regret_stack_fraction=float(regret.mean()/stack))
            records.append(record)
    return dict(contexts=records,context_balanced_mean_regret_stack_fraction=float(np.mean([r['mean_regret_stack_fraction'] for r in records])),
                context_balanced_mean_regret_bb=float(np.mean([r['mean_regret_bb'] for r in records])),
                probability_rule='Positive-score regret matching; nonpositive rows choose the maximum legal score.',
                rows=sum(r['rows'] for r in records))

def save_models(path,models):
    path=Path(path)
    if path.exists():raise FileExistsError(path)
    arrays={f'p{actor}.{name}':value.detach().cpu().numpy() for actor,m in enumerate(models) for name,value in m.state_dict().items()}
    with path.open('xb') as f:np.savez_compressed(f,**arrays)
    return dict(file=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def load_models(reference,seed,width):
    path=Path(reference['file'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=reference['sha256']:raise ValueError('Changed checkpoint')
    models=fresh(seed,width,'cuda')
    with np.load(path,allow_pickle=False) as arrays:
        expected={f'p{actor}.{name}' for actor,m in enumerate(models) for name in m.state_dict()}
        if set(arrays.files)!=expected:raise ValueError('Wrong checkpoint keys')
        for actor,m in enumerate(models):
            state={name:torch.as_tensor(arrays[f'p{actor}.{name}'].copy(),device='cuda') for name in m.state_dict()}
            if any(not bool(torch.isfinite(x).all()) for x in state.values()):raise ValueError('Nonfinite checkpoint')
            m.load_state_dict(state,strict=True)
    return models

def fit(seed,width,train,validation,store,guard,progress):
    start=time.monotonic();models=fresh(seed,width,'cuda')
    generator=torch.Generator(device='cuda');generator.manual_seed(seed+100000)
    optimizer=torch.optim.Adam(models.parameters(),lr=.001,foreach=False)
    checkpoints=[];last_loss=None
    for step in range(8193):
        if step in (0,1024,4096,8192):
            guard();metrics=evaluate(models,validation,width,guard,detail=False)
            path=Path(store)/f'seed-{seed}-width-{width}-step-{step}.npz'
            saved=save_models(path,models)
            checkpoints.append(dict(step=step,validation=metrics,weights=saved))
            progress('validation',seed=seed,width=width,step=step,
                     mean_normalized_regret=metrics['context_balanced_mean_regret_stack_fraction'])
        if step==8192:break
        if step%64==0:guard()
        x,actors,target=train.sample(4096,width,generator)
        models.train();optimizer.zero_grad(set_to_none=True);pred=scores(models,x,actors)[:,:2]
        loss=(pred[:,0].square()+(pred[:,1]-target).square()).mean()/2
        loss.backward();optimizer.step()
        if step%512==0:
            last_loss=float(loss.detach())
            if not np.isfinite(last_loss):raise ValueError('Nonfinite fit loss')
            progress('fitting',seed=seed,width=width,step=step,last_normalized_loss=last_loss)
    selected=min(checkpoints,key=lambda r:(r['validation']['context_balanced_mean_regret_stack_fraction'],r['step']))
    if any(not bool(torch.isfinite(p).all()) for p in models.parameters()):raise ValueError('Nonfinite fitted model')
    torch.cuda.synchronize()
    return dict(seed=seed,width=width,steps=8192,batch_size=4096,learning_rate=.001,
                training_seconds=time.monotonic()-start,checkpoints=checkpoints,selected=selected,model_type=MODEL_TYPE)
