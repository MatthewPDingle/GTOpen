"""Read-only independent reconstruction of the retained NTFS controls.

Queries Win32 file handles, attributes and named allocation directly, hashes
ordinary logical reads of both copies and the original, and replays synthetic
fixture bytes only. Never creates/compresses/links/deletes a research file,
launches a process, imports a poker runner, fits, or changes control evidence.
This qualifies retention for the existing candidate; it is no poker accuracy
claim, volume quota, or guarantee for a larger/deeper research run.
"""
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import random
import sys
import time
import traceback

OUT = Path(__file__).resolve().parent
STAGE = OUT.parent
sys.path.insert(0, str(STAGE))
sys.dont_write_bytecode = True
import ntfs_expected_retention_v1 as old_api
import ntfs_expected_retention_v2 as new_api
import preflop_expected_native_execution_v1 as execution

PROFILE = Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')
STORES = [Path(fr'S:\GTOpen-research\ntfs-expected-profile-control-v{i}') for i in (1, 2)]
MANIFEST = STAGE/'preflop-expected-native-cycle-independent-readback-v2/retained-files.json'
LOCAL_RESULT = STAGE/'preflop-expected-ntfs-retention-control-v2-result.json'
SOURCE_PINS = {
    'ntfs_expected_retention_v1.py': 'ca09c0713ccecfa4181aac7f33f5c8e7f3acbdfc66fabbdedd8a1a136fa632f5',
    'ntfs_expected_retention_v2.py': '95dbba0d6e29bf8b71702ac87e79302975a9eb641ed82131ca5b5888e6e10f15',
    'preflop_expected_ntfs_retention_check_v1.py': 'bf4d01caceb5cf5dca5d852eb5c65e54cc1b2ad724e7fe3a432364bd60de99e0',
    'preflop_expected_ntfs_retention_check_v2.py': '13977c7caed26e3e135e1011f9dc407a9db628e7ef846e53098dadfe49e78bbe',
    'preflop_expected_native_execution_v1.py': '332a3244ed1e1241978d9348c60b9361e49c16d4ee0286a5af02a32c6ee9056e',
}
EXTERNAL_PINS = {
    str(MANIFEST): 'd1fb931157542df733cdcb7b67bdb4002073266bcfa505a1e4f2d8ff75817b27',
    str(PROFILE/'registration.json'): '22cb43489f0c9be4c4625639cf778ff7ac1b444765e22e376f025a6e21ac9e4a',
    str(PROFILE/'result.json'): '7341ac78404cb69dc8f32e42fd0be74cee77564541479cd85bb44acabcd7ff30',
    str(STORES[0]/'attempt.json'): '89393f65b64cea4679c024d7bf7abceebf99f352112567f36467c0f81e50c294',
    str(STORES[0]/'failure.json'): '874ad876e68987b55bd6546a30cb9ba62b40261126689c8598f7db8edc958bea',
    str(STORES[1]/'attempt.json'): '11683ba312267520c939cc8de9082e6d42f7a328c1bcc6d31a6c1d2827e9419f',
    str(STORES[1]/'result.json'): '76332542bb08b521b51f2b36f1429ef6e7d93c929ac7632915152727c98d8b0a',
    str(LOCAL_RESULT): '76332542bb08b521b51f2b36f1429ef6e7d93c929ac7632915152727c98d8b0a',
}
PINS = {**{str(STAGE/name):value for name,value in SOURCE_PINS.items()}, **EXTERNAL_PINS}
COMPRESSED, REPARSE, DIRECTORY = 0x800, 0x400, 0x10
READS, CHECKS = {}, []
SCOPE = ('Read-only retained-candidate NTFS retention qualification. No new '
    'poker/native process, fitting, production change, control mutation, '
    'historical compression/linking/deletion or Git operation. No poker '
    'accuracy claim or guaranteed larger-run storage bound.')


def require(test, message):
    if not test:
        raise ValueError(message)


def sha(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path, identity=None):
    path = Path(path)
    value = sha(path)
    if identity is not None:
        require(value == identity, 'Changed pinned bytes: '+str(path))
    READS[str(path)] = value
    return json.loads(path.read_bytes())


def save(name, value):
    with (OUT/name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def note(stage, **details):
    value = dict(stage=stage, seconds=time.monotonic()-BEGAN, **details)
    CHECKS.append(value)
    print(json.dumps(value, sort_keys=True), flush=True)


class ByHandle(ctypes.Structure):
    _fields_ = [('attributes', wintypes.DWORD), ('creation', wintypes.FILETIME),
        ('access', wintypes.FILETIME), ('write', wintypes.FILETIME),
        ('volume', wintypes.DWORD), ('size_high', wintypes.DWORD),
        ('size_low', wintypes.DWORD), ('links', wintypes.DWORD),
        ('index_high', wintypes.DWORD), ('index_low', wintypes.DWORD)]


def setup_win32():
    require(os.name == 'nt', 'Actual Win32 readback required')
    dll = ctypes.WinDLL('kernel32', use_last_error=True)
    dll.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    dll.CreateFileW.restype = wintypes.HANDLE
    dll.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(ByHandle)]
    dll.GetFileInformationByHandle.restype = wintypes.BOOL
    dll.CloseHandle.argtypes = [wintypes.HANDLE]
    dll.CloseHandle.restype = wintypes.BOOL
    dll.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
    dll.GetFileAttributesW.restype = wintypes.DWORD
    dll.GetCompressedFileSizeW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
    dll.GetCompressedFileSizeW.restype = wintypes.DWORD
    dll.GetVolumeInformationW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR,
        wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD]
    dll.GetVolumeInformationW.restype = wintypes.BOOL
    return dll


def long(path):
    return '\\\\?\\'+str(Path(path).absolute())


def win32_file(path):
    path = Path(path)
    handle = DLL.CreateFileW(long(path), 0, 7, None, 3, 0x02000000, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        info = ByHandle()
        if not DLL.GetFileInformationByHandle(handle, ctypes.byref(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        attrs = DLL.GetFileAttributesW(long(path))
        if attrs == 0xffffffff:
            raise ctypes.WinError(ctypes.get_last_error())
        require(attrs == info.attributes, 'Handle/path attributes differ: '+str(path))
        result = dict(volume=info.volume, index=(info.index_high<<32)|info.index_low,
            links=info.links, attributes=info.attributes,
            logical_bytes=(info.size_high<<32)|info.size_low)
        if not attrs & DIRECTORY:
            high = wintypes.DWORD()
            ctypes.set_last_error(0)
            low = DLL.GetCompressedFileSizeW(long(path), ctypes.byref(high))
            if low == 0xffffffff and ctypes.get_last_error():
                raise ctypes.WinError(ctypes.get_last_error())
            result['named_allocated_file_bytes'] = (high.value<<32)|low
        return result
    finally:
        if not DLL.CloseHandle(handle):
            raise ctypes.WinError(ctypes.get_last_error())


def volume():
    label, fs = ctypes.create_unicode_buffer(261), ctypes.create_unicode_buffer(261)
    serial, component, flags = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
    if not DLL.GetVolumeInformationW('S:\\', label, 261, ctypes.byref(serial),
            ctypes.byref(component), ctypes.byref(flags), fs, 261):
        raise ctypes.WinError(ctypes.get_last_error())
    require(fs.value == 'NTFS', 'Control volume is not NTFS')
    return dict(volume_label=label.value, filesystem=fs.value, serial=serial.value,
        flags=flags.value, maximum_component_length=component.value)


def tree(root):
    files, directories, pending = {}, {}, [Path(root)]
    while pending:
        current = pending.pop()
        info = win32_file(current)
        require(info['attributes'] & DIRECTORY and not info['attributes'] & REPARSE,
            'A tree directory is a reparse point: '+str(current))
        directories[str(current.relative_to(root))] = info
        with os.scandir(current) as entries:
            for entry in entries:
                info = win32_file(entry.path)
                require(not info['attributes'] & REPARSE, 'Reparse point in retained tree')
                if info['attributes'] & DIRECTORY:
                    pending.append(Path(entry.path))
                else:
                    files[str(Path(entry.path).relative_to(root))] = info
    return files, directories


def inspect_profile_tree(root, manifest, *, compressed):
    files, directories = tree(root)
    require(set(files) == set(manifest), 'Copied/original exact file set differs: '+str(root))
    expected_directories = {'.'}
    for name in manifest:
        path = Path(name)
        require(not path.is_absolute() and '..' not in path.parts, 'Unsafe retained relative path')
        expected_directories.update(str(parent) for parent in path.parents)
    require(set(directories) == expected_directories, 'Extra or missing retained tree directory')
    if compressed:
        require(all(info['attributes'] & COMPRESSED for info in directories.values()),
            'Nested compression inheritance missing')
    identities = set()
    evidence = {}
    for name, entry in manifest.items():
        path = root/name
        info = files[name]
        require(info['links'] == 1, 'Hardlinked profile artifact receives storage credit')
        identity = (info['volume'], info['index'])
        require(identity not in identities, 'Profile tree repeats a physical file identity')
        identities.add(identity)
        before = path.stat()
        require(info['logical_bytes'] == before.st_size == entry['bytes'], 'Logical size changed: '+str(path))
        require(sha(path) == entry['sha256'], 'Ordinary logical-read hash changed: '+str(path))
        after = path.stat()
        require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
            and win32_file(path) == info, 'Artifact changed during retained readback')
        if compressed:
            require(info['attributes'] & COMPRESSED, 'Copied file is not transparently compressed')
        evidence[name] = dict(info, sha256=entry['sha256'])
    return dict(files=len(files), directories=len(directories),
        logical_bytes=sum(info['logical_bytes'] for info in files.values()),
        named_allocated_file_bytes=sum(info['named_allocated_file_bytes'] for info in files.values()),
        compressed_files=sum(bool(info['attributes'] & COMPRESSED) for info in files.values())), evidence


def inspect_fixture(store, attempt, result=None):
    root = store/'fixture/nested'
    files, directories = tree(root)
    require(set(files) == {'writer.py', 'direct-output.bin', 'python-writer-stdout.bin',
        'python-writer-stderr.bin', 'python-writer-receipt.json', 'renamed.bin', 'hardlink.bin'},
        'Synthetic retained fixture file set changed')
    require(set(directories) == {'.'} and all(v['attributes'] & COMPRESSED for v in files.values()),
        'Synthetic output inheritance changed')
    raw = b'abcdef0123456789'*524288
    require((root/'direct-output.bin').read_bytes() == raw
        and (root/'python-writer-stdout.bin').read_bytes() == raw
        and (root/'python-writer-stderr.bin').read_bytes() == b'',
        'Ordinary synthetic direct/stdout bytes differ from exact recipe')
    expected = bytearray(random.Random(3181).randbytes(2_000_000))
    patchbytes = b'qualified-random-access'
    expected[77777:77777+len(patchbytes)] = patchbytes
    expected.extend(b'append-tail')
    require((root/'renamed.bin').read_bytes() == expected
        and (root/'hardlink.bin').read_bytes() == expected,
        'Reopened/seeked/appended/renamed fixture bytes differ')
    one, two = files['renamed.bin'], files['hardlink.bin']
    require(one == two and one['links'] == 2 and one['logical_bytes'] == 2_000_011,
        'Preserved synthetic hardlink lacks exact two-link handle identity')
    direntry_links = {e.name:e.stat(follow_symlinks=False).st_nlink for e in os.scandir(root)
        if e.name in ('renamed.bin', 'hardlink.bin')}
    path_links = {name:(root/name).stat().st_nlink for name in direntry_links}
    require(all(v == 0 for v in direntry_links.values()) and all(v == 2 for v in path_links.values()),
        'Exact v1 DirEntry-versus-Path link-count diagnosis changed')
    wanted_identity = {k:v for k,v in one.items() if k != 'named_allocated_file_bytes'}
    require(new_api.file_identity(root/'renamed.bin') == wanted_identity,
        'v2 helper handle identity differs from independent Win32 query')
    try:
        new_api.measure_tree(root, lambda:None)
    except ValueError as exc:
        rejection = str(exc)
        require('Hardlinked' in rejection, 'Unexpected v2 hardlink refusal')
    else:
        raise ValueError('v2 admits the actual preserved hardlink fixture')
    legacy = old_api.measure_tree(root, lambda:None)
    require(legacy['files'] == 7, 'v1 false acceptance was not independently reproduced')
    receipt_path = root/'python-writer-receipt.json'
    receipt = read(receipt_path)
    invocation = dict(receipt_path=str(receipt_path), receipt_sha256=sha(receipt_path), receipt=receipt,
        stdout_path=receipt['stdout']['path'], stdout_sha256=receipt['stdout']['sha256'],
        stderr_path=receipt['stderr']['path'], stderr_sha256=receipt['stderr']['sha256'])
    python = Path(r'C:\Program Files\Python312\python.exe')
    require(receipt['expected_identities'] == {str(python):'5aba6ec903f2e0e946459f98dc45c8129d3f22187f5adac00713d733191d3a3f',
        str(root/'writer.py'):'f52bb8720671bce40d7540128f1846ac008d4fc0127af383f4af860f6ce3bde8'},
        'Original Python writer/executable identity differs')
    execution.verify_native(invocation, executable=str(python),
        arguments=['-B', str(root/'writer.py'), str(root/'direct-output.bin')],
        expected_identities=receipt['expected_identities'])
    require(attempt['started_unix'] <= receipt['started_unix'] <= receipt['terminal_unix']
        <= attempt['started_unix']+attempt['maximum_seconds'], 'Fixture escaped the owning bounded control')
    if result is not None:
        require(result['native_fixture'] == invocation and result['hardlink_identity'] == wanted_identity
            and result['python_stat_nlink'] == 2, 'Stored v2 fixture/process identity changed')
    return dict(files=files, actual_direntry_stat_nlink=direntry_links, actual_path_stat_nlink=path_links,
        v1_false_acceptance_reproduced=True, v2_handle_refusal=rejection,
        exact_direct_stdout_and_random_access_bytes=True, owned_python_receipt=invocation)


def forbidden(*args, **kwargs):
    raise AssertionError('Retention audit cannot create/compress/link/delete a store or launch a process')


def audit():
    for path, identity in PINS.items():
        require(sha(path) == identity, 'Source/attempt/failure fingerprint changed: '+path)
        READS[path] = identity
    manifest = read(MANIFEST, EXTERNAL_PINS[str(MANIFEST)])
    require(len(manifest) == 809 and sum(v['bytes'] for v in manifest.values()) == 1_278_992_546,
        'Original exact profile manifest changed')
    attempts = [read(s/'attempt.json', EXTERNAL_PINS[str(s/'attempt.json')]) for s in STORES]
    failure = read(STORES[0]/'failure.json', EXTERNAL_PINS[str(STORES[0]/'failure.json')])
    require(failure['type'] == 'AssertionError' and failure['message'] == 'Hardlinked accounting accepted'
        and 'preflop_expected_ntfs_retention_check_v1.py' in failure['traceback'], 'Original v1 failure changed')
    require(not (STORES[0]/'result.json').exists() and not (STORES[0]/'copied-manifest.json').exists(),
        'Failed v1 control was converted to a pass')
    result = read(STORES[1]/'result.json', EXTERNAL_PINS[str(STORES[1]/'result.json')])
    require(read(LOCAL_RESULT, EXTERNAL_PINS[str(LOCAL_RESULT)]) == result and not (STORES[1]/'failure.json').exists(),
        'Complete v2 pass mirrors/terminal state differ')
    common = {str(MANIFEST):EXTERNAL_PINS[str(MANIFEST)],
        str(PROFILE/'registration.json'):EXTERNAL_PINS[str(PROFILE/'registration.json')],
        str(PROFILE/'result.json'):EXTERNAL_PINS[str(PROFILE/'result.json')],
        str(STAGE/'preflop_expected_native_execution_v1.py'):SOURCE_PINS['preflop_expected_native_execution_v1.py']}
    for version, attempt in enumerate(attempts, 1):
        expected_pins = dict(common, **{str(STAGE/name):SOURCE_PINS[name] for name in
            (f'ntfs_expected_retention_v{version}.py', f'preflop_expected_ntfs_retention_check_v{version}.py')})
        if version == 2:
            expected_pins.update({str(STAGE/name):SOURCE_PINS[name] for name in
                ('ntfs_expected_retention_v1.py', 'preflop_expected_ntfs_retention_check_v1.py')})
            expected_pins[str(STORES[0]/'failure.json')] = EXTERNAL_PINS[str(STORES[0]/'failure.json')]
        require(set(attempt) == {'copy_workers','files','inputs','maximum_seconds','scope','source','started_unix'}
            and attempt['inputs'] == expected_pins and attempt['copy_workers'] == 8 and attempt['files'] == 809
            and attempt['maximum_seconds'] == 600 and attempt['source'] == str(PROFILE),
            'Prospective attempt source/input/copy scope differs')
    require(attempts[0]['started_unix'] < attempts[1]['started_unix']
        and result['inputs'] == attempts[1]['inputs'] and result['passed'] is True
        and result['scientific_accuracy_qualified'] is False and result['production_modified'] is False
        and result['store'] == str(STORES[1]) and result['files'] == 809 and result['seconds'] == 6.75
        and result['seconds'] <= attempts[1]['maximum_seconds'], 'Retention terminal scope/timing changed')
    note('source-attempt-failure-and-pass-pins-verified',pins=len(PINS),v1_failure=failure['message'])
    original, original_files = inspect_profile_tree(PROFILE, manifest, compressed=False)
    copies, copied_files = [], []
    for store in STORES:
        require(win32_file(store)['attributes'] & COMPRESSED, 'New control store compression flag missing')
        summary, files = inspect_profile_tree(store/'profile-copy', manifest, compressed=True)
        copies.append(summary);copied_files.append(files)
        note('complete-ordinary-byte-copy-readback',store=str(store),**summary)
    copied_manifest = read(STORES[1]/'copied-manifest.json', result['copied_manifest_sha256'])
    require(len(copied_manifest) == 809 and [row['path'] for row in copied_manifest] == list(manifest),
        'Copied manifest ordering/file set changed')
    for row in copied_manifest:
        name = row['path'];old,new = original_files[name],copied_files[1][name]
        require(set(row) == {'path','bytes','sha256','original_unchanged','original_compressed',
            'original_named_allocated_bytes','copied_named_allocated_bytes','seconds'}
            and row['bytes'] == manifest[name]['bytes'] and row['sha256'] == manifest[name]['sha256']
            and row['original_unchanged'] is True
            and row['original_compressed'] == bool(old['attributes'] & COMPRESSED)
            and row['original_named_allocated_bytes'] == old['named_allocated_file_bytes']
            and row['copied_named_allocated_bytes'] == new['named_allocated_file_bytes'],
            'Copied per-file manifest disagrees with exact independent readback')
    measured = new_api.measure_tree(STORES[1]/'profile-copy', lambda:None)
    require(measured == result['copied_storage']
        and {k:measured[k] for k in copies[1] if k != 'directories'}
            == {k:v for k,v in copies[1].items() if k != 'directories'},
        'Stored/helper/independent named allocation differs')
    require(original['compressed_files'] == result['original_compressed_files'] == 0
        and original['named_allocated_file_bytes'] == result['original_named_allocated_bytes'] == 1_278_992_546
        and copies[1]['named_allocated_file_bytes'] == 311_489_940
        and result['compressed_over_original'] == 311_489_940/1_278_992_546,
        'Original/compressed candidate-specific allocation differs')
    require(result['refused'] == ['existing','root','outside','nested-existing-parent','reparse-point','hardlink-accounting'],
        'Stored refusal scope changed')
    require(all(result[k] is True for k in ('logical_hashes_exact','all_originals_unchanged','nested_inheritance',
        'actual_python_stdout_and_direct_output','seek_append_rename_exact')), 'Stored transparent-I/O qualification differs')
    fixtures = [inspect_fixture(s,a,result if i == 1 else None) for i,(s,a) in enumerate(zip(STORES,attempts))]
    note('win32-allocation-inheritance-hardlink-and-python-fixtures-verified',
        copied_allocated_bytes=copies[1]['named_allocated_file_bytes'],
        actual_direntry_nlink=fixtures[1]['actual_direntry_stat_nlink'],
        actual_path_nlink=fixtures[1]['actual_path_stat_nlink'])
    full_trees = []
    for i,store in enumerate(STORES):
        files, _ = tree(store)
        top = {str(p.relative_to(store)) for p in store.iterdir() if p.is_file()}
        require(top == ({'attempt.json','failure.json'} if i == 0
            else {'attempt.json','copied-manifest.json','result.json'}), 'Retained control top-level file set changed')
        require(set(files) == {str(Path('profile-copy')/name) for name in manifest}
            | {str(Path('fixture/nested')/name) for name in fixtures[i]['files']} | top,
            'Extra or missing retained control file')
        full_trees.append(dict(store=str(store),files={name:dict(info,sha256=sha(store/name))
            for name,info in files.items()}))
    for path,identity in PINS.items():
        require(sha(path) == identity, 'Input/source/control changed during independent audit')
    for module in (old_api,new_api):
        require(sha(module.__file__) == SOURCE_PINS[Path(module.__file__).name], 'Imported retention source changed')
    save('file-evidence.json',dict(original=original_files,copies=copied_files,
        complete_control_stores=full_trees))
    return dict(passed=True,scope=SCOPE,source_pins=SOURCE_PINS,input_pins=PINS,
        filesystem=volume(),original=original,copies=copies,fixtures=fixtures,
        original_v1_failure_preserved=True,v1_copied_files_all_byte_identical=True,
        v1_cause='Python 3.12 os.DirEntry.stat(follow_symlinks=False).st_nlink is 0 for actual two-link files; Path.stat() and Win32 handles report 2.',
        source_comment_qualification="The unchanged v2 comment says stat.nlink can report 1. That is not the observed fixture: the exact v1 DirEntry call reports 0, while Path.stat() reports 2. The v2 implementation actually queries GetFileInformationByHandle and correctly refuses links!=1.",
        v2_actual_win32_hardlink_refusal=True,copied_manifest_sha256=result['copied_manifest_sha256'],
        logical_hashes_exact=True,original_sources_and_controls_unchanged=True,
        retained_profile_logical_bytes=1_278_992_546,v2_named_allocated_file_bytes=311_489_940,
        saved_named_allocated_file_bytes=967_502_606,candidate_compressed_over_original=result['compressed_over_original'],
        allocation_is_sum_of_named_files_not_total_volume_occupancy=True,
        scientific_accuracy_qualified=False,larger_run_storage_guaranteed=False,
        historical_compression_linking_deletion=False,processes_launched=0,
        file_evidence_sha256=sha(OUT/'file-evidence.json'),audit_source_sha256=sha(__file__),
        reads=READS,checks=CHECKS,seconds=time.monotonic()-BEGAN,
        limitations=['Directory metadata, transient allocations, caches and filesystem overhead require a separate volume reserve.',
            'Compression ratio is measured on this retained candidate, not promised for deeper/larger outputs.',
            'Readback verifies historical receipts/bytes; it does not reconstruct past live OS ancestry.',
            'The reparse control is a source-visible mocked flag, not an actual reparse fixture; no new fixture is created here.'])


if __name__ == '__main__':
    BEGAN = time.monotonic()
    require(not (OUT/'result.json').exists() and not (OUT/'failure.json').exists(), 'Preserve one-shot audit evidence')
    DLL = setup_win32()
    for module in (old_api,new_api):
        module.create_new_store = forbidden
    execution.run_native = forbidden
    try:
        outcome = audit()
        save('result.json',outcome)
        print(json.dumps(dict(passed=True,seconds=outcome['seconds'],files=outcome['copies'][1]['files'],
            logical_bytes=outcome['retained_profile_logical_bytes'],
            named_allocated_file_bytes=outcome['v2_named_allocated_file_bytes'],result=str(OUT/'result.json'))),flush=True)
    except BaseException as exc:
        save('failure.json',dict(passed=False,scope=SCOPE,type=type(exc).__name__,message=str(exc),
            traceback=traceback.format_exc(),checks=CHECKS,reads=READS,audit_source_sha256=sha(__file__)))
        raise
