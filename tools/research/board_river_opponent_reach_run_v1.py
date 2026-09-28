"""Fixed 80-case diagnostic against each frozen opponent's actual history reach."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import json
from pathlib import Path
import subprocess
import time
import traceback
import uuid
import numpy as np
import psutil
from board_river_bounds_pilot_support_v2 import (ROOT,OUT,LOCK,OTHER,CONTEXT,read,sha,verify,
    Guard as PilotGuard,inputs as bank_inputs,load,CUDA_BUDGET_BYTES,CUDA_HEADROOM_BYTES)
from board_later_fit_holdout_train_v1 import configure
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import measure
from global_research_inventory_v2 import measure as global_measure
from bounded_parallel_evaluation_archive_v2 import production_available
from sampled_physical_deals_v1 import PhysicalDeals
from board_river_opponent_reach_math_v1 import posterior,fold_call_readout

PREFIX='board-river-opponent-reach-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
TOOLS=ROOT/'tools/research'
EXE=ROOT/'target/release/examples/hu_river_conditional_queries_v1.exe'
LIMIT=500_000_000
REG=OUT/(PREFIX+'-registration.json')
RESULT=OUT/(PREFIX+'-result.json')
SELECTION=OUT/(PREFIX+'-selected-cases.json')


def status(value):atomic_json(OUT/(PREFIX+'-status.json'),value,replace=True)


class Guard(PilotGuard):
    def __init__(self):
        super().__init__(limit=3600);self.last_local=0
    def __call__(self):
        # The qualified guard keeps its own pilot roots empty. This new store
        # has the smaller predeclared allowance, including completed controls.
        super().__call__()
        now=time.monotonic()
        if now-self.last_local>20:
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<LIMIT
            self.last_local=now


def inputs():
    paths,qualified=bank_inputs();selection=read(SELECTION);verify(selection['inputs'])
    cp=OUT/(PREFIX+'-control.json');cr=OUT/(PREFIX+'-control-registration.json');controls=read(cp)
    assert controls['passed'] and controls['complete'] and controls['registration_sha256']==sha(cr)
    verify(read(cr)['inputs']);paths.update(selection['inputs']);paths.update(read(cr)['inputs'])
    for p in (Path(__file__),TOOLS/'board_river_opponent_reach_math_v1.py',SELECTION,cp,cr,EXE,
              OUT/'BOARD-RIVER-OPPONENT-REACH-PLAN.md',OUT/'weighted-complete-river-bounds-pilot-v1-independent-review.json',
              OUT/'BOARD-RIVER-BOUNDS-PILOT-DECISION.md'):
        paths[str(p)]=sha(p)
    assert selection['selected_cases']==80
    return paths,qualified,selection


def immutable(path,value):
    if path.exists():assert read(path)==value
    else:atomic_json(path,value)


def export(case,folder,guard):
    rp=folder/'request.json';op=folder/'export.json'
    immutable(rp,dict(format=1,hi=case['hi'],lo=case['lo']))
    if not op.exists():
        guard();p=subprocess.run([str(EXE),str(CONTEXT),str(rp),str(op)],capture_output=True,text=True,
                                 timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        if p.returncode:raise RuntimeError(p.stderr[-3000:])
    doc=read(op)
    assert doc['context_source']==CONTEXT.read_text() and doc['request_source']==rp.read_text()
    for k in ('hi','lo','actor','phase','n'):assert doc['target'][k]==case[k]
    for k in ('pot','amount_to_call','rake'):assert doc['geometry'][k]==case[k]
    return doc


def case_result(case,folder,banks,entry,guard):
    began=time.monotonic();doc=export(case,folder,guard);export_seconds=time.monotonic()-began
    npz=folder/'policies.npz';started=time.monotonic()
    if not npz.exists():
        values={}
        for i,bank in enumerate(banks):
            p,reach=bank.average(doc['queries'],guard=guard)
            values[f'policy_{i}']=p;values[f'own_reach_{i}']=reach
        temporary=folder/('policies-'+uuid.uuid4().hex+'.npz')
        with temporary.open('xb') as f:
            np.savez_compressed(f,**values);f.flush();os.fsync(f.fileno())
        os.rename(temporary,npz)
    inference_seconds=time.monotonic()-started
    with np.load(npz,allow_pickle=False) as source:
        values={k:source[k] for k in source.files}
    records=[];target=doc['target']['query_index']
    for name,i in (('A',0),('B',2)):
        stats,arrays=posterior(doc,values[f'policy_{i}'],entry)
        original=fold_call_readout(values[f'policy_{i}'][target],stats['call_minus_fold_bb'])
        bounded=fold_call_readout(values[f'policy_{i+1}'][target],stats['call_minus_fold_bb'])
        # Bounds can alter raise probability too. Do not assign full policy EV
        # to the change in call probability without pricing those other actions.
        records.append(dict(bank=name,opponent_version='original',conditional=stats,original=original,bounded=bounded,
            original_target_own_reach=float(values[f'own_reach_{i}'][target]),
            bounded_target_own_reach=float(values[f'own_reach_{i+1}'][target])))
    result=dict(case=case,records=records,request_sha256=sha(folder/'request.json'),
        export_sha256=sha(folder/'export.json'),policies_sha256=sha(npz),
        queries=len(doc['queries']['observations']),export_seconds=export_seconds,inference_seconds=inference_seconds,
        seconds=time.monotonic()-began,registration_sha256=sha(REG))
    atomic_json(folder/'result.json',result)
    return result


def main(resume):
    paths,qualified,selection=inputs();assert not RESULT.exists()
    assert not LOCK.exists() and not OTHER.exists() and STORE.is_dir()
    began=time.monotonic();acquired=False;guard=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert production_available() and psutil.virtual_memory().available>24_000_000_000
        inventory=global_measure();size=measure(STORE)
        assert sum(x['allocated_file_bytes'] for x in inventory)+max(0,LIMIT-size['allocated_file_bytes'])<800_000_000_000
        if resume:
            reg=read(REG);assert reg['inputs']==paths and reg['store']==str(STORE)
        else:
            assert not REG.exists() and not (STORE/'cases').exists()
            reg=dict(inputs=paths,store=str(STORE),storage_admission=inventory,maximum_output_bytes=LIMIT,
                maximum_invocation_seconds=3600,selected_cases=80,selection_seed=9289902,
                cuda_allocator_budget_bytes=CUDA_BUDGET_BYTES,cuda_external_headroom_bytes=CUDA_HEADROOM_BYTES,
                desktop_policy='Share with light desktop/video use; yield to active solves or GPU utilization >=65%.',
                source='Both frozen 78-model banks; original opponent history-conditioned range.',
                inference='Exact 990-combination conditional contrast given the fixed approximate opponent policy.',
                stopping='All preselected cases; no result-dependent selection or stopping.',
                statistics='Descriptive query-balanced diagnostic; not reach-weighted or fresh-deal EV evidence.',
                production_modified=False,training_performed=False,created_unix=time.time())
            atomic_json(REG,reg);(STORE/'cases').mkdir()
        import torch
        configure();torch.use_deterministic_algorithms(True);guard=Guard();guard.started=began
        banks,shared,identity=load(guard,qualified);immutable(STORE/'bank-identities.json',identity)
        entry=PhysicalDeals(CONTEXT.read_text(),mode='full_deck',seed=0).weights
        routes={};projection_path=STORE/'first-case-admission.json'
        for index,case in enumerate(selection['cases']):
            guard();folder=STORE/'cases'/case['case_id'];folder.mkdir(exist_ok=True)
            if (folder/'result.json').exists():
                result=read(folder/'result.json');assert result['case']==case and result['registration_sha256']==sha(REG)
                for field,name in (('request_sha256','request.json'),('export_sha256','export.json'),('policies_sha256','policies.npz')):
                    assert result[field]==sha(folder/name)
            else:result=case_result(case,folder,banks,entry,guard)
            routes[case['case_id']]=sha(folder/'result.json')
            if index==0 and not projection_path.exists():
                first=measure(folder);current=measure(STORE)
                projected_bytes=current['logical_bytes']+2*first['logical_bytes']*79
                projected_seconds=time.monotonic()-began+2*max(result['seconds'],1)*79
                admission=dict(first_case_bytes=first['logical_bytes'],first_case_seconds=result['seconds'],
                    projected_bytes=projected_bytes,projected_seconds=projected_seconds,
                    admitted=projected_bytes<LIMIT and projected_seconds<3600)
                atomic_json(projection_path,admission)
            assert read(projection_path)['admitted'],'First-case resource projection exceeded plan; preserve evidence'
            progress=dict(state='running',completed_cases=index+1,total_cases=80,seconds=time.monotonic()-began,pid=os.getpid())
            status(progress)
            if (index+1)%8==0 or index==0:print(json.dumps(progress),flush=True)
        verify(paths);storage=measure(STORE,guard)
        assert storage['logical_bytes']<LIMIT and storage['allocated_file_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),store=str(STORE),cases=80,
            bank_identities_sha256=sha(STORE/'bank-identities.json'),first_case_admission_sha256=sha(projection_path),
            routes=routes,storage=storage,seconds_this_invocation=time.monotonic()-began,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            resource_probes=guard.probes,independent_review_required=True,training_performed=False,production_modified=False)
        atomic_json(RESULT,result);status(dict(state='complete; independent readback pending',cases=80))
        print(json.dumps({k:result[k] for k in ('complete','cases','storage','seconds_this_invocation')}),flush=True)
    except Exception as e:
        p=STORE/('failure-'+uuid.uuid4().hex+'.json')
        atomic_json(p,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-began))
        status(dict(state='interrupted',failure=str(p),error=repr(e)));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args();main(args.resume)
