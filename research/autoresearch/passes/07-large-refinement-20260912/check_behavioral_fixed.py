"""Independent gates, fixed checkpoint coverage and saved-file audit verification."""
import gzip,hashlib,json,math
from run07 import HERE,RAW,digest
from check_joint import require
from check_root_repair import checked_local
from run_behavioral_fixed import CASES,name
def verify():
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text());cases=[];sources=[];executables=[]
    prerequisites=[]
    for label in ('behavioral-numerical-v1','behavioral-native-compat-v1','behavioral-default-suite-v1','behavioral-build-v1'):
        run=json.loads((RAW/(label+'-exit.json')).read_text())
        require(run['returncode']==0 and run['reason'] is None,'Failed prerequisite '+label)
        for path,h in run['inputs'].items():require(digest(path)==h,'Changed prerequisite input '+path)
        prerequisites.append({k:v for k,v in run['solver_source_files'].items() if '/src/' in k.replace('\\','/')})
    for e in CASES:
        n=name(e);process=json.loads((RAW/(n+'-exit.json')).read_text())
        audit_process=json.loads((RAW/(n+'-audit-exit.json')).read_text())
        for run in (process,audit_process):
            require(run['returncode']==0 and run['reason'] is None,'Incomplete '+n)
            for path,h in run['inputs'].items():require(digest(path)==h,'Changed input '+path)
        sources.append(process['solver_source_files']);executables.append(process['exe_sha256'])
        packed=RAW/(n+'-result.json.gz');data=gzip.decompress(packed.read_bytes());r=json.loads(data)
        env=json.loads((RAW/(n+'-result-envelope.json')).read_text())
        require(digest(packed)==env['gzip_sha256'] and hashlib.sha256(data).hexdigest()==env['original_sha256'] and len(data)==env['original_bytes'],'Result hash')
        require((r['nodes'],r['samples'],r['seed'],r['epsilon_label'])==(23038,1024,42,e) and abs(r['epsilon']-float(e))<1e-8,'Wrong case')
        require(r['schedule']=='gamma15' and r['horizon']==1000 and r['limit']==r['iteration']==1000,'Wrong schedule')
        require(r['roundtrip_exact'] and r['fresh_saved_evaluation_exact'] and not r['large_game_qualified'] and not r['normal_global_resume_supported'],'Wrong scope/preservation')
        checks=r['checks'];require([c['iteration'] for c in checks]==list(range(50,1001,50)),'Missing checkpoints')
        streak=0;compact=[]
        for c in checks:
            g=c['gaps'];v=c['evs'];k=c['constrained_gaps']
            require(len(g)==len(v)==len(k)==6 and all(math.isfinite(x) for x in g+v+k),'Invalid diagnostics')
            require(min(g)>=-1e-6 and min(k)>=-1e-6 and all(a<=b+1e-5 for a,b in zip(k,g)),'Invalid constrained bound')
            require(abs(sum(g)-c['gap'])<1e-12 and abs(sum(k)-c['constrained_gap'])<1e-12 and c['full_reference_samples']==1024,'Wrong aggregate')
            passed=checked_local(c['rows'],paths);streak=streak+1 if c['gap']<=0.005 and passed==6 else 0
            require(c['passed']==passed and c['consecutive_combined_passes']==streak,'Wrong local gates')
            compact.append(dict(iteration=c['iteration'],gap=c['gap'],constrained_gap=c['constrained_gap'],passed=passed))
        audit=json.loads((RAW/(n+'-audit.json')).read_text())
        require([x['candidate'] for x in audit['rows']]==[x['candidate'] for x in checks[-1]['rows']],'Saved audit differs')
        require(0<r['solve_seconds']<=r['seconds'] and math.isfinite(r['seconds']),'Wrong timing')
        cases.append(dict(epsilon=float(e),seconds=r['seconds'],final=compact[-1],checks=compact))
    require(all(s==sources[0] for s in sources) and len(set(executables))==1,'Different source/executable')
    library={k:v for k,v in sources[0].items() if '/src/' in k.replace('\\','/')}
    require(all(p==library for p in prerequisites),'Library changed since prerequisite validation')
    baseline=cases[0]['final']['passed'];admitted=[]
    for c in cases[1:]:
        c['transition_design_admitted']=c['final']['passed']>baseline and c['final']['constrained_gap']<=0.005
        if c['transition_design_admitted']:admitted.append(c['epsilon'])
    return dict(evidence_verified=True,cases=cases,transition_design_candidates=admitted,
        large_game_qualified=False,scope='Fixed epsilon diagnostic; no transition or speed qualification')
if __name__=='__main__':print(json.dumps(verify(),indent=2))
