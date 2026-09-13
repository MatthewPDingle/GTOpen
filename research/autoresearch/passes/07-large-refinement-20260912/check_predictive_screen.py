"""Recompute every hand gate and check independent saved histories."""
from check_joint import *
from check_root_repair import checked_local
from check_average_opponent_screen import archive
from run07 import LAB, digest
from run_predictive_screen import CASES, case_name


def verify():
    paths = json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    cases = []; build_identity = None
    for samples, seed, mode in CASES:
        name = case_name(samples,seed,mode)
        r = archive(name)
        for suffix in ('-exit.json','-audit-exit.json'):
            p = read(name+suffix)
            require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
        process = read(name+'-exit.json')
        identity = (process['exe_sha256'], process['solver_source_files'],
                    process['source_diff_sha256'], process['inputs'])
        if build_identity is None: build_identity = identity
        else: require(identity == build_identity,'Cases did not use identical executable/source/inputs')
        require(r['nodes']==23038 and r['samples']==samples and r['seed']==seed
                and r['mode']==mode and r['normalized'] is (mode=='control')
                and r['pair'] is (samples==64)
                and r['schedule']==('gamma15' if mode=='control' else 'predictive_rm_plus_quadratic')
                and r['horizon']==1000 and r['limit']==3000,'Wrong configuration')
        require((0<r['pair_extra_bytes']<=1024**3) if samples==64 else r['pair_extra_bytes']==0,
                'Wrong extra allocation')
        storage=r['prediction_storage']
        if mode=='control': require(storage is None,'Control has predictive state')
        else:
            require(storage['fits_four_gib'] is True and storage['cap_bytes']==4*1024**3,
                    'Wrong storage cap')
            require(storage['history_floats']==169*storage['vector_terminals']+storage['scalar_terminals'],
                    'Wrong compressed history count')
            require(storage['history_bytes']==4*storage['history_floats']
                    and storage['offset_bytes']==4*(storage['vector_terminals']+storage['scalar_terminals'])
                    and storage['policy_bytes']==4*169*(23038-1),'Wrong storage sizes')
            require(storage['persistent_extra_bytes']==storage['history_bytes']+storage['offset_bytes']+storage['policy_bytes']
                    and storage['persistent_extra_bytes']<=1024**3,'Wrong allocation')
        require(r['roundtrip_exact'] is True and r['large_game_qualified'] is False,'Preservation/scope')
        require(1<=len(r['checks'])<=120,'Wrong check count')
        streak=0; checks=[]
        for index,c in enumerate(r['checks']):
            require(c['iteration']==25*(index+1) and c['full_reference_samples']==1024
                    and streak<2,'Wrong cadence/late stopping')
            require(len(c['gaps'])==len(c['evs'])==6
                    and all(math.isfinite(v) and v>=0 for v in c['gaps'])
                    and all(math.isfinite(v) for v in c['evs']),'Invalid global evaluation')
            gap=sum(c['gaps']); require(abs(gap-c['gap'])<1e-12,'Wrong gap sum')
            passed=checked_local(c['rows'],paths)
            require(passed==c['passed'],'Wrong local count')
            streak=streak+1 if gap<=.005 and passed==6 else 0
            require(streak==c['consecutive_combined_passes'],'Wrong combined gate')
            checks.append(dict(iteration=c['iteration'],gap=gap,passed=passed,streak=streak))
        require(r['qualified'] is (streak>=2) and r['iteration']==checks[-1]['iteration']
                and (r['qualified'] or r['iteration']==3000),'Wrong stop')
        audit=read(name+'-audit.json')
        require(checked_local(audit['rows'],paths)==checks[-1]['passed'],'Saved count differs')
        require(len(audit['rows'])==len(r['checks'][-1]['rows']),'Saved rows missing')
        for actual,expected in zip(audit['rows'],r['checks'][-1]['rows']):
            require(actual['candidate']==expected['candidate'],'Saved per-hand records differ')
        if mode=='control':
            prior_name=f'normalized-pair-tail-seed{seed}-v1'; prior=archive(prior_name)
            require(r['iteration']==prior['iteration'] and len(r['checks'])==len(prior['checks']),
                    'Disabled trajectory length differs')
            for new,old in zip(r['checks'],prior['checks']):
                for key in ('iteration','gaps','evs','gap','rows','passed','consecutive_combined_passes'):
                    require(new[key]==old[key],'Disabled trajectory changed: '+key)
            require(digest(LAB/'target/convergence'/name/'final.gtop')
                    ==digest(LAB/'target/convergence'/prior_name/'final.gtop'),'Disabled saved history differs')
        require(math.isfinite(r['seconds']) and r['seconds']>0,'Invalid time')
        cases.append(dict(samples=samples,seed=seed,mode=mode,seconds=r['seconds'],
            iteration=r['iteration'],qualified=r['qualified'],checks=checks,
            independent_saved_audit_exact=True,disabled_replay_exact=mode=='control'))
    full=next(c for c in cases if c['samples']==1024 and c['mode']=='predict')
    zero=next(c for c in cases if c['mode']=='zero')
    sampled=True
    for c in (c for c in cases if c['mode']=='predict' and c['samples']==64):
        control=next(b for b in cases if b['mode']=='control' and b['seed']==c['seed'])
        require(control['qualified'],'Control failed')
        c['complete_time_ratio']=c['seconds']/control['seconds']
        c['passes_screen']=c['qualified'] and c['complete_time_ratio']<=2
        sampled &= c['passes_screen']
    full_admitted=full['qualified'] and (not zero['qualified'] or full['seconds']<=zero['seconds'])
    return dict(evidence_verified=True,cases=cases,full_particle_large_admitted=full_admitted,
                sampled_large_admitted=sampled,large_game_qualified=False,
                scope='Small predictive algorithm/sampling screen only; large quality and speed remain unproven')


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
