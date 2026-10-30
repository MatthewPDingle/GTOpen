"""Bounded CPU qualification of exact river prices, ranks and call/fold values."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import threading
import time
import traceback
import uuid
import numpy as np
import psutil
import river_matched_training_pilot_v1 as pilot
from owned_windows_job_v1 import OwnedJob
from stack_price_reference_v1 import board_group,rank_seven,conditional_counts,price,call_advantage,decision_regret

ROOT=pilot.ROOT; OUT=pilot.OUT; NAME='stack-price-reference-control-v1'
STORE=Path('S:/GTOpen-research')/NAME
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
REG=OUT/(NAME+'-registration.json'); RESULT=OUT/(NAME+'-result.json'); STATUS=OUT/(NAME+'-status.json')
RANKS=ROOT/'target/release/examples/hu_board_hand_ranks_v1.exe'
NATIVE=ROOT/'target/release/examples/hu_river_value_reference_v1.exe'
DEPTHS=(20,40,100,200,400); SEED=9296301; LIMIT=250_000_000; RESERVE=50_000_000
MAX_SECONDS=3600; WORKERS=8
read=pilot.read; sha=pilot.sha; write=pilot.atomic_json

def native(exe,args,data=None):
    run=subprocess.run([str(exe),*map(str,args)],input=None if data is None else json.dumps(data).encode(),
                       capture_output=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode: raise RuntimeError(run.stderr.decode(errors='replace')[-2000:])
    return json.loads(run.stdout)

def public_key(row):
    h=1
    for token in row['history']: h=(h<<3)|token
    return str((1<<63)|(h<<4)|row['public_id'])

def geometry_worker(depth):
    source=GEOMETRY/'fixtures'/f'stack-{depth}-context.json'
    proof=native(NATIVE,['control',source]); assert proof['passed'] and proof['maximum_record_error_bb']<1e-9
    write(STORE/f'stack-{depth}-native-control.json',proof)
    public=read(GEOMETRY/f'stack-{depth}-public.json')
    rows={r['hi']:r for r in public['public_states'] if r['phase']==3 and [a['kind'] for a in r['actions']]==['fold','call']}
    matched={public_key(r):r for r in proof['templates'] if r['legal_actions']==2}
    assert set(rows)==set(matched) and len(matched)==sum(r['legal_actions']==2 for r in proof['templates'])
    maximum=0.; prices=[]
    for key,row in rows.items():
        reference=price(row); actual=matched[key]
        assert actual['actor']==row['actor'] and actual['call_ends_showdown']
        pairs=[(reference['pot'],actual['pot']),(reference['call_cost'],actual['amount_to_call']),
               (reference['rake'],actual['rake']),(row['rake_fraction'],actual['rake_fraction']),
               (row['rake_cap'],actual['rake_cap'])]
        pairs+=list(zip(reference['endpoints_loss_tie_win'],actual['endpoints_loss_tie_win']))
        maximum=max(maximum,*[abs(a-b) for a,b in pairs]); prices.append(reference['equity_threshold'])
    assert rows and maximum<1e-9
    return dict(kind='geometry',stack=depth,states=len(rows),actors=sorted({r['actor'] for r in rows.values()}),
        minimum_call_equity=min(prices),maximum_call_equity=max(prices),
        distinct_prices_rounded_9dp=len(set(round(x,9) for x in prices)),maximum_cashflow_error_bb=maximum,
        native_walk_records=proof['known_deal_walk_records'])

def board_worker(index,board):
    began=time.monotonic(); ranks=native(RANKS,board); write(STORE/f'board-{index}-native-ranks.json',ranks)
    assert ranks['board']==board and ranks['larger_rank_is_stronger']
    hands=np.asarray([r['hand'] for r in ranks['rows']],dtype=np.int64)
    strength=np.asarray([r['rank'] for r in ranks['rows']],dtype=np.int64)
    independent=np.asarray([rank_seven(list(map(int,h))+board) for h in hands],dtype=np.int64)
    order=np.argsort(strength); ds=np.diff(strength[order]); dp=np.diff(independent[order])
    assert np.all(dp>=0) and np.array_equal(ds==0,dp==0)
    counts=conditional_counts(board,hands,strength)
    assert np.array_equal(counts,conditional_counts(board,hands,independent))
    inputs=[list(map(int,h))+board for h in hands]
    enumerated=native(NATIVE,['equities',1],inputs)
    assert enumerated['opponent_pairs_per_row']==990 and np.array_equal(counts,enumerated['counts_win_tie_loss'])
    write(STORE/f'board-{index}-native-counts.json',enumerated)
    # Fixed visible variants; no additional strategic choices or model fitting.
    variants=[]; expected=[]
    for j in (0,360,720,1080):
        cards=inputs[j]
        variants.extend([[cards[1],cards[0],*cards[:1:-1]],
                         [c//4*4+(c%4+1)%4 for c in cards]])
        expected.extend([counts[j].tolist()]*2)
    assert native(NATIVE,['equities',1],variants)['counts_win_tie_loss']==expected
    if index in (0,1): assert np.all(counts==[0,990,0])
    if index==3: assert np.all(counts[np.any(hands==48,axis=1)]==[990,0,0])
    write(STORE/f'board-{index}-reference.json',dict(board=board,canonical_group=board_group(board),
        hands=hands.tolist(),independent_five_subset_ranks=independent.tolist(),counts_win_tie_loss=counts.tolist(),
        probe_only=True,exclude_from_future_fit_and_test=True))
    return dict(kind='board',index=index,board=board,canonical_group=board_group(board),
        hero_hands=1081,opponent_pairs_per_hand=990,independent_five_card_evaluations=1081*21,
        serial_native_seconds=enumerated['seconds'],seconds=time.monotonic()-began)

def worker(request):
    assert sys.stdin.readline().strip()=='OWNED_START', 'Wait for confirmed job ownership'
    task=read(request)
    result=geometry_worker(task['stack']) if task['kind']=='geometry' else board_worker(task['index'],task['board'])
    print(json.dumps(result),flush=True)

def specification():
    fixed=[[32,36,40,44,48],[0,1,2,3,48],[0,13,26,35,40],[32,36,40,44,1]]
    rng=random.Random(SEED); groups={board_group(b) for b in fixed}
    while len(fixed)<12:
        board=rng.sample(range(52),5); key=board_group(board)
        if key not in groups: fixed.append(board); groups.add(key)
    gp=OUT/'stack-geometry-control-v1-result.json'; gr=OUT/'stack-geometry-control-v1-registration.json'
    geometry=read(gp); assert geometry['passed'] and geometry['registration_sha256']==sha(gr)
    prior=OUT/'board-river-value-reference-v1-registration.json'; frozen=read(prior)['inputs']
    for exe in (RANKS,NATIVE): assert sha(exe)==frozen[str(exe)]
    paths=[Path(__file__),gp,gr,prior,RANKS,NATIVE,OUT/'STACK-PRICE-REFERENCE-DESIGN.md',
           OUT/'STACK-PRICE-REFERENCE-QUALIFICATION.md',ROOT/'crates/solver/src/evaluator.rs',
           ROOT/'crates/solver/src/tree.rs',ROOT/'crates/solver/examples/hu_river_value_reference_v1.rs',
           ROOT/'crates/solver/examples/hu_board_hand_ranks_v1.rs',
           *[ROOT/'crates/solver/examples/research_sampled'/n for n in ('state.rs','poker_reference_v1.rs','observation_v1.rs')]]
    for depth in DEPTHS:
        for path in (GEOMETRY/'fixtures'/f'stack-{depth}-context.json',GEOMETRY/f'stack-{depth}-public.json'):
            assert sha(path)==geometry['artifacts'][str(path)];paths.append(path)
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py': paths.append(Path(path))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},probe_seed=SEED,probe_boards=fixed,
        probe_board_groups=[board_group(b) for b in fixed],fitting_depths=list(DEPTHS),heldout_depths_not_labelled=[60,150],
        maximum_seconds=MAX_SECONDS,maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,
        global_allocated_cap=pilot.GLOBAL_LIMIT,workers=WORKERS,native_threads_per_worker=1,
        cashflow_absolute_tolerance=1e-9,rank_and_count_equality='exact',
        scope='Exact restricted call/fold oracle; probe-only boards excluded from later fitting and tests.',
        gpu_used=False,training_started=False,final_test_evaluated=False,production_modified=False)

def main(run):
    spec=specification()
    if not run:
        print(json.dumps(dict(preflight_passed=True,contexts=len(DEPTHS),boards=12,workers=WORKERS,gpu_used=False)),flush=True);return
    assert not any(p.exists() for p in (REG,RESULT,STORE)), 'Preserve all attempts'
    assert not pilot.LOCK.exists() and not pilot.OTHER.exists() and pilot.production_available()
    assert psutil.cpu_percent(interval=1)<50 and psutil.virtual_memory().available>28_000_000_000
    assert psutil.disk_usage('S:/').free>40_000_000_000
    acquired=False;started=time.monotonic()
    def status(stage,**kw): write(STATUS,dict(stage=stage,pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),**kw),replace=True)
    def guard():
        assert time.monotonic()-started<MAX_SECONDS, 'One-hour limit'
        assert pilot.production_available() and not pilot.OTHER.exists(), 'Other work has priority'
        assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    try:
        with pilot.LOCK.open('x') as f: f.write(str(os.getpid()))
        acquired=True;status('storage_admission')
        inventory=pilot.global_measure();allocated=sum(x['allocated_file_bytes'] for x in inventory)
        assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT;guard()
        write(REG,spec);pilot.create(STORE)
        write(STORE/'admission.json',dict(inventory=inventory,allocated_bytes=allocated,reservation=LIMIT+RESERVE))
        tasks=[dict(kind='geometry',stack=d) for d in DEPTHS]+[dict(kind='board',index=i,board=b) for i,b in enumerate(spec['probe_boards'])]
        results=[]
        with OwnedJob() as job:
            stopped=threading.Event()
            def launch(task_id,task):
                if stopped.is_set(): raise RuntimeError('Qualification workers cancelled')
                request=STORE/f'request-{task_id}.json';write(request,task)
                proc=subprocess.Popen([sys.executable,'-B',__file__,'--worker',str(request)],stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
                try:
                    job.assign(proc)
                    stdout,stderr=proc.communicate(b'OWNED_START\n',timeout=240)
                    if proc.returncode: raise RuntimeError(stderr.decode(errors='replace')[-3000:])
                    return json.loads(stdout)
                except BaseException:
                    if proc.poll() is None: proc.kill();proc.wait(timeout=10)
                    raise
            with ThreadPoolExecutor(max_workers=WORKERS) as pool:
                futures={pool.submit(launch,i,t) for i,t in enumerate(tasks)}
                try:
                    while futures:
                        guard();done,futures=wait(futures,timeout=2,return_when=FIRST_COMPLETED)
                        for future in done:
                            value=future.result();results.append(value)
                            status('qualifying_oracle',completed=len(results),total=len(tasks),latest=value['kind'])
                            print(json.dumps(dict(completed=len(results),total=len(tasks),latest=value['kind'])),flush=True)
                except BaseException:
                    stopped.set();job.close()
                    for future in futures: future.cancel()
                    raise
            accounting=job.accounting();assert accounting['active_processes']==0
        geometry=sorted((r for r in results if r['kind']=='geometry'),key=lambda r:r['stack'])
        boards=sorted((r for r in results if r['kind']=='board'),key=lambda r:r['index'])
        maximum=0.;evaluated=0
        for depth in DEPTHS:
            guard();ledger=read(GEOMETRY/f'stack-{depth}-public.json')
            rows=[r for r in ledger['public_states'] if r['phase']==3 and [a['kind'] for a in r['actions']]==['fold','call']]
            for board in boards:
                counts=np.asarray(read(STORE/f"board-{board['index']}-reference.json")['counts_win_tie_loss'])
                eq=(counts[:,0]+counts[:,1]/2)/990
                for row in rows:
                    d=call_advantage(counts,row);g=price(row);closed=eq*g['net_pot']-g['call_cost']
                    maximum=max(maximum,float(np.max(abs(d-closed))));evaluated+=len(d)
                    assert np.max(abs(decision_regret((d>0).astype(float),d)))<1e-10
                    assert np.max(abs(decision_regret((d<0).astype(float),d)-abs(d)))<1e-10
                    assert np.max(abs(decision_regret(.5,d)-abs(d)/2))<1e-10
        assert maximum<1e-9
        rejected=[]
        def reject(label,fn):
            try: fn()
            except ValueError: rejected.append(label)
            else: raise AssertionError('Accepted invalid '+label)
        reject('duplicate_board',lambda:board_group([0,0,1,2,3]))
        reject('invalid_card',lambda:board_group([0,1,2,3,52]))
        reject('incomplete_holdings',lambda:conditional_counts([0,1,2,3,4],[[5,6]],[1]))
        reject('wrong_count_mass',lambda:call_advantage(np.asarray([[1,2,3]]),rows[0]))
        reject('negative_counts',lambda:call_advantage(np.asarray([[-1,1,990]]),rows[0]))
        reject('extra_legal_action',lambda:price(dict(rows[0],actions=rows[0]['actions']+[dict(kind='raise')])) )
        reject('negative_probability',lambda:decision_regret(-.1,1.))
        reject('nonfinite_advantage',lambda:decision_regret(.5,float('nan')))
        invalid=subprocess.run([str(NATIVE),'equities','1'],input=b'[[0,0,1,2,3,4,5]]',capture_output=True,
            timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
        assert invalid.returncode!=0 and b'Overlapping or invalid visible cards' in invalid.stderr
        rejected.append('native_duplicate_cards')
        pilot.verify(spec['inputs']);guard();storage=pilot.study_measure(STORE);assert storage['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),contexts=geometry,boards=boards,
            native_terminal_states=sum(r['states'] for r in geometry),independently_ranked_holdings=12*1081,
            enumerated_directed_private_pairs=12*1081*990,call_values_checked=evaluated,
            maximum_equity_cashflow_formula_error_bb=maximum,oracle_regret_zero=True,
            negative_controls=rejected,owned_workers=accounting,storage=storage,seconds=time.monotonic()-started,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            heldout_depth_labels_read=False,probe_only=True,training_started=False,final_test_evaluated=False,
            gpu_used=False,full_preflop_accuracy_qualified=False,production_modified=False)
        write(RESULT,result);status('complete',result=str(RESULT))
        print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','boards')}),flush=True)
    except BaseException as error:
        write(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc(),
            registration_sha256=sha(REG) if REG.exists() else None))
        raise
    finally:
        if acquired:
            assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--worker')
    args=parser.parse_args()
    if args.worker: worker(args.worker)
    else: main(args.run)
