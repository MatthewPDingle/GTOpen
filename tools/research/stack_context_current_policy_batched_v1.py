"""Separate current-policy candidate: routed overlays and batched river features.

Not installed in the registered study. Retains canonical input validation,
float32 feature values, model inference and the original bounded LRU order.
"""
import numpy as np
from stack_context_current_policy_routed_v1 import CurrentPolicy as RoutedPolicy
from visible_summaries_vector_v1 import features
from stack_board_relative_features_bulk_v1 import relative_features_bulk


class CurrentPolicy(RoutedPolicy):
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
            ids=np.flatnonzero(phase==3)
            if len(ids):
                river_keys=lo[ids]&np.uint64((1<<42)-1)
                unique,first=np.unique(river_keys,return_index=True)
                # Keep one batch-local value per requested key, including old
                # cache hits that may be evicted and requested again below.
                values={int(key):self.relative_cache[int(key)] for key in unique
                        if int(key) in self.relative_cache}
                missing=np.asarray([int(key) not in values for key in unique])
                pending=first[missing]
                for start in range(0,len(pending),2048):
                    chosen=pending[start:start+2048]
                    batch=relative_features_bulk(cards[ids[chosen]])
                    values.update((int(river_keys[j]),row) for j,row in zip(chosen,batch))
                # Replay the original LRU order and bound. Batching changes
                # calculation order only, never the returned feature values.
                for i,key in zip(ids,river_keys):
                    key=int(key)
                    if key not in self.relative_cache:
                        self.relative_cache[key]=values[key]
                        if len(self.relative_cache)>8192:self.relative_cache.popitem(last=False)
                    self.relative_cache.move_to_end(key);extra[i]=self.relative_cache[key]
            parts.append(extra)
        result=np.concatenate(parts,axis=1).astype(np.float64)
        if result.shape!=(n,self.width) or not np.isfinite(result).all():raise ValueError('Invalid context inputs')
        return result,actor,np.asarray(arity,dtype=int),keys

