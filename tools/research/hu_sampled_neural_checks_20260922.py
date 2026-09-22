"""Independent finite sampler and bounded-reservoir checks, without CUDA."""
from itertools import permutations
import numpy as np
from hu_sampled_neural_control_20260922 import (
    Reservoir, geometry, sample_batch, exact_average_increment, flat_policy)
from hu_sampled_convergence_run_20260922 import step


def check(data):
    features, mask, actors = geometry(data)
    assert features.shape == (60,28) and (features.sum(axis=1)==3).all()
    # Same observable key always has identical inputs across hidden deals.
    comparisons=0
    for n,a in enumerate(data['arity']):
        if not a: continue
        for d,deal in enumerate(data['deals']):
            info=data['deal_infos'][d][n]
            node,own,board=data['information_keys'][info]
            assert own==deal[data['actors'][n]] and node==n
            assert board in (-1,deal[2])
            x=np.zeros(28);x[n]=1;x[19+own]=1;x[23+board+1]=1
            assert np.array_equal(x,features[info])
            comparisons+=1
    uniform=mask/mask.sum(axis=1,keepdims=True)
    pure=np.zeros_like(uniform)
    for i in range(len(pure)):pure[i,i%int(mask[i].sum())]=1
    rng=np.random.default_rng(90222)
    random=rng.random(mask.shape)*mask;random/=random.sum(axis=1,keepdims=True)
    max_error=0.;zero_own_records=0;traversals=0
    for p in (uniform,pure,random):
        _,avg=step(data,0,flat_policy(data,p),0,1)
        assert np.max(np.abs(np.asarray(avg)-flat_policy(data,exact_average_increment(data,p))))<1e-13
        for case in range(2):
            for updater in range(2):
                deals=np.arange(24);draws=rng.random((24,19))
                adv,avg,values=sample_batch(data,case,p,deals,draws,updater)
                expected_adv=[];expected_avg=[];roots=[]
                for d in deals:
                    def walk(n,own_reach):
                        nonlocal zero_own_records
                        arity=data['arity'][n]
                        if not arity:return data['cases'][case]['utilities'][d][n][updater]
                        info=data['deal_infos'][d][n];s=p[info];children=data['children'][n]
                        if data['actors'][n]!=updater:
                            expected_avg.append((info,s.copy()))
                            cumulative=0.;chosen=arity-1
                            for a in range(arity):
                                cumulative+=s[a]
                                if draws[d,n]<cumulative:chosen=a;break
                            return walk(children[chosen],own_reach)
                        v=np.array([walk(children[a],own_reach*s[a]) for a in range(arity)])
                        value=float(v@s[:arity]);r=np.zeros(3);r[:arity]=v-value
                        expected_adv.append((info,r))
                        if own_reach==0:zero_own_records+=1
                        return value
                    roots.append(walk(0,1.));traversals+=1
                max_error=max(max_error,float(np.max(np.abs(values-roots))))
                # Compare multisets, preserving every repeated occurrence.
                def sort_records(records):
                    return sorted((int(i),*map(float,v)) for i,v in records)
                for actual,expected in ((adv,expected_adv),(avg,expected_avg)):
                    aa=sort_records(zip(*actual));bb=sort_records(expected)
                    assert len(aa)==len(bb)
                    assert [r[0] for r in aa]==[r[0] for r in bb]
                    max_error=max(max_error,float(np.max(np.abs(np.array(aa)-np.array(bb)))))
    assert max_error<1e-12 and zero_own_records>0
    # Exhaust all 5! priority orderings: each record must occur in exactly K/N
    # of size-2 reservoirs, independent of how the stream is batched.
    counts=np.zeros(5,dtype=int)
    class Fixed:
        def __init__(self,v):self.v=np.asarray(v,dtype=float)/6;self.offset=0
        def random(self,n):
            out=self.v[self.offset:self.offset+n];self.offset+=n;return out
    for priority in permutations(range(1,6)):
        full=Reservoir(2,0);chunked=Reservoir(2,0)
        full.rng=Fixed(priority);chunked.rng=Fixed(priority)
        ids=np.arange(5);v=np.repeat(ids[:,None],3,axis=1)
        full.add(ids,v);chunked.add(ids[:2],v[:2]);chunked.add(ids[2:],v[2:])
        assert sorted(full.ids)==sorted(chunked.ids)
        assert full.seen==chunked.seen==5 and len(full.ids)==2
        counts[full.ids]+=1
    assert np.all(counts==48)
    repeat=Reservoir(10,1);repeat.add([3,3,3],np.eye(3))
    assert repeat.seen==len(repeat.ids)==3 and len(np.unique(repeat.values,axis=0))==3
    return dict(passed=True,recursive_replay_traversals=traversals,
                maximum_sampler_error=max_error,zero_own_reach_records_verified=zero_own_records,
                observable_input_checks=comparisons,reservoir_priority_permutations=120,
                inclusion_counts=counts.tolist(),exact_average_contract_checked=True,
                duplicate_records_preserved=True,production_modified=False)
