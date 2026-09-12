"""Recompute the independent-stratum variance diagnostic and registered gate."""
import hashlib,struct
from check_joint import *
from check_pair_control import near
from check_particle_batches import verify as fixed_verify


def verify():
    fixed=fixed_verify()
    p=read('particle-independent-numerical-v1-exit.json')
    require(p['returncode']==0 and p['reason'] is None,'Incomplete diagnostic')
    expected_hash=hashlib.sha256((RAW/'particle-batch-manifest-v1.json').read_bytes()).hexdigest()
    require(len(p['inputs'])==1 and list(p['inputs'].values())==[expected_hash],'Frozen partition changed')
    data=read('particle-independent-variance-v1.json');rows=data['fixtures']
    require([(r['players'],r['family']) for r in rows]==[(n,f) for n in (3,4,6,8) for f in range(3)],'Missing fixtures')
    old=read('particle-batch-variance-v1.json')['fixtures'];weighted=[]
    for r,previous in zip(rows,old):
        require(r['checksum_fnv64']==fixed['checksum_fnv64'],'Changed partition')
        require((r['native_samples'],r['particle_outcomes'],r['strata'],r['stratum_size'])==(64,1024,64,16),'Wrong support')
        require([h['class_index'] for h in r['hands']]==list(range(169)),'Missing hand classes')
        pooled=[0.,0.]
        for h,old_hand in zip(r['hands'],previous['hands']):
            require(len(h['variance_bb2'])==2,'Missing estimator')
            require(all(math.isfinite(v) and abs(v)<.0002 for v in
                        (h['native_mean_bias_bb'],h['particle_mean_bias_bb'],h['stratum_mean_bias_bb'])),'Biased mean')
            near(h['stratum_mean_bias_bb'],h['particle_mean_bias_bb'],1e-10)
            require(math.isfinite(h['within_variance_sum_bb2']) and h['within_variance_sum_bb2']>=0,'Invalid within variance')
            require(all(math.isfinite(v) and v>=0 for v in h['variance_bb2']),'Invalid variance')
            near(h['variance_bb2'][1],h['within_variance_sum_bb2']/4096)
            # Same fixed ranges and native kernel should reproduce the earlier control.
            near(h['variance_bb2'][0],old_hand['variance_bb2'][0],1e-8)
            near(h['native_mean_bias_bb'],old_hand['bias_bb'][0],1e-8)
            if h['variance_bb2'][0]>1e-10:near(h['ratio'],h['variance_bb2'][1]/h['variance_bb2'][0])
            else:require(h['ratio'] is None,'Unstable ratio')
            a,b=divmod(h['class_index'],13)
            weight=struct.unpack('f',struct.pack('f',(6 if a==b else 4 if a>b else 12)/1326))[0]
            for i in range(2):pooled[i]+=weight*h['variance_bb2'][i]
        for i in range(2):near(pooled[i],r['pooled_variance'][i])
        near(r['ratio'],pooled[1]/pooled[0]);weighted.append(pooled)
    ratio=sum(r[1] for r in weighted)/sum(r[0] for r in weighted)
    eight_ratio=sum(r[1] for r in weighted[-3:])/sum(r[0] for r in weighted[-3:])
    near(ratio,data['pooled_ratio']);near(eight_ratio,data['eight_player_ratio'])
    passed=ratio<=.9 and all(r['ratio']<=1.25 for r in rows)
    require(data['passed'] is passed,'Incorrect gate')
    return dict(evidence_verified=True,passed=passed,pooled_ratio=ratio,eight_player_ratio=eight_ratio,
                fixtures=[dict(players=r['players'],family=r['family'],ratio=r['ratio']) for r in rows])


if __name__=='__main__':print(json.dumps(verify(),indent=2))
