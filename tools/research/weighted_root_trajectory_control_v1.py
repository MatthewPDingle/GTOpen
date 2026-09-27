"""Known-answer trajectory checks plus independent real pilot root readback."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
import math
from pathlib import Path
import time
import psutil
from weighted_root_trajectory_v1 import summarize, CATALOG, safe_read_only_resources
from later_action_root_trajectory_20260926 import policy
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from preflop_allin_matrix_v1 import AllinMatrix
from weighted_training_checkpoint_v1 import model_document
from weighted_training_policy_v1 import probabilities


def main():
    started=time.monotonic()
    assert safe_read_only_resources() and psutil.cpu_percent(interval=1)<60
    mass=[1./169]*169
    counts=[[g*(4 if c<5 else 3) for c in range(169)] for g in range(79)]
    importance=[[float(n) for n in row] for row in counts]
    uniform=[[[.25]*4 for _ in range(169)] for _ in range(79)]
    expected=[[.25]*4 for _ in range(169)]
    fixed=summarize(uniform,counts,importance,mass,expected)
    assert fixed['count_total']==39936 and fixed['mean_step_tv_last_26']==0
    assert fixed['middle_last_window_tv']==fixed['final_current_vs_played_average_tv']==0
    changed=copy.deepcopy(uniform);changed[-1]=[[1.,0.,0.,0.] for _ in range(169)]
    last=summarize(changed,counts,importance,mass,expected)
    assert abs(last['final_current_vs_played_average_tv']-.75)<1e-12
    assert last['played_action_frequencies']==fixed['played_action_frequencies']
    alternating=[[[float(a==g%2) for a in range(4)] for _ in range(169)] for g in range(79)]
    denominator=78*79/2
    oracle=[[sum(g+1 for g in range(78) if g%2==a)/denominator if a<2 else 0. for a in range(4)] for _ in range(169)]
    moving=summarize(alternating,counts,importance,mass,oracle)
    assert abs(moving['mean_step_tv_last_26']-1)<1e-12
    assert moving['updates'][-1]['cumulative_average_tv_to_complete']==0
    rejected=[]
    def reject(name,fn):
        try: fn()
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('Accepted '+name)
    bad=copy.deepcopy(counts);bad[1][0]=2;bad[1][1]+=2
    reject('missing guaranteed class coverage',lambda:summarize(uniform,bad,importance,mass,expected))
    reject('missing final diagnostic model',lambda:summarize(uniform[:-1],counts,importance,mass,expected))
    reject('wrong played average',lambda:summarize(alternating,counts,importance,mass,expected))
    badp=copy.deepcopy(uniform);badp[20][7][0]=float('nan')
    reject('nonfinite policy',lambda:summarize(badp,counts,importance,mass,expected))
    badmass=copy.deepcopy(importance);badmass[1][10]=0
    reject('missing importance mass',lambda:summarize(uniform,counts,badmass,mass,expected))
    # Use only the completed, pre-study pilot. Do not inspect unfinished arms.
    pp=OUT/'weighted-training-pilot-v1-result.json';pr=OUT/'weighted-training-pilot-v1-registration.json'
    pilot=read(pp)
    assert pilot['passed'] and pilot['completed_generations']==2
    for path,digest in read(pr)['inputs'].items(): assert sha(path)==digest,path
    source=(OUT/'bb-context-candidate.json').read_text();catalog=CATALOG.read_text()
    mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    args=dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=AllinMatrix(read(mp),source).btn_mass)
    folder=Path(pilot['store']);objects=folder/'objects'
    metrics=[folder/f'iteration-{i:04d}/metrics.json' for i in (1,2)]
    for path,step in zip(metrics,pilot['steps']): assert sha(path)==step['metrics_sha256']
    refs=[read(metrics[0])['used_model'],read(metrics[0])['next_model'],read(metrics[1])['next_model']]
    root_obs={r['hand_class']:r['observation'] for r in json.loads(catalog)['native_observations'] if r['player']==0}
    assert set(root_obs)==set(range(169))
    query=dict(context_source=source,observations=[root_obs[c] for c in range(169)])
    worst=0.
    for g,reference in enumerate(refs):
        doc=model_document(objects,reference,**args)
        assert doc['generation']==g
        direct,_=probabilities(query,doc,device='cpu',**{k:v for k,v in args.items() if k!='context_source'})
        state=doc['root_state']
        fallback={c:direct[c].tolist() for c,n in enumerate(state['sample_counts']) if not n}
        scalar=policy(state,fallback)
        worst=max(worst,max(abs(x-y) for p,q in zip(scalar,direct) for x,y in zip(p,q)))
    assert worst<1e-12
    sourcepath=Path(__file__).with_name('weighted_root_trajectory_v1.py')
    prefix='weighted-root-trajectory-control-v1'
    rp=OUT/f'{prefix}-registration.json'
    inputs={str(p):sha(p) for p in [pp,pr,*metrics,CATALOG,mp,*Path(__file__).parent.glob('*.py')]}
    save(rp,dict(inputs=inputs,control_only=True,new_deals=0,gpu_used=False))
    output=dict(passed=True,registration_sha256=sha(rp),source_sha256=sha(sourcepath),
        known_answer_cases=3,rejections=rejected,real_pilot_generations=3,real_pilot_class_policies=507,
        maximum_scalar_policy_error=worst,seconds=time.monotonic()-started,
        gpu_used=False,new_deals=0,production_modified=False,full_study_diagnostic_pending=True)
    save(OUT/f'{prefix}-result.json',output)
    print(json.dumps(output),flush=True)


if __name__=='__main__':main()
