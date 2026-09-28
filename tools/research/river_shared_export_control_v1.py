"""Paired native transport/value batching qualification on frozen actual-policy cases."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy,hashlib,io,json,subprocess,sys,time,traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import psutil
from river_policy_batch_v1 import CPUCurrentPolicy,merge_queries
from river_shared_values_v1 import evaluate_many
from river_full_action_math_v1 import evaluate,validate_document
from river_full_action_control_v1 import bundle
from board_training_checkpoint_v1 import model_document
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-shared-export-control-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
PRIOR=OUT/'river-learned-batch-cost-v1';CONTEXT=OUT/'bb-context-candidate.json';PLAN=OUT/'RIVER-SHARED-EXPORT-PLAN.md'
OLD=ROOT/'target/release/examples/hu_river_action_queries_v1.exe';NEW=ROOT/'target/release/examples/hu_river_action_queries_batch_v1.exe'
LIMIT=512_000_000
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def size():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
def save(p,x):
    raw=(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();assert size()+len(raw)<LIMIT
    with Path(p).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def guard():
    assert production_available() and psutil.virtual_memory().available>24_000_000_000
    assert psutil.Process().memory_info().rss<16_000_000_000 and size()<LIMIT
def invoke(exe,request,dest,log):
    t=time.perf_counter();p=subprocess.run([str(exe),str(CONTEXT),str(request),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    save(log,dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr,seconds=time.perf_counter()-t));assert p.returncode==0,p.stderr
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p
def timepart(times,label,fn):
    t=time.perf_counter();result=fn();times[label]=time.perf_counter()-t;return result

def run_old(folder,requests,engine,entry,policy_id,source):
    folder.mkdir();times={};start=time.perf_counter()
    def export(item):
        i,r=item;rp=folder/f'{i:02d}-request.json';dest=folder/f'{i:02d}-export.json';save(rp,r);invoke(OLD,rp,dest,folder/f'{i:02d}-process.json');return read(dest)
    def all_exports():
        result=[]
        with ThreadPoolExecutor(max_workers=4) as pool:
            offset=0
            while offset<len(requests):
                workers=min(4,(LIMIT-size()-1_000_000)//64_000_000);assert workers>=1
                part=list(enumerate(requests))[offset:offset+workers]
                result.extend(pool.map(export,part));offset+=len(part)
        return result
    docs=timepart(times,'export_and_parse',all_exports)
    union,mapping=timepart(times,'union',lambda:merge_queries([d['queries'] for d in docs],source))
    prepared=timepart(times,'prepare',lambda:engine.prepare(union));p=timepart(times,'infer',lambda:engine.infer(prepared))
    def values():return [evaluate(d,bundle(d,p[m].tolist(),policy_id),entry,expected_policy_id=policy_id,expected_context_source=source) for d,m in zip(docs,mapping)]
    result=timepart(times,'values',values);times['total']=time.perf_counter()-start
    return dict(docs=docs,query=union,mapping=mapping,p=p,values=result,times=times)

def run_new(folder,requests,engine,entry,policy_id,source):
    folder.mkdir();times={};start=time.perf_counter()
    def export():
        assert size()+64_000_000<LIMIT;rp=folder/'request.json';dest=folder/'export.json';save(rp,dict(format=1,targets=requests));invoke(NEW,rp,dest,folder/'process.json');return read(dest)
    batch=timepart(times,'export_and_parse',export);assert batch['context_source']==source and batch['format']==2
    prepared=timepart(times,'prepare',lambda:engine.prepare(batch['queries']));p=timepart(times,'infer',lambda:engine.infer(prepared))
    result=timepart(times,'values',lambda:evaluate_many(batch,bundle(batch,p.tolist(),policy_id),entry,expected_policy_id=policy_id,expected_context_source=source));times['total']=time.perf_counter()-start
    return dict(batch=batch,query=batch['queries'],p=p,values=result,times=times)

def equivalence(old,new,requests,prior_folder):
    batch=new['batch'];assert len(old['docs'])==len(batch['targets'])==len(requests);obs=batch['queries']['observations']
    lookup={(o['hi'],o['lo']):i for i,o in enumerate(obs)};assert len(lookup)==len(obs);allkeys=set();maxp=maxv=0.
    original_queries=read(prior_folder/'queries.json')['observations'];original_lookup={(o['hi'],o['lo']):i for i,o in enumerate(original_queries)}
    overlay=read(prior_folder/'river-overlay.json');oldregrets={r['query']:r['advantages'] for r in overlay['rows']}
    with np.load(prior_folder/'conditional-policies.npz',allow_pickle=False) as retained:
        for i,(doc,got,request,mapping,a,b) in enumerate(zip(old['docs'],batch['targets'],requests,old['mapping'],old['values'],new['values'])):
            key=(request['hi'],request['lo']);assert (got['target']['hi'],got['target']['lo'])==key
            refobs=doc['queries']['observations'];ids=np.array([lookup[(o['hi'],o['lo'])] for o in refobs]);reverse={int(g):j for j,g in enumerate(ids)}
            for j,o in enumerate(refobs):
                allkeys.add((o['hi'],o['lo']));x=copy.deepcopy(o);x['own_history']=[[int(ids[k]),action,n] for k,action,n in o['own_history']];assert x==obs[int(ids[j])]
            restored=copy.deepcopy(got);restored['target']['query_index']=reverse[restored['target']['query_index']]
            for pair in restored['pairs']:pair['path']=[[reverse[q],action,n] for q,action,n in pair['path']]
            for node in restored['nodes']:
                if node['kind']=='decision':node['query_index']=reverse[node['query_index']]
            for k in ('target','geometry','pairs','nodes','counts_loss_tie_win'):assert restored[k]==doc[k],k
            restored.update(context_source=source,request_source=doc['request_source'],queries=doc['queries'])
            validate_document(restored,source)
            qid=original_lookup[key];targetp=new['p'][ids];original=retained['p-'+str(qid)]
            for p in (old['p'][mapping],original):
                error=float(np.max(abs(targetp-p)));maxp=max(maxp,error);assert error<1e-10 and np.array_equal(targetp>0,p>0)
            assert a['supported']==b['supported']
            for k in ('opponent_mass','own_history_likelihood','pair_action_values'):
                error=float(np.max(abs(np.asarray(a[k])-np.asarray(b[k]))));maxv=max(maxv,error);assert error<1e-8
            if a['supported']:
                for k in ('posterior','action_values','value','regrets'):
                    error=float(np.max(abs(np.asarray(a[k])-np.asarray(b[k]))));maxv=max(maxv,error);assert error<1e-8
                assert np.max(abs(np.asarray(oldregrets[qid])[:got['target']['n']]-b['regrets']))<1e-8
    assert allkeys==set(lookup);return dict(maximum_policy_error=maxp,maximum_value_error=maxv,identical_native_structure=True,union_rows=len(obs))

def main():
    global source
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE));STORE.mkdir();start=time.monotonic();guard()
    prior_reg=OUT/'river-learned-batch-cost-v1-registration.json';prior_result=OUT/'river-learned-batch-cost-v1-result.json'
    reg=read(prior_reg);pilot=read(prior_result);assert pilot['passed'] and pilot['complete'] and pilot['registration_sha256']==sha(prior_reg);verify(reg['inputs'])
    inputs=dict(reg['inputs']);paths=[Path(__file__),PLAN,NEW,OLD,ROOT/'crates/solver/examples/hu_river_action_queries_batch_v1.rs',prior_reg,prior_result]
    for case in pilot['cases']:
        for file,h in case['artifacts'].items():
            p=PRIOR/case['case']/file;assert sha(p)==h;paths.append(p)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs.update({str(p):sha(p) for p in paths});verify(inputs)
    save(REG,dict(format=1,created_unix=time.time(),inputs=inputs,cases=[c['case'] for c in pilot['cases']],order='old/new on even indices, new/old on odd indices',maximum_seconds=900,maximum_bytes=LIMIT,gpu_used=False,training=False))
    try:
        source=CONTEXT.read_text();cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        entry_mass=AllinMatrix(read(mp),source).btn_mass;weights=PhysicalDeals(source,mode='full_deck',seed=0).weights;entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,r)} for r in weights]
        engines={}
        for b in reg['policies']:
            args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=entry_mass,root_config=b['root_config'])
            model=model_document(b['folder'],b['reference'],context_source=source,**args);engines[b['policy_id']]=CPUCurrentPolicy(model,source,**args)
        reports=[];first_request=None
        for i,case in enumerate(pilot['cases']):
            guard();original=PRIOR/case['case'];folder=STORE/case['case'];folder.mkdir()
            q=read(original/'queries.json');updates=read(original/'updates.json');obs=q['observations']
            keys=list(dict.fromkeys((obs[r[0]]['hi'],obs[r[0]]['lo']) for r in updates['records'] if r[2]>0 and obs[r[0]]['phase']==3));assert keys
            requests=[dict(format=1,hi=k[0],lo=k[1]) for k in keys];engine=engines[case['policy_id']]
            if first_request is None:first_request=requests
            run={}
            for name in (('old','new') if i%2==0 else ('new','old')):
                run[name]=(run_old if name=='old' else run_new)(folder/name,requests,engine,entry,case['policy_id'],source)
            before=time.perf_counter();checks=equivalence(run['old'],run['new'],requests,original);check_seconds=time.perf_counter()-before
            report=dict(case=case['case'],targets=len(requests),old=run['old']['times'],new=run['new']['times'],speedup=run['old']['times']['total']/run['new']['times']['total'],qualification_seconds=check_seconds,**checks)
            save(folder/'result.json',report);reports.append(report);print(json.dumps(dict(case=case['case'],targets=len(requests),speedup=report['speedup'])),flush=True)
            del run;assert time.monotonic()-start<900
        negatives=[]
        first_query=read(PRIOR/pilot['cases'][0]['case']/'queries.json')['observations'][0]
        bad=[('empty',dict(format=1,targets=[])),('duplicate',dict(format=1,targets=[first_request[0]]*2)),('too-many',dict(format=1,targets=[first_request[0]]*33)),
            ('format',dict(format=9,targets=first_request)),('not-river',dict(format=1,targets=[dict(format=1,hi=first_query['hi'],lo=first_query['lo'])]))]
        for name,data in bad:
            rp=STORE/('bad-'+name+'.json');dest=STORE/('bad-'+name+'-output.json');save(rp,data)
            p=subprocess.run([str(NEW),str(CONTEXT),str(rp),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
            save(STORE/('bad-'+name+'-process.json'),dict(code=p.returncode,stderr=p.stderr));assert p.returncode!=0 and not dest.exists();negatives.append(dict(case=name,rejected=True))
        verify(inputs);guard();oldsum=sum(x['old']['total'] for x in reports);newsum=sum(x['new']['total'] for x in reports)
        save(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,negative_controls=negatives,old_seconds=oldsum,new_seconds=newsum,speedup=oldsum/newsum,seconds=time.monotonic()-start,
            retained_bytes_before_result=size(),gpu_used=False,production_modified=False,training=False,scope='Paired transport/preparation/conditional-value cost only; not overall training or convergence speed.'))
        print(json.dumps(dict(passed=True,speedup=oldsum/newsum,seconds=time.monotonic()-start)),flush=True)
    except Exception as e:save(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
