"""Descriptive training-fit decomposition of the completed baseline pilot.

No new training, held-out outcomes, policy selection or production changes.
"""
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_checkpoint_v1 import read_object, model_document
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_fit_v1 import grouped_rows, fresh_network
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-pilot-fit-diagnosis-v1'


def main():
    import torch
    torch.set_num_threads(2)
    began = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-began < 180 and psutil.virtual_memory().available >= 20_000_000_000
    guard()
    regpath = OUT/'sampled-physical-cached-fit-v1-registration.json'
    reg = json.loads(regpath.read_text())
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    objects = Path(reg['objects']); checkpoint = json.loads(read_object(objects,reg['checkpoint']))
    context = Path(reg['context']).read_text(); nets = model_document(objects,checkpoint['next_model'])['networks']
    fits = json.loads(Path(reg['source_metrics']).read_text())['fits']; players = []
    for player in (0,1):
        guard(); ref = checkpoint['reservoirs'][player]; read_object(objects,ref)
        reservoir = PhysicalReservoir.load(objects/ref['file'],context); grouped = grouped_rows(reservoir)
        keys,first,inverse,counts = np.unique(reservoir.keys[:reservoir.size],axis=0,
            return_index=True,return_inverse=True,return_counts=True)
        assert np.array_equal(counts,grouped['counts'])
        active = grouped['active']; arity = grouped['arity']; targets = grouped['targets']
        model = fresh_network(0)
        with torch.no_grad():
            for layer,j in enumerate((0,2,4)):
                model[j].weight.copy_(torch.tensor(nets[player][f'w{layer}']).reshape(model[j].weight.shape))
                model[j].bias.copy_(torch.tensor(nets[player][f'b{layer}']))
            predictions = []
            for start in range(0,len(active),4096):
                guard(); chunk = active[start:start+4096]; x = np.zeros((len(chunk),269),np.float32)
                x[np.arange(len(chunk))[:,None],chunk] = 1
                predictions.append(model(torch.from_numpy(x)).numpy().astype(float))
        predictions = np.concatenate(predictions)
        legal = np.arange(4)[None,:] < arity[:,None]; weights = legal*counts[:,None]
        squared = (predictions-targets)**2
        measured_loss = float((squared*weights).sum()/grouped['denominator'])
        assert abs(measured_loss-fits[player]['normalized_grouped_loss_after']) < 1e-5
        phase = np.array([next(int(a-135) for a in row if 135 <= a < 139) for row in active])
        assert np.array_equal(phase == 0,keys[:,0] < 2**63)
        subsets = [(n,phase == i) for i,n in enumerate(('preflop','flop','turn','river'))]
        if player == 0: subsets.append(('BB first decision',keys[:,0] == 1))
        groups = []
        for name,mask in subsets:
            slots = int(weights[mask].sum()); contribution = float((squared[mask]*weights[mask]).sum())
            groups.append(dict(name=name,unique_observations=int(mask.sum()),retained_examples=int(counts[mask].sum()),
                share_of_legal_training_targets=slots/grouped['denominator'],
                mean_squared_fit_error_normalized=contribution/slots if slots else None,
                root_mean_squared_fit_error_bb=grouped['scale']*(contribution/slots)**.5 if slots else None,
                share_of_total_grouped_fit_error=contribution/(squared*weights).sum()))
        root_rows = []
        if player == 0:
            for i in np.flatnonzero(keys[:,0] == 1):
                code = int(keys[i,1]); c = hand_class([code&63,(code>>6)&63])
                raw = reservoir.values[:reservoir.size][inverse == i]
                mean = raw.mean(0); std = raw.std(0,ddof=1) if len(raw)>1 else np.zeros(4)
                fitted = predictions[i]*grouped['scale']
                assert np.max(np.abs(mean-targets[i]*grouped['scale'])) < 1e-10
                def policy(v):
                    out=np.maximum(v,0.)
                    if out.sum()>0:return (out/out.sum()).tolist()
                    out=np.zeros(4);out[int(np.argmax(v))]=1;return out.tolist()
                root_rows.append(dict(hand_class=c,retained_examples=int(counts[i]),target_mean_advantage_bb=mean.tolist(),
                    target_sample_standard_deviation_bb=std.tolist(),fitted_advantage_bb=fitted.tolist(),
                    target_regret_matched_policy=policy(mean),fitted_regret_matched_policy=policy(fitted),
                    maximum_action_error_bb=float(np.max(np.abs(fitted-mean)))))
        players.append(dict(player=player,retained_examples=reservoir.size,unique_observations=len(active),
            normalized_grouped_loss=measured_loss,source_cuda_loss=fits[player]['normalized_grouped_loss_after'],
            normalized_within_observation_variance=grouped['variance'],advantage_scale=grouped['scale'],
            groups=groups,root_rows=root_rows))
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    document = dict(source_registration_sha256=sha(regpath),source_checkpoint=reg['checkpoint'],
        source_generation=checkpoint['next_model']['generation'],source_model=checkpoint['next_model'],
        source_used_in_strength_evaluation=False,reviewer_sha256=sha(Path(__file__)),players=players,
        seconds=time.monotonic()-began,production_modified=False,
        scope='Training-only descriptive decomposition for the unused next model from the old pilot. CPU inference crosschecked against saved CUDA aggregate loss. Empirical regret targets are noisy historical training labels, not true action EVs or GTO policies. This does not select or alter the running dense candidate.')
    save(OUT/f'{PREFIX}-result.json',document)
    print(json.dumps(dict(seconds=document['seconds'],players=[{k:v for k,v in p.items() if k!='root_rows'} for p in players])))


if __name__ == '__main__': main()
