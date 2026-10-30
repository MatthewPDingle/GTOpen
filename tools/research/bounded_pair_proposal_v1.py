"""Exact-rational proposal prototype; no poker, floating sampler or policy access."""
from fractions import Fraction as F


def rational(x):
    if type(x) not in (int,F):raise ValueError('Explicit exact rational required')
    return F(x)


def proposal(probabilities, lower, upper):
    p=tuple(map(rational,probabilities))
    lo=tuple(tuple(map(rational,row)) for row in lower)
    hi=tuple(tuple(map(rational,row)) for row in upper)
    if not p or min(p)<0 or sum(p)!=1:raise ValueError('Normalized finite support required')
    if len(lo)!=len(p) or len(hi)!=len(p):raise ValueError('One interval row per support point')
    k=len(lo[0])
    if not k or any(len(a)!=k or len(b)!=k for a,b in zip(lo,hi)):raise ValueError('Common nonempty contrast shape')
    if any(a>b for l,u in zip(lo,hi) for a,b in zip(l,u)):raise ValueError('Ordered bounds required')
    c=tuple(tuple((a+b)/2 for a,b in zip(l,u)) for l,u in zip(lo,hi))
    width=tuple(max((b-a)/2 for a,b in zip(l,u)) for l,u in zip(lo,hi))
    z=sum(a*b for a,b in zip(p,width))
    center=tuple(sum(a*c[i][j] for i,a in enumerate(p)) for j in range(k))
    q=tuple(a*b/z if z else F(0) for a,b in zip(p,width))
    return dict(p=p,lower=lo,upper=hi,c=c,b=width,z=z,center=center,q=q,
                deterministic=z==0)


def observation(plan,index,values):
    if type(index) is not int or not 0<=index<len(plan['p']):raise ValueError('Invalid support index')
    x=tuple(map(rational,values))
    if len(x)!=len(plan['center']):raise ValueError('Contrast shape changed')
    if not plan['q'][index]:raise ValueError('Unsampled zero-mass support')
    if any(not a<=v<=b for v,a,b in zip(x,plan['lower'][index],plan['upper'][index])):
        raise ValueError('Outcome outside prospective envelope; do not clip')
    return tuple(center+plan['z']*(v-c)/plan['b'][index]
                 for center,v,c in zip(plan['center'],x,plan['c'][index]))
