"""Independent scalar finite fixtures and replay of the completed old diagnostic."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import copy
import math
from pathlib import Path
import time
import numpy as np
from exact_aware_root_response_v1 import fit,frozen_policy,admit_test_ids
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle

PREFIX='exact-aware-response-control-v1'


def main():
    started=time.monotonic();assert idle()
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    paths=[Path(__file__),ROOT/'tools/research/exact_aware_root_response_v1.py',ROOT/'tools/research/root_residual_evaluation_v1.py']
    inputs={str(p):sha(p) for p in paths}
    old_rp=OUT/'exact-aware-response-diagnostic-v1-registration.json';old_pp=OUT/'exact-aware-response-diagnostic-v1-result.json'
    old_reg,old=read(old_rp),read(old_pp)
    assert old['passed'] and old['registration_sha256']==sha(old_rp)
    for p,h in old_reg['inputs'].items():assert sha(p)==h,p
    inputs.update(old_reg['inputs']);inputs.update({str(old_rp):sha(old_rp),str(old_pp):sha(old_pp)})
    save(rp,dict(inputs=inputs,scope='Responder implementation control, not a fresh poker evaluation.',production_modified=False,gpu_used=False))
    context='0'*64;mass=np.arange(1,170,dtype=float);mass/=mass.sum()
    base=np.tile([.4,.3,.2,.1],(169,1));fold=np.full(169,-1.);jam=np.array([(c%9)-4. for c in range(169)])
    cs=[];qs=[]
    for c in range(169):
        # Unequal class coverage; below-threshold cases explicitly retain base.
        for j in range(c%5+1):
            cs.append(c);qs.append([-199.,c%7-3.+j*.1,c%11-5.-j*.2,199.])
    ids=[f'synthetic-train-{i}' for i in range(len(cs))]
    doc=fit(ids,cs,qs,base,mass,mass*fold,mass*jam,context_sha256=context,minimum_training_deals=3)
    maximum=0.
    for c in range(169):
        rows=[q for h,q in zip(cs,qs) if h==c]
        means=[fold[c],math.fsum(q[1] for q in rows)/len(rows),math.fsum(q[2] for q in rows)/len(rows),jam[c]]
        a=max(range(4),key=lambda i:means[i]) if len(rows)>=3 else -1
        assert doc['selected_actions'][c]==a and doc['training_counts'][c]==len(rows)
        maximum=max(maximum,max(abs(x-y) for x,y in zip(means,doc['class_action_means'][c])))
    frozen_policy(doc,context_sha256=context);admit_test_ids(doc,['independent-test-0'],context_sha256=context)
    # Bogus sampled fold/shove variation cannot affect fit; actual call/raise can.
    altered=np.array(qs);altered[:,0]=123.;altered[:,3]=-123.
    alternate=fit(ids,cs,altered,base,mass,mass*fold,mass*jam,context_sha256=context,minimum_training_deals=3)
    assert alternate['probabilities']==doc['probabilities'] and alternate['class_action_means']==doc['class_action_means']
    tied=fit(['tie'],[0],[[-1.,-1.,-1.,-1.]],base,mass,-mass,-mass,context_sha256=context,minimum_training_deals=1)
    assert tied['selected_actions'][0]==0
    rejected=[]
    mutated=copy.deepcopy(doc);mutated['probabilities'][0]=[1.,0.,0.,0.]
    for name,fn in [('context',lambda:frozen_policy(doc,context_sha256='1'*64)),
                    ('overlap',lambda:admit_test_ids(doc,[ids[0]],context_sha256=context)),
                    ('changed-fallback',lambda:frozen_policy(mutated,context_sha256=context)),
                    ('duplicate-train',lambda:fit(['same']*len(cs),cs,qs,base,mass,mass*fold,mass*jam,context_sha256=context,minimum_training_deals=3)),
                    ('bad-exact-values',lambda:fit(ids,cs,qs,base,mass,mass*fold,np.full(169,np.nan),context_sha256=context,minimum_training_deals=3))]:
        try:fn()
        except ValueError:rejected.append(name)
        else:raise AssertionError(name)
    # Reproduce the old diagnostic's already inspected exact-aware choices.
    source='sampled-physical-hybrid-allin-evaluation-v1';sr=read(OUT/f'{source}-registration.json');sp=read(OUT/f'{source}-result.json')
    bp=read(OUT/'bb-fold-jam-response-v3-result.json');rows=bp['candidates']['combined_269']['classes']
    base=np.array([r['baseline'] for r in rows]);mass=np.array([r['entry_probability'] for r in rows])
    fold=np.array([r['fold_value'] for r in rows]);jam=np.array([r['jam_value'] for r in rows]);store=Path(sr['store'])
    cs=[];qs=[];ids=[]
    for offset in range(0,8192,16):
        path=store/f'{source}-train-{offset}'/'summary.json';assert sha(path)==sp['batch_summary_hashes'][path.parent.name]
        s=read(path);cs.extend(s['classes']);qs.extend(s['action_values']);ids.extend(f'train-{offset}-{i}' for i in range(16))
    context=sha(sr['context']);doc=fit(ids,cs,qs,base,mass,mass*fold,mass*jam,context_sha256=context,minimum_training_deals=16)
    assert doc['selected_actions']==old['comparisons']['exact-aware']['actions']
    frozen_policy(doc,context_sha256=context)
    for p,h in inputs.items():assert sha(p)==h,p
    assert maximum<1e-12 and idle() and time.monotonic()-started<120
    result=dict(passed=True,registration_sha256=sha(rp),synthetic_classes=169,unequal_coverage=True,
        maximum_scalar_mean_error=maximum,ignored_sampled_fold_jam_verified=True,first_max_tie_verified=True,
        old_diagnostic_choices_reproduced=169,rejected=rejected,seconds=time.monotonic()-started,
        production_modified=False,gpu_used=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',result);print(result)


if __name__=='__main__':main()
