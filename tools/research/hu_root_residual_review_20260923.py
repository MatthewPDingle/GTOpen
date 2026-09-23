"""Independent scalar reconstruction of the old-sample residual diagnostic."""
import json
import math
from pathlib import Path
import time
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='root-residual-diagnostic-v1'


def read(p):return json.loads(Path(p).read_text())


def stats(xs):
    mean=math.fsum(xs)/len(xs)
    return mean,math.fsum((x-mean)**2 for x in xs)/(len(xs)-1)


def main():
    start=time.monotonic();assert idle()
    rp,pp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    sr=read(OUT/f'{reg["source"]}-registration.json');store=Path(sr['store'])
    policy=read('S:/GTOpen-research/exhaustive-btn-response-v2/combined_269-policy.json')
    baseline=policy['root_probabilities'];response=read(store/'response.json')
    exact=read(OUT/'bb-fold-jam-response-v3-result.json')['candidates']['combined_269']['classes']
    context=read(sr['context']);L=-context['config']['stack'];U=-L+context['dead_money']
    data={}
    for phase,n in [('train',8192),('test',16384)]:
        rows=[]
        for offset in range(0,n,16):
            path=store/f'{reg["source"]}-{phase}-{offset}'/'summary.json'
            assert reg['inputs'][str(path)]==sha(path)
            s=read(path);rows.extend(zip(s['classes'],s['action_values'],s['baseline_values']))
        assert len(rows)==n;data[phase]=rows
    max_error=0.;checks={}
    for name,record in result['comparisons'].items():
        assert idle() and time.monotonic()-start<600
        rho=[]
        for c in range(169):
            action=response['actions'][c] if name=='trained-response' else ['always-fold','always-call','always-raise','always-jam'].index(name)
            rho.append(baseline[c] if action<0 else [float(a==action) for a in range(4)])
        d=[[rho[c][a]-baseline[c][a] for a in range(4)] for c in range(169)]
        training=[[] for _ in range(169)]
        for c,q,_ in data['train']:training[c].append(d[c][1]*q[1]+d[c][2]*q[2])
        raw=[math.fsum(rho[c][a]*q[a] for a in range(4))-base for c,q,base in data['test']]
        original_mean,original_var=stats(raw)
        max_error=max(max_error,abs(original_mean-record['original_mean']),abs(original_var-record['original_sample_variance']))
        versions={}
        for name2,version in record['versions'].items():
            centred=name2=='centred'
            centre=[math.fsum(t)/len(t) if centred and t else 0. for t in training]
            p=version['prepared'];assert p['delta']==d and p['counts']==list(map(len,training))
            max_error=max(max_error,max(abs(a-b) for a,b in zip(centre,p['centre'])))
            exact_part=math.fsum(row['entry_probability']*(d[c][0]*row['fold_value']+d[c][3]*row['jam_value']) for c,row in enumerate(exact))
            known_centre=math.fsum(row['entry_probability']*centre[c] for c,row in enumerate(exact))
            residual=[math.fsum([d[c][1]*q[1],d[c][2]*q[2],-centre[c]]) for c,q,_ in data['test']]
            mean,var=stats(residual);estimate=mean+exact_part+known_centre
            corners=[d[c][1]*q1+d[c][2]*q2-centre[c] for c in range(169) for q1 in (L,U) for q2 in (L,U)]
            lo,hi=min(corners)-1e-9,max(corners)+1e-9
            log=math.log(800.)
            def r(n):return (2*var*log/n)**.5+7*(hi-lo)*log/(3*(n-1))
            for a,b in [(exact_part,p['exact_fold_jam_offset']),(known_centre,p['centre_population_offset']),
                (exact_part+known_centre,p['total_offset']),(estimate,version['descriptive_mean']),
                (var,version['sample_variance']),(var/original_var,version['variance_ratio_to_original']),
                (lo,p['residual_lower']),(hi,p['residual_upper']),(r(16384),version['hypothetical_radius_at_old_count'])]:
                max_error=max(max_error,abs(a-b))
            assert min(residual)>=lo and max(residual)<=hi
            for target,n in version['hypothetical_deals_for_radius'].items():
                assert n is not None and r(n)<=float(target) and (n==2 or r(n-1)>float(target))
            versions[name2]=dict(sample_variance=var,descriptive_mean=estimate,all_analytic_corners_checked=676)
        checks[name]=versions
    assert max_error<1e-8
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    assert idle() and time.monotonic()-start<600
    review=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),reviewer_sha256=sha(Path(__file__)),
        maximum_scalar_error=max_error,comparisons=checks,seconds=time.monotonic()-start,
        gpu_used=False,production_modified=False,accuracy_qualified=False,
        scope='Scalar sums, training-only centres, physical payoff corners and hypothetical sample counts reconstructed. Reuses old inspected data; not independent strategic confirmation.')
    save(OUT/f'{PREFIX}-independent-review.json',review);print(review)


if __name__=='__main__':main()
