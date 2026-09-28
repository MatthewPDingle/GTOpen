"""Bounded fixed-current-policy pilot; no self-play training or deployment."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import hashlib
import io
import json
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback
import numpy as np
import torch
from river_full_action_math_v1 import digest,validate_document,evaluate,observation
from river_full_action_control_v1 import archive,bundle
from river_current_policy_math_v1 import CurrentPolicy,moments,distribution_control,cached_sample
from board_training_checkpoint_v1 import model_document
from board_training_policy_v1 import probabilities as reference_probabilities
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from board_river_bounds_pilot_support_v2 import Guard
from board_later_fit_holdout_train_v1 import configure
from preflop_allin_matrix_v1 import AllinMatrix
from global_research_inventory_v2 import measure as global_measure

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-current-policy-pilot-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
PLAN=OUT/'RIVER-CURRENT-POLICY-PILOT-PLAN.md'
CONTEXT=OUT/'bb-context-candidate.json'
OLD_STORE=OUT/'river-full-action-control-v1'
EXE=ROOT/'target/release/examples/hu_river_action_queries_v1.exe'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
LIMIT=100_000_000


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def size():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())+sum(p.stat().st_size for p in (REG,RESULT,FAILURE) if p.exists())
def write(path,value):
    data=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    assert size()+len(data)<=LIMIT
    with Path(path).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p


def fixtures():
    previous=read(OUT/'river-full-action-control-v1-result.json');rows=[];paths=[]
    assert previous['passed'] and previous['complete']
    for case in previous['cases']:
        if 'zero-rake' in case['name']:continue
        path=OLD_STORE/(case['name']+'-export.json');assert sha(path)==case['export_sha256']
        rows.append(dict(name=case['name'],path=str(path),native_seconds=read(OLD_STORE/(case['name']+'-native.json'))['seconds']))
        paths.extend([path,OLD_STORE/(case['name']+'-native.json')])
    qp=Path('S:/GTOpen-research/board-river-target-learning-v1/selection/deal-000-queries.json')
    cp=OUT/'board-later-public-state-catalog-v1.json';paths.extend([qp,cp])
    q=read(qp);catalog=read(cp);assert catalog['passed']
    lookup={(r['public_id'],r['actor'],r['phase'],tuple(r['history'])):r for r in catalog['rows']}
    found={}
    for o in q['observations']:
        if o['phase']!=3:continue
        _,actor,phase,branch,history=observation(o);r=lookup[(branch,actor,phase,tuple(history))]
        for a,kind in enumerate(r['action_kinds']):
            if kind in ('bet','raise') and abs(r['action_costs'][a]-r['remaining_actor'])<1e-9:
                found.setdefault((actor,kind),dict(name=f'p{actor}-jam-{kind}',
                    request=dict(format=1,hi=o['hi'],lo=o['lo']),actor=actor,kind=kind,action=a,
                    geometry=r,source_query_index=q['observations'].index(o)))
    assert set(found)=={(a,k) for a in (0,1) for k in ('bet','raise')}
    rows.extend(found[key] for key in sorted(found))
    for actor in (0,1):
        for suffix in ('.zip','.manifest.json'):
            paths.append(Path('S:/GTOpen-research/board-river-target-learning-v1/cases')/(f'd000-p{actor}-under10-0'+suffix))
    return rows,paths


def new_document(row,guard):
    guard();name=row['name'];source=STORE/(name+'-request.json');dest=STORE/(name+'-export.json');write(source,row['request'])
    assert size()+64_000_000<=LIMIT
    t=time.perf_counter();proc=subprocess.run([str(EXE),str(CONTEXT),str(source),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    wall=time.perf_counter()-t
    write(STORE/(name+'-native.json'),dict(code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,seconds=wall))
    assert proc.returncode==0 and dest.exists();doc=read(dest)
    _,old=archive(f"d000-p{row['actor']}-under10-0")
    assert doc['target']['cards']==old['target']['cards']
    assert [(x['cards'],x['outcome_loss_tie_win']) for x in doc['pairs']]==[(x['cards'],x['outcome_loss_tie_win']) for x in old['pairs']]
    root=doc['nodes'][doc['pairs'][0]['root']];action=root['actions'][row['action']]
    assert action['kind']==row['kind'] and action['all_in'] and abs(action['paid']-row['geometry']['remaining_actor'])<1e-9
    return doc,wall,dest


def collect_model_inputs():
    bank_reg_path=OUT/'board-river-bounds-bank-v1-registration.json';bank_result_path=OUT/'board-river-bounds-bank-v1-result.json'
    bank_reg=read(bank_reg_path);result=read(bank_result_path)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(bank_reg_path)
    paths=[bank_reg_path,bank_result_path];policies=[]
    for identity in bank_reg['banks']:
        assert identity['completed_iterations']==78 and len(identity['model_references'])==78
        ref=identity['model_references'][77];assert ref['generation']==77
        folder=Path('S:/GTOpen-research/board-root-matched-prefix-v1')/identity['arm']/'objects'
        path=folder/ref['file'];assert sha(path)==ref['sha256'];paths.append(path)
        policies.append(dict(arm=identity['arm'],reference=ref,folder=str(folder),root_config=identity['root_config'],
                             policy_id=identity['arm']+'|generation77|'+ref['sha256']))
    return policies,paths


def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE,LOCK,OTHER));start=time.monotonic()
    configure();torch.use_deterministic_algorithms(True);guard=Guard(limit=600)
    source=CONTEXT.read_text();catalog_path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    matrix_path=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    rows,paths=fixtures();policies,model_paths=collect_model_inputs();paths.extend(model_paths)
    for prefix in ('river-full-action-control-v1','river-full-action-provenance-v1'):
        reg=OUT/(prefix+'-registration.json');result=OUT/(prefix+'-result.json')
        assert read(result)['passed'] and read(result)['complete'] and read(result)['registration_sha256']==sha(reg)
        verify(read(reg)['inputs']);paths.extend([reg,result])
    paths.extend([Path(__file__),PLAN,CONTEXT,EXE,catalog_path,matrix_path,ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',
                  ROOT/'crates/solver/examples/hu_river_action_queries_v1.rs',ROOT/'crates/solver/examples/research_sampled/policy_walk_allin_v1.rs'])
    paths.extend((ROOT/'crates/solver/src').rglob('*.rs'));paths.extend((ROOT/'crates/solver/examples/research_sampled').glob('*.rs'))
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and Path(f).is_relative_to(ROOT) and Path(f).suffix=='.py':paths.append(Path(f))
    inputs={str(p):sha(p) for p in paths}
    STORE.mkdir();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard()
        inventory=global_measure();assert sum(x['allocated_file_bytes'] for x in inventory)+LIMIT<800_000_000_000
        write(REG,dict(format=1,created_unix=time.time(),inputs=inputs,cases=rows,policies=policies,storage_admission=inventory,
            maximum_seconds=600,maximum_added_bytes=LIMIT,maximum_cuda_bytes=4_000_000_000,external_cuda_headroom=2_000_000_000,
            seeds=dict(cached_samples=9289991),fixed_pair_controls=[0,495,989],timing_repetitions=3,cached_samples_per_case=2048,
            policy_tolerance=1e-10,action_value_tolerance=1e-7,moment_covariance_tolerance=1e-8,
            torch_version=torch.__version__,numpy_version=np.__version__,training=False,production_modified=False,
            scope='Conditional river values and target moments/cost under two fixed played model pairs; no upstream sampling or convergence qualification.'))
        args=dict(catalog_source=catalog_path.read_text(),matrix_sha256=sha(matrix_path),entry_mass=AllinMatrix(read(matrix_path),source).btn_mass)
        prior=PhysicalDeals(source,mode='full_deck',seed=0).weights
        entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,row)} for row in prior]
        engines=[]
        for identity in policies:
            guard();kwargs=dict(args,root_config=identity['root_config'])
            model=model_document(Path(identity['folder']),identity['reference'],context_source=source,**kwargs)
            engines.append((model,CurrentPolicy(model,source,guard=guard,**kwargs),kwargs))
        records=[];peak_policy_error=0.;peak_value_error=0.
        for row in rows:
            guard();name=row['name']
            if 'request' in row:doc,native_seconds,path=new_document(row,guard)
            else:doc=read(row['path']);native_seconds=row['native_seconds'];path=Path(row['path'])
            checked=validate_document(doc,source)
            uniform=np.asarray([[1/o['n'] if a<o['n'] else 0. for a in range(4)] for o in doc['queries']['observations']])
            uniform_controls=[distribution_control(doc,uniform,i) for i in (0,495,989)]
            by_policy=[];saved={}
            for identity,(model,engine,kwargs) in zip(policies,engines):
                guard();policy_id=identity['policy_id'];t=time.perf_counter()
                cpu,_=reference_probabilities(doc['queries'],model,device='cpu',**kwargs);cpu_time=time.perf_counter()-t
                timings=[];v=None;p=None
                for repeat in range(3):
                    guard();t=time.perf_counter();prepared=engine.prepare(doc['queries']);prep=time.perf_counter()-t
                    torch.cuda.synchronize();t=time.perf_counter();p=engine.infer(prepared,guard=guard);torch.cuda.synchronize();infer=time.perf_counter()-t
                    error=float(np.max(abs(cpu-p)));assert error<=1e-10 and np.array_equal(cpu>0,p>0);peak_policy_error=max(peak_policy_error,error)
                    b=bundle(doc,p.tolist(),policy_id);t=time.perf_counter()
                    current=evaluate(doc,b,entry,expected_policy_id=policy_id,expected_context_source=source);evaluation=time.perf_counter()-t
                    if v is not None:
                        assert current['supported']==v['supported']
                        if v['supported']:assert current['action_values']==v['action_values']
                    v=current;timings.append(dict(repetition=repeat,prepare_seconds=prep,infer_seconds=infer,value_seconds=evaluation))
                cpu_value=evaluate(doc,bundle(doc,cpu.tolist(),policy_id),entry,expected_policy_id=policy_id,expected_context_source=source)
                assert cpu_value['supported']==v['supported']
                value_error=None
                if v['supported']:
                    value_error=max(abs(x-y) for x,y in zip(cpu_value['action_values'],v['action_values']));assert value_error<=1e-7;peak_value_error=max(peak_value_error,value_error)
                controls=[distribution_control(doc,p,i) for i in (0,495,989)]
                value=dict(supported=v['supported'],opponent_mass=v['opponent_mass'],own_likelihood=v['own_history_likelihood'],
                           hero_entry_weight=entry[doc['target']['actor']][tuple(sorted(doc['target']['cards'][:2]))])
                stats=sampling=None
                if v['supported']:
                    stats=moments(doc,p,v['posterior']);assert np.max(abs(np.asarray(stats['action_means'])-v['action_values']))<1e-8
                    value.update(action_values=v['action_values'],value=v['value'],regrets=v['regrets'])
                    # Draw identities outside the timer; report only cached traversal.
                    seed=int.from_bytes(hashlib.sha256(f'9289991|{name}|{policy_id}'.encode()).digest()[:8],'big')
                    rng=np.random.Generator(np.random.PCG64(seed));indices=rng.choice(990,size=2048,p=v['posterior'])
                    action_rng=random.Random(seed);samples=[];visits=[0,0];t=time.perf_counter()
                    for index in indices:
                        sample,counts=cached_sample(doc,p,int(index),action_rng);samples.append(sample)
                        visits[0]+=counts[0];visits[1]+=counts[1]
                    wall=time.perf_counter()-t;samples=np.asarray(samples)
                    sampling=dict(draws=2048,seconds=wall,seconds_per_cached_sample=wall/2048,mean_regrets=samples.mean(0).tolist(),
                        observed_sum_regret_variances=float(samples.var(0).sum()),decision_visits=visits[0],terminal_visits=visits[1],
                        scope='Cached Python subtree only, excluding native query generation, feature preparation and policy inference; not an end-to-end comparator.')
                saved[identity['arm']]=p
                by_policy.append(dict(policy_id=policy_id,arm=identity['arm'],probability_sha256=b['probabilities_sha256'],
                    policy_error=float(np.max(abs(cpu-p))),value_error=value_error,cpu_reference_seconds=cpu_time,timings=timings,
                    conditional=value,moments=stats,cached_sampling=sampling,distribution_controls=controls))
            target=STORE/(name+'-policies.npz');buffer=io.BytesIO();np.savez_compressed(buffer,**saved);raw=buffer.getvalue();assert size()+len(raw)<=LIMIT
            with target.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
            with np.load(target,allow_pickle=False) as z:
                for key,p in saved.items():assert np.array_equal(z[key],p)
            record=dict(case=name,actor=doc['target']['actor'],export_path=str(path),export_sha256=sha(path),queries=checked['observations'],nodes=checked['nodes'],
                checks=checked,native_seconds=native_seconds,native_timing_source='new pilot run' if 'request' in row else 'prior control run; separate environment/timestamp',
                uniform_distribution_controls=uniform_controls,policies=by_policy,policy_archive_sha256=sha(target))
            write(STORE/(name+'-result.json'),record);records.append(record)
            print(json.dumps(dict(case=name,passed=True,supported=[p['conditional']['supported'] for p in by_policy],
                own_likelihoods=[p['conditional']['own_likelihood'] for p in by_policy])),flush=True)
        verify(inputs);guard();assert size()<LIMIT
        write(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=records,seconds=time.monotonic()-start,
            maximum_policy_error=peak_policy_error,maximum_action_value_error=peak_value_error,
            cuda_peak_allocated_bytes=torch.cuda.max_memory_allocated(),cuda_peak_reserved_bytes=torch.cuda.max_memory_reserved(),
            desktop_probes=guard.probes,bytes_before_result=size(),training=False,production_modified=False))
        print(json.dumps(dict(passed=True,cases=len(records),seconds=time.monotonic()-start,bytes=size(),maximum_policy_error=peak_policy_error)),flush=True)
    except Exception as e:
        write(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
