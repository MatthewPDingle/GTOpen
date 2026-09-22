"""CPU numerical controls for the visible-feature fitter, not a poker trial."""
import json
from pathlib import Path
import time
import numpy as np
import psutil
import torch
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_fit_v1 import grouped_rows,export_network
from sampled_visible_initialization_v1 import features,fresh_visible_network
from sampled_visible_hybrid_fit_v1 import PreparedObjective,fit
from sampled_visible_hybrid_checkpoint_v1 import read_object

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-visible-hybrid-fit-control-v1'


def main():
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    started=time.monotonic()
    def guard():
        assert time.monotonic()-started<180 and idle()
        assert psutil.virtual_memory().available>=20_000_000_000
    guard()
    priorpath=OUT/'sampled-visible-hybrid-checkpoint-control-v1-result.json'
    prior=json.loads(priorpath.read_text());assert prior['passed']
    for p,h in prior['artifacts'].items():assert sha(p)==h,p
    objects=Path('S:/GTOpen-research/sampled-visible-hybrid-checkpoint-control-v1/objects')
    doc=json.loads(read_object(objects,prior['continued_checkpoint']))
    context=(OUT/'bb-context-candidate.json').read_text()
    inputs=[priorpath,Path(__file__),*[ROOT/'tools/research'/n for n in (
        'sampled_visible_hybrid_fit_v1.py','sampled_visible_initialization_v1.py',
        'sampled_visible_poker_features_v1.py','sampled_physical_fit_v1.py')]]
    reg=dict(inputs={str(p):sha(p) for p in inputs},steps=8,seed=19391,chunk_size=13,
        scope='Two 64-visit old fixture reservoirs, CPU numerical fitting controls only. No new cards, candidate training, GPU workload, hyperparameter selection or strength claim.',production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,reg);results=[]
    for player,ref in enumerate(doc['reservoirs']):
        guard();read_object(objects,ref)
        reservoir=PhysicalReservoir.load(objects/ref['file'],context)
        grouped=grouped_rows(reservoir);prepared=PreparedObjective(grouped,'cpu',guard)
        assert prepared.x.shape[1]==302
        # Compare grouped gradients with a raw-visit objective. Grouping subtracts
        # only a parameter-independent within-key variance from the loss.
        rawx=torch.as_tensor(features([dict(active_features=a.tolist()) for a in reservoir.active[:reservoir.size]]))
        rawy=torch.as_tensor(reservoir.values[:reservoir.size]/grouped['scale'],dtype=torch.float32)
        legal=torch.as_tensor(np.arange(4)[None,:]<reservoir.arity[:reservoir.size,None])
        model=fresh_visible_network(reg['seed']+player)
        rawloss=((model(rawx)-rawy).square()*legal).sum()/grouped['denominator']
        rawloss.backward();rawgrads=[p.grad.clone() for p in model.parameters()]
        model.zero_grad(set_to_none=True)
        groupedloss=prepared.objective(model,13,guard,backward=True)
        gradient_error=max(float((a-p.grad).abs().max()) for a,p in zip(rawgrads,model.parameters()))
        loss_error=abs(float(rawloss.detach())-grouped['variance']-groupedloss)
        assert gradient_error<1e-5 and loss_error<1e-5
        state=torch.random.get_rng_state().clone()
        actual,metric=fit(reservoir,seed=reg['seed']+player,steps=8,device='cpu',chunk_size=13,guard=guard)
        assert torch.equal(state,torch.random.get_rng_state())
        repeat,_=fit(reservoir,seed=reg['seed']+player,steps=8,device='cpu',chunk_size=13,guard=guard)
        assert actual==repeat
        # Independent full-tensor optimizer loop: no prepared/chunked objective.
        reference=fresh_visible_network(reg['seed']+player)
        optimizer=torch.optim.Adam(reference.parameters(),lr=.003)
        x=features([dict(active_features=a.tolist()) for a in grouped['active']])
        target=torch.tensor(grouped['targets'],dtype=torch.float32)
        weights=torch.tensor((np.arange(4)[None,:]<grouped['arity'][:,None])*grouped['counts'][:,None],dtype=torch.float32)
        for _ in range(8):
            optimizer.zero_grad(set_to_none=True)
            loss=((reference(torch.as_tensor(x))-target).square()*weights).sum()/grouped['denominator']
            loss.backward();optimizer.step()
        expected=export_network(reference)
        parameter_error=max(float(np.max(abs(np.asarray(actual[k])-expected[k]))) for k in actual)
        assert parameter_error<5e-5
        newcols=np.asarray(actual['w0']).reshape(64,302)[:,269:]
        assert np.count_nonzero(newcols)>0
        results.append(dict(player=player,retained=reservoir.size,grouped=len(grouped['active']),
            raw_grouped_loss_error=loss_error,raw_grouped_gradient_error=gradient_error,
            full_tensor_optimizer_parameter_error=parameter_error,repeat_parameters_exact=True,
            unchanged_global_rng=True,learned_new_columns=int(np.count_nonzero(newcols)),
            optimizer_steps_per_check=8,metric=metric))
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    guard();result=dict(passed=True,registration_sha256=sha(rp),records=results,
        seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,scope=reg['scope'])
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))


if __name__=='__main__':main()
