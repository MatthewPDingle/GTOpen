"""Prospective comparison IO with explicit closed-file reservation driver.

No builtins/open replacement, file/source mutation, native argument changes,
scientific budget changes or retries. A live snapshot admits known six-owner
bursts; strict quiescent accounting remains the existing NTFS reader's job.
"""
import atexit
import copy
import ctypes
from ctypes import wintypes
from contextlib import contextmanager
import functools
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import time
import uuid
import types

import psutil
import ntfs_expected_retention_v3 as ntfs
import preflop_expected_python_artifacts_v1 as artifacts

METHOD = 'scoped-expected-comparison-archived-io-v4'
CONFIG_FIELDS = {'format','method','execution_mode','store_root','store_identity',
    'allocated_core_bytes','logical_core_bytes','live_burst_bytes','metadata_slack_bytes',
    'diagnostic_reserve_bytes','diagnostic_tail_bytes','diagnostic_artifact_bytes','max_python_artifact_bytes',
    'max_owners','max_raw_integrity_read_bytes','source_identities','config_sha256','resource_driver'}
LIMITS = dict(allocated_core_bytes=16_000_000_000,logical_core_bytes=512_000_000_000,
    live_burst_bytes=6_000_000_000,metadata_slack_bytes=1_000_000_000,
    diagnostic_reserve_bytes=64_000_000,diagnostic_tail_bytes=16_000_000,diagnostic_artifact_bytes=1_000_000,
    max_python_artifact_bytes=64_000_000,max_owners=6,max_raw_integrity_read_bytes=16_000_000_000_000)
STAGE = Path(__file__).resolve().parent
_STATE = None
_MODULE_NAMES = ('preflop_expected_training_pipeline_v2','preflop_expected_river_workers_v2',
    'preflop_expected_board_workers_v2','preflop_expected_native_execution_v2',
    'sampled_visible_hybrid_checkpoint_v1','preflop_expected_policy_v1',
    'weighted_physical_reservoir_v1','preflop_expected_river_transport_archived_v4')


def sha(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def digest(value):
    return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def _modules(): return {n:importlib.import_module(n) for n in _MODULE_NAMES}


def _canonical(path):
    lexical=Path(os.path.abspath(path));resolved=lexical.resolve()
    if lexical!=resolved:raise ValueError('Canonical ordinary owning-store paths required')
    return resolved


def _ordinary_parents(path):
    for parent in (path,*path.parents):
        if parent.exists() and ntfs.attributes(parent)&ntfs.REPARSE:
            raise ValueError('Reparse-point owning-store paths refused')


def _root_identity(root):
    _ordinary_parents(root)
    if not root.is_dir():raise ValueError('Existing isolated owning store required')
    value=ntfs.file_identity(root)
    return dict(volume=value['volume'],index=value['index'])


def source_identities():
    modules=_modules();paths=[Path(__file__).resolve(),Path(artifacts.__file__).resolve(),Path(ntfs.__file__).resolve()]
    paths.extend(Path(m.__file__).resolve() for m in modules.values())
    compatibility=importlib.import_module('preflop_expected_compatibility_v1')
    paths.append(Path(compatibility.__file__).resolve())
    for name in ('sealed_cycle_archive_v2','sealed_cycle_archive_v3'):
        paths.append(Path(importlib.import_module(name).__file__).resolve())
    return {str(p):sha(p) for p in paths}


def config(store_root, *, resource_driver,execution_mode='study', **limits):
    if set(limits)-set(LIMITS):raise ValueError('Unknown operational resource limit')
    root=_canonical(store_root)
    result=dict(format=1,method=METHOD,execution_mode=execution_mode,store_root=str(root),
        store_identity=_root_identity(root),**dict(LIMITS,**limits),source_identities=source_identities(),
        resource_driver=copy.deepcopy(resource_driver))
    result['config_sha256']=digest(result)
    return require_config(result)


def require_config(value):
    if (not isinstance(value,dict) or set(value)!=CONFIG_FIELDS or type(value['format']) is not int
            or value['format']!=1 or value['method']!=METHOD or value['execution_mode'] not in ('study','software-control')):
        raise ValueError('Complete scoped resource configuration required')
    driver=value['resource_driver']
    if (not isinstance(driver,dict) or set(driver)!={'name','path','sha256'}
            or not isinstance(driver['name'],str) or not driver['name'].isidentifier()
            or Path(driver['path']).stem!=driver['name'] or sha(driver['path'])!=driver['sha256']):
        raise ValueError('Actual separately qualified immutable reservation driver required; no fallback')
    expected=dict(value);identity=expected.pop('config_sha256')
    if not isinstance(identity,str) or identity!=digest(expected):raise ValueError('Changed immutable resource configuration')
    root=_canonical(value['store_root'])
    if (str(root)!=value['store_root'] or value['store_identity']!=_root_identity(root)
            or any(type(value[k]) is not int or not 1<=value[k]<=v for k,v in LIMITS.items())):
        raise ValueError('Changed owning-store identity or invalid resource envelope')
    if value['max_python_artifact_bytes']!=64_000_000 or value['max_owners']!=6:
        raise ValueError('Fixed64MB Python artifacts and six-owner resource contract required')
    if value['execution_mode']=='study':
        if any(value[k]!=v for k,v in LIMITS.items()) or root.parent not in ntfs.ROOTS:
            raise ValueError('Exact registered study limits and research-store location required')
    elif root.parent!=Path(r'S:\GTOpen-research'):
        raise ValueError('Reservation-driver software controls require a fresh direct S store')
    if (not 256<=value['diagnostic_artifact_bytes']<=value['diagnostic_tail_bytes']
            <value['diagnostic_reserve_bytes']):
        raise ValueError('Separate protected diagnostic tail and bounded artifact required')
    expected_sources=source_identities()
    if value['source_identities']!=expected_sources:raise ValueError('Resource adapter or bound implementation source changed')
    return copy.deepcopy(value)


def _cfg(value=None):
    if value is not None:return require_config(value)
    if _STATE is None:raise RuntimeError('Scoped profile IO is not installed in this process')
    return _STATE['config']


def _inside(path, *, directory=False,io_config=None):
    cfg=_cfg(io_config);root=Path(cfg['store_root']);target=_canonical(path)
    if target==root and not directory or not target.is_relative_to(root):raise ValueError('Artifact is outside its owning store')
    _ordinary_parents(target.parent if not directory else target)
    return target


def _diagnostic(path,root):
    return (path.is_relative_to(root/'diagnostics') or path.name.endswith('-receipt.json')
        or path in (root/'failure.json',root/'released.json'))


def _transient(path,root):
    # These exact temporary names are created by the captured immutable-object
    # publisher or qualified checkpoint reservoir writer; other loss is refused.
    if re.fullmatch(r'\.partial-[0-9a-f]{32}',path.name):return 64_000_000
    if re.fullmatch(r'\.postflop-reservoir-[0-9a-f]{32}\.npz',path.name):return 64_000_000
    return None


def live_store_snapshot(io_config=None):
    cfg=_cfg(io_config);root=Path(cfg['store_root'])
    if _root_identity(root)!=cfg['store_identity']:raise ValueError('Owning-store directory replaced')
    pending=[root];logical=allocated=files=compressed=diag_logical=diag_allocated=0;missing=[];growing=0
    while pending:
        directory=pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                path=Path(entry.path)
                current_attributes=0
                try:
                    before=entry.stat(follow_symlinks=False)
                    if before.st_file_attributes&ntfs.REPARSE:raise ValueError('Reparse output refused')
                    if entry.is_dir(follow_symlinks=False):pending.append(path);continue
                    if not entry.is_file(follow_symlinks=False):raise ValueError('Nonordinary output refused')
                    info=ntfs.file_identity(path)
                    if info['links']!=1 or info['attributes']&ntfs.REPARSE:raise ValueError('Shared output identity refused')
                    physical=ntfs.allocated_bytes(path)
                    current_attributes=info['attributes']
                    size=max(before.st_size,info['logical_bytes'])
                    growing+=before.st_size!=info['logical_bytes']
                except FileNotFoundError:
                    allowance=_transient(path,root)
                    if allowance is None:raise ValueError('Unqualified output disappearance: '+str(path))
                    # Do not grant compression credit to a disappearing owned
                    # partial. Its immutable replacement can also be counted.
                    if _diagnostic(path,root):allowance=cfg['diagnostic_artifact_bytes']
                    size=physical=allowance;missing.append(dict(path=str(path),bytes=allowance))
                logical+=size;allocated+=physical;files+=1
                compressed+=bool(current_attributes&ntfs.COMPRESSED)
                if _diagnostic(path,root):diag_logical+=size;diag_allocated+=physical
    return dict(logical_bytes=logical,named_allocated_file_bytes=allocated,files=files,
        compressed_files=compressed,diagnostic_logical_bytes=diag_logical,
        diagnostic_named_allocated_bytes=diag_allocated,growing_samples=growing,
        disappearing_owned_transients=missing,transient_allowance_bytes=sum(p['bytes'] for p in missing),
        method='live-owned-growing-files-with-bounded-transient-allowance-v1',
        config_sha256=cfg['config_sha256'],burst_after_scan_bytes=cfg['live_burst_bytes'])


def _owners(cfg):
    directory=Path(cfg['store_root'])/'diagnostics';count=0
    for path in directory.glob('io-*-install.json'):
        release=path.with_name(path.name.replace('-install.json','-release.json'))
        if release.exists():continue
        value=json.loads(path.read_bytes())
        if value['config_sha256']!=cfg['config_sha256']:raise ValueError('Mixed owning-store configurations refused')
        try:process=psutil.Process(value['pid'])
        except psutil.NoSuchProcess:continue
        if abs(process.create_time()-value['creation_time'])<.002:count+=1
    return count


def _driver(cfg):
    if _STATE is not None and _STATE['config']==cfg:return _STATE['driver']
    module=importlib.import_module(cfg['resource_driver']['name'])
    if Path(module.__file__).resolve()!=Path(cfg['resource_driver']['path']).resolve() or sha(module.__file__)!=cfg['resource_driver']['sha256']:
        raise ValueError('Loaded reservation driver source differs from registered pin')
    return module.open(cfg)


def _admit(critical,io_config=None):
    cfg=_cfg(io_config)
    # The new driver must use persistent closed totals and active reservations.
    # It is NOT optional: no every-poll full-walk fallback or cache-ratio credit.
    return _driver(cfg).admit(critical)


def quiescent(io_config=None,*,compression_receipts=()):
    cfg=_cfg(io_config);return _driver(cfg).quiescent(compression_receipts=compression_receipts)


def archive_context(context_root,archive_root,*,max_pack_bytes,activity_guard,io_config=None,
                    include_board_captures=False):
    """Storage-only post-join callback; keep JSON/NPZ and board diagnostics loose.

    Original native receipts and references are unchanged. Only native .bin
    captures in this completed context are eligible. The driver records their
    historical identities and verifies the archive before removing raw files.
    """
    if type(include_board_captures) is not bool:raise ValueError('Explicit board-retention phase')
    cfg=_cfg(io_config);driver=_driver(cfg)
    context=_inside(context_root,directory=True,io_config=cfg)
    output=_inside(archive_root,directory=True,io_config=cfg)
    if output.is_relative_to(context) or context.is_relative_to(output):
        raise ValueError('Context/archive namespaces must be disjoint')
    with driver._transaction() as c:
        rows=list(c.execute('SELECT closed.path,closed.kind FROM closed LEFT JOIN retirements '
                            'ON closed.path=retirements.path WHERE retirements.path IS NULL'))
    members=[]
    root=Path(cfg['store_root'])
    for name,kind in rows:
        path=root/name
        if (kind=='native-aggregate' and path.is_relative_to(context)
                and path.suffix=='.bin'
                and (include_board_captures or not path.is_relative_to(context/'board-targets'))):
            members.append(path)
    if not members:raise ValueError('Completed context has no closed eligible captures')
    activity_guard()
    receipt=driver.archive_members(context,output,sorted(members),max_pack_bytes=max_pack_bytes,
        guard=activity_guard,workers=8)
    after=driver.retire_archived_members(receipt['archive_id'],members,guard=activity_guard)
    return dict(method='post-joined-context-native-capture-archive-v1',archive=receipt,after=after,
        original_native_receipts_unchanged=True,original_native_verification_preserved=True,
        excluded_loose_formats=['JSON','NPZ'],board_diagnostics_remain_loose=not include_board_captures,
        board_captures_allowed_after_diagnostics=include_board_captures,
        source_draws_or_fits_added=False,full_study_admitted=False)


def _reserve(paths,max_bytes,kind,*,protected=False,io_config=None):
    cfg=_cfg(io_config)
    return _driver(cfg).reserve([str(_inside(p,io_config=cfg)) for p in paths],max_bytes,kind,protected=protected)


def _seal(token,paths,*,io_config=None):
    cfg=_cfg(io_config)
    return _driver(cfg).seal(token,[str(_inside(p,io_config=cfg)) for p in paths])


def guard():return _admit(False)
def diagnostic_guard(io_config=None):return _admit(True,io_config)


@contextmanager
def _diagnostic_mutex(cfg):
    # Serialize exact named diagnostic pre-admission and atomic publication
    # across six owners. A kernel mutex adds no unaccounted filesystem output.
    dll=ctypes.WinDLL('kernel32',use_last_error=True)
    dll.CreateMutexW.argtypes=[wintypes.LPVOID,wintypes.BOOL,wintypes.LPCWSTR]
    dll.CreateMutexW.restype=wintypes.HANDLE
    dll.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
    dll.WaitForSingleObject.restype=wintypes.DWORD
    dll.ReleaseMutex.argtypes=[wintypes.HANDLE];dll.ReleaseMutex.restype=wintypes.BOOL
    dll.CloseHandle.argtypes=[wintypes.HANDLE];dll.CloseHandle.restype=wintypes.BOOL
    name='Local\\GTOpenExpectedIO-'+digest(dict(root=cfg['store_root'],identity=cfg['store_identity']))
    handle=dll.CreateMutexW(None,False,name)
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    held=False
    try:
        result=dll.WaitForSingleObject(handle,30_000)
        if result not in (0,0x80):raise TimeoutError('Owned diagnostic admission mutex unavailable')
        held=True;yield
    finally:
        if held and not dll.ReleaseMutex(handle):raise ctypes.WinError(ctypes.get_last_error())
        if not dll.CloseHandle(handle):raise ctypes.WinError(ctypes.get_last_error())


def save_diagnostic(path, document, *, io_config=None,protected=False):
    cfg=_cfg(io_config);path=_inside(path,io_config=cfg);root=Path(cfg['store_root'])
    if type(protected) is not bool:raise ValueError('Explicit protected diagnostic classification required')
    if not _diagnostic(path,root):raise ValueError('Explicit diagnostic destination required')
    terminal=path in (root/'failure.json',root/'released.json')
    release=(path.parent==root/'diagnostics' and bool(re.fullmatch(r'io-[0-9]+-[0-9]+-release\.json',path.name)))
    failed_receipt=(path.name.endswith('-receipt.json') and isinstance(document,dict)
        and document.get('format')==2 and document.get('method')=='native-process-bound-export-v2'
        and document.get('outcome')=='failed')
    if terminal and not protected or protected and not (terminal or release or failed_receipt):
        raise ValueError('Only fixed failure/release/native-failure records use the protected diagnostic tail')
    raw=artifacts.json_bytes(document,sort_keys=True,max_bytes=cfg['diagnostic_artifact_bytes'])
    with _diagnostic_mutex(cfg):
        before=_admit(True,cfg)
        ceiling=cfg['diagnostic_reserve_bytes']-(0 if protected else cfg['diagnostic_tail_bytes'])
        if before['diagnostic_logical_bytes']+len(raw)>ceiling:
            raise RuntimeError('Protected diagnostic tail or aggregate allowance exhausted')
        if os.path.lexists(path):raise FileExistsError('Diagnostic destination must be new: '+str(path))
        temporary=path.parent/('.partial-'+uuid.uuid4().hex)
        token=_reserve([temporary,path],len(raw),'diagnostic-rename',protected=protected,io_config=cfg)
        # No polling/core/cancellation gate here: one failure + release per
        # owner and two coordinator terminal records fit the protected16MB.
        artifacts.write_bytes(temporary,raw,guard=lambda:_admit(True,cfg),max_bytes=cfg['diagnostic_artifact_bytes'])
        os.rename(temporary,path)
        _seal(token,[path],io_config=cfg)
        _admit(True,cfg)


def _save(path, document):
    raw=artifacts.json_bytes(document,max_bytes=64_000_000)
    return write_bytes(path,raw)


def write_bytes(path,raw):
    path=_inside(path)
    if type(raw) is not bytes or len(raw)>64_000_000:raise ValueError('Bounded exact Python artifact bytes required')
    token=_reserve([path],len(raw),'python-bytes')
    artifacts.write_bytes(path,raw,guard=guard)
    return _seal(token,[path])


def save_npz(path,**arrays):
    path=_inside(path)
    # The qualified helper already buffers at most64MB before any file open.
    # Reserve the exact finished serialized buffer, never a compression ratio.
    raw=artifacts.npz_bytes(**arrays)
    return write_bytes(path,raw)


def _receipt(path, document):save_diagnostic(path,document,protected=document.get('outcome')!='success')


def _publish(directory, kind, content, suffix='json'):
    directory=_inside(directory,directory=True)
    if not isinstance(kind,str) or not re.fullmatch('[a-z]+',kind) or suffix not in ('json','npz'):
        raise ValueError('Owned immutable-object kind and suffix required')
    if not isinstance(content,bytes):raise TypeError('Immutable publication bytes required')
    if len(content)>64_000_000:raise artifacts.ArtifactLimitError('Immutable Python artifact exceeds64MB')
    guard();result=_STATE['original_publish'](directory,kind,content,suffix);guard();return result


def _reservoir_save(reservoir,path):
    path=_inside(path);token=_reserve([path],64_000_000,'weighted-reservoir')
    artifacts.save_weighted_reservoir(reservoir,path,guard=guard)
    return _seal(token,[path])


def _run_native(*args,**kwargs):
    _inside(kwargs['folder'],directory=True)
    original_guard=kwargs['guard']
    if not callable(original_guard):raise TypeError('Explicit native caller guard required')
    def combined():
        original_guard();guard()
    kwargs=dict(kwargs,guard=combined)
    folder=Path(kwargs['folder']);label=kwargs['label']
    paths=[folder/(label+'-stdout.bin'),folder/(label+'-stderr.bin'),
        *[Path(row['path']) for row in kwargs.get('direct_outputs',())]]
    token=_reserve(paths,kwargs['max_output_bytes'],'native-aggregate')
    guard()
    try:result=_STATE['original_run_native'](*args,**kwargs)
    except BaseException as failure:
        # The captured native writer already retained its failed receipt. Do
        # not replace cancellation/core-limit errors with another normal gate.
        try:diagnostic_guard()
        except BaseException as accounting:failure.add_note('Terminal store accounting: '+str(accounting))
        raise
    _seal(token,paths);guard();return result


def initialize_board(*args,io_config,**kwargs):
    install(io_config)
    return _STATE['original_board_initialize'](*args,**kwargs)


def initialize_river(*args,io_config,**kwargs):
    install(io_config)
    return _STATE['original_river_initialize'](*args,**kwargs)


def _binding_label(value):
    if isinstance(value,types.ModuleType):return dict(module=value.__name__,path=str(Path(value.__file__).resolve()),sha256=sha(value.__file__))
    if isinstance(value,functools.partial):return dict(callable=_binding_label(value.func),config_sha256=value.keywords['io_config']['config_sha256'])
    return value.__module__+'.'+value.__qualname__


def install(io_config):
    global _STATE
    cfg=require_config(io_config)
    if _STATE is not None:
        if cfg!=_STATE['config']:raise ValueError('Cannot replace installed immutable resource configuration')
        for owner,name,old,new in _STATE['bindings']:
            if getattr(owner,name) is not new:raise ValueError('Installed named IO binding changed')
        return copy.deepcopy(_STATE['witness_ref'])
    modules=_modules();pipeline,river,board,native,storage,policy,reservoir,transport=[modules[n] for n in _MODULE_NAMES]
    originals=[]
    def bind(owner,name,new):
        old=getattr(owner,name);originals.append((owner,name,old,new));setattr(owner,name,new)
    driver=_driver(cfg)
    _STATE=dict(config=cfg,bindings=originals,original_publish=storage.publish,driver=driver,
        original_run_native=native.run_native,original_board_initialize=board.initialize,
        original_river_initialize=river.initialize,witness_ref=None)
    try:
        compatibility=importlib.import_module('preflop_expected_compatibility_v1')
        for owner in (pipeline,river):bind(owner,'InitialTargets',compatibility.CanonicalInitialTargets)
        for owner,name in ((pipeline,'save'),(river,'save'),(board,'_save')):bind(owner,name,_save)
        bind(native,'_write',_receipt)
        # Object aliases remain original until explicit checkpoint CAS bindings
        # enter. The old captured raw _publish wrapper is incompatible with CAS.
        bind(reservoir.WeightedPhysicalReservoir,'save',_reservoir_save)
        for owner in (native,pipeline,river,transport):bind(owner,'run_native',_run_native)
        bind(river,'transport',transport)
        bind(board,'initialize',functools.partial(initialize_board,io_config=copy.deepcopy(cfg)))
        bind(river,'initialize',functools.partial(initialize_river,io_config=copy.deepcopy(cfg)))
        directory=Path(cfg['store_root'])/'diagnostics';directory.mkdir(exist_ok=True)
        pid=os.getpid();created=psutil.Process().create_time();name=f'io-{pid}-{time.time_ns()}'
        path=directory/(name+'-install.json');release=directory/(name+'-release.json')
        witness=dict(format=1,method=METHOD,config_sha256=cfg['config_sha256'],source_identities=cfg['source_identities'],
            pid=pid,creation_time=created,installed_unix=time.time(),
            bindings=[dict(owner=(o.__module__+'.'+o.__qualname__ if isinstance(o,type) else o.__name__),attribute=n,
                original=_binding_label(old),replacement=_binding_label(new)) for o,n,old,new in originals])
        save_diagnostic(path,witness)
        _STATE.update(release_path=release,witness_ref=dict(path=str(path),sha256=sha(path),witness=witness))
        from multiprocessing.util import Finalize
        _STATE['finalizer']=Finalize(None,_exit_restore,exitpriority=10)
        guard();return copy.deepcopy(_STATE['witness_ref'])
    except BaseException:
        for owner,name,old,new in reversed(originals):
            if getattr(owner,name) is new:setattr(owner,name,old)
        _STATE=None;raise


def uninstall():
    global _STATE
    if _STATE is None:return None
    state=_STATE
    if any(getattr(o,n) is not new for o,n,old,new in state['bindings']):
        raise ValueError('Cannot restore externally changed named IO binding')
    path=state['release_path']
    try:
        save_diagnostic(path,dict(format=1,method=METHOD,config_sha256=state['config']['config_sha256'],
            installation=state['witness_ref']['path'],pid=os.getpid(),creation_time=psutil.Process().create_time(),
            released_unix=time.time(),restored_named_bindings=True),protected=True)
    finally:
        for owner,name,old,new in reversed(state['bindings']):setattr(owner,name,old)
        if 'finalizer' in state:state['finalizer'].cancel()
        try:state['driver'].close()
        finally:_STATE=None
    return dict(path=str(path),sha256=sha(path))


def _exit_restore():
    if _STATE is not None:
        try:uninstall()
        except BaseException:pass  # Existing witnesses/raw evidence remain; no retry or deletion.


atexit.register(_exit_restore)
