"""Persistent reservations for owned raw writers, with quiescent reconciliation.

Polling examines active declared outputs, not every retained file. Closed files
are rechecked at explicit complete boundaries. This is admission/acceptance
accounting, not a hard transient filesystem quota or raw-byte authenticator.
"""
import contextlib
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import time
import uuid
import psutil

METHOD = 'persistent-owned-archived-residency-reservations-v5'
LIMITS = ('allocated_core_bytes','logical_core_bytes','live_burst_bytes',
          'metadata_slack_bytes','diagnostic_reserve_bytes','max_owners','max_raw_integrity_read_bytes')
DLL = None


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


class Info(ctypes.Structure):
    _fields_ = [('attributes',wintypes.DWORD),('created',wintypes.FILETIME),
        ('accessed',wintypes.FILETIME),('written',wintypes.FILETIME),
        ('volume',wintypes.DWORD),('high',wintypes.DWORD),('low',wintypes.DWORD),
        ('links',wintypes.DWORD),('index_high',wintypes.DWORD),('index_low',wintypes.DWORD)]


def api():
    global DLL
    require(os.name=='nt','Windows allocation accounting required')
    if DLL is None:
        dll=ctypes.WinDLL('kernel32',use_last_error=True)
        dll.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,
            wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
        dll.CreateFileW.restype=wintypes.HANDLE
        dll.GetFileInformationByHandle.argtypes=[wintypes.HANDLE,ctypes.POINTER(Info)]
        dll.GetFileInformationByHandle.restype=wintypes.BOOL
        dll.CloseHandle.argtypes=[wintypes.HANDLE];dll.CloseHandle.restype=wintypes.BOOL
        dll.GetCompressedFileSizeW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
        dll.GetCompressedFileSizeW.restype=wintypes.DWORD
        dll.GetDiskFreeSpaceW.argtypes=[wintypes.LPCWSTR]+[ctypes.POINTER(wintypes.DWORD)]*4
        dll.GetDiskFreeSpaceW.restype=wintypes.BOOL
        DLL=dll
    return DLL


def information(path, *, directory=False):
    dll=api();name='\\\\?\\'+str(path)
    handle=dll.CreateFileW(name,0x80,7,None,3,0x02200000,None)
    if handle==wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        v=Info()
        if not dll.GetFileInformationByHandle(handle,ctypes.byref(v)):
            raise ctypes.WinError(ctypes.get_last_error())
        require(not v.attributes&0x400 and bool(v.attributes&0x10)==directory,'Ordinary file/directory required')
        if not directory:
            require(v.links==1,'Single-link output required')
        high=wintypes.DWORD();ctypes.set_last_error(0)
        low=dll.GetCompressedFileSizeW(name,ctypes.byref(high)) if not directory else 0
        if low==0xffffffff and ctypes.get_last_error():
            raise ctypes.WinError(ctypes.get_last_error())
        return dict(volume=v.volume,index=(v.index_high<<32)|v.index_low,
            logical=(v.high<<32)|v.low,api_named=(high.value<<32)|low,
            written=(v.written.dwHighDateTime<<32)|v.written.dwLowDateTime,
            created=(v.created.dwHighDateTime<<32)|v.created.dwLowDateTime,
            attributes=v.attributes)
    finally:
        if not dll.CloseHandle(handle):
            raise ctypes.WinError(ctypes.get_last_error())


class Guard:
    def __init__(self,config):
        require(isinstance(config,dict),'Explicit immutable IO config required')
        role=config.get('resource_driver',{})
        require(role==dict(name='resource_driver_archived_comparison_v5',path=str(Path(__file__).resolve()),
            sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),'Frozen actual resource-driver role required')
        require(config.get('execution_mode') in ('study','software-control'),'Explicit execution mode')
        require(config.get('method')=='scoped-expected-comparison-archived-io-v4','Declared compatible IO contract required')
        document=dict(config);config_sha=document.pop('config_sha256',None)
        require(config_sha==hashlib.sha256((encode(document)+'\n').encode()).hexdigest(),'Immutable config hash changed')
        require(all(type(config.get(k)) is int and config[k]>0 for k in LIMITS),'Explicit positive budgets required')
        require(config['max_owners']<=6,'At most six owners required')
        ceiling=(16_000_000_000,512_000_000_000,6_000_000_000,1_000_000_000,64_000_000,6,16_000_000_000_000)
        if config['execution_mode']=='study':
            raise ValueError('Prospective study admission not qualified; software controls only')
            require(tuple(config[k] for k in LIMITS)==ceiling,'Exact full-comparison study caps required')
        else:
            require(all(config[k]<=v for k,v in zip(LIMITS,ceiling)),'Bounded separate software-control caps required')
        self.config=json.loads(encode(config));self.root=Path(os.path.abspath(config['store_root']))
        require(self.root.parent==Path(r'S:\GTOpen-research') and self.root.resolve()==self.root,
            'Canonical direct S research store required')
        ident=information(self.root,directory=True)
        require(config['store_identity']=={k:ident[k] for k in ('volume','index')},'Root identity changed')
        self.identity=config['store_identity'];self.config_raw=encode(config)
        values=[wintypes.DWORD() for _ in range(4)]
        if not api().GetDiskFreeSpaceW(str(self.root.anchor),*[ctypes.byref(v) for v in values]):
            raise ctypes.WinError(ctypes.get_last_error())
        self.cluster=values[0].value*values[1].value
        self.directory=self.root/'diagnostics';self.directory.mkdir(exist_ok=True)
        information(self.directory,directory=True)
        self.db=self.directory/'raw-reservations-v1.sqlite3'
        self.birth=psutil.Process().create_time();self.pid=os.getpid();self.scans=0;self.attempted_integrity_reads=0
        with self._transaction(initialize=True) as c:
            c.execute('CREATE TABLE IF NOT EXISTS settings(config TEXT,operations INTEGER,closed_logical INTEGER,closed_named INTEGER,diagnostic_logical INTEGER,closed_files INTEGER,integrity_read INTEGER)')
            c.execute('CREATE TABLE IF NOT EXISTS owners(pid INTEGER,birth REAL,active INTEGER,PRIMARY KEY(pid,birth))')
            c.execute('CREATE TABLE IF NOT EXISTS reservations(token TEXT PRIMARY KEY,paths TEXT,maximum INTEGER,named_maximum INTEGER,kind TEXT,protected INTEGER,pid INTEGER,birth REAL)')
            c.execute('CREATE TABLE IF NOT EXISTS closed(path TEXT PRIMARY KEY,info TEXT,kind TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS archives(id TEXT PRIMARY KEY,outputs TEXT,manifest_sha256 TEXT,members TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS retirements(path TEXT PRIMARY KEY,archive_id TEXT,state TEXT,original_info TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY,operation TEXT,token TEXT,unix REAL)')
            rows=c.execute('SELECT config FROM settings').fetchall()
            if not rows:
                c.execute('INSERT INTO settings VALUES(?,0,0,0,0,0,0)',(self.config_raw,))
            else:
                require(rows==[(self.config_raw,)],'Changed persistent config; counters are not reset')
            c.execute('INSERT OR REPLACE INTO owners VALUES(?,?,1)',(self.pid,self.birth))
            self._audit(c,'open','')
            self._snapshot(c,False)

    @contextlib.contextmanager
    def _transaction(self,initialize=False):
        ident=information(self.root,directory=True)
        require({k:ident[k] for k in ('volume','index')}==self.identity,'Root directory replaced')
        c=sqlite3.connect(self.db,timeout=20,isolation_level=None);reads0=self.attempted_integrity_reads
        try:
            c.execute('PRAGMA journal_mode=DELETE');c.execute('PRAGMA synchronous=FULL');c.execute('BEGIN IMMEDIATE')
            if not initialize:
                require(c.execute('SELECT config FROM settings').fetchall()==[(self.config_raw,)],'Persistent config changed')
            yield c
            c.execute('COMMIT')
        except BaseException:
            if c.in_transaction:
                c.execute('ROLLBACK')
            # Hash work already performed is charged even when file acceptance
            # fails. No failed reservation, partial output or read credit is reset.
            failed_reads=self.attempted_integrity_reads-reads0
            if failed_reads:
                c.execute('BEGIN IMMEDIATE')
                c.execute('UPDATE settings SET integrity_read=integrity_read+?',(failed_reads,))
                self._audit(c,'failed-integrity-read','')
                c.execute('COMMIT')
            raise
        finally:
            c.close()

    def _audit(self,c,operation,token):
        c.execute('UPDATE settings SET operations=operations+1')
        seq=c.execute('SELECT operations FROM settings').fetchone()[0]
        c.execute('INSERT INTO audit VALUES(?,?,?,?)',(seq,operation,token,time.time()))
        pages=c.execute('PRAGMA page_count').fetchone()[0]*c.execute('PRAGMA page_size').fetchone()[0]
        journal=Path(str(self.db)+'-journal')
        journal_bytes=self._named(information(journal)) if journal.exists() else 0
        require(pages+journal_bytes+2*self.cluster<=self.config['metadata_slack_bytes'],
            'Transaction metadata reserve exhausted before publication')

    def _path(self,path):
        path=Path(os.path.abspath(path))
        require(path!=self.root and path.is_relative_to(self.root) and path.resolve()==path,'Output escaped owned root')
        for parent in [path.parent,*path.parent.parents]:
            if not parent.is_relative_to(self.root):
                break
            if parent.exists():
                information(parent,directory=True)
        require(path not in (self.db,Path(str(self.db)+'-journal')),'Writer targets private ledger')
        # Windows aliases must reserve the same history key even after a raw
        # file has been removed. Existing Path equality alone is insufficient.
        return os.path.normcase(str(path.relative_to(self.root)))

    def _named(self,info):
        # GetCompressedFileSize may give logical bytes for an uncompressed file;
        # round to actual cluster boundaries rather than claiming partial clusters.
        return math.ceil(info['api_named']/self.cluster)*self.cluster

    def _metadata(self):
        total=0
        for path in (self.db,Path(str(self.db)+'-journal')):
            if path.exists():
                total+=self._named(information(path))
        require(total<=self.config['metadata_slack_bytes'],'Private ledger metadata reserve exhausted')
        return total

    def _hash_closed(self,c,path,info):
        limit=self.config['max_raw_integrity_read_bytes']
        require(type(limit) is int and limit>0,'Explicit finite integrity read bound')
        used=c.execute('SELECT integrity_read FROM settings').fetchone()[0]
        require(used+info['logical']<=limit,'Cumulative raw-integrity read budget')
        # Caller must establish producer termination. This verifies a stable
        # closed read; it does not prevent a foreign application from rewriting.
        self.attempted_integrity_reads+=info['logical'];value=hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1_048_576),b''):
                value.update(block)
        after=information(path)
        require(all(after[k]==info[k] for k in ('volume','index','logical','created','written')),
            'File changed during integrity hashing')
        c.execute('UPDATE settings SET integrity_read=integrity_read+?',(info['logical'],))
        return value.hexdigest()

    def _snapshot(self,c,critical):
        pending=list(c.execute('SELECT token,paths,maximum,named_maximum,kind,protected,pid,birth FROM reservations'))
        logical,named,diagnostic,closed_count=c.execute('SELECT closed_logical,closed_named,diagnostic_logical,closed_files FROM settings').fetchone()
        active_bytes=0;active_files=0
        for token,paths,maximum,named_max,kind,protected,pid,birth in pending:
            actual=actual_named=0
            for text in json.loads(paths):
                path=self.root/text
                self._path(path)
                if path.exists():
                    value=information(path);actual+=value['logical'];actual_named+=self._named(value);active_files+=1
            require(actual<=maximum and actual_named<=named_max,'Active writer exceeded reserved aggregate output')
            active_bytes+=actual;logical+=maximum;named+=named_max
            if kind.startswith('diagnostic'):
                diagnostic+=maximum
        owners=0
        for pid,birth in c.execute('SELECT pid,birth FROM owners WHERE active=1'):
            try:
                process=psutil.Process(pid)
                owners+=abs(process.create_time()-birth)<.002
            except psutil.NoSuchProcess:
                pass
        require(owners<=self.config['max_owners'],'Six-owner ceiling exceeded')
        metadata=self._metadata()
        extra=self.config['live_burst_bytes']+self.config['diagnostic_reserve_bytes'] if critical else 0
        require(logical<=self.config['logical_core_bytes']+extra,'Logical retained-plus-pending ceiling')
        require(named+self.config['metadata_slack_bytes']<=self.config['allocated_core_bytes']+extra,'Named retained-plus-pending ceiling')
        require(diagnostic<=self.config['diagnostic_reserve_bytes'],'Diagnostic reserve exhausted')
        return dict(method=METHOD,logical_bytes=logical,named_allocated_file_bytes=named+metadata,
            diagnostic_logical_bytes=diagnostic,closed_files=closed_count,active_files=active_files,
            active_actual_logical_bytes=active_bytes,pending_writers=len(pending),live_owners=owners,
            reserved_named_bytes=sum(v[3] for v in pending),metadata_allocated_bytes=metadata,
            full_scans_in_this_process=self.scans,hard_filesystem_quota=False,
            integrity_read_bytes=c.execute('SELECT integrity_read FROM settings').fetchone()[0],
            integrity_read_ceiling_bytes=self.config['max_raw_integrity_read_bytes'])

    def admit(self,critical=False):
        require(type(critical) is bool,'Explicit critical flag')
        with self._transaction() as c:
            return self._snapshot(c,critical)

    def reserve(self,paths,max_bytes,kind,protected=False):
        require(isinstance(paths,(list,tuple)) and 0<len(paths)<=16,'Declared finite output paths required')
        require(type(max_bytes) is int and 0<max_bytes<=8_000_000_000,'Finite aggregate logical bound required')
        require(isinstance(kind,str) and re.fullmatch('[a-z][a-z0-9-]{0,79}',kind),'Explicit writer kind required')
        require(type(protected) is bool and (not protected or kind.startswith('diagnostic')),'Only diagnostics use protected tail')
        names=[self._path(path) for path in paths]
        require(len(set(names))==len(names),'Duplicate output paths')
        token=uuid.uuid4().hex
        with self._transaction() as c:
            used={p for p, in c.execute('SELECT path FROM closed')}
            for p, in c.execute('SELECT paths FROM reservations'):
                used.update(json.loads(p))
            require(not used.intersection(names),'Output path already closed or reserved')
            require(not any(os.path.lexists(self.root/name) for name in names),'Writer requires new output paths')
            named_max=max_bytes+self.cluster*(len(names)+1)
            c.execute('INSERT INTO reservations VALUES(?,?,?,?,?,?,?,?)',
                (token,encode(names),max_bytes,named_max,kind,int(protected),self.pid,self.birth))
            self._snapshot(c,protected)
            self._audit(c,'reserve',token)
        return token

    def seal(self,token,paths):
        require(isinstance(token,str) and re.fullmatch('[0-9a-f]{32}',token),'Explicit reservation token')
        require(isinstance(paths,(list,tuple)) and len(paths)>0,'Declared final paths required')
        names=[self._path(p) for p in paths]
        require(len(set(names))==len(names),'Duplicate final paths')
        with self._transaction() as c:
            row=c.execute('SELECT paths,maximum,named_maximum,kind,protected,pid,birth FROM reservations WHERE token=?',(token,)).fetchone()
            require(row is not None,'Missing or already sealed reservation')
            declared,maximum,named_max,kind,protected,pid,birth=row
            require((pid,birth)==(self.pid,self.birth),'Writer ownership differs from reservation')
            declared=json.loads(declared)
            require(set(names).issubset(declared),'Unregistered rename destination')
            require(set(names)==set(declared) or kind in ('diagnostic-rename','archive-group'),'Only declared diagnostic temp-to-final rename may omit a path')
            require(all(not os.path.lexists(self.root/p) for p in set(declared)-set(names)),'Unsealed alternate path still exists')
            values={name:information(self.root/name) for name in names}
            require(sum(v['logical'] for v in values.values())<=maximum and
                sum(self._named(v) for v in values.values())<=named_max,'Sealed writer exceeded aggregate bound')
            for name,v in values.items():
                v['raw_sha256']=self._hash_closed(c,self.root/name,v)
                c.execute('INSERT INTO closed VALUES(?,?,?)',(name,encode(v),kind))
            logical=sum(v['logical'] for v in values.values());named=sum(self._named(v) for v in values.values())
            c.execute('UPDATE settings SET closed_logical=closed_logical+?,closed_named=closed_named+?,diagnostic_logical=diagnostic_logical+?,closed_files=closed_files+?',
                (logical,named,logical if kind.startswith('diagnostic') else 0,len(values)))
            c.execute('DELETE FROM reservations WHERE token=?',(token,))
            self._snapshot(c,bool(protected));self._audit(c,'seal',token)
            return dict(token=token,files=values,logical=sum(v['logical'] for v in values.values()),
                named=sum(self._named(v) for v in values.values()))

    def quiescent(self,compression_receipts=()):
        require(isinstance(compression_receipts,(list,tuple)),'Explicit ordered compression receipts')
        compression={}
        for receipt in compression_receipts:
            require(isinstance(receipt,dict) and receipt.get('method')=='closed-file-ntfs-compression-v1',
                'Qualified compression helper receipt required')
            path=self._path(receipt['path'])
            require(path not in compression,'Duplicate compression path')
            compression[path]=receipt
        with self._transaction() as c:
            require(c.execute('SELECT COUNT(*) FROM reservations').fetchone()[0]==0,
                'Unfinished/failed writer reservations remain; no release or reset')
            history={p:json.loads(v) for p,v in c.execute('SELECT path,info FROM closed')}
            retirements=list(c.execute('SELECT path,archive_id,state,original_info FROM retirements'))
            require(all(state=='retired' for _,_,state,_ in retirements),
                'Unsettled retirement intent; explicit storage reconciliation required')
            retired={p for p,_,_,_ in retirements}
            require(retired.issubset(history),'Retirement without immutable member history')
            expected={p:v for p,v in history.items() if p not in retired}
            counters=c.execute('SELECT closed_logical,closed_named,diagnostic_logical,closed_files FROM settings').fetchone()
            expected_diagnostic=sum(json.loads(v)['logical'] for v,kind in c.execute('SELECT info,kind FROM closed') if kind.startswith('diagnostic'))
            require(counters==(sum(v['logical'] for v in history.values()),sum(self._named(v) for v in expected.values()),expected_diagnostic,len(history)),
                'Closed totals differ from persistent file ledger')
            for path,archive_id,_,original in retirements:
                require(json.loads(original)==history[path],'Retired member history changed')
                archive=c.execute('SELECT outputs,manifest_sha256,members FROM archives WHERE id=?',(archive_id,)).fetchone()
                require(archive is not None and path in json.loads(archive[2]),'Missing accepted archive membership')
                for output,info in json.loads(archive[0]).items():
                    require(output in expected and all(expected[output][k]==info[k] for k in
                        ('volume','index','logical','created','written','raw_sha256')),
                        'Accepted archive container history changed')
            actual={};self.scans+=1
            for directory,dirs,names in os.walk(self.root,followlinks=False):
                for name in dirs:
                    information(Path(directory)/name,directory=True)
                for name in names:
                    path=Path(directory)/name
                    if path in (self.db,Path(str(self.db)+'-journal')):
                        continue
                    relative=self._path(path);actual[relative]=information(path)
            require(set(actual)==set(expected),'Unreserved creation or disappearance at complete boundary')
            require(set(compression).issubset(actual),'Compression receipt refers to absent closed file')
            inherited_settlements=[]
            for path,value in actual.items():
                old=expected[path]
                require(all(value[k]==old[k] for k in ('volume','index','logical','created','written')),
                    'Closed file identity/size/write time changed')
                require((value['attributes']^old['attributes'])&~0x800==0,'Unexpected closed-file attribute change')
                changed=value['attributes']!=old['attributes'] or value['api_named']!=old['api_named']
                if changed or path in compression:
                    if path in compression:
                        receipt=compression[path]
                        require(receipt['raw_sha256']==old['raw_sha256'] and receipt['logical_bytes']==old['logical'],
                            'Compression raw identity differs from sealed file')
                        require(receipt['before']['volume']==old['volume'] and receipt['before']['index']==old['index']
                            and receipt['after']['volume']==value['volume'] and receipt['after']['index']==value['index']
                            and receipt['before']['written']==old['written'] and receipt['after']['written']==value['written'],
                            'Compression metadata witness differs')
                    else:
                        # NTFS inherited compression may settle after a writer
                        # closes/seals. Credit only a lower allocation, with the
                        # same already-compressed attributes and exact sealed
                        # identity, size and creation/write times checked above.
                        require(value['attributes']==old['attributes'] and value['attributes']&0x800
                            and value['api_named']<old['api_named'],
                            'Unwitnessed closed-file compression change')
                    require(self._hash_closed(c,self.root/path,value)==old['raw_sha256'],
                        'Compression changed sealed raw bytes')
                    if path not in compression:
                        inherited_settlements.append(dict(path=str(self.root/path),raw_sha256=old['raw_sha256'],
                            logical_bytes=old['logical'],before=old,after=value.copy(),
                            method='sha256-verified-inherited-ntfs-allocation-settlement-v1'))
                value['raw_sha256']=old['raw_sha256']
                c.execute('UPDATE closed SET info=? WHERE path=?',(encode(value),path))
            c.execute('UPDATE settings SET closed_named=?',(sum(self._named(v) for v in actual.values()),))
            self._audit(c,'quiescent','')
            return dict(self._snapshot(c,False),verified_inherited_compression_settlements=inherited_settlements,
                archived_members=len(retired),archived_original_logical_bytes=sum(history[p]['logical'] for p in retired),
                resident_closed_logical_bytes=sum(v['logical'] for v in expected.values()))

    def close(self):
        with self._transaction() as c:
            c.execute('UPDATE owners SET active=0 WHERE pid=? AND birth=?',(self.pid,self.birth))
            self._audit(c,'close','')

    def charge_integrity(self,amount,operation):
        """Persist a conservative read charge before external codec work."""
        require(type(amount) is int and amount>=0,'Finite prepaid integrity bytes')
        require(isinstance(operation,str) and re.fullmatch('[a-z][a-z0-9-]{0,79}',operation),
            'Explicit integrity operation')
        with self._transaction() as c:
            used=c.execute('SELECT integrity_read FROM settings').fetchone()[0]
            limit=self.config['max_raw_integrity_read_bytes']
            require(used+amount<=limit,'Cumulative external-integrity read budget')
            c.execute('UPDATE settings SET integrity_read=integrity_read+?',(amount,))
            self._audit(c,operation,'')

    def archive_members(self,source_root,output,members,*,max_pack_bytes,guard=lambda:None,workers=8):
        """Complete one reserved archive; this does not retire any member."""
        from sealed_cycle_archive_v3 import create, Archive
        source_root=Path(source_root);output=Path(output)
        self._path(source_root);self._path(output)
        require(source_root.is_dir() and not output.exists(),'New disjoint archive destination required')
        require(0<len(members)<=10000,'Explicit finite member list')
        names=[self._path(p) for p in members]
        require(len(set(names))==len(names),'Duplicate archive members')
        self.quiescent()
        with self._transaction() as c:
            require(c.execute('SELECT COUNT(*) FROM retirements WHERE state!=?',('retired',)).fetchone()[0]==0,
                'Unsettled retirement intent')
            items=[]
            for name in names:
                row=c.execute('SELECT info,kind FROM closed WHERE path=?',(name,)).fetchone()
                require(row is not None and row[1]=='native-aggregate',
                    'Only closed native bulk from this owned attempt may be archived')
                require(c.execute('SELECT COUNT(*) FROM retirements WHERE path=?',(name,)).fetchone()[0]==0,
                    'Member already planned or retired')
                for old, in c.execute('SELECT members FROM archives'):
                    require(name not in json.loads(old),'Member already has an accepted archive')
                info=json.loads(row[0]);path=self.root/name
                require(path.is_relative_to(source_root),'Member outside closed context')
                require(information(path)=={k:v for k,v in info.items() if k!='raw_sha256'},
                    'Archive source identity differs from sealed record')
                items.append(dict(name=path.relative_to(source_root).as_posix(),bytes=info['logical'],
                    sha256=info['raw_sha256'],identity={k:v for k,v in info.items() if k!='raw_sha256'}))
        raw=sum(v['bytes'] for v in items)
        maximum=max_pack_bytes+16_000_000+16_384
        outputs=[output/n for n in ('payload.gta','manifest.json','verified.json','failure.json')]
        token=self.reserve(outputs,maximum,'archive-group')
        # Encoder source, create verification, acceptance verification; all pack
        # body digests/decoding plus manifest reads are included conservatively.
        # This is prepaid and never refunded, including interrupted operations.
        self.charge_integrity(3*raw+8*max_pack_bytes+64_000_000,'archive-prepaid-read')
        create(source_root,output,items,identity=information,guard=guard,workers=workers,
            max_pack_bytes=max_pack_bytes)
        actual=[p for p in outputs if p.exists()]
        require(set(actual)==set(outputs[:3]),'Only complete successful archive may be accepted')
        sealed=self.seal(token,actual)
        manifest_sha=sealed['files'][self._path(output/'manifest.json')]['raw_sha256']
        archive=Archive(output,manifest_sha)
        require(archive.manifest['source_root']==str(source_root.resolve()),'Archive source namespace differs')
        require(set(archive.files)=={v['name'] for v in items},'Archive membership differs from selected outputs')
        for item in items:
            require(archive.files[item['name']]['bytes']==item['bytes'] and
                archive.files[item['name']]['sha256']==item['sha256'], 'Archive original member differs')
            archive.verify(item['name'])
        archive_id=uuid.uuid4().hex
        with self._transaction() as c:
            c.execute('INSERT INTO archives VALUES(?,?,?,?)',
                (archive_id,encode(sealed['files']),manifest_sha,encode(names)))
            self._audit(c,'accept-archive',archive_id);self._snapshot(c,False)
        return dict(archive_id=archive_id,root=str(output),manifest_sha256=manifest_sha,members=names,
            archived_original_bytes=raw,containers=sealed['files'],originals_retired=False)

    def _accepted_archive(self,c,archive_id):
        row=c.execute('SELECT outputs,manifest_sha256,members FROM archives WHERE id=?',(archive_id,)).fetchone()
        require(row is not None,'No accepted immutable archive')
        outputs=json.loads(row[0])
        for name,old in outputs.items():
            actual=information(self.root/name)
            require(all(actual[k]==old[k] for k in ('volume','index','logical','created','written')),
                'Accepted archive container replaced or changed')
            require((actual['attributes']^old['attributes'])&~0x800==0,'Archive attributes changed')
        return outputs,row[1],json.loads(row[2])

    @contextlib.contextmanager
    def _pin_archive(self,archive_id):
        """Keep verified containers open, denying write/delete until retirement ends."""
        from sealed_cycle_archive_v3 import Archive
        handles=[]
        try:
            with self._transaction() as c:
                row=c.execute('SELECT outputs,manifest_sha256,members FROM archives WHERE id=?',(archive_id,)).fetchone()
                require(row is not None,'No accepted archive')
                outputs=json.loads(row[0])
            for name,old in outputs.items():
                path=self.root/name;self._path(path)
                handle=api().CreateFileW('\\\\?\\'+str(path),0x80000080,1,None,3,0x00200000,None)
                if handle==wintypes.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
                handles.append(handle);v=Info()
                if not api().GetFileInformationByHandle(handle,ctypes.byref(v)):
                    raise ctypes.WinError(ctypes.get_last_error())
                require(v.links==1 and not v.attributes&(0x400|0x10),'Ordinary pinned archive container')
                require((v.volume,(v.index_high<<32)|v.index_low,(v.high<<32)|v.low,
                    (v.created.dwHighDateTime<<32)|v.created.dwLowDateTime,
                    (v.written.dwHighDateTime<<32)|v.written.dwLowDateTime)==
                    tuple(old[k] for k in ('volume','index','logical','created','written')),
                    'Pinned archive container differs from accepted identity')
            manifest_name=next(p for p in outputs if Path(p).name=='manifest.json')
            # Prepaid constructor digest; member verification was performed at
            # acceptance, and every frame is authenticated on later readback.
            self.charge_integrity(sum(v['logical'] for v in outputs.values())+8,'archive-pin-read')
            archive=Archive((self.root/manifest_name).parent,row[1])
            yield archive
        finally:
            for handle in reversed(handles):
                if not api().CloseHandle(handle):raise ctypes.WinError(ctypes.get_last_error())

    def _retire_one_pinned(self,archive_id,path,*,_after_delete=None):
        """Witness exact handle deletion; a crash leaves a durable intent."""
        name=self._path(path);path=self.root/name
        dll=api()
        handle=dll.CreateFileW('\\\\?\\'+str(path),0x80010000,1,None,3,0x00200000,None)
        if handle==wintypes.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
        try:
            value=Info()
            if not dll.GetFileInformationByHandle(handle,ctypes.byref(value)):
                raise ctypes.WinError(ctypes.get_last_error())
            require(not value.attributes&(0x400|0x10) and value.links==1,'Ordinary single-link retirement member')
            with self._transaction() as c:
                _,_,members=self._accepted_archive(c,archive_id)
                require(name in members,'Unaccepted archive member')
                require(c.execute('SELECT COUNT(*) FROM reservations').fetchone()[0]==0,'Live writer prevents retirement')
                require(c.execute('SELECT COUNT(*) FROM retirements WHERE path=?',(name,)).fetchone()[0]==0,
                    'Existing retirement intent; do not retry')
                old=json.loads(c.execute('SELECT info FROM closed WHERE path=?',(name,)).fetchone()[0])
                require((value.volume,(value.index_high<<32)|value.index_low,(value.high<<32)|value.low,
                    (value.created.dwHighDateTime<<32)|value.created.dwLowDateTime,
                    (value.written.dwHighDateTime<<32)|value.written.dwLowDateTime)==
                    tuple(old[k] for k in ('volume','index','logical','created','written')),
                    'Retirement member identity changed')
                used=c.execute('SELECT integrity_read FROM settings').fetchone()[0]
                limit=self.config['max_raw_integrity_read_bytes']
                require(used+old['logical']<=limit,'Retirement read ceiling')
                # Prepaid before reading through the exact deletion handle.
                c.execute('UPDATE settings SET integrity_read=integrity_read+?',(old['logical'],))
                self._audit(c,'retirement-prepaid-read',name)
            dll.ReadFile.argtypes=[wintypes.HANDLE,wintypes.LPVOID,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD),wintypes.LPVOID]
            dll.ReadFile.restype=wintypes.BOOL
            buffer=ctypes.create_string_buffer(1_048_576);n=wintypes.DWORD();sha=hashlib.sha256();total=0
            while True:
                if not dll.ReadFile(handle,buffer,len(buffer),ctypes.byref(n),None):
                    raise ctypes.WinError(ctypes.get_last_error())
                if not n.value:break
                total+=n.value;sha.update(buffer.raw[:n.value])
            require(total==old['logical'] and sha.hexdigest()==old['raw_sha256'],'Retirement raw hash changed')
            with self._transaction() as c:
                self._accepted_archive(c,archive_id)
                require(c.execute('SELECT info FROM closed WHERE path=?',(name,)).fetchone()==(encode(old),),
                    'Closed member changed before retirement intent')
                c.execute('INSERT INTO retirements VALUES(?,?,?,?)',(name,archive_id,'intent',encode(old)))
                self._audit(c,'retirement-intent',name);self._snapshot(c,False)
            dll.SetFileInformationByHandle.argtypes=[wintypes.HANDLE,ctypes.c_int,wintypes.LPVOID,wintypes.DWORD]
            dll.SetFileInformationByHandle.restype=wintypes.BOOL
            delete=ctypes.c_ubyte(1)
            if not dll.SetFileInformationByHandle(handle,4,ctypes.byref(delete),ctypes.sizeof(delete)):
                raise ctypes.WinError(ctypes.get_last_error())
        finally:
            if not dll.CloseHandle(handle):raise ctypes.WinError(ctypes.get_last_error())
        require(not os.path.lexists(path),'Retirement did not remove exact member')
        if _after_delete is not None:_after_delete()
        self._complete_retirement(archive_id,name)

    def _retire_one(self,archive_id,path,*,_after_delete=None):
        with self._pin_archive(archive_id):
            self._retire_one_pinned(archive_id,path,_after_delete=_after_delete)

    def _complete_retirement(self,archive_id,name):
        with self._transaction() as c:
            self._accepted_archive(c,archive_id)
            row=c.execute('SELECT archive_id,state,original_info FROM retirements WHERE path=?',(name,)).fetchone()
            require(row is not None and row[:2]==(archive_id,'intent'),'No matching durable retirement intent')
            require(not os.path.lexists(self.root/name),'Intent member still resident; no space credit')
            old=json.loads(row[2])
            require(c.execute('SELECT info FROM closed WHERE path=?',(name,)).fetchone()==(encode(old),),
                'Immutable retired history changed')
            c.execute('UPDATE retirements SET state=? WHERE path=?',('retired',name))
            c.execute('UPDATE settings SET closed_named=closed_named-?',(self._named(old),))
            self._audit(c,'retirement-complete',name);self._snapshot(c,False)

    def retire_archived_members(self,archive_id,members,guard=lambda:None):
        require(len(members)>0 and len(set(str(p) for p in members))==len(members),'Explicit unique members')
        with self._pin_archive(archive_id):
            for path in members:
                guard();self._retire_one_pinned(archive_id,path)
        return self.quiescent()

    def _reconcile_retirement_pinned(self,archive_id,path):
        """Storage-only recovery of an already absent exact intent, no science retry."""
        from sealed_cycle_archive_v3 import Archive
        name=self._path(path)
        with self._transaction() as c:
            outputs,manifest_sha,members=self._accepted_archive(c,archive_id)
            require(name in members,'Not a registered archived member')
            intent=c.execute('SELECT state,original_info FROM retirements WHERE path=? AND archive_id=?',
                (name,archive_id)).fetchone()
            require(intent is not None and intent[0]=='intent' and not os.path.lexists(self.root/name),
                'Only absent durable retirement intent may reconcile')
            manifest_name=next(p for p in outputs if Path(p).name=='manifest.json')
            root=(self.root/manifest_name).parent;old=json.loads(intent[1])
        self.charge_integrity(sum(v['logical'] for v in outputs.values())+old['logical']+16_000_000,
            'retirement-reconcile-read')
        archive=Archive(root,manifest_sha)
        member=(self.root/name).relative_to(Path(archive.manifest['source_root'])).as_posix()
        require(archive.files[member]['sha256']==old['raw_sha256'] and archive.verify(member)==old['logical'],
            'Intent archive raw identity differs')
        self._complete_retirement(archive_id,name)

    def reconcile_retirement(self,archive_id,path):
        with self._pin_archive(archive_id):
            self._reconcile_retirement_pinned(archive_id,path)


def open(config):
    return Guard(config)
