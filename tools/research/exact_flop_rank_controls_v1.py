"""Research-only exact-mean target controls. Never used as policy inputs."""
import itertools
import math
import numpy as np

EVENTS=('high_once','high_twice','low_once','low_twice','over_once','over_twice','paired','trips')


def choose(n,k):
    return math.comb(int(n),k) if n>=k else 0


def validate(cards,count):
    if (len(cards)!=count or any(type(x) not in (int,np.int64,np.int32) or not 0<=x<52 for x in cards)
            or len(set(cards))!=count):
        raise ValueError('Distinct physical cards in 0..51 required')


def expectation(private):
    validate(private,4)
    high,low=sorted((private[0]//4,private[1]//4),reverse=True)
    ranks=np.full(13,4,dtype=np.int64)
    for card in private:ranks[card//4]-=1
    n=int(ranks.sum()); den=choose(n,3)
    def event(k):
        return [1-choose(n-k,3)/den,(choose(k,2)*(n-k)+choose(k,3))/den]
    distinct=sum(int(ranks[a]*ranks[b]*ranks[c]) for a,b,c in itertools.combinations(range(13),3))
    return np.array(event(int(ranks[high]))+(event(int(ranks[low])) if high!=low else [0.,0.])
                    +event(int(ranks[high+1:].sum()))+[1-distinct/den,sum(choose(x,3) for x in ranks)/den])


def features(private,flop):
    validate(private,4);validate(flop,3)
    if set(private)&set(flop):raise ValueError('Private and board cards overlap')
    high,low=sorted((private[0]//4,private[1]//4),reverse=True)
    ranks=[x//4 for x in flop]
    a=ranks.count(high);b=ranks.count(low);over=sum(x>high for x in ranks)
    return np.array([a>=1,a>=2,b>=1 and high!=low,b>=2 and high!=low,over>=1,over>=2,len(set(ranks))<3,len(set(ranks))==1],dtype=float)


def fit_coefficients(x,y):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if x.ndim!=2 or x.shape[1]!=8 or y.shape!=(len(x),3) or not len(x) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Finite training rows and three action contrasts required')
    xc=x-x.mean(0);yc=y-y.mean(0)
    # Fixed ridge on summed normal equations, not a tuned normalized penalty.
    return np.linalg.solve(xc.T@xc+np.eye(8),xc.T@yc)


def crossfit(x,y,classes):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float);classes=np.asarray(classes)
    if (x.ndim!=2 or x.shape[1]!=8 or y.shape!=(len(x),3) or classes.shape!=(len(x),)
            or classes.dtype.kind not in 'iu' or np.any((classes<0)|(classes>=169))
            or not np.isfinite(x).all() or not np.isfinite(y).all()):
        raise ValueError('Finite centered features, contrasts, and native classes required')
    parity=np.arange(len(x))%2;out=y.copy();coefficients=np.zeros((169,2,8,3));counts=np.zeros((169,2),dtype=int)
    for c in range(169):
        for target_half in range(2):
            train=(classes==c)&(parity!=target_half);test=(classes==c)&(parity==target_half)
            counts[c,target_half]=int(train.sum())
            if counts[c,target_half]>=20:
                coefficients[c,target_half]=fit_coefficients(x[train],y[train])
                # Exact-mean-centered held-out features only: no fitted intercept.
                out[test]-=x[test]@coefficients[c,target_half]
    return out,coefficients,counts


def self_test():
    fixtures=[[48,49,44,45],[48,45,50,41],[0,1,2,3],[48,44,40,36],[8,28,36,37]]
    maximum=0.;records=[]
    for private in fixtures:
        remaining=[c for c in range(52) if c not in private]
        flops=list(itertools.combinations(remaining,3))
        assert len(flops)==17296
        observed=np.array([features(private,list(f)) for f in flops]).mean(0)
        err=float(np.max(abs(observed-expectation(private))));maximum=max(maximum,err)
        assert err<1e-13
        records.append(dict(private=private,flops=len(flops),maximum_error=err))
    rng=np.random.default_rng(52626);x=rng.normal(size=(80,8));y=rng.normal(size=(80,3));classes=np.zeros(80,dtype=int)
    original,beta,counts=crossfit(x,y,classes)
    shifted=y+np.array([100.,-50.,7.])
    assert np.max(abs(fit_coefficients(x,y)-fit_coefficients(x,shifted)))<1e-12
    changed=y.copy();changed[::2]+=50*x[::2,:3]
    _,new_beta,_=crossfit(x,changed,classes)
    assert np.array_equal(beta[0,0],new_beta[0,0])
    assert not np.array_equal(beta[0,1],new_beta[0,1])
    zero,zero_beta,_=crossfit(np.zeros_like(x),y,classes)
    assert np.array_equal(zero,y) and not np.any(zero_beta)
    small,small_beta,_=crossfit(x[:10],y[:10],classes[:10])
    assert np.array_equal(small,y[:10]) and not np.any(small_beta)
    try:features([0,1,2,3],[3,4,5])
    except ValueError:pass
    else:raise AssertionError('Overlap must be refused')
    return dict(passed=True,fixtures=records,maximum_exact_mean_error=maximum,
                checks=['exhaustive conditional flop expectations','constant payoff shift invariance','held-out target isolation','zero-feature identity','small-sample fallback','card overlap rejection'],
                variance_improvement_tested=False,production_modified=False)
