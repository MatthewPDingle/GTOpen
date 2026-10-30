"""Prospective complete-policy evaluation after both matched trials pass audit.

--control reuses previously inspected deals and checks CPU/CUDA complete banks.
--study requires that control and uses the prospectively fixed unseen seed.
No root action forcing, checkpoint selection, or production deployment.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import sys
import time
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from hu_paired_continuation_support_20260925 import launch,setup_cuda,guard_for
from hu_action_integrated_exact_20260925 import bank_args
from frozen_complete_trial_bank_v1 import load_completed_trial
from action_integrated_policy_bulk_v1 import ActionIntegratedCudaBankBulk64
from action_integrated_policy_v1 import ActionIntegratedCpuBank64
from crossed_complete_policy_batch_v1 import evaluate_batch
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from sampled_physical_deals_v1 import PhysicalDeals
from owned_batch_archive_v1 import OwnedBatchArchive
from ntfs_research_storage_v1 import measure_tree
from complete_bank_root_stability_v1 import summarize as root_stability

TRAINING=('action-integrated-fresh-pilot-v1','later-action-matched-first-v1',
          'action-integrated-replication-v1','later-action-matched-replication-v1')
PREFIXES={'control':'later-action-complete-evaluation-control-v1',
          'study':'later-action-complete-evaluation-study-v1'}
TEST_DEALS=65536
TEST_SEED=382921
BATCH_SIZE=32


def worker(reg):
    setup_cuda();guard=guard_for(reg);guard();start=time.monotonic()
    mode=reg['mode'];prefix=PREFIXES[mode];store=Path(reg['store'])
    assert reg['prefix']==prefix and reg['training_prefixes']==list(TRAINING)
    assert reg['deals']==(64 if mode=='control' else TEST_DEALS)
    assert reg['test_seed']==(None if mode=='control' else TEST_SEED)
    context=OUT/'bb-context-candidate.json';source=context.read_text();args=bank_args(source)
    banks=[];cpu_banks=[];identities=[];load_seconds=[]
    for name in TRAINING:
        guard();began=time.monotonic()
        models,weights,identity=load_completed_trial(OUT,name,expected_updates=78,bank_args=args,guard=guard)
        banks.append(ActionIntegratedCudaBankBulk64(models,weights,completed_iterations=78,
            models_per_chunk=8,guard=guard,**args))
        if mode=='control':
            cpu_banks.append(ActionIntegratedCpuBank64(models,completed_iterations=78,
                weights_by_player=weights,**args))
        identities.append(identity);load_seconds.append(time.monotonic()-began)
        del models
    # Every policy history is frozen before the first fresh draw.
    cache=load_complete_cache();store.mkdir(exist_ok=False)
    save(store/'bank-identities.json',identities)
    catalog=json.loads(args['catalog_source'])['native_observations']
    query=dict(context_source=source,observations=[r['observation'] for r in catalog])
    assert len(catalog)==265 and all(o['own_history']==[] for o in query['observations'])
    roots=[];root_cpu_checks=[]
    for k,bank in enumerate(banks):
        p,reach=bank.average(query,guard=guard)
        assert np.array_equal(reach,np.full(265,3081.))
        root=np.zeros((169,4));seen=set()
        for row,prob in zip(catalog,p):
            if row['player']==0:root[row['hand_class']]=prob;seen.add(row['hand_class'])
        assert seen==set(range(169));roots.append(root)
        if mode=='control':
            cp,cr=cpu_banks[k].average(query,guard=guard)
            error=float(np.max(abs(cp-p)));assert error<1e-10 and np.array_equal(cr,reach)
            root_cpu_checks.append(dict(bank=k,maximum_policy_error=error))
    matrix=read(OUT/'preflop-allin-matrix-control-v1-matrix.json')
    mass=np.asarray(matrix['class_mass']).sum(1);mass/=mass.sum()
    save(store/'root-stability.json',root_stability(roots,mass))
    sampler=None
    if mode=='study':
        sampler=PhysicalDeals(source,mode='full_deck',seed=TEST_SEED)
        save(store/'sampler-initial.json',sampler.checkpoint())
    else:
        reused=read(reg['reused_batch'])['deals'];assert len(reused)==64
    archives=OwnedBatchArchive.create(store,guard=guard)
    context_doc=json.loads(source)
    comparison=CompletePolicyComparison(stack=context_doc['config']['stack'],
        dead_money=context_doc['dead_money'],deals=reg['deals'])
    manifests={};summaries={};cpu_checks=[];timings=np.zeros(4);native_seconds=0.
    for offset in range(0,reg['deals'],BATCH_SIZE):
        guard();name=f'test-{offset:06d}'
        deals=sampler.sample(BATCH_SIZE)['deals'] if sampler else reused[offset:offset+BATCH_SIZE]
        batch=dict(format=2,batch_id=f'{prefix}-{name}',seed=0,query_limit=100000,deals=deals)
        folder=archives.begin(name)
        summary=evaluate_batch(batch=batch,folder=folder,context_path=context,banks=banks,cache=cache,
            query_executable=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
            evaluation_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',guard=guard)
        comparison.add(summary['values'])
        if mode=='control':
            query=read(folder/'queries.json');transport=read(folder/'profiles.json')
            for k,bank in enumerate(cpu_banks):
                guard();p,s=bank.average(query,guard=guard)
                # Pure old/old and new/new profiles preserve both actors' rows.
                actual=np.asarray([r['probabilities'] for r in transport['profiles'][(0,3,4,7)[k]]['policies']])
                error=float(np.max(abs(p-actual)));assert error<1e-10
                cpu_checks.append(dict(batch=name,bank=k,maximum_policy_error=error))
        summaries[name]=sha(folder/'summary.json')
        manifests[name]=archives.publish(name);assert archives.release(name)==manifests[name]
        timings+=summary['averaging_seconds'];native_seconds+=summary['native_seconds']
        if offset//BATCH_SIZE%32==0:
            print(json.dumps(dict(deals=offset+BATCH_SIZE,total=reg['deals'],seconds=time.monotonic()-start)),flush=True)
    analysis=comparison.finish();analysis.update(control_only=mode=='control')
    save(store/'analysis.json',analysis)
    if sampler:save(store/'sampler-final.json',sampler.checkpoint())
    for path,h in reg['inputs'].items():guard();assert sha(path)==h,path
    storage=measure_tree(store,guard)
    assert storage['allocated_file_bytes']<=reg['maximum_output_bytes']
    save(OUT/f'{prefix}-result.json',dict(passed=True,complete=True,
        registration_sha256=sha(OUT/f'{prefix}-registration.json'),deals=reg['deals'],mode=mode,
        store=str(store),analysis_sha256=sha(store/'analysis.json'),
        bank_identities_sha256=sha(store/'bank-identities.json'),archive_manifest_hashes=manifests,
        root_stability_sha256=sha(store/'root-stability.json'),root_cpu_checks=root_cpu_checks,
        batch_summary_hashes=summaries,archive_owner_sha256=archives.owner_sha256,
        cpu_checks=cpu_checks,load_seconds=load_seconds,averaging_seconds=timings.tolist(),
        native_seconds=native_seconds,storage=storage,seconds=time.monotonic()-start,
        production_modified=False,accuracy_qualified=False,
        scope='Crossed complete policies, fixed deals and one final look. Requires independent readback. No best-response bound or general accuracy claim.'))


def run(mode):
    prefix=PREFIXES[mode];extra=[]
    # Require both full histories and their independent reviews before admission.
    for name in TRAINING:
        paths=[OUT/f'{name}-{s}.json' for s in ('registration','result','independent-review','readback-registration')]
        reg,result,audit,readback=map(read,paths)
        assert result['passed'] and result['terminal'] and result['completed_iterations']==78
        assert audit['passed'] and audit['completed_updates']==78
        assert result['registration_sha256']==audit['source_registration_sha256']==sha(paths[0])
        assert audit['source_result_sha256']==sha(paths[1]) and audit['readback_registration_sha256']==sha(paths[3])
        extra.extend(paths)
    for gate in ('crossed-complete-policy-control-v1','crossed-trained-bank-control-v1'):
        rp,pp=[OUT/f'{gate}-{s}.json' for s in ('registration','result')]
        assert read(pp)['passed'] and read(pp)['registration_sha256']==sha(rp);extra.extend([rp,pp])
    old=read(OUT/'action-integrated-replication-v1-result.json')
    metric=Path(old['store'])/'iteration-0001/metrics.json'
    assert sha(metric)==old['steps'][0]['metrics_sha256']
    reused=metric.parent/'batch-00/batch.json'
    assert sha(reused)==read(metric)['subbatches'][0]['artifacts']['batch']
    extra.extend([metric,reused,OUT/'LATER-ACTION-MATCHED-STUDY-PLAN.md',
        OUT/'CROSSED-COMPLETE-POLICY-COMPARISON-CONTROLS.md',
        ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
        ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'])
    cap=40_000_000;projection=None
    if mode=='study':
        control=PREFIXES['control']
        rp,pp,ap=[OUT/f'{control}-{s}.json' for s in ('registration','result','independent-review')]
        result,audit=read(pp),read(ap)
        assert result['passed'] and result['mode']=='control' and result['deals']==64
        assert result['registration_sha256']==sha(rp) and audit['passed'] and audit['source_result_sha256']==sha(pp)
        assert len(result['cpu_checks'])==8 and max(r['maximum_policy_error'] for r in result['cpu_checks'])<1e-10
        assert len(result['root_cpu_checks'])==4 and max(r['maximum_policy_error'] for r in result['root_cpu_checks'])<1e-10
        # Set capacity before seeing test deals; 50% margin over the final-bank pilot.
        projection=int(result['storage']['logical_bytes']*TEST_DEALS/64*1.5)+20_000_000
        assert projection<=12_000_000_000,'Rework evidence storage before any fresh sampling'
        cap=max(8_000_000_000,projection);extra.extend([rp,pp,ap])
    key='GTOPEN_CROSSED_EVALUATION_PREFIX';previous=os.environ.get(key);os.environ[key]=prefix
    try:
        launch(Path(__file__).resolve(),prefix,dict(mode=mode,store=str(Path('T:/GTOpen-research')/prefix),
            training_prefixes=list(TRAINING),deals=64 if mode=='control' else TEST_DEALS,
            test_seed=None if mode=='control' else TEST_SEED,batch_size=BATCH_SIZE,
            reused_batch=str(reused),extra_inputs=list(map(str,extra)),
            storage_projection_with_50pct_margin=projection,
            scope='Fixed complete-profile comparison. Control uses previously inspected deals; study draws its sealed fresh seed only after all banks are frozen.'),
            cap=cap,seconds=14400 if mode=='control' else 21600)
    finally:
        if previous is None:os.environ.pop(key,None)
        else:os.environ[key]=previous


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:
        prefix=os.environ.get('GTOPEN_CROSSED_EVALUATION_PREFIX');assert prefix in PREFIXES.values()
        worker(read(OUT/f'{prefix}-registration.json'))
    else:
        assert len(sys.argv)==2 and sys.argv[1] in ('--control','--study')
        run(sys.argv[1][2:])
