"""Independent scalar readback for fixed-count wider-root evaluation artifacts.

Replays both chance streams and reconciles native payoff files, fitted choices,
half-sample stability, physical residual bounds and all final intervals. Does
not rerun neural inference or native poker traversal; controllers must admit
those separately and verify frozen input identities before and after this call.
"""
import json
import math
from pathlib import Path
from sampled_physical_root_evaluation_v1 import sha,hand_class
from sampled_player_stratified_response_deals_v2 import sample
from sampled_physical_deals_v1 import PhysicalDeals

SERIES=('trained-response','always-fold','always-call','always-raise','always-jam')


def read(path):
    return json.loads(Path(path).read_text())


def review(context_path,folder,config,exact,cache_sha256,guard):
    guard();folder=Path(folder);context_path=Path(context_path)
    source=context_path.read_text();context=json.loads(source)
    assert sha(context_path)==exact['context_sha256']
    pc,nt,bs,minimum=[config[k] for k in ('per_class','test_deals','batch_size','minimum_training_deals')]
    assert all(type(x) is int and x>0 for x in (pc,nt,bs,minimum))
    assert pc%2==0 and nt>=2 and nt%bs==0 and config['train_seed']!=config['test_seed']
    assert 0<config['family_alpha']<1
    base,mass,fold,jam=[exact[k] for k in ('baseline','masses','fold_entries','jam_entries')]
    assert all(len(x)==169 for x in (base,mass,fold,jam))
    assert all(math.isfinite(x) and x>0 for x in mass) and abs(math.fsum(mass)-1)<1e-12
    assert all(len(row)==4 and all(math.isfinite(x) and x>=0 for x in row) and abs(math.fsum(row)-1)<1e-12 for row in base)
    assert all(math.isfinite(x) for row in (fold,jam) for x in row)
    result=read(folder/'result.json');response=read(folder/'response.json')
    prepared=read(folder/'residual-preparation.json');test_start=read(folder/'test-start.json')
    assert result['complete'] and result['population_test_only'] and not result['best_response_upper_bound']
    assert result['production_modified'] is False and result['training_deals']==169*pc and result['test_deals']==nt
    assert response['format']==1 and response['method']=='exact-aware-root-response-v1'
    assert response['context_sha256']==exact['context_sha256'] and response['baseline']==base
    assert response['class_population_masses']==mass and response['minimum_training_deals']==minimum
    assert all(len(response[k])==169 for k in ('probabilities','training_counts','selected_actions','class_action_means'))
    assert all(len(row)==4 for row in response['class_action_means'])
    rh,ph=sha(folder/'response.json'),sha(folder/'residual-preparation.json')
    assert rh==result['response_sha256']==test_start['response_sha256']
    assert ph==result['preparation_sha256']==test_start['preparation_sha256']
    assert test_start['response_frozen_before_test'] is True
    # File order is supporting evidence; code review and replay establish the
    # actual sampler separation. Timestamps alone do not prove independence.
    assert max((folder/n).stat().st_mtime_ns for n in ('response.json','residual-preparation.json')) <= (folder/'test-start.json').stat().st_mtime_ns
    sampled=sample(source,player=0,seed=config['train_seed'],per_class=pc,classes=list(range(169)),guard=guard)
    assert read(folder/'training-deals.json')==sampled
    test=PhysicalDeals(source,mode='full_deck',seed=config['test_seed'])
    assert test.checkpoint()==test_start['initial_rng']
    lo=-context['config']['stack'];hi=context['config']['stack']+context['dead_money']
    data={};ids={};maximum=0.;expected_names=[];stored={name:[] for name in SERIES}
    def close(a,b):
        nonlocal maximum
        assert math.isfinite(a) and math.isfinite(b)
        error=abs(a-b);maximum=max(maximum,error);assert error<1e-9,(a,b)
    for phase,n in (('train',169*pc),('test',nt)):
        cs=[];qs=[];names=[]
        for at in range(0,n,bs):
            guard();name=f'{phase}-{at:06d}';expected_names.append(name);part=folder/name
            s=read(part/'summary.json');assert sha(part/'summary.json')==result['batch_summary_hashes'][name]
            assert set(s['artifacts'])=={'query-batch.json','conditional-batch.json','queries.json','profiles.json','native.json'}
            for filename,h in s['artifacts'].items():guard();assert sha(part/filename)==h
            wanted=sampled['deals'][at:at+bs] if phase=='train' else test.sample(bs)['deals']
            batch=read(part/'query-batch.json')
            assert batch['format']==2 and batch['deals']==wanted and batch['batch_id']==f"{config['id']}-{name}"
            assert not any(k.startswith('allin_') or k=='terminal_estimator' for k in batch)
            queries=read(part/'queries.json')
            assert queries['context_source']==source and json.loads(queries['batch_source'])==batch
            native=read(part/'native.json');assert native['format']==2 and native['terminal_estimator']=='conditional-preflop-allin-v1'
            assert native['postflop_outcomes']=='sampled-board'
            profiles=native['profiles'];assert [p['name'] for p in profiles]==['baseline','action-0','action-1','action-2','action-3']
            assert all(len(p['deals'])==len(wanted) for p in profiles)
            assert s['format']==2 and s['terminal_estimator']==native['terminal_estimator'] and s['allin_cache_sha256']==cache_sha256
            assert s['policy_input']=='unlabelled visible queries' and s['postflop_outcomes']=='sampled-board'
            assert s['classes']==[hand_class(d[:2]) for d in wanted]
            assert all(len(s[k])==len(wanted) for k in ('action_values','baseline_values','root_probabilities'))
            for i,c in enumerate(s['classes']):
                q=s['action_values'][i];assert len(q)==4 and all(math.isfinite(x) and lo-1e-9<=x<=hi+1e-9 for x in q)
                assert len(s['root_probabilities'][i])==4
                for a in range(4):close(q[a],profiles[a+1]['deals'][i]['values'][0]);close(s['root_probabilities'][i][a],base[c][a])
                close(s['baseline_values'][i],profiles[0]['deals'][i]['values'][0])
                close(math.fsum(q[a]*base[c][a] for a in range(4)),s['baseline_values'][i])
                close(q[0],-context['nodes'][0]['invested'][0])
            for k in ('maximum_forward_cashflow_error','maximum_conservation_error'):
                close(s[k],native[k]);assert 0<=s[k]<1e-9
            assert 0<=s['maximum_root_mixture_error']<1e-9
            cs.extend(s['classes']);qs.extend(s['action_values'])
            names.extend(f"{config['id']}-{name}-{i}" for i in range(len(wanted)))
            if phase=='test':
                residual=read(part/'residuals.json');assert residual['response_sha256']==rh and residual['preparation_sha256']==ph
                assert set(residual['values'])==set(SERIES)
                for label in SERIES:assert len(residual['values'][label])==len(wanted);stored[label].extend(residual['values'][label])
        data[phase]=(cs,qs);ids[phase]=names
    assert set(result['batch_summary_hashes'])==set(expected_names)
    assert set(prepared)==set(result['intervals'])==set(SERIES)
    assert not set(ids['train'])&set(ids['test']) and ids['train']==response['training_ids']
    assert len(set(ids['train']))==169*pc and len(set(ids['test']))==nt
    def scalar_fit(cs,qs):
        rows=[[] for _ in range(169)]
        for c,q in zip(cs,qs):rows[c].append(q)
        counts=[len(x) for x in rows];means=[];actions=[];rho=[]
        for c,group in enumerate(rows):
            m=[fold[c]/mass[c],math.fsum(q[1] for q in group)/max(1,len(group)),math.fsum(q[2] for q in group)/max(1,len(group)),jam[c]/mass[c]]
            a=max(range(4),key=lambda k:m[k]) if len(group)>=minimum else -1
            means.append(m);actions.append(a);rho.append(base[c] if a==-1 else [float(k==a) for k in range(4)])
        return counts,means,actions,rho
    counts,means,actions,rho=scalar_fit(*data['train'])
    assert counts==[pc]*169==response['training_counts']==result['training_counts']
    assert actions==response['selected_actions'] and rho==response['probabilities']
    for a,b in zip(means,response['class_action_means']):
        for x,y in zip(a,b):close(x,y)
    mid=169*pc//2;halves=[scalar_fit(data['train'][0][s],data['train'][1][s]) for s in (slice(0,mid),slice(mid,None))]
    assert all(h[0]==[pc//2]*169 for h in halves)
    eligible=[c for c in range(169) if pc//2>=minimum];disagree=[c for c in eligible if halves[0][2][c]!=halves[1][2][c]]
    stability=read(folder/'training-stability.json');assert stability==result['stability']
    assert stability['eligible_classes']==len(eligible) and stability['disagreeing_classes']==len(disagree)
    assert stability['half_actions']==[h[2] for h in halves] and stability['diagnostic_only'] and not stability['used_to_select_response']
    close(stability['disagreement_population_mass'],math.fsum(mass[c] for c in disagree))
    test_counts=[0]*169
    for c in data['test'][0]:test_counts[c]+=1
    assert test_counts==result['test_counts'] and test.draws==nt
    for index,name in enumerate(SERIES):
        p=prepared[name];alternative=rho if index==0 else [[float(a==index-1) for a in range(4)] for _ in range(169)]
        delta=[[alternative[c][a]-base[c][a] for a in range(4)] for c in range(169)]
        assert p['delta']==delta and p['centre']==[0.]*169 and p['counts']==counts and p['centred'] is False
        close(p['action_lower'],lo);close(p['action_upper'],hi);close(p['centre_population_offset'],0.)
        offset=math.fsum(delta[c][0]*fold[c]+delta[c][3]*jam[c] for c in range(169))
        lower=min(math.fsum(x*(lo if x>=0 else hi) for x in row[1:3]) for row in delta)-1e-9
        upper=max(math.fsum(x*(hi if x>=0 else lo) for x in row[1:3]) for row in delta)+1e-9
        close(offset,p['total_offset']);close(offset,p['exact_fold_jam_offset']);close(lower,p['residual_lower']);close(upper,p['residual_upper'])
        values=[math.fsum(delta[c][a]*q[a] for a in (1,2)) for c,q in zip(*data['test'])]
        assert len(values)==len(stored[name])==nt and all(lower<=v<=upper for v in values)
        for a,b in zip(values,stored[name]):close(a,b)
        mean=math.fsum(values)/nt;var=math.fsum((x-mean)**2 for x in values)/(nt-1)
        logarithm=math.log(4*5/config['family_alpha']);radius=math.sqrt(2*var*logarithm/nt)+7*(upper-lower)*logarithm/(3*(nt-1))
        expected=dict(mean=mean+offset,lower=max(lower,mean-radius)+offset,upper=min(upper,mean+radius)+offset,
            residual_mean=mean,exact_offset=offset,sample_variance=var,radius=radius)
        interval=result['intervals'][name];assert interval['count']==nt and interval['family_error_probability']==config['family_alpha'] and interval['bounds_best_response_above'] is False
        for k,v in expected.items():close(v,interval[k])
    guard()
    return dict(passed=True,complete_training_deals_replayed=169*pc,complete_population_test_deals_replayed=nt,
        batch_count=len(expected_names),class_response_choices_reconstructed=169,stability_halves_reconstructed=2,
        intervals_reconstructed=5,maximum_scalar_error_bb=maximum,production_modified=False,accuracy_qualified=False,
        limitation='Reconciles stored native payoffs; does not independently rerun native poker traversal or neural inference.')
