"""Matched full-update river-target pilot; resume only complete joint boundaries."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse,copy,gc,hashlib,json,re,shutil,subprocess,sys,time,traceback,uuid
from pathlib import Path
import numpy as np
import psutil
import board_training_checkpoint_v1 as checkpoint
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_training_pipeline_v1 import update as baseline_update
from river_training_pipeline_v1 import update as candidate_update
from board_training_pipeline_control_v1 import compare_states
from board_training_policy_v1 import average as reference_average
from board_training_gpu_bank_v1 import BoardRootCudaBank64
from river_weighted_overlay_ingest_v1 import METHOD
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import AllinCache
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure as study_measure
from global_research_inventory_v2 import measure as global_measure
from bounded_parallel_evaluation_archive_v2 import production_available,ParallelArchives
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive
from weighted_evaluation_checkpoint_v1 import publish,restore_latest,committed
from crossed_complete_policy_batch_v1 import evaluate_batch
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from sampled_physical_deals_v1 import PhysicalDeals
from weighted_learning_cuda_control_20260927 import LOCK,OTHER
from board_river_bounds_pilot_support_v2 import memory_admitted,CUDA_BUDGET_BYTES

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-matched-training-pilot-v1';STORE=Path('S:/GTOpen-research/weighted-complete-river-training-pilot-v1')
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');STATUS=OUT/(NAME+'-status.json')
PLAN=OUT/'RIVER-MATCHED-TRAINING-PILOT-PLAN.md'
CONTEXT=OUT/'bb-context-candidate.json';MATRIX=OUT/'preflop-allin-matrix-control-v1-matrix.json'
CATALOG=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
PHYSICAL=Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json')
LIMIT=8_000_000_000;RESERVE=2_000_000_000;GLOBAL_LIMIT=800_000_000_000
TEST_DEALS=1024;TEST_SEED=9293101
ORDER=('A-baseline','A-river','B-river','B-baseline')
BANK_ORDER=('A-baseline','A-river','B-baseline','B-river')
EXES={k:ROOT/'target/release/examples'/v for k,v in dict(
    executable='hu_sampled_allin_bridge_v3.exe',trace_executable='hu_sampled_action_trace_v2.exe',
    integration_executable='hu_sampled_profile_allin_evaluation_v1.exe',board_executable='hu_fixed_board_tree_v1.exe',
    river_executable='hu_river_two_stage_stream_v1.exe',query_executable='hu_sampled_bank_bridge.exe').items()}

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(inputs):
    for p,h in inputs.items():
        if sha(p)!=h:raise ValueError('Registered input changed: '+p)
def immutable(p,value):
    if p.exists():assert read(p)==value,str(p)
    else:atomic_json(p,value)
def status(state,**values):
    atomic_json(STATUS,dict(state=state,pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),**values),replace=True)
def gpu_snapshot():
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        timeout=10,creationflags=subprocess.CREATE_NO_WINDOW).decode().strip().splitlines()
    assert len(raw)==1
    util,free=map(float,raw[0].split(','));return dict(utilization_percent=util,free_bytes=int(free*1024**2))
def available():
    g=gpu_snapshot()
    ok=(not LOCK.exists() and not OTHER.exists() and production_available() and psutil.cpu_percent(interval=1)<50
        and psutil.virtual_memory().available>28_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
        and g['utilization_percent']<65 and memory_admitted(g['free_bytes'],0))
    return ok,g

class Guard:
    def __init__(self):self.started=time.monotonic();self.last=0.;self.last_gpu=0.;self.last_storage=0.;self.probes=[];self.wait_seconds=0.
    def __call__(self):
        now=time.monotonic()
        if now-self.started>14400:raise TimeoutError('Four-hour invocation limit; preserve completed boundaries')
        if now-self.last<2:return
        assert production_available() and not OTHER.exists(),'Production or another study has priority'
        assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
        import torch
        assert torch.cuda.memory_allocated()<=CUDA_BUDGET_BYTES and torch.cuda.memory_reserved()<=CUDA_BUDGET_BYTES
        self.last=now
        if now-self.last_storage>20:
            size=0
            for p in STORE.rglob('*'):
                try:
                    if p.is_file():size+=p.stat().st_size
                except FileNotFoundError:
                    # Archive workers may retire only their verified new scratch copies.
                    assert '.batch-work' in p.relative_to(STORE).parts
            assert size<LIMIT,'New evidence budget exhausted; preserve files'
            self.last_storage=now
        if now-self.last_gpu>30:
            torch.cuda.synchronize();time.sleep(1.2);start=time.monotonic();announced=False
            while True:
                assert time.monotonic()-self.started<14400 and production_available() and not OTHER.exists()
                value=gpu_snapshot();reserved=torch.cuda.memory_reserved()
                self.probes.append(dict(elapsed=time.monotonic()-self.started,own_reserved_bytes=reserved,**value))
                if value['utilization_percent']<65 and memory_admitted(value['free_bytes'],reserved):break
                if not announced:status('yielding_to_other_gpu_work',**value);announced=True
                time.sleep(5)
            self.wait_seconds+=time.monotonic()-start;self.last_gpu=time.monotonic()

def specification():
    pattern=re.compile(r'"[^"\n]*seed[^"\n]*"\s*:\s*'+str(TEST_SEED)+r'\b')
    for path in OUT.glob('*registration.json'):
        if path!=REG and pattern.search(path.read_text()):
            raise ValueError('Proposed fresh test seed was already registered: '+str(path))
    pre=OUT/'river-training-preflight-v1.json';proof=read(pre)
    assert proof['passed'] and proof['read_only'] and not proof['training_started']
    verify(proof['inputs']);source=CONTEXT.read_text();matrix=AllinMatrix(read(MATRIX),source)
    paths=[Path(__file__),PLAN,pre,PHYSICAL,*EXES.values(),ROOT/'crates/solver/examples/hu_river_two_stage_stream_v1.rs']
    cache_review=OUT/'complete-private-allin-cache-v2-independent-review.json';cache=read(cache_review);assert cache['passed']
    paths.extend([cache_review,Path(cache['cache_artifact'])])
    inputs=dict(proof['inputs']);arms={}
    for label,row in zip(('A','B'),proof['arms']):
        objects=Path(row['objects']);cp=objects/row['source_checkpoint']['file'];doc=read(cp)
        assert sha(cp)==row['source_checkpoint']['sha256'] and doc['completed_iterations']==78
        assert doc['next_model']['generation']==78 and doc['played_bank'][-1]['generation']==77
        assert doc['config']['allin_cache_sha256']==cache['cache_sha256']
        for treatment in ('baseline','river'):
            cfg=copy.deepcopy(doc['config'])
            if treatment=='river':cfg['river_targets']=dict(method=METHOD,K=64)
            checkpoint.require_config(cfg)
            arms[label+'-'+treatment]=dict(source_arm=row['arm'],source_objects=str(objects),source_checkpoint=row['source_checkpoint'],
                original_config=doc['config'],config=cfg,treatment=treatment)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs.update({str(p):sha(p) for p in paths});verify(inputs)
    args=dict(context_source=source,catalog_source=CATALOG.read_text(),matrix_sha256=sha(MATRIX),entry_mass=matrix.btn_mass)
    return dict(format=1,inputs=inputs,arms=arms,order=list(ORDER),bank_order=list(BANK_ORDER),store=str(STORE),
        initial_iteration=78,final_iteration=80,physical_workers=4,board_workers=4,
        test_deals=TEST_DEALS,test_seed=TEST_SEED,maximum_new_bytes=LIMIT,reserved_followup_bytes=RESERVE,
        global_allocated_cap=GLOBAL_LIMIT,maximum_invocation_seconds=14400,maximum_initial_wait_seconds=43200,
        qualification='A-river update 79 interruption before publication and exact restart replay; excluded from learning cost.',
        evaluation='80 played models (0..79), own-history reach weighted; 1024 fresh common deals, eight crossed full-policy gains, one final look.',
        gpu_sharing='Light desktop below 65%; 4GB own CUDA cap, 2GB external headroom; yield to heavy work and active solves.',
        production_modified=False,accuracy_qualified=False),args,cache

def model_args(args,arm):return dict(args,root_config=arm['config']['board_root'])

def copy_source(folder,arm,args):
    objects=folder/'objects';objects.mkdir(exist_ok=True)
    source=Path(arm['source_objects']);ref=arm['source_checkpoint'];doc=read(source/ref['file'])
    for r in [ref,*doc['played_bank'],doc['next_model'],*doc['reservoirs']]:
        origin=source/r['file'];dest=objects/r['file'];assert sha(origin)==r['sha256']
        if not dest.exists():
            temp=objects/('.copy-'+uuid.uuid4().hex)
            shutil.copyfile(origin,temp);assert sha(temp)==r['sha256'];os.rename(temp,dest)
        assert sha(dest)==r['sha256']
    state=checkpoint.restore_checkpoint(objects,ref,arm['original_config'],**model_args(args,arm))
    fork=checkpoint.save_checkpoint(objects,state,arm['config'],**model_args(args,arm))
    restored=checkpoint.restore_checkpoint(objects,fork,arm['config'],**model_args(args,arm));compare_states(state,restored)
    return state,fork

def restore_arm(folder,arm,args):
    pp=folder/'progress.json'
    if pp.exists():
        p=read(pp);assert p['registration_sha256']==sha(REG) and p['initial_source']==arm['source_checkpoint']
        assert p['completed'] in (78,79,80) and len(p['updates'])==p['completed']-78
        for row in p['updates']:
            path=folder/row['metrics'];assert sha(path)==row['sha256']
            metric=read(path);assert metric['iteration']==row['iteration']
            for sub in metric['subbatches']:
                part=path.parent/f"batch-{sub['chunk']:02d}"
                for name,h in sub['artifacts'].items():assert sha(part/name)==h,name
        state=checkpoint.restore_checkpoint(folder/'objects',p['checkpoint'],arm['config'],**model_args(args,arm))
        assert state['completed_iterations']==p['completed'];return state,p
    state,fork=copy_source(folder,arm,args)
    p=dict(registration_sha256=sha(REG),initial_source=arm['source_checkpoint'],initial_fork=fork,completed=78,checkpoint=fork,updates=[])
    atomic_json(pp,p);return state,p

def step_arguments(arm,args,cache,guard):
    return dict(context_path=CONTEXT,catalog_source=args['catalog_source'],matrix_source=MATRIX.read_text(),matrix_sha256=args['matrix_sha256'],
        cache=cache,**{k:v for k,v in EXES.items() if k not in ('river_executable','query_executable')},
        physical_catalog_source=PHYSICAL.read_text(),batch_prefix=NAME+'|'+arm['source_arm'],guard=guard,workers=4,board_workers=4)

class InjectedStop(RuntimeError):pass
def qualify(folder,arm,args,cache,guard):
    proof=folder/'qualification.json'
    if proof.exists():
        q=read(proof);assert q['passed'] and q['registration_sha256']==sha(REG)
        for p,h in q['artifacts'].items():assert sha(folder/p)==h,p
        return
    # Resume from the original fork regardless of uncommitted earlier attempts.
    progress=read(folder/'progress.json');objects=folder/'objects';cfg=arm['config'];ma=model_args(args,arm)
    ref=progress['initial_fork'];state=checkpoint.restore_checkpoint(objects,ref,cfg,**ma)
    original=copy.deepcopy(state);attempt=folder/('qualification-'+uuid.uuid4().hex[:8]);attempt.mkdir()
    step=step_arguments(arm,args,cache,guard);step['river_executable']=EXES['river_executable']
    def stop(stage):
        if stage=='root-update-complete':raise InjectedStop(stage)
    before=time.monotonic()
    try:candidate_update(attempt/'interrupted',objects,state,cfg,on_stage=stop,**step)
    except InjectedStop:pass
    else:raise AssertionError('Expected deliberate pre-publication stop')
    compare_states(state,original);assert not (attempt/'interrupted/metrics.json').exists()
    resumed=checkpoint.restore_checkpoint(objects,ref,cfg,**ma);compare_states(resumed,original)
    first=candidate_update(attempt/'complete',objects,resumed,cfg,**step)
    reload=checkpoint.restore_checkpoint(objects,first['checkpoint'],cfg,**ma);compare_states(reload,resumed)
    replay=checkpoint.restore_checkpoint(objects,ref,cfg,**ma)
    second=candidate_update(attempt/'replay',objects,replay,cfg,**step)
    compare_states(resumed,replay);assert first['checkpoint']==second['checkpoint'] and first['subbatches']==second['subbatches']
    q=dict(passed=True,registration_sha256=sha(REG),checkpoint=first['checkpoint'],interruption='root-update-complete',
        exact_restart_replay=True,seconds=time.monotonic()-before,training_cost_excluded=True,
        completed_metrics=str((attempt/'complete/metrics.json').relative_to(folder)),
        artifacts={str(p.relative_to(folder)):sha(p) for p in attempt.rglob('*') if p.is_file()})
    atomic_json(proof,q)

def train(reg,args,cache,guard):
    for name in ORDER:
        guard();arm=reg['arms'][name];folder=STORE/name;folder.mkdir(exist_ok=True)
        state,p=restore_arm(folder,arm,args);objects=folder/'objects';cfg=arm['config'];ma=model_args(args,arm)
        if name=='A-river':
            status('qualifying_full_update_and_restart',arm=name);qualify(folder,arm,args,cache,guard)
        while state['completed_iterations']<80:
            guard();it=state['completed_iterations']+1;status('training',arm=name,iteration=it)
            dest=folder/(f'generation-{it:04d}-'+uuid.uuid4().hex[:8]);step=step_arguments(arm,args,cache,guard)
            update=baseline_update if arm['treatment']=='baseline' else candidate_update
            if arm['treatment']=='river':step['river_executable']=EXES['river_executable']
            waited=guard.wait_seconds;metric=update(dest,objects,state,cfg,**step)
            restored=checkpoint.restore_checkpoint(objects,metric['checkpoint'],cfg,**ma);compare_states(restored,state)
            assert state['played_bank'][-1]['generation']==it-1 and state['next_model']['generation']==it
            p=dict(p,completed=it,checkpoint=metric['checkpoint'],updates=[*p['updates'],dict(iteration=it,
                metrics=str((dest/'metrics.json').relative_to(folder)),sha256=sha(dest/'metrics.json'),
                competing_gpu_wait_seconds=guard.wait_seconds-waited)])
            atomic_json(folder/'progress.json',p,replace=True)
            print(json.dumps(dict(state='trained',arm=name,iteration=it,seconds=metric['seconds'])),flush=True)
            del restored;gc.collect()
        del state;gc.collect()
    # Compare paired first-update source and policy rows; the sole treatment is target replacement.
    paired=[]
    for label in ('A','B'):
        a,b=[STORE/(label+'-'+kind) for kind in ('baseline','river')]
        pa,pb=read(a/'progress.json'),read(b/'progress.json')
        x,y=a/pa['updates'][0]['metrics'],b/pb['updates'][0]['metrics']
        assert read(x.parent/'source-generation.json')==read(y.parent/'source-generation.json')
        assert read(x.parent/'current-initial-policy.json')==read(y.parent/'current-initial-policy.json')
        for i in range(8):
            for item in ('batch','queries','policies','updates','action-trace','derived-targets','postflop-targets','weighted-targets','integrated-targets'):
                assert sha(x.parent/f'batch-{i:02d}'/(item+'.json'))==sha(y.parent/f'batch-{i:02d}'/(item+'.json')),item
        paired.append(dict(seed=label,first_update_source_policies_and_base_targets_equal=True,baseline_checkpoint=pa['checkpoint'],candidate_checkpoint=pb['checkpoint']))
    return paired

def banks_for_eval(reg,args,guard):
    banks=[];references=[];identities=[]
    for name in BANK_ORDER:
        guard();arm=reg['arms'][name];folder=STORE/name;pp=folder/'progress.json';progress=read(pp)
        assert progress['completed']==80
        state=checkpoint.restore_checkpoint(folder/'objects',progress['checkpoint'],arm['config'],**model_args(args,arm))
        models=[checkpoint.model_document(folder/'objects',ref,**model_args(args,arm)) for ref in state['played_bank']]
        assert [m['generation'] for m in models]==list(range(80))
        weights=np.tile(np.arange(1.,81.),(2,1));ma=model_args(args,arm)
        banks.append(BoardRootCudaBank64(models,weights,completed_iterations=80,models_per_chunk=4,guard=guard,**ma))
        references.append((models,weights,ma))
        identities.append(dict(arm=name,checkpoint=progress['checkpoint'],progress_sha256=sha(pp),played_models=state['played_bank'],
                               unplayed_excluded=state['next_model'],root_config=arm['config']['board_root']))
        del state;gc.collect()
    return banks,references,identities

def evaluate(reg,args,cache,guard):
    status('loading_played_policy_banks');banks,references,identities=banks_for_eval(reg,args,guard)
    immutable(STORE/'bank-identities.json',identities);identity=sha(STORE/'bank-identities.json');source=args['context_source']
    common=dict(context_path=CONTEXT,banks=banks,cache=cache,guard=guard,query_executable=EXES['query_executable'],evaluation_executable=EXES['integration_executable'])
    control=STORE/'evaluation-transport-control.json'
    if not control.exists():
        # Reuse a TRAIN deal for transport checks; this is not an accuracy observation.
        first=read(STORE/'A-baseline/progress.json')['updates'][0]
        trainfolder=(STORE/'A-baseline'/first['metrics']).parent
        deal=read(trainfolder/'source-generation.json')['deals'][0]
        dest=STORE/('transport-'+uuid.uuid4().hex[:8])
        evaluate_batch(batch=dict(format=2,batch_id=NAME+'-transport',seed=0,query_limit=100000,deals=[deal]),folder=dest,**common)
        queries=read(dest/'queries.json');errors=[]
        for bank,(models,weights,ma) in zip(banks,references):
            gpu,support=bank.average(queries,guard=guard)
            cpu,reach=reference_average(queries,models,completed_iterations=80,weights_by_player=weights,
                guard=guard,device='cpu',**{k:v for k,v in ma.items() if k!='context_source'})
            error=float(np.max(abs(cpu-gpu)));reach_error=float(np.max(abs(reach-support)))
            assert error<1e-10 and reach_error<1e-8
            errors.append(dict(policy_error=error,own_reach_error=reach_error))
        immutable(control,dict(passed=True,bank_identities_sha256=identity,errors=errors,new_test_deals=0,
            artifacts={str(p.relative_to(STORE)):sha(p) for p in dest.iterdir() if p.is_file()}))
    else:
        proof=read(control);assert proof['passed'] and proof['bank_identities_sha256']==identity
        verify({str(STORE/p):h for p,h in proof['artifacts'].items()})
    del references;gc.collect()
    common_checkpoint=dict(registration_sha256=sha(REG),bank_identities_sha256=identity,context_source=source,guard=guard)
    if committed(STORE):sampler,comparison,routes,ref=restore_latest(STORE,total_deals=TEST_DEALS,seed=TEST_SEED,**common_checkpoint)
    else:
        sampler=PhysicalDeals(source,mode='full_deck',seed=TEST_SEED);c=json.loads(source)
        comparison=CompletePolicyComparison(stack=c['config']['stack'],dead_money=c['dead_money'],deals=TEST_DEALS)
        routes={};ref=publish(STORE,sampler=sampler,comparison=comparison,routes=routes,**common_checkpoint)
    archive=OwnedColumnarEvaluationArchive.create(STORE/('attempt-'+uuid.uuid4().hex),guard=guard)
    pool=ParallelArchives(archive,guard=guard,maximum_workers=4);metadata={};start=sampler.draws
    try:
        for offset in range(start,TEST_DEALS,32):
            guard();pool.wait_slot();name=f'test-{offset:06d}';status('fresh_policy_evaluation',completed_deals=offset,total_deals=TEST_DEALS)
            batch=dict(format=2,batch_id=NAME+'-'+name,seed=0,query_limit=100000,deals=sampler.sample(32)['deals'])
            folder=archive.begin(name);summary=evaluate_batch(batch=batch,folder=folder,**common);comparison.add(summary['values'])
            metadata[name]=dict(attempt=archive.root.name,owner_sha256=archive.owner_sha256,summary_sha256=sha(folder/'summary.json'));pool.submit(name)
            if (offset-start)//32%4==3 or offset+32==TEST_DEALS:
                for key,h in pool.drain().items():routes[key]=dict(metadata[key],manifest_sha256=h)
                ref=publish(STORE,sampler=sampler,comparison=comparison,routes=routes,**common_checkpoint)
        pool.close();pool=None
        analysis=comparison.finish();immutable(STORE/'analysis.json',analysis)
        return dict(deals=TEST_DEALS,seed=TEST_SEED,checkpoint=ref,analysis_sha256=sha(STORE/'analysis.json'),bank_identities_sha256=identity,routes=routes)
    finally:
        if pool is not None:pool.close()

def main(run=False,resume=False,wait=False):
    spec,args,cache_review=specification()
    if not run:
        print(json.dumps(dict(ready=True,training_started=False,source_boundary=78,final_boundary=80,arms=4,updates=8,
            qualification_updates_excluded=3,test_deals=TEST_DEALS,store=str(STORE),gpu=gpu_snapshot())),flush=True);return
    if resume:
        reg=read(REG);assert reg==spec;verify(reg['inputs']);assert not RESULT.exists()
    else:
        assert not REG.exists() and not RESULT.exists() and not STORE.exists();atomic_json(REG,spec);reg=spec
    began=time.monotonic();last=0.
    while True:
        ok,probe=available()
        if ok:break
        if time.monotonic()-last>60:status('waiting_for_resources',**probe);last=time.monotonic()
        if not wait or time.monotonic()-began>reg['maximum_initial_wait_seconds']:return
        time.sleep(15)
    acquired=False;guard=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;inventory=global_measure();allocated=sum(r['allocated_file_bytes'] for r in inventory)
        used=study_measure(STORE)['allocated_file_bytes'] if STORE.exists() else 0
        assert allocated+max(0,LIMIT-used)+RESERVE<=GLOBAL_LIMIT,'Global storage admission failed'
        if not STORE.exists():create(STORE)
        admission=STORE/('admission-'+uuid.uuid4().hex[:8]+'.json')
        atomic_json(admission,dict(registration_sha256=sha(REG),inventory=inventory,allocated_bytes=allocated,reserved_bytes=max(0,LIMIT-used)+RESERVE,
                                   pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),gpu=probe))
        verify(reg['inputs'])
        import torch
        assert torch.cuda.is_available() and all(a['config']['torch_version']==torch.__version__ and a['config']['numpy_version']==np.__version__ for a in reg['arms'].values())
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        guard=Guard();guard();cache=AllinCache(cache_review['cache_artifact'],cache_review['cache_sha256'])
        paired=train(reg,args,cache,guard);assessment=evaluate(reg,args,cache,guard)
        verify(reg['inputs']);guard();measurement=study_measure(STORE);assert measurement['logical_bytes']<LIMIT
        metrics=[]
        for name in BANK_ORDER:
            p=read(STORE/name/'progress.json');rows=[read(STORE/name/r['metrics']) for r in p['updates']]
            metrics.append(dict(arm=name,completed=p['completed'],checkpoint=p['checkpoint'],training_seconds=sum(r['seconds'] for r in rows),
                                competing_gpu_wait_seconds=sum(r['competing_gpu_wait_seconds'] for r in p['updates']),
                                generations=[dict(iteration=r['iteration'],seconds=r['seconds'],timings=r['timings']) for r in rows]))
        atomic_json(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),training=metrics,paired_controls=paired,evaluation=assessment,
            storage=measurement,seconds_this_invocation=time.monotonic()-guard.started,gpu_resource_wait_seconds=guard.wait_seconds,
            gpu_used=True,accuracy_qualified=False,independent_analysis_required=True,production_modified=False))
        status('complete_analysis_pending',result=str(RESULT));print(json.dumps(dict(complete=True,result=str(RESULT))),flush=True)
    except BaseException as error:
        path=OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json')
        atomic_json(path,dict(registration_sha256=sha(REG),error=repr(error),traceback=traceback.format_exc(),preserve_partial_attempts=True))
        status('interrupted',evidence=str(path));raise
    finally:
        if acquired:assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--wait',action='store_true')
    a=p.parse_args()
    if (a.resume or a.wait) and not a.run:p.error('--resume/--wait require --run')
    main(a.run,a.resume,a.wait)
