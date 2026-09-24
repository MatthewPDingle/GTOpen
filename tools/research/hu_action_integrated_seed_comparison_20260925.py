"""Descriptive complete-class comparison of matched old/new training seed pairs."""
import math
from pathlib import Path
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from hu_root_retained_seed_range_comparison_20260924 import load,label,ACTIONS


def compare(a,b):
    classes=[]
    for i,(x,y) in enumerate(zip(a,b)):
        m=x['entry_probability'];assert abs(m-y['entry_probability'])<1e-12
        first,second=x['baseline'],y['baseline']
        assert len(first)==len(second)==4 and min(first+second)>=0
        assert abs(sum(first)-1)<1e-12 and abs(sum(second)-1)<1e-12
        delta=[v-u for u,v in zip(first,second)]
        classes.append(dict(hand_class=i,hand=label(i),entry_mass=m,
            first=first,second=second,change=delta,total_variation=.5*sum(map(abs,delta))))
    assert len(classes)==169 and abs(math.fsum(c['entry_mass'] for c in classes)-1)<1e-12
    mixes={key:dict(zip(ACTIONS,[math.fsum(c['entry_mass']*c[key][i] for c in classes)
        for i in range(4)])) for key in ('first','second','change')}
    tv=math.fsum(c['entry_mass']*c['total_variation'] for c in classes)
    assert .5*sum(map(abs,mixes['change'].values()))<=tv+1e-12
    return dict(root_action_mixes=mixes,entry_weighted_total_variation=tv,
        maximum_class_total_variation=max(c['total_variation'] for c in classes),classes=classes)


def main():
    path=OUT/'action-integrated-seed-comparison-v1-result.json'
    assert not path.exists()
    prefixes=['root-retained-exact-v1','root-retained-replication-exact-v1',
              'action-integrated-first-exact-v1','action-integrated-replication-exact-v1']
    datasets=[];inputs={};contexts=[];seeds=[];endpoints={}
    for prefix in prefixes:
        policy,rows,more=load(prefix);inputs.update(more)
        reg=read(OUT/f'{prefix}-registration.json')
        training=read(reg['training_registration'])
        inputs[reg['training_registration']]=sha(reg['training_registration'])
        contexts.append(policy['context_sha256']);datasets.append(rows)
        seeds.append({k:training['config'][k] for k in
            ('sampler_seed','action_seed','reservoir_seeds','fit_seed_base')})
        result=read(OUT/f'{prefix}-result.json')
        endpoints[prefix]={k:{metric:v[metric] for metric in ('bb_gain','btn_gain')}
            for k,v in result['pairings'].items()}
    assert len(set(contexts))==1 and seeds[0]==seeds[2] and seeds[1]==seeds[3]
    comparisons={
        'old_cross_seed':compare(datasets[0],datasets[1]),
        'integrated_cross_seed':compare(datasets[2],datasets[3]),
        'first_matched_algorithm_change':compare(datasets[0],datasets[2]),
        'replication_matched_algorithm_change':compare(datasets[1],datasets[3])}
    change=comparisons['integrated_cross_seed']['entry_weighted_total_variation']-comparisons['old_cross_seed']['entry_weighted_total_variation']
    for p in (Path(__file__),ROOT/'tools/research/hu_root_retained_seed_range_comparison_20260924.py',
              OUT/'ACTION-INTEGRATED-ENDPOINT-COMPARISON-PLAN.md'):
        inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    result=dict(passed=True,inputs=inputs,primary='linear/linear, generations 0..77',
        matched_seeds=seeds,comparisons=comparisons,all_endpoint_pairings=endpoints,
        cross_seed_variation_change=change,production_modified=False,accuracy_qualified=False,
        scope='Descriptive matched-estimator comparison with two fixed training seeds. No independent validation samples, confidence interval, full exploitability estimate, or evidence for other scenarios. Smaller cross-seed variation alone is not accurate play.')
    save(path,result)
    print({'old_variation':comparisons['old_cross_seed']['entry_weighted_total_variation'],
        'integrated_variation':comparisons['integrated_cross_seed']['entry_weighted_total_variation'],
        'variation_change':change})


if __name__=='__main__':main()
