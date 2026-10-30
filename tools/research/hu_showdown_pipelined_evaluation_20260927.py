"""Execution-only pipelined continuation of the admitted fixed fresh study.

Control reuses old deals and checks all four full banks against CPU inference.
Study draws a sealed fresh stream only after all training/audits and controls.
No live training, partial-bank evaluation, model selection, or production edits.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from hu_paired_continuation_support_20260925 import setup_cuda,LOCK,OTHER
from hu_root_retained_storage_admitted_study_20260924 import measure,LIMIT,METADATA_RESERVE
from recovered_evaluation_runtime_v1 import guard_for
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from composite_showdown_bank_v1 import load_bank, training_gates
from action_integrated_policy_v1 import ActionIntegratedCpuBank64
from action_integrated_policy_shared_v1 import ActionIntegratedCudaBankShared64
from showdown_root_policy_v1 import ShowdownRootCpuBank64
from showdown_root_policy_shared_v1 import ShowdownRootCudaBankShared64
from crossed_complete_policy_batch_shared_v1 import evaluate_batch
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive
from sampled_physical_deals_v1 import PhysicalDeals
from complete_bank_root_stability_v1 import summarize as root_stability

TRAINING=('9266201-baseline','9266201-corrected','9266301-baseline','9266301-corrected')
PREFIXES={'study':'showdown-pipelined-evaluation-study-v1'}
OLD='showdown-composite-evaluation-study-v1'
SNAPSHOT='showdown-evaluation-resume-snapshot-v1'
from bounded_parallel_evaluation_archive_20260927 import ParallelArchives
from evaluation_resume_routing_20260927 import restore_accumulator
from showdown_evaluation_resume_snapshot_20260927 import restore_batch
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')

TEST_DEALS=65536
TEST_SEED=9267201
BATCH_SIZE=32


def worker(reg):
    setup_cuda();guard=pipeline_guard(reg);guard();start=time.monotonic()
    for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
    mode=reg['mode'];prefix=PREFIXES[mode];store=Path(reg['store'])
    assert reg['prefix']==prefix and reg['training_arms']==list(TRAINING)
    assert reg['deals']==(64 if mode=='control' else TEST_DEALS)
    assert reg['test_seed']==(None if mode=='control' else TEST_SEED) and reg['batch_size']==32
    context=OUT/'bb-context-candidate.json';source=context.read_text();args=bank_args(source)
    banks=[];cpu=[];identities=[];load_seconds=[]
    for name in TRAINING:
        began=time.monotonic()
        models,weights,identity=load_bank(OUT,name,completed=78,purpose='evaluation',bank_args=args,guard=guard)
        corrected=identity['treatment']=='corrected'
        cls=ShowdownRootCudaBankShared64 if corrected else ActionIntegratedCudaBankShared64
        banks.append(cls(models,weights,completed_iterations=78,models_per_chunk=8,guard=guard,**args))
        if mode=='control':
            cls=ShowdownRootCpuBank64 if corrected else ActionIntegratedCpuBank64
            cpu.append(cls(models,completed_iterations=78,weights_by_player=weights,**args))
        identities.append(identity);load_seconds.append(time.monotonic()-began);del models
    archives=OwnedColumnarEvaluationArchive.create(store,guard=guard)
    save(store/'bank-identities.json',identities)
    assert identities==read(Path(reg['original_store'])/'bank-identities.json')
    catalog=json.loads(args['catalog_source'])['native_observations']
    query=dict(context_source=source,observations=[r['observation'] for r in catalog])
    assert len(catalog)==265 and all(o['own_history']==[] for o in query['observations'])
    roots=[];root_checks=[]
    for k,bank in enumerate(banks):
        p,reach=bank.average(query,guard=guard)
        assert np.array_equal(reach,np.full(265,3081.))
        root=np.zeros((169,4));seen=set()
        for row,prob in zip(catalog,p):
            if row['player']==0:root[row['hand_class']]=prob;seen.add(row['hand_class'])
        assert seen==set(range(169));roots.append(root)
        if mode=='control':
            cp,cr=cpu[k].average(query,guard=guard)
            error=float(np.max(abs(cp-p)));assert error<1e-10 and np.array_equal(cr,reach)
            root_checks.append(dict(bank=k,maximum_policy_error=error))
    matrix=read(OUT/'preflop-allin-matrix-control-v1-matrix.json')
    mass=np.asarray(matrix['class_mass']).sum(1);mass/=mass.sum()
    save(store/'root-stability.json',root_stability(roots,mass))
    assert sha(store/'root-stability.json')==sha(Path(reg['original_store'])/'root-stability.json')
    cache=load_complete_cache();sampler=None
    # Replay the two already inspected control batches before any new deals.
    # This checks the actual resumed GPU banks, transport and native payoffs.
    from owned_columnar_evaluation_archive_v1 import restore
    control_result=read(OUT/'showdown-composite-evaluation-control-v1-result.json')
    control_store=Path(control_result['store'])
    replay=OwnedColumnarEvaluationArchive.create(store/'migration-control',guard=guard)
    control_checks=[]
    for name,expected in control_result['archive_manifest_hashes'].items():
        mp=control_store/(name+'.manifest.json');assert sha(mp)==expected
        original=restore(control_store/(name+'.xz'),read(mp),guard=guard)
        folder=replay.begin(name)
        evaluate_batch(batch=json.loads(original['query-batch.json']),folder=folder,context_path=context,banks=banks,cache=cache,
            query_executable=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
            evaluation_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',guard=guard)
        assert (folder/'profiles.json').read_bytes()==original['profiles.json']
        assert read(folder/'native.json')['profiles']==json.loads(original['native.json'])['profiles']
        identity=replay.publish(name);assert replay.release(name)==identity
        control_checks.append(dict(batch=name,profiles_byte_identical=True,native_profile_values_identical=True,manifest_sha256=identity))
    assert len(control_checks)==2
    save(store/'migration-control-result.json',dict(passed=True,deals=64,checks=control_checks,
        original_control_result_sha256=sha(OUT/'showdown-composite-evaluation-control-v1-result.json')))
    if mode=='study':
        sampler=PhysicalDeals(source,mode='full_deck',seed=TEST_SEED)
        save(store/'sampler-initial.json',sampler.checkpoint())
    else:
        reused=read(reg['reused_batch'])['deals'];assert len(reused)==64
    context_doc=json.loads(source)
    comparison=CompletePolicyComparison(stack=context_doc['config']['stack'],dead_money=context_doc['dead_money'],deals=reg['deals'])
    snapshot=read(OUT/f'{SNAPSHOT}-checkpoint.json')
    snapshot_result=read(OUT/f'{SNAPSHOT}-result.json')
    snapshot_reg=read(OUT/f'{SNAPSHOT}-registration.json')
    assert snapshot_result['passed'] and snapshot_result['registration_sha256']==sha(OUT/f'{SNAPSHOT}-registration.json')
    assert snapshot_result['checkpoint_sha256']==sha(OUT/f'{SNAPSHOT}-checkpoint.json')
    assert all(reg['original_manifest_hashes'][n]==h for n,h in snapshot_reg['manifests'].items())
    sampler=PhysicalDeals.restore(snapshot['sampler'],source)
    restore_accumulator(comparison,snapshot['series'],snapshot_result['completed_deals'])
    manifests=dict(reg['original_manifest_hashes']);summaries=dict(snapshot_result['batch_summary_hashes'])
    for offset in range(snapshot_result['completed_deals'],reg['original_completed_deals'],32):
        guard();name=f'test-{offset:06d}'
        _,batch,summary,digest,_=restore_batch((name,manifests[name]))
        assert batch==dict(format=2,batch_id=f'{OLD}-{name}',seed=0,query_limit=100000,deals=sampler.sample(32)['deals'])
        comparison.add(summary['values']);summaries[name]=digest
    assert sampler.draws==reg['original_completed_deals']
    save(store/'resume-sampler.json',sampler.checkpoint())
    cpu_checks=[];timings=np.zeros(4);native_seconds=0.;archive_bytes=0
    pool=ParallelArchives(archives,guard=guard,maximum_workers=4)

    try:
        for offset in range(reg['original_completed_deals'],reg['deals'],BATCH_SIZE):
            guard();pool.wait_slot();name=f'test-{offset:06d}'
            deals=sampler.sample(BATCH_SIZE)['deals'] if sampler else reused[offset:offset+BATCH_SIZE]
            batch=dict(format=2,batch_id=f'{OLD}-{name}',seed=0,query_limit=100000,deals=deals)
            folder=archives.begin(name)
            summary=evaluate_batch(batch=batch,folder=folder,context_path=context,banks=banks,cache=cache,
                query_executable=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
                evaluation_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',guard=guard)
            comparison.add(summary['values'])
            if mode=='control':
                query=read(folder/'queries.json');transport=read(folder/'profiles.json')
                for k,bank in enumerate(cpu):
                    cp,_=bank.average(query,guard=guard)
                    actual=np.asarray([r['probabilities'] for r in transport['profiles'][(0,3,4,7)[k]]['policies']])
                    error=float(np.max(abs(cp-actual)));assert error<1e-10
                    cpu_checks.append(dict(batch=name,bank=k,maximum_policy_error=error))
            summaries[name]=sha(folder/'summary.json')
            pool.submit(name)
            timings+=summary['averaging_seconds'];native_seconds+=summary['native_seconds']
            if offset//32%32==0:
                print(json.dumps(dict(deals=offset+32,total=reg['deals'],seconds=time.monotonic()-start)),flush=True)
        manifests.update(pool.drain())
    finally:
        pool.close()
    assert len(manifests)==2048 and len(summaries)==2048
    archive_bytes=sum(p.stat().st_size for p in store.glob('test-*') if p.is_file())
    analysis=comparison.finish();analysis.update(control_only=mode=='control');save(store/'analysis.json',analysis)
    if sampler:save(store/'sampler-final.json',sampler.checkpoint())
    for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
    logical=sum(p.stat().st_size for p in store.rglob('*') if p.is_file())
    assert logical<=reg['maximum_output_bytes']
    save(OUT/f'{prefix}-result.json',dict(passed=True,complete=True,mode=mode,deals=reg['deals'],store=str(store),
        original_registration_sha256=reg['original_registration_sha256'],original_completed_deals=reg['original_completed_deals'],
        migration_control_sha256=sha(store/'migration-control-result.json'),
        registration_sha256=sha(OUT/f'{prefix}-registration.json'),analysis_sha256=sha(store/'analysis.json'),
        bank_identities_sha256=sha(store/'bank-identities.json'),root_stability_sha256=sha(store/'root-stability.json'),
        archive_manifest_hashes=manifests,batch_summary_hashes=summaries,archive_owner_sha256=archives.owner_sha256,
        root_cpu_checks=root_checks,cpu_checks=cpu_checks,load_seconds=load_seconds,
        averaging_seconds=timings.tolist(),native_seconds=native_seconds,archive_bytes=archive_bytes,
        logical_bytes=logical,seconds=time.monotonic()-start,production_modified=False,accuracy_qualified=False,
        scope='Complete frozen policies and original game payoffs; fixed one-look comparison. Requires independent readback. No general accuracy or best-response bound.'))


def pipeline_guard(reg, *, gpu=True):
    started=time.monotonic(); last=last_size=0.
    store=Path(reg['store'])
    assert store==Path('S:/GTOpen-research')/PREFIXES['study']
    def guard():
        nonlocal last,last_size
        now=time.monotonic();assert now-started<reg['maximum_seconds']
        if now-last>2:
            assert idle() and not OTHER.exists()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert shutil.disk_usage('S:/').free>=40_000_000_000
            assert shutil.disk_usage('T:/').free>=1_000_000_000
            if gpu:
                import torch
                assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            last=now
        if now-last_size>10:
            paths=list(OUT.glob(reg['prefix']+'*'))
            if store.exists():paths.extend(store.rglob('*'))
            total=0
            for path in paths:
                try:
                    if path.is_file():total+=path.stat().st_size
                except FileNotFoundError:
                    # A successfully archived owned scratch member may disappear
                    # between enumeration and stat. Durable archives never may.
                    assert path.is_relative_to(store/'.batch-work')
            assert total<=reg['maximum_output_bytes']
            last_size=now
    return guard


def checks():
    for name in ('archive-parallel-control-20260927-result',
        'showdown-fast-decoder-controls-20260927','bounded-parallel-archive-control-20260927',
        'bounded-parallel-archive-negative-control-20260927','showdown-resume-routing-control-20260927'):
        assert read(OUT/(name+'.json'))['passed'],name
    for p,h in read(OUT/'showdown-resume-routing-control-20260927.json')['inputs'].items():assert sha(p)==h
    assert read(OUT/'showdown-fast-decoder-controls-20260927.json')['source_sha256']==sha(ROOT/'tools/research/crossed_profile_decoder_fast_candidate_20260927.py')
    assert read(OUT/'bounded-parallel-archive-control-20260927.json')['source_sha256']==sha(ROOT/'tools/research/bounded_parallel_evaluation_archive_20260927.py')
    snapshot=read(OUT/f'{SNAPSHOT}-result.json')
    assert snapshot['passed'] and snapshot['registration_sha256']==sha(OUT/f'{SNAPSHOT}-registration.json')
    assert snapshot['checkpoint_sha256']==sha(OUT/f'{SNAPSHOT}-checkpoint.json')
    for p,h in read(OUT/f'{SNAPSHOT}-registration.json')['inputs'].items():assert sha(p)==h


def transition():
    checks();assert idle() and not OTHER.exists()
    prefix=PREFIXES['study'];intent=OUT/f'{prefix}-interruption.json';assert not intent.exists()
    assert not (OUT/f'{OLD}-result.json').exists()
    admission=read(OUT/f'{OLD}-admission.json')
    identities=[]
    for role,key in (('--study','controller_pid'),('--worker','worker_pid')):
        p=psutil.Process(admission[key]);cmd=p.cmdline()
        assert p.is_running() and role in cmd
        assert any(Path(x).name=='hu_showdown_composite_evaluation_v1_20260927.py' for x in cmd)
        identities.append(dict(pid=p.pid,created=p.create_time(),command=cmd))
    assert psutil.Process(identities[1]['pid']).ppid()==identities[0]['pid']
    assert LOCK.read_text().strip()==str(identities[0]['pid'])
    reg=read(OUT/f'{OLD}-registration.json')
    assert admission['registration_sha256']==sha(OUT/f'{OLD}-registration.json')
    for p,h in reg['inputs'].items():assert sha(p)==h
    # Check conservative storage headroom before interrupting the original job.
    prepared=read(OUT/f'{SNAPSHOT}-result.json')['completed_deals']
    projected_suffix=int(np.ceil((reg['maximum_output_bytes']-64_000_000)*(65536-prepared)/65536))+192_000_000
    preflight_inventory=measure()
    assert sum(r['allocated_file_bytes'] for r in preflight_inventory)+projected_suffix+METADATA_RESERVE+64_000_000<=LIMIT
    assert shutil.disk_usage('S:/').free>=40_000_000_000+projected_suffix
    save(intent,dict(reason='User-requested execution speedup; preserve full sample and completed archives.',
        identities=identities,original_registration_sha256=sha(OUT/f'{OLD}-registration.json'),
        snapshot_result_sha256=sha(OUT/f'{SNAPSHOT}-result.json'),
        continuation_source_sha256=sha(Path(__file__)),production_modified=False))
    worker_process=psutil.Process(identities[1]['pid'])
    assert worker_process.create_time()==identities[1]['created']
    for child in reversed(worker_process.children(recursive=True)):
        try:child.terminate();child.wait(timeout=10)
        except psutil.NoSuchProcess:pass
    worker_process.terminate();worker_process.wait(timeout=20)
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        if (OUT/f'{OLD}-status.json').exists() and not LOCK.exists():break
        time.sleep(.5)
    status=read(OUT/f'{OLD}-status.json')
    assert status['state']=='failed' and status['exit_code']!=0 and not LOCK.exists()
    # The old supervisor must finish its failed completion gate before the new
    # controller takes ownership; it is never allowed to review partial data.
    old_handoff=OUT/'showdown-study-review-handoff-v1-status.json'
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        if old_handoff.exists() and read(old_handoff)['state']=='failed':break
        time.sleep(.5)
    assert read(old_handoff)['state']=='failed'


def run():
    checks();assert idle() and not LOCK.exists() and not OTHER.exists()
    prefix=PREFIXES['study'];rp=OUT/f'{prefix}-registration.json'
    store=Path('S:/GTOpen-research')/prefix
    assert not rp.exists() and not store.exists()
    original_rp=OUT/f'{OLD}-registration.json';old=read(original_rp)
    status=read(OUT/f'{OLD}-status.json')
    assert status['state']=='failed' and status['exit_code']!=0
    assert not (OUT/f'{OLD}-result.json').exists()
    assert (OUT/f'{prefix}-interruption.json').exists()
    oldstore=Path(old['store']);manifests={};packed={}
    for offset in range(0,65536,32):
        name=f'test-{offset:06d}';mp=oldstore/(name+'.manifest.json')
        if not mp.exists():break
        if (oldstore/'.batch-work'/name).exists():break
        manifests[name]=sha(mp);m=read(mp)
        assert sha(oldstore/(name+'.xz'))==m['packed_sha256'];packed[name]=m['packed_sha256']
        receipt=read(oldstore/'.batch-work'/(name+'.receipt.json'))
        assert receipt['manifest_sha256']==manifests[name]
    completed=32*len(manifests)
    assert read(OUT/f'{SNAPSHOT}-result.json')['completed_deals']<=completed<65536
    remaining=86400-status['seconds'];assert remaining>1800
    # Includes four queued scratch batches; all retained old partials are
    # already counted by the fresh global inventory below.
    cap=int(np.ceil((old['maximum_output_bytes']-64_000_000)*(65536-completed)/65536))+192_000_000
    inventory=measure();total=sum(r['allocated_file_bytes'] for r in inventory)
    assert total+cap+METADATA_RESERVE<=LIMIT
    assert shutil.disk_usage('S:/').free>=40_000_000_000+cap
    inputs=dict(old['inputs'])
    inputs.update({str(p):sha(p) for p in (ROOT/'tools/research').glob('*.py')})
    paths=[original_rp,OUT/f'{OLD}-status.json',OUT/f'{prefix}-interruption.json',
        OUT/'showdown-study-review-handoff-v1-status.json',OUT/'SHOWDOWN-PIPELINED-EVALUATION-CONTINUATION-PLAN.md']
    paths+=list(OUT.glob(f'{SNAPSHOT}-*.json'))
    for n in ('archive-parallel-control-20260927-result','showdown-fast-decoder-controls-20260927',
        'bounded-parallel-archive-control-20260927','bounded-parallel-archive-negative-control-20260927',
        'showdown-resume-routing-control-20260927'):
        paths.append(OUT/(n+'.json'))
    paths += [oldstore/n for n in ('bank-identities.json','root-stability.json','sampler-initial.json')]
    inputs.update({str(p):sha(p) for p in paths})
    reg=dict(old,inputs=inputs,prefix=prefix,store=str(store),original_store=str(oldstore),
        original_registration_sha256=sha(original_rp),original_manifest_hashes=manifests,
        original_packed_hashes=packed,original_completed_deals=completed,batch_id_prefix=OLD,
        storage_inventory=inventory,projected_allocated_bytes=total+cap+METADATA_RESERVE,
        maximum_output_bytes=cap,maximum_seconds=remaining,original_seconds=status['seconds'],
        production_modified=False,archive_workers=4)
    save(rp,reg);child=None;error=None;acquired=False;started=time.monotonic()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard=pipeline_guard(reg,gpu=False);guard()
        with (OUT/f'{prefix}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            save(OUT/f'{prefix}-admission.json',dict(controller_pid=os.getpid(),worker_pid=child.pid,
                registration_sha256=sha(rp),production_modified=False))
            while child.poll() is None:
                guard()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0,'Preserve interrupted continuation; no automatic retry'
        assert read(OUT/f'{prefix}-result.json')['passed']
    except BaseException as exc:error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            for descendant in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:descendant.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{prefix}-status.json',dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,seconds=time.monotonic()-started,production_modified=False))
    # One automatic review of the complete combined result; failure is retained.
    reviewer=ROOT/'tools/research/hu_showdown_pipelined_evaluation_review_20260927.py'
    with (OUT/f'{prefix}-review.log').open('x') as log:
        review=subprocess.run([sys.executable,str(reviewer),'study'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
            timeout=21720,creationflags=subprocess.CREATE_NO_WINDOW)
    assert review.returncode==0 and read(OUT/f'{prefix}-independent-review.json')['passed']


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f"{PREFIXES['study']}-registration.json"))
    else:
        assert sys.argv[1:]==['--transition-and-run']
        transition();run()
