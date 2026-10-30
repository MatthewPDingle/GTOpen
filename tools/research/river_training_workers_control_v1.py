"""Real spawned-worker parity, ordered insertion, and unchanged root integration."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import ast,copy,hashlib,json,shutil,sys,time,traceback
from pathlib import Path
import numpy as np
import psutil
import river_training_workers_v1 as workers
from river_weighted_overlay_ingest_v1 import ingest,digest
from weighted_training_workers_v1 import CollectedVisits
from weighted_later_action_ingest_v1 import ingest as baseline
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir,ARRAYS
from weighted_deal_binding_v1 import DealWeightGeneration
from board_training_checkpoint_v1 import model_document
from board_training_policy_v1 import probabilities
from preflop_allin_matrix_v1 import AllinMatrix
from exact_initial_training_ingest_v2 import InitialTargets
from sampled_allin_protocol_v3 import AllinCache
from bounded_parallel_evaluation_archive_v2 import production_available
from sampled_physical_root_evaluation_v1 import save

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-training-workers-control-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
CONTEXT=OUT/'bb-context-candidate.json';LIMIT=40_000_000
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def guard():
    assert production_available() and psutil.virtual_memory().available>24_000_000_000
    assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<LIMIT
def same_events(a,b):
    assert len(a)==len(b)
    for x,y in zip(a,b):
        assert x[0]==y[0] and x[2:]==y[2:]
        for c,d in zip(x[1],y[1]):assert np.array_equal(c,d)
def same_reservoir(a,b):
    assert a.seen==b.seen and a.rng.bit_generator.state==b.rng.bit_generator.state
    for k in ARRAYS:assert np.array_equal(getattr(a,k),getattr(b,k)),k
def fingerprint(rs):
    return [(r.seen,copy.deepcopy(r.rng.bit_generator.state),{k:hashlib.sha256(getattr(r,k).tobytes()).hexdigest() for k in ARRAYS}) for r in rs]

def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE));STORE.mkdir();began=time.monotonic();guard()
    prior=OUT/'river-weighted-overlay-control-v2';pr=OUT/'river-weighted-overlay-control-v2-registration.json';pe=OUT/'river-weighted-overlay-control-v2-result.json'
    reg,result=read(pr),read(pe);assert result['passed'] and result['registration_sha256']==sha(pr)
    reviewpath=OUT/'complete-private-allin-cache-v2-independent-review.json';review=read(reviewpath);assert review['passed']
    exe=ROOT/'target/release/examples';bridge=exe/'hu_sampled_allin_bridge_v3.exe';trace=exe/'hu_sampled_action_trace_v2.exe';integrator=exe/'hu_sampled_profile_allin_evaluation_v1.exe';river=exe/'hu_river_two_stage_stream_v1.exe'
    paths=[Path(__file__),OUT/'RIVER-TRAINING-INTEGRATION-PLAN.md',pr,pe,reviewpath,bridge,trace,integrator,river,ROOT/'tools/research/river_training_pipeline_v1.py',prior/'source-generation.json']
    inputs=dict(reg['inputs'])
    for case in result['cases']:
        for name,h in case['artifacts'].items():
            p=prior/case['case']/name;assert sha(p)==h;paths.append(p)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs.update({str(p):sha(p) for p in paths})
    for p,h in inputs.items():assert sha(p)==h,p
    save(REG,dict(format=1,inputs=inputs,maximum_bytes=LIMIT,maximum_seconds=360,workers=2,training=False,gpu_used=False,
                  cases=[c['case'] for c in result['cases']],scope='Worker integration only; no fitting or new quality data.'))
    try:
        source=CONTEXT.read_text();generation=DealWeightGeneration(read(prior/'source-generation.json'),source)
        cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        matrix=AllinMatrix(read(mp),source);catalog=read(cp);cache=AllinCache(review['cache_artifact'],review['cache_sha256']);reports=[];pids=set();negatives=[]
        for bank in reg['policies']:
            args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=matrix.btn_mass,root_config=bank['root_config'])
            model=model_document(bank['folder'],bank['reference'],context_source=source,**args)
            modelraw=(Path(bank['folder'])/bank['reference']['file']).read_text();policyid=hashlib.sha256(modelraw.encode()).hexdigest()
            catalogq=dict(context_source=source,observations=[r['observation'] for r in catalog['native_observations']])
            initial,_=probabilities(catalogq,model,device='cpu',**args);root=np.zeros((169,4));calls=np.zeros(169)
            for item,row in zip(catalog['native_observations'],initial):
                if item['player']==0:root[item['hand_class']]=row
                else:calls[item['hand_class']]=row[1]
            targets=InitialTargets(mp.read_text(),source,root,calls,matrix_sha256=sha(mp),generation=77)
            options=dict(context_path=CONTEXT,cache=cache,targets=targets,generation=generation,iteration=78,executable=bridge,
                trace_executable=trace,integration_executable=integrator,river_executable=river,
                river_payload=dict(model_source=modelraw,policy_id=policyid,model_args=args))
            cases=[c for c in result['cases'] if c['case'].endswith(bank['arm'])];tasks=[]
            for case in cases:
                folder=STORE/case['case'];folder.mkdir()
                for mode in ('serial','parallel'):
                    part=folder/mode;part.mkdir()
                    for n in ('batch.json','queries.json','policies.json'):shutil.copyfile(prior/case['case']/n,part/n)
                tasks.append((case,folder))
            workers.initialize(**options)
            with workers.pool(2,**options) as executor:
                futures=[executor.submit(workers.complete,str(f/'parallel'),c['source_offset']) for c,f in tasks]
                serial=[workers.complete(str(f/'serial'),c['source_offset']) for c,f in tasks]
                parallel=[f.result(timeout=120) for f in futures]
            real=[WeightedPhysicalReservoir(7,p,92828401+p,source) for p in (0,1)]
            oracle=[WeightedPhysicalReservoir(7,p,92828401+p,source) for p in (0,1)]
            for (case,folder),a,b in zip(tasks,serial,parallel):
                guard();same_events(a['events'],b['events']);assert a['counts']==b['counts'] and a['binding']==b['binding']
                assert a['integrated']==b['integrated'] and a['river']==b['river'];pids.add(b['pid'])
                original=prior/case['case'];q=read(original/'queries.json');u=read(original/'updates.json');p=read(original/'policies.json');t=read(original/'trace.json')
                ev=[];receivers=[CollectedVisits(i,source,ev) for i in (0,1)]
                _,initial,later,weighted=baseline(q,u,p,receivers,78,cache,targets,t,generation=generation,start=case['source_offset'],guard=guard)
                for label,want in [('derived-targets',initial),('postflop-targets',later),('weighted-targets',weighted)]:assert read(folder/'parallel'/(label+'.json'))==want
                overlay=read(folder/'parallel/conditional/overlay.json');evidence=read(folder/'parallel/conditional/evidence.json')
                ingest(q,u,p,oracle,78,cache,targets,t,generation=generation,start=case['source_offset'],overlay=overlay,
                       expected_policy_id=policyid,expected_evidence_sha256=digest(evidence),guard=guard)
                before=fingerprint(real)
                for label,changed,offset,it in [('wrong-order',b,case['source_offset']+1,78),('wrong-iteration',b,case['source_offset'],79),('wrong-count',dict(b,counts=[-1,-1]),case['source_offset'],78)]:
                    try:workers.commit(changed,real,expected_start=offset,iteration=it)
                    except ValueError:pass
                    else:raise AssertionError(label)
                    assert fingerprint(real)==before
                    if label not in negatives:negatives.append(label)
                workers.commit(b,real,expected_start=case['source_offset'],iteration=78)
                for x,y in zip(real,oracle):same_reservoir(x,y)
                item=dict(case=case['case'],counts=b['counts'],river=b['river'],serial_seconds=a['seconds'],parallel_worker_seconds=b['seconds'],
                          worker_pid=b['pid'],worker_rss=b['rss_bytes'],all_events_equal=True,root_integration_equal=True,ordered_reservoir_equal=True,
                          artifacts={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()})
                save(folder/'result.json',item);reports.append(item)
                print(json.dumps(dict(case=case['case'],passed=True)),flush=True)
            for label,key,value in [('wrong-model-digest','policy_id','0'*64),('wrong-generation','iteration',79)]:
                bad=copy.deepcopy(options)
                if key=='iteration':bad[key]=value
                else:bad['river_payload'][key]=value
                try:workers.initialize(**bad)
                except ValueError:pass
                else:raise AssertionError(label)
                if label not in negatives:negatives.append(label)
        assert len(pids)>=2 and sum(sum(c['counts']) for c in reports)==131
        # Only the worker/target plumbing changes; comparison runner must still exercise both fits and full checkpoint publication.
        for p,h in inputs.items():assert sha(p)==h,p
        guard();assert time.monotonic()-began<360
        save(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,negative_controls=negatives,worker_pids=sorted(pids),
                         seconds=time.monotonic()-began,training=False,gpu_used=False,production_modified=False,
                         scope='Spawned CPU target/commit integration passed. Full GPU fit/publication comparison remains to run.'))
        print(json.dumps(dict(passed=True,cases=len(reports),workers=len(pids))),flush=True)
    except BaseException as error:save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),seconds=time.monotonic()-began));raise
if __name__=='__main__':main()
