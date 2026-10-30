"""Fixed same-card factorial comparison of the two full played continuations."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import numpy as np
from later_average_support_v1 import OUT,read,weights,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_batch_protocol_v2 import policy_document
from hu_action_integrated_exact_20260925 import load_bank,bank_args
from action_integrated_policy_bulk_v1 import ActionIntegratedCudaBankBulk64
from hu_paired_continuation_support_20260925 import launch,setup_cuda,guard_for
from paired_continuation_statistics_v1 import summarize,PROFILES
from owned_batch_archive_v1 import OwnedBatchArchive

PREFIX='paired-continuation-v1'
STORE=Path('T:/GTOpen-research')/PREFIX
OLD=Path('T:/GTOpen-research/root-retained-wider-study-v1/evaluation')
COUNT=169*64


def invoke(name,args,guard):
    guard()
    run=subprocess.run([str(ROOT/'target/release/examples'/f'{name}.exe'),*map(str,args)],
        cwd=ROOT,capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    assert run.returncode==0,run.stderr[-2000:]
    guard()


def batch_values(batch,folder,guard,banks,cache,expected_roots):
    folder.mkdir(exist_ok=False)
    context=OUT/'bb-context-candidate.json'
    raw=folder/'query-batch.json';labelled=folder/'conditional-batch.json'
    qp=folder/'queries.json';pp=folder/'profiles.json';npth=folder/'native.json'
    save(raw,batch);labels=cache.batch(batch);save(labelled,labels);cache.check_batch(labels)
    invoke('hu_sampled_bank_bridge',['queries',context,raw,'-',qp],guard)
    query=read(qp)
    assert query['context_source']==context.read_text() and query['batch_source']==raw.read_text()
    obs=query['observations'];actors=np.array([o['actor'] for o in obs])
    roots=[i for i,o in enumerate(obs) if o['phase']==0 and int(o['hi'])==1]
    assert roots and all(obs[i]['actor']==0 and obs[i]['n']==4 and obs[i]['own_history']==[] for i in roots)
    policies=[];coverage=[];timings=[]
    for bank,expected in zip(banks,expected_roots):
        guard();before=time.monotonic();p,support=bank.average(query,guard=guard)
        timings.append(time.monotonic()-before);policies.append(p)
        root_rows=[]
        for i in roots:
            lo=int(obs[i]['lo']);c=hand_class([lo&63,(lo>>6)&63])
            assert np.max(abs(p[i]-np.asarray(expected[c])))<1e-10
            root_rows.append(dict(query=i,hand_class=c,probabilities=p[i].tolist()))
        coverage.append(dict(probabilities_sha256=hashlib.sha256(p.tobytes()).hexdigest(),
            support_sha256=hashlib.sha256(support.tobytes()).hexdigest(),roots=root_rows,
            rows_by_actor_phase=[[int(sum(o['actor']==a and o['phase']==s for o in obs)) for s in range(4)] for a in range(2)],
            zero_reach_by_actor_phase=[[int(sum(o['actor']==a and o['phase']==s and support[i]==0 for i,o in enumerate(obs))) for s in range(4)] for a in range(2)]))
    profiles=[]
    for label,(a,b) in zip(PROFILES,((0,0),(0,1),(1,0),(1,1))):
        mixed=np.where((actors==0)[:,None],policies[a],policies[b])
        for action,name in ((1,'call'),(2,'raise')):
            changed=mixed.copy();changed[roots]=0.;changed[roots,action]=1.
            profiles.append(dict(name=f'{label}-{name}',policies=policy_document(query,changed)['policies']))
    save(pp,dict(format=1,context_source=query['context_source'],batch_source=labelled.read_text(),profiles=profiles))
    before=time.monotonic()
    invoke('hu_sampled_profile_allin_evaluation_v1',[context,labelled,pp,npth],guard)
    native_seconds=time.monotonic()-before
    native=read(npth)
    assert native['format']==2 and native['terminal_estimator']=='conditional-preflop-allin-v1'
    assert native['postflop_outcomes']=='sampled-board'
    assert [p['name'] for p in native['profiles']]==[p['name'] for p in profiles]
    assert native['maximum_forward_cashflow_error']<1e-10 and native['maximum_conservation_error']<1e-10
    n=len(batch['deals']);assert all(len(p['deals'])==n for p in native['profiles'])
    values=np.asarray([[d['values'][0] for d in p['deals']] for p in native['profiles']]).T.reshape(n,4,2)
    context_doc=json.loads(query['context_source']);stack=context_doc['config']['stack']
    assert np.isfinite(values).all() and np.all(values>=-stack-1e-10) and np.all(values<=stack+context_doc['dead_money']+1e-10)
    summary=dict(format=1,purpose='paired-continuation-diagnostic',classes=[hand_class(d[:2]) for d in batch['deals']],
        values=values.tolist(),profile_order=list(PROFILES),action_order=['call','raise'],
        coverage=coverage,averaging_seconds=timings,native_seconds=native_seconds,
        allin_cache_sha256=cache.sha256,maximum_forward_cashflow_error=native['maximum_forward_cashflow_error'],
        maximum_conservation_error=native['maximum_conservation_error'],
        artifacts={p.name:sha(p) for p in (raw,labelled,qp,pp,npth)})
    save(folder/'summary.json',summary)
    return summary


def worker(reg):
    setup_cuda();guard=guard_for(reg);guard();started=time.monotonic()
    source=(OUT/'bb-context-candidate.json').read_text();args=bank_args(source)
    banks=[];loading=[];expected=[]
    for t,endpoint in zip(reg['trials'],reg['endpoint_policies']):
        guard();before=time.monotonic()
        models=load_bank(read(t['registration']),read(t['audit']),source,78)
        banks.append(ActionIntegratedCudaBankBulk64(models,weights('linear',78),completed_iterations=78,guard=guard,**args))
        loading.append(time.monotonic()-before);del models
        policy=read(endpoint);assert policy['played_generations']==list(range(78)) and policy['excluded_generation']==78
        assert policy['weights']==weights('linear',78).tolist()
        assert policy['checkpoint']==read(t['result'])['final_checkpoint']
        expected.append(policy['root_probabilities'])
    cache=load_complete_cache();sampled=read(OLD/'training-deals.json')
    masses=sampled['original_class_masses'];deals=sampled['deals'][:COUNT]
    assert sampled['hand_classes'][:COUNT]==list(range(169))*64
    STORE.mkdir(exist_ok=False);archives=OwnedBatchArchive.create(STORE,guard=guard)
    all_values=[];manifests={};summaries={};phase_seconds=[0.,0.];native_seconds=0.
    for offset in range(0,COUNT,32):
        guard();name=f'train-{offset:06d}'
        batch=dict(format=2,batch_id=f'{PREFIX}-{name}',seed=0,query_limit=100000,deals=deals[offset:offset+32])
        folder=archives.begin(name)
        summary=batch_values(batch,folder,guard,banks,cache,expected)
        assert summary['classes']==sampled['hand_classes'][offset:offset+32]
        all_values.extend(summary['values']);summaries[name]=sha(folder/'summary.json')
        manifests[name]=archives.publish(name);assert archives.release(name)==manifests[name]
        phase_seconds=[x+y for x,y in zip(phase_seconds,summary['averaging_seconds'])]
        native_seconds+=summary['native_seconds']
        if offset//32%16==0:
            print(json.dumps(dict(deals=offset+32,total=COUNT,seconds=time.monotonic()-started)),flush=True)
    analysis=summarize(all_values,masses)
    save(STORE/'analysis.json',analysis)
    for path,digest in reg['inputs'].items():guard();assert sha(path)==digest,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        deals=COUNT,per_class=64,batches=len(manifests),store=str(STORE),analysis_sha256=sha(STORE/'analysis.json'),
        archive_manifest_hashes=manifests,batch_summary_hashes=summaries,archive_owner_sha256=archives.owner_sha256,
        loading_seconds=loading,averaging_seconds=phase_seconds,native_seconds=native_seconds,
        seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,
        scope='Reused class-balanced deals and crossed frozen full-bank continuations; descriptive policy sensitivity, not a fresh strength test or proof of error in either seed.'))


def run():
    control=OUT/'bulk-average-control-v2-result.json'
    assert read(control)['passed'] and all(t['byte_identical'] for t in read(control)['trials'])
    assert read(control)['registration_sha256']==sha(OUT/'bulk-average-control-v2-registration.json')
    assert read(OUT/'bulk-average-control-v2-status.json')['state']=='complete'
    extra=[control,OUT/'bulk-average-control-v2-registration.json',
        OUT/'PAIRED-CONTINUATION-DIAGNOSTIC-PLAN.md',OLD/'training-deals.json',OLD/'result.json',
        OUT/'root-retained-wider-study-v1-evaluation.json',OUT/'root-retained-wider-study-v1-independent-review.json']
    ev=read(extra[-2]);assert ev['result_sha256']==sha(OLD/'result.json')
    assert read(extra[-1])['passed'] and read(extra[-1])['evaluation_sha256']==sha(extra[-2])
    extra.extend([OUT/'bulk-average-control-v2-status.json',
        ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
        ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
        OUT/'complete-private-allin-cache-v2-registration.json',
        OUT/'complete-private-allin-cache-v2-result.json',
        OUT/'complete-private-allin-cache-v2-independent-review.json'])
    detail=read(OLD/'result.json');sampled=read(OLD/'training-deals.json')
    assert sampled['per_class']==256 and sampled['hand_classes']==list(range(169))*256
    # Authenticate every reused physical deal against the previously audited outputs.
    for at in range(0,COUNT,64):
        part=OLD/f'train-{at:06d}';sp=part/'summary.json';bp=part/'query-batch.json'
        assert sha(sp)==detail['batch_summary_hashes'][part.name]
        assert sha(bp)==read(sp)['artifacts']['query-batch.json']
        assert read(bp)['deals']==sampled['deals'][at:at+64]
        extra.extend([sp,bp])
    endpoints=[]
    for name in ('first','replication'):
        ep=OUT/f'action-integrated-{name}-exact-v1-result.json'
        audit=OUT/f'action-integrated-{name}-exact-v1-independent-review.json'
        assert read(audit)['passed'] and read(audit)['result_sha256']==sha(ep)
        policy=Path(f'T:/GTOpen-research/action-integrated-{name}-exact-v1/linear-policy.json')
        assert read(ep)['artifacts'][str(policy)]==sha(policy)
        endpoints.append(str(policy));extra.extend([ep,audit,policy])
    launch(Path(__file__).resolve(),PREFIX,dict(store=str(STORE),endpoint_policies=endpoints,
        extra_inputs=list(map(str,extra)),deals=COUNT,per_class=64,batch_size=32,
        scope='Frozen four-profile factorial diagnostic; same previously inspected physical deals, no new training or holdout.'),
        cap=4_000_000_000,seconds=7200)


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:]==['--run'];run()
