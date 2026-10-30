"""Resumable exact conditional labels; CPU prefetch/archive overlap GPU teachers."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import argparse
import io
import json
from pathlib import Path
import subprocess
import time
import traceback
import uuid
import numpy as np
import psutil
from board_river_deal_coverage_common_v1 import *
from board_river_target_archive_v1 import pack,read_archive,MEMBERS
from board_prefix_publication_v1 import atomic_json
from board_river_bounds_pilot_support_v2 import Guard as BaseGuard,inputs as bank_inputs,load
from board_later_fit_holdout_train_v1 import configure
from board_river_opponent_reach_math_v1 import posterior
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_visible_hybrid_gpu_bank_bulk_v1 import prepare_tables
from bounded_parallel_evaluation_archive_v2 import production_available
from global_research_inventory_v2 import measure as global_measure
from board_study_storage_v1 import measure

SELECTION=OUT/(PREFIX+'-selection.json')
REG=OUT/(PREFIX+'-collection-registration.json')
RESULT=OUT/(PREFIX+'-collection.json')
CONTROL=OUT/(PREFIX+'-archive-control.json')


def status(value):atomic_json(OUT/(PREFIX+'-status.json'),value,replace=True)


def sources():
    paths,qualified=bank_inputs();selection=read(SELECTION)
    assert selection['passed'] and selection['complete'];verify(selection['inputs']);paths.update(selection['inputs'])
    paths.update({str(p):sha(p) for p in (SELECTION,Path(__file__),ROOT/'tools/research/board_river_target_archive_v1.py',
        ROOT/'tools/research/board_river_deal_coverage_common_v1.py',ROOT/'tools/research/board_river_opponent_reach_math_v1.py',PLAN,EXE,
        OUT/'board-river-opponent-reach-v1-attribution.json')})
    return paths,qualified,selection


class Guard(BaseGuard):
    def __init__(self):super().__init__(limit=7200);self.last_local=0
    def __call__(self):
        super().__call__();now=time.monotonic()
        if now-self.last_local>30:
            total=0
            for p in STORE.rglob('*'):
                try:
                    if p.is_file():total+=p.stat().st_size
                except FileNotFoundError:assert 'work' in p.relative_to(STORE).parts
            assert total<LIMIT;self.last_local=now


def archive_control(paths):
    assert not CONTROL.exists() and not (STORE/'control').exists()
    control=STORE/'control';control.mkdir();folder=control/'fixture';folder.mkdir()
    payloads={name:(name.encode()*64+b'\x00\xff\n') for name in MEMBERS}
    for name,data in payloads.items():(folder/name).write_bytes(data)
    archive=control/'fixture.zip';record=pack(folder,archive);manifest=read(archive.with_suffix('.manifest.json'))
    assert read_archive(archive,manifest)==payloads and not list(folder.iterdir())
    bad=control/'corrupt.zip';data=bytearray(archive.read_bytes());data[len(data)//2]^=1;bad.write_bytes(data)
    rejected=False
    try:read_archive(bad,manifest)
    except AssertionError:rejected=True
    assert rejected
    # Exercise recovery of an existing verified archive with retained scratch.
    retry=control/'resume';retry.mkdir()
    for name,data in payloads.items():(retry/name).write_bytes(data)
    repeated=pack(retry,archive);assert repeated==record and not list(retry.iterdir())
    verify(paths);atomic_json(CONTROL,dict(passed=True,inputs=paths,exact_readback=True,corruption_rejected=True,
        existing_archive_recovery=True,verified_transient_cleanup=True,record=record,gpu_used=False))
    print(json.dumps(dict(archive_controls_passed=True)),flush=True)


def export(case):
    assert production_available() and not OTHER.exists()
    folder=STORE/'work'/case['case_id'];folder.mkdir(exist_ok=True);request=folder/'request.json';output=folder/'export.json'
    wanted=dict(format=1,hi=case['hi'],lo=case['lo'])
    if request.exists():assert read(request)==wanted
    else:atomic_json(request,wanted)
    began=time.monotonic()
    if not output.exists():
        child=subprocess.run([str(EXE),str(CONTEXT),str(request),str(output)],capture_output=True,text=True,
            timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        if child.returncode:raise RuntimeError(child.stderr[-3000:])
    doc=read(output);assert doc['context_source']==CONTEXT.read_text() and doc['request_source']==request.read_text()
    for k in ('hi','lo','actor','phase','n'):assert doc['target'][k]==case[k]
    for k in ('pot','amount_to_call','rake'):assert doc['geometry'][k]==case[k]
    assert doc['queries']['observations'][doc['target']['query_index']]['active_features']==case['active_features']
    return folder,doc,time.monotonic()-began


def initial_share(doc,layout,total):
    # Both frozen generation-zero networks have zero output weights and unit
    # biases. Apply their exact table overrides before computing own reach.
    assert np.all(layout['parameters']['w2'][0]==0) and np.all(layout['parameters']['b2'][0]==1)
    obs=doc['queries']['observations'];p=np.zeros((len(obs),4))
    for i,o in enumerate(obs):p[i,:o['n']]=1/o['n']
    ids,values,mask=prepare_tables(doc['queries'],layout['tables'][:1],layout['context_source'])
    if len(ids):p[ids]=np.where(mask[0,:,None],values[0],p[ids])
    reach=1.
    for i,a,n in obs[doc['target']['query_index']]['own_history']:reach*=p[i,a]
    assert reach<=total+1e-10
    return None if total==0 else float(reach/total)


def compute(case,item,banks,shared,entry,guard):
    folder,doc,native_seconds=item;began=time.monotonic();records=[];arrays={};q=doc['target']['query_index']
    path=folder/'policies.npz';record_path=folder/'record.json'
    if record_path.exists():
        record=read(record_path);assert record['case']==case and record['registration_sha256']==sha(REG)
        assert record['policies_sha256']==sha(path);return folder,record
    if path.exists():
        with np.load(path,allow_pickle=False) as z:arrays={k:z[k] for k in z.files}
    else:
        for bank,i in (('A',0),('B',2)):
            p,reach=banks[i].average(doc['queries'],guard=guard)
            arrays['policy_'+bank]=p;arrays['own_reach_'+bank]=reach
    for bank,i in (('A',0),('B',1)):
        p=arrays['policy_'+bank];reach=arrays['own_reach_'+bank]
        stats,detail=posterior(doc,p,entry)
        close=abs(reach[q]-stats['hero_own_likelihood']*3081);assert close<1e-9*max(1.,reach[q])
        labels=None if not stats['supported'] else sampled_labels(case['case_id'],bank,detail['posterior'],detail['outcomes'],doc['geometry']['endpoints_loss_tie_win'])
        if labels is not None:assert abs(labels['exact']-stats['call_minus_fold_bb'])<1e-9
        arrays['posterior_'+bank]=detail['posterior'];arrays['opponent_likelihood_'+bank]=detail['opponent_likelihood']
        records.append(dict(bank=bank,conditional=stats,labels=labels,original_policy=p[q].tolist(),
            target_own_reach=float(reach[q]),initial_share=initial_share(doc,shared.data[i]['layout'],float(reach[q]))))
    if not path.exists():
        with path.open('xb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
    record=dict(case=case,records=records,registration_sha256=sha(REG),policies_sha256=sha(path),
        export_sha256=sha(folder/'export.json'),queries=len(doc['queries']['observations']),native_seconds=native_seconds,
        teacher_and_label_seconds=time.monotonic()-began)
    atomic_json(record_path,record);return folder,record


def study(paths,qualified,selection,resume,inventory,guard):
    control=read(CONTROL);assert control['passed'] and control['inputs']==paths
    paths={**paths,str(CONTROL):sha(CONTROL)}
    if resume:
        reg=read(REG);assert reg['inputs']==paths and reg['selected_cases']==selection['selected_cases']
    else:
        assert not REG.exists() and not (STORE/'cases').exists()
        atomic_json(REG,dict(inputs=paths,selected_cases=selection['selected_cases'],maximum_bytes=LIMIT,
            maximum_invocation_seconds=7200,storage_admission=inventory,mode='two original full banks; exact, sample1, sample16',
            native_prefetch=4,archive_workers=2,created_unix=time.time(),training_started=False,production_modified=False))
        (STORE/'cases').mkdir();(STORE/'work').mkdir()
    assert not RESULT.exists();banks,shared,identity=load(guard,qualified)
    ip=STORE/'bank-identities.json'
    if ip.exists():assert read(ip)==identity
    else:atomic_json(ip,identity)
    attribution=read(OUT/'board-river-opponent-reach-v1-attribution.json')
    prior=Path('S:/GTOpen-research/board-river-opponent-reach-v1/cases')
    for row in attribution['rows']:
        if row['case_id'] not in ('river-000','river-032','river-040','river-074'):continue
        old=read(prior/row['case_id']/'export.json');index=0 if row['bank']=='A' else 1
        actual=initial_share(old,shared.data[index]['layout'],row['total_target_reach'])
        assert abs(actual-row['initial_share'])<1e-12
    entry=PhysicalDeals(CONTEXT.read_text(),mode='full_deck',seed=0).weights
    pending=[];routes={}
    for case in selection['cases']:
        mp=STORE/'cases'/(case['case_id']+'.manifest.json');ap=mp.with_suffix('').with_suffix('.zip')
        if mp.exists():
            manifest=read(mp);assert manifest['archive_sha256']==sha(ap)
            routes[case['case_id']]=dict(manifest_sha256=sha(mp),archive_sha256=manifest['archive_sha256'])
        else:pending.append(case)
    before=len(routes);started=time.monotonic();trial=[];projection=STORE/'collection-admission.json'
    native=ThreadPoolExecutor(max_workers=4);archivers=ThreadPoolExecutor(max_workers=2);futures={};packing=deque()
    def publish_one(future,case,seconds):
        proof=future.result();routes[case['case_id']]={k:proof[k] for k in ('manifest_sha256','archive_sha256')}
        if len(trial)<8:trial.append(dict(**proof,seconds=seconds))
        if len(trial)==8 and not projection.exists():
            current=measure(STORE);remaining=selection['selected_cases']-len(routes)
            estimated_bytes=current['logical_bytes']+max(x['compressed_bytes'] for x in trial)*remaining*2+64_000_000
            per_case=(time.monotonic()-started)/max(1,len(routes)-before)
            estimated_seconds=time.monotonic()-guard.started+per_case*remaining*2
            atomic_json(projection,dict(first_cases=8,estimated_bytes=estimated_bytes,estimated_seconds=estimated_seconds,
                admitted=estimated_bytes<LIMIT and estimated_seconds<7200))
        if projection.exists():assert read(projection)['admitted'],'Resource projection exceeds registered limit'
        status(dict(state='collecting conditional targets',completed_cases=len(routes),total_cases=selection['selected_cases'],
            seconds=time.monotonic()-guard.started,pid=os.getpid()))
        if len(routes)%32==0:print(json.dumps(dict(completed_cases=len(routes),total_cases=selection['selected_cases'],seconds=time.monotonic()-guard.started)),flush=True)
    try:
        for index,case in enumerate(pending):
            guard()
            # Limit speculative work to four visible cases, never another GPU bank.
            for ahead in range(index,min(index+4,len(pending))):
                if ahead not in futures:futures[ahead]=native.submit(export,pending[ahead])
            began=time.monotonic();item=futures.pop(index).result();folder,record=compute(case,item,banks,shared,entry,guard)
            if len(packing)>=2:publish_one(*packing.popleft())
            packing.append((archivers.submit(pack,folder,STORE/'cases'/(case['case_id']+'.zip')),case,time.monotonic()-began))
            # Before the first admission, consume only the first eight cases.
            if index==7 and not projection.exists():
                while packing:publish_one(*packing.popleft())
        while packing:publish_one(*packing.popleft())
    finally:
        native.shutdown(wait=True,cancel_futures=True);archivers.shutdown(wait=True,cancel_futures=True)
    assert len(routes)==selection['selected_cases'];verify(paths);storage=measure(STORE,guard)
    assert storage['logical_bytes']<LIMIT and storage['allocated_file_bytes']<LIMIT
    import torch
    result=dict(passed=True,complete=True,registration_sha256=sha(REG),bank_identities_sha256=sha(ip),
        routes={c['case_id']:routes[c['case_id']] for c in selection['cases']},cases=len(routes),store=str(STORE),storage=storage,
        seconds_this_invocation=time.monotonic()-guard.started,peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
        peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),independent_readback_required=True,training_started=False,
        final_evaluation_scored=False,production_modified=False)
    atomic_json(RESULT,result);status(dict(state='labels complete; readback required',completed_cases=len(routes)))
    print(json.dumps({k:result[k] for k in ('complete','cases','storage','seconds_this_invocation')}),flush=True)


def main(mode,resume):
    paths,qualified,selection=sources()
    if mode=='ready':print(json.dumps(dict(ready=True,selected_cases=selection['selected_cases'])));return
    assert not LOCK.exists() and not OTHER.exists();acquired=False;began=time.monotonic()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert production_available() and psutil.virtual_memory().available>24_000_000_000
        if mode=='control':archive_control(paths);return
        inventory=global_measure();current=measure(STORE)
        assert sum(r['allocated_file_bytes'] for r in inventory)+max(0,LIMIT-current['allocated_file_bytes'])<800_000_000_000
        import torch
        configure();torch.use_deterministic_algorithms(True);guard=Guard();guard.started=began
        study(paths,qualified,selection,resume,inventory,guard)
    except Exception as e:
        path=OUT/(PREFIX+'-failure-'+uuid.uuid4().hex+'.json')
        atomic_json(path,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-began))
        status(dict(state='interrupted',failure=str(path),error=repr(e)));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('ready','control','study'),default='ready')
    parser.add_argument('--resume',action='store_true');args=parser.parse_args();assert not args.resume or args.mode=='study'
    main(args.mode,args.resume)
