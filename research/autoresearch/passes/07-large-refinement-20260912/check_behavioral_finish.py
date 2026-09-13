"""Recompute native finishing gates and complete two-stage cost."""
import gzip,hashlib,json,math
from run07 import HERE,RAW,digest
from check_joint import require
from check_root_repair import checked_local
from run_behavioral_finish import CASES,name,pretrain_name
def verify():
    from check_behavioral_fixed import verify as fixed
    prior=fixed();require(prior['transition_design_candidates']==[0.01,0.05],'Prior admission changed')
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text());cases=[];sources=[];executables=[];prereqs=[]
    for label in ('behavioral-transition-numerical-v1','behavioral-finish-native-v1','behavioral-finish-default-v1','behavioral-finish-build-v1'):
        r=json.loads((RAW/(label+'-exit.json')).read_text());require(r['returncode']==0 and r['reason'] is None,'Failed prerequisite')
        for p,h in r['inputs'].items():require(digest(p)==h,'Changed prerequisite input')
        prereqs.append({k:v for k,v in r['solver_source_files'].items() if '/src/' in k.replace('\\','/')})
    for eps,mode in CASES:
        n=name(eps,mode);process=json.loads((RAW/(n+'-exit.json')).read_text());audit_process=json.loads((RAW/(n+'-audit-exit.json')).read_text())
        for r in (process,audit_process):
            require(r['returncode']==0 and r['reason'] is None,'Incomplete '+n)
            for p,h in r['inputs'].items():require(digest(p)==h,'Changed input '+p)
        sources.append(process['solver_source_files']);executables.append(process['exe_sha256'])
        packed=RAW/(n+'-result.json.gz');data=gzip.decompress(packed.read_bytes());r=json.loads(data)
        env=json.loads((RAW/(n+'-result-envelope.json')).read_text())
        require(digest(packed)==env['gzip_sha256'] and hashlib.sha256(data).hexdigest()==env['original_sha256'] and len(data)==env['original_bytes'],'Result hash')
        require((r['nodes'],r['samples'],r['seed'],r['epsilon_label'],r['reset'])==(23038,1024,42,eps,mode=='reset'),'Wrong case')
        require(r['schedule']=='gamma15' and r['horizon']==1000 and r['limit']==1000 and r['original_iteration']==1000,'Wrong schedule')
        require(all(r[k] is True for k in ('retained_regrets_exact','initialization_exact','native_only','roundtrip_exact','fresh_saved_evaluation_exact')),'Preservation/evaluation mismatch')
        require(not r['large_game_qualified'] and not r['normal_global_resume_supported'],'Invalid scope')
        prep=r['preparation'];require((prep['reset_entries']>0 and prep['reset_learning_nodes']>0 and prep['iteration']==1000) if mode=='reset' else (prep['reset_entries']==prep['reset_learning_nodes']==0),'Wrong reset')
        checks=r['checks'];require([c['iteration'] for c in checks]==list(range(1025,r['iteration']+1,25)) and 1025<=r['iteration']<=2000,'Missing checkpoints')
        streak=0;compact=[]
        for c in checks:
            g=c['gaps'];v=c['evs'];require(len(g)==len(v)==6 and all(math.isfinite(x) for x in g+v) and min(g)>=-1e-6,'Invalid full diagnostics')
            require(abs(sum(g)-c['gap'])<1e-12 and c['full_reference_samples']==1024 and c['finishing_iteration']==c['iteration']-1000,'Wrong aggregation/age')
            passed=checked_local(c['rows'],paths);streak=streak+1 if c['gap']<=0.005 and passed==6 else 0
            require(c['passed']==passed and c['consecutive_combined_passes']==streak,'Wrong combined gates')
            if c is not checks[-1]:require(streak<2,'Continued a qualified case')
            compact.append(dict(iteration=c['iteration'],gap=c['gap'],passed=passed,streak=streak))
        require(r['qualified'] is (streak>=2) and (r['qualified'] or r['iteration']==2000),'Wrong stopping')
        audit=json.loads((RAW/(n+'-audit.json')).read_text());require([x['candidate'] for x in audit['rows']]==[x['candidate'] for x in checks[-1]['rows']],'Saved audit mismatch')
        pre=json.loads(gzip.decompress((RAW/(pretrain_name(eps)+'-result.json.gz')).read_bytes()))
        require(pre['seconds']==r['pretrain_seconds'] and 0<r['solve_seconds']<=r['finishing_seconds'] and math.isfinite(r['finishing_seconds']),'Invalid stage timing')
        require(abs(r['total_seconds']-r['pretrain_seconds']-r['finishing_seconds'])<1e-9,'Excluded pretraining cost')
        cases.append(dict(epsilon=float(eps),mode=mode,qualified=r['qualified'],pretrain_seconds=r['pretrain_seconds'],finishing_seconds=r['finishing_seconds'],total_seconds=r['total_seconds'],final=compact[-1],checks=compact))
    require(all(s==sources[0] for s in sources) and len(set(executables))==1,'Source/executable mismatch')
    library={k:v for k,v in sources[0].items() if '/src/' in k.replace('\\','/')};require(all(p==library for p in prereqs),'Library changed after validation')
    control=cases[1];eligible=[]
    for c in cases[2:]:
        c['next_small_screen_admitted']=c['qualified'] and (not control['qualified'] or c['total_seconds']<=control['total_seconds'])
        c['measured_speedup']=control['total_seconds']/c['total_seconds'] if c['qualified'] and control['qualified'] else None
        if c['next_small_screen_admitted']:eligible.append(c['epsilon'])
    return dict(evidence_verified=True,cases=cases,next_small_screen_candidates=eligible,large_game_qualified=False,
        scope='First-seed two-stage native finish, no large speed qualification')
if __name__=='__main__':print(json.dumps(verify(),indent=2))
