"""Lossless XZ bundles for newly owned research scratch, never legacy evidence.

Explicit manifests authenticate both container and every original byte stream.
Retiring raw scratch requires a durable, independently decoded archive first.
"""
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import struct

MAX_RAW = 512 * 1024**2
MAX_PACKED = 128 * 1024**2
MAX_HEADER = 1024**2
ROOT = Path('S:/GTOpen-research').resolve()
MAGIC = b'GTOARCH1'


def digest(raw): return hashlib.sha256(raw).hexdigest()
def encoded(v): return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def owner(root,token):
    root=Path(root).resolve()
    if root==ROOT or not root.is_relative_to(ROOT): raise ValueError('Owned research descendant required')
    p=root
    while p!=ROOT:
        if p.is_symlink() or p.lstat().st_file_attributes & 0x400: raise ValueError('Linked ownership path')
        p=p.parent
    record=json.loads((root/'archive-owner.json').read_bytes())
    if record!={'format':1,'token':token,'purpose':'new-research-scratch-v1'}:
        raise ValueError('Explicit new scratch ownership required')
    return root


def name(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*\.(json|npz)',value):
        raise ValueError('Single JSON or NPZ member name required')
    return value


def unpack(path,manifest,*,guard):
    guard();path=Path(path)
    if manifest.get('format')!=1 or manifest.get('codec')!='xz-bundle-v1':raise ValueError('Wrong archive format')
    n=manifest['packed_bytes']
    if type(n)!=int or not 0<n<=MAX_PACKED or path.stat().st_size!=n or path.is_symlink():
        raise ValueError('Invalid archive length/type')
    packed=path.read_bytes()
    if digest(packed)!=manifest['packed_sha256']:raise ValueError('Changed compressed archive')
    decoder=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=128*1024**2)
    raw=decoder.decompress(packed,max_length=MAX_RAW+MAX_HEADER+17)
    if not decoder.eof or decoder.unused_data or len(raw)>MAX_RAW+MAX_HEADER+16:
        raise ValueError('Oversized, truncated or trailing archive')
    if raw[:8]!=MAGIC:raise ValueError('Wrong archive magic')
    size=struct.unpack('<Q',raw[8:16])[0]
    if not 0<size<=MAX_HEADER:raise ValueError('Invalid member header')
    header=json.loads(raw[16:16+size]);offset=16+size;result={}
    if header!=manifest['members']:raise ValueError('Member manifest differs')
    for item in header:
        key=name(item['name']);length=item['bytes']
        if key in result or type(length)!=int or not 0<=length<=MAX_RAW:raise ValueError('Invalid member')
        data=raw[offset:offset+length];offset+=length
        if len(data)!=length or digest(data)!=item['sha256']:raise ValueError('Changed original bytes')
        result[key]=data
    if offset!=len(raw) or not result:raise ValueError('Trailing or empty archive')
    guard();return result


def pack(source,names,destination,*,root,token,guard):
    root=owner(root,token);source=Path(source).resolve();destination=Path(destination).resolve()
    if source==root or not source.is_relative_to(root) or not destination.is_relative_to(root):
        raise ValueError('Sources and archives must stay inside owned scratch')
    # Every source ancestor is checked, not merely the resolved final filename.
    for ancestor in [source,*source.parents]:
        if ancestor==root:break
        if ancestor.is_symlink() or ancestor.lstat().st_file_attributes & 0x400:raise ValueError('Linked source folder')
    names=list(names)
    if len(names)!=len(set(names)) or not names:raise ValueError('Distinct members required')
    items=[];payload=[]
    for key in sorted(names):
        guard();key=name(key);path=source/key
        if path.is_symlink() or path.lstat().st_file_attributes & 0x400:raise ValueError('Linked member')
        if path.stat().st_size+sum(map(len,payload))>MAX_RAW:raise ValueError('Raw bundle exceeds cap')
        data=path.read_bytes();payload.append(data)
        items.append(dict(name=key,bytes=len(data),sha256=digest(data)))
    if sum(map(len,payload))>MAX_RAW:raise ValueError('Bounded raw bundle required')
    header=encoded(items)
    if len(header)>MAX_HEADER:raise ValueError('Member header too large')
    packed=lzma.compress(MAGIC+struct.pack('<Q',len(header))+header+b''.join(payload),preset=6)
    if len(packed)>MAX_PACKED:raise ValueError('Archive exceeds cap')
    manifest=dict(format=1,codec='xz-bundle-v1',packed_bytes=len(packed),packed_sha256=digest(packed),members=items)
    guard()
    with destination.open('xb') as stream:stream.write(packed);stream.flush();os.fsync(stream.fileno())
    restored=unpack(destination,manifest,guard=guard)
    if restored!={i['name']:b for i,b in zip(items,payload)}:raise ValueError('Archive readback differs')
    with destination.with_suffix(destination.suffix+'.json').open('xb') as stream:
        stream.write(encoded(manifest));stream.flush();os.fsync(stream.fileno())
    return manifest


def retire(source,destination,manifest,*,root,token,guard):
    """Remove only exact owned duplicate files; retain directory and durable archive."""
    root=owner(root,token);source=Path(source).resolve();destination=Path(destination).resolve()
    if source==root or not source.is_relative_to(root) or not destination.is_relative_to(root):
        raise ValueError('Removal must stay inside new owned scratch')
    if json.loads(destination.with_suffix(destination.suffix+'.json').read_bytes())!=manifest:
        raise ValueError('Durable archive manifest required before retirement')
    restored=unpack(destination,manifest,guard=guard)
    targets=[]
    for key,data in restored.items():
        target=source/name(key)
        if (target.resolve().parent!=source or not target.resolve().is_relative_to(root)
                or target.is_symlink() or target.lstat().st_file_attributes & 0x400
                or target.read_bytes()!=data):raise ValueError('Changed or redirected raw scratch')
        targets.append(target)
    guard()
    for target in targets:target.unlink()  # Nonrecursive, validated owned duplicate files only.
