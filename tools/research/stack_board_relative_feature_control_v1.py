"""CPU qualification of visible-only features on retained, excluded probes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from itertools import combinations,permutations
import hashlib,json
from pathlib import Path
import subprocess,sys,time,traceback,uuid
import numpy as np
import psutil
from stack_board_relative_features_v1 import relative_features,WIDTH,NAMES
from stack_price_reference_v1 import rank_five,board_group
from stack_price_learning_data_v2 import card_factors
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure,path_within_research
from global_research_inventory_v3 import measure as inventory
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER
from owned_windows_job_v1 import OwnedJob

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-board-relative-feature-control-v1';STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def oracle(hole,board):
    # Independent five-card subset enumeration, including minimum private usage.
    subsets=list(combinations(hole+board,5));values=[rank_five(list(s)) for s in subsets]
    best=max(values);public=rank_five(board);assert best>=public
    minimum=min(sum(c in hole for c in s) for s,v in zip(subsets,values) if v==best)
    category=public//15**5;full_category=best//15**5
    def kickers(code):
        value=code%15**5;rs=[]
        for i in range(5):
            digit=value//15**(4-i);value%=15**(4-i)
            rs.append((digit-1)/13 if digit else 0)
        return np.asarray(rs,dtype=np.float32)
    relation=0 if best==public else 1 if category==full_category else 2
    x=np.zeros(WIDTH,dtype=np.float32);x[category]=1;x[9:14]=kickers(public);x[14+relation]=1
    if category==full_category:x[17:22]=kickers(best)-kickers(public)
    x[22+minimum]=1
    return x

def board_control(task):
    board=task['board'];index=task['index'];began=time.monotonic()
    factors=card_factors(board);extra=[];maximum=0.;variants=0
    for i,(hand,canonical) in enumerate(zip(factors['hands'].tolist(),factors['canonical_cards'].tolist())):
        actual=relative_features(hand,board);expected=oracle(hand,board)
        maximum=max(maximum,float(np.max(abs(actual-expected))))
        assert np.array_equal(actual,expected),(index,i,actual.tolist(),expected.tolist())
        assert np.array_equal(actual,relative_features(canonical[:2],canonical[2:]))
        extra.append(actual)
        if i in (0,1,180,360,540,720,900,1080):
            for suit in permutations(range(4)):
                cards=[c//4*4+suit[c%4] for c in hand+board]
                for private in (cards[:2],cards[:2][::-1]):
                    for flop in permutations(cards[2:5]):
                        assert np.array_equal(actual,relative_features(private,list(flop)+cards[5:]))
                        variants+=1
    dest=STORE/f'board-{index}-extra.npz'
    with dest.open('xb') as f:np.savez_compressed(f,features=np.asarray(extra))
    return dict(index=index,board=board,canonical_group=board_group(board),rows=len(extra),
        independent_five_card_evaluations=len(extra)*22,invariance_variants=variants,
        maximum_oracle_error=maximum,file=str(dest),sha256=sha(dest),seconds=time.monotonic()-began)

def worker(path):
    assert sys.stdin.readline().strip()=='OWNED_START'
    req=read(path);assert Path(req['store'])==STORE and Path(path).parent==STORE
    path_within_research(STORE)
    print(json.dumps([board_control(t) for t in req['tasks']]),flush=True)

def main(run):
    original=OUT/'stack-price-reference-control-v1-registration.json';old=read(original)
    diagnosis=OUT/'stack-board-error-diagnosis-v2-result.json';d=read(diagnosis)
    assert d['passed'] and d['maximum_original_validation_replay_error_bb']<1e-4
    proof=OUT/'global-research-inventory-v3-control-v2.json'
    ip=OUT/'global-research-inventory-v3-registration-v2.json'
    assert read(proof)['passed'] and read(proof)['registration_sha256']==sha(ip)
    for p,h in read(ip)['inputs'].items():assert sha(p)==h
    tasks=[dict(index=i,board=b) for i,b in enumerate(old['probe_boards'])];assert len(tasks)==12
    paths=[Path(__file__),original,diagnosis,proof,ip,OUT/'STACK-BOARD-RELATIVE-FEATURES-PLAN.md']
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    spec=dict(inputs={str(p):sha(p) for p in paths},tasks=tasks,feature_names=list(NAMES),width=WIDTH,
        workers=4,maximum_seconds=600,maximum_new_bytes=32_000_000,reserve_bytes=32_000_000,
        cpu_admission_percent=50,cpu_stop_percent=75,gpu_used=False,new_training=False,
        probe_boards_excluded_from_future_learning=True,production_modified=False,
        scope='Feature mathematics and invariance only; no learned-model or range accuracy claim.')
    if not run:print(json.dumps(dict(preflight_passed=True,boards=12,width=WIDTH,gpu_used=False)));return
    assert not any(p.exists() for p in (REG,RESULT,STORE,LOCK,OTHER))
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-started<600
        if now-last<2:return
        assert production_available() and not OTHER.exists()
        assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
        assert psutil.cpu_percent(interval=None)<75,'Heavy CPU work takes priority'
        last=now
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        rows=inventory();assert sum(r['allocated_file_bytes'] for r in rows)+64_000_000<=800_000_000_000
        atomic_json(REG,spec);create(STORE);atomic_json(STORE/'admission.json',dict(inventory=rows))
        bad=[([0],[2,3,4,5,6]),([0,0],[2,3,4,5,6]),([0,1],[2,3,4,5]),
            ([0,1],[2,3,4,5,6,7]),([0,1],[0,2,3,4,5]),([0,52],[2,3,4,5,6]),
            ([False,1],[2,3,4,5,6]),([0.,1],[2,3,4,5,6])]
        for h,b in bad:
            try:relative_features(h,b)
            except ValueError:pass
            else:raise AssertionError('Invalid visible input accepted')
        records=[];psutil.cpu_percent(interval=None)
        with OwnedJob() as job:
            def launch(batch):
                request=STORE/f"batch-{batch[0]['index']}.json"
                atomic_json(request,dict(store=str(STORE),tasks=batch))
                p=subprocess.Popen([sys.executable,'-B',__file__,'--worker',str(request)],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
                try:
                    job.assign(p);out,err=p.communicate(b'OWNED_START\n',timeout=500)
                    if p.returncode:raise RuntimeError(err.decode(errors='replace')[-3000:])
                    return json.loads(out)
                except BaseException:
                    if p.poll() is None:p.kill();p.wait(timeout=10)
                    raise
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures={pool.submit(launch,tasks[i::4]) for i in range(4)}
                try:
                    while futures:
                        guard();done,futures=wait(futures,timeout=2,return_when=FIRST_COMPLETED)
                        for future in done:records.extend(future.result())
                except BaseException:
                    job.close()
                    for f in futures:f.cancel()
                    raise
            accounting=job.accounting();assert accounting['active_processes']==0
        assert sorted(r['index'] for r in records)==list(range(12))
        for p,h in spec['inputs'].items():assert sha(p)==h,p
        guard();size=measure(STORE);assert size['logical_bytes']<32_000_000
        result=dict(passed=True,registration_sha256=sha(REG),records=sorted(records,key=lambda r:r['index']),
            rows=sum(r['rows'] for r in records),independent_five_card_evaluations=sum(r['independent_five_card_evaluations'] for r in records),
            invariance_variants=sum(r['invariance_variants'] for r in records),invalid_inputs_rejected=len(bad),
            maximum_oracle_error=max(r['maximum_oracle_error'] for r in records),job=accounting,
            seconds=time.monotonic()-started,storage=size,gpu_used=False,new_training=False,production_modified=False,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()})
        atomic_json(RESULT,result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('records','artifacts')}),flush=True)
    except BaseException as e:
        atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(e),traceback=traceback.format_exc()))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--worker');a=p.parse_args()
    if a.worker:worker(a.worker)
    else:main(a.run)
