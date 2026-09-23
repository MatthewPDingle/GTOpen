"""Post-audit comparison of the visible-input trial and its immediate comparator.

Descriptive across different held-out seeds and jointly changed policies.
Never selects a checkpoint, patches a hand, or qualifies deployment.
"""
import json
from pathlib import Path
import time
import numpy as np
from hu_sampled_physical_dense_comparison_20260922 import read,OUT
from sampled_physical_root_evaluation_v1 import ROOT,sha,save

PREFIX='sampled-visible-hybrid-completion-comparison-v1'
NAMES={'combined_269':'sampled-physical-hybrid-allin','visible_302':'sampled-visible-hybrid-completion'}


def main():
    started=time.monotonic();evidence={};btn={};configs={};candidates={}
    for name,prefix in NAMES.items():
        paths={k:OUT/f'{prefix}-btn-evaluation-v1-{k}.json' for k in ('registration','result','independent-review','status')}
        docs={k:json.loads(p.read_text()) for k,p in paths.items()}
        assert docs['status']['state']=='complete' and docs['result']['passed'] and docs['independent-review']['passed']
        assert docs['result']['registration_sha256']==sha(paths['registration'])
        assert docs['independent-review']['inputs'][str(paths['result'])]==sha(paths['result'])
        for p,h in docs['registration']['inputs'].items():assert sha(p)==h,p
        evidence.update({str(p):sha(p) for p in paths.values()});btn[name]=docs['result']
        candidates[name]=read(prefix+'-evaluation-v1')
        evidence.update(candidates[name]['evidence'])
        er=OUT/f'{prefix}-evaluation-v1-registration.json';r=json.loads(er.read_text())
        tr=Path(r['training_registration']);training=json.loads(tr.read_text());configs[name]=training['config']
        evidence[str(tr)]=sha(tr);assert r['selected_iterations']==78
        assert sha(r['context'])==sha(OUT/'bb-context-candidate.json')
    assert candidates['combined_269']['test_seed']==89102 and candidates['visible_302']['test_seed']==99102
    assert configs['visible_302']['architecture']==[302,64,64,4]
    assert {k:v for k,v in configs['visible_302'].items() if k not in ('architecture','representation')}=={k:v for k,v in configs['combined_269'].items() if k!='architecture'}
    prior_path=OUT/'sampled-physical-hybrid-allin-exact-root-mix-v1-result.json'
    prior_reg=OUT/'sampled-physical-hybrid-allin-exact-root-mix-v1-registration.json'
    prior=json.loads(prior_path.read_text());reg=json.loads(prior_reg.read_text())
    assert prior['passed'] and prior['registration_sha256']==sha(prior_reg)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    mass=np.array(prior['class_probabilities']);assert mass.shape==(169,) and abs(mass.sum()-1)<1e-12
    evidence.update({str(prior_path):sha(prior_path),str(prior_reg):sha(prior_reg),str(Path(__file__)):sha(Path(__file__)),
        str(ROOT/'tools/research/hu_sampled_physical_dense_comparison_20260922.py'):sha(ROOT/'tools/research/hu_sampled_physical_dense_comparison_20260922.py')})
    registration=dict(inputs=evidence,scope='Complete audited policies and all 169 classes, exact existing compatible-card prior, descriptive cross-candidate comparison only.',production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,registration)
    policies={};changes=[]
    for name,c in candidates.items():
        rows=c['classes'];assert [r['hand_class'] for r in rows]==list(range(169))
        p=np.asarray([r['baseline_probabilities'] for r in rows]);assert p.shape==(169,4) and np.max(abs(p.sum(1)-1))<1e-12
        policies[name]=p;c['complete_prior_action_mix']=(mass@p).tolist()
    delta=policies['visible_302']-policies['combined_269']
    for i in range(169):
        a=candidates['combined_269']['classes'][i];b=candidates['visible_302']['classes'][i]
        assert a['hand']==b['hand']
        changes.append(dict(hand=a['hand'],hand_class=i,entry_probability=float(mass[i]),action_probability_change=delta[i].tolist(),
            baseline_test_deals=a['test_deals'],candidate_test_deals=b['test_deals'],
            baseline_call_minus_fold_bb=a['call_minus_fold_bb'],candidate_call_minus_fold_bb=b['call_minus_fold_bb']))
    for p,h in evidence.items():assert sha(p)==h,p
    result=dict(registration_sha256=sha(rp),candidates=candidates,btn=btn,training_configs=configs,class_changes=changes,
        complete_prior_weighted_policy_distance=float(mass@(abs(delta).sum(1)/2)),seconds=time.monotonic()-started,
        accuracy_qualified=False,production_modified=False,
        scope=registration['scope']+' Different opponents, continuations and independent test streams. Policy distance is not accuracy. Per-hand EVs are noisy diagnostics. Restricted deviations do not upper-bound a full best response; no Wizard equivalence, cross-stack generalization, or UTG/LJ transfer claim.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps(dict(mixes={k:v['complete_prior_action_mix'] for k,v in candidates.items()},policy_distance=result['complete_prior_weighted_policy_distance'],accuracy_qualified=False)))

if __name__=='__main__':main()
