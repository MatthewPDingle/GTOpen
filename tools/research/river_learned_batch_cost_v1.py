"""Bounded actual-policy river labels against the existing action-integrated trainer."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy,hashlib,io,itertools,json,subprocess,sys,time,traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import psutil
from river_policy_batch_v1 import CPUCurrentPolicy,merge_queries
from river_full_action_math_v1 import evaluate,digest,validate_document
from river_full_action_control_v1 import bundle
from board_training_policy_v1 import probabilities as reference
from board_training_checkpoint_v1 import model_document
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import AllinCache,policy_document
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from later_action_training_ingest_v1 import replacements
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-learned-batch-cost-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
CONTEXT=OUT/'bb-context-candidate.json';PLAN=OUT/'RIVER-LEARNED-BATCH-COST-PLAN.md'
EXES={k:ROOT/'target/release/examples'/v for k,v in dict(bridge='hu_sampled_allin_bridge_v3.exe',trace='hu_sampled_action_trace_v2.exe',export='hu_river_action_queries_v1.exe').items()}
LIMIT=512_000_000
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def used():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
def save(p,x):
    raw=(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();assert used()+len(raw)<LIMIT
    with Path(p).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def guard():
    assert production_available(),'Active production solve'
    assert psutil.virtual_memory().available>24_000_000_000
    assert psutil.Process().memory_info().rss<16_000_000_000
    assert used()<LIMIT
def invoke(exe,args,log):
    began=time.perf_counter();p=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    result=dict(seconds=time.perf_counter()-began,code=p.returncode,stdout=p.stdout,stderr=p.stderr);save(log,result);assert p.returncode==0,result
    return result['seconds']
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p
def pair_index(doc,deal):
    hero=doc['target']['actor'];visible=list(deal[hero*2:hero*2+2])+list(deal[4:]);wanted=doc['target']['cards'];found=[]
    for suit in itertools.permutations(range(4)):
        x=[4*(c//4)+suit[c%4] for c in visible];x[:2]=sorted(x[:2]);x[2:5]=sorted(x[2:5])
        if x==wanted:
            pair=sorted(4*(c//4)+suit[c%4] for c in deal[(1-hero)*2:(1-hero)*2+2]);found.append(next(i for i,p in enumerate(doc['pairs']) if p['cards']==pair))
    assert found;return found
def compare_preparation(engine,query,union_prepared,mapping):
    other=engine.prepare(query);a=union_prepared['arrays'];b=other['arrays']
    for key in ('features','actors','legal'):assert np.array_equal(getattr(a,key)[mapping],getattr(b,key))
    for key in ('table','mask','arity'):assert np.array_equal(union_prepared[key][mapping],other[key])
    for i,o in enumerate(query['observations']):
        n=len(o['own_history']);u=int(mapping[i])
        assert np.array_equal(a.valid[u,:n],b.valid[i,:n]) and not a.valid[u,n:].any()
        assert np.array_equal(a.action[u,:n],b.action[i,:n])
        assert np.array_equal(a.prior[u,:n],mapping[b.prior[i,:n]])

def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE));STORE.mkdir();start=time.monotonic();guard()
    oldreg_path=OUT/'river-current-policy-pilot-v1-registration.json';oldreg=read(oldreg_path)
    bank=oldreg['policies'];qpaths=[Path(f'S:/GTOpen-research/board-river-target-learning-v1/selection/deal-{i:03d}-queries.json') for i in range(4)]
    cache_review_path=OUT/'complete-private-allin-cache-v2-independent-review.json';review=read(cache_review_path);assert review['passed']
    source=CONTEXT.read_text();catalog=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');matrix=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    paths=[Path(__file__),PLAN,CONTEXT,oldreg_path,cache_review_path,Path(review['cache_artifact']),catalog,matrix,*qpaths,*EXES.values(),ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml']
    for x in EXES.values():paths.append(ROOT/'crates/solver/examples'/(x.stem+'.rs'))
    paths.extend((ROOT/'crates/solver/src').rglob('*.rs'));paths.extend((ROOT/'crates/solver/examples/research_sampled').glob('*.rs'))
    for b in bank:paths.append(Path(b['folder'])/b['reference']['file'])
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs={str(p):sha(p) for p in paths};verify(inputs)
    save(REG,dict(format=1,inputs=inputs,created_unix=time.time(),policies=bank,deals=[json.loads(read(p)['batch_source'])['deals'][0] for p in qpaths],seeds=[9282901+i for i in range(4)],
        gpu_used=False,training=False,maximum_seconds=900,maximum_added_bytes=LIMIT,maximum_unique_exports=128,cpu_export_workers=4,
        baseline='Existing full-action trace at sampled private cards; actual played generation77 with all policy overrides.',
        overlay='Visited river training rows only; preserve all flop/turn/preflop targets; no ancestor substitution or fitting.'))
    try:
        cache=AllinCache(review['cache_artifact'],review['cache_sha256']);catalog_source=catalog.read_text();mass=AllinMatrix(read(matrix),source).btn_mass
        prior=PhysicalDeals(source,mode='full_deck',seed=0).weights;entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,r)} for r in prior]
        engines=[]
        for b in bank:
            args=dict(catalog_source=catalog_source,matrix_sha256=sha(matrix),entry_mass=mass,root_config=b['root_config'])
            model=model_document(b['folder'],b['reference'],context_source=source,**args);engines.append((model,CPUCurrentPolicy(model,source,**args),args))
        exports={};reports=[];exportdir=STORE/'exports';exportdir.mkdir()
        for did,qp in enumerate(qpaths):
            old=read(qp);assert old['context_source']==source;deal=json.loads(old['batch_source'])['deals'][0]
            for b,(model,engine,args) in zip(bank,engines):
                guard();case=f"d{did:03d}-{b['arm']}";folder=STORE/case;folder.mkdir();timings={}
                batch=cache.batch(dict(format=2,batch_id=NAME+'|'+case,seed=9282901+did,query_limit=10000,deals=[deal]));bp=folder/'batch.json';save(bp,batch)
                rawqp=folder/'queries.json';timings['native_queries']=invoke(EXES['bridge'],['queries',CONTEXT,bp,'-',rawqp],folder/'query-process.json')
                query=read(rawqp);obs=query['observations'];assert len(obs)==len(old['observations'])
                for a,c in zip(obs,old['observations']):assert all(a[k]==c[k] for k in a)
                annotated=dict(query,observations=copy.deepcopy(old['observations']));t=time.perf_counter();prepared=engine.prepare(annotated);timings['baseline_prepare']=time.perf_counter()-t
                t=time.perf_counter();p=engine.infer(prepared);timings['baseline_infer']=time.perf_counter()-t
                t=time.perf_counter();rp,_=reference(annotated,model,device='cpu',**args);timings['baseline_reference_check']=time.perf_counter()-t
                assert np.max(abs(rp-p))<1e-10 and np.array_equal(rp>0,p>0)
                policies=policy_document(query,p);pp=folder/'policies.json';save(pp,policies)
                up=folder/'updates.json';tp=folder/'trace.json'
                timings['native_sampler']=invoke(EXES['bridge'],['verify',CONTEXT,bp,pp,up],folder/'sampler-process.json')
                timings['native_trace']=invoke(EXES['trace'],[CONTEXT,bp,pp,tp],folder/'trace-process.json')
                updates=read(up);trace=read(tp);t=time.perf_counter();existing,witness=replacements(query,updates,policies,trace);timings['baseline_target_validation']=time.perf_counter()-t
                visits=[(i,r) for i,r in enumerate(updates['records']) if r[2]>0 and obs[r[0]]['phase']==3]
                identities=list(dict.fromkeys((obs[r[0]]['hi'],obs[r[0]]['lo']) for i,r in visits));new=[k for k in identities if k not in exports]
                assert len(exports)+len(new)<=128,'Unique export feasibility cap exceeded'
                t=time.perf_counter()
                def export(k):
                    name=f'{k[0]}-{k[1]}';request=exportdir/(name+'-request.json');dest=exportdir/(name+'-export.json')
                    save(request,dict(format=1,hi=k[0],lo=k[1]));wall=invoke(EXES['export'],[CONTEXT,request,dest],exportdir/(name+'-process.json'))
                    return k,dict(path=str(dest),sha256=sha(dest),seconds=wall)
                with ThreadPoolExecutor(max_workers=4) as pool:
                    for offset in range(0,len(new),4):
                        guard();part=new[offset:offset+4];assert used()+len(part)*64_000_000<LIMIT
                        for key,data in pool.map(export,part):exports[key]=data
                timings['extra_export_wall']=time.perf_counter()-t
                docs=[read(exports[k]['path']) for k in identities];t=time.perf_counter()
                for doc in docs:validate_document(doc,source)
                timings['extra_native_validation']=time.perf_counter()-t
                targets={};max_pair_error=0.;max_policy_error=0.;rawrows=sum(len(d['queries']['observations']) for d in docs);unionrows=0;variance=[]
                if docs:
                    t=time.perf_counter();union,mappings=merge_queries([d['queries'] for d in docs],source);timings['extra_union']=time.perf_counter()-t;unionrows=len(union['observations'])
                    t=time.perf_counter();combined=engine.prepare(union);timings['extra_prepare']=time.perf_counter()-t
                    t=time.perf_counter();allp=engine.infer(combined);timings['extra_infer']=time.perf_counter()-t
                    t=time.perf_counter()
                    for doc,mapping in zip(docs,mappings):
                        compare_preparation(engine,doc['queries'],combined,mapping);original,_=reference(doc['queries'],model,device='cpu',**args)
                        e=float(np.max(abs(original-allp[mapping])));max_policy_error=max(max_policy_error,e);assert e<1e-10 and np.array_equal(original>0,allp[mapping]>0)
                    timings['extra_reference_checks']=time.perf_counter()-t
                    t=time.perf_counter();tracemap={x['query']:x for x in trace['traces'][0]['nodes']};kept={}
                    for doc,mapping,key in zip(docs,mappings,identities):
                        probabilities=allp[mapping];exact=evaluate(doc,bundle(doc,probabilities.tolist(),b['policy_id']),entry,expected_policy_id=b['policy_id'],expected_context_source=source)
                        assert exact['supported'],'Actual positive-source sampled visit has no opponent support'
                        qi=next(i for i,o in enumerate(obs) if (o['hi'],o['lo'])==key);actor=obs[qi]['actor'];n=obs[qi]['n']
                        assert abs(entry[actor][tuple(sorted(doc['target']['cards'][:2]))])>0
                        actual=np.asarray(tracemap[qi]['action_values'])[:n,actor]
                        for ix in pair_index(doc,deal):
                            e=float(np.max(abs(actual-np.asarray(exact['pair_action_values'][ix]))));max_pair_error=max(max_pair_error,e);assert e<1e-8
                        targetp=probabilities[doc['target']['query_index']];assert np.max(abs(targetp-p[qi]))<1e-10
                        regret=np.zeros(4);regret[:n]=exact['regrets'];assert abs(p[qi]@regret)<1e-8;targets[key]=regret
                        pairq=np.asarray(exact['pair_action_values']);pairreg=pairq-(pairq@targetp[:n])[:,None];posterior=np.asarray(exact['posterior'])
                        var=float((posterior[:,None]*(pairreg-regret[:n])**2).sum());variance.append(var)
                        kept['p-'+str(qi)]=probabilities
                    timings['extra_values_and_pair_checks']=time.perf_counter()-t
                    buffer=io.BytesIO();np.savez_compressed(buffer,**kept);raw=buffer.getvalue();assert used()+len(raw)<LIMIT
                    with (folder/'conditional-policies.npz').open('xb') as f:f.write(raw)
                    with np.load(folder/'conditional-policies.npz',allow_pickle=False) as z:
                        for key,value in kept.items():assert np.array_equal(z[key],value)
                overlay={i:value.copy() for i,value in existing.items()};changed=[]
                for i,r in visits:
                    qi=r[0];key=(obs[qi]['hi'],obs[qi]['lo']);overlay[i]=targets[key].copy()
                    changed.append(dict(record=i,query=qi,updater=r[1],advantages=overlay[i].tolist(),previous=existing[i].tolist()))
                assert list(overlay)==list(existing)
                riverids={i for i,r in visits}
                for i in existing:
                    if i not in riverids:assert np.array_equal(existing[i],overlay[i])
                save(folder/'river-overlay.json',dict(policy_id=b['policy_id'],queries_sha256=sha(rawqp),policies_sha256=sha(pp),updates_sha256=sha(up),trace_sha256=sha(tp),
                    rows=changed,unchanged_other_postflop_rows=len(existing)-len(visits),preflop_overrides_untouched=True,source_weights_applied=False))
                baseline=sum(timings.get(k,0.) for k in ('native_queries','baseline_prepare','baseline_infer','native_sampler','native_trace','baseline_target_validation'))
                extra=sum(v for k,v in timings.items() if k.startswith('extra_') and k not in ('extra_reference_checks','extra_native_validation'))
                report=dict(case=case,deal_index=did,policy_id=b['policy_id'],positive_records=sum(r[2]>0 for r in updates['records']),postflop_records=len(existing),river_records=len(visits),
                    unique_river_keys=len(identities),new_exports=len(new),raw_conditional_query_rows=rawrows,union_query_rows=unionrows,
                    unchanged_other_postflop_rows=len(existing)-len(visits),maximum_pair_action_error=max_pair_error,maximum_policy_error=max_policy_error,
                    remaining_private_hand_variance_sum=variance,timings=timings,baseline_stage_seconds=baseline,extra_stage_seconds=extra,
                    cost_ratio=(baseline+extra)/baseline,artifacts={str(f.relative_to(folder)):sha(f) for f in folder.iterdir() if f.is_file()})
                save(folder/'result.json',report);reports.append(report)
                print(json.dumps(dict(case=case,river_visits=len(visits),union_rows=unionrows,cost_ratio=report['cost_ratio'])),flush=True)
                assert time.monotonic()-start<900
        verify(inputs);guard();save(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,exports=[dict(key=list(k),**v) for k,v in exports.items()],
            seconds=time.monotonic()-start,gpu_used=False,training=False,production_modified=False,bytes_before_result=used(),
            scope='Visited river-only training target overlay under actual policies. Existing action-integrated flop/turn targets and preflop overrides preserved. CPU cost, no quality or convergence claim.'))
        print(json.dumps(dict(passed=True,cases=len(reports),exports=len(exports),seconds=time.monotonic()-start)),flush=True)
    except Exception as e:save(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
