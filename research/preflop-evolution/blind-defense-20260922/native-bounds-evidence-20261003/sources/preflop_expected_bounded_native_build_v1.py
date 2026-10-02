"""One-shot isolated offline compilation of prospective export-only examples."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from concurrent.futures import ThreadPoolExecutor
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil
import ntfs_expected_retention_v2 as ntfs
import preflop_expected_native_execution_v2 as execution

STAGE=Path(__file__).resolve().parent
REPO=Path(r'T:\Dev\GTOpen')
STORE=Path(r'S:\GTOpen-research\native-bounded-export-build-v1')
ROOTS=[Path(r'S:\GTOpen-research'),Path(r'T:\GTOpen-research'),REPO/'research']
CAP=800_000_000_000
RESERVE=5_000_000_000
CARGO=Path(r'C:\Users\there\.cargo\bin\cargo.exe')
sys.path.append(str(REPO/'tools/research'))
from bounded_parallel_evaluation_archive_v2 import production_available

def sha(path):return execution.sha(path)
def write(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as file:
        file.write(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n')
        file.flush();os.fsync(file.fileno())
def inventory(root):
    kernel=ntfs._api();total=0;logical=0;files=0;directories=0;pending=[root]
    while pending:
        directory=pending.pop();directories+=1
        with os.scandir(directory) as items:
            for item in items:
                info=item.stat(follow_symlinks=False)
                if getattr(info,'st_file_attributes',0)&ntfs.REPARSE:
                    raise ValueError('Redirected storage inventory entry: '+item.path)
                if item.is_dir(follow_symlinks=False):pending.append(Path(item.path));continue
                if not item.is_file(follow_symlinks=False):raise ValueError('Nonordinary inventory entry')
                high=wintypes.DWORD();ctypes.set_last_error(0)
                low=kernel.GetCompressedFileSizeW(ntfs._long(item.path),ctypes.byref(high))
                if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
                total+=(high.value<<32)|low;logical+=info.st_size;files+=1
    return dict(root=str(root),allocated_file_bytes=total,logical_file_bytes=logical,files=files,directories=directories)
def store_size():
    return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
def guard():
    if psutil.virtual_memory().available<24_000_000_000:raise ValueError('Insufficient free RAM for isolated compilation')
    if psutil.disk_usage('S:\\').free<20_000_000_000:raise ValueError('S volume reserve exhausted')
    if store_size()>4_000_000_000:raise ValueError('Isolated build output exceeds admitted logical envelope')
def build(spec,pins):
    folder=STORE/spec['name'];folder.mkdir()
    target=folder/'target'
    argv=[str(CARGO),'build','--locked','--offline','--release','-p','solver','--jobs','8','--message-format=json','--target-dir',str(target)]
    if spec['features']:argv+=['--features',spec['features']]
    for name in spec['examples']:argv+=['--example',name]
    record=dict(argv=argv,features=spec['features'],started_unix=time.time(),caller=dict(pid=os.getpid(),creation_time=psutil.Process().create_time()),process=None)
    write(folder/'planned-command.json',record)
    child=None;began=time.monotonic()
    try:
        with (folder/'cargo-stdout.jsonl').open('xb') as output,(folder/'cargo-stderr.txt').open('xb') as error:
            child=subprocess.Popen(argv,cwd=REPO,stdin=subprocess.DEVNULL,stdout=output,stderr=error,creationflags=subprocess.CREATE_NO_WINDOW)
            record['process']=dict(pid=child.pid,creation_time=execution._creation(child),parent_pid=os.getpid(),observed_argv=child.args)
            while child.poll() is None:
                guard()
                if time.monotonic()-began>900:raise TimeoutError('Isolated compilation deadline')
                try:child.wait(timeout=1)
                except subprocess.TimeoutExpired:pass
        record['returncode']=child.returncode
        if child.returncode!=0:raise RuntimeError('Compilation failed; retained build logs')
        artifacts={}
        for line in (folder/'cargo-stdout.jsonl').read_text().splitlines():
            item=json.loads(line)
            if item.get('reason')=='compiler-artifact' and item.get('executable'):
                name=item['target']['name']
                if name in spec['examples']:
                    path=Path(item['executable']).resolve()
                    if not path.is_relative_to(target.resolve()):raise ValueError('Artifact escaped isolated target')
                    artifacts[name]=dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size)
        if set(artifacts)!=set(spec['examples']):raise ValueError('Incomplete isolated binary set')
        record.update(passed=True,artifacts=artifacts)
    except BaseException as exc:
        record.update(passed=False,failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc()))
        raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
        record['terminal_unix']=time.time();record['seconds']=time.monotonic()-began
        record['log_identities']={str(p):sha(p) for p in folder.glob('cargo-*')}
        write(folder/'result.json',record)
    return record
def main():
    if STORE.exists():raise FileExistsError('Never retry started build namespace')
    pub=STAGE/'native-bounded-export-sources-v2/publication.json';doc=json.loads(pub.read_text())
    pins={str(pub):sha(pub),str(Path(__file__).resolve()):sha(__file__),str(CARGO):sha(CARGO)}
    for path in [STAGE/'preflop_expected_native_execution_v2.py',STAGE/'ntfs_expected_retention_v2.py',
                 REPO/'tools/research/bounded_parallel_evaluation_archive_v2.py',
                 REPO/'tools/research/reboot_research_idle_v1.py']:
        pins[str(path)]=sha(path)
    if not production_available():raise ValueError('Production solve is active; compilation not admitted')
    for row in doc['sources']:
        for path,key in ((row['original'],'original_sha256'),(row['new'],'new_sha256')):
            if sha(path)!=row[key]:raise ValueError('Changed exporter source')
            pins[path]=row[key]
    pins[doc['helper']['path']]=doc['helper']['sha256']
    for path in [REPO/'Cargo.toml',REPO/'Cargo.lock',REPO/'crates/solver/Cargo.toml',
                 *sorted((REPO/'crates/solver/src').rglob('*.rs')),
                 *sorted((REPO/'crates/solver/examples/research_sampled').glob('*.rs'))]:
        pins[str(path.resolve())]=sha(path)
    review=json.loads((STAGE/'native-export-bounds-review-v1/source-pins.json').read_text())
    for item in review['native_binaries'].values():
        path=item['path'];pins[path]=item['sha256']
        if sha(path)!=pins[path]:raise ValueError('Original registered executable changed')
    began=time.monotonic()
    with ThreadPoolExecutor(3) as pool:roots=list(pool.map(inventory,ROOTS))
    snapshot=dict(format=1,observed_unix=time.time(),read_only=True,roots=roots,
        allocated_total_bytes=sum(r['allocated_file_bytes'] for r in roots),seconds=time.monotonic()-began)
    if snapshot['allocated_total_bytes']+RESERVE>CAP:raise ValueError('Global build storage admission exceeds 800GB')
    created=ntfs.create_new_store(STORE)
    write(STORE/'store-creation.json',dict(path=str(created),attributes=ntfs.attributes(created),created_unix=time.time()))
    write(STORE/'inventory.json',snapshot)
    specifications=[dict(name='default-features',features='',examples=['hu_fixed_board_tree_bounded_v2','hu_sampled_allin_history_bridge_bounded_v2','hu_sampled_action_trace_bounded_v3']),
        dict(name='river-features',features='continuation-transfer-research',examples=['hu_river_two_stage_stream_bounded_v2'])]
    registration=dict(format=1,name=STORE.name,source_identities=pins,builds=specifications,
        storage_cap=CAP,transient_build_and_metadata_reserve=RESERVE,maximum_logical_build_outputs=4_000_000_000,
        inventory_sha256=sha(STORE/'inventory.json'),scope='Offline compilation only; no native poker, new deals, model inference, fitting, accuracy experiment or production change.')
    write(STORE/'registration.json',registration)
    print(json.dumps(dict(event='build-registered',store=str(STORE),allocated_total=snapshot['allocated_total_bytes'],inventory_seconds=snapshot['seconds'])),flush=True)
    with ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda spec:build(spec,pins),specifications))
    for path,digest in pins.items():
        if sha(path)!=digest:raise ValueError('Pinned source or original executable changed during build')
    result=dict(passed=True,builds=results,originals_preserved=True,source_identities=pins,
        terminal_unix=time.time(),seconds=time.monotonic()-began,logical_build_bytes=store_size())
    write(STORE/'result.json',result)
    print(json.dumps(dict(passed=True,store=str(STORE),seconds=result['seconds'],logical_build_bytes=result['logical_build_bytes'],artifacts={k:v for r in results for k,v in r['artifacts'].items()})),flush=True)
if __name__=='__main__':main()
