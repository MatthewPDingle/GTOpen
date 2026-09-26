"""Bounded parallel re-evaluation of saved fixed continuations; no new deals."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import concurrent.futures as cf
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid
import numpy as np
import psutil
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from hu_frozen_root_action_control_v2_20260926 import transform, verify, cls, EXE, OUT, ROOT, LOCK, OTHER
from frozen_root_precision_summary_v1 import summarize
from reboot_research_idle_v1 import idle
from hu_root_retained_storage_admitted_study_20260924 import measure, LIMIT, METADATA_RESERVE


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,separators=(',',':'),allow_nan=False)
def encoded(v):return json.dumps(v,separators=(',',':'),allow_nan=False).encode()


def batch_job(reg, index, source_name):
    start=time.monotonic();store=Path(reg['store']);name=f'test-{index:06d}'
    assert re.fullmatch('test-[0-9]{6}',source_name)
    def guard():
        assert time.monotonic()-start<180 and idle() and not OTHER.exists()
        assert psutil.virtual_memory().available>=20_000_000_000
        assert shutil.disk_usage('S:/').free>=40_000_000_000
    guard();assert sha(store/'owner.json')==reg['owner_sha256']
    folder=store/'scratch'/name;assert folder.resolve().parent==(store/'scratch').resolve()
    folder.mkdir()
    source_result=read(reg['source_result'])
    assert sha(reg['source_result'])==reg['inputs'][reg['source_result']]
    reader=ArchivedEvaluationReader(source_result['store'],source_result['archive_manifest_hashes'],external_files=[],guard=guard)
    src=Path(source_result['store'])/source_name
    original=reader.read_json(src/'profiles.json');old_native=reader.read_json(src/'native.json')
    batch=reader.read_json(src/'query-batch.json')
    actual=transform(original)
    (folder/'profiles.json').write_bytes(encoded(actual))
    (folder/'context.json').write_bytes(original['context_source'].encode())
    (folder/'conditional-batch.json').write_bytes(original['batch_source'].encode())
    guard();native_start=time.monotonic()
    cp=subprocess.run([str(EXE),str(folder/'context.json'),str(folder/'conditional-batch.json'),
        str(folder/'profiles.json'),str(folder/'native.json')],cwd=ROOT,capture_output=True,
        text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    assert cp.returncode==0,cp.stderr[-1000:]
    native_seconds=time.monotonic()-native_start;guard()
    native=read(folder/'native.json');checked=verify(original,actual,native,old_native,batch)
    hashes={p.name:sha(p) for p in folder.iterdir()}
    payload=dict(source_batch=source_name,source_manifest_sha256=source_result['archive_manifest_hashes'][source_name],
        generated_artifacts=hashes,classes=[cls(d[:2]) for d in batch['deals']],
        native=native,check=checked)
    raw=encoded(payload);archive=store/'batches'/(name+'.json.gz')
    with archive.open('xb') as f:
        f.write(gzip.compress(raw,compresslevel=6,mtime=0));f.flush();os.fsync(f.fileno())
    assert gzip.decompress(archive.read_bytes())==raw
    # Only this exclusive job's reproducible derivatives are released. Original
    # archives remain untouched; output plus source/code/transport digests persist.
    assert set(hashes)=={'profiles.json','context.json','conditional-batch.json','native.json'}
    guard()
    for filename,digest in hashes.items():
        p=folder/filename
        assert p.resolve().parent==folder.resolve() and not p.is_symlink() and sha(p)==digest
    for filename in hashes:(folder/filename).unlink()
    folder.rmdir()
    return dict(index=index,source=source_name,path=str(archive),sha256=sha(archive),
        compressed_bytes=archive.stat().st_size,scratch_bytes=sum(len(original[k].encode()) for k in ['context_source','batch_source'])+len(encoded(actual)),
        native_sha256=hashes['native.json'],seconds=time.monotonic()-start,native_seconds=native_seconds,
        maximum_root_mixture_error=checked['maximum_root_mixture_error'])


def values_from(reg,jobs):
    arrays=[];classes=[]
    for row in sorted(jobs,key=lambda x:x['index']):
        assert sha(row['path'])==row['sha256']
        doc=json.loads(gzip.decompress(Path(row['path']).read_bytes()))
        assert doc['source_batch']==row['source']
        n=len(doc['classes']);v=np.empty((4,n,4))
        for b in range(4):
            for a in range(4):v[b,:,a]=[d['values'][0] for d in doc['native']['profiles'][5*b+a+1]['deals']]
        for q in doc['check']['rows']:assert np.array_equal(v[q['bank'],q['deal']],q['root_action_values'])
        arrays.append(v);classes.extend(doc['classes'])
    return np.concatenate(arrays,axis=1),np.array(classes,dtype=np.int64)


def review(prefix):
    reg=read(OUT/f'{prefix}-registration.json');result_path=OUT/f'{prefix}-result.json';result=read(result_path)
    assert result['passed'] and result['registration_sha256']==sha(OUT/f'{prefix}-registration.json')
    v,c=values_from(reg,result['jobs']);analysis=read(Path(reg['store'])/'analysis.json')
    assert sha(Path(reg['store'])/'analysis.json')==result['analysis_sha256']
    maximum=0.
    for b in range(4):
        for hand,row in enumerate(analysis['banks'][b]['classes']):
            ids=np.flatnonzero(c==hand);n=len(ids);assert row['count']==n
            if not n:assert row['contrast_means'] is None;continue
            for k,(a,d) in enumerate([(1,0),(2,0),(2,1)]):
                x=[float(v[b,i,a]-v[b,i,d]) for i in ids];mean=math.fsum(x)/n
                maximum=max(maximum,abs(mean-row['contrast_means'][k]))
                if n>1:
                    se=math.sqrt(math.fsum((z-mean)**2 for z in x)/(n-1)/n)
                    maximum=max(maximum,abs(se-row['descriptive_standard_errors'][k]))
                else:assert row['descriptive_standard_errors'] is None
            for half,h in enumerate(row['halves']):
                sub=[i for i in ids if i%2==half];assert h['count']==len(sub)
                if sub:
                    means=[math.fsum(float(v[b,i,a]) for i in sub)/len(sub) for a in range(3)]
                    assert h['maximizing_non_jam_action']==max(range(3),key=means.__getitem__)
                    maximum=max(maximum,max(abs(a-z) for a,z in zip(means,h['non_jam_action_means'])))
    assert maximum<1e-9
    save(OUT/f'{prefix}-readback.json',dict(passed=True,source_result_sha256=sha(result_path),
        maximum_statistical_error=maximum,rows=v.shape[1],
        scope='Separate scalar moment and half-sample readback of authenticated fixed-root output; no new poker solve.'))


def main(mode):
    assert mode in ('control','study');prefix=f'frozen-root-precision-{mode}-v1'
    store=Path('S:/GTOpen-research')/prefix;rp=OUT/f'{prefix}-registration.json'
    assert idle() and not LOCK.exists() and not OTHER.exists() and not store.exists() and not rp.exists()
    control_prefix='frozen-root-action-control-v2'
    control=read(OUT/f'{control_prefix}-result.json');control_review=read(OUT/f'{control_prefix}-readback.json')
    assert read(OUT/f'{control_prefix}-status.json')['state']=='complete' and control_review['passed']
    assert control_review['source_result_sha256']==sha(OUT/f'{control_prefix}-result.json')
    source='later-action-recovered-evaluation-control-v1' if mode=='control' else 'later-action-compact-evaluation-study-v1'
    sp=OUT/f'{source}-result.json';source_result=read(sp);source_review=read(OUT/f'{source}-independent-review.json')
    assert source_result['complete'] and source_review['passed'] and source_review['source_result_sha256']==sha(sp)
    sources=['test-000000','test-000032']*2 if mode=='control' else [f'test-{i:06d}' for i in range(0,65536,32)]
    cap=400_000_000 if mode=='control' else 1_000_000_000
    if mode=='study':
        prior=read(OUT/'frozen-root-precision-control-v1-result.json')
        assert read(OUT/'frozen-root-precision-control-v1-status.json')['state']=='complete'
        assert read(OUT/'frozen-root-precision-control-v1-readback.json')['passed']
        projection=max(j['compressed_bytes'] for j in prior['jobs'])*2048*2+200_000_000
        assert projection<=cap,'Revise storage admission before full archived-data pass'
    else:projection=cap
    inventory=measure();projected=sum(x['allocated_file_bytes'] for x in inventory)+cap+METADATA_RESERVE
    assert projected<=LIMIT
    paths=[Path(__file__).resolve(),EXE,sp,OUT/f'{source}-independent-review.json',OUT/f'{control_prefix}-result.json',
        OUT/f'{control_prefix}-readback.json',OUT/'later-action-final-root-stability.json',
        OUT/'FROZEN-ROOT-VARIANCE-DIAGNOSTIC-PLAN.md']
    paths.extend(ROOT/'tools/research'/p for p in ['hu_frozen_root_action_control_v2_20260926.py',
        'frozen_root_precision_summary_v1.py','archived_evaluation_reader_v1.py','sampled_evidence_archive_v1.py','reboot_research_idle_v1.py'])
    reg=dict(prefix=prefix,store=str(store),inputs={str(p):sha(p) for p in paths},source_result=str(sp),sources=sources,
        workers=4,maximum_seconds=1200 if mode=='control' else 14400,maximum_output_bytes=cap,
        projected_output_bytes=projection,projected_allocated_bytes=projected,storage_inventory=inventory,
        fresh_deals=False,distinct_deals=64 if mode=='control' else 65536,mode=mode,
        gpu_used=False,production_modified=False)
    store.mkdir();(store/'scratch').mkdir();(store/'batches').mkdir()
    save(store/'owner.json',dict(prefix=prefix,nonce=uuid.uuid4().hex,scope='reproducible derivative scratch only'))
    reg['owner_sha256']=sha(store/'owner.json');save(rp,reg)
    started=time.monotonic();jobs=[];error=None
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        with cf.ProcessPoolExecutor(max_workers=4) as pool:
            pending={};next_index=0
            while pending or next_index<len(sources):
                assert time.monotonic()-started<reg['maximum_seconds'] and idle() and not OTHER.exists()
                assert psutil.virtual_memory().available>=20_000_000_000
                assert sum(p.stat().st_size for p in store.rglob('*') if p.is_file())<=cap
                while len(pending)<4 and next_index<len(sources):
                    future=pool.submit(batch_job,reg,next_index,sources[next_index]);pending[future]=next_index;next_index+=1
                done,_=cf.wait(pending,timeout=5,return_when=cf.FIRST_COMPLETED)
                for future in done:
                    row=future.result();jobs.append(row);del pending[future]
                    if mode=='control':
                        expected=next(x for x in control['jobs'] if x['name']==row['source'])
                        assert row['native_sha256']==expected['artifacts']['native.json']
                if done and (len(jobs)%32==0 or mode=='control'):
                    print(json.dumps(dict(completed_batches=len(jobs),total_batches=len(sources),seconds=time.monotonic()-started)),flush=True)
        assert len(jobs)==len(sources)
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        v,c=values_from(reg,jobs);m=read(OUT/'later-action-final-root-stability.json')['entry_masses']
        analysis=summarize(v,c,m);save(store/'analysis.json',analysis)
        save(OUT/f'{prefix}-result.json',dict(passed=True,registration_sha256=sha(rp),jobs=sorted(jobs,key=lambda x:x['index']),
            analysis_sha256=sha(store/'analysis.json'),seconds=time.monotonic()-started,mode=mode,
            control_only=mode=='control',fresh_deals=False,accuracy_qualified=False))
        cp=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--review',prefix],cwd=ROOT,
            capture_output=True,text=True,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
        assert cp.returncode==0,cp.stderr[-2000:]
        assert read(OUT/f'{prefix}-readback.json')['passed']
    except BaseException as exc:error=repr(exc);raise
    finally:
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{prefix}-status.json',dict(state='failed' if error else 'complete',error=error,
            completed_batches=len(jobs),seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--review':review(sys.argv[2])
    else:
        assert sys.argv[1:] in (['--control'],['--study'])
        main(sys.argv[1][2:])
