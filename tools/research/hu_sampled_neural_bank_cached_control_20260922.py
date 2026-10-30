"""Same bank training; decompress checkpoint arrays once during verification."""
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
import hu_sampled_neural_bank_control_20260922 as baseline
from hu_sampled_neural_control_20260922 import geometry,flat_policy
from hu_sampled_neural_fallback_20260922 import highest_regret_fallback
from hu_sampled_policy_bank_20260922 import average_bank
from hu_sampled_convergence_fixture_20260922 import evaluate


def load_policies(path,features,mask,actors):
    import torch
    # NPZ lazy access decompresses an entire tensor each time. Materialize each
    # tensor once, then index its iteration dimension without more disk work.
    with np.load(path) as stored:cache={key:stored[key] for key in stored.files}
    iterations=int(cache['iterations']);assert bool(cache['uniform_initial'])
    recovered=[mask/mask.sum(axis=1,keepdims=True)];model=baseline.network()
    for t in range(iterations-1):
        policy=np.zeros_like(recovered[0])
        for player in range(2):
            state={k:torch.as_tensor(cache[f'p{player}_{k}'][t],device='cuda') for k in model.state_dict()}
            model.load_state_dict(state);scale=torch.as_tensor(cache[f'p{player}_scales'][t],device='cuda')
            with torch.no_grad():pred=(model(features)*scale).cpu().numpy().astype(np.float64)
            candidate=highest_regret_fallback(pred,mask)
            policy[actors==player]=candidate[actors==player]
        recovered.append(policy)
    return recovered


def replay_bank(path,data,features,mask,actors,played):
    recovered=load_policies(path,features,mask,actors)
    assert len(recovered)==len(played)
    error=float(np.max(np.abs(np.asarray(recovered)-np.asarray(played))))
    assert error<1e-12,'Cached reader did not reproduce played policies.'
    averaged,_=average_bank(data,recovered)
    return averaged,error


def recover_interrupted(reg):
    import torch
    started=time.monotonic();torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False
    data=json.loads(Path(reg['fixture']).read_text());x,mask,actors=geometry(data)
    features=torch.as_tensor(x,device='cuda');snapshot=Path(reg['recovery_snapshot'])
    played=load_policies(snapshot,features,mask,actors)
    old=json.loads(Path(reg['recovery_partial_result']).read_text())
    assert old['case']==0 and old['seed']==17 and not old['terminal']
    maximum=0.;evaluations=[]
    for checkpoint in old['checkpoints']:
        t=checkpoint['iteration'];p,_=average_bank(data,played[:t]);flat=flat_policy(data,p)
        maximum=max(maximum,float(np.max(np.abs(np.asarray(flat)-checkpoint['average_policy']))))
    assert maximum<1e-10
    p,_=average_bank(data,played);flat=flat_policy(data,p)
    result=dict(passed=True,source_iteration=len(played),previous_verified_iteration=old['checkpoints'][-1]['iteration'],
        maximum_prior_policy_error=maximum,evaluation=evaluate(data,flat,0),average_policy=flat,
        seconds=time.monotonic()-started,snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        scope='Recover evaluation of already trained weights; no continued training or altered strategy.',production_modified=False)
    Path(reg['output_prefix']+'-recovery.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='average_policy'}),flush=True)


if __name__=='__main__':
    reg=json.loads(Path(sys.argv[1]).read_text())
    recover_interrupted(reg)
    baseline.replay_bank=replay_bank
    baseline.main()
