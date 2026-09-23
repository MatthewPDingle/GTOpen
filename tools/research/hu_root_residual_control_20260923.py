"""Scalar finite-population identity and analytic-bound tests for the residual estimator."""
import itertools
import math
from pathlib import Path
import time
import numpy as np
from root_residual_evaluation_v1 import prepare,residuals
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='root-residual-control-v1'


def main():
    started=time.monotonic();assert idle()
    paths=[Path(__file__),ROOT/'tools/research/root_residual_evaluation_v1.py']
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs={str(p):sha(p) for p in paths},seed=27701,
        scope='Synthetic finite population identity, own-class centring and physical-corner bounds; no poker quality claim.'))
    rng=np.random.Generator(np.random.PCG64(27701));mass=np.arange(1,170,dtype=float);mass/=mass.sum()
    baseline=rng.dirichlet(np.ones(4),size=169)
    # All 169 classes have three unequally weighted outcomes, unlike training.
    classes=np.repeat(np.arange(169),3);conditional=np.tile([.2,.3,.5],169)
    probability=np.repeat(mass,3)*conditional
    q=rng.uniform(-200,200.5,size=(507,4))
    folds=np.array([math.fsum(probability[i]*q[i,0] for i in range(c*3,c*3+3)) for c in range(169)])
    jams=np.array([math.fsum(probability[i]*q[i,3] for i in range(c*3,c*3+3)) for c in range(169)])
    training_classes=np.repeat(np.arange(5,169),2);training=rng.uniform(-200,200.5,size=(328,4))
    alternatives=[baseline.copy(),*[np.tile(np.eye(4)[a],(169,1)) for a in range(4)],np.eye(4)[np.arange(169)%4],rng.dirichlet(np.ones(4),size=169)]
    error=0.;records=[]
    for k,response in enumerate(alternatives):
        delta=response-baseline
        direct=math.fsum(probability[i]*math.fsum(delta[classes[i],a]*q[i,a] for a in range(4)) for i in range(507))
        for centre in (False,True):
            p=prepare(baseline,response,mass,folds,jams,training_classes=training_classes,
                      training_actions=training,centre=centre,lower=-200,upper=200.5)
            r=residuals(p,classes,q)
            got=p['total_offset']+math.fsum(probability[i]*r[i] for i in range(507))
            error=max(error,abs(got-direct));assert p['centre'][:5]==[0.]*5
            scalar=[]
            for i,c in enumerate(classes):
                scalar.append(delta[c,1]*q[i,1]+delta[c,2]*q[i,2]-p['centre'][c])
            assert np.max(abs(r-scalar))<1e-12
            for c in range(169):
                for call,raise_ in itertools.product((-200,200.5),repeat=2):
                    corner=delta[c,1]*call+delta[c,2]*raise_-p['centre'][c]
                    assert p['residual_lower']<=corner<=p['residual_upper']
            if k==0:assert got==0 and np.all(r==0)
            records.append(dict(alternative=k,centred=centre,identity_error=abs(got-direct),corner_checks=169*4))
    rejected=[]
    def reject(name,fn):
        try:fn()
        except ValueError:rejected.append(name);return
        raise AssertionError('Accepted '+name)
    reject('invalid-class',lambda:residuals(p,[169],[[0,0,0,0]]))
    reject('outside-physical-bounds',lambda:residuals(p,[0],[[0,999,0,0]]))
    reject('nonfinite-values',lambda:residuals(p,[0],[[0,float('nan'),0,0]]))
    reject('unnormalized-policy',lambda:prepare(baseline*2,baseline,mass,folds,jams,
        training_classes=training_classes,training_actions=training,centre=True,lower=-200,upper=200.5))
    assert error<1e-10 and idle() and time.monotonic()-started<60
    result=dict(passed=True,registration_sha256=sha(rp),maximum_identity_error_bb=error,
        checks=records,rejections=rejected,seconds=time.monotonic()-started,
        production_modified=False,gpu_used=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',result);print(result)


if __name__=='__main__':main()
