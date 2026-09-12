"""Current policy evaluated as a one-action deviation against average continuation."""
from check_joint import *


def verify():
    cases=[]
    for source in ('six-native-a','six-s64-a'):
        for mode in ('control','candidate'):
            n=f'fixed-unit-screen-{source}-{mode}-v1';p=read(n+'-diagnostics-exit.json')
            require(p['returncode']==0 and p['reason'] is None,'Incomplete diagnostics')
            audit=read(n+'-audit.json');diag=read(n+'-diagnostics.json');rows=[]
            require(len(audit['rows'])==len(diag['nodes'])==6,'Missing paths')
            for row,node in zip(audit['rows'],diag['nodes']):
                c=row['candidate'];require(node['path']==c['path'] and node['iteration']==600,'Wrong diagnostic state')
                worst=0.;fallbacks=0
                require(len(c['hands'])==len(node['hands'])==169,'Incomplete hands')
                for h,d in zip(c['hands'],node['hands']):
                    require(h['class_index']==d['class_index'],'Wrong hand identity')
                    require(h['candidate_probabilities']==d['average_probabilities'],'Different average policy')
                    probs=d['current_probabilities'];q=h['action_values_bb']
                    require(len(probs)==len(q) and all(math.isfinite(v) and 0<=v<=1 for v in probs) and abs(sum(probs)-1)<1e-5,'Invalid current policy')
                    if h['conditional_hand_mass']>=.0025:
                        worst=max(worst,sum(v for value,v in zip(q,probs) if max(q)-value>.1));fallbacks+=d['current_uniform_fallback']
                rows.append(dict(path=c['path'],average_worst_bad_mass=c['worst_relevant_probability_on_strongly_inferior_actions'],
                    current_one_action_bad_mass_vs_average_continuation=worst,relevant_current_uniform_fallbacks=fallbacks,
                    current_counterfactual_mass=node['current_counterfactual_prefix_mass'],average_counterfactual_mass=node['average_counterfactual_prefix_mass']))
            cases.append(dict(source=source,mode=mode,rows=rows))
    return dict(evidence_verified=True,cases=cases,scope='Not a full current-policy equilibrium audit; one-action deviations use saved average continuation values')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
