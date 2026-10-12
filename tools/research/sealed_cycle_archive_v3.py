"""Streaming lossless archive for complete, closed research cycles.

Frames from eight encoders share a bounded queue and are written directly to
one pack. Large native files are never buffered whole or copied to scratch.
The original sources are read only. No retirement or scientific work occurs.
"""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import hashlib
import io
import json
import math
import os
from pathlib import Path
import queue
import threading
import time
import zlib

from sealed_cycle_archive_v2 import FRAME, ROW, member_name, digest, Member

MAGIC=b'GTOARC3\0'
MAX_MANIFEST=16000000


def create(root,output,items,*,identity,guard=lambda:None,workers=8,
           max_file_bytes=2000000000,max_raw_bytes=40000000000,
           max_pack_bytes=12000000000,max_seconds=3600,queue_frames=16):
    root=Path(root).resolve(strict=True);output=Path(output).resolve()
    if output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('Source/archive namespace overlap')
    items=list(items);names=[member_name(v['name']) for v in items]
    if not 0<len(items)<=10000 or len(set(names))!=len(names):
        raise ValueError('Duplicate or excessive members')
    if (type(workers) is not int or type(queue_frames) is not int
            or not 1<=workers<=8 or not 1<=queue_frames<=16):
        raise ValueError('Encoder/queue envelope')
    if (type(max_file_bytes) is not int or type(max_raw_bytes) is not int
            or type(max_pack_bytes) is not int
            or not 0<max_file_bytes<=2000000000 or not 0<max_raw_bytes<=40000000000
            or not len(MAGIC)<=max_pack_bytes<=12000000000
            or type(max_seconds) not in (int,float) or not math.isfinite(max_seconds)
            or not 0<max_seconds<=3600
            or any(type(v['bytes']) is not int or not 0<=v['bytes']<=max_file_bytes for v in items)
            or sum(v['bytes'] for v in items)>max_raw_bytes):
        raise ValueError('Source size envelope')
    guard();output.mkdir(parents=True,exist_ok=False)
    began=time.monotonic();stop=threading.Event();messages=queue.Queue(queue_frames)
    def check():
        if stop.is_set():raise RuntimeError('Streaming archive cancelled')
        if time.monotonic()-began>max_seconds:raise TimeoutError('Streaming archive deadline')
    def send(message):
        while True:
            check()
            try:messages.put(message,timeout=.1);return
            except queue.Full:pass
    def encode(index):
        check();item=items[index];path=root.joinpath(*item['name'].split('/')).resolve(strict=True)
        if not path.is_relative_to(root):raise ValueError('Source escape')
        before=identity(path)
        if before!=item['identity']:raise ValueError('Source identity changed')
        total=number=0;h=hashlib.sha256()
        with path.open('rb') as f:
            while raw:=f.read(FRAME):
                check();total+=len(raw)
                if total>item['bytes']:raise ValueError('Source grew')
                h.update(raw);compressed=zlib.compress(raw,6)
                codec=int(len(compressed)<len(raw));payload=compressed if codec else raw
                send(('frame',index,number,len(raw),codec,hashlib.sha256(raw).hexdigest(),payload))
                number+=1
        check()
        if total!=item['bytes'] or h.hexdigest()!=item['sha256'] or identity(path)!=before:
            raise ValueError('Source bytes or identity changed')
        send(('done',index,number,total))
    rows=[dict(**v,offset=0,stored_bytes=0,frames=[]) for v in items]
    completed=set();pending={};next_index=0;packed=len(MAGIC);last_guard=0.
    try:
        with (output/'payload.gta').open('xb') as pack,ThreadPoolExecutor(max_workers=workers) as pool:
            pack.write(MAGIC)
            def submit():
                nonlocal next_index
                if next_index<len(items):
                    pending[next_index]=pool.submit(encode,next_index);next_index+=1
            try:
                for _ in range(workers):submit()
                while len(completed)<len(items):
                    check()
                    if time.monotonic()-last_guard>=.5:
                        guard();last_guard=time.monotonic()
                    for f in pending.values():
                        if f.done() and f.exception() is not None:f.result()
                    try:message=messages.get(timeout=.1)
                    except queue.Empty:continue
                    kind,index,*fields=message
                    if index in completed or index not in pending:
                        raise ValueError('Invalid member lifecycle')
                    row=rows[index]
                    if kind=='frame':
                        number,n,codec,h,payload=fields
                        if number!=len(row['frames']) or packed+ROW.size+len(payload)>max_pack_bytes:
                            raise ValueError('Frame order/output envelope')
                        pack.write(ROW.pack(n,len(payload),codec,bytes.fromhex(h)))
                        pack.write(payload)
                        row['frames'].append([packed,n,len(payload),codec,h])
                        amount=ROW.size+len(payload);packed+=amount;row['stored_bytes']+=amount
                    elif kind=='done':
                        number,total=fields
                        if number!=len(row['frames']) or total!=row['bytes']:
                            raise ValueError('Incomplete member')
                        pending.pop(index).result();completed.add(index);submit()
                    else:raise ValueError('Invalid encoder message')
                if not messages.empty() or pending:raise ValueError('Unsettled encoders')
            except BaseException:
                stop.set()
                for f in pending.values():f.cancel()
                raise
            pack.flush();os.fsync(pack.fileno())
        check();guard()
        doc=dict(format=3,method='streaming-closed-cycle-zlib6-archive-v3',
                 source_root=str(root),payload='payload.gta',payload_bytes=packed,
                 payload_sha256=digest(output/'payload.gta',check),
                 raw_bytes=sum(v['bytes'] for v in items),frame_bytes=FRAME,
                 workers=workers,queue_frames=queue_frames,
                 max_file_bytes=max_file_bytes,max_raw_bytes=max_raw_bytes,
                 files=sorted(rows,key=lambda v:v['name']),seconds=time.monotonic()-began)
        body=json.dumps(doc,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        if len(body)>MAX_MANIFEST:raise ValueError('Manifest envelope')
        with (output/'manifest.json').open('xb') as f:f.write(body);f.flush();os.fsync(f.fileno())
        manifest_hash=hashlib.sha256(body).hexdigest()
        archive=Archive(output,manifest_hash,check=check,_preseal_verification=True)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            verifies=set()
            try:
                for name in names:verifies.add(pool.submit(archive.verify,name,check))
                while verifies:
                    check();guard()
                    done,verifies=wait(verifies,timeout=.5,return_when=FIRST_COMPLETED)
                    for f in done:f.result()
            except BaseException:
                stop.set()
                for f in verifies:f.cancel()
                raise
        check();guard()
        with (output/'verified.json').open('x') as f:
            json.dump(dict(manifest_sha256=manifest_hash,all_members_verified=True,
                           files=len(items),raw_bytes=doc['raw_bytes'],
                           seconds=time.monotonic()-began,original_files_retired=False),f)
            f.flush();os.fsync(f.fileno())
        check();guard();return doc
    except BaseException as error:
        stop.set()
        with (output/'failure.json').open('x') as f:
            json.dump(dict(accepted=False,error=repr(error),completed_members=len(completed)),f)
        raise


class Archive:
    def __init__(self,root,manifest_sha256,check=lambda:None,_preseal_verification=False):
        self.root=Path(root).resolve(strict=True)
        if (self.root/'failure.json').exists():raise ValueError('Failed archive')
        manifest=self.root/'manifest.json'
        if manifest.stat().st_size>MAX_MANIFEST:
            raise ValueError('Manifest size envelope')
        body=manifest.read_bytes()
        if len(body)>MAX_MANIFEST or hashlib.sha256(body).hexdigest()!=manifest_sha256:
            raise ValueError('Manifest identity changed')
        doc=json.loads(body);self.manifest=doc;self.manifest_sha256=manifest_sha256
        if (doc['format']!=3 or doc['frame_bytes']!=FRAME or doc['payload']!='payload.gta'
                or not 0<doc['max_file_bytes']<=2000000000 or not 0<doc['max_raw_bytes']<=40000000000
                or not 0<len(doc['files'])<=10000):raise ValueError('Streaming archive format')
        if not _preseal_verification:
            seal=self.root/'verified.json'
            if not seal.is_file() or seal.stat().st_size>8192:raise ValueError('No completion seal')
            value=json.loads(seal.read_bytes())
            if (value.get('manifest_sha256')!=manifest_sha256 or value.get('all_members_verified') is not True
                    or value.get('files')!=len(doc['files']) or value.get('raw_bytes')!=doc['raw_bytes']):
                raise ValueError('Completion seal mismatch')
        self.payload=self.root/'payload.gta'
        if self.payload.stat().st_size!=doc['payload_bytes'] or digest(self.payload,check)!=doc['payload_sha256']:
            raise ValueError('Payload changed')
        with self.payload.open('rb') as f:
            if f.read(len(MAGIC))!=MAGIC:raise ValueError('Payload magic')
        self.files={};intervals=[]
        for item in doc['files']:
            check();name=member_name(item['name'])
            if name in self.files or item['offset']!=0 or not 0<=item['bytes']<=doc['max_file_bytes']:
                raise ValueError('Invalid member')
            raw=stored=0
            for number,(offset,n,c,codec,h) in enumerate(item['frames']):
                if (not 0<n<=FRAME or not 0<c<=n or codec not in (0,1)
                        or len(bytes.fromhex(h))!=32 or (codec==0 and c!=n)
                        or (number<len(item['frames'])-1 and n!=FRAME)):
                    raise ValueError('Frame geometry')
                raw+=n;stored+=ROW.size+c;intervals.append((offset,offset+ROW.size+c))
            if raw!=item['bytes'] or stored!=item['stored_bytes']:raise ValueError('Member totals')
            self.files[name]=item
        position=len(MAGIC)
        for start,end in sorted(intervals):
            if start!=position or end<=start:raise ValueError('Frame gaps/overlaps')
            position=end
        if (position!=doc['payload_bytes'] or sum(v['bytes'] for v in self.files.values())!=doc['raw_bytes']
                or doc['raw_bytes']>doc['max_raw_bytes']):raise ValueError('Archive totals')

    def open(self,name,expected_sha256=None):
        item=self.files[member_name(name)]
        if expected_sha256 is not None and item['sha256']!=expected_sha256:
            raise ValueError('Original reference changed')
        return io.BufferedReader(Member(self.payload,item))

    def read_json(self,name,expected_sha256=None):
        with self.open(name,expected_sha256) as f:return json.load(f)

    def verify(self,name,check=lambda:None):
        h=hashlib.sha256()
        with self.open(name) as f:
            for raw in iter(lambda:f.read(FRAME),b''):check();h.update(raw)
        if h.hexdigest()!=self.files[name]['sha256']:raise ValueError('Member checksum changed')
        return self.files[name]['bytes']
