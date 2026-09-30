"""Verify dynamic scheduling against retained exact archives of eight large jobs."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import json
from pathlib import Path
import shutil
import time
import traceback
import psutil
from stack_context_cycle_archive_v1 import read,sha,verify_index,finish_retirement
from stack_context_cycle_archive_v2 import archive_cycle
from owned_columnar_evaluation_archive_v1 import durable,encoded
from board_study_storage_v1 import create,measure
from river_matched_training_pilot_v1 import ROOT,OUT,LOCK,OTHER,production_available

NAME='stack-context-cycle-archive-parallel-check-v1'
STORE=Path('S:/GTOpen-research')/NAME
PREVIOUS=Path('S:/GTOpen-research/stack-context-cycle-archive-control-v1')
TOKEN=NAME+'-new-copies-only'
REG,ATTEMPT,RESULT,FAILURE=(OUT/(NAME+s+'.json') for s in ('-registration','-attempt','-result','-failure'))


def main():
    if any(path.exists() for path in (STORE,REG,ATTEMPT,RESULT,FAILURE,LOCK,OTHER)):
        raise ValueError('Existing attempt or research owner')
    prior_path=OUT/'stack-context-cycle-archive-control-v1-result.json';prior=read(prior_path)
    if not prior['passed'] or not prior['complete'] or not prior['partial_retirement_recovered']:
        raise ValueError('Complete baseline archive/recovery check required')
    plan=read(PREVIOUS/'archive/plan.json'); index=read(PREVIOUS/'archive/index.json')
    if sha(PREVIOUS/'archive/index.json')!=prior['index_sha256']:
        raise ValueError('Changed baseline archive index')
    pairs=sorted(zip(plan['jobs'],index['bundles']),key=lambda pair:sum(row['bytes'] for row in pair[0]['members']),reverse=True)[:8]
    start=time.monotonic();last=0
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-start>900:
            raise RuntimeError('15-minute scheduler check bound')
        if now-last>2:
            if (OTHER.exists() or not production_available() or psutil.virtual_memory().available<24_000_000_000
                    or psutil.disk_usage('S:/').free<40_000_000_000):
                raise RuntimeError('Yield to other work/resource pressure')
            last=now
    guard()
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        create(STORE);durable(STORE/'archive-owner.json',encoded(dict(format=1,token=TOKEN,purpose='new-research-scratch-v1')))
        scripts=[Path(__file__).resolve(),ROOT/'tools/research/stack_context_cycle_archive_v2.py',ROOT/'tools/research/stack_context_cycle_archive_v1.py',
                 ROOT/'tools/research/owned_research_archive_v1.py',ROOT/'tools/research/owned_columnar_evaluation_archive_v1.py']
        durable(REG,encoded(dict(inputs={str(path):sha(path) for path in scripts},prior_result_sha256=sha(prior_path),
            selected=pairs,workers=4,maximum_seconds=900,new_labels=False,new_fits=False)))
        durable(ATTEMPT,encoded(dict(pid=os.getpid(),process_created=psutil.Process().create_time(),registration_sha256=sha(REG))))
        copies=STORE/'copies';copies.mkdir(); expected={}; raw_bytes=0
        originals=read(OUT/'stack-context-cycle-archive-control-v1-registration.json')['originals']
        for number,(job,record) in enumerate(pairs):
            folder=copies/f'job-{number:02d}';folder.mkdir()
            for row in job['members']:
                original=Path('S:/GTOpen-research/stack-context-native-cycle-control-v4/cycle-1')/row['path']
                if originals[str(original)]!=row['sha256'] or sha(original)!=row['sha256']:
                    raise ValueError('Changed legacy original')
                guard();target=folder/original.name;shutil.copyfile(original,target);raw_bytes+=target.stat().st_size
            previous_manifest=read(Path(job['destination']).with_suffix('.xz.json'))
            expected[folder.name]=previous_manifest['packed_sha256']
        began=time.monotonic(); cpu_start=time.process_time()
        archive_cycle(copies,STORE/'archive',root=STORE,token=TOKEN,guard=guard,workers=4,retire=False)
        wall=time.monotonic()-began; cpu=time.process_time()-cpu_start
        after,documents=verify_index(STORE/'archive',root=STORE,token=TOKEN,guard=guard)
        for job,record in zip(after['jobs'],documents['bundles']):
            manifest=read(Path(job['destination']).with_suffix('.xz.json'))
            if manifest['packed_sha256']!=expected[Path(job['source']).name]:
                raise ValueError('Dynamic scheduling changed compressed or original bytes')
        finish_retirement(STORE/'archive',root=STORE,token=TOKEN,guard=guard)
        durable(RESULT,encoded(dict(complete=True,passed=True,registration_sha256=sha(REG),jobs=len(pairs),raw_bytes=raw_bytes,
            packed_bytes=documents['packed_bytes'],archive_seconds=wall,archive_cpu_seconds=cpu,average_cpu_cores=cpu/wall,
            seconds=time.monotonic()-start,byte_identical_to_baseline_archives=True,legacy_originals_unchanged=True,
            storage=measure(STORE),new_labels=False,new_fits=False,
            scope='Exact archive equivalence and dynamic scheduling; no head-to-head wall-speed claim')))
        print(json.dumps(dict(passed=True,jobs=len(pairs),seconds=time.monotonic()-start,archive_seconds=wall,average_cpu_cores=cpu/wall)),flush=True)
    except BaseException as error:
        durable(FAILURE,encoded(dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False)));raise
    finally:
        if LOCK.exists() and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
