"""Input-disjoint fixed-data splits, with training-only target normalization."""
import hashlib
import numpy as np

SALT='gtopen-later-fit-holdout-20260928-v1'
NAMES=('train','validation','test')


def digest(array):
    a=np.ascontiguousarray(array)
    return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()


def prepare(active,arity,values,weights,*,salt=SALT):
    active=np.asarray(active);arity=np.asarray(arity);values=np.asarray(values,dtype=np.float64)
    weights=np.asarray(weights,dtype=np.float64);n=len(active)
    assert n > 0 and active.shape==(n,36) and active.dtype.kind in 'iu'
    assert arity.shape==(n,) and arity.dtype.kind in 'iu' and values.shape==(n,4) and weights.shape==(n,)
    assert np.all((active>=0)&(active<269)) and np.all(np.diff(active.astype(int),axis=1)>0)
    assert np.all((arity>=2)&(arity<=4)) and np.isfinite(values).all()
    assert np.isfinite(weights).all() and np.all((weights>0)&(weights<=65536))
    legal=np.arange(4)[None,:]<arity[:,None]
    assert not np.any(values[~legal])
    visible,inverse=np.unique(active,axis=0,return_inverse=True)
    # Same visible input always has the same split, even across distinct native
    # keys or legal menus. Endianness and salt separator are explicit.
    buckets=np.array([int.from_bytes(hashlib.sha256(salt.encode()+b'\0'+row.astype('<u2').tobytes()).digest()[:8],
        'big')%10000 for row in visible])
    splits=np.where(buckets<7000,0,np.where(buckets<8500,1,2)).astype(np.uint8)
    row_splits=splits[inverse];assert set(row_splits)=={0,1,2}
    train=row_splits==0
    scale=max(.01,float(np.sqrt(np.sum(values[train]**2*weights[train,None])/(4*weights[train].sum()))))
    # Group equal visible inputs and equal legal menus: masks remain exact.
    geometry=np.column_stack([active,arity]);unique,first,group=np.unique(geometry,axis=0,return_index=True,return_inverse=True)
    count=np.bincount(group);mass=np.bincount(group,weights=weights)
    sums=np.zeros((len(unique),4));np.add.at(sums,group,values*weights[:,None])
    means=sums/mass[:,None];group_splits=row_splits[first]
    assert np.array_equal(group_splits[group],row_splits)
    result={};metadata=[]
    for index,name in enumerate(NAMES):
        selected=group_splits==index;raw=row_splits==index
        group_arity=arity[first[selected]].copy();group_mass=mass[selected]
        denominator=float(np.dot(group_mass,group_arity.astype(float)))
        residual=values[raw]-means[group[raw]]
        variance=float(np.sum(residual**2*weights[raw,None]*legal[raw])/denominator/scale**2)
        data=dict(active=active[first[selected]].copy(),arity=group_arity,masses=group_mass.copy(),
            targets=means[selected]/scale,scale=scale,denominator=denominator,variance=variance,
            counts=count[selected].copy(),examples=int(raw.sum()),method='source-deal-weighted-visible-objective-v1')
        assert np.isfinite(data['targets']).all() and variance>=0
        result[name]=data
        metadata.append(dict(name=name,examples=data['examples'],visible_inputs=int(np.count_nonzero(splits==index)),
            grouped_input_menus=len(data['active']),source_weight=float(group_mass.sum()),
            legal_target_mass=denominator,active_sha256=digest(data['active']),arity_sha256=digest(group_arity),
            targets_sha256=digest(data['targets']),masses_sha256=digest(group_mass)))
    # A separate set test protects against accidental grouping/split changes.
    sets=[{row.astype('<u2').tobytes() for row in result[name]['active']} for name in NAMES]
    assert all(sets[i].isdisjoint(sets[j]) for i in range(3) for j in range(i))
    assert sum(len(s) for s in sets)==len(visible)
    return result,dict(salt=salt,training_scale=scale,row_splits_sha256=digest(row_splits),
        source_rows=n,unique_visible_inputs=len(visible),duplicate_visible_rows=n-len(visible),
        source_inputs_sha256=digest(active),splits=metadata),row_splits


def grouped_loss(prediction,data):
    prediction=np.asarray(prediction,dtype=float)
    assert prediction.shape==data['targets'].shape and np.isfinite(prediction).all()
    legal=np.arange(4)[None,:]<data['arity'][:,None]
    return float(np.sum((prediction-data['targets'])**2*legal*data['masses'][:,None])/data['denominator'])


def direct_loss(prediction,arity,values,weights,scale):
    legal=np.arange(4)[None,:]<np.asarray(arity)[:,None]
    return float(np.sum((prediction-values/scale)**2*legal*weights[:,None])/np.dot(weights,arity))


def control():
    # Synthetic sorted visible vectors are sufficient for split/loss arithmetic;
    # they are not asserted to encode legal poker hands or passed to inference.
    unique=np.array([list(range(35))+[35+i] for i in range(100)],dtype=np.uint16)
    active=np.repeat(unique,3,axis=0);n=len(active)
    arity=np.tile([2,3,2],100).astype(np.uint8)
    weights=(1+np.arange(n)%7)/3
    values=np.array([[float((i%11)-5)*(a+1) for a in range(4)] for i in range(n)])
    values[np.arange(4)[None,:]>=arity[:,None]]=0
    data,proof,split=prepare(active,arity,values,weights)
    assert proof['duplicate_visible_rows']==200
    assert all(len(set(split[i:i+3]))==1 for i in range(0,n,3))
    def prediction(a):return np.column_stack([a[:,-1]/100+k/10 for k in range(4)])
    maximum=0.
    for index,name in enumerate(NAMES):
        raw=split==index;part=data[name]
        original=direct_loss(prediction(active[raw]),arity[raw],values[raw],weights[raw],proof['training_scale'])
        grouped=grouped_loss(prediction(part['active']),part)+part['variance']
        maximum=max(maximum,abs(original-grouped));assert abs(original-grouped)<1e-12
    changed=values.copy();changed[split!=0]*=1000
    _,other,new_splits=prepare(active,arity,changed,weights)
    assert proof['training_scale']==other['training_scale'] and np.array_equal(split,new_splits)
    perm=np.random.Generator(np.random.PCG64(9282201)).permutation(n)
    _,reordered,new_splits=prepare(active[perm],arity[perm],values[perm],weights[perm])
    assert np.array_equal(new_splits,split[perm])
    assert abs(reordered['training_scale']-proof['training_scale'])<1e-12
    return dict(passed=True,duplicate_inputs_kept_together=True,differing_menus_kept_together=True,
        heldout_targets_cannot_change_scale=True,row_order_independent=True,
        maximum_direct_grouped_loss_difference=maximum,synthetic_rows=n)
