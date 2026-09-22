"""Locate retained-data fit error in a previously completed candidate, CPU only.

Generation 77 is the last *played* network in the 78-generation dense all-in
bank. This is a fit diagnostic of that component, not of the average strategy,
not held-out accuracy, and not a best-response or convergence result.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_checkpoint_v1 import read_object,model_document
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_fit_v1 import grouped_rows

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-fit-error-diagnostic-v1'


def matching(scores,arity):
    legal=np.arange(4)[None,:]<arity[:,None]
    positive=np.maximum(scores,0)*legal;sums=positive.sum(1);valid=sums>0
    positive[valid]/=sums[valid,None]
    idx=np.flatnonzero(~valid)
    positive[idx,np.argmax(np.where(legal,scores,-np.inf),axis=1)[idx]]=1.
    assert np.max(abs(positive.sum(1)-1))<1e-12 and not np.any(positive[~legal])
    return positive


def main():
    began=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>=2:
            assert now-began<600 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            last=now
    guard()
    tp=OUT/'sampled-physical-allin-pilot-v1-registration.json'
    rp=OUT/'sampled-physical-allin-pilot-v1-independent-review.json'
    training=json.loads(tp.read_text());review=json.loads(rp.read_text())
    assert review['passed'] and review['terminal_complete'] and review['completed_iterations']==78
    assert review['source_registration_sha256']==sha(tp)
    for p,h in training['inputs'].items():assert sha(ROOT/p)==h,p
    store=Path(training['store']);objects=store/'checkpoint-objects'
    metricpath=store/'iteration-0077/metrics.json';metric=json.loads(metricpath.read_text())
    assert sha(metricpath)==review['steps'][76]['metrics_sha256']
    ref=metric['checkpoint'];checkpoint=json.loads(read_object(objects,ref))
    model=model_document(objects,checkpoint['next_model']);assert model['generation']==77
    final=json.loads(read_object(objects,review['checkpoint']))
    assert final['played_bank'][77]==checkpoint['next_model']
    context=(OUT/'bb-context-candidate.json').read_text()
    paths=[Path(__file__),tp,rp,metricpath,objects/ref['file'],objects/checkpoint['next_model']['file'],
        *[objects/r['file'] for r in checkpoint['reservoirs']],
        ROOT/'tools/research/sampled_physical_fit_v1.py',ROOT/'tools/research/sampled_physical_checkpoint_v1.py',
        ROOT/'tools/research/sampled_physical_reservoir_v1.py']
    scope='Post-hoc retained-data error decomposition for the previously completed dense exact-all-in generation 77. No fitting, new data, GPU work, policy editing, average-bank selection or independent accuracy claim.'
    reg=dict(inputs={str(p):sha(p) for p in paths},generation=77,scope=scope,production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,reg);players=[]
    for player,resref in enumerate(checkpoint['reservoirs']):
        guard();read_object(objects,resref)
        reservoir=PhysicalReservoir.load(objects/resref['file'],context)
        assert reservoir.player==player
        grouped=grouped_rows(reservoir)
        _,first,inverse,counts=np.unique(reservoir.keys[:reservoir.size],axis=0,return_index=True,return_inverse=True,return_counts=True)
        assert np.array_equal(grouped['active'],reservoir.active[first]) and np.array_equal(counts,grouped['counts'])
        mask=(grouped['active']>=135)&(grouped['active']<139)
        assert np.all(mask.sum(1)==1)
        phase=grouped['active'][mask].astype(int)-135
        assert np.array_equal(phase==0,reservoir.keys[first,0]<2**63)
        scores=np.empty((len(first),4));net=model['networks'][player]
        for start in range(0,len(first),4096):
            guard();active=grouped['active'][start:start+4096]
            x=np.zeros((len(active),269),np.float64);x[np.arange(len(active))[:,None],active]=1.
            for layer,shape in enumerate(((64,269),(64,64),(4,64))):
                w=np.asarray(net[f'w{layer}'],np.float32).astype(np.float64).reshape(shape)
                b=np.asarray(net[f'b{layer}'],np.float32).astype(np.float64)
                x=x@w.T+b
                if layer<2:x=np.maximum(x,0)
            scores[start:start+len(active)]=x
        legal=np.arange(4)[None,:]<grouped['arity'][:,None]
        weights=legal*counts[:,None]
        error=((scores-grouped['targets'])**2*weights).sum(1)
        loss=float(error.sum()/grouped['denominator'])
        logged=metric['fits'][player]['normalized_grouped_loss_after']
        assert abs(loss-logged)<1e-5*(1+abs(logged)),(loss,logged)
        assert grouped['scale']==model['advantage_scales'][player]
        raw=reservoir.values[:reservoir.size]/grouped['scale']
        rawlegal=np.arange(4)[None,:]<reservoir.arity[:reservoir.size,None]
        within=((raw-grouped['targets'][inverse])**2*rawlegal).sum(1)
        assert abs(within.sum()/grouped['denominator']-grouped['variance'])<1e-12
        p=matching(scores,grouped['arity']);target=matching(grouped['targets'],grouped['arity'])
        tv=.5*np.abs(p-target).sum(1)
        streets=[]
        for street,name in enumerate(('preflop','flop','turn','river')):
            selected=phase==street;rawselected=phase[inverse]==street
            denominator=int(weights[selected].sum());mass=int(counts[selected].sum())
            streets.append(dict(street=name,grouped_observations=int(selected.sum()),retained_visits=mass,
                legal_targets=denominator,normalized_grouped_mse=float(error[selected].sum()/denominator) if denominator else None,
                fraction_total_fit_error=float(error[selected].sum()/error.sum()),
                normalized_within_observation_variance=float(within[rawselected].sum()/denominator) if denominator else None,
                retained_weighted_policy_total_variation=float(np.dot(counts[selected],tv[selected])/mass) if mass else None))
        assert sum(s['retained_visits'] for s in streets)==reservoir.size
        assert abs(sum(s['fraction_total_fit_error'] for s in streets)-1)<1e-12
        players.append(dict(player=player,generation=77,retained=reservoir.size,scale=grouped['scale'],
            reconstructed_normalized_grouped_loss=loss,logged_cuda_float32_loss=logged,
            loss_readback_error=abs(loss-logged),streets=streets))
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    guard();result=dict(passed=True,registration_sha256=sha(regpath),players=players,
        seconds=time.monotonic()-began,production_modified=False,accuracy_qualified=False,scope=scope)
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))


if __name__=='__main__':main()
