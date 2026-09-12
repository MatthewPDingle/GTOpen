"""Verify every combined gate and independent saved audit in the particle screen."""
import gzip
import hashlib
from check_root_repair import checked_local
from check_joint import *


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify():
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    cases=[]
    for samples,seed in ((64,42),(64,314159),(1024,42)):
        for mode in (0,1):
            name=f'particle-quality-s{samples}-seed{seed}-norm{mode}-v1'
            packed=(RAW/(name+'-result.json.gz')).read_bytes()
            data=gzip.decompress(packed);envelope=read(name+'-result-envelope.json')
            require(len(data)==envelope['original_bytes'] and sha(data)==envelope['original_sha256']
                    and sha(packed)==envelope['gzip_sha256'],'Corrupt compressed evidence')
            r=json.loads(data)
            for suffix in ('-exit.json','-audit-exit.json'):
                p=read(name+suffix)
                require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
            require(r['nodes']==23038 and r['samples']==samples and r['seed']==seed
                    and r['normalized'] is bool(mode) and r['schedule']=='gamma15'
                    and r['horizon']==r['limit']==1000,'Wrong configuration')
            require(r['roundtrip_exact'] and r['large_game_qualified'] is False,'Wrong scope')
            streak=0;verified=[]
            for index,c in enumerate(r['checks']):
                require(c['iteration']==25*(index+1) and c['full_reference_samples']==1024,
                        'Wrong check coverage')
                gaps=c['gaps']
                require(len(gaps)==len(c['evs'])==6 and all(math.isfinite(v) and v>=0 for v in gaps)
                        and all(math.isfinite(v) for v in c['evs']),'Invalid global check')
                gap=sum(gaps);require(abs(gap-c['gap'])<1e-12,'Wrong gap sum')
                passed=checked_local(c['rows'],paths)
                require(c['passed']==passed,'Wrong conditional count')
                require(streak<2,'Continued after qualified stop')
                streak=streak+1 if gap<=.005 and passed==6 else 0
                require(c['consecutive_combined_passes']==streak,'Wrong combined streak')
                verified.append(dict(iteration=c['iteration'],gap=gap,passed=passed,streak=streak))
            require(r['qualified'] is (streak>=2) and r['iteration']==r['checks'][-1]['iteration']
                    and (r['qualified'] or r['iteration']==1000),'Wrong terminal condition')
            audit=read(name+'-audit.json')
            require(checked_local(audit['rows'],paths)==verified[-1]['passed'],'Saved pass mismatch')
            for actual,expected in zip(audit['rows'],r['checks'][-1]['rows']):
                require(actual['candidate']==expected['candidate'],'Saved per-hand audit differs')
            replay=None
            if samples==64 and mode==1:
                lab=HERE.parents[3]
                original=lab/'target/convergence'/f'normalized-regret-six-{seed}-1-v1/final.gtop'
                current=lab/'target/convergence'/name/'final.gtop'
                require(sha(original.read_bytes())==sha(current.read_bytes()),'Audit cadence perturbed replay')
                replay=sha(current.read_bytes())
            cases.append(dict(samples=samples,seed=seed,normalized=bool(mode),iteration=r['iteration'],
                              seconds=r['seconds'],solve_seconds=r['solve_seconds'],qualified=r['qualified'],
                              checks=verified,independent_saved_audit_exact=True,replay_sha256=replay))
    require(sum(c['qualified'] for c in cases)==1 and cases[-1]['qualified'],'Unexpected qualification outcome')
    return dict(evidence_verified=True,cases=cases,large_game_qualified=False,
                scope='Small combined-quality screen only; no qualified speedup over failing controls')


if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
