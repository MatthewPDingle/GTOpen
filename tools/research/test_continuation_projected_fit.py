import unittest
import numpy as np
import continuation_projected_fit as run


class ProjectionTests(unittest.TestCase):
    def test_projection_is_inference_equivalent(self):
        rng=np.random.default_rng(90210)
        for concentration in [1.,.05]:
            mass=rng.dirichlet(np.full(169,concentration),size=2)
            x=rng.normal(size=(2,169,104));x[...,0]=1
            raw=rng.uniform(size=(2,169));raw-=(raw*mass).sum()/2-.5
            case=dict(mass=mass,x=x,raw=raw,observed=np.ones((2,169)))
            projected=run.project(case)
            np.testing.assert_allclose((projected['x']*mass[...,None]).sum(axis=(0,1)),0,atol=1e-14)
            model=dict(mean=rng.normal(size=104),scale=rng.uniform(.1,3,size=104),coef=rng.normal(size=104))
            pred=run.study.pilot.predict(case,model)
            direct=raw+projected['x']@(np.array(model['coef'])/model['scale'])
            # Different summation order across 104 columns; synthetic values
            # span tens of pots. Allow binary64 accumulation roundoff only.
            np.testing.assert_allclose(pred,direct,rtol=0,atol=1e-11)

    def test_fit_handles_null_columns_and_recovers_linear_labels(self):
        rng=np.random.default_rng(2468);coefficient=np.array([0.,.15,-.25]);cases=[]
        for _ in range(5):
            x=rng.normal(size=(2,169,3));x[...,0]=1
            mass=rng.dirichlet(np.ones(169),size=2)
            case=dict(x=x,mass=mass,observed=np.ones((2,169)),raw=np.full((2,169),.5))
            projected=run.project(case);case['residual']=projected['x']@coefficient;cases.append(case)
        model=run.study.pilot.fit_ridge([run.project(c) for c in cases],1e-9)
        for case in cases:
            pred=run.study.pilot.predict(case,model)
            np.testing.assert_allclose(pred,case['raw']+case['residual'],atol=1e-8,rtol=0)


if __name__=='__main__':unittest.main()
