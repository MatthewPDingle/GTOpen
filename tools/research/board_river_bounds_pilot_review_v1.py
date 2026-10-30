"""Parallel archive readback and fixed-pilot statistics; no policy selection."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1',PYTHONDONTWRITEBYTECODE='1')
import concurrent.futures
from functools import lru_cache
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,read,sha,verify
from bounded_parallel_evaluation_archive_v2 import production_available,install_fast_decoder
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_bank_v1 import histories
from later_average_support_v1 import load_complete_cache
from weighted_evaluation_checkpoint_v1 import restore_latest
from board_prefix_publication_v1 import atomic_json

PREFIX='weighted-complete-river-bounds-pilot-v1'
DEALS=4096;SEED=9289901


class Guard:
    def __init__(self):self.started=time.monotonic();self.last=0.
    def __call__(self):
        assert time.monotonic()-self.started<3600
        if time.monotonic()-self.last<2:return
        assert production_available() and not OTHER.exists() and psutil.virtual_memory().available>24_000_000_000
        self.last=time.monotonic()


@lru_cache(maxsize=1)
def cache():return load_complete_cache()


def inspect(job):
    store,name,route,expected_deals,source=job;guard=Guard();install_fast_decoder()
    root=Path(store)/route['attempt'];reader=ColumnarEvaluationReader(root,{name:route['manifest_sha256']},guard=guard)
    folder=root/name
    summary=reader.read_json(folder/'summary.json');assert reader.sha256(folder/'summary.json')==route['summary_sha256']
    for member,h in summary['artifacts'].items():assert reader.sha256(folder/member)==h
    assert set(summary['artifacts'])=={'query-batch.json','conditional-batch.json','queries.json','profiles.json','native.json','residuals.json'}
    raw=reader.read_json(folder/'query-batch.json');assert raw['deals']==expected_deals and len(expected_deals)==32
    assert set(raw)=={'format','batch_id','seed','query_limit','deals'}
    assert raw['batch_id']==f'{PREFIX}-{name}' and raw['seed']==0 and raw['query_limit']==100000
    assert all(len(d)==9 and len(set(d))==9 and all(0<=c<52 for c in d) for d in expected_deals)
    conditional=reader.read_json(folder/'conditional-batch.json')
    assert conditional==cache().batch(raw);cache().check_batch(conditional)
    query=reader.read_json(folder/'queries.json');obs=query['observations'];histories(obs)
    assert query['context_source']==source and query['batch_source']==reader.read_bytes(folder/'query-batch.json').decode()
    transport=reader.read_json(folder/'profiles.json')
    assert transport['context_source']==source and transport['batch_source']==reader.read_bytes(folder/'conditional-batch.json').decode()
    native=reader.read_json(folder/'native.json');profiles=transport['profiles']
    expected_names=[f'{seed}:{name}' for seed in ('first','replication') for name in
        ('oldBB-oldBTN','oldBB-newBTN','newBB-oldBTN','newBB-newBTN')]
    assert [p['name'] for p in profiles]==expected_names==[p['name'] for p in native['profiles']]==summary['profile_order']
    assert native['format']==2 and native['terminal_estimator']=='conditional-preflop-allin-v1' and native['postflop_outcomes']=='sampled-board'
    actors=np.array([o['actor'] for o in obs]);arity=np.array([o['n'] for o in obs]);legal=np.arange(4)[None,:]<arity[:,None]
    all_p=[]
    keys=[(o['hi'],o['lo'],o['actor'],o['n']) for o in obs]
    for profile in profiles:
        rows=profile['policies'];assert [(r['hi'],r['lo'],r['actor'],r['n']) for r in rows]==keys
        p=np.asarray([r['probabilities'] for r in rows],dtype=np.float64)
        assert p.shape==(len(obs),4) and np.isfinite(p).all() and np.all(p>=0) and np.all(p[~legal]==0)
        assert np.max(abs(p.sum(1)-1))<1e-10;all_p.append(p)
    policies=[all_p[i] for i in (0,3,4,7)]
    assert len(summary['coverage'])==4 and summary['allin_cache_sha256']==cache().sha256
    for p,c in zip(policies,summary['coverage']):assert hashlib.sha256(p.tobytes()).hexdigest()==c['probabilities_sha256']
    for seed in range(2):
        for j,(bb,btn) in enumerate(((0,0),(0,1),(1,0),(1,1))):
            correct=np.where((actors==0)[:,None],policies[2*seed+bb],policies[2*seed+btn])
            assert np.array_equal(correct,all_p[4*seed+j])
    values=np.asarray([[d['values'] for d in p['deals']] for p in native['profiles']],dtype=np.float64).transpose(1,0,2).reshape(32,2,4,2)
    assert np.array_equal(values,np.array(summary['values'])) and np.isfinite(values).all()
    context=json.loads(source);stack=context['config']['stack'];dead=context['dead_money']
    assert np.all(values>=-stack) and np.all(values<=stack+dead)
    delta=[]
    for s in range(2):delta.extend((values[:,s,2,0]-values[:,s,0,0],values[:,s,3,0]-values[:,s,1,0],
        values[:,s,1,1]-values[:,s,0,1],values[:,s,3,1]-values[:,s,2,1]))
    delta=np.stack(delta,axis=1);residual=reader.read_json(folder/'residuals.json')
    assert np.array_equal(delta,np.asarray(residual['values'])) and not residual['bounds_best_response_above']
    for field in ('maximum_forward_cashflow_error','maximum_conservation_error'):
        assert native[field]==summary[field] and 0<=native[field]<1e-10
    return dict(name=name,deals=32,queries=len(obs),differences=delta.tolist(),
        query_seconds=summary['query_seconds'],inference_seconds=sum(summary['averaging_seconds']),native_seconds=summary['native_seconds'],
        maximum_cashflow_error=native['maximum_forward_cashflow_error'],maximum_conservation_error=native['maximum_conservation_error'])


def near(a,b):assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-12),(a,b)


def main():
    rp=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    reg=read(rp);result=read(result_path);guard=Guard()
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert reg['deals']==result['deals']==DEALS and reg['test_seed']==result['test_seed']==SEED
    store=Path(result['store']);assert str(store)==reg['store']
    assert not LOCK.exists() and not OTHER.exists();acquired=False
    rr=OUT/(PREFIX+'-readback-registration.json');review_path=OUT/(PREFIX+'-independent-review.json')
    assert not rr.exists() and not review_path.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();verify(reg['inputs'])
        for member,key in (('bank-identities.json','bank_identities_sha256'),('analysis.json','analysis_sha256'),
                ('sampler-initial.json','sampler_initial_sha256'),('sampler-final.json','sampler_final_sha256')):assert sha(store/member)==result[key]
        source=(OUT/'bb-context-candidate.json').read_text()
        recovered,acc,routes,checkpoint=restore_latest(store,registration_sha256=sha(rp),bank_identities_sha256=result['bank_identities_sha256'],
            context_source=source,total_deals=DEALS,seed=SEED,guard=guard)
        assert checkpoint==result['checkpoint'] and routes==result['routes'] and recovered.draws==DEALS
        assert read(store/'sampler-final.json')==recovered.checkpoint()
        analysis=read(store/'analysis.json');assert acc.finish()==analysis
        sampler=PhysicalDeals(source,mode='full_deck',seed=SEED);assert sampler.checkpoint()==read(store/'sampler-initial.json')
        jobs=[(str(store),f'test-{i:06d}',routes[f'test-{i:06d}'],sampler.sample(32)['deals'],source) for i in range(0,DEALS,32)]
        assert sampler.checkpoint()==recovered.checkpoint()
        paths=dict(reg['inputs']);paths.update({str(p):sha(p) for p in (Path(__file__),rp,result_path,store/checkpoint['file'])})
        atomic_json(rr,dict(inputs=paths,workers=8,deals=DEALS,source_result_sha256=sha(result_path),
            maximum_seconds=3600,scope='All archived chance, conditional labels, transport crossings, native values and statistics; no neural inference or independent poker engine.',
            production_modified=False,gpu_used=False))
        with concurrent.futures.ProcessPoolExecutor(max_workers=8,mp_context=multiprocessing.get_context('spawn')) as pool:
            rows=list(pool.map(inspect,jobs,chunksize=1))
        d=np.concatenate([np.array(r['differences']) for r in rows]);assert d.shape==(DEALS,8)
        statistics=[];context=json.loads(source);radius=2*context['config']['stack']+context['dead_money'];log=math.log(4*8/.05)
        for i,old in enumerate(analysis['contrasts']):
            mean=float(np.mean(d[:,i]));variance=float(np.var(d[:,i],ddof=1));se=math.sqrt(variance/DEALS)
            rad=math.sqrt(2*variance*log/DEALS)+7*(2*radius)*log/(3*(DEALS-1))
            for key,value in (('mean',mean),('sample_variance',variance),('standard_error',se),('radius',rad),
                              ('lower',max(-radius,mean-rad)),('upper',min(radius,mean+rad))):near(old[key],value)
            statistics.append(dict(name=old['name'],mean=mean,standard_error=se,standard_deviation=math.sqrt(variance),
                bounded_lower=old['lower'],bounded_upper=old['upper'],approximate_95_lower=mean-1.96*se,approximate_95_upper=mean+1.96*se))
        verify(paths);estimated=math.ceil((3*max(s['standard_deviation'] for s in statistics)/.01)**2)
        output=dict(passed=True,complete=True,registration_sha256=sha(rr),source_result_sha256=sha(result_path),
            deals=DEALS,unique_batches=len(rows),queries_checked=sum(r['queries'] for r in rows),statistics=statistics,
            approximate_planning_deals_for_three_se_001bb=estimated,
            component_seconds={k:sum(r[k] for r in rows) for k in ('query_seconds','inference_seconds','native_seconds')},
            maximum_cashflow_error=max(r['maximum_cashflow_error'] for r in rows),maximum_conservation_error=max(r['maximum_conservation_error'] for r in rows),
            seconds=time.monotonic()-guard.started,production_modified=False,accuracy_qualified=False,neural_inference_recomputed=False,
            interpretation='Pilot only; approximate intervals are descriptive, simultaneous bounded intervals are the registered finite-sample statements.')
        atomic_json(review_path,output);print(json.dumps(output),flush=True)
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
