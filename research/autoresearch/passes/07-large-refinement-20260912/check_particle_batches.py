"""Independently verify the frozen partition and every recorded numerical gate."""
import hashlib,struct
from check_pair_control import near
from check_joint import *


def verify():
    construction=read('particle-batch-construction-v1-exit.json')
    numerical=read('particle-batch-numerical-v1-exit.json')
    for p in (construction,numerical):
        require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
    require(construction['solver_source_files']==numerical['solver_source_files'],'Sources changed after freezing construction')
    manifest=read('particle-batch-manifest-v1.json')
    require(manifest['construction_seed']==90211,'Changed construction seed')
    permutation=manifest['permutation'];strata=manifest['strata']
    require(sorted(permutation)==list(range(1024)),'Particle omission or duplication')
    require(len(strata)==64 and all(len(s)==16 for s in strata),'Incorrect stratum shape')
    require(sorted(p for s in strata for p in s)==list(range(1024)),'Invalid partition')
    require(permutation==[s[j] for j in range(16) for s in strata],'Batch does not sample each stratum once')
    checksum=0xcbf29ce484222325
    for p in permutation:
        for byte in struct.pack('<I',p):checksum=((checksum^byte)*0x100000001b3)&((1<<64)-1)
    require(manifest['checksum_fnv64']==f'{checksum:016x}','Checksum mismatch')
    expected_hash=hashlib.sha256((RAW/'particle-batch-manifest-v1.json').read_bytes()).hexdigest()
    require(len(numerical['inputs'])==1 and list(numerical['inputs'].values())==[expected_hash],'Frozen manifest changed')
    data=read('particle-batch-variance-v1.json');rows=data['fixtures']
    require([(r['players'],r['family']) for r in rows]==[(n,f) for n in (3,4,6,8) for f in range(3)],'Incomplete fixture coverage')
    variances=[]
    for r in rows:
        require(r['checksum_fnv64']==manifest['checksum_fnv64'],'Different partition used')
        require(r['samples']==64 and r['counts']==[1024,16],'Wrong sample count or incomplete estimator support')
        require([h['class_index'] for h in r['hands']]==list(range(169)),'Missing hand classes')
        pooled=[0.,0.]
        for h in r['hands']:
            a,b=divmod(h['class_index'],13)
            weight=struct.unpack('f',struct.pack('f',(6 if a==b else 4 if a>b else 12)/1326))[0]
            require(len(h['bias_bb'])==len(h['variance_bb2'])==2,'Missing estimator')
            require(all(math.isfinite(x) and abs(x)<.0002 for x in h['bias_bb']),'Biased sample mean')
            require(all(math.isfinite(x) and x>=0 for x in h['variance_bb2']),'Invalid variance')
            for i in range(2):pooled[i]+=weight*h['variance_bb2'][i]
            if h['variance_bb2'][0]>1e-10:near(h['ratio'],h['variance_bb2'][1]/h['variance_bb2'][0])
            else:require(h['ratio'] is None,'Unstable variance ratio')
        for i in range(2):near(pooled[i],r['pooled_variance'][i])
        near(r['ratio'],pooled[1]/pooled[0]);variances.append(pooled)
    ratio=sum(v[1] for v in variances)/sum(v[0] for v in variances)
    eight_ratio=sum(v[1] for v in variances[-3:])/sum(v[0] for v in variances[-3:])
    near(ratio,data['pooled_ratio']);near(eight_ratio,data['eight_player_ratio'])
    passed=ratio<=.9 and all(r['ratio']<=1.25 for r in rows)
    require(data['passed'] is passed,'Incorrect gate decision')
    return dict(evidence_verified=True,passed=passed,checksum_fnv64=manifest['checksum_fnv64'],
                pooled_ratio=ratio,eight_player_ratio=eight_ratio,
                fixtures=[dict(players=r['players'],family=r['family'],ratio=r['ratio']) for r in rows])


if __name__=='__main__':print(json.dumps(verify(),indent=2))
