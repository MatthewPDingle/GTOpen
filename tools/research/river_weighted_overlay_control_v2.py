"""Fresh valid source slices through actual weighted river-overlay insertion."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy,hashlib,json,subprocess,sys,time,traceback
from pathlib import Path
import numpy as np
import psutil
from river_weighted_overlay_ingest_v1 import ingest
from river_training_overlay_targets_v1 import generate
from weighted_later_action_ingest_v1 import ingest as baseline
from weighted_training_workers_v1 import CollectedVisits
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir,ARRAYS
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_deal_binding_v1 import DealWeightGeneration
from board_training_checkpoint_v1 import model_document
from board_training_policy_v1 import probabilities
from later_action_training_v1 import first_action_view
from river_policy_batch_v1 import CPUCurrentPolicy
from exact_initial_training_ingest_v2 import InitialTargets,digest
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import AllinCache,policy_document
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-weighted-overlay-control-v2';FIXTURE='river-weighted-overlay-control-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
CONTEXT=OUT/'bb-context-candidate.json';PLAN=OUT/'RIVER-WEIGHTED-OVERLAY-V2-PLAN.md';LIMIT=512_000_000
BRIDGE=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe';TRACE=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
NATIVE=ROOT/'target/release/examples/hu_river_two_stage_v1.exe'

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def used():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
def save(p,x):
    raw=(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();assert used()+len(raw)<LIMIT
    with Path(p).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def guard():
    assert production_available() and psutil.virtual_memory().available>24_000_000_000
    assert psutil.Process().memory_info().rss<16_000_000_000 and used()+64_000_000<LIMIT
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p
def invoke(exe,args,log):
    guard();p=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    save(log,dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
def fingerprint(reservoirs):
    return [(r.seen,copy.deepcopy(r.rng.bit_generator.state),{k:hashlib.sha256(getattr(r,k).tobytes()).hexdigest() for k in ARRAYS}) for r in reservoirs]
def new_reservoirs(source):return [WeightedPhysicalReservoir(7,p,92828401+p,source) for p in (0,1)]
def same(a,b,*,values=True):
    assert a.seen==b.seen and a.rng.bit_generator.state==b.rng.bit_generator.state
    for key in ARRAYS:
        if key!='values' or values:assert np.array_equal(getattr(a,key),getattr(b,key)),key

def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE));STORE.mkdir();start=time.monotonic();guard()
    upstream=OUT/'river-posterior64-native-control-v1-registration.json';prior=read(upstream);inputs=dict(prior['inputs']);verify(inputs)
    bankpath=OUT/'river-learned-batch-cost-v1-registration.json';bank=read(bankpath)['policies']
    reviewpath=OUT/'complete-private-allin-cache-v2-independent-review.json';review=read(reviewpath);assert review['passed']
    paths=[Path(__file__),PLAN,OUT/'RIVER-WEIGHTED-OVERLAY-PLAN.md',OUT/'river-weighted-overlay-control-v1-registration.json',OUT/'river-weighted-overlay-control-v1-failure.json',CONTEXT,BRIDGE,TRACE,NATIVE,bankpath,upstream,reviewpath,Path(review['cache_artifact'])]
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs.update({str(p):sha(p) for p in paths});verify(inputs)
    save(REG,dict(format=1,inputs=inputs,source_deals=384,source_seed=92828201,source_offsets=[0,1,2,3],
        native_action_seed_base=92828301,reservoir_capacity=7,reservoir_seed_base=92828401,maximum_seconds=300,maximum_bytes=LIMIT,
        policies=bank,K=64,reservoir_lifetime='Continuous across the four source slices, separate per model',fixture_identity=FIXTURE,gpu_used=False,training=False))
    try:
        source=CONTEXT.read_text();cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        catalog=read(cp);matrix_source=mp.read_text();matrix=AllinMatrix(read(mp),source);response_hi=json.loads(source)['nodes'][0]['children'][3]+1
        sample=ClassStratifiedDeals(source,seed=92828201).sample(384);generation=DealWeightGeneration(sample,source);save(STORE/'source-generation.json',sample)
        cache=AllinCache(review['cache_artifact'],review['cache_sha256']);models=[]
        weights=PhysicalDeals(source,mode='full_deck',seed=0).weights;entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,r)} for r in weights]
        for b in bank:
            args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=matrix.btn_mass,root_config=b['root_config'])
            model=model_document(b['folder'],b['reference'],context_source=source,**args);assert model['generation']==77
            catalogq=dict(context_source=source,observations=[r['observation'] for r in catalog['native_observations']])
            initial,_=probabilities(catalogq,model,device='cpu',**args);root=np.zeros((169,4));calls=np.zeros(169)
            for item,row in zip(catalog['native_observations'],initial):
                if item['player']==0:root[item['hand_class']]=row
                else:calls[item['hand_class']]=row[1]
            targets=InitialTargets(matrix_source,source,root,calls,matrix_sha256=sha(mp),generation=77)
            models.append((b,model,args,targets,CPUCurrentPolicy(model,source,**args)))
        reports=[];negative_names=[];padding_tested=False;other_negatives=False;overflow=[0,0]
        persistent={b['policy_id']:(new_reservoirs(source),new_reservoirs(source),new_reservoirs(source)) for b in bank}
        for offset in range(4):
            for b,model,args,targets,engine in models:
                guard();case=f"d{offset:03d}-{b['arm']}";folder=STORE/case;folder.mkdir();began=time.perf_counter()
                batch=cache.batch(dict(format=2,batch_id=FIXTURE+'|'+case,seed=92828301+offset,query_limit=10000,deals=[sample['deals'][offset]]))
                bp=folder/'batch.json';qp=folder/'queries.json';pp=folder/'policies.json';up=folder/'updates.json';tp=folder/'trace.json';save(bp,batch)
                invoke(BRIDGE,['queries',CONTEXT,bp,'-',qp],folder/'queries-process.json');query=read(qp)
                p,_=probabilities(first_action_view(query,response_hi),model,device='cpu',**args);policies=policy_document(query,p);save(pp,policies)
                invoke(BRIDGE,['verify',CONTEXT,bp,pp,up],folder/'updates-process.json');invoke(TRACE,[CONTEXT,bp,pp,tp],folder/'trace-process.json')
                updates=read(up);trace=read(tp)
                before=time.perf_counter();overlay,evidence=generate(query,updates,policies,trace,generation=generation,start=offset,iteration=78,
                    policy_id=b['policy_id'],case_id=FIXTURE+'|'+case,engine=engine,entry=entry,executable=NATIVE,context_path=CONTEXT,
                    folder=folder/'conditional',guard=guard,write=save);generation_seconds=time.perf_counter()-before
                events=[];collectors=[CollectedVisits(actor,source,events) for actor in (0,1)]
                baseargs=dict(generation=generation,start=offset,guard=guard)
                counts,initial_audit,later_audit,weight_audit=baseline(query,updates,policies,collectors,78,cache,targets,trace,**baseargs)
                baseline_real,oracle,candidate=persistent[b['policy_id']]
                replacements={r['record']:r for r in overlay['rows']};positives=[(i,r) for i,r in enumerate(updates['records']) if r[2]>0]
                assert len(events)==len(positives);untouched={0:0,1:0,2:0};changed=0
                for (i,record),(actor,row,it,weight) in zip(positives,events):
                    assert weight==generation.weights[offset] and it==78
                    baseline_real[actor]._insert(row,it,deal_weight=weight)
                    if i in replacements:
                        value=np.asarray(replacements[i]['advantages']);changed+=int(not np.array_equal(value,row[3]));row=(*row[:3],value)
                    else:
                        phase=query['observations'][record[0]]['phase'];assert phase in untouched;untouched[phase]+=1
                    oracle[actor]._insert(row,it,deal_weight=weight)
                callargs=dict(**baseargs,overlay=overlay,expected_policy_id=b['policy_id'],expected_evidence_sha256=digest(evidence))
                prior_seen=[r.seen for r in candidate]
                before=time.perf_counter();got=ingest(query,updates,policies,candidate,78,cache,targets,trace,**callargs);insertion_seconds=time.perf_counter()-before
                assert got[0]==counts and got[1:4]==(initial_audit,later_audit,weight_audit)
                for actor in (0,1):
                    same(candidate[actor],oracle[actor]);same(candidate[actor],baseline_real[actor],values=False)
                    overflow[actor]+=max(0,candidate[actor].seen-candidate[actor].capacity)-max(0,prior_seen[actor]-candidate[actor].capacity)
                    path=folder/f'reservoir-{actor}.npz';candidate[actor].save(path)
                    same(WeightedPhysicalReservoir.load(path,source),candidate[actor])
                # Also compare every staged event, including rows dropped by Algorithm R.
                candidate_events=[];candidate_collectors=[CollectedVisits(actor,source,candidate_events) for actor in (0,1)]
                ingest(query,updates,policies,candidate_collectors,78,cache,targets,trace,**callargs)
                for (i,_),old,new in zip(positives,events,candidate_events):
                    assert old[0]==new[0] and old[2:]==new[2:]
                    for a,c in zip(old[1][:3],new[1][:3]):assert np.array_equal(a,c)
                    expected=np.asarray(replacements[i]['advantages']) if i in replacements else old[1][3]
                    assert np.array_equal(new[1][3],expected)
                def reject(name,bad_overlay=None,bad_trace=None,bad_policy_id=None):
                    before=fingerprint(candidate);kw=dict(callargs)
                    if bad_overlay is not None:kw['overlay']=bad_overlay
                    if bad_policy_id is not None:kw['expected_policy_id']=bad_policy_id
                    try:ingest(query,updates,policies,candidate,78,cache,targets,trace if bad_trace is None else bad_trace,**kw)
                    except (ValueError,AssertionError,KeyError,IndexError):pass
                    else:raise AssertionError('Malformed input accepted: '+name)
                    assert fingerprint(candidate)==before;negative_names.append(name)
                if overlay['rows'] and not other_negatives:
                    for field in ('context_sha256','queries_sha256','trace_sha256','source_generation_sha256'):
                        bad=copy.deepcopy(overlay);bad['binding'][field]='0'*64;reject('wrong-'+field,bad)
                    reject('wrong-policy',bad_policy_id='not-current')
                    bad=copy.deepcopy(overlay);bad['evidence_sha256']='0'*64;reject('wrong-evidence',bad)
                    bad=copy.deepcopy(overlay);bad['rows'].append(copy.deepcopy(bad['rows'][0]));reject('duplicate-record',bad)
                    bad=copy.deepcopy(overlay);bad['rows'].pop();reject('missing-record',bad)
                    bad=copy.deepcopy(overlay);bad['rows'][0]['query']+=1;reject('wrong-query-record',bad)
                    bad=copy.deepcopy(overlay);bad['rows'][0]['key'][0]='1';reject('wrong-key',bad)
                    bad=copy.deepcopy(overlay);bad['rows'][0]['advantages'][0]=float('nan');reject('nonfinite-values',bad)
                    bad=copy.deepcopy(overlay);n=query['observations'][bad['rows'][0]['query']]['n']
                    bad['rows'][0]['advantages'][:n]=[v+1 for v in bad['rows'][0]['advantages'][:n]];reject('miscentering',bad)
                    bad=copy.deepcopy(overlay);bad['rows'][0]['opponent_mass']=0.;reject('unsupported-posterior',bad)
                    bad=copy.deepcopy(overlay);bad['rows'][0]['draw_count']=63;reject('wrong-draw-count',bad)
                    broken=copy.deepcopy(trace);broken['sampled_roots'][0][2]+=1
                    bad=copy.deepcopy(overlay);bad['binding']['trace_sha256']=digest(broken)
                    reject('underlying-trace-corruption',bad,bad_trace=broken)
                    if len(overlay['rows'])>1:
                        bad=copy.deepcopy(overlay);bad['rows'][0],bad['rows'][1]=bad['rows'][1],bad['rows'][0];reject('reordered-records',bad)
                    other_negatives=True
                if not padding_tested:
                    for j,r in enumerate(overlay['rows']):
                        n=query['observations'][r['query']]['n']
                        if n<4:
                            bad=copy.deepcopy(overlay);bad['rows'][j]['advantages'][n]=1;reject('illegal-padding',bad);padding_tested=True;break
                save(folder/'ingestion-audit.json',dict(initial=got[1],later=got[2],weighted=got[3],river=got[4]))
                report=dict(case=case,source_offset=offset,source_weight=generation.weights[offset],counts=counts,river_rows=len(overlay['rows']),changed_river_values=changed,
                    untouched_rows=untouched,seen=[r.seen for r in candidate],rng_and_weights_unchanged=True,all_staged_events_checked=len(events),
                    generation_seconds=generation_seconds,insertion_seconds=insertion_seconds,seconds=time.perf_counter()-began,
                    artifacts={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()})
                save(folder/'result.json',report);reports.append(report);print(json.dumps(dict(case=case,rows=sum(counts),rivers=len(overlay['rows']))),flush=True)
                assert time.monotonic()-start<300
        assert other_negatives and padding_tested and all(n>0 for n in overflow)
        verify(inputs);guard();save(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,negative_controls=negative_names,
            overflow_insertions_by_actor=overflow,source_generation_sha256=sha(STORE/'source-generation.json'),seconds=time.monotonic()-start,
            retained_bytes_before_result=used(),gpu_used=False,training=False,production_modified=False,
            scope='Actual weighted insertion on four slices of a new valid stratified TRAIN source, two current policies; no fitted policy or fresh quality evaluation.'))
        print(json.dumps(dict(passed=True,river_rows=sum(c['river_rows'] for c in reports),overflow=overflow,seconds=time.monotonic()-start)),flush=True)
    except Exception as e:save(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise

if __name__=='__main__':main()
