"""Qualify real archived replay, interrupted-prefix recovery and all-class moments."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
from decimal import Decimal, localcontext
import json
from pathlib import Path
import shutil
import time
import psutil
from board_root_action_decomposition_v1 import NAMES, encoded
from board_root_action_replay_store_v1 import sha, attempt, commit, recover, verify_receipt, retire
from board_root_action_replay_worker_v1 import create_pool, wave, stop_pool
from board_root_action_statistics_v1 import Summary, Moments, PAIRS
from board_prefix_publication_v1 import atomic_json
from weighted_evaluation_readback_v1 import worker_guard

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-root-action-replay-control-v1';STORE=Path('S:/GTOpen-research')/PREFIX
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
BATCHES=['test-000000','test-032768']


def decimal_review(documents, summary):
    maximum=0.;checked=0
    for p,profile in enumerate(summary['profiles']):
        groups={c:[] for c in range(169)};all_rows=[]
        for doc in documents:
            for row in doc['profiles'][p]['deals']:
                q=row['action_values'];probs=row['root_probabilities']
                with localcontext() as ctx:
                    ctx.prec=40
                    values=[Decimal(str(x)) for action in q for x in action]
                    values += [Decimal(str(q[a][0]))-Decimal(str(q[b][0])) for a,b in PAIRS]
                    values += [sum(Decimal(str(probs[a]))*Decimal(str(q[a][k])) for a in range(4)) for k in range(3)]
                groups[row['native_class_index']].append(values);all_rows.append(values)
        for c,rows in [(-1,all_rows),*groups.items()]:
            saved=profile['overall'] if c < 0 else profile['classes'][c]
            assert saved['evaluation_count'] == len(rows)
            means=[x for a in saved['action_means'] for x in a]
            means += [r['mean_a_minus_b'] for r in saved['paired_BB_differences']]+saved['original_mixture_means']
            errors=[x for a in saved['action_standard_errors'] for x in a]
            errors += [r['standard_error'] for r in saved['paired_BB_differences']]+saved['original_mixture_standard_errors']
            if not rows:
                assert means == errors == [None]*21;continue
            with localcontext() as ctx:
                ctx.prec=40
                for k in range(21):
                    mean=sum(row[k] for row in rows)/len(rows)
                    delta=abs(float(mean)-means[k]);maximum=max(maximum,delta);assert delta < 1e-10
                    if len(rows) == 1:assert errors[k] is None
                    else:
                        se=(sum((row[k]-mean)**2 for row in rows)/(len(rows)-1)/len(rows)).sqrt()
                        delta=abs(float(se)-errors[k]);maximum=max(maximum,delta);assert delta < 1e-10
                    checked+=1
    return dict(maximum_error=maximum,moments_checked=checked,decimal_precision=40)


def main():
    started=time.monotonic();last=0.;pool=None;acquired=False
    def guard():
        nonlocal last
        assert time.monotonic()-started < 900
        if time.monotonic()-last > 2:worker_guard();last=time.monotonic()
    guard();assert not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    assert psutil.cpu_percent(interval=1) < 50
    bench_reg=OUT/'board-root-action-workers-v1-registration.json'
    bench_result=OUT/'board-root-action-workers-v1-result.json'
    bench_review=OUT/'board-root-action-workers-v1-review.json'
    br,bv,ba=[json.loads(p.read_bytes()) for p in (bench_reg,bench_result,bench_review)]
    assert bv['passed'] and ba['passed'] and bv['recommended_workers'] == ba['recommended_workers'] == 12
    assert ba['registration_sha256'] == bv['registration_sha256'] == sha(bench_reg) and ba['result_sha256'] == sha(bench_result)
    for p,h in br['inputs'].items():assert sha(p) == h
    original_control=json.loads((OUT/'board-root-action-control-v1-registration.json').read_bytes())
    for p,h in original_control['inputs'].items():assert sha(p) == h
    # The immediately preceding admitted benchmark reserved 2 GB. This bounded
    # control adds at most 0.5 GB, before fresh full-study storage admission.
    assert sum(r['allocated_file_bytes'] for r in br['global_inventory'])+2_500_000_000 < 800_000_000_000
    source_path=OUT/'weighted-complete-board-root-study-v1-result.json';source=json.loads(source_path.read_bytes())
    context=OUT/'bb-context-candidate.json';native=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    stability=Path(source['store'])/'root-stability.json'
    assert sha(stability) == source['root_stability_sha256']
    files=[Path(__file__),bench_reg,bench_result,bench_review,source_path,context,native,stability]
    files += [ROOT/'tools/research'/n for n in ('board_root_action_decomposition_v1.py','board_root_action_replay_store_v1.py',
        'board_root_action_replay_worker_v1.py','board_root_action_statistics_v1.py','board_prefix_publication_v1.py')]
    rp=OUT/(PREFIX+'-registration.json');assert not rp.exists()
    reg=dict(format=1,store=str(STORE),batches=BATCHES,source_store=source['store'],
        source_routes={n:source['routes'][n] for n in BATCHES},context_path=str(context),executable=str(native),
        root_stability_path=str(stability),inputs={str(p):sha(p) for p in files},maximum_seconds=900,
        maximum_additional_bytes=500_000_000,inventory_reference=str(bench_reg),unique_existing_deals=64,new_deals=0,
        checks=['original_reference_parity','uncommitted_complete_batch_excluded','new_attempt_resume',
            'changed_artifact_rejected','changed_source_route_rejected','reordered_prefix_rejected',
            'foreign_scratch_rejected','all_class_decimal_moments','duplicate_statistics_batch_rejected'])
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert not OTHER.exists();guard()
        atomic_json(rp,reg);identity=sha(rp);STORE.mkdir()
        atomic_json(STORE/'owner.json',dict(root=str(STORE),registration_sha256=identity))
        reference=commit(STORE,identity,BATCHES,{},None,{},reg['source_routes'],guard)
        first=attempt(STORE,identity);pool=create_pool(rp,2)
        done=wave(pool,first.name,BATCHES,guard)
        prefix={BATCHES[0]:done[BATCHES[0]]}
        reference=commit(STORE,identity,BATCHES,prefix,reference,{},reg['source_routes'],guard)
        before=sha(first/BATCHES[1]/'receipt.json')
        recovered,again=recover(STORE,identity,BATCHES,reg['source_routes'],guard)
        assert recovered == prefix and again == reference
        second=attempt(STORE,identity)
        new=wave(pool,second.name,[BATCHES[1]],guard)
        routes={**prefix,**new}
        reference=commit(STORE,identity,BATCHES,routes,reference,prefix,reg['source_routes'],guard)
        assert sha(first/BATCHES[1]/'receipt.json') == before
        assert recover(STORE,identity,BATCHES,reg['source_routes'],guard) == (routes,reference)
        documents=[]
        for n in BATCHES:
            _,folder=verify_receipt(STORE,identity,n,routes[n],reg['source_routes'][n])
            doc=json.loads((folder/'action-values.json').read_bytes());documents.append(doc)
            original=json.loads((Path('S:/GTOpen-research/board-root-action-control-v1')/n/'action-values.json').read_bytes())
            del original['maximum_replay_error'];assert doc == original
        assert (first/BATCHES[1]/'action-values.json').read_bytes() == (second/BATCHES[1]/'action-values.json').read_bytes()
        rejected=[]
        def rejects(label,fn):
            try:fn()
            except (ValueError,AssertionError):rejected.append(label)
            else:raise AssertionError('Failed to reject '+label)
        rejects('changed_source_route',lambda:verify_receipt(STORE,identity,BATCHES[0],routes[BATCHES[0]],{}))
        rejects('reordered_prefix',lambda:commit(STORE,identity,BATCHES,dict(reversed(list(routes.items()))),
            reference,routes,reg['source_routes'],guard))
        receipt=json.loads((first/BATCHES[0]/'receipt.json').read_bytes())
        rejects('foreign_scratch',lambda:retire(STORE,Path('S:/GTOpen-research/board-root-action-control-v1')/BATCHES[0],receipt))
        fixture=STORE/'corruption-fixture';fixture.mkdir()
        atomic_json(fixture/'owner.json',dict(root=str(fixture),registration_sha256=identity))
        target=attempt(fixture,identity);copy=target/BATCHES[0];copy.mkdir()
        for file in (first/BATCHES[0]).iterdir():shutil.copyfile(file,copy/file.name)
        with (copy/'action-values.json').open('ab') as f:f.write(b' ')
        rejects('changed_artifact',lambda:verify_receipt(fixture,identity,BATCHES[0],
            dict(attempt=target.name,receipt_sha256=sha(copy/'receipt.json')),reg['source_routes'][BATCHES[0]]))
        summary=Summary(BATCHES)
        for n,d in zip(BATCHES,documents):summary.add(n,d)
        stats=summary.finish();proof=decimal_review(documents,stats)
        rejects('duplicate_statistics_batch',lambda:summary.add(BATCHES[0],documents[0]))
        for p in stats['profiles']:
            assert len(p['classes']) == 169 and sum(c['evaluation_count'] for c in p['classes']) == 64
        m=Moments()
        for v in (1.,3.,5.):m.add([v]*21)
        assert m.n == 3 and all(abs(x-3.) < 1e-12 for x in m.mean)
        assert abs(m.finish()['action_standard_errors'][0][0]-(4/3)**.5) < 1e-12
        atomic_json(STORE/'summary.json',stats)
        pool.shutdown(wait=True);pool=None
        for p,h in reg['inputs'].items():assert sha(p) == h
        output=dict(passed=True,registration_sha256=identity,source_hashes_unchanged=True,
            unique_existing_deals=64,replayed_batch_jobs=3,new_deals=0,gpu_used=False,
            uncommitted_batch_preserved_and_excluded=True,resume_exact=True,original_control_values_exact=True,
            final_checkpoint=reference,summary_sha256=sha(STORE/'summary.json'),rejected=rejected,
            independent_decimal_moments=proof,sample_standard_error_control=True,
            bytes_retained=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()),seconds=time.monotonic()-started)
        assert output['bytes_retained'] < reg['maximum_additional_bytes']
        atomic_json(OUT/(PREFIX+'-result.json'),output);print(json.dumps(output),flush=True)
    finally:
        if pool is not None:stop_pool(pool);pool.shutdown(wait=True,cancel_futures=True)
        if acquired:
            assert LOCK.read_text() == str(os.getpid());LOCK.unlink()


if __name__ == '__main__':main()
