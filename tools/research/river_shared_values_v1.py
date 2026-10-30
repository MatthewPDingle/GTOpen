"""Share policy/entry validation across unchanged complete native river trees."""
import itertools
import math
from river_full_action_math_v1 import probabilities


def evaluate_many(batch,bundle,entry,*,expected_policy_id,expected_context_source):
    if batch['format']!=2 or not batch['targets']:raise ValueError('Explicit nonempty native batch required')
    p=probabilities(batch,bundle,expected_policy_id=expected_policy_id,expected_context_source=expected_context_source)
    all_pairs=set(itertools.combinations(range(52),2))
    if len(entry)!=2 or any(set(e)!=all_pairs or any(not math.isfinite(v) or v<0 for v in e.values()) for e in entry):raise ValueError('Invalid entry ranges')
    rows=batch['queries']['observations'];result=[];seen=set()
    for doc in batch['targets']:
        target=doc['target'];key=(target['hi'],target['lo'])
        if key in seen:raise ValueError('Duplicate target')
        seen.add(key);hero=target['actor'];n=target['n'];ti=target['query_index']
        if any(rows[ti][k]!=target[k] for k in ('hi','lo','actor','phase','n')):raise ValueError('Wrong target identity')
        nodes=doc['nodes'];values=[]
        for i,node in enumerate(nodes):
            if node['kind']!='decision':values.append(node['payoff'])
            else:
                assert all(0<=c<i for c in node['children'])
                values.append(math.fsum(p[node['query_index']][a]*values[c] for a,c in enumerate(node['children'])))
        weights=[];own=[];actions=[]
        for pair in doc['pairs']:
            root=nodes[pair['root']];assert root['query_index']==ti
            actions.append([values[c] for c in root['children']]);mass=entry[1-hero][tuple(pair['cards'])];my_reach=1.
            for i,a,arity in pair['path']:
                assert rows[i]['n']==arity and 0<=a<arity
                if rows[i]['actor']==hero:my_reach*=p[i][a]
                else:mass*=p[i][a]
            assert math.isfinite(mass) and mass>=0;weights.append(mass);own.append(my_reach)
        assert len(actions)==990 and max(own)-min(own)<1e-12
        total=math.fsum(weights);value=dict(supported=total>0,opponent_mass=total,own_history_likelihood=own[0],pair_action_values=actions,policy_id=expected_policy_id)
        if total>0:
            posterior=[w/total for w in weights];q=[math.fsum(w*v[a] for w,v in zip(posterior,actions)) for a in range(n)]
            mean=math.fsum(x*y for x,y in zip(p[ti][:n],q));regrets=[x-mean for x in q]
            assert abs(math.fsum(x*y for x,y in zip(p[ti][:n],regrets)))<1e-8
            value.update(posterior=posterior,action_values=q,value=mean,regrets=regrets)
        result.append(value)
    return result
