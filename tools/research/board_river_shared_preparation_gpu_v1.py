"""Full-bank output and timing qualification; only after the live study ends."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import io
import ast
import json
from pathlib import Path
import time
import traceback
import numpy as np
from board_river_deal_coverage_common_v1 import ROOT,OUT,STORE,PREFIX,OLD_STORE,CONTEXT,LOCK,OTHER,read,sha,verify
from board_river_bounds_bank_v1 import prepare_queries
from board_training_bank_layout_v1 import validate_queries
from board_river_bounds_pilot_support_v2 import Guard,inputs,load
from board_river_target_archive_v1 import read_archive
from board_prefix_publication_v1 import atomic_json
from board_later_fit_holdout_train_v1 import configure
from board_river_opponent_reach_math_v1 import posterior
from sampled_physical_deals_v1 import PhysicalDeals

NAME='board-river-shared-preparation-gpu-v1'
PLAN=OUT/'BOARD-RIVER-SHARED-PREPARATION-GPU-PLAN.md'


def shared(query,layouts,catalog):
    assert layouts
    prepared=prepare_queries(query,layouts[0],catalog)
    for layout in layouts[1:]:validate_queries(layout,prepared['queries'])
    for key in ('arity','phase','eligible','public','reach_affected'):
        prepared[key].flags.writeable=False
    return [prepared]*len(layouts)


def main():
    reg=OUT/(NAME+'-registration.json');dest=OUT/(NAME+'-result.json')
    assert not reg.exists() and not dest.exists() and not LOCK.exists() and not OTHER.exists();acquired=False
    finished=read(OUT/(PREFIX+'-pipeline.json'));assert finished['passed'] and finished['complete']
    profile_reg=OUT/'board-river-shared-preparation-profile-v1-registration.json'
    profile_result=OUT/'board-river-shared-preparation-profile-v1-result.json'
    cpu=read(profile_result);assert cpu['passed'] and cpu['complete'] and cpu['registration_sha256']==sha(profile_reg)
    def function_ast(path):
        nodes=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='shared']
        assert len(nodes)==1;return ast.dump(nodes[0],include_attributes=False)
    assert function_ast(Path(__file__))==function_ast(ROOT/'tools/research/board_river_shared_preparation_profile_v1.py')
    sources,qualified=inputs();sources.update(read(profile_reg)['inputs']);verify(sources)
    paths=[Path(__file__),PLAN,profile_reg,profile_result,OUT/(PREFIX+'-pipeline.json'),ROOT/'tools/research/board_river_opponent_reach_math_v1.py']
    sources.update({str(p):sha(p) for p in paths})
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        import torch
        configure();torch.use_deterministic_algorithms(True);guard=Guard(limit=600);guard()
        atomic_json(reg,dict(inputs=sources,case_ids=read(profile_reg)['case_ids'],maximum_seconds=600,
            maximum_added_bytes=2_000_000,order=['separate','shared','shared','separate'],change='CPU preparation reuse only',
            production_modified=False,created_unix=time.time()))
        banks,pair,identity=load(guard,qualified);catalog=read(OUT/'board-later-public-state-catalog-v1.json')
        layouts=[d['layout'] for d in pair.data];fixtures=[]
        for case_id in read(profile_reg)['case_ids']:
            mp=OLD_STORE/'cases'/(case_id+'.manifest.json');ap=OLD_STORE/'cases'/(case_id+'.zip')
            raw=read_archive(ap,read(mp));doc=json.loads(raw['export.json'])
            with np.load(io.BytesIO(raw['policies.npz']),allow_pickle=False) as z:archived={k:z[k] for k in z.files}
            fixtures.append((case_id,doc,archived,json.loads(raw['record.json'])))
        entry=PhysicalDeals(CONTEXT.read_text(),mode='full_deck',seed=0).weights
        guard_seconds=[0.]
        def timed_guard():
            start=time.perf_counter();guard();guard_seconds[0]+=time.perf_counter()-start
        def run(query,mode):
            if mode=='separate':return [banks[i].average(query,guard=timed_guard) for i in (0,2)]
            cpu_prepared=shared(query,layouts,catalog);out=[]
            for item,data in zip(cpu_prepared,pair.data):
                prepared=data['bank'].prepare(item)
                out.append(data['bank'].average_prepared(prepared,enabled=False,chunk=8,guard=timed_guard))
            return out
        controls=[]
        for case_id,doc,archive,record in fixtures:
            guard();reference=run(doc['queries'],'separate');candidate=run(doc['queries'],'shared')
            pmax=rmax=dmax=0.
            for b,((p,r),(q,s)) in enumerate(zip(reference,candidate)):
                assert p.dtype==q.dtype and p.shape==q.shape and p.tobytes()==q.tobytes()
                assert r.dtype==s.dtype and r.shape==s.shape and r.tobytes()==s.tobytes()
                expected=archive['policy_'+('A','B')[b]];reach=archive['own_reach_'+('A','B')[b]]
                pe=float(np.max(abs(p-expected)));re=float(np.max(abs(r-reach)/np.maximum(1.,abs(reach))))
                assert pe<1e-12 and re<1e-9;pmax=max(pmax,pe);rmax=max(rmax,re)
                value,detail=posterior(doc,q,entry);old=record['records'][b]['conditional']
                assert value['supported']==old['supported']
                if value['supported']:
                    de=abs(value['call_minus_fold_bb']-old['call_minus_fold_bb']);assert de<1e-9;dmax=max(dmax,de)
            controls.append(dict(case_id=case_id,byte_equal=True,archived_policy_error=pmax,archived_reach_relative_error=rmax,conditional_value_error=dmax))
        timings=[]
        for mode in ('separate','shared','shared','separate'):
            torch.cuda.synchronize();before=guard_seconds[0];began=time.perf_counter()
            for _,doc,_,_ in fixtures:run(doc['queries'],mode)
            torch.cuda.synchronize();wall=time.perf_counter()-began;guard_time=guard_seconds[0]-before
            timings.append(dict(mode=mode,wall_seconds=wall,guard_seconds=guard_time,wall_excluding_guard=wall-guard_time))
        separate=sum(r['wall_seconds'] for r in timings if r['mode']=='separate')
        candidate=sum(r['wall_seconds'] for r in timings if r['mode']=='shared')
        raw_separate=sum(r['wall_excluding_guard'] for r in timings if r['mode']=='separate')
        raw_candidate=sum(r['wall_excluding_guard'] for r in timings if r['mode']=='shared')
        checks=dict(byte_equal_outputs=all(r['byte_equal'] for r in controls),faster_without_guard=raw_candidate<raw_separate,
            inclusive_regression_at_most_5_percent=candidate<=1.05*separate)
        verify(sources);guard()
        result=dict(passed=True,complete=True,registration_sha256=sha(reg),controls=controls,timings=timings,checks=checks,
            qualifies_for_future_collector=all(checks.values()),inclusive_speedup=separate/candidate,
            speedup_excluding_guard=raw_separate/raw_candidate,
            saved_seconds_per_case_excluding_guard=(raw_separate-raw_candidate)/(2*len(fixtures)),
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            seconds=time.monotonic()-guard.started,model_or_targets_changed=False,production_modified=False)
        atomic_json(dest,result);assert dest.stat().st_size+reg.stat().st_size<2_000_000
        print(json.dumps(result),flush=True)
    except Exception as error:
        atomic_json(OUT/(NAME+'-failure.json'),dict(error=repr(error),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
