"""Deadline-bound reference generation and fixed data-expansion evaluation."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import datetime as dt
import json
import msvcrt
import subprocess
import sys
import numpy as np
import continuation_range_bridges as bridge

study=bridge.study
OUT=bridge.OUT
DEADLINE=dt.datetime(2026,9,16,20,49,2,tzinfo=dt.timezone.utc)


def checked(partition):
    m=study.read(OUT/partition/'manifest.json')
    assert study.signed({k:v for k,v in m.items() if k!='id'})==m
    for path,sha in m['inputs'].items():assert study.pilot.sha(study.ROOT/path)==sha,path
    return m


def other_research():
    command="Get-CimInstance Win32_Process | Select-Object Name,ProcessId,CommandLine | ConvertTo-Json -Compress"
    result=subprocess.run(['powershell.exe','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
    found=[]
    for p in json.loads(result.stdout):
        if p['ProcessId']==os.getpid():continue
        name=p['Name'].lower();cmd=(p['CommandLine'] or '').lower()
        if name.startswith('range-value-reference') or name in ['learned_interface.exe','learned_decisions.exe']:
            found.append(p)
        if name=='python.exe' and ('continuation_policy_refinement.py run' in cmd or 'continuation_overnight.py run' in cmd):
            found.append(p)
    return found


def validate_reference(r,j,m):
    assert r['manifest_id']==m['id'] and study.same_job(r['job'],j) and r['target_met']
    assert r['query_mode']=='materialized_full_enumeration'
    assert 0<=r['gap_pct']<=m['target_gap_pct'] and 0<=r['gpu_gap_pct']<=m['target_gap_pct']
    assert abs(sum(r['means_bb'])-j['config']['tree']['starting_pot'])<.002
    assert r['pair_mass']>0
    for p in range(2):
        mass=sum(h['pair_mass'] for h in r['hands'][p])
        assert abs(mass/r['pair_mass']-1)<1e-5
        mean=sum(h['pair_mass']*h['ev_bb'] for h in r['hands'][p])/mass
        assert abs(mean-r['means_bb'][p])<1e-6
        assert all(np.isfinite([h['pair_mass'],h['ev_bb'],h['equity'],h['br_ev_bb']]).all() for h in r['hands'][p])


def contexts(partition):
    m=checked(partition);counts,eq=study.pilot.matrices();cases=[]
    for case in m['cases']:
        rows=[]
        for j in m['jobs']:
            if j['case']!=case['id']:continue
            r=study.read(OUT/partition/'jobs'/f"{j['id']}.json")
            validate_reference(r,j,m)
            rows.append(r)
        assert len(rows)==len(m['boards'])
        c=study.pilot.context(case,counts,eq)
        residual,observed,unadjusted=study.pilot.aggregate(case,rows)
        c.update(case=case,residual=residual,observed=observed,unadjusted=unadjusted,rows=rows,
            base_x=c['x'].copy(),base_names=list(c['names']))
        cases.append(c)
    return cases


def run_partition(partition):
    m=checked(partition)
    if partition=='evaluation':
        frozen=study.read(OUT/'candidate-freeze.json')
        assert frozen['sha256']==study.pilot.sha(OUT/'candidate.json') and frozen['evaluation_manifest_id']==m['id']
    env=dict(os.environ);env['PATH']=str(study.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    directory=OUT/partition
    while True:
        done=[]
        for j in m['jobs']:
            path=directory/'jobs'/f"{j['id']}.json"
            if not path.exists():continue
            r=study.read(path)
            validate_reference(r,j,m)
            done.append(j['id'])
        state=dict(stage=partition,completed=len(done),total=len(m['jobs']),controller_pid=os.getpid(),updated=study.night.now())
        study.night.dump(OUT/'status.json',state)
        if len(done)==len(m['jobs']):return
        if dt.datetime.now(dt.timezone.utc)>=DEADLINE:
            study.night.dump(OUT/'status.json',dict(state,stage='deadline_checkpoint'))
            raise SystemExit(4)
        if study.night.live_busy():
            study.night.dump(OUT/'status.json',dict(state,stage='live_app_deferred'))
            raise SystemExit(3)
        assert not other_research(),'Another controller or GPU research process is alive; do not overlap it'
        with (directory/f'batch-{len(done):04d}.log').open('a') as log:
            child=subprocess.Popen([str(study.ROOT/m['binary_path']),str(directory/'manifest.json'),'4'],cwd=study.ROOT,
                env=env,stdout=log,stderr=subprocess.STDOUT)
            study.night.dump(OUT/'status.json',dict(state,active_child_pid=child.pid))
            code=child.wait()
            if code:raise RuntimeError(f'Reference child {child.pid} failed with exit {code}; inspect batch log')
        print(partition,min(len(done)+4,len(m['jobs'])),'/',len(m['jobs']),flush=True)


def train():
    if (OUT/'training-screen.json').exists():
        result=study.read(OUT/'training-screen.json')
        if result['eligible']:assert study.pilot.sha(OUT/'candidate.json')==study.read(OUT/'candidate-freeze.json')['sha256']
        return result['eligible']
    assert not list((OUT/'evaluation/jobs').glob('*.json')),'Evaluation predates candidate freeze'
    original=study.fit.load_cases('train');development=study.contexts('development');extra=contexts('training')
    cases=original+development+extra;assert len(cases)==62
    families=sorted({c['case']['family'] for c in cases});assert len(families)==4
    assert all(c['case']['partition']=='train' for c in cases)
    control=study.read(study.ROOT/'research/preflop-evolution/continuation/night-shift-20260916/curvature-pilot-selection.json')
    control=next(r for r in control['scores'] if r['kind']=='shape' and r['alpha']==.1)
    rows=[];newrows=[]
    for family in families:
        model=study.fit.fit([c for c in cases if c['case']['family']!=family],'shape',.1)
        for source,destination in [(original,rows),(development+extra,newrows)]:
            for c in source:
                if c['case']['family']==family:
                    destination.append(dict(case=c['case']['id'],family=family,**study.pilot.metrics(c,study.fit.predict(c,model))))
    means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
    improvement=1-float(np.mean(list(means.values())))/control['mean']
    worst=max(means[f]/control['family_means'][f] for f in families)
    eligible=improvement>=.05 and worst<=1.05
    result=dict(eligible=eligible,improvement=improvement,worst_family_ratio=worst,family_means=means,
        original_validation_cases=rows,new_validation_cases=newrows,production_enabled=False,
        note='Training-family CV eligibility on unchanged original validation cases, not prospective accuracy evidence.')
    if eligible:
        model=study.fit.fit(cases,'shape',.1)
        model.update(schema=2,production_enabled=False,training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            manifest_id=checked('training')['id'],label='Fixed shape/0.1 predictor with training range bridges; no test labels used.')
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),
            evaluation_manifest_id=checked('evaluation')['id'],evaluation_completed_jobs=0))
    study.freeze(OUT/'training-screen.json',result)
    print('Training eligibility:',eligible,'improvement',improvement,'worst-family ratio',worst,flush=True)
    return eligible


def evaluate():
    model=study.read(OUT/'candidate.json');old=study.read(study.night.OUT/'candidate.json')
    assert study.pilot.sha(OUT/'candidate.json')==study.read(OUT/'candidate-freeze.json')['sha256']
    cases=contexts('evaluation');results=[];boots=[]
    for c in cases:
        pred=study.fit.predict(c,model);previous=study.fit.predict(c,old)
        errors=study.pilot.metrics(c,pred);errors['previous']=study.pilot.metrics(c,previous)['candidate']
        boot=study.fit.bootstrap(c,pred);boot['previous']=study.fit.bootstrap(c,previous)['candidate'];boots.append(boot)
        quality=study.fit.quality(c)
        results.append(dict(case=c['case']['id'],family=c['case']['family'],mae_pct_pot=errors,
            regression_vs_previous=errors['candidate']/errors['previous']-1,
            paired_90_improvement_ci={n:np.quantile(1-boot['candidate']/boot[n],[.05,.95]).tolist() for n in ['balanced','previous']},
            max_reference_gap_pct=max(r['gap_pct'] for r in c['rows']),max_gpu_gap_pct=max(r['gpu_gap_pct'] for r in c['rows']),
            mean_br_gain_pct_pot=float((quality*c['mass']).sum()/2),
            max_probe_br_gain_pct_pot=float(quality[:,[study.pilot.INDEX[h] for h in study.night.PROBES]].max()),
            max_reference_accounting_error_bb=max(abs(sum(r['means_bb'])-c['case']['pot']) for r in c['rows']),
            candidate_pot_sum=float((pred*c['mass']).sum())))
    families=[]
    for family in sorted({c['family'] for c in results}):
        ids=[i for i,c in enumerate(results) if c['family']==family]
        errors={n:float(np.mean([results[i]['mae_pct_pot'][n] for i in ids])) for n in ['candidate','balanced','previous','raw']}
        bootstrap={n:np.mean([boots[i][n] for i in ids],axis=0) for n in errors}
        families.append(dict(family=family,mae_pct_pot=errors,improvement_vs_balanced=1-errors['candidate']/errors['balanced'],
            paired_90_improvement_ci={n:np.quantile(1-bootstrap['candidate']/bootstrap[n],[.05,.95]).tolist() for n in ['balanced','previous']}))
    passed=all(f['improvement_vs_balanced']>=.15 for f in families) and all(r['regression_vs_previous']<=.1 for r in results)
    result=dict(accuracy_screen_passed=passed,cases=results,families=families,production_enabled=False,
        candidate_sha256=study.pilot.sha(OUT/'candidate.json'),
        caveat='Fresh-board evaluation on historically used case identities from source families excluded from all fitting. Intervals condition on the fitted model, not training/source-family uncertainty.')
    study.night.dump(OUT/'evaluation.json',result)
    return result


def run():
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
        msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            run_partition('training')
            if not train():
                study.night.dump(OUT/'status.json',dict(stage='rejected_training_screen',updated=study.night.now(),production_enabled=False))
                return
            run_partition('evaluation');result=evaluate()
            study.night.dump(OUT/'status.json',dict(stage='complete',accuracy_screen_passed=result['accuracy_screen_passed'],updated=study.night.now(),production_enabled=False))
        except Exception as error:
            study.night.dump(OUT/'status.json',dict(stage='failed',error=str(error),updated=study.night.now()))
            raise
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':{'run':run,'train':train,'evaluate':evaluate}[sys.argv[1]]()
