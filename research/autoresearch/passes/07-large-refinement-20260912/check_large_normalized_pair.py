"""Independent per-seed acceptance gate for large corrected normalization."""
import gzip
import hashlib
from check_root_repair import checked_local
from check_joint import *

import sys


def verify(seed=42):
    require(seed in (42,314159), "Unregistered seed")
    NAME=f"large-normalized-pair-seed{seed}-v1"
    packed=(RAW/(NAME+'-result.json.gz')).read_bytes()
    data=gzip.decompress(packed);envelope=read(NAME+'-result-envelope.json')
    require(len(data)==envelope['original_bytes']
            and hashlib.sha256(data).hexdigest()==envelope['original_sha256']
            and hashlib.sha256(packed).hexdigest()==envelope['gzip_sha256'],
            'Corrupt compressed evidence')
    r=json.loads(data);paths=json.loads((HERE/'broad-paths.json').read_text())
    require(len(paths)==27 and len({tuple(p) for p in paths})==27,'Wrong path set')
    for suffix in ('-exit.json','-audit-exit.json'):
        p=read(NAME+suffix)
        require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
    require(r['nodes']==1567754 and r['samples']==64 and r['seed']==seed and r['pair'] is True and 0<r['pair_extra_bytes']<=1024*1024*1024
            and r['normalized'] is True and r['schedule']=='gamma15'
            and r['horizon']==1000 and r['limit']==3000,'Wrong registered experiment')
    require(r['roundtrip_exact'] and r['independent_saved_audit_pending']
            and r['large_game_qualified'] is False,'Premature qualification')
    streak=0;checks=[]
    require(1<=len(r['checks'])<=60,'Wrong check count')
    for index,c in enumerate(r['checks']):
        require(c['iteration']==50*(index+1) and c['full_reference_samples']==1024,
                'Wrong check cadence or model')
        gaps=c['gaps'];evs=c['evs']
        require(len(gaps)==len(evs)==8 and all(math.isfinite(v) and v>=0 for v in gaps)
                and all(math.isfinite(v) for v in evs),'Invalid global check')
        gap=sum(gaps);require(abs(gap-c['gap'])<1e-12,'Wrong gap sum')
        passed=checked_local(c['rows'],paths)
        require(c['passed']==passed and streak<2,'Wrong count or late stopping')
        streak=streak+1 if gap<=.005 and passed==27 else 0
        require(c['consecutive_combined_passes']==streak,'Wrong combined gate')
        checks.append(dict(iteration=c['iteration'],gap=gap,passed=passed,streak=streak,
                           elapsed_seconds=c['elapsed_seconds']))
    require(r['qualified'] is (streak>=2) and r['iteration']==checks[-1]['iteration']
            and (r['qualified'] or r['iteration']==3000),'Wrong terminal condition')
    audit=read(NAME+'-audit.json')
    require(checked_local(audit['rows'],paths)==checks[-1]['passed'],'Saved count differs')
    for actual,expected in zip(audit['rows'],r['checks'][-1]['rows']):
        require(actual['candidate']==expected['candidate'],'Saved per-hand record differs')
    return dict(evidence_verified=True,combined_quality_passed=streak>=2,large_game_qualified=False,seed=seed,checks=checks,
                seconds=r['seconds'],solve_seconds=r['solve_seconds'],
                setup_seconds=r['setup_seconds'],save_validation_seconds=r['save_validation_seconds'],
                independent_saved_audit_exact=True,
                scope='Canonical coupled-deck model, global gap and 27 one-action conditional checks; no deployment or qualified speedup claim')


if __name__=='__main__':
    print(json.dumps(verify(int(sys.argv[1]) if len(sys.argv)>1 else 42),indent=2))
