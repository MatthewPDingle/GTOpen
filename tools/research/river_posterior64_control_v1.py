"""Qualify two-stage posterior sampling against frozen full native river trees."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy, hashlib, json, math, sys, time, traceback
from pathlib import Path
import numpy as np
import psutil
from river_posterior64_v1 import SAMPLES, subset, history_indices, posterior, draw, future_indices, sampled_target
from river_policy_batch_v1 import CPUCurrentPolicy
from river_shared_values_v1 import evaluate_many
from river_full_action_control_v1 import bundle
from board_training_checkpoint_v1 import model_document
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT = Path('T:/Dev/GTOpen'); OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'river-posterior64-control-v1'; STORE = OUT/NAME
REG = OUT/(NAME+'-registration.json'); RESULT = OUT/(NAME+'-result.json'); FAILURE = OUT/(NAME+'-failure.json')
LIMIT = 8_000_000

def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def size(): return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) + sum(p.stat().st_size for p in (REG, RESULT, FAILURE) if p.exists())
def save(p, x):
    raw = (json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()
    assert size()+len(raw)<LIMIT
    with Path(p).open('xb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
def verify(inputs):
    for p,h in inputs.items(): assert sha(p)==h, p
def guard():
    assert production_available() and psutil.virtual_memory().available>24_000_000_000
    assert psutil.Process().memory_info().rss<16_000_000_000 and size()<LIMIT
def rejected(fn):
    try: fn()
    except (ValueError, AssertionError, KeyError, IndexError): return True
    raise AssertionError('Invalid input accepted')

def saved_policy(batch, case, prior, exports):
    rows = batch['queries']['observations']; lookup = {(r['hi'],r['lo']):i for i,r in enumerate(rows)}
    original = read(prior/case['case']/'queries.json')['observations']
    qids = {(o['hi'],o['lo']):i for i,o in enumerate(original)}
    p = np.full((len(rows),4), np.nan)
    with np.load(prior/case['case']/'conditional-policies.npz', allow_pickle=False) as retained:
        for doc in batch['targets']:
            key = (doc['target']['hi'], doc['target']['lo']); old = read(exports[key]['path'])
            ids = np.array([lookup[(o['hi'],o['lo'])] for o in old['queries']['observations']])
            values = retained['p-'+str(qids[key])]; used = np.isfinite(p[ids,0])
            assert np.array_equal(p[ids[used]],values[used]); p[ids] = values
    assert np.isfinite(p).all()
    return p

def prepare_policy(engine, queries, indices, reference):
    began = time.perf_counter(); selected, ids = subset(queries, indices)
    p = engine.infer(engine.prepare(selected)); elapsed = time.perf_counter()-began
    error = float(np.max(abs(p-reference[ids])))
    assert error<1e-10 and np.array_equal(p>0, reference[ids]>0)
    full = np.full(reference.shape, np.nan); full[ids] = p
    return full, ids, elapsed, error

def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE)); STORE.mkdir(); start=time.monotonic(); guard()
    regpath=OUT/'river-learned-batch-cost-v1-registration.json'; prior_result=OUT/'river-learned-batch-cost-v1-result.json'
    previous=read(prior_result); oldreg=read(regpath); seal=read(OUT/'river-batch-evidence-review-v1.json')
    assert previous['passed'] and seal['passed'] and previous['registration_sha256']==sha(regpath)
    prior=OUT/'river-learned-batch-cost-v1'; shared=OUT/'river-shared-export-control-v1'
    exports={tuple(e['key']):e for e in previous['exports']}
    inputs=dict(oldreg['inputs']); paths=[Path(__file__),OUT/'RIVER-POSTERIOR64-PLAN.md',regpath,prior_result,OUT/'river-batch-evidence-review-v1.json']
    manifests={e['name']:e['artifacts'] for e in seal['experiments']}
    for case in previous['cases']:
        for rel in ('new/export.json',):
            p=shared/case['case']/rel; assert sha(p)==manifests[shared.name][case['case']+'/'+rel]['sha256']; paths.append(p)
        for rel in ('queries.json','conditional-policies.npz'):
            p=prior/case['case']/rel; assert sha(p)==case['artifacts'][rel]; paths.append(p)
    for item in exports.values(): assert sha(item['path'])==item['sha256']; paths.append(Path(item['path']))
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py': paths.append(Path(p))
    inputs.update({str(p):sha(p) for p in paths}); verify(inputs)
    save(REG,dict(format=1,inputs=inputs,K=SAMPLES,moment_repetitions=2048,cases=[c['case'] for c in previous['cases']],
                  gate_maximum_total_query_ratio=.75,maximum_seconds=300,maximum_bytes=LIMIT,gpu_used=False,training=False))
    try:
        source=(OUT/'bb-context-candidate.json').read_text(); cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json'); mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        weights=PhysicalDeals(source,mode='full_deck',seed=0).weights; entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,r)} for r in weights]
        mass=AllinMatrix(read(mp),source).btn_mass; engines={}
        for item in oldreg['policies']:
            args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=mass,root_config=item['root_config'])
            model=model_document(item['folder'],item['reference'],context_source=source,**args)
            engines[item['policy_id']]=CPUCurrentPolicy(model,source,**args)
        reports=[]; negative_done=False
        for case in previous['cases']:
            guard(); batch=read(shared/case['case']/'new/export.json'); rows=batch['queries']['observations']
            p=saved_policy(batch,case,prior,exports); identity=case['policy_id']; engine=engines[identity]
            exact=evaluate_many(batch,bundle(batch,p.tolist(),identity),entry,expected_policy_id=identity,expected_context_source=source)
            first,ids1,time1,error1=prepare_policy(engine,batch['queries'],history_indices(batch),p)
            plans=[]; needed=set(); maxpost=0.
            for doc,ref in zip(batch['targets'],exact):
                post,total,own=posterior(doc,rows,first,entry)
                error=float(np.max(abs(post-ref['posterior']))); maxpost=max(maxpost,error); assert error<1e-12
                assert abs(total-ref['opponent_mass'])<1e-10 and abs(own-ref['own_history_likelihood'])<1e-12
                name=case['case']+'|'+identity+'|'+doc['target']['hi']+'|'+doc['target']['lo']
                draws=draw(post,name); needed.update(future_indices(doc,draws)); plans.append((doc,ref,post,draws,name))
            second,ids2,time2,error2=prepare_policy(engine,batch['queries'],needed,p)
            target_reports=[]; maxvalue=0.
            for doc,ref,post,draws,name in plans:
                estimated=sampled_target(doc,second,draws); q=np.asarray(ref['pair_action_values']); n=q.shape[1]
                sigma=p[doc['target']['query_index'],:n]; selected=q[draws].mean(0); independent=selected-float(sigma@selected)
                error=float(np.max(abs(estimated['regrets']-independent))); maxvalue=max(maxvalue,error); assert error<1e-8
                assert np.max(abs(estimated['action_values']-selected))<1e-8 and abs(sigma@estimated['regrets'])<1e-8
                pairreg=q-(q@sigma)[:,None]; expected=post@pairreg; exactreg=np.asarray(ref['regrets'])
                assert np.max(abs(expected-exactreg))<1e-8
                centered=pairreg-expected; covariance=centered.T@(centered*post[:,None]); sample_cov=covariance/SAMPLES
                seed=int.from_bytes(hashlib.sha256(('independent-moments|'+name).encode()).digest()[:16],'little')
                rng=np.random.Generator(np.random.PCG64(seed)); cdf=np.cumsum(post); cdf[-1]=1.
                mcids=np.searchsorted(cdf,rng.random((2048,SAMPLES)),side='right')
                means=pairreg[mcids].mean(1); mean=means.mean(0); se=np.sqrt(np.maximum(0.,np.diag(sample_cov))/len(means))
                assert np.all(abs(mean-expected)<=8*se+1e-9)
                mse=float(np.mean(np.sum((means-expected)**2,axis=1))); predicted=float(np.trace(sample_cov))
                target_reports.append(dict(hi=doc['target']['hi'],lo=doc['target']['lo'],actor=doc['target']['actor'],
                    draws=draws.tolist(),unique_pairs=len(np.unique(draws)),posterior_positive_pairs=int(np.count_nonzero(post)),
                    expected_regrets=expected.tolist(),sampled_regrets=estimated['regrets'].tolist(),
                    single_draw_covariance=covariance.tolist(),sample_mean_covariance=sample_cov.tolist(),
                    observed_mean=mean.tolist(),mean_standard_error=se.tolist(),empirical_mse=mse,expected_mse=predicted,
                    maximum_selected_value_error=error))
                if not negative_done:
                    noentry=[dict(e) for e in entry]; noentry[1-doc['target']['actor']]={k:0. for k in noentry[1-doc['target']['actor']]}
                    broken=copy.deepcopy(doc); broken['pairs'].pop()
                    assert rejected(lambda:posterior(doc,rows,first,noentry))
                    assert rejected(lambda:posterior(broken,rows,first,entry))
                    assert rejected(lambda:draw(post*2,name)) and rejected(lambda:draw(np.full(990,np.nan),name))
                    assert rejected(lambda:future_indices(doc,draws[:-1]))
                    bad=draws.copy(); bad[0]=990; assert rejected(lambda:future_indices(doc,bad))
                    assert rejected(lambda:sampled_target(doc,np.full(p.shape,np.nan),draws))
                    # Repeat a deliberately uneven pair mix to catch deduplication of draws.
                    a=int(np.argmax(post)); b=int(np.argmax(np.max(abs(q-q[a]),axis=1)))
                    repeated=np.array([a]*63+[b],dtype=np.int64)
                    good=sampled_target(doc,p,repeated); weighted=(63*q[a]+q[b])/64
                    assert np.max(abs(good['action_values']-weighted))<1e-8
                    assert np.max(abs(weighted-(q[a]+q[b])/2))>1e-8
                    negative_done=True
            report=dict(case=case['case'],targets=len(plans),full_queries=len(rows),history_queries=len(ids1),selected_future_queries=len(ids2),
                        duplicated_queries=len(set(ids1)&set(ids2)),total_prepared_queries=len(ids1)+len(ids2),
                        history_subset_prepare_infer_seconds=time1,selected_subset_prepare_infer_seconds=time2,
                        maximum_policy_error=max(error1,error2),maximum_posterior_error=maxpost,maximum_sampled_value_error=maxvalue,
                        target_results=target_reports)
            save(STORE/(case['case']+'.json'),report); reports.append(report)
            print(json.dumps(dict(case=case['case'],query_ratio=report['total_prepared_queries']/len(rows))),flush=True)
            assert time.monotonic()-start<300
        verify(inputs); guard(); full=sum(c['full_queries'] for c in reports); reduced=sum(c['total_prepared_queries'] for c in reports)
        save(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,full_queries=full,total_prepared_queries=reduced,
                         query_ratio=reduced/full,native_implementation_gate_passed=reduced/full<=.75,negative_controls_passed=7,multiplicity_control_passed=True,
                         seconds=time.monotonic()-start,gpu_used=False,training=False,production_modified=False,
                         scope='Reused TRAIN exact posterior and unbiased 64-draw target controls. Query demand only; no native wall-time or range-quality claim.'))
        print(json.dumps(dict(passed=True,query_ratio=reduced/full,gate=reduced/full<=.75,seconds=time.monotonic()-start)),flush=True)
    except Exception as e:
        save(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start)); raise

if __name__=='__main__': main()
