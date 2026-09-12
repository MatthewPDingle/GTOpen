"""Independently recompute all registered fixed-unit screen gates."""
from check_root_repair import checked_local,f32
from check_joint import *


def verify():
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text());results=[]
    for source in ('six-native-a','six-s64-a'):
        for mode in ('control','candidate'):
            name=f'fixed-unit-screen-{source}-{mode}-v1';r=read(name+'-result.json');process=read(name+'-exit.json')
            audit=read(name+'-audit.json');ap=read(name+'-audit-exit.json')
            for p in (process,ap):require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
            require(r['mode']==mode and r['roundtrip_exact'] is True and r['persistent_resume_supported'] is False,'Wrong mode or persistence claim')
            initial=checked_local(r['initial']['rows'],paths);checks=[];streak=0
            require(1<=len(r['checks'])<=11,'Wrong check count')
            for i,c in enumerate(r['checks']):
                require(c['global_age']==350+25*i,'Wrong retained global age')
                g=c['global_gaps'];require(len(g)==6 and all(math.isfinite(v) and v>=0 for v in g),'Invalid global gaps')
                total=sum(g);require(abs(total-c['gap_total'])<1e-12,'Wrong total gap')
                count=checked_local(c['rows'],paths);passes=total<=.005 and count==6
                require(c['passed']==count and c['passes_combined'] is passes,'Incorrect combined gate')
                streak=streak+1 if passes else 0
                require(streak<2 or i==len(r['checks'])-1,'Did not stop at registered success')
                checks.append(dict(age=c['global_age'],gap=total,passed=count,qualifies_twice=streak>=2))
            qualified=streak>=2;require(r['qualified'] is qualified,'Wrong final qualification')
            require(qualified or len(checks)==11,'Early stop without qualification')
            require(checked_local(audit['rows'],paths)==checks[-1]['passed'],'Saved audit gate differs')
            require([x['candidate'] for x in audit['rows']]==[x['candidate'] for x in r['checks'][-1]['rows']],'Saved audit values differ')
            if mode=='candidate':
                m=r['metadata'];start=r['refinement']['metadata']
                require(m['valid'] and m['origin_global_age']==350 and m['current_global_age']==checks[-1]['age'],'Wrong metadata age')
                require(m['unit_checksum']==start['unit_checksum'] and m['branches']==start['branches'],'Units or reference contexts changed')
                require(m['ordinary_resume_supported'] is False and m['persistent_resume_supported'] is False,'Unsupported resume claim')
                require(m['unit_bytes']==23038*8,'Wrong unit memory')
                require([b['path'] for b in m['branches']]==[[2,0,0],[1,0,0]],'Wrong disjoint roots')
                ownership=set()
                for b in m['branches']:
                    require(b['local_age']==1000 and b['global_age_at_refinement']==350,'Wrong local schedule')
                    masses=b['reference_masses_f32'];require(len(masses)==6,'Wrong mass coverage')
                    require(masses==[f32(v) for v in b['reference_masses_f64']],'Wrong stored mass conversion')
                    factors=[]
                    for actor in range(6):
                        value=1.
                        for q,mass in enumerate(masses):
                            if q!=actor:value=f32(value*mass)
                        factors.append(value)
                    require(factors==b['regret_factors_f32'],'Wrong regret factors')
                    for node in b['learning_nodes']:
                        require(0<=node<23038 and node not in ownership,'Invalid or overlapping ownership');ownership.add(node)
                require(ownership,'Empty learning ownership')
            else:require(r['metadata'] is None and r['refinement'] is None,'Control changed histories through refinement')
            results.append(dict(source=source,mode=mode,seconds=r['seconds'],process_seconds=process['seconds'],initial_passes=initial,checks=checks,qualified=qualified))
    candidates=[r for r in results if r['mode']=='candidate']
    return dict(evidence_verified=True,large_trial_admitted=all(r['qualified'] for r in candidates),results=results,
                scope='Small six-path feasibility screen; large all-27 accuracy remains unqualified')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
