"""Read-only profile bytes, in-memory zlib samples and prospective arithmetic.

No native/scientific process, filesystem compression, hardlink, original write,
or accuracy qualification. Outputs are new staging files only.
"""
import collections
from concurrent.futures import ThreadPoolExecutor
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import time
import zlib

STAGE = Path(__file__).resolve().parent
PROFILE = Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')
POPULATION = Path(r'S:\GTOpen-research\stack-context-population-v1')
RESEARCH = Path(r'T:\Dev\GTOpen\tools\research')
KERNEL = ctypes.WinDLL('kernel32', use_last_error=True)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for b in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


class Memory(ctypes.Structure):
    _fields_ = [('length', wintypes.DWORD), ('load', wintypes.DWORD)] + [
        (name, ctypes.c_ulonglong) for name in (
            'total_physical', 'available_physical', 'total_page', 'available_page',
            'total_virtual', 'available_virtual', 'available_extended')]


def available_memory():
    value = Memory(); value.length = ctypes.sizeof(value)
    if not KERNEL.GlobalMemoryStatusEx(ctypes.byref(value)):
        raise ctypes.WinError(ctypes.get_last_error())
    return value.available_physical


def cpu_times():
    idle, kernel, user = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
    if not KERNEL.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
        raise ctypes.WinError(ctypes.get_last_error())
    convert = lambda v: (v.dwHighDateTime << 32) | v.dwLowDateTime
    return convert(idle), convert(kernel) + convert(user)


def measure(entry):
    label, path = entry
    assert path.is_relative_to(PROFILE) and path.is_file() and not path.is_symlink()
    before = path.stat()
    assert not before.st_file_attributes & 0x400
    raw = path.read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    started = time.perf_counter()
    compressed = zlib.compress(raw, level=6)
    compression_seconds = time.perf_counter() - started
    started = time.perf_counter()
    recovered = zlib.decompress(compressed)
    decompression_seconds = time.perf_counter() - started
    assert recovered == raw and hashlib.sha256(recovered).hexdigest() == raw_sha
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns, before.st_ino) == (
        after.st_size, after.st_mtime_ns, after.st_ino)
    assert sha(path) == raw_sha
    return dict(label=label, path=str(path), raw_bytes=len(raw), zlib_bytes=len(compressed),
        compressed_over_raw=len(compressed)/len(raw), raw_sha256=raw_sha,
        compression_seconds=compression_seconds, decompression_seconds=decompression_seconds,
        roundtrip_exact=True, original_file_unchanged=True)


def main():
    # Fixed first/middle/last selection before compression; not chosen by ratios.
    exports = sorted(PROFILE.glob('cycle-0001/*/batch-*/conditional/*-native.json'))
    boards = sorted(PROFILE.glob('cycle-0001/*/board-targets/board-*/board-tree-stdout.bin'))
    assert len(exports) == 76 and len(boards) == 2
    selected = [('river-first', exports[0]), ('river-middle', exports[len(exports)//2]),
        ('river-last', exports[-1]), ('board-first', boards[0]), ('board-last', boards[-1])]
    assert len(set(p for _, p in selected)) == 5
    memory = available_memory(); assert memory >= 20_000_000_000
    KERNEL.GetCurrentProcess.restype = wintypes.HANDLE
    KERNEL.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    KERNEL.SetPriorityClass.restype = wintypes.BOOL
    if not KERNEL.SetPriorityClass(KERNEL.GetCurrentProcess(), 0x00004000):
        raise ctypes.WinError(ctypes.get_last_error())
    before_idle, before_total = cpu_times(); time.sleep(.25)
    after_idle, after_total = cpu_times()
    total = after_total-before_total; assert total > 0
    cpu_fraction = 1-(after_idle-before_idle)/total
    assert cpu_fraction < .8, 'Read-only compression deferred while host CPU is busy'
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as pool:
        samples = list(pool.map(measure, selected))
    sample_wall_seconds = time.perf_counter()-started
    geometry = {}
    sources = [STAGE/'preflop-expected-profile-resource-analysis-v1.json', Path(__file__).resolve(),
        RESEARCH/'ntfs_research_storage_v1.py',
        RESEARCH/'hu_root_retained_storage_admitted_study_20260924.py',
        RESEARCH/'board_next_storage_snapshot_v3.py']
    for stack in (20, 40, 100, 200, 400):
        context_path, public_path = (POPULATION/f'stack-{stack}'/name
            for name in ('context.json', 'public.json'))
        context = json.loads(context_path.read_bytes()); public = json.loads(public_path.read_bytes())
        assert public['context_source'] == context_path.read_text(encoding='utf-8')
        counts = collections.Counter(str(row['phase']) for row in public['public_states'])
        geometry[str(stack)] = dict(context_sha256=sha(context_path), public_sha256=sha(public_path),
            public_states=len(public['public_states']), phases=dict(sorted(counts.items())),
            leaves=[node['leaf'] for node in context['nodes'] if node['kind'] == 2])
        sources.extend((context_path, public_path))
    analysis = json.loads(sources[0].read_bytes())
    river_factor = sum(g['phases'].get('3', 0) for g in geometry.values())/geometry['20']['phases']['3']
    public_factor = sum(g['public_states'] for g in geometry.values())/geometry['20']['public_states']
    river = analysis['groups']['river_native_process_stdout']['logical_bytes']
    board = analysis['groups']['board_native_tree_stdout']['logical_bytes']
    other = analysis['logical_bytes'] - 2*river - board
    projected = dict(label='Geometry proxy only; not a measured five-stack bound',
        assumptions='Same169 deals/context,K2 boards/context,posterior64,onecycle; no compression credit',
        river_public_state_factor=river_factor, total_public_state_factor=public_factor,
        raw_copied_logical_bytes=round(2*river*river_factor+(board+other)*public_factor),
        raw_hardlinked_unique_file_bytes=round(river*river_factor+(board+other)*public_factor),
        naive_fivefold_bytes=analysis['logical_bytes']*5,
        caveats=['Native subtree size and visited histories need not scale linearly with public-state count',
            'Next cumulative policy may change the physical visitation distribution',
            'Hardlink credit requires an independently qualified unique-file-ID inventory; existing inventory sums names',
            'No sampled zlib ratio is a filesystem compression ratio or admission credit'])
    output = dict(format=1, scope='Read-only software/resource planning, no accuracy claim',
        profile=str(PROFILE), raw_profile_unchanged=True, in_memory_only=True,
        algorithm='zlib level6', threads=5, available_memory_bytes=memory,
        initial_cpu_utilization_fraction=cpu_fraction, sample_wall_seconds=sample_wall_seconds,
        predetermined_selection='Sorted76 river exports indices0,38,75 and both sorted2 board tree stdout files',
        samples=samples, geometry=geometry, projection=projected,
        prior_inventory_headroom_after_profile_bytes=analysis['budget_headroom_after_this_profile_bytes'],
        source_identities={str(path):sha(path) for path in sources},
        official_references={
            'ntfs_transparency':'https://learn.microsoft.com/en-us/windows/win32/fileio/file-compression-and-decompression',
            'compact_inheritance_and_algorithms':'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact',
            'wof_chunks':'https://learn.microsoft.com/en-us/windows/win32/api/wofapi/ns-wofapi-wof_file_compression_info_v1',
            'hardlink_same_volume_mutation':'https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions'})
    path = STAGE/'preflop-expected-profile-storage-options-analysis-v1.json'
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(output, stream, sort_keys=True, separators=(',', ':')); stream.write('\n')
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__': main()
