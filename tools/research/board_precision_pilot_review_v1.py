"""Complete-coverage readback and descriptive fixed-policy pilot analysis."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
import math
from pathlib import Path
import time
import numpy as np
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import CLASSES,PAIRS
import board_precision_pilot_v1 as pilot


def label(c):
    # Use the physical-card -> native class map instead of assuming matrix order.
    hand=PAIRS[np.flatnonzero(CLASSES==c)[0]];a,b=sorted([int(x)//4 for x in hand],reverse=True)
    ranks='23456789TJQKA'
    return ranks[a]+ranks[b]+('' if a==b else ('s' if hand[0]%4==hand[1]%4 else 'o'))


def main():
    began=time.monotonic();rp=pilot.REG;result_path=OUT/f'{pilot.PREFIX}-result.json'
    reg=read(rp);result=read(result_path)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    assert reg['boards']==32 and reg['private_deals']==5408 and reg['workers']==4 and reg['no_optional_stopping']
    for path,digest in reg['inputs'].items():assert sha(path)==digest,path
    results={x['id']:x for x in result['results']};jobs={x['id']:x for x in reg['jobs']}
    assert len(results)==len(result['results'])==len(jobs)==117 and set(results)==set(jobs)
    rng=np.random.default_rng(reg['board_seed']);boards=[]
    for _ in range(32):
        b=rng.choice(52,size=5,replace=False).tolist();b[:3]=sorted(b[:3]);boards.append(b)
    source=Path(reg['context']).read_text();private=ClassStratifiedDeals(source,seed=reg['private_seed']).sample(5408)
    sampler=PhysicalDeals(source,mode='full_deck',seed=0);class_mass=np.bincount(CLASSES,weights=sampler.first[0],minlength=169)
    assert private['class_counts']==[32]*169
    board_values=[];private_values=[[] for _ in range(169)];times={'board':[],'private':[]}
    input_hashes={str(rp):sha(rp),str(result_path):sha(result_path),str(Path(__file__)):sha(Path(__file__))}
    checked_files=0
    for jid in sorted(jobs):
        job=jobs[jid];entry=results[jid];assert sha(entry['result'])==entry['sha256'];r=read(entry['result'])
        assert r['id']==jid and r['kind']==job['kind'] and r['worker_wall_seconds']==entry['seconds']
        x=np.asarray(r['variable_values']);assert np.isfinite(x).all() and np.all(x[:,[0,3]]==0)
        times[job['kind']].append(r['worker_wall_seconds']);input_hashes[entry['result']]=entry['sha256']
        if job['kind']=='board':
            i=int(jid.split('-')[1]);assert job['board']==boards[i] and x.shape==(169,4)
            request=pilot.STORE/jid/'request.json';assert sha(request)==r['evidence']['request_sha256']
            q=read(request);assert q['board']==boards[i]
            legal=~np.isin(PAIRS,boards[i]).any(1)
            expected=[PAIRS[np.flatnonzero(legal&(sampler.weights[p]>0))].tolist() for p in (0,1)]
            assert q['hands']==expected and [len(h) for h in expected]==r['evidence']['supported_holdings']
            assert len(r['evidence']['native_tree_sha256'])==64
            board_values.append(x)
        else:
            start=int(jid.split('-')[1])*64;deals=private['deals'][start:start+64];classes=private['hand_classes'][start:start+64]
            assert job['deals']==deals and job['hand_classes']==classes==r['evidence']['hand_classes']
            assert x.shape==(len(deals),4)
            for path,digest in r['evidence']['artifacts'].items():assert sha(path)==digest,path;checked_files+=1
            batch=pilot.STORE/jid/'batch.json';assert read(batch)['deals']==deals
            native=read(pilot.STORE/jid/'values.json')['rows']
            assert [n['deal_index'] for n in native]==list(range(len(deals)))
            assert np.array_equal(x,np.array([n['variable_action_values'] for n in native]))
            for c,v in zip(classes,x):private_values[c].append(v)
    assert len(board_values)==32 and all(len(x)==32 for x in private_values)
    board=np.asarray(board_values);physical=np.transpose(np.asarray(private_values),(1,0,2))
    pilot.initialize(reg);exact=pilot.STATE['exact'];del pilot.STATE
    summaries=[];classes_out=[dict(hand_class=c,hand=label(c),entry_mass=float(class_mass[c]),
        board_action_means=(board[:,c].mean(0)+exact[c]).tolist(),
        private_action_means=(physical[:,c].mean(0)+exact[c]).tolist(),contrasts={}) for c in range(169)]
    for name,a,b in [('raise-call',2,1),('call-fold',1,0),('raise-fold',2,0)]:
        xb=board[:,:,a]-board[:,:,b];xp=physical[:,:,a]-physical[:,:,b]
        vb=xb.var(0,ddof=1);vp=xp.var(0,ddof=1)
        # A separate scalar reduction checks the numeric moments for all classes.
        scalar_error=0.
        for c in range(169):
            for x,v in ((xb,vb),(xp,vp)):
                m=math.fsum(float(z) for z in x[:,c])/32
                vscalar=math.fsum((float(z)-m)**2 for z in x[:,c])/31
                scalar_error=max(scalar_error,abs(vscalar-v[c]))
        assert scalar_error<1e-8
        mean_var_b=float(class_mass@vb/32);mean_var_p=float(class_mass@vp/32)
        cost_b=mean_var_b*sum(times['board']);cost_p=mean_var_p*sum(times['private'])
        summaries.append(dict(contrast=name,board_rms_se=math.sqrt(mean_var_b),private_rms_se=math.sqrt(mean_var_p),
            board_to_private_mean_variance_ratio=mean_var_b/mean_var_p if mean_var_p else None,
            board_to_private_variance_cost_ratio=cost_b/cost_p if cost_p else None,
            scalar_moment_max_error=scalar_error,
            classes_with_lower_board_sample_variance=int(np.sum(vb<vp)),
            entry_mass_with_lower_board_sample_variance=float(class_mass[vb<vp].sum())))
        for c in range(169):
            delta=float(xb[:,c].mean()-xp[:,c].mean());combined=math.sqrt(float((vb[c]+vp[c])/32))
            classes_out[c]['contrasts'][name]=dict(board_sample_variance=float(vb[c]),private_sample_variance=float(vp[c]),
                mean_difference=delta,descriptive_combined_se=combined,
                descriptive_difference_over_se=delta/combined if combined else None)
    class_path=OUT/f'{pilot.PREFIX}-all-classes.json';save(class_path,classes_out)
    report=dict(passed=True,registration_sha256=sha(rp),pilot_result_sha256=sha(result_path),summaries=summaries,
        summed_worker_seconds={k:sum(v) for k,v in times.items()},pilot_elapsed_seconds=result['seconds'],
        class_table=str(class_path),class_table_sha256=sha(class_path),verified_private_artifacts=checked_files,
        inputs=input_hashes,seconds=time.monotonic()-began,accuracy_qualified=False,
        interpretation='Descriptive fixed-policy precision/cost pilot; 32 boards, correlated class errors, no confidence claim or automatic training promotion.')
    save(OUT/f'{pilot.PREFIX}-review.json',report)
    print(json.dumps({k:report[k] for k in ('passed','summaries','summed_worker_seconds','pilot_elapsed_seconds','seconds')}))


if __name__=='__main__':main()
