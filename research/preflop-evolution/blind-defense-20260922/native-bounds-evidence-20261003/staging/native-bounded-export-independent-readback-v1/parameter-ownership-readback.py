"""Supplementary read-only argv, source coverage and live NTFS ownership audit.

Only reads retained records and filesystem metadata. No native control or poker
calculation is executed. The first audit and its source are preserved unchanged.
"""
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
STORE = Path(r'S:\GTOpen-research\native-bounded-export-controls-v1')
FAILURES = []
CHECKS = 0
FILES = {}


def require(ok, name, **data):
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(dict(check=name, **data))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            digest.update(part)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


class Info(ctypes.Structure):
    _fields_ = [('attributes', wintypes.DWORD), ('created', wintypes.FILETIME),
                ('accessed', wintypes.FILETIME), ('written', wintypes.FILETIME),
                ('volume', wintypes.DWORD), ('size_high', wintypes.DWORD), ('size_low', wintypes.DWORD),
                ('links', wintypes.DWORD), ('index_high', wintypes.DWORD), ('index_low', wintypes.DWORD)]


kernel = ctypes.WinDLL('kernel32', use_last_error=True)
create = kernel.CreateFileW
create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                   wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
create.restype = wintypes.HANDLE
query = kernel.GetFileInformationByHandle
query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Info)]
query.restype = wintypes.BOOL
close = kernel.CloseHandle
close.argtypes = [wintypes.HANDLE]
close.restype = wintypes.BOOL


def ownership(path):
    p = Path(path)
    if str(p) in FILES:
        return
    handle = create(str(p), 0x80, 7, None, 3, 0x02200000, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        value = Info()
        if not query(handle, ctypes.byref(value)):
            raise ctypes.WinError(ctypes.get_last_error())
        require(not value.attributes & 0x400, 'No reparse target', path=str(p))
        if not p.is_dir():
            require(value.links == 1, 'Output must have one NTFS link', path=str(p), links=value.links)
        FILES[str(p)] = dict(volume=value.volume, file_id=(value.index_high << 32) | value.index_low,
                            links=value.links, directory=p.is_dir(), attributes=value.attributes)
    finally:
        close(handle)


def run():
    original = read(HERE / 'result.json')
    require(original['passed'] is True, 'Initial audit passed')
    require(sha(HERE / 'readback.py') == original['audit_source_sha256'], 'Initial audit source preserved')
    result = read(STORE / 'result.json')
    registration = read(STORE / 'registration.json')
    expected_sources = read(STAGE / 'native-bounded-export-sources-v2/publication.json')['sources']
    runtime_sources = {str(STAGE / 'preflop_expected_bounded_native_control_v1.py'),
                       str(STAGE / 'preflop_expected_native_execution_v2.py'),
                       r'T:\Dev\GTOpen\crates\solver\examples\research_sampled\research_bounded_output_v1.rs'}
    runtime_sources.update(x['new'] for x in expected_sources)
    primary = [v for case in result['primary'] for v in case['invocations']]
    children = primary + result['helper'] + result['river_input']
    for case in children:
        wrapped = case.get('result', case)
        r = wrapped['receipt']
        for channel in (r['stdout'], r['stderr'], *r['direct_output_artifacts']):
            if channel['exists']:
                ownership(channel['path'])
        ownership(wrapped['receipt_path'])
        current = Path(r['folder'])
        while current.is_relative_to(STORE):
            ownership(current)
            if current == STORE:
                break
            current = current.parent
        require(r['caller'] == children[0].get('result', children[0])['receipt']['caller'],
                'All controls belong to the same qualified caller', label=case['label'])
        if case in primary or case in result['river_input']:
            require(runtime_sources.issubset(r['expected_identities']), 'Required runtime source pins are present', label=case['label'])
            for path in runtime_sources:
                require(r['expected_identities'].get(path) == registration['source_identities'].get(path),
                        'Receipt and registration source hash agree', path=path, label=case['label'])
    root = STORE / 'serialization-helper'
    threshold = (root / 'fixture.json').stat().st_size + 9 + 256
    specs = {
        'inclusive': ('bytes', threshold, str(threshold), True),
        'one-extra': ('bytes', threshold+1, str(threshold+1), True),
        'one-short': ('bytes', threshold-1, str(threshold-1), False),
        'empty': ('empty', 256, '256', True),
        'large-error': ('large-error', 256, '256', False),
        'large-panic': ('large-panic', 256, '256', False),
        'invalid-zero': ('bytes', 256, '0', False),
        'above-ceiling': ('bytes', 2048, '2049', False),
        'invalid-text': ('bytes', 256, 'x', False),
        'default-cap': ('bytes', 2048, None, True),
        'stdio-only': ('stdio', (root / 'fixture.json').stat().st_size+5+256,
                       str((root / 'fixture.json').stat().st_size+5+256), True),
        'existing-file': ('bytes', threshold, str(threshold), False),
        'existing-directory': ('bytes', threshold, str(threshold), False),
    }
    for item in result['helper']:
        label = item['label']
        mode, cap, cli_limit, successful = specs[label]
        target = root / label / ('sentinel' if label.startswith('existing-') else 'direct.bin')
        expected = [str(root / 'bounded-output-control.exe'), mode, str(root / 'fixture.json'), str(target)]
        if cli_limit is not None:
            expected.append('--output-byte-limit=' + cli_limit)
        r = item.get('result', item)['receipt']
        require(r['argv'] == expected and r['max_output_bytes'] == cap, 'Exact helper argv and acceptance cap', label=label)
        require(bool(item.get('expected_refusal')) != successful, 'Expected helper outcome', label=label)
        if not successful and not label.startswith('existing-'):
            require(not target.exists(), 'Helper error did not write untracked target', label=label)
        if label == 'large-panic':
            require(r['returncode'] == 101, 'Large panic uses caught-panic exit code')
        elif not successful:
            require(r['returncode'] == 1, 'Helper refusal uses controlled-error exit code', label=label)
        if label.startswith('existing-'):
            ownership(target)
    reference = result['primary'][5]['reference']
    for item in result['river_input']:
        label = item['label']
        r = item.get('result', item)['receipt']
        source = STORE / 'river-input-limits' / (label + '.json')
        context = str(source) if label.startswith('context') else reference['original_argv'][1]
        incoming = reference['stdin']['path'] if label.startswith('context') else str(source)
        expected = [registration['binaries']['river']['path'], context, '--output-byte-limit=64000000']
        require(r['argv'] == expected and r['stdin']['path'] == incoming and r['max_output_bytes'] == 64_000_000,
                'Exact river input control argv/stdin/cap', label=label)
        require(not r['direct_outputs'], 'River input controls use no direct file', label=label)
        require(bool(item.get('expected_refusal')) == (not label.endswith('at-limit')),
                'River boundary outcome matches case', label=label)
    require(len(children) == 39, 'All 39 children checked')


if __name__ == '__main__':
    output = HERE / 'parameter-ownership-result.json'
    if output.exists():
        raise FileExistsError('Never overwrite audit evidence')
    run()
    value = dict(passed=not FAILURES, checks=CHECKS, failures=FAILURES,
                 initial_audit_sha256=sha(HERE / 'result.json'), source_sha256=sha(__file__),
                 native_control_receipts_checked=39, filesystem_identities=FILES,
                 no_controls_rerun=True, no_build_rerun=True, scientific_accuracy_qualified=False,
                 terminal_unix=time.time())
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps(dict(passed=value['passed'], checks=CHECKS, failures=FAILURES,
                         filesystem_identities=len(FILES), result=str(output))))
