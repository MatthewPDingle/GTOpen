"""Durable parallel archive equivalence and failure handling on owned copies."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import threading
import time
import uuid
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import pack,unpack,retire
from parallel_owned_archive_v1 import pack_many

PREFIX='parallel-owned-archive-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started<300
        if STORE.exists():assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<40_000_000
    guard();rp,dest=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    assert not STORE.exists() and not rp.exists() and not dest.exists()
    sp=OUT/'showdown-training-integration-control-v1-result.json'
    ap=OUT/'showdown-training-integration-control-v1-independent-review.json'
    source,audit=read(sp),read(ap)
    assert source['passed'] and audit['passed'] and audit['source_result_sha256']==sha(sp)
    files=sorted((Path(source['store'])/'objects').iterdir())
    for p in files:assert sha(p)==source['artifacts'][str(p)]
    inputs={str(p):sha(p) for p in [sp,ap,*files,Path(__file__).resolve(),
        ROOT/'tools/research/parallel_owned_archive_v1.py',ROOT/'tools/research/owned_research_archive_v1.py']}
    save(rp,dict(inputs=inputs,store=str(STORE),maximum_seconds=300,maximum_output_bytes=40_000_000,
                 workers=3,jobs=8,gpu_used=False,scope='Owned copied objects only; no active training changes.'))
    rejected=[]
    def reject(label,fn):
        try:fn()
        except ValueError:rejected.append(label)
        else:raise AssertionError('Accepted '+label)
    try:
        STORE.mkdir();token=uuid.uuid4().hex
        save(STORE/'archive-owner.json',dict(format=1,token=token,purpose='new-research-scratch-v1'))
        jobs=[]
        for i in range(8):
            folder=STORE/f'iteration/batch-{i:02d}';folder.mkdir(parents=True)
            selected=files[i::8]
            for p in selected:
                with (folder/p.name).open('xb') as f:f.write(p.read_bytes())
            jobs.append(dict(source=folder,names=[p.name for p in selected],destination=STORE/f'parallel-{i:02d}.xz'))
        kwargs=dict(root=STORE,token=token,guard=guard,workers=3)
        reject('invalid worker count',lambda:pack_many(jobs,**dict(kwargs,workers=True)))
        reject('duplicate source',lambda:pack_many([jobs[0],dict(jobs[0],destination=STORE/'duplicate.xz')],**kwargs))
        reject('duplicate output',lambda:pack_many([jobs[0],dict(jobs[1],destination=jobs[0]['destination'])],**kwargs))
        reject('escaping source',lambda:pack_many([dict(jobs[0],source=STORE.parent)],**kwargs))
        reject('missing source',lambda:pack_many([dict(jobs[0],names=['missing.json'])],**kwargs))
        reject('wrong owner',lambda:pack_many(jobs,**dict(kwargs,token='wrong')))
        assert not list(STORE.glob('*.xz'))
        # Fail one worker after work is submitted. The batch call must fail;
        # all raw files remain, whether sibling jobs finish or are cancelled.
        failed=False
        def fail_once():
            nonlocal failed
            guard()
            if threading.current_thread().name.startswith('owned-archive') and not failed:
                failed=True
                raise RuntimeError('Injected worker failure')
        failure_jobs=[dict(j,destination=STORE/f'failed-{i:02d}.xz') for i,j in enumerate(jobs)]
        try:pack_many(failure_jobs,**dict(kwargs,guard=fail_once))
        except RuntimeError as exc:assert 'Injected worker failure' in str(exc)
        else:raise AssertionError('Partial batch reported success')
        assert failed
        for job in jobs:
            for name in job['names']:assert sha(job['source']/name)==source['artifacts'][str(Path(source['store'])/'objects'/name)]
        failure_archives=[p.name for p in STORE.glob('failed-*.xz')]
        # Serial and parallel use exactly the same sources, settings and format.
        began=time.monotonic()
        reference=[pack(j['source'],j['names'],STORE/f'serial-{i:02d}.xz',root=STORE,token=token,guard=guard)
                   for i,j in enumerate(jobs)]
        serial_seconds=time.monotonic()-began
        began=time.monotonic();actual=pack_many(jobs,**kwargs);parallel_seconds=time.monotonic()-began
        assert actual==reference
        for i,(job,manifest) in enumerate(zip(jobs,actual)):
            assert job['destination'].read_bytes()==(STORE/f'serial-{i:02d}.xz').read_bytes()
            assert job['destination'].with_suffix('.xz.json').read_bytes()==(STORE/f'serial-{i:02d}.xz.json').read_bytes()
            assert unpack(job['destination'],manifest,guard=guard)=={n:(job['source']/n).read_bytes() for n in job['names']}
        # No retirement occurs until every archive above has passed readback.
        for job,manifest in zip(jobs,actual):
            retire(job['source'],job['destination'],manifest,root=STORE,token=token,guard=guard)
            assert not list(job['source'].iterdir())
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),workers=3,jobs=8,
            serial_seconds=serial_seconds,parallel_seconds=parallel_seconds,
            archives_and_manifests_byte_identical=True,all_originals_verified_before_retirement=True,
            failed_worker_preserved_all_originals=True,preserved_failure_archives=failure_archives,
            rejections=rejected,artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            seconds=time.monotonic()-started,gpu_used=False,live_training_modified=False,
            legacy_files_modified=False,production_modified=False,
            scope='Durable archive integration and worker-failure contract on small copied objects. No full training speed or equivalence claim.')
        save(dest,result);print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))
    except BaseException as exc:
        save(dest,dict(passed=False,error=repr(exc),registration_sha256=sha(rp)))
        raise


if __name__=='__main__':main()
