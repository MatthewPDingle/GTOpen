"""Descriptive paired effects; deliberately no policy selection or confidence claim."""
import numpy as np

PROFILES=('AA','AB','BA','BB')
CONTRASTS=('call','raise','call minus raise')
EFFECTS=('diagonal','BB policy','BTN policy','interaction')


def summarize(values, masses):
    # Values are round-robin class order: repeat, class, profile, call/raise.
    q=np.asarray(values,dtype=np.float64).reshape(64,169,4,2).transpose(1,0,2,3)
    m=np.asarray(masses,dtype=np.float64)
    assert m.shape==(169,) and np.all(m>0) and abs(m.sum()-1)<1e-12
    assert np.isfinite(q).all()
    x=np.concatenate([q,(q[:,:,:,0]-q[:,:,:,1])[:,:,:,None]],axis=3)
    aa,ab,ba,bb=[x[:,:,k,:] for k in range(4)]
    e=np.stack([bb-aa,((ba-aa)+(bb-ab))/2,((ab-aa)+(bb-ba))/2,bb-ba-ab+aa],axis=2)
    assert np.max(abs(e[:,:,0]-e[:,:,1]-e[:,:,2]))<1e-10
    rows=[]
    for c in range(169):
        def stats(a):
            return dict(mean=a.mean(0).tolist(),sample_variance=a.var(0,ddof=1).tolist(),
                standard_error=np.sqrt(a.var(0,ddof=1)/64).tolist(),
                half_means=[a[:32].mean(0).tolist(),a[32:].mean(0).tolist()])
        rows.append(dict(hand_class=c,mass=float(m[c]),samples=64,
            profiles=stats(x[c]),effects=stats(e[c])))
    mean=e.mean(1);var=e.var(1,ddof=1)
    return dict(profiles=list(PROFILES),contrasts=list(CONTRASTS),effect_names=list(EFFECTS),
        classes=rows,
        weighted_effect_mean=np.einsum('c,cek->ek',m,mean).tolist(),
        weighted_rms_class_effect_mean=np.sqrt(np.einsum('c,cek->ek',m,mean**2)).tolist(),
        weighted_rms_class_effect_standard_error=np.sqrt(np.einsum('c,cek->ek',m,var/64)).tolist(),
        weighted_rms_class_profile_standard_error=np.sqrt(np.einsum('c,cpk->pk',m,x.var(1,ddof=1)/64)).tolist(),
        accuracy_qualified=False,simultaneous_confidence_claim=False)
