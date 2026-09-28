"""Fixed full-sample root-only diagnostic. Default mode never starts work."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import argparse
import json
from pathlib import Path
import time
import uuid
import psutil
from board_root_action_replay_store_v1 import sha, attempt, commit, recover, verify_receipt
from board_root_action_replay_worker_v1 import create_pool, wave, stop_pool
from board_root_action_statistics_v1 import Summary
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import measure as study_measure
from global_research_inventory_v2 import measure as global_measure
from weighted_evaluation_readback_v1 import worker_guard
from board_root_action_decomposition_v1 import encoded

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-root-action-replay-v1';STORE=Path('S:/GTOpen-research')/PREFIX
REG=OUT/(PREFIX+'-registration.json')
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
BATCHES=[f'test-{i:06d}' for i in range(0,65536,32)]


def read(path):return json.loads(Path(path).read_bytes())


def qualify():
    cr,cp=[OUT/f'board-root-action-replay-control-v1-{s}.json' for s in ('registration','result')]
    control=read(cp)
    assert control['passed'] and control['registration_sha256'] == sha(cr)
    assert control['resume_exact'] and control['uncommitted_batch_preserved_and_excluded']
    assert control['original_control_values_exact'] and control['independent_decimal_moments']['maximum_error'] < 1e-10
    assert control['sample_standard_error_control'] and control['unique_existing_deals'] == 64
    assert control['rejected'] == ['changed_source_route','reordered_prefix','foreign_scratch','changed_artifact','duplicate_statistics_batch']
    for p,h in read(cr)['inputs'].items():assert sha(p) == h
    br,bp,ba=[OUT/f'board-root-action-workers-v1-{s}.json' for s in ('registration','result','review')]
    bench,audit=read(bp),read(ba)
    assert bench['passed'] and audit['passed'] and bench['recommended_workers'] == audit['recommended_workers'] == 12
    assert bench['registration_sha256'] == audit['registration_sha256'] == sha(br) and audit['result_sha256'] == sha(bp)
    for p,h in read(br)['inputs'].items():assert sha(p) == h
    for p,h in read(OUT/'board-root-action-control-v1-registration.json')['inputs'].items():assert sha(p) == h
    return [cr,cp,br,bp,ba]


def main(run=False,resume=False):
    paths=qualify()
    if not run:
        print(json.dumps(dict(qualified=True,workers=12,deals=65536,fresh_deals=0,gpu_used=False,
            fresh_resource_and_storage_admission_required=True,full_replay_launched=False)))
        return
    started=time.monotonic();deadline=time.time()+7200;last=0.;pool=None;acquired=False;run_folder=None
    def guard():
        nonlocal last
        assert time.time() < deadline,'Registered replay deadline reached'
        if time.monotonic()-last > 2:
            worker_guard();assert not OTHER.exists(),'Another research owner has priority'
            assert psutil.disk_usage('S:/').free > 10_000_000_000
            last=time.monotonic()
    guard();assert not LOCK.exists()
    cpu=psutil.cpu_percent(interval=1);assert cpu < 30 and psutil.virtual_memory().available > 28_000_000_000
    replay_path=OUT/(PREFIX+'-replay.json')
    assert not replay_path.exists(),'Replay already finished; complete the independent review instead'
    if resume:
        reg=read(REG);assert reg['batches'] == BATCHES and reg['store'] == str(STORE)
        deadline=reg['deadline_unix'];guard()
        for p,h in reg['inputs'].items():assert sha(p) == h
    else:
        assert not REG.exists() and not STORE.exists(),'Preserve prior registration; use explicit resume'
        original_path=OUT/'weighted-complete-board-root-study-v1-result.json'
        original=read(original_path);source_store=Path(original['store'])
        checkpoint=source_store/original['checkpoint']['file']
        assert sha(checkpoint) == original['checkpoint']['sha256']
        assert read(checkpoint)['routes'] == original['routes'] and set(original['routes']) == set(BATCHES)
        context=OUT/'bb-context-candidate.json'
        executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
        stability=source_store/'root-stability.json';assert sha(stability) == original['root_stability_sha256']
        files=paths+[Path(__file__),original_path,checkpoint,context,executable,stability,
            OUT/'BOARD-ROOT-ACTION-REPLAY-PLAN.md',OUT/'BOARD-ROOT-ACTION-DECOMPOSITION-PLAN.md']
        files += [ROOT/'tools/research'/n for n in ('board_root_action_decomposition_v1.py',
            'board_root_action_replay_worker_v1.py','board_root_action_replay_store_v1.py','board_root_action_statistics_v1.py',
            'owned_columnar_evaluation_archive_v1.py','crossed_profile_columnar_v1.py','crossed_profile_columnar_v2.py',
            'board_prefix_publication_v1.py','board_study_storage_v1.py','global_research_inventory_v2.py')]
        reg=dict(format=1,store=str(STORE),source_store=str(source_store),source_routes=original['routes'],
            source_checkpoint=original['checkpoint'],batches=BATCHES,deals=65536,fresh_deals=0,workers=12,wave_batches=32,
            context_path=str(context),executable=str(executable),root_stability_path=str(stability),
            inputs={str(p):sha(p) for p in files},maximum_allocated_bytes=4_000_000_000,
            maximum_logical_bytes=4_000_000_000,global_storage_limit=800_000_000_000,
            maximum_batch_scratch_bytes=90_000_000,maximum_completed_batch_bytes=1_000_000,
            deadline_unix=deadline,maximum_seconds=7200,initial_cpu_percent=cpu,
            gpu_used=False,production_modified=False,exploratory=True,accuracy_qualified=False,
            stopping='Every original batch, independent of outcomes. Resource interruptions preserve the same committed prefix.',
            statistical_scope='Root-only action values, original complete averaged continuation policies fixed.')
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard()
        inventory=global_measure()
        existing=study_measure(STORE,guard)['allocated_file_bytes'] if resume else 0
        reserve=max(0,reg['maximum_allocated_bytes']-existing)+2_000_000_000
        assert sum(r['allocated_file_bytes'] for r in inventory)+reserve <= reg['global_storage_limit']
        guard()
        if not resume:
            reg['admission']=dict(roots=inventory,reserved_bytes=reserve)
            atomic_json(REG,reg);STORE.mkdir()
            atomic_json(STORE/'owner.json',dict(root=str(STORE),registration_sha256=sha(REG)))
            routes={};reference=commit(STORE,sha(REG),BATCHES,{},None,{},reg['source_routes'],guard)
        else:
            routes,reference=recover(STORE,sha(REG),BATCHES,reg['source_routes'],guard)
        identity=sha(REG);run_folder=attempt(STORE,identity)
        atomic_json(run_folder/'admission.json',dict(roots=inventory,reserved_bytes=reserve,
            resumed=resume,completed_batches=len(routes),pid=os.getpid(),created=psutil.Process().create_time()))
        print(json.dumps(dict(state='replaying',pid=os.getpid(),created=psutil.Process().create_time(),
            workers=reg['workers'],completed_deals=len(routes)*32,total_deals=65536,
            registration_sha256=identity,attempt=run_folder.name)),flush=True)
        pool=create_pool(REG,reg['workers'])
        while len(routes) < len(BATCHES):
            guard();remaining=len(BATCHES)-len(routes);storage=study_measure(STORE,guard)
            transient=min(reg['workers'],remaining)*reg['maximum_batch_scratch_bytes']
            retained=min(reg['wave_batches'],remaining)*reg['maximum_completed_batch_bytes']
            assert storage['allocated_file_bytes']+transient+retained < reg['maximum_allocated_bytes']
            assert storage['logical_bytes']+transient+retained < reg['maximum_logical_bytes']
            names=BATCHES[len(routes):len(routes)+reg['wave_batches']]
            added=wave(pool,run_folder.name,names,guard)
            next_routes={**routes,**added}
            reference=commit(STORE,identity,BATCHES,next_routes,reference,routes,reg['source_routes'],guard)
            routes=next_routes
            print(json.dumps(dict(state='replaying',completed_deals=len(routes)*32,total_deals=65536,
                elapsed_seconds=time.monotonic()-started,checkpoint=reference)),flush=True)
        pool.shutdown(wait=True);pool=None
        # Read committed evidence in the registered order for deterministic moments.
        restored,again=recover(STORE,identity,BATCHES,reg['source_routes'],guard)
        assert restored == routes and again == reference
        summary=Summary(BATCHES);maximum=0.
        for name in BATCHES:
            guard();receipt,folder=verify_receipt(STORE,identity,name,routes[name],reg['source_routes'][name])
            document=read(folder/'action-values.json');summary.add(name,document)
            maximum=max(maximum,receipt['maximum_mixture_error'])
        stats=summary.finish()
        if (STORE/'summary.json').exists():
            assert (STORE/'summary.json').read_bytes() == encoded(stats)+b'\n','Preserve changed summary'
        else:atomic_json(STORE/'summary.json',stats)
        for p,h in reg['inputs'].items():guard();assert sha(p) == h
        storage=study_measure(STORE,guard)
        assert storage['allocated_file_bytes'] < reg['maximum_allocated_bytes']
        assert storage['logical_bytes'] < reg['maximum_logical_bytes']
        output=dict(replay_finished=True,complete=False,independent_review_required=True,
            registration_sha256=identity,final_checkpoint=reference,deals=65536,batches=len(routes),
            summary_sha256=sha(STORE/'summary.json'),maximum_mixture_error=maximum,storage=storage,
            seconds_this_invocation=time.monotonic()-started,gpu_used=False,fresh_deals=0,
            production_modified=False,accuracy_qualified=False)
        atomic_json(replay_path,output)
        atomic_json(run_folder/'finished.json',dict(replay_sha256=sha(replay_path),elapsed_seconds=time.monotonic()-started))
        print(json.dumps(output),flush=True)
    except BaseException as error:
        if run_folder is not None:
            atomic_json(run_folder/'interrupted.json',dict(error=repr(error),elapsed_seconds=time.monotonic()-started,
                instruction='Preserve all evidence. Verify the process is stopped, then explicit resume within the registered deadline.'))
        raise
    finally:
        if pool is not None:stop_pool(pool);pool.shutdown(wait=True,cancel_futures=True)
        if acquired:
            assert LOCK.read_text() == str(os.getpid());LOCK.unlink()


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--resume',action='store_true')
    args=parser.parse_args();assert not args.resume or args.run
    main(args.run,args.resume)
