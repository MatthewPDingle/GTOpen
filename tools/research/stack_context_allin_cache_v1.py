"""Complete role-preserving all-in counts for any legal pair of private hands.

Candidate-independent exact arithmetic, not training or a learning experiment.
Reuse reviewed counts; reverse roles with explicit win/loss reversal. Enumerate
only one member of each remaining role-reversal pair with the existing native
exhaustive scorer. Retain all outputs; failures are never retried here.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil
from sampled_allin_protocol_v3 import AllinCache,BOARDS,canonical
from storage_strategic_common_prior_20260920 import PAIRS,MASKS
from later_average_support_v1 import load_complete_cache
from sampled_physical_root_evaluation_v1 import save,sha
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from bounded_parallel_evaluation_archive_v2 import production_available
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-complete-allin-cache-v1';STORE=Path('S:/GTOpen-research')/NAME
REG,ATTEMPT,RESULT,FAILURE,STATUS=(OUT/(NAME+s+'.json') for s in ('-registration','-attempt','-result','-failure','-status'))
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
EXE=ROOT/'target/release/examples/hu_allin_board_reference.exe'


def read(path):return json.loads(Path(path).read_bytes())
def reverse_key(key):return canonical(list(key[2:]+key[:2]))
def reverse_row(key,row):
    return dict(private_cards=list(key),wins=row['losses'],ties=row['ties'],losses=row['wins'],boards=row['boards'])


def expand(rows):
    result={k:dict(v) for k,v in rows.items()}
    for key,row in rows.items():
        target=reverse_key(key);value=reverse_row(target,row)
        if target in result and result[target]!=value:raise ValueError('Role-reversal count contradiction')
        result[target]=value
    return result


def universe(guard=lambda:None):
    ii,jj=np.nonzero((MASKS[:,None]&MASKS[None,:])==0);values=set()
    for start in range(0,len(ii),65536):
        guard();cards=np.concatenate((PAIRS[ii[start:start+65536]],PAIRS[jj[start:start+65536]]),axis=1).astype(np.uint32)
        best=np.full(len(cards),2**24-1,dtype=np.uint32)
        for p in itertools.permutations(range(4)):
            m=4*(cards//4)+np.asarray(p,dtype=np.uint32)[cards%4]
            a=np.minimum(m[:,0],m[:,1]);b=np.maximum(m[:,0],m[:,1])
            c=np.minimum(m[:,2],m[:,3]);d=np.maximum(m[:,2],m[:,3])
            best=np.minimum(best,(a<<18)|(b<<12)|(c<<6)|d)
        values.update(map(int,best))
    keys=sorted(tuple((key>>s)&63 for s in (18,12,6,0)) for key in values)
    if len(ii)!=1624350 or len(keys)!=93769:raise ValueError('Incomplete legal private-hand universe')
    return keys


def native_row(case,row):
    if row['private_cards']!=case['private_cards']:raise ValueError('Native private-card identity changed')
    if (any(type(row[k]) is not int or row[k]<0 for k in ('wins','ties','losses','exact_boards'))
            or row['wins']+row['ties']+row['losses']!=row['exact_boards'] or row['exact_boards']!=BOARDS
            or row['equity']!=(row['wins']+.5*row['ties'])/BOARDS):
        raise ValueError('Incomplete or inconsistent exact counts')
    expected=[]
    for board in case['sampled_boards']:
        winner=showdown(case['private_cards']+board)
        expected.append(1 if winner<0 else 2 if winner==0 else 0)
    if row['sampled_scores']!=expected:raise ValueError('Independent sample-board scorer disagrees')
    return dict(private_cards=row['private_cards'],wins=row['wins'],ties=row['ties'],losses=row['losses'],boards=BOARDS)


def verify(inputs):
    for path,identity in inputs.items():
        if sha(path)!=identity:raise ValueError('Input changed: '+path)


def prepare():
    if any(p.exists() for p in (STORE,REG,ATTEMPT,RESULT,FAILURE)):raise ValueError('Preserve existing preparation/attempt')
    if not production_available():raise ValueError('Production has priority')
    accounting=inventory()
    if sum(r['allocated_file_bytes'] for r in accounting)+1_000_000_000>800_000_000_000:
        raise ValueError('Global allocated storage cap')
    if psutil.disk_usage('S:/').free<40_000_000_000 or psutil.virtual_memory().available<28_000_000_000:
        raise ValueError('Resource reserve unavailable')
    began=time.monotonic()
    def guard():
        if time.monotonic()-began>180 or not production_available():raise ValueError('Preparation limit/activity')
    base=load_complete_cache();guard();keys=universe(guard);reused=expand(base.rows)
    if not set(reused)<=set(keys):raise ValueError('Cache outside complete universe')
    missing=sorted(set(keys)-set(reused));native_keys=sorted({min(k,reverse_key(k)) for k in missing})
    if not all(reverse_key(k) in missing for k in missing):raise ValueError('Incomplete reversal closure')
    paths={Path(__file__).resolve(),ROOT/'tools/research/stack_context_allin_cache_readback_v1.py',
           ROOT/'tools/research/test_stack_context_allin_cache_v1.py',EXE,
           ROOT/'crates/solver/examples/hu_allin_board_reference.rs',ROOT/'crates/solver/src/evaluator.rs',
           OUT/'STACK-CONTEXT-COMPLETE-ALLIN-CACHE-PLAN.md'}
    for suffix in ('registration','result','independent-review'):
        paths.add(OUT/f'complete-private-allin-cache-v2-{suffix}.json')
    original=read(OUT/'complete-private-allin-cache-v2-independent-review.json')
    paths.add(Path(original['cache_artifact']))
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py':paths.add(Path(path))
    create(STORE);save(STORE/'admission.json',accounting)
    save(STORE/'keys.json',keys);save(STORE/'native-keys.json',native_keys)
    save(STORE/'reused-cache.json',dict(format=1,player_roles_fixed=True,rows=[reused[k] for k in sorted(reused)]))
    paths.update((STORE/'keys.json',STORE/'native-keys.json',STORE/'reused-cache.json'))
    spec=dict(inputs={str(p):sha(p) for p in sorted(paths)},original_cache=original['cache_artifact'],
        original_cache_sha256=base.sha256,canonical_keys=len(keys),physical_pairs=1624350,
        directly_reused=len(base.rows),reused_after_role_reversal=len(reused),missing_keys=len(missing),
        native_keys=len(native_keys),maximum_workers=12,batch_size=20,maximum_seconds=7200,
        maximum_new_bytes=1_000_000_000,host_reserve_bytes=24_000_000_000,disk_reserve_bytes=40_000_000_000,
        admission_cpu_percent=50,heavy_external_cpu_percent=50,readback_required=True,
        policy_candidates=[],training_started=False,production_modified=False,
        scope='Exact private-card equity counts for the complete legal universe, independent of policies, positions, stack sizes and rake. Stack-specific cash-flow matrices remain separate.')
    save(REG,spec);print(json.dumps({k:spec[k] for k in ('canonical_keys','directly_reused','reused_after_role_reversal','missing_keys','native_keys')}))


def run():
    active_cpu={};last_status=0.
    spec=read(REG);verify(spec['inputs'])
    if any(p.exists() for p in (ATTEMPT,RESULT,FAILURE,LOCK,OTHER)):raise ValueError('Existing attempt/result or resource owner; no retry')
    if (not production_available() or psutil.cpu_percent(interval=1)>=spec['admission_cpu_percent']
            or psutil.virtual_memory().available<28_000_000_000 or psutil.disk_usage('S:/').free<spec['disk_reserve_bytes']):
        print(json.dumps(dict(deferred=True)));return
    began=time.monotonic();live={};done={};position=0;counter=0;last_probe=0.;external=0.;busy=False
    keys=[tuple(k) for k in read(STORE/'native-keys.json')];batches=[keys[i:i+20] for i in range(0,len(keys),20)]
    native_folder=STORE/'native';native_folder.mkdir()
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    def status(state):
        atomic_json(STATUS,dict(state=state,pid=os.getpid(),process_created=psutil.Process().create_time(),
            elapsed=time.monotonic()-began,completed_batches=len(done),total_batches=len(batches),
            active=[dict(index=i,pid=p.pid,created=created) for i,(p,log,started,created) in live.items()],
            external_cpu_percent=external),replace=True)
    try:
        save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),registration_sha256=sha(REG)))
        while position<len(batches) or live:
            now=time.monotonic()
            if now-began>spec['maximum_seconds']:raise TimeoutError('Exact-cache execution budget')
            if LOCK.read_text()!=str(os.getpid()) or OTHER.exists():raise RuntimeError('Research lock changed')
            if now-last_probe>=2:
                own=0.
                for process in active_cpu.values():
                    try:own+=process.cpu_percent()
                    except psutil.NoSuchProcess:pass
                own/=psutil.cpu_count()
                external=max(0.,psutil.cpu_percent()-own)
                busy=(not production_available() or external>=spec['heavy_external_cpu_percent']
                    or psutil.virtual_memory().available<spec['host_reserve_bytes']
                    or psutil.disk_usage('S:/').free<spec['disk_reserve_bytes'])
                last_probe=now
            for index,(child,log,started,created) in list(live.items()):
                if child.poll() is None:
                    if now-started>120:raise TimeoutError('Native batch deadline; no retry')
                    continue
                log.close();del live[index];active_cpu.pop(index,None)
                if child.returncode:raise RuntimeError('Native enumeration failed; evidence retained')
                ip=native_folder/f'input-{index:05d}.json';op=native_folder/f'output-{index:05d}.json'
                cases=read(ip)['cases'];rows=read(op)
                if len(rows)!=len(cases):raise ValueError('Native batch truncated')
                checked=[native_row(c,r) for c,r in zip(cases,rows)]
                done[index]=dict(rows=checked,input_sha256=sha(ip),output_sha256=sha(op),
                    native_seconds=sum(r['exact_seconds'] for r in rows),wall_seconds=now-started)
            while not busy and position<len(batches) and len(live)<spec['maximum_workers']:
                index=position;position+=1;selected=batches[index]
                cases=[]
                for key in selected:
                    deck=[c for c in range(52) if c not in key]
                    cases.append(dict(private_cards=list(key),sampled_boards=[deck[:5],deck[-5:]]))
                ip=native_folder/f'input-{index:05d}.json';op=native_folder/f'output-{index:05d}.json'
                save(ip,dict(format=1,cases=cases));log=(native_folder/f'process-{index:05d}.log').open('x')
                child=subprocess.Popen([str(EXE),str(ip),str(op)],stdout=log,stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
                process=psutil.Process(child.pid);process.cpu_percent();active_cpu[index]=process
                live[index]=(child,log,time.monotonic(),process.create_time())
            if len(done)//25>counter:
                counter=len(done)//25;status('yielding' if busy else 'enumerating')
                print(json.dumps(dict(completed_batches=len(done),total_batches=len(batches),elapsed=time.monotonic()-began)),flush=True)
            elif now-last_status>10:status('yielding' if busy else 'enumerating');last_status=now
            time.sleep(.2 if live else 2)
        reused=AllinCache(STORE/'reused-cache.json',spec['inputs'][str(STORE/'reused-cache.json')])
        enumerated={tuple(row['private_cards']):row for i in sorted(done) for row in done[i]['rows']}
        if sorted(enumerated)!=keys:raise ValueError('Native key order/coverage differs')
        added=expand(enumerated)
        if set(added)&set(reused.rows):raise ValueError('Enumeration overlaps reused population')
        merged=dict(reused.rows)
        merged.update(added)
        if sorted(merged)!=[tuple(k) for k in read(STORE/'keys.json')]:raise ValueError('Incomplete final universe')
        cp=STORE/'cache.json';save(cp,dict(format=1,player_roles_fixed=True,rows=[merged[k] for k in sorted(merged)]))
        AllinCache(cp,sha(cp));verify(spec['inputs']);size=measure(STORE)
        if size['logical_bytes']>spec['maximum_new_bytes']:raise ValueError('Storage budget exceeded')
        save(RESULT,dict(complete=True,passed=True,registration_sha256=sha(REG),cache_artifact=str(cp),cache_sha256=sha(cp),
            native_keys=len(enumerated),canonical_keys=len(merged),seconds=time.monotonic()-began,storage=size,
            batches={str(i):{k:v for k,v in row.items() if k!='rows'} for i,row in done.items()},
            native_seconds=sum(r['native_seconds'] for r in done.values()),independently_reviewed=False,
            scientific_training=False,accuracy_qualified=False,production_modified=False))
        status('complete');print(json.dumps(dict(complete=True,seconds=time.monotonic()-began)))
    except BaseException as error:
        save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False))
        status('failed');raise
    finally:
        for child,log,_,_ in live.values():
            if child.poll() is None:child.terminate();child.wait(timeout=20)
            log.close()
        if LOCK.exists() and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    elif sys.argv[1:]==['--run']:run()
    else:raise SystemExit('Use --prepare or --run')
