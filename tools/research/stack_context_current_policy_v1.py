"""Frozen full-context policy for native training/evaluation workers.

Score-only fixed-board rows may omit ancestor indices. They can be scored as
current-policy decisions, but never masquerade as a played-policy average.
Normal native query batches retain and validate their actual own histories.
"""
import copy
from collections import OrderedDict
import numpy as np
import stack_context_full_policy_v1 as full
from weighted_preflop_table_v1 import Table
from visible_summaries_vector_v1 import features
from stack_board_relative_features_v1 import relative_features
from sampled_physical_bank_v1 import histories
from board_river_bounds_math_v1 import policy


class CurrentPolicy:
    def __init__(self,model,registry,*,context_sha256,resources,device='cpu'):
        if device not in ('cpu','cuda'):raise ValueError('Explicit CPU/CUDA inference required')
        overrides=full.validate(model,registry,resources)
        self.context_sha256=context_sha256;self.context_source=registry.source(context_sha256)
        self.entry=copy.deepcopy(registry._get(context_sha256));self.width=registry.manifest['representation']['input_width']
        self.generation=model['generation'];self.device=device;self.relative_cache=OrderedDict()
        self.tables=[Table(t,self.context_source) for t in model['shared']['preflop_tables'].get(context_sha256,[]) if t is not None]
        if context_sha256 in overrides:self.tables.extend(overrides[context_sha256])
        self.weights=[]
        if device=='cuda':
            import torch
            if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:raise ValueError('Disable TF32')
        for net in model['shared']['networks']:
            layers=[]
            for layer,shape in enumerate(((64,self.width),(64,64),(4,64))):
                w=np.asarray(net[f'w{layer}'],np.float32).astype(np.float64).reshape(shape)
                b=np.asarray(net[f'b{layer}'],np.float32).astype(np.float64)
                if device=='cuda':w,b=torch.tensor(w,device='cuda'),torch.tensor(b,device='cuda')
                layers.append((w,b))
            self.weights.append(layers)

    def _features(self,observations):
        if not observations:raise ValueError('Nonempty native observations required')
        x=features(observations);n=len(x)
        def column(start,width):return np.argmax(x[:,start:start+width],axis=1)
        actor=column(133,2);phase=column(135,4);node=column(139,16)
        cards=np.column_stack([np.where(column(19*i,14)==13,63,
            4*column(19*i,14)+column(19*i+14,5)) for i in range(7)]).astype(np.uint64)
        lo=(actor.astype(np.uint64)<<np.uint64(42))|np.sum(cards<<np.arange(0,42,6,dtype=np.uint64),axis=1,dtype=np.uint64)
        tokens=np.column_stack([column(155+6*i,6) for i in range(19)]).astype(np.uint64)
        if np.any((phase==0)&np.any(tokens!=0,axis=1)) or np.any((phase>0)&(np.sum(tokens==5,axis=1)!=phase-1)):
            raise ValueError('Visible street/history mismatch')
        h=np.ones(n,dtype=np.uint64)
        for t in tokens.T:
            live=t>0;h[live]=(h[live]<<np.uint64(3))|t[live]
        if np.any(h>=2**59):raise ValueError('Public history overflow')
        hi=np.where(phase==0,node.astype(np.uint64)+np.uint64(1),
                    np.uint64(1<<63)|(h<<np.uint64(4))|node.astype(np.uint64))
        prices=[];arity=[];keys=[]
        for i,o in enumerate(observations):
            for name,value in (('hi',hi[i]),('lo',lo[i])):
                if not isinstance(o[name],str) or o[name]!=str(int(value)):
                    raise ValueError('Canonical keys disagree with native visible features')
            if o['hi'] not in self.entry['lookup']:raise ValueError('Unknown public state in this context')
            public,price=self.entry['lookup'][o['hi']]
            if (any(type(o[k]) is not int for k in ('actor','phase','n'))
                    or (o['actor'],o['phase'],o['n'])!=(public['actor'],public['phase'],len(public['actions']))
                    or (o['actor'],o['phase'])!=(actor[i],phase[i])):
                raise ValueError('Native actor, street or legal menu disagrees with context')
            arity.append(o['n']);prices.append(price);keys.append((self.context_sha256,o['hi'],o['lo']))
        parts=[x,np.asarray(prices,np.float32)]
        if self.width==387:
            extra=np.zeros((n,25),np.float32)
            for i in np.flatnonzero(phase==3):
                key=int(lo[i])&((1<<42)-1)
                if key not in self.relative_cache:
                    row=cards[i].astype(int).tolist()
                    self.relative_cache[key]=relative_features(row[:2],row[2:])
                    if len(self.relative_cache)>8192:self.relative_cache.popitem(last=False)
                self.relative_cache.move_to_end(key);extra[i]=self.relative_cache[key]
            parts.append(extra)
        result=np.concatenate(parts,axis=1).astype(np.float64)
        if result.shape!=(n,self.width) or not np.isfinite(result).all():raise ValueError('Invalid context inputs')
        return result,actor,np.asarray(arity,dtype=int),keys

    def prepare(self,queries,*,require_history=True):
        if type(require_history) is not bool or queries['context_source']!=self.context_source:
            raise ValueError('Explicit history mode and matching native context required')
        obs=queries['observations']
        if require_history:
            if any('own_history' not in row for row in obs):
                raise ValueError('Native queries must retain actual own-history links')
            own=histories(obs)
        else:
            if any('own_history' in row for row in obs):
                raise ValueError('Score-only rows must not supply unchecked history links')
            if any(row['phase']==0 for row in obs):
                raise ValueError('Only fixed-board postflop rows may omit own-history links')
            own=None
        x,actor,arity,keys=self._features(obs);legal=np.arange(4)[None,:]<arity[:,None]
        table=legal.astype(np.float64)/arity[:,None];mask=np.zeros(len(obs),dtype=bool)
        for overlay in self.tables:
            table,ids=overlay.apply(obs,table);mask[np.asarray(ids,dtype=int)]=True
        return dict(features=x,actors=actor,arity=arity,legal=legal,keys=keys,own_history=own,
                    table=table,mask=mask,context_sha256=self.context_sha256,owner=self)

    def infer(self,prepared):
        if prepared.get('owner') is not self or prepared.get('context_sha256')!=self.context_sha256:
            raise ValueError('Prepared rows belong to another frozen policy/context')
        scores=np.zeros((len(prepared['features']),4))
        if self.device=='cuda':import torch
        for actor,layers in enumerate(self.weights):
            ids=np.flatnonzero(prepared['actors']==actor)
            if not len(ids):continue
            y=prepared['features'][ids]
            if self.device=='cuda':y=torch.as_tensor(y,device='cuda')
            for i,(w,b) in enumerate(layers):
                if i==0 and self.width==387:
                    if self.device=='cpu':y=(y[:,:362].copy()@w[:,:362].copy().T+b)+y[:,362:].copy()@w[:,362:].copy().T
                    else:y=(y[:,:362].contiguous()@w[:,:362].contiguous().T+b)+y[:,362:].contiguous()@w[:,362:].contiguous().T
                else:y=y@w.T+b
                if i<2:y=np.maximum(y,0.) if self.device=='cpu' else torch.relu(y)
            scores[ids]=y if self.device=='cpu' else y.cpu().numpy()
        if not np.isfinite(scores).all():raise ValueError('Nonfinite full-policy scores')
        p=policy(scores,prepared['arity']);p[prepared['mask']]=prepared['table'][prepared['mask']]
        if not np.isfinite(p).all() or np.any(p<0) or np.any(p[~prepared['legal']]) or np.max(abs(p.sum(1)-1))>1e-12:
            raise ValueError('Invalid current full-context policy')
        return p

    def score_rows(self,context_source,observations):
        return self.infer(self.prepare(dict(context_source=context_source,observations=observations),require_history=False))
