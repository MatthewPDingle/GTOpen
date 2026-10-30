"""Read-only full-action river values with a single identified current policy."""
import hashlib
import itertools
import json
import math
from functools import lru_cache


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


@lru_cache(maxsize=100_000)
def canonical(cards):
    variants=[]
    for perm in itertools.permutations(range(4)):
        c=[63 if x==63 else x//4*4+perm[x%4] for x in cards]
        c[:2]=sorted(c[:2]);c[2:5]=sorted(c[2:5]);variants.append(tuple(c))
    return min(variants,key=lambda c:sum(x<<(6*i) for i,x in enumerate(c)))


def observation(o):
    hi,lo=int(o['hi']),int(o['lo']);assert 0<hi<2**64 and 0<=lo<2**43
    actor=(lo>>42)&1;cards=tuple((lo>>(6*i))&63 for i in range(7))
    assert all(c<52 or c==63 for c in cards) and len({c for c in cards if c<52})==sum(c<52 for c in cards)
    assert cards[:2]==tuple(sorted(cards[:2])) and all(c<52 for c in cards[:2])
    if hi>>63==0:
        assert hi<=16
        phase=0;branch=hi-1;history=[]
    else:
        branch=hi&15;h=(hi&((1<<63)-1))>>4;history=[]
        while h>1:history.append(h&7);h>>=3
        assert h==1;history=history[::-1]
        phase=1 if cards[5]==63 else 2 if cards[6]==63 else 3
        assert history.count(5)==phase-1
    assert len(history)<=19 and all(1<=x<=5 for x in history)
    count=(2,5,6,7)[phase];assert all(c<52 for c in cards[:count]) and all(c==63 for c in cards[count:])
    assert cards==canonical(cards) and actor==o['actor'] and phase==o['phase'] and o['n'] in (2,3,4)
    active=[]
    for i,c in enumerate(cards):active.extend([19*i+(13 if c==63 else c//4),19*i+14+(4 if c==63 else c%4)])
    active.extend([133+actor,135+phase,139+branch]);active.extend(155+6*i+(history[i] if i<len(history) else 0) for i in range(19))
    assert active==o['active_features']
    return cards,actor,phase,branch,history


def validate_document(doc,context_source):
    assert doc['format']==1 and doc['context_source']==context_source
    queries=doc['queries'];assert queries['format']==2 and queries['context_source']==context_source
    assert queries['batch_source']==doc['request_source']
    rows=queries['observations'];assert 0<len(rows)<=250_000
    assert len({(o['hi'],o['lo']) for o in rows})==len(rows)
    decoded=[observation(o) for o in rows];target=doc['target'];hero=target['actor'];cards=target['cards']
    assert target['phase']==3 and len(cards)==7 and len(set(cards))==7
    target_index=target['query_index'];assert decoded[target_index][0]==tuple(cards)
    assert decoded[target_index][3]==target['branch']
    assert all(rows[target_index][k]==target[k] for k in ('hi','lo','actor','phase','n'))
    context=json.loads(context_source);geometry=doc['geometry'];leaf=context['nodes'][target['branch']]['leaf']
    for k,expected in [('rake_fraction',context['rake_fraction']),('rake_cap',context['rake_cap']),
                       ('branch_offset',leaf['value_offsets'][hero]),('starting_pot',leaf['starting_pot']),
                       ('effective_stack',leaf['effective_stack'])]:assert geometry[k]==expected
    for i,o in enumerate(rows):
        seen=set()
        for depth,(prior,a,n) in enumerate(o['own_history']):
            assert 0<=prior<len(rows) and prior!=i and prior not in seen
            assert rows[prior]['actor']==o['actor'] and rows[prior]['n']==n and 0<=a<n
            assert rows[prior]['own_history']==o['own_history'][:depth];seen.add(prior)
    pairs=doc['pairs'];assert len(pairs)==990
    expected=list(itertools.combinations([c for c in range(52) if c not in cards],2))
    assert [tuple(x['cards']) for x in pairs]==expected
    nodes=doc['nodes'];assert 0<len(nodes)<=500_000 and len(nodes)==990*geometry['nodes_per_pair']
    max_error=0.;fold_refunds=ties=allins=0;action_types=set();base_signature=None
    for pi,pair in enumerate(pairs):
        start=pi*geometry['nodes_per_pair'];stop=start+geometry['nodes_per_pair'];assert pair['node_start']==start and pair['root']==stop-1
        outcome=pair['outcome_loss_tie_win'];assert outcome in (0,1,2)
        private=[None,None];private[hero]=cards[:2];private[1-hero]=pair['cards']
        def check_query(index,path):
            o=rows[index];visible,actor,phase,_,_=decoded[index]
            count=(0,3,4,5)[phase]
            want=tuple(private[actor]+cards[2:2+count]+[63]*(5-count))
            assert canonical(want)==visible,'Hidden-card leakage or incorrect visible geometry'
            assert o['own_history']==[link for link in path if rows[link[0]]['actor']==actor]
        path=[]
        for link in pair['path']:
            index,a,n=link;assert 0<=index<len(rows) and rows[index]['n']==n and 0<=a<n
            check_query(index,path);path.append(link)
        assert nodes[pair['root']]['query_index']==target_index
        seen=set();signature=[]
        def visit(index,history):
            nonlocal max_error,fold_refunds,ties,allins
            assert start<=index<stop and index not in seen;seen.add(index)
            node=nodes[index];put=node['put'];assert len(put)==2 and all(math.isfinite(v) and v>=0 for v in put)
            if node['kind']=='decision':
                i=node['query_index'];o=rows[i];assert node['actor']==o['actor'] and len(node['children'])==o['n']==len(node['actions'])
                assert decoded[i][2:4]==(3,target['branch'])
                check_query(i,history)
                signature.append((index-start,node['actor'],put,node['actions'],[x-start for x in node['children']]))
                for a,(child,edge) in enumerate(zip(node['children'],node['actions'])):
                    assert start<=child<index;who=node['actor'];paid=edge['paid'];after=nodes[child]['put']
                    assert paid>=-1e-10 and abs(after[who]-put[who]-paid)<1e-9 and after[1-who]==put[1-who]
                    kind=edge['kind'];action_types.add(kind)
                    if kind in ('fold','check'):assert paid==0 and edge['to'] is None and not edge['all_in']
                    elif kind=='call':assert abs(paid-(put[1-who]-put[who]))<1e-9
                    elif kind=='bet':assert abs(put[0]-put[1])<1e-9 and paid>0
                    elif kind=='raise':assert after[who]>put[1-who]
                    else:raise AssertionError('Unknown legal action')
                    expected_allin=kind in ('call','bet','raise') and abs(after[who]-(geometry['starting_pot']/2+geometry['effective_stack']))<1e-8
                    assert edge['all_in']==expected_allin;allins+=int(expected_allin)
                    if nodes[child]['kind']=='decision':
                        next_query=nodes[child]['query_index']
                        assert decoded[next_query][4]==decoded[i][4]+[a+1]
                    visit(child,history+[[i,a,o['n']]])
            else:
                assert node['kind'] in ('fold','showdown')
                if node['kind']=='fold':
                    folded=node['folded'];assert folded in (0,1);amount=put[folded];assert amount<=put[1-folded]+1e-9
                    fold_refunds+=int(put[1-folded]>amount+1e-9)
                else:
                    assert node['folded'] is None and abs(put[0]-put[1])<1e-9;amount=put[0];ties+=int(outcome==1)
                rake=2*amount*geometry['rake_fraction']
                if geometry['rake_cap']>0:rake=min(rake,geometry['rake_cap'])
                if node['kind']=='fold':value=-amount if folded==hero else amount-rake
                else:value=(-amount,-rake/2,amount-rake)[outcome]
                error=abs(value+geometry['branch_offset']-node['payoff']);assert error<1e-9;max_error=max(max_error,error)
        visit(pair['root'],path);assert len(seen)==stop-start
        if base_signature is None:base_signature=signature
        else:assert signature==base_signature,'Private cards changed legal/public tree'
    assert sum(doc['counts_loss_tie_win'])==990
    assert [sum(p['outcome_loss_tie_win']==x for p in pairs) for x in range(3)]==doc['counts_loss_tie_win']
    return dict(pairs=990,observations=len(rows),nodes=len(nodes),maximum_terminal_error=max_error,
                tie_terminals=ties,uncalled_bet_refunds=fold_refunds,all_in_edges=allins,action_types=sorted(action_types))


def probabilities(doc,bundle,*,expected_policy_id,expected_context_source):
    if doc['context_source']!=expected_context_source or bundle['context_source']!=expected_context_source:raise ValueError('Context mismatch')
    if bundle['policy_id']!=expected_policy_id:raise ValueError('Current policy identity mismatch')
    if bundle['query_sha256']!=digest(doc['queries']):raise ValueError('Query identity mismatch')
    p=bundle['probabilities']
    if bundle['probabilities_sha256']!=digest(p):raise ValueError('Changed policy probabilities')
    rows=doc['queries']['observations']
    if len(p)!=len(rows):raise ValueError('Policy row count mismatch')
    for row,o in zip(p,rows):
        if len(row)!=4 or any(not math.isfinite(v) or v<0 for v in row) or any(row[o['n']:]) or abs(math.fsum(row)-1)>1e-12:
            raise ValueError('Invalid legal action probabilities')
    return p


def evaluate(doc,bundle,entry,*,expected_policy_id,expected_context_source):
    p=probabilities(doc,bundle,expected_policy_id=expected_policy_id,expected_context_source=expected_context_source)
    nodes=doc['nodes'];rows=doc['queries']['observations'];target=doc['target'];hero=target['actor'];n=target['n']
    all_pairs=set(itertools.combinations(range(52),2))
    assert len(entry)==2 and all(set(e)==all_pairs and all(math.isfinite(v) and v>=0 for v in e.values()) for e in entry)
    values=[]
    for i,node in enumerate(nodes):
        if node['kind']!='decision':values.append(node['payoff'])
        else:
            assert all(0<=child<i for child in node['children'])
            values.append(math.fsum(p[node['query_index']][a]*values[child] for a,child in enumerate(node['children'])))
    pair_values=[];weights=[];own=[];maximum=0.
    # Independently sum all root-action terminal paths, rather than bottom-up values.
    def terminal_paths(index,reach):
        node=nodes[index]
        if node['kind']!='decision':return [reach*node['payoff']]
        terms=[]
        for a,child in enumerate(node['children']):terms.extend(terminal_paths(child,reach*p[node['query_index']][a]))
        return terms
    for pair in doc['pairs']:
        root=nodes[pair['root']];action=[values[child] for child in root['children']]
        for a,child in enumerate(root['children']):
            error=abs(action[a]-math.fsum(terminal_paths(child,1.)));assert error<1e-9;maximum=max(maximum,error)
        pair_values.append(action)
        mass=entry[1-hero][tuple(pair['cards'])];my_reach=1.
        for index,a,_ in pair['path']:
            if rows[index]['actor']==hero:my_reach*=p[index][a]
            else:mass*=p[index][a]
        assert math.isfinite(mass) and mass>=0;weights.append(mass);own.append(my_reach)
    assert max(own)-min(own)<1e-12
    mass=math.fsum(weights);result=dict(supported=mass>0,opponent_mass=mass,own_history_likelihood=own[0],
        maximum_path_value_error=maximum,pair_action_values=pair_values,policy_id=expected_policy_id)
    if mass>0:
        posterior=[w/mass for w in weights];assert abs(math.fsum(posterior)-1)<1e-12
        action=[math.fsum(w*v[a] for w,v in zip(posterior,pair_values)) for a in range(n)]
        value=math.fsum(x*y for x,y in zip(p[target['query_index']][:n],action));regrets=[x-value for x in action]
        assert abs(math.fsum(x*y for x,y in zip(p[target['query_index']][:n],regrets)))<1e-9
        result.update(action_values=action,value=value,regrets=regrets,posterior=posterior)
    return result
