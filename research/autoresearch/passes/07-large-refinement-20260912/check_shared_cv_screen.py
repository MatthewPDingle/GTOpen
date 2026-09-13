"""Independent first-seed CV screen gates and saved-state audit verifier."""
import gzip,hashlib,json,math
from run07 import HERE,LAB,RAW,digest
from check_joint import require
from check_root_repair import checked_local
from run_shared_cv_screen import CASES,name
def verify():
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text());cases=[];source_versions=[];exe_hashes=[]
    for samples,mode in CASES:
        n=name(samples,mode);process=json.loads((RAW/(n+'-exit.json')).read_text())
        audit_process=json.loads((RAW/(n+'-audit-exit.json')).read_text())
        for run in (process,audit_process):
            require(run['returncode']==0 and run['reason'] is None,'Incomplete case '+n)
            for path,h in run['inputs'].items():require(digest(path)==h,'Changed input '+path)
        source_versions.append(process['solver_source_files']);exe_hashes.append(process['exe_sha256'])
        packed=RAW/(n+'-result.json.gz');data=gzip.decompress(packed.read_bytes());r=json.loads(data)
        envelope=json.loads((RAW/(n+'-result-envelope.json')).read_text())
        require(digest(packed)==envelope['gzip_sha256'] and hashlib.sha256(data).hexdigest()==envelope['original_sha256'] and len(data)==envelope['original_bytes'],'Result hash mismatch')
        require((r['nodes'],r['samples'],r['seed'],r['mode'])==(23038,samples,42,mode),'Wrong case')
        require(r['schedule']=='gamma15' and r['horizon']==1000 and r['limit']==3000 and r['roundtrip_exact'] is True,'Schedule/preservation mismatch')
        require(r['large_game_qualified'] is False,'Unsupported qualification')
        checks=r['checks'];require([c['iteration'] for c in checks]==list(range(25,r['iteration']+1,25)),'Incomplete check trajectory')
        streak=0;compact=[]
        for c in checks:
            gaps=c['gaps'];evs=c['evs'];require(len(gaps)==len(evs)==6 and all(math.isfinite(x) for x in gaps+evs) and min(gaps)>=0,'Invalid global values')
            require(abs(sum(gaps)-c['gap'])<1e-12 and c['full_reference_samples']==1024,'Noncanonical gap')
            passed=checked_local(c['rows'],paths);streak=streak+1 if c['gap']<=0.005 and passed==6 else 0
            require(c['passed']==passed and c['consecutive_combined_passes']==streak,'Wrong gate/streak')
            if c is not checks[-1]:require(streak<2,'Continued qualified case')
            compact.append(dict(iteration=c['iteration'],gap=c['gap'],passed=passed,streak=streak))
        require(r['qualified'] is (streak>=2) and (r['qualified'] or r['iteration']==3000),'Incorrect stopping decision')
        if mode.startswith('shared'):
            interval=int(mode[6:]);stats=r['shared_stats'];s=stats['storage']
            require(s==r['storage'] and s['persistent_extra_bytes']<=4*1024**3 and s['fits_four_gib'],'Wrong shared storage')
            expected=(r['iteration']-1)//interval+1
            require(stats['refresh_epochs']==expected and stats['last_refresh_iteration']==(expected-1)*interval and stats['captured_sweeps']==6,'Wrong refresh/capture behavior')
            require(r['cv_stats']==[s['persistent_extra_bytes'],expected],'Wrong CV stats')
        elif mode=='old32':
            require(r['shared_stats'] is None and r['cv_stats'][1]==6*((r['iteration']-1)//32+1),'Old reference refresh changed')
        else:require(r['shared_stats'] is None and r['cv_stats'] is None and r['storage']['persistent_extra_bytes']==0,'Control enabled CV')
        audit=json.loads((RAW/(n+'-audit.json')).read_text())
        require([x['candidate'] for x in audit['rows']]==[x['candidate'] for x in checks[-1]['rows']],'Independent saved audit mismatch')
        require(math.isfinite(r['seconds']) and r['seconds']>0 and 0<r['solve_seconds']<=r['seconds'],'Invalid timing')
        cases.append(dict(samples=samples,mode=mode,seconds=r['seconds'],iteration=r['iteration'],qualified=r['qualified'],final=compact[-1],checks=compact,extra_bytes=r['storage']['persistent_extra_bytes']))
    require(all(v==source_versions[0] for v in source_versions) and len(set(exe_hashes))==1,'Cases used different implementations')
    full=cases[0];plain=cases[1];eligible=[]
    for c in cases[3:]:
        c['full_time_ratio']=c['seconds']/full['seconds'];c['plain_time_ratio']=c['seconds']/plain['seconds']
        c['passes_screen']=c['qualified'] and full['qualified'] and c['full_time_ratio']<=0.5 and (not plain['qualified'] or c['plain_time_ratio']<=2)
        if c['passes_screen']:eligible.append(c)
    selected=min(eligible,key=lambda c:c['seconds'])['mode'] if eligible else None
    return dict(evidence_verified=True,cases=cases,selected_second_seed_mode=selected,second_seed_admitted=selected is not None,
        large_game_qualified=False,scope='First seed small convergence screen only; no large deployment qualification')
if __name__=='__main__':print(json.dumps(verify(),indent=2))
