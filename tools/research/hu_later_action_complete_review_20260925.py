"""Independent scalar readback of the complete-policy crossed evaluation.

Replays chance, validates archived transports/payoff identities, and recomputes
paired statistics. Does not perform neural inference or rerun native poker.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import time
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from later_average_support_v1 import OUT,read,load_complete_cache
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from sampled_physical_deals_v1 import PhysicalDeals
from reboot_research_idle_v1 import idle

NAMES=tuple(f'{s}:{p}' for s in ('first','replication') for p in
    ('oldBB-oldBTN','oldBB-newBTN','newBB-oldBTN','newBB-newBTN'))
GAINS=tuple(f'{s}:{p}' for s in ('first','replication') for p in
    ('newBB-v-oldBB-against-oldBTN','newBB-v-oldBB-against-newBTN',
     'newBTN-v-oldBTN-against-oldBB','newBTN-v-oldBTN-against-newBB'))


def verify_batch(reader,folder,expected_batch,source,cache,root_policies=None):
    files=('query-batch.json','conditional-batch.json','queries.json','profiles.json',
           'native.json','residuals.json','summary.json')
    raw={name:reader.read_bytes(folder/name) for name in files}
    d={name:json.loads(value) for name,value in raw.items()}
    summary=d['summary.json'];assert set(summary['artifacts'])==set(files)-{'summary.json'}
    for name,h in summary['artifacts'].items():assert hashlib.sha256(raw[name]).hexdigest()==h
    assert d['query-batch.json']==expected_batch
    labels=d['conditional-batch.json'];cache.check_batch(labels)
    assert labels['deals']==expected_batch['deals']
    query=d['queries.json'];transport=d['profiles.json'];native=d['native.json']
    assert query['context_source']==transport['context_source']==source
    assert query['batch_source']==raw['query-batch.json'].decode()
    assert transport['batch_source']==raw['conditional-batch.json'].decode()
    assert transport['format']==1 and query['format']==2
    assert [p['name'] for p in transport['profiles']]==[p['name'] for p in native['profiles']]==list(NAMES)
    assert native['format']==2 and native['terminal_estimator']=='conditional-preflop-allin-v1'
    assert native['postflop_outcomes']=='sampled-board' and native['fixed_policy_evaluation_only']
    assert native['bounds_best_response_above'] is False
    profiles=[p['policies'] for p in transport['profiles']];obs=query['observations']
    assert all(len(p)==len(obs) for p in profiles)
    for i,o in enumerate(obs):
        assert o['actor'] in (0,1) and o['n'] in (2,3,4)
        for k,profile in enumerate(profiles):
            row=profile[i];assert {a:row[a] for a in ('hi','lo','actor','n')}=={a:o[a] for a in ('hi','lo','actor','n')}
            p=row['probabilities'];assert len(p)==4 and all(math.isfinite(v) and v>=0 for v in p)
            assert abs(math.fsum(p)-1)<1e-10 and all(v==0 for v in p[o['n']:])
            seed=k//4;pair=k%4;bb,btn=divmod(pair,2)
            donor=seed*4+3*(bb if o['actor']==0 else btn)
            assert p==profiles[donor][i]['probabilities'],'Mixed profile changed actor policy'
    for k,pure in enumerate((0,3,4,7)):
        h=hashlib.sha256()
        for o,row in zip(obs,profiles[pure]):
            h.update(struct.pack('<4d',*row['probabilities']))
            if root_policies is not None and o['phase']==0 and int(o['hi'])==1:
                assert o['actor']==0 and o['own_history']==[]
                lo=int(o['lo']);c=hand_class([lo&63,(lo>>6)&63])
                assert max(abs(a-b) for a,b in zip(row['probabilities'],root_policies[k][c]))<1e-10
        assert h.hexdigest()==summary['coverage'][k]['probabilities_sha256']
    context=json.loads(source);stack=context['config']['stack'];dead=context['dead_money']
    n=len(expected_batch['deals']);assert summary['deals']==n and summary['profile_order']==list(NAMES)
    assert all(len(p['deals'])==n for p in native['profiles'])
    assert summary['allin_cache_sha256']==cache.sha256
    for key in ('maximum_conservation_error','maximum_forward_cashflow_error'):
        assert summary[key]==native[key] and 0<=native[key]<1e-10
    output=[]
    for at in range(n):
        values=[];delta=[]
        for seed in range(2):
            pair=[]
            for p in native['profiles'][4*seed:4*seed+4]:
                r=p['deals'][at];assert r['deal_index']==at and abs(r['terminal_mass']-1)<1e-10
                assert math.isfinite(r['expected_rake']) and r['expected_rake']>=0
                v=r['values'];assert len(v)==2 and all(math.isfinite(x) and -stack<=x<=stack+dead for x in v)
                assert abs(math.fsum(v)+r['expected_rake']-dead)<1e-8
                pair.append(v)
            values.append(pair)
            delta.extend((pair[2][0]-pair[0][0],pair[3][0]-pair[1][0],
                          pair[1][1]-pair[0][1],pair[3][1]-pair[2][1]))
        assert values==summary['values'][at]
        assert delta==d['residuals.json']['values'][at]
        output.append(delta)
    assert d['residuals.json']['purpose']=='eight-paired-complete-policy-gains'
    assert d['residuals.json']['bounds_best_response_above'] is False
    return output,len(obs),hashlib.sha256(raw['summary.json']).hexdigest()


def verify_stability(document,matrix):
    p=document['root_probabilities'];m=document['entry_masses']
    assert len(p)==4 and all(len(bank)==169 for bank in p) and len(m)==169
    assert document['policy_order']==['first-old','first-new','replication-old','replication-new']
    assert document['action_order']==['fold','call','raise','jam'] and document['accuracy_qualified'] is False
    rows=[math.fsum(row) for row in matrix['class_mass']];total=math.fsum(rows)
    for a,b in zip(m,rows):assert a>0 and abs(a-b/total)<1e-12
    assert abs(math.fsum(m)-1)<1e-12
    for bank in p:
        for row in bank:
            assert len(row)==4 and all(math.isfinite(v) and v>=0 for v in row)
            assert abs(math.fsum(row)-1)<1e-10
    for k,bank in enumerate(p):
        for action in range(4):
            wanted=math.fsum(w*row[action] for w,row in zip(m,bank))
            assert abs(wanted-document['aggregate_action_frequencies'][k][action])<1e-12
    wanted_comparisons=[('baseline_cross_seed',0,2),('candidate_cross_seed',1,3),
        ('first_matched_change',0,1),('replication_matched_change',2,3)]
    assert set(document['comparisons'])=={x[0] for x in wanted_comparisons}
    for name,a,b in wanted_comparisons:
        row=document['comparisons'][name]
        tv=[math.fsum(abs(u-v) for u,v in zip(x,y))*.5 for x,y in zip(p[a],p[b])]
        assert len(row['class_total_variation'])==169
        assert max(abs(x-y) for x,y in zip(tv,row['class_total_variation']))<1e-12
        assert abs(math.fsum(w*v for w,v in zip(m,tv))-row['entry_weighted_total_variation'])<1e-12
        differs=sum(max(range(4),key=x.__getitem__)!=max(range(4),key=y.__getitem__) for x,y in zip(p[a],p[b]))
        assert differs==row['classes_with_different_most_frequent_action']
    difference=document['comparisons']['candidate_cross_seed']['entry_weighted_total_variation']-document['comparisons']['baseline_cross_seed']['entry_weighted_total_variation']
    assert abs(difference-document['candidate_minus_baseline_variation'])<1e-12
    return p


def main(mode):
    assert mode in ('control','study');prefix=f'later-action-complete-evaluation-{mode}-v1'
    start=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-start<7200
        if now-last>2:assert idle();last=now
    guard();rp,pp=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert reg['mode']==result['mode']==mode and result['deals']==reg['deals']==(64 if mode=='control' else 65536)
    assert reg['test_seed']==(None if mode=='control' else 382921) and reg['batch_size']==32
    for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
    store=Path(result['store']);assert str(store)==reg['store']
    assert sha(store/'analysis.json')==result['analysis_sha256']
    assert sha(store/'bank-identities.json')==result['bank_identities_sha256']
    assert sha(store/'root-stability.json')==result['root_stability_sha256']
    root_policies=verify_stability(read(store/'root-stability.json'),read(OUT/'preflop-allin-matrix-control-v1-matrix.json'))
    identities=read(store/'bank-identities.json')
    for name,identity in zip(reg['training_prefixes'],identities,strict=True):
        assert identity['prefix']==name and identity['played_generations']==list(range(78))
        assert identity['excluded_generation']==78 and identity['weights']==[list(range(1,79))]*2
        tr,tp,ta=[OUT/f'{name}-{s}.json' for s in ('registration','result','independent-review')]
        assert identity['registration_sha256']==sha(tr) and identity['result_sha256']==sha(tp) and identity['audit_sha256']==sha(ta)
        assert identity['checkpoint']==read(tp)['final_checkpoint']
    reviewrp=OUT/f'{prefix}-readback-registration.json'
    save(reviewrp,dict(inputs={str(rp):sha(rp),str(pp):sha(pp),str(Path(__file__).resolve()):sha(Path(__file__))},
        maximum_seconds=7200,gpu_used=False,production_modified=False,
        scope='Independent chance, transport, archived values and paired intervals. No repeated neural inference or independent poker evaluation.'))
    try:
        source=(OUT/'bb-context-candidate.json').read_text();context=json.loads(source)
        cache=load_complete_cache();sampler=None
        if mode=='study':
            sampler=PhysicalDeals(source,mode='full_deck',seed=382921)
            assert read(store/'sampler-initial.json')==sampler.checkpoint()
        else:reused=read(reg['reused_batch'])['deals']
        reader=ArchivedEvaluationReader(store,result['archive_manifest_hashes'],external_files=[],guard=guard)
        expected_names=[f'test-{i:06d}' for i in range(0,reg['deals'],32)]
        assert set(expected_names)==set(result['archive_manifest_hashes'])==set(result['batch_summary_hashes'])
        values=[];observations=0
        for offset,name in zip(range(0,reg['deals'],32),expected_names):
            guard();deals=sampler.sample(32)['deals'] if sampler else reused[offset:offset+32]
            batch=dict(format=2,batch_id=f'{prefix}-{name}',seed=0,query_limit=100000,deals=deals)
            delta,n,digest=verify_batch(reader,store/name,batch,source,cache,root_policies)
            assert digest==result['batch_summary_hashes'][name];values.extend(delta);observations+=n
            if offset//32%64==0:print(json.dumps(dict(reviewed_deals=offset+32)),flush=True)
        if sampler:assert read(store/'sampler-final.json')==sampler.checkpoint()
        analysis=read(store/'analysis.json');n=len(values);bound=2*context['config']['stack']+context['dead_money']
        assert n==analysis['deals']==reg['deals'] and analysis['profile_order']==list(NAMES)
        assert analysis['family_error_probability']==.05 and analysis['accuracy_qualified'] is False
        assert analysis['control_only']==(mode=='control') and analysis['bounds_best_response_above'] is False
        error=0.
        def close(a,b):
            nonlocal error
            delta=abs(a-b);assert math.isfinite(delta) and delta<1e-8;error=max(error,delta)
        for i,row in enumerate(analysis['contrasts']):
            assert row['name']==GAINS[i] and row['count']==n and row['family_error_probability']==.05
            x=[v[i] for v in values];assert all(-bound<=v<=bound for v in x)
            mean=math.fsum(x)/n;var=math.fsum((v-mean)**2 for v in x)/(n-1)
            radius=math.sqrt(2*var*math.log(32/.05)/n)+7*(2*bound)*math.log(32/.05)/(3*(n-1))
            for key,wanted in dict(mean=mean,sample_variance=var,standard_error=math.sqrt(var/n),
                radius=radius,lower=max(-bound,mean-radius),upper=min(bound,mean+radius)).items():close(row[key],wanted)
        assert len(analysis['contrasts'])==8
        for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
        save(OUT/f'{prefix}-independent-review.json',dict(passed=True,source_registration_sha256=sha(rp),
            source_result_sha256=sha(pp),readback_registration_sha256=sha(reviewrp),deals=n,
            observations=observations,maximum_statistical_error=error,seconds=time.monotonic()-start,
            gpu_used=False,production_modified=False,accuracy_qualified=False))
    except BaseException as exc:
        save(OUT/f'{prefix}-independent-review.json',dict(passed=False,error=repr(exc),
            readback_registration_sha256=sha(reviewrp),seconds=time.monotonic()-start))
        raise


if __name__=='__main__':
    assert len(sys.argv)==2;main(sys.argv[1])
