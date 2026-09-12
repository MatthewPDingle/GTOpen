"""Recompute conditional sampling moments directly from every recorded offset."""
import gzip
import hashlib
from check_joint import *
from check_root_repair import f32


def verify_result(r,paths):
    require(r['samples']==64 and r['offsets']==1024,'Wrong sampler')
    require(r['source_and_device_histories_unchanged'] and r['full_restore_exact'],
            'Missing preservation evidence')
    require([row['path'] for row in r['rows']]==paths,'Wrong path coverage')
    output=[]
    for row in r['rows']:
        source=row['source'];full=row['full_action_values_raw_action_major']
        draws=row['offset_action_values_raw_action_major'];sigma=row['current_sigma_action_major']
        na=len(source['actions']);require(len(full)==len(sigma)==169*na,'Wrong action coverage')
        require(len(draws)==1024 and all(len(d)==len(full) for d in draws),'Wrong offset coverage')
        require(all(math.isfinite(x) for d in draws for x in d)
                and all(math.isfinite(x) for x in full+sigma),'Nonfinite data')
        masses=row['gpu_prefix_mass_by_seat'];denom=1.
        require(all(math.isfinite(v) and v>=0 for v in masses),'Invalid prefix masses')
        for p,m in enumerate(masses):
            require(abs(m-source['current_prefix_mass_by_seat'][p])<=1e-5*(1+abs(m)),
                    'Current prefix snapshot differs')
            if p!=row['actor']:denom=f32(denom*m)
        require(row['zero_opponent_reach'] is (denom==0),'Wrong zero-reach classification')
        denom=max(denom,f32(1e-12))
        require(denom==row['normalized_regret_denominator_f32'],'Wrong normalization denominator')
        cpu=row['cpu_reference'];hands=[]
        require([h['class_index'] for h in source['hands']]==list(range(169)),'Wrong hand order')
        for h,hand in enumerate(source['hands']):
            probabilities=[sigma[a*169+h] for a in range(na)]
            require(all(0<=p<=1 for p in probabilities) and abs(sum(probabilities)-1)<1e-5
                    and probabilities==hand['current_probabilities'],'Wrong frozen current policy')
            q=[full[a*169+h]/denom for a in range(na)]
            full_delta=[v-sum(v*p for v,p in zip(q,probabilities)) for v in q]
            sums=[0.]*na;sumsq=[0.]*na;products=[[0.]*na for _ in range(na)]
            raw_sum=[0.]*na;promoted=0
            acceptable=[a for a,v in enumerate(q) if max(q)-v<=.1]
            inferior=[a for a in range(na) if a not in acceptable]
            for draw in draws:
                raw=[draw[a*169+h] for a in range(na)]
                values=[v/denom for v in raw];base=sum(v*p for v,p in zip(values,probabilities))
                delta=[v-base for v in values]
                if inferior and max(values[a] for a in inferior)>max(values[a] for a in acceptable):promoted+=1
                for a in range(na):
                    raw_sum[a]+=raw[a];sums[a]+=delta[a];sumsq[a]+=delta[a]*delta[a]
                    for b in range(na):products[a][b]+=delta[a]*delta[b]
            mean=[v/1024 for v in sums]
            variance=[max(0.,sumsq[a]/1024-mean[a]*mean[a]) for a in range(na)]
            bias=[mean[a]-full_delta[a] for a in range(na)]
            for a in range(na):
                raw_full=full[a*169+h]
                require(abs(raw_sum[a]/1024-raw_full)<=.0002*(1+abs(raw_full)),
                        'Cyclic estimator mean differs from canonical value')
                if cpu['status']=='evaluated':
                    expected=cpu['hands'][h]['action_values_bb'][a]*cpu['opponent_mass']
                    require(abs(raw_full-expected)<=.0002*(1+abs(expected)),
                            'Full action value differs from CPU reference')
            covariance=[[products[a][b]/1024-mean[a]*mean[b] for b in range(na)] for a in range(na)]
            ordered=sorted(q,reverse=True);best_margin=ordered[0]-ordered[1] if len(ordered)>1 else None
            hands.append(dict(class_index=h,hand=hand['hand'],current_hand_mass=hand['current_conditional_hand_mass'],
                full_normalized_action_values=q,full_normalized_regret_difference=full_delta,
                regret_mean=mean,regret_bias=bias,regret_variance=variance,regret_mse=[v+b*b for v,b in zip(variance,bias)],
                raw_regret_mean=[v*denom for v in mean],raw_regret_bias=[v*denom for v in bias],
                raw_regret_variance=[v*denom*denom for v in variance],
                regret_covariance=covariance,probability_strictly_promoting_inferior_action=promoted/1024))
            hands[-1]['full_best_action_margin_bb']=best_margin
            hands[-1]['best_action_reversal_probability']=promoted/1024 if best_margin is not None and best_margin>.1 else None
        relevant=[h for h in hands if h['current_hand_mass']>=.0025]
        output.append(dict(path=row['path'],actor=row['actor'],forced=source['forced'],frozen=source['frozen'],
            zero_opponent_reach=row['zero_opponent_reach'],denominator=denom,
            cpu_reference_status=cpu['status'],hands=hands,
            worst_relevant_promotion=max((h['probability_strictly_promoting_inferior_action'] for h in relevant),default=None)))
    return dict(evidence_verified=True,source_iteration=r['source_iteration'],rows=output,
                scope='Fixed-current-policy sampling moments; no convergence, speed or deployment qualification')


def case(name):
    for suffix in ('-exit.json',):
        p=read(name+suffix);require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
    packed=(RAW/(name+'-result.json.gz')).read_bytes();data=gzip.decompress(packed)
    envelope=read(name+'-result-envelope.json')
    require(len(data)==envelope['original_bytes']
            and hashlib.sha256(data).hexdigest()==envelope['original_sha256']
            and hashlib.sha256(packed).hexdigest()==envelope['gzip_sha256'],'Corrupt evidence archive')
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    r=json.loads(data);require(r['nodes']==23038 and r['source_iteration'] in (950,1000),'Wrong source fixture')
    return verify_result(r,paths)


if __name__=='__main__':
    require(len(sys.argv)==2,'Expected registered artifact name')
    print(json.dumps(case(sys.argv[1]),indent=2))
