"""Policy-bound trace parity, postflop-only ingestion, and reservoir RNG controls."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2')
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from hu_paired_continuation_support_20260925 import guard_for,launch
from exact_initial_training_ingest_v2 import InitialTargets,ingest as initial_ingest,digest
from later_action_training_ingest_v1 import ingest
from sampled_physical_reservoir_v1 import PhysicalReservoir,checked_row

PREFIX='later-action-ingest-control-v1'
STORE=Path('T:/GTOpen-research')/PREFIX
TRACE=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
CAPACITY=97


def fingerprint(reservoirs):
    h=hashlib.sha256()
    for r in reservoirs:
        h.update(str(r.seen).encode());h.update(json.dumps(r.rng.bit_generator.state,sort_keys=True).encode())
        for k in ('keys','active','arity','values','iterations'):h.update(getattr(r,k).tobytes())
    return h.hexdigest()


def worker(reg):
    started=time.monotonic();guard=guard_for(reg,gpu=False);guard()
    store=Path(reg['store']);store.mkdir(exist_ok=False)
    previous=read(OUT/'later-action-trace-control-v1-registration.json')
    oldstore=Path(previous['store']);trial=read(reg['trials'][1]['result'])
    cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    mp=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix_source=mp.read_text()
    cache=load_complete_cache()
    base=[PhysicalReservoir(CAPACITY,p,381103+p,source) for p in range(2)]
    actual=copy.deepcopy(base);oracle=copy.deepcopy(base)
    rows=[];rejected=[];changed_total=0
    for iteration in reg['iterations']:
        guard();folder=Path(trial['store'])/f'iteration-{iteration:04d}';fixture=folder/'batch-00'
        dest=store/f'iteration-{iteration:04d}';dest.mkdir()
        tp=dest/'trace.json'
        p=subprocess.run([str(TRACE),str(cp),str(fixture/'batch.json'),str(fixture/'policies.json'),str(tp)],
            capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        assert p.returncode==0,p.stderr[-2000:]
        trace=read(tp);oldtrace=read(oldstore/f'iteration-{iteration:04d}/trace.json')
        assert trace['format']==2 and trace['method']=='all-node-action-trace-v2'
        assert trace['policy_source']==(fixture/'policies.json').read_text()
        assert {k:v for k,v in trace.items() if k not in ('format','method','policy_source')}=={
            k:v for k,v in oldtrace.items() if k not in ('format','method')}
        queries,updates,policies=[read(fixture/f'{n}.json') for n in ('queries','updates','policies')]
        frozen=read(folder/'current-initial-policy.json')
        targets=InitialTargets(matrix_source,source,frozen['root'],frozen['calls'],matrix_sha256=sha(mp),generation=iteration-1)
        hashes=[digest(v) for v in (queries,updates,policies,trace)]
        counts,initial_audit=initial_ingest(queries,updates,policies,base,iteration,cache,targets,guard=guard)
        nc,na,audit=ingest(queries,updates,policies,actual,iteration,cache,targets,trace,guard=guard)
        assert nc==counts and na==initial_audit
        corrections={r['record']:r['advantages'] for r in initial_audit['bb_root_corrections']}
        nodes=[{n['query']:n for n in d['nodes']} for d in trace['traces']]
        heads=[i for i,r in enumerate(updates['records']) if queries['observations'][r[0]]['hi']=='1']
        group=0;changed=0;postflop=0;preflop=0;phases=set();expected_witnesses=[]
        for i,(qi,player,tag,values) in enumerate(updates['records']):
            while group+1<len(heads) and i>=heads[group+1]:group+=1
            if tag<=0:continue
            obs=queries['observations'][qi]
            if obs['phase']>0:
                did,updater=divmod(group,2);assert updater==player
                node=nodes[did][qi];probs=policies['policies'][qi]['probabilities']
                expected=math.fsum(probs[a]*node['action_values'][a][player] for a in range(tag))
                new=[node['action_values'][a][player]-expected if a<tag else 0. for a in range(4)]
                changed+=int(max(abs(a-b) for a,b in zip(new,values))>1e-10)
                postflop+=1;phases.add(obs['phase']);expected_witnesses.append(i)
            else:
                new=corrections.get(i,values);preflop+=1
            oracle[player]._insert(checked_row(obs,new),iteration)
        assert [r['record'] for r in audit['postflop_replacements']]==expected_witnesses
        assert phases=={1,2,3} and changed>0 and preflop>0
        worst=0.
        for b,a,o in zip(base,actual,oracle):
            assert b.seen==a.seen==o.seen and b.rng.bit_generator.state==a.rng.bit_generator.state==o.rng.bit_generator.state
            assert a.seen>CAPACITY
            for name in ('keys','active','arity','iterations'):
                assert np.array_equal(getattr(b,name),getattr(a,name)) and np.array_equal(getattr(o,name),getattr(a,name))
            worst=max(worst,float(np.max(abs(a.values-o.values))))
            pre=(a.keys[:,0]>>np.uint64(63))==0
            assert np.array_equal(a.values[pre],b.values[pre])
        assert worst<1e-10
        assert hashes==[digest(v) for v in (queries,updates,policies,trace)]
        save(dest/'initial-audit.json',initial_audit);save(dest/'postflop-audit.json',audit)
        row=dict(iteration=iteration,counts=counts,postflop_targets=postflop,changed_postflop_targets=changed,
            preserved_preflop_targets=preflop,phases=sorted(phases),maximum_oracle_error=worst,
            metadata_and_rng_identical=True,preflop_retained_values_identical=True,v1_v2_trace_values_identical=True)
        rows.append(row);changed_total+=changed;print(json.dumps(row),flush=True)
        if iteration==reg['iterations'][0]:
            def reject(name,bad):
                before=fingerprint(actual)
                try:ingest(queries,updates,policies,actual,iteration,cache,targets,bad,guard=guard)
                except (ValueError,KeyError,TypeError):pass
                else:raise AssertionError('Accepted invalid trace: '+name)
                assert fingerprint(actual)==before
                rejected.append(name)
            reject('unbound old trace',dict(trace,format=1,method='all-node-action-trace-v1'))
            reject('missing policy identity',{k:v for k,v in trace.items() if k!='policy_source'})
            reject('different policy',dict(trace,policy_source='{}'))
            reject('different batch',dict(trace,batch_source='{}'))
            reject('missing target',dict(trace,conditional_targets=trace['conditional_targets'][:-1]))
            bad=copy.deepcopy(trace);bad['conditional_targets'][-1]['deal']+=1;reject('moved physical deal',bad)
            bad=copy.deepcopy(trace);bad['conditional_targets'][-1]['advantages'][0]+=1;reject('uncentered late target',bad)
    for path,h in reg['inputs'].items():guard();assert sha(path)==h,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        fixtures=rows,rejections=rejected,total_changed_postflop_targets=changed_total,
        artifacts={str(p):sha(p) for p in store.rglob('*') if p.is_file()},seconds=time.monotonic()-started,
        production_modified=False,training_started=False,accuracy_qualified=False,
        scope='Saved-batch ingestion control with forced reservoir replacement. No trained model or range improvement claim.'))


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:]==['--run']
        review=OUT/'later-action-trace-control-v1-independent-review.json';assert read(review)['passed']
        result=read(OUT/'action-integrated-replication-v1-result.json')
        extras=[str(TRACE),str(review),str(ROOT/'crates/solver/examples/hu_sampled_action_trace_v2.rs')]
        extras.extend(str(p) for p in (ROOT/'crates/solver/examples/research_sampled').glob('*.rs'))
        control=read(OUT/'later-action-trace-control-v1-result.json')
        extras.extend([str(OUT/'later-action-trace-control-v1-result.json'),str(OUT/'later-action-trace-control-v1-registration.json')])
        extras.extend(control['artifacts'])
        for iteration in (1,26,78):
            folder=Path(result['store'])/f'iteration-{iteration:04d}';mp=folder/'metrics.json'
            assert sha(mp)==result['steps'][iteration-1]['metrics_sha256'];metric=read(mp);extras.append(str(mp))
            fp=folder/'current-initial-policy.json';assert sha(fp)==metric['initial_policy_sha256'];extras.append(str(fp))
            for name in ('batch','queries','policies','updates'):
                p=folder/'batch-00'/f'{name}.json'
                assert sha(p)==metric['subbatches'][0]['artifacts'][name];extras.append(str(p))
        launch(Path(__file__).resolve(),PREFIX,dict(extra_inputs=extras,iterations=[1,26,78],store=str(STORE),
            scope='Postflop-only derived targets, exact initial overrides preserved, scalar oracle and atomic negative tests.'),
            cap=256_000_000,seconds=1800)
