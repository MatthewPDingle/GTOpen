"""Independent archive/transport reconstruction and Decimal all-class readback.

Uses saved native results; does not claim an independent poker engine or neural
inference. Reconstructs the exact forced input digest without the replay adapter.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
from decimal import Decimal, getcontext
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import time
import psutil
from weighted_routed_evaluation_readback_v1 import RoutedReader
from board_root_action_replay_store_v1 import recover,verify_receipt,sha
from board_root_action_replay_worker_v1 import stop_pool
from board_prefix_publication_v1 import atomic_json
from weighted_evaluation_readback_v1 import worker_guard

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
ACTIONS=('fold','call','raise','jam')
NAMES=tuple(s+':'+p for s in ('first','replication') for p in
    ('oldBB-oldBTN','oldBB-newBTN','newBB-oldBTN','newBB-newBTN'))
PAIRS=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
STATE=None


def read(path):return json.loads(Path(path).read_bytes())


def hand_class(cards):
    a,b=cards;low,high=sorted((a//4,b//4))
    return high*13+low if a % 4 == b % 4 or low == high else low*13+high


def initialize(registration):
    global STATE
    getcontext().prec=40
    audit=read(registration);reg=read(audit['replay_registration'])
    for p,h in audit['inputs'].items():
        # Large original registrations are hashed only once per worker.
        assert sha(p) == h,p
    source=read(audit['original_result']);old_store=Path(source['store'])
    reader=RoutedReader(old_store,source['routes'],guard=lambda:None)
    STATE=audit,reg,reader,old_store,read(reg['root_stability_path'])


def chunk(names):
    start=time.monotonic();audit,reg,reader,old_store,roots=STATE
    store=Path(reg['store']);identity=sha(audit['replay_registration'])
    moments={};proofs=[]
    def guard():
        assert time.monotonic()-start < 360 and psutil.virtual_memory().available > 20_000_000_000
    for name in names:
        guard()
        receipt,folder=verify_receipt(store,identity,name,audit['replay_routes'][name],reg['source_routes'][name])
        members={n:reader.read_bytes(old_store/name/n) for n in
            ('query-batch.json','conditional-batch.json','queries.json','profiles.json','native.json','summary.json','residuals.json')}
        for n,b in members.items():assert hashlib.sha256(b).hexdigest() == receipt['source_artifact_sha256'][n]
        source=json.loads(members['profiles.json']);queries=json.loads(members['queries.json'])
        deals=json.loads(members['query-batch.json'])['deals'];saved=json.loads(members['native.json'])
        assert len(deals) == 32 and all(len(d) == len(set(d)) == 9 and all(0 <= x < 52 for x in d) for d in deals)
        assert tuple(p['name'] for p in source['profiles']) == tuple(p['name'] for p in saved['profiles']) == NAMES
        assert source['context_source'] == Path(reg['context_path']).read_bytes().decode()
        assert source['batch_source'] == members['conditional-batch.json'].decode()
        assert queries['context_source'] == source['context_source']
        assert queries['batch_source'] == members['query-batch.json'].decode()
        obs=queries['observations'];indices={};by_class={}
        for i,o in enumerate(obs):
            if o['hi'] != '1':continue
            assert o['actor'] == 0 and o['phase'] == 0 and o['n'] == 4 and o['own_history'] == []
            lo=int(o['lo']);assert lo >> 42 == 0 and all((lo >> (6*k)) & 63 == 63 for k in range(2,7))
            c=hand_class([lo & 63,(lo >> 6) & 63]);assert c not in by_class
            indices[i]=c;by_class[c]=i
        assert set(by_class) == {hand_class(d[:2]) for d in deals}
        forced_profiles=[]
        for p in source['profiles']:
            assert len(p['policies']) == len(obs)
            for a,label in enumerate(ACTIONS):
                rows=[]
                for i,row in enumerate(p['policies']):
                    if i in indices:
                        assert all(row[k] == obs[i][k] for k in ('hi','lo','actor','n'))
                        row={**row,'probabilities':[float(k == a) for k in range(4)]}
                    rows.append(row)
                forced_profiles.append(dict(name=p['name']+':root-'+label,policies=rows))
        transport={**source,'profiles':forced_profiles}
        forced_hash=hashlib.sha256(json.dumps(transport,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        assert forced_hash == receipt['scratch_sha256']['forced-profiles.json']
        assert hashlib.sha256(members['conditional-batch.json']).hexdigest() == receipt['scratch_sha256']['conditional-batch.json']
        native=read(folder/'native.json');compact=read(folder/'action-values.json')
        assert native['format'] == 2 and native['fixed_policy_evaluation_only'] and not native['bounds_best_response_above']
        assert native['terminal_estimator'] == 'conditional-preflop-allin-v1' and native['postflop_outcomes'] == 'sampled-board'
        assert len(native['profiles']) == 32 and tuple(p['name'] for p in compact['profiles']) == NAMES
        assert compact['columns'] == ['BB_bb_per_entry','BTN_bb_per_entry','expected_rake_bb']
        for field in ('maximum_conservation_error','maximum_forward_cashflow_error'):
            assert 0 <= native[field] < 1e-10
        dead=Decimal(str(json.loads(source['context_source'])['dead_money']))
        mixture_error=Decimal(0)
        for p,label in enumerate(NAMES):
            assert len(compact['profiles'][p]['deals']) == len(saved['profiles'][p]['deals']) == 32
            for a,action in enumerate(ACTIONS):
                assert native['profiles'][p*4+a]['name'] == label+':root-'+action
                assert len(native['profiles'][p*4+a]['deals']) == 32
            for did,deal in enumerate(deals):
                c=hand_class(deal[:2]);row=compact['profiles'][p]['deals'][did]
                probs=source['profiles'][p]['policies'][by_class[c]]['probabilities']
                assert row['deal_index'] == did and row['native_class_index'] == c and row['root_probabilities'] == probs
                donor=(p//4)*2+int(p % 4 >= 2)
                assert max(abs(a-b) for a,b in zip(probs,roots['root_probabilities'][donor][c])) < 1e-12
                assert len(row['action_values']) == 4 and all(len(q) == 3 for q in row['action_values'])
                q=[]
                for a in range(4):
                    outcome=native['profiles'][p*4+a]['deals'][did]
                    assert outcome['deal_index'] == did and abs(outcome['terminal_mass']-1) < 1e-12
                    values=[*outcome['values'],outcome['expected_rake']]
                    assert values == row['action_values'][a] and all(math.isfinite(x) for x in values)
                    values=list(map(lambda x:Decimal(str(x)),values));q.append(values)
                    assert values[2] >= 0 and abs(sum(values)-dead) < Decimal('1e-10')
                mixed=[sum(Decimal(str(probs[a]))*q[a][k] for a in range(4)) for k in range(3)]
                old=saved['profiles'][p]['deals'][did]
                assert old['deal_index'] == did
                error=max(abs(x-Decimal(str(y))) for x,y in zip(mixed,[*old['values'],old['expected_rake']]))
                assert error < Decimal('1e-10');mixture_error=max(mixture_error,error)
                vector=[v for action in q for v in action]+[q[a][0]-q[b][0] for a,b in PAIRS]+mixed
                key=p*169+c
                if key not in moments:moments[key]=[0,[Decimal(0)]*21,[Decimal(0)]*21]
                m=moments[key];m[0]+=1
                for k,v in enumerate(vector):m[1][k]+=v;m[2][k]+=v*v
        proofs.append(dict(name=name,receipt_sha256=audit['replay_routes'][name]['receipt_sha256'],
            forced_transport_sha256=forced_hash,policy_rows=len(obs)*32,
            maximum_decimal_mixture_error=str(mixture_error),deals=32))
    return dict(proofs=proofs,moments={str(k):[n,list(map(str,s)),list(map(str,q))] for k,(n,s,q) in moments.items()},
        seconds=time.monotonic()-start)


def check_moments(saved,n,sums,squares):
    assert saved['evaluation_count'] == n
    means=[v for a in saved['action_means'] for v in a]
    means += [d['mean_a_minus_b'] for d in saved['paired_BB_differences']]+saved['original_mixture_means']
    errors=[v for a in saved['action_standard_errors'] for v in a]
    errors += [d['standard_error'] for d in saved['paired_BB_differences']]+saved['original_mixture_standard_errors']
    assert [(d['action_a'],d['action_b']) for d in saved['paired_BB_differences']] == [(ACTIONS[a],ACTIONS[b]) for a,b in PAIRS]
    if n == 0:
        assert means == errors == [None]*21;return 0.
    maximum=0.
    for k in range(21):
        mean=sums[k]/n;delta=abs(float(mean)-means[k]);assert delta < 1e-10;maximum=max(maximum,delta)
        if n == 1:assert errors[k] is None
        else:
            numerator=squares[k]-sums[k]*sums[k]/n
            assert numerator >= Decimal('-1e-24')
            error=(max(Decimal(0),numerator)/(n-1)/n).sqrt()
            delta=abs(float(error)-errors[k]);assert delta < 1e-10;maximum=max(maximum,delta)
    return maximum


def main(control=False,run=False):
    getcontext().prec=40
    target='board-root-action-replay-control-v1' if control else 'board-root-action-replay-v1'
    prefix='board-root-action-replay-readback-control-v1' if control else 'board-root-action-replay-readback-v1'
    rp=OUT/(target+'-registration.json');pp=OUT/(target+('-result.json' if control else '-replay.json'))
    if not run:
        print(json.dumps(dict(ready=rp.exists() and pp.exists(),control=control,review_not_run=True,gpu_used=False)))
        return
    started=time.monotonic();last=0.;pool=None;acquired=False
    def guard():
        nonlocal last
        assert time.monotonic()-started < 3600
        if time.monotonic()-last > 2:worker_guard();last=time.monotonic()
    guard();assert psutil.virtual_memory().available > 28_000_000_000
    reg,result=read(rp),read(pp);assert result['registration_sha256'] == sha(rp)
    if control:
        assert result['passed']
    else:
        assert result['replay_finished'] and result['independent_review_required']
    for p,h in reg['inputs'].items():guard();assert sha(p) == h,p
    qualification=[]
    if not control:
        proof_path=OUT/'board-root-action-replay-readback-control-v1-result.json'
        proof_registration=OUT/'board-root-action-replay-readback-control-v1-registration.json'
        proof=read(proof_path)
        assert proof['passed'] and proof['deals'] == 64 and proof['reviewer_sha256'] == sha(Path(__file__))
        assert proof['readback_registration_sha256'] == sha(proof_registration)
        for p,h in read(proof_registration)['inputs'].items():
            guard();assert sha(p) == h,p
        qualification=[proof_path,proof_registration]
        assert psutil.cpu_percent(interval=1) < 30 and not LOCK.exists() and not OTHER.exists()
    store=Path(reg['store']);summary_path=store/'summary.json'
    assert sha(summary_path) == result['summary_sha256']
    routes,checkpoint=recover(store,sha(rp),reg['batches'],reg['source_routes'],guard)
    assert checkpoint == result['final_checkpoint'] and list(routes) == reg['batches']
    original=OUT/'weighted-complete-board-root-study-v1-result.json'
    assert sha(original) == reg['inputs'][str(original)]
    files=[rp,pp,summary_path,store/checkpoint['file'],original,Path(__file__),*qualification]
    files += [ROOT/'tools/research'/n for n in ('weighted_routed_evaluation_readback_v1.py',
        'owned_columnar_evaluation_archive_v1.py','crossed_profile_columnar_v1.py','crossed_profile_columnar_v2.py',
        'board_root_action_replay_store_v1.py')]
    audit_path=OUT/(prefix+'-registration.json');destination=OUT/(prefix+'-result.json')
    assert not audit_path.exists() and not destination.exists()
    workers=2 if control else 12
    audit=dict(format=1,inputs={**reg['inputs'],**{str(p):sha(p) for p in files}},replay_registration=str(rp),
        original_result=str(original),replay_routes=routes,workers=workers,chunk_batches=16,
        maximum_seconds=3600,decimal_precision=40,deals=len(routes)*32,gpu_used=False,new_deals=0,
        scope='All source archives, reconstructed forced-input digests, native outcomes, physical class identities and descriptive moments; no independent poker engine.')
    try:
        if not control:
            with LOCK.open('x') as f:f.write(str(os.getpid()))
            acquired=True;assert not OTHER.exists()
        atomic_json(audit_path,audit)
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize,initargs=(str(audit_path),))
        groups=[reg['batches'][i:i+16] for i in range(0,len(routes),16)]
        futures=[pool.submit(chunk,names) for names in groups]
        totals={};proofs=[];maximum_mixture=Decimal(0)
        for index,future in enumerate(futures):
            while True:
                guard()
                try:part=future.result(timeout=1);break
                except concurrent.futures.TimeoutError:pass
            assert [p['name'] for p in part['proofs']] == groups[index]
            proofs.extend(part['proofs'])
            maximum_mixture=max(maximum_mixture,max(Decimal(p['maximum_decimal_mixture_error']) for p in part['proofs']))
            for key,(n,s,q) in part['moments'].items():
                key=int(key);assert 0 <= key < 8*169 and n > 0 and len(s) == len(q) == 21
                if key not in totals:totals[key]=[0,[Decimal(0)]*21,[Decimal(0)]*21]
                t=totals[key];t[0]+=n
                for k in range(21):t[1][k]+=Decimal(s[k]);t[2][k]+=Decimal(q[k])
            if (index+1) % 8 == 0:print(json.dumps(dict(verified_deals=len(proofs)*32,total_deals=len(routes)*32)),flush=True)
        pool.shutdown(wait=True);pool=None
        summary=read(summary_path);maximum_statistics=0.;counts=[]
        assert summary['deals'] == len(routes)*32 and summary['batches'] == len(routes)
        assert summary['all_classes_included'] and summary['exploratory'] and not summary['accuracy_qualified']
        assert not summary['bounds_best_response_above'] and tuple(summary['action_order']) == ACTIONS
        assert tuple(p['name'] for p in summary['profiles']) == NAMES
        roots=read(reg['root_stability_path'])
        for p,profile in enumerate(summary['profiles']):
            assert len(profile['classes']) == 169
            combined=[0,[Decimal(0)]*21,[Decimal(0)]*21];current=[]
            for c,saved in enumerate(profile['classes']):
                assert saved['native_class_index'] == c
                n,s,q=totals.get(p*169+c,[0,[Decimal(0)]*21,[Decimal(0)]*21]);current.append(n)
                maximum_statistics=max(maximum_statistics,check_moments(saved,n,s,q))
                if n:
                    donor=(p//4)*2+int(p % 4 >= 2)
                    assert max(abs(a-b) for a,b in zip(saved['root_probabilities'],roots['root_probabilities'][donor][c])) < 1e-12
                else:assert saved['root_probabilities'] is None
                combined[0]+=n
                for k in range(21):combined[1][k]+=s[k];combined[2][k]+=q[k]
            assert sum(current) == len(routes)*32
            if counts:assert current == counts
            else:counts=current
            maximum_statistics=max(maximum_statistics,check_moments(profile['overall'],*combined))
        for p,h in audit['inputs'].items():guard();assert sha(p) == h,p
        output=dict(passed=True,complete=True,readback_registration_sha256=sha(audit_path),
            source_registration_sha256=sha(rp),source_replay_sha256=sha(pp),reviewer_sha256=sha(Path(__file__)),
            deals=len(routes)*32,batches=len(routes),all_classes_checked=169,profiles_checked=8,
            source_forced_transports_reconstructed=True,policy_rows_verified=sum(p['policy_rows'] for p in proofs),
            maximum_decimal_mixture_error=str(maximum_mixture),maximum_statistics_error=maximum_statistics,
            class_evaluation_counts=counts,batch_proofs=proofs,seconds=time.monotonic()-started,
            independent_poker_engine=False,new_neural_inference=False,gpu_used=False,new_deals=0,
            accuracy_qualified=False,scientific_interpretation_pending=True)
        atomic_json(destination,output)
        print(json.dumps({k:v for k,v in output.items() if k not in ('batch_proofs','class_evaluation_counts')}),flush=True)
    finally:
        if pool is not None:stop_pool(pool);pool.shutdown(wait=True,cancel_futures=True)
        if acquired:
            assert LOCK.read_text() == str(os.getpid());LOCK.unlink()


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--control',action='store_true');parser.add_argument('--run',action='store_true')
    args=parser.parse_args();main(args.control,args.run)
