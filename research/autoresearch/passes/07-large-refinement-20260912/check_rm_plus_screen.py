"""Recompute every hand gate and check independent saved histories."""
from check_joint import *
from check_root_repair import checked_local
from check_average_opponent_screen import archive
from run07 import LAB, digest
from run_rm_plus_screen import CASES, case_name


def verify():
    paths = json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    cases = []; build_identity = None
    for samples, seed, plus in CASES:
        name = case_name(samples,seed,plus)
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
                and r['rm_plus'] is plus and r['normalized'] is (not plus)
                and r['pair'] is (samples==64)
                and r['schedule']==('rm_plus_linear' if plus else 'gamma15')
                and r['horizon']==1000 and r['limit']==3000,'Wrong configuration')
        require((0<r['pair_extra_bytes']<=1024**3) if samples==64 else r['pair_extra_bytes']==0,
                'Wrong extra allocation')
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
        if not plus:
            prior_name=f'normalized-pair-tail-seed{seed}-v1'; prior=archive(prior_name)
            require(r['iteration']==prior['iteration'] and len(r['checks'])==len(prior['checks']),
                    'Disabled trajectory length differs')
            for new,old in zip(r['checks'],prior['checks']):
                for key in ('iteration','gaps','evs','gap','rows','passed','consecutive_combined_passes'):
                    require(new[key]==old[key],'Disabled trajectory changed: '+key)
            require(digest(LAB/'target/convergence'/name/'final.gtop')
                    ==digest(LAB/'target/convergence'/prior_name/'final.gtop'),'Disabled saved history differs')
        require(math.isfinite(r['seconds']) and r['seconds']>0,'Invalid time')
        cases.append(dict(samples=samples,seed=seed,rm_plus=plus,seconds=r['seconds'],
            iteration=r['iteration'],qualified=r['qualified'],checks=checks,
            independent_saved_audit_exact=True,disabled_replay_exact=not plus))
    full=next(c for c in cases if c['samples']==1024)
    sampled=True
    for c in (c for c in cases if c['rm_plus'] and c['samples']==64):
        control=next(b for b in cases if not b['rm_plus'] and b['seed']==c['seed'])
        require(control['qualified'],'Control failed')
        c['complete_time_ratio']=c['seconds']/control['seconds']
        c['passes_screen']=c['qualified'] and c['complete_time_ratio']<=2
        sampled &= c['passes_screen']
    return dict(evidence_verified=True,cases=cases,full_particle_large_admitted=full['qualified'],
                sampled_large_admitted=sampled,large_game_qualified=False,
                scope='Small algorithm/sampling screen only; large quality and speed remain unproven')


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
