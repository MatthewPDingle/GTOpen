"""Prospective complete-bank comparison; --control must precede --study.

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
from compact_showdown_bank_v2 import load_bank
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
PREFIXES={k:f'showdown-complete-evaluation-{k}-v2' for k in ('control','study')}
TEST_DEALS=65536
TEST_SEED=9267201
BATCH_SIZE=32


def training_gates():
    rp=OUT/'showdown-matched-training-v1-registration.json'
    pp=OUT/'showdown-matched-training-v1-result.json'
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['terminal'] and result['registration_sha256']==sha(rp)
    assert [a['name'] for a in reg['arms']]==list(TRAINING)==[a['name'] for a in result['arms']]
    paths=[rp,pp]
    for arm in result['arms']:
        assert arm['completed_iterations']==78 and arm['final_restore_verified']
        name=arm['name'];prefix=f'showdown-training-readback-v2-{name}-0078'
        ar,ap=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
        audit=read(ap)
        assert audit['passed'] and audit['complete_arm'] and audit['completed_updates']==78
        assert audit['arm']==name and audit['source_registration_sha256']==sha(rp)
        assert audit['readback_registration_sha256']==sha(ar)
        paths.extend([ar,ap,Path(arm['store'])/'result.json'])
    return paths


def worker(reg):
    setup_cuda();guard=guard_for(reg);guard();start=time.monotonic()
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
    cache=load_complete_cache();sampler=None
    if mode=='study':
        sampler=PhysicalDeals(source,mode='full_deck',seed=TEST_SEED)
        save(store/'sampler-initial.json',sampler.checkpoint())
    else:
        reused=read(reg['reused_batch'])['deals'];assert len(reused)==64
    context_doc=json.loads(source)
    comparison=CompletePolicyComparison(stack=context_doc['config']['stack'],dead_money=context_doc['dead_money'],deals=reg['deals'])
    manifests={};summaries={};cpu_checks=[];timings=np.zeros(4);native_seconds=0.;archive_bytes=0
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
            for k,bank in enumerate(cpu):
                cp,_=bank.average(query,guard=guard)
                actual=np.asarray([r['probabilities'] for r in transport['profiles'][(0,3,4,7)[k]]['policies']])
                error=float(np.max(abs(cp-actual)));assert error<1e-10
                cpu_checks.append(dict(batch=name,bank=k,maximum_policy_error=error))
        summaries[name]=sha(folder/'summary.json')
        manifests[name]=archives.publish(name);assert archives.release(name)==manifests[name]
        archive_bytes+=(store/(name+'.xz')).stat().st_size+(store/(name+'.manifest.json')).stat().st_size
        timings+=summary['averaging_seconds'];native_seconds+=summary['native_seconds']
        if offset//32%32==0:
            print(json.dumps(dict(deals=offset+32,total=reg['deals'],seconds=time.monotonic()-start)),flush=True)
    analysis=comparison.finish();analysis.update(control_only=mode=='control');save(store/'analysis.json',analysis)
    if sampler:save(store/'sampler-final.json',sampler.checkpoint())
    for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
    logical=sum(p.stat().st_size for p in store.rglob('*') if p.is_file())
    assert logical<=reg['maximum_output_bytes']
    save(OUT/f'{prefix}-result.json',dict(passed=True,complete=True,mode=mode,deals=reg['deals'],store=str(store),
        registration_sha256=sha(OUT/f'{prefix}-registration.json'),analysis_sha256=sha(store/'analysis.json'),
        bank_identities_sha256=sha(store/'bank-identities.json'),root_stability_sha256=sha(store/'root-stability.json'),
        archive_manifest_hashes=manifests,batch_summary_hashes=summaries,archive_owner_sha256=archives.owner_sha256,
        root_cpu_checks=root_checks,cpu_checks=cpu_checks,load_seconds=load_seconds,
        averaging_seconds=timings.tolist(),native_seconds=native_seconds,archive_bytes=archive_bytes,
        logical_bytes=logical,seconds=time.monotonic()-start,production_modified=False,accuracy_qualified=False,
        scope='Complete frozen policies and original game payoffs; fixed one-look comparison. Requires independent readback. No general accuracy or best-response bound.'))


def run(mode):
    assert mode in PREFIXES and idle() and not LOCK.exists() and not OTHER.exists()
    prefix=PREFIXES[mode];store=Path('S:/GTOpen-research')/prefix
    rp=OUT/f'{prefix}-registration.json';assert not store.exists() and not rp.exists()
    paths=training_gates()
    for gate in ('columnar-evaluation-archive-control-v1','shared-query-gpu-control-v1',
                 'compact-showdown-bank-control-v2','completed-object-retention-control-v1'):
        gr,gp=[OUT/f'{gate}-{s}.json' for s in ('registration','result')]
        assert read(gp)['passed'] and read(gp)['registration_sha256']==sha(gr);paths.extend([gr,gp])
    shared_review=OUT/'shared-query-gpu-control-v1-independent-review.json'
    assert read(shared_review)['passed'] and read(shared_review)['source_result_sha256']==sha(OUT/'shared-query-gpu-control-v1-result.json')
    paths.append(shared_review)
    old_path=OUT/'action-integrated-replication-v1-result.json';old=read(old_path)
    metric=Path(old['store'])/'iteration-0001/metrics.json';assert sha(metric)==old['steps'][0]['metrics_sha256']
    reused=metric.parent/'batch-00/batch.json';assert sha(reused)==read(metric)['subbatches'][0]['artifacts']['batch']
    paths.extend([old_path,metric,reused,OUT/'SHOWDOWN-COMPLETE-EVALUATION-PLAN.md',
        OUT/'bb-context-candidate.json',OUT/'preflop-allin-matrix-control-v1-matrix.json',
        ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
        ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'])
    cap=60_000_000;projection=None
    if mode=='study':
        cp=PREFIXES['control'];cr,cv,ca=[OUT/f'{cp}-{s}.json' for s in ('registration','result','independent-review')]
        control,audit=read(cv),read(ca)
        assert control['passed'] and control['mode']=='control' and control['deals']==64
        assert control['registration_sha256']==sha(cr) and audit['passed'] and audit['source_result_sha256']==sha(cv)
        assert len(control['cpu_checks'])==8 and max(r['maximum_policy_error'] for r in control['cpu_checks'])<1e-10
        assert len(control['root_cpu_checks'])==4 and max(r['maximum_policy_error'] for r in control['root_cpu_checks'])<1e-10
        projection=int(np.ceil(control['archive_bytes']*TEST_DEALS/64*1.25))+64_000_000
        assert projection<=2_500_000_000,'Rework retention before drawing any fresh deals'
        cap=projection;paths.extend([cr,cv,ca])
    inventory=measure();total=sum(r['allocated_file_bytes'] for r in inventory)
    assert total+cap+METADATA_RESERVE<=LIMIT,'Evaluation not admitted: preserve existing evidence'
    assert shutil.disk_usage('S:/').free>=40_000_000_000+cap
    inputs={str(p):sha(p) for p in (ROOT/'tools/research').glob('*.py')}
    inputs.update({str(p):sha(p) for p in paths})
    reg=dict(inputs=inputs,prefix=prefix,mode=mode,store=str(store),training_arms=list(TRAINING),
        deals=64 if mode=='control' else TEST_DEALS,test_seed=None if mode=='control' else TEST_SEED,
        batch_size=BATCH_SIZE,reused_batch=str(reused),storage_inventory=inventory,
        projected_allocated_bytes=total+cap+METADATA_RESERVE,storage_projection=projection,
        maximum_output_bytes=cap,maximum_seconds=14400 if mode=='control' else 86400,
        production_modified=False,stopping='Fixed sample, one final look; resource or user-activity guards may stop without a complete result.')
    save(rp,reg);child=None;error=None;acquired=False;started=time.monotonic()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard=guard_for(reg,gpu=False);guard()
        with (OUT/f'{prefix}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',mode],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            save(OUT/f'{prefix}-admission.json',dict(controller_pid=os.getpid(),worker_pid=child.pid,
                registration_sha256=sha(rp),production_modified=False))
            while child.poll() is None:
                guard()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0,'Preserve incomplete attempt; no automatic retry'
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


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker' and sys.argv[2] in PREFIXES:
        worker(read(OUT/f'{PREFIXES[sys.argv[2]]}-registration.json'))
    else:
        assert len(sys.argv)==2 and sys.argv[1] in ('--control','--study')
        run(sys.argv[1][2:])
