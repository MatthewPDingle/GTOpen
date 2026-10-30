"""CPU-only, no-optimizer checks for matched visible-feature initialization."""
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_fit_v1 import fresh_network
from sampled_visible_initialization_v1 import features,fresh_visible_network

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-visible-initialization-control-v1'


def main():
    import torch
    torch.set_num_threads(2)
    started=time.monotonic()
    assert idle() and psutil.virtual_memory().available>=20_000_000_000
    # Existing response-training numerical fixture; no held-out poker outcomes.
    prior=OUT/'sampled-physical-allin-precision-control-v1-independent-review.json'
    review=json.loads(prior.read_text());assert review['passed']
    query=Path('S:/GTOpen-research/sampled-physical-allin-precision-control-v1/gpu-0/queries.json')
    assert sha(query)==review['artifacts'][str(query)]
    paths=[Path(__file__),prior,query,*[ROOT/'tools/research'/n for n in (
        'sampled_visible_initialization_v1.py','sampled_visible_poker_features_v1.py','sampled_physical_fit_v1.py')]]
    registration=dict(inputs={str(p):sha(p) for p in paths},seeds=[19301,19302,19303,19304],
        scope='Matched initialization and gradient-flow control only. Existing training observations, no optimizer steps, new chance data, outcome labels, checkpoint or strength claim.',production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,registration)
    obs=json.loads(query.read_text())['observations'];x=features(obs)
    old=np.zeros((len(obs),269),np.float32)
    for i,o in enumerate(obs):old[i,o['active_features']]=1.
    assert np.array_equal(old,x[:,:269]) and x.shape==(len(obs),302)
    pre=np.array([o['phase']==0 for o in obs]);assert pre.any() and (~pre).any()
    assert np.all(x[pre,269:]==0) and np.any(x[~pre,269:]!=0)
    rows=[]
    for seed in registration['seeds']:
        assert idle()
        state=torch.random.get_rng_state().clone()
        original=fresh_network(seed);model=fresh_visible_network(seed)
        assert torch.equal(state,torch.random.get_rng_state())
        assert torch.equal(original[0].weight,model[0].weight[:,:269])
        assert torch.count_nonzero(model[0].weight[:,269:])==0
        assert torch.equal(original[0].bias,model[0].bias)
        for layer in (2,4):
            assert all(torch.equal(v,model[layer].state_dict()[k]) for k,v in original[layer].state_dict().items())
        with torch.no_grad():
            error32=float((original(torch.as_tensor(old))-model(torch.as_tensor(x))).abs().max())
            original.double();model.double()
            error64=float((original(torch.as_tensor(old).double())-model(torch.as_tensor(x).double())).abs().max())
        assert error32<1e-6 and error64<1e-12
        # Backward only: show zero new columns can learn, with no weight update.
        model(torch.as_tensor(x[~pre]).double()).square().sum().backward()
        grad=float(model[0].weight.grad[:,269:].abs().max());assert grad>0
        model.zero_grad(set_to_none=True)
        model(torch.as_tensor(x[pre]).double()).square().sum().backward()
        assert torch.count_nonzero(model[0].weight.grad[:,269:])==0
        assert torch.count_nonzero(model[0].weight[:,269:])==0
        rows.append(dict(seed=seed,float32_score_error=error32,float64_score_error=error64,
            postflop_new_column_maximum_gradient=grad,preflop_new_column_gradient=0,
            original_parameters=sum(p.numel() for p in original.parameters()),
            augmented_parameters=sum(p.numel() for p in model.parameters())))
    for p,h in registration['inputs'].items():assert sha(p)==h,p
    assert idle()
    result=dict(passed=True,registration_sha256=sha(regpath),observations=len(obs),
        preflop_observations=int(pre.sum()),postflop_observations=int((~pre).sum()),
        records=rows,optimizer_steps=0,seconds=time.monotonic()-started,
        production_modified=False,scope=registration['scope'])
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))


if __name__=='__main__':main()
