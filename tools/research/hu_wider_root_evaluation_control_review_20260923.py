"""Readback using scalar response/residual/interval arithmetic and chance replay."""
import math
from pathlib import Path
import time
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha,save,hand_class
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_player_stratified_response_deals_v2 import sample
from reboot_research_idle_v1 import idle

PREFIX='wider-root-evaluation-control-v1'


def main():
    start=time.monotonic();assert idle()
    rp,pp=[OUT/f'{PREFIX}-{k}.json' for k in ('registration','result')]
    reg,outer=read(rp),read(pp);assert outer['passed'] and outer['registration_sha256']==sha(rp)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    folder=Path(reg['store']);result=read(folder/'result.json');assert sha(folder/'result.json')==outer['result_sha256']
    config=reg['config'];exact=reg['exact'];source=(OUT/'bb-context-candidate.json').read_text()
    assert sha(OUT/'bb-context-candidate.json')==exact['context_sha256']
    sampled=read(folder/'training-deals.json')
    assert sampled==sample(source,player=0,seed=config['train_seed'],per_class=2,classes=list(range(169)),guard=lambda:None)
    response=read(folder/'response.json');prepared=read(folder/'residual-preparation.json');test_start=read(folder/'test-start.json')
    assert sha(folder/'response.json')==result['response_sha256']==test_start['response_sha256']
    assert sha(folder/'residual-preparation.json')==result['preparation_sha256']==test_start['preparation_sha256']
    assert (folder/'response.json').stat().st_mtime_ns <= (folder/'test-start.json').stat().st_mtime_ns
    test=PhysicalDeals(source,mode='full_deck',seed=config['test_seed']);assert test.checkpoint()==test_start['initial_rng']
    data={};maximum=0.;ids={}
    for phase,n in [('train',338),('test',128)]:
        cs=[];qs=[];names=[]
        for offset in range(0,n,16):
            name=f'{phase}-{offset:06d}';part=folder/name;s=read(part/'summary.json')
            assert sha(part/'summary.json')==result['batch_summary_hashes'][name]
            for filename,h in s['artifacts'].items():assert sha(part/filename)==h
            batch=read(part/'query-batch.json')
            wanted=sampled['deals'][offset:offset+16] if phase=='train' else test.sample(16)['deals']
            assert batch['deals']==wanted and s['classes']==[hand_class(d[:2]) for d in wanted]
            assert batch['format']==2 and s['policy_input']=='unlabelled visible queries' and s['postflop_outcomes']=='sampled-board'
            assert s['maximum_root_mixture_error']<1e-9 and s['maximum_forward_cashflow_error']<1e-9
            cs.extend(s['classes']);qs.extend(s['action_values']);names.extend(f"{config['id']}-{name}-{i}" for i in range(len(wanted)))
        data[phase]=(cs,qs);ids[phase]=names
    assert not set(ids['train'])&set(ids['test']) and ids['train']==response['training_ids']
    actions=[];counts=[];means=[]
    for c in range(169):
        rows=[q for h,q in zip(*data['train']) if h==c];counts.append(len(rows));assert len(rows)==2
        m=[exact['fold_entries'][c]/exact['masses'][c],math.fsum(q[1] for q in rows)/2,
           math.fsum(q[2] for q in rows)/2,exact['jam_entries'][c]/exact['masses'][c]]
        a=max(range(4),key=lambda i:m[i]);actions.append(a);means.append(m)
        maximum=max(maximum,max(abs(x-y) for x,y in zip(m,response['class_action_means'][c])))
        assert response['probabilities'][c]==[float(i==a) for i in range(4)]
    assert actions==response['selected_actions'] and counts==result['training_counts']
    context=read(OUT/'bb-context-candidate.json');lo=-context['config']['stack'];hi=context['config']['stack']+context['dead_money']
    series=('trained-response','always-fold','always-call','always-raise','always-jam');test_counts=[0]*169
    for c in data['test'][0]:test_counts[c]+=1
    assert test_counts==result['test_counts'] and test.draws==128
    for index,name in enumerate(series):
        rho=response['probabilities'] if index==0 else [[float(a==index-1) for a in range(4)]]*169
        delta=[[rho[c][a]-exact['baseline'][c][a] for a in range(4)] for c in range(169)]
        offset=math.fsum(delta[c][0]*exact['fold_entries'][c]+delta[c][3]*exact['jam_entries'][c] for c in range(169))
        lower=min(math.fsum(x*(lo if x>=0 else hi) for x in row[1:3]) for row in delta)-1e-9
        upper=max(math.fsum(x*(hi if x>=0 else lo) for x in row[1:3]) for row in delta)+1e-9
        values=[math.fsum(delta[c][a]*q[a] for a in (1,2)) for c,q in zip(*data['test'])]
        assert all(lower<=v<=upper for v in values)
        mean=math.fsum(values)/128;var=math.fsum((x-mean)**2 for x in values)/127
        logarithm=math.log(4*5/config['family_alpha']);radius=math.sqrt(2*var*logarithm/128)+7*(upper-lower)*logarithm/(3*127)
        expected=dict(mean=mean+offset,lower=max(lower,mean-radius)+offset,upper=min(upper,mean+radius)+offset,
            residual_mean=mean,exact_offset=offset,sample_variance=var,radius=radius)
        for k,v in expected.items():maximum=max(maximum,abs(v-result['intervals'][name][k]))
        maximum=max(maximum,abs(offset-prepared[name]['total_offset']),abs(lower-prepared[name]['residual_lower']),abs(upper-prepared[name]['residual_upper']))
        assert prepared[name]['centre']==[0.]*169
        stored=[]
        for at in range(0,128,16):
            d=read(folder/f'test-{at:06d}'/'residuals.json');assert d['response_sha256']==result['response_sha256'];stored.extend(d['values'][name])
        maximum=max(maximum,max(abs(a-b) for a,b in zip(stored,values)))
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    assert maximum<1e-9 and idle() and time.monotonic()-start<120
    audit=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),reviewer_sha256=sha(Path(__file__)),
        complete_training_deals_replayed=338,complete_population_test_deals_replayed=128,
        class_response_choices_reconstructed=169,intervals_reconstructed=5,maximum_scalar_error_bb=maximum,
        seconds=time.monotonic()-start,gpu_used=False,production_modified=False,accuracy_qualified=False,
        limitation='Execution control only. Native payoffs and bank inference were not independently rerun by this readback.')
    save(OUT/f'{PREFIX}-independent-review.json',audit);print(audit)


if __name__=='__main__':main()
