"""Paired full/native two-stage river generation, with exact tree references."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy,hashlib,json,subprocess,sys,time,traceback
from pathlib import Path
import numpy as np
import psutil
from river_posterior64_v1 import posterior,draw
from river_selected_native_values_v1 import evaluate as sampled_evaluate
from river_posterior64_control_v2 import saved_policy,rejected
from river_policy_batch_v1 import CPUCurrentPolicy
from river_shared_values_v1 import evaluate_many
from river_full_action_control_v1 import bundle
from board_training_checkpoint_v1 import model_document
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-posterior64-native-control-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
CONTEXT=OUT/'bb-context-candidate.json';PLAN=OUT/'RIVER-POSTERIOR64-NATIVE-PLAN.md'
FULL=ROOT/'target/release/examples/hu_river_action_queries_batch_v1.exe';NATIVE=ROOT/'target/release/examples/hu_river_two_stage_v1.exe'
LIMIT=384_000_000

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def size():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
def save(p,x):
    raw=(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();assert size()+len(raw)<LIMIT
    with Path(p).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p
def guard():
    assert production_available() and psutil.virtual_memory().available>24_000_000_000
    assert psutil.Process().memory_info().rss<16_000_000_000 and size()<LIMIT
def part(times,key,fn):
    t=time.perf_counter();r=fn();times[key]=time.perf_counter()-t;return r
def export(exe,folder,name,request):
    assert size()+64_000_000<LIMIT
    rp=folder/(name+'-request.json');dest=folder/(name+'-export.json');save(rp,request)
    p=subprocess.run([str(exe),str(CONTEXT),str(rp),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    save(folder/(name+'-process.json'),dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
    return read(dest)

def full_run(folder,requests,engine,entry,identity,source):
    folder.mkdir();start=time.perf_counter();times={}
    batch=part(times,'export_parse',lambda:export(FULL,folder,'full',dict(format=1,targets=requests)))
    p=part(times,'prepare_infer',lambda:engine.infer(engine.prepare(batch['queries'])))
    values=part(times,'values',lambda:evaluate_many(batch,bundle(batch,p.tolist(),identity),entry,expected_policy_id=identity,expected_context_source=source))
    times['total']=time.perf_counter()-start
    return dict(batch=batch,p=p,values=values,times=times)

def sampled_run(folder,requests,engine,entry,identity,case):
    folder.mkdir();start=time.perf_counter();times={}
    history=part(times,'history_export_parse',lambda:export(NATIVE,folder,'history',dict(format=1,mode='history',targets=requests)))
    p1=part(times,'history_prepare_infer',lambda:engine.infer(engine.prepare(history['queries'])))
    def select():
        plans=[];targets=[]
        for doc in history['targets']:
            post,mass,own=posterior(doc,history['queries']['observations'],p1,entry)
            t=doc['target'];name=case+'|'+identity+'|'+t['hi']+'|'+t['lo'];draws=draw(post,name)
            cards=[doc['pairs'][int(i)]['cards'] for i in draws]
            targets.append(dict(format=1,hi=t['hi'],lo=t['lo'],selected_pairs=[list(p) for p in sorted(set(map(tuple,cards)))]))
            plans.append(dict(posterior=post,mass=mass,own=own,draws=draws,cards=cards))
        return plans,targets
    plans,targets=part(times,'posterior_select',select)
    selected=part(times,'selected_export_parse',lambda:export(NATIVE,folder,'selected',dict(format=1,mode='selected',targets=targets)))
    p2=part(times,'selected_prepare_infer',lambda:engine.infer(engine.prepare(selected['queries'])))
    values=part(times,'sample_values',lambda:[sampled_evaluate(d,p2,p['cards']) for d,p in zip(selected['targets'],plans)])
    times['total']=time.perf_counter()-start
    return dict(history=history,p1=p1,selected=selected,p2=p2,plans=plans,values=values,times=times)

def compare_transport(got,full,p,reference):
    assert got['format']==3 and got['mode'] in ('history','selected') and got['context_source']==full['context_source']
    assert got['queries']['context_source']==full['context_source'] and got['queries']['batch_source']==got['request_source']
    assert len(got['targets'])==len(full['targets'])
    old=full['queries']['observations'];lookup={(o['hi'],o['lo']):i for i,o in enumerate(old)}
    rows=got['queries']['observations'];ids=np.array([lookup[(o['hi'],o['lo'])] for o in rows]);assert len(set(ids))==len(ids)
    for i,row in enumerate(rows):
        r=copy.deepcopy(row);r['own_history']=[[int(ids[j]),a,n] for j,a,n in r['own_history']];assert r==old[int(ids[i])]
    err=float(np.max(abs(p-reference[ids])));assert err<1e-10 and np.array_equal(p>0,reference[ids]>0)
    for actual,ref in zip(got['targets'],full['targets']):
        target=dict(actual['target']);target['query_index']=int(ids[target['query_index']]);assert target==ref['target']
        assert actual['geometry']==ref['geometry'];pairs={tuple(p['cards']):p for p in ref['pairs']}
        if got['mode']=='history':assert len(actual['pairs'])==990 and not actual['nodes']
        else:assert 1<=len(actual['pairs'])<=64
        assert len(set(tuple(x['cards']) for x in actual['pairs']))==len(actual['pairs'])
        counts=[0,0,0]
        for pair in actual['pairs']:
            want=pairs[tuple(pair['cards'])];path=[[int(ids[j]),a,n] for j,a,n in pair['path']];assert path==want['path']
            if got['mode']=='history':assert set(pair)=={'cards','path'};continue
            assert pair['outcome_loss_tie_win']==want['outcome_loss_tie_win'];counts[pair['outcome_loss_tie_win']]+=1
            assert pair['root']-pair['node_start']==want['root']-want['node_start']
            offset=want['node_start']-pair['node_start']
            for i in range(pair['node_start'],pair['root']+1):
                node=copy.deepcopy(actual['nodes'][i])
                if node['kind']=='decision':node['query_index']=int(ids[node['query_index']]);node['children']=[c+offset for c in node['children']]
                assert node==ref['nodes'][i+offset]
        assert actual['counts_loss_tie_win']==counts
    return err

def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE));STORE.mkdir();start=time.monotonic();guard()
    prior_reg=OUT/'river-learned-batch-cost-v1-registration.json';prior_result=OUT/'river-learned-batch-cost-v1-result.json'
    check_reg=OUT/'river-posterior64-control-v2-registration.json';check_result=OUT/'river-posterior64-control-v2-result.json'
    reg=read(prior_reg);pilot=read(prior_result);checked=read(check_result);assert checked['passed'] and checked['native_implementation_gate_passed']
    assert checked['registration_sha256']==sha(check_reg);inputs=dict(read(check_reg)['inputs']);verify(inputs)
    paths=[Path(__file__),PLAN,FULL,NATIVE,ROOT/'crates/solver/examples/hu_river_two_stage_v1.rs',check_reg,check_result]
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs.update({str(p):sha(p) for p in paths});verify(inputs)
    save(REG,dict(format=1,inputs=inputs,K=64,cases=[c['case'] for c in pilot['cases']],maximum_seconds=300,maximum_bytes=LIMIT,
                  order='full/new on even indices, new/full on odd indices',gpu_used=False,training=False))
    try:
        source=CONTEXT.read_text();cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        weights=PhysicalDeals(source,mode='full_deck',seed=0).weights;entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,r)} for r in weights]
        mass=AllinMatrix(read(mp),source).btn_mass;engines={}
        for b in reg['policies']:
            args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=mass,root_config=b['root_config'])
            model=model_document(b['folder'],b['reference'],context_source=source,**args);engines[b['policy_id']]=CPUCurrentPolicy(model,source,**args)
        prior=OUT/'river-learned-batch-cost-v1';shared=OUT/'river-shared-export-control-v1';exports={tuple(x['key']):x for x in pilot['exports']}
        reports=[];negatives=[];first_full=first_requests=None
        for index,(case,qualification) in enumerate(zip(pilot['cases'],checked['cases'])):
            guard();assert case['case']==qualification['case'];folder=STORE/case['case'];folder.mkdir()
            reference=read(shared/case['case']/'new/export.json');expectedp=saved_policy(reference,case,prior,exports)
            requests=[dict(format=1,hi=d['target']['hi'],lo=d['target']['lo']) for d in reference['targets']]
            if first_full is None:first_full=reference;first_requests=requests
            run={};engine=engines[case['policy_id']]
            for name in (('full','new') if index%2==0 else ('new','full')):
                if name=='full':run[name]=full_run(folder/name,requests,engine,entry,case['policy_id'],source)
                else:run[name]=sampled_run(folder/name,requests,engine,entry,case['policy_id'],case['case'])
            began=time.perf_counter();old=run['full'];new=run['new']
            assert old['batch']['targets']==reference['targets'] and old['batch']['queries']['observations']==reference['queries']['observations']
            assert np.max(abs(old['p']-expectedp))<1e-10 and np.array_equal(old['p']>0,expectedp>0)
            e1=compare_transport(new['history'],old['batch'],new['p1'],old['p']);e2=compare_transport(new['selected'],old['batch'],new['p2'],old['p'])
            errors=[]
            for j,(ref,plan,value,got,qtest) in enumerate(zip(old['values'],new['plans'],new['values'],new['selected']['targets'],qualification['target_results'])):
                assert np.max(abs(plan['posterior']-ref['posterior']))<1e-12 and plan['draws'].tolist()==qtest['draws']
                assert abs(plan['mass']-ref['opponent_mass'])<1e-10 and abs(plan['own']-ref['own_history_likelihood'])<1e-12
                pairmap={tuple(pair['cards']):i for i,pair in enumerate(old['batch']['targets'][j]['pairs'])}
                for cards,v in value['pair_values'].items():assert np.max(abs(np.asarray(v)-ref['pair_action_values'][pairmap[cards]]))<1e-8
                err=float(np.max(abs(value['regrets']-qtest['sampled_regrets'])));assert err<1e-8;errors.append(err)
            if index==0:
                d=new['selected']['targets'][0];cards=new['plans'][0]['cards'];p=new['p2']
                assert rejected(lambda:sampled_evaluate(d,p,cards[:-1]))
                assert rejected(lambda:sampled_evaluate(d,np.full(p.shape,np.nan),cards))
                badcards=copy.deepcopy(cards);badcards[0]=d['target']['cards'][:2]
                assert rejected(lambda:sampled_evaluate(d,p,badcards))
                every=[pair['cards'] for pair in d['pairs']]
                repeated=every+[every[0]]*(64-len(every))
                repeat_result=sampled_evaluate(d,p,repeated)
                pair_vectors=new['values'][0]['pair_values']
                expected=np.mean([pair_vectors[tuple(c)] for c in repeated],axis=0)
                assert np.max(abs(repeat_result['action_values']-expected))<1e-8
                negatives.extend(['wrong-draw-count','missing-policy','wrong-draw-set'])
            report=dict(case=case['case'],targets=len(requests),full=old['times'],new=new['times'],speedup=old['times']['total']/new['times']['total'],
                full_queries=len(old['p']),history_queries=len(new['p1']),selected_queries=len(new['p2']),maximum_policy_error=max(e1,e2),
                maximum_sampled_regret_error=max(errors),qualification_seconds=time.perf_counter()-began,
                artifacts={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()})
            save(folder/'result.json',report);reports.append(report);print(json.dumps(dict(case=case['case'],speedup=report['speedup'])),flush=True)
            del run;assert time.monotonic()-start<300
        target=first_requests[0];pairs=[p['cards'] for p in first_full['targets'][0]['pairs']];blocked=sorted(first_full['targets'][0]['target']['cards'][:2])
        one=lambda selected:dict(format=1,mode='selected',targets=[dict(target,selected_pairs=selected)])
        bad=[('unknown-mode',dict(format=1,mode='other',targets=[target])),('history-selection',dict(format=1,mode='history',targets=[dict(target,selected_pairs=pairs[:1])])),
             ('missing-selection',dict(format=1,mode='selected',targets=[target])),('empty-selection',one([])),('oversized-selection',one(pairs[:65])),
             ('duplicate-pair',one([pairs[0],pairs[0]])),('unsorted-pairs',one([pairs[1],pairs[0]])),('blocked-pair',one([blocked])),
             ('repeated-card',one([[0,0]])),('invalid-card',one([[0,52]])),('duplicate-target',dict(format=1,mode='history',targets=[target,target]))]
        for name,request in bad:
            rp=STORE/('bad-'+name+'.json');dest=STORE/('bad-'+name+'-output.json');save(rp,request)
            proc=subprocess.run([str(NATIVE),str(CONTEXT),str(rp),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
            save(STORE/('bad-'+name+'-process.json'),dict(code=proc.returncode,stderr=proc.stderr));assert proc.returncode!=0 and not dest.exists();negatives.append(name)
        verify(inputs);guard();fulltime=sum(c['full']['total'] for c in reports);newtime=sum(c['new']['total'] for c in reports)
        save(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,negative_controls=negatives,
            full_seconds=fulltime,new_seconds=newtime,speedup=fulltime/newtime,seconds=time.monotonic()-start,retained_bytes_before_result=size(),multiplicity_control_passed=True,
            gpu_used=False,training=False,production_modified=False,scope='Paired real generation cost versus exhaustive averaging on reused TRAIN cases; not time-to-quality or production performance.'))
        print(json.dumps(dict(passed=True,speedup=fulltime/newtime,seconds=time.monotonic()-start)),flush=True)
    except Exception as e:save(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise

if __name__=='__main__':main()
